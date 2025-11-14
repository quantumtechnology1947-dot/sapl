# Material Management Module Refactoring Plan

## Executive Summary

This document outlines the comprehensive refactoring of the `material_management` Django app module, splitting the monolithic `views.py` (4,562 lines, 76 views) into focused, maintainable modules with extracted business logic.

**Status:** services.py ✅ CREATED | views/ structure ✅ CREATED | View split 🔄 IN PROGRESS

---

## Current Structure

```
material_management/
  views.py              # 4,562 lines, 76 class-based views
  po_services.py        # 423 lines (PO business logic already extracted)
  forms.py              # 343 lines
  urls.py               # 194 lines
  models.py             # 625 lines (managed=False)
```

---

## Target Structure

```
material_management/
  views/
    __init__.py         # Re-export all views for backward compatibility
    dashboard.py        # ✅ CREATED - 1 view: MaterialManagementDashboardView
    masters.py          # 12 views: BusinessNature (4), BusinessType (4), ServiceCoverage (4)
    buyer.py            # 5 views: Buyer CRUD + EmployeeAutocomplete
    supplier.py         # 5 views: Supplier CRUD + ScopeOfSupplier
    rate.py             # 8 views: RateSet, RateRegister, RateLockUnlock
    pr.py               # 9 views: PR CRUD + PRNewSearch, PRNewDetails
    spr.py              # 9 views: SPR CRUD + SPRNew, SPRNewDetails
    po.py               # 13 views: PO CRUD + PONew, POPRItems, POSPRItems, POHeader
    approval.py         # 9 views: PR/SPR/PO Check, Approve, Authorize
    reports.py          # 5 views: RateRegister, RateLock, SupplierRating, MaterialForecasting, MaterialSearch
    api.py              # 3 views: ItemSearch, SupplierAutocomplete, SupplierRate
  services.py           # ✅ CREATED - 665 lines (PR/SPR/Rate/Approval business logic)
  po_services.py        # 423 lines (existing PO business logic)
  forms.py              # 343 lines (unchanged)
  urls.py               # 194 lines (unchanged - imports from views/__init__.py)
  models.py             # 625 lines (unchanged - managed=False)
```

---

## services.py - Business Logic Extraction

**Status:** ✅ CREATED (665 lines)

### Services Created:

1. **PRNumberService**
   - `generate_pr_number(comp_id, fin_year_id)` - Generate next PR number

2. **SPRNumberService**
   - `generate_spr_number(comp_id, fin_year_id)` - Generate next SPR number

3. **PRCreationService**
   - `create_pr_from_temp(comp_id, fin_year_id, session_id, wo_no, temp_items)` - Create PR from temp table
   - `create_pr_bulk(comp_id, fin_year_id, session_id, wo_no, items_data)` - Create PR from bulk data

4. **SPRCreationService**
   - `create_spr_from_temp(comp_id, fin_year_id, session_id, dept_id, wo_no, temp_items)` - Create SPR from session
   - `create_spr_bulk(comp_id, fin_year_id, session_id, dept_id, wo_no, items_data)` - Create SPR from bulk data

5. **ApprovalWorkflowService**
   - `check_pr(pr_id, user_id)` - Mark PR as checked
   - `approve_pr(pr_id, user_id)` - Mark PR as approved
   - `authorize_pr(pr_id, user_id)` - Mark PR as authorized
   - `check_spr(spr_id, user_id)` - Mark SPR as checked
   - `approve_spr(spr_id, user_id)` - Mark SPR as approved
   - `authorize_spr(spr_id, user_id)` - Mark SPR as authorized

6. **RateLockService**
   - `lock_item_rate(item_id, comp_id, lock_type, user_id)` - Lock item rate
   - `unlock_item_rate(item_id, comp_id, lock_type, user_id)` - Unlock item rate
   - `get_item_lock_status(item_id, comp_id)` - Get lock status

7. **SupplierService**
   - `extract_supplier_id(supplier_input, comp_id)` - Parse supplier ID from various formats

8. **RateRegisterService**
   - `get_min_rate_for_item(item_id, comp_id)` - Get historical minimum rate
   - `add_rate_to_register(item_id, supplier_id, comp_id, qty, rate, discount, po_no)` - Add rate entry

