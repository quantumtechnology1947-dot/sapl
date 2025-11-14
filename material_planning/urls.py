"""
URL Configuration for Material Planning Module
"""

from django.urls import path
from . import views

app_name = 'material_planning'

urlpatterns = [
    # Dashboard
    path('', views.MaterialPlanningDashboardView.as_view(), name='dashboard'),

    # Process Master (Masters)
    path('process/', views.ProcessMasterListView.as_view(), name='process-list'),
    path('process/create/', views.ProcessMasterCreateView.as_view(), name='process-create'),
    path('process/<int:id>/edit/', views.ProcessMasterUpdateView.as_view(), name='process-edit'),
    path('process/<int:id>/delete/', views.ProcessMasterDeleteView.as_view(), name='process-delete'),
    path('process/<int:id>/row/', views.ProcessMasterRowView.as_view(), name='process-row'),
    
    # Material Plan List and Details (Planning Edit & Edit Details)
    path('plans/', views.MaterialPlanListView.as_view(), name='plan-list'),
    path('plans/<int:plan_id>/', views.MaterialPlanDetailView.as_view(), name='plan-detail'),  # Changed to only use plan_id

    # Planning Search & Create (for future implementation)
    path('planning/search/', views.PlanningSearchView.as_view(), name='planning-search'),
    path('planning/create/<str:wono>/', views.PlanningCreateView.as_view(), name='planning-create'),

    # Material Plan CRUD (keeping for compatibility)
    path('plans/create/', views.MaterialPlanCreateView.as_view(), name='plan-create'),
    path('plans/<int:plan_id>/update/', views.MaterialPlanUpdateView.as_view(), name='plan-update'),
    path('plans/<int:plan_id>/delete/', views.MaterialPlanDeleteView.as_view(), name='plan-delete'),
    
    # HTMX Endpoints
    path('api/supplier-autocomplete/', views.SupplierAutocompleteView.as_view(), name='supplier-autocomplete'),
    path('api/supplier-search/', views.SupplierAutocompleteView.as_view(), name='supplier-search'),  # Backward compatibility (alias)
    path('api/bom-load/<str:wono>/', views.BomLoadView.as_view(), name='bom-load'),
    path('api/bom-item-detail/<str:wono>/<int:item_id>/', views.BomItemDetailView.as_view(), name='bom-item-detail'),
    path('api/add-to-temp/<str:wono>/', views.AddToTempView.as_view(), name='add-to-temp'),
    path('api/planning-save/<str:wono>/', views.PlanningSaveView.as_view(), name='planning-save'),
    path('plans/inline-edit/', views.MaterialPlanListView.as_view(), name='plan-inline-edit'),
    
    # Reports
    path('reports/', views.PlanningReportView.as_view(), name='planning-report'),
    path('plans/<int:plan_id>/print/', views.PlanningPrintView.as_view(), name='planning-print'),
]
