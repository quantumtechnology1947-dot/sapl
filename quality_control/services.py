"""
Quality Control Services

Centralized business logic for quality control operations:
- GQN (Goods Quality Note) processing
- MRQN (Material Return Quality Note) processing
- Quality analysis and reporting
"""
from decimal import Decimal
from datetime import datetime
from django.db.models import Sum, Q, F, Count, Avg
from django.db import transaction

from inventory.models import (
    TblinvMaterialreceivedMaster,
    TblinvMaterialreceivedDetails,
    TblinvMaterialreturnMaster,
    TblinvInwardMaster,
)
from material_management.models import POMaster, Supplier
from quality_control.models import (
    TblqcMaterialqualityMaster,
    TblqcMaterialqualityDetails,
    TblqcMaterialreturnqualityMaster,
    TblqcScrapregister,
    TblqcRejectionReason,
)


# ============================================================================
# GQN (Goods Quality Note) Services
# ============================================================================

class GQNNumberService:
    """Service for generating GQN numbers"""

    @staticmethod
    def generate_gqn_number(comp_id, fin_year_id):
        """
        Generate next GQN number for the financial year
        Format: "GQN-0001", "GQN-0002", etc.
        """
        last_gqn = TblqcMaterialqualityMaster.objects.filter(
            compid=comp_id,
            finyearid=fin_year_id
        ).order_by('-id').first()

        if last_gqn and last_gqn.gqnno:
            try:
                # Extract number from "GQN-0001" format
                parts = last_gqn.gqnno.split('-')
                if len(parts) == 2:
                    next_num = int(parts[1]) + 1
                else:
                    next_num = 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        return f'GQN-{next_num:04d}'


class GQNGRRService:
    """Service for getting GRR records pending quality inspection"""

    @staticmethod
    def get_pending_grr_records(comp_id, fin_year_id, search_type=None, search_value=None):
        """
        Get GRR records that have pending quality inspection

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            search_type: '0' = Supplier Name, '1' = GRR No, '2' = PO No
            search_value: Search value

        Returns:
            QuerySet of GRR records with remaining qty > 0
        """
        from sys_admin.models import TblfinancialMaster

        # Get all GRR records - show current and previous financial years like old ASP.NET system
        grr_qs = TblinvMaterialreceivedMaster.objects.filter(
            compid=comp_id,
            finyearid__lte=fin_year_id
        ).select_related()

        # Apply search filters
        if search_type and search_value:
            if search_type == '0':  # Supplier Name
                supplier_ids = Supplier.objects.filter(
                    supplier_name__icontains=search_value
                ).values_list('supplier_id', flat=True)

                grr_qs = grr_qs.filter(
                    ginid__in=TblinvInwardMaster.objects.filter(
                        pomid__in=POMaster.objects.filter(
                            supplier_id__in=supplier_ids
                        ).values_list('po_id', flat=True)
                    ).values_list('id', flat=True)
                )
            elif search_type == '1':  # GRR No
                grr_qs = grr_qs.filter(grrno__icontains=search_value)
            elif search_type == '2':  # PO No
                grr_qs = grr_qs.filter(
                    ginid__in=TblinvInwardMaster.objects.filter(
                        pomid__in=POMaster.objects.filter(
                            po_no__icontains=search_value
                        ).values_list('po_id', flat=True)
                    ).values_list('id', flat=True)
                )

        # Calculate pending qty and filter
        pending_grrs = []

        for grr in grr_qs.order_by('-id'):
            # Calculate GRRQty = SUM(ReceivedQty)
            grr_qty = TblinvMaterialreceivedDetails.objects.filter(
                mid=grr.id
            ).aggregate(total=Sum('receivedqty'))['total']

            if grr_qty is None:
                grr_qty = Decimal('0')
            else:
                grr_qty = Decimal(str(grr_qty))

            # Calculate GQNQty = SUM(AcceptedQty) + SUM(RejectedQty)
            gqn_qty = TblqcMaterialqualityDetails.objects.filter(
                mid__grrid=grr.id
            ).aggregate(
                accepted=Sum('acceptedqty'),
                rejected=Sum('rejectedqty')
            )

            accepted = Decimal(str(gqn_qty['accepted'])) if gqn_qty['accepted'] else Decimal('0')
            rejected = Decimal(str(gqn_qty['rejected'])) if gqn_qty['rejected'] else Decimal('0')
            total_inspected = accepted + rejected

            remaining = grr_qty - total_inspected

            if round(float(remaining), 3) > 0:
                grr.received_qty = float(grr_qty)
                grr.inspected_qty = float(total_inspected)
                grr.remaining_qty = float(remaining)

                try:
                    finyear = TblfinancialMaster.objects.get(finyearid=grr.finyearid)
                    grr.finyear_name = finyear.finyear
                except:
                    grr.finyear_name = str(grr.finyearid)

                pending_grrs.append(grr)

        return pending_grrs

    @staticmethod
    def get_grr_with_details(grr_id):
        """
        Get GRR record with all item details for quality inspection

        Returns:
            Tuple of (grr_master, grr_details_list)
        """
        grr_master = TblinvMaterialreceivedMaster.objects.get(id=grr_id)
        grr_details = TblinvMaterialreceivedDetails.objects.filter(mid=grr_id)

        # Enrich details with pending qty
        for detail in grr_details:
            inspected = TblqcMaterialqualityDetails.objects.filter(
                grrid=grr_id,
                gqnno__isnull=False
            ).aggregate(
                total=Sum('acceptedqty') + Sum('rejectedqty') +
                      Sum('normalaccqty') + Sum('deviatedqty') + Sum('segregatedqty')
            )['total'] or 0

            detail.inspected_qty = inspected
            detail.pending_qty = (detail.receivedqty or 0) - inspected

        return grr_master, list(grr_details)


