"""
Material Management Views Module

All views re-exported from modular files for backward compatibility with urls.py
This allows urls.py to continue using `from . import views` without modification.

Structure:
- dashboard.py: Dashboard + Base mixin (2 classes)
- masters.py: BusinessNature, BusinessType, ServiceCoverage (12 views)
- buyer.py: Buyer master + Employee autocomplete (5 views)
- supplier.py: Supplier master + Scope report (6 views)
- rate.py: Rate management views (9 views)
- pr.py: Purchase Requisition views (9 views)
- spr.py: Special Purpose Requisition views (9 views)
- po.py: Purchase Order views (16 views)
- reports.py: Report views (4 views)
- api.py: API endpoints (3 views)

Total: 76 view classes
"""

# Dashboard & Base Mixin
from .dashboard import (
    MaterialManagementDashboardView,
    MaterialManagementBaseMixin,
)

# Masters - BusinessNature, BusinessType, ServiceCoverage
from .masters import (
    BusinessNatureListView,
    BusinessNatureCreateView,
    BusinessNatureUpdateView,
    BusinessNatureDeleteView,
    BusinessTypeListView,
    BusinessTypeCreateView,
    BusinessTypeUpdateView,
    BusinessTypeDeleteView,
    ServiceCoverageListView,
    ServiceCoverageCreateView,
    ServiceCoverageUpdateView,
    ServiceCoverageDeleteView,
)

# Buyer - Buyer master + Employee autocomplete
from .buyer import (
    BuyerListView,
    BuyerCreateView,
    BuyerUpdateView,
    BuyerDeleteView,
    EmployeeAutocompleteView,
)

# Supplier - Supplier master + Scope report
from .supplier import (
    SupplierListView,
    SupplierCreateView,
    SupplierDetailView,
    SupplierUpdateView,
    SupplierDeleteView,
    ScopeOfSupplierView,
)

# Rate - Rate Register and Lock/Unlock views
from .rate import (
    RateSetSearchView,
    RateSetDetailsView,
    RateRegisterListView,
    RateRegisterDetailView,
    RateLockUnlockView,
    RateLockUnlockListView,
    RateLockUnlockToggleView,
    RateLockUnlockActionView,
    RateLockUnlockReportView,
)

# PR - Purchase Requisition views
from .pr import (
    PRListView,
    PRNewSearchView,
    PRNewDetailsView,
    PRDetailView,
    PRUpdateView,
    PRDeleteView,
    PRCheckView,
    PRApproveView,
    PRAuthorizeView,
)

# SPR - Special Purpose Requisition views
from .spr import (
    SPRListView,
    SPRNewView,
    SPRNewDetailsView,
    SPRDetailView,
    SPRUpdateView,
    SPRDeleteView,
    SPRCheckView,
    SPRApproveView,
    SPRAuthorizeView,
)

# PO - Purchase Order views
from .po import (
    POListView,
    PONewView,
    POPRItemsView,
    POSPRItemsView,
    POPRItemSelectView,
    POSPRItemSelectView,
    POHeaderView,
    PODetailView,
    POUpdateView,
    PODeleteView,
    POCheckActionView,
    POApproveActionView,
    POAuthorizeActionView,
    POCheckView,
    POApproveView,
    POAuthorizeView,
)

# Reports - Report views
from .reports import (
    RateRegisterReportView,
    SupplierRatingReportView,
    MaterialForecastingReportView,
    MaterialSearchView,
)

# API - API endpoints
from .api import (
    ItemSearchAPIView,
    SupplierAutocompleteAPIView,
    SupplierRateAPIView,
)

# Re-export all views for backward compatibility
__all__ = [
    # Base (2)
    'MaterialManagementBaseMixin',
    'MaterialManagementDashboardView',

    # Masters (12)
    'BusinessNatureListView',
    'BusinessNatureCreateView',
    'BusinessNatureUpdateView',
    'BusinessNatureDeleteView',
    'BusinessTypeListView',
    'BusinessTypeCreateView',
    'BusinessTypeUpdateView',
    'BusinessTypeDeleteView',
    'ServiceCoverageListView',
    'ServiceCoverageCreateView',
    'ServiceCoverageUpdateView',
    'ServiceCoverageDeleteView',

    # Buyer (5)
    'BuyerListView',
    'BuyerCreateView',
    'BuyerUpdateView',
    'BuyerDeleteView',
    'EmployeeAutocompleteView',

    # Supplier (6)
    'SupplierListView',
    'SupplierCreateView',
    'SupplierDetailView',
    'SupplierUpdateView',
    'SupplierDeleteView',
    'ScopeOfSupplierView',

    # Rate (9)
    'RateSetSearchView',
    'RateSetDetailsView',
    'RateRegisterListView',
    'RateRegisterDetailView',
    'RateLockUnlockView',
    'RateLockUnlockListView',
    'RateLockUnlockToggleView',
    'RateLockUnlockActionView',
    'RateLockUnlockReportView',

    # PR (9)
    'PRListView',
    'PRNewSearchView',
    'PRNewDetailsView',
    'PRDetailView',
    'PRUpdateView',
    'PRDeleteView',
    'PRCheckView',
    'PRApproveView',
    'PRAuthorizeView',

    # SPR (9)
    'SPRListView',
    'SPRNewView',
    'SPRNewDetailsView',
    'SPRDetailView',
    'SPRUpdateView',
    'SPRDeleteView',
    'SPRCheckView',
    'SPRApproveView',
    'SPRAuthorizeView',

    # PO (16)
    'POListView',
    'PONewView',
    'POPRItemsView',
    'POSPRItemsView',
    'POPRItemSelectView',
    'POSPRItemSelectView',
    'POHeaderView',
    'PODetailView',
    'POUpdateView',
    'PODeleteView',
    'POCheckActionView',
    'POApproveActionView',
    'POAuthorizeActionView',
    'POCheckView',
    'POApproveView',
    'POAuthorizeView',

    # Reports (4)
    'RateRegisterReportView',
    'SupplierRatingReportView',
    'MaterialForecastingReportView',
    'MaterialSearchView',

    # API (3)
    'ItemSearchAPIView',
    'SupplierAutocompleteAPIView',
    'SupplierRateAPIView',
]
