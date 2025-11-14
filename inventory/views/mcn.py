"""
Inventory Module Views
Modernized with core mixins and query optimization.
Requirements: 3.1, 3.4, 5.5, 13.1, 13.2, 13.3
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
    MRSMasterForm,  # MRSDetailFormSet,  # Commented out - formsets don't work with managed=False models
    MINMasterForm,  # MINDetailFormSet,  # Commented out
    MRNMasterForm,  # MRNDetailFormSet,  # Commented out
    VehicleProcessMasterForm,
    VehicleMasterForm,
    AutoWISTimeScheduleForm,
    StockLedgerFilterForm,
)
# NOTE: All formsets have been commented out in forms.py due to foreign key issues with managed=False models
from ..services import (
    MaterialRequisitionService,
    MaterialIssueService,
    MaterialReturnService,
    DashboardService,
)




class MCNListView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """MCN List View"""
    # model = Tblmcnmaster  # Model does not exist
    template_name = 'inventory/transactions/mcn_list.html'
    context_object_name = 'mcns'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('supplierid')
        
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(mcnno__icontains=search) |
                Q(supplierid__suppliername__icontains=search)
            )
        
        return queryset.order_by('-mcndate', '-mcnid')




class MCNCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """MCN Create View"""
    # model = Tblmcnmaster  # Model does not exist
    # form_class = MCNMasterForm  # Form commented out
    template_name = 'inventory/transactions/mcn_form.html'
    success_url = reverse_lazy('inventory:mcn-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.request.session.get('compid', 1)
        kwargs['finyearid'] = self.request.session.get('finyearid', 1)
        kwargs['sessionid'] = self.request.session.get('sessionid', 1)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['detail_formset'] = MCNDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = MCNDetailFormSet(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']
        
        if detail_formset.is_valid():
            from ..services import MaterialCreditNoteService
            compid = self.request.session.get('compid', 1)
            finyearid = self.request.session.get('finyearid', 1)
            
            mcn_number = MaterialCreditNoteService.generate_mcn_number(compid, finyearid)
            form.instance.mcnno = mcn_number
            
            self.object = form.save()
            detail_formset.instance = self.object
            detail_formset.save()
            
            messages.success(self.request, f'MCN {mcn_number} created successfully!')
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)




class MCNDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """MCN Detail View"""
    # model = Tblmcnmaster  # Model does not exist
    template_name = 'inventory/transactions/mcn_detail.html'
    context_object_name = 'mcn'
    pk_url_kwarg = 'mcnid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        details = Tblmcndetail.objects.filter(mcnid=self.object).select_related('itemid')
        context['details'] = details
        return context




class MCNDeleteView(LoginRequiredMixin, CompanyFinancialYearMixin, DeleteView):
    """MCN Delete View"""
    # model = Tblmcnmaster  # Model does not exist
    template_name = 'inventory/transactions/mcn_confirm_delete.html'
    success_url = reverse_lazy('inventory:mcn-list')
    pk_url_kwarg = 'mcnid'
    
    def delete(self, request, *args, **kwargs):
        mcn = self.get_object()
        messages.success(request, f'MCN {mcn.mcnno} deleted successfully!')
        return super().delete(request, *args, **kwargs)




class MCNPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """MCN Print View"""
    # model = Tblmcnmaster  # Model does not exist
    template_name = 'inventory/transactions/mcn_print.html'
    context_object_name = 'mcn'
    pk_url_kwarg = 'mcnid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        details = Tblmcndetail.objects.filter(mcnid=self.object).select_related('itemid')
        context['details'] = details
        return context


# ============================================================================
# CLOSING STOCK VIEWS
# ============================================================================



