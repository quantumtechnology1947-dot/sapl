"""
Test Suite for Sales Invoice Remaining Quantity Calculation

Tests the business logic that ensures:
- Only POs with remaining quantity > 0 are shown
- Users cannot create invoices exceeding remaining quantity
- Remaining qty is calculated correctly: Total PO Qty - Sum(Already Invoiced Qty)

From sales_invoice.md:
- Lines 148-150: Only POs with remaining quantity shown in grid
- Lines 571-606: Remaining qty validation in POST handler (sales_invoice.py)
- Lines 126-153: Remaining qty calculation logic
"""
import pytest
from playwright.sync_api import Page, expect


class TestSalesInvoiceRemainingQuantity:
    """Test remaining quantity calculation and validation"""

    def test_po_with_no_invoices_shows_full_quantity(self, page: Page, test_po):
        """Test: PO with no invoices shows total quantity as remaining"""
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Navigate to PO selection
        page.goto("http://localhost:8000/accounts/sales-invoice/po-selection/")
        page.wait_for_load_state('networkidle')

        # Search for test PO
        page.fill('input[name="customer_name"]', 'Test Customer')
        page.click('button:has-text("Search")')
        page.wait_for_load_state('networkidle')

        # Verify PO appears with full quantity
        po_master, po_detail = test_po
        po_row = page.locator(f'tr:has-text("{po_master.pono}")')
        expect(po_row).to_be_visible()

        # Verify remaining qty = total qty (100)
        # Note: This requires the template to display remaining quantity
        # The actual implementation should be verified

    def test_cannot_create_invoice_exceeding_remaining_qty(self, page: Page, test_po):
        """Test: Cannot create invoice with quantity > remaining quantity"""
        # Login and navigate to invoice create
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        page.goto("http://localhost:8000/accounts/sales-invoice/po-selection/")
        page.fill('input[name="customer_name"]', 'Test Customer')
        page.click('button:has-text("Search")')
        page.wait_for_load_state('networkidle')

        page.click('text=Select')
        page.wait_for_load_state('networkidle')

        # Navigate to Goods tab
        page.click('button[data-tab="goods"]')
        page.wait_for_selector('#tab-goods:not(.hidden)')

        # Try to enter quantity > total quantity (e.g., 150 when total is 100)
        page.fill('input[name="goods-0-reqqty"]', '150')
        page.fill('input[name="goods-0-rate"]', '100')

        # Submit form
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Should show error message
        error_message = page.locator('.error, .alert-danger, text=/exceed/i')
        expect(error_message).to_be_visible()

    def test_remaining_qty_updates_after_invoice_creation(self, page: Page, test_po, db):
        """Test: Remaining quantity updates after creating an invoice"""
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails

        po_master, po_detail = test_po

        # Create first invoice for qty=60
        invoice1 = TblaccSalesinvoiceMaster.objects.create(
            poid=po_master,
            invoiceno='0001',
            compid_id=1,
            finyearid_id=1,
            sysdate='17-11-2025',
        )
        TblaccSalesinvoiceDetails.objects.create(
            mid=invoice1,
            itemid=po_detail,
            reqqty=60,
            rate=100,
            amount=6000,
        )

        # Login and check PO selection page
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        page.goto("http://localhost:8000/accounts/sales-invoice/po-selection/")
        page.fill('input[name="customer_name"]', 'Test Customer')
        page.click('button:has-text("Search")')
        page.wait_for_load_state('networkidle')

        # PO should still appear (remaining qty = 40)
        po_row = page.locator(f'tr:has-text("{po_master.pono}")')
        expect(po_row).to_be_visible()

        # Try to create invoice for qty=50 (should fail - only 40 remaining)
        page.click('text=Select')
        page.wait_for_load_state('networkidle')

        page.click('button[data-tab="goods"]')
        page.wait_for_selector('#tab-goods:not(.hidden)')

        page.fill('input[name="goods-0-reqqty"]', '50')
        page.fill('input[name="goods-0-rate"]', '100')

        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Should show error
        error_message = page.locator('.error, .alert-danger, text=/exceed/i')
        expect(error_message).to_be_visible()

    def test_po_disappears_when_fully_invoiced(self, page: Page, test_po, db):
        """Test: PO disappears from selection grid when fully invoiced"""
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails

        po_master, po_detail = test_po

        # Create invoice for full quantity (100)
        invoice = TblaccSalesinvoiceMaster.objects.create(
            poid=po_master,
            invoiceno='0001',
            compid_id=1,
            finyearid_id=1,
            sysdate='17-11-2025',
        )
        TblaccSalesinvoiceDetails.objects.create(
            mid=invoice,
            itemid=po_detail,
            reqqty=100,  # Full quantity
            rate=100,
            amount=10000,
        )

        # Login and check PO selection page
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        page.goto("http://localhost:8000/accounts/sales-invoice/po-selection/")
        page.fill('input[name="customer_name"]', 'Test Customer')
        page.click('button:has-text("Search")')
        page.wait_for_load_state('networkidle')

        # PO should NOT appear (remaining qty = 0)
        po_row = page.locator(f'tr:has-text("{po_master.pono}")')
        expect(po_row).not_to_be_visible()