---

## View File Breakdown

### 1. dashboard.py (✅ CREATED)

**Views:** 1
**Lines:** ~40

- `MaterialManagementDashboardView` - Dashboard with metrics

### 2. masters.py (📋 TO CREATE)

**Views:** 12
**Lines:** ~380
**Original Location:** views.py lines 118-469

Views:
- `BusinessNatureListView` - List with HTMX inline editing
- `BusinessNatureCreateView` - HTMX inline create
- `BusinessNatureUpdateView` - HTMX inline edit
- `BusinessNatureDeleteView` - HTMX delete
- `BusinessTypeListView` - List with HTMX inline editing
- `BusinessTypeCreateView` - HTMX inline create
- `BusinessTypeUpdateView` - HTMX inline edit
- `BusinessTypeDeleteView` - HTMX delete
- `ServiceCoverageListView` - List with HTMX inline editing
- `ServiceCoverageCreateView` - HTMX inline create
- `ServiceCoverageUpdateView` - HTMX inline edit
- `ServiceCoverageDeleteView` - HTMX delete

**Imports Needed:**
```python
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib import messages
from core.mixins import HTMXResponseMixin
from .dashboard import MaterialManagementBaseMixin
from ..models import BusinessNature, BusinessType, ServiceCoverage
from ..forms import BusinessNatureForm, BusinessTypeForm, ServiceCoverageForm
```

### 3. buyer.py (📋 TO CREATE)

**Views:** 5
**Lines:** ~220
**Original Location:** views.py lines 476-599

Views:
- `BuyerListView` - List with category filter
- `BuyerCreateView` - Create buyer
- `BuyerUpdateView` - Update buyer
- `BuyerDeleteView` - Delete buyer
- `EmployeeAutocompleteView` - API endpoint for employee search

**Business Logic:** None (simple CRUD)

### 4. supplier.py (📋 TO CREATE)

**Views:** 5
**Lines:** ~280
**Original Location:** views.py lines 626-837

Views:
- `SupplierListView` - Supplier list with search
- `SupplierCreateView` - Create supplier (65 fields)
- `SupplierDetailView` - Supplier details
- `SupplierUpdateView` - Update supplier
- `SupplierDeleteView` - Delete supplier

**Business Logic:** Supplier ID generation (if needed)

### 5. rate.py (📋 TO CREATE)

**Views:** 8
**Lines:** ~680
**Original Location:** views.py lines 838-1184 + 4329-4476

Views:
- `RateSetSearchView` - Search items for rate setting
- `RateSetDetailsView` - Set minimum rates
- `RateRegisterListView` - View rate register (read-only)
- `RateRegisterDetailView` - Item rate history
- `RateLockUnlockListView` - Lock/unlock interface
- `RateLockUnlockActionView` - Perform lock/unlock
- `RateLockUnlockReportView` - Lock/unlock report
- `RateLockUnlockToggleView` - DEPRECATED (remove?)

**Business Logic:** Uses `RateLockService`, `RateRegisterService` from services.py

### 6. pr.py (📋 TO CREATE)

**Views:** 9
**Lines:** ~1,050
**Original Location:** views.py lines 1389-2424

Views:
- `PRListView` - List PRs with filters
- `PRNewSearchView` - Step 1: Search WO
- `PRNewDetailsView` - Step 2: Add items (uses services.PRCreationService)
- `PRDetailView` - View PR details
- `PRUpdateView` - Update PR
- `PRDeleteView` - Delete PR
- `PRCheckView` - Check workflow
- `PRApproveView` - Approve workflow
- `PRAuthorizeView` - Authorize workflow

**Business Logic:** Uses `PRNumberService`, `PRCreationService` from services.py

**Key Methods to Refactor:**
- `generate_pr()` → Use `PRCreationService.create_pr_from_temp()`
- `generate_pr_from_nested_grid()` → Use `PRCreationService.create_pr_bulk()`
- `generate_pr_bulk()` → Use `PRCreationService.create_pr_bulk()`

### 7. spr.py (📋 TO CREATE)

**Views:** 9
**Lines:** ~730
**Original Location:** views.py lines 2436-3173

