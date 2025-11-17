"""
Test Suite for Sales Invoice Delete View

Tests the ability to delete existing invoices including:
- Loading delete confirmation page
- Successful deletion with quantity restoration to PO
- Cancel delete operation
- 404 handling for non-existent invoices
- Verification that deletion affects database
"""
import pytest
from playwright.sync_api import Page, expect
from datetime import datetime


class TestSalesInvoiceDeleteView:
    """Test invoice delete functionality"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, db):
        """Setup: Create test invoice and login"""
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails
        from sales_distribution.models import SdCustMaster, SdCustPoMaster, SdCustPoDetails
        from design.models import TbldgItemMaster

        # Create customer
        self.customer = SdCustMaster.objects.create(
            customercode='DEL001',
            customername='Delete Test Customer',
            compid_id=1,
        )

        # Create PO
        self.po = SdCustPoMaster.objects.create(
            pono='PO-DEL-001',
            customerid=self.customer,
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
        )

        # Create item
        self.item, _ = TbldgItemMaster.objects.get_or_create(
            itemid=888,
            defaults={'itemname': 'Test Delete Item', 'itemcode': 'ITEM888'}
        )

        # Create PO detail with total qty 100
        self.po_detail = SdCustPoDetails.objects.create(
            poid=self.po,
            itemid=self.item,
            totalqty=100,
            rate=100.00,
        )

        # Create invoice to delete
        self.invoice = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='DEL0001',
            poid=self.po,
            pono='PO-DEL-001',
            customercode='DEL001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=1,
            finyearid_id=1,
            buyer_name='Delete Test Buyer',
        )

        # Create invoice detail with qty 50
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

    def test_delete_confirmation_page_loads(self):
        """Test: Delete confirmation page loads correctly"""
        page = self.page

        # Navigate to invoice list
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        # Click Delete button for the invoice
        delete_button = page.locator(f'tr:has-text("{self.invoice.invoiceno}") a:has-text("Delete")')
        expect(delete_button).to_be_visible()
        delete_button.click()
        page.wait_for_load_state('networkidle')

        # Verify URL contains delete path
        expect(page).to_have_url(lambda url: '/delete/' in url)

        # Verify confirmation message is displayed
        confirmation_text = page.locator('text=/Are you sure/i, text=/confirm/i, text=/delete/i').first
        expect(confirmation_text).to_be_visible()

        # Verify invoice number is displayed
        invoice_display = page.locator(f'text=/DEL0001/i, text=/Invoice.*DEL0001/i').first
        expect(invoice_display).to_be_visible()

    def test_successful_deletion_removes_from_database(self):
        """Test: Clicking confirm deletes invoice from database"""
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails

        page = self.page

        # Verify invoice exists before deletion
        assert TblaccSalesinvoiceMaster.objects.filter(id=self.invoice.id).exists()
        assert TblaccSalesinvoiceDetails.objects.filter(mid=self.invoice).exists()

        # Navigate to delete page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/delete/")
        page.wait_for_load_state('networkidle')

        # Click confirm delete button
        confirm_button = page.locator(
            'button[type="submit"]:has-text("Delete"), '
            'button:has-text("Confirm"), '
            'button:has-text("Yes")'
        )
        confirm_button.first.click()
        page.wait_for_load_state('networkidle')

        # Should redirect to list page
        expect(page).to_have_url(lambda url: '/sales-invoice' in url and '/delete/' not in url)

        # Verify success message
        success_message = page.locator('.alert-success, .message-success, text=/deleted successfully/i')
        expect(success_message.first).to_be_visible()

        # Verify invoice deleted from database
        assert not TblaccSalesinvoiceMaster.objects.filter(id=self.invoice.id).exists()
        assert not TblaccSalesinvoiceDetails.objects.filter(mid_id=self.invoice.id).exists()

    def test_deletion_restores_quantity_to_po(self):
        """Test: Deleting invoice restores quantity back to PO"""
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails
        from sales_distribution.models import SdCustPoDetails

        page = self.page

        # Create second invoice with qty 30
        invoice2 = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='DEL0002',
            poid=self.po,
            pono='PO-DEL-001',
            customercode='DEL001',
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
        # - Invoice 1 (DEL0001): qty=50
        # - Invoice 2 (DEL0002): qty=30
        # - Total invoiced: 80
        # - Remaining: 20 (out of 100 total)

        # Delete first invoice (qty=50)
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/delete/")
        page.wait_for_load_state('networkidle')

        confirm_button = page.locator('button[type="submit"]:has-text("Delete"), button:has-text("Confirm")').first
        confirm_button.click()
        page.wait_for_load_state('networkidle')

        # After deletion:
        # - Only Invoice 2 exists: qty=30
        # - Remaining should be: 70 (100 - 30)

        # Verify remaining quantity calculation
        # Try to create new invoice with qty=70 (should succeed)
        page.goto("http://localhost:8000/accounts/sales-invoice/select-po/")
        page.wait_for_load_state('networkidle')

        # The remaining qty should now allow up to 70
        # This is indirectly verified by the quantity validation
        # Direct verification: check that sum of invoiced qty is now only 30
        total_invoiced = TblaccSalesinvoiceDetails.objects.filter(
            itemid=self.po_detail,
            mid__compid=1
        ).aggregate(total=models.Sum('reqqty'))['total'] or 0

        assert total_invoiced == 30, f"Expected 30, got {total_invoiced}"

    def test_cancel_delete_operation(self):
        """Test: Clicking cancel preserves the invoice"""
        from accounts.models import TblaccSalesinvoiceMaster

        page = self.page

        # Navigate to delete page
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/delete/")
        page.wait_for_load_state('networkidle')

        # Click cancel button
        cancel_button = page.locator(
            'a:has-text("Cancel"), '
            'button:has-text("Cancel"), '
            'a:has-text("Back")'
        )
        cancel_button.first.click()
        page.wait_for_load_state('networkidle')

        # Should redirect to list page
        expect(page).to_have_url(lambda url: '/sales-invoice' in url and '/delete/' not in url)

        # Verify invoice still exists in database
        assert TblaccSalesinvoiceMaster.objects.filter(id=self.invoice.id).exists()

    def test_delete_nonexistent_invoice_shows_404(self):
        """Test: Deleting non-existent invoice shows 404"""
        page = self.page

        # Try to delete invoice with invalid ID
        page.goto("http://localhost:8000/accounts/sales-invoice/99999/delete/")
        page.wait_for_load_state('networkidle')

        # Should show 404 or error message
        error_content = page.content()
        assert '404' in error_content or 'not found' in error_content.lower()

    def test_delete_removes_invoice_from_list(self):
        """Test: Deleted invoice no longer appears in list view"""
        page = self.page

        # Navigate to list and verify invoice is present
        page.goto("http://localhost:8000/accounts/sales-invoice/")
        page.wait_for_load_state('networkidle')

        invoice_row = page.locator(f'tr:has-text("{self.invoice.invoiceno}")')
        expect(invoice_row).to_be_visible()

        # Delete the invoice
        delete_button = invoice_row.locator('a:has-text("Delete")')
        delete_button.click()
        page.wait_for_load_state('networkidle')

        # Confirm deletion
        confirm_button = page.locator('button[type="submit"]:has-text("Delete"), button:has-text("Confirm")').first
        confirm_button.click()
        page.wait_for_load_state('networkidle')

        # Verify invoice row is no longer in the list
        invoice_row_after = page.locator(f'tr:has-text("{self.invoice.invoiceno}")')
        expect(invoice_row_after).not_to_be_visible()

    def test_delete_with_multiple_items_restores_all_quantities(self):
        """Test: Deleting invoice with multiple items restores all quantities"""
        from accounts.models import TblaccSalesinvoiceDetails
        from sales_distribution.models import SdCustPoDetails
        from design.models import TbldgItemMaster

        page = self.page

        # Create second item
        item2, _ = TbldgItemMaster.objects.get_or_create(
            itemid=777,
            defaults={'itemname': 'Test Delete Item 2', 'itemcode': 'ITEM777'}
        )

        # Create PO detail for second item
        po_detail2 = SdCustPoDetails.objects.create(
            poid=self.po,
            itemid=item2,
            totalqty=200,
            rate=50.00,
        )

        # Add second item to invoice
        TblaccSalesinvoiceDetails.objects.create(
            mid=self.invoice,
            itemid=po_detail2,
            reqqty=100,
            rate=50,
            amount=5000,
        )

        # Now invoice has:
        # - Item 888: qty=50 (out of 100 total)
        # - Item 777: qty=100 (out of 200 total)

        # Delete invoice
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{self.invoice.id}/delete/")
        page.wait_for_load_state('networkidle')

        confirm_button = page.locator('button[type="submit"]:has-text("Delete"), button:has-text("Confirm")').first
        confirm_button.click()
        page.wait_for_load_state('networkidle')

        # Verify both items have quantities restored
        # Item 888: should have 100 available (0 invoiced)
        # Item 777: should have 200 available (0 invoiced)

        from django.db import models
        total_item1 = TblaccSalesinvoiceDetails.objects.filter(
            itemid=self.po_detail,
            mid__compid=1
        ).aggregate(total=models.Sum('reqqty'))['total'] or 0

        total_item2 = TblaccSalesinvoiceDetails.objects.filter(
            itemid=po_detail2,
            mid__compid=1
        ).aggregate(total=models.Sum('reqqty'))['total'] or 0

        assert total_item1 == 0, f"Item 1 should have 0 invoiced, got {total_item1}"
        assert total_item2 == 0, f"Item 2 should have 0 invoiced, got {total_item2}"

    def test_cannot_delete_invoice_from_another_company(self):
        """Test: Cannot delete invoice from different company (security)"""
        from accounts.models import TblaccSalesinvoiceMaster

        page = self.page

        # Create invoice with different company ID
        other_invoice = TblaccSalesinvoiceMaster.objects.create(
            invoiceno='OTHER0001',
            poid=self.po,
            pono='PO-DEL-001',
            customercode='DEL001',
            sysdate=datetime.now().strftime('%d-%m-%Y'),
            compid_id=999,  # Different company
            finyearid_id=1,
        )

        # Try to delete it (should fail - 404 or permission denied)
        page.goto(f"http://localhost:8000/accounts/sales-invoice/{other_invoice.id}/delete/")
        page.wait_for_load_state('networkidle')

        # Should show error (404 or permission denied)
        error_content = page.content()
        is_error = '404' in error_content or 'not found' in error_content.lower() or \
                   'permission' in error_content.lower() or 'access denied' in error_content.lower()

        assert is_error, "Should not allow deleting invoice from another company"

        # Verify invoice still exists
        assert TblaccSalesinvoiceMaster.objects.filter(id=other_invoice.id).exists()
