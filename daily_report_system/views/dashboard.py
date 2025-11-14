"""
Dashboard View

Main dashboard for Daily Reporting System showing statistics and recent projects.
"""

from django.views.generic import TemplateView
from core.mixins import BaseDetailViewMixin
from daily_report_system.services import PlanService


class DRSDashboardView(BaseDetailViewMixin, TemplateView):
    """
    Dashboard - Shows daily reporting tracker with statistics.

    Displays comprehensive statistics for projects, designs,
    manufacturing plans, vendor plans, and activities.
    """
    template_name = 'daily_report_system/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get statistics from service layer
        statistics = PlanService.get_plan_statistics(compid, finyearid)
        context.update(statistics)

        # Get recent projects
        context['recent_projects'] = PlanService.get_recent_projects(compid, finyearid, limit=10)

        return context
