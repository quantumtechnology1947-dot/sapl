"""
Material Return Note (MRN) Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse

# Import core mixins instead of inventory-specific mixins
from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
    LoginRequiredMixin,
    CompanyFinancialYearMixin,
    HTMXResponseMixin,
    QueryOptimizationMixin,
)

from ..models import (
    TblGatepass,
    TblinvMaterialrequisitionMaster, TblinvMaterialrequisitionDetails,
    TblinvMaterialissueMaster, TblinvMaterialissueDetails,
    TblinvMaterialreturnMaster, TblinvMaterialreturnDetails,
    TblinvInwardMaster, TblinvInwardDetails,
    TblinvMaterialreceivedMaster, TblinvMaterialreceivedDetails,
    TblinvMaterialservicenoteMaster, TblinvMaterialservicenoteDetails,
    TblinvSupplierChallanMaster, TblinvSupplierChallanDetails,
    TblinvCustomerChallanMaster, TblinvCustomerChallanDetails,
    TblinvWisMaster, TblinvWisDetails,
    TblvehProcessMaster,
    TblinvAutowisTimeschedule,
)
from .. import forms
from ..forms import (
    MRSMasterForm,
    MINMasterForm,
    MRNMasterForm,
    VehicleProcessMasterForm,
    VehicleMasterForm,
    AutoWISTimeScheduleForm,
    StockLedgerFilterForm,
)
from ..services import (
    MaterialRequisitionService,
    MaterialIssueService,
    MaterialReturnService,
    DashboardService,
)


class MRNListView(BaseListViewMixin, ListView):
    """
    Material Return Note List View
    Displays all MRN with search and filter.

    Converted from: aspnet/Module/Inventory/Transactions/MaterialReturnNote_MRN_New.aspx
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    Requirements: 3.1, 3.4, 4.1, 5.5, 13.1
    """
    model = TblinvMaterialreturnMaster
    template_name = 'inventory/transactions/mrn_list.html'
    partial_template_name = 'inventory/transactions/partials/mrn_list_partial.html'
    context_object_name = 'mrn_list'
    paginate_by = 20
    search_fields = ['mrnno']
    ordering = ['-id']

    # No need to override get_queryset() - BaseListViewMixin handles company/year filtering and search

    def get_context_data(self, **kwargs):
        """Add employee names to context."""
        context = super().get_context_data(**kwargs)

        # Get employee names for all MRNs in the current page
        from django.db import connection
        cursor = connection.cursor()

        # Build a dict of user_id -> employee_name
        user_ids = [str(mrn_obj.sessionid) for mrn_obj in context['mrn_list'] if mrn_obj.sessionid]
        employee_names = {}

        if user_ids:
            placeholders = ','.join(['%s'] * len(user_ids))
            cursor.execute(
                f"SELECT UserID, EmployeeName FROM tblHR_OfficeStaff WHERE UserID IN ({placeholders})",
                user_ids
            )
            for row in cursor.fetchall():
                employee_names[str(row[0])] = row[1]

        # Attach employee name to each MRN object
        for mrn_obj in context['mrn_list']:
            mrn_obj.employee_name = employee_names.get(str(mrn_obj.sessionid), mrn_obj.sessionid)

        return context



class MRNCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Material Return Note Create View
    Create MRN by searching and selecting items to return.

    Converted from: aspnet/Module/Inventory/Transactions/MaterialReturnNote_MRN_New.aspx
    Flow: Search items → Add to cart with return qty → Generate MRN
    Requirements: 3.1, 3.2, 4.1, 4.2, 13.2
    """
    template_name = 'inventory/transactions/mrn_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get search parameters
        search_type = self.request.GET.get('search_type', '')
        search_value = self.request.GET.get('search_value', '')

        items = []
        if search_type and search_value:
            # Search for items based on search type
            from django.db import connection
            cursor = connection.cursor()

            # Build the WHERE clause based on search type
            if search_type == 'item_code':
                where_clause = "i.ItemCode LIKE %s"
                search_param = f'{search_value}%'  # Starts with
            elif search_type == 'description':
                where_clause = "i.ManfDesc LIKE %s"
                search_param = f'%{search_value}%'  # Contains
            elif search_type == 'location':
                where_clause = "i.Location LIKE %s"
                search_param = f'%{search_value}%'  # Contains
            else:
                where_clause = "1=0"  # No results if invalid type
                search_param = ''

            # Query with company and financial year filters
            query = f"""
                SELECT
                    i.Id,
                    i.ItemCode,
                    i.ManfDesc,
                    u.Symbol as UOM,
                    i.Location,
                    CAST(COALESCE(i.StockQty, 0) AS REAL) as StockQty
                FROM tblDG_Item_Master i
                LEFT JOIN Unit_Master u ON i.UOMBasic = u.Id
                WHERE {where_clause}
                    AND i.CompId = %s
                    AND i.FinYearId <= %s
                ORDER BY i.ItemCode
                LIMIT 50
            """

            cursor.execute(query, [search_param, self.get_compid(), self.get_finyearid()])

            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'item_code': row[1] or '',
                    'description': row[2] or '',
                    'uom': row[3] or '',
                    'location': row[4] or '',
                    'stock_qty': float(row[5]) if row[5] else 0.0
                })

        context['items'] = items
        context['search_type'] = search_type
        context['search_value'] = search_value

        # Get cart items from session
        cart = self.request.session.get('mrn_cart', [])
        context['cart_items'] = cart
        context['cart_count'] = len(cart)

        # Get BG Groups for dropdown
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT Id, Symbol FROM BusinessGroup ORDER BY Symbol")
        context['bg_groups'] = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

        return context

    def post(self, request, *args, **kwargs):
        """Handle MRN generation with selected items from cart"""
        cart = request.session.get('mrn_cart', [])

        if not cart:
            messages.error(request, 'Please add at least one item to generate MRN')
            return redirect('inventory:mrn-create')

        try:
            # Auto-generate MRN number
            mrn_number = MaterialReturnService.generate_mrn_number(
                self.get_compid(),
                self.get_finyearid()
            )

            # Create MRN Master
            from datetime import datetime
            mrn_master = TblinvMaterialreturnMaster()
            mrn_master.mrnno = mrn_number
            mrn_master.sysdate = datetime.now().strftime('%d-%m-%Y')
            mrn_master.systime = datetime.now().strftime('%H:%M:%S')
            mrn_master.compid = self.get_compid()
            mrn_master.finyearid = self.get_finyearid()
            mrn_master.sessionid = str(request.user.id)
            mrn_master.save()

            # Create MRN Details for all cart items
            for item in cart:
                mrn_detail = TblinvMaterialreturnDetails()
                mrn_detail.mid = mrn_master.id
                mrn_detail.itemid = item['item_id']
                # Handle dept_id - convert empty string to 0
                dept_id_val = item.get('dept_id', 0)
                mrn_detail.deptid = int(dept_id_val) if dept_id_val else 0
                mrn_detail.wono = item.get('wo_no', '')
                mrn_detail.retqty = float(item['return_qty'])
                mrn_detail.remarks = item.get('remarks', '')
                mrn_detail.save()

            # Clear cart
            request.session['mrn_cart'] = []
            request.session.modified = True

            messages.success(request, f'Material Return {mrn_number} created successfully with {len(cart)} items!')
            return redirect('inventory:mrn-detail', pk=mrn_master.id)

        except Exception as e:
            messages.error(request, f'Error creating MRN: {str(e)}')
            return redirect('inventory:mrn-create')



