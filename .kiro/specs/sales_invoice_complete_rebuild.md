---
title: Sales Invoice Module - Complete Rebuild
status: draft
priority: high
created: 2025-11-17
---

# Sales Invoice Module - Complete End-to-End Rebuild

## Objective
Completely rebuild the Sales Invoice module by analyzing all legacy ASP.NET files, understanding the complete workflow, and creating a fully functional Django implementation with all tabs working correctly.

## Phase 1: Analysis & Discovery

### 1.1 Analyze Legacy ASP.NET Files
Inspect and document the complete logic from these files:
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Dashboard.aspx]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Dashboard.aspx.cs]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_New.aspx]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_New.aspx.cs]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_New_Details.aspx]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_New_Details.aspx.cs]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Edit.aspx]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Edit.aspx.cs]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Edit_Details.aspx]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Edit_Details.aspx.cs]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Delete.aspx]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Delete.aspx.cs]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Print.aspx]]
- #[[file:aaspnet/Module/Accounts/Transactions/SalesInvoice_Print.aspx.cs]]

### 1.2 Document Complete Workflow
Map out the entire user journey:
1. **Dashboard/List** → View all invoices with search/filter
2. **PO Selection** → Select PO, Work Order(s), and Invoice Type
3. **Invoice Creation** → 4-tab form (Buyer, Consignee, Goods, Taxation)
4. **Save** → Validate and persist to database
5. **Edit** → Modify existing invoice
6. **Delete** → Remove invoice and restore PO quantities
7. **Print** → Generate PDF invoice

### 1.3 Database Schema Analysis
Review and document:
- #[[file:accounts/models.py]] - Existing models
- Table: `tblAcc_SalesInvoice_Master`
- Table: `tblAcc_SalesInvoice_Details`
- Table: `tblAcc_SalesInvoice_Master_Type`
- Related tables: `SD_Cust_PO_Master`, `SD_Cust_PO_Details`, `SD_Cust_WorkOrder_Master`

### 1.4 Business Rules Documentation
Extract all business rules:
- Invoice number generation (sequential, 4-digit zero-padded)
- Remaining quantity calculation (Total PO Qty - Sum of Invoiced Qty)
- Amount percentage validation (cannot exceed 100%)
- Tax calculations (CGST/IGST/SGST based on invoice type)
- Required field validations
- Cascading dropdown logic (Country → State → City)

## Phase 2: Design

### 2.1 URL Structure
```
/accounts/transactions/sales-invoice/                    # List view
/accounts/transactions/sales-invoice/select-po/          # PO selection
/accounts/transactions/sales-invoice/create/             # Create form
/accounts/transactions/sales-invoice/<id>/edit/          # Edit form
/accounts/transactions/sales-invoice/<id>/delete/        # Delete confirmation
/accounts/transactions/sales-invoice/<id>/print/         # Print view
```

### 2.2 View Architecture
```
SalesInvoiceListView          # List with search/filter/pagination
SalesInvoicePOSelectionView   # PO selection with WO dropdown
SalesInvoiceCreateView        # 4-tab creation form
SalesInvoiceUpdateView        # Edit existing invoice
SalesInvoiceDeleteView        # Delete with confirmation
SalesInvoicePrintView         # PDF generation
```

### 2.3 Form Structure
```
POSelectionSearchForm         # Search POs by customer/PO number
SalesInvoiceHeaderForm        # Invoice header fields
SalesInvoiceBuyerForm         # Buyer information (13 fields)
SalesInvoiceConsigneeForm     # Consignee information (13 fields)
SalesInvoiceGoodsFormSet      # Items grid with checkboxes
SalesInvoiceTaxationForm      # Tax calculations
```

### 2.4 Service Layer
```
SalesInvoiceService           # Core business logic
SalesInvoiceValidationService # Validation rules
SalesInvoiceCalculationService # Tax and total calculations
SalesInvoiceLookupService     # Master data lookups
```

### 2.5 UI/UX Design
- **Classic ASP.NET styling** - Match legacy look and feel
- **Tab navigation** - JavaScript-based tab switching
- **HTMX enhancements** - Dynamic dropdowns and autocomplete
- **Responsive tables** - Scrollable grids for items
- **Inline validation** - Real-time feedback

## Phase 3: Implementation

### 3.1 Models (if needed)
Review existing models in #[[file:accounts/models.py]] and ensure all fields are properly mapped.

### 3.2 Forms
Create/recreate all forms in #[[file:accounts/forms_sales_invoice.py]]:
- Proper field validation
- Cascading dropdowns
- Formset for items
- Hidden fields for session data

### 3.3 Views
Implement/fix all views in #[[file:accounts/views/transactions/sales_invoice.py]]:
- List view with search/filter
- PO selection with WO dropdown (fix the dropdown issue)
- Create view with proper tab rendering
- Edit view with pre-populated data
- Delete view with quantity restoration
- Print view with PDF generation

### 3.4 Services
Complete all services in #[[file:accounts/services_sales_invoice.py]]:
- Invoice number generation
- Remaining quantity calculation
- Amount percentage validation
- Tax calculations
- Grand total calculation

