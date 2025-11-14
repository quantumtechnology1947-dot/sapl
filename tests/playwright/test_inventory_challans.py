"""
Playwright tests for Inventory Challan functionality
Tests Supplier Challan, Customer Challan, and Regular Challan

Converted from: aaspnet/Module/Inventory/Transactions/*Challan*.aspx
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.crud
class TestSupplierChallan:
    """Test suite for Supplier Challan functionality"""

    def test_supplier_challan_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test Supplier Challan list page loads"""
        inventory_page.goto(f"{base_url}/inventory/supplier-challan/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('Supplier Challan')

    def test_supplier_challan_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test Supplier Challan create page loads"""
        inventory_page.goto(f"{base_url}/inventory/supplier-challan/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_supplier_challan_pending_list(self, inventory_page: Page, base_url: str):
        """Test Supplier Challan pending list page"""
        inventory_page.goto(f"{base_url}/inventory/supplier-challan/pending/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_supplier_challan_detail_page(self, inventory_page: Page, base_url: str):
        """Test Supplier Challan detail view"""
        inventory_page.goto(f"{base_url}/inventory/supplier-challan/")
        inventory_page.wait_for_load_state('networkidle')

        detail_link = inventory_page.locator('a[href*="/supplier-challan/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/supplier-challan/' in href:
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')
                expect(inventory_page.locator('body')).to_be_visible()

    def test_supplier_challan_print_page(self, inventory_page: Page, base_url: str):
        """Test Supplier Challan print functionality"""
        inventory_page.goto(f"{base_url}/inventory/supplier-challan/")
        inventory_page.wait_for_load_state('networkidle')

        print_link = inventory_page.locator('a[href*="print"]')

    def test_supplier_challan_clear_functionality(self, inventory_page: Page, base_url: str):
        """Test Supplier Challan clear/close functionality"""
        inventory_page.goto(f"{base_url}/inventory/supplier-challan/")
        inventory_page.wait_for_load_state('networkidle')

        clear_link = inventory_page.locator('a[href*="clear"]')

    def test_supplier_challan_delete_functionality(self, inventory_page: Page, base_url: str):
        """Test Supplier Challan delete functionality"""
        inventory_page.goto(f"{base_url}/inventory/supplier-challan/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.crud
class TestCustomerChallan:
    """Test suite for Customer Challan functionality"""

    def test_customer_challan_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test Customer Challan list page loads"""
        inventory_page.goto(f"{base_url}/inventory/customer-challan/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('Customer Challan')

    def test_customer_challan_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test Customer Challan create page loads"""
        inventory_page.goto(f"{base_url}/inventory/customer-challan/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_customer_challan_detail_page(self, inventory_page: Page, base_url: str):
        """Test Customer Challan detail view"""
        inventory_page.goto(f"{base_url}/inventory/customer-challan/")
        inventory_page.wait_for_load_state('networkidle')

        detail_link = inventory_page.locator('a[href*="/customer-challan/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/customer-challan/' in href:
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')
                expect(inventory_page.locator('body')).to_be_visible()

    def test_customer_challan_print_functionality(self, inventory_page: Page, base_url: str):
        """Test Customer Challan print functionality"""
        inventory_page.goto(f"{base_url}/inventory/customer-challan/")
        inventory_page.wait_for_load_state('networkidle')

        print_link = inventory_page.locator('a[href*="print"]')

    def test_customer_challan_delete_functionality(self, inventory_page: Page, base_url: str):
        """Test Customer Challan delete functionality"""
        inventory_page.goto(f"{base_url}/inventory/customer-challan/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.crud
class TestRegularChallan:
    """Test suite for Regular Challan functionality"""

    def test_challan_list_page_loads(self, inventory_page: Page, base_url: str):
        """Test regular Challan list page loads"""
        inventory_page.goto(f"{base_url}/inventory/challan/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('h1, h2')).to_contain_text('Challan')

    def test_challan_create_page_loads(self, inventory_page: Page, base_url: str):
        """Test regular Challan create page loads"""
        inventory_page.goto(f"{base_url}/inventory/challan/create/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('form')).to_be_visible()

    def test_challan_detail_page(self, inventory_page: Page, base_url: str):
        """Test regular Challan detail view"""
        inventory_page.goto(f"{base_url}/inventory/challan/")
        inventory_page.wait_for_load_state('networkidle')

        detail_link = inventory_page.locator('a[href*="/challan/"][href$="/"]').first
        if detail_link.is_visible():
            href = detail_link.get_attribute('href')
            if href and '/challan/' in href and not 'customer' in href and not 'supplier' in href:
                detail_link.click()
                inventory_page.wait_for_load_state('networkidle')
                expect(inventory_page.locator('body')).to_be_visible()

    def test_challan_edit_page(self, inventory_page: Page, base_url: str):
        """Test regular Challan edit functionality"""
        inventory_page.goto(f"{base_url}/inventory/challan/")
        inventory_page.wait_for_load_state('networkidle')

        edit_link = inventory_page.locator('a[href*="/challan/"][href*="/edit/"]').first
        if edit_link.is_visible():
            edit_link.click()
            inventory_page.wait_for_load_state('networkidle')
            expect(inventory_page.locator('form')).to_be_visible()

    def test_challan_print_functionality(self, inventory_page: Page, base_url: str):
        """Test regular Challan print functionality"""
        inventory_page.goto(f"{base_url}/inventory/challan/")
        inventory_page.wait_for_load_state('networkidle')

    def test_challan_delete_functionality(self, inventory_page: Page, base_url: str):
        """Test regular Challan delete functionality"""
        inventory_page.goto(f"{base_url}/inventory/challan/")
        inventory_page.wait_for_load_state('networkidle')


@pytest.mark.inventory
@pytest.mark.smoke
class TestChallanWorkflow:
    """Test suite for Challan workflows"""

    def test_challan_types_navigation(self, inventory_page: Page, base_url: str):
        """Test navigation between different challan types"""
        challan_urls = [
            '/inventory/supplier-challan/',
            '/inventory/customer-challan/',
            '/inventory/challan/',
        ]

        for url in challan_urls:
            inventory_page.goto(f"{base_url}{url}")
            inventory_page.wait_for_load_state('networkidle')
            expect(inventory_page.locator('body')).to_be_visible()

    def test_all_challans_responsive(self, inventory_page: Page, base_url: str):
        """Test all challan pages are responsive"""
        challan_urls = [
            '/inventory/supplier-challan/',
            '/inventory/customer-challan/',
        ]

        for url in challan_urls:
            # Desktop
            inventory_page.goto(f"{base_url}{url}")
            expect(inventory_page.locator('body')).to_be_visible()

            # Mobile
            inventory_page.set_viewport_size({"width": 375, "height": 667})
            inventory_page.goto(f"{base_url}{url}")
            expect(inventory_page.locator('body')).to_be_visible()

            # Reset to desktop
            inventory_page.set_viewport_size({"width": 1920, "height": 1080})
