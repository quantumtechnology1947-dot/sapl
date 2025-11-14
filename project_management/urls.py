"""
Project Management Module URLs
"""

from django.urls import path
from . import views

app_name = 'project_management'

urlpatterns = [
    # Dashboard
    path('', views.ProjectManagementDashboardView.as_view(), name='dashboard'),

    # ManPower Planning
    path('manpower/', views.ManPowerPlanningListViewUniform.as_view(), name='manpower-list'),
    path('manpower/create/', views.ManPowerPlanningCreateView.as_view(), name='manpower-create'),
    path('manpower/<int:pk>/', views.ManPowerPlanningDetailView.as_view(), name='manpower-detail'),
    path('manpower/<int:pk>/update/', views.ManPowerPlanningUpdateView.as_view(), name='manpower-update'),
    path('manpower/<int:pk>/delete/', views.ManPowerPlanningDeleteView.as_view(), name='manpower-delete'),

    # Material Credit Note
    path('mcn/', views.MaterialCreditNoteListView.as_view(), name='mcn-list'),
    path('mcn/new/', views.MaterialCreditNoteNewView.as_view(), name='mcn-new'),
    path('mcn/create/', views.MaterialCreditNoteCreateView.as_view(), name='mcn-create'),
    path('mcn/<int:pk>/', views.MaterialCreditNoteDetailView.as_view(), name='mcn-detail'),
    path('mcn/<int:pk>/update/', views.MaterialCreditNoteUpdateView.as_view(), name='mcn-update'),
    path('mcn/<int:pk>/delete/', views.MaterialCreditNoteDeleteView.as_view(), name='mcn-delete'),

    # OnSite Attendance - ASP.NET Style
    path('attendance/', views.OnSiteAttendanceListView.as_view(), name='attendance-list-view'),
    path('attendance/new/', views.OnSiteAttendanceNewView.as_view(), name='attendance-new'),
    path('attendance/edit/', views.OnSiteAttendanceEditView.as_view(), name='attendance-edit'),
    path('attendance/delete/', views.OnSiteAttendanceDeleteView.as_view(), name='attendance-delete'),
    path('attendance/print/', views.OnSiteAttendancePrintView.as_view(), name='attendance-print'),

    # Project Planning
    path('project/', views.ProjectPlanningListViewUniform.as_view(), name='project-list'),
    path('project/create/', views.ProjectPlanningCreateView.as_view(), name='project-create'),
    path('project/<int:pk>/', views.ProjectPlanningDetailView.as_view(), name='project-detail'),
    path('project/<int:pk>/update/', views.ProjectPlanningUpdateView.as_view(), name='project-update'),
    path('project/<int:pk>/delete/', views.ProjectPlanningDeleteView.as_view(), name='project-delete'),
    path('project/<int:pk>/download/', views.ProjectPlanningDownloadFileView.as_view(), name='project-download'),

    # Project Status
    path('status/', views.ProjectStatusListView.as_view(), name='status-list'),
    path('status/create/', views.ProjectStatusCreateView.as_view(), name='status-create'),
    path('status/<int:pk>/', views.ProjectStatusDetailView.as_view(), name='status-detail'),
    path('status/<int:pk>/update/', views.ProjectStatusUpdateView.as_view(), name='status-update'),
    path('status/<int:pk>/delete/', views.ProjectStatusDeleteView.as_view(), name='status-delete'),
]
