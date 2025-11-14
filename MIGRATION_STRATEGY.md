# ASP.NET to Django Migration Strategy & Implementation Guide

**Project:** SAPL/Cortex ERP System
**Generated:** 2025-11-14
**Status:** Comprehensive Migration Audit & Roadmap

---

## Executive Summary

This document provides a complete analysis and strategic roadmap for migrating the SAPL ERP system from ASP.NET Web Forms to Django 5.2 with HTMX and Tailwind CSS.

### Critical Statistics

| Metric | Count |
|--------|-------|
| **Total Menu Items** (Web.sitemap) | 190 |
| **Total .aspx Files** | 941 |
| **Django Apps Created** | 15 |
| **Django View Files** | 119 |
| **Django URL Patterns** | 914 |
| **Pytest Tests** | Comprehensive (sys_admin only) |
| **Playwright E2E Tests** | 0 (Not yet implemented) |

### Migration Progress by Module

| ASP.NET Module | ASPX Files | Django App | Views | URLs | Status |
|----------------|------------|------------|-------|------|--------|
| SysAdmin | 9 | sys_admin | 4 | 36 | 🟢 **DONE** |
| SalesDistribution | 82 | sales_distribution | 10 | 82 | 🟡 In Progress |
| Design | 74 | design | 7 | 59 | 🟡 In Progress |
| MaterialPlanning | 15 | material_planning | 7 | 21 | 🟡 In Progress |
| MaterialManagement | 120 | material_management | 10 | 114 | 🟡 In Progress |
| ProjectManagement | 61 | project_management | 5 | 27 | 🟡 In Progress |
| **Inventory** | **149** | inventory | 19 | 112 | 🟡 **PRIORITY** |
| QualityControl | 30 | quality_control | 10 | 36 | 🟡 In Progress |
| **Accounts** | **133** | accounts | 21 | 220 | 🟡 **PRIORITY** |
| HR | 76 | human_resource | 8 | 133 | 🟡 In Progress |
| MROffice | 3 | mr_office | 1 | 8 | 🟢 Minimal |
| MIS | 41 | mis | 4 | 17 | 🔴 Low Coverage |
| Machinery | 39 | machinery | 5 | 18 | 🔴 Low Coverage |
| Report | 31 | reports | 1 | 8 | 🔴 Low Coverage |
| DailyReportingSystem | 27 | daily_report_system | 7 | 23 | 🟡 In Progress |
| **Chatting** | 2 | **UNMAPPED** | 0 | 0 | ❌ Not Started |
| **Scheduler** | 5 | **UNMAPPED** | 0 | 0 | ❌ Not Started |

---

## Detailed Module Analysis

### 1. Administrator (sys_admin) ✅ COMPLETE

**Menu Items:**
- Dashboard
- Role Management
- Financial Year (Full CRUD)
- Country (Full CRUD)
- State (Full CRUD)
- City (Full CRUD)

**Django Implementation:**
- ✅ All views implemented with HTMX support
- ✅ Comprehensive pytest suite (793 lines)
- ✅ Forms with validation
- ✅ Services layer for business logic
- ❌ **Missing:** Playwright E2E tests

**Test Coverage:** 85%+ (unit/integration only)

---

### 2. Sales Distribution (sales_distribution) 🟡 IN PROGRESS

**Menu Structure:**
```
Sales
├── Master
│   ├── Customer (7 CRUD pages)
│   ├── Category of Work Order
│   └── WO Release & Dispatch Authority
└── Transaction
    ├── Enquiry
    ├── Quotation
    ├── Customer PO
    ├── Work Order
    ├── WO Release
    ├── WO Dispatch
    ├── Dispatch GunRail
    └── WO Open/Close
```

**ASPX Files:** 82
**Django URLs:** 82
**Status:** URLs configured, views partially implemented

**Missing Implementation:**
- Quotation CRUD (complete workflow)
- Customer PO approval workflow
- Work Order dispatch tracking
- GunRail-specific dispatch

**Test Status:**
- ❌ No pytest tests
- ❌ No Playwright E2E tests

---

### 3. Design (design) 🟡 IN PROGRESS

