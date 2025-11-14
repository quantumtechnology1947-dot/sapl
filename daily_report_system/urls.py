"""
Daily Reporting System URL Configuration
"""

from django.urls import path
from .views import (
    # Dashboard
    DRSDashboardView,
    # Design Plan
    DesignPlanListView,
    DesignPlanCreateView,
    DesignPlanUpdateView,
    DesignPlanDeleteView,
    DesignPlanDetailView,
    # Manufacturing Plan
    ManufacturingPlanListView,
    ManufacturingPlanCreateView,
    ManufacturingPlanUpdateView,
    ManufacturingPlanDeleteView,
    ManufacturingPlanDetailView,
    # Vendor Plan
    VendorPlanListView,
    VendorPlanCreateView,
    VendorPlanUpdateView,
    VendorPlanDeleteView,
    VendorPlanDetailView,
    # Hardware
    HardwarePlanListView,
    HardwarePlanDetailView,
    # Main Sheet
    ProjectMainSheetListView,
    ProjectMainSheetDetailView,
    # Reports
    DepartmentalWorkingPlanView,
    IndividualWorkingPlanView,
    DetailProjectPlanView,
    ProjectSummaryView,
)

app_name = 'daily_report_system'

urlpatterns = [
    # Dashboard
    path('', DRSDashboardView.as_view(), name='dashboard'),

    # Design Plan
    path('design-plan/', DesignPlanListView.as_view(), name='design-plan-list'),
    path('design-plan/create/', DesignPlanCreateView.as_view(), name='design-plan-create'),
    path('design-plan/<int:pk>/', DesignPlanDetailView.as_view(), name='design-plan-detail'),
    path('design-plan/<int:pk>/edit/', DesignPlanUpdateView.as_view(), name='design-plan-edit'),
    path('design-plan/<int:pk>/delete/', DesignPlanDeleteView.as_view(), name='design-plan-delete'),

    # Manufacturing Plan
    path('manufacturing-plan/', ManufacturingPlanListView.as_view(), name='manufacturing-plan-list'),
    path('manufacturing-plan/create/', ManufacturingPlanCreateView.as_view(), name='manufacturing-plan-create'),
    path('manufacturing-plan/<int:pk>/', ManufacturingPlanDetailView.as_view(), name='manufacturing-plan-detail'),
    path('manufacturing-plan/<int:pk>/edit/', ManufacturingPlanUpdateView.as_view(), name='manufacturing-plan-edit'),
    path('manufacturing-plan/<int:pk>/delete/', ManufacturingPlanDeleteView.as_view(), name='manufacturing-plan-delete'),

    # Vendor Plan
    path('vendor-plan/', VendorPlanListView.as_view(), name='vendor-plan-list'),
    path('vendor-plan/create/', VendorPlanCreateView.as_view(), name='vendor-plan-create'),
    path('vendor-plan/<int:pk>/', VendorPlanDetailView.as_view(), name='vendor-plan-detail'),
    path('vendor-plan/<int:pk>/edit/', VendorPlanUpdateView.as_view(), name='vendor-plan-edit'),
    path('vendor-plan/<int:pk>/delete/', VendorPlanDeleteView.as_view(), name='vendor-plan-delete'),

    # Hardware Plan
    path('hardware-plan/', HardwarePlanListView.as_view(), name='hardware-plan-list'),
    path('hardware-plan/<int:pk>/', HardwarePlanDetailView.as_view(), name='hardware-plan-detail'),

    # Project Main Sheet
    path('mainsheet/', ProjectMainSheetListView.as_view(), name='mainsheet-list'),
    path('mainsheet/<int:pk>/', ProjectMainSheetDetailView.as_view(), name='mainsheet-detail'),

    # Reports
    path('reports/departmental-working-plan/', DepartmentalWorkingPlanView.as_view(), name='report-departmental-working-plan'),
    path('reports/individual-working-plan/', IndividualWorkingPlanView.as_view(), name='report-individual-working-plan'),
    path('reports/detail-project-plan/', DetailProjectPlanView.as_view(), name='report-detail-project-plan'),
    path('reports/project-summary/', ProjectSummaryView.as_view(), name='report-project-summary'),
]
