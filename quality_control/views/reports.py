"""
Quality Control Reports Views

Handles various quality control reports:
- Quality Summary Report
- Rejection Analysis Report
"""
from django.views.generic import TemplateView

from .base import QualityControlBaseMixin
from quality_control.services import QualityStatisticsService, RejectionAnalysisService


class QualityReportView(QualityControlBaseMixin, TemplateView):
    """Quality Control Summary Report"""
    template_name = 'quality_control/reports/quality_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # Get report data from service
        report_data = QualityStatisticsService.get_quality_report_data(
            compid, finyearid, from_date, to_date
        )
        context.update(report_data)

        return context


class RejectionAnalysisView(QualityControlBaseMixin, TemplateView):
    """Rejection Analysis Report"""
    template_name = 'quality_control/reports/rejection_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # Get rejection analysis from service
        analysis = RejectionAnalysisService.get_rejection_summary(
            compid, finyearid, from_date, to_date
        )
        context.update(analysis)

        return context
