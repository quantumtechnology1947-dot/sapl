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

# Miscellaneous Master Views
# Small lookup tables and auxiliary masters

class ExcisableCommodityListView(BaseListViewMixin, ListView):
    model = TblexcisecommodityMaster
    template_name = 'accounts/masters/excisable-commodity_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['description', 'code']
    partial_template_name = 'accounts/partials/excisable_commodity_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('description')

class ExcisableCommodityCreateView(BaseCreateViewMixin, CreateView):
    model = TblexcisecommodityMaster
    template_name = 'accounts/masters/excisable-commodity_form.html'
    fields = ['code', 'description']
    success_url = reverse_lazy('accounts:excisable-commodity-list')
    success_message = 'Excisable commodity created successfully'
    partial_template_name = 'accounts/partials/excisable_commodity_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class ExcisableCommodityUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblexcisecommodityMaster
    template_name = 'accounts/masters/excisable-commodity_form.html'
    fields = ['code', 'description']
    success_url = reverse_lazy('accounts:excisable-commodity-list')
    success_message = 'Excisable commodity updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/excisable_commodity_row.html'

class ExcisableCommodityDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblexcisecommodityMaster
    template_name = 'accounts/masters/excisable-commodity_confirm_delete.html'
    success_url = reverse_lazy('accounts:excisable-commodity-list')
    pk_url_kwarg = 'pk'


# Excise Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class ExciseListView(BaseListViewMixin, ListView):
    model = TblexciseserMaster
    template_name = 'accounts/masters/excise_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['description', 'code']
    partial_template_name = 'accounts/partials/excise_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('description')

class ExciseCreateView(BaseCreateViewMixin, CreateView):
    model = TblexciseserMaster
    template_name = 'accounts/masters/excise_form.html'
    fields = ['code', 'description', 'rate']
    success_url = reverse_lazy('accounts:excise-list')
    success_message = 'Excise created successfully'
    partial_template_name = 'accounts/partials/excise_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class ExciseUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblexciseserMaster
    template_name = 'accounts/masters/excise_form.html'
    fields = ['code', 'description', 'rate']
    success_url = reverse_lazy('accounts:excise-list')
    success_message = 'Excise updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/excise_row.html'

class ExciseDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblexciseserMaster
    template_name = 'accounts/masters/excise_confirm_delete.html'
    success_url = reverse_lazy('accounts:excise-list')
    pk_url_kwarg = 'pk'


# Freight Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class FreightListView(BaseListViewMixin, ListView):
    model = TblfreightMaster
    template_name = 'accounts/masters/freight_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['description', 'code']
    partial_template_name = 'accounts/partials/freight_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('description')

class FreightCreateView(BaseCreateViewMixin, CreateView):
    model = TblfreightMaster
    template_name = 'accounts/masters/freight_form.html'
    fields = ['code', 'description', 'rate']
    success_url = reverse_lazy('accounts:freight-list')
    success_message = 'Freight created successfully'
    partial_template_name = 'accounts/partials/freight_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class FreightUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblfreightMaster
    template_name = 'accounts/masters/freight_form.html'
    fields = ['code', 'description', 'rate']
    success_url = reverse_lazy('accounts:freight-list')
    success_message = 'Freight updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/freight_row.html'

class FreightDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblfreightMaster
    template_name = 'accounts/masters/freight_confirm_delete.html'
    success_url = reverse_lazy('accounts:freight-list')
    pk_url_kwarg = 'pk'


# IOU Reasons Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class IOUReasonsListView(BaseListViewMixin, ListView):
    model = TblaccIouReasons
    template_name = 'accounts/masters/iou-reasons_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['reasons']
    partial_template_name = 'accounts/partials/iou-reasons_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('reasons')

class IOUReasonsCreateView(BaseCreateViewMixin, CreateView):
    model = TblaccIouReasons
    template_name = 'accounts/masters/iou-reasons_form.html'
    fields = ['reasons']
    success_url = reverse_lazy('accounts:iou-reasons-list')
    success_message = 'IOU Reason created successfully'
    partial_template_name = 'accounts/partials/iou-reasons_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class IOUReasonsUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblaccIouReasons
    template_name = 'accounts/masters/iou-reasons_form.html'
    fields = ['reasons']
    success_url = reverse_lazy('accounts:iou-reasons-list')
    success_message = 'IOU Reason updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/iou-reasons_row.html'

class IOUReasonsDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblaccIouReasons
    template_name = 'accounts/masters/iou-reasons_confirm_delete.html'
    success_url = reverse_lazy('accounts:iou-reasons-list')
    pk_url_kwarg = 'pk'


# Interest Type Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class IntrestTypeListView(BaseListViewMixin, ListView):
    model = TblaccIntresttype
    template_name = 'accounts/masters/intrest-type_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['type']
    partial_template_name = 'accounts/partials/intrest-type_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('type')

class IntrestTypeCreateView(BaseCreateViewMixin, CreateView):
    model = TblaccIntresttype
    template_name = 'accounts/masters/intrest-type_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:intrest-type-list')
    success_message = 'Interest Type created successfully'
    partial_template_name = 'accounts/partials/intrest-type_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class IntrestTypeUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblaccIntresttype
    template_name = 'accounts/masters/intrest-type_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:intrest-type-list')
    success_message = 'Interest Type updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/intrest-type_row.html'

class IntrestTypeDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblaccIntresttype
    template_name = 'accounts/masters/intrest-type_confirm_delete.html'
    success_url = reverse_lazy('accounts:intrest-type-list')
    pk_url_kwarg = 'pk'


# Invoice Against Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class InvoiceAgainstListView(BaseListViewMixin, ListView):
    model = TblaccInvoiceagainst
    template_name = 'accounts/masters/invoice-against_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['type']
    partial_template_name = 'accounts/partials/invoice-against_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('type')

class InvoiceAgainstCreateView(BaseCreateViewMixin, CreateView):
    model = TblaccInvoiceagainst
    template_name = 'accounts/masters/invoice-against_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:invoice-against-list')
    success_message = 'Invoice Against created successfully'
    partial_template_name = 'accounts/partials/invoice-against_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class InvoiceAgainstUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblaccInvoiceagainst
    template_name = 'accounts/masters/invoice-against_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:invoice-against-list')
    success_message = 'Invoice Against updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/invoice-against_row.html'

class InvoiceAgainstDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblaccInvoiceagainst
    template_name = 'accounts/masters/invoice-against_confirm_delete.html'
    success_url = reverse_lazy('accounts:invoice-against-list')
    pk_url_kwarg = 'pk'


# Loan Type Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class LoanTypeListView(BaseListViewMixin, ListView):
    model = TblaccLoantype
    template_name = 'accounts/masters/loan-type_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['type']
    partial_template_name = 'accounts/partials/loan-type_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('type')

class LoanTypeCreateView(BaseCreateViewMixin, CreateView):
    model = TblaccLoantype
    template_name = 'accounts/masters/loan-type_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:loan-type-list')
    success_message = 'Loan Type created successfully'
    partial_template_name = 'accounts/partials/loan-type_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class LoanTypeUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblaccLoantype
    template_name = 'accounts/masters/loan-type_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:loan-type-list')
    success_message = 'Loan Type updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/loan-type_row.html'

class LoanTypeDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblaccLoantype
    template_name = 'accounts/masters/loan-type_confirm_delete.html'
    success_url = reverse_lazy('accounts:loan-type-list')
    pk_url_kwarg = 'pk'


# ========================================================================
# Capital Particulars Views (Transactions)
# ========================================================================
# Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Capital.aspx
# Model: TblaccCapitalMaster (accounts/models.py:554-565)

class OctoriListView(BaseListViewMixin, ListView):
    model = TbloctroiMaster
    template_name = 'accounts/masters/octori_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['description', 'code']
    partial_template_name = 'accounts/partials/octori_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('description')

class OctoriCreateView(BaseCreateViewMixin, CreateView):
    model = TbloctroiMaster
    template_name = 'accounts/masters/octori_form.html'
    fields = ['code', 'description', 'rate']
    success_url = reverse_lazy('accounts:octori-list')
    success_message = 'Octori created successfully'
    partial_template_name = 'accounts/partials/octori_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class OctoriUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TbloctroiMaster
    template_name = 'accounts/masters/octori_form.html'
    fields = ['code', 'description', 'rate']
    success_url = reverse_lazy('accounts:octori-list')
    success_message = 'Octori updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/octori_row.html'

class OctoriDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TbloctroiMaster
    template_name = 'accounts/masters/octori_confirm_delete.html'
    success_url = reverse_lazy('accounts:octori-list')
    pk_url_kwarg = 'pk'


# Packing & Forwarding Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class PackingForwardingListView(BaseListViewMixin, ListView):
    model = TblpackingMaster
    template_name = 'accounts/masters/packing-forwarding_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['description', 'code']
    partial_template_name = 'accounts/partials/packing-forwarding_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('description')

class PackingForwardingCreateView(BaseCreateViewMixin, CreateView):
    model = TblpackingMaster
    template_name = 'accounts/masters/packing-forwarding_form.html'
    fields = ['code', 'description']
    success_url = reverse_lazy('accounts:packing-forwarding-list')
    success_message = 'Packing Forwarding created successfully'
    partial_template_name = 'accounts/partials/packing-forwarding_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class PackingForwardingUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblpackingMaster
    template_name = 'accounts/masters/packing-forwarding_form.html'
    fields = ['code', 'description']
    success_url = reverse_lazy('accounts:packing-forwarding-list')
    success_message = 'Packing Forwarding updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/packing-forwarding_row.html'

class PackingForwardingDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblpackingMaster
    template_name = 'accounts/masters/packing-forwarding_confirm_delete.html'
    success_url = reverse_lazy('accounts:packing-forwarding-list')
    pk_url_kwarg = 'pk'


# Paid Type Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class PaidTypeListView(BaseListViewMixin, ListView):
    model = TblaccPaidtype
    template_name = 'accounts/masters/paid-type_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['type']
    partial_template_name = 'accounts/partials/paid-type_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('type')

class PaidTypeCreateView(BaseCreateViewMixin, CreateView):
    model = TblaccPaidtype
    template_name = 'accounts/masters/paid-type_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:paid-type-list')
    success_message = 'Paid Type created successfully'
    partial_template_name = 'accounts/partials/paid-type_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class PaidTypeUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblaccPaidtype
    template_name = 'accounts/masters/paid-type_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:paid-type-list')
    success_message = 'Paid Type updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/paid-type_row.html'

class PaidTypeDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblaccPaidtype
    template_name = 'accounts/masters/paid-type_confirm_delete.html'
    success_url = reverse_lazy('accounts:paid-type-list')
    pk_url_kwarg = 'pk'


# Payment/Receipt Against Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class PaymentReceiptAgainstListView(BaseListViewMixin, ListView):
    model = TblaccReceiptagainst
    template_name = 'accounts/masters/payment-receipt-against_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['type']
    partial_template_name = 'accounts/partials/payment-receipt-against_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('type')

class PaymentReceiptAgainstCreateView(BaseCreateViewMixin, CreateView):
    model = TblaccReceiptagainst
    template_name = 'accounts/masters/payment-receipt-against_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:payment-receipt-against-list')
    success_message = 'Payment Receipt Against created successfully'
    partial_template_name = 'accounts/partials/payment-receipt-against_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class PaymentReceiptAgainstUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblaccReceiptagainst
    template_name = 'accounts/masters/payment-receipt-against_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:payment-receipt-against-list')
    success_message = 'Payment Receipt Against updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/payment-receipt-against_row.html'

class PaymentReceiptAgainstDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblaccReceiptagainst
    template_name = 'accounts/masters/payment-receipt-against_confirm_delete.html'
    success_url = reverse_lazy('accounts:payment-receipt-against-list')
    pk_url_kwarg = 'pk'


# Payment Mode Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class PaymentModeListView(BaseListViewMixin, ListView):
    model = TblaccPaymentmode
    template_name = 'accounts/masters/payment-mode_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['mode']
    partial_template_name = 'accounts/partials/payment-mode_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('mode')