class GQNCreationService:
    """Service for creating GQN from GRR"""

    @staticmethod
    @transaction.atomic
    def create_gqn_from_grr(comp_id, fin_year_id, user_id, grr_id, grr_no, quality_data):
        """
        Create GQN from GRR with quality inspection data

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            user_id: User ID creating the GQN
            grr_id: GRR Master ID
            grr_no: GRR Number
            quality_data: List of dicts with quality inspection data

        Returns:
            Created GQN master instance
        """
        now = datetime.now()

        # Generate GQN number
        gqn_no = GQNNumberService.generate_gqn_number(comp_id, fin_year_id)

        # Create GQN Master
        gqn_master = TblqcMaterialqualityMaster.objects.create(
            gqnno=gqn_no,
            grrno=grr_no,
            grrid=grr_id,
            compid=comp_id,
            finyearid=fin_year_id,
            sessionid=str(user_id),
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S')
        )

        # Create GQN Details
        for item_data in quality_data:
            TblqcMaterialqualityDetails.objects.create(
                mid=gqn_master,
                gqnno=gqn_no,
                grrid=item_data.get('grr_detail_id'),
                normalaccqty=item_data.get('normal_acc_qty', 0),
                acceptedqty=item_data.get('accepted_qty', 0),
                deviatedqty=item_data.get('deviated_qty', 0),
                segregatedqty=item_data.get('segregated_qty', 0),
                rejectedqty=item_data.get('rejected_qty', 0),
                rejectionreason=item_data.get('rejection_reason'),
                sn=item_data.get('sn', ''),
                pn=item_data.get('pn', ''),
                remarks=item_data.get('remarks', '')
            )

        return gqn_master


# ============================================================================
# MRQN (Material Return Quality Note) Services
# ============================================================================

class MRQNNumberService:
    """Service for generating MRQN numbers"""

    @staticmethod
    def generate_mrqn_number(comp_id, fin_year_id):
        """
        Generate next MRQN number for the financial year
        Format: "MRQN-0001", "MRQN-0002", etc.
        """
        last_mrqn = TblqcMaterialreturnqualityMaster.objects.filter(
            compid=comp_id,
            finyearid=fin_year_id
        ).order_by('-id').first()

        if last_mrqn and last_mrqn.mrqnno:
            try:
                parts = last_mrqn.mrqnno.split('-')
                if len(parts) == 2:
                    next_num = int(parts[1]) + 1
                else:
                    next_num = 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        return f'MRQN-{next_num:04d}'


