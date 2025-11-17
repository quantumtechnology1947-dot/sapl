"""
Transaction views for the Accounts module.
"""

from .bank_voucher import BankVoucherListView, BankVoucherCreateView, BankVoucherUpdateView, BankVoucherDeleteView, BankVoucherPrintView
from .cash_voucher import (
    CashVoucherPaymentListView, CashVoucherPaymentCreateView, CashVoucherPaymentUpdateView, CashVoucherPaymentDeleteView,
    CashVoucherReceiptListView, CashVoucherReceiptCreateView, CashVoucherReceiptUpdateView, CashVoucherReceiptDeleteView,
    CashVoucherPaymentPrintView, CashVoucherReceiptPrintView
)
from .journal_entry import JournalEntryListView, JournalEntryCreateView, JournalEntryUpdateView, JournalEntryDeleteView
from .contra_entry import ContraEntryListView, ContraEntryCreateView, ContraEntryUpdateView, ContraEntryDeleteView
from .bill_booking import (
    BillBookingAuthorizeListView,
    BillBookingListView, BillBookingCreateView, BillBookingUpdateView, BillBookingDeleteView,
    BillBookingAuthorizeView, BillBookingAttachmentUploadView, BillBookingAttachmentDownloadView,
    BillBookingAttachmentDeleteView, BillBookingPrintView
)
# Sales Invoice - Comprehensive implementation
from .sales_invoice import (
    SalesInvoicePOSelectionView, SalesInvoiceCreateView, SalesInvoiceListView,
    SalesInvoiceUpdateView, SalesInvoiceDeleteView, SalesInvoicePrintView,
    CustomerAutocompleteView, GetStatesView, GetCitiesView,
    GetCommodityTariffView, SearchCustomerView, CopyBuyerToConsigneeView,
    CalculateRemainingQuantityView
)
# Service Tax Invoice
from .service_tax_invoice import (
    service_tax_invoice_list, service_tax_invoice_create,
    service_tax_invoice_edit, service_tax_invoice_delete,
    service_tax_invoice_print, get_states_by_country,
    get_cities_by_state, customer_autocomplete, copy_buyer_to_consignee
)
from .proforma_invoice import (
    ProformaInvoiceListView, ProformaInvoiceCreateView, ProformaInvoiceUpdateView, ProformaInvoiceDeleteView,
    ProformaToSalesInvoiceView, ProformaInvoicePrintView
)
from .debit_note import (
    DebitNoteListView, DebitNoteCreateView, DebitNoteUpdateView, DebitNoteDeleteView,
    CreditNoteListView, CreditNoteCreateView, CreditNoteUpdateView, CreditNoteDeleteView
)
from .asset_register import AssetRegisterListView, AssetRegisterCreateView, AssetRegisterUpdateView, AssetRegisterDeleteView, AssetDisposalView
from .tour_voucher import TourVoucherListView, TourVoucherCreateView, TourVoucherUpdateView, TourVoucherDeleteView, TourVoucherPrintView
from .iou import IOUListView, IOUCreateView, IOUUpdateView, IOUDeleteView, IOUAuthorizeView, IOUReceiveView
from .iou_payment_receipt import (
    IOUPaymentReceiptView, IOUPaymentDeleteView, IOUPaymentAuthorizeView,
    IOUReceiptDeleteView, IOUReceiptAddView
)
from .advice import (
    AdviceView, AdviceAutocompleteView, AdviceInsertTempView,
    AdviceDeleteTempView, AdviceProceedView,
    AdviceSearchBillsView, AdviceAddBillToTempView,
    AdviceDeleteCreditorTempView, AdviceProceedCreditorView,
    AdviceSalaryInsertTempView, AdviceSalaryDeleteTempView, AdviceSalaryProceedView,
    AdviceOthersInsertTempView, AdviceOthersDeleteTempView, AdviceOthersProceedView
)
from .policy import PolicyListView, PolicyUploadView, PolicyDownloadView

