"""
Vehicle Process Master Views

Handles CRUD operations for vehicle process records.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
)
from ..models import TblvehProcessMaster


class VehicleProcessListView(BaseListViewMixin, ListView):
    """Vehicle Process List - List all vehicle processes"""
    model = TblvehProcessMaster
    template_name = 'machinery/process/list.html'
    partial_template_name = 'machinery/process/partials/process_list.html'
    context_object_name = 'processes'
    paginate_by = 25
    search_fields = ['vehicalname', 'vehicalno']
    ordering = ['-id']


class VehicleProcessCreateView(BaseCreateViewMixin, CreateView):
    """Vehicle Process Create - Create new vehicle process"""
    model = TblvehProcessMaster
    template_name = 'machinery/process/form.html'
    partial_template_name = 'machinery/process/partials/process_form.html'
    fields = ['vehicalname', 'vehicalno']
    success_url = reverse_lazy('machinery:process-list')
    success_message = 'Vehicle process created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Vehicle Process'
        context['back_url'] = reverse_lazy('machinery:process-list')
        return context


class VehicleProcessUpdateView(BaseUpdateViewMixin, UpdateView):
    """Vehicle Process Update - Edit existing vehicle process"""
    model = TblvehProcessMaster
    template_name = 'machinery/process/form.html'
    partial_template_name = 'machinery/process/partials/process_form.html'
    fields = ['vehicalname', 'vehicalno']
    success_url = reverse_lazy('machinery:process-list')
    success_message = 'Vehicle process updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Vehicle Process'
        context['back_url'] = reverse_lazy('machinery:process-list')
        return context


class VehicleProcessDeleteView(BaseDeleteViewMixin, DeleteView):
    """Vehicle Process Delete - Delete vehicle process"""
    model = TblvehProcessMaster
    template_name = 'machinery/process/confirm_delete.html'
    success_url = reverse_lazy('machinery:process-list')
    success_message = 'Vehicle process deleted successfully'


class VehicleProcessDetailView(BaseDetailViewMixin, DetailView):
    """Vehicle Process Detail - View vehicle process details"""
    model = TblvehProcessMaster
    template_name = 'machinery/process/detail.html'
    partial_template_name = 'machinery/process/partials/process_detail.html'
    context_object_name = 'process'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy('machinery:process-list')
        return context
