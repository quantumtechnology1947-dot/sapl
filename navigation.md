# ERP System - Navigation Structure for React

This document outlines the complete navigation layout for the SAPL/Cortex ERP system to be implemented in React.

## Navigation Hierarchy

### Home

---

### 1. Administrator
- Role Management
- Financial Year
- Country
- State
- City

---

### 2. Sales
#### Master
- Customer
- Category of Work Order
- WO Release & Dispatch Authority

#### Transaction
- Enquiry
- Quotation
- Customer PO
- Work Order
- WO Release
- WO Dispatch
- Dispatch GunRail
- WO Open/Close

---

### 3. Design
#### Master
- BoughtOut Category
- Item Master
- Unit Master
- ECN Reason

#### Transaction
- BOM
- Slido Gunrail
- ECN Unlock

#### Report
- Item history

---

### 4. Planning
#### Master
- Material Process

#### Transaction
- BOM

---

### 5. Material
#### Master
- Business Nature
- Business Type
- Service Coverage
- Buyer
- Supplier
- Set Rate

#### Transaction
- Scope Of Supplier
- Rate Lock/UnLock
- Purchase Requisition [PR]
- Special Purpose Requisition [SPR]
- Check SPR
- Approve SPR
- Purchase Order [PO]
- Check PO
- Approve PO
- Authorize PO

#### Report
- Rate Register
- Rate Lock/UnLock
- Material Forecasting
- Inward/Outward Register
- Search

---

### 6. Project
#### Transaction
- Man Power Planning
- Project Planning

#### Report
- Project Summary

---

### 7. Reports
#### Reports
- Boughtout Design
- Boughtout Vendor
- Boughtout Assemly
- Manufacturing Design
- Manufacturing Vendor
- Manufacturing Assemly

---

### 8. Inventory
#### Master
- Item location
- VEHICLE ENTRY

#### Transaction
- VEHICLE REGISTRATION FORM
- Goods Inward Note [GIN]
- Goods Received Receipt [GRR]
- Goods Service Note [GSN]
- Material Requisition Slip [MRS]
- Material Issue Note [MIN]
- Material Return Note [MRN]
- Delivery Challan
- Challan Summary
- Release WIS
- Dry / Actual WIS Run
- Closing Stock

#### Reports
- Stock Ledger
- Stock Statement
- Material Issue/Shortage list
- Moving-Non Moving Items
- Inward/Outward Register
- Search

---

### 9. QC
#### Transaction
- Goods Quality Note [GQN]
- Material Return Quality Note [MRQN]
- Authorize MCN

#### Report
- Goods Rejection Note [GRN]
- Scrap Material

---

### 10. Accounts
#### Master
- Account Heads
- CGST/IGST
- SGST
- Excisable Commodity
- Warrenty Terms
- Payment Terms
- Cash/Bank Entry
- IOU Reasons
- Bank
- Payment Mode
- Asset

#### Transaction
- Sales Invoice
- IOU Payment/Receipt
- Bill Booking
- Authorize Bill Booking
- POLICY
- Cash Voucher
- Payment/Receipt Voucher
- Advice
- Creditors/Debitors
- Bank Reconciliation
- Balance Sheet
- Asset Register

#### Report
- Sales Register
- Purchase Register
- Pending For Invoice
- PVEV Search
- Cash/Bank Register

---

### 11. HR
#### Master
- Business Group
- Designation
- Department
- Grade
- SwapCard No
- Corporate Mobile
- Intercom Ext
- Gate Pass Types
- Holiday
- PF Slab
- Working Days

#### Transaction
- News And Notices
- Offer Letter
- Staff
- DOCUMENTS
- Mobile Bill
- ASSET LIST
- Authorize Gate Pass
- Bank Loan
- PayRoll

#### Report
- Staff

---

### 12. MR
#### Master
(Empty - Dashboard only)

#### Transaction
- Format/Documents

#### Report
(Empty - Dashboard only)

---

### 13. MIS
#### Transaction
- Financial Budget

#### Report
- Sales Distribution
- Purchase
- Sales
- BOM Costing
- Purchase/Sales Computation
- QA Report

---

### 14. Support
- Change Password
- System Credentials
- ECN

---

### 15. Standalone Pages
- GatePass
- MyScheduler
- IOU
- ChatRoom
- ModuleList

---

## React Implementation Notes

### Navigation Structure
1. **Top-level Menu Items**: 15 main modules (Administrator, Sales, Design, Planning, Material, Project, Reports, Inventory, QC, Accounts, HR, MR, MIS, Support) + 5 standalone pages
2. **Sub-menus**: Most modules have 2-3 levels of nesting (Master, Transaction, Report)
3. **Depth**: Maximum 3 levels deep (Module → Category → Item)

### Component Suggestions
- **NavBar**: Top-level horizontal menu
- **DropdownMenu**: For modules with sub-menus
- **MenuItem**: Individual navigation items
- **MegaMenu**: Optional for larger sections like Inventory or Accounts

### Key Features to Implement
- Collapsible/Expandable menus
- Active state highlighting
- Breadcrumb navigation
- Responsive mobile menu
- Search functionality for quick navigation
- Recent/Favorites section
- Role-based menu visibility (based on user permissions)

### Grouping Strategy
Consider grouping modules by business function:
1. **Administration**: Administrator, Support
2. **Sales & Marketing**: Sales, Design
3. **Supply Chain**: Material, Planning, Inventory, QC
4. **Projects**: Project, Reports
5. **Finance**: Accounts
6. **Human Resources**: HR
7. **Operations**: MR, MIS
8. **Utilities**: GatePass, MyScheduler, IOU, ChatRoom

---

## Module Count Summary
- Total Modules: 14 main modules
- Total Master Screens: ~50+
- Total Transaction Screens: ~60+
- Total Report Screens: ~30+
- Standalone Features: 5

---

## Next Steps for React Implementation
1. Create a navigation configuration file (JSON/TypeScript)
2. Build reusable NavBar and MenuItem components
3. Implement routing structure matching this hierarchy
4. Add permission-based visibility logic
5. Create breadcrumb component
6. Implement mobile-responsive drawer/hamburger menu
7. Add search/filter functionality for large menus