__all__ = [
    'BankVoucherListView', 'BankVoucherCreateView', 'BankVoucherUpdateView', 'BankVoucherDeleteView', 'BankVoucherPrintView',
    'CashVoucherPaymentListView', 'CashVoucherPaymentCreateView', 'CashVoucherPaymentUpdateView', 'CashVoucherPaymentDeleteView',
    'CashVoucherReceiptListView', 'CashVoucherReceiptCreateView', 'CashVoucherReceiptUpdateView', 'CashVoucherReceiptDeleteView',
    'CashVoucherPaymentPrintView', 'CashVoucherReceiptPrintView',
    'JournalEntryListView', 'JournalEntryCreateView', 'JournalEntryUpdateView', 'JournalEntryDeleteView',
    'ContraEntryListView', 'ContraEntryCreateView', 'ContraEntryUpdateView', 'ContraEntryDeleteView',
    'BillBookingListView', 'BillBookingCreateView', 'BillBookingUpdateView', 'BillBookingDeleteView',
    'BillBookingAuthorizeView', 'BillBookingAuthorizeListView', 'BillBookingAttachmentUploadView', 'BillBookingAttachmentDownloadView',
    'BillBookingAttachmentDeleteView', 'BillBookingPrintView',
    'SalesInvoicePOSelectionView', 'SalesInvoiceCreateView', 'SalesInvoiceListView',
    'SalesInvoiceUpdateView', 'SalesInvoiceDeleteView', 'SalesInvoicePrintView',
    'CustomerAutocompleteView', 'GetStatesView', 'GetCitiesView',
    'GetCommodityTariffView', 'SearchCustomerView', 'CopyBuyerToConsigneeView',
    'CalculateRemainingQuantityView',
    'ProformaInvoiceListView', 'ProformaInvoiceCreateView', 'ProformaInvoiceUpdateView', 'ProformaInvoiceDeleteView',
    'ProformaToSalesInvoiceView', 'ProformaInvoicePrintView',
    'DebitNoteListView', 'DebitNoteCreateView', 'DebitNoteUpdateView', 'DebitNoteDeleteView',
    'CreditNoteListView', 'CreditNoteCreateView', 'CreditNoteUpdateView', 'CreditNoteDeleteView',
    'AssetRegisterListView', 'AssetRegisterCreateView', 'AssetRegisterUpdateView', 'AssetRegisterDeleteView', 'AssetDisposalView',
    'TourVoucherListView', 'TourVoucherCreateView', 'TourVoucherUpdateView', 'TourVoucherDeleteView', 'TourVoucherPrintView',
    'IOUListView', 'IOUCreateView', 'IOUUpdateView', 'IOUDeleteView', 'IOUAuthorizeView', 'IOUReceiveView',
    'IOUPaymentReceiptView', 'IOUPaymentDeleteView', 'IOUPaymentAuthorizeView', 'IOUReceiptDeleteView', 'IOUReceiptAddView',
    'AdviceView', 'AdviceAutocompleteView', 'AdviceInsertTempView', 'AdviceDeleteTempView', 'AdviceProceedView',
    'AdviceSearchBillsView', 'AdviceAddBillToTempView', 'AdviceDeleteCreditorTempView', 'AdviceProceedCreditorView',
    'AdviceSalaryInsertTempView', 'AdviceSalaryDeleteTempView', 'AdviceSalaryProceedView',
    'AdviceOthersInsertTempView', 'AdviceOthersDeleteTempView', 'AdviceOthersProceedView',
    'PolicyListView', 'PolicyUploadView', 'PolicyDownloadView',
    'service_tax_invoice_list', 'service_tax_invoice_create', 'service_tax_invoice_edit',
    'service_tax_invoice_delete', 'service_tax_invoice_print', 'get_states_by_country',
    'get_cities_by_state', 'customer_autocomplete', 'copy_buyer_to_consignee',
]
