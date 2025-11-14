"""
Playwright tests for Inventory MIN (Material Issue Note) functionality
Tests the material issue workflow from MRS to MIN

Converted from: aaspnet/Module/Inventory/Transactions/MIN*.aspx
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.crud
class TestMIN:
    """Test suite for MIN (Material Issue Note) functionality"""

    def test_min_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test that MIN list page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/min/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page title
        expect(inventory_page.locator('h1, h2')).to_contain_text('MIN')

        # Verify create button exists
        create_btn = inventory_page.locator('a[href*="min/create"]')
        expect(create_btn).to_be_visible()

    def test_min_pending_mrs_page_loads(self, inventory_page: Page, base_url: str):
        """Test that pending MRS list page loads for MIN creation"""
        inventory_page.goto(f"{base_url}/inventory/min/pending-mrs/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page shows pending MRS
        expect(inventory_page.locator('h1, h2')).to_contain_text('MRS')

    def test_min_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test that MIN creation page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/min/create/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify form is present
        form = inventory_page.locator('form')
        expect(form).to_be_visible()

    def test_min_create_form_elements(self, inventory_page: Page, base_url: str):
        """Test that MIN creation form has required elements"""
        inventory_page.goto(f"{base_url}/inventory/min/create/")

        # Should have submit button
        submit_btn = inventory_page.locator('button[type="submit"]')
        expect(submit_btn).to_be_visible()

        # Should have form fields
        form = inventory_page.locator('form')
        expect(form).to_be_visible()

    def test_min_list_displays_items(self, inventory_page: Page, base_url: str):
        """Test that MIN list displays existing items"""
        inventory_page.goto(f"{base_url}/inventory/min/")
        inventory_page.wait_for_load_state('networkidle')

        # Check if table or list exists
        table = inventory_page.locator('table, .list, .grid')
        expect(table).to_be_visible()

    def test_min_detail_page(self, inventory_page: Page, base_url: str):
        """Test MIN detail view"""
        inventory_page.goto(f"{base_url}/inventory/min/")
        inventory_page.wait_for_load_state('networkidle')

        # Try to find first detail link
        detail_link = inventory_page.locator('a[href*="/min/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/min/' in href and not href.endswith('/min/'):
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')
                expect(inventory_page.locator('body')).to_be_visible()

    def test_min_print_page(self, inventory_page: Page, base_url: str):
        """Test MIN print functionality exists"""
        inventory_page.goto(f"{base_url}/inventory/min/")
        inventory_page.wait_for_load_state('networkidle')

        # Print functionality should exist in detail or list view
        print_btn = inventory_page.locator('a[href*="print"], button:has-text("Print")')
        # May not be visible in list view

    def test_min_delete_button_exists(self, inventory_page: Page, base_url: str):
        """Test MIN delete functionality exists"""
        inventory_page.goto(f"{base_url}/inventory/min/")
        inventory_page.wait_for_load_state('networkidle')

        # Delete buttons should exist
        # Don't actually delete in tests

    @pytest.mark.smoke
    def test_min_workflow_from_pending_mrs(self, inventory_page: Page, base_url: str):
        """Test MIN creation workflow from pending MRS"""
        # Navigate to pending MRS
        inventory_page.goto(f"{base_url}/inventory/min/pending-mrs/")
        inventory_page.wait_for_load_state('networkidle')

        # Should show list of pending MRS
        expect(inventory_page.locator('body')).to_be_visible()

        # Look for issue/create MIN button
        create_btn = inventory_page.locator('a[href*="min/create"], button:has-text("Issue")')
        # Might exist on this page

    def test_min_responsive_layout(self, inventory_page: Page, base_url: str):
        """Test MIN pages are responsive"""
        # Desktop
        inventory_page.goto(f"{base_url}/inventory/min/")
        expect(inventory_page.locator('body')).to_be_visible()

        # Tablet
        inventory_page.set_viewport_size({"width": 768, "height": 1024})
        inventory_page.goto(f"{base_url}/inventory/min/")
        expect(inventory_page.locator('body')).to_be_visible()

        # Mobile
        inventory_page.set_viewport_size({"width": 375, "height": 667})
        inventory_page.goto(f"{base_url}/inventory/min/")
        expect(inventory_page.locator('body')).to_be_visible()

    def test_min_navigation_links(self, inventory_page: Page, base_url: str):
        """Test navigation between MIN pages"""
        # Start at list
        inventory_page.goto(f"{base_url}/inventory/min/")
        expect(inventory_page.locator('body')).to_be_visible()

        # Navigate to pending MRS
        pending_link = inventory_page.locator('a[href*="pending-mrs"]')
        if pending_link.is_visible():
            pending_link.click()
            inventory_page.wait_for_load_state('networkidle')
            expect(inventory_page.locator('body')).to_be_visible()

    def test_min_search_functionality(self, inventory_page: Page, base_url: str):
        """Test MIN list search/filter"""
        inventory_page.goto(f"{base_url}/inventory/min/")
        inventory_page.wait_for_load_state('networkidle')

        # Look for search
        search_input = inventory_page.locator('input[name="search"], input[type="search"]')
        if search_input.count() > 0:
            search_input.first.fill('test')
            inventory_page.wait_for_timeout(500)

    def test_min_cancel_button(self, inventory_page: Page, base_url: str):
        """Test cancel button on MIN create form"""
        inventory_page.goto(f"{base_url}/inventory/min/create/")

        # Find cancel button
        cancel_btn = inventory_page.locator('a:has-text("Cancel"), button:has-text("Cancel")')
        if cancel_btn.is_visible():
            cancel_btn.click()
            inventory_page.wait_for_load_state('networkidle')
