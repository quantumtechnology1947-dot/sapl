"""
URL patterns for the Accounts module.
"""

from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # ========================================================================
    # Dashboards
    # ========================================================================
    path('', views.AccountsDashboardView.as_view(), name='dashboard'),
    path('masters/', views.MastersDashboardView.as_view(), name='masters-dashboard'),
    path('transactions/', views.TransactionsDashboardView.as_view(), name='transactions-dashboard'),
    
    # ========================================================================
    # Master Data URLs - Account Head
    # ========================================================================
    path('masters/acchead/', views.AccHeadListView.as_view(), name='acchead-list'),
    path('masters/acchead/create/', views.AccHeadCreateView.as_view(), name='acchead-create'),
    path('masters/acchead/<int:id>/edit/', views.AccHeadUpdateView.as_view(), name='acchead-edit'),
    path('masters/acchead/<int:id>/delete/', views.AccHeadDeleteView.as_view(), name='acchead-delete'),
    
    # ========================================================================
    # Master Data URLs - Bank
    # ========================================================================
    path('masters/bank/', views.BankListView.as_view(), name='bank-list'),
    path('masters/bank/create/', views.BankCreateView.as_view(), name='bank-create'),
    path('masters/bank/<int:id>/edit/', views.BankUpdateView.as_view(), name='bank-edit'),
    path('masters/bank/<int:id>/delete/', views.BankDeleteView.as_view(), name='bank-delete'),
    
    # ========================================================================
    # Master Data URLs - Currency
    # ========================================================================
    path('masters/currency/', views.CurrencyListView.as_view(), name='currency-list'),
    path('masters/currency/create/', views.CurrencyCreateView.as_view(), name='currency-create'),
    path('masters/currency/<int:id>/edit/', views.CurrencyUpdateView.as_view(), name='currency-edit'),
    path('masters/currency/<int:id>/delete/', views.CurrencyDeleteView.as_view(), name='currency-delete'),
    
    # ========================================================================
    # Master Data URLs - Payment Terms
    # ========================================================================
    path('masters/payment-terms/', views.PaymentTermsListView.as_view(), name='payment-terms-list'),
    path('masters/payment-terms/create/', views.PaymentTermsCreateView.as_view(), name='payment-terms-create'),
    path('masters/payment-terms/<int:id>/edit/', views.PaymentTermsUpdateView.as_view(), name='payment-terms-edit'),
    path('masters/payment-terms/<int:id>/delete/', views.PaymentTermsDeleteView.as_view(), name='payment-terms-delete'),
    
    # ========================================================================
    # Master Data URLs - TDS Code
    # ========================================================================
    path('masters/tds-code/', views.TDSCodeListView.as_view(), name='tds-code-list'),
    path('masters/tds-code/create/', views.TDSCodeCreateView.as_view(), name='tds-code-create'),
    path('masters/tds-code/<int:id>/edit/', views.TDSCodeUpdateView.as_view(), name='tds-code-edit'),
    path('masters/tds-code/<int:id>/delete/', views.TDSCodeDeleteView.as_view(), name='tds-code-delete'),
    
    # ========================================================================
    # Master Data URLs - GST (CGST/SGST/IGST)
    # ========================================================================
    # TODO: Implement GST views
    # path('masters/gst/', views.GSTListView.as_view(), name='gst-list'),
    # path('masters/gst/create/', views.GSTCreateView.as_view(), name='gst-create'),
    # path('masters/gst/<int:pk>/edit/', views.GSTUpdateView.as_view(), name='gst-edit'),
    # path('masters/gst/<int:pk>/delete/', views.GSTDeleteView.as_view(), name='gst-delete'),
    
    # ========================================================================
    # Transaction URLs - Bank Voucher
    # ========================================================================
    path('transactions/bank-voucher/', views.BankVoucherListView.as_view(), name='bank-voucher-list'),
    path('transactions/bank-voucher/create/', views.BankVoucherCreateView.as_view(), name='bank-voucher-create'),
    path('transactions/bank-voucher/<int:id>/edit/', views.BankVoucherUpdateView.as_view(), name='bank-voucher-edit'),
    path('transactions/bank-voucher/<int:id>/delete/', views.BankVoucherDeleteView.as_view(), name='bank-voucher-delete'),
    path('transactions/bank-voucher/<int:id>/print/', views.BankVoucherPrintView.as_view(), name='bank-voucher-print'),

    # ========================================================================
    # Transaction URLs - Cash Voucher Payment
    # ========================================================================
    path('transactions/cash-voucher-payment/', views.CashVoucherPaymentListView.as_view(), name='cash-voucher-payment-list'),
    path('transactions/cash-voucher-payment/create/', views.CashVoucherPaymentCreateView.as_view(), name='cash-voucher-payment-create'),
    path('transactions/cash-voucher-payment/<int:id>/edit/', views.CashVoucherPaymentUpdateView.as_view(), name='cash-voucher-payment-edit'),
    path('transactions/cash-voucher-payment/<int:id>/delete/', views.CashVoucherPaymentDeleteView.as_view(), name='cash-voucher-payment-delete'),
    path('transactions/cash-voucher-payment/<int:id>/print/', views.CashVoucherPaymentPrintView.as_view(), name='cash-voucher-payment-print'),

    # ========================================================================
    # Transaction URLs - Cash Voucher Receipt
    # ========================================================================
    path('transactions/cash-voucher-receipt/', views.CashVoucherReceiptListView.as_view(), name='cash-voucher-receipt-list'),
    path('transactions/cash-voucher-receipt/create/', views.CashVoucherReceiptCreateView.as_view(), name='cash-voucher-receipt-create'),
    path('transactions/cash-voucher-receipt/<int:id>/edit/', views.CashVoucherReceiptUpdateView.as_view(), name='cash-voucher-receipt-edit'),
    path('transactions/cash-voucher-receipt/<int:id>/delete/', views.CashVoucherReceiptDeleteView.as_view(), name='cash-voucher-receipt-delete'),
    path('transactions/cash-voucher-receipt/<int:id>/print/', views.CashVoucherReceiptPrintView.as_view(), name='cash-voucher-receipt-print'),

    # ========================================================================
    # Transaction URLs - Journal Entry
    # ========================================================================
    path('transactions/journal-entry/', views.JournalEntryListView.as_view(), name='journal-entry-list'),
    path('transactions/journal-entry/create/', views.JournalEntryCreateView.as_view(), name='journal-entry-create'),
    path('transactions/journal-entry/<int:id>/edit/', views.JournalEntryUpdateView.as_view(), name='journal-entry-edit'),
    path('transactions/journal-entry/<int:id>/delete/', views.JournalEntryDeleteView.as_view(), name='journal-entry-delete'),
    
    # ========================================================================
    # Transaction URLs - Contra Entry
    # ========================================================================
    path('transactions/contra-entry/', views.ContraEntryListView.as_view(), name='contra-entry-list'),
    path('transactions/contra-entry/create/', views.ContraEntryCreateView.as_view(), name='contra-entry-create'),
    path('transactions/contra-entry/<int:id>/edit/', views.ContraEntryUpdateView.as_view(), name='contra-entry-edit'),
    path('transactions/contra-entry/<int:id>/delete/', views.ContraEntryDeleteView.as_view(), name='contra-entry-delete'),

    # ========================================================================
    # Transaction URLs - Advice Payment
    # ========================================================================
    path('transactions/advice/', views.AdvicePaymentListView.as_view(), name='advice-list'),
    path('transactions/advice/create/', views.AdvicePaymentCreateView.as_view(), name='advice-create'),
    path('transactions/advice/<int:advice_id>/edit/', views.AdvicePaymentUpdateView.as_view(), name='advice-edit'),
    path('transactions/advice/<int:advice_id>/delete/', views.AdvicePaymentDeleteView.as_view(), name='advice-delete'),
    path('transactions/advice/<int:advice_id>/print/', views.AdvicePaymentPrintView.as_view(), name='advice-print'),

    # ========================================================================
    # Transaction URLs - Capital Particulars
    # ========================================================================
    path('transactions/capital/', views.CapitalListView.as_view(), name='capital-list'),
    path('transactions/capital/create/', views.CapitalCreateView.as_view(), name='capital-create'),
    path('transactions/capital/<int:capital_id>/edit/', views.CapitalUpdateView.as_view(), name='capital-edit'),
    path('transactions/capital/<int:capital_id>/delete/', views.CapitalDeleteView.as_view(), name='capital-delete'),

    # ========================================================================
    # Transaction URLs - Loan Particulars
    # ========================================================================
    path('transactions/loan/', views.LoanListView.as_view(), name='loan-list'),
    path('transactions/loan/create/', views.LoanCreateView.as_view(), name='loan-create'),
    path('transactions/loan/<int:loan_id>/edit/', views.LoanUpdateView.as_view(), name='loan-edit'),
    path('transactions/loan/<int:loan_id>/delete/', views.LoanDeleteView.as_view(), name='loan-delete'),

    # ========================================================================
    # HTMX AJAX Endpoints (Converted to CBVs)
    # ========================================================================
    path('ajax/get-states/', views.GetStatesView.as_view(), name='get-states'),
    path('ajax/get-cities/', views.GetCitiesView.as_view(), name='get-cities'),

    # ========================================================================
    # Invoice URLs - Sales Invoice
    # ========================================================================
    path('invoices/sales-invoice/', views.SalesInvoiceListView.as_view(), name='sales-invoice-list'),
    path('invoices/sales-invoice/create/', views.SalesInvoiceCreateView.as_view(), name='sales-invoice-create'),
    path('invoices/sales-invoice/<int:id>/edit/', views.SalesInvoiceUpdateView.as_view(), name='sales-invoice-edit'),
    path('invoices/sales-invoice/<int:id>/delete/', views.SalesInvoiceDeleteView.as_view(), name='sales-invoice-delete'),
    path('invoices/sales-invoice/<int:id>/print/', views.SalesInvoicePrintView.as_view(), name='sales-invoice-print'),

    # ========================================================================
    # Invoice URLs - Service Tax Invoice
    # ========================================================================
    path('invoices/service-tax-invoice/', views.ServiceTaxInvoiceListView.as_view(), name='service-tax-invoice-list'),
    path('invoices/service-tax-invoice/create/', views.ServiceTaxInvoiceCreateView.as_view(), name='service-tax-invoice-create'),
    path('invoices/service-tax-invoice/<int:id>/edit/', views.ServiceTaxInvoiceUpdateView.as_view(), name='service-tax-invoice-edit'),
    path('invoices/service-tax-invoice/<int:id>/delete/', views.ServiceTaxInvoiceDeleteView.as_view(), name='service-tax-invoice-delete'),
    path('invoices/service-tax-invoice/<int:id>/print/', views.ServiceTaxInvoicePrintView.as_view(), name='service-tax-invoice-print'),


    # ========================================================================
    # Invoice URLs - Bill Booking
    # ========================================================================
    path('invoices/bill-booking/', views.BillBookingListView.as_view(), name='bill-booking-list'),
    path('invoices/bill-booking/create/', views.BillBookingCreateView.as_view(), name='bill-booking-create'),
    path('invoices/bill-booking/<int:id>/edit/', views.BillBookingUpdateView.as_view(), name='bill-booking-edit'),
    path('invoices/bill-booking/<int:id>/delete/', views.BillBookingDeleteView.as_view(), name='bill-booking-delete'),
    path('invoices/bill-booking/<int:id>/authorize/', views.BillBookingAuthorizeView.as_view(), name='bill-booking-authorize'),
    path('invoices/bill-booking/<int:id>/print/', views.BillBookingPrintView.as_view(), name='bill-booking-print'),

    # Bill Booking Attachments
    path('invoices/bill-booking/<int:bill_id>/attachments/upload/', views.BillBookingAttachmentUploadView.as_view(), name='bill-booking-attachment-upload'),
    path('invoices/bill-booking/attachments/<int:attachment_id>/download/', views.BillBookingAttachmentDownloadView.as_view(), name='bill-booking-attachment-download'),
    path('invoices/bill-booking/attachments/<int:attachment_id>/delete/', views.BillBookingAttachmentDeleteView.as_view(), name='bill-booking-attachment-delete'),
    
    # ========================================================================
    # Invoice URLs - Proforma Invoice
    # ========================================================================
    path('invoices/proforma-invoice/', views.ProformaInvoiceListView.as_view(), name='proforma-invoice-list'),
    path('invoices/proforma-invoice/create/', views.ProformaInvoiceCreateView.as_view(), name='proforma-invoice-create'),
    path('invoices/proforma-invoice/<int:id>/edit/', views.ProformaInvoiceUpdateView.as_view(), name='proforma-invoice-edit'),
    path('invoices/proforma-invoice/<int:id>/delete/', views.ProformaInvoiceDeleteView.as_view(), name='proforma-invoice-delete'),
    path('invoices/proforma-invoice/<int:id>/print/', views.ProformaInvoicePrintView.as_view(), name='proforma-invoice-print'),
    path('invoices/proforma-invoice/<int:proforma_id>/convert-to-sales/', views.ProformaToSalesInvoiceView.as_view(), name='proforma-to-sales-invoice'),

    # ========================================================================
    # Invoice URLs - Credit Note
    # ========================================================================
    path('invoices/credit-note/', views.CreditNoteListView.as_view(), name='credit-note-list'),
    path('invoices/credit-note/create/', views.CreditNoteCreateView.as_view(), name='credit-note-create'),
    path('invoices/credit-note/<int:id>/edit/', views.CreditNoteUpdateView.as_view(), name='credit-note-edit'),
    path('invoices/credit-note/<int:id>/delete/', views.CreditNoteDeleteView.as_view(), name='credit-note-delete'),
    
    # ========================================================================
    # Invoice URLs - Debit Note
    # ========================================================================
    path('invoices/debit-note/', views.DebitNoteListView.as_view(), name='debit-note-list'),
    path('invoices/debit-note/create/', views.DebitNoteCreateView.as_view(), name='debit-note-create'),
    path('invoices/debit-note/<int:id>/edit/', views.DebitNoteUpdateView.as_view(), name='debit-note-edit'),
    path('invoices/debit-note/<int:id>/delete/', views.DebitNoteDeleteView.as_view(), name='debit-note-delete'),

    # ========================================================================
    # Tour Voucher URLs
    # ========================================================================
    path('transactions/tour-voucher/', views.TourVoucherListView.as_view(), name='tour-voucher-list'),
    path('transactions/tour-voucher/create/', views.TourVoucherCreateView.as_view(), name='tour-voucher-create'),
    path('transactions/tour-voucher/<int:id>/edit/', views.TourVoucherUpdateView.as_view(), name='tour-voucher-edit'),
    path('transactions/tour-voucher/<int:id>/delete/', views.TourVoucherDeleteView.as_view(), name='tour-voucher-delete'),
    path('transactions/tour-voucher/<int:id>/print/', views.TourVoucherPrintView.as_view(), name='tour-voucher-print'),

    # ========================================================================
    # IOU Payment/Receipt URLs
    # ========================================================================
    path('transactions/iou/', views.IOUListView.as_view(), name='iou-list'),
    path('transactions/iou/create/', views.IOUCreateView.as_view(), name='iou-create'),
    path('transactions/iou/<int:id>/edit/', views.IOUUpdateView.as_view(), name='iou-edit'),
    path('transactions/iou/<int:id>/delete/', views.IOUDeleteView.as_view(), name='iou-delete'),
    path('transactions/iou/<int:id>/authorize/', views.IOUAuthorizeView.as_view(), name='iou-authorize'),
    path('transactions/iou/<int:id>/receive/', views.IOUReceiveView.as_view(), name='iou-receive'),

    # ========================================================================
    # Bank Reconciliation URLs
    # ========================================================================
    path('reconciliation/banks/', views.BankReconciliationListView.as_view(), name='bank-reconciliation-list'),
    path('reconciliation/bank/<int:bank_id>/', views.BankReconciliationView.as_view(), name='bank-reconciliation'),
    path('reconciliation/bank/<int:bank_id>/mark/', views.BankReconciliationMarkView.as_view(), name='bank-reconciliation-mark'),
    path('reconciliation/bank/<int:bank_id>/charges/', views.BankChargesAddView.as_view(), name='bank-charges-add'),
    
    # ========================================================================
    # Asset Register URLs
    # ========================================================================
    path('assets/register/', views.AssetRegisterListView.as_view(), name='asset-register-list'),
    path('assets/register/create/', views.AssetRegisterCreateView.as_view(), name='asset-register-create'),
    path('assets/register/<int:id>/edit/', views.AssetRegisterUpdateView.as_view(), name='asset-register-edit'),
    path('assets/register/<int:id>/delete/', views.AssetRegisterDeleteView.as_view(), name='asset-register-delete'),
    path('assets/register/<int:asset_id>/dispose/', views.AssetDisposalView.as_view(), name='asset-disposal'),
    
    # AJAX endpoint for asset subcategories
    path('ajax/get-asset-subcategories/', views.GetAssetSubcategoriesView.as_view(), name='get-asset-subcategories'),
    
    # ========================================================================
    # Financial Reports URLs
    # ========================================================================
    path('reports/balance-sheet/', views.BalanceSheetView.as_view(), name='balance-sheet'),
    path('reports/profit-loss/', views.ProfitLossView.as_view(), name='profit-loss'),
    path('reports/trial-balance/', views.TrialBalanceView.as_view(), name='trial-balance'),
    path('reports/ledger/', views.LedgerView.as_view(), name='ledger'),
    path('reports/aging/', views.AgingReportView.as_view(), name='aging-report'),

    # ========================================================================
    # Generated Simple Lookup Masters URLs
    # ========================================================================
    path('masters/excisable-commodity/', views.ExcisableCommodityListView.as_view(), name='excisable-commodity-list'),
    path('masters/excisable-commodity/create/', views.ExcisableCommodityCreateView.as_view(), name='excisable-commodity-create'),
    path('masters/excisable-commodity/<int:pk>/edit/', views.ExcisableCommodityUpdateView.as_view(), name='excisable-commodity-edit'),
    path('masters/excisable-commodity/<int:pk>/delete/', views.ExcisableCommodityDeleteView.as_view(), name='excisable-commodity-delete'),

    path('masters/excise/', views.ExciseListView.as_view(), name='excise-list'),
    path('masters/excise/create/', views.ExciseCreateView.as_view(), name='excise-create'),
    path('masters/excise/<int:pk>/edit/', views.ExciseUpdateView.as_view(), name='excise-edit'),
    path('masters/excise/<int:pk>/delete/', views.ExciseDeleteView.as_view(), name='excise-delete'),

    path('masters/freight/', views.FreightListView.as_view(), name='freight-list'),
    path('masters/freight/create/', views.FreightCreateView.as_view(), name='freight-create'),
    path('masters/freight/<int:pk>/edit/', views.FreightUpdateView.as_view(), name='freight-edit'),
    path('masters/freight/<int:pk>/delete/', views.FreightDeleteView.as_view(), name='freight-delete'),

    path('masters/iou-reasons/', views.IOUReasonsListView.as_view(), name='iou-reasons-list'),
    path('masters/iou-reasons/create/', views.IOUReasonsCreateView.as_view(), name='iou-reasons-create'),
    path('masters/iou-reasons/<int:pk>/edit/', views.IOUReasonsUpdateView.as_view(), name='iou-reasons-edit'),
    path('masters/iou-reasons/<int:pk>/delete/', views.IOUReasonsDeleteView.as_view(), name='iou-reasons-delete'),

    path('masters/intrest-type/', views.IntrestTypeListView.as_view(), name='intrest-type-list'),
    path('masters/intrest-type/create/', views.IntrestTypeCreateView.as_view(), name='intrest-type-create'),
    path('masters/intrest-type/<int:pk>/edit/', views.IntrestTypeUpdateView.as_view(), name='intrest-type-edit'),
    path('masters/intrest-type/<int:pk>/delete/', views.IntrestTypeDeleteView.as_view(), name='intrest-type-delete'),

    path('masters/invoice-against/', views.InvoiceAgainstListView.as_view(), name='invoice-against-list'),
    path('masters/invoice-against/create/', views.InvoiceAgainstCreateView.as_view(), name='invoice-against-create'),
    path('masters/invoice-against/<int:pk>/edit/', views.InvoiceAgainstUpdateView.as_view(), name='invoice-against-edit'),
    path('masters/invoice-against/<int:pk>/delete/', views.InvoiceAgainstDeleteView.as_view(), name='invoice-against-delete'),

    path('masters/loan-type/', views.LoanTypeListView.as_view(), name='loan-type-list'),
    path('masters/loan-type/create/', views.LoanTypeCreateView.as_view(), name='loan-type-create'),
    path('masters/loan-type/<int:pk>/edit/', views.LoanTypeUpdateView.as_view(), name='loan-type-edit'),
    path('masters/loan-type/<int:pk>/delete/', views.LoanTypeDeleteView.as_view(), name='loan-type-delete'),

    path('masters/octori/', views.OctoriListView.as_view(), name='octori-list'),
    path('masters/octori/create/', views.OctoriCreateView.as_view(), name='octori-create'),
    path('masters/octori/<int:pk>/edit/', views.OctoriUpdateView.as_view(), name='octori-edit'),
    path('masters/octori/<int:pk>/delete/', views.OctoriDeleteView.as_view(), name='octori-delete'),

    path('masters/packing-forwarding/', views.PackingForwardingListView.as_view(), name='packing-forwarding-list'),
    path('masters/packing-forwarding/create/', views.PackingForwardingCreateView.as_view(), name='packing-forwarding-create'),
    path('masters/packing-forwarding/<int:pk>/edit/', views.PackingForwardingUpdateView.as_view(), name='packing-forwarding-edit'),
    path('masters/packing-forwarding/<int:pk>/delete/', views.PackingForwardingDeleteView.as_view(), name='packing-forwarding-delete'),

    path('masters/paid-type/', views.PaidTypeListView.as_view(), name='paid-type-list'),
    path('masters/paid-type/create/', views.PaidTypeCreateView.as_view(), name='paid-type-create'),
    path('masters/paid-type/<int:pk>/edit/', views.PaidTypeUpdateView.as_view(), name='paid-type-edit'),
    path('masters/paid-type/<int:pk>/delete/', views.PaidTypeDeleteView.as_view(), name='paid-type-delete'),

    path('masters/payment-receipt-against/', views.PaymentReceiptAgainstListView.as_view(), name='payment-receipt-against-list'),
    path('masters/payment-receipt-against/create/', views.PaymentReceiptAgainstCreateView.as_view(), name='payment-receipt-against-create'),
    path('masters/payment-receipt-against/<int:pk>/edit/', views.PaymentReceiptAgainstUpdateView.as_view(), name='payment-receipt-against-edit'),
    path('masters/payment-receipt-against/<int:pk>/delete/', views.PaymentReceiptAgainstDeleteView.as_view(), name='payment-receipt-against-delete'),

    path('masters/payment-mode/', views.PaymentModeListView.as_view(), name='payment-mode-list'),
    path('masters/payment-mode/create/', views.PaymentModeCreateView.as_view(), name='payment-mode-create'),
    path('masters/payment-mode/<int:pk>/edit/', views.PaymentModeUpdateView.as_view(), name='payment-mode-edit'),
    path('masters/payment-mode/<int:pk>/delete/', views.PaymentModeDeleteView.as_view(), name='payment-mode-delete'),

    path('masters/tour-expencess/', views.TourExpencessListView.as_view(), name='tour-expencess-list'),
    path('masters/tour-expencess/create/', views.TourExpencessCreateView.as_view(), name='tour-expencess-create'),
    path('masters/tour-expencess/<int:pk>/edit/', views.TourExpencessUpdateView.as_view(), name='tour-expencess-edit'),
    path('masters/tour-expencess/<int:pk>/delete/', views.TourExpencessDeleteView.as_view(), name='tour-expencess-delete'),

    path('masters/vat/', views.VATListView.as_view(), name='vat-list'),
    path('masters/vat/create/', views.VATCreateView.as_view(), name='vat-create'),
    path('masters/vat/<int:pk>/edit/', views.VATUpdateView.as_view(), name='vat-edit'),
    path('masters/vat/<int:pk>/delete/', views.VATDeleteView.as_view(), name='vat-delete'),

    path('masters/warrenty-terms/', views.WarrentyTermsListView.as_view(), name='warrenty-terms-list'),
    path('masters/warrenty-terms/create/', views.WarrentyTermsCreateView.as_view(), name='warrenty-terms-create'),
    path('masters/warrenty-terms/<int:pk>/edit/', views.WarrentyTermsUpdateView.as_view(), name='warrenty-terms-edit'),
    path('masters/warrenty-terms/<int:pk>/delete/', views.WarrentyTermsDeleteView.as_view(), name='warrenty-terms-delete'),
    
    # ========================================================================
    # TODO: Implement missing master views below
    # ========================================================================
    # path('masters/excise-service/', views.ExciseServiceListView.as_view(), name='excise-service-list'),
    # path('masters/intrest-type/', views.InterestTypeListView.as_view(), name='intrest-type-list'),
    # path('masters/invoice-against/', views.InvoiceAgainstListView.as_view(), name='invoice-against-list'),
    # path('masters/loan-type/', views.LoanTypeListView.as_view(), name='loan-type-list'),
    # path('masters/octori/', views.OctroiListView.as_view(), name='octori-list'),
    # path('masters/excisable-commodity/', views.ExcisableCommodityListView.as_view(), name='excisable-commodity-list'),
    # path('masters/paid-type/', views.PaidTypeListView.as_view(), name='paid-type-list'),
    # path('masters/freight/', views.FreightListView.as_view(), name='freight-list'),
    # path('masters/vat/', views.VATListView.as_view(), name='vat-list'),
    
    # ========================================================================
    # New Simplified Master Views
    # ========================================================================
    path('masters/currencies/', views.CurrencyListView.as_view(), name='currency-list'),
    path('masters/currencies/create/', views.CurrencyCreateView.as_view(), name='currency-create'),
    path('masters/currencies/<int:pk>/update/', views.CurrencyUpdateView.as_view(), name='currency-update'),
    path('masters/currencies/<int:pk>/delete/', views.CurrencyDeleteView.as_view(), name='currency-delete'),

    # TODO: Implement Packing views
    # path('masters/packing/', views.PackingListView.as_view(), name='packing-list'),
    # path('masters/packing/create/', views.PackingCreateView.as_view(), name='packing-create'),
    # path('masters/packing/<int:pk>/update/', views.PackingUpdateView.as_view(), name='packing-update'),
    # path('masters/packing/<int:pk>/delete/', views.PackingDeleteView.as_view(), name='packing-delete'),

    # Bank Master
    path('masters/banks/', views.BankListView.as_view(), name='bank-list'),
    path('masters/banks/create/', views.BankCreateView.as_view(), name='bank-create'),
    path('masters/banks/<int:pk>/update/', views.BankUpdateView.as_view(), name='bank-update'),
    path('masters/banks/<int:pk>/delete/', views.BankDeleteView.as_view(), name='bank-delete'),

    # TODO: Process Master - views not yet implemented
    # path('masters/processes/', views.ProcessListView.as_view(), name='process-list'),
    # path('masters/processes/create/', views.ProcessCreateView.as_view(), name='process-create'),
    # path('masters/processes/<int:pk>/update/', views.ProcessUpdateView.as_view(), name='process-update'),
    # path('masters/processes/<int:pk>/delete/', views.ProcessDeleteView.as_view(), name='process-delete'),

    # TODO: Invoice Type Master - views not yet implemented
    # path('masters/invoice-type/', views.InvoiceTypeListView.as_view(), name='invoice-type-list'),
    # path('masters/invoice-type/create/', views.InvoiceTypeCreateView.as_view(), name='invoice-type-create'),
    # path('masters/invoice-type/<int:pk>/update/', views.InvoiceTypeUpdateView.as_view(), name='invoice-type-update'),
    # path('masters/invoice-type/<int:pk>/delete/', views.InvoiceTypeDeleteView.as_view(), name='invoice-type-delete'),
    
    # TODO: Taxable Services Master - views not yet implemented
    # path('masters/taxable-services/', views.TaxableServicesListView.as_view(), name='taxable-services-list'),
    # path('masters/taxable-services/create/', views.TaxableServicesCreateView.as_view(), name='taxable-services-create'),
    # path('masters/taxable-services/<int:pk>/update/', views.TaxableServicesUpdateView.as_view(), name='taxable-services-update'),
    # path('masters/taxable-services/<int:pk>/delete/', views.TaxableServicesDeleteView.as_view(), name='taxable-services-delete'),
    
    # TODO: Loan Master - views not yet implemented
    # path('masters/loan-master/', views.LoanMasterListView.as_view(), name='loan-master-list'),
    # path('masters/loan-master/create/', views.LoanMasterCreateView.as_view(), name='loan-master-create'),
    # path('masters/loan-master/<int:pk>/update/', views.LoanMasterUpdateView.as_view(), name='loan-master-update'),
    # path('masters/loan-master/<int:pk>/delete/', views.LoanMasterDeleteView.as_view(), name='loan-master-delete'),
]
