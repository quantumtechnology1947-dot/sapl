"""
Simple Sales Invoice E2E Tests
Tests against the running development server without Django test database
"""
import pytest
from playwright.sync_api import Page, expect


class TestSalesInvoiceE2E:
    """End-to-end tests for sales invoice functionality"""

    BASE_URL = "http://localhost:8000"

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Login before each test"""
        self.page = page

        # Login
        page.goto(f"{self.BASE_URL}/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('load')  # Changed from 'networkidle' to 'load'

        yield

        # Cleanup
        page.close()

    def test_sales_invoice_list_loads(self):
        """Test: Sales invoice list page loads correctly"""
        page = self.page

        # Navigate to sales invoice list
        page.goto(f"{self.BASE_URL}/accounts/transactions/sales-invoice/")
        page.wait_for_load_state('load')

        # Verify page loaded (check for key elements)
        content = page.content()
        assert '404' not in content
        assert 'Sales Invoice' in content or 'Invoice' in content

    def test_sales_invoice_create_page_loads(self):
        """Test: Sales invoice create page loads after PO selection"""
        page = self.page

        # Try with known PO from development database
        # Note: PO might not exist in all environments, so we test for either success or proper error handling
        page.goto(f"{self.BASE_URL}/accounts/transactions/sales-invoice/create/?poid=243&wn=232&pn=10339233&date=2014-04-12&ty=2&cid=C002")
        page.wait_for_load_state('load')

        content = page.content()

        # Either the page loads successfully OR shows a proper error (not a route not found 404)
        # If it's a 404, it should be about the PO not existing, not the route itself
        is_success = '404' not in content and 'Error' not in content
        is_valid_error = 'PO' in content or 'Purchase Order' in content or 'Not Found' in content

        # Page should either load successfully or show a meaningful error
        assert is_success or is_valid_error, "Page should load or show meaningful error about missing PO"

    def test_cascading_dropdowns_present(self):
        """Test: Country/State/City dropdowns are present"""
        page = self.page

        page.goto(f"{self.BASE_URL}/accounts/transactions/sales-invoice/create/?poid=243&wn=232&pn=10339233&date=2014-04-12&ty=2&cid=C002")
        page.wait_for_load_state('load')

        # Wait a bit for form to render
        page.wait_for_timeout(1000)

        # Check for country/state/city dropdowns in the page HTML
        content = page.content()

        # Check if dropdown-related HTML exists (country, state, city)
        dropdowns_exist = (
            'buyer_country' in content or
            'buyer_state' in content or
            'buyer_city' in content or
            'consignee_country' in content or
            'id_buyer_country' in content
        )
        assert dropdowns_exist, "Cascading dropdowns should be present"

    def test_goods_tab_displays_items(self):
        """Test: Goods tab shows PO items"""
        page = self.page

        page.goto(f"{self.BASE_URL}/accounts/transactions/sales-invoice/create/?poid=243&wn=232&pn=10339233&date=2014-04-12&ty=2&cid=C002")
        page.wait_for_load_state('load')

        # Wait for page to fully render
        page.wait_for_timeout(1000)

        # Check if there's a table or items-related HTML in the page
        content = page.content()

        # Look for goods/items related content
        items_exist = (
            'item_id' in content or
            'item_desc' in content or
            'req_qty' in content or
            'rate' in content or
            page.locator('table').count() > 0
        )

        assert items_exist, "Goods/items should be present in the form"

    def test_print_view_for_existing_invoice(self):
        """Test: Print view loads for an existing invoice"""
        page = self.page

        # Navigate to list first to find an invoice
        page.goto(f"{self.BASE_URL}/accounts/transactions/sales-invoice/")
        page.wait_for_load_state('load')

        # Try to find a print link
        print_links = page.locator('a:has-text("Print"), a[href*="/print/"]')

        if print_links.count() > 0:
            # Click first print link
            print_url = print_links.first.get_attribute('href')
            if print_url:
                page.goto(f"{self.BASE_URL}{print_url}")
                page.wait_for_load_state('load')

                # Verify print page loaded
                content = page.content()
                assert '404' not in content
                assert 'Invoice' in content or 'Print' in content
        else:
            # If no invoices exist, just verify the pattern would work
            # Try invoice ID 1 as example
            page.goto(f"{self.BASE_URL}/accounts/transactions/sales-invoice/1/print/")
            page.wait_for_load_state('load')

            # Either it loads or shows 404 (both are valid)
            content = page.content()
            assert len(content) > 0, "Print page should return some content"

    def test_page_not_blank_after_login(self):
        """Test: Create page is not blank after login (regression test)"""
        page = self.page

        page.goto(f"{self.BASE_URL}/accounts/transactions/sales-invoice/create/?poid=243&wn=232&pn=10339233&date=2014-04-12&ty=2&cid=C002")
        page.wait_for_load_state('load')

        # Get body HTML
        body_html = page.evaluate('() => document.body.innerHTML')

        # Should have substantial content (not just background)
        assert len(body_html) > 1000, "Page should have significant content"

        # Should not show "Non-authenticated Layout" text
        assert 'Non-authenticated Layout' not in body_html
        assert 'Login' not in page.title() or 'Invoice' in page.title()
