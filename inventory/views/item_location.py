"""
Item Location Views
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


class ItemLocationListView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """Item Location List View - Manages warehouse location master"""
    template_name = 'inventory/masters/item_location_list.html'
    context_object_name = 'locations'
    paginate_by = 20

    def get_queryset(self):
        """Return warehouse locations from design module"""
        from design.models import TbldgLocationMaster

        queryset = TbldgLocationMaster.objects.filter(
            compid=self.get_compid()
        )

        # Apply search if present
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(locationlabel__icontains=search) |
                Q(locationno__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset.order_by('-id')



class ItemLocationCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """Item Location Create View - Creates new warehouse location"""
    template_name = 'inventory/masters/item_location_form.html'
    success_url = reverse_lazy('inventory:item-location-list')

    def get_form_class(self):
        """Return the ItemLocationForm"""
        from inventory.forms import ItemLocationForm
        return ItemLocationForm

    def form_valid(self, form):
        # Set system fields
        from datetime import datetime
        form.instance.sysdate = datetime.now().strftime('%Y-%m-%d')
        form.instance.systime = datetime.now().strftime('%I:%M:%S %p')
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.sessionid = self.get_sessionid()

        self.object = form.save()
        messages.success(self.request, 'Location created successfully!')
        return HttpResponseRedirect(self.get_success_url())



class ItemLocationDeleteView(LoginRequiredMixin, CompanyFinancialYearMixin, DeleteView):
    """Item Location Delete View - Deletes warehouse location"""
    template_name = 'inventory/masters/item_location_confirm_delete.html'
    success_url = reverse_lazy('inventory:item-location-list')
    pk_url_kwarg = 'itemlocationid'
    context_object_name = 'location'

    def get_queryset(self):
        """Get locations for current company"""
        from design.models import TbldgLocationMaster
        return TbldgLocationMaster.objects.filter(compid=self.get_compid())

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Location deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# MATERIAL CREDIT NOTE (MCN) VIEWS
# ============================================================================


