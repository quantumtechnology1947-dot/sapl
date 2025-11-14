"""
Reports Module URL Configuration
ASP.NET Reference: aaspnet/Module/Report/Reports/
Spec: .kiro/specs/reports-module/requirements.md
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('', views.ReportsDashboardView.as_view(), name='dashboard'),
    
    # Boughtout Reports
    path('boughtout/design/', views.BoughtoutDesignReportView.as_view(), name='boughtout-design'),
    path('boughtout/vendor/', views.BoughtoutVendorReportView.as_view(), name='boughtout-vendor'),
    path('boughtout/assembly/', views.BoughtoutAssemblyReportView.as_view(), name='boughtout-assembly'),
    
    # Manufacturing Reports
    path('manufacturing/design/', views.ManufacturingDesignReportView.as_view(), name='manufacturing-design'),
    path('manufacturing/vendor/', views.ManufacturingVendorReportView.as_view(), name='manufacturing-vendor'),
    path('manufacturing/assembly/', views.ManufacturingAssemblyReportView.as_view(), name='manufacturing-assembly'),
    
    # Export endpoints
    path('<str:report_type>/export/pdf/', views.ReportExportPDFView.as_view(), name='export-pdf'),
    path('<str:report_type>/export/excel/', views.ReportExportExcelView.as_view(), name='export-excel'),
]