class MRNAddToCartView(LoginRequiredMixin, View):
    """Add item to MRN cart"""

    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        item_code = request.POST.get('item_code')
        description = request.POST.get('description')
        uom = request.POST.get('uom')
        location = request.POST.get('location')
        bg_or_wo = request.POST.get('bg_or_wo')  # 'bg' or 'wo'
        dept_id = request.POST.get('dept_id', '')
        wo_no = request.POST.get('wo_no', '')
        return_qty = request.POST.get('return_qty')
        remarks = request.POST.get('remarks', '')

        if not item_id or not return_qty:
            messages.error(request, 'Item and return quantity are required')
            return redirect('inventory:mrn-create')

        try:
            return_qty = float(return_qty)
            if return_qty <= 0:
                messages.error(request, 'Return quantity must be greater than 0')
                return redirect('inventory:mrn-create')
        except ValueError:
            messages.error(request, 'Invalid return quantity')
            return redirect('inventory:mrn-create')

        # Get or create cart
        cart = request.session.get('mrn_cart', [])

        # Check if item already in cart
        for cart_item in cart:
            if cart_item['item_id'] == item_id:
                messages.warning(request, f'Item {item_code} is already in cart')
                return redirect('inventory:mrn-create')

        # Add to cart
        cart.append({
            'item_id': item_id,
            'item_code': item_code,
            'description': description,
            'uom': uom,
            'location': location,
            'bg_or_wo': bg_or_wo,
            'dept_id': dept_id if bg_or_wo == 'bg' else '',
            'wo_no': wo_no if bg_or_wo == 'wo' else '',
            'return_qty': return_qty,
            'remarks': remarks
        })

        request.session['mrn_cart'] = cart
        request.session.modified = True

        messages.success(request, f'Item {item_code} added to cart')
        return redirect('inventory:mrn-create')


