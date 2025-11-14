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
    AccHeadForm, TDSCodeForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# TDS Code Master Views

class TDSCodeListView(BaseListViewMixin, ListView):
    """
    Display paginated list of TDS codes.
    Converted from: aspnet/Module/Accounts/Masters/TDS_Code.aspx
    """
    model = TblaccTdscodeMaster
    template_name = 'accounts/masters/tds_code_list.html'
    context_object_name = 'tds_codes'
    paginate_by = 20
    search_fields = ['sectionno', 'natureofpayment']
    partial_template_name = 'accounts/partials/tds_code_list_partial.html'

    def get_queryset(self):
        """Order by section number."""
        queryset = super().get_queryset()
        return queryset.order_by('sectionno')

class TDSCodeCreateView(BaseCreateViewMixin, CreateView):
    """Create new TDS code."""
    model = TblaccTdscodeMaster
    form_class = TDSCodeForm
    template_name = 'accounts/masters/tds_code_form.html'
    success_url = reverse_lazy('accounts:tds-code-list')
    success_message = 'TDS Code created successfully'
    partial_template_name = 'accounts/partials/tds_code_row.html'

class TDSCodeUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing TDS code."""
    model = TblaccTdscodeMaster
    form_class = TDSCodeForm
    template_name = 'accounts/masters/tds_code_form.html'
    success_url = reverse_lazy('accounts:tds-code-list')
    success_message = 'TDS Code updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/tds_code_row.html'

class TDSCodeDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete TDS code."""
    model = TblaccTdscodeMaster
    success_url = reverse_lazy('accounts:tds-code-list')
    pk_url_kwarg = 'id'



# ============================================================================
# Master Data Dashboard
# ============================================================================

from django.views.generic import TemplateView