class MRQNSearchService:
    """Service for searching and filtering MRN records"""

    @staticmethod
    def search_mrn_records(comp_id, search_by=None, search_value=None):
        """
        Search MRN records for MRQN creation

        Args:
            comp_id: Company ID
            search_by: '0' = MRN No, '1' = Employee Name
            search_value: Search value

        Returns:
            QuerySet of MRN records
        """
        queryset = TblinvMaterialreturnMaster.objects.filter(
            compid=comp_id
        )

        if search_value:
            if search_by == '0':  # MRN No
                queryset = queryset.filter(mrnno__icontains=search_value)
            elif search_by == '1':  # Employee Name
                queryset = queryset.filter(mrnno__icontains=search_value)

        return queryset.order_by('-id')

    @staticmethod
    def get_mrn_with_details(mrn_id):
        """
        Get MRN record with all item details

        Returns:
            Tuple of (mrn_master, mrn_details_list)
        """
        from inventory.models import TblinvMaterialreturnDetails

        mrn_master = TblinvMaterialreturnMaster.objects.get(id=mrn_id)
        mrn_details = TblinvMaterialreturnDetails.objects.filter(mid=mrn_id)

        return mrn_master, list(mrn_details)


class AuthorizedMCNService:
    """Service for authorizing MCN details"""

    @staticmethod
    @transaction.atomic
    def authorize_mcn_details(comp_id, fin_year_id, user_id, mcn_id, auth_data):
        """
        Authorize MCN details with QA quantity

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            user_id: User ID authorizing
            mcn_id: MCN Master ID
            auth_data: List of dicts with authorization data

        Returns:
            Number of records authorized
        """
        now = datetime.now()
        count = 0

        for item_data in auth_data:
            TblqcAuthorizedmcn.objects.create(
                mcnid=mcn_id,
                mcndid=item_data.get('mcnd_id'),
                qaqty=item_data.get('qa_qty', 0),
                compid=comp_id,
                finyearid=fin_year_id,
                sessionid=str(user_id),
                sysdate=now.strftime('%d-%m-%Y'),
                systime=now.strftime('%H:%M:%S')
            )
            count += 1

        return count


class MRQNCreationService:
    """Service for creating MRQN from MRN"""

    @staticmethod
    @transaction.atomic
    def create_mrqn_from_mrn(comp_id, fin_year_id, user_id, mrn_id, mrn_no, quality_data):
        """
        Create MRQN from MRN with quality inspection data

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            user_id: User ID creating the MRQN
            mrn_id: MRN Master ID
            mrn_no: MRN Number
            quality_data: List of dicts with quality inspection data

        Returns:
            Created MRQN master instance
        """
        now = datetime.now()

        # Generate MRQN number
        mrqn_no = MRQNNumberService.generate_mrqn_number(comp_id, fin_year_id)

        # Create MRQN Master
        mrqn_master = TblqcMaterialreturnqualityMaster.objects.create(
            mrqnno=mrqn_no,
            mrnno=mrn_no,
            mrnid=mrn_id,
            compid=comp_id,
            finyearid=fin_year_id,
            sessionid=str(user_id),
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S')
        )

        # Create MRQN Details
        from quality_control.models import TblqcMaterialreturnqualityDetails
        for item_data in quality_data:
            TblqcMaterialreturnqualityDetails.objects.create(
                mid=mrqn_master,
                mrqnno=mrqn_no,
                mrnid=item_data.get('mrn_detail_id'),
                acceptedqty=item_data.get('accepted_qty', 0),
                rejectedqty=item_data.get('rejected_qty', 0),
            )

        return mrqn_master


# ============================================================================
# Quality Statistics and Reporting Services
# ============================================================================

