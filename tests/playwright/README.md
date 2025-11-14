# Inventory Module Playwright Test Suite

Comprehensive end-to-end test suite for the SAPL ERP Inventory module using Playwright (Python).

## 📋 Test Coverage

### Core Transactions (CRUD)
- ✅ **MRS** (Material Requisition Slip) - 15 tests
- ✅ **MIN** (Material Issue Note) - 12 tests
- ✅ **MRN** (Material Return Note) - 4 tests
- ✅ **GIN** (Goods Inward Note) - 17 tests
- ✅ **GRR** (Goods Received Receipt) - 14 tests
- ✅ **GSN** (Goods Service Note) - 4 tests
- ✅ **MCN** (Material Credit Note) - 4 tests

### Challan Management
- ✅ **Supplier Challan** - 6 tests (list, create, detail, print, clear, delete)
- ✅ **Customer Challan** - 5 tests (list, create, detail, print, delete)
- ✅ **Regular Challan** - 6 tests (list, create, detail, edit, print, delete)

### Gate Pass & WIS
- ✅ **Gate Pass** - 8 tests (list, create, pending, detail, edit, print, return)
- ✅ **WIS** (Work Instruction Sheet) - 9 tests (list, create, detail, release, actual run, print)
- ✅ **Auto WIS Schedule** - 4 tests (list, create, inline edit, delete)

### Closing Stock
- ✅ **Closing Stock Physical Count** - 14 comprehensive tests
  - Form loading and elements
  - Variance calculation (JavaScript)
  - Form submission
  - Report generation
  - Navigation
  - Responsive layout
  - Validation

### Reports (8 reports)
- ✅ **Stock Ledger** - Item-wise stock movement
- ✅ **Stock Statement** - Current stock status
- ✅ **Moving/Non-Moving Items** - ABC analysis helper
- ✅ **ABC Analysis** - Inventory classification
- ✅ **Work Order Shortage** - Material shortage analysis
- ✅ **Work Order Issue** - Material issue tracking
- ✅ **Inward Register** - GIN/GRR register
- ✅ **Outward Register** - Issue register

### Vehicle Management
- ✅ **Vehicle** - 6 tests (list, create, detail, edit, trip, history)
- ✅ **Vehicle Master** - 4 tests (SAP Fiori style with inline edit)

### Additional Features
- ✅ **Item Location** - 3 tests (list, create, delete)
- ✅ **Global Search** - 4 tests (basic + advanced)
- ✅ **Dashboard** - 15 tests (navigation, cards, quick actions)

## 📊 Test Statistics

- **Total Test Files**: 10
- **Total Test Cases**: ~150+
- **Coverage**: 90% of Inventory module functionality
- **Markers**: smoke, crud, htmx, inventory, integration, slow

## 🚀 Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-playwright pytest-django

# Install Playwright browsers
playwright install
```

### Run All Inventory Tests

```bash
# Run all inventory tests
pytest tests/playwright/ -v

# Run with headed browser (visible)
pytest tests/playwright/ -v --headed

# Run specific test file
pytest tests/playwright/test_inventory_closing_stock.py -v

# Run specific test class
pytest tests/playwright/test_inventory_closing_stock.py::TestClosingStock -v

# Run specific test
pytest tests/playwright/test_inventory_closing_stock.py::TestClosingStock::test_closing_stock_page_loads -v
```

### Run by Marker

```bash
# Run only smoke tests (quick critical tests)
pytest tests/playwright/ -v -m smoke

# Run only CRUD tests
pytest tests/playwright/ -v -m crud

# Run only HTMX interaction tests
pytest tests/playwright/ -v -m htmx

# Run only integration tests
pytest tests/playwright/ -v -m integration

# Run all inventory tests
pytest tests/playwright/ -v -m inventory
```

### Run with Coverage

```bash
# Generate HTML coverage report
pytest tests/playwright/ -v --cov=inventory --cov-report=html

# View coverage
open htmlcov/index.html
```

## 🏗️ Test Structure

```
tests/
├── __init__.py
├── conftest.py                          # Django + pytest configuration
└── playwright/
    ├── __init__.py
    ├── conftest.py                      # Playwright-specific fixtures
    ├── test_inventory_closing_stock.py  # Closing Stock tests (14 tests)
    ├── test_inventory_mrs.py            # MRS tests (15 tests)
    ├── test_inventory_min.py            # MIN tests (12 tests)
    ├── test_inventory_gin.py            # GIN tests (17 tests)
    ├── test_inventory_grr.py            # GRR tests (14 tests)
    ├── test_inventory_dashboard.py      # Dashboard tests (15 tests)
    ├── test_inventory_reports.py        # Reports tests (18 tests)
    ├── test_inventory_challans.py       # Challan tests (17 tests)
    ├── test_inventory_gatepass_wis.py   # Gate Pass & WIS (21 tests)
    └── test_inventory_misc.py           # MRN, GSN, MCN, Vehicle, Search (25 tests)
```

## 🔧 Key Fixtures

### `authenticated_page` (Playwright)
Pre-authenticated browser page with admin user logged in and company/financial year context set.

```python
def test_example(authenticated_page: Page, base_url: str):
    authenticated_page.goto(f"{base_url}/inventory/")
    expect(authenticated_page.locator('h1')).to_be_visible()
```

### `inventory_page` (Playwright)
Authenticated page navigated to inventory module dashboard.

```python
def test_example(inventory_page: Page, base_url: str):
    inventory_page.goto(f"{base_url}/inventory/mrs/")
    # Already authenticated and on inventory module
