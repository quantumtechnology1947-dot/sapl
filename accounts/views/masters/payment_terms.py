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
    AccHeadForm, PaymentTermsForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Payment Terms Master Views

class PaymentTermsListView(BaseListViewMixin, ListView):
    """
    Display paginated list of payment terms with search functionality.
    Converted from: aspnet/Module/Accounts/Masters/PaymentTerms.aspx
    """
    model = TblaccPaymentmode
    template_name = 'accounts/masters/payment_terms_list.html'
    context_object_name = 'payment_terms'
    paginate_by = 20
    search_fields = ['terms']
    partial_template_name = 'accounts/partials/payment_terms_list_partial.html'

    def get_queryset(self):
        """Order by ID."""
        queryset = super().get_queryset()
        return queryset.order_by('id')

class PaymentTermsCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new payment terms.
    Converted from: aspnet/Module/Accounts/Masters/PaymentTerms.aspx (Insert)
    """
    model = TblaccPaymentmode
    form_class = PaymentTermsForm
    template_name = 'accounts/masters/payment_terms_form.html'
    success_url = reverse_lazy('accounts:payment-terms-list')
    success_message = 'Payment terms created successfully'
    partial_template_name = 'accounts/partials/payment_terms_row.html'

class PaymentTermsUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing payment terms.
    Converted from: aspnet/Module/Accounts/Masters/PaymentTerms.aspx (Edit)
    """
    model = TblaccPaymentmode
    form_class = PaymentTermsForm
    template_name = 'accounts/masters/payment_terms_form.html'
    success_url = reverse_lazy('accounts:payment-terms-list')
    success_message = 'Payment terms updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/payment_terms_row.html'

class PaymentTermsDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete payment terms.
    Converted from: aspnet/Module/Accounts/Masters/PaymentTerms.aspx (Delete)
    """
    model = TblaccPaymentmode
    success_url = reverse_lazy('accounts:payment-terms-list')
    pk_url_kwarg = 'id'



# ============================================================================
# TDS Code Views
# ============================================================================

from ...models import TblaccTdscodeMaster
from ...forms import TDSCodeForm