class QualityStatisticsService:
    """Service for calculating quality control statistics"""

    @staticmethod
    def get_dashboard_statistics(comp_id, fin_year_id):
        """
        Get dashboard statistics for quality control

        Returns:
            Dict with counts and recent records
        """
        statistics = {
            'total_gqn': TblqcMaterialqualityMaster.objects.filter(
                compid=comp_id, finyearid=fin_year_id
            ).count(),
            'total_mrqn': TblqcMaterialreturnqualityMaster.objects.filter(
                compid=comp_id, finyearid=fin_year_id
            ).count(),
            'total_scrap': TblqcScrapregister.objects.filter(
                compid=comp_id, finyearid=fin_year_id
            ).count(),
            'rejection_reasons': TblqcRejectionReason.objects.all().count(),
        }

        statistics['recent_gqns'] = TblqcMaterialqualityMaster.objects.filter(
            compid=comp_id, finyearid=fin_year_id
        ).order_by('-id')[:5]

        statistics['recent_mrqns'] = TblqcMaterialreturnqualityMaster.objects.filter(
            compid=comp_id, finyearid=fin_year_id
        ).order_by('-id')[:5]

        return statistics

    @staticmethod
    def get_quality_report_data(comp_id, fin_year_id, from_date=None, to_date=None):
        """
        Get quality report data with optional date filtering

        Returns:
            Dict with GQN, MRQN, and Scrap data
        """
        gqn_queryset = TblqcMaterialqualityMaster.objects.filter(
            compid=comp_id, finyearid=fin_year_id
        )
        if from_date and to_date:
            gqn_queryset = gqn_queryset.filter(sysdate__gte=from_date, sysdate__lte=to_date)

        mrqn_queryset = TblqcMaterialreturnqualityMaster.objects.filter(
            compid=comp_id, finyearid=fin_year_id
        )
        if from_date and to_date:
            mrqn_queryset = mrqn_queryset.filter(sysdate__gte=from_date, sysdate__lte=to_date)

        scrap_queryset = TblqcScrapregister.objects.filter(
            compid=comp_id, finyearid=fin_year_id
        )
        if from_date and to_date:
            scrap_queryset = scrap_queryset.filter(sysdate__gte=from_date, sysdate__lte=to_date)

        return {
            'gqn_data': gqn_queryset,
            'mrqn_data': mrqn_queryset,
            'scrap_data': scrap_queryset,
            'total_scrap_qty': scrap_queryset.aggregate(total=Sum('qty'))['total'] or 0,
        }


class RejectionAnalysisService:
    """Service for rejection analysis and calculations"""

    @staticmethod
    def get_rejection_summary(comp_id, fin_year_id, from_date=None, to_date=None):
        """
        Get rejection summary grouped by rejection reason

        Returns:
            List of dicts with rejection reason and totals
        """
        details_queryset = TblqcMaterialqualityDetails.objects.filter(
            mid__compid=comp_id,
            mid__finyearid=fin_year_id
        ).exclude(rejectedqty__isnull=True).exclude(rejectedqty=0)

        if from_date and to_date:
            details_queryset = details_queryset.filter(
                mid__sysdate__gte=from_date,
                mid__sysdate__lte=to_date
            )

        rejection_summary = details_queryset.values('rejectionreason').annotate(
            total_rejected=Sum('rejectedqty'),
            count=Count('id')
        ).order_by('-total_rejected')

        rejection_reasons = {r.id: r for r in TblqcRejectionReason.objects.all()}

        result = []
        for item in rejection_summary:
            reason_id = item['rejectionreason']
            item['reason_obj'] = rejection_reasons.get(reason_id) if reason_id else None
            result.append(item)

        total_rejected = sum(item['total_rejected'] for item in result)

        return {
            'rejection_summary': result,
            'total_rejected': total_rejected,
        }

    @staticmethod
    def calculate_quality_metrics(gqn_details_queryset):
        """
        Calculate quality metrics from GQN details

        Args:
            gqn_details_queryset: QuerySet of TblqcMaterialqualityDetails

        Returns:
            Dict with quality metrics (acceptance rate, rejection rate, etc.)
        """
        aggregates = gqn_details_queryset.aggregate(
            total_accepted=Sum('acceptedqty'),
            total_rejected=Sum('rejectedqty'),
            total_deviated=Sum('deviatedqty'),
            total_segregated=Sum('segregatedqty'),
            total_normal_acc=Sum('normalaccqty'),
        )

        total_accepted = Decimal(str(aggregates['total_accepted'] or 0))
        total_rejected = Decimal(str(aggregates['total_rejected'] or 0))
        total_deviated = Decimal(str(aggregates['total_deviated'] or 0))
        total_segregated = Decimal(str(aggregates['total_segregated'] or 0))
        total_normal_acc = Decimal(str(aggregates['total_normal_acc'] or 0))

        total_inspected = total_accepted + total_rejected + total_deviated + total_segregated

        acceptance_rate = (total_accepted / total_inspected * 100) if total_inspected > 0 else 0
        rejection_rate = (total_rejected / total_inspected * 100) if total_inspected > 0 else 0

        return {
            'total_accepted': float(total_accepted),
            'total_rejected': float(total_rejected),
            'total_deviated': float(total_deviated),
            'total_segregated': float(total_segregated),
            'total_normal_acc': float(total_normal_acc),
            'total_inspected': float(total_inspected),
            'acceptance_rate': float(acceptance_rate),
            'rejection_rate': float(rejection_rate),
        }
