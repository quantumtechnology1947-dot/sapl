"""
Auto WIS Time Schedule Views

Handles CRUD operations for auto WIS time schedules.
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
from ..models import TblinvAutowisTimeschedule


class AutoWISScheduleListView(BaseListViewMixin, ListView):
    """Auto WIS Schedule List - List all auto WIS schedules"""
    model = TblinvAutowisTimeschedule
    template_name = 'machinery/schedule/list.html'
    partial_template_name = 'machinery/schedule/partials/schedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 25
    search_fields = ['timeauto']
    ordering = ['-id']


class AutoWISScheduleCreateView(BaseCreateViewMixin, CreateView):
    """Auto WIS Schedule Create - Create new schedule"""
    model = TblinvAutowisTimeschedule
    template_name = 'machinery/schedule/form.html'
    partial_template_name = 'machinery/schedule/partials/schedule_form.html'
    fields = ['timeauto', 'timetoorder']
    success_url = reverse_lazy('machinery:schedule-list')
    success_message = 'Schedule created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Schedule'
        context['back_url'] = reverse_lazy('machinery:schedule-list')
        return context

    def form_valid(self, form):
        """Set company and financial year before saving"""
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)


class AutoWISScheduleUpdateView(BaseUpdateViewMixin, UpdateView):
    """Auto WIS Schedule Update - Edit existing schedule"""
    model = TblinvAutowisTimeschedule
    template_name = 'machinery/schedule/form.html'
    partial_template_name = 'machinery/schedule/partials/schedule_form.html'
    fields = ['timeauto', 'timetoorder']
    success_url = reverse_lazy('machinery:schedule-list')
    success_message = 'Schedule updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Schedule'
        context['back_url'] = reverse_lazy('machinery:schedule-list')
        return context


class AutoWISScheduleDeleteView(BaseDeleteViewMixin, DeleteView):
    """Auto WIS Schedule Delete - Delete schedule"""
    model = TblinvAutowisTimeschedule
    template_name = 'machinery/schedule/confirm_delete.html'
    success_url = reverse_lazy('machinery:schedule-list')
    success_message = 'Schedule deleted successfully'


class AutoWISScheduleDetailView(BaseDetailViewMixin, DetailView):
    """Auto WIS Schedule Detail - View schedule details"""
    model = TblinvAutowisTimeschedule
    template_name = 'machinery/schedule/detail.html'
    partial_template_name = 'machinery/schedule/partials/schedule_detail.html'
    context_object_name = 'schedule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy('machinery:schedule-list')
        return context
