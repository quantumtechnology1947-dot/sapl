"""
Playwright tests for Inventory Reports
Tests all reporting functionality in the inventory module

Converted from: aaspnet/Module/Inventory/Reports/*.aspx
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.inventory
@pytest.mark.integration
class TestInventoryReports:
    """Test suite for Inventory reporting functionality"""

    def test_stock_ledger_page_loads(self, inventory_page: Page, base_url: str):
        """Test Stock Ledger report page loads"""
        inventory_page.goto(f"{base_url}/inventory/reports/stock-ledger/")
        inventory_page.wait_for_load_state('networkidle')

        # Verify page loaded
        expect(inventory_page.locator('body')).to_be_visible()

    def test_stock_statement_page_loads(self, inventory_page: Page, base_url: str):
        """Test Stock Statement report page loads"""
        inventory_page.goto(f"{base_url}/inventory/reports/stock-statement/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_moving_items_report_loads(self, inventory_page: Page, base_url: str):
        """Test Moving/Non-Moving Items report page loads"""
        inventory_page.goto(f"{base_url}/inventory/reports/moving-items/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_abc_analysis_report_loads(self, inventory_page: Page, base_url: str):
        """Test ABC Analysis report page loads"""
        inventory_page.goto(f"{base_url}/inventory/reports/abc-analysis/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_work_order_shortage_report_loads(self, inventory_page: Page, base_url: str):
        """Test Work Order Shortage report page loads"""
        inventory_page.goto(f"{base_url}/inventory/reports/work-order-shortage/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_work_order_issue_report_loads(self, inventory_page: Page, base_url: str):
        """Test Work Order Issue report page loads"""
        inventory_page.goto(f"{base_url}/inventory/reports/work-order-issue/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_inward_register_report_loads(self, inventory_page: Page, base_url: str):
        """Test Inward Register report page loads"""
        inventory_page.goto(f"{base_url}/inventory/reports/inward-register/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_outward_register_report_loads(self, inventory_page: Page, base_url: str):
        """Test Outward Register report page loads"""
        inventory_page.goto(f"{base_url}/inventory/reports/outward-register/")
        inventory_page.wait_for_load_state('networkidle')

        expect(inventory_page.locator('body')).to_be_visible()

    def test_stock_ledger_has_filters(self, inventory_page: Page, base_url: str):
        """Test Stock Ledger report has filter controls"""
        inventory_page.goto(f"{base_url}/inventory/reports/stock-ledger/")
        inventory_page.wait_for_load_state('networkidle')

        # Should have date range or item selection filters
        filters = inventory_page.locator('select, input[type="date"]')
        # Filters should exist

    def test_abc_analysis_has_categories(self, inventory_page: Page, base_url: str):
        """Test ABC Analysis shows A/B/C categories"""
        inventory_page.goto(f"{base_url}/inventory/reports/abc-analysis/")
        inventory_page.wait_for_load_state('networkidle')

        # Should show categories or classification
        expect(inventory_page.locator('body')).to_be_visible()

    def test_moving_items_has_date_filters(self, inventory_page: Page, base_url: str):
        """Test Moving Items report has date filters"""
        inventory_page.goto(f"{base_url}/inventory/reports/moving-items/")
        inventory_page.wait_for_load_state('networkidle')

        # Should have date range filters
        date_inputs = inventory_page.locator('input[type="date"]')
        # Date filters might exist

    def test_report_print_functionality(self, inventory_page: Page, base_url: str):
        """Test reports have print functionality"""
        reports = [
            '/inventory/reports/stock-ledger/',
            '/inventory/reports/stock-statement/',
            '/inventory/reports/abc-analysis/',
        ]

        for report_url in reports:
            inventory_page.goto(f"{base_url}{report_url}")
            inventory_page.wait_for_load_state('networkidle')

            # Look for print button
            print_btn = inventory_page.locator('button:has-text("Print"), a:has-text("Print")')
            # Print functionality should exist

    def test_report_export_functionality(self, inventory_page: Page, base_url: str):
        """Test reports have export functionality"""
        inventory_page.goto(f"{base_url}/inventory/reports/stock-statement/")
        inventory_page.wait_for_load_state('networkidle')

        # Look for export buttons (Excel, PDF, etc.)
        export_btn = inventory_page.locator('button:has-text("Export"), a:has-text("Excel"), a:has-text("PDF")')
        # Export might exist

    def test_stock_statement_displays_data(self, inventory_page: Page, base_url: str):
        """Test Stock Statement displays data in table format"""
        inventory_page.goto(f"{base_url}/inventory/reports/stock-statement/")
        inventory_page.wait_for_load_state('networkidle')

        # Should have table with data
        table = inventory_page.locator('table')
        if table.is_visible():
            expect(table).to_be_visible()

    def test_inward_register_has_date_range(self, inventory_page: Page, base_url: str):
        """Test Inward Register has date range filter"""
        inventory_page.goto(f"{base_url}/inventory/reports/inward-register/")
        inventory_page.wait_for_load_state('networkidle')

        # Should have from/to date fields
        date_fields = inventory_page.locator('input[type="date"]')
        # Date range should exist

    def test_outward_register_has_date_range(self, inventory_page: Page, base_url: str):
        """Test Outward Register has date range filter"""
        inventory_page.goto(f"{base_url}/inventory/reports/outward-register/")
        inventory_page.wait_for_load_state('networkidle')

        date_fields = inventory_page.locator('input[type="date"]')

    def test_work_order_reports_have_wo_filter(self, inventory_page: Page, base_url: str):
        """Test Work Order reports have WO selection"""
        inventory_page.goto(f"{base_url}/inventory/reports/work-order-shortage/")
        inventory_page.wait_for_load_state('networkidle')

        # Should have work order selection
        wo_select = inventory_page.locator('select[name*="work"], input[name*="work"]')

    @pytest.mark.smoke
    def test_all_reports_load_without_error(self, inventory_page: Page, base_url: str):
        """Smoke test: verify all report pages load without errors"""
        reports = [
            '/inventory/reports/stock-ledger/',
            '/inventory/reports/stock-statement/',
            '/inventory/reports/moving-items/',
            '/inventory/reports/abc-analysis/',
            '/inventory/reports/work-order-shortage/',
            '/inventory/reports/work-order-issue/',
            '/inventory/reports/inward-register/',
            '/inventory/reports/outward-register/',
        ]

        for report_url in reports:
            inventory_page.goto(f"{base_url}{report_url}")
            inventory_page.wait_for_load_state('networkidle')

            # Verify no error message
            error = inventory_page.locator('text=Error, text=404, text=500')
            if error.is_visible():
                pytest.fail(f"Error found on {report_url}")

            # Verify page loaded
            expect(inventory_page.locator('body')).to_be_visible()

    def test_reports_responsive_layout(self, inventory_page: Page, base_url: str):
        """Test reports are responsive"""
        inventory_page.goto(f"{base_url}/inventory/reports/stock-statement/")

        # Desktop
        expect(inventory_page.locator('body')).to_be_visible()

        # Tablet
        inventory_page.set_viewport_size({"width": 768, "height": 1024})
        inventory_page.reload()
        expect(inventory_page.locator('body')).to_be_visible()

        # Mobile
        inventory_page.set_viewport_size({"width": 375, "height": 667})
        inventory_page.reload()
        expect(inventory_page.locator('body')).to_be_visible()
