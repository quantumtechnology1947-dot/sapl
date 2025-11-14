"""
Machinery Dashboard View

Displays statistics and overview of machinery module.
"""

from django.views.generic import TemplateView
from django.db.models import Count, Sum

from core.mixins import BaseDetailViewMixin
from ..models import (
    TblvehMasterDetails,
    TblvehProcessMaster,
    TblinvAutowisTimeschedule,
)


class MachineryDashboardView(BaseDetailViewMixin, TemplateView):
    """Dashboard - Shows machinery and vehicle statistics"""
    template_name = 'machinery/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Statistics
        context['total_vehicles'] = TblvehMasterDetails.objects.filter(
            compid=compid, finyearid=finyearid
        ).count()

        context['total_processes'] = TblvehProcessMaster.objects.count()
        context['total_schedules'] = TblinvAutowisTimeschedule.objects.filter(
            compid=compid, finyearid=finyearid
        ).count()

        # Recent vehicles
        context['recent_vehicles'] = TblvehMasterDetails.objects.filter(
            compid=compid, finyearid=finyearid
        ).order_by('-id')[:10]

        # Recent processes
        context['recent_processes'] = TblvehProcessMaster.objects.all().order_by('-id')[:10]

        return context
