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
    AccHeadForm, CurrencyForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Currency Master Views

class CurrencyListView(BaseListViewMixin, ListView):
    """
    Display paginated list of currencies with search functionality.
    Converted from: aspnet/Module/Accounts/Masters/Currency.aspx
    Optimized: Added select_related for foreign keys
    """
    model = TblaccCurrencyMaster
    template_name = 'accounts/masters/currency_list.html'
    context_object_name = 'currencies'
    paginate_by = 20
    search_fields = ['name', 'symbol']
    select_related_fields = ['cid']
    partial_template_name = 'accounts/partials/currency_list_partial.html'

    def get_queryset(self):
        """Order by currency name."""
        queryset = super().get_queryset()
        return queryset.order_by('name')

class CurrencyCreateView(BaseCreateViewMixin, CreateView):
    """
    Create a new currency.
    Converted from: aspnet/Module/Accounts/Masters/Currency.aspx (Insert)
    """
    model = TblaccCurrencyMaster
    form_class = CurrencyForm
    template_name = 'accounts/masters/currency_form.html'
    success_url = reverse_lazy('accounts:currency-list')
    success_message = 'Currency created successfully'
    partial_template_name = 'accounts/partials/currency_row.html'

class CurrencyUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update an existing currency.
    Converted from: aspnet/Module/Accounts/Masters/Currency.aspx (Edit)
    """
    model = TblaccCurrencyMaster
    form_class = CurrencyForm
    template_name = 'accounts/masters/currency_form.html'
    success_url = reverse_lazy('accounts:currency-list')
    success_message = 'Currency updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/currency_row.html'

class CurrencyDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete a currency.
    Converted from: aspnet/Module/Accounts/Masters/Currency.aspx (Delete)
    """
    model = TblaccCurrencyMaster
    success_url = reverse_lazy('accounts:currency-list')
    pk_url_kwarg = 'id'



# ============================================================================
# Payment Terms Views
# ============================================================================

from ...models import TblaccPaymentmode
from ...forms import PaymentTermsForm

