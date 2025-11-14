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
    AccHeadForm, BankForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Bank Master Views

class BankListView(BaseListViewMixin, ListView):
    """
    Display paginated list of banks with search functionality.
    Converted from: aspnet/Module/Accounts/Masters/Bank.aspx
    Optimized: Added select_related for foreign keys
    """
    model = TblaccBank
    template_name = 'accounts/masters/bank_list.html'
    context_object_name = 'banks'
    paginate_by = 20
    search_fields = ['name', 'ifsc', 'address', 'contactno']
    select_related_fields = ['cid', 'sid', 'cityid']
    partial_template_name = 'accounts/partials/bank_list_partial.html'

    def get_queryset(self):
        """Order by bank name."""
        queryset = super().get_queryset()
        return queryset.order_by('name')

class BankCreateView(BaseCreateViewMixin, CreateView):
    """
    Create a new bank.
    Converted from: aspnet/Module/Accounts/Masters/Bank.aspx (Insert)
    """
    model = TblaccBank
    form_class = BankForm
    template_name = 'accounts/masters/bank_form.html'
    success_url = reverse_lazy('accounts:bank-list')
    success_message = 'Bank created successfully'
    partial_template_name = 'accounts/partials/bank_row.html'

class BankUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update an existing bank.
    Converted from: aspnet/Module/Accounts/Masters/Bank.aspx (Edit)
    """
    model = TblaccBank
    form_class = BankForm
    template_name = 'accounts/masters/bank_form.html'
    success_url = reverse_lazy('accounts:bank-list')
    success_message = 'Bank updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/bank_row.html'

class BankDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete a bank.
    Converted from: aspnet/Module/Accounts/Masters/Bank.aspx (Delete)
    """
    model = TblaccBank
    success_url = reverse_lazy('accounts:bank-list')
    pk_url_kwarg = 'id'


# ============================================================================
# HTMX AJAX Endpoints (Converted to CBVs)
# ============================================================================