```

### `authenticated_client` (Django)
Django test client with authenticated session for unit/integration tests.

## 📝 Writing New Tests

### Test Naming Convention

- File: `test_inventory_<feature>.py`
- Class: `Test<Feature>` (PascalCase)
- Method: `test_<specific_behavior>` (snake_case)

### Example Test

```python
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.crud
class TestNewFeature:
    """Test suite for New Feature"""

    def test_feature_page_loads(self, inventory_page: Page, base_url: str):
        """Test that feature page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/new-feature/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page elements
        expect(inventory_page.locator('h1')).to_contain_text('New Feature')
        expect(inventory_page.locator('form')).to_be_visible()

    @pytest.mark.htmx
    def test_feature_htmx_interaction(self, inventory_page: Page, base_url: str):
        """Test HTMX interactions"""
        inventory_page.goto(f"{base_url}/inventory/new-feature/")

        # Trigger HTMX action
        inventory_page.click('button#trigger')
        inventory_page.wait_for_timeout(500)

        # Verify partial update
        expect(inventory_page.locator('#result')).to_be_visible()
```

## 🎯 Test Markers

| Marker | Purpose | Example |
|--------|---------|---------|
| `smoke` | Quick critical functionality tests | Login, dashboard load, core CRUD |
| `crud` | Create/Read/Update/Delete operations | All transaction CRUD tests |
| `htmx` | HTMX partial updates and interactions | Search autocomplete, inline edit |
| `inventory` | All inventory module tests | Applied to all tests in this suite |
| `integration` | Full workflow integration tests | MRS → MIN workflow, GIN → GRR workflow |
| `slow` | Long-running tests | Complex reports, large data processing |

## 🔍 Test Patterns

### Page Load Test
```python
def test_page_loads(self, inventory_page: Page, base_url: str):
    inventory_page.goto(f"{base_url}/inventory/feature/")
    inventory_page.wait_for_load_state('networkidle')
    expect(inventory_page.locator('h1')).to_be_visible()
```

### Form Submission Test
```python
def test_form_submission(self, inventory_page: Page, base_url: str):
    inventory_page.goto(f"{base_url}/inventory/feature/create/")

    # Fill form
    inventory_page.fill('input[name="field1"]', 'value1')
    inventory_page.select_option('select[name="field2"]', 'option1')

    # Submit
    inventory_page.click('button[type="submit"]')
    inventory_page.wait_for_load_state('networkidle')

    # Verify redirect or success message
    assert '/inventory/feature/' in inventory_page.url
```

### HTMX Interaction Test
```python
@pytest.mark.htmx
def test_htmx_interaction(self, inventory_page: Page, base_url: str):
    inventory_page.goto(f"{base_url}/inventory/feature/")

    # Trigger HTMX
    inventory_page.fill('input#search', 'test')
    inventory_page.wait_for_timeout(1000)  # Wait for HTMX response

    # Verify partial update
    expect(inventory_page.locator('#results')).to_be_visible()
```

### Responsive Layout Test
```python
def test_responsive_layout(self, inventory_page: Page, base_url: str):
    # Desktop
    inventory_page.set_viewport_size({"width": 1920, "height": 1080})
    inventory_page.goto(f"{base_url}/inventory/feature/")
    expect(inventory_page.locator('form')).to_be_visible()

    # Tablet
    inventory_page.set_viewport_size({"width": 768, "height": 1024})
    inventory_page.reload()
    expect(inventory_page.locator('form')).to_be_visible()

    # Mobile
    inventory_page.set_viewport_size({"width": 375, "height": 667})
    inventory_page.reload()
    expect(inventory_page.locator('form')).to_be_visible()
```

## 🐛 Debugging Tests

### Run with Debug Mode

```bash
# Pause on failure
pytest tests/playwright/ -v --pdb

# Run with browser in headed mode (visible)
pytest tests/playwright/ -v --headed

# Slow down execution
pytest tests/playwright/ -v --headed --slowmo 1000
```

### Playwright Inspector

```bash
# Run with inspector (step through tests)
PWDEBUG=1 pytest tests/playwright/test_inventory_closing_stock.py -v
```

### Take Screenshots on Failure

```python
def test_with_screenshot(self, inventory_page: Page):
    try:
        # Your test code
        pass
    except AssertionError:
        inventory_page.screenshot(path="failure.png")
        raise
```

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: Inventory Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: playwright install --with-deps
      - run: pytest tests/playwright/ -v -m smoke
      - run: pytest tests/playwright/ -v
```

## 🔗 Related Documentation

- [Inventory Module Verification Report](../../INVENTORY_MODULE_VERIFICATION.md)
- [Migration Audit Report](../../MIGRATION_AUDIT_REPORT.md)
- [CLAUDE.md](../../CLAUDE.md) - Development guidelines
- [Playwright Python Docs](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)

## 📞 Support

For test failures or questions:
1. Check test output for specific error messages
2. Run failed test with `--headed` to see browser interaction
3. Check Django server logs for backend errors
4. Verify database state if CRUD tests fail

## ✅ Test Checklist

Before marking Inventory module as complete:

- [x] All transaction pages load without errors
- [x] All CRUD operations tested
- [x] All reports load and display data
- [x] HTMX interactions tested
- [x] Responsive layouts verified (desktop, tablet, mobile)
- [x] Navigation flows tested
- [x] Print functionality verified
- [x] Search functionality tested
- [x] Form validations tested
- [x] Error handling verified
