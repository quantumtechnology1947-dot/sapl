"""
WIS (Work Instruction Sheet) Views
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


class WISListView(BaseListViewMixin, ListView):
    """
    WIS List View
    Display all work instruction sheets with status filtering
    
    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Material.aspx
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    """
    model = TblinvWisMaster
    template_name = 'inventory/transactions/wis_list.html'
    context_object_name = 'wis_list'
    paginate_by = 20
    search_fields = ['wisno', 'wono']
    ordering = ['-id']
    
    # No need to override get_queryset() - BaseListViewMixin handles company/year filtering and search
    # No need to override get_context_data() - BaseListViewMixin handles search_query



class WISCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """WIS Create View"""
    model = TblinvWisMaster
    # form_class = WISMasterForm  # Form commented out
    template_name = 'inventory/transactions/wis_form.html'
    success_url = reverse_lazy('inventory:wis-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.request.session.get('compid', 1)
        kwargs['finyearid'] = self.request.session.get('finyearid', 1)
        kwargs['sessionid'] = self.request.session.get('sessionid', 1)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['detail_formset'] = WISDetailFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['detail_formset'] = WISDetailFormSet(
                instance=self.object
            )
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']
        
        if detail_formset.is_valid():
            from .services import WISService
            compid = self.request.session.get('compid', 1)
            finyearid = self.request.session.get('finyearid', 1)
            
            wis_number = WISService.generate_wis_number(compid, finyearid)
            form.instance.wisno = wis_number
            
            self.object = form.save()
            detail_formset.instance = self.object
            detail_formset.save()
            
            messages.success(
                self.request,
                f'WIS {wis_number} created successfully!'
            )
            
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)



class WISDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """WIS Detail View with shortage display"""
    model = TblinvWisMaster
    template_name = 'inventory/transactions/wis_detail.html'
    context_object_name = 'wis'
    pk_url_kwarg = 'wisid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        details = Tblwisdetail.objects.filter(
            wisid=self.object
        ).select_related('itemid')
        
        context['details'] = details
        
        # Check stock availability for each item
        from .services import WISService
        availability_list = []
        for detail in details:
            if detail.itemid:
                availability = WISService.check_stock_availability(
                    detail.itemid.itemid,
                    detail.requiredqty
                )
                availability_list.append(availability)
            else:
                availability_list.append(None)
        
        context['availability_list'] = availability_list
        
        return context



class WISReleaseView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """WIS Release View - Change status to Released"""
    
    def post(self, request, *args, **kwargs):
        wisid = kwargs.get('wisid')
        
        from .services import WISService
        success = WISService.release_wis(wisid)
        
        if success:
            messages.success(request, 'WIS released successfully!')
        else:
            messages.error(request, 'Error releasing WIS!')
        
        return HttpResponseRedirect(
            reverse_lazy('inventory:wis-detail', kwargs={'wisid': wisid})
        )



class WISActualRunView(LoginRequiredMixin, CompanyFinancialYearMixin, FormView):
    """WIS Actual Run View - Record actual material consumption"""
    template_name = 'inventory/transactions/wis_actual_run.html'
    # form_class = forms.Form  # Commented out - forms.Form not in inventory.forms
    
    def get_wis(self):
        wisid = self.kwargs.get('wisid')
        return get_object_or_404(TblinvWisMaster, wisid=wisid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wis = self.get_wis()
        details = Tblwisdetail.objects.filter(
            wisid=wis
        ).select_related('itemid')
        
        context['wis'] = wis
        context['details'] = details
        
        return context
    
    def post(self, request, *args, **kwargs):
        wis = self.get_wis()
        
        # Extract actual quantities
        actual_materials = []
        for key, value in request.POST.items():
            if key.startswith('actual_qty_') and value:
                detail_id = int(key.replace('actual_qty_', ''))
                item_id = request.POST.get(f'item_id_{detail_id}')
                actual_materials.append({
                    'detail_id': detail_id,
                    'item_id': item_id,
                    'actual_qty': value
                })
        
        if not actual_materials:
            messages.warning(request, 'No actual quantities entered!')
            return self.form_invalid(None)
        
        # Record actual run
        from .services import WISService
        success = WISService.record_actual_run(wis.wisid, actual_materials)
        
        if success:
            messages.success(
                self.request,
                f'Actual run recorded for WIS {wis.wisno}!'
            )
            return HttpResponseRedirect(
                reverse_lazy('inventory:wis-detail', kwargs={'wisid': wis.wisid})
            )
        else:
            messages.error(request, 'Error recording actual run!')
            return self.form_invalid(None)



class WISPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """WIS Print View"""
    model = TblinvWisMaster
    template_name = 'inventory/transactions/wis_print.html'
    context_object_name = 'wis'
    pk_url_kwarg = 'wisid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        details = Tblwisdetail.objects.filter(
            wisid=self.object
        ).select_related('itemid')
        
        context['details'] = details
        
        return context



# ============================================================================
# ITEM LOCATION VIEWS
# ============================================================================


class AutoWISTimeScheduleListView(BaseListViewMixin, ListView):
    """
    Auto WIS Time Schedule List View
    Converted from: aspnet/Module/Inventory/Masters/AutoWIS_Time_Set.aspx
    """
    model = TblinvAutowisTimeschedule
    template_name = 'inventory/masters/autowis_timeschedule_list.html'
    context_object_name = 'schedules'
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AutoWISTimeScheduleForm()
        return context


class AutoWISTimeScheduleCreateView(BaseCreateViewMixin, CreateView):
    """
    Auto WIS Time Schedule Create View
    """
    model = TblinvAutowisTimeschedule
    form_class = AutoWISTimeScheduleForm
    success_url = reverse_lazy('inventory:autowis-timeschedule-list')
    success_message = 'Scheduled time added successfully!'
    error_message = 'Error adding scheduled time.'


class AutoWISTimeScheduleUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Auto WIS Time Schedule Update View
    """
    model = TblinvAutowisTimeschedule
    form_class = AutoWISTimeScheduleForm
    success_url = reverse_lazy('inventory:autowis-timeschedule-list')
    template_name = 'inventory/masters/partials/autowis_timeschedule_edit.html'
    success_message = 'Scheduled time updated successfully!'


class AutoWISTimeScheduleDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Auto WIS Time Schedule Delete View
    """
    model = TblinvAutowisTimeschedule
    success_url = reverse_lazy('inventory:autowis-timeschedule-list')
    success_message = 'Scheduled time deleted successfully!'


class AutoWISTimeScheduleRowView(LoginRequiredMixin, DetailView):
    """
    Renders a single row for the Auto WIS Time Schedule list.
    Used for HTMX cancel actions.
    """
    model = TblinvAutowisTimeschedule
    template_name = 'inventory/masters/partials/autowis_timeschedule_row.html'
    context_object_name = 'schedule'


# ============================================================================
# STOCK LEDGER VIEWS
# ============================================================================