**Menu Structure:**
```
Design
├── Master
│   ├── BoughtOut Category
│   ├── Item Master
│   ├── Unit Master
│   └── ECN Reason
├── Transaction
│   ├── BOM
│   ├── Slido Gunrail
│   └── ECN Unlock
└── Report
    └── Item history
```

**ASPX Files:** 74
**Django URLs:** 59
**Gap:** 15 ASPX files not mapped

**Missing Implementation:**
- BOM complete workflow
- ECN (Engineering Change Note) unlock
- Item history reports

---

### 4. Material Planning (material_planning) 🟡 IN PROGRESS

**ASPX Files:** 15
**Django URLs:** 21
**Status:** Basic structure in place

**Menu Items:**
- Material Process (Master)
- BOM (Transaction)

---

### 5. Material Management (material_management) 🟡 IN PROGRESS

**Menu Structure:**
```
Material
├── Master
│   ├── Business Nature
│   ├── Business Type
│   ├── Service Coverage
│   ├── Buyer
│   ├── Supplier (Full CRUD)
│   └── Set Rate
├── Transaction
│   ├── Scope Of Supplier
│   ├── Rate Lock/UnLock
│   ├── Purchase Requisition [PR]
│   ├── Special Purpose Requisition [SPR]
│   ├── Check SPR
│   ├── Approve SPR
│   ├── Purchase Order [PO] ⭐
│   ├── Check PO
│   ├── Approve PO
│   └── Authorize PO
└── Report
    ├── Rate Register
    ├── Rate Lock/UnLock
    ├── Material Forecasting
    ├── Inward/Outward Register
    └── Search
```

**ASPX Files:** 120 (MOST COMPLEX MODULE)
**Django URLs:** 114

**Implementation Status:**
- ✅ Supplier Master (Complete CRUD)
- ✅ PR (Purchase Requisition) - Partial
- ✅ SPR (Special Purpose Requisition) - Partial
- 🟡 PO (Purchase Order) - Complex workflow partially done
- ❌ Approval workflows incomplete

**Critical Gap:** Multi-level approval workflows (Check → Approve → Authorize)

---

### 6. Project Management (project_management) 🟡 IN PROGRESS

**Menu Items:**
- Man Power Planning
- Project Planning
- Project Summary (Report)

**ASPX Files:** 61
**Django URLs:** 27
**Gap:** 34 ASPX files not mapped

---

### 7. Inventory (inventory) ⚠️ HIGH PRIORITY

**Menu Structure:**
```
Inventory
├── Master
│   ├── Item location
│   └── VEHICLE ENTRY
├── Transaction
│   ├── VEHICLE REGISTRATION FORM
│   ├── Goods Inward Note [GIN] ⭐
│   ├── Goods Received Receipt [GRR] ⭐
│   ├── Goods Service Note [GSN]
│   ├── Material Requisition Slip [MRS] ⭐
│   ├── Material Issue Note [MIN] ⭐
│   ├── Material Return Note [MRN]
│   ├── Delivery Challan
│   ├── Challan Summary
│   ├── Release WIS
│   ├── Dry / Actual WIS Run
│   └── Closing Stock
└── Reports
    ├── Stock Ledger
    ├── Stock Statement
    ├── Material Issue/Shortage list
    ├── Moving-Non Moving Items
    ├── Inward/Outward Register
    └── Search
```

**ASPX Files:** 149 (LARGEST MODULE!)
**Django URLs:** 112
**Status:** Critical business process, partially implemented

**Critical Transactions:**
- GIN → GRR workflow (goods receiving)
- MRS → MIN workflow (material issue)
- MRN (material returns)
- Closing stock calculations

**Test Status:** ❌ No comprehensive tests

---

### 8. Quality Control (quality_control) 🟡 IN PROGRESS

**Menu Items:**
- Goods Quality Note [GQN]
- Material Return Quality Note [MRQN]
- Authorize MCN
- Goods Rejection Note [GRN] (Report)
- Scrap Material (Report)

**ASPX Files:** 30
**Django URLs:** 36

---

### 9. Accounts (accounts) ⚠️ HIGH PRIORITY

