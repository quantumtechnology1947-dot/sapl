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
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Account Head Master Views

class AccHeadListView(BaseListViewMixin, ListView):
    """
    Display paginated list of account heads with search functionality.
    Converted from: aspnet/Module/Accounts/Masters/AccHead.aspx
    """
    model = Acchead
    template_name = 'accounts/masters/acchead_list.html'
    context_object_name = 'accheads'
    paginate_by = 20
    search_fields = ['description', 'category', 'symbol', 'abbrivation']
    partial_template_name = 'accounts/partials/acchead_list_partial.html'

    def get_queryset(self):
        """Order by category and description."""
        queryset = super().get_queryset()
        return queryset.order_by('category', 'description')

class AccHeadCreateView(BaseCreateViewMixin, CreateView):
    """
    Create a new account head.
    Converted from: aspnet/Module/Accounts/Masters/AccHead.aspx (Insert)
    """
    model = Acchead
    form_class = AccHeadForm
    template_name = 'accounts/masters/acchead_form.html'
    success_url = reverse_lazy('accounts:acchead-list')
    success_message = 'Account Head created successfully'
    partial_template_name = 'accounts/partials/acchead_row.html'

    def form_valid(self, form):
        """Handle AJAX requests."""
        response = super().form_valid(form)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'id': self.object.id})

        return response

    def form_invalid(self, form):
        """Handle AJAX validation errors."""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        return super().form_invalid(form)

class AccHeadUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update an existing account head.
    Converted from: aspnet/Module/Accounts/Masters/AccHead.aspx (Edit)
    """
    model = Acchead
    form_class = AccHeadForm
    template_name = 'accounts/masters/acchead_form.html'
    success_url = reverse_lazy('accounts:acchead-list')
    success_message = 'Account Head updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/acchead_row.html'

class AccHeadDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete an account head.
    Converted from: aspnet/Module/Accounts/Masters/AccHead.aspx (Delete)
    """
    model = Acchead
    success_url = reverse_lazy('accounts:acchead-list')
    pk_url_kwarg = 'id'



# ============================================================================
# Bank Master Views
# ============================================================================

from django.db.models import Q
from django.http import JsonResponse
from ...models import TblaccBank
from ...forms import BankForm
from sys_admin.models import Tblcountry, Tblstate, Tblcity

