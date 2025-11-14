"""
URL configuration for core app.
Handles authentication and dashboard routes.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', views.DashboardView.as_view(), name='home'),
    
    # Financial Year Context Switching
    path('context/company-list/', views.CompanyListView.as_view(), name='company-list'),
    path('context/finyear-list/', views.FinYearListView.as_view(), name='finyear-list'),
    path('context/switch-company/', views.SwitchCompanyView.as_view(), name='switch-company'),
    path('context/switch-finyear/', views.SwitchFinYearView.as_view(), name='switch-finyear'),

    # HTMX Utility endpoints
    path('empty/', views.EmptyView.as_view(), name='empty'),
]
