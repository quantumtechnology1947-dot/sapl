"""
Design Views Module
Refactored from monolithic views.py (3,382 lines) into focused modules.

Module Structure:
- category.py: Category Master CRUD (4 views)
- subcategory.py: Sub-Category Master CRUD (4 views)
- item.py: Item Master CRUD + downloads (7 views)
- bom.py: BOM Management + API endpoints (28 views)
- ecn.py: ECN Management (11 views)
- reports.py: Item History BOM reports (3 views)
- utilities.py: Unit Master, ECN Reason, SubCategory helper (9 views)

Total: 61 views across 7 modules
"""

# Category Master (4 views)
from .category import (
    DesignCategoryListView,
    DesignCategoryCreateView,
    DesignCategoryUpdateView,
    DesignCategoryDeleteView,
)

# Sub-Category Master (4 views)
from .subcategory import (
    DesignSubCategoryListView,
    DesignSubCategoryCreateView,
    DesignSubCategoryUpdateView,
    DesignSubCategoryDeleteView,
)

# Item Master (7 views)
from .item import (
    ItemMasterListView,
    ItemMasterDetailView,
    ItemMasterCreateView,
    ItemMasterUpdateView,
    ItemMasterDeleteView,
    ItemFileDownloadView,
    ItemAttachmentDownloadView,
)

# BOM Management (28 views)
from .bom import (
    # Core BOM views
    BomListView,
    BomCreateSelectWoView,
    BomTreeView,
    BomCreateView,
    BomUpdateView,
    BomDeleteView,
    BomCopyView,
    
    # Assembly and Child Management
    BomCreateAssemblyView,
    BomAddChildView,
    BomAddItemsView,
    
    # 4-Tab Wizard
    BomAddItemsWizardView,
    BomWizardSearchItemsView,
    BomWizardAddExistingItemView,
    BomWizardAddNewItemView,
    BomWizardRemoveItemView,
    BomWizardCommitView,
    BomWizardCancelView,
    
    # API Endpoints
    ItemSearchApiView,
    BomUpdateQuantityApiView,
    BomSearchItemsApiView,
    BomStageItemApiView,
    BomGetStagedItemsApiView,
    BomUnstagItemApiView,
    BomCommitStagedItemsApiView,
    BomClearStagedItemsApiView,
    BomBulkDeleteApiView,
)

# ECN Management (11 views)
from .ecn import (
    EcnListView,
    EcnDetailView,
    EcnCreateView,
    EcnUpdateView,
    EcnApplyView,
    EcnUnlockView,
)

# Reports (3 views)
from .reports import (
    ItemHistoryBomSearchView,
    ItemHistoryBomDetailView,
    BomAmendmentHistoryView,
)

# Utilities (9 views)
from .utilities import (
    SubCategoryByCategoryView,
    UnitMasterListView,
    UnitMasterCreateView,
    UnitMasterUpdateView,
    UnitMasterDeleteView,
    EcnReasonListView,
    EcnReasonCreateView,
    EcnReasonUpdateView,
    EcnReasonDeleteView,
    EcnWoListView,
)

# Export all views for backwards compatibility
__all__ = [
    # Category Master
    'DesignCategoryListView',
    'DesignCategoryCreateView',
    'DesignCategoryUpdateView',
    'DesignCategoryDeleteView',
    
    # Sub-Category Master
    'DesignSubCategoryListView',
    'DesignSubCategoryCreateView',
    'DesignSubCategoryUpdateView',
    'DesignSubCategoryDeleteView',
    
    # Item Master
    'ItemMasterListView',
    'ItemMasterDetailView',
    'ItemMasterCreateView',
    'ItemMasterUpdateView',
    'ItemMasterDeleteView',
    'ItemFileDownloadView',
    'ItemAttachmentDownloadView',
    
    # BOM Management
    'BomListView',
    'BomCreateSelectWoView',
    'BomTreeView',
    'BomCreateView',
    'BomUpdateView',
    'BomDeleteView',
    'BomCopyView',
    'BomCreateAssemblyView',
    'BomAddChildView',
    'BomAddItemsView',
    'BomAddItemsWizardView',
    'BomWizardSearchItemsView',
    'BomWizardAddExistingItemView',
    'BomWizardAddNewItemView',
    'BomWizardRemoveItemView',
    'BomWizardCommitView',
    'BomWizardCancelView',
    'ItemSearchApiView',
    'BomUpdateQuantityApiView',
    'BomSearchItemsApiView',
    'BomStageItemApiView',
    'BomGetStagedItemsApiView',
    'BomUnstagItemApiView',
    'BomCommitStagedItemsApiView',
    'BomClearStagedItemsApiView',
    'BomBulkDeleteApiView',
    
    # ECN Management
    'EcnListView',
    'EcnDetailView',
    'EcnCreateView',
    'EcnUpdateView',
    'EcnApplyView',
    'EcnUnlockView',
    
    # Reports
    'ItemHistoryBomSearchView',
    'ItemHistoryBomDetailView',
    'BomAmendmentHistoryView',
    
    # Utilities
    'SubCategoryByCategoryView',
    'UnitMasterListView',
    'UnitMasterCreateView',
    'UnitMasterUpdateView',
    'UnitMasterDeleteView',
    'EcnReasonListView',
    'EcnReasonCreateView',
    'EcnReasonUpdateView',
    'EcnReasonDeleteView',
    'EcnWoListView',
]
