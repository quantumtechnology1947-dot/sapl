"""
MIS Views Package

Re-exports all views from modular files for backward compatibility.
"""

# Dashboard and Menu Views
from .dashboard import (
    MISTransactionMenuView,
    AutocompleteView,
)

# Work Order Search and Budget Allocation Views
from .wo_search import (
    WorkOrderBudgetSearchView,
    BudgetAllocationView,
    WOBudgetDetailView,
)

# Budget Hours Views
from .budget_hours import (
    BudgetHoursAssignView,
    BudgetHoursWorkOrderSearchView,
    WOBudgetHoursDetailView,
    BudgetHoursSubCategoryAPIView,
)

# Budget Reports and Management Views
from .budget_reports import (
    BudgetCodeListView,
    BudgetCodeCreateView,
    BudgetCodeUpdateView,
    BudgetCodeDeleteView,
    BudgetCodeDetailView,
    BusinessGroupBudgetAssignView,
    BusinessGroupDetailView,
    BudgetHrsFieldCategorySubCategoryView,
)

__all__ = [
    # Dashboard
    'MISTransactionMenuView',
    'AutocompleteView',

    # Work Order Search
    'WorkOrderBudgetSearchView',
    'BudgetAllocationView',
    'WOBudgetDetailView',

    # Budget Hours
    'BudgetHoursAssignView',
    'BudgetHoursWorkOrderSearchView',
    'WOBudgetHoursDetailView',
    'BudgetHoursSubCategoryAPIView',

    # Budget Reports
    'BudgetCodeListView',
    'BudgetCodeCreateView',
    'BudgetCodeUpdateView',
    'BudgetCodeDeleteView',
    'BudgetCodeDetailView',
    'BusinessGroupBudgetAssignView',
    'BusinessGroupDetailView',
    'BudgetHrsFieldCategorySubCategoryView',
]
