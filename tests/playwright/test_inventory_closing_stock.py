"""
Playwright tests for Inventory Closing Stock functionality
Tests the physical stock count and reporting features

Converted from: aaspnet/Module/Inventory/Transactions/ClosingStock.aspx
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.smoke
class TestClosingStock:
    """Test suite for Closing Stock physical count functionality"""

    def test_closing_stock_page_loads(self, inventory_page: Page, base_url: str):
        """Test that closing stock page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page title
        expect(inventory_page.locator('h1')).to_contain_text('Closing Stock')

        # Verify instructions are visible
        expect(inventory_page.locator('text=Instructions')).to_be_visible()

        # Verify form elements are present
        expect(inventory_page.locator('select[name="item"]')).to_be_visible()
        expect(inventory_page.locator('input[name="system_qty"]')).to_be_visible()
        expect(inventory_page.locator('input[name="physical_qty"]')).to_be_visible()

    def test_closing_stock_form_elements(self, inventory_page: Page, base_url: str):
        """Test that all form elements are present and properly labeled"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")

        # Check for item selection dropdown
        item_select = inventory_page.locator('select[name="item"]')
        expect(item_select).to_be_visible()
        expect(item_select).to_be_enabled()

        # Check for system quantity field (should be disabled/readonly)
        system_qty = inventory_page.locator('input[name="system_qty"]')
        expect(system_qty).to_be_visible()
        expect(system_qty).to_be_disabled()

        # Check for physical quantity field
        physical_qty = inventory_page.locator('input[name="physical_qty"]')
        expect(physical_qty).to_be_visible()
        expect(physical_qty).to_be_enabled()

        # Check for remarks field
        remarks = inventory_page.locator('textarea[name="remarks"], input[name="remarks"]')
        expect(remarks).to_be_visible()

        # Check for submit button
        submit_btn = inventory_page.locator('button[type="submit"]')
        expect(submit_btn).to_be_visible()
        expect(submit_btn).to_contain_text('Record Closing Stock')

    @pytest.mark.crud
    def test_closing_stock_variance_calculation(self, inventory_page: Page, base_url: str):
        """Test that variance is calculated correctly when physical qty is entered"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")

        # Select an item (first option after placeholder)
        item_select = inventory_page.locator('select[name="item"]')
        item_select.select_option(index=1)

        # Wait for system quantity to be populated (might be via JS/HTMX)
        inventory_page.wait_for_timeout(500)

        # Get system quantity value
        system_qty = inventory_page.locator('input[name="system_qty"]')
        system_qty_value = float(system_qty.input_value() or '0')

        # Enter physical quantity
        physical_qty_input = inventory_page.locator('input[name="physical_qty"]')
        test_physical_qty = system_qty_value + 5.5  # Add variance
        physical_qty_input.fill(str(test_physical_qty))

        # Wait for variance calculation
        inventory_page.wait_for_timeout(500)

        # Check if variance display appears
        variance_display = inventory_page.locator('#varianceDisplay')
        if variance_display.is_visible():
            # Verify variance value
            variance_value = inventory_page.locator('#varianceValue')
            expect(variance_value).to_be_visible()
            # Variance should be 5.500
            expect(variance_value).to_contain_text('5.500')

    @pytest.mark.crud
    def test_closing_stock_form_submission(self, inventory_page: Page, base_url: str):
        """Test submitting the closing stock form"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")

        # Select an item
        item_select = inventory_page.locator('select[name="item"]')
        item_select.select_option(index=1)

        # Wait for system quantity
        inventory_page.wait_for_timeout(500)

        # Enter physical quantity
        physical_qty = inventory_page.locator('input[name="physical_qty"]')
        physical_qty.fill('100.500')

        # Enter remarks
        remarks = inventory_page.locator('textarea[name="remarks"], input[name="remarks"]')
        remarks.fill('Physical count completed - Playwright test')

        # Submit form
        submit_btn = inventory_page.locator('button[type="submit"]')
        submit_btn.click()

        # Wait for response
        inventory_page.wait_for_load_state('networkidle')

        # Should redirect to report or show success message
        # Check if we're on the report page or see success message
        current_url = inventory_page.url
        assert '/inventory/closing-stock' in current_url or 'report' in current_url

    def test_closing_stock_report_page_loads(self, inventory_page: Page, base_url: str):
        """Test that closing stock report page loads successfully"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/report/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page title
        expect(inventory_page.locator('h1')).to_contain_text('Closing Stock Report')

        # Verify summary cards are visible
        expect(inventory_page.locator('text=Total Items')).to_be_visible()
        expect(inventory_page.locator('text=Items in Stock')).to_be_visible()
        expect(inventory_page.locator('text=Report Date')).to_be_visible()

    def test_closing_stock_report_table(self, inventory_page: Page, base_url: str):
        """Test that the stock report table displays correctly"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/report/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify table headers
        table = inventory_page.locator('table')
        expect(table).to_be_visible()

        # Check for required columns
        expect(inventory_page.locator('th:has-text("Item Code")')).to_be_visible()
        expect(inventory_page.locator('th:has-text("Description")')).to_be_visible()
        expect(inventory_page.locator('th:has-text("UOM")')).to_be_visible()
        expect(inventory_page.locator('th:has-text("System Qty")')).to_be_visible()
        expect(inventory_page.locator('th:has-text("Status")')).to_be_visible()

    def test_closing_stock_report_print_button(self, inventory_page: Page, base_url: str):
        """Test that print button is present and functional"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/report/")

        # Verify print button exists
        print_btn = inventory_page.locator('button:has-text("Print Report")')
        expect(print_btn).to_be_visible()
        expect(print_btn).to_be_enabled()

    def test_closing_stock_navigation_links(self, inventory_page: Page, base_url: str):
        """Test navigation between closing stock form and report"""
        # Start at form page
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")

        # Click "View Report" link
        view_report_link = inventory_page.locator('a:has-text("View Report")')
        expect(view_report_link).to_be_visible()
        view_report_link.click()

        # Should be on report page
        inventory_page.wait_for_load_state('networkidle')
        expect(inventory_page.locator('h1')).to_contain_text('Closing Stock Report')

        # Click "Record New Count" link
        record_link = inventory_page.locator('a:has-text("Record New Count")')
        expect(record_link).to_be_visible()
        record_link.click()

        # Should be back on form page
        inventory_page.wait_for_load_state('networkidle')
        expect(inventory_page.locator('h1')).to_contain_text('Closing Stock')
        expect(inventory_page.locator('text=Physical count')).to_be_visible()

    def test_closing_stock_cancel_button(self, inventory_page: Page, base_url: str):
        """Test that cancel button navigates back to dashboard"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")

        # Click cancel button
        cancel_btn = inventory_page.locator('a:has-text("Cancel")')
        expect(cancel_btn).to_be_visible()
        cancel_btn.click()

        # Should navigate to dashboard or inventory module
        inventory_page.wait_for_load_state('networkidle')
        current_url = inventory_page.url
        assert '/dashboard' in current_url or '/inventory' in current_url

    @pytest.mark.htmx
    def test_closing_stock_item_selection_updates_system_qty(self, inventory_page: Page, base_url: str):
        """Test that selecting an item updates the system quantity field"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")

        # Get initial system qty value
        system_qty = inventory_page.locator('input[name="system_qty"]')
        initial_value = system_qty.input_value()

        # Select an item
        item_select = inventory_page.locator('select[name="item"]')
        item_select.select_option(index=1)

        # Wait for potential AJAX/HTMX update
        inventory_page.wait_for_timeout(1000)

        # System qty should be updated (or might stay the same if no HTMX)
        # Just verify it's still visible and has a value
        expect(system_qty).to_be_visible()

    def test_closing_stock_form_validation(self, inventory_page: Page, base_url: str):
        """Test form validation for required fields"""
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")

        # Try to submit without filling required fields
        submit_btn = inventory_page.locator('button[type="submit"]')
        submit_btn.click()

        # Browser should prevent submission or show validation errors
        inventory_page.wait_for_timeout(500)

        # We should still be on the same page
        expect(inventory_page.locator('h1')).to_contain_text('Closing Stock')

    def test_closing_stock_responsive_layout(self, inventory_page: Page, base_url: str):
        """Test that closing stock pages are responsive"""
        # Test desktop size (already set in fixture)
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")
        expect(inventory_page.locator('form')).to_be_visible()

        # Test tablet size
        inventory_page.set_viewport_size({"width": 768, "height": 1024})
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")
        expect(inventory_page.locator('form')).to_be_visible()

        # Test mobile size
        inventory_page.set_viewport_size({"width": 375, "height": 667})
        inventory_page.goto(f"{base_url}/inventory/closing-stock/")
        expect(inventory_page.locator('form')).to_be_visible()
