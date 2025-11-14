# Accounts Module

Financial accounting and transaction management for SAPL ERP.

## Overview

The Accounts module handles all financial operations including:
- **Master Data:** Account heads, banks, currencies, payment terms, tax codes
- **Transactions:** Invoices, vouchers, journal entries, bill booking
- **Reports:** Sales register, purchase register, balance sheet, aging reports
- **Reconciliation:** Bank reconciliation and statement matching

## Status

**Migration Progress:** 85% complete

- ✅ **Models:** 100% (managed=False, uses production database)
- ✅ **Views:** 85% (182 view classes implemented)
- ✅ **Forms:** 95% (76KB forms.py)
- ✅ **Templates:** 95% (102 templates)
- ✅ **URLs:** 90% (30KB urls.py)
- ⚠️ **Tests:** 30% (105 test cases created, implementation in progress)

## Quick Start

### Running the Module

```bash
# Start Django server
python manage.py runserver

# Access accounts module
http://localhost:8000/accounts/
```

### Running Tests

```bash
# Quick smoke tests
./run_accounts_tests.sh

# Or manually
pytest tests/playwright/test_accounts_smoke.py -v
```

## Module Structure

```
accounts/
├── models.py              # 97KB - All account models (managed=False)
├── views/                 # 182 view classes
│   ├── dashboard.py       # Dashboards
│   ├── masters/           # Master data views
│   │   ├── acchead.py     # Account heads
│   │   ├── bank.py        # Banks
│   │   ├── currency.py    # Currencies
│   │   ├── payment_terms.py
│   │   ├── tds_code.py
│   │   └── misc.py        # 20+ misc masters
│   ├── transactions/      # Transaction views
│   │   ├── sales_invoice.py
│   │   ├── bill_booking.py
│   │   ├── bank_voucher.py
│   │   ├── cash_voucher.py
│   │   ├── journal_entry.py
│   │   ├── iou.py
│   │   ├── proforma_invoice.py
│   │   ├── debit_note.py
│   │   ├── contra_entry.py
│   │   ├── asset_register.py
│   │   └── tour_voucher.py
│   ├── reports.py         # Financial reports
│   ├── reconciliation.py  # Bank reconciliation
│   └── htmx_endpoints.py  # HTMX API endpoints
├── forms.py               # 76KB - All forms
├── services.py            # 46KB - Business logic
├── urls.py                # 30KB - URL patterns
├── templates/             # 102 templates
│   └── accounts/
│       ├── masters/       # Master templates
│       ├── transactions/  # Transaction templates
│       ├── partials/      # HTMX partials
│       └── invoices/      # Invoice templates
└── templatetags/          # Custom template tags
```

## Features Implemented

### Master Data (25 features)

✅ **Fully Implemented:**
- Account Heads (AccHead)
- Bank Master
- Currency Master
- Payment Terms
- TDS Code Master
- Excisable Commodity
- Excise Service
- Freight Master
- IOU Reasons
- Interest Type
- Invoice Against
- Loan Type
- Octroi
- Packing/Forwarding
- Paid Type
- Payment Mode
- Payment/Receipt Against
- Tour Expenses Type
- VAT Master
- Warranty Terms

⚠️ **Partial/Missing:**
- Cash/Bank Entry (needs verification)
- Cheque Series (needs verification)

### Transactions (11+ core features)

✅ **Fully Implemented:**
1. Sales Invoice (with details, print, advice)
2. Bill Booking (with authorization workflow)
3. Bank Voucher (payment with print)
4. Cash Voucher (payment and receipt)
5. Journal Entry
6. Proforma Invoice
7. IOU (I Owe You)
8. Debit Note
9. Contra Entry
10. Asset Register
11. Tour Voucher (with advance details)

### Reports (5+ reports)

✅ **Implemented:**
- Dashboard Reports
- Aging Report
- Balance Sheet

⚠️ **Partial:**
- Sales Register
- Cash/Bank Register

❌ **TODO:**
- Purchase Register
- Purchase VAT Register
- Search functionality

### Reconciliation

✅ **Fully Implemented:**
- Bank Reconciliation
- Reconciliation Summary
- Mark/Unmark Transactions
- Reconciliation List

## API Endpoints

### Master Data

```
GET    /accounts/masters/acchead/           # List account heads
POST   /accounts/masters/acchead/create/    # Create account head
PUT    /accounts/masters/acchead/<id>/edit/ # Edit account head
DELETE /accounts/masters/acchead/<id>/delete/ # Delete account head
```

