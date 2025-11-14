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
    BankVoucherDetailFormSet,
    BankVoucherMasterForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Bank Voucher Transaction Views

class BankVoucherListView(BaseListViewMixin, ListView):
    """Display list of bank vouchers filtered by company and financial year."""
    model = TblaccBankvoucherPaymentMaster
    template_name = 'accounts/transactions/bank_voucher_list.html'
    context_object_name = 'vouchers'
    paginate_by = 20
    search_fields = ['bvpno', 'payto']
    partial_template_name = 'accounts/partials/bank_voucher_list_partial.html'

    def get_queryset(self):
        """Order by ID descending (newest first)."""
        queryset = super().get_queryset()
        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        """Add bank lookups for display."""
        context = super().get_context_data(**kwargs)
        banks = {b.id: b.name for b in TblaccBank.objects.all()}
        context['banks'] = banks
        return context

class BankVoucherCreateView(BaseCreateViewMixin, CreateView):
    """Create new bank voucher with line items."""
    model = TblaccBankvoucherPaymentMaster
    form_class = BankVoucherMasterForm
    template_name = 'accounts/transactions/bank_voucher_form.html'
    success_url = reverse_lazy('accounts:bank-voucher-list')
    success_message = 'Bank voucher created successfully'
    partial_template_name = 'accounts/partials/bank_voucher_row.html'

    def get_context_data(self, **kwargs):
        """Add detail formset to context."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = BankVoucherDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = BankVoucherDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Save master and detail records with audit fields from mixins."""
        # Set company and financial year from session (handled by CompanyFinancialYearMixin)
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()

        # Audit fields (sysdate, systime, sessionid) are set by AuditMixin.form_valid()
        # Call parent to set audit fields
        response = super().form_valid(form)

        # Save detail formset
        context = self.get_context_data()
        detail_formset = context['detail_formset']

        if detail_formset.is_valid():
            detail_formset.instance = self.object
            detail_formset.save()
            return response
        else:
            # Rollback will happen automatically due to @transaction.atomic
            return self.render_to_response(self.get_context_data(form=form))

class BankVoucherUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing bank voucher."""
    model = TblaccBankvoucherPaymentMaster
    form_class = BankVoucherMasterForm
    template_name = 'accounts/transactions/bank_voucher_form.html'
    success_url = reverse_lazy('accounts:bank-voucher-list')
    success_message = 'Bank voucher updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/bank_voucher_row.html'

    def get_context_data(self, **kwargs):
        """Add detail formset to context."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = BankVoucherDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = BankVoucherDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Save master and detail records. Audit fields updated by AuditMixin."""
        response = super().form_valid(form)

        # Save detail formset
        context = self.get_context_data()
        detail_formset = context['detail_formset']

        if detail_formset.is_valid():
            detail_formset.instance = self.object
            detail_formset.save()
            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))

class BankVoucherDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete bank voucher."""
    model = TblaccBankvoucherPaymentMaster
    success_url = reverse_lazy('accounts:bank-voucher-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/transactions/bank_voucher_confirm_delete.html'


# ============================================================================
# Cash Voucher Views
# ============================================================================

from ...models import TblaccCashvoucherPaymentMaster, TblaccCashvoucherPaymentDetails, TblaccCashvoucherReceiptMaster
from ...forms import CashVoucherPaymentForm, CashVoucherPaymentDetailFormSet, CashVoucherReceiptForm

class BankVoucherPrintView(LoginRequiredMixin, DetailView):
    """
    Generate PDF for Bank Voucher.
    Converted from: aspnet/Module/Accounts/Transactions/BankVoucher_Print.aspx
    """
    model = TblaccBankvoucherPaymentMaster
    pk_url_kwarg = 'id'
    template_name = 'accounts/vouchers/bank_voucher_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()

        # Get voucher details
        details = TblaccBankvoucherPaymentDetails.objects.filter(mid=voucher.id)

        # Get financial year name
        finyear_name = None
        try:
            from sys_admin.models import TblfinancialMaster as FinancialYear
            finyear = FinancialYear.objects.get(pk=voucher.finyearid)
            finyear_name = finyear.finyear
        except:
            finyear_name = str(voucher.finyearid)

        # Get bank name
        bank_name = None
        try:
            bank = TblaccBank.objects.get(pk=voucher.bankid)
            bank_name = bank.bankname
        except:
            bank_name = str(voucher.bankid)

        # Calculate total amount
        total_amount = sum(detail.amount or 0 for detail in details)

        context.update({
            'voucher': voucher,
            'details': details,
            'finyear_name': finyear_name,
            'bank_name': bank_name,
            'total_amount': total_amount,
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        """Generate PDF from template"""
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa
        from io import BytesIO

        # Render HTML template
        html_string = render_to_string(self.template_name, context)

        # Generate PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

        if pdf.err:
            return HttpResponse(f'Error generating PDF: {pdf.err}', content_type='text/html')

        # Return as PDF response
        voucher_no = context['voucher'].bvpno if context['voucher'].bvpno else f'BVP_{context["voucher"].id}'
        filename = f'Bank_Voucher_{voucher_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response

