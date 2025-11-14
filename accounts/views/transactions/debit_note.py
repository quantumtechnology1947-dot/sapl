"""
Views for the Accounts module.
Converted from ASP.NET Module/Accounts/Masters/*.aspx
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.db import transaction, models
from django.contrib import messages
from datetime import datetime

# Import core mixins for standardized view behavior
from core.mixins import (
    BaseListViewMixin, BaseCreateViewMixin, BaseUpdateViewMixin,
    BaseDeleteViewMixin, BaseDetailViewMixin, HTMXResponseMixin,
    CompanyFinancialYearMixin, AuditMixin
)
from ...models import (
    Acchead, TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails,
    TblaccServicetaxinvoiceMaster, TblaccServicetaxinvoiceDetails,
    TblaccAdvicePaymentMaster, TblaccAdvicePaymentDetails,
    TblaccCapitalMaster, TblaccCapitalDetails,
    TblaccLoanmaster, TblaccLoandetails,
    TblaccTourvoucherMaster, TblaccTourvoucheradvanceDetails,
    TblaccTourintimationMaster, TblaccIouMaster,
    TblaccCashvoucherPaymentMaster, TblaccCashvoucherPaymentDetails,
    TblaccCashvoucherReceiptMaster,
    TblaccBankvoucherPaymentMaster, TblaccBankvoucherPaymentDetails,
    TblaccProformainvoiceMaster, TblaccProformainvoiceDetails,
    TblaccBillbookingMaster, TblaccBillbookingDetails, TblaccBillbookingAttachMaster,
    TblaccBank, TblpackingMaster, TblaccContraEntry,
    TblaccCurrencyMaster, TblaccTdscodeMaster, TblvatMaster, TblwarrentyMaster,
    TblaccAssetRegister, TblaccDebitnote,
    # Simple lookup masters
    TblaccIntresttype, TblaccInvoiceagainst, TblaccIouReasons, TblaccLoantype,
    TblaccPaidtype, TblaccPaymentmode, TblaccReceiptagainst, TblaccTourexpencesstype,
    TblexcisecommodityMaster, TblexciseserMaster, TblfreightMaster, TbloctroiMaster,
)

# Import GST views
# TODO: Implement GST views
# from .gst_views import GSTListView, GSTCreateView, GSTUpdateView, GSTDeleteView

# Import new master views
# TODO: Create these view files
# from .invoice_type_views import InvoiceTypeListView, InvoiceTypeCreateView, InvoiceTypeUpdateView, InvoiceTypeDeleteView
# from .taxable_services_views import TaxableServicesListView, TaxableServicesCreateView, TaxableServicesUpdateView, TaxableServicesDeleteView
# from .loan_master_views import LoanMasterListView, LoanMasterCreateView, LoanMasterUpdateView, LoanMasterDeleteView
from ...forms import (
    CreditNoteForm,
    DebitNoteForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Debit Note & Credit Note Transaction Views

class DebitNoteListView(BaseListViewMixin, ListView):
    """
    Display list of debit notes (issued to suppliers).

    Requirements: 8.1
    """
    model = TblaccDebitnote
    template_name = 'accounts/invoices/debit_note_list.html'
    context_object_name = 'notes'
    paginate_by = 20
    search_fields = ['debitno', 'sce', 'refrence']
    partial_template_name = 'accounts/partials/debit_note_list_partial.html'

    def get_queryset(self):
        """Filter for debit notes only (types 1-9)."""
        queryset = super().get_queryset().filter(types__lt=10)
        return queryset.order_by('-id')

class DebitNoteCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new debit note for purchase returns/adjustments.
    Creates reversal accounting entries: Debit Supplier, Credit Purchase Return.

    Requirements: 8.3, 8.5
    """
    model = TblaccDebitnote
    form_class = DebitNoteForm
    template_name = 'accounts/invoices/debit_note_form.html'
    success_url = reverse_lazy('accounts:debit-note-list')
    success_message = 'Debit note created successfully'
    partial_template_name = 'accounts/partials/debit_note_row.html'

    @transaction.atomic
    def form_valid(self, form):
        # Set audit fields via mixin
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()

        # Generate debit note number
        form.instance.debitno = VoucherService.generate_voucher_number('DN', self.get_compid())

        response = super().form_valid(form)

        # TODO: Create accounting entries
        # Debit: Accounts Payable (Supplier)
        # Credit: Purchase Returns

        return response

class DebitNoteUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing debit note."""
    model = TblaccDebitnote
    form_class = DebitNoteForm
    template_name = 'accounts/invoices/debit_note_form.html'
    success_url = reverse_lazy('accounts:debit-note-list')
    success_message = 'Debit note updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/debit_note_row.html'

class DebitNoteDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete debit note."""
    model = TblaccDebitnote
    success_url = reverse_lazy('accounts:debit-note-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/invoices/debit_note_confirm_delete.html'

class CreditNoteListView(BaseListViewMixin, ListView):
    """
    Display list of credit notes (issued to customers).

    Requirements: 8.1
    """
    model = TblaccDebitnote
    template_name = 'accounts/invoices/credit_note_list.html'
    context_object_name = 'notes'
    paginate_by = 20
    search_fields = ['debitno', 'sce', 'refrence']
    partial_template_name = 'accounts/partials/credit_note_list_partial.html'

    def get_queryset(self):
        """Filter for credit notes only (types 10+)."""
        queryset = super().get_queryset().filter(types__gte=10)
        return queryset.order_by('-id')

class CreditNoteCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new credit note for sales returns/adjustments.
    Creates reversal accounting entries: Debit Sales Return, Credit Customer.

    Requirements: 8.2, 8.4
    """
    model = TblaccDebitnote
    form_class = CreditNoteForm
    template_name = 'accounts/invoices/credit_note_form.html'
    success_url = reverse_lazy('accounts:credit-note-list')
    success_message = 'Credit note created successfully'
    partial_template_name = 'accounts/partials/credit_note_row.html'

    @transaction.atomic
    def form_valid(self, form):
        # Set audit fields via mixin
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()

        # Generate credit note number
        form.instance.debitno = VoucherService.generate_voucher_number('CN', self.get_compid())

        response = super().form_valid(form)

        # TODO: Create accounting entries
        # Debit: Sales Returns
        # Credit: Accounts Receivable (Customer)

        # TODO: Update customer outstanding balance

        return response

class CreditNoteUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing credit note."""
    model = TblaccDebitnote
    form_class = CreditNoteForm
    template_name = 'accounts/invoices/credit_note_form.html'
    success_url = reverse_lazy('accounts:credit-note-list')
    success_message = 'Credit note updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/credit_note_row.html'

class CreditNoteDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete credit note."""
    model = TblaccDebitnote
    success_url = reverse_lazy('accounts:credit-note-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/invoices/credit_note_confirm_delete.html'



# ============================================================================
# Bank Reconciliation Views
# ============================================================================

from ...services import ReconciliationService

