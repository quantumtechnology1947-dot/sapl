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
    JournalEntryForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Journal Entry Transaction Views

class JournalEntryListView(BaseListViewMixin, ListView):
    """Display list of journal entries."""
    model = TblaccContraEntry
    template_name = 'accounts/transactions/journal_entry_list.html'
    context_object_name = 'entries'
    paginate_by = 20
    search_fields = ['narration', 'voucherno']
    partial_template_name = 'accounts/partials/journal_entry_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-id')

class JournalEntryCreateView(BaseCreateViewMixin, CreateView):
    """Create new journal entry."""
    model = TblaccContraEntry
    form_class = JournalEntryForm
    template_name = 'accounts/transactions/journal_entry_form.html'
    success_url = reverse_lazy('accounts:journal-entry-list')
    success_message = 'Journal entry created successfully'
    partial_template_name = 'accounts/partials/journal_entry_row.html'

    def form_valid(self, form):
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class JournalEntryUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing journal entry."""
    model = TblaccContraEntry
    form_class = JournalEntryForm
    template_name = 'accounts/transactions/journal_entry_form.html'
    success_url = reverse_lazy('accounts:journal-entry-list')
    success_message = 'Journal entry updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/journal_entry_row.html'

class JournalEntryDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete journal entry."""
    model = TblaccContraEntry
    success_url = reverse_lazy('accounts:journal-entry-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/transactions/journal_entry_confirm_delete.html'


# ============================================================================
# Contra Entry Views
# ============================================================================

from ...forms import ContraEntryForm