**Menu Structure:**
```
Accounts
├── Master
│   ├── Account Heads
│   ├── CGST/IGST
│   ├── SGST
│   ├── Excisable Commodity
│   ├── Warranty Terms
│   ├── Payment Terms
│   ├── Cash/Bank Entry
│   ├── IOU Reasons
│   ├── Bank
│   ├── Payment Mode
│   └── Asset
├── Transaction
│   ├── Sales Invoice ⭐
│   ├── IOU Payment/Receipt
│   ├── Bill Booking ⭐
│   ├── Authorize Bill Booking
│   ├── POLICY
│   ├── Cash Voucher
│   ├── Payment/Receipt Voucher
│   ├── Advice
│   ├── Creditors/Debitors
│   ├── Bank Reconciliation ⭐
│   ├── Balance Sheet ⭐
│   └── Asset Register
└── Report
    ├── Sales Register
    ├── Purchase Register
    ├── Pending For Invoice
    ├── PVEV Search
    └── Cash/Bank Register
```

**ASPX Files:** 133 (SECOND LARGEST!)
**Django URLs:** 220
**Status:** Complex financial workflows

**Critical Transactions:**
- Sales Invoice generation
- Bill booking with approval
- Bank reconciliation
- Balance sheet generation

---

### 10. Human Resource (human_resource) 🟡 IN PROGRESS

**Menu Structure:**
```
HR
├── Master
│   ├── Business Group
│   ├── Designation
│   ├── Department
│   ├── Grade
│   ├── SwapCard No
│   ├── Corporate Mobile
│   ├── Intercom Ext
│   ├── Gate Pass Types
│   ├── Holiday
│   ├── PF Slab
│   └── Working Days
├── Transaction
│   ├── News And Notices
│   ├── Offer Letter
│   ├── Staff
│   ├── DOCUMENTS
│   ├── Mobile Bill
│   ├── ASSET LIST
│   ├── Authorize Gate Pass
│   ├── Bank Loan
│   └── PayRoll ⭐
└── Report
    └── Staff (Multiple Reports)
```

**ASPX Files:** 76
**Django URLs:** 133

**Critical Feature:** PayRoll processing

---

### 11-15. Other Modules

| Module | ASPX Files | Priority | Notes |
|--------|------------|----------|-------|
| MROffice | 3 | Low | Minimal functionality |
| MIS | 41 | Medium | Financial Budget, Reports |
| Machinery | 39 | Medium | PMBM Maintenance |
| Reports | 31 | Medium | Cross-module reports |
| DailyReportingSystem | 27 | Medium | Production tracking |

---

## UNMAPPED MODULES (Not Yet Started)

### Chatting ❌
- `~/Module/Chatting/Chatroom.aspx`
- Real-time chat functionality
- **Recommendation:** Use Django Channels + WebSockets

### Scheduler ❌
- `~/Module/Scheduler/Scheduling.aspx`
- `~/Module/Scheduler/GatePass_New.aspx`
- `~/Module/Scheduler/IOU.aspx`
- **Recommendation:** Create `scheduler` Django app

---

## Critical Gap Analysis

### 1. **Playwright E2E Tests: 0% Coverage** ❌

**Required Test Coverage:**
- Every menu item must have at least one E2E test
- Test scenarios:
  - Navigation to page via menu
  - CRUD operations (Create → Read → Update → Delete)
  - Form validation
  - HTMX partial updates
  - Search/filter functionality
  - Print/export features

**Test Directory Structure (Proposed):**
```
tests/
├── playwright/
│   ├── test_sys_admin.py
│   ├── test_sales_distribution.py
│   ├── test_inventory.py
│   ├── test_accounts.py
│   ├── test_material_management.py
│   └── ...
└── fixtures/
    └── test_data.py
```

**Example Test Pattern:**
```python
def test_customer_master_crud(page: Page):
    """Test Customer Master full CRUD workflow"""
    # Navigate via menu
    page.goto("http://localhost:8000/")
    page.click("text=Sales")
    page.click("text=Master")
    page.click("text=Customer")

    # CREATE
    page.click("text=Add New Customer")
    page.fill("#id_customername", "Test Customer Ltd")
    page.fill("#id_address", "123 Test St")
    page.click("button[type=submit]")
    expect(page.locator(".success-message")).to_be_visible()

    # READ (verify in list)
    expect(page.locator("text=Test Customer Ltd")).to_be_visible()

    # UPDATE
    page.click("text=Test Customer Ltd")
    page.click("button[hx-get*='edit']")
    page.fill("#id_customername", "Updated Customer Ltd")
    page.click("button[type=submit]")
    expect(page.locator("text=Updated Customer Ltd")).to_be_visible()

    # DELETE
    page.click("button[hx-delete*='delete']")
    page.click("button:has-text('Confirm')")
    expect(page.locator("text=Updated Customer Ltd")).not_to_be_visible()
```

