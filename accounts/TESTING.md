# Accounts Module - Testing Guide

## Test Coverage

**Total Test Files:** 2
- `test_accounts_smoke.py` - 15 quick smoke tests
- `test_accounts_comprehensive.py` - ~90 comprehensive tests

**Coverage Areas:**
- ✅ Dashboard views
- ✅ Master data (AccHead, Bank, Currency, Payment Terms, TDS Code, etc.)
- ✅ Transactions (Sales Invoice, Bill Booking, Vouchers, Journal Entry, etc.)
- ✅ Reports
- ✅ Reconciliation
- ✅ HTMX interactions
- ✅ Form validation
- ✅ Search and pagination
- ✅ Print/Export functionality

## Running Tests

### Quick Start

```bash
# Easy way - Use the test runner script
./run_accounts_tests.sh

# Choose from menu:
# 1. Smoke tests (fast)
# 2. Comprehensive tests (thorough)
# 3. All tests
# 4. Headed mode (see browser)
```

### Manual Test Execution

#### 1. Run Smoke Tests (Recommended to start)

```bash
# Fast smoke tests (~30 seconds)
pytest tests/playwright/test_accounts_smoke.py -v

# With browser visible
pytest tests/playwright/test_accounts_smoke.py -v --headed
```

#### 2. Run Comprehensive Tests

```bash
# Full test suite (~5 minutes)
pytest tests/playwright/test_accounts_comprehensive.py -v

# Run specific test class
pytest tests/playwright/test_accounts_comprehensive.py::TestAccountHeadMaster -v

# Run single test
pytest tests/playwright/test_accounts_comprehensive.py::TestAccountHeadMaster::test_acchead_list_view_loads -v
```

#### 3. Run by Marker

```bash
# Smoke tests only
pytest -m smoke -v

# HTMX interaction tests
pytest -m htmx -v

# CRUD tests
pytest -m crud -v

# Slow tests
pytest -m slow -v
```

#### 4. Run All Accounts Tests

```bash
pytest tests/playwright/test_accounts*.py -v
```

## Test Structure

### Smoke Tests (`test_accounts_smoke.py`)

Quick validation that pages load without errors:

| Test Class | Tests | Purpose |
|------------|-------|---------|
| TestAccountsModuleSmoke | 10 | Core pages load |
| TestAccountsCreateForms | 3 | Forms render |
| TestAccountsNavigation | 2 | Navigation works |

**Total:** 15 tests

### Comprehensive Tests (`test_accounts_comprehensive.py`)

Full functionality testing:

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestAccountsDashboard | 3 | Dashboard |
| TestAccountHeadMaster | 3+ | Account Head CRUD |
| TestBankMaster | 2 | Bank CRUD |
| TestCurrencyMaster | 2 | Currency CRUD |
| TestPaymentTermsMaster | 2 | Payment Terms CRUD |
| TestTDSCodeMaster | 2 | TDS Code CRUD |
| TestSalesInvoice | 3 | Sales Invoice |
| TestBankVoucher | 3 | Bank Voucher |
| TestCashVoucher | 2 | Cash Voucher |
| TestJournalEntry | 2 | Journal Entry |
| TestBillBooking | 3 | Bill Booking |
| TestAdvicePayment | 2 | Advice Payment |
| TestContraEntry | 1 | Contra Entry |
| TestDebitNote | 1 | Debit Note |
| TestProformaInvoice | 1 | Proforma Invoice |
| TestIOUTransactions | 1 | IOU |
| TestAssetRegister | 1 | Asset Register |
| TestTourVoucher | 1 | Tour Voucher |
| TestAccountsReports | 5 | Reports |
| TestBankReconciliation | 3 | Reconciliation |
| TestSearchFunctionality | 4 | Search |
| TestPagination | 1 | Pagination |
| TestHTMXInteractions | 1 | HTMX |
| TestFormValidation | 1 | Validation |
| TestPrintExport | 3 | Print/Export |
| TestAccountsSmoke | 1 | Smoke |

**Total:** ~90 tests

## Test Data

### Setup

Tests use the existing `db.sqlite3` database. For clean testing:

