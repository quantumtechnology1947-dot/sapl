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
    CashVoucherReceiptForm,
    CashVoucherPaymentDetailFormSet,
    CashVoucherPaymentForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Cash Voucher Transaction Views

class CashVoucherPaymentListView(BaseListViewMixin, ListView):
    """Display list of cash payment vouchers filtered by company and financial year."""
    model = TblaccCashvoucherPaymentMaster
    template_name = 'accounts/transactions/cash_voucher_payment_list.html'
    context_object_name = 'vouchers'
    paginate_by = 20
    search_fields = ['paidto', 'cvpno']
    partial_template_name = 'accounts/partials/cash_voucher_payment_list_partial.html'

    def get_queryset(self):
        """Order by ID descending (newest first)."""
        queryset = super().get_queryset()
        return queryset.order_by('-id')

class CashVoucherPaymentCreateView(BaseCreateViewMixin, CreateView):
    """Create new cash payment voucher with line items."""
    model = TblaccCashvoucherPaymentMaster
    form_class = CashVoucherPaymentForm
    template_name = 'accounts/transactions/cash_voucher_payment_form.html'
    success_url = reverse_lazy('accounts:cash-voucher-payment-list')
    success_message = 'Cash payment voucher created successfully'
    partial_template_name = 'accounts/partials/cash_voucher_payment_row.html'

    def get_context_data(self, **kwargs):
        """Add detail formset to context."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = CashVoucherPaymentDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = CashVoucherPaymentDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Save master and detail records with audit fields from mixins."""
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()

        # Audit fields set by AuditMixin
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

class CashVoucherPaymentUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing cash payment voucher."""
    model = TblaccCashvoucherPaymentMaster
    form_class = CashVoucherPaymentForm
    template_name = 'accounts/transactions/cash_voucher_payment_form.html'
    success_url = reverse_lazy('accounts:cash-voucher-payment-list')
    success_message = 'Cash payment voucher updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/cash_voucher_payment_row.html'

    def get_context_data(self, **kwargs):
        """Add detail formset to context."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = CashVoucherPaymentDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = CashVoucherPaymentDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Save master and detail records. Audit fields updated by AuditMixin."""
        response = super().form_valid(form)

        context = self.get_context_data()
        detail_formset = context['detail_formset']

        if detail_formset.is_valid():
            detail_formset.instance = self.object
            detail_formset.save()
            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))

class CashVoucherPaymentDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete cash payment voucher."""
    model = TblaccCashvoucherPaymentMaster
    success_url = reverse_lazy('accounts:cash-voucher-payment-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/transactions/cash_voucher_payment_confirm_delete.html'

class CashVoucherReceiptListView(BaseListViewMixin, ListView):
    """Display list of cash receipt vouchers filtered by company and financial year."""
    model = TblaccCashvoucherReceiptMaster
    template_name = 'accounts/transactions/cash_voucher_receipt_list.html'
    context_object_name = 'vouchers'
    paginate_by = 20
    search_fields = ['cashreceivedagainst', 'cvrno']
    partial_template_name = 'accounts/partials/cash_voucher_receipt_list_partial.html'

    def get_queryset(self):
        """Order by ID descending (newest first)."""
        queryset = super().get_queryset()
        return queryset.order_by('-id')

class CashVoucherReceiptCreateView(BaseCreateViewMixin, CreateView):
    """Create new cash receipt voucher."""
    model = TblaccCashvoucherReceiptMaster
    form_class = CashVoucherReceiptForm
    template_name = 'accounts/transactions/cash_voucher_receipt_form.html'
    success_url = reverse_lazy('accounts:cash-voucher-receipt-list')
    success_message = 'Cash receipt voucher created successfully'
    partial_template_name = 'accounts/partials/cash_voucher_receipt_row.html'

    @transaction.atomic
    def form_valid(self, form):
        """Save with company, financial year, and audit fields from mixins."""
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        # Audit fields set by AuditMixin
        return super().form_valid(form)

class CashVoucherReceiptUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing cash receipt voucher."""
    model = TblaccCashvoucherReceiptMaster
    form_class = CashVoucherReceiptForm
    template_name = 'accounts/transactions/cash_voucher_receipt_form.html'
    success_url = reverse_lazy('accounts:cash-voucher-receipt-list')
    success_message = 'Cash receipt voucher updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/cash_voucher_receipt_row.html'

class CashVoucherReceiptDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete cash receipt voucher."""
    model = TblaccCashvoucherReceiptMaster
    success_url = reverse_lazy('accounts:cash-voucher-receipt-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/transactions/cash_voucher_receipt_confirm_delete.html'


# ============================================================================
# Transactions Dashboard
# ============================================================================

class CashVoucherPaymentPrintView(LoginRequiredMixin, DetailView):
    """
    Generate PDF for Cash Voucher Payment.
    Converted from: aspnet/Module/Accounts/Transactions/CashVoucher_Payment_Print_Details.aspx
    """
    model = TblaccCashvoucherPaymentMaster
    pk_url_kwarg = 'id'
    template_name = 'accounts/vouchers/cash_voucher_payment_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()

        # Get voucher details
        details = TblaccCashvoucherPaymentDetails.objects.filter(mid=voucher.id)

        # Get financial year name
        finyear_name = None
        try:
            from sys_admin.models import TblfinancialMaster as FinancialYear
            finyear = FinancialYear.objects.get(pk=voucher.finyearid)
            finyear_name = finyear.finyear
        except:
            finyear_name = str(voucher.finyearid)

        # Calculate total amount
        total_amount = sum(detail.amount or 0 for detail in details)

        context.update({
            'voucher': voucher,
            'details': details,
            'finyear_name': finyear_name,
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
        voucher_no = context['voucher'].cvpno if context['voucher'].cvpno else f'CVP_{context["voucher"].id}'
        filename = f'Cash_Voucher_Payment_{voucher_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response

class CashVoucherReceiptPrintView(LoginRequiredMixin, DetailView):
    """
    Generate PDF for Cash Voucher Receipt.
    Converted from: aspnet/Module/Accounts/Transactions/CashVoucher_Receipt_Print_Details.aspx
    """
    model = TblaccCashvoucherReceiptMaster
    pk_url_kwarg = 'id'
    template_name = 'accounts/vouchers/cash_voucher_receipt_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()

        # Get financial year name
        finyear_name = None
        try:
            from sys_admin.models import TblfinancialMaster as FinancialYear
            finyear = FinancialYear.objects.get(pk=voucher.finyearid)
            finyear_name = finyear.finyear
        except:
            finyear_name = str(voucher.finyearid)

        context.update({
            'voucher': voucher,
            'finyear_name': finyear_name,
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
        voucher_no = context['voucher'].cvrno if context['voucher'].cvrno else f'CVR_{context["voucher"].id}'
        filename = f'Cash_Voucher_Receipt_{voucher_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response

