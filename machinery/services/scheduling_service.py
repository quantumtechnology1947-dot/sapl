"""
Scheduling Service

Business logic for schedule calculations, availability checks, and conflict detection.
"""

from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum
from typing import List, Dict, Optional

from ..models import (
    TblinvAutowisTimeschedule,
    TblvehMasterDetails,
    TblvehProcessMaster,
)


class SchedulingService:
    """Service for handling schedule-related business logic"""

    def __init__(self, compid: int, finyearid: int):
        """
        Initialize service with company and financial year context.

        Args:
            compid: Company ID
            finyearid: Financial Year ID
        """
        self.compid = compid
        self.finyearid = finyearid

    def get_upcoming_schedules(self, limit: int = 10) -> List[TblinvAutowisTimeschedule]:
        """
        Get upcoming schedules ordered by time.

        Args:
            limit: Maximum number of schedules to return

        Returns:
            List of upcoming TblinvAutowisTimeschedule objects
        """
        now = datetime.now()
        return TblinvAutowisTimeschedule.objects.filter(
            compid=self.compid,
            finyearid=self.finyearid,
            timetoorder__gte=now
        ).order_by('timetoorder')[:limit]

    def get_overdue_schedules(self) -> List[TblinvAutowisTimeschedule]:
        """
        Get schedules that are overdue (timetoorder in the past).

        Returns:
            List of overdue TblinvAutowisTimeschedule objects
        """
        now = datetime.now()
        return TblinvAutowisTimeschedule.objects.filter(
            compid=self.compid,
            finyearid=self.finyearid,
            timetoorder__lt=now
        ).order_by('timetoorder')

    def check_schedule_conflict(
        self,
        timetoorder: datetime,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if a schedule conflicts with existing schedules.

        Args:
            timetoorder: Proposed schedule time
            exclude_id: Schedule ID to exclude from conflict check (for updates)

        Returns:
            True if conflict exists, False otherwise
        """
        # Define conflict window (e.g., 1 hour before and after)
        conflict_window = timedelta(hours=1)
        start_time = timetoorder - conflict_window
        end_time = timetoorder + conflict_window

        query = TblinvAutowisTimeschedule.objects.filter(
            compid=self.compid,
            finyearid=self.finyearid,
            timetoorder__range=(start_time, end_time)
        )

        if exclude_id:
            query = query.exclude(id=exclude_id)

        return query.exists()

    def get_available_time_slots(
        self,
        date: datetime.date,
        start_hour: int = 8,
        end_hour: int = 18
    ) -> List[datetime]:
        """
        Get available time slots for a given date.

        Args:
            date: Date to check availability
            start_hour: Start of working hours (default 8 AM)
            end_hour: End of working hours (default 6 PM)

        Returns:
            List of available datetime slots
        """
        available_slots = []

        # Get existing schedules for the date
        existing_schedules = TblinvAutowisTimeschedule.objects.filter(
            compid=self.compid,
            finyearid=self.finyearid,
            timetoorder__date=date
        ).values_list('timetoorder', flat=True)

        existing_times = set(
            schedule.replace(minute=0, second=0, microsecond=0)
            for schedule in existing_schedules
        )

        # Generate hourly slots
        for hour in range(start_hour, end_hour):
            slot = datetime.combine(date, datetime.min.time()).replace(hour=hour)
            if slot not in existing_times:
                available_slots.append(slot)

        return available_slots

    def calculate_utilization_metrics(self) -> Dict[str, any]:
        """
        Calculate machinery and vehicle utilization metrics.

        Returns:
            Dictionary containing utilization statistics
        """
        # Vehicle metrics
        vehicles = TblvehMasterDetails.objects.filter(
            compid=self.compid,
            finyearid=self.finyearid
        )

        total_vehicles = vehicles.count()
        total_distance = vehicles.aggregate(total=Sum('fromto'))['total'] or 0
        total_fuel_cost = vehicles.aggregate(total=Sum('fluel_rs'))['total'] or 0
        avg_distance_per_vehicle = total_distance / total_vehicles if total_vehicles > 0 else 0

        # Schedule metrics
        schedules = TblinvAutowisTimeschedule.objects.filter(
            compid=self.compid,
            finyearid=self.finyearid
        )
        total_schedules = schedules.count()

        now = datetime.now()
        upcoming_count = schedules.filter(timetoorder__gte=now).count()
        overdue_count = schedules.filter(timetoorder__lt=now).count()

        # Process metrics
        total_processes = TblvehProcessMaster.objects.count()

        return {
            'vehicles': {
                'total': total_vehicles,
                'total_distance': total_distance,
                'total_fuel_cost': total_fuel_cost,
                'avg_distance_per_vehicle': round(avg_distance_per_vehicle, 2),
            },
            'schedules': {
                'total': total_schedules,
                'upcoming': upcoming_count,
                'overdue': overdue_count,
                'completion_rate': round(
                    (total_schedules - overdue_count) / total_schedules * 100, 2
                ) if total_schedules > 0 else 0,
            },
            'processes': {
                'total': total_processes,
            },
        }

    def get_vehicle_schedule_summary(
        self,
        vehicle_id: int
    ) -> Dict[str, any]:
        """
        Get schedule summary for a specific vehicle.

        Args:
            vehicle_id: Vehicle ID

        Returns:
            Dictionary with vehicle schedule information
        """
        try:
            vehicle = TblvehMasterDetails.objects.get(
                id=vehicle_id,
                compid=self.compid,
                finyearid=self.finyearid
            )
        except TblvehMasterDetails.DoesNotExist:
            return {}

        # Calculate vehicle-specific metrics
        total_distance = vehicle.fromto or 0
        fuel_cost = vehicle.fluel_rs or 0
        avg_fuel = vehicle.avg or 0

        return {
            'vehicle': {
                'id': vehicle.id,
                'vehno': vehicle.vehno,
                'vehical_name': vehicle.vehical_name,
                'destination': vehicle.destination,
            },
            'metrics': {
                'total_distance': total_distance,
                'fuel_cost': fuel_cost,
                'avg_fuel': avg_fuel,
                'cost_per_km': round(fuel_cost / total_distance, 2) if total_distance > 0 else 0,
            },
        }

    def optimize_schedule(self) -> List[Dict[str, any]]:
        """
        Suggest optimized schedule based on current data.

        Returns:
            List of schedule optimization suggestions
        """
        suggestions = []

        # Check for overdue schedules
        overdue = self.get_overdue_schedules()
        if overdue:
            suggestions.append({
                'type': 'overdue',
                'priority': 'high',
                'message': f'{len(overdue)} overdue schedules need attention',
                'count': len(overdue),
            })

        # Check for scheduling gaps
        upcoming = self.get_upcoming_schedules(limit=50)
        if upcoming:
            # Analyze gaps between schedules
            times = [s.timetoorder for s in upcoming if s.timetoorder]
            times.sort()

            for i in range(len(times) - 1):
                gap = times[i + 1] - times[i]
                if gap > timedelta(days=7):  # Gap larger than 7 days
                    suggestions.append({
                        'type': 'gap',
                        'priority': 'medium',
                        'message': f'Large gap detected: {gap.days} days between schedules',
                        'start_date': times[i].isoformat(),
                        'end_date': times[i + 1].isoformat(),
                    })

        # Check vehicle utilization
        vehicles = TblvehMasterDetails.objects.filter(
            compid=self.compid,
            finyearid=self.finyearid
        )

        inactive_vehicles = vehicles.filter(
            Q(fromto__isnull=True) | Q(fromto=0)
        ).count()

        if inactive_vehicles > 0:
            suggestions.append({
                'type': 'underutilized',
                'priority': 'low',
                'message': f'{inactive_vehicles} vehicles have no distance recorded',
                'count': inactive_vehicles,
            })

        return suggestions
