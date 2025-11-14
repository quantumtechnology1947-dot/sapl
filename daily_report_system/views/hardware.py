"""
Hardware Plan Views

List and detail views for hardware plans.
"""

from django.views.generic import ListView, DetailView
from core.mixins import BaseListViewMixin, BaseDetailViewMixin
from daily_report_system.models import TblpmProjectHardwareMasterDetail
from daily_report_system.services import PlanService


class HardwarePlanListView(BaseListViewMixin, ListView):
    """
    Hardware Plan List - List all hardware plans with search.

    Supports HTMX partial updates and search functionality.
    """
    model = TblpmProjectHardwareMasterDetail
    template_name = 'daily_report_system/hardware_plan/list.html'
    context_object_name = 'plans'
    paginate_by = 25
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        return PlanService.search_hardware_plans(queryset, search)


class HardwarePlanDetailView(BaseDetailViewMixin, DetailView):
    """
    Hardware Plan Detail - View hardware plan details.

    Displays comprehensive information about a hardware plan.
    """
    model = TblpmProjectHardwareMasterDetail
    template_name = 'daily_report_system/hardware_plan/detail.html'
    context_object_name = 'plan'
