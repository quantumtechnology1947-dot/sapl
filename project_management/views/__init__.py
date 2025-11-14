"""
Project Management Views

Modular view organization for better maintainability.
All views are re-exported here to maintain backward compatibility with urls.py.
"""

# Dashboard
from .dashboard import ProjectManagementDashboardView

# ManPower Planning Views
from .manpower import (
    ManPowerPlanningListViewUniform,
    ManPowerPlanningCreateView,
    ManPowerPlanningDetailView,
    ManPowerPlanningUpdateView,
    ManPowerPlanningDeleteView,
)

# Material Credit Note Views
from .material_credit_note import (
    MaterialCreditNoteNewView,
    MaterialCreditNoteListView,
    MaterialCreditNoteCreateView,
    MaterialCreditNoteDetailView,
    MaterialCreditNoteUpdateView,
    MaterialCreditNoteDeleteView,
)

# Project Planning Views
from .project_planning import (
    ProjectPlanningListView,
    ProjectPlanningListViewUniform,
    ProjectPlanningCreateView,
    ProjectPlanningDetailView,
    ProjectPlanningUpdateView,
    ProjectPlanningDeleteView,
    ProjectPlanningDownloadFileView,
    ProjectStatusListView,
    ProjectStatusCreateView,
    ProjectStatusDetailView,
    ProjectStatusUpdateView,
    ProjectStatusDeleteView,
)

# OnSite Attendance Views
from .attendance import (
    OnSiteAttendanceListView,
    OnSiteAttendanceNewView,
    OnSiteAttendanceEditView,
    OnSiteAttendanceDeleteView,
    OnSiteAttendancePrintView,
)

# Export all views for backward compatibility
__all__ = [
    # Dashboard
    'ProjectManagementDashboardView',

    # ManPower Planning
    'ManPowerPlanningListViewUniform',
    'ManPowerPlanningCreateView',
    'ManPowerPlanningDetailView',
    'ManPowerPlanningUpdateView',
    'ManPowerPlanningDeleteView',

    # Material Credit Note
    'MaterialCreditNoteNewView',
    'MaterialCreditNoteListView',
    'MaterialCreditNoteCreateView',
    'MaterialCreditNoteDetailView',
    'MaterialCreditNoteUpdateView',
    'MaterialCreditNoteDeleteView',

    # Project Planning
    'ProjectPlanningListView',
    'ProjectPlanningListViewUniform',
    'ProjectPlanningCreateView',
    'ProjectPlanningDetailView',
    'ProjectPlanningUpdateView',
    'ProjectPlanningDeleteView',
    'ProjectPlanningDownloadFileView',
    'ProjectStatusListView',
    'ProjectStatusCreateView',
    'ProjectStatusDetailView',
    'ProjectStatusUpdateView',
    'ProjectStatusDeleteView',

    # OnSite Attendance
    'OnSiteAttendanceListView',
    'OnSiteAttendanceNewView',
    'OnSiteAttendanceEditView',
    'OnSiteAttendanceDeleteView',
    'OnSiteAttendancePrintView',
]
