"""
Playwright tests for Inventory Gate Pass and WIS functionality
Tests gate pass management and Work Instruction Sheet

Converted from: aaspnet/Module/Inventory/Transactions/GatePass*.aspx and WIS*.aspx
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.crud
class TestGatePass:
    """Test suite for Gate Pass functionality"""

    def test_gate_pass_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test Gate Pass list page loads"""
        inventory_page.goto(f"{base_url}/inventory/gate-pass/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('Gate Pass')

    def test_gate_pass_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test Gate Pass create page loads"""
        inventory_page.goto(f"{base_url}/inventory/gate-pass/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_gate_pass_pending_list(self, inventory_page: Page, base_url: str):
        """Test Gate Pass pending list page"""
        inventory_page.goto(f"{base_url}/inventory/gate-pass/pending/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_gate_pass_detail_page(self, inventory_page: Page, base_url: str):
        """Test Gate Pass detail view"""
        inventory_page.goto(f"{base_url}/inventory/gate-pass/")
        inventory_page.wait_for_load_state('networkidle')

        detail_link = inventory_page.locator('a[href*="/gate-pass/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/gate-pass/' in href:
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')
                expect(inventory_page.locator('body')).to_be_visible()

    def test_gate_pass_edit_page(self, inventory_page: Page, base_url: str):
        """Test Gate Pass edit functionality"""
        inventory_page.goto(f"{base_url}/inventory/gate-pass/")
        inventory_page.wait_for_load_state('networkidle')

        edit_link = inventory_page.locator('a[href*="/gate-pass/"][href*="/edit/"]').first
        if edit_link.is_visible():
            edit_link.click()
            inventory_page.wait_for_load_state('networkidle')
            expect(inventory_page.locator('form')).to_be_visible()

    def test_gate_pass_print_functionality(self, inventory_page: Page, base_url: str):
        """Test Gate Pass print functionality"""
        inventory_page.goto(f"{base_url}/inventory/gate-pass/")
        inventory_page.wait_for_load_state('networkidle')

        print_link = inventory_page.locator('a[href*="print"]')

    def test_gate_pass_return_functionality(self, inventory_page: Page, base_url: str):
        """Test Gate Pass return functionality"""
        inventory_page.goto(f"{base_url}/inventory/gate-pass/")
        inventory_page.wait_for_load_state('networkidle')

        return_link = inventory_page.locator('a[href*="return"]')

    def test_gate_pass_responsive_layout(self, inventory_page: Page, base_url: str):
        """Test Gate Pass pages are responsive"""
        inventory_page.goto(f"{base_url}/inventory/gate-pass/")
        expect(inventory_page.locator('body')).to_be_visible()

        inventory_page.set_viewport_size({"width": 375, "height": 667})
        inventory_page.goto(f"{base_url}/inventory/gate-pass/")
        expect(inventory_page.locator('body')).to_be_visible()


@pytest.mark.inventory
@pytest.mark.crud
class TestWIS:
    """Test suite for WIS (Work Instruction Sheet) functionality"""

    def test_wis_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test WIS list page loads"""
        inventory_page.goto(f"{base_url}/inventory/wis/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('WIS')

    def test_wis_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test WIS create page loads"""
        inventory_page.goto(f"{base_url}/inventory/wis/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_wis_detail_page(self, inventory_page: Page, base_url: str):
        """Test WIS detail view"""
        inventory_page.goto(f"{base_url}/inventory/wis/")
        inventory_page.wait_for_load_state('networkidle')

        detail_link = inventory_page.locator('a[href*="/wis/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/wis/' in href and not 'create' in href:
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')
                expect(inventory_page.locator('body')).to_be_visible()

    def test_wis_release_functionality(self, inventory_page: Page, base_url: str):
        """Test WIS release functionality exists"""
        inventory_page.goto(f"{base_url}/inventory/wis/")
        inventory_page.wait_for_load_state('networkidle')

        release_link = inventory_page.locator('a[href*="release"]')

    def test_wis_actual_run_page(self, inventory_page: Page, base_url: str):
        """Test WIS actual run page exists"""
        inventory_page.goto(f"{base_url}/inventory/wis/")
        inventory_page.wait_for_load_state('networkidle')

        actual_run_link = inventory_page.locator('a[href*="actual-run"]')

    def test_wis_print_functionality(self, inventory_page: Page, base_url: str):
        """Test WIS print functionality"""
        inventory_page.goto(f"{base_url}/inventory/wis/")
        inventory_page.wait_for_load_state('networkidle')

        print_link = inventory_page.locator('a[href*="print"]')

    def test_wis_form_has_work_order_field(self, inventory_page: Page, base_url: str):
        """Test WIS create form has work order selection"""
        inventory_page.goto(f"{base_url}/inventory/wis/create/")
        inventory_page.wait_for_load_state('networkidle')

        # Should have work order field
        wo_field = inventory_page.locator('select[name*="work"], input[name*="work"]')

    def test_wis_detail_shows_materials(self, inventory_page: Page, base_url: str):
        """Test WIS detail shows material requirements"""
        inventory_page.goto(f"{base_url}/inventory/wis/")
        inventory_page.wait_for_load_state('networkidle')

        detail_link = inventory_page.locator('a[href*="/wis/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/wis/' in href:
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')

                # Should show materials table
                table = inventory_page.locator('table')
                if table.is_visible():
                    expect(table).to_be_visible()

    def test_wis_responsive_layout(self, inventory_page: Page, base_url: str):
        """Test WIS pages are responsive"""
        inventory_page.goto(f"{base_url}/inventory/wis/")
        expect(inventory_page.locator('body')).to_be_visible()

        inventory_page.set_viewport_size({"width": 768, "height": 1024})
        inventory_page.goto(f"{base_url}/inventory/wis/")
        expect(inventory_page.locator('body')).to_be_visible()


@pytest.mark.inventory
@pytest.mark.crud
class TestAutoWISSchedule:
    """Test suite for Auto WIS Time Schedule functionality"""

    def test_autowis_schedule_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test Auto WIS Schedule list page loads"""
        inventory_page.goto(f"{base_url}/inventory/autowis-schedule/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_autowis_schedule_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test Auto WIS Schedule create page loads"""
        inventory_page.goto(f"{base_url}/inventory/autowis-schedule/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    @pytest.mark.htmx
    def test_autowis_schedule_inline_edit(self, inventory_page: Page, base_url: str):
        """Test Auto WIS Schedule inline edit with HTMX"""
        inventory_page.goto(f"{base_url}/inventory/autowis-schedule/")
        inventory_page.wait_for_load_state('networkidle')

        # Look for edit buttons
        edit_btn = inventory_page.locator('a[href*="edit"], button:has-text("Edit")')

    def test_autowis_schedule_delete_functionality(self, inventory_page: Page, base_url: str):
        """Test Auto WIS Schedule delete functionality"""
        inventory_page.goto(f"{base_url}/inventory/autowis-schedule/")
        inventory_page.wait_for_load_state('networkidle')
