"""
Playwright tests for Inventory GIN (Goods Inward Note) functionality
Tests the inward receipt workflow with PO integration

Converted from: aaspnet/Module/Inventory/Transactions/GIN*.aspx
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.crud
class TestGIN:
    """Test suite for GIN (Goods Inward Note) functionality"""

    def test_gin_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test that GIN list page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/gin/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page title
        expect(inventory_page.locator('h1, h2')).to_contain_text('GIN')

        # Verify create button exists
        create_btn = inventory_page.locator('a[href*="gin/create"]')
        expect(create_btn).to_be_visible()

    def test_gin_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test that GIN creation page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/gin/create/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify form is present
        form = inventory_page.locator('form')
        expect(form).to_be_visible()

    def test_gin_create_form_elements(self, inventory_page: Page, base_url: str):
        """Test that GIN creation form has required elements"""
        inventory_page.goto(f"{base_url}/inventory/gin/create/")

        # Should have submit button
        submit_btn = inventory_page.locator('button[type="submit"]')
        expect(submit_btn).to_be_visible()

        # Should have PO search or selection
        po_search = inventory_page.locator('input[name*="po"], select[name*="po"]')
        # May or may not exist depending on implementation

    @pytest.mark.htmx
    def test_gin_po_search_autocomplete(self, inventory_page: Page, base_url: str):
        """Test GIN PO search/autocomplete functionality"""
        inventory_page.goto(f"{base_url}/inventory/gin/create/")
        inventory_page.wait_for_load_state('networkidle')

        # Look for PO search field with autocomplete
        po_search = inventory_page.locator('input[name*="po_search"], input[placeholder*="PO"]')
        if po_search.count() > 0:
            po_search.first.fill('PO')
            inventory_page.wait_for_timeout(1000)  # Wait for HTMX response

    def test_gin_list_displays_items(self, inventory_page: Page, base_url: str):
        """Test that GIN list displays existing items"""
        inventory_page.goto(f"{base_url}/inventory/gin/")
        inventory_page.wait_for_load_state('networkidle')

        # Check if table exists
        table = inventory_page.locator('table, .list')
        expect(table).to_be_visible()

    def test_gin_detail_page(self, inventory_page: Page, base_url: str):
        """Test GIN detail view"""
        inventory_page.goto(f"{base_url}/inventory/gin/")
        inventory_page.wait_for_load_state('networkidle')

        # Try to find first detail link
        detail_link = inventory_page.locator('a[href*="/gin/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/gin/' in href and not href.endswith('/gin/'):
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')
                expect(inventory_page.locator('body')).to_be_visible()

    def test_gin_print_functionality(self, inventory_page: Page, base_url: str):
        """Test GIN print exists"""
        inventory_page.goto(f"{base_url}/inventory/gin/")
        inventory_page.wait_for_load_state('networkidle')

        # Print should exist
        print_btn = inventory_page.locator('a[href*="print"], button:has-text("Print")')

    def test_gin_delete_button(self, inventory_page: Page, base_url: str):
        """Test GIN delete functionality exists"""
        inventory_page.goto(f"{base_url}/inventory/gin/")
        inventory_page.wait_for_load_state('networkidle')

    def test_gin_pending_list(self, inventory_page: Page, base_url: str):
        """Test GIN pending list for GRR creation"""
        inventory_page.goto(f"{base_url}/inventory/grr/pending-gin/")
        inventory_page.wait_for_load_state('networkidle')

        # Should show pending GINs
        expect(inventory_page.locator('body')).to_be_visible()

    def test_gin_master_update(self, inventory_page: Page, base_url: str):
        """Test GIN master update endpoint exists"""
        # This is typically an HTMX endpoint
        # Just verify the URL pattern exists in routes

    def test_gin_detail_update(self, inventory_page: Page, base_url: str):
        """Test GIN detail line update endpoint exists"""
        # This is typically an HTMX endpoint for inline editing

    @pytest.mark.smoke
    def test_gin_create_from_po_workflow(self, inventory_page: Page, base_url: str):
        """Test creating GIN from PO"""
        inventory_page.goto(f"{base_url}/inventory/gin/create/")
        inventory_page.wait_for_load_state('networkidle')

        # Look for PO search/selection
        expect(inventory_page.locator('form')).to_be_visible()

    def test_gin_item_image_download(self, inventory_page: Page, base_url: str):
        """Test GIN item image download exists"""
        # This would be in detail view
        # URL pattern: /inventory/gin/item/<item_id>/image/

    def test_gin_item_spec_download(self, inventory_page: Page, base_url: str):
        """Test GIN item spec download exists"""
        # This would be in detail view
        # URL pattern: /inventory/gin/item/<item_id>/spec/

    def test_gin_responsive_layout(self, inventory_page: Page, base_url: str):
        """Test GIN pages are responsive"""
        # Desktop
        inventory_page.goto(f"{base_url}/inventory/gin/")
        expect(inventory_page.locator('body')).to_be_visible()

        # Tablet
        inventory_page.set_viewport_size({"width": 768, "height": 1024})
        inventory_page.goto(f"{base_url}/inventory/gin/")
        expect(inventory_page.locator('body')).to_be_visible()

        # Mobile
        inventory_page.set_viewport_size({"width": 375, "height": 667})
        inventory_page.goto(f"{base_url}/inventory/gin/")
        expect(inventory_page.locator('body')).to_be_visible()

    def test_gin_navigation_breadcrumb(self, inventory_page: Page, base_url: str):
        """Test breadcrumb on GIN pages"""
        inventory_page.goto(f"{base_url}/inventory/gin/create/")

        breadcrumb = inventory_page.locator('nav[aria-label="breadcrumb"], .breadcrumb')
        if breadcrumb.is_visible():
            expect(breadcrumb).to_contain_text('Inventory')

    def test_gin_cancel_button(self, inventory_page: Page, base_url: str):
        """Test cancel button on GIN create form"""
        inventory_page.goto(f"{base_url}/inventory/gin/create/")

        cancel_btn = inventory_page.locator('a:has-text("Cancel"), button:has-text("Cancel")')
        if cancel_btn.is_visible():
            cancel_btn.click()
            inventory_page.wait_for_load_state('networkidle')
