"""
Daily Reporting System Views

Modularized view components for all DRS functionality.
"""

from .dashboard import DRSDashboardView
from .design_plan import (
    DesignPlanListView,
    DesignPlanCreateView,
    DesignPlanUpdateView,
    DesignPlanDeleteView,
    DesignPlanDetailView,
)
from .manufacturing_plan import (
    ManufacturingPlanListView,
    ManufacturingPlanCreateView,
    ManufacturingPlanUpdateView,
    ManufacturingPlanDeleteView,
    ManufacturingPlanDetailView,
)
from .vendor_plan import (
    VendorPlanListView,
    VendorPlanCreateView,
    VendorPlanUpdateView,
    VendorPlanDeleteView,
    VendorPlanDetailView,
)
from .hardware import (
    HardwarePlanListView,
    HardwarePlanDetailView,
)
from .mainsheet import (
    ProjectMainSheetListView,
    ProjectMainSheetDetailView,
)
from .reports import (
    DepartmentalWorkingPlanView,
    IndividualWorkingPlanView,
    DetailProjectPlanView,
    ProjectSummaryView,
)

__all__ = [
    # Dashboard
    'DRSDashboardView',
    # Design Plan
    'DesignPlanListView',
    'DesignPlanCreateView',
    'DesignPlanUpdateView',
    'DesignPlanDeleteView',
    'DesignPlanDetailView',
    # Manufacturing Plan
    'ManufacturingPlanListView',
    'ManufacturingPlanCreateView',
    'ManufacturingPlanUpdateView',
    'ManufacturingPlanDeleteView',
    'ManufacturingPlanDetailView',
    # Vendor Plan
    'VendorPlanListView',
    'VendorPlanCreateView',
    'VendorPlanUpdateView',
    'VendorPlanDeleteView',
    'VendorPlanDetailView',
    # Hardware
    'HardwarePlanListView',
    'HardwarePlanDetailView',
    # Main Sheet
    'ProjectMainSheetListView',
    'ProjectMainSheetDetailView',
    # Reports
    'DepartmentalWorkingPlanView',
    'IndividualWorkingPlanView',
    'DetailProjectPlanView',
    'ProjectSummaryView',
]