### 3.5 Templates
Create/fix all templates:
- #[[file:accounts/templates/accounts/transactions/sales_invoice_list.html]]
- #[[file:accounts/templates/accounts/transactions/sales_invoice_po_selection.html]]
- #[[file:accounts/templates/accounts/transactions/sales_invoice_create.html]]
- #[[file:accounts/templates/accounts/transactions/partials/sales_invoice_buyer_tab.html]]
- #[[file:accounts/templates/accounts/transactions/partials/sales_invoice_consignee_tab.html]]
- #[[file:accounts/templates/accounts/transactions/partials/sales_invoice_items_tab.html]]
- #[[file:accounts/templates/accounts/transactions/partials/sales_invoice_taxation_tab.html]]
- #[[file:accounts/templates/accounts/transactions/sales_invoice_delete.html]]
- #[[file:accounts/templates/accounts/transactions/sales_invoice_print.html]]

### 3.6 URLs
Verify URL configuration in #[[file:accounts/urls_sales_invoice.py]] and #[[file:accounts/urls.py]]

### 3.7 JavaScript
Implement all client-side functionality:
- Tab switching logic
- WO dropdown toggle
- Cascading dropdowns (Country → State → City)
- Copy buyer to consignee
- Item selection and validation
- Real-time calculations

## Phase 4: Testing

### 4.1 Unit Tests
- Invoice number generation
- Remaining quantity calculation
- Amount percentage validation
- Tax calculations

### 4.2 Integration Tests
- PO selection flow
- Invoice creation end-to-end
- Invoice editing
- Invoice deletion with quantity restoration

### 4.3 Browser Testing
Test complete user flow:
1. Navigate to Sales Invoice list
2. Click "New Invoice"
3. Search and select a PO
4. Select Work Order(s) from dropdown
5. Select Invoice Type
6. Click "Select" to proceed
7. Verify header fields are populated
8. Navigate to Buyer tab - verify pre-populated data
9. Navigate to Consignee tab - test "Copy from Buyer"
10. Navigate to Goods tab - select items, enter quantities
11. Navigate to Taxation tab - select tax rates
12. Submit form
13. Verify invoice is created
14. Test Edit functionality
15. Test Delete functionality
16. Test Print functionality

### 4.4 Validation Testing
- Test all required field validations
- Test quantity validation (req qty <= remaining qty)
- Test percentage validation (total <= 100%)
- Test date format validation
- Test email format validation
- Test cascading dropdown behavior

## Phase 5: Documentation

### 5.1 Code Documentation
- Docstrings for all classes and methods
- Inline comments for complex logic
- README for module overview

### 5.2 User Documentation
- User guide for creating invoices
- Screenshots of each step
- Troubleshooting guide

## Success Criteria

✅ All tabs render correctly and switch properly
✅ PO selection with WO dropdown works
✅ Buyer tab pre-populates from customer data
✅ Consignee tab has "Copy from Buyer" functionality
✅ Goods tab shows items with remaining quantities
✅ Items can be selected with checkboxes
✅ Quantities can be entered and validated
✅ Taxation tab calculates taxes correctly
✅ Form submission creates invoice successfully
✅ Invoice number is auto-generated correctly
✅ Edit functionality works
✅ Delete functionality restores quantities
✅ Print functionality generates PDF
✅ All validations work as expected
✅ UI matches ASP.NET styling
✅ No console errors
✅ All HTMX interactions work

## Known Issues to Fix

1. **Tab Content Not Showing** - Tab panels are hidden, JavaScript not switching properly
2. **WO Dropdown Not Working** - Dropdown panel not appearing on click
3. **Form Submission** - Need to verify POST handler works correctly
4. **Cascading Dropdowns** - State/City dropdowns need HTMX endpoints
5. **Item Selection** - Checkbox selection and quantity validation
6. **Tax Calculation** - Real-time calculation on form

## Implementation Notes

- Use existing database models (managed=False)
- Match ASP.NET field names exactly
- Preserve all business logic from legacy code
- Use HTMX for dynamic interactions
- Use Alpine.js or vanilla JS for tab switching
- Maintain classic ASP.NET styling
- Ensure backward compatibility with existing data

## Timeline

- Phase 1 (Analysis): 2 hours
- Phase 2 (Design): 1 hour
- Phase 3 (Implementation): 4 hours
- Phase 4 (Testing): 2 hours
- Phase 5 (Documentation): 1 hour

**Total Estimated Time: 10 hours**

## Dependencies

- Django 4.x
- HTMX
- TailwindCSS (for styling)
- ReportLab or WeasyPrint (for PDF generation)
- Existing database schema
- Legacy ASP.NET code for reference

## Deliverables

1. Fully functional Sales Invoice module
2. All templates working correctly
3. All tabs rendering and switching properly
4. Complete test coverage
5. User documentation
6. Code documentation

---

**Status**: Ready for implementation
**Assigned To**: AI Agent
**Priority**: High
**Estimated Completion**: 2025-11-17