Similar patterns for:
- `/masters/bank/`
- `/masters/currency/`
- `/masters/payment-terms/`
- `/masters/tds-code/`

### Transactions

```
GET    /accounts/transactions/sales-invoice/
POST   /accounts/transactions/sales-invoice/create/
PUT    /accounts/transactions/sales-invoice/<id>/edit/
DELETE /accounts/transactions/sales-invoice/<id>/delete/
GET    /accounts/transactions/sales-invoice/<id>/print/
```

Similar patterns for:
- `/transactions/bill-booking/`
- `/transactions/bank-voucher/`
- `/transactions/cash-voucher-payment/`
- `/transactions/cash-voucher-receipt/`
- `/transactions/journal-entry/`
- `/transactions/iou/`
- `/transactions/proforma-invoice/`
- `/transactions/debit-note/`
- `/transactions/contra-entry/`
- `/transactions/asset-register/`
- `/transactions/tour-voucher/`

### Reports

```
GET /accounts/reports/sales-register/
GET /accounts/reports/purchase-register/
GET /accounts/reports/cash-bank-register/
GET /accounts/reports/balance-sheet/
GET /accounts/reports/aging/
```

### Reconciliation

```
GET  /accounts/reconciliation/
GET  /accounts/reconciliation/<bank_id>/
POST /accounts/reconciliation/mark/
GET  /accounts/reconciliation/summary/
```

## Testing

See [TESTING.md](./TESTING.md) for complete testing guide.

**Quick Test:**

```bash
# Smoke tests (~30 seconds)
pytest tests/playwright/test_accounts_smoke.py -v

# Comprehensive tests (~5 minutes)
pytest tests/playwright/test_accounts_comprehensive.py -v
```

**Test Coverage:**
- 105 test cases created
- 15 smoke tests (ready to run)
- 90 comprehensive tests (implementation in progress)

## Migration Status

See [MIGRATION_STATUS.md](./MIGRATION_STATUS.md) for detailed status.

**Summary:**
- ASP.NET files: 133 total
- Django implementation: ~85% complete
- Test coverage: 30% (growing)

## Development Guidelines

### Creating New Features

1. **Models** - DO NOT modify (managed=False)
2. **Views** - Extend from `core/mixins.py`
3. **Forms** - Add to `forms.py`
4. **URLs** - Add to `urls.py` with kebab-case
5. **Templates** - Use Tailwind CSS + HTMX
6. **Tests** - Write Playwright tests

### Audit Fields (CRITICAL)

All transactions MUST populate:

```python
obj.sysdate = datetime.now().strftime('%d-%m-%Y')
obj.systime = datetime.now().strftime('%H:%M:%S')
obj.sessionid = str(request.user.id)
obj.compid = request.session.get('compid', 1)
obj.finyearid = request.session.get('finyearid', 1)
```

### Using Core Mixins

```python
from core.mixins import BaseListViewMixin, BaseCreateViewMixin

class MyListView(BaseListViewMixin, ListView):
    model = MyModel
    template_name = 'accounts/my_list.html'
    search_fields = ['name', 'code']
    paginate_by = 20
```

## ASP.NET Reference

Original ASP.NET code: `aaspnet/Module/Accounts/`

- Masters: `aaspnet/Module/Accounts/Masters/*.aspx`
- Transactions: `aaspnet/Module/Accounts/Transactions/*.aspx`
- Reports: `aaspnet/Module/Accounts/Reports/*.aspx`

## Documentation

- [MIGRATION_STATUS.md](./MIGRATION_STATUS.md) - Detailed migration status
- [TESTING.md](./TESTING.md) - Testing guide
- [VIEWS_STRUCTURE.md](./VIEWS_STRUCTURE.md) - View architecture
- [REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md) - Refactoring notes

## Contributing

1. Check [MIGRATION_STATUS.md](./MIGRATION_STATUS.md) for missing features
2. Implement following Django best practices
3. Write Playwright tests
4. Update documentation
5. Submit PR

## Support

For questions or issues:
1. Check existing documentation
2. Review `CLAUDE.md` in project root
3. Consult `core/mixins.py` for patterns

---

**Module Owner:** Accounts Team
**Last Updated:** Auto-generated
**Status:** 85% Complete, Ready for Testing
