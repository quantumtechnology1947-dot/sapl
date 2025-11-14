"""
PO (Purchase Order) Service Classes
Converted from: aaspnet/Module/MaterialManagement/Transactions/PO_*.aspx.cs

Business logic for Purchase Order creation, editing, and approval workflows.
"""
from decimal import Decimal
from datetime import datetime
from django.db.models import Sum, Q, F, Count, Max
from django.db import transaction

from .models import (
    POMaster, PODetails, PRMaster, PRDetails, SPRMaster, SPRDetails,
    MmPrPoTemp, MmSprPoTemp, Supplier, RateRegister
)
# TODO: Add MmRateLockUnlockMaster model for rate locking functionality
from design.models import TbldgItemMaster


class PONumberService:
    """Service for generating PO numbers"""

    @staticmethod
    def generate_po_number(comp_id, fin_year_id):
        """
        Generate next PO number for the financial year
        Format: "0001", "0002", etc.
        """
        # Order by po_id (AutoField) to get most recent PO, not po_no (string ordering issue)
        last_po = POMaster.objects.filter(
            comp_id=comp_id,
            fin_year_id=fin_year_id
        ).order_by('-po_id').first()

        if last_po and last_po.po_no:
            try:
                next_num = int(last_po.po_no) + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        return f'{next_num:04d}'  # e.g., "0001", "0002"


class POSupplierService:
    """Service for getting suppliers with pending PR/SPR items"""

    @staticmethod
    def get_suppliers_with_pr_items(comp_id, fin_year_id, supplier_code=None):
        """
        Get suppliers who have PR items that haven't been fully converted to PO
        Mimics: GetSupplier_PO_PR stored procedure
        """
        from django.db import connection

        # This would ideally call the stored procedure
        # For now, we'll build the equivalent query
        suppliers = []

        # Get all PRs (no authorization filter needed for PR, unlike SPR)
        pr_details = PRDetails.objects.filter(
            m_id__in=PRMaster.objects.filter(
                comp_id=comp_id,
                fin_year_id=fin_year_id
            ).values_list('pr_id', flat=True)
        )

        if supplier_code:
            pr_details = pr_details.filter(supplier_id=supplier_code)

        # Group by supplier and count items with remaining quantity
        supplier_data = {}
        for detail in pr_details:
            # Calculate remaining quantity
            po_qty = PODetails.objects.filter(
                pr_id=detail.id
            ).aggregate(total=Sum('qty'))['total'] or 0

            remain_qty = float(detail.qty) - float(po_qty)

            if remain_qty > 0:
                if detail.supplier_id not in supplier_data:
                    try:
                        supplier = Supplier.objects.get(supplier_id=detail.supplier_id)
                        supplier_data[detail.supplier_id] = {
                            'name': supplier.supplier_name,
                            'code': detail.supplier_id,
                            'item_count': 0
                        }
                    except Supplier.DoesNotExist:
                        continue

                supplier_data[detail.supplier_id]['item_count'] += 1

        return list(supplier_data.values())

    @staticmethod
    def get_suppliers_with_spr_items(comp_id, fin_year_id, supplier_code=None):
        """
        Get suppliers who have SPR items that haven't been fully converted to PO
        Mimics: GetSupplier_PO_SPR stored procedure
        """
        suppliers = []

        # Get all authorized SPRs
        spr_details = SPRDetails.objects.filter(
            m_id__in=SPRMaster.objects.filter(
                comp_id=comp_id,
                fin_year_id=fin_year_id,
                authorize=1
            ).values_list('spr_id', flat=True)
        )

        if supplier_code:
            spr_details = spr_details.filter(supplier_id=supplier_code)

        # Group by supplier and count items with remaining quantity
        supplier_data = {}
        for detail in spr_details:
            # Calculate remaining quantity
            po_qty = PODetails.objects.filter(
                spr_id=detail.id
            ).aggregate(total=Sum('qty'))['total'] or 0

            remain_qty = float(detail.qty) - float(po_qty)

            if remain_qty > 0:
                if detail.supplier_id not in supplier_data:
                    try:
                        supplier = Supplier.objects.get(supplier_id=detail.supplier_id)
                        supplier_data[detail.supplier_id] = {
                            'name': supplier.supplier_name,
                            'code': detail.supplier_id,
                            'item_count': 0
                        }
                    except Supplier.DoesNotExist:
                        continue

                supplier_data[detail.supplier_id]['item_count'] += 1

        return list(supplier_data.values())


