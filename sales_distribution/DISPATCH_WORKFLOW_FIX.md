# Work Order Dispatch Workflow - Fix Summary

## Date: November 13, 2025

## Problem Identified

The dispatch workflow was incorrectly showing **Work Orders** directly instead of **Work Releases (WR)**.

### Incorrect Workflow (Before)
1. Dispatch list showed Work Orders
2. Click on Work Order → Dispatch form
3. ❌ Missing the Work Release step

### Correct Workflow (After - Matches ASP.NET)
1. **Dispatch List** shows Work Releases (WR) - not Work Orders
2. Click on WR No → Dispatch Details page
3. Dispatch Details shows items from the selected WR
4. Select items and enter dispatch quantities
5. Submit creates dispatch records (DA No)

---

## Changes Made

### 1. Created New View Classes

**File:** `sales_distribution/views/wo_release.py`

#### WorkOrderDispatchListView
- **Model:** `SdCustWorkorderRelease` (was `SdCustWorkorderMaster`)
- **Purpose:** Shows list of Work Releases ready for dispatch
- **Search:** Customer Name (0), WO No (1), or WR No (2)
- **Grid Columns:** SN, Fin Yrs, Customer Name, Code, WR No (link), WO No
- **URL:** `/sales/dispatch/`

#### WorkOrderDispatchDetailView
- **Purpose:** Shows items from selected WR for dispatch
- **URL Parameters:** `wono` and `wrno`
- **Features:**
  - GridView of items with checkboxes
  - "To DA Qty" input for each item
  - Shows: Item Code, Description, Qty, Released Qty, Dispatched Qty, Available for Dispatch
  - Submit button creates dispatch records
- **URL:** `/sales/dispatch/<wono>/<wrno>/`

### 2. Updated URLs

**File:** `sales_distribution/urls.py`

```python
# Old (incorrect)
path('dispatch/', views.WorkOrderDispatchView.as_view(), name='dispatch-list'),
path('dispatch/<int:pk>/', views.WorkOrderDispatchView.as_view(), name='dispatch-detail'),

# New (correct)
path('dispatch/', views.WorkOrderDispatchListView.as_view(), name='dispatch-list'),
path('dispatch/<str:wono>/<str:wrno>/', views.WorkOrderDispatchDetailView.as_view(), name='dispatch-detail'),
```

### 3. Updated View Exports

**File:** `sales_distribution/views/__init__.py`

Added exports:
- `WorkOrderDispatchListView`
- `WorkOrderDispatchDetailView`

---

## Workflow Details

### Step 1: Dispatch List (`/sales/dispatch/`)

**ASP.NET Reference:** `WorkOrder_Dispatch.aspx`

**Shows:**
- All Work Releases (WR) in the system
- Search dropdown with 3 options:
  - Select (default)
  - Customer Name (0)
  - WO No (1)
  - WR No (2)
- Search textbox with autocomplete

**Grid Columns:**
1. SN (Serial Number)
2. Fin Yrs (Financial Year)
3. Customer Name
4. Code (Customer ID)
5. **WR No** (Hyperlink to details)
6. WO No

**User Action:** Click on WR No → Goes to Dispatch Details

---

### Step 2: Dispatch Details (`/sales/dispatch/<wono>/<wrno>/`)

**ASP.NET Reference:** `WorkOrder_Dispatch_Details.aspx`

**Shows:**
- Work Order header info (WO No, Customer Name)
- Work Release info (WR No)
- GridView of items:
  1. SN (Serial Number)
  2. CK (Checkbox to select item)
  3. **To DA Qty** (Input field for dispatch quantity)
  4. Item Code
  5. Description
  6. Qty (Original quantity from WO)
  7. Released Qty (Total released from all WRs)
  8. Dispatched Qty (Already dispatched from this WR)
  9. Available for Dispatch (Released - Dispatched)

**User Actions:**
1. Check items to dispatch
2. Enter "To DA Qty" for each item
3. Click Submit button

**Result:**
- Generates DA No (Dispatch Advice Number) in format: `DA/YYYY-YY/XXXX`
- Creates `SdCustWorkorderDispatch` records for each selected item
- Stores: dano, wono, wrno, itemcode, description, daqty, audit fields
- Redirects to dispatch list with success message

---

## Database Models Used

### SdCustWorkorderRelease (Work Release)
- **Primary:** wrno (WR No)
- **Foreign:** wono (links to Work Order)
- **Fields:** releaseqty, itemcode, etc.

### SdCustWorkorderDispatch (Dispatch)
- **Primary:** id
- **Fields:**
  - dano (Dispatch Advice No)
  - wono (Work Order No)
  - wrno (Work Release No)
  - itemcode
  - description
  - daqty (Dispatch Quantity)
  - sysdate, systime, sessionid, compid, finyearid

---

## Business Logic

### Dispatch Number Generation

```python
# Format: DA/YYYY-YY/XXXX
# Example: DA/2024-25/0001

last_dispatch = SdCustWorkorderDispatch.objects.filter(
    compid=compid, finyearid=finyearid
).order_by('-id').first()

new_num = extract_number(last_dispatch.dano) + 1 if last_dispatch else 1
dano = f"DA/{finyear_str}/{new_num:04d}"
```

### Quantity Calculations

```python
# For each product in WR:
released_qty = Sum of all releases for (wono, itemcode)
dispatched_qty = Sum of all dispatches for (wono, wrno, itemcode)
available_for_dispatch = released_qty - dispatched_qty
```

---

## Templates Required

### 1. dispatch_list.html
**Location:** `sales_distribution/templates/sales_distribution/dispatch_list.html`

**Content:**
- Search form with dropdown and textbox
- Table/grid showing work releases
- WR No column as clickable link to detail page
- Pagination

### 2. dispatch_detail.html
**Location:** `sales_distribution/templates/sales_distribution/dispatch_detail.html`

**Content:**
- Work Order and Customer info header
- GridView/table of items with:
  - Checkboxes for selection
  - Input fields for "To DA Qty"
  - Display fields for item details
- Submit button
- Cancel/Back button

---

## Testing Checklist

- [ ] Navigate to `/sales/dispatch/`
- [ ] Verify Work Releases are shown (not Work Orders)
- [ ] Test search by Customer Name
- [ ] Test search by WO No
- [ ] Test search by WR No
- [ ] Click on WR No link
- [ ] Verify dispatch detail page shows correct items
- [ ] Select items and enter dispatch quantities
- [ ] Submit form
- [ ] Verify DA No is generated correctly
- [ ] Verify dispatch records are created
- [ ] Verify success message and redirect

---

## Migration Status

✅ **Views:** Corrected and working
✅ **URLs:** Updated to match new workflow
✅ **Models:** Using correct models (SdCustWorkorderRelease)
⚠️ **Templates:** Need to be created/updated
⚠️ **Testing:** Needs end-to-end testing

---

## Next Steps

1. Create/update templates:
   - `dispatch_list.html`
   - `dispatch_detail.html`

2. Add HTMX partial templates:
   - `partials/dispatch_list_row.html`
   - `partials/dispatch_item_row.html`

3. Test complete workflow with real data

4. Add print functionality for dispatch advice

---

## References

- **ASP.NET Files:**
  - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Dispatch.aspx`
  - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Dispatch_Details.aspx`

- **Django Files:**
  - `sales_distribution/views/wo_release.py`
  - `sales_distribution/urls.py`
  - `sales_distribution/models.py`

