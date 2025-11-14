"""
Report Views

Various report views for design plans, manufacturing plans, and project summaries.
"""

from django.views.generic import TemplateView
from core.mixins import BaseDetailViewMixin
from daily_report_system.services import ReportService


class DepartmentalWorkingPlanView(BaseDetailViewMixin, TemplateView):
    """
    Departmental Working Plan Report.

    Shows all design plans organized by department.
    """
    template_name = 'daily_report_system/reports/departmental_working_plan.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = ReportService.get_departmental_working_plan_data()
        return context


class IndividualWorkingPlanView(BaseDetailViewMixin, TemplateView):
    """
    Individual Working Plan Report.

    Shows project activities organized by individual.
    """
    template_name = 'daily_report_system/reports/individual_working_plan.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = ReportService.get_individual_working_plan_data()
        return context


class DetailProjectPlanView(BaseDetailViewMixin, TemplateView):
    """
    Detail Project Plan Report.

    Shows comprehensive project details including design and manufacturing plans.
    """
    template_name = 'daily_report_system/reports/detail_project_plan.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        report_data = ReportService.get_detail_project_plan_data(compid, finyearid)
        context.update(report_data)

        return context


class ProjectSummaryView(BaseDetailViewMixin, TemplateView):
    """
    Project Summary Report.

    Shows high-level summary statistics and recent projects.
    """
    template_name = 'daily_report_system/reports/project_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        report_data = ReportService.get_project_summary_data(compid, finyearid, limit=20)
        context.update(report_data)

        return context
