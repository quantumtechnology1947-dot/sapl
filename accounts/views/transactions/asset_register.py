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
    TblaccAssetRegister, TblaccAssetCategory, TblaccDebitnote,
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
    AssetDisposalForm,
    AssetRegisterForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Asset Register Transaction Views

class AssetRegisterListView(BaseListViewMixin, ListView):
    """
    Display list of assets with category filter.

    Requirements: 10.1
    """
    model = TblaccAssetRegister
    template_name = 'accounts/assets/asset_register_list.html'
    context_object_name = 'assets'
    paginate_by = 20
    search_fields = ['assetno', 'assetname']
    partial_template_name = 'accounts/partials/asset_register_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(acategoyid=category_id)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = TblaccAssetCategory.objects.all()
        context['category_filter'] = self.request.GET.get('category', '')
        return context

class AssetRegisterCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new asset in register.

    Requirements: 10.2
    """
    model = TblaccAssetRegister
    form_class = AssetRegisterForm
    template_name = 'accounts/assets/asset_register_form.html'
    success_url = reverse_lazy('accounts:asset-register-list')
    success_message = 'Asset registered successfully'
    partial_template_name = 'accounts/partials/asset_register_row.html'

class AssetRegisterUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing asset."""
    model = TblaccAssetRegister
    form_class = AssetRegisterForm
    template_name = 'accounts/assets/asset_register_form.html'
    success_url = reverse_lazy('accounts:asset-register-list')
    success_message = 'Asset updated successfully'
    partial_template_name = 'accounts/partials/asset_register_row.html'
    pk_url_kwarg = 'id'

class AssetRegisterDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete asset from register."""
    model = TblaccAssetRegister
    success_url = reverse_lazy('accounts:asset-register-list')
    success_message = 'Asset deleted successfully'
    pk_url_kwarg = 'id'
    template_name = 'accounts/assets/asset_register_confirm_delete.html'

class AssetDisposalView(CompanyFinancialYearMixin, LoginRequiredMixin, FormView):
    """
    Dispose asset and calculate gain/loss.

    Requirements: 10.6
    """
    form_class = AssetDisposalForm
    template_name = 'accounts/assets/asset_disposal_form.html'

    def get_success_url(self):
        return reverse_lazy('accounts:asset-register-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset_id = self.kwargs.get('asset_id')
        context['asset'] = TblaccAssetRegister.objects.get(id=asset_id)
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Process asset disposal."""
        asset_id = self.kwargs.get('asset_id')
        disposal_date = form.cleaned_data['disposal_date']
        disposal_amount = form.cleaned_data['disposal_amount']
        remarks = form.cleaned_data['remarks']

        # Use AssetService to dispose asset
        from ...services import AssetService

        result = AssetService.dispose_asset(
            asset_id=asset_id,
            disposal_date=disposal_date.strftime('%Y-%m-%d'),
            disposal_amount=float(disposal_amount)
        )

        # TODO: Show gain/loss message to user

        return HttpResponseRedirect(self.get_success_url())


# AJAX endpoint for asset subcategories

