"""
Test Suite for Sales Invoice Cascading Dropdowns

Tests the Country → State → City cascading dropdown functionality for both
Buyer and Consignee tabs in the Sales Invoice module.

From sales_invoice.md:
- Lines 113-120: Buyer tab fields with cascading Country/State/City
- Lines 280-448: JavaScript implementation of cascading dropdowns
- Lines 719-758: Django view endpoints for state/city data

Test Strategy:
1. Test Buyer tab: Country → State → City cascade
2. Test Consignee tab: Country → State → City cascade
3. Test "Copy from Buyer" button (should copy cascade state)
4. Test initial load with pre-populated values
5. Test error handling (invalid IDs, network errors)
"""
import pytest
from playwright.sync_api import Page, expect
import time


class TestSalesInvoiceCascadingDropdowns:
    """Test cascading dropdown functionality"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, test_po):
        """Setup: Navigate to sales invoice create page"""
        # Start Django server (assume it's running on localhost:8000)
        self.page = page
        self.po_master, self.po_detail = test_po

        # Login first
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Navigate to PO selection page
        page.goto("http://localhost:8000/accounts/sales-invoice/po-selection/")
        page.wait_for_load_state('networkidle')

        # Search for test PO
        page.fill('input[name="customer_name"]', 'Test Customer')
        page.click('button:has-text("Search")')
        page.wait_for_load_state('networkidle')

        # Click "Select" link for the PO
        page.click('text=Select')
        page.wait_for_load_state('networkidle')

        # Should now be on the invoice create page
        expect(page).to_have_url(lambda url: '/sales-invoice/create/' in url)

        yield

        # Teardown: Close page
        page.close()

    def test_buyer_country_to_state_cascade(self):
        """Test: Buyer Country selection populates State dropdown"""
        page = self.page

        # Navigate to Buyer tab
        page.click('button[data-tab="buyer"]')
        page.wait_for_selector('#tab-buyer:not(.hidden)')

        # Get initial state options count (should be just placeholder)
        state_select = page.locator('#id_buyer_state')
        initial_count = state_select.locator('option').count()
        assert initial_count == 1, "State dropdown should initially have only placeholder"

        # Select a country (e.g., India = 1)
        country_select = page.locator('#id_buyer_country')
        country_select.select_option('1')  # India

        # Wait for AJAX call to complete
        page.wait_for_timeout(1000)  # Wait 1s for fetch to complete
        page.wait_for_load_state('networkidle')

        # Verify states are populated
        state_count = state_select.locator('option').count()
        assert state_count > 1, f"States should be populated (found {state_count} options)"

        # Verify first option is placeholder
        first_option = state_select.locator('option').first
        expect(first_option).to_have_text('Select State')

        # Verify we have actual state options
        second_option = state_select.locator('option').nth(1)
        expect(second_option).not_to_have_value('')

    def test_buyer_state_to_city_cascade(self):
        """Test: Buyer State selection populates City dropdown"""
        page = self.page

        # Navigate to Buyer tab
        page.click('button[data-tab="buyer"]')
        page.wait_for_selector('#tab-buyer:not(.hidden)')

        # Select country first
        page.locator('#id_buyer_country').select_option('1')  # India
        page.wait_for_timeout(1000)

        # Get initial city options count
        city_select = page.locator('#id_buyer_city')
        initial_count = city_select.locator('option').count()
        assert initial_count == 1, "City dropdown should initially have only placeholder"

        # Select a state (e.g., Maharashtra = 1)
        state_select = page.locator('#id_buyer_state')
        page.wait_for_selector('#id_buyer_state option[value="1"]')
        state_select.select_option('1')  # Maharashtra

        # Wait for AJAX call to complete
        page.wait_for_timeout(1000)
        page.wait_for_load_state('networkidle')

        # Verify cities are populated
        city_count = city_select.locator('option').count()
        assert city_count > 1, f"Cities should be populated (found {city_count} options)"

        # Verify first option is placeholder
        first_option = city_select.locator('option').first
        expect(first_option).to_have_text('Select City')

    def test_consignee_country_to_state_cascade(self):
        """Test: Consignee Country selection populates State dropdown"""
        page = self.page

        # Navigate to Consignee tab
        page.click('button[data-tab="consignee"]')
        page.wait_for_selector('#tab-consignee:not(.hidden)')

        # Get initial state options count
        state_select = page.locator('#id_cong_state')
        initial_count = state_select.locator('option').count()
        assert initial_count == 1, "Consignee state dropdown should initially have only placeholder"

        # Select a country
        country_select = page.locator('#id_cong_country')
        country_select.select_option('1')  # India

        # Wait for AJAX call
        page.wait_for_timeout(1000)
        page.wait_for_load_state('networkidle')

        # Verify states are populated
        state_count = state_select.locator('option').count()
        assert state_count > 1, f"Consignee states should be populated (found {state_count} options)"

    def test_consignee_state_to_city_cascade(self):
        """Test: Consignee State selection populates City dropdown"""
        page = self.page

        # Navigate to Consignee tab
        page.click('button[data-tab="consignee"]')
        page.wait_for_selector('#tab-consignee:not(.hidden)')

        # Select country first
        page.locator('#id_cong_country').select_option('1')  # India
        page.wait_for_timeout(1000)

        # Get initial city options count
        city_select = page.locator('#id_cong_city')
        initial_count = city_select.locator('option').count()
        assert initial_count == 1, "Consignee city dropdown should initially have only placeholder"

        # Select a state
        state_select = page.locator('#id_cong_state')
        page.wait_for_selector('#id_cong_state option[value="1"]')
        state_select.select_option('1')  # Maharashtra

        # Wait for AJAX call
        page.wait_for_timeout(1000)
        page.wait_for_load_state('networkidle')

        # Verify cities are populated
        city_count = city_select.locator('option').count()
        assert city_count > 1, f"Consignee cities should be populated (found {city_count} options)"

    def test_country_change_clears_state_and_city(self):
        """Test: Changing country clears state and city selections"""
        page = self.page

        # Navigate to Buyer tab
        page.click('button[data-tab="buyer"]')
        page.wait_for_selector('#tab-buyer:not(.hidden)')

        # Select country, state, and city
        page.locator('#id_buyer_country').select_option('1')
        page.wait_for_timeout(1000)

        page.locator('#id_buyer_state').select_option('1')
        page.wait_for_timeout(1000)

        page.locator('#id_buyer_city').select_option('1')
        page.wait_for_timeout(500)

        # Now change country
        page.locator('#id_buyer_country').select_option('2')  # Different country
        page.wait_for_timeout(1000)

        # Verify state and city are cleared
        state_value = page.locator('#id_buyer_state').input_value()
        assert state_value == '', "State should be cleared when country changes"

        city_select = page.locator('#id_buyer_city')
        city_count = city_select.locator('option').count()
        assert city_count == 1, "City dropdown should be reset to placeholder only"

    def test_copy_from_buyer_button(self):
        """Test: Copy from Buyer button copies cascading dropdown values"""
        page = self.page

        # Navigate to Buyer tab and fill data
        page.click('button[data-tab="buyer"]')
        page.wait_for_selector('#tab-buyer:not(.hidden)')

        # Fill buyer address data with cascading dropdowns
        page.fill('#id_buyer_name', 'Test Buyer Name')
        page.fill('#id_buyer_address', '123 Test Street')

        page.locator('#id_buyer_country').select_option('1')  # India
        page.wait_for_timeout(1000)

        page.locator('#id_buyer_state').select_option('1')  # Maharashtra
        page.wait_for_timeout(1000)

        page.locator('#id_buyer_city').select_option('1')  # Mumbai
        page.wait_for_timeout(500)

        page.fill('#id_buyer_phone', '1234567890')

        # Navigate to Consignee tab
        page.click('button[data-tab="consignee"]')
        page.wait_for_selector('#tab-consignee:not(.hidden)')

        # Click "Copy from Buyer" button
        page.click('button:has-text("Copy from Buyer")')
        page.wait_for_timeout(1000)

        # Verify all fields including cascading dropdowns are copied
        expect(page.locator('#id_cong_name')).to_have_value('Test Buyer Name')
        expect(page.locator('#id_cong_address')).to_have_value('123 Test Street')
        expect(page.locator('#id_cong_country')).to_have_value('1')
        expect(page.locator('#id_cong_state')).to_have_value('1')
        expect(page.locator('#id_cong_city')).to_have_value('1')
        expect(page.locator('#id_cong_phone')).to_have_value('1234567890')

        # Verify consignee state dropdown is populated (not just placeholder)
        cong_state_count = page.locator('#id_cong_state option').count()
        assert cong_state_count > 1, "Consignee state dropdown should be populated after copy"

        # Verify consignee city dropdown is populated
        cong_city_count = page.locator('#id_cong_city option').count()
        assert cong_city_count > 1, "Consignee city dropdown should be populated after copy"

    def test_api_endpoints_return_valid_json(self):
        """Test: API endpoints return valid JSON data"""
        page = self.page

        # Test get_states endpoint
        response = page.request.get(
            "http://localhost:8000/accounts/sales-invoice/api/get-states/?country_id=1"
        )
        assert response.status == 200, f"get_states endpoint failed: {response.status}"

        data = response.json()
        assert 'states' in data, "Response should contain 'states' key"
        assert isinstance(data['states'], list), "States should be a list"
        assert len(data['states']) > 0, "States list should not be empty for India (id=1)"

        # Verify state data structure
        first_state = data['states'][0]
        assert 'sid' in first_state, "State should have 'sid' field"
        assert 'statename' in first_state, "State should have 'statename' field"

        # Test get_cities endpoint
        response = page.request.get(
            "http://localhost:8000/accounts/sales-invoice/api/get-cities/?state_id=1"
        )
        assert response.status == 200, f"get_cities endpoint failed: {response.status}"

        data = response.json()
        assert 'cities' in data, "Response should contain 'cities' key"
        assert isinstance(data['cities'], list), "Cities should be a list"

        # Verify city data structure if cities exist
        if len(data['cities']) > 0:
            first_city = data['cities'][0]
            assert 'cityid' in first_city, "City should have 'cityid' field"
            assert 'cityname' in first_city, "City should have 'cityname' field"

    def test_empty_country_selection_clears_dropdowns(self):
        """Test: Selecting empty country option clears state and city"""
        page = self.page

        # Navigate to Buyer tab
        page.click('button[data-tab="buyer"]')
        page.wait_for_selector('#tab-buyer:not(.hidden)')

        # First, populate all dropdowns
        page.locator('#id_buyer_country').select_option('1')
        page.wait_for_timeout(1000)

        page.locator('#id_buyer_state').select_option('1')
        page.wait_for_timeout(1000)

        page.locator('#id_buyer_city').select_option('1')
        page.wait_for_timeout(500)

        # Now select empty country option (placeholder)
        page.locator('#id_buyer_country').select_option('')
        page.wait_for_timeout(1000)

        # Verify state and city dropdowns are reset
        state_count = page.locator('#id_buyer_state option').count()
        city_count = page.locator('#id_buyer_city option').count()

        assert state_count == 1, "State dropdown should be reset to placeholder only"
        assert city_count == 1, "City dropdown should be reset to placeholder only"

        # Verify they have placeholder text
        expect(page.locator('#id_buyer_state option').first).to_have_text('Select State')
        expect(page.locator('#id_buyer_city option').first).to_have_text('Select City')


@pytest.mark.skip(reason="Edge case test - run manually if needed")
class TestSalesInvoiceCascadingEdgeCases:
    """Edge case tests for cascading dropdowns"""

    def test_invalid_country_id(self, page: Page):
        """Test: Invalid country ID returns empty states list"""
        response = page.request.get(
            "http://localhost:8000/accounts/sales-invoice/api/get-states/?country_id=99999"
        )
        assert response.status == 200

        data = response.json()
        assert data['states'] == [], "Invalid country ID should return empty list"

    def test_invalid_state_id(self, page: Page):
        """Test: Invalid state ID returns empty cities list"""
        response = page.request.get(
            "http://localhost:8000/accounts/sales-invoice/api/get-cities/?state_id=99999"
        )
        assert response.status == 200

        data = response.json()
        assert data['cities'] == [], "Invalid state ID should return empty list"

    def test_missing_query_parameter(self, page: Page):
        """Test: Missing query parameter is handled gracefully"""
        response = page.request.get(
            "http://localhost:8000/accounts/sales-invoice/api/get-states/"
        )
        # Should not crash, should return empty or error
        assert response.status in [200, 400], "Missing parameter should be handled gracefully"
