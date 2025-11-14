"""
Supplier and Customer Challan Views
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


class SupplierChallanListView(BaseListViewMixin, ListView):
    """
    Supplier Challan List View
    Display all supplier challans with search and status filtering
    
    Converted from: aspnet/Module/Inventory/Transactions/SupplierChallan_New.aspx
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    """
    model = TblinvSupplierChallanMaster
    template_name = 'inventory/transactions/supplier_challan_list.html'
    context_object_name = 'challans'
    paginate_by = 20
    search_fields = ['supplierchallanno']
    ordering = ['-id']
    
    # No need to override get_queryset() - BaseListViewMixin handles company/year filtering and search
    # No need to override get_context_data() - BaseListViewMixin handles search_query
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context



class SupplierChallanCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """
    Supplier Challan Create View
    Create new supplier challan with line items
    """
    model = TblinvSupplierChallanMaster
    # form_class = SupplierChallanMasterForm  # Form commented out - schema mismatch
    template_name = 'inventory/transactions/supplier_challan_form.html'
    success_url = reverse_lazy('inventory:supplier-challan-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.request.session.get('compid', 1)
        kwargs['finyearid'] = self.request.session.get('finyearid', 1)
        kwargs['sessionid'] = self.request.session.get('sessionid', 1)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['detail_formset'] = SupplierChallanDetailFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['detail_formset'] = SupplierChallanDetailFormSet(
                instance=self.object
            )
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']
        
        if detail_formset.is_valid():
            # Generate challan number
            from .services import SupplierChallanService
            compid = self.request.session.get('compid', 1)
            finyearid = self.request.session.get('finyearid', 1)
            
            challan_number = SupplierChallanService.generate_supplier_challan_number(
                compid, finyearid
            )
            form.instance.supplierchallanno = challan_number
            
            self.object = form.save()
            detail_formset.instance = self.object
            detail_formset.save()
            
            messages.success(
                self.request,
                f'Supplier Challan {challan_number} created successfully!'
            )
            
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)



class SupplierChallanDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    Supplier Challan Detail View
    Display challan details with balance quantities
    """
    model = TblinvSupplierChallanMaster
    template_name = 'inventory/transactions/supplier_challan_detail.html'
    context_object_name = 'challan'
    pk_url_kwarg = 'supplierchallanid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get detail items
        details = Tblsupplierchallandetail.objects.filter(
            supplierchallanid=self.object
        ).select_related('itemid')
        
        context['details'] = details
        
        # Calculate totals
        from decimal import Decimal
        total_sent = sum((d.qty or Decimal('0')) for d in details)
        total_received = sum((d.receivedqty or Decimal('0')) for d in details)
        total_balance = sum((d.balanceqty or Decimal('0')) for d in details)
        
        context['total_sent'] = total_sent
        context['total_received'] = total_received
        context['total_balance'] = total_balance
        
        # Determine status
        if total_balance == Decimal('0'):
            context['status'] = 'Cleared'
            context['status_class'] = 'bg-green-100 text-green-800'
        elif total_balance == total_sent:
            context['status'] = 'Pending'
            context['status_class'] = 'bg-yellow-100 text-yellow-800'
        else:
            context['status'] = 'Partially Cleared'
            context['status_class'] = 'bg-blue-100 text-blue-800'
        
        return context



class SupplierChallanDeleteView(LoginRequiredMixin, CompanyFinancialYearMixin, DeleteView):
    """
    Supplier Challan Delete View
    Delete supplier challan (only if not cleared)
    """
    model = TblinvSupplierChallanMaster
    template_name = 'inventory/transactions/supplier_challan_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier-challan-list')
    pk_url_kwarg = 'supplierchallanid'
    
    def delete(self, request, *args, **kwargs):
        challan = self.get_object()
        
        # Check if challan has been cleared
        details = Tblsupplierchallandetail.objects.filter(supplierchallanid=challan)
        from decimal import Decimal
        total_received = sum((d.receivedqty or Decimal('0')) for d in details)
        
        if total_received > Decimal('0'):
            messages.error(
                request,
                'Cannot delete challan that has been partially or fully cleared!'
            )
            return HttpResponseRedirect(reverse_lazy('inventory:supplier-challan-detail', kwargs={'supplierchallanid': challan.supplierchallanid}))
        
        messages.success(
            request,
            f'Supplier Challan {challan.supplierchallanno} deleted successfully!'
        )
        
        return super().delete(request, *args, **kwargs)



class SupplierChallanPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    Supplier Challan Print View
    Print-friendly delivery note
    """
    model = TblinvSupplierChallanMaster
    template_name = 'inventory/transactions/supplier_challan_print.html'
    context_object_name = 'challan'
    pk_url_kwarg = 'supplierchallanid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get detail items
        details = Tblsupplierchallandetail.objects.filter(
            supplierchallanid=self.object
        ).select_related('itemid')
        
        context['details'] = details
        
        return context



class SupplierChallanClearView(LoginRequiredMixin, CompanyFinancialYearMixin, FormView):
    """
    Supplier Challan Clear View
    Record received quantities (clearing workflow)
    """
    template_name = 'inventory/transactions/supplier_challan_clear.html'
    # form_class = SupplierChallanClearForm  # Form commented out
    
    def get_challan(self):
        supplierchallanid = self.kwargs.get('supplierchallanid')
        return get_object_or_404(TblinvSupplierChallanMaster, supplierchallanid=supplierchallanid)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        challan = self.get_challan()
        details = Tblsupplierchallandetail.objects.filter(
            supplierchallanid=challan
        ).select_related('itemid')
        kwargs['challan_details'] = details
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        challan = self.get_challan()
        details = Tblsupplierchallandetail.objects.filter(
            supplierchallanid=challan
        ).select_related('itemid')
        
        context['challan'] = challan
        context['details'] = details
        
        return context
    
    def form_valid(self, form):
        challan = self.get_challan()
        
        # Extract received quantities from form
        received_items = []
        for field_name, value in form.cleaned_data.items():
            if field_name.startswith('received_qty_') and value and value > 0:
                detail_id = int(field_name.replace('received_qty_', ''))
                received_items.append({
                    'detail_id': detail_id,
                    'received_qty': value
                })
        
        if not received_items:
            messages.warning(self.request, 'No received quantities entered!')
            return self.form_invalid(form)
        
        # Clear challan
        from .services import SupplierChallanService
        success = SupplierChallanService.clear_challan(
            challan.supplierchallanid,
            received_items
        )
        
        if success:
            messages.success(
                self.request,
                f'Supplier Challan {challan.supplierchallanno} cleared successfully!'
            )
            return HttpResponseRedirect(
                reverse_lazy('inventory:supplier-challan-detail', kwargs={'supplierchallanid': challan.supplierchallanid})
            )
        else:
            messages.error(self.request, 'Error clearing challan!')
            return self.form_invalid(form)



class SupplierChallanPendingListView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    Supplier Challan Pending List View
    Display challans with pending balance
    """
    model = TblinvSupplierChallanMaster
    template_name = 'inventory/transactions/supplier_challan_pending_list.html'
    context_object_name = 'challans'
    paginate_by = 20
    
    def get_queryset(self):
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)
        
        from .services import SupplierChallanService
        return SupplierChallanService.get_pending_challans(compid, finyearid)


# ============================================================================
# CUSTOMER CHALLAN VIEWS
# ============================================================================


class CustomerChallanListView(BaseListViewMixin, ListView):
    """
    Customer Challan List View
    Display all customer challans with search
    
    Converted from: aspnet/Module/Inventory/Transactions/CustomerChallan_New.aspx
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    """
    model = TblinvCustomerChallanMaster
    template_name = 'inventory/transactions/customer_challan_list.html'
    context_object_name = 'challans'
    paginate_by = 20
    search_fields = ['ccno', 'wono']
    ordering = ['-id']
    
    # No need to override get_queryset() - BaseListViewMixin handles company/year filtering and search
    # No need to override get_context_data() - BaseListViewMixin handles search_query



class CustomerChallanCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """
    Customer Challan Create View
    Create new customer challan with line items
    """
    model = TblinvCustomerChallanMaster
    # form_class = CustomerChallanMasterForm  # Form commented out
    fields = ['ccno', 'customerid', 'wono']  # Basic fields from model
    template_name = 'inventory/transactions/customer_challan_form.html'
    success_url = reverse_lazy('inventory:customer-challan-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add CSS classes to form fields
        for field_name, field in form.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            })
        return form
    
    def form_valid(self, form):
        # Set audit fields
        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()
        
        form.instance.sysdate = sysdate
        form.instance.systime = systime
        form.instance.compid = self.request.session.get('compid', 1)
        form.instance.finyearid = self.request.session.get('finyearid', 1)
        form.instance.sessionid = self.request.session.get('sessionid', '1')
        
        self.object = form.save()
        
        messages.success(
            self.request,
            f'Customer Challan {form.instance.ccno} created successfully!'
        )
        
        return HttpResponseRedirect(self.get_success_url())



class CustomerChallanDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    Customer Challan Detail View
    Display challan details with work order reference
    """
    model = TblinvCustomerChallanMaster
    template_name = 'inventory/transactions/customer_challan_detail.html'
    context_object_name = 'challan'
    pk_url_kwarg = 'customerchallanid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get detail items
        details = Tblcustomerchallandetail.objects.filter(
            customerchallanid=self.object
        ).select_related('itemid')
        
        context['details'] = details
        
        # Calculate total quantity
        from decimal import Decimal
        total_qty = sum((d.qty or Decimal('0')) for d in details)
        context['total_qty'] = total_qty
        
        return context



class CustomerChallanDeleteView(LoginRequiredMixin, CompanyFinancialYearMixin, DeleteView):
    """
    Customer Challan Delete View
    Delete customer challan
    """
    model = TblinvCustomerChallanMaster
    template_name = 'inventory/transactions/customer_challan_confirm_delete.html'
    success_url = reverse_lazy('inventory:customer-challan-list')
    pk_url_kwarg = 'customerchallanid'
    
    def delete(self, request, *args, **kwargs):
        challan = self.get_object()
        
        messages.success(
            request,
            f'Customer Challan {challan.customerchallanno} deleted successfully!'
        )
        
        return super().delete(request, *args, **kwargs)



class CustomerChallanPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    Customer Challan Print View
    Print-friendly delivery note
    """
    model = TblinvCustomerChallanMaster
    template_name = 'inventory/transactions/customer_challan_print.html'
    context_object_name = 'challan'
    pk_url_kwarg = 'customerchallanid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get detail items
        details = Tblcustomerchallandetail.objects.filter(
            customerchallanid=self.object
        ).select_related('itemid')
        
        context['details'] = details
        
        return context



# ============================================================================
# GATE PASS VIEWS
# ============================================================================


class ChallanListView(BaseListViewMixin, ListView):
    """
    Regular Challan List View
    
    Displays all challans with search and date filtering.
    
    Converted from: aspnet/Module/Inventory/Transactions/Challan.aspx
    Requirements: 6.4
    """
    # model = TblinvChallanMaster  # Model does not exist
    template_name = 'inventory/challans/challan_list.html'
    context_object_name = 'challans'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            compid=self.get_compid(),
            finyearid=self.get_finyearid()
        ).order_by('-challanid')
        
        # Search by challan number
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(challanno__icontains=search)
        
        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            from datetime import datetime
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(challandate__gte=start_dt)
            except:
                pass
        
        if end_date:
            from datetime import datetime
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(challandate__lte=end_dt)
            except:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context