class POCalculationService:
    """Service for PO amount calculations"""

    @staticmethod
    def calculate_basic_amt(qty: Decimal, rate: Decimal) -> Decimal:
        """Calculate basic amount: Qty * Rate"""
        return qty * rate

    @staticmethod
    def calculate_disc_amt(qty: Decimal, rate: Decimal, discount: Decimal) -> Decimal:
        """Calculate discount amount: (Qty * Rate) * (Discount / 100)"""
        basic = qty * rate
        return basic * (discount / 100)

    @staticmethod
    def calculate_net_amt(qty: Decimal, rate: Decimal, discount: Decimal) -> Decimal:
        """Calculate net amount after discount"""
        basic = qty * rate
        disc = basic * (discount / 100)
        return basic - disc

    @staticmethod
    def calculate_tax_amt(net_amt: Decimal, pf_val: Decimal, exst_val: Decimal, vat_val: Decimal) -> dict:
        """
        Calculate individual tax amounts and total
        Returns: {'pf_amt': X, 'exst_amt': Y, 'vat_amt': Z, 'total_tax': T}
        """
        pf_amt = net_amt * (pf_val / 100) if pf_val else Decimal('0')
        exst_amt = net_amt * (exst_val / 100) if exst_val else Decimal('0')
        vat_amt = net_amt * (vat_val / 100) if vat_val else Decimal('0')

        return {
            'pf_amt': pf_amt,
            'exst_amt': exst_amt,
            'vat_amt': vat_amt,
            'total_tax': pf_amt + exst_amt + vat_amt
        }

    @staticmethod
    def calculate_total_amt(qty: Decimal, rate: Decimal, discount: Decimal,
                          pf_val: Decimal = Decimal('0'),
                          exst_val: Decimal = Decimal('0'),
                          vat_val: Decimal = Decimal('0')) -> Decimal:
        """Calculate final total amount including all taxes"""
        net_amt = POCalculationService.calculate_net_amt(qty, rate, discount)
        tax_info = POCalculationService.calculate_tax_amt(net_amt, pf_val, exst_val, vat_val)
        return net_amt + tax_info['total_tax']


class RateValidationService:
    """Service for validating rates against rate register and lock status"""

    @staticmethod
    def get_min_historical_rate(item_id, comp_id):
        """
        Get minimum historical rate (after discount) from rate register
        Returns None if no historical rate exists
        """
        min_rate = RateRegister.objects.filter(
            item_id=item_id,
            comp_id=comp_id
        ).aggregate(
            min_rate=Min(F('rate') - (F('rate') * F('discount') / 100))
        )['min_rate']

        return min_rate

    @staticmethod
    def is_rate_acceptable(item_id, comp_id, rate, discount):
        """
        Check if the new rate is acceptable based on:
        1. Historical minimum rate
        2. Lock/unlock status

        Returns: (is_acceptable: bool, message: str)
        """
        # Calculate new rate after discount
        new_rate = rate - (rate * discount / 100)

        # Get historical minimum rate
        min_rate = RateValidationService.get_min_historical_rate(item_id, comp_id)

        # If no historical rate, accept (first time purchase)
        if min_rate is None:
            return True, "Rate accepted (first time purchase)"

        # If new rate is less than or equal to historical minimum, accept
        if new_rate <= min_rate:
            return True, "Rate accepted (within historical range)"

        # New rate is higher - check if item is unlocked
        # TODO: Implement rate lock/unlock check using MmRateLockUnlockMaster model
        # For now, allow all rates (as if unlocked)
        return True, "Rate accepted (rate locking not yet implemented)"


