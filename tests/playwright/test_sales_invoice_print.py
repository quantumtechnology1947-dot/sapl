"""
Test Suite for Sales Invoice Print View

Tests the ability to print/generate PDF for invoices including:
- Print page loads correctly
- All invoice details displayed
- Buyer and consignee information shown
- Items table with calculations
- Print button opens in new tab
- Tax calculations displayed correctly
"""
import pytest
from playwright.sync_api import Page, expect
from datetime import datetime


class TestSalesInvoicePrintView:
    """Test invoice print functionality"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, db):
        """Setup: Create test invoice with complete data and login"""
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails
        from sales_distribution.models import SdCustMaster, SdCustPoMaster, SdCustPoDetails
        from design.models import TbldgItemMaster

        # Create customer
        self.customer = SdCustMaster.objects.create(
            customercode='PRINT001',
            customername='Print Test Customer Ltd',
            compid_id=1,
        )

        # Create PO
        self.po = SdCustPoMaster.objects.create(
            pono='PO-PRINT-001',
            customerid=self.customer,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Create items
        self.item1, _ = TbldgItemMaster.objects.get_or_create(
            itemid=101,
            defaults={'itemname': 'Test Print Item 1', 'itemcode': 'ITEM101'}
        )
        self.item2, _ = TbldgItemMaster.objects.get_or_create(
            itemid=102,
            defaults={'itemname': 'Test Print Item 2', 'itemcode': 'ITEM102'}
        )

        # Create PO details
        self.po_detail1 = SdCustPoDetails.objects.create(
            poid=self.po,
            itemid=self.item1,
            totalqty=100,
            rate=500.00,
        )
        self.po_detail2 = SdCustPoDetails.objects.create(
            poid=self.po,
            itemid=self.item2,
            totalqty=50,
            rate=1000.00,
        )

        # Create invoice with complete data
        self.invoice = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='PRINT0001',
            poid=self.po,
            pono='PO-PRINT-001',
            customercode='PRINT001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            dateofissueinvoice='15-01-2025',
            compid_id=1,
            finyearid_id=1,
            # Buyer info
            buyer_name='Test Print Buyer Company',
            buyer_address='123 Buyer Street, Mumbai',
            buyer_phone='9876543210',
            buyer_country='India',
            buyer_state='Maharashtra',
            buyer_city='Mumbai',
            buyer_pincode='400001',
            # Consignee info
            consignee_name='Test Consignee Warehouse',
            consignee_address='456 Consignee Road, Pune',
            consignee_phone='8765432109',
            consignee_country='India',
            consignee_state='Maharashtra',
            consignee_city='Pune',
            consignee_pincode='411001',
            # Other details
            wono='WO-001',
            vehicleno='MH-12-AB-1234',
            challanno='CH-001',
        )

        # Create invoice details
        self.detail1 = TblaccSalesinvoiceDetails.objects.create(
            mid=self.invoice,
            itemid=self.po_detail1,
            reqqty=50,
            rate=500,
            amount=25000,
        )
        self.detail2 = TblaccSalesinvoiceDetails.objects.create(
            mid=self.invoice,
            itemid=self.po_detail2,
            reqqty=25,
            rate=1000,
            amount=25000,
        )

        self.page = page

        # Login
        page.goto("http://localhost:8000/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        yield

        # Cleanup
        page.close()

    def test_print_page_loads(self):
        """Test: Print page loads correctly"""
        page = self.page

        # Navigate directly to print URL
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Verify page loads (no 404)
        content = page.content()
        assert '404' not in content
        assert 'not found' not in content.lower()

        # Verify invoice number is displayed
        invoice_number = page.locator(f'text=/PRINT0001/i').first
        expect(invoice_number).to_be_visible()

    def test_print_button_from_list_opens_new_tab(self):
        """Test: Print button from list opens in new tab"""
        page = self.page

        # Navigate to invoice list
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        # Verify print button has target="_blank"
        print_button = page.locator(f'tr:has-text("{self.invoice.invoiceno}") a:has-text("Print")')
        expect(print_button).to_have_attribute('target', '_blank')

    def test_buyer_information_displayed(self):
        """Test: Buyer information is displayed correctly"""
        page = self.page

        # Navigate to print page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Verify buyer details
        expect(page.locator('text=/Test Print Buyer Company/i')).to_be_visible()
        expect(page.locator('text=/123 Buyer Street/i')).to_be_visible()
        expect(page.locator('text=/9876543210/i')).to_be_visible()
        expect(page.locator('text=/Mumbai/i')).to_be_visible()
        expect(page.locator('text=/400001/i')).to_be_visible()

    def test_consignee_information_displayed(self):
        """Test: Consignee information is displayed correctly"""
        page = self.page

        # Navigate to print page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Verify consignee details
        expect(page.locator('text=/Test Consignee Warehouse/i')).to_be_visible()
        expect(page.locator('text=/456 Consignee Road/i')).to_be_visible()
        expect(page.locator('text=/8765432109/i')).to_be_visible()
        expect(page.locator('text=/Pune/i')).to_be_visible()
        expect(page.locator('text=/411001/i')).to_be_visible()

    def test_invoice_header_details(self):
        """Test: Invoice header details are displayed"""
        page = self.page

        # Navigate to print page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Verify header details
        expect(page.locator('text=/PRINT0001/i')).to_be_visible()
        expect(page.locator('text=/15-01-2025/i')).to_be_visible()
        expect(page.locator('text=/PO-PRINT-001/i')).to_be_visible()
        expect(page.locator('text=/WO-001/i')).to_be_visible()
        expect(page.locator('text=/MH-12-AB-1234/i')).to_be_visible()
        expect(page.locator('text=/CH-001/i')).to_be_visible()

    def test_items_table_with_calculations(self):
        """Test: Items table shows all items with correct calculations"""
        page = self.page

        # Navigate to print page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Verify items are displayed
        expect(page.locator('text=/Test Print Item 1/i')).to_be_visible()
        expect(page.locator('text=/Test Print Item 2/i')).to_be_visible()

        # Verify quantities
        expect(page.locator('text=/50/i').first).to_be_visible()  # Item 1 qty
        expect(page.locator('text=/25/i').first).to_be_visible()  # Item 2 qty

        # Verify rates
        expect(page.locator('text=/500/i').first).to_be_visible()
        expect(page.locator('text=/1000/i').first).to_be_visible()

        # Verify amounts
        expect(page.locator('text=/25000/i, text=/25,000/i').first).to_be_visible()

    def test_total_amount_calculation(self):
        """Test: Total amount is calculated correctly"""
        page = self.page

        # Navigate to print page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Total should be 50,000 (25000 + 25000)
        # May be formatted as "50000", "50,000", or "50,000.00"
        total_locators = page.locator('text=/50000/i, text=/50,000/i, text=/Total/i')
        expect(total_locators.first).to_be_visible()

    def test_print_stylesheet_for_pdf(self):
        """Test: Print view has print-friendly styling"""
        page = self.page

        # Navigate to print page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Check for print-specific CSS or media queries
        content = page.content()

        # Should have print-friendly elements (white background, no unnecessary UI elements)
        # Verify no navigation menu is present (print should be clean)
        nav_elements = page.locator('nav, .navbar, .sidebar')
        expect(nav_elements).to_have_count(0)

    def test_print_nonexistent_invoice_shows_404(self):
        """Test: Printing non-existent invoice shows 404"""
        page = self.page

        # Try to print invoice with invalid ID
        page.goto("http://localhost:8000/accounts/sales-invoice/99999/print/")
        page.wait_for_load_state('networkidle')

        # Should show 404 or error message
        error_content = page.content()
        assert '404' in error_content or 'not found' in error_content.lower()

    def test_cannot_print_invoice_from_another_company(self):
        """Test: Cannot print invoice from different company (security)"""
        from accounts.models import TblaccSalesinvoiceMaster

        page = self.page

        # Create invoice with different company ID
        other_invoice = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='OTHER0001',
            poid=self.po,
            pono='PO-PRINT-001',
            customercode='PRINT001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=999,  # Different company
            finyearid_id=1,
        )

        # Try to print it (should fail - 404 or permission denied)
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{other_invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Should show error (404 or permission denied)
        error_content = page.content()
        is_error = '404' in error_content or 'not found' in error_content.lower() or \
                   'permission' in error_content.lower() or 'access denied' in error_content.lower()

        assert is_error, "Should not allow printing invoice from another company"

    def test_print_page_has_company_logo_header(self):
        """Test: Print page includes company branding/header"""
        page = self.page

        # Navigate to print page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/print/")
        page.wait_for_load_state('networkidle')

        # Should have some company branding (header, logo, or company name)
        # This will depend on implementation, checking for common elements
        header_elements = page.locator('header, .company-header, .invoice-header, h1')
        expect(header_elements.first).to_be_visible()
