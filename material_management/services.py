"""
Material Management Business Logic Services

Extracted business logic from views.py to promote reusability and separation of concerns.
Handles PR/SPR number generation, approval workflows, and rate management logic.
"""

from decimal import Decimal
from datetime import datetime
from django.db.models import Max, F, Sum, Q
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.db import transaction

from .models import (
    PRMaster, PRDetails, TempPR,
    SPRMaster, SPRDetails,
    RateRegister, RateLockUnlock,
    Supplier
)


class PRNumberService:
    """Service for generating PR numbers"""

    @staticmethod
    def generate_pr_number(comp_id, fin_year_id):
        """
        Generate next PR number for the financial year
        Format: "0001", "0002", etc.

        Matches ASP.NET logic from PR_New_Details.aspx.cs lines 1049-1065
        """
        max_pr = PRMaster.objects.filter(
            comp_id=comp_id,
            fin_year_id=fin_year_id
        ).aggregate(
            max_no=Max(Cast('pr_no', IntegerField()))
        )['max_no']

        next_pr_no = str((max_pr if max_pr else 0) + 1).zfill(4)
        return next_pr_no


class SPRNumberService:
    """Service for generating SPR numbers"""

    @staticmethod
    def generate_spr_number(comp_id, fin_year_id):
        """
        Generate next SPR number for the financial year
        Format: "0001", "0002", etc.
        """
        max_spr = SPRMaster.objects.filter(
            comp_id=comp_id,
            fin_year_id=fin_year_id
        ).aggregate(max_id=Max('spr_id'))['max_id']

        next_spr_id = (max_spr or 0) + 1
        next_spr_no = f'{next_spr_id:04d}'
        return next_spr_no


class PRCreationService:
    """Service for creating Purchase Requisitions"""

    @staticmethod
    @transaction.atomic
    def create_pr_from_temp(comp_id, fin_year_id, session_id, wo_no, temp_items):
        """
        Generate PR from temp items

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            session_id: Session ID
            wo_no: Work Order Number
            temp_items: QuerySet of TempPR items

        Returns:
            tuple: (pr_master, next_pr_no, success_message)

        Matches ASP.NET logic from PR_New_Details.aspx.cs lines 1032-1142
        """
        import datetime as dt_module

        # Generate PR Number
        next_pr_no = PRNumberService.generate_pr_number(comp_id, fin_year_id)

        # Get current date and time
        now = datetime.now()
        sys_date = now.strftime('%d-%m-%Y')  # ASP.NET format
        sys_time = now.strftime('%H:%M:%S')

        # Insert PR Master
        pr_master = PRMaster.objects.create(
            comp_id=comp_id,
            fin_year_id=fin_year_id,
            session_id=session_id,
            pr_no=next_pr_no,
            wo_no=wo_no,
            sys_date=sys_date,
            sys_time=sys_time
        )

        # Move temp items to PR Details
        for temp in temp_items:
            # Format delivery date as string
            if isinstance(temp.del_date, dt_module.date):
                del_date_str = temp.del_date.strftime('%d-%m-%Y')
            else:
                del_date_str = temp.del_date

            # Create PR Detail record
            PRDetails.objects.create(
                m_id=pr_master.pr_id,  # FK to PR Master
                pr_no=next_pr_no,
                item_id=temp.item_id,
                supplier_id=temp.supplier_id,
                qty=temp.qty,
                rate=temp.rate,
                discount=temp.discount,
                del_date=del_date_str,
                ah_id=28  # Default account head ID
            )

        # Delete temp items
        temp_items.delete()

        success_message = f'PR {next_pr_no} generated successfully!'
        return pr_master, next_pr_no, success_message

    @staticmethod
    @transaction.atomic
    def create_pr_bulk(comp_id, fin_year_id, session_id, wo_no, items_data):
        """
        Generate PR directly from bulk item data (no temp table)

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            session_id: Session ID
            wo_no: Work Order Number
            items_data: List of dicts with item_id, supplier_id, qty, rate, discount, del_date

        Returns:
            tuple: (pr_master, next_pr_no, success_message)
        """
        import datetime as dt_module

        # Generate PR Number
        next_pr_no = PRNumberService.generate_pr_number(comp_id, fin_year_id)

        # Get current date and time
        now = datetime.now()
        sys_date = now.strftime('%d-%m-%Y')
        sys_time = now.strftime('%H:%M:%S')

        # Create PR Master
        pr_master = PRMaster.objects.create(
            comp_id=comp_id,
            fin_year_id=fin_year_id,
            session_id=session_id,
            pr_no=next_pr_no,
            wo_no=wo_no,
            sys_date=sys_date,
            sys_time=sys_time
        )

        # Create PR Details for each item
        for item_data in items_data:
            item_id = item_data.get('item_id')
            supplier_id = item_data.get('supplier_id', '')
            qty = Decimal(str(item_data.get('qty', 1)))
            rate = Decimal(str(item_data.get('rate', 0)))
            discount = Decimal(str(item_data.get('discount', 0)))
            delivery_date = item_data.get('del_date')

            # Format delivery date
            if delivery_date:
                try:
                    date_obj = dt_module.datetime.strptime(delivery_date, '%Y-%m-%d')
                    del_date_str = date_obj.strftime('%d-%m-%Y')
                except:
                    del_date_str = delivery_date
            else:
                del_date_str = now.strftime('%d-%m-%Y')

            # Create PR Detail
            PRDetails.objects.create(
                m_id=pr_master.pr_id,
                pr_no=next_pr_no,
                item_id=item_id,
                supplier_id=supplier_id,
                qty=qty,
                rate=rate,
                discount=discount,
                del_date=del_date_str,
                ah_id=28
            )

        success_message = f'PR {next_pr_no} generated successfully with {len(items_data)} item(s)!'
        return pr_master, next_pr_no, success_message