class ChallanCreateView(BaseCreateViewMixin, CreateView):
    """
    Regular Challan Create View
    
    Create new challan with line items.
    
    Converted from: aspnet/Module/Inventory/Transactions/Challan.aspx
    Requirements: 6.1, 6.2
    """
    # model = TblinvChallanMaster  # Model does not exist
    # form_class = ChallanMasterForm  # Form commented out
    template_name = 'inventory/challans/challan_form.html'
    success_url = reverse_lazy('inventory:challan-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.get_compid()
        kwargs['finyearid'] = self.get_finyearid()
        kwargs['sessionid'] = self.get_sessionid()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = ChallanDetailFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'compid': self.get_compid()}
            )
        else:
            context['formset'] = ChallanDetailFormSet(
                instance=self.object,
                form_kwargs={'compid': self.get_compid()}
            )
        
        # Generate challan number
        from .services import ChallanService
        context['challan_number'] = ChallanService.generate_challan_number(
            self.get_compid(),
            self.get_finyearid()
        )
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            # Save master
            self.object = form.save()
            
            # Save details
            formset.instance = self.object
            formset.save()
            
            messages.success(self.request, f'Challan {self.object.challanno} created successfully.')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)



class ChallanDetailView(BaseDetailViewMixin, DetailView):
    """
    Regular Challan Detail View
    
    Display challan with all line items.
    
    Converted from: aspnet/Module/Inventory/Transactions/Challan.aspx
    Requirements: 6.5
    """
    # model = TblinvChallanMaster  # Model does not exist
    template_name = 'inventory/challans/challan_detail.html'
    context_object_name = 'challan'
    pk_url_kwarg = 'challanid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get challan details
        context['details'] = TblinvChallanDetails.objects.filter(
            challanid=self.object.challanid
        ).select_related('itemid')
        
        return context



class ChallanUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Regular Challan Update View
    
    Edit an existing challan and its line items.
    """
    # model = TblinvChallanMaster  # Model does not exist
    # form_class = ChallanMasterForm  # Form commented out
    template_name = 'inventory/challans/challan_form.html'
    success_url = reverse_lazy('inventory:challan-list')
    pk_url_kwarg = 'challanid'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.get_compid()
        kwargs['finyearid'] = self.get_finyearid()
        kwargs['sessionid'] = self.get_sessionid()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ChallanDetailFormSet(
                self.request.POST, 
                instance=self.object,
                form_kwargs={'compid': self.get_compid()}
            )
        else:
            context['formset'] = ChallanDetailFormSet(
                instance=self.object,
                form_kwargs={'compid': self.get_compid()}
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, f'Challan {self.object.challanno} updated successfully.')
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)



class ChallanDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Regular Challan Delete View
    
    Delete challan with confirmation.
    
    Converted from: aspnet/Module/Inventory/Transactions/Challan_Delete.aspx
    Requirements: 6.7, 6.8
    """
    # model = TblinvChallanMaster  # Model does not exist
    template_name = 'inventory/challans/challan_confirm_delete.html'
    success_url = reverse_lazy('inventory:challan-list')
    pk_url_kwarg = 'challanid'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        from .services import ChallanService
        success, message = ChallanService.delete_challan(self.object.challanid)
        
        if success:
            messages.success(request, message)
            return redirect(self.success_url)
        else:
            messages.error(request, message)
            return redirect('inventory:challan-detail', challanid=self.object.challanid)



class ChallanPrintView(BaseDetailViewMixin, DetailView):
    """
    Regular Challan Print View
    
    Print-friendly challan layout.
    
    Converted from: aspnet/Module/Inventory/Transactions/Challan.aspx
    Requirements: 6.6
    """
    # model = TblinvChallanMaster  # Model does not exist
    template_name = 'inventory/challans/challan_print.html'
    context_object_name = 'challan'
    pk_url_kwarg = 'challanid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get challan details
        context['details'] = TblinvChallanDetails.objects.filter(
            challanid=self.object.challanid
        ).select_related('itemid')
        
        return context


# ============================================================================
# VEHICLE PROCESS MASTER VIEWS
# ============================================================================


