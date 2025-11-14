"""
WIS (Work Instruction Sheet) Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseRedirect

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
    WISMasterForm,
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

    Converted from: aspnet/Module/Inventory/Transactions/ReleaseWIS.aspx
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
    """
    WIS Create View

    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Material.aspx (create section)
    """
    model = TblinvWisMaster
    form_class = WISMasterForm
    template_name = 'inventory/transactions/wis_form.html'
    success_url = reverse_lazy('inventory:wis-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.request.session.get('compid', 1)
        kwargs['finyearid'] = self.request.session.get('finyearid', 1)
        kwargs['sessionid'] = self.request.session.get('sessionid', 1)
        return kwargs

    def form_valid(self, form):
        """Save WIS with audit fields"""
        from datetime import datetime

        # Set audit fields
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.compid = self.request.session.get('compid', 1)
        form.instance.finyearid = self.request.session.get('finyearid', 1)
        form.instance.sessionid = str(self.request.user.id)

        # Generate WIS number if not provided
        if not form.instance.wisno:
            from ..services import generate_transaction_number
            form.instance.wisno = generate_transaction_number('WIS', form.instance.compid, form.instance.finyearid)

        self.object = form.save()

        messages.success(
            self.request,
            f'WIS {self.object.wisno} created successfully!'
        )

        return HttpResponseRedirect(self.get_success_url())



class WISDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    WIS Detail View with material details

    Converted from: aspnet/Module/Inventory/Transactions/WIS_View_TransWise.aspx
    """
    model = TblinvWisMaster
    template_name = 'inventory/transactions/wis_detail.html'
    context_object_name = 'wis'
    pk_url_kwarg = 'pk'  # Fixed: use 'pk' not 'wisid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get WIS details - fixed model name and filter field
        details = TblinvWisDetails.objects.filter(
            mid=self.object
        )

        context['details'] = details

        # Get item information for each detail
        from design.models import TbldgItemMaster
        details_with_items = []
        for detail in details:
            item = None
            if detail.itemid:
                try:
                    item = TbldgItemMaster.objects.get(itemid=detail.itemid)
                except TbldgItemMaster.DoesNotExist:
                    pass
            details_with_items.append({
                'detail': detail,
                'item': item
            })

        context['details_with_items'] = details_with_items

        return context



class WISReleaseView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    WIS Release View - Mark WIS as released

    Converted from: aspnet/Module/Inventory/Transactions/ReleaseWIS.aspx
    """

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        try:
            wis = TblinvWisMaster.objects.get(pk=pk)

            # Record in release table
            from ..models import TblinvWoreleaseWis
            from datetime import datetime

            release_record, created = TblinvWoreleaseWis.objects.get_or_create(
                compid=wis.compid,
                finyearid=wis.finyearid,
                wono=wis.wono,
                defaults={
                    'releasesysdate': datetime.now().strftime('%d-%m-%Y')
                }
            )

            messages.success(request, f'WIS {wis.wisno} released successfully!')
        except TblinvWisMaster.DoesNotExist:
            messages.error(request, 'WIS not found!')
        except Exception as e:
            messages.error(request, f'Error releasing WIS: {str(e)}')

        return HttpResponseRedirect(
            reverse_lazy('inventory:wis-detail', kwargs={'pk': pk})
        )



class WISActualRunView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    WIS Actual Run View - Display materials for actual run

    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Material.aspx
    Note: Complex BOM calculation logic from ASP.NET deferred to Phase 2
    """
    template_name = 'inventory/transactions/wis_actual_run.html'

    def get_wis(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(TblinvWisMaster, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wis = self.get_wis()

        # Get WIS details
        details = TblinvWisDetails.objects.filter(mid=wis)

        # Get item information
        from design.models import TbldgItemMaster
        details_with_items = []
        for detail in details:
            item = None
            if detail.itemid:
                try:
                    item = TbldgItemMaster.objects.get(itemid=detail.itemid)
                except TbldgItemMaster.DoesNotExist:
                    pass
            details_with_items.append({
                'detail': detail,
                'item': item
            })

        context['wis'] = wis
        context['details_with_items'] = details_with_items

        return context



class WISPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    WIS Print View

    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Print.aspx
    """
    model = TblinvWisMaster
    template_name = 'inventory/transactions/wis_print.html'
    context_object_name = 'wis'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get WIS details
        details = TblinvWisDetails.objects.filter(mid=self.object)

        # Get item information
        from design.models import TbldgItemMaster
        details_with_items = []
        for detail in details:
            item = None
            if detail.itemid:
                try:
                    item = TbldgItemMaster.objects.get(itemid=detail.itemid)
                except TbldgItemMaster.DoesNotExist:
                    pass
            details_with_items.append({
                'detail': detail,
                'item': item
            })

        context['details_with_items'] = details_with_items

        return context



# ============================================================================
# AUTO WIS TIME SCHEDULE VIEWS
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
