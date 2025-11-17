# Sales Invoice Module - Django Migration Plan

## Overview
The Sales Invoice module is a comprehensive invoicing system that manages customer invoices with GST/IGST taxation support, multiple invoice types, and detailed buyer/consignee/goods tracking.

## Module Structure

### URLs
- `/accounts/transactions/sales-invoice/` - Dashboard/List view
- `/accounts/transactions/sales-invoice/new/` - Create new invoice (step 1: select PO)
- `/accounts/transactions/sales-invoice/create/<po_id>/` - Create invoice form
- `/accounts/transactions/sales-invoice/edit/<invoice_id>/` - Edit invoice
- `/accounts/transactions/sales-invoice/delete/<invoice_id>/` - Delete invoice
- `/accounts/transactions/sales-invoice/print/<invoice_id>/` - Print invoice

### Models Required

#### SalesInvoice (Main Model)
- invoice_number (CharField, unique, auto-generated)
- invoice_date (DateField)
- mode_of_invoice (CharField: Within Maharashtra, Out of Maharashtra)
- po_number (ForeignKey to PurchaseOrder)
- po_date (DateField)
- wo_number (CharField)
- category (CharField: Industrial Consumer, Wholesale Dealer, Government Department, Other)
- excisable_commodity (CharField)
- tariff_head_no (CharField)
- mode_of_transport (CharField: By Road, By Air, By Ship, By Post, By Courier)
- date_of_issue (DateField)
- date_of_removal (DateField)
- company (ForeignKey to Company)
- financial_year (ForeignKey to FinancialYear)
- created_by (ForeignKey to User)
- created_at (DateTimeField)
- updated_at (DateTimeField)

#### SalesInvoiceParty (Buyer/Consignee)
- invoice (ForeignKey to SalesInvoice)
- party_type (CharField: Buyer, Consignee)
- customer (ForeignKey to Customer)
- address (TextField)
- country (CharField)
- state (CharField)
- city (CharField)
- contact_person (CharField)
- phone (CharField)
- mobile (CharField)
- email (EmailField)
- gst_number (CharField)

#### SalesInvoiceItem
- invoice (ForeignKey to SalesInvoice)
- item_description (CharField)
- unit (CharField)
- quantity (DecimalField)
- remaining_quantity (DecimalField)
- required_quantity (DecimalField)
- unit_of_quantity (CharField)
- amount_in_per (DecimalField)
- rate (DecimalField)
- total_amount (DecimalField, calculated)

#### SalesInvoiceTaxation
- invoice (OneToOneField to SalesInvoice)
- cgst_igst_type (CharField)
- cgst_igst_rate (DecimalField)
- vat_sgst_type (CharField)
- vat_sgst_rate (DecimalField)
- cgst_amount (DecimalField, calculated)
- sgst_amount (DecimalField, calculated)
- igst_amount (DecimalField, calculated)
- total_tax_amount (DecimalField, calculated)
- grand_total (DecimalField, calculated)

### Views Structure

#### SalesInvoiceListView
- Display paginated list of invoices
- Search by customer name, PO number, invoice number
- Filter by financial year, company
- Actions: New, Edit, Delete, Print

#### SalesInvoiceNewView
- Step 1: Display list of POs to select from
- Search by customer name or PO number
- Select WO number and invoice type
- Redirect to create form

#### SalesInvoiceCreateView
- Multi-step form with tabs:
  - Buyer Information
  - Consignee Information
  - Goods/Items
  - Taxation
- HTMX for tab navigation
- Auto-populate from PO data
- Calculate totals automatically

#### SalesInvoiceEditView
- Same as create but pre-populated
- Multi-step form with tabs
- Update existing invoice

#### SalesInvoiceDeleteView
- Confirm deletion
- Soft delete or hard delete based on business rules

#### SalesInvoicePrintView
- Generate PDF invoice
- Include all details: buyer, consignee, items, taxation
- Company letterhead and formatting

### Templates Structure

```
accounts/templates/accounts/transactions/
├── sales_invoice_list.html
├── sales_invoice_new.html
├── sales_invoice_form.html
├── sales_invoice_print.html
└── partials/
    ├── sales_invoice_buyer_tab.html
    ├── sales_invoice_consignee_tab.html
    ├── sales_invoice_goods_tab.html
    ├── sales_invoice_taxation_tab.html
    └── sales_invoice_search_results.html
```

### Services/Business Logic

#### SalesInvoiceService
- `generate_invoice_number()` - Auto-generate invoice number
- `calculate_item_total(item)` - Calculate item total
- `calculate_tax_amounts(invoice)` - Calculate CGST/SGST/IGST
- `calculate_grand_total(invoice)` - Calculate final total
- `copy_buyer_to_consignee(invoice)` - Copy buyer details to consignee
- `validate_invoice(invoice)` - Validate invoice data

### Forms

#### SalesInvoiceHeaderForm
- Invoice header fields
- PO selection
- Category, commodity, transport mode

#### SalesInvoicePartyForm
- Buyer/Consignee information
- Customer search
- Address details

#### SalesInvoiceItemFormSet
- Inline formset for items
- Dynamic add/remove rows

#### SalesInvoiceTaxationForm
- Tax type selection
- Tax rate selection
- Auto-calculate amounts

### Key Features to Implement

1. **Multi-step Form with Tabs**
   - Use HTMX for seamless tab navigation
   - Save progress at each step
   - Validation per tab

2. **Auto-calculations**
   - Item totals
   - Tax amounts (CGST/SGST/IGST)
   - Grand total
   - Real-time updates with HTMX

3. **Customer Search**
   - HTMX-powered search
   - Auto-populate customer details
   - GST number validation

4. **Copy Functionality**
   - Copy buyer details to consignee
   - One-click duplication

5. **Invoice Number Generation**
   - Auto-generate sequential numbers
   - Format: INV-YYYY-XXXX

6. **PDF Generation**
   - Professional invoice layout
   - Company branding
   - Tax calculations
   - Terms and conditions

7. **Permissions**
   - Create: Sales team, Accounts team
   - Edit: Accounts team only
   - Delete: Accounts manager only
   - Print: All authorized users

## Implementation Steps

1. **Phase 1: Models**
   - Create all models
   - Add migrations
   - Create admin interface

2. **Phase 2: Basic CRUD**
   - List view with search/filter
   - Create view (simple form)
   - Edit view
   - Delete view

3. **Phase 3: Multi-step Form**
   - Implement tab navigation
   - HTMX integration
   - Form validation

4. **Phase 4: Calculations**
   - Item total calculations
   - Tax calculations
   - Grand total

5. **Phase 5: PDF Generation**
   - Invoice template
   - PDF rendering
   - Download functionality

6. **Phase 6: Testing**
   - Unit tests
   - Integration tests
   - User acceptance testing

## Database Relationships

```
SalesInvoice (1) -----> (N) SalesInvoiceItem
SalesInvoice (1) -----> (1) SalesInvoiceTaxation
SalesInvoice (1) -----> (N) SalesInvoiceParty
SalesInvoice (N) -----> (1) PurchaseOrder
SalesInvoice (N) -----> (1) Customer
SalesInvoice (N) -----> (1) Company
SalesInvoice (N) -----> (1) FinancialYear
```

## Notes
- The module follows the same pattern as IOU Payment/Receipt
- Uses HTMX for dynamic interactions
- Classic ASP.NET styling maintained
- GST compliance required
- Audit trail for all changes