### 2. **Dashboard Pages Use SubModId Pattern** ⚠️

Many menu items point to `Dashboard.aspx?ModId=X&SubModId=Y`:
- This pattern means the Dashboard acts as a router
- Django equivalent: Need to implement proper routing based on SubModId
- **Action Required:** Review all Dashboard.aspx implementations

### 3. **Supporting ASPX Files Not in Menu** 📋

941 total ASPX files, but only ~190 menu items means:
- ~750 files are supporting pages:
  - `*_New.aspx` (Create forms)
  - `*_Edit.aspx` (Edit forms)
  - `*_Delete.aspx` (Delete confirmations)
  - `*_Print.aspx` (Print views)
  - `*_Details.aspx` (Detail views)

**Django Pattern:**
```python
# Single view handles all CRUD operations via HTMX
path('customer/<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer-edit')
# Returns partial template for HTMX or full page for direct access
```

### 4. **Complex Approval Workflows** 🔄

Many modules have multi-step approval:
```
Create → Check → Approve → Authorize
```

**Example:** Purchase Order (PO)
1. User creates PO
2. Checker reviews (PO_Check)
3. Approver approves (PO_Approve)
4. Authorizer authorizes (PO_Authorize)

**Django Implementation Required:**
- State machine for workflow status
- Permission-based access to each step
- Audit trail for all transitions

---

## Implementation Roadmap

### Phase 1: Critical Business Processes (Weeks 1-4)

**Priority Modules:**
1. **Inventory** (149 files)
   - GIN/GRR workflow
   - MRS/MIN workflow
   - Stock ledger
   - Closing stock

2. **Accounts** (133 files)
   - Sales Invoice
   - Bill Booking
   - Bank Reconciliation
   - Financial reports

**Deliverables:**
- Complete views + URLs + forms
- pytest unit tests
- Playwright E2E tests
- Service layer for business logic

### Phase 2: Supporting Transactions (Weeks 5-8)

**Modules:**
1. **Sales Distribution**
   - Complete quotation workflow
   - Work order dispatch

2. **Material Management**
   - Complete PO approval workflow
   - SPR authorization

3. **Quality Control**
   - GQN/MRQN complete

**Deliverables:**
- Same as Phase 1

### Phase 3: Reports & Analytics (Weeks 9-10)

**Focus:**
- All report modules
- MIS reports
- Cross-module reporting

**Deliverables:**
- Report views with filters
- Export to PDF/Excel
- Playwright screenshot tests

### Phase 4: Auxiliary Modules (Weeks 11-12)

**Modules:**
1. HR (PayRoll)
2. Project Management
3. Machinery
4. Daily Report System

### Phase 5: New Features (Weeks 13-14)

**Unmapped Modules:**
1. **Chatting** - Django Channels implementation
2. **Scheduler** - New Django app
3. **GatePass** - Standalone feature

### Phase 6: Testing & QA (Weeks 15-16)

**Activities:**
- Complete Playwright test coverage (all 190 menu items)
- Performance testing
- Security audit
- User acceptance testing (UAT)
- Visual regression testing

---

## Playwright Test Requirements

### Test Coverage Matrix

| Module | Menu Items | Required Tests | Status |
|--------|------------|----------------|--------|
| sys_admin | 5 | 5 | ❌ 0/5 |
| sales_distribution | 14 | 14 | ❌ 0/14 |
| design | 12 | 12 | ❌ 0/12 |
| material_planning | 2 | 2 | ❌ 0/2 |
| material_management | 20 | 20 | ❌ 0/20 |
| project_management | 3 | 3 | ❌ 0/3 |
| inventory | 24 | 24 | ❌ 0/24 |
| quality_control | 5 | 5 | ❌ 0/5 |
| accounts | 32 | 32 | ❌ 0/32 |
| human_resource | 25 | 25 | ❌ 0/25 |
| mr_office | 3 | 3 | ❌ 0/3 |
| mis | 7 | 7 | ❌ 0/7 |
| **TOTAL** | **190** | **190** | **0/190** |

