"""
Gate Pass Views
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


class GatePassListView(BaseListViewMixin, ListView):
    """
    Gate Pass List View
    Display all gate passes with search
    
    Converted from: aspnet/Module/Inventory/Transactions/GatePass_Insert.aspx
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    NOTE: Using TblGatepass - master/detail models dont exist
    """
    model = TblGatepass
    template_name = 'inventory/transactions/gate_pass_list.html'
    context_object_name = 'gatepasses'
    paginate_by = 20
    search_fields = ['chalanno', 'wono', 'description']
    ordering = ['-id']
    
    # No need to override get_queryset() - BaseListViewMixin handles search
    # No need to override get_context_data() - BaseListViewMixin handles search_query



class GatePassCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """Gate Pass Create View"""
    model = TblGatepass  # NOTE: Using TblGatepass - master/detail models dont exist
    # form_class = GatePassMasterForm  # Form commented out
    template_name = 'inventory/transactions/gate_pass_form.html'
    success_url = reverse_lazy('inventory:gate-pass-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.request.session.get('compid', 1)
        kwargs['finyearid'] = self.request.session.get('finyearid', 1)
        kwargs['sessionid'] = self.request.session.get('sessionid', 1)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['detail_formset'] = GatePassDetailFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['detail_formset'] = GatePassDetailFormSet(
                instance=self.object
            )
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']
        
        if detail_formset.is_valid():
            from .services import GatePassService
            compid = self.request.session.get('compid', 1)
            finyearid = self.request.session.get('finyearid', 1)
            
            gatepass_number = GatePassService.generate_gatepass_number(compid, finyearid)
            form.instance.gatepassno = gatepass_number
            
            self.object = form.save()
            detail_formset.instance = self.object
            detail_formset.save()
            
            messages.success(
                self.request,
                f'Gate Pass {gatepass_number} created successfully!'
            )
            
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)



class GatePassDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """Gate Pass Detail View"""
    model = TblGatepass  # NOTE: Using TblGatepass - master/detail models dont exist
    template_name = 'inventory/transactions/gate_pass_detail.html'
    context_object_name = 'gatepass'
    pk_url_kwarg = 'gatepassid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        details = Tblgatepassdetail.objects.filter(
            gatepassid=self.object
        ).select_related('itemid')
        
        context['details'] = details
        
        # Calculate days pending if returnable and not returned
        if self.object.isreturnable and not self.object.returndate:
            from .services import GatePassService
            days_pending = GatePassService.calculate_days_pending(self.object.gatepassdate)
            context['days_pending'] = days_pending
        
        return context



class GatePassUpdateView(LoginRequiredMixin, CompanyFinancialYearMixin, UpdateView):
    """Gate Pass Update View"""
    model = TblGatepass  # NOTE: Using TblGatepass - master/detail models dont exist
    # form_class = GatePassMasterForm  # Form commented out
    template_name = 'inventory/transactions/gate_pass_form.html'
    success_url = reverse_lazy('inventory:gate-pass-list')
    pk_url_kwarg = 'gatepassid'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.request.session.get('compid', 1)
        kwargs['finyearid'] = self.request.session.get('finyearid', 1)
        kwargs['sessionid'] = self.request.session.get('sessionid', 1)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = GatePassDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = GatePassDetailFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']
        if detail_formset.is_valid():
            self.object = form.save()
            detail_formset.instance = self.object
            detail_formset.save()
            messages.success(self.request, f'Gate Pass {self.object.gatepassno} updated successfully!')
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)



class GatePassPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """Gate Pass Print View"""
    model = TblGatepass  # NOTE: Using TblGatepass - master/detail models dont exist
    template_name = 'inventory/transactions/gate_pass_print.html'
    context_object_name = 'gatepass'
    pk_url_kwarg = 'gatepassid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        details = Tblgatepassdetail.objects.filter(
            gatepassid=self.object
        ).select_related('itemid')
        
        context['details'] = details
        
        return context



class GatePassReturnView(LoginRequiredMixin, CompanyFinancialYearMixin, FormView):
    """Gate Pass Return View - Record returned items"""
    template_name = 'inventory/transactions/gate_pass_return.html'
    # form_class = django forms.Form  # Dynamic form - commented out
    
    def get_gatepass(self):
        gatepassid = self.kwargs.get('gatepassid')
        return get_object_or_404(TblGatepass, gatepassid=gatepassid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gatepass = self.get_gatepass()
        details = Tblgatepassdetail.objects.filter(
            gatepassid=gatepass
        ).select_related('itemid')
        
        context['gatepass'] = gatepass
        context['details'] = details
        
        return context
    
    def post(self, request, *args, **kwargs):
        gatepass = self.get_gatepass()
        
        # Extract return data from POST
        return_items = []
        for key, value in request.POST.items():
            if key.startswith('returned_qty_') and value:
                detail_id = int(key.replace('returned_qty_', ''))
                return_items.append({
                    'detail_id': detail_id,
                    'returned_qty': value
                })
        
        if not return_items:
            messages.warning(request, 'No returned quantities entered!')
            return self.form_invalid(None)
        
        # Record return
        from .services import GatePassService
        from datetime import date
        
        success = GatePassService.record_return(
            gatepass.gatepassid,
            date.today(),
            return_items
        )
        
        if success:
            messages.success(
                request,
                f'Gate Pass {gatepass.gatepassno} return recorded successfully!'
            )
            return HttpResponseRedirect(
                reverse_lazy('inventory:gate-pass-detail', kwargs={'gatepassid': gatepass.gatepassid})
            )
        else:
            messages.error(request, 'Error recording return!')
            return self.form_invalid(None)



class GatePassPendingListView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """Gate Pass Pending List View - Unreturned returnable passes"""
    model = TblGatepass  # NOTE: Using TblGatepass - master/detail models dont exist
    template_name = 'inventory/transactions/gate_pass_pending_list.html'
    context_object_name = 'gatepasses'
    paginate_by = 20
    
    def get_queryset(self):
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)
        
        from .services import GatePassService
        return GatePassService.get_pending_returnable_passes(compid, finyearid)


# ============================================================================
# VEHICLE VIEWS
# ============================================================================


