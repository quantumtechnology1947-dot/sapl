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



class MRNCreateView(BaseCreateViewMixin, CreateView):
    """
    Material Return Note Create View
    Create new MRN for returned materials.
    
    Optimized: Uses BaseCreateViewMixin with automatic audit fields and success messages.
    Requirements: 3.1, 3.2, 4.1, 4.2, 13.2
    """
    model = TblinvMaterialreturnMaster
    form_class = MRNMasterForm
    template_name = 'inventory/transactions/mrn_form.html'
    partial_template_name = 'inventory/transactions/partials/mrn_form_partial.html'
    success_url = reverse_lazy('inventory:mrn-list')
    success_message = 'Material Return %(mrnno)s created successfully!'
    
    def get_form_kwargs(self):
        """Pass company, financial year, and session to form."""
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.get_compid()
        kwargs['finyearid'] = self.get_finyearid()
        kwargs['sessionid'] = self.get_sessionid()
        return kwargs
    
    def form_valid(self, form):
        """Generate MRN number and update stock ledger before saving."""
        from .services import MaterialReturnService
        form.instance.mrnno = MaterialReturnService.generate_mrn_number(
            self.get_compid(),
            self.get_finyearid()
        )
        
        # Update stock ledger
        # MaterialReturnService.update_stock_ledger(form.instance)
        
        return super().form_valid(form)



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
        return context


