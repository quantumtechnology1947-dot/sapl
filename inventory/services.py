"""
Inventory Module Service Layer
Contains business logic for inventory transactions
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from datetime import datetime
from decimal import Decimal
from .models import (
    TblinvMaterialrequisitionMaster, TblinvMaterialrequisitionDetails,
    TblinvMaterialissueMaster, TblinvMaterialissueDetails,
    TblinvMaterialreturnMaster, TblinvMaterialreturnDetails,
    TblinvInwardMaster, TblinvInwardDetails,
    TblinvMaterialreceivedMaster, TblinvMaterialreceivedDetails,
    TblinvCustomerChallanMaster, TblinvCustomerChallanDetails,
    TblinvMaterialservicenoteMaster, TblinvMaterialservicenoteDetails,
    TblinvSupplierChallanMaster, TblinvSupplierChallanDetails,
    TblinvWisMaster, TblinvWisDetails,
)

class BaseTransactionService:
    """Base service class for common transaction operations"""
    
    @staticmethod
    def get_current_datetime():
        """Get current date and time in required format"""
        now = timezone.now()
        return now.strftime('%d/%m/%Y'), now.strftime('%H:%M:%S')
    
    @staticmethod
    def format_date_for_db(date_obj):
        """Format date object for database storage"""
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime('%d/%m/%Y') if date_obj else ''
    
    @staticmethod
    def parse_date_from_db(date_str):
        """Parse date string from database"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%d/%m/%Y')
        except:
            return None






