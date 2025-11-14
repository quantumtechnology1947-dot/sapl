"""
Machinery Module URL Configuration
"""

from django.urls import path
from .views import (
    MachineryDashboardView,
    VehicleMasterListView,
    VehicleMasterCreateView,
    VehicleMasterDetailView,
    VehicleMasterUpdateView,
    VehicleMasterDeleteView,
    VehicleProcessListView,
    VehicleProcessCreateView,
    VehicleProcessDetailView,
    VehicleProcessUpdateView,
    VehicleProcessDeleteView,
    AutoWISScheduleListView,
    AutoWISScheduleCreateView,
    AutoWISScheduleDetailView,
    AutoWISScheduleUpdateView,
    AutoWISScheduleDeleteView,
    VehicleReportView,
    ScheduleReportView,
    MachineryUtilizationView,
)

app_name = 'machinery'

urlpatterns = [
    # Dashboard
    path('', MachineryDashboardView.as_view(), name='dashboard'),

    # Vehicle Master
    path('vehicle/', VehicleMasterListView.as_view(), name='vehicle-list'),
    path('vehicle/create/', VehicleMasterCreateView.as_view(), name='vehicle-create'),
    path('vehicle/<int:pk>/', VehicleMasterDetailView.as_view(), name='vehicle-detail'),
    path('vehicle/<int:pk>/edit/', VehicleMasterUpdateView.as_view(), name='vehicle-edit'),
    path('vehicle/<int:pk>/delete/', VehicleMasterDeleteView.as_view(), name='vehicle-delete'),

    # Vehicle Process
    path('process/', VehicleProcessListView.as_view(), name='process-list'),
    path('process/create/', VehicleProcessCreateView.as_view(), name='process-create'),
    path('process/<int:pk>/', VehicleProcessDetailView.as_view(), name='process-detail'),
    path('process/<int:pk>/edit/', VehicleProcessUpdateView.as_view(), name='process-edit'),
    path('process/<int:pk>/delete/', VehicleProcessDeleteView.as_view(), name='process-delete'),

    # Auto WIS Schedule
    path('schedule/', AutoWISScheduleListView.as_view(), name='schedule-list'),
    path('schedule/create/', AutoWISScheduleCreateView.as_view(), name='schedule-create'),
    path('schedule/<int:pk>/', AutoWISScheduleDetailView.as_view(), name='schedule-detail'),
    path('schedule/<int:pk>/edit/', AutoWISScheduleUpdateView.as_view(), name='schedule-edit'),
    path('schedule/<int:pk>/delete/', AutoWISScheduleDeleteView.as_view(), name='schedule-delete'),

    # Reports
    path('reports/vehicle-report/', VehicleReportView.as_view(), name='report-vehicle'),
    path('reports/schedule-report/', ScheduleReportView.as_view(), name='report-schedule'),
    path('reports/utilization/', MachineryUtilizationView.as_view(), name='report-utilization'),
]
