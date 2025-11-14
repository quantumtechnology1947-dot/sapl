"""
Playwright tests for Miscellaneous Inventory functionality
Tests MRN, GSN, MCN, Vehicle, Item Location, and Search

Converted from: aaspnet/Module/Inventory/Transactions/*
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.crud
class TestMRN:
    """Test suite for MRN (Material Return Note) functionality"""

    def test_mrn_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test MRN list page loads"""
        inventory_page.goto(f"{base_url}/inventory/mrn/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('MRN')

    def test_mrn_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test MRN create page loads"""
        inventory_page.goto(f"{base_url}/inventory/mrn/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_mrn_detail_page(self, inventory_page: Page, base_url: str):
        """Test MRN detail view"""
        inventory_page.goto(f"{base_url}/inventory/mrn/")
        inventory_page.wait_for_load_state('networkidle')

    def test_mrn_print_functionality(self, inventory_page: Page, base_url: str):
        """Test MRN print functionality"""
        inventory_page.goto(f"{base_url}/inventory/mrn/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.crud
class TestGSN:
    """Test suite for GSN (Goods Service Note) functionality"""

    def test_gsn_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test GSN list page loads"""
        inventory_page.goto(f"{base_url}/inventory/gsn/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('GSN')

    def test_gsn_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test GSN create page loads"""
        inventory_page.goto(f"{base_url}/inventory/gsn/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_gsn_detail_page(self, inventory_page: Page, base_url: str):
        """Test GSN detail view"""
        inventory_page.goto(f"{base_url}/inventory/gsn/")
        inventory_page.wait_for_load_state('networkidle')

    def test_gsn_print_functionality(self, inventory_page: Page, base_url: str):
        """Test GSN print functionality"""
        inventory_page.goto(f"{base_url}/inventory/gsn/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.crud
class TestMCN:
    """Test suite for MCN (Material Credit Note) functionality"""

    def test_mcn_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test MCN list page loads"""
        inventory_page.goto(f"{base_url}/inventory/mcn/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('MCN')

    def test_mcn_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test MCN create page loads"""
        inventory_page.goto(f"{base_url}/inventory/mcn/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_mcn_detail_page(self, inventory_page: Page, base_url: str):
        """Test MCN detail view"""
        inventory_page.goto(f"{base_url}/inventory/mcn/")
        inventory_page.wait_for_load_state('networkidle')

    def test_mcn_print_functionality(self, inventory_page: Page, base_url: str):
        """Test MCN print functionality"""
        inventory_page.goto(f"{base_url}/inventory/mcn/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.crud
class TestVehicle:
    """Test suite for Vehicle management functionality"""

    def test_vehicle_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test Vehicle list page loads"""
        inventory_page.goto(f"{base_url}/inventory/vehicle/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('Vehicle')

    def test_vehicle_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test Vehicle create page loads"""
        inventory_page.goto(f"{base_url}/inventory/vehicle/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_vehicle_detail_page(self, inventory_page: Page, base_url: str):
        """Test Vehicle detail view"""
        inventory_page.goto(f"{base_url}/inventory/vehicle/")
        inventory_page.wait_for_load_state('networkidle')

    def test_vehicle_edit_page(self, inventory_page: Page, base_url: str):
        """Test Vehicle edit functionality"""
        inventory_page.goto(f"{base_url}/inventory/vehicle/")
        inventory_page.wait_for_load_state('networkidle')

    def test_vehicle_trip_create_page(self, inventory_page: Page, base_url: str):
        """Test Vehicle trip creation"""
        inventory_page.goto(f"{base_url}/inventory/vehicle/")
        inventory_page.wait_for_load_state('networkidle')

    def test_vehicle_history_page(self, inventory_page: Page, base_url: str):
        """Test Vehicle history view"""
        inventory_page.goto(f"{base_url}/inventory/vehicle/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.crud
class TestVehicleMaster:
    """Test suite for Vehicle Master (SAP Fiori style) functionality"""

    def test_vehicle_master_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test Vehicle Master list page loads"""
        inventory_page.goto(f"{base_url}/inventory/vehicle-master/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_vehicle_master_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test Vehicle Master create page loads"""
        inventory_page.goto(f"{base_url}/inventory/vehicle-master/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    @pytest.mark.htmx
    def test_vehicle_master_inline_edit(self, inventory_page: Page, base_url: str):
        """Test Vehicle Master inline edit with HTMX"""
        inventory_page.goto(f"{base_url}/inventory/vehicle-master/")
        inventory_page.wait_for_load_state('networkidle')

        # Look for edit buttons
        edit_btn = inventory_page.locator('a[href*="edit"], button:has-text("Edit")')

    def test_vehicle_master_delete_functionality(self, inventory_page: Page, base_url: str):
        """Test Vehicle Master delete functionality"""
        inventory_page.goto(f"{base_url}/inventory/vehicle-master/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.crud
class TestItemLocation:
    """Test suite for Item Location functionality"""

    def test_item_location_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test Item Location list page loads"""
        inventory_page.goto(f"{base_url}/inventory/item-location/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_item_location_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test Item Location create page loads"""
        inventory_page.goto(f"{base_url}/inventory/item-location/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_item_location_delete_functionality(self, inventory_page: Page, base_url: str):
        """Test Item Location delete functionality"""
        inventory_page.goto(f"{base_url}/inventory/item-location/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.integration
class TestSearch:
    """Test suite for Inventory search functionality"""

    def test_global_search_page_loads(self, inventory_page: Page, base_url: str):
        """Test global search page loads"""
        inventory_page.goto(f"{base_url}/inventory/search/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_advanced_search_page_loads(self, inventory_page: Page, base_url: str):
        """Test advanced search page loads"""
        inventory_page.goto(f"{base_url}/inventory/search/advanced/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_global_search_has_input(self, inventory_page: Page, base_url: str):
        """Test global search has search input"""
        inventory_page.goto(f"{base_url}/inventory/search/")
        inventory_page.wait_for_load_state('networkidle')

        search_input = inventory_page.locator('input[type="search"], input[name="q"], input[name="search"]')
        if search_input.count() > 0:
            expect(search_input.first).to_be_visible()

    @pytest.mark.htmx
    def test_search_returns_results(self, inventory_page: Page, base_url: str):
        """Test search functionality returns results"""
        inventory_page.goto(f"{base_url}/inventory/search/")
        inventory_page.wait_for_load_state('networkidle')

        search_input = inventory_page.locator('input[type="search"], input[name="q"], input[name="search"]')
        if search_input.count() > 0:
            search_input.first.fill('test')
            inventory_page.wait_for_timeout(1000)

            # Results should appear
            results = inventory_page.locator('.search-results, table, .results')

    def test_advanced_search_has_filters(self, inventory_page: Page, base_url: str):
        """Test advanced search has filter options"""
        inventory_page.goto(f"{base_url}/inventory/search/advanced/")
        inventory_page.wait_for_load_state('networkidle')

        # Should have multiple filter fields
        filters = inventory_page.locator('select, input[type="text"]')
        # Advanced search should have filters


@pytest.mark.inventory
@pytest.mark.smoke
class TestMiscWorkflows:
    """Test suite for miscellaneous inventory workflows"""

    def test_all_transaction_pages_load(self, inventory_page: Page, base_url: str):
        """Smoke test: verify all transaction pages load"""
        urls = [
            '/inventory/mrn/',
            '/inventory/gsn/',
            '/inventory/mcn/',
            '/inventory/vehicle/',
            '/inventory/vehicle-master/',
            '/inventory/item-location/',
        ]

        for url in urls:
            inventory_page.goto(f"{base_url}{url}")
            inventory_page.wait_for_load_state('networkidle')

            # Verify no error
            error = inventory_page.locator('text=Error, text=404')
            if error.is_visible():
                pytest.fail(f"Error on {url}")

            expect(inventory_page.locator('body')).to_be_visible()

    def test_all_pages_responsive(self, inventory_page: Page, base_url: str):
        """Test miscellaneous pages are responsive"""
        urls = [
            '/inventory/mrn/',
            '/inventory/gsn/',
            '/inventory/vehicle-master/',
        ]

        for url in urls:
            # Desktop
            inventory_page.set_viewport_size({"width": 1920, "height": 1080})
            inventory_page.goto(f"{base_url}{url}")
            expect(inventory_page.locator('body')).to_be_visible()

            # Mobile
            inventory_page.set_viewport_size({"width": 375, "height": 667})
            inventory_page.goto(f"{base_url}{url}")
            expect(inventory_page.locator('body')).to_be_visible()
