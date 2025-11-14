"""
Machinery Reports Views

Comprehensive reports for machinery, vehicles, and schedules.
"""

from django.views.generic import TemplateView
from django.db.models import Sum

from core.mixins import BaseDetailViewMixin
from ..models import (
    TblvehMasterDetails,
    TblvehProcessMaster,
    TblinvAutowisTimeschedule,
)
from ..services.scheduling_service import SchedulingService


class VehicleReportView(BaseDetailViewMixin, TemplateView):
    """Vehicle Report - Comprehensive vehicle report"""
    template_name = 'machinery/reports/vehicle_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        vehicles = TblvehMasterDetails.objects.filter(
            compid=compid, finyearid=finyearid
        ).order_by('vehno')

        context['vehicles'] = vehicles
        context['total_vehicles'] = vehicles.count()

        # Calculate aggregate statistics
        context['total_distance'] = vehicles.aggregate(
            total=Sum('fromto')
        )['total'] or 0

        context['avg_fuel'] = vehicles.aggregate(
            avg=Sum('avg')
        )['avg'] or 0

        return context


class ScheduleReportView(BaseDetailViewMixin, TemplateView):
    """Schedule Report - Auto WIS schedule report"""
    template_name = 'machinery/reports/schedule_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        schedules = TblinvAutowisTimeschedule.objects.filter(
            compid=compid, finyearid=finyearid
        ).order_by('-timetoorder')

        context['schedules'] = schedules
        context['total_schedules'] = schedules.count()

        # Add schedule statistics from service
        service = SchedulingService(compid, finyearid)
        context['upcoming_schedules'] = service.get_upcoming_schedules(limit=10)

        return context


class MachineryUtilizationView(BaseDetailViewMixin, TemplateView):
    """Machinery Utilization Report - Overall machinery utilization"""
    template_name = 'machinery/reports/utilization.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        context['vehicles'] = TblvehMasterDetails.objects.filter(
            compid=compid, finyearid=finyearid
        ).order_by('-date')

        context['processes'] = TblvehProcessMaster.objects.all()

        context['summary'] = {
            'total_vehicles': TblvehMasterDetails.objects.filter(
                compid=compid, finyearid=finyearid
            ).count(),
            'total_processes': TblvehProcessMaster.objects.count(),
            'total_schedules': TblinvAutowisTimeschedule.objects.filter(
                compid=compid, finyearid=finyearid
            ).count(),
        }

        # Add utilization metrics from service
        service = SchedulingService(compid, finyearid)
        context['utilization_metrics'] = service.calculate_utilization_metrics()

        return context
