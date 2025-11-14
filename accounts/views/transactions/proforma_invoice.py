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
    ProformaInvoiceDetailFormSet,
    ProformaInvoiceHeaderForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Proforma Invoice Transaction Views

class ProformaInvoiceListView(BaseListViewMixin, ListView):
    """
    Display list of proforma invoices.
    Proforma invoices are quotations without accounting entries.

    Requirements: 7.1
    """
    model = TblaccProformainvoiceMaster
    template_name = 'accounts/invoices/proforma_invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    search_fields = ['invoiceno', 'buyer_name']
    partial_template_name = 'accounts/partials/proforma_invoice_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-id')

class ProformaInvoiceCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new proforma invoice without accounting entries.

    Requirements: 7.2, 7.3
    """
    model = TblaccProformainvoiceMaster
    form_class = ProformaInvoiceHeaderForm
    template_name = 'accounts/invoices/proforma_invoice_form.html'
    success_url = reverse_lazy('accounts:proforma-invoice-list')
    success_message = 'Proforma invoice created successfully'
    partial_template_name = 'accounts/partials/proforma_invoice_row.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = ProformaInvoiceDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = ProformaInvoiceDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['detail_formset']

        if formset.is_valid():
            # Set audit fields via mixin
            form.instance.compid = self.get_compid()
            form.instance.finyearid = self.get_finyearid()

            # Generate proforma invoice number
            form.instance.invoiceno = VoucherService.generate_voucher_number('PI', self.get_compid())

            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()

            return response
        else:
            return self.form_invalid(form)

class ProformaInvoiceUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing proforma invoice."""
    model = TblaccProformainvoiceMaster
    form_class = ProformaInvoiceHeaderForm
    template_name = 'accounts/invoices/proforma_invoice_form.html'
    success_url = reverse_lazy('accounts:proforma-invoice-list')
    success_message = 'Proforma invoice updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/proforma_invoice_row.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = ProformaInvoiceDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = ProformaInvoiceDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['detail_formset']

        if formset.is_valid():
            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()
            return response
        else:
            return self.form_invalid(form)

class ProformaInvoiceDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete proforma invoice."""
    model = TblaccProformainvoiceMaster
    success_url = reverse_lazy('accounts:proforma-invoice-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/invoices/proforma_invoice_confirm_delete.html'

class ProformaToSalesInvoiceView(BaseCreateViewMixin, CreateView):
    """
    Convert proforma invoice to sales invoice.
    Copies all line items and creates actual invoice with accounting entries.

    Requirements: 7.4, 7.6
    """
    model = TblaccSalesinvoiceMaster
    template_name = 'accounts/invoices/proforma_to_sales_invoice.html'
    success_url = reverse_lazy('accounts:sales-invoice-list')
    success_message = 'Proforma invoice converted to sales invoice successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proforma_id = self.kwargs.get('proforma_id')
        context['proforma'] = TblaccProformainvoiceMaster.objects.get(id=proforma_id)
        context['proforma_items'] = TblaccProformainvoiceDetails.objects.filter(mid=proforma_id)
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Convert proforma to sales invoice."""
        proforma_id = self.kwargs.get('proforma_id')
        proforma = TblaccProformainvoiceMaster.objects.get(id=proforma_id)
        proforma_items = TblaccProformainvoiceDetails.objects.filter(mid=proforma_id)

        # Create sales invoice master
        sales_invoice = TblaccSalesinvoiceMaster.objects.create(
            sysdate=datetime.now().strftime('%Y-%m-%d'),
            systime=datetime.now().strftime('%H:%M:%S'),
            sessionid=request.session.session_key,
            compid=proforma.compid,
            finyearid=proforma.finyearid,
            invoiceno=VoucherService.generate_voucher_number('SI', proforma.finyearid),
            pono=proforma.pono,
            wono=proforma.wono,
            # Copy other relevant fields
        )

        # Copy line items
        for item in proforma_items:
            TblaccSalesinvoiceDetails.objects.create(
                mid=sales_invoice,
                itemid=item.itemid,
                qty=item.qty,
                rate=item.rate,
                # Copy other relevant fields
            )

        # Create accounting entries
        InvoiceService.create_accounting_entries(sales_invoice)

        return HttpResponseRedirect(self.success_url)



# ============================================================================
# Credit/Debit Note Views
# ============================================================================

from ...models import TblaccDebitnote
from ...forms import DebitNoteForm, CreditNoteForm

class ProformaInvoicePrintView(LoginRequiredMixin, DetailView):
    """
    Generate PDF for Proforma Invoice.
    Converted from: aspnet/Module/Accounts/Transactions/ProformaInvoice_Print.aspx
    """
    model = TblaccProformainvoiceMaster
    pk_url_kwarg = 'id'
    template_name = 'accounts/invoices/proforma_invoice_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()

        # Get invoice details
        details = TblaccProformainvoiceDetails.objects.filter(mid=invoice.id)

        # Get customer info (cross-module integration with Sales)
        customer = None
        try:
            from sales_distribution.models import SdCustMaster
            customer = SdCustMaster.objects.get(customerid=invoice.customercode)
        except:
            pass

        # Get financial year name
        finyear_name = None
        try:
            from sys_admin.models import TblfinancialMaster as FinancialYear
            finyear = FinancialYear.objects.get(pk=invoice.finyearid)
            finyear_name = finyear.finyear
        except:
            finyear_name = str(invoice.finyearid)

        # Calculate totals
        subtotal = sum(detail.value or 0 for detail in details)

        context.update({
            'invoice': invoice,
            'details': details,
            'customer': customer,
            'finyear_name': finyear_name,
            'subtotal': subtotal,
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
        invoice_no = context['invoice'].invoiceno if context['invoice'].invoiceno else f'PI_{context["invoice"].id}'
        filename = f'Proforma_Invoice_{invoice_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response

