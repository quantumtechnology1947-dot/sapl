# Sales Invoice Module - Complete Django Implementation

## Summary

Based on the investigation of the legacy ASP.NET system at:
`http://localhost/NewERP/Module/Accounts/Transactions/SalesInvoice_Dashboard.aspx`

This document provides a complete step-by-step implementation plan for migrating the Sales Invoice module to Django.

## Key Findings from Legacy System

### Pages Analyzed:
1. **Dashboard** (`SalesInvoice_Dashboard.aspx`) - Empty landing page with New/Edit/Delete/Print links
2. **New Invoice** (`SalesInvoice_New.aspx`) - List of POs to select from with WO No and Type selection
3. **Edit Invoice** (`SalesInvoice_Edit.aspx`) - List of existing invoices
4. **Edit Details** (`SalesInvoice_Edit_Details.aspx`) - Multi-tab form with:
   - **Buyer Tab**: Customer details, address, GST info
   - **Consignee Tab**: Delivery address (can copy from buyer)
   - **Goods Tab**: Invoice items with quantities and rates
   - **Taxation Tab**: CGST/IGST and VAT/SGST selection

### Data Structure Identified:

**Invoice Header:**
- Invoice No: 0091 (auto-generated)
- Date: 28-02-2023
- Mode of Invoice: Within Maharashtra / Out of Maharashtra
- PO No: verbal_NMC_9-11-22
- PO Date: 09-11-2022
- WO No: N0283
- Category: Industrial Consumer, Wholesale Dealer, Government Department, Other
- Excisable Commodity: Jigs & Fixture Other (dropdown with many options)
- Tariff Head No: 84799090
- Mode of Transport: By Road, By Air, By Ship, By Post, By Courier
- Date Of Issue Of Invoice: 28-02-2023
- Date Of Removal: 28-02-2023

**Buyer/Consignee:**
- Name: TRACK COMPONENTS LIMITED [T019]
- Address: A1/4 Mvml vendor park ,chakan phase iv,, MIDC, Bhosari, Pimpri-Chinchwad, Maharashtra 410501
- Country: India
- State: Maharashtra
- City: Pune
- Contact person: Rahul Agnihotri
- Phone No: 9090909090
- Mobile No: 9090909090
- E-mail: xyz@gmail.com
- GST No: 27AABCT2865J1Z2

**Invoice Items:**
- SN: 1
- Item Desc: 0101CAF02780N(PANEL ASSY COWL INNER)
- Unit: NOS
- Qty: 1
- Rem Qty: 0
- Req Qty: 1
- Unit Of Qty: NOS
- Amt In Per: 100
- Rate: 850000

**Taxation:**
- CGST/IGST: IGST@18%
- VAT: SGST@ 9%

## Implementation Plan

### Phase 1: Create Models (New Django-managed models)

Since the existing models are `managed=False` (legacy database), we'll create new Django-managed models for the Sales Invoice module.

### Phase 2: Create Forms

### Phase 3: Create Views

### Phase 4: Create Templates

### Phase 5: Create URLs

### Phase 6: Create Services

### Phase 7: Testing

## Detailed Implementation

See the following files for complete code:
- `accounts/models_sales_invoice.py` - New models
- `accounts/forms_sales_invoice.py` - Forms
- `accounts/views/transactions/sales_invoice.py` - Views
- `accounts/services_sales_invoice.py` - Business logic
- `accounts/templates/accounts/transactions/sales_invoice_*.html` - Templates
- `accounts/urls_sales_invoice.py` - URL patterns

## Migration Strategy

1. Create new Django-managed tables with proper relationships
2. Migrate data from legacy tables (if needed)
3. Implement CRUD operations
4. Add GST calculations
5. Add PDF generation
6. Add permissions and audit trail

## Notes

- The legacy system uses session-based temporary tables
- Django will use proper form sessions and database transactions
- GST rates and types are hardcoded in dropdowns - should be moved to database
- Invoice numbering should be atomic and sequential
- PDF generation will use ReportLab or WeasyPrint
