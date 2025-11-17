"""
Test Suite for Sales Invoice List View

Tests the Invoice List/Search functionality including:
- Page loading and display
- Search by Customer Name
- Search by PO Number
- Search by Invoice Number
- Pagination (15 items per page)

From sales_invoice.md requirements and gap analysis:
- Invoice list view for searching and accessing existing invoices
- Search filters for Customer, PO, Invoice Number
- Pagination with 15 items per page
"""
import pytest
from playwright.sync_api import Page, expect
from datetime import datetime


class TestSalesInvoiceListView:
    """Test invoice list and search functionality"""

    def test_invoice_list_page_loads(self, page: Page, db):
        """Test: Invoice list page loads successfully"""
        from accounts.models import TblaccSalesinvoiceMaster
        from sales_distribution.models import SdCustMaster, SdCustPoMaster

        # Create test customer
        customer = SdCustMaster.objects.create(
            customercode='TEST001',
            customername='Test Customer',
            compid_id=1,
        )

        # Create test PO
        po = SdCustPoMaster.objects.create(
            pono='PO001',
            customerid=customer,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Create test invoice
        invoice = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='0001',
            poid=po,
            customercode='TEST001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Login
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Navigate to invoice list
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        # Verify page loaded
        expect(page).to_have_title(lambda title: 'Sales Invoice' in title or 'Invoice' in title)

        # Verify invoice appears in list
        invoice_row = page.locator(f'tr:has-text("{invoice.invoiceno}")')
        expect(invoice_row).to_be_visible()

    def test_search_by_customer_name(self, page: Page, db):
        """Test: Search invoices by customer name"""
        from accounts.models import TblaccSalesinvoiceMaster
        from sales_distribution.models import SdCustMaster, SdCustPoMaster

        # Create customer 1
        customer1 = SdCustMaster.objects.create(
            customercode='CUST001',
            customername='Alpha Company',
            compid_id=1,
        )

        po1 = SdCustPoMaster.objects.create(
            pono='PO001',
            customerid=customer1,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        invoice1 = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='0001',
            poid=po1,
            customercode='CUST001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Create customer 2
        customer2 = SdCustMaster.objects.create(
            customercode='CUST002',
            customername='Beta Corporation',
            compid_id=1,
        )

        po2 = SdCustPoMaster.objects.create(
            pono='PO002',
            customerid=customer2,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        invoice2 = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='0002',
            poid=po2,
            customercode='CUST002',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Login
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Navigate to invoice list
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        # Search for "Alpha"
        search_input = page.locator('input[name="customer_name"], input[name="customer"], input[placeholder*="Customer"]').first
        search_input.fill('Alpha')

        # Submit search (either button or HTMX auto-search)
        search_button = page.locator('button:has-text("Search"), button[type="submit"]').first
        if search_button.is_visible():
            search_button.click()

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)  # Wait for HTMX if used

        # Verify only invoice1 appears
        expect(page.locator(f'tr:has-text("{invoice1.invoiceno}")')).to_be_visible()
        expect(page.locator(f'tr:has-text("{invoice2.invoiceno}")')).not_to_be_visible()

    def test_search_by_po_number(self, page: Page, db):
        """Test: Search invoices by PO number"""
        from accounts.models import TblaccSalesinvoiceMaster
        from sales_distribution.models import SdCustMaster, SdCustPoMaster

        customer = SdCustMaster.objects.create(
            customercode='CUST001',
            customername='Test Customer',
            compid_id=1,
        )

        # Create PO 1
        po1 = SdCustPoMaster.objects.create(
            pono='PO-2025-001',
            customerid=customer,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        invoice1 = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='0001',
            poid=po1,
            pono='PO-2025-001',
            customercode='CUST001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Create PO 2
        po2 = SdCustPoMaster.objects.create(
            pono='PO-2025-002',
            customerid=customer,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        invoice2 = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='0002',
            poid=po2,
            pono='PO-2025-002',
            customercode='CUST001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Login
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Navigate to invoice list
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        # Search for "PO-2025-001"
        po_input = page.locator('input[name="po_number"], input[name="po"], input[placeholder*="PO"]').first
        po_input.fill('PO-2025-001')

        search_button = page.locator('button:has-text("Search"), button[type="submit"]').first
        if search_button.is_visible():
            search_button.click()

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)

        # Verify only invoice1 appears
        expect(page.locator(f'tr:has-text("{invoice1.invoiceno}")')).to_be_visible()
        expect(page.locator(f'tr:has-text("{invoice2.invoiceno}")')).not_to_be_visible()

    def test_pagination_shows_max_15_items(self, page: Page, db):
        """Test: Pagination displays max 15 invoices per page"""
        from accounts.models import TblaccSalesinvoiceMaster
        from sales_distribution.models import SdCustMaster, SdCustPoMaster

        # Create test customer and PO
        customer = SdCustMaster.objects.create(
            customercode='CUST001',
            customername='Test Customer',
            compid_id=1,
        )

        po = SdCustPoMaster.objects.create(
            pono='PO001',
            customerid=customer,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Create 20 invoices
        for i in range(1, 21):
            TblaccSalesinvoiceMaster.objects.create(
                invoiceno=f'{i:04d}',  # 0001, 0002, ..., 0020
                poid=po,
                customercode='CUST001',
                sysdate=datetime.now().strftime('%d-%m-%Y'),
                compid_id=1,
                finyearid_id=1,
            )

        # Login
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Navigate to invoice list
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        # Count invoice rows in table (exclude header)
        table_rows = page.locator('table tbody tr')
        row_count = table_rows.count()

        # Should show max 15 items
        assert row_count <= 15, f"Expected max 15 rows, found {row_count}"

        # Verify pagination controls exist
        pagination = page.locator('.pagination, nav[aria-label="Pagination"], .pager')
        expect(pagination).to_be_visible()

        # Verify "Next" or "2" button exists
        next_button = page.locator('a:has-text("Next"), a:has-text("2"), button:has-text("Next")')
        expect(next_button.first).to_be_visible()

    def test_invoice_list_action_buttons(self, page: Page, db):
        """Test: Each invoice row has Edit, Delete, Print action buttons"""
        from accounts.models import TblaccSalesinvoiceMaster
        from sales_distribution.models import SdCustMaster, SdCustPoMaster

        # Create test data
        customer = SdCustMaster.objects.create(
            customercode='CUST001',
            customername='Test Customer',
            compid_id=1,
        )

        po = SdCustPoMaster.objects.create(
            pono='PO001',
            customerid=customer,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        invoice = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='0001',
            poid=po,
            customercode='CUST001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Login
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Navigate to invoice list
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        # Find the invoice row
        invoice_row = page.locator(f'tr:has-text("{invoice.invoiceno}")')
        expect(invoice_row).to_be_visible()

        # Verify action buttons exist (at least one of each type)
        edit_button = invoice_row.locator('a:has-text("Edit"), button:has-text("Edit"), a[href*="edit"]')
        expect(edit_button.first).to_be_visible()

        # Delete button might be in a form or as a link
        delete_button = invoice_row.locator('a:has-text("Delete"), button:has-text("Delete"), a[href*="delete"]')
        expect(delete_button.first).to_be_visible()

        # Print button
        print_button = invoice_row.locator('a:has-text("Print"), button:has-text("Print"), a[href*="print"]')
        expect(print_button.first).to_be_visible()