class SPRCreationService:
    """Service for creating Special Purpose Requisitions"""

    @staticmethod
    @transaction.atomic
    def create_spr_from_temp(comp_id, fin_year_id, session_id, dept_id, wo_no, temp_items):
        """
        Generate SPR from temp items stored in session

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            session_id: Session ID
            dept_id: Department ID
            wo_no: Work Order Number (optional)
            temp_items: List of dicts with item data

        Returns:
            tuple: (spr_master, next_spr_no, success_message)
        """
        import datetime as dt_module

        # Generate SPR Number
        next_spr_no = SPRNumberService.generate_spr_number(comp_id, fin_year_id)

        # Create SPR Master
        now = datetime.now()
        spr_master = SPRMaster.objects.create(
            spr_no=next_spr_no,
            comp_id=comp_id,
            fin_year_id=fin_year_id,
            session_id=session_id,
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S'),
            checked=0,
            approve=0,
            authorize=0
        )

        # Process each temp item
        for temp_item in temp_items:
            item_id = temp_item.get('item_id')
            qty = Decimal(str(temp_item.get('qty', 1)))
            supplier_input = temp_item.get('supplier', '')
            rate = Decimal(str(temp_item.get('rate', 0)))
            discount = Decimal(str(temp_item.get('discount', 0)))
            delivery_date = temp_item.get('del_date')
            ah_id = temp_item.get('ah_id')
            remarks = temp_item.get('remarks', '')

            # Extract supplier ID
            supplier_id = SupplierService.extract_supplier_id(supplier_input, comp_id)

            # Format delivery date
            if delivery_date:
                try:
                    date_obj = dt_module.datetime.strptime(delivery_date, '%Y-%m-%d')
                    del_date_str = date_obj.strftime('%d-%m-%Y')
                except:
                    del_date_str = delivery_date
            else:
                del_date_str = now.strftime('%d-%m-%Y')

            # Create SPR Detail
            SPRDetails.objects.create(
                m_id=spr_master.spr_id,
                spr_no=next_spr_no,
                item_id=item_id,
                supplier_id=supplier_id,
                qty=qty,
                rate=rate,
                discount=discount,
                del_date=del_date_str,
                ah_id=ah_id,
                wo_no=wo_no if wo_no else '',
                dept_id=int(dept_id) if dept_id and int(dept_id) > 0 else 0,
                remarks=remarks
            )

        success_message = f'SPR {next_spr_no} generated successfully with {len(temp_items)} item(s)!'
        return spr_master, next_spr_no, success_message

    @staticmethod
    @transaction.atomic
    def create_spr_bulk(comp_id, fin_year_id, session_id, dept_id, wo_no, items_data):
        """
        Generate SPR directly from bulk item data (no temp table)

        Args:
            comp_id: Company ID
            fin_year_id: Financial Year ID
            session_id: Session ID
            dept_id: Department ID
            wo_no: Work Order Number (optional)
            items_data: List of dicts with item data

        Returns:
            tuple: (spr_master, next_spr_no, success_message)
        """
        import datetime as dt_module

        # Generate SPR Number
        next_spr_no = SPRNumberService.generate_spr_number(comp_id, fin_year_id)

        # Create SPR Master
        now = datetime.now()
        spr_master = SPRMaster.objects.create(
            spr_no=next_spr_no,
            comp_id=comp_id,
            fin_year_id=fin_year_id,
            session_id=session_id,
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S'),
            checked=0,
            approve=0,
            authorize=0
        )

        # Process each item
        for item_data in items_data:
            item_id = item_data.get('item_id')
            qty = float(item_data.get('qty', 1))
            supplier_input = item_data.get('supplier')
            rate = float(item_data.get('rate', 0))
            discount = float(item_data.get('discount', 0))
            delivery_date = item_data.get('delivery_date')
            ah_id = item_data.get('ah_id')
            remarks = item_data.get('remarks', '')

            # Extract supplier ID
            supplier_id = SupplierService.extract_supplier_id(supplier_input, comp_id)

            # Format delivery date
            if delivery_date:
                try:
                    date_obj = dt_module.datetime.strptime(delivery_date, '%Y-%m-%d')
                    del_date_str = date_obj.strftime('%d-%m-%Y')
                except:
                    del_date_str = delivery_date
            else:
                del_date_str = now.strftime('%d-%m-%Y')

            # Create SPR Detail
            SPRDetails.objects.create(
                m_id=spr_master.spr_id,
                spr_no=next_spr_no,
                item_id=item_id,
                supplier_id=supplier_id,
                qty=Decimal(str(qty)),
                rate=Decimal(str(rate)),
                discount=Decimal(str(discount)),
                del_date=del_date_str,
                ah_id=ah_id,
                wo_no=wo_no if wo_no else '',
                dept_id=int(dept_id) if dept_id and int(dept_id) > 0 else 0,
                remarks=remarks
            )

        success_message = f'SPR {next_spr_no} generated successfully with {len(items_data)} item(s)!'
        return spr_master, next_spr_no, success_message


