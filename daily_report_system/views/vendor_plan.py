"""
Vendor Plan Views

CRUD operations for vendor plans.
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
from daily_report_system.models import TblpmProjectVendorPlanDetail
from daily_report_system.services import PlanService


class VendorPlanListView(BaseListViewMixin, ListView):
    """
    Vendor Plan List - List all vendor plans with search.

    Supports HTMX partial updates and search functionality.
    """
    model = TblpmProjectVendorPlanDetail
    template_name = 'daily_report_system/vendor_plan/list.html'
    context_object_name = 'plans'
    paginate_by = 25
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        return PlanService.search_vendor_plans(queryset, search)


class VendorPlanCreateView(BaseCreateViewMixin, CreateView):
    """
    Vendor Plan Create - Create new vendor plan.

    Uses core mixins for audit fields and HTMX support.
    """
    model = TblpmProjectVendorPlanDetail
    template_name = 'daily_report_system/vendor_plan/form.html'
    fields = [
        'prjctno', 'itemcode', 'description', 'uom', 'bomq',
        'design', 'vendorplandate', 'vendoract', 'wono', 'vendorplan'
    ]
    success_url = reverse_lazy('daily_report_system:vendor-plan-list')
    success_message = 'Vendor plan created successfully'


class VendorPlanUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Vendor Plan Update - Edit existing vendor plan.

    Uses core mixins for audit fields and HTMX support.
    """
    model = TblpmProjectVendorPlanDetail
    template_name = 'daily_report_system/vendor_plan/form.html'
    fields = [
        'prjctno', 'itemcode', 'description', 'uom', 'bomq',
        'design', 'vendorplandate', 'vendoract', 'wono', 'vendorplan'
    ]
    success_url = reverse_lazy('daily_report_system:vendor-plan-list')
    success_message = 'Vendor plan updated successfully'


class VendorPlanDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Vendor Plan Delete - Delete vendor plan.

    Supports HTMX 204 response for row removal.
    """
    model = TblpmProjectVendorPlanDetail
    template_name = 'daily_report_system/vendor_plan/confirm_delete.html'
    success_url = reverse_lazy('daily_report_system:vendor-plan-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Vendor plan deleted successfully')
        return super().delete(request, *args, **kwargs)


class VendorPlanDetailView(BaseDetailViewMixin, DetailView):
    """
    Vendor Plan Detail - View vendor plan details.

    Displays comprehensive information about a vendor plan.
    """
    model = TblpmProjectVendorPlanDetail
    template_name = 'daily_report_system/vendor_plan/detail.html'
    context_object_name = 'plan'