class PaymentModeCreateView(BaseCreateViewMixin, CreateView):
    model = TblaccPaymentmode
    template_name = 'accounts/masters/payment-mode_form.html'
    fields = ['mode']
    success_url = reverse_lazy('accounts:payment-mode-list')
    success_message = 'Payment Mode created successfully'
    partial_template_name = 'accounts/partials/payment-mode_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class PaymentModeUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblaccPaymentmode
    template_name = 'accounts/masters/payment-mode_form.html'
    fields = ['mode']
    success_url = reverse_lazy('accounts:payment-mode-list')
    success_message = 'Payment Mode updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/payment-mode_row.html'

class PaymentModeDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblaccPaymentmode
    template_name = 'accounts/masters/payment-mode_confirm_delete.html'
    success_url = reverse_lazy('accounts:payment-mode-list')
    pk_url_kwarg = 'pk'


# Tour Expenses Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class TourExpencessListView(BaseListViewMixin, ListView):
    model = TblaccTourexpencesstype
    template_name = 'accounts/masters/tour-expencess_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['type']
    partial_template_name = 'accounts/partials/tour-expencess_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('type')

class TourExpencessCreateView(BaseCreateViewMixin, CreateView):
    model = TblaccTourexpencesstype
    template_name = 'accounts/masters/tour-expencess_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:tour-expencess-list')
    success_message = 'Tour Expencess created successfully'
    partial_template_name = 'accounts/partials/tour-expencess_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class TourExpencessUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblaccTourexpencesstype
    template_name = 'accounts/masters/tour-expencess_form.html'
    fields = ['type']
    success_url = reverse_lazy('accounts:tour-expencess-list')
    success_message = 'Tour Expencess updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/tour-expencess_row.html'

class TourExpencessDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblaccTourexpencesstype
    template_name = 'accounts/masters/tour-expencess_confirm_delete.html'
    success_url = reverse_lazy('accounts:tour-expencess-list')
    pk_url_kwarg = 'pk'


# VAT Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class VATListView(BaseListViewMixin, ListView):
    model = TblvatMaster
    template_name = 'accounts/masters/vat_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['description', 'code']
    partial_template_name = 'accounts/partials/vat_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('description')

class VATCreateView(BaseCreateViewMixin, CreateView):
    model = TblvatMaster
    template_name = 'accounts/masters/vat_form.html'
    fields = ['code', 'description', 'rate']
    success_url = reverse_lazy('accounts:vat-list')
    success_message = 'VAT created successfully'
    partial_template_name = 'accounts/partials/vat_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class VATUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblvatMaster
    template_name = 'accounts/masters/vat_form.html'
    fields = ['code', 'description', 'rate']
    success_url = reverse_lazy('accounts:vat-list')
    success_message = 'VAT updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/vat_row.html'

class VATDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblvatMaster
    template_name = 'accounts/masters/vat_confirm_delete.html'
    success_url = reverse_lazy('accounts:vat-list')
    pk_url_kwarg = 'pk'


# Warranty Terms Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

class WarrentyTermsListView(BaseListViewMixin, ListView):
    model = TblwarrentyMaster
    template_name = 'accounts/masters/warrenty-terms_list.html'
    context_object_name = 'items'
    paginate_by = 20
    search_fields = ['terms']
    partial_template_name = 'accounts/partials/warrenty-terms_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('terms')

class WarrentyTermsCreateView(BaseCreateViewMixin, CreateView):
    model = TblwarrentyMaster
    template_name = 'accounts/masters/warrenty-terms_form.html'
    fields = ['terms']
    success_url = reverse_lazy('accounts:warrenty-terms-list')
    success_message = 'Warranty Terms created successfully'
    partial_template_name = 'accounts/partials/warrenty-terms_row.html'

    def form_valid(self, form):
        if hasattr(form.instance, 'compid'):
            form.instance.compid = self.get_compid()
        if hasattr(form.instance, 'finyearid'):
            form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class WarrentyTermsUpdateView(BaseUpdateViewMixin, UpdateView):
    model = TblwarrentyMaster
    template_name = 'accounts/masters/warrenty-terms_form.html'
    fields = ['terms']
    success_url = reverse_lazy('accounts:warrenty-terms-list')
    success_message = 'Warranty Terms updated successfully'
    pk_url_kwarg = 'pk'
    partial_template_name = 'accounts/partials/warrenty-terms_row.html'

