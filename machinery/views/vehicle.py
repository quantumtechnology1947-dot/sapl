"""
Vehicle Master Views

Handles CRUD operations for vehicle master records.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from datetime import datetime

from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
)
from ..models import TblvehMasterDetails


class VehicleMasterListView(BaseListViewMixin, ListView):
    """Vehicle Master List - List all vehicles with search and pagination"""
    model = TblvehMasterDetails
    template_name = 'machinery/vehicle/list.html'
    partial_template_name = 'machinery/vehicle/partials/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 25
    search_fields = ['vehno', 'vehical_name', 'contact', 'destination']
    ordering = ['-id']

    def get_queryset(self):
        """Filter by company and financial year, with search"""
        queryset = super().get_queryset()
        return queryset


class VehicleMasterCreateView(BaseCreateViewMixin, CreateView):
    """Vehicle Master Create - Create new vehicle"""
    model = TblvehMasterDetails
    template_name = 'machinery/vehicle/form.html'
    partial_template_name = 'machinery/vehicle/partials/vehicle_form.html'
    fields = [
        'vehno', 'date', 'vehical_name', 'contact', 'destination',
        'address', 'fromkm', 'fromto', 'avg', 'fluel_date',
        'fluel_rs', 'material', 'emp'
    ]
    success_url = reverse_lazy('machinery:vehicle-list')
    success_message = 'Vehicle created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Vehicle'
        context['back_url'] = reverse_lazy('machinery:vehicle-list')
        return context

    def form_valid(self, form):
        """Set audit fields before saving"""
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)


class VehicleMasterUpdateView(BaseUpdateViewMixin, UpdateView):
    """Vehicle Master Update - Edit existing vehicle"""
    model = TblvehMasterDetails
    template_name = 'machinery/vehicle/form.html'
    partial_template_name = 'machinery/vehicle/partials/vehicle_form.html'
    fields = [
        'vehno', 'date', 'vehical_name', 'contact', 'destination',
        'address', 'fromkm', 'fromto', 'avg', 'fluel_date',
        'fluel_rs', 'material', 'emp'
    ]
    success_url = reverse_lazy('machinery:vehicle-list')
    success_message = 'Vehicle updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Vehicle'
        context['back_url'] = reverse_lazy('machinery:vehicle-list')
        return context


class VehicleMasterDeleteView(BaseDeleteViewMixin, DeleteView):
    """Vehicle Master Delete - Delete vehicle"""
    model = TblvehMasterDetails
    template_name = 'machinery/vehicle/confirm_delete.html'
    success_url = reverse_lazy('machinery:vehicle-list')
    success_message = 'Vehicle deleted successfully'


class VehicleMasterDetailView(BaseDetailViewMixin, DetailView):
    """Vehicle Master Detail - View vehicle details"""
    model = TblvehMasterDetails
    template_name = 'machinery/vehicle/detail.html'
    partial_template_name = 'machinery/vehicle/partials/vehicle_detail.html'
    context_object_name = 'vehicle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy('machinery:vehicle-list')
        return context
