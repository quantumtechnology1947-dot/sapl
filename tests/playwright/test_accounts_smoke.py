"""
Accounts Module - Smoke Tests
Quick tests to verify core functionality works
Run with: pytest tests/playwright/test_accounts_smoke.py -v --headed
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def authenticated_page(page: Page):
    """Login and return authenticated page"""
    page.goto("http://localhost:8000/login/")
    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "admin")
    page.click("button[type=submit]")
    page.wait_for_url("**")  # Wait for navigation
    return page


@pytest.mark.smoke
class TestAccountsModuleSmoke:
    """Smoke tests for Accounts module"""

    def test_accounts_dashboard_loads(self, authenticated_page: Page):
        """Verify accounts dashboard is accessible"""
        authenticated_page.goto("http://localhost:8000/accounts/")

        # Should not show error pages
        page_content = authenticated_page.content()
        assert "404 Not Found" not in page_content
        assert "500 Internal Server Error" not in page_content
        assert "Server Error (500)" not in page_content

        # Should have accounts-related content
        page_content_lower = page_content.lower()
        assert any(word in page_content_lower for word in ["accounts", "dashboard", "master", "transaction"])

    def test_masters_dashboard_loads(self, authenticated_page: Page):
        """Verify masters dashboard is accessible"""
        authenticated_page.goto("http://localhost:8000/accounts/masters/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

    def test_acchead_list_loads(self, authenticated_page: Page):
        """Verify account head list view loads"""
        authenticated_page.goto("http://localhost:8000/accounts/masters/acchead/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

        # Should have table or list elements
        page_content = authenticated_page.content()
        assert any(tag in page_content for tag in ["<table", "<tbody", "list-group"])

    def test_bank_list_loads(self, authenticated_page: Page):
        """Verify bank list view loads"""
        authenticated_page.goto("http://localhost:8000/accounts/masters/bank/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

    def test_currency_list_loads(self, authenticated_page: Page):
        """Verify currency list view loads"""
        authenticated_page.goto("http://localhost:8000/accounts/masters/currency/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

    def test_sales_invoice_list_loads(self, authenticated_page: Page):
        """Verify sales invoice list view loads"""
        authenticated_page.goto("http://localhost:8000/accounts/transactions/sales-invoice/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

    def test_bill_booking_list_loads(self, authenticated_page: Page):
        """Verify bill booking list view loads"""
        authenticated_page.goto("http://localhost:8000/accounts/transactions/bill-booking/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

    def test_bank_voucher_list_loads(self, authenticated_page: Page):
        """Verify bank voucher list view loads"""
        authenticated_page.goto("http://localhost:8000/accounts/transactions/bank-voucher/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

    def test_cash_voucher_payment_list_loads(self, authenticated_page: Page):
        """Verify cash voucher payment list view loads"""
        authenticated_page.goto("http://localhost:8000/accounts/transactions/cash-voucher-payment/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

    def test_journal_entry_list_loads(self, authenticated_page: Page):
        """Verify journal entry list view loads"""
        authenticated_page.goto("http://localhost:8000/accounts/transactions/journal-entry/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()


@pytest.mark.smoke
class TestAccountsCreateForms:
    """Smoke tests for create forms"""

    def test_acchead_create_form_loads(self, authenticated_page: Page):
        """Verify account head create form loads"""
        authenticated_page.goto("http://localhost:8000/accounts/masters/acchead/create/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()

        # Should have a form
        assert "<form" in authenticated_page.content()

    def test_bank_create_form_loads(self, authenticated_page: Page):
        """Verify bank create form loads"""
        authenticated_page.goto("http://localhost:8000/accounts/masters/bank/create/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()
        assert "<form" in authenticated_page.content()

    def test_sales_invoice_create_form_loads(self, authenticated_page: Page):
        """Verify sales invoice create form loads"""
        authenticated_page.goto("http://localhost:8000/accounts/transactions/sales-invoice/create/")

        assert "404" not in authenticated_page.content()
        assert "500" not in authenticated_page.content()
        assert "<form" in authenticated_page.content()


@pytest.mark.smoke
@pytest.mark.slow
class TestAccountsNavigation:
    """Test navigation between pages"""

    def test_navigate_from_dashboard_to_masters(self, authenticated_page: Page):
        """Test navigating from dashboard to masters"""
        authenticated_page.goto("http://localhost:8000/accounts/")

        # Find and click masters link
        masters_link = authenticated_page.locator("a[href*='masters']").first
        if masters_link.count() > 0:
            masters_link.click()
            authenticated_page.wait_for_timeout(1000)

            # Should be on masters page
            assert "/accounts/masters" in authenticated_page.url

    def test_navigate_from_dashboard_to_transactions(self, authenticated_page: Page):
        """Test navigating from dashboard to transactions"""
        authenticated_page.goto("http://localhost:8000/accounts/")

        # Find and click transactions link
        trans_link = authenticated_page.locator("a[href*='transactions']").first
        if trans_link.count() > 0:
            trans_link.click()
            authenticated_page.wait_for_timeout(1000)

            # Should be on transactions page
            assert "/accounts/transactions" in authenticated_page.url
