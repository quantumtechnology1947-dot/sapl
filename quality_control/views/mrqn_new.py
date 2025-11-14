"""
Material Return Quality Note (MRQN) Views - Complete Workflow

Multi-step workflow for MRQN creation and management:
1. List pending MRN records
2. Select MRN and enter quality inspection data
3. Create MRQN
4. Manage existing MRQNs (CRUD)
"""
from django.views.generic import ListView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.db import models
from datetime import datetime

from .base import QualityControlBaseMixin
from quality_control.models import TblqcMaterialreturnqualityMaster, TblqcRejectionReason
from inventory.models import TblinvMaterialreturnMaster, TblinvMaterialreturnDetails


class MRQNNewView(QualityControlBaseMixin, TemplateView):
    """
    MRQN Step 1: List pending MRN records for quality inspection
    Similar to GQN workflow
    """
    template_name = 'quality_control/mrqn/mrn_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get search parameters
        search_type = self.request.GET.get('search_type', '0')  # 0=MRN No, 1=Department
        search_value = self.request.GET.get('search_value', '')

        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get pending MRN records
        pending_mrns = self.get_pending_mrn_records(
            compid,
            finyearid,
            search_type if search_value else None,
            search_value if search_value else None
        )

        context['pending_mrns'] = pending_mrns
        context['search_type'] = search_type
        context['search_value'] = search_value

        return context

    def get_pending_mrn_records(self, comp_id, fin_year_id, search_type=None, search_value=None):
        """Get MRN records that have pending quality inspection"""
        from sys_admin.models import TblfinancialMaster
        from decimal import Decimal

        # Get all MRN records - show current and previous financial years
        mrn_qs = TblinvMaterialreturnMaster.objects.filter(
            compid=comp_id,
            finyearid__lte=fin_year_id
        ).select_related()

        # Apply search filters
        if search_type and search_value:
            if search_type == '0':  # MRN No
                mrn_qs = mrn_qs.filter(mrnno__icontains=search_value)
            elif search_type == '1':  # Department (would need to join with details)
                pass  # TODO: Implement department search

        # Calculate pending qty and filter
        pending_mrns = []

        for mrn in mrn_qs.order_by('-id'):
            # Calculate MRN Qty = SUM(RetQty)
            mrn_qty = TblinvMaterialreturnDetails.objects.filter(
                mid=mrn.id
            ).aggregate(total=models.Sum('retqty'))['total']

            if mrn_qty is None:
                mrn_qty = Decimal('0')
            else:
                mrn_qty = Decimal(str(mrn_qty))

            # Calculate MRQN Qty = SUM(AcceptedQty) + SUM(RejectedQty)
            from quality_control.models import TblqcMaterialreturnqualityDetails
            mrqn_qty = TblqcMaterialreturnqualityDetails.objects.filter(
                mid__mrnid=mrn.id
            ).aggregate(
                accepted=models.Sum('acceptedqty'),
                rejected=models.Sum('rejectedqty')
            )

            accepted = Decimal(str(mrqn_qty['accepted'])) if mrqn_qty['accepted'] else Decimal('0')
            rejected = Decimal(str(mrqn_qty['rejected'])) if mrqn_qty['rejected'] else Decimal('0')
            total_inspected = accepted + rejected

            remaining = mrn_qty - total_inspected

            if round(float(remaining), 3) > 0:
                mrn.returned_qty = float(mrn_qty)
                mrn.inspected_qty = float(total_inspected)
                mrn.remaining_qty = float(remaining)

                try:
                    finyear = TblfinancialMaster.objects.get(finyearid=mrn.finyearid)
                    mrn.finyear_name = finyear.finyear
                except:
                    mrn.finyear_name = str(mrn.finyearid)

                pending_mrns.append(mrn)

        return pending_mrns


class MRQNMRNDetailsView(QualityControlBaseMixin, TemplateView):
    """
    MRQN Step 2: Show MRN details and quality inspection form
    """
    template_name = 'quality_control/mrqn/mrn_details.html'

    def get(self, request, mrn_id):
        try:
            # Get MRN with details
            mrn_master = TblinvMaterialreturnMaster.objects.get(id=mrn_id)
            mrn_details = TblinvMaterialreturnDetails.objects.filter(mid=mrn_id)

            # Get rejection reasons for dropdown
            rejection_reasons = TblqcRejectionReason.objects.all()

            # Enrich MRN details with item information
            enriched_details = []
            for detail in mrn_details:
                enriched_detail = {
                    'id': detail.id,
                    'retqty': detail.retqty,
                    'item_id': detail.itemid,
                    'dept_id': detail.deptid,
                    'wo_no': detail.wono,
                    'remarks': detail.remarks,
                    'item_code': 'N/A',
                    'description': 'N/A',
                    'uom': 'NOS',
                }

                # Try to get real item information
                try:
                    from design.models import TbldgItemMaster
                    item = TbldgItemMaster.objects.get(id=detail.itemid)
                    enriched_detail.update({
                        'item_code': item.itemcode or 'N/A',
                        'description': item.manfdesc or 'N/A',
                        'uom': 'NOS',
                    })
                except Exception as e:
                    print(f"Warning: Could not get item info for detail {detail.id}: {e}")
                    pass

                enriched_details.append(enriched_detail)

            context = {
                'mrn_master': mrn_master,
                'mrn_details': enriched_details,
                'rejection_reasons': rejection_reasons,
            }

            return self.render_to_response(context)

        except Exception as e:
            messages.error(request, f'Error loading MRN details: {str(e)}')
            return redirect('quality_control:mrqn-new')

    def post(self, request, mrn_id):
        """Save MRQN with quality inspection data"""
        # Get MRN info
        mrn = TblinvMaterialreturnMaster.objects.get(id=mrn_id)

        # Parse quality inspection data from form
        quality_data = []
        item_ids = request.POST.getlist('item_id')

        for item_id in item_ids:
            # Check if this item was selected (checked)
            if request.POST.get(f'selected_{item_id}'):
                # Get all quantity values
                accepted_qty = float(request.POST.get(f'accepted_qty_{item_id}', 0) or 0)
                rejected_qty = float(request.POST.get(f'rejected_qty_{item_id}', 0) or 0)
                
                quality_data.append({
                    'mrn_detail_id': int(item_id),
                    'accepted_qty': accepted_qty,
                    'rejected_qty': rejected_qty,
                })

        if not quality_data:
            messages.error(request, 'Please select at least one item and enter quality inspection data!')
            return redirect('quality_control:mrqn-mrn-details', mrn_id=mrn_id)

        try:
            # Create MRQN using service
            from quality_control.services import MRQNCreationService
            mrqn = MRQNCreationService.create_mrqn_from_mrn(
                self.get_compid(),
                self.get_finyearid(),
                request.user.id,
                mrn_id,
                mrn.mrnno,
                quality_data
            )

            messages.success(request, f'MRQN {mrqn.mrqnno} created successfully!')
            return redirect('quality_control:mrqn-list')

        except Exception as e:
            messages.error(request, f'Error creating MRQN: {str(e)}')
            return redirect('quality_control:mrqn-mrn-details', mrn_id=mrn_id)