Views:
- `SPRListView` - List SPRs
- `SPRNewView` - Step 1: Select department/category
- `SPRNewDetailsView` - Step 2: AI-suggested items (uses services.SPRCreationService)
- `SPRDetailView` - View SPR details
- `SPRUpdateView` - Update SPR
- `SPRDeleteView` - Delete SPR
- `SPRCheckView` - Check workflow
- `SPRApproveView` - Approve workflow
- `SPRAuthorizeView` - Authorize workflow

**Business Logic:** Uses `SPRNumberService`, `SPRCreationService` from services.py

**Key Methods to Refactor:**
- `generate_spr()` → Use `SPRCreationService.create_spr_from_temp()`
- `generate_spr_bulk()` → Use `SPRCreationService.create_spr_bulk()`

### 8. po.py (📋 TO CREATE)

**Views:** 13
**Lines:** ~820
**Original Location:** views.py lines 3195-3987

Views:
- `POListView` - List POs
- `PONewView` - Step 1: Supplier selection
- `POPRItemsView` - Step 2: PR items grid
- `POSPRItemsView` - Step 2: SPR items grid
- `POPRItemSelectView` - Step 3: PR item entry
- `POSPRItemSelectView` - Step 3: SPR item entry
- `POHeaderView` - Step 4: Final PO creation
- `PODetailView` - View PO
- `POUpdateView` - Update PO
- `PODeleteView` - Delete PO
- `POCheckActionView` - Check action
- `POApproveActionView` - Approve action
- `POAuthorizeActionView` - Authorize action

**Business Logic:** Uses `po_services.py` (already exists with PONumberService, POCreationService, etc.)

**Note:** Some PO views are disabled in urls.py (lines 100-137) and use function-based views from `po_views.py` instead

### 9. approval.py (📋 TO CREATE)

**Views:** 9
**Lines:** ~270
**Original Location:** views.py lines 3889-3963

Views:
- `POCheckView` - PO check list
- `POApproveView` - PO approve list
- `POAuthorizeView` - PO authorize list

**Note:** PR/SPR approval views are in pr.py and spr.py respectively

**Business Logic:** Uses `ApprovalWorkflowService` from services.py

### 10. reports.py (📋 TO CREATE)

**Views:** 5
**Lines:** ~250
**Original Location:** views.py lines 4000-4165

Views:
- `RateRegisterReportView` - Rate register report
- `RateLockUnlockReportView` - Rate lock report
- `SupplierRatingReportView` - Supplier rating
- `MaterialForecastingReportView` - Material forecasting
- `MaterialSearchView` - Material search

**Business Logic:** Mostly queries, minimal logic

### 11. api.py (📋 TO CREATE)

**Views:** 3
**Lines:** ~180
**Original Location:** views.py lines 4167-4328

Views:
- `ItemSearchAPIView` - Item search API
- `SupplierAutocompleteAPIView` - Supplier autocomplete
- `SupplierRateAPIView` - Get supplier rate

**Business Logic:** Uses `RateRegisterService` from services.py

### 12. views/__init__.py (📋 TO CREATE)

**Purpose:** Re-export all views for backward compatibility with urls.py

