"""
Material Planning Views Package

Refactored from monolithic views.py (2,412 lines) into focused view modules.
Each module handles a specific area of material planning functionality.
"""

# Base mixin used by all views
from .base import MaterialPlanningBaseMixin

# Dashboard
from .dashboard import MaterialPlanningDashboardView

# Plan CRUD and Print
from .plan import (
    MaterialPlanListView,
    MaterialPlanCreateView,
    MaterialPlanDetailView,
    MaterialPlanUpdateView,
    MaterialPlanDeleteView,
    PlanningPrintView,
)

# Plan Detail Management (RM/Process/Finish)
from .plan_detail import (
    PlanningEditView,
    PlanningEditDetailsView,
    BomItemDetailView,
    AddToTempView,
    PlanningSaveView,
)

# BOM Search and Integration
from .bom import (
    PlanningSearchView,
    PlanningCreateView,
    BomLoadView,
    SupplierAutocompleteView,
)

# Process Master CRUD
from .process_master import (
    ProcessMasterListView,
    ProcessMasterCreateView,
    ProcessMasterUpdateView,
    ProcessMasterDeleteView,
    ProcessMasterRowView,
)

# Reports
from .report import PlanningReportView

# Export all views
__all__ = [
    # Base
    'MaterialPlanningBaseMixin',

    # Dashboard
    'MaterialPlanningDashboardView',

    # Plan CRUD
    'MaterialPlanListView',
    'MaterialPlanCreateView',
    'MaterialPlanDetailView',
    'MaterialPlanUpdateView',
    'MaterialPlanDeleteView',
    'PlanningPrintView',

    # Plan Details
    'PlanningEditView',
    'PlanningEditDetailsView',
    'BomItemDetailView',
    'AddToTempView',
    'PlanningSaveView',

    # BOM
    'PlanningSearchView',
    'PlanningCreateView',
    'BomLoadView',
    'SupplierAutocompleteView',

    # Process Master
    'ProcessMasterListView',
    'ProcessMasterCreateView',
    'ProcessMasterUpdateView',
    'ProcessMasterDeleteView',
    'ProcessMasterRowView',

    # Reports
    'PlanningReportView',
]
