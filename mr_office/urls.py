"""
MR Office Module URL Configuration
Converted from: aaspnet/Module/MROffice/
"""

from django.urls import path
from . import views

app_name = 'mr_office'

urlpatterns = [
    # Dashboard
    path('', views.MROfficeDashboardView.as_view(), name='dashboard'),

    # Documents (MR Office - ISO)
    path('documents/', views.DocumentListView.as_view(), name='document-list'),
    path('documents/create/', views.DocumentCreateView.as_view(), name='document-create'),
    path('documents/upload/', views.DocumentCreateView.as_view(), name='document-upload'),  # Alias for create
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<int:pk>/download/', views.DocumentDownloadView.as_view(), name='document-download'),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document-delete'),

    # Reports
    path('reports/storage/', views.DocumentStorageReportView.as_view(), name='storage-report'),
    path('reports/by-module/', views.DocumentListByModuleView.as_view(), name='by-module-report'),
]