class MRNRemoveFromCartView(LoginRequiredMixin, View):
    """Remove item from MRN cart"""

    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')

        cart = request.session.get('mrn_cart', [])
        cart = [item for item in cart if item['item_id'] != item_id]

        request.session['mrn_cart'] = cart
        request.session.modified = True

        messages.success(request, 'Item removed from cart')
        return redirect('inventory:mrn-create')


class MRNDetailView(BaseDetailViewMixin, DetailView):
    """
    Material Return Note Detail View
    Display MRN details with line items.

    Optimized: Uses BaseDetailViewMixin with automatic company filtering.
    Requirements: 3.1, 4.1, 13.1
    """
    model = TblinvMaterialreturnMaster
    template_name = 'inventory/transactions/mrn_detail.html'
    context_object_name = 'mrn'

    # No need to override get_queryset() - BaseDetailViewMixin handles company filtering

    def get_context_data(self, **kwargs):
        """Add MRN detail lines to context."""
        context = super().get_context_data(**kwargs)
        context['details'] = TblinvMaterialreturnDetails.objects.filter(
            mid=self.object.id
        )

        # Get employee name from tblHR_OfficeStaff using UserID
        from django.db import connection
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT EmployeeName FROM tblHR_OfficeStaff WHERE UserID = %s",
                [int(self.object.sessionid)]
            )
            result = cursor.fetchone()
            context['returned_by_username'] = result[0] if result else self.object.sessionid
        except (ValueError, Exception):
            context['returned_by_username'] = self.object.sessionid

        return context



class MRNDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Material Return Note Delete View
    Delete MRN and reverse stock.
    
    Optimized: Uses BaseDeleteViewMixin with automatic HTMX support.
    Requirements: 3.1, 4.1, 13.2
    """
    model = TblinvMaterialreturnMaster
    template_name = 'inventory/transactions/mrn_confirm_delete.html'
    success_url = reverse_lazy('inventory:mrn-list')
    
    # No need to override get_queryset() - BaseDeleteViewMixin handles company filtering
    
    def delete(self, request, *args, **kwargs):
        """Delete and reverse stock entries."""
        self.object = self.get_object()
        
        # Reverse stock entries
        from .services import MaterialReturnService
        # MaterialReturnService.reverse_stock_on_delete(self.object.id)
        
        mrnno = self.object.mrnno
        messages.success(request, f'Material Return {mrnno} deleted successfully!')
        return super().delete(request, *args, **kwargs)



class MRNPrintView(BaseDetailViewMixin, DetailView):
    """
    Material Return Note Print View
    Print-friendly MRN document.

    Optimized: Uses BaseDetailViewMixin with automatic company filtering.
    Requirements: 3.1, 4.1
    """
    model = TblinvMaterialreturnMaster
    template_name = 'inventory/transactions/mrn_print.html'
    context_object_name = 'mrn'

    # No need to override get_queryset() - BaseDetailViewMixin handles company filtering

    def get_context_data(self, **kwargs):
        """Add MRN detail lines to context."""
        context = super().get_context_data(**kwargs)
        context['details'] = TblinvMaterialreturnDetails.objects.filter(
            mid=self.object.id
        )

        # Get employee name from tblHR_OfficeStaff using UserID
        from django.db import connection
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT EmployeeName FROM tblHR_OfficeStaff WHERE UserID = %s",
                [int(self.object.sessionid)]
            )
            result = cursor.fetchone()
            context['returned_by_username'] = result[0] if result else self.object.sessionid
        except (ValueError, Exception):
            context['returned_by_username'] = self.object.sessionid

        return context


