"""
Views for the Accounts module.
Re-exports all views from the organized submodules.
"""

# Dashboard views
from .dashboard import AccountsDashboardView, MastersDashboardView, TransactionsDashboardView

# Master views
from .masters import *

# Transaction views
from .transactions import *

# Reconciliation views
from .reconciliation import (
    BankReconciliationView, MarkAsReconciledView, ReconciliationSummaryView,
    BankReconciliationMarkView, BankChargesAddView, BankReconciliationListView
)

# HTMX/AJAX endpoint views
from .htmx_endpoints import (
    GetStatesView, GetCitiesView, GetAssetSubcategoriesView,
    GetStatesJSONView, GetCitiesJSONView
)

# Report views
from .reports import BalanceSheetView, ProfitLossView, TrialBalanceView, LedgerView, AgingReportView

# Creditors/Debitors views
from .creditors_debitors import (
    CreditorsDebitorsListView, CreditorsTabView, DebitorsTabView,
    CreditorCreateView, CreditorDeleteView,
    DebitorCreateView, DebitorDeleteView,
    CreditorsDetailView, DebitorsDetailView,
    SundryCreditorsView, SundryCreditorsCategoryView
)

# Explicitly list all exports for clarity
__all__ = [
    # Dashboards
    'AccountsDashboardView', 'MastersDashboardView', 'TransactionsDashboardView',
    
    # Masters
    'AccHeadListView', 'AccHeadCreateView', 'AccHeadUpdateView', 'AccHeadDeleteView',
    'BankListView', 'BankCreateView', 'BankUpdateView', 'BankDeleteView',
    'CurrencyListView', 'CurrencyCreateView', 'CurrencyUpdateView', 'CurrencyDeleteView',
    'PaymentTermsListView', 'PaymentTermsCreateView', 'PaymentTermsUpdateView', 'PaymentTermsDeleteView',
    'TDSCodeListView', 'TDSCodeCreateView', 'TDSCodeUpdateView', 'TDSCodeDeleteView',
    'ExcisableCommodityListView', 'ExcisableCommodityCreateView', 'ExcisableCommodityUpdateView', 'ExcisableCommodityDeleteView',
    'ExciseListView', 'ExciseCreateView', 'ExciseUpdateView', 'ExciseDeleteView',
    'FreightListView', 'FreightCreateView', 'FreightUpdateView', 'FreightDeleteView',
    'IOUReasonsListView', 'IOUReasonsCreateView', 'IOUReasonsUpdateView', 'IOUReasonsDeleteView',
    'IntrestTypeListView', 'IntrestTypeCreateView', 'IntrestTypeUpdateView', 'IntrestTypeDeleteView',
    'InvoiceAgainstListView', 'InvoiceAgainstCreateView', 'InvoiceAgainstUpdateView', 'InvoiceAgainstDeleteView',
    'LoanTypeListView', 'LoanTypeCreateView', 'LoanTypeUpdateView', 'LoanTypeDeleteView',
    'OctoriListView', 'OctoriCreateView', 'OctoriUpdateView', 'OctoriDeleteView',
    'PackingForwardingListView', 'PackingForwardingCreateView', 'PackingForwardingUpdateView', 'PackingForwardingDeleteView',
    'PaidTypeListView', 'PaidTypeCreateView', 'PaidTypeUpdateView', 'PaidTypeDeleteView',
    'PaymentReceiptAgainstListView', 'PaymentReceiptAgainstCreateView', 'PaymentReceiptAgainstUpdateView', 'PaymentReceiptAgainstDeleteView',
    'PaymentModeListView', 'PaymentModeCreateView', 'PaymentModeUpdateView', 'PaymentModeDeleteView',
    'TourExpencessListView', 'TourExpencessCreateView', 'TourExpencessUpdateView', 'TourExpencessDeleteView',
    'VATListView', 'VATCreateView', 'VATUpdateView', 'VATDeleteView',
    'WarrentyTermsListView', 'WarrentyTermsCreateView', 'WarrentyTermsUpdateView', 'WarrentyTermsDeleteView',
    'CapitalListView', 'CapitalCreateView', 'CapitalUpdateView', 'CapitalDeleteView',
    'LoanListView', 'LoanCreateView', 'LoanUpdateView', 'LoanDeleteView',
    
    # Transactions
    'BankVoucherListView', 'BankVoucherCreateView', 'BankVoucherUpdateView', 'BankVoucherDeleteView', 'BankVoucherPrintView',
    'CashVoucherPaymentListView', 'CashVoucherPaymentCreateView', 'CashVoucherPaymentUpdateView', 'CashVoucherPaymentDeleteView',
    'CashVoucherReceiptListView', 'CashVoucherReceiptCreateView', 'CashVoucherReceiptUpdateView', 'CashVoucherReceiptDeleteView',
    'CashVoucherPaymentPrintView', 'CashVoucherReceiptPrintView',
    'JournalEntryListView', 'JournalEntryCreateView', 'JournalEntryUpdateView', 'JournalEntryDeleteView',
    'ContraEntryListView', 'ContraEntryCreateView', 'ContraEntryUpdateView', 'ContraEntryDeleteView',
    'BillBookingListView', 'BillBookingCreateView', 'BillBookingUpdateView', 'BillBookingDeleteView',
    'BillBookingAuthorizeView', 'BillBookingAttachmentUploadView', 'BillBookingAttachmentDownloadView',
    'BillBookingAttachmentDeleteView', 'BillBookingPrintView',
    'SalesInvoiceListView', 'SalesInvoiceCreateView', 'SalesInvoiceUpdateView', 'SalesInvoiceDeleteView', 'SalesInvoicePrintView',
    'ServiceTaxInvoiceListView', 'ServiceTaxInvoiceCreateView', 'ServiceTaxInvoiceUpdateView', 'ServiceTaxInvoiceDeleteView', 'ServiceTaxInvoicePrintView',
    'AdvicePaymentListView', 'AdvicePaymentCreateView', 'AdvicePaymentUpdateView', 'AdvicePaymentDeleteView', 'AdvicePaymentPrintView',
    'ProformaInvoiceListView', 'ProformaInvoiceCreateView', 'ProformaInvoiceUpdateView', 'ProformaInvoiceDeleteView',
    'ProformaToSalesInvoiceView', 'ProformaInvoicePrintView',
    'DebitNoteListView', 'DebitNoteCreateView', 'DebitNoteUpdateView', 'DebitNoteDeleteView',
    'CreditNoteListView', 'CreditNoteCreateView', 'CreditNoteUpdateView', 'CreditNoteDeleteView',
    'AssetRegisterListView', 'AssetRegisterCreateView', 'AssetRegisterUpdateView', 'AssetRegisterDeleteView', 'AssetDisposalView',
    'TourVoucherListView', 'TourVoucherCreateView', 'TourVoucherUpdateView', 'TourVoucherDeleteView', 'TourVoucherPrintView',
    'IOUListView', 'IOUCreateView', 'IOUUpdateView', 'IOUDeleteView', 'IOUAuthorizeView', 'IOUReceiveView',
    
    # Reconciliation
    'BankReconciliationView', 'MarkAsReconciledView', 'ReconciliationSummaryView',
    'BankReconciliationMarkView', 'BankChargesAddView', 'BankReconciliationListView',
    
    # HTMX Endpoints
    'GetStatesView', 'GetCitiesView', 'GetAssetSubcategoriesView',
    'GetStatesJSONView', 'GetCitiesJSONView',
    
    # Reports
    'BalanceSheetView', 'ProfitLossView', 'TrialBalanceView', 'LedgerView', 'AgingReportView',

    # Creditors/Debitors
    'CreditorsDebitorsListView', 'CreditorsTabView', 'DebitorsTabView',
    'CreditorCreateView', 'CreditorDeleteView',
    'DebitorCreateView', 'DebitorDeleteView',
    'CreditorsDetailView', 'DebitorsDetailView',
    'SundryCreditorsView', 'SundryCreditorsCategoryView',
]
