"""
SysAdmin URL Configuration
Converted from ASP.NET Module/SysAdmin
"""

from django.urls import path
from . import views

app_name = 'sys_admin'

urlpatterns = [
    # Dashboard
    path('', views.SysAdminDashboardView.as_view(), name='dashboard'),
    
    # Country Master
    path('country/', views.CountryListView.as_view(), name='country-list'),
    path('country/create/', views.CountryCreateView.as_view(), name='country-create'),
    path('country/<int:cid>/edit/', views.CountryUpdateView.as_view(), name='country-edit'),
    path('country/<int:cid>/delete/', views.CountryDeleteView.as_view(), name='country-delete'),
    path('country/<int:cid>/row/', views.CountryRowView.as_view(), name='country-row'),
    
    # State Master
    path('state/', views.StateListView.as_view(), name='state-list'),
    path('state/create/', views.StateCreateView.as_view(), name='state-create'),
    path('state/<int:sid>/edit/', views.StateUpdateView.as_view(), name='state-edit'),
    path('state/<int:sid>/delete/', views.StateDeleteView.as_view(), name='state-delete'),
    path('state/<int:sid>/row/', views.StateRowView.as_view(), name='state-row'),
    
    # City Master
    path('city/', views.CityListView.as_view(), name='city-list'),
    path('city/create/', views.CityCreateView.as_view(), name='city-create'),
    path('city/<int:cityid>/edit/', views.CityUpdateView.as_view(), name='city-edit'),
    path('city/<int:cityid>/delete/', views.CityDeleteView.as_view(), name='city-delete'),
    path('city/<int:cityid>/row/', views.CityRowView.as_view(), name='city-row'),
    
    # HTMX Cascade Endpoints
    path('states-by-country/<int:cid>/', views.StatesByCountryView.as_view(), name='states-by-country'),
    path('states-by-country/', views.StatesByCountryView.as_view(), name='states-by-country-query'),
    
    # Financial Year Master
    path('financial-year/', views.FinancialYearListView.as_view(), name='financial_year_list'),
    path('financial-year/', views.FinancialYearListView.as_view(), name='financial-year-list'),  # Alias
    path('financial-year/create/', views.FinancialYearCreateView.as_view(), name='financial_year_create'),
    path('financial-year/confirm/', views.FinancialYearConfirmView.as_view(), name='financial-year-confirm'),
    path('financial-year/<int:pk>/', views.FinancialYearDetailsView.as_view(), name='financial_year_details'),
    path('financial-year/<int:pk>/edit/', views.FinancialYearUpdateView.as_view(), name='financial_year_edit'),
    path('financial-year/<int:finyearid>/edit/', views.FinancialYearUpdateView.as_view(), name='financial-year-edit'),  # Alias for inline editing
    path('financial-year/<int:pk>/delete/', views.FinancialYearDeleteView.as_view(), name='financial_year_delete'),
    path('financial-year/<int:finyearid>/delete/', views.FinancialYearDeleteView.as_view(), name='financial-year-delete'),  # Alias for inline deletion
    path('financial-year/<int:finyearid>/row/', views.FinancialYearRowView.as_view(), name='financial-year-row'),
    
    # Unit Master
    path('unit/', views.UnitMasterListView.as_view(), name='unit-master-list'),
    path('unit/create/', views.UnitMasterCreateView.as_view(), name='unit-master-create'),
    path('unit/<int:id>/edit/', views.UnitMasterUpdateView.as_view(), name='unit-master-edit'),
    path('unit/<int:id>/delete/', views.UnitMasterDeleteView.as_view(), name='unit-master-delete'),
    
    # GST Master
    path('gst-master/', views.GSTMasterListView.as_view(), name='gst-master-list'),
    path('gst-master/create/', views.GSTMasterCreateView.as_view(), name='gst-master-create'),
    path('gst-master/<int:pk>/edit/', views.GSTMasterUpdateView.as_view(), name='gst-master-edit'),
    path('gst-master/<int:pk>/delete/', views.GSTMasterDeleteView.as_view(), name='gst-master-delete'),
    path('gst-master/<int:pk>/', views.GSTMasterDetailView.as_view(), name='gst-master-detail'),
]
