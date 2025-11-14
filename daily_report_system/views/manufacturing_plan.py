"""
Manufacturing Plan Views

CRUD operations for manufacturing plans.
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
from daily_report_system.models import TblpmProjectManufacturingPlanDetail
from daily_report_system.services import PlanService


class ManufacturingPlanListView(BaseListViewMixin, ListView):
    """
    Manufacturing Plan List - List all manufacturing plans with search.

    Supports HTMX partial updates and search functionality.
    """
    model = TblpmProjectManufacturingPlanDetail
    template_name = 'daily_report_system/manufacturing_plan/list.html'
    context_object_name = 'plans'
    paginate_by = 25
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        return PlanService.search_manufacturing_plans(queryset, search)


class ManufacturingPlanCreateView(BaseCreateViewMixin, CreateView):
    """
    Manufacturing Plan Create - Create new manufacturing plan.

    Uses core mixins for audit fields and HTMX support.
    """
    model = TblpmProjectManufacturingPlanDetail
    template_name = 'daily_report_system/manufacturing_plan/form.html'
    fields = [
        'prjctno', 'itemcode', 'description', 'uom', 'bomq',
        'design', 'vendorplandate', 'vendoract', 'wono', 'vendorplan'
    ]
    success_url = reverse_lazy('daily_report_system:manufacturing-plan-list')
    success_message = 'Manufacturing plan created successfully'


class ManufacturingPlanUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Manufacturing Plan Update - Edit existing manufacturing plan.

    Uses core mixins for audit fields and HTMX support.
    """
    model = TblpmProjectManufacturingPlanDetail
    template_name = 'daily_report_system/manufacturing_plan/form.html'
    fields = [
        'prjctno', 'itemcode', 'description', 'uom', 'bomq',
        'design', 'vendorplandate', 'vendoract', 'wono', 'vendorplan'
    ]
    success_url = reverse_lazy('daily_report_system:manufacturing-plan-list')
    success_message = 'Manufacturing plan updated successfully'


class ManufacturingPlanDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Manufacturing Plan Delete - Delete manufacturing plan.

    Supports HTMX 204 response for row removal.
    """
    model = TblpmProjectManufacturingPlanDetail
    template_name = 'daily_report_system/manufacturing_plan/confirm_delete.html'
    success_url = reverse_lazy('daily_report_system:manufacturing-plan-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Manufacturing plan deleted successfully')
        return super().delete(request, *args, **kwargs)


class ManufacturingPlanDetailView(BaseDetailViewMixin, DetailView):
    """
    Manufacturing Plan Detail - View manufacturing plan details.

    Displays comprehensive information about a manufacturing plan.
    """
    model = TblpmProjectManufacturingPlanDetail
    template_name = 'daily_report_system/manufacturing_plan/detail.html'
    context_object_name = 'plan'