class ApprovalWorkflowService:
    """Service for PR/SPR/PO approval workflows"""

    @staticmethod
    def check_pr(pr_id, checked_by_user_id):
        """Mark PR as checked"""
        pr = PRMaster.objects.get(pr_id=pr_id)
        pr.checked = 1
        pr.checked_by = checked_by_user_id
        pr.checked_date = datetime.now().strftime('%d-%m-%Y')
        pr.save()
        return pr

    @staticmethod
    def approve_pr(pr_id, approved_by_user_id):
        """Mark PR as approved"""
        pr = PRMaster.objects.get(pr_id=pr_id)
        pr.approve = 1
        pr.approved_by = approved_by_user_id
        pr.approved_date = datetime.now().strftime('%d-%m-%Y')
        pr.save()
        return pr

    @staticmethod
    def authorize_pr(pr_id, authorized_by_user_id):
        """Mark PR as authorized"""
        pr = PRMaster.objects.get(pr_id=pr_id)
        pr.authorize = 1
        pr.authorized_by = authorized_by_user_id
        pr.authorized_date = datetime.now().strftime('%d-%m-%Y')
        pr.save()
        return pr

    @staticmethod
    def check_spr(spr_id, checked_by_user_id):
        """Mark SPR as checked"""
        spr = SPRMaster.objects.get(spr_id=spr_id)
        spr.checked = 1
        spr.checked_by = checked_by_user_id
        spr.checked_date = datetime.now().strftime('%d-%m-%Y')
        spr.save()
        return spr

    @staticmethod
    def approve_spr(spr_id, approved_by_user_id):
        """Mark SPR as approved"""
        spr = SPRMaster.objects.get(spr_id=spr_id)
        spr.approve = 1
        spr.approved_by = approved_by_user_id
        spr.approved_date = datetime.now().strftime('%d-%m-%Y')
        spr.save()
        return spr

    @staticmethod
    def authorize_spr(spr_id, authorized_by_user_id):
        """Mark SPR as authorized"""
        spr = SPRMaster.objects.get(spr_id=spr_id)
        spr.authorize = 1
        spr.authorized_by = authorized_by_user_id
        spr.authorized_date = datetime.now().strftime('%d-%m-%Y')
        spr.save()
        return spr


