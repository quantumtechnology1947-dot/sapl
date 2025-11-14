"""
Project Main Sheet Views

List and detail views for project main sheets.
"""

from django.views.generic import ListView, DetailView
from core.mixins import BaseListViewMixin, BaseDetailViewMixin
from daily_report_system.models import TblpmProjectplanningMainsheet
from daily_report_system.services import PlanService


class ProjectMainSheetListView(BaseListViewMixin, ListView):
    """
    Project Main Sheet List - List all project activities with search.

    Supports HTMX partial updates and search functionality.
    """
    model = TblpmProjectplanningMainsheet
    template_name = 'daily_report_system/mainsheet/list.html'
    context_object_name = 'sheets'
    paginate_by = 25
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        return PlanService.search_mainsheet(queryset, search)


class ProjectMainSheetDetailView(BaseDetailViewMixin, DetailView):
    """
    Project Main Sheet Detail - View main sheet details.

    Displays comprehensive information about a project main sheet.
    """
    model = TblpmProjectplanningMainsheet
    template_name = 'daily_report_system/mainsheet/detail.html'
    context_object_name = 'sheet'
