"""
Quality Control Dashboard View
"""
from django.views.generic import TemplateView
from .base import QualityControlBaseMixin
from quality_control.services import QualityStatisticsService


class QualityControlDashboardView(QualityControlBaseMixin, TemplateView):
    """Quality Control Dashboard with statistics and quick actions"""
    template_name = 'quality_control/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get statistics from service
        statistics = QualityStatisticsService.get_dashboard_statistics(compid, finyearid)
        context.update(statistics)

        return context
