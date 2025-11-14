"""
URL Configuration for Material Costing Module
"""

from django.urls import path
from . import views

app_name = 'material_costing'

urlpatterns = [
    # Dashboard
    path('', views.MaterialCostingDashboardView.as_view(), name='dashboard'),

    # Material Category
    path('materials/', views.MaterialCategoryView.as_view(), name='material-category'),

    # Live Cost Management
    path('live-costs/', views.LiveCostListView.as_view(), name='live-cost-list'),
    path('live-costs/create/', views.LiveCostCreateView.as_view(), name='live-cost-create'),
    path('live-costs/<int:cost_id>/update/', views.LiveCostUpdateView.as_view(), name='live-cost-update'),
    path('live-costs/<int:cost_id>/delete/', views.LiveCostDeleteView.as_view(), name='live-cost-delete'),
]
