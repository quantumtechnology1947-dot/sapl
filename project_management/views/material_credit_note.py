"""
Material Credit Note Views

MCN creation and management with BOM validation and material tracking.
Uses MCNService for complex business logic.
Extracted from monolithic views.py.
"""

from datetime import datetime
from django.views.generic import TemplateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages

from ..models import TblpmMaterialcreditnoteMaster, TblpmMaterialcreditnoteDetails
from ..services import MCNService


class ProjectManagementBaseMixin(LoginRequiredMixin):
    """Base mixin for all Project Management views"""
    login_url = '/login/'

    def get_compid(self):
        return self.request.session.get('company_id', 1)

    def get_finyearid(self):
        return self.request.session.get('financial_year_id', 1)

    def get_sessionid(self):
        return self.request.session.session_key or 'default'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compid'] = self.get_compid()
        context['finyearid'] = self.get_finyearid()
        return context


class MaterialCreditNoteNewView(ProjectManagementBaseMixin, TemplateView):
    """
    Material Credit Note New - Shows Work Orders for creating NEW MCNs
    Based on ASP.NET MaterialCreditNote_MCN_New.aspx
    Shows all open work orders - clicking a WO redirects to MCN creation form
    """
    template_name = 'project_management/mcn/new.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from sales_distribution.models import SdCustWorkorderMaster

        compid = self.get_compid()

        # Search parameters
        search_field = self.request.GET.get('search_field', '1')
        search_value = self.request.GET.get('search_value', '')

        # Get open Work Orders
        work_orders_query = SdCustWorkorderMaster.objects.filter(
            compid=compid,
            closeopen=0
        ).order_by('wono')

        # Apply search filters
        if search_value:
            if search_field == '0':  # Customer
                work_orders_query = work_orders_query.filter(customerid__icontains=search_value)
            elif search_field == '1':  # WO Number
                work_orders_query = work_orders_query.filter(wono__icontains=search_value)
            elif search_field == '2':  # Project Title
                work_orders_query = work_orders_query.filter(taskprojecttitle__icontains=search_value)

        # Enrich work orders using service
        context['work_orders'] = MCNService.enrich_work_orders_with_mcn_info(
            work_orders_query[:150], compid
        )
        context['search_field'] = search_field
        context['search_value'] = search_value
        context['page_mode'] = 'new'

        return context


class MaterialCreditNoteListView(ProjectManagementBaseMixin, TemplateView):
    """
    Material Credit Note List - Shows Work Orders for MCN creation/editing
    Based on ASP.NET MaterialCreditNote_MCN_Edit.aspx
    """
    template_name = 'project_management/mcn/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from sales_distribution.models import SdCustWorkorderMaster

        compid = self.get_compid()

        # Search parameters
        search_field = self.request.GET.get('search_field', '1')
        search_value = self.request.GET.get('search_value', '')

        # Get open Work Orders
        work_orders_query = SdCustWorkorderMaster.objects.filter(
            compid=compid,
            closeopen=0
        ).order_by('wono')

        # Apply search filters
        if search_value:
            if search_field == '0':
                work_orders_query = work_orders_query.filter(customerid__icontains=search_value)
            elif search_field == '1':
                work_orders_query = work_orders_query.filter(wono__icontains=search_value)
            elif search_field == '2':
                work_orders_query = work_orders_query.filter(taskprojecttitle__icontains=search_value)

        # Enrich work orders using service
        context['work_orders'] = MCNService.enrich_work_orders_with_mcn_info(
            work_orders_query[:150], compid
        )
        context['search_field'] = search_field
        context['search_value'] = search_value

        return context


class MaterialCreditNoteCreateView(ProjectManagementBaseMixin, TemplateView):
    """
    Create Material Credit Note - New Details
    Based on ASP.NET MaterialCreditNote_MCN_New_Details.aspx
    Shows BOM items for selected WO and allows entering MCN quantities
    Uses MCNService for validation and creation
    """
    template_name = 'project_management/mcn/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from sales_distribution.models import SdCustWorkorderMaster, SdCustMaster

        compid = self.get_compid()
        wono = self.request.GET.get('wono', '')

        # Get Work Order details
        wo = SdCustWorkorderMaster.objects.filter(compid=compid, wono=wono).first()

        if wo:
            context['wono'] = wo.wono
            context['project_title'] = wo.taskprojecttitle or '-'

            # Get customer details
            customer = SdCustMaster.objects.filter(compid=compid, customerid=wo.customerid).first()
            context['customer_name'] = f"{customer.customername} [{customer.customerid}]" if customer else '-'

            # Get BOM items using service
            context['bom_items'] = MCNService.get_bom_items_with_mcn_history(compid, wono)
        else:
            context['wono'] = wono
            context['project_title'] = '-'
            context['customer_name'] = '-'
            context['bom_items'] = []
            messages.warning(self.request, f'Work Order {wono} not found')

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle MCN creation with BOM items
        Uses MCNService for validation and creation
        """
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        sessionid = self.get_sessionid()
        wono = request.POST.get('wono')

        # Validate MCN quantities using service
        is_valid, bom_data, count, k = MCNService.validate_mcn_quantities(
            request.POST, compid, wono
        )

        if is_valid:
            # Create MCN with details using service
            mcn_master, saved_count = MCNService.create_mcn_with_details(
                compid, finyearid, sessionid, wono, bom_data, request.POST
            )

            if saved_count > 0:
                messages.success(
                    request,
                    f'Material Credit Note {mcn_master.mcnno} created successfully with {saved_count} items!'
                )
                return HttpResponseRedirect(reverse('project_management:mcn-list'))
            else:
                messages.error(request, 'No items were saved. Please check your input.')
                return HttpResponseRedirect(reverse('project_management:mcn-create') + f'?wono={wono}')
        else:
            messages.error(request, 'Invalid input data. MCN quantity cannot exceed BOM quantity.')
            return HttpResponseRedirect(reverse('project_management:mcn-create') + f'?wono={wono}')


class MaterialCreditNoteDetailView(ProjectManagementBaseMixin, DetailView):
    """View Material Credit Note Details"""
    model = TblpmMaterialcreditnoteMaster
    template_name = 'project_management/mcn/detail.html'
    context_object_name = 'mcn'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get details using service
        context['details'] = MCNService.get_mcn_details(self.object)
        return context


class MaterialCreditNoteUpdateView(ProjectManagementBaseMixin, UpdateView):
    """Update Material Credit Note"""
    model = TblpmMaterialcreditnoteMaster
    fields = ['mcnno', 'wono']
    template_name = 'project_management/mcn/form.html'
    success_url = reverse_lazy('project_management:mcn-list')
    pk_url_kwarg = 'pk'


class MaterialCreditNoteDeleteView(ProjectManagementBaseMixin, DeleteView):
    """Delete Material Credit Note"""
    model = TblpmMaterialcreditnoteMaster
    success_url = reverse_lazy('project_management:mcn-list')
    pk_url_kwarg = 'pk'