```bash
# Backup production data
cp db.sqlite3 db.sqlite3.backup

# Load test data
python manage.py loaddata csv_data/accounts_test_data.json
```

### Creating Test Data

Test data should be created via:
1. Django management commands
2. Fixtures in `csv_data/`
3. Factory functions in test setup

## Writing New Tests

### Template

```python
class TestNewFeature:
    """Test description"""

    def test_feature_works(self, authenticated_page: Page):
        """Test that feature works"""
        authenticated_page.goto("http://localhost:8000/accounts/feature/")

        # Assertions
        assert "404" not in authenticated_page.content()
        expect(authenticated_page.locator("form")).to_be_visible()
```

### Best Practices

1. **Use fixtures** - `authenticated_page` for logged-in state
2. **Wait for elements** - Use `wait_for_selector` or `expect().to_be_visible()`
3. **Clear assertions** - Test one thing per test
4. **Use markers** - `@pytest.mark.smoke`, `@pytest.mark.htmx`, etc.
5. **Clean up** - Reset state after tests

### Common Patterns

#### Testing List Views

```python
def test_list_view(self, authenticated_page: Page):
    authenticated_page.goto("http://localhost:8000/accounts/masters/acchead/")

    # Should not error
    assert "404" not in authenticated_page.content()

    # Should have table
    authenticated_page.wait_for_selector("table", timeout=5000)
```

#### Testing Create Forms

```python
def test_create_form(self, authenticated_page: Page):
    authenticated_page.goto("http://localhost:8000/accounts/masters/acchead/create/")

    # Fill form
    authenticated_page.fill("#id_category", "Test")

    # Submit
    authenticated_page.click("button[type=submit]")

    # Verify success
    authenticated_page.wait_for_timeout(1000)
    assert "Test" in authenticated_page.content()
```

#### Testing HTMX

```python
@pytest.mark.htmx
def test_htmx_interaction(self, authenticated_page: Page):
    authenticated_page.goto("http://localhost:8000/accounts/transactions/sales-invoice/create/")

    # Click HTMX button
    authenticated_page.click("button[hx-get]")

    # Wait for response
    authenticated_page.wait_for_timeout(500)

    # Verify update
    assert authenticated_page.locator(".new-row").count() > 0
```

## Continuous Integration

### GitHub Actions

Add to `.github/workflows/tests.yml`:

```yaml
name: Accounts Module Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install chromium

    - name: Run migrations
      run: python manage.py migrate

    - name: Run smoke tests
      run: pytest tests/playwright/test_accounts_smoke.py -v

    - name: Run comprehensive tests
      run: pytest tests/playwright/test_accounts_comprehensive.py -v
```

## Troubleshooting

### Issue: "Element not found"

**Solution:** Increase timeout or check selector

```python
authenticated_page.wait_for_selector("table", timeout=10000)
```

### Issue: "Login fails"

**Solution:** Check credentials in fixture

```python
page.fill("input[name='username']", "admin")
page.fill("input[name='password']", "admin")
```

### Issue: "Tests are slow"

**Solution:** Run smoke tests first, or use markers

```bash
pytest -m "smoke and not slow" -v
```

### Issue: "HTMX tests fail"

**Solution:** Ensure server has HTMX loaded, check network tab

```python
authenticated_page.wait_for_load_state("networkidle")
```

## Test Coverage Goals

| Metric | Current | Target |
|--------|---------|--------|
| Views Tested | ~30/182 | 182/182 (100%) |
| Forms Tested | ~10/50 | 50/50 (100%) |
| HTMX Interactions | ~2/20 | 20/20 (100%) |
| Reports Tested | ~3/10 | 10/10 (100%) |

## Next Steps

1. ✅ Create smoke test suite
2. ✅ Create comprehensive test suite
3. ⏳ Implement all test TODOs
4. ⏳ Add database validation tests
5. ⏳ Add print/export tests
6. ⏳ Add performance tests
7. ⏳ Add accessibility tests

## Resources

- [Playwright Python Docs](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [HTMX Testing Guide](https://htmx.org/docs/#testing)

---

**Last Updated:** Auto-generated
**Test Status:** In Progress (30/182 views tested)