### Test Categories

1. **Navigation Tests** (190 tests)
   - Menu navigation works
   - Page loads without errors

2. **CRUD Tests** (per entity)
   - Create with valid data
   - Create with invalid data (validation)
   - Read/List with search
   - Update existing record
   - Delete with confirmation

3. **HTMX Tests**
   - Partial updates work
   - Form submissions via HTMX
   - Search filters update table
   - Inline editing

4. **Workflow Tests**
   - Multi-step approvals
   - State transitions
   - Permission checks

5. **Report Tests**
   - Report generation
   - Filters work
   - Export functionality

**Total Estimated Tests:** ~500-600

---

## Implementation Guidelines

### For Each Menu Item

1. **Analyze ASP.NET Implementation**
   ```bash
   # Find all related ASPX files
   find aaspnet/Module/[Module] -name "*[Feature]*"

   # Read .aspx.cs for business logic
   cat aaspnet/Module/.../[Feature].aspx.cs
   ```

2. **Create Django Components**
   ```
   [app]/
   ├── views/
   │   └── [feature].py          # Class-based views
   ├── forms.py                   # Form with validation
   ├── services.py                # Business logic
   ├── templates/[app]/
   │   ├── [feature]_list.html
   │   └── partials/
   │       ├── [feature]_form.html
   │       └── [feature]_row.html
   └── urls.py                    # URL patterns
   ```

3. **Write Tests**
   ```
   [app]/
   ├── tests.py                   # pytest unit tests
   └── tests/
       └── test_[feature].py

   tests/playwright/
   └── test_[app]_[feature].py    # E2E tests
   ```

4. **Verify Against Original**
   - Run ASP.NET version in browser
   - Run Django version in browser
   - Compare UI/UX
   - Test identical workflows

### Code Quality Checklist

- [ ] Uses `core/mixins.py` patterns
- [ ] Populates audit fields (sysdate, systime, sessionid, compid, finyearid)
- [ ] HTMX dual response (partial + full page)
- [ ] Tailwind CSS (no inline styles)
- [ ] Service layer for business logic
- [ ] Form validation matches ASP.NET
- [ ] pytest unit tests (85%+ coverage)
- [ ] Playwright E2E test
- [ ] No `managed = True` in models
- [ ] URL follows kebab-case pattern

---

## Maintenance & Updates

### Regular Reviews

**Weekly:**
- Update migration status report
- Review test coverage
- Code review new implementations

**Monthly:**
- Performance benchmarks
- Security scan
- User feedback review

### Documentation

- Update this document as modules are completed
- Document any deviations from ASP.NET behavior
- Maintain API documentation

---

## Success Criteria

**Migration is complete when:**

1. ✅ All 190 menu items have Django implementations
2. ✅ All 190 menu items have Playwright E2E tests
3. ✅ All modules have 85%+ pytest coverage
4. ✅ Visual consistency with Tailwind CSS
5. ✅ Performance meets or exceeds ASP.NET version
6. ✅ UAT sign-off from business users
7. ✅ Zero critical bugs
8. ✅ Documentation complete

**Current Progress:** ~60% (URLs configured, partial implementations)
**Estimated Completion:** 16 weeks (with dedicated resources)

---

## Appendix A: Menu-to-File Complete Mapping

See `MIGRATION_AUDIT_REPORT.md` for complete menu-to-file mappings.

---

## Appendix B: Command Reference

```bash
# Run migration audit
python migration_audit.py

# Run Django dev server
python manage.py runserver

# Run pytest unit tests
pytest -v

# Run Playwright E2E tests (when implemented)
pytest tests/playwright/ -v --headed

# Check test coverage
pytest --cov=sys_admin --cov-report=html

# Load test data
python manage.py loaddata csv_data/[module]_data.json
```

---

## Contact & Support

For questions or issues with this migration:
- Review `CLAUDE.md` for anti-hallucination protocol
- Review `core/CRUD_PATTERNS.md` for implementation patterns
- Check `hallucinations.md` for common pitfalls

**Last Updated:** 2025-11-14