```python
"""
Material Management Views Module

All views re-exported from modular files for backward compatibility with urls.py
"""

# Dashboard
from .dashboard import MaterialManagementDashboardView, MaterialManagementBaseMixin

# Masters
from .masters import (
    BusinessNatureListView, BusinessNatureCreateView,
    BusinessNatureUpdateView, BusinessNatureDeleteView,
    BusinessTypeListView, BusinessTypeCreateView,
    BusinessTypeUpdateView, BusinessTypeDeleteView,
    ServiceCoverageListView, ServiceCoverageCreateView,
    ServiceCoverageUpdateView, ServiceCoverageDeleteView,
)

# Buyer
from .buyer import (
    BuyerListView, BuyerCreateView, BuyerUpdateView,
    BuyerDeleteView, EmployeeAutocompleteView,
)

# Supplier
from .supplier import (
    SupplierListView, SupplierCreateView, SupplierDetailView,
    SupplierUpdateView, SupplierDeleteView, ScopeOfSupplierView,
)

# Rate Management
from .rate import (
    RateSetSearchView, RateSetDetailsView, RateRegisterListView,
    RateRegisterDetailView, RateLockUnlockListView,
    RateLockUnlockActionView, RateLockUnlockReportView,
    RateLockUnlockToggleView,
)

# PR
from .pr import (
    PRListView, PRNewSearchView, PRNewDetailsView,
    PRDetailView, PRUpdateView, PRDeleteView,
    PRCheckView, PRApproveView, PRAuthorizeView,
)

# SPR
from .spr import (
    SPRListView, SPRNewView, SPRNewDetailsView,
    SPRDetailView, SPRUpdateView, SPRDeleteView,
    SPRCheckView, SPRApproveView, SPRAuthorizeView,
)

# PO
from .po import (
    POListView, PONewView, POPRItemsView, POSPRItemsView,
    POPRItemSelectView, POSPRItemSelectView, POHeaderView,
    PODetailView, POUpdateView, PODeleteView,
    POCheckActionView, POApproveActionView, POAuthorizeActionView,
)

# Approval
from .approval import (
    POCheckView, POApproveView, POAuthorizeView,
)

# Reports
from .reports import (
    RateRegisterReportView, RateLockUnlockReportView,
    SupplierRatingReportView, MaterialForecastingReportView,
    MaterialSearchView,
)

# API
from .api import (
    ItemSearchAPIView, SupplierAutocompleteAPIView,
    SupplierRateAPIView,
)

__all__ = [
    # Base
    'MaterialManagementBaseMixin',
    'MaterialManagementDashboardView',

    # Masters
    'BusinessNatureListView', 'BusinessNatureCreateView',
    'BusinessNatureUpdateView', 'BusinessNatureDeleteView',
    'BusinessTypeListView', 'BusinessTypeCreateView',
    'BusinessTypeUpdateView', 'BusinessTypeDeleteView',
    'ServiceCoverageListView', 'ServiceCoverageCreateView',
    'ServiceCoverageUpdateView', 'ServiceCoverageDeleteView',

    # Buyer
    'BuyerListView', 'BuyerCreateView', 'BuyerUpdateView',
    'BuyerDeleteView', 'EmployeeAutocompleteView',

    # Supplier
    'SupplierListView', 'SupplierCreateView', 'SupplierDetailView',
    'SupplierUpdateView', 'SupplierDeleteView', 'ScopeOfSupplierView',

    # Rate
    'RateSetSearchView', 'RateSetDetailsView', 'RateRegisterListView',
    'RateRegisterDetailView', 'RateLockUnlockListView',
    'RateLockUnlockActionView', 'RateLockUnlockReportView',
    'RateLockUnlockToggleView',

    # PR
    'PRListView', 'PRNewSearchView', 'PRNewDetailsView',
    'PRDetailView', 'PRUpdateView', 'PRDeleteView',
    'PRCheckView', 'PRApproveView', 'PRAuthorizeView',

    # SPR
    'SPRListView', 'SPRNewView', 'SPRNewDetailsView',
    'SPRDetailView', 'SPRUpdateView', 'SPRDeleteView',
    'SPRCheckView', 'SPRApproveView', 'SPRAuthorizeView',

    # PO
    'POListView', 'PONewView', 'POPRItemsView', 'POSPRItemsView',
    'POPRItemSelectView', 'POSPRItemSelectView', 'POHeaderView',
    'PODetailView', 'POUpdateView', 'PODeleteView',
    'POCheckActionView', 'POApproveActionView', 'POAuthorizeActionView',

    # Approval
    'POCheckView', 'POApproveView', 'POAuthorizeView',

    # Reports
    'RateRegisterReportView', 'RateLockUnlockReportView',
    'SupplierRatingReportView', 'MaterialForecastingReportView',
    'MaterialSearchView',

    # API
    'ItemSearchAPIView', 'SupplierAutocompleteAPIView',
    'SupplierRateAPIView',
]
```

---

## urls.py Compatibility

**IMPORTANT:** urls.py will continue to work WITHOUT modification because:

1. Current import: `from . import views`
2. Views accessed as: `views.BusinessNatureListView.as_view()`
3. With `views/__init__.py` re-exporting all views, this still works!

**Example from urls.py:**
```python
from . import views  # Now points to views/__init__.py

urlpatterns = [
    path('business-nature/', views.BusinessNatureListView.as_view(), name='business-nature-list'),
    # This still works because BusinessNatureListView is re-exported in views/__init__.py
]
```

