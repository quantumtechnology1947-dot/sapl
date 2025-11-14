"""
Machinery Views Package

Re-exports all views for convenient import.
"""

# Dashboard
from .dashboard import MachineryDashboardView

# Vehicle Master Views
from .vehicle import (
    VehicleMasterListView,
    VehicleMasterCreateView,
    VehicleMasterUpdateView,
    VehicleMasterDeleteView,
    VehicleMasterDetailView,
)

# Vehicle Process Views
from .process import (
    VehicleProcessListView,
    VehicleProcessCreateView,
    VehicleProcessUpdateView,
    VehicleProcessDeleteView,
    VehicleProcessDetailView,
)

# Schedule Views
from .schedule import (
    AutoWISScheduleListView,
    AutoWISScheduleCreateView,
    AutoWISScheduleUpdateView,
    AutoWISScheduleDeleteView,
    AutoWISScheduleDetailView,
)

# Report Views
from .reports import (
    VehicleReportView,
    ScheduleReportView,
    MachineryUtilizationView,
)

__all__ = [
    # Dashboard
    'MachineryDashboardView',

    # Vehicle Master
    'VehicleMasterListView',
    'VehicleMasterCreateView',
    'VehicleMasterUpdateView',
    'VehicleMasterDeleteView',
    'VehicleMasterDetailView',

    # Vehicle Process
    'VehicleProcessListView',
    'VehicleProcessCreateView',
    'VehicleProcessUpdateView',
    'VehicleProcessDeleteView',
    'VehicleProcessDetailView',

    # Schedule
    'AutoWISScheduleListView',
    'AutoWISScheduleCreateView',
    'AutoWISScheduleUpdateView',
    'AutoWISScheduleDeleteView',
    'AutoWISScheduleDetailView',

    # Reports
    'VehicleReportView',
    'ScheduleReportView',
    'MachineryUtilizationView',
]