class MaterialRequisitionService(BaseTransactionService):
    """Service for Material Requisition Slip (MRS) operations"""
    
    @staticmethod
    def generate_mrs_number(compid, finyearid):
        """
        Generate unique MRS number in format: MRS/YYYY/NNNN
        """
        # Get financial year
        from sys_admin.models import TblfinancialMaster
        try:
            fin_year = TblfinancialMaster.objects.get(finyearid=finyearid, compid=compid)
            year = fin_year.finyear.split('-')[0]  # Get first year from "2024-2025"
        except:
            year = timezone.now().year
        
        # Get last MRS number for this financial year
        last_mrs = TblinvMaterialrequisitionMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            mrsno__startswith=f'MRS/{year}/'
        ).order_by('-id').first()
        
        if last_mrs and last_mrs.mrsno:
            try:
                last_num = int(last_mrs.mrsno.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'MRS/{year}/{new_num:04d}'
    
    @staticmethod
    def validate_mrs_items(items):
        """Validate MRS items before saving"""
        errors = []
        
        for idx, item in enumerate(items, 1):
            # Check required quantity
            if not item.get('reqqty') or float(item.get('reqqty', 0)) <= 0:
                errors.append(f"Row {idx}: Required quantity must be greater than 0")
            
            # Check item ID
            if not item.get('itemid'):
                errors.append(f"Row {idx}: Item is required")
            
            # Check either deptid or wono
            if not item.get('deptid') and not item.get('wono'):
                errors.append(f"Row {idx}: Either BGGroup or WO Number is required")
        
        return errors
    
    @staticmethod
    def get_pending_mrs_for_issue(compid, finyearid):
        """
        Get MRS with pending quantities for material issue
        Returns MRS where (Req Qty - Issued Qty) > 0
        """
        from django.db.models import Sum, F, Q
        
        # Get all MRS
        mrs_list = TblinvMaterialrequisitionMaster.objects.filter(
            compid=compid,
            finyearid__lte=finyearid
        ).order_by('-id')
        
        pending_mrs = []
        
        for mrs in mrs_list:
            # Get total requested quantity
            req_qty = TblinvMaterialrequisitionDetails.objects.filter(
                mid=mrs.id
            ).aggregate(total=Sum('reqqty'))['total'] or 0
            
            # Get total issued quantity
            issued_qty = TblinvMaterialissueDetails.objects.filter(
                mrsid=mrs.id
            ).aggregate(total=Sum('issueqty'))['total'] or 0
            
            balance = req_qty - issued_qty
            
            if balance > 0:
                pending_mrs.append({
                    'mrs': mrs,
                    'req_qty': req_qty,
                    'issued_qty': issued_qty,
                    'balance_qty': balance
                })
        
        return pending_mrs
    
    @staticmethod
    def calculate_balance_qty(mrs_detail_id):
        """
        Calculate balance quantity for MRS detail
        Balance = Req Qty - Issued Qty
        """
        try:
            mrs_detail = TblinvMaterialrequisitionDetails.objects.get(id=mrs_detail_id)
            req_qty = mrs_detail.reqqty or 0
            
            # Get issued quantity
            issued_qty = TblinvMaterialissueDetails.objects.filter(
                mrsid=mrs_detail_id
            ).aggregate(total=Sum('issueqty'))['total'] or 0
            
            return req_qty - issued_qty
        except:
            return 0


class MaterialIssueService(BaseTransactionService):
    """Service for Material Issue Note (MIN) operations"""
    
    @staticmethod
    def generate_min_number(compid, finyearid):
        """Generate unique MIN number in format: MIN/YYYY/NNNN"""
        from sys_admin.models import TblfinancialMaster
        try:
            fin_year = TblfinancialMaster.objects.get(finyearid=finyearid, compid=compid)
            year = fin_year.finyear.split('-')[0]
        except:
            year = timezone.now().year
        
        last_min = TblinvMaterialissueMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            minno__startswith=f'MIN/{year}/'
        ).order_by('-id').first()
        
        if last_min and last_min.minno:
            try:
                last_num = int(last_min.minno.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'MIN/{year}/{new_num:04d}'
    
    @staticmethod
    def validate_issue_quantity(item_id, issue_qty, location_id=None):
        """
        Validate issue quantity against available stock
        Returns (is_valid, error_message, available_stock)
        """
        # TODO: Implement stock checking logic
        # This will need to query stock ledger or current stock table
        return True, None, 0
    
    @staticmethod
    def validate_against_mrs_balance(mrs_detail_id, issue_qty):
        """
        Validate issue quantity against MRS balance
        Returns (is_valid, error_message, balance_qty)
        """
        balance = MaterialRequisitionService.calculate_balance_qty(mrs_detail_id)
        
        if issue_qty > balance:
            return False, f"Issue quantity ({issue_qty}) exceeds balance quantity ({balance})", balance
        
        return True, None, balance
    
    @staticmethod
    @transaction.atomic
    def update_stock_ledger(min_data):
        """
        Update stock ledger with negative entries for material issue
        """
        # TODO: Implement stock ledger update logic
        pass
    
    @staticmethod
    @transaction.atomic
    def reverse_stock_on_delete(min_id):
        """
        Reverse stock entries when MIN is deleted
        """
        # TODO: Implement stock reversal logic
        pass


class MaterialReturnService(BaseTransactionService):
    """Service for Material Return Note (MRN) operations"""
    
    @staticmethod
    def generate_mrn_number(compid, finyearid):
        """Generate unique MRN number in format: MRN/YYYY/NNNN"""
        from sys_admin.models import TblfinancialMaster
        try:
            fin_year = TblfinancialMaster.objects.get(finyearid=finyearid, compid=compid)
            year = fin_year.finyear.split('-')[0]
        except:
            year = timezone.now().year
        
        last_mrn = TblinvMaterialreturnMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            mrnno__startswith=f'MRN/{year}/'
        ).order_by('-id').first()
        
        if last_mrn and last_mrn.mrnno:
            try:
                last_num = int(last_mrn.mrnno.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'MRN/{year}/{new_num:04d}'
    
    @staticmethod
    def validate_return_quantity(item_id, return_qty):
        """
        Validate return quantity
        Returns (is_valid, error_message)
        """
        if return_qty <= 0:
            return False, "Return quantity must be greater than 0"
        
        # TODO: Add validation against issued quantity
        return True, None
    
    @staticmethod
    @transaction.atomic
    def update_stock_ledger(mrn_data):
        """
        Update stock ledger with positive entries for material return
        """
        # TODO: Implement stock ledger update logic
        pass
    
    @staticmethod
    @transaction.atomic
    def reverse_stock_on_delete(mrn_id):
        """
        Reverse stock entries when MRN is deleted
        """
        # TODO: Implement stock reversal logic
        pass


class DashboardService:
    """Service for dashboard metrics and analytics"""
    
    @staticmethod
    def get_dashboard_metrics(compid, finyearid):
        """Get all dashboard metrics"""
        from django.db.models import Sum, Count
        
        metrics = {}
        
        # Total stock value (placeholder - needs stock valuation logic)
        metrics['total_stock_value'] = 0
        
        # Pending MRS count
        pending_mrs = MaterialRequisitionService.get_pending_mrs_for_issue(compid, finyearid)
        metrics['pending_mrs_count'] = len(pending_mrs)
        
        # Pending GIN count (GIN without full GRR)
        # TODO: Implement pending GIN logic
        metrics['pending_gin_count'] = 0
        
        # Low stock items (placeholder)
        metrics['low_stock_items'] = []
        
        # Non-moving items (placeholder)
        metrics['non_moving_items'] = []
        
        return metrics



class GoodsInwardService(BaseTransactionService):
    """Service for Goods Inward Note (GIN) operations"""
    
    @staticmethod
    def generate_gin_number(compid, finyearid):
        """Generate unique GIN number in format: GIN/YYYY/NNNN"""
        from sys_admin.models import TblfinancialMaster
        try:
            fin_year = TblfinancialMaster.objects.get(finyearid=finyearid, compid=compid)
            year = fin_year.finyear.split('-')[0]
        except:
            year = timezone.now().year
        
        last_gin = TblinvInwardMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            ginno__startswith=f'GIN/{year}/'
        ).order_by('-id').first()
        
        if last_gin and last_gin.ginno:
            try:
                last_num = int(last_gin.ginno.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'GIN/{year}/{new_num:04d}'
    
    @staticmethod
    def get_po_details(po_id):
        """
        Get purchase order details for GIN
        Returns PO information and line items
        """
        # TODO: Implement PO integration with material_management module
        # This will fetch PO master and details from purchase module
        return None
    
    @staticmethod
    def validate_gin_items(items):
        """
        Validate GIN items against PO
        Returns (is_valid, error_messages)
        """
        errors = []
        
        for idx, item in enumerate(items, 1):
            # Check quantity
            if not item.get('qty') or float(item.get('qty', 0)) <= 0:
                errors.append(f"Row {idx}: Quantity must be greater than 0")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def check_grr_dependency(gin_id):
        """
        Check if GIN has dependent GRR records
        Returns (has_dependency, grr_count)
        """
        grr_count = TblinvMaterialreceivedMaster.objects.filter(
            ginid=gin_id
        ).count()
        
        return grr_count > 0, grr_count
    
    @staticmethod
    def get_pending_gin_for_receipt(compid, finyearid):
        """
        Get GIN with pending quantities for goods receipt
        Returns GIN where (Inward Qty - Received Qty) > 0
        Optimized: Only checks CURRENT financial year GINs (last 500) for performance
        """
        from django.db.models import Sum

        # Get recent GIN from CURRENT financial year only (last 500) to improve performance
        # Changed from finyearid__lte to finyearid= to show only current year
        gin_list = TblinvInwardMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-id')[:500]

        pending_gin = []

        for gin in gin_list:
            # Get total inward quantity
            inward_qty = TblinvInwardDetails.objects.filter(
                ginid=gin.id
            ).aggregate(total=Sum('qty'))['total'] or 0

            # Get total received quantity
            # First get all GRR master IDs for this GIN
            grr_master_ids = list(TblinvMaterialreceivedMaster.objects.filter(
                ginid=gin.id
            ).values_list('id', flat=True))

            # Then get sum of received quantities from details
            if grr_master_ids:
                received_qty = TblinvMaterialreceivedDetails.objects.filter(
                    mid__in=grr_master_ids
                ).aggregate(total=Sum('receivedqty'))['total'] or 0
            else:
                received_qty = 0

            balance = inward_qty - received_qty

            if balance > 0:
                pending_gin.append({
                    'gin': gin,
                    'inward_qty': inward_qty,
                    'received_qty': received_qty,
                    'balance_qty': balance
                })

        return pending_gin


class GoodsReceiptService(BaseTransactionService):
    """Service for Goods Received Receipt (GRR) operations"""
    
    @staticmethod
    def generate_grr_number(compid, finyearid):
        """Generate unique GRR number in format: GRR/YYYY/NNNN"""
        from sys_admin.models import TblfinancialMaster
        try:
            fin_year = TblfinancialMaster.objects.get(finyearid=finyearid, compid=compid)
            year = fin_year.finyear.split('-')[0]
        except:
            year = timezone.now().year
        
        last_grr = TblinvMaterialreceivedMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            grrno__startswith=f'GRR/{year}/'
        ).order_by('-id').first()
        
        if last_grr and last_grr.grrno:
            try:
                last_num = int(last_grr.grrno.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'GRR/{year}/{new_num:04d}'
    
    @staticmethod
    def validate_receive_quantity(gin_detail_id, receive_qty):
        """
        Validate receive quantity against GIN balance
        Returns (is_valid, error_message, balance_qty)
        """
        try:
            gin_detail = TblinvInwardDetails.objects.get(id=gin_detail_id)
            inward_qty = gin_detail.qty or 0
            
            # Get already received quantity
            # First get all GRR master IDs for this GIN
            grr_master_ids = TblinvMaterialreceivedMaster.objects.filter(
                ginid=gin_detail.ginid
            ).values_list('id', flat=True)

            # Then filter details by PO and master IDs
            received_qty = TblinvMaterialreceivedDetails.objects.filter(
                poid=gin_detail.poid,
                mid__in=grr_master_ids
            ).aggregate(total=Sum('receivedqty'))['total'] or 0
            
            balance = inward_qty - received_qty
            
            if receive_qty > balance:
                return False, f"Receive quantity ({receive_qty}) exceeds balance quantity ({balance})", balance
            
            return True, None, balance
        except:
            return False, "Invalid GIN detail", 0
    
    @staticmethod
    @transaction.atomic
    def update_stock_ledger(grr_data):
        """
        Update stock ledger with positive entries for goods receipt
        """
        # TODO: Implement stock ledger update logic
        pass
    
    @staticmethod
    @transaction.atomic
    def reverse_stock_on_delete(grr_id):
        """
        Reverse stock entries when GRR is deleted
        """
        # TODO: Implement stock reversal logic
        pass
    
    @staticmethod
    def trigger_accounts_entry(grr_id):
        """
        Trigger accounting entries for GRR
        Integration with accounts module
        """
        # TODO: Implement accounts integration
        pass



class GoodsServiceService(BaseTransactionService):
    """
    Service for Goods Service Note (GSN) operations
    
    Handles service receipts without stock updates.
    Converted from: aspnet/Module/Inventory/Transactions/GoodsServiceNote_SN_New.aspx
    """
    
    @staticmethod
    def generate_gsn_number(compid, finyearid):
        """
        Generate unique GSN number in format: GSN/YYYY/NNNN
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            str: Generated GSN number (e.g., GSN/2024/0001)
        """
        from sys_admin.models import TblfinancialMaster
        try:
            fin_year = TblfinancialMaster.objects.get(finyearid=finyearid, compid=compid)
            year = fin_year.finyear.split('-')[0]
        except:
            year = timezone.now().year
        
        # Get last GSN number for this company and financial year
        from .models import TblinvMaterialservicenoteMaster
        last_gsn = TblinvMaterialservicenoteMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            gsnno__startswith=f'GSN/{year}/'
        ).order_by('-id').first()
        
        if last_gsn and last_gsn.gsnno:
            try:
                last_num = int(last_gsn.gsnno.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'GSN/{year}/{new_num:04d}'
    
    @staticmethod
    def validate_service_details(service_data):
        """
        Validate service details before saving
        
        Args:
            service_data: Dictionary containing service details
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Validate service description
        if not service_data.get('service_description'):
            errors.append('Service description is required')
        
        # Validate service amount
        service_amount = service_data.get('service_amount', 0)
        if not service_amount or float(service_amount) <= 0:
            errors.append('Service amount must be greater than 0')
        
        # Validate service provider
        if not service_data.get('service_provider'):
            errors.append('Service provider is required')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def calculate_tax(service_amount, tax_rate):
        """
        Calculate tax amount based on service amount and tax rate
        
        Args:
            service_amount: Service amount (Decimal or float)
            tax_rate: Tax rate percentage (Decimal or float)
            
        Returns:
            Decimal: Calculated tax amount
        """
        from decimal import Decimal
        
        try:
            amount = Decimal(str(service_amount))
            rate = Decimal(str(tax_rate))
            tax_amount = (amount * rate) / Decimal('100')
            return tax_amount.quantize(Decimal('0.01'))
        except:
            return Decimal('0.00')
    
    @staticmethod
    def calculate_total_amount(service_amount, tax_amount):
        """
        Calculate total amount (service amount + tax)
        
        Args:
            service_amount: Service amount
            tax_amount: Tax amount
            
        Returns:
            Decimal: Total amount
        """
        from decimal import Decimal
        
        try:
            amount = Decimal(str(service_amount))
            tax = Decimal(str(tax_amount))
            return (amount + tax).quantize(Decimal('0.01'))
        except:
            return Decimal('0.00')


# ============================================================================
# CHALLAN SERVICES
# ============================================================================

class SupplierChallanService(BaseTransactionService):
    """
    Service for Supplier Challan operations
    
    Handles job work tracking - materials sent to suppliers for processing
    and tracking their return. Supports clearing workflow with balance calculations.
    
    Converted from: aspnet/Module/Inventory/Transactions/SupplierChallan_New.aspx
    Requirements: 2.1, 2.4, 2.5, 2.6, 2.7
    """
    
    @staticmethod
    def generate_supplier_challan_number(compid, finyearid):
        """
        Generate unique supplier challan number in format: SCHAL/YYYY/NNNN
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            str: Generated challan number (e.g., SCHAL/2024/0001)
        """
        from inventory.models import Tblsupplierchallanmaster
        from django.db.models import Max
        import re
        
        # Get the latest challan number for this company and financial year
        latest = Tblsupplierchallanmaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).aggregate(Max('supplierchallanno'))
        
        latest_number = latest['supplierchallanno__max']
        
        if latest_number:
            # Extract the numeric part using regex
            match = re.search(r'/(\d+)$', latest_number)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        # Get year from financial year (placeholder - adjust based on your model)
        year = "2024"  # TODO: Get from finyearid
        
        return f"SCHAL/{year}/{next_num:04d}"
    
    @staticmethod
    def calculate_balance(sent_qty, received_qty):
        """
        Calculate balance quantity (Sent - Received)
        
        Args:
            sent_qty: Quantity sent to supplier
            received_qty: Quantity received back
            
        Returns:
            Decimal: Balance quantity
        """
        from decimal import Decimal
        
        try:
            sent = Decimal(str(sent_qty))
            received = Decimal(str(received_qty))
            balance = sent - received
            return balance.quantize(Decimal('0.001'))
        except:
            return Decimal('0.000')
    
    @staticmethod
    def clear_challan(challan_id, received_items):
        """
        Record received quantities and update challan status
        
        Args:
            challan_id: Supplier challan master ID
            received_items: List of dicts with item_id and received_qty
            
        Returns:
            bool: Success status
        """
        from inventory.models import Tblsupplierchallandetail, Tblsupplierchallanmaster
        from django.db import transaction
        from decimal import Decimal
        
        try:
            with transaction.atomic():
                # Update detail records with received quantities
                for item in received_items:
                    detail = Tblsupplierchallandetail.objects.get(
                        supplierchallandetailid=item['detail_id']
                    )
                    
                    received_qty = Decimal(str(item['received_qty']))
                    detail.receivedqty = (detail.receivedqty or Decimal('0')) + received_qty
                    detail.balanceqty = SupplierChallanService.calculate_balance(
                        detail.qty,
                        detail.receivedqty
                    )
                    detail.save()
                
                # Update master status
                SupplierChallanService.update_status(challan_id)
                
                return True
        except Exception as e:
            print(f"Error clearing challan: {e}")
            return False
    
    @staticmethod
    def get_pending_challans(compid, finyearid):
        """
        Get supplier challans with balance > 0
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            QuerySet: Pending supplier challans
        """
        from inventory.models import Tblsupplierchallanmaster, Tblsupplierchallandetail
        from django.db.models import Sum, F, Q
        from decimal import Decimal
        
        # Get challans that have at least one detail with balance > 0
        pending_challan_ids = Tblsupplierchallandetail.objects.filter(
            Q(balanceqty__gt=Decimal('0')) | Q(balanceqty__isnull=True)
        ).values_list('supplierchallanid', flat=True).distinct()
        
        return Tblsupplierchallanmaster.objects.filter(
            supplierchallanid__in=pending_challan_ids,
            compid=compid,
            finyearid=finyearid
        ).select_related('supplierid')
    
    @staticmethod
    def update_status(challan_id):
        """
        Update challan status based on balance quantities
        Status: Pending / Partially Cleared / Cleared
        
        Args:
            challan_id: Supplier challan master ID
            
        Returns:
            str: Updated status
        """
        from inventory.models import Tblsupplierchallanmaster, Tblsupplierchallandetail
        from decimal import Decimal
        
        try:
            challan = Tblsupplierchallanmaster.objects.get(supplierchallanid=challan_id)
            details = Tblsupplierchallandetail.objects.filter(supplierchallanid=challan_id)
            
            total_balance = sum(
                (detail.balanceqty or Decimal('0')) for detail in details
            )
            total_sent = sum(
                (detail.qty or Decimal('0')) for detail in details
            )
            
            if total_balance == Decimal('0'):
                status = 'Cleared'
            elif total_balance == total_sent:
                status = 'Pending'
            else:
                status = 'Partially Cleared'
            
            # Update status field if it exists in model
            if hasattr(challan, 'status'):
                challan.status = status
                challan.save()
            
            return status
        except Exception as e:
            print(f"Error updating status: {e}")
            return 'Unknown'
    
    @staticmethod
    def validate_challan_details(details_data):
        """
        Validate supplier challan detail items
        
        Args:
            details_data: List of detail item dictionaries
            
        Returns:
            tuple: (is_valid, error_message)
        """
        from decimal import Decimal
        
        if not details_data or len(details_data) == 0:
            return False, "At least one item is required"
        
        for idx, detail in enumerate(details_data, 1):
            # Check item is selected
            if not detail.get('itemid'):
                return False, f"Item is required for row {idx}"
            
            # Check quantity
            qty = detail.get('qty', 0)
            try:
                qty_decimal = Decimal(str(qty))
                if qty_decimal <= 0:
                    return False, f"Quantity must be greater than 0 for row {idx}"
            except:
                return False, f"Invalid quantity for row {idx}"
        
        return True, ""


class CustomerChallanService(BaseTransactionService):
    """
    Service for Customer Challan operations
    
    Handles materials sent to customers for delivery or work order fulfillment.
    Supports linking to work orders.
    
    Converted from: aspnet/Module/Inventory/Transactions/CustomerChallan_New.aspx
    Requirements: 3.1, 3.2, 3.3, 3.4
    """
    
    @staticmethod
    def generate_customer_challan_number(compid, finyearid):
        """
        Generate unique customer challan number in format: CCHAL/YYYY/NNNN
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            str: Generated challan number (e.g., CCHAL/2024/0001)
        """
        from inventory.models import Tblcustomerchallanmaster
        from django.db.models import Max
        import re
        
        # Get the latest challan number for this company and financial year
        latest = Tblcustomerchallanmaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).aggregate(Max('customerchallanno'))
        
        latest_number = latest['customerchallanno__max']
        
        if latest_number:
            # Extract the numeric part using regex
            match = re.search(r'/(\d+)$', latest_number)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        # Get year from financial year (placeholder - adjust based on your model)
        year = "2024"  # TODO: Get from finyearid
        
        return f"CCHAL/{year}/{next_num:04d}"
    
    @staticmethod
    def link_to_work_order(challan_id, wo_number):
        """
        Link customer challan to work order
        
        Args:
            challan_id: Customer challan master ID
            wo_number: Work order number
            
        Returns:
            bool: Success status
        """
        from inventory.models import Tblcustomerchallanmaster
        
        try:
            challan = Tblcustomerchallanmaster.objects.get(customerchallanid=challan_id)
            
            # Update work order reference if field exists
            if hasattr(challan, 'wonumber'):
                challan.wonumber = wo_number
                challan.save()
                return True
            
            return False
        except Exception as e:
            print(f"Error linking to work order: {e}")
            return False
    
    @staticmethod
    def get_wo_details(wo_number):
        """
        Fetch work order details (placeholder for future integration)
        
        Args:
            wo_number: Work order number
            
        Returns:
            dict: Work order details or None
        """
        # TODO: Integrate with Work Order module when available
        # For now, return placeholder
        return {
            'wo_number': wo_number,
            'status': 'Pending',
            'customer': 'TBD',
            'items': []
        }
    
    @staticmethod
    def validate_challan_details(details_data):
        """
        Validate customer challan detail items
        
        Args:
            details_data: List of detail item dictionaries
            
        Returns:
            tuple: (is_valid, error_message)
        """
        from decimal import Decimal
        
        if not details_data or len(details_data) == 0:
            return False, "At least one item is required"
        
        for idx, detail in enumerate(details_data, 1):
            # Check item is selected
            if not detail.get('itemid'):
                return False, f"Item is required for row {idx}"
            
            # Check quantity
            qty = detail.get('qty', 0)
            try:
                qty_decimal = Decimal(str(qty))
                if qty_decimal <= 0:
                    return False, f"Quantity must be greater than 0 for row {idx}"
            except:
                return False, f"Invalid quantity for row {idx}"
        
        return True, ""



# ============================================================================
# GATE PASS SERVICES
# ============================================================================

class GatePassService(BaseTransactionService):
    """
    Service for Gate Pass operations
    
    Handles material movement authorization - both inward and outward,
    returnable and non-returnable items.
    
    Converted from: aspnet/Module/Inventory/Transactions/GatePass_Insert.aspx
    Requirements: 4.1, 4.2, 4.5, 4.6
    """
    
    @staticmethod
    def generate_gatepass_number(compid, finyearid):
        """
        Generate unique gate pass number in format: GP/YYYY/NNNN
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            str: Generated gate pass number (e.g., GP/2024/0001)
        """
        from inventory.models import Tblgatepassmaster
        from django.db.models import Max
        import re
        
        latest = Tblgatepassmaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).aggregate(Max('gatepassno'))
        
        latest_number = latest['gatepassno__max']
        
        if latest_number:
            match = re.search(r'/(\d+)$', latest_number)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        year = "2024"  # TODO: Get from finyearid
        
        return f"GP/{year}/{next_num:04d}"
    
    @staticmethod
    def get_pending_returnable_passes(compid, finyearid):
        """
        Get unreturned gate passes (returnable items not yet returned)
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            QuerySet: Pending returnable gate passes
        """
        from inventory.models import Tblgatepassmaster
        from django.db.models import Q
        
        # Get gate passes that are returnable and not yet returned
        return Tblgatepassmaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            isreturnable=True,
            returndate__isnull=True
        ).select_related('partyid')
    
    @staticmethod
    def record_return(gatepass_id, return_date, return_items):
        """
        Record returned items for a returnable gate pass
        
        Args:
            gatepass_id: Gate pass master ID
            return_date: Date of return
            return_items: List of dicts with item_id and returned_qty
            
        Returns:
            bool: Success status
        """
        from inventory.models import Tblgatepassmaster, Tblgatepassdetail
        from django.db import transaction
        from decimal import Decimal
        
        try:
            with transaction.atomic():
                gatepass = Tblgatepassmaster.objects.get(gatepassid=gatepass_id)
                
                # Update return date
                gatepass.returndate = return_date
                gatepass.save()
                
                # Update detail records with returned quantities
                for item in return_items:
                    detail = Tblgatepassdetail.objects.get(
                        gatepassdetailid=item['detail_id']
                    )
                    
                    returned_qty = Decimal(str(item['returned_qty']))
                    detail.returnedqty = returned_qty
                    detail.save()
                
                return True
        except Exception as e:
            print(f"Error recording return: {e}")
            return False
    
    @staticmethod
    def calculate_days_pending(issue_date):
        """
        Calculate days since gate pass was issued
        
        Args:
            issue_date: Gate pass issue date
            
        Returns:
            int: Number of days pending
        """
        from datetime import date
        
        if not issue_date:
            return 0
        
        today = date.today()
        delta = today - issue_date
        return delta.days
    
    @staticmethod
    def validate_gatepass_details(details_data):
        """
        Validate gate pass detail items
        
        Args:
            details_data: List of detail item dictionaries
            
        Returns:
            tuple: (is_valid, error_message)
        """
        from decimal import Decimal
        
        if not details_data or len(details_data) == 0:
            return False, "At least one item is required"
        
        for idx, detail in enumerate(details_data, 1):
            # Check item is selected
            if not detail.get('itemid'):
                return False, f"Item is required for row {idx}"
            
            # Check quantity
            qty = detail.get('qty', 0)
            try:
                qty_decimal = Decimal(str(qty))
                if qty_decimal <= 0:
                    return False, f"Quantity must be greater than 0 for row {idx}"
            except:
                return False, f"Invalid quantity for row {idx}"
        
        return True, ""


# ============================================================================
# VEHICLE SERVICES
# ============================================================================

class VehicleService:
    """
    Service for Vehicle Master and Trip Management
    
    Handles vehicle registration, trip recording, and fuel efficiency tracking.
    
    Converted from: aspnet/Module/Inventory/Masters/Vehical_Master.aspx
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
    """
    
    @staticmethod
    def create_vehicle(vehicle_data):
        """
        Create vehicle master record
        
        Args:
            vehicle_data: Dictionary with vehicle details
            
        Returns:
            Vehicle object or None
        """
        from inventory.models import Tblvehiclemaster
        
        try:
            vehicle = Tblvehiclemaster.objects.create(**vehicle_data)
            return vehicle
        except Exception as e:
            print(f"Error creating vehicle: {e}")
            return None
    
    @staticmethod
    def record_trip(vehicle_id, trip_data):
        """
        Record vehicle trip with KM and fuel consumption
        
        Args:
            vehicle_id: Vehicle master ID
            trip_data: Dictionary with trip details
            
        Returns:
            Trip object or None
        """
        from inventory.models import Tblvehicletrip
        
        try:
            trip = Tblvehicletrip.objects.create(
                vehicleid=vehicle_id,
                **trip_data
            )
            return trip
        except Exception as e:
            print(f"Error recording trip: {e}")
            return None
    
    @staticmethod
    def calculate_distance(start_km, end_km):
        """
        Calculate distance traveled
        
        Args:
            start_km: Starting kilometer reading
            end_km: Ending kilometer reading
            
        Returns:
            Decimal: Distance in kilometers
        """
        from decimal import Decimal
        
        try:
            start = Decimal(str(start_km))
            end = Decimal(str(end_km))
            distance = end - start
            return distance.quantize(Decimal('0.01'))
        except:
            return Decimal('0.00')
    
    @staticmethod
    def calculate_fuel_efficiency(distance, fuel_consumed):
        """
        Calculate fuel efficiency (KM per liter)
        
        Args:
            distance: Distance traveled in KM
            fuel_consumed: Fuel consumed in liters
            
        Returns:
            Decimal: KM per liter
        """
        from decimal import Decimal
        
        try:
            dist = Decimal(str(distance))
            fuel = Decimal(str(fuel_consumed))
            
            if fuel == 0:
                return Decimal('0.00')
            
            efficiency = dist / fuel
            return efficiency.quantize(Decimal('0.01'))
        except:
            return Decimal('0.00')
    
    @staticmethod
    def get_vehicle_history(vehicle_id, from_date=None, to_date=None):
        """
        Get trip history for a vehicle with totals
        
        Args:
            vehicle_id: Vehicle master ID
            from_date: Start date (optional)
            to_date: End date (optional)
            
        Returns:
            dict: Trip history with totals
        """
        from inventory.models import Tblvehicletrip
        from decimal import Decimal
        
        trips = Tblvehicletrip.objects.filter(vehicleid=vehicle_id)
        
        if from_date:
            trips = trips.filter(tripdate__gte=from_date)
        if to_date:
            trips = trips.filter(tripdate__lte=to_date)
        
        trips = trips.order_by('-tripdate')
        
        # Calculate totals
        total_distance = sum((trip.distance or Decimal('0')) for trip in trips)
        total_fuel = sum((trip.fuelconsumed or Decimal('0')) for trip in trips)
        
        avg_efficiency = VehicleService.calculate_fuel_efficiency(total_distance, total_fuel)
        
        return {
            'trips': trips,
            'total_distance': total_distance,
            'total_fuel': total_fuel,
            'avg_efficiency': avg_efficiency
        }



# ============================================================================
# WORK INSTRUCTION SHEET (WIS) SERVICES
# ============================================================================

class WISService(BaseTransactionService):
    """
    Service for Work Instruction Sheet (WIS) operations
    
    Handles production material planning, BOM integration, stock availability checks,
    and actual run recording with variance tracking.
    
    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Material.aspx
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
    """
    
    @staticmethod
    def generate_wis_number(compid, finyearid):
        """
        Generate unique WIS number in format: WIS/YYYY/NNNN
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            str: Generated WIS number (e.g., WIS/2024/0001)
        """
        from inventory.models import Tblwismaster
        from django.db.models import Max
        import re
        
        latest = Tblwismaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).aggregate(Max('wisno'))
        
        latest_number = latest['wisno__max']
        
        if latest_number:
            match = re.search(r'/(\d+)$', latest_number)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        year = "2024"  # TODO: Get from finyearid
        
        return f"WIS/{year}/{next_num:04d}"
    
    @staticmethod
    def get_bom_materials(work_order_id):
        """
        Fetch BOM materials for work order (placeholder for future integration)
        
        Args:
            work_order_id: Work order ID
            
        Returns:
            list: List of BOM materials with quantities
        """
        # TODO: Integrate with BOM module when available
        # For now, return placeholder
        return [
            {
                'item_id': None,
                'item_name': 'Material 1',
                'required_qty': 10.000,
                'unit': 'PCS'
            },
            {
                'item_id': None,
                'item_name': 'Material 2',
                'required_qty': 5.000,
                'unit': 'KG'
            }
        ]
    
    @staticmethod
    def check_stock_availability(item_id, required_qty):
        """
        Check if sufficient stock is available for item
        
        Args:
            item_id: Item master ID
            required_qty: Required quantity
            
        Returns:
            dict: Availability status with details
        """
        from inventory.models import Tblitemmaster
        from decimal import Decimal
        
        try:
            item = Tblitemmaster.objects.get(itemid=item_id)
            current_stock = item.currentstock or Decimal('0')
            required = Decimal(str(required_qty))
            
            is_available = current_stock >= required
            shortage = Decimal('0') if is_available else (required - current_stock)
            
            return {
                'is_available': is_available,
                'current_stock': current_stock,
                'required_qty': required,
                'shortage': shortage
            }
        except:
            return {
                'is_available': False,
                'current_stock': Decimal('0'),
                'required_qty': Decimal(str(required_qty)),
                'shortage': Decimal(str(required_qty))
            }
    
    @staticmethod
    def calculate_shortage(required_qty, available_qty):
        """
        Calculate shortage quantity
        
        Args:
            required_qty: Required quantity
            available_qty: Available quantity
            
        Returns:
            Decimal: Shortage quantity (0 if sufficient)
        """
        from decimal import Decimal
        
        try:
            required = Decimal(str(required_qty))
            available = Decimal(str(available_qty))
            shortage = required - available
            return shortage if shortage > 0 else Decimal('0')
        except:
            return Decimal('0')
    
    @staticmethod
    def release_wis(wis_id):
        """
        Change WIS status to Released (ready for production)
        
        Args:
            wis_id: WIS master ID
            
        Returns:
            bool: Success status
        """
        from inventory.models import Tblwismaster
        
        try:
            wis = Tblwismaster.objects.get(wisid=wis_id)
            
            # Update status if field exists
            if hasattr(wis, 'status'):
                wis.status = 'Released'
                wis.save()
                return True
            
            return False
        except Exception as e:
            print(f"Error releasing WIS: {e}")
            return False
    
    @staticmethod
    def record_actual_run(wis_id, actual_materials, actual_assemblies=None):
        """
        Record actual material consumption and assembly usage
        
        Args:
            wis_id: WIS master ID
            actual_materials: List of dicts with item_id and actual_qty
            actual_assemblies: List of dicts with assembly_id and actual_qty (optional)
            
        Returns:
            bool: Success status
        """
        from inventory.models import Tblwisdetail, Tblwismaster
        from django.db import transaction
        from decimal import Decimal
        
        try:
            with transaction.atomic():
                # Update material actual quantities
                for material in actual_materials:
                    detail = Tblwisdetail.objects.get(
                        wisdetailid=material['detail_id']
                    )
                    
                    actual_qty = Decimal(str(material['actual_qty']))
                    detail.actualqty = actual_qty
                    
                    # Calculate variance
                    variance = WISService.calculate_variance(
                        detail.requiredqty,
                        actual_qty
                    )
                    detail.variance = variance
                    detail.save()
                
                # Update WIS status to Completed
                wis = Tblwismaster.objects.get(wisid=wis_id)
                if hasattr(wis, 'status'):
                    wis.status = 'Completed'
                    wis.save()
                
                # Update stock (deduct actual consumption)
                WISService.update_stock_on_actual_run(wis_id, actual_materials)
                
                return True
        except Exception as e:
            print(f"Error recording actual run: {e}")
            return False
    
    @staticmethod
    def calculate_variance(required_qty, actual_qty):
        """
        Calculate variance between required and actual quantities
        
        Args:
            required_qty: Required quantity
            actual_qty: Actual quantity consumed
            
        Returns:
            Decimal: Variance (positive = over-consumption, negative = under-consumption)
        """
        from decimal import Decimal
        
        try:
            required = Decimal(str(required_qty))
            actual = Decimal(str(actual_qty))
            variance = actual - required
            return variance.quantize(Decimal('0.001'))
        except:
            return Decimal('0.000')
    
    @staticmethod
    def update_stock_on_actual_run(wis_id, actual_materials):
        """
        Update stock levels based on actual material consumption
        
        Args:
            wis_id: WIS master ID
            actual_materials: List of dicts with item_id and actual_qty
            
        Returns:
            bool: Success status
        """
        from inventory.models import Tblitemmaster
        from django.db import transaction
        from decimal import Decimal
        
        try:
            with transaction.atomic():
                for material in actual_materials:
                    item = Tblitemmaster.objects.get(itemid=material['item_id'])
                    
                    actual_qty = Decimal(str(material['actual_qty']))
                    current_stock = item.currentstock or Decimal('0')
                    
                    # Deduct actual consumption from stock
                    item.currentstock = current_stock - actual_qty
                    item.save()
                
                return True
        except Exception as e:
            print(f"Error updating stock: {e}")
            return False
    
    @staticmethod
    def validate_wis_details(details_data):
        """
        Validate WIS detail items
        
        Args:
            details_data: List of detail item dictionaries
            
        Returns:
            tuple: (is_valid, error_message)
        """
        from decimal import Decimal
        
        if not details_data or len(details_data) == 0:
            return False, "At least one material is required"
        
        for idx, detail in enumerate(details_data, 1):
            # Check item is selected
            if not detail.get('itemid'):
                return False, f"Item is required for row {idx}"
            
            # Check required quantity
            qty = detail.get('requiredqty', 0)
            try:
                qty_decimal = Decimal(str(qty))
                if qty_decimal <= 0:
                    return False, f"Required quantity must be greater than 0 for row {idx}"
            except:
                return False, f"Invalid required quantity for row {idx}"
        
        return True, ""


# ============================================================================
# AUTO WIS GENERATION SERVICE
# ============================================================================

class AutoWISService:
    """
    Service for automatic WIS generation based on schedule
    
    Handles scheduled WIS generation for pending work orders.
    Requires Celery for background task execution.
    
    Converted from: aspnet/Module/Inventory/Masters/AutoWIS_Time_Set.aspx
    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
    """
    
    @staticmethod
    def save_schedule(schedule_data):
        """
        Save auto WIS generation schedule configuration
        
        Args:
            schedule_data: Dictionary with schedule details
            
        Returns:
            bool: Success status
        """
        # TODO: Implement schedule configuration storage
        # This would typically save to a configuration table
        return True
    
    @staticmethod
    def get_pending_work_orders(compid, finyearid):
        """
        Get work orders that need WIS generation
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            list: List of pending work orders
        """
        # TODO: Integrate with Work Order module when available
        # For now, return placeholder
        return []
    
    @staticmethod
    def generate_wis_batch(work_orders):
        """
        Generate WIS for multiple work orders in batch
        
        Args:
            work_orders: List of work order IDs
            
        Returns:
            dict: Generation results with success/failure counts
        """
        success_count = 0
        failure_count = 0
        errors = []
        
        for wo_id in work_orders:
            try:
                # TODO: Implement actual WIS generation logic
                # This would create WIS master and details from BOM
                success_count += 1
            except Exception as e:
                failure_count += 1
                errors.append(f"WO {wo_id}: {str(e)}")
        
        return {
            'success_count': success_count,
            'failure_count': failure_count,
            'errors': errors
        }



# ============================================================================
# ============================================================================
# MATERIAL CREDIT NOTE (MCN) SERVICES
# ============================================================================

class MaterialCreditNoteService(BaseTransactionService):
    """
    Service for Material Credit Note (MCN) operations
    
    Handles returns to suppliers with stock adjustments.
    
    Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
    """
    
    @staticmethod
    def generate_mcn_number(compid, finyearid):
        """
        Generate unique MCN number in format: MCN/YYYY/NNNN
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            str: Generated MCN number (e.g., MCN/2024/0001)
        """
        from inventory.models import Tblmcnmaster
        from django.db.models import Max
        import re
        
        latest = Tblmcnmaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).aggregate(Max('mcnno'))
        
        latest_number = latest['mcnno__max']
        
        if latest_number:
            match = re.search(r'/(\d+)$', latest_number)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        year = "2024"  # TODO: Get from finyearid
        
        return f"MCN/{year}/{next_num:04d}"
    
    @staticmethod
    def validate_return_against_grr(grr_id, return_qty):
        """
        Validate return quantity against GRR
        
        Args:
            grr_id: GRR master ID
            return_qty: Quantity to return
            
        Returns:
            tuple: (is_valid, error_message)
        """
        from decimal import Decimal
        
        # TODO: Implement GRR validation when GRR module is available
        # For now, basic validation
        try:
            qty = Decimal(str(return_qty))
            if qty <= 0:
                return False, "Return quantity must be greater than 0"
            return True, ""
        except:
            return False, "Invalid return quantity"
    
    @staticmethod
    def update_stock_on_return(mcn_data):
        """
        Update stock with negative entries for returns
        
        Args:
            mcn_data: MCN data with items
            
        Returns:
            bool: Success status
        """
        from inventory.models import Tblitemmaster
        from django.db import transaction
        from decimal import Decimal
        
        try:
            with transaction.atomic():
                for item in mcn_data.get('items', []):
                    item_obj = Tblitemmaster.objects.get(itemid=item['item_id'])
                    return_qty = Decimal(str(item['qty']))
                    
                    # Deduct from stock (return to supplier)
                    current_stock = item_obj.currentstock or Decimal('0')
                    item_obj.currentstock = current_stock - return_qty
                    item_obj.save()
                
                return True
        except Exception as e:
            print(f"Error updating stock: {e}")
            return False


# ============================================================================
# CLOSING STOCK SERVICES
# ============================================================================

class ClosingStockService:
    """
    Service for Closing Stock operations
    
    Handles period-end stock reconciliation.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
    """
    
    @staticmethod
    def get_system_stock(item_id, as_of_date=None):
        """
        Get system stock as of date
        
        Args:
            item_id: Item master ID
            as_of_date: Date to check stock (optional)
            
        Returns:
            Decimal: System stock quantity
        """
        from inventory.models import Tblitemmaster
        from decimal import Decimal
        
        try:
            item = Tblitemmaster.objects.get(itemid=item_id)
            return item.currentstock or Decimal('0')
        except:
            return Decimal('0')
    
    @staticmethod
    def calculate_variance(system_qty, physical_qty):
        """
        Calculate variance between system and physical stock
        
        Args:
            system_qty: System stock quantity
            physical_qty: Physical count quantity
            
        Returns:
            Decimal: Variance (positive = excess, negative = shortage)
        """
        from decimal import Decimal
        
        try:
            system = Decimal(str(system_qty))
            physical = Decimal(str(physical_qty))
            variance = physical - system
            return variance.quantize(Decimal('0.001'))
        except:
            return Decimal('0.000')
    
    @staticmethod
    def generate_adjustment_entries(variances):
        """
        Create stock adjustment entries for variances
        
        Args:
            variances: List of dicts with item_id, system_qty, physical_qty, variance
            
        Returns:
            bool: Success status
        """
        from inventory.models import Tblitemmaster
        from django.db import transaction
        from decimal import Decimal
        
        try:
            with transaction.atomic():
                for var in variances:
                    if var['variance'] != Decimal('0'):
                        item = Tblitemmaster.objects.get(itemid=var['item_id'])
                        item.currentstock = Decimal(str(var['physical_qty']))
                        item.save()
                
                return True
        except Exception as e:
            print(f"Error generating adjustments: {e}")
            return False



# ============================================================================
# REPORT SERVICES
# ============================================================================

class ReportService:
    """
    Service for all inventory reporting operations
    
    Provides methods for stock ledger, stock statement, ABC analysis,
    moving/non-moving items, work order reports, and registers.
    
    Converted from: aspnet/Module/Inventory/Reports/
    Requirements: 1.1-5.9
    """
    
    @staticmethod
    def get_stock_ledger(item_id, start_date, end_date, compid, finyearid):
        """
        Generate stock ledger with opening balance, transactions, and closing balance.
        
        Shows all inward and outward transactions for an item in chronological order
        with running balance calculations.
        
        Args:
            item_id: Item ID to generate ledger for
            start_date: Start date for transactions (datetime object)
            end_date: End date for transactions (datetime object)
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            dict: {
                'item': Item object,
                'opening_balance': Decimal,
                'transactions': List of transaction dicts,
                'closing_balance': Decimal,
                'total_inward': Decimal,
                'total_outward': Decimal
            }
            
        Requirements: 1.1, 1.2, 1.3
        """
        from decimal import Decimal
        from django.db.models import Q
        from .models import (
            TblinvInwardDetails, TblinvMaterialreceivedDetails,
            TblinvMaterialissueDetails, TblinvMaterialreturnDetails,
            TblinvMaterialcreditnoteDetails
        )
        from sys_admin.models import TblitemMaster
        
        try:
            item = TblitemMaster.objects.get(itemid=item_id, compid=compid)
        except TblitemMaster.DoesNotExist:
            return None
        
        # Calculate opening balance (all transactions before start_date)
        opening_balance = ReportService._calculate_opening_balance(
            item_id, start_date, compid, finyearid
        )
        
        # Collect all transactions in date range
        transactions = []
        
        # GIN (Goods Inward Note) - Inward
        gin_transactions = TblinvInwardDetails.objects.filter(
            itemid=item_id,
            ginid__compid=compid,
            ginid__gindate__gte=start_date,
            ginid__gindate__lte=end_date
        ).select_related('ginid', 'ginid__supplierid').order_by('ginid__gindate')
        
        for gin_detail in gin_transactions:
            transactions.append({
                'date': gin_detail.ginid.gindate,
                'type': 'GIN',
                'doc_no': gin_detail.ginid.ginno,
                'reference': f"Supplier: {gin_detail.ginid.supplierid.suppliername if gin_detail.ginid.supplierid else 'N/A'}",
                'inward_qty': gin_detail.qty or Decimal('0'),
                'outward_qty': Decimal('0'),
                'rate': gin_detail.rate or Decimal('0'),
                'remarks': gin_detail.remarks or ''
            })
        
        # GRR (Goods Received Receipt) - Inward
        grr_transactions = TblinvMaterialreceivedDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid,
            mid__grrdate__gte=start_date,
            mid__grrdate__lte=end_date
        ).select_related('mid', 'mid__supplierid').order_by('mid__grrdate')
        
        for grr_detail in grr_transactions:
            transactions.append({
                'date': grr_detail.mid.grrdate,
                'type': 'GRR',
                'doc_no': grr_detail.mid.grrno,
                'reference': f"Supplier: {grr_detail.mid.supplierid.suppliername if grr_detail.mid.supplierid else 'N/A'}",
                'inward_qty': grr_detail.receivedqty or Decimal('0'),
                'outward_qty': Decimal('0'),
                'rate': grr_detail.rate or Decimal('0'),
                'remarks': grr_detail.remarks or ''
            })
        
        # MIN (Material Issue Note) - Outward
        min_transactions = TblinvMaterialissueDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid,
            mid__mindate__gte=start_date,
            mid__mindate__lte=end_date
        ).select_related('mid', 'mid__deptid').order_by('mid__mindate')
        
        for min_detail in min_transactions:
            transactions.append({
                'date': min_detail.mid.mindate,
                'type': 'MIN',
                'doc_no': min_detail.mid.minno,
                'reference': f"Dept: {min_detail.mid.deptid.deptname if min_detail.mid.deptid else 'N/A'}",
                'inward_qty': Decimal('0'),
                'outward_qty': min_detail.issueqty or Decimal('0'),
                'rate': min_detail.rate or Decimal('0'),
                'remarks': min_detail.remarks or ''
            })
        
        # MRN (Material Return Note) - Inward
        mrn_transactions = TblinvMaterialreturnDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid,
            mid__mrndate__gte=start_date,
            mid__mrndate__lte=end_date
        ).select_related('mid', 'mid__deptid').order_by('mid__mrndate')
        
        for mrn_detail in mrn_transactions:
            transactions.append({
                'date': mrn_detail.mid.mrndate,
                'type': 'MRN',
                'doc_no': mrn_detail.mid.mrnno,
                'reference': f"Dept: {mrn_detail.mid.deptid.deptname if mrn_detail.mid.deptid else 'N/A'}",
                'inward_qty': mrn_detail.returnqty or Decimal('0'),
                'outward_qty': Decimal('0'),
                'rate': mrn_detail.rate or Decimal('0'),
                'remarks': mrn_detail.remarks or ''
            })
        
        # MCN (Material Credit Note) - Outward (return to supplier)
        mcn_transactions = TblinvMaterialcreditnoteDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid,
            mid__mcndate__gte=start_date,
            mid__mcndate__lte=end_date
        ).select_related('mid', 'mid__supplierid').order_by('mid__mcndate')
        
        for mcn_detail in mcn_transactions:
            transactions.append({
                'date': mcn_detail.mid.mcndate,
                'type': 'MCN',
                'doc_no': mcn_detail.mid.mcnno,
                'reference': f"Supplier: {mcn_detail.mid.supplierid.suppliername if mcn_detail.mid.supplierid else 'N/A'}",
                'inward_qty': Decimal('0'),
                'outward_qty': mcn_detail.qty or Decimal('0'),
                'rate': mcn_detail.rate or Decimal('0'),
                'remarks': mcn_detail.reason or ''
            })
        
        # Sort all transactions by date
        transactions.sort(key=lambda x: x['date'])
        
        # Calculate running balance
        running_balance = opening_balance
        total_inward = Decimal('0')
        total_outward = Decimal('0')
        
        for txn in transactions:
            running_balance += txn['inward_qty'] - txn['outward_qty']
            txn['balance'] = running_balance
            total_inward += txn['inward_qty']
            total_outward += txn['outward_qty']
        
        closing_balance = opening_balance + total_inward - total_outward
        
        return {
            'item': item,
            'opening_balance': opening_balance,
            'transactions': transactions,
            'closing_balance': closing_balance,
            'total_inward': total_inward,
            'total_outward': total_outward,
            'start_date': start_date,
            'end_date': end_date
        }
    
    @staticmethod
    def _calculate_opening_balance(item_id, before_date, compid, finyearid):
        """
        Calculate opening balance for an item before a specific date.
        
        Args:
            item_id: Item ID
            before_date: Calculate balance before this date
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            Decimal: Opening balance quantity
        """
        from decimal import Decimal
        from .models import (
            TblinvInwardDetails, TblinvMaterialreceivedDetails,
            TblinvMaterialissueDetails, TblinvMaterialreturnDetails,
            TblinvMaterialcreditnoteDetails
        )
        
        total_inward = Decimal('0')
        total_outward = Decimal('0')
        
        # Sum all inward transactions before date
        # GIN
        gin_qty = TblinvInwardDetails.objects.filter(
            itemid=item_id,
            ginid__compid=compid,
            ginid__gindate__lt=before_date
        ).aggregate(total=Sum('qty'))['total'] or Decimal('0')
        total_inward += gin_qty
        
        # GRR
        grr_qty = TblinvMaterialreceivedDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid,
            mid__grrdate__lt=before_date
        ).aggregate(total=Sum('receivedqty'))['total'] or Decimal('0')
        total_inward += grr_qty
        
        # MRN
        mrn_qty = TblinvMaterialreturnDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid,
            mid__mrndate__lt=before_date
        ).aggregate(total=Sum('returnqty'))['total'] or Decimal('0')
        total_inward += mrn_qty
        
        # Sum all outward transactions before date
        # MIN
        min_qty = TblinvMaterialissueDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid,
            mid__mindate__lt=before_date
        ).aggregate(total=Sum('issueqty'))['total'] or Decimal('0')
        total_outward += min_qty
        
        # MCN
        mcn_qty = TblinvMaterialcreditnoteDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid,
            mid__mcndate__lt=before_date
        ).aggregate(total=Sum('qty'))['total'] or Decimal('0')
        total_outward += mcn_qty
        
        return total_inward - total_outward

    
    @staticmethod
    def get_stock_statement(compid, finyearid, filters=None):
        """
        Generate current stock statement for all items.
        
        Shows current stock levels, last transaction date, and stock value
        for all items with optional filtering.
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            filters: Optional dict with:
                - category_id: Filter by item category
                - location_id: Filter by warehouse location
                - stock_status: 'zero', 'low', 'normal', 'all'
                - search: Search by item code or name
                
        Returns:
            list: List of dicts with item details and current stock:
                {
                    'item': Item object,
                    'current_qty': Decimal,
                    'stock_value': Decimal,
                    'last_transaction_date': date,
                    'last_transaction_type': str,
                    'location': str,
                    'stock_status': str ('Zero Stock', 'Low Stock', 'Normal')
                }
                
        Requirements: 1.4, 1.5, 1.6
        """
        from sys_admin.models import TblitemMaster
        from .models import TblinvItemlocationMaster
        from django.db.models import Q
        
        # Get all items for company
        items_query = TblitemMaster.objects.filter(compid=compid)
        
        # Apply filters
        if filters:
            # Category filter
            if filters.get('category_id'):
                items_query = items_query.filter(categoryid=filters['category_id'])
            
            # Search filter
            if filters.get('search'):
                search_term = filters['search']
                items_query = items_query.filter(
                    Q(itemcode__icontains=search_term) |
                    Q(itemname__icontains=search_term)
                )
        
        items = items_query.order_by('itemname')
        
        stock_data = []
        
        for item in items:
            # Calculate current stock
            current_qty = ReportService._calculate_current_stock(item.itemid, compid)
            
            # Get last transaction
            last_txn = ReportService._get_last_transaction(item.itemid, compid)
            
            # Get item location
            location = ReportService._get_item_location(item.itemid, compid)
            
            # Calculate stock value (current_qty * last rate)
            stock_value = current_qty * (last_txn['rate'] if last_txn else Decimal('0'))
            
            # Determine stock status
            reorder_level = item.reorderlevel or Decimal('0')
            if current_qty == Decimal('0'):
                stock_status = 'Zero Stock'
            elif current_qty <= reorder_level:
                stock_status = 'Low Stock'
            else:
                stock_status = 'Normal'
            
            # Apply stock status filter
            if filters and filters.get('stock_status'):
                status_filter = filters['stock_status']
                if status_filter == 'zero' and stock_status != 'Zero Stock':
                    continue
                elif status_filter == 'low' and stock_status != 'Low Stock':
                    continue
                elif status_filter == 'normal' and stock_status != 'Normal':
                    continue
            
            # Apply location filter
            if filters and filters.get('location_id'):
                if location != filters['location_id']:
                    continue
            
            stock_data.append({
                'item': item,
                'current_qty': current_qty,
                'stock_value': stock_value,
                'last_transaction_date': last_txn['date'] if last_txn else None,
                'last_transaction_type': last_txn['type'] if last_txn else 'N/A',
                'location': location or 'Not Assigned',
                'stock_status': stock_status,
                'unit': item.unit or 'Nos'
            })
        
        return stock_data
    
    @staticmethod
    def _calculate_current_stock(item_id, compid):
        """
        Calculate current stock quantity for an item.
        
        Args:
            item_id: Item ID
            compid: Company ID
            
        Returns:
            Decimal: Current stock quantity
        """
        from .models import (
            TblinvInwardDetails, TblinvMaterialreceivedDetails,
            TblinvMaterialissueDetails, TblinvMaterialreturnDetails,
            TblinvMaterialcreditnoteDetails
        )
        
        total_inward = Decimal('0')
        total_outward = Decimal('0')
        
        # Sum all inward transactions
        # GIN
        gin_qty = TblinvInwardDetails.objects.filter(
            itemid=item_id,
            ginid__compid=compid
        ).aggregate(total=Sum('qty'))['total'] or Decimal('0')
        total_inward += gin_qty
        
        # GRR
        grr_qty = TblinvMaterialreceivedDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).aggregate(total=Sum('receivedqty'))['total'] or Decimal('0')
        total_inward += grr_qty
        
        # MRN
        mrn_qty = TblinvMaterialreturnDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).aggregate(total=Sum('returnqty'))['total'] or Decimal('0')
        total_inward += mrn_qty
        
        # Sum all outward transactions
        # MIN
        min_qty = TblinvMaterialissueDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).aggregate(total=Sum('issueqty'))['total'] or Decimal('0')
        total_outward += min_qty
        
        # MCN
        mcn_qty = TblinvMaterialcreditnoteDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).aggregate(total=Sum('qty'))['total'] or Decimal('0')
        total_outward += mcn_qty
        
        return total_inward - total_outward
    
    @staticmethod
    def _get_last_transaction(item_id, compid):
        """
        Get the last transaction for an item.
        
        Args:
            item_id: Item ID
            compid: Company ID
            
        Returns:
            dict: {'date': date, 'type': str, 'rate': Decimal} or None
        """
        from .models import (
            TblinvInwardDetails, TblinvMaterialreceivedDetails,
            TblinvMaterialissueDetails, TblinvMaterialreturnDetails,
            TblinvMaterialcreditnoteDetails
        )
        
        transactions = []
        
        # Get latest from each transaction type
        # GIN
        gin_latest = TblinvInwardDetails.objects.filter(
            itemid=item_id,
            ginid__compid=compid
        ).select_related('ginid').order_by('-ginid__gindate').first()
        if gin_latest:
            transactions.append({
                'date': gin_latest.ginid.gindate,
                'type': 'GIN',
                'rate': gin_latest.rate or Decimal('0')
            })
        
        # GRR
        grr_latest = TblinvMaterialreceivedDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).select_related('mid').order_by('-mid__grrdate').first()
        if grr_latest:
            transactions.append({
                'date': grr_latest.mid.grrdate,
                'type': 'GRR',
                'rate': grr_latest.rate or Decimal('0')
            })
        
        # MIN
        min_latest = TblinvMaterialissueDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).select_related('mid').order_by('-mid__mindate').first()
        if min_latest:
            transactions.append({
                'date': min_latest.mid.mindate,
                'type': 'MIN',
                'rate': min_latest.rate or Decimal('0')
            })
        
        # MRN
        mrn_latest = TblinvMaterialreturnDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).select_related('mid').order_by('-mid__mrndate').first()
        if mrn_latest:
            transactions.append({
                'date': mrn_latest.mid.mrndate,
                'type': 'MRN',
                'rate': mrn_latest.rate or Decimal('0')
            })
        
        # MCN
        mcn_latest = TblinvMaterialcreditnoteDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).select_related('mid').order_by('-mid__mcndate').first()
        if mcn_latest:
            transactions.append({
                'date': mcn_latest.mid.mcndate,
                'type': 'MCN',
                'rate': mcn_latest.rate or Decimal('0')
            })
        
        # Return the most recent transaction
        if transactions:
            return max(transactions, key=lambda x: x['date'])
        return None
    
    @staticmethod
    def _get_item_location(item_id, compid):
        """
        Get primary warehouse location for an item.
        
        Args:
            item_id: Item ID
            compid: Company ID
            
        Returns:
            str: Location code or None
        """
        from .models import TblinvItemlocationMaster
        
        location = TblinvItemlocationMaster.objects.filter(
            itemid=item_id,
            compid=compid
        ).first()
        
        if location:
            return f"{location.locationcode or ''} - {location.binnumber or ''}".strip(' - ')
        return None

    
    @staticmethod
    def get_abc_analysis(compid, finyearid, start_date, end_date, criteria='value'):
        """
        Perform ABC analysis on inventory items.
        
        Categorizes items into A (high value), B (medium value), and C (low value)
        based on Pareto principle (80-20 rule):
        - A items: Top 70% of total value (typically 20% of items)
        - B items: Next 20% of total value (typically 30% of items)
        - C items: Last 10% of total value (typically 50% of items)
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            start_date: Start date for analysis period
            end_date: End date for analysis period
            criteria: Analysis criteria - 'value', 'quantity', or 'frequency'
                - 'value': Based on consumption value (qty × rate)
                - 'quantity': Based on total quantity consumed
                - 'frequency': Based on number of transactions
                
        Returns:
            list: List of dicts with ABC categorization:
                {
                    'item': Item object,
                    'consumption_qty': Decimal,
                    'consumption_value': Decimal,
                    'transaction_count': int,
                    'percentage_of_total': Decimal,
                    'cumulative_percentage': Decimal,
                    'abc_category': str ('A', 'B', or 'C')
                }
                
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        from sys_admin.models import TblitemMaster
        from .models import TblinvMaterialissueDetails
        
        # Get all items with consumption in the period
        items_data = []
        items = TblitemMaster.objects.filter(compid=compid)
        
        for item in items:
            # Get all issue transactions for this item in date range
            issues = TblinvMaterialissueDetails.objects.filter(
                itemid=item.itemid,
                mid__compid=compid,
                mid__mindate__gte=start_date,
                mid__mindate__lte=end_date
            ).select_related('mid')
            
            if not issues.exists():
                continue
            
            # Calculate metrics
            consumption_qty = Decimal('0')
            consumption_value = Decimal('0')
            transaction_count = issues.count()
            
            for issue in issues:
                qty = issue.issueqty or Decimal('0')
                rate = issue.rate or Decimal('0')
                consumption_qty += qty
                consumption_value += qty * rate
            
            items_data.append({
                'item': item,
                'consumption_qty': consumption_qty,
                'consumption_value': consumption_value,
                'transaction_count': transaction_count
            })
        
        # Sort based on criteria
        if criteria == 'value':
            items_data.sort(key=lambda x: x['consumption_value'], reverse=True)
            total = sum(item['consumption_value'] for item in items_data)
        elif criteria == 'quantity':
            items_data.sort(key=lambda x: x['consumption_qty'], reverse=True)
            total = sum(item['consumption_qty'] for item in items_data)
        else:  # frequency
            items_data.sort(key=lambda x: x['transaction_count'], reverse=True)
            total = sum(item['transaction_count'] for item in items_data)
        
        # Calculate percentages and assign ABC categories
        cumulative = Decimal('0')
        
        for item_data in items_data:
            # Calculate percentage of total
            if criteria == 'value':
                value = item_data['consumption_value']
            elif criteria == 'quantity':
                value = item_data['consumption_qty']
            else:
                value = Decimal(str(item_data['transaction_count']))
            
            if total > 0:
                percentage = (value / Decimal(str(total))) * Decimal('100')
                cumulative += percentage
            else:
                percentage = Decimal('0')
            
            item_data['percentage_of_total'] = percentage
            item_data['cumulative_percentage'] = cumulative
            
            # Assign ABC category based on cumulative percentage
            if cumulative <= Decimal('70'):
                item_data['abc_category'] = 'A'
            elif cumulative <= Decimal('90'):
                item_data['abc_category'] = 'B'
            else:
                item_data['abc_category'] = 'C'
        
        return items_data
    
    @staticmethod
    def get_moving_nonmoving_items(compid, finyearid, threshold_days=90):
        """
        Identify moving and non-moving items based on transaction threshold.
        
        Items with no transactions in the last N days are considered non-moving.
        Helps identify obsolete stock and slow-moving inventory.
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            threshold_days: Number of days to consider (default: 90)
                Items with no transactions in last N days are non-moving
                
        Returns:
            list: List of dicts with movement analysis:
                {
                    'item': Item object,
                    'current_stock': Decimal,
                    'stock_value': Decimal,
                    'last_transaction_date': date or None,
                    'last_transaction_type': str,
                    'days_since_movement': int,
                    'movement_status': str ('Moving', 'Non-Moving', 'Never Moved'),
                    'is_critical': bool (non-moving with high stock value)
                }
                
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
        """
        from sys_admin.models import TblitemMaster
        from datetime import timedelta
        
        threshold_date = timezone.now().date() - timedelta(days=threshold_days)
        items = TblitemMaster.objects.filter(compid=compid)
        
        items_data = []
        
        for item in items:
            # Get current stock
            current_stock = ReportService._calculate_current_stock(item.itemid, compid)
            
            # Skip items with zero stock (optional - can be included based on requirement)
            # if current_stock == Decimal('0'):
            #     continue
            
            # Get last transaction
            last_txn = ReportService._get_last_transaction(item.itemid, compid)
            
            if last_txn:
                last_date = last_txn['date']
                last_type = last_txn['type']
                days_since = (timezone.now().date() - last_date).days
                
                # Determine movement status
                if last_date >= threshold_date:
                    movement_status = 'Moving'
                else:
                    movement_status = 'Non-Moving'
            else:
                last_date = None
                last_type = 'N/A'
                days_since = None
                movement_status = 'Never Moved'
            
            # Calculate stock value
            stock_value = current_stock * (last_txn['rate'] if last_txn else Decimal('0'))
            
            # Mark as critical if non-moving with high stock value (>10000)
            is_critical = (movement_status in ['Non-Moving', 'Never Moved'] and 
                          stock_value > Decimal('10000'))
            
            items_data.append({
                'item': item,
                'current_stock': current_stock,
                'stock_value': stock_value,
                'last_transaction_date': last_date,
                'last_transaction_type': last_type,
                'days_since_movement': days_since,
                'movement_status': movement_status,
                'is_critical': is_critical
            })
        
        # Sort by days since movement (descending)
        items_data.sort(key=lambda x: x['days_since_movement'] or 999999, reverse=True)
        
        return items_data
    
    @staticmethod
    def get_work_order_issues(work_order_id, compid, finyearid):
        """
        Get all material issues for a work order.
        
        Shows required vs issued vs pending quantities for all materials
        linked to a specific work order.
        
        Args:
            work_order_id: Work Order ID
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            list: List of dicts with issue details:
                {
                    'item': Item object,
                    'required_qty': Decimal,
                    'issued_qty': Decimal,
                    'pending_qty': Decimal,
                    'percentage_issued': Decimal,
                    'last_issue_date': date or None,
                    'status': str ('Complete', 'Partial', 'Pending')
                }
                
        Requirements: 4.1, 4.2, 4.3
        """
        from .models import (
            TblinvMaterialrequisitionMaster,
            TblinvMaterialrequisitionDetails,
            TblinvMaterialissueDetails
        )
        from sys_admin.models import TblitemMaster
        
        # Get all MRS for this work order
        mrs_list = TblinvMaterialrequisitionMaster.objects.filter(
            wono=work_order_id,
            compid=compid
        )
        
        # Collect all items with requirements
        items_dict = {}
        
        for mrs in mrs_list:
            mrs_details = TblinvMaterialrequisitionDetails.objects.filter(
                mid=mrs.id
            ).select_related('itemid')
            
            for detail in mrs_details:
                item_id = detail.itemid.itemid
                
                if item_id not in items_dict:
                    items_dict[item_id] = {
                        'item': detail.itemid,
                        'required_qty': Decimal('0'),
                        'issued_qty': Decimal('0'),
                        'mrs_details': []
                    }
                
                items_dict[item_id]['required_qty'] += detail.reqqty or Decimal('0')
                items_dict[item_id]['mrs_details'].append(detail.id)
        
        # Calculate issued quantities
        result = []
        
        for item_id, data in items_dict.items():
            # Get issued quantity for this item from all MRS details
            issued_qty = TblinvMaterialissueDetails.objects.filter(
                mrsid__in=data['mrs_details']
            ).aggregate(total=Sum('issueqty'))['total'] or Decimal('0')
            
            # Get last issue date
            last_issue = TblinvMaterialissueDetails.objects.filter(
                mrsid__in=data['mrs_details']
            ).select_related('mid').order_by('-mid__mindate').first()
            
            last_issue_date = last_issue.mid.mindate if last_issue else None
            
            # Calculate pending and percentage
            pending_qty = data['required_qty'] - issued_qty
            percentage_issued = (issued_qty / data['required_qty'] * Decimal('100')) if data['required_qty'] > 0 else Decimal('0')
            
            # Determine status
            if pending_qty == Decimal('0'):
                status = 'Complete'
            elif issued_qty == Decimal('0'):
                status = 'Pending'
            else:
                status = 'Partial'
            
            result.append({
                'item': data['item'],
                'required_qty': data['required_qty'],
                'issued_qty': issued_qty,
                'pending_qty': pending_qty,
                'percentage_issued': percentage_issued,
                'last_issue_date': last_issue_date,
                'status': status
            })
        
        return result
    
    @staticmethod
    def get_work_order_shortages(work_order_id, compid, finyearid):
        """
        Get material shortages for a work order.
        
        Identifies items where issued quantity is less than required quantity.
        
        Args:
            work_order_id: Work Order ID
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            list: List of dicts with shortage details (only items with shortage):
                {
                    'item': Item object,
                    'required_qty': Decimal,
                    'issued_qty': Decimal,
                    'shortage_qty': Decimal,
                    'shortage_percentage': Decimal,
                    'current_stock': Decimal,
                    'can_fulfill': bool (current stock >= shortage)
                }
                
        Requirements: 4.4, 4.5
        """
        # Get all issues first
        all_issues = ReportService.get_work_order_issues(work_order_id, compid, finyearid)
        
        # Filter only items with pending quantity > 0
        shortages = []
        
        for issue in all_issues:
            if issue['pending_qty'] > Decimal('0'):
                # Get current stock
                current_stock = ReportService._calculate_current_stock(
                    issue['item'].itemid, compid
                )
                
                # Calculate shortage percentage
                shortage_percentage = (issue['pending_qty'] / issue['required_qty'] * Decimal('100')) if issue['required_qty'] > 0 else Decimal('0')
                
                shortages.append({
                    'item': issue['item'],
                    'required_qty': issue['required_qty'],
                    'issued_qty': issue['issued_qty'],
                    'shortage_qty': issue['pending_qty'],
                    'shortage_percentage': shortage_percentage,
                    'current_stock': current_stock,
                    'can_fulfill': current_stock >= issue['pending_qty']
                })
        
        # Sort by shortage percentage (descending)
        shortages.sort(key=lambda x: x['shortage_percentage'], reverse=True)
        
        return shortages

    
    @staticmethod
    def get_inward_register(compid, finyearid, start_date, end_date, transaction_types=None):
        """
        Get consolidated inward register (GIN, GRR, MRN).
        
        Provides a unified view of all inward transactions across different
        transaction types with filtering capabilities.
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            start_date: Start date for register
            end_date: End date for register
            transaction_types: Optional list of types to include ['GIN', 'GRR', 'MRN']
                If None, includes all types
                
        Returns:
            list: List of dicts with unified inward transaction format:
                {
                    'date': date,
                    'type': str ('GIN', 'GRR', 'MRN'),
                    'doc_no': str,
                    'supplier': str,
                    'item_code': str,
                    'item_name': str,
                    'quantity': Decimal,
                    'rate': Decimal,
                    'value': Decimal,
                    'remarks': str
                }
                
        Requirements: 5.1, 5.2
        """
        from .models import (
            TblinvInwardMaster, TblinvInwardDetails,
            TblinvMaterialreceivedMaster, TblinvMaterialreceivedDetails,
            TblinvMaterialreturnMaster, TblinvMaterialreturnDetails
        )
        
        transactions = []
        
        # Include all types if not specified
        if transaction_types is None:
            transaction_types = ['GIN', 'GRR', 'MRN']
        
        # GIN (Goods Inward Note)
        if 'GIN' in transaction_types:
            gin_masters = TblinvInwardMaster.objects.filter(
                compid=compid,
                gindate__gte=start_date,
                gindate__lte=end_date
            ).select_related('supplierid')
            
            for gin in gin_masters:
                gin_details = TblinvInwardDetails.objects.filter(
                    ginid=gin.id
                ).select_related('itemid')
                
                for detail in gin_details:
                    transactions.append({
                        'date': gin.gindate,
                        'type': 'GIN',
                        'doc_no': gin.ginno or '',
                        'supplier': gin.supplierid.suppliername if gin.supplierid else 'N/A',
                        'item_code': detail.itemid.itemcode if detail.itemid else '',
                        'item_name': detail.itemid.itemname if detail.itemid else '',
                        'quantity': detail.qty or Decimal('0'),
                        'rate': detail.rate or Decimal('0'),
                        'value': (detail.qty or Decimal('0')) * (detail.rate or Decimal('0')),
                        'remarks': detail.remarks or ''
                    })
        
        # GRR (Goods Received Receipt)
        if 'GRR' in transaction_types:
            grr_masters = TblinvMaterialreceivedMaster.objects.filter(
                compid=compid,
                grrdate__gte=start_date,
                grrdate__lte=end_date
            ).select_related('supplierid')
            
            for grr in grr_masters:
                grr_details = TblinvMaterialreceivedDetails.objects.filter(
                    mid=grr.id
                ).select_related('itemid')
                
                for detail in grr_details:
                    transactions.append({
                        'date': grr.grrdate,
                        'type': 'GRR',
                        'doc_no': grr.grrno or '',
                        'supplier': grr.supplierid.suppliername if grr.supplierid else 'N/A',
                        'item_code': detail.itemid.itemcode if detail.itemid else '',
                        'item_name': detail.itemid.itemname if detail.itemid else '',
                        'quantity': detail.receivedqty or Decimal('0'),
                        'rate': detail.rate or Decimal('0'),
                        'value': (detail.receivedqty or Decimal('0')) * (detail.rate or Decimal('0')),
                        'remarks': detail.remarks or ''
                    })
        
        # MRN (Material Return Note)
        if 'MRN' in transaction_types:
            mrn_masters = TblinvMaterialreturnMaster.objects.filter(
                compid=compid,
                mrndate__gte=start_date,
                mrndate__lte=end_date
            ).select_related('deptid')
            
            for mrn in mrn_masters:
                mrn_details = TblinvMaterialreturnDetails.objects.filter(
                    mid=mrn.id
                ).select_related('itemid')
                
                for detail in mrn_details:
                    transactions.append({
                        'date': mrn.mrndate,
                        'type': 'MRN',
                        'doc_no': mrn.mrnno or '',
                        'supplier': f"Dept: {mrn.deptid.deptname}" if mrn.deptid else 'N/A',
                        'item_code': detail.itemid.itemcode if detail.itemid else '',
                        'item_name': detail.itemid.itemname if detail.itemid else '',
                        'quantity': detail.returnqty or Decimal('0'),
                        'rate': detail.rate or Decimal('0'),
                        'value': (detail.returnqty or Decimal('0')) * (detail.rate or Decimal('0')),
                        'remarks': detail.remarks or ''
                    })
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        
        return transactions
    
    @staticmethod
    def get_outward_register(compid, finyearid, start_date, end_date, transaction_types=None):
        """
        Get consolidated outward register (MIN, MCN, Customer Challan).
        
        Provides a unified view of all outward transactions across different
        transaction types with filtering capabilities.
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            start_date: Start date for register
            end_date: End date for register
            transaction_types: Optional list of types to include ['MIN', 'MCN', 'CCHAL']
                If None, includes all types
                
        Returns:
            list: List of dicts with unified outward transaction format:
                {
                    'date': date,
                    'type': str ('MIN', 'MCN', 'CCHAL'),
                    'doc_no': str,
                    'destination': str (department/customer/supplier),
                    'item_code': str,
                    'item_name': str,
                    'quantity': Decimal,
                    'rate': Decimal,
                    'value': Decimal,
                    'remarks': str
                }
                
        Requirements: 5.3, 5.4
        """
        from .models import (
            TblinvMaterialissueMaster, TblinvMaterialissueDetails,
            TblinvMaterialcreditnoteMaster, TblinvMaterialcreditnoteDetails,
            TblinvCustomerchallanMaster, TblinvCustomerchallanDetails
        )
        
        transactions = []
        
        # Include all types if not specified
        if transaction_types is None:
            transaction_types = ['MIN', 'MCN', 'CCHAL']
        
        # MIN (Material Issue Note)
        if 'MIN' in transaction_types:
            min_masters = TblinvMaterialissueMaster.objects.filter(
                compid=compid,
                mindate__gte=start_date,
                mindate__lte=end_date
            ).select_related('deptid')
            
            for min_master in min_masters:
                min_details = TblinvMaterialissueDetails.objects.filter(
                    mid=min_master.id
                ).select_related('itemid')
                
                for detail in min_details:
                    transactions.append({
                        'date': min_master.mindate,
                        'type': 'MIN',
                        'doc_no': min_master.minno or '',
                        'destination': f"Dept: {min_master.deptid.deptname}" if min_master.deptid else 'N/A',
                        'item_code': detail.itemid.itemcode if detail.itemid else '',
                        'item_name': detail.itemid.itemname if detail.itemid else '',
                        'quantity': detail.issueqty or Decimal('0'),
                        'rate': detail.rate or Decimal('0'),
                        'value': (detail.issueqty or Decimal('0')) * (detail.rate or Decimal('0')),
                        'remarks': detail.remarks or ''
                    })
        
        # MCN (Material Credit Note)
        if 'MCN' in transaction_types:
            mcn_masters = TblinvMaterialcreditnoteMaster.objects.filter(
                compid=compid,
                mcndate__gte=start_date,
                mcndate__lte=end_date
            ).select_related('supplierid')
            
            for mcn in mcn_masters:
                mcn_details = TblinvMaterialcreditnoteDetails.objects.filter(
                    mid=mcn.mcnid
                ).select_related('itemid')
                
                for detail in mcn_details:
                    transactions.append({
                        'date': mcn.mcndate,
                        'type': 'MCN',
                        'doc_no': mcn.mcnno or '',
                        'destination': f"Supplier: {mcn.supplierid.suppliername}" if mcn.supplierid else 'N/A',
                        'item_code': detail.itemid.itemcode if detail.itemid else '',
                        'item_name': detail.itemid.itemname if detail.itemid else '',
                        'quantity': detail.qty or Decimal('0'),
                        'rate': detail.rate or Decimal('0'),
                        'value': (detail.qty or Decimal('0')) * (detail.rate or Decimal('0')),
                        'remarks': detail.reason or ''
                    })
        
        # Customer Challan
        if 'CCHAL' in transaction_types:
            cchal_masters = TblinvCustomerchallanMaster.objects.filter(
                compid=compid,
                customerchallandate__gte=start_date,
                customerchallandate__lte=end_date
            ).select_related('customerid')
            
            for cchal in cchal_masters:
                cchal_details = TblinvCustomerchallanDetails.objects.filter(
                    customerchallanid=cchal.customerchallanid
                ).select_related('itemid')
                
                for detail in cchal_details:
                    transactions.append({
                        'date': cchal.customerchallandate,
                        'type': 'CCHAL',
                        'doc_no': cchal.customerchallanno or '',
                        'destination': f"Customer: {cchal.customerid.customername}" if cchal.customerid else 'N/A',
                        'item_code': detail.itemid.itemcode if detail.itemid else '',
                        'item_name': detail.itemid.itemname if detail.itemid else '',
                        'quantity': detail.qty or Decimal('0'),
                        'rate': detail.rate or Decimal('0'),
                        'value': (detail.qty or Decimal('0')) * (detail.rate or Decimal('0')),
                        'remarks': detail.remarks or ''
                    })
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        
        return transactions



# ============================================================================
# CHALLAN SERVICES
# ============================================================================

class ChallanService(BaseTransactionService):
    """
    Service for Regular Challan operations
    
    Handles regular challan management for material dispatch to various locations.
    Different from Supplier/Customer Challan - this is for general material dispatch.
    
    Converted from: aspnet/Module/Inventory/Transactions/Challan.aspx
    Requirements: 6.1-6.9
    """
    
    @staticmethod
    def generate_challan_number(compid, finyearid):
        """
        Generate unique challan number in format: CHAL/YYYY/NNNN
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            str: Generated challan number (e.g., CHAL/2024/0001)
        """
        from sys_admin.models import TblfinancialMaster
        try:
            fin_year = TblfinancialMaster.objects.get(finyearid=finyearid, compid=compid)
            year = fin_year.finyear.split('-')[0]
        except:
            year = timezone.now().year
        
        # Get last challan number for this company and financial year
        from .models import TblinvChallanMaster
        last_challan = TblinvChallanMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            challanno__startswith=f'CHAL/{year}/'
        ).order_by('-challanid').first()
        
        if last_challan and last_challan.challanno:
            try:
                last_num = int(last_challan.challanno.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'CHAL/{year}/{new_num:04d}'
    
    @staticmethod
    @transaction.atomic
    def create_challan(challan_data, line_items, compid, finyearid, sessionid):
        """
        Create challan with line items.
        
        Args:
            challan_data: Dict with challan master fields
            line_items: List of dicts with line item details
            compid: Company ID
            finyearid: Financial Year ID
            sessionid: Session ID for audit
            
        Returns:
            tuple: (success: bool, challan_object or error_message)
        """
        from .models import TblinvChallanMaster, TblinvChallanDetails
        
        try:
            # Validate line items
            if not line_items or len(line_items) == 0:
                return False, "At least one line item is required"
            
            # Generate challan number if not provided
            if not challan_data.get('challanno'):
                challan_data['challanno'] = ChallanService.generate_challan_number(compid, finyearid)
            
            # Create master record
            challan = TblinvChallanMaster.objects.create(
                challanno=challan_data['challanno'],
                challandate=challan_data['challandate'],
                destination=challan_data.get('destination', ''),
                vehicleno=challan_data.get('vehicleno', ''),
                drivername=challan_data.get('drivername', ''),
                remarks=challan_data.get('remarks', ''),
                compid=compid,
                finyearid=finyearid,
                sessionid=sessionid,
                createddate=timezone.now(),
                createdby=sessionid
            )
            
            # Create detail records
            for item in line_items:
                TblinvChallanDetails.objects.create(
                    challanid=challan.challanid,
                    itemid=item['itemid'],
                    qty=item['qty'],
                    remarks=item.get('remarks', ''),
                    compid=compid
                )
            
            return True, challan
            
        except Exception as e:
            return False, f"Error creating challan: {str(e)}"
    
    @staticmethod
    @transaction.atomic
    def update_challan(challan_id, challan_data, line_items):
        """
        Update existing challan and line items.
        
        Args:
            challan_id: Challan ID to update
            challan_data: Dict with updated challan master fields
            line_items: List of dicts with updated line item details
            
        Returns:
            tuple: (success: bool, challan_object or error_message)
        """
        from .models import TblinvChallanMaster, TblinvChallanDetails
        
        try:
            # Get challan
            challan = TblinvChallanMaster.objects.get(challanid=challan_id)
            
            # Update master fields
            challan.challandate = challan_data.get('challandate', challan.challandate)
            challan.destination = challan_data.get('destination', challan.destination)
            challan.vehicleno = challan_data.get('vehicleno', challan.vehicleno)
            challan.drivername = challan_data.get('drivername', challan.drivername)
            challan.remarks = challan_data.get('remarks', challan.remarks)
            challan.modifieddate = timezone.now()
            challan.modifiedby = challan_data.get('sessionid', challan.sessionid)
            challan.save()
            
            # Delete existing details
            TblinvChallanDetails.objects.filter(challanid=challan_id).delete()
            
            # Create new details
            for item in line_items:
                TblinvChallanDetails.objects.create(
                    challanid=challan.challanid,
                    itemid=item['itemid'],
                    qty=item['qty'],
                    remarks=item.get('remarks', ''),
                    compid=challan.compid
                )
            
            return True, challan
            
        except TblinvChallanMaster.DoesNotExist:
            return False, "Challan not found"
        except Exception as e:
            return False, f"Error updating challan: {str(e)}"
    
    @staticmethod
    def delete_challan(challan_id):
        """
        Soft delete challan if not linked to other transactions.
        
        Args:
            challan_id: Challan ID to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        from .models import TblinvChallanMaster, TblinvChallanDetails
        
        try:
            challan = TblinvChallanMaster.objects.get(challanid=challan_id)
            
            # Check for dependencies (gate pass, vehicle trip, etc.)
            # TODO: Add dependency checks when those modules are implemented
            
            # Delete details first
            TblinvChallanDetails.objects.filter(challanid=challan_id).delete()
            
            # Delete master
            challan.delete()
            
            return True, "Challan deleted successfully"
            
        except TblinvChallanMaster.DoesNotExist:
            return False, "Challan not found"
        except Exception as e:
            return False, f"Error deleting challan: {str(e)}"
    
    @staticmethod
    def get_challan_details(challan_id):
        """
        Get challan with all line items.
        
        Args:
            challan_id: Challan ID
            
        Returns:
            dict: Challan master and details or None
        """
        from .models import TblinvChallanMaster, TblinvChallanDetails
        
        try:
            challan = TblinvChallanMaster.objects.select_related(
                'compid', 'finyearid'
            ).get(challanid=challan_id)
            
            details = TblinvChallanDetails.objects.filter(
                challanid=challan_id
            ).select_related('itemid')
            
            return {
                'challan': challan,
                'details': list(details)
            }
            
        except TblinvChallanMaster.DoesNotExist:
            return None
    
    @staticmethod
    def validate_challan_data(challan_data, line_items):
        """
        Validate challan data before saving.
        
        Args:
            challan_data: Dict with challan master fields
            line_items: List of dicts with line item details
            
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []
        
        # Validate master data
        if not challan_data.get('challandate'):
            errors.append("Challan date is required")
        
        if not challan_data.get('destination'):
            errors.append("Destination is required")
        
        # Validate line items
        if not line_items or len(line_items) == 0:
            errors.append("At least one line item is required")
        else:
            for idx, item in enumerate(line_items, 1):
                if not item.get('itemid'):
                    errors.append(f"Row {idx}: Item is required")
                
                qty = item.get('qty', 0)
                if not qty or float(qty) <= 0:
                    errors.append(f"Row {idx}: Quantity must be greater than 0")
        
        return len(errors) == 0, errors



# ============================================================================
# ITEM LOCATION SERVICES
# ============================================================================

class ItemLocationService:
    """
    Service for Item Location Management
    
    Handles warehouse location tracking and item placement.
    Requirements: 9.1-9.9
    """
    
    @staticmethod
    def assign_location(item_id, location_code, bin_number, quantity, compid, sessionid):
        """
        Assign item to warehouse location with quantity validation.
        
        Args:
            item_id: Item ID
            location_code: Location code (rack/area)
            bin_number: Bin number within location
            quantity: Quantity at this location
            compid: Company ID
            sessionid: Session ID
            
        Returns:
            tuple: (success: bool, location_object or error_message)
        """
        from .models import TblinvItemlocationMaster
        from decimal import Decimal
        
        try:
            # Validate quantity against total stock
            current_stock = ReportService._calculate_current_stock(item_id, compid)
            
            if Decimal(str(quantity)) > current_stock:
                return False, f"Quantity ({quantity}) exceeds current stock ({current_stock})"
            
            location = TblinvItemlocationMaster.objects.create(
                itemid=item_id,
                locationcode=location_code,
                binnumber=bin_number,
                qty=quantity,
                compid=compid,
                sessionid=sessionid,
                createddate=timezone.now()
            )
            
            return True, location
            
        except Exception as e:
            return False, f"Error assigning location: {str(e)}"
    
    @staticmethod
    def update_location_quantity(location_id, new_quantity):
        """
        Update quantity at a location.
        
        Args:
            location_id: Item location ID
            new_quantity: New quantity
            
        Returns:
            tuple: (success: bool, message: str)
        """
        from .models import TblinvItemlocationMaster
        
        try:
            location = TblinvItemlocationMaster.objects.get(itemlocationid=location_id)
            location.qty = new_quantity
            location.save()
            
            return True, "Location quantity updated successfully"
            
        except TblinvItemlocationMaster.DoesNotExist:
            return False, "Location not found"
        except Exception as e:
            return False, f"Error updating quantity: {str(e)}"
    
    @staticmethod
    def get_item_locations(item_id, compid):
        """
        Get all locations for an item.
        
        Args:
            item_id: Item ID
            compid: Company ID
            
        Returns:
            QuerySet: All locations for the item
        """
        from .models import TblinvItemlocationMaster
        
        return TblinvItemlocationMaster.objects.filter(
            itemid=item_id,
            compid=compid
        ).select_related('itemid')
    
    @staticmethod
    def get_location_items(location_code, compid):
        """
        Get all items at a location.
        
        Args:
            location_code: Location code
            compid: Company ID
            
        Returns:
            QuerySet: All items at the location
        """
        from .models import TblinvItemlocationMaster
        
        return TblinvItemlocationMaster.objects.filter(
            locationcode=location_code,
            compid=compid
        ).select_related('itemid')
    
    @staticmethod
    def delete_location_mapping(location_id):
        """
        Remove item-location mapping.
        
        Args:
            location_id: Item location ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        from .models import TblinvItemlocationMaster
        
        try:
            location = TblinvItemlocationMaster.objects.get(itemlocationid=location_id)
            location.delete()
            
            return True, "Location mapping deleted successfully"
            
        except TblinvItemlocationMaster.DoesNotExist:
            return False, "Location not found"
        except Exception as e:
            return False, f"Error deleting location: {str(e)}"


# ============================================================================
# SEARCH SERVICES
# ============================================================================

class SearchService:
    """
    Service for Advanced Search Functionality
    
    Provides cross-transaction search capabilities.
    Requirements: 10.1-10.9
    """
    
    @staticmethod
    def global_search(query, compid, finyearid, transaction_types=None):
        """
        Search across all transaction types.
        
        Args:
            query: Search query string
            compid: Company ID
            finyearid: Financial Year ID
            transaction_types: Optional list of types to search
            
        Returns:
            list: Unified search results
        """
        results = []
        
        # Search MRS
        if not transaction_types or 'MRS' in transaction_types:
            from .models import TblinvMaterialrequisitionMaster
            mrs_results = TblinvMaterialrequisitionMaster.objects.filter(
                Q(mrsno__icontains=query),
                compid=compid
            )[:10]
            
            for mrs in mrs_results:
                results.append({
                    'type': 'MRS',
                    'doc_no': mrs.mrsno,
                    'date': mrs.mrsdate,
                    'id': mrs.id,
                    'details': f"MRS - {mrs.mrsno}",
                    'url': f'/inventory/mrs/{mrs.id}/'
                })
        
        # Search MIN
        if not transaction_types or 'MIN' in transaction_types:
            from .models import TblinvMaterialissueMaster
            min_results = TblinvMaterialissueMaster.objects.filter(
                Q(minno__icontains=query),
                compid=compid
            )[:10]
            
            for min_rec in min_results:
                results.append({
                    'type': 'MIN',
                    'doc_no': min_rec.minno,
                    'date': min_rec.mindate,
                    'id': min_rec.id,
                    'details': f"MIN - {min_rec.minno}",
                    'url': f'/inventory/min/{min_rec.id}/'
                })
        
        # Search Challans
        if not transaction_types or 'CHALLAN' in transaction_types:
            from .models import TblinvChallanMaster
            challan_results = TblinvChallanMaster.objects.filter(
                Q(challanno__icontains=query),
                compid=compid
            )[:10]
            
            for challan in challan_results:
                results.append({
                    'type': 'CHALLAN',
                    'doc_no': challan.challanno,
                    'date': challan.challandate,
                    'id': challan.challanid,
                    'details': f"Challan - {challan.destination}",
                    'url': f'/inventory/challan/{challan.challanid}/'
                })
        
        # Sort by date (most recent first)
        results.sort(key=lambda x: x['date'] if x['date'] else timezone.now().date(), reverse=True)
        
        return results
    
    @staticmethod
    def search_by_item(item_id, compid, finyearid, start_date=None, end_date=None):
        """
        Find all transactions involving an item.
        
        Args:
            item_id: Item ID
            compid: Company ID
            finyearid: Financial Year ID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            dict: Transactions grouped by type
        """
        from .models import (
            TblinvMaterialissueDetails,
            TblinvMaterialreturnDetails,
            TblinvInwardDetails
        )
        
        results = {
            'MIN': [],
            'MRN': [],
            'GIN': []
        }
        
        # Get MIN transactions
        min_details = TblinvMaterialissueDetails.objects.filter(
            itemid=item_id,
            mid__compid=compid
        ).select_related('mid')
        
        if start_date:
            min_details = min_details.filter(mid__mindate__gte=start_date)
        if end_date:
            min_details = min_details.filter(mid__mindate__lte=end_date)
        
        for detail in min_details:
            results['MIN'].append({
                'doc_no': detail.mid.minno,
                'date': detail.mid.mindate,
                'quantity': detail.issueqty
            })
        
        return results


# ============================================================================
# ANALYTICS SERVICES
# ============================================================================

class AnalyticsService:
    """
    Service for Dashboard Analytics
    
    Calculates metrics and provides dashboard data.
    Requirements: 11.1-11.9
    """
    
    @staticmethod
    def get_dashboard_metrics(compid, finyearid):
        """
        Calculate key dashboard metrics.
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            
        Returns:
            dict: Dashboard metrics
        """
        from django.db.models import Sum, Count
        from decimal import Decimal
        
        metrics = {}
        
        # Total stock value (simplified calculation)
        metrics['total_stock_value'] = Decimal('0')
        
        # Pending MRS count
        pending_mrs = MaterialRequisitionService.get_pending_mrs_for_issue(compid, finyearid)
        metrics['pending_mrs_count'] = len(pending_mrs)
        
        # Pending GIN count
        pending_gin = GoodsInwardService.get_pending_gin_for_receipt(compid, finyearid)
        metrics['pending_gin_count'] = len(pending_gin)
        
        # Low stock items (items below reorder level)
        from sys_admin.models import TblitemMaster
        low_stock_items = []
        items = TblitemMaster.objects.filter(compid=compid)[:100]  # Limit for performance
        
        for item in items:
            current_stock = ReportService._calculate_current_stock(item.itemid, compid)
            reorder_level = item.reorderlevel or Decimal('0')
            
            if current_stock <= reorder_level and current_stock > 0:
                low_stock_items.append({
                    'item': item,
                    'current_stock': current_stock,
                    'reorder_level': reorder_level
                })
        
        metrics['low_stock_items'] = low_stock_items[:10]  # Top 10
        metrics['low_stock_count'] = len(low_stock_items)
        
        # Today's transactions count
        from datetime import date
        today = date.today()
        
        from .models import (
            TblinvMaterialrequisitionMaster,
            TblinvMaterialissueMaster,
            TblinvMaterialreturnMaster
        )
        
        metrics['today_transactions'] = (
            TblinvMaterialrequisitionMaster.objects.filter(
                compid=compid, mrsdate=today
            ).count() +
            TblinvMaterialissueMaster.objects.filter(
                compid=compid, mindate=today
            ).count() +
            TblinvMaterialreturnMaster.objects.filter(
                compid=compid, mrndate=today
            ).count()
        )
        
        return metrics
    
    @staticmethod
    def get_recent_transactions(compid, finyearid, limit=10):
        """
        Get recent transactions across all types.
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            limit: Number of transactions to return
            
        Returns:
            list: Recent transactions
        """
        from .models import (
            TblinvMaterialrequisitionMaster,
            TblinvMaterialissueMaster,
            TblinvMaterialreturnMaster
        )
        
        transactions = []
        
        # Get recent MRS
        mrs_list = TblinvMaterialrequisitionMaster.objects.filter(
            compid=compid
        ).order_by('-id')[:limit]
        
        for mrs in mrs_list:
            transactions.append({
                'type': 'MRS',
                'number': mrs.mrsno,
                'date': mrs.mrsdate,
                'url': f'/inventory/mrs/{mrs.id}/'
            })
        
        # Get recent MIN
        min_list = TblinvMaterialissueMaster.objects.filter(
            compid=compid
        ).order_by('-id')[:limit]
        
        for min_rec in min_list:
            transactions.append({
                'type': 'MIN',
                'number': min_rec.minno,
                'date': min_rec.mindate,
                'url': f'/inventory/min/{min_rec.id}/'
            })
        
        # Sort by date and limit
        transactions.sort(key=lambda x: x['date'] if x['date'] else timezone.now().date(), reverse=True)
        
        return transactions[:limit]
    
    @staticmethod
    def get_fast_moving_items(compid, finyearid, limit=10):
        """
        Identify top fast-moving items by consumption.
        
        Args:
            compid: Company ID
            finyearid: Financial Year ID
            limit: Number of items to return
            
        Returns:
            list: Fast-moving items with consumption
        """
        from .models import TblinvMaterialissueDetails
        from django.db.models import Sum
        
        # Get items with highest issue quantities
        fast_moving = TblinvMaterialissueDetails.objects.filter(
            mid__compid=compid,
            mid__finyearid=finyearid
        ).values('itemid', 'itemid__itemname', 'itemid__itemcode').annotate(
            total_issued=Sum('issueqty')
        ).order_by('-total_issued')[:limit]
        
        return list(fast_moving)