**No url.py changes needed!** ✅

---

## Migration Strategy

### Phase 1: Preparation ✅
- [x] Create `services.py` with business logic
- [x] Create `views/` directory
- [x] Create `views/dashboard.py`

### Phase 2: View Modularization (📋 IN PROGRESS)
- [ ] Create `views/masters.py` - 12 views
- [ ] Create `views/buyer.py` - 5 views
- [ ] Create `views/supplier.py` - 5 views
- [ ] Create `views/rate.py` - 8 views
- [ ] Create `views/pr.py` - 9 views (refactor to use services.py)
- [ ] Create `views/spr.py` - 9 views (refactor to use services.py)
- [ ] Create `views/po.py` - 13 views
- [ ] Create `views/approval.py` - 9 views
- [ ] Create `views/reports.py` - 5 views
- [ ] Create `views/api.py` - 3 views
- [ ] Create `views/__init__.py` - Re-export all views

### Phase 3: Testing
- [ ] Verify urls.py resolves all views
- [ ] Test each view endpoint
- [ ] Verify HTMX responses
- [ ] Test PR/SPR creation flows
- [ ] Test approval workflows
- [ ] Test rate locking

### Phase 4: Cleanup
- [ ] Backup original `views.py` to `views.py.backup`
- [ ] Delete original `views.py`
- [ ] Update documentation

---

## Benefits

1. **Maintainability:** 380 lines/file vs 4,562 lines/file
2. **Separation of Concerns:** Business logic in services, views handle HTTP
3. **Reusability:** Services can be used by multiple views
4. **Testability:** Service methods easier to unit test
5. **Readability:** Clear file naming shows module responsibility
6. **Performance:** No change (same code, different organization)

---

## Risks & Mitigation

### Risk 1: Import Breakage
**Mitigation:** `views/__init__.py` re-exports all views for backward compatibility

### Risk 2: Circular Imports
**Mitigation:** Relative imports (`from ..models import`) prevent circular dependencies

### Risk 3: Missing Dependencies
**Mitigation:** Each view file explicitly imports what it needs

### Risk 4: Testing Overhead
**Mitigation:** Systematic endpoint testing after migration

---

## Next Steps

1. **Create remaining view files** using the pattern from `dashboard.py`
2. **Create `views/__init__.py`** to re-export all views
3. **Test urls.py** to ensure all views resolve
4. **Update views to use services.py** where applicable
5. **Backup and remove original views.py**

---

## File Size Summary

| File | Views | Lines | Status |
|------|-------|-------|--------|
| dashboard.py | 1 | 40 | ✅ Created |
| masters.py | 12 | 380 | 📋 Pending |
| buyer.py | 5 | 220 | 📋 Pending |
| supplier.py | 5 | 280 | 📋 Pending |
| rate.py | 8 | 680 | 📋 Pending |
| pr.py | 9 | 1,050 | 📋 Pending |
| spr.py | 9 | 730 | 📋 Pending |
| po.py | 13 | 820 | 📋 Pending |
| approval.py | 3 | 90 | 📋 Pending |
| reports.py | 5 | 250 | 📋 Pending |
| api.py | 3 | 180 | 📋 Pending |
| __init__.py | - | 150 | 📋 Pending |
| **TOTAL** | **76** | **4,870** | **1/12** |

---

## Services Summary

| Service | Methods | Lines | Status |
|---------|---------|-------|--------|
| PRNumberService | 1 | 20 | ✅ Created |
| SPRNumberService | 1 | 15 | ✅ Created |
| PRCreationService | 2 | 150 | ✅ Created |
| SPRCreationService | 2 | 150 | ✅ Created |
| ApprovalWorkflowService | 6 | 90 | ✅ Created |
| RateLockService | 3 | 80 | ✅ Created |
| SupplierService | 1 | 30 | ✅ Created |
| RateRegisterService | 2 | 50 | ✅ Created |
| **TOTAL** | **18** | **665** | **✅ COMPLETE** |

---

**Last Updated:** 2025-11-12
**Status:** services.py ✅ | dashboard.py ✅ | Remaining views 📋