class POCreationService:
    """Service for creating PO from PR/SPR"""

    @staticmethod
    @transaction.atomic
    def create_po_from_pr(comp_id, fin_year_id, user_id, supplier_id, po_data, temp_items):
        """
        Create PO from PR items

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            user_id: User ID creating the PO
            supplier_id: Supplier ID
            po_data: Dict with reference, payment terms, TC, etc.
            temp_items: QuerySet of MmPrPoTemp items

        Returns:
            Created POMaster instance
        """
        now = datetime.now()

        # Generate PO number
        po_no = PONumberService.generate_po_number(comp_id, fin_year_id)

        # Create PO Master
        po_master = POMaster.objects.create(
            po_no=po_no,
            comp_id=comp_id,
            fin_year_id=fin_year_id,
            supplier_id=supplier_id,
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S'),
            session_id=str(user_id),
            pr_spr_flag=0,  # 0 = PR
            amendment_no=0,
            reference=po_data.get('reference'),
            reference_date=po_data.get('reference_date'),
            reference_desc=po_data.get('reference_desc'),
            payment_terms=po_data.get('payment_terms'),
            warrenty=po_data.get('warrenty'),
            freight=po_data.get('freight'),
            octroi=po_data.get('octroi'),
            mode_of_dispatch=po_data.get('mode_of_dispatch'),
            inspection=po_data.get('inspection'),
            ship_to=po_data.get('ship_to'),
            remarks=po_data.get('remarks'),
            insurance=po_data.get('insurance'),
            tc=po_data.get('tc'),
            checked=0,
            approve=0,
            authorize=0
        )

        # Create PO Details from temp items
        for temp_item in temp_items:
            PODetails.objects.create(
                m_id=po_master.po_id,
                po_no=po_no,
                pr_no=temp_item.pr_no,
                pr_id=temp_item.pr_id,
                qty=temp_item.qty,
                rate=temp_item.rate,
                discount=temp_item.discount,
                add_desc=temp_item.add_desc,
                pf=temp_item.pf,
                ex_st=temp_item.ex_st,
                vat=temp_item.vat,
                del_date=temp_item.del_date,
                budget_code=temp_item.budget_code,
                amendment_no=0
            )

        # TODO: Lock items in rate lock table
        # TODO: Insert into rate register

        # Clean up temp table
        temp_items.delete()

        return po_master

    @staticmethod
    @transaction.atomic
    def create_po_from_spr(comp_id, fin_year_id, user_id, supplier_id, po_data, temp_items):
        """
        Create PO from SPR items
        Similar to create_po_from_pr but with pr_spr_flag=1
        """
        now = datetime.now()

        # Generate PO number
        po_no = PONumberService.generate_po_number(comp_id, fin_year_id)

        # Create PO Master
        po_master = POMaster.objects.create(
            po_no=po_no,
            comp_id=comp_id,
            fin_year_id=fin_year_id,
            supplier_id=supplier_id,
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S'),
            session_id=str(user_id),
            pr_spr_flag=1,  # 1 = SPR
            amendment_no=0,
            reference=po_data.get('reference'),
            reference_date=po_data.get('reference_date'),
            reference_desc=po_data.get('reference_desc'),
            payment_terms=po_data.get('payment_terms'),
            warrenty=po_data.get('warrenty'),
            freight=po_data.get('freight'),
            octroi=po_data.get('octroi'),
            mode_of_dispatch=po_data.get('mode_of_dispatch'),
            inspection=po_data.get('inspection'),
            ship_to=po_data.get('ship_to'),
            remarks=po_data.get('remarks'),
            insurance=po_data.get('insurance'),
            tc=po_data.get('tc'),
            checked=0,
            approve=0,
            authorize=0
        )

        # Create PO Details from temp items
        for temp_item in temp_items:
            PODetails.objects.create(
                m_id=po_master.po_id,
                po_no=po_no,
                spr_no=temp_item.spr_no,
                spr_id=temp_item.spr_id,
                qty=temp_item.qty,
                rate=temp_item.rate,
                discount=temp_item.discount,
                add_desc=temp_item.add_desc,
                pf=temp_item.pf,
                ex_st=temp_item.ex_st,
                vat=temp_item.vat,
                del_date=temp_item.del_date,
                budget_code=temp_item.budget_code,
                amendment_no=0
            )

        # Clean up temp table
        temp_items.delete()

        return po_master


class POTempService:
    """Service for managing temporary PO tables during creation"""

    @staticmethod
    def cleanup_pr_temp(comp_id, user_id):
        """Delete all PR temp items for this user/company"""
        MmPrPoTemp.objects.filter(
            comp_id=comp_id,
            session_id=str(user_id)
        ).delete()

    @staticmethod
    def cleanup_spr_temp(comp_id, user_id):
        """Delete all SPR temp items for this user/company"""
        MmSprPoTemp.objects.filter(
            comp_id=comp_id,
            session_id=str(user_id)
        ).delete()

    @staticmethod
    def get_pr_temp_items(comp_id, user_id):
        """Get all PR temp items for this user"""
        return MmPrPoTemp.objects.filter(
            comp_id=comp_id,
            session_id=str(user_id)
        )

    @staticmethod
    def get_spr_temp_items(comp_id, user_id):
        """Get all SPR temp items for this user"""
        return MmSprPoTemp.objects.filter(
            comp_id=comp_id,
            session_id=str(user_id)
        )

