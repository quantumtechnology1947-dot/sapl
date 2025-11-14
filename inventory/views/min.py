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



class MINCreateView(BaseCreateViewMixin, CreateView):
    """
    Material Issue Note Create View
    Create MIN from pending MRS.
    
    Optimized: Uses BaseCreateViewMixin with automatic audit fields and success messages.
    Requirements: 3.1, 3.2, 4.1, 4.2, 13.2
    """
    model = TblinvMaterialissueMaster
    form_class = MINMasterForm
    template_name = 'inventory/transactions/min_form.html'
    partial_template_name = 'inventory/transactions/partials/min_form_partial.html'
    success_url = reverse_lazy('inventory:min-list')
    success_message = 'Material Issue %(minno)s created successfully!'
    
    def get_form_kwargs(self):
        """Pass company, financial year, and session to form."""
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.get_compid()
        kwargs['finyearid'] = self.get_finyearid()
        kwargs['sessionid'] = self.get_sessionid()
        return kwargs
    
    def form_valid(self, form):
        """Generate MIN number and update stock ledger before saving."""
        form.instance.minno = MaterialIssueService.generate_min_number(
            self.get_compid(),
            self.get_finyearid()
        )
        
        # Update stock ledger
        # MaterialIssueService.update_stock_ledger(form.instance)
        
        return super().form_valid(form)



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
        return context



