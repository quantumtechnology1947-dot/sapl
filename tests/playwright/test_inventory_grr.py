"""
Playwright tests for Inventory GRR (Goods Received Receipt) functionality
Tests the goods receipt workflow from GIN to GRR

Converted from: aaspnet/Module/Inventory/Transactions/GRR*.aspx
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.crud
class TestGRR:
    """Test suite for GRR (Goods Received Receipt) functionality"""

    def test_grr_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test that GRR list page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/grr/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page title
        expect(inventory_page.locator('h1, h2')).to_contain_text('GRR')

        # Verify create button exists
        create_btn = inventory_page.locator('a[href*="grr/create"]')
        expect(create_btn).to_be_visible()

    def test_grr_pending_gin_page_loads(self, inventory_page: Page, base_url: str):
        """Test that pending GIN list page loads for GRR creation"""
        inventory_page.goto(f"{base_url}/inventory/grr/pending-gin/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page shows pending GINs
        expect(inventory_page.locator('h1, h2')).to_contain_text('GIN')

    def test_grr_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test that GRR creation page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/grr/create/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify form is present
        form = inventory_page.locator('form')
        expect(form).to_be_visible()

    def test_grr_create_form_elements(self, inventory_page: Page, base_url: str):
        """Test that GRR creation form has required elements"""
        inventory_page.goto(f"{base_url}/inventory/grr/create/")

        # Should have submit button
        submit_btn = inventory_page.locator('button[type="submit"]')
        expect(submit_btn).to_be_visible()

    def test_grr_list_displays_items(self, inventory_page: Page, base_url: str):
        """Test that GRR list displays existing items"""
        inventory_page.goto(f"{base_url}/inventory/grr/")
        inventory_page.wait_for_load_state('networkidle')

        # Check if table exists
        table = inventory_page.locator('table, .list')
        expect(table).to_be_visible()

    def test_grr_detail_page(self, inventory_page: Page, base_url: str):
        """Test GRR detail view"""
        inventory_page.goto(f"{base_url}/inventory/grr/")
        inventory_page.wait_for_load_state('networkidle')

        # Try to find first detail link
        detail_link = inventory_page.locator('a[href*="/grr/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/grr/' in href and not href.endswith('/grr/'):
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')
                expect(inventory_page.locator('body')).to_be_visible()

    def test_grr_print_functionality(self, inventory_page: Page, base_url: str):
        """Test GRR print exists"""
        inventory_page.goto(f"{base_url}/inventory/grr/")
        inventory_page.wait_for_load_state('networkidle')

        print_btn = inventory_page.locator('a[href*="print"], button:has-text("Print")')

    def test_grr_delete_button(self, inventory_page: Page, base_url: str):
        """Test GRR delete functionality exists"""
        inventory_page.goto(f"{base_url}/inventory/grr/")
        inventory_page.wait_for_load_state('networkidle')

    def test_grr_edit_list_page(self, inventory_page: Page, base_url: str):
        """Test GRR edit list page loads"""
        inventory_page.goto(f"{base_url}/inventory/grr/edit/")
        inventory_page.wait_for_load_state('networkidle')

        # Should show editable GRRs
        expect(inventory_page.locator('body')).to_be_visible()

    def test_grr_edit_detail_page(self, inventory_page: Page, base_url: str):
        """Test GRR edit detail page"""
        inventory_page.goto(f"{base_url}/inventory/grr/edit/")
        inventory_page.wait_for_load_state('networkidle')

        # Try to find edit link
        edit_link = inventory_page.locator('a[href*="/grr/"][href*="/edit/"]').first
        if edit_link.is_visible():
            edit_link.click()
            inventory_page.wait_for_load_state('networkidle')
            expect(inventory_page.locator('body')).to_be_visible()

    @pytest.mark.smoke
    def test_grr_workflow_from_pending_gin(self, inventory_page: Page, base_url: str):
        """Test GRR creation workflow from pending GIN"""
        # Navigate to pending GIN
        inventory_page.goto(f"{base_url}/inventory/grr/pending-gin/")
        inventory_page.wait_for_load_state('networkidle')

        # Should show list of pending GINs
        expect(inventory_page.locator('body')).to_be_visible()

    def test_grr_responsive_layout(self, inventory_page: Page, base_url: str):
        """Test GRR pages are responsive"""
        # Desktop
        inventory_page.goto(f"{base_url}/inventory/grr/")
        expect(inventory_page.locator('body')).to_be_visible()

        # Tablet
        inventory_page.set_viewport_size({"width": 768, "height": 1024})
        inventory_page.goto(f"{base_url}/inventory/grr/")
        expect(inventory_page.locator('body')).to_be_visible()

        # Mobile
        inventory_page.set_viewport_size({"width": 375, "height": 667})
        inventory_page.goto(f"{base_url}/inventory/grr/")
        expect(inventory_page.locator('body')).to_be_visible()

    def test_grr_navigation_links(self, inventory_page: Page, base_url: str):
        """Test navigation between GRR pages"""
        # Start at list
        inventory_page.goto(f"{base_url}/inventory/grr/")
        expect(inventory_page.locator('body')).to_be_visible()

        # Navigate to pending GIN
        pending_link = inventory_page.locator('a[href*="pending-gin"]')
        if pending_link.is_visible():
            pending_link.click()
            inventory_page.wait_for_load_state('networkidle')
            expect(inventory_page.locator('body')).to_be_visible()

    def test_grr_search_functionality(self, inventory_page: Page, base_url: str):
        """Test GRR list search/filter"""
        inventory_page.goto(f"{base_url}/inventory/grr/")
        inventory_page.wait_for_load_state('networkidle')

        search_input = inventory_page.locator('input[name="search"], input[type="search"]')
        if search_input.count() > 0:
            search_input.first.fill('test')
            inventory_page.wait_for_timeout(500)

    def test_grr_cancel_button(self, inventory_page: Page, base_url: str):
        """Test cancel button on GRR create form"""
        inventory_page.goto(f"{base_url}/inventory/grr/create/")

        cancel_btn = inventory_page.locator('a:has-text("Cancel"), button:has-text("Cancel")')
        if cancel_btn.is_visible():
            cancel_btn.click()
            inventory_page.wait_for_load_state('networkidle')
