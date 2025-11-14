
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Django browser reload (development only)
    path('__reload__/', include('django_browser_reload.urls')),
    
    # ERP app URLs
    path('', include('core.urls')),
    path('sys-admin/', include('sys_admin.urls')),
    path('hr/', include('human_resource.urls')),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales_distribution.urls')),
    path('design/', include('design.urls')),
    path('material-management/', include('material_management.urls')),
    path('material-planning/', include('material_planning.urls')),
    path('material-costing/', include('material_costing.urls')),
    path('projects/', include('project_management.urls')),
    path('quality/', include('quality_control.urls')),
    path('mis/', include('mis.urls')),
    path('mr-office/', include('mr_office.urls')),
    path('daily-reports/', include('daily_report_system.urls')),
    path('machinery/', include('machinery.urls')),
    # path('reports/', include('reports.urls')),  # TEMPORARILY DISABLED - has import errors
]
