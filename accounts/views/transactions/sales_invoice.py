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
    SalesInvoiceDetailFormSet,
    SalesInvoiceMasterForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Sales Invoice & Related Transaction Views

class SalesInvoiceListView(BaseListViewMixin, ListView):
    """Display list of sales invoices."""
    model = TblaccSalesinvoiceMaster
    template_name = 'accounts/invoices/sales_invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    search_fields = ['invoiceno', 'buyer_name', 'customercode']
    partial_template_name = 'accounts/partials/sales_invoice_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-id')

class SalesInvoiceCreateView(BaseCreateViewMixin, CreateView):
    """Create new sales invoice with line items."""
    model = TblaccSalesinvoiceMaster
    form_class = SalesInvoiceMasterForm
    template_name = 'accounts/invoices/sales_invoice_form.html'
    success_url = reverse_lazy('accounts:sales-invoice-list')
    success_message = 'Sales invoice created successfully'
    partial_template_name = 'accounts/partials/sales_invoice_row.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = SalesInvoiceDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = SalesInvoiceDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']

        # Set audit fields via mixin
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.timeofissueinvoice = datetime.now().strftime('%H:%M:%S')
        form.instance.cst = 0  # Default CST

        # Generate invoice number if not provided
        if not form.instance.invoiceno:
            from ...services import VoucherService
            form.instance.invoiceno = VoucherService.generate_voucher_number('SI', self.get_compid())

        if detail_formset.is_valid():
            response = super().form_valid(form)
            detail_formset.instance = self.object
            detail_formset.save()

            # Create accounting entries (placeholder)
            # from ...services import AccountingService
            # AccountingService.create_sales_invoice_entries(self.object)

            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))

class SalesInvoiceUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing sales invoice."""
    model = TblaccSalesinvoiceMaster
    form_class = SalesInvoiceMasterForm
    template_name = 'accounts/invoices/sales_invoice_form.html'
    success_url = reverse_lazy('accounts:sales-invoice-list')
    success_message = 'Sales invoice updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/sales_invoice_row.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = SalesInvoiceDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = SalesInvoiceDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']

        if detail_formset.is_valid():
            response = super().form_valid(form)
            detail_formset.instance = self.object
            detail_formset.save()
            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))

class SalesInvoiceDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete sales invoice."""
    model = TblaccSalesinvoiceMaster
    success_url = reverse_lazy('accounts:sales-invoice-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/invoices/sales_invoice_confirm_delete.html'


# ============================================================================
# Bill Booking Views
# ============================================================================

from ...models import TblaccBillbookingMaster, TblaccBillbookingDetails
from ...forms import BillBookingMasterForm, BillBookingDetailFormSet

class SalesInvoicePrintView(LoginRequiredMixin, DetailView):
    """
    Generate professional PDF for Sales Invoice.
    Converted from: D:/inetpub/NewERP/Module/Accounts/Transactions/SalesInvoice_Print_Details.aspx

    Note: Uses xhtml2pdf instead of Crystal Reports for Windows compatibility
    """
    model = TblaccSalesinvoiceMaster
    pk_url_kwarg = 'id'
    template_name = 'accounts/salesinvoice_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()

        # Get invoice line items
        line_items = TblaccSalesinvoiceDetails.objects.filter(mid=invoice).select_related()

        # Get customer info
        try:
            from sales_distribution.models import SdCustMaster
            customer = SdCustMaster.objects.get(customerid=invoice.customercode)
        except:
            customer = None

        # Get financial year name
        finyear_name = None
        try:
            from sys_admin.models import TblfinancialMaster as FinancialYear
            finyear = FinancialYear.objects.get(pk=invoice.finyearid)
            finyear_name = finyear.finyear
        except:
            finyear_name = str(invoice.finyearid)

        # Get employee/user name
        employee_name = None
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(pk=int(invoice.sessionid))
            employee_name = user.username
        except:
            employee_name = invoice.sessionid

        # Get buyer city/state/country names
        buyer_city_name = invoice.buyer_city.cityname if invoice.buyer_city else None
        buyer_state_name = None
        buyer_country_name = None

        if invoice.buyer_state:
            try:
                from sys_admin.models import Tblstate
                state = Tblstate.objects.get(pk=invoice.buyer_state)
                buyer_state_name = state.statename
            except:
                pass

        if invoice.buyer_country:
            try:
                from sys_admin.models import Tblcountry
                country = Tblcountry.objects.get(pk=invoice.buyer_country)
                buyer_country_name = country.countryname
            except:
                pass

        # Get consignee city/state/country names
        cong_city_name = invoice.cong_city.cityname if invoice.cong_city else None
        cong_state_name = None
        cong_country_name = None

        if invoice.cong_state:
            try:
                from sys_admin.models import Tblstate
                state = Tblstate.objects.get(pk=invoice.cong_state)
                cong_state_name = state.statename
            except:
                pass

        if invoice.cong_country:
            try:
                from sys_admin.models import Tblcountry
                country = Tblcountry.objects.get(pk=invoice.cong_country)
                cong_country_name = country.countryname
            except:
                pass

        # Calculate line item totals
        subtotal = 0
        for item in line_items:
            line_total = item.qty * item.rate
            # Apply discount
            if item.amtinper:
                line_total -= (line_total * item.amtinper / 100)
            subtotal += line_total
            item.line_total = line_total

        # Handle charges - invoice has type fields (1=percentage, 0=fixed)
        pf_amount = 0
        if invoice.pf:
            if invoice.pftype == 1:  # Percentage
                pf_amount = subtotal * invoice.pf / 100
            else:  # Fixed amount
                pf_amount = invoice.pf

        freight_amount = 0
        if invoice.freight:
            if invoice.freighttype == 1:  # Percentage
                freight_amount = subtotal * invoice.freight / 100
            else:  # Fixed amount
                freight_amount = invoice.freight

        insurance_amount = 0
        if invoice.insurance:
            if invoice.insurancetype == 1:  # Percentage
                insurance_amount = subtotal * invoice.insurance / 100
            else:  # Fixed amount
                insurance_amount = invoice.insurance

        # Additional charges
        add_amount = 0
        if invoice.addamt:
            if invoice.addtype == 1:  # Percentage
                add_amount = subtotal * invoice.addamt / 100
            else:  # Fixed amount
                add_amount = invoice.addamt

        # Deductions
        deduction_amount = 0
        if invoice.deduction:
            if invoice.deductiontype == 1:  # Percentage
                deduction_amount = subtotal * invoice.deduction / 100
            else:  # Fixed amount
                deduction_amount = invoice.deduction

        # Calculate tax amounts
        sed_amount = 0
        if invoice.sed:
            if invoice.sedtype == 1:  # Percentage
                sed_amount = subtotal * invoice.sed / 100
            else:
                sed_amount = invoice.sed

        aed_amount = 0
        if invoice.aed:
            if invoice.aedtype == 1:  # Percentage
                aed_amount = subtotal * invoice.aed / 100
            else:
                aed_amount = invoice.aed

        # VAT/CST (these appear to be IDs/codes, not percentages)
        vat_amount = invoice.vat if invoice.vat else 0
        cst_amount = invoice.cst if invoice.cst else 0

        other_amount = invoice.otheramt if invoice.otheramt else 0

        grand_total = subtotal + pf_amount + freight_amount + insurance_amount + add_amount + sed_amount + aed_amount + other_amount - deduction_amount

        # Company info from settings
        context.update({
            'invoice': invoice,
            'line_items': line_items,
            'customer': customer,
            'finyear_name': finyear_name,
            'employee_name': employee_name,
            'buyer_city_name': buyer_city_name,
            'buyer_state_name': buyer_state_name,
            'buyer_country_name': buyer_country_name,
            'cong_city_name': cong_city_name,
            'cong_state_name': cong_state_name,
            'cong_country_name': cong_country_name,
            'subtotal': subtotal,
            'pf_amount': pf_amount,
            'freight_amount': freight_amount,
            'insurance_amount': insurance_amount,
            'add_amount': add_amount,
            'deduction_amount': deduction_amount,
            'sed_amount': sed_amount,
            'aed_amount': aed_amount,
            'vat_amount': vat_amount,
            'cst_amount': cst_amount,
            'other_amount': other_amount,
            'grand_total': grand_total,
            'company_name': 'Synergytech Automation Pvt. Ltd.',
            'company_address': 'Pune, Maharashtra, India',
            'company_phone': '+91-XXX-XXXXXXX',
            'company_email': 'sales@synergytechs.com',
            'company_website': 'www.synergytechs.com',
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
        invoice_no = context['invoice'].invoiceno if context['invoice'].invoiceno else f'INV_{context["invoice"].id}'
        filename = f'Sales_Invoice_{invoice_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response


# ============================================================================
# Service Tax Invoice Views
# Converted from: aspnet/Module/Accounts/Transactions/ServiceTaxInvoice_*.aspx
# ============================================================================

class ServiceTaxInvoiceListView(BaseListViewMixin, ListView):
    """
    Display paginated list of service tax invoices with search functionality.
    Converted from: aspnet/Module/Accounts/Transactions/ServiceTaxInvoice_Dashboard.aspx
    """
    model = TblaccServicetaxinvoiceMaster
    template_name = 'accounts/invoices/service_tax_invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    search_fields = ['invoiceno', 'pono', 'customercode']
    partial_template_name = 'accounts/partials/service_tax_invoice_list_partial.html'

    def get_queryset(self):
        """Filter service tax invoices by company and financial year."""
        queryset = super().get_queryset()
        # Filter by company and financial year
        queryset = queryset.filter(compid=self.get_compid(), finyearid=self.get_finyearid())
        return queryset.order_by('-id')

class ServiceTaxInvoiceCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new service tax invoice from PO/WO.
    Converted from: aspnet/Module/Accounts/Transactions/ServiceTaxInvoice_New.aspx
    """
    model = TblaccServicetaxinvoiceMaster
    template_name = 'accounts/invoices/service_tax_invoice_form.html'
    fields = ['invoiceno', 'pono', 'wono', 'dateofissueinvoice', 'customercode', 'buyer_name', 'buyer_add']
    success_url = reverse_lazy('accounts:service-tax-invoice-list')
    success_message = 'Service tax invoice created successfully'
    partial_template_name = 'accounts/partials/service_tax_invoice_row.html'

    def form_valid(self, form):
        """Set audit fields before saving."""
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        return super().form_valid(form)

class ServiceTaxInvoiceUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing service tax invoice.
    Converted from: aspnet/Module/Accounts/Transactions/ServiceTaxInvoice_Edit.aspx
    """
    model = TblaccServicetaxinvoiceMaster
    template_name = 'accounts/invoices/service_tax_invoice_form.html'
    fields = ['invoiceno', 'pono', 'wono', 'dateofissueinvoice', 'customercode', 'buyer_name', 'buyer_add']
    success_url = reverse_lazy('accounts:service-tax-invoice-list')
    success_message = 'Service tax invoice updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/service_tax_invoice_row.html'

class ServiceTaxInvoiceDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete service tax invoice.
    Converted from: aspnet/Module/Accounts/Transactions/ServiceTaxInvoice_Delete.aspx
    """
    model = TblaccServicetaxinvoiceMaster
    template_name = 'accounts/invoices/service_tax_invoice_confirm_delete.html'
    success_url = reverse_lazy('accounts:service-tax-invoice-list')
    pk_url_kwarg = 'id'

class ServiceTaxInvoicePrintView(LoginRequiredMixin, DetailView):
    """
    Generate professional PDF for Service Tax Invoice.
    Converted from: aspnet/Module/Accounts/Transactions/ServiceTaxInvoice_Print.aspx
    """
    model = TblaccServicetaxinvoiceMaster
    pk_url_kwarg = 'id'
    template_name = 'accounts/invoices/service_tax_invoice_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()

        # Get invoice line items
        line_items = TblaccServicetaxinvoiceDetails.objects.filter(mid=invoice)

        # Get customer info
        try:
            from sales_distribution.models import SdCustMaster
            customer = SdCustMaster.objects.get(customerid=invoice.customercode)
        except:
            customer = None

        # Get financial year name
        finyear_name = None
        try:
            from sys_admin.models import TblfinancialMaster as FinancialYear
            finyear = FinancialYear.objects.get(pk=invoice.finyearid)
            finyear_name = finyear.finyear
        except:
            finyear_name = str(invoice.finyearid)

        # Calculate totals
        subtotal = sum(item.qty * item.rate for item in line_items)

        context.update({
            'invoice': invoice,
            'line_items': line_items,
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
        invoice_no = context['invoice'].invoiceno if context['invoice'].invoiceno else f'STI_{context["invoice"].id}'
        filename = f'Service_Tax_Invoice_{invoice_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response


# ============================================================================
# Advice Payment Views
# Converted from: aspnet/Module/Accounts/Transactions/Advice.aspx
# ============================================================================

class AdvicePaymentListView(BaseListViewMixin, ListView):
    """
    Display paginated list of advice payments with search functionality.
    Converted from: aspnet/Module/Accounts/Transactions/Advice.aspx
    """
    model = TblaccAdvicePaymentMaster
    template_name = 'accounts/transactions/advice_list.html'
    partial_template_name = 'accounts/transactions/partials/advice_list_partial.html'
    context_object_name = 'advices'
    paginate_by = 20
    search_fields = ['adno', 'payto', 'chequeno']

    def get_queryset(self):
        """Filter advice payments with ordering."""
        return super().get_queryset().order_by('-id')

class AdvicePaymentCreateView(BaseCreateViewMixin, CreateView):
    """
    Create a new advice payment with details.
    Converted from: aspnet/Module/Accounts/Transactions/Advice.aspx (Insert)
    """
    model = TblaccAdvicePaymentMaster
    form_class = AdvicePaymentMasterForm
    template_name = 'accounts/transactions/advice_form.html'
    partial_template_name = 'accounts/transactions/partials/advice_form_partial.html'
    success_url = reverse_lazy('accounts:advice-list')
    success_message = 'Advice payment created successfully.'

    def get_context_data(self, **kwargs):
        """Add formset for advice details."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = AdvicePaymentDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = AdvicePaymentDetailFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        """Save advice payment with details and audit fields."""
        context = self.get_context_data()
        detail_formset = context['detail_formset']

        with transaction.atomic():
            # Set audit fields using mixin methods
            now = datetime.now()
            form.instance.sysdate = now.strftime('%d-%m-%Y')
            form.instance.systime = now.strftime('%H:%M:%S')
            form.instance.sessionid = str(self.request.user.id)
            form.instance.compid = self.get_compid()
            form.instance.finyearid = self.get_finyearid()

            # Generate Advice Number
            last_advice = TblaccAdvicePaymentMaster.objects.order_by('-id').first()
            if last_advice and last_advice.adno:
                try:
                    last_num = int(last_advice.adno.replace('AD', ''))
                    form.instance.adno = f'AD{last_num + 1:05d}'
                except:
                    form.instance.adno = 'AD00001'
            else:
                form.instance.adno = 'AD00001'

            self.object = form.save()

            if detail_formset.is_valid():
                detail_formset.instance = self.object
                detail_formset.save()
            else:
                return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())

class AdvicePaymentUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update an existing advice payment.
    Converted from: aspnet/Module/Accounts/Transactions/Advice.aspx (Edit)
    """
    model = TblaccAdvicePaymentMaster
    form_class = AdvicePaymentMasterForm
    template_name = 'accounts/transactions/advice_form.html'
    partial_template_name = 'accounts/transactions/partials/advice_form_partial.html'
    success_url = reverse_lazy('accounts:advice-list')
    success_message = 'Advice payment updated successfully.'
    pk_url_kwarg = 'advice_id'

    def get_context_data(self, **kwargs):
        """Add formset for advice details."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = AdvicePaymentDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = AdvicePaymentDetailFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        """Update advice payment with details."""
        context = self.get_context_data()
        detail_formset = context['detail_formset']

        with transaction.atomic():
            # Update audit fields using mixin methods
            now = datetime.now()
            form.instance.sysdate = now.strftime('%d-%m-%Y')
            form.instance.systime = now.strftime('%H:%M:%S')
            form.instance.sessionid = str(self.request.user.id)

            self.object = form.save()

            if detail_formset.is_valid():
                detail_formset.instance = self.object
                detail_formset.save()
            else:
                return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())

class AdvicePaymentDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete an advice payment.
    Converted from: aspnet/Module/Accounts/Transactions/Advice_Delete.aspx
    """
    model = TblaccAdvicePaymentMaster
    template_name = 'accounts/transactions/advice_confirm_delete.html'
    success_url = reverse_lazy('accounts:advice-list')
    pk_url_kwarg = 'advice_id'

    def get_context_data(self, **kwargs):
        """Add advice details to context."""
        context = super().get_context_data(**kwargs)
        context['advice_details'] = TblaccAdvicePaymentDetails.objects.filter(mid=self.object)
        return context

class AdvicePaymentPrintView(LoginRequiredMixin, DetailView):
    """
    Print advice payment as PDF.
    Converted from: aspnet/Module/Accounts/Transactions/Advice_Print.aspx
    """
    model = TblaccAdvicePaymentMaster
    template_name = 'accounts/transactions/advice_print_pdf.html'
    pk_url_kwarg = 'advice_id'

    def get_context_data(self, **kwargs):
        """Add advice details and calculations to context."""
        context = super().get_context_data(**kwargs)
        advice = self.object

        # Get advice details
        details = TblaccAdvicePaymentDetails.objects.filter(mid=advice)
        context['advice'] = advice
        context['advice_details'] = details

        # Calculate total amount
        total_amount = sum(detail.amount or 0 for detail in details)
        context['total_amount'] = total_amount

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
        advice_no = context['advice'].adno if context['advice'].adno else f'AD_{context["advice"].id}'
        filename = f'Advice_Payment_{advice_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response
# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =
# GENERATED SIMPLE MASTER VIEWS
# Generated by: generate_simple_masters.py
# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =# =


# Excisable Commodity Views
# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -# -