class RateLockService:
    """Service for rate locking/unlocking operations"""

    @staticmethod
    def lock_item_rate(item_id, comp_id, lock_type, user_id):
        """
        Lock an item's rate

        Args:
            item_id: Item ID
            comp_id: Company ID
            lock_type: Lock type (e.g., 'Manual', 'Auto')
            user_id: User performing the action

        Returns:
            RateLockUnlock instance
        """
        now = datetime.now()

        lock_record = RateLockUnlock.objects.create(
            item_id=item_id,
            comp_id=comp_id,
            lock_unlock=1,  # 1 = Locked
            type=lock_type,
            session_id=str(user_id),
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S')
        )

        return lock_record

    @staticmethod
    def unlock_item_rate(item_id, comp_id, lock_type, user_id):
        """
        Unlock an item's rate

        Args:
            item_id: Item ID
            comp_id: Company ID
            lock_type: Lock type (e.g., 'Manual', 'Auto')
            user_id: User performing the action

        Returns:
            RateLockUnlock instance
        """
        now = datetime.now()

        unlock_record = RateLockUnlock.objects.create(
            item_id=item_id,
            comp_id=comp_id,
            lock_unlock=0,  # 0 = Unlocked
            type=lock_type,
            session_id=str(user_id),
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S')
        )

        return unlock_record

    @staticmethod
    def get_item_lock_status(item_id, comp_id):
        """
        Get current lock status of an item

        Returns:
            dict: {'is_locked': bool, 'lock_type': str, 'lock_id': int}
        """
        latest_lock = RateLockUnlock.objects.filter(
            item_id=item_id,
            comp_id=comp_id
        ).order_by('-id').first()

        if not latest_lock:
            return {'is_locked': False, 'lock_type': None, 'lock_id': None}

        return {
            'is_locked': latest_lock.lock_unlock == 1,
            'lock_type': latest_lock.type,
            'lock_id': latest_lock.id
        }


class SupplierService:
    """Service for supplier-related operations"""

    @staticmethod
    def extract_supplier_id(supplier_input, comp_id):
        """
        Extract supplier ID from various input formats

        Args:
            supplier_input: Can be supplier name, "ID - Name", or just ID
            comp_id: Company ID

        Returns:
            str: Supplier ID
        """
        if not supplier_input:
            return ''

        try:
            # Try to find by exact name match
            supplier = Supplier.objects.filter(
                supplier_name=supplier_input,
                comp_id=comp_id
            ).first()

            if supplier:
                return supplier.supplier_id
            else:
                # Parse "ID - Name" format
                if ' - ' in supplier_input:
                    return supplier_input.split(' - ')[0].strip()
                else:
                    return supplier_input
        except:
            # Fallback parsing
            if ' - ' in supplier_input:
                return supplier_input.split(' - ')[0].strip()
            else:
                return supplier_input


class RateRegisterService:
    """Service for rate register operations"""

    @staticmethod
    def get_min_rate_for_item(item_id, comp_id):
        """
        Get minimum historical rate (after discount) for an item

        Returns:
            Decimal or None
        """
        min_rate = RateRegister.objects.filter(
            item_id=item_id,
            comp_id=comp_id
        ).aggregate(
            min_rate=F('rate') - (F('rate') * F('discount') / 100)
        )['min_rate']

        return min_rate

    @staticmethod
    def add_rate_to_register(item_id, supplier_id, comp_id, qty, rate, discount, po_no=''):
        """
        Add a new entry to the rate register

        Args:
            item_id: Item ID
            supplier_id: Supplier ID
            comp_id: Company ID
            qty: Quantity
            rate: Rate
            discount: Discount percentage
            po_no: PO Number (optional)

        Returns:
            RateRegister instance
        """
        now = datetime.now()

        rate_entry = RateRegister.objects.create(
            item_id=item_id,
            supplier_id=supplier_id,
            comp_id=comp_id,
            qty=qty,
            rate=rate,
            discount=discount,
            po_no=po_no,
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S')
        )

        return rate_entry
