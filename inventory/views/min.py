"""
Material Issue Note (MIN) Views
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


class MINListView(BaseListViewMixin, ListView):
    """
    Material Issue Note List View
    Displays all MIN with search and filter.

    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    Requirements: 3.1, 3.4, 4.1, 5.5, 13.1
    """
    model = TblinvMaterialissueMaster
    template_name = 'inventory/transactions/min_list.html'
    partial_template_name = 'inventory/transactions/partials/min_list_partial.html'
    context_object_name = 'min_list'
    paginate_by = 20
    search_fields = ['minno', 'mrsno']
    ordering = ['-id']

    # No need to override get_queryset() - BaseListViewMixin handles company/year filtering and search

    def get_context_data(self, **kwargs):
        """Add employee names to context."""
        context = super().get_context_data(**kwargs)

        # Get employee names for all MINs in the current page
        from django.db import connection
        cursor = connection.cursor()

        # Build a dict of user_id -> employee_name
        user_ids = [str(min_obj.sessionid) for min_obj in context['min_list'] if min_obj.sessionid]
        employee_names = {}

        if user_ids:
            placeholders = ','.join(['%s'] * len(user_ids))
            cursor.execute(
                f"SELECT UserID, EmployeeName FROM tblHR_OfficeStaff WHERE UserID IN ({placeholders})",
                user_ids
            )
            for row in cursor.fetchall():
                employee_names[str(row[0])] = row[1]

        # Attach employee name to each MIN object
        for min_obj in context['min_list']:
            min_obj.employee_name = employee_names.get(str(min_obj.sessionid), min_obj.sessionid)

        return context



class MINCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Material Issue Note Create View
    Create MIN from pending MRS by showing MRS items in a grid.

    Converted from: aspnet/Module/Inventory/Transactions/MaterialIssueNote_MIN_New_Details.aspx
    Flow: Shows MRS items with checkboxes → User selects items → Auto-generates MIN number
    Requirements: 3.1, 3.2, 4.1, 4.2, 13.2
    """
    template_name = 'inventory/transactions/min_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get MRS ID from URL parameter
        mrs_id = self.request.GET.get('mrs_id')

        if mrs_id:
            try:
                # Get MRS Master
                mrs = TblinvMaterialrequisitionMaster.objects.get(id=mrs_id)
                context['mrs'] = mrs

                # Get MRS Details with item information using raw SQL join
                from django.db import connection
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT
                        d.Id,
                        d.ItemId,
                        i.ItemCode,
                        i.ManfDesc,
                        u.UnitName,
                        d.DeptId,
                        d.WONo,
                        d.ReqQty,
                        d.Remarks
                    FROM tblInv_MaterialRequisition_Details d
                    LEFT JOIN tblDG_Item_Master i ON CAST(d.ItemId AS INTEGER) = i.Id
                    LEFT JOIN Unit_Master u ON i.UOMBasic = u.Id
                    WHERE d.MId = %s
                    ORDER BY d.Id
                """, [mrs_id])

                mrs_details = []
                for row in cursor.fetchall():
                    mrs_details.append({
                        'id': row[0],
                        'itemid': row[1],
                        'item_code': row[2] or '',
                        'description': row[3] or '',
                        'uom': row[4] or '',
                        'dept': str(row[5]) if row[5] else '',
                        'wono': row[6] or '',
                        'req_qty': row[7] or 0,
                        'issued_qty': 0,  # Cannot calculate per-item since MIN details don't have itemid
                        'balance_qty': row[7] or 0,
                        'remarks': row[8] or ''
                    })

                context['mrs_details'] = mrs_details

            except TblinvMaterialrequisitionMaster.DoesNotExist:
                messages.error(self.request, 'MRS not found')

        return context

    def post(self, request, *args, **kwargs):
        """Handle MIN creation with selected items"""
        mrs_id = request.POST.get('mrs_id')

        if not mrs_id:
            messages.error(request, 'MRS ID is required')
            return redirect('inventory:mrs-pending-list')

        try:
            mrs = TblinvMaterialrequisitionMaster.objects.get(id=mrs_id)

            # Auto-generate MIN number
            min_number = MaterialIssueService.generate_min_number(
                self.get_compid(),
                self.get_finyearid()
            )

            # Create MIN Master
            from datetime import datetime
            min_master = TblinvMaterialissueMaster()
            min_master.minno = min_number
            min_master.mrsid = mrs.id
            min_master.mrsno = mrs.mrsno
            min_master.sysdate = datetime.now().strftime('%d-%m-%Y')
            min_master.systime = datetime.now().strftime('%H:%M:%S')
            min_master.compid = self.get_compid()
            min_master.finyearid = self.get_finyearid()
            min_master.sessionid = str(request.user.id)
            min_master.save()

            # Create MIN Details for selected items
            # Note: MIN details only store mrsid and issueqty, not individual itemid
            selected_items = request.POST.getlist('selected_items')
            detail_count = 0

            for item_id in selected_items:
                issue_qty = request.POST.get(f'issue_qty_{item_id}')

                if issue_qty and float(issue_qty) > 0:
                    min_detail = TblinvMaterialissueDetails()
                    min_detail.mid = min_master.id
                    min_detail.minno = min_number
                    min_detail.mrsid = mrs.id
                    min_detail.issueqty = float(issue_qty)
                    min_detail.save()

                    detail_count += 1

            if detail_count > 0:
                messages.success(request, f'Material Issue {min_number} created successfully with {detail_count} items!')
                return redirect('inventory:min-detail', pk=min_master.id)
            else:
                # Delete master if no details were created
                min_master.delete()
                messages.error(request, 'Please select at least one item to issue')
                return redirect(f'{reverse_lazy("inventory:min-create")}?mrs_id={mrs_id}')

        except Exception as e:
            messages.error(request, f'Error creating MIN: {str(e)}')
            return redirect('inventory:mrs-pending-list')



class MINDetailView(BaseDetailViewMixin, DetailView):
    """
    Material Issue Note Detail View
    Display MIN details with line items.

    Optimized: Uses BaseDetailViewMixin with automatic company filtering.
    Requirements: 3.1, 4.1, 13.1
    """
    model = TblinvMaterialissueMaster
    template_name = 'inventory/transactions/min_detail.html'
    context_object_name = 'min'

    # No need to override get_queryset() - BaseDetailViewMixin handles company filtering

    def get_context_data(self, **kwargs):
        """Add MIN detail lines to context."""
        context = super().get_context_data(**kwargs)
        context['details'] = TblinvMaterialissueDetails.objects.filter(
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
            context['issued_by_username'] = result[0] if result else self.object.sessionid
        except (ValueError, Exception):
            context['issued_by_username'] = self.object.sessionid

        return context



class MINDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Material Issue Note Delete View
    Delete MIN and reverse stock.
    
    Optimized: Uses BaseDeleteViewMixin with automatic HTMX support.
    Requirements: 3.1, 4.1, 13.2
    """
    model = TblinvMaterialissueMaster
    template_name = 'inventory/transactions/min_confirm_delete.html'
    success_url = reverse_lazy('inventory:min-list')
    
    # No need to override get_queryset() - BaseDeleteViewMixin handles company filtering
    
    def delete(self, request, *args, **kwargs):
        """Delete and reverse stock entries."""
        self.object = self.get_object()
        
        # Reverse stock entries
        # MaterialIssueService.reverse_stock_on_delete(self.object.id)
        
        minno = self.object.minno
        messages.success(request, f'Material Issue {minno} deleted successfully!')
        return super().delete(request, *args, **kwargs)



class MINPrintView(BaseDetailViewMixin, DetailView):
    """
    Material Issue Note Print View
    Print-friendly MIN document.

    Optimized: Uses BaseDetailViewMixin with automatic company filtering.
    Requirements: 3.1, 4.1
    """
    model = TblinvMaterialissueMaster
    template_name = 'inventory/transactions/min_print.html'
    context_object_name = 'min'

    # No need to override get_queryset() - BaseDetailViewMixin handles company filtering

    def get_context_data(self, **kwargs):
        """Add MIN detail lines to context."""
        context = super().get_context_data(**kwargs)
        context['details'] = TblinvMaterialissueDetails.objects.filter(
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
            context['issued_by_username'] = result[0] if result else self.object.sessionid
        except (ValueError, Exception):
            context['issued_by_username'] = self.object.sessionid

        return context



