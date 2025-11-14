"""
Design Plan Views

CRUD operations for design plans.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
)
from daily_report_system.models import TblpmProjectplanningDesigner
from daily_report_system.services import PlanService


class DesignPlanListView(BaseListViewMixin, ListView):
    """
    Design Plan List - List all design plans with search.

    Supports HTMX partial updates and search functionality.
    """
    model = TblpmProjectplanningDesigner
    template_name = 'daily_report_system/design_plan/list.html'
    context_object_name = 'plans'
    paginate_by = 25
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        return PlanService.search_design_plans(queryset, search)


class DesignPlanCreateView(BaseCreateViewMixin, CreateView):
    """
    Design Plan Create - Create new design plan.

    Uses core mixins for audit fields and HTMX support.
    """
    model = TblpmProjectplanningDesigner
    template_name = 'daily_report_system/design_plan/form.html'
    fields = [
        'name_proj', 'wo_no', 'no_fix_rqu', 'des_lea', 'des_mem',
        'sr_no', 'name_act', 'rev_no', 'no_days', 'as_plan_from',
        'as_plan_to', 'ac_from'
    ]
    success_url = reverse_lazy('daily_report_system:design-plan-list')
    success_message = 'Design plan created successfully'


class DesignPlanUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Design Plan Update - Edit existing design plan.

    Uses core mixins for audit fields and HTMX support.
    """
    model = TblpmProjectplanningDesigner
    template_name = 'daily_report_system/design_plan/form.html'
    fields = [
        'name_proj', 'wo_no', 'no_fix_rqu', 'des_lea', 'des_mem',
        'sr_no', 'name_act', 'rev_no', 'no_days', 'as_plan_from',
        'as_plan_to', 'ac_from'
    ]
    success_url = reverse_lazy('daily_report_system:design-plan-list')
    success_message = 'Design plan updated successfully'


class DesignPlanDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Design Plan Delete - Delete design plan.

    Supports HTMX 204 response for row removal.
    """
    model = TblpmProjectplanningDesigner
    template_name = 'daily_report_system/design_plan/confirm_delete.html'
    success_url = reverse_lazy('daily_report_system:design-plan-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Design plan deleted successfully')
        return super().delete(request, *args, **kwargs)


class DesignPlanDetailView(BaseDetailViewMixin, DetailView):
    """
    Design Plan Detail - View design plan details.

    Displays comprehensive information about a design plan.
    """
    model = TblpmProjectplanningDesigner
    template_name = 'daily_report_system/design_plan/detail.html'
    context_object_name = 'plan'
