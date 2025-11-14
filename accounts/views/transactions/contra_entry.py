"""
Views for the Accounts module.
Converted from ASP.NET Module/Accounts/Masters/*.aspx
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View, FormView, TemplateView
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
    ContraEntryForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Contra Entry Transaction Views

class ContraEntryListView(BaseListViewMixin, ListView):
    """
    Display list of contra entries (cash-bank transfers).
    Converted from: ASP.NET Contra Entry module
    """
    model = TblaccContraEntry
    template_name = 'accounts/transactions/contra_entry_list.html'
    context_object_name = 'entries'
    paginate_by = 20
    search_fields = ['narration', 'voucherno']
    partial_template_name = 'accounts/partials/contra_entry_list_partial.html'

    def get_queryset(self):
        """Filter contra entries."""
        queryset = super().get_queryset()
        return queryset.order_by('-id')

class ContraEntryCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new contra entry for cash-bank transfers.
    Simplified two-line entry (From Account → To Account).
    """
    model = TblaccContraEntry
    form_class = ContraEntryForm
    template_name = 'accounts/transactions/contra_entry_form.html'
    success_url = reverse_lazy('accounts:contra-entry-list')
    success_message = 'Contra entry created successfully'
    partial_template_name = 'accounts/partials/contra_entry_row.html'

    @transaction.atomic
    def form_valid(self, form):
        """Save contra entry with audit fields."""
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class ContraEntryUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing contra entry."""
    model = TblaccContraEntry
    form_class = ContraEntryForm
    template_name = 'accounts/transactions/contra_entry_form.html'
    success_url = reverse_lazy('accounts:contra-entry-list')
    success_message = 'Contra entry updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/contra_entry_row.html'

class ContraEntryDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete contra entry."""
    model = TblaccContraEntry
    success_url = reverse_lazy('accounts:contra-entry-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/transactions/contra_entry_confirm_delete.html'



# ============================================================================
# Bank Reconciliation Views
# ============================================================================

from django.views.generic import TemplateView
from django.http import JsonResponse
from ...services import ReconciliationService
from ...models import TblaccBankrecanciliation, TblaccBankvoucherPaymentMaster, TblaccBankvoucherReceivedMasters

