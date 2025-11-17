"""
Test Suite for Sales Invoice Edit/Update View

Tests the ability to edit existing invoices including:
- Loading invoice data into all 4 tabs
- Updating invoice fields
- Recalculating remaining quantity (excluding current invoice)
- Validation on edit
"""
import pytest
from playwright.sync_api import Page, expect
from datetime import datetime


class TestSalesInvoiceEditView:
    """Test invoice edit/update functionality"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, db):
        """Setup: Create test invoice and login"""
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails
        from sales_distribution.models import SdCustMaster, SdCustPoMaster, SdCustPoDetails
        from design.models import TbldgItemMaster

        # Create customer
        self.customer = SdCustMaster.objects.create(
            customercode='EDIT001',
            customername='Edit Test Customer',
            compid_id=1,
        )

        # Create PO
        self.po = SdCustPoMaster.objects.create(
            pono='PO-EDIT-001',
            customerid=self.customer,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Create item
        self.item, _ = TbldgItemMaster.objects.get_or_create(
            itemid=999,
            defaults={'itemname': 'Test Edit Item', 'itemcode': 'ITEM999'}
        )

        # Create PO detail
        self.po_detail = SdCustPoDetails.objects.create(
            poid=self.po,
            itemid=self.item,
            totalqty=100,
            rate=100.00,
        )

        # Create invoice to edit
        self.invoice = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='EDIT0001',
            poid=self.po,
            pono='PO-EDIT-001',
            customercode='EDIT001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
            # Buyer info
            buyer_name='Original Buyer Name',
            buyer_address='123 Original Street',
            buyer_phone='1111111111',
        )

        # Create invoice detail
        self.invoice_detail = TblaccSalesinvoiceDetails.objects.create(
            mid=self.invoice,
            itemid=self.po_detail,
            reqqty=50,
            rate=100,
            amount=5000,
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

    def test_edit_page_loads_with_invoice_data(self):
        """Test: Edit page loads and displays existing invoice data"""
        page = self.page

        # Navigate to invoice list
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        # Click Edit button for the invoice
        edit_button = page.locator(f'tr:has-text("{self.invoice.invoiceno}") a:has-text("Edit")')
        expect(edit_button).to_be_visible()
        edit_button.click()
        page.wait_for_load_state('networkidle')

        # Verify URL contains edit path
        expect(page).to_have_url(lambda url: '/edit/' in url)

        # Verify invoice number is displayed (readonly or label)
        invoice_no_field = page.locator('#id_invoiceno, input[name="invoiceno"]').first
        if invoice_no_field.is_visible():
            expect(invoice_no_field).to_have_value('EDIT0001')

    def test_buyer_tab_prepopulated(self):
        """Test: Buyer tab shows existing data"""
        page = self.page

        # Navigate to edit page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/edit/")
        page.wait_for_load_state('networkidle')

        # Click Buyer tab
        buyer_tab = page.locator('button[data-tab="buyer"], a[href="#buyer"]').first
        if buyer_tab.is_visible():
            buyer_tab.click()
            page.wait_for_timeout(500)

        # Verify buyer name is pre-filled
        buyer_name = page.locator('#id_buyer_name, input[name="buyer_name"]').first
        expect(buyer_name).to_have_value('Original Buyer Name')

        # Verify buyer phone is pre-filled
        buyer_phone = page.locator('#id_buyer_phone, input[name="buyer_phone"]').first
        expect(buyer_phone).to_have_value('1111111111')

    def test_edit_and_save_buyer_info(self):
        """Test: Can edit and save buyer information"""
        page = self.page

        # Navigate to edit page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/edit/")
        page.wait_for_load_state('networkidle')

        # Navigate to buyer tab
        buyer_tab = page.locator('button[data-tab="buyer"], a[href="#buyer"]').first
        if buyer_tab.is_visible():
            buyer_tab.click()
            page.wait_for_timeout(500)

        # Update buyer phone
        buyer_phone = page.locator('#id_buyer_phone, input[name="buyer_phone"]').first
        buyer_phone.fill('9999999999')

        # Submit form
        submit_button = page.locator('button[type="submit"]:has-text("Save"), button:has-text("Update")')
        submit_button.first.click()
        page.wait_for_load_state('networkidle')

        # Verify redirect to list or success message
        expect(page).to_have_url(lambda url: '/sales-invoice' in url)

        # Reload invoice from DB and verify change
        from accounts.models import TblaccSalesinvoiceMaster
        updated_invoice = TblaccSalesinvoiceMaster.objects.get(id=self.invoice.id)
        assert updated_invoice.buyer_phone == '9999999999'

    def test_goods_tab_shows_existing_items(self):
        """Test: Goods tab displays existing invoice items"""
        page = self.page

        # Navigate to edit page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/edit/")
        page.wait_for_load_state('networkidle')

        # Navigate to goods tab
        goods_tab = page.locator('button[data-tab="goods"], a[href="#goods"]').first
        if goods_tab.is_visible():
            goods_tab.click()
            page.wait_for_timeout(500)

        # Verify quantity field shows 50 (existing quantity)
        qty_field = page.locator('input[name*="reqqty"], input[name*="quantity"]').first
        expect(qty_field).to_have_value('50')

        # Verify rate shows 100
        rate_field = page.locator('input[name*="rate"]').first
        expect(rate_field).to_have_value('100')

    def test_remaining_qty_excludes_current_invoice(self):
        """Test: Remaining quantity calculation excludes current invoice"""
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails

        page = self.page

        # Create second invoice with qty=30 (total PO qty = 100)
        invoice2 = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='EDIT0002',
            poid=self.po,
            pono='PO-EDIT-001',
            customercode='EDIT001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        TblaccSalesinvoiceDetails.objects.create(
            mid=invoice2,
            itemid=self.po_detail,
            reqqty=30,
            rate=100,
            amount=3000,
        )

        # Now:
        # - Original invoice (EDIT0001): qty=50
        # - Second invoice (EDIT0002): qty=30
        # - Total used: 80
        # - Remaining: 20

        # When editing EDIT0001, remaining should be:
        # 100 (total) - 30 (EDIT0002) = 70 (excluding current invoice's 50)

        # Navigate to edit page for first invoice
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/edit/")
        page.wait_for_load_state('networkidle')

        # Try to change quantity to 80 (should fail - only 70 available)
        goods_tab = page.locator('button[data-tab="goods"], a[href="#goods"]').first
        if goods_tab.is_visible():
            goods_tab.click()
            page.wait_for_timeout(500)

        qty_field = page.locator('input[name*="reqqty"], input[name*="quantity"]').first
        qty_field.fill('80')

        # Submit
        submit_button = page.locator('button[type="submit"]:has-text("Save"), button:has-text("Update")')
        submit_button.first.click()
        page.wait_for_load_state('networkidle')

        # Should show error (exceeds remaining quantity)
        error_message = page.locator('.error, .alert-danger, text=/exceed/i, text=/remaining/i')
        expect(error_message.first).to_be_visible()

    def test_edit_preserves_unchanged_fields(self):
        """Test: Editing one field doesn't clear others"""
        page = self.page

        # Navigate to edit page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/edit/")
        page.wait_for_load_state('networkidle')

        # Just change buyer address
        buyer_tab = page.locator('button[data-tab="buyer"], a[href="#buyer"]').first
        if buyer_tab.is_visible():
            buyer_tab.click()
            page.wait_for_timeout(500)

        buyer_address = page.locator('#id_buyer_address, textarea[name="buyer_address"]').first
        buyer_address.fill('456 New Street')

        # Submit
        submit_button = page.locator('button[type="submit"]:has-text("Save"), button:has-text("Update")')
        submit_button.first.click()
        page.wait_for_load_state('networkidle')

        # Verify from DB
        from accounts.models import TblaccSalesinvoiceMaster
        updated_invoice = TblaccSalesinvoiceMaster.objects.get(id=self.invoice.id)

        # Address changed
        assert updated_invoice.buyer_address == '456 New Street'

        # Other fields preserved
        assert updated_invoice.buyer_name == 'Original Buyer Name'
        assert updated_invoice.buyer_phone == '1111111111'

    def test_cannot_edit_nonexistent_invoice(self):
        """Test: Editing non-existent invoice shows 404"""
        page = self.page

        # Try to edit invoice with invalid ID
        page.goto("http://localhost:8000/accounts/sales-invoice/99999/edit/")
        page.wait_for_load_state('networkidle')

        # Should show 404 or error message
        error_content = page.content()
        assert '404' in error_content or 'not found' in error_content.lower()