class WarrentyTermsDeleteView(BaseDeleteViewMixin, DeleteView):
    model = TblwarrentyMaster
    template_name = 'accounts/masters/warrenty-terms_confirm_delete.html'
    success_url = reverse_lazy('accounts:warrenty-terms-list')
    pk_url_kwarg = 'pk'


# ============================================================================
# Tour Voucher Transaction Views
# Converted from: aspnet/Module/Accounts/Transactions/TourVoucher*.aspx
# ============================================================================

class CapitalListView(BaseListViewMixin, ListView):
    """
    Display paginated list of capital particulars.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Capital.aspx
    """
    model = TblaccCapitalMaster
    template_name = 'accounts/transactions/capital_list.html'
    context_object_name = 'capitals'
    paginate_by = 20
    search_fields = ['particulars']
    partial_template_name = 'accounts/partials/capital_list_partial.html'

    def get_queryset(self):
        """Filter capital records based on search query."""
        queryset = super().get_queryset()
        return queryset.order_by('-id')

class CapitalCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new capital particular entry.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Capital.aspx
    """
    model = TblaccCapitalMaster
    template_name = 'accounts/transactions/capital_form.html'
    fields = ['particulars']
    success_url = reverse_lazy('accounts:capital-list')
    success_message = 'Capital created successfully'
    partial_template_name = 'accounts/partials/capital_row.html'

    def form_valid(self, form):
        """Populate audit fields before saving."""
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class CapitalUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing capital particular entry.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Capital.aspx
    """
    model = TblaccCapitalMaster
    template_name = 'accounts/transactions/capital_form.html'
    fields = ['particulars']
    success_url = reverse_lazy('accounts:capital-list')
    success_message = 'Capital updated successfully'
    pk_url_kwarg = 'capital_id'
    partial_template_name = 'accounts/partials/capital_row.html'

class CapitalDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete capital particular entry.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Capital.aspx
    """
    model = TblaccCapitalMaster
    template_name = 'accounts/transactions/capital_confirm_delete.html'
    success_url = reverse_lazy('accounts:capital-list')
    pk_url_kwarg = 'capital_id'


# ========================================================================
# Loan Particulars Views (Transactions)
# ========================================================================
# Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Loan.aspx
# Model: TblaccLoanmaster (accounts/models.py:1243-1254)

class LoanListView(BaseListViewMixin, ListView):
    """
    Display paginated list of loan particulars.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Loan.aspx
    """
    model = TblaccLoanmaster
    template_name = 'accounts/transactions/loan_list.html'
    context_object_name = 'loans'
    paginate_by = 20
    search_fields = ['particulars']
    partial_template_name = 'accounts/partials/loan_list_partial.html'

    def get_queryset(self):
        """Filter loan records based on search query."""
        queryset = super().get_queryset()
        return queryset.order_by('-id')

class LoanCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new loan particular entry.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Loan.aspx
    """
    model = TblaccLoanmaster
    template_name = 'accounts/transactions/loan_form.html'
    fields = ['particulars']
    success_url = reverse_lazy('accounts:loan-list')
    success_message = 'Loan created successfully'
    partial_template_name = 'accounts/partials/loan_row.html'

    def form_valid(self, form):
        """Populate audit fields before saving."""
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class LoanUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing loan particular entry.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Loan.aspx
    """
    model = TblaccLoanmaster
    template_name = 'accounts/transactions/loan_form.html'
    fields = ['particulars']
    success_url = reverse_lazy('accounts:loan-list')
    success_message = 'Loan updated successfully'
    pk_url_kwarg = 'loan_id'
    partial_template_name = 'accounts/partials/loan_row.html'

class LoanDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete loan particular entry.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/Loan.aspx
    """
    model = TblaccLoanmaster
    template_name = 'accounts/transactions/loan_confirm_delete.html'
    success_url = reverse_lazy('accounts:loan-list')
    pk_url_kwarg = 'loan_id'


# Octori Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

