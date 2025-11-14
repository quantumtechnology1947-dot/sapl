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
    BillBookingAttachmentForm,
    BillBookingDetailFormSet,
    BillBookingMasterForm,
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Bill Booking Transaction Views

class BillBookingListView(BaseListViewMixin, ListView):
    """Display list of bill bookings with status filter."""
    model = TblaccBillbookingMaster
    template_name = 'accounts/invoices/bill_booking_list.html'
    context_object_name = 'bills'
    paginate_by = 20
    search_fields = ['pvevno', 'supplierid', 'billno']
    partial_template_name = 'accounts/partials/bill_booking_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status', '')

        if status:
            if status == 'pending':
                queryset = queryset.filter(authorize=0)
            elif status == 'authorized':
                queryset = queryset.filter(authorize=1)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context

class BillBookingCreateView(BaseCreateViewMixin, CreateView):
    """Create new bill booking with line items."""
    model = TblaccBillbookingMaster
    form_class = BillBookingMasterForm
    template_name = 'accounts/invoices/bill_booking_form.html'
    success_url = reverse_lazy('accounts:bill-booking-list')
    success_message = 'Bill booking created successfully'
    partial_template_name = 'accounts/partials/bill_booking_row.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = BillBookingDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = BillBookingDetailFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']

        # Set audit fields via mixin
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()

        # Generate bill booking number if not provided
        if not form.instance.pvevno:
            from ...services import VoucherService
            form.instance.pvevno = VoucherService.generate_voucher_number('BB', self.get_compid())

        # Set default authorization status if not provided
        if form.instance.authorize is None:
            form.instance.authorize = 0  # Pending

        if detail_formset.is_valid():
            response = super().form_valid(form)
            detail_formset.instance = self.object
            detail_formset.save()

            # Calculate TDS if TDS code is provided
            # This would be implemented in the service layer

            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))

class BillBookingUpdateView(BaseUpdateViewMixin, UpdateView):
    """Update existing bill booking."""
    model = TblaccBillbookingMaster
    form_class = BillBookingMasterForm
    template_name = 'accounts/invoices/bill_booking_form.html'
    success_url = reverse_lazy('accounts:bill-booking-list')
    success_message = 'Bill booking updated successfully'
    pk_url_kwarg = 'id'
    partial_template_name = 'accounts/partials/bill_booking_row.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detail_formset'] = BillBookingDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = BillBookingDetailFormSet(instance=self.object)
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

class BillBookingDeleteView(BaseDeleteViewMixin, DeleteView):
    """Delete bill booking."""
    model = TblaccBillbookingMaster
    success_url = reverse_lazy('accounts:bill-booking-list')
    pk_url_kwarg = 'id'
    template_name = 'accounts/invoices/bill_booking_confirm_delete.html'

class BillBookingAuthorizeView(BaseUpdateViewMixin, UpdateView):
    """Authorize a bill booking."""
    model = TblaccBillbookingMaster
    fields = []
    template_name = 'accounts/invoices/bill_booking_authorize.html'
    success_url = reverse_lazy('accounts:bill-booking-list')
    success_message = 'Bill booking authorized successfully'
    pk_url_kwarg = 'id'

    @transaction.atomic
    def form_valid(self, form):
        # Set authorization fields
        now = datetime.now()
        form.instance.authorize = 1
        form.instance.authorizeby = str(self.request.user.username)
        form.instance.authorizedate = now.strftime('%Y-%m-%d')
        form.instance.authorizetime = now.strftime('%H:%M:%S')

        return super().form_valid(form)



# ============================================================================
# Bill Booking Attachment Views
# ============================================================================

from django.views.generic import CreateView, DeleteView
from django.http import HttpResponse, FileResponse
from ...models import TblaccBillbookingAttachMaster
from ...forms import BillBookingAttachmentForm

class BillBookingAttachmentUploadView(CompanyFinancialYearMixin, LoginRequiredMixin, CreateView):
    """
    Upload attachment for bill booking.
    Stores file in database as binary data.

    Requirements: 6.9
    """
    model = TblaccBillbookingAttachMaster
    form_class = BillBookingAttachmentForm
    template_name = 'accounts/invoices/bill_booking_attachment_upload.html'

    def get_success_url(self):
        """Redirect back to bill booking edit page."""
        bill_id = self.kwargs.get('bill_id')
        return reverse_lazy('accounts:bill-booking-edit', kwargs={'id': bill_id})

    def get_context_data(self, **kwargs):
        """Add bill booking to context."""
        context = super().get_context_data(**kwargs)
        bill_id = self.kwargs.get('bill_id')
        context['bill'] = TblaccBillbookingMaster.objects.get(id=bill_id)

        # Get existing attachments
        context['attachments'] = TblaccBillbookingAttachMaster.objects.filter(mid=bill_id)

        return context

    @transaction.atomic
    def form_valid(self, form):
        """Save file to database."""
        bill_id = self.kwargs.get('bill_id')
        uploaded_file = form.cleaned_data['file']

        # Read file content
        file_content = uploaded_file.read()

        # Create attachment record
        attachment = TblaccBillbookingAttachMaster.objects.create(
            mid=bill_id,
            compid=self.get_compid(),
            sessionid=self.request.session.session_key,
            finyearid=self.get_finyearid(),
            filename=uploaded_file.name,
            filesize=uploaded_file.size,
            contenttype=uploaded_file.content_type,
            filedata=file_content
        )
        
        self.object = attachment
        return HttpResponseRedirect(self.get_success_url())

class BillBookingAttachmentDownloadView(LoginRequiredMixin, DetailView):
    """
    Download attachment from bill booking.
    Retrieves file from database and serves it.
    
    Requirements: 6.9
    """
    model = TblaccBillbookingAttachMaster
    pk_url_kwarg = 'attachment_id'
    
    def get(self, request, *args, **kwargs):
        """Serve file for download."""
        attachment = self.get_object()
        
        # Create response with file content
        response = HttpResponse(
            bytes(attachment.filedata),
            content_type=attachment.contenttype or 'application/octet-stream'
        )
        
        # Set filename for download
        response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
        response['Content-Length'] = attachment.filesize
        
        return response

class BillBookingAttachmentDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete attachment from bill booking.

    Requirements: 6.9
    """
    model = TblaccBillbookingAttachMaster
    pk_url_kwarg = 'attachment_id'

    def get_success_url(self):
        """Redirect back to bill booking edit page."""
        bill_id = self.object.mid
        return reverse_lazy('accounts:bill-booking-edit', kwargs={'id': bill_id})



# ============================================================================
# Proforma Invoice Views
# ============================================================================

from ...models import TblaccProformainvoiceMaster, TblaccProformainvoiceDetails
from ...forms import ProformaInvoiceHeaderForm, ProformaInvoiceDetailFormSet

class BillBookingPrintView(LoginRequiredMixin, DetailView):
    """
    Generate PDF for Bill Booking.
    Converted from: aspnet/Module/Accounts/Transactions/BillBooking_Print.aspx
    """
    model = TblaccBillbookingMaster
    pk_url_kwarg = 'id'
    template_name = 'accounts/transactions/bill_booking_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bill = self.get_object()

        # Get bill details
        details = TblaccBillbookingDetails.objects.filter(mid=bill.id)

        # Get financial year name
        finyear_name = None
        try:
            from sys_admin.models import TblfinancialMaster as FinancialYear
            finyear = FinancialYear.objects.get(pk=bill.finyearid)
            finyear_name = finyear.finyear
        except:
            finyear_name = str(bill.finyearid)

        # Calculate totals
        subtotal = sum((detail.qty or 0) * (detail.rate or 0) for detail in details)

        context.update({
            'bill': bill,
            'details': details,
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
        bill_no = context['bill'].billno if context['bill'].billno else f'BB_{context["bill"].id}'
        filename = f'Bill_Booking_{bill_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response


# ============================================================================
# ============================================================================
# NOTE: All master views below need to be implemented
# These imports are commented out until the view files are created
# ============================================================================
# from .payment_mode_views import PaymentModeListView, PaymentModeCreateView, PaymentModeUpdateView, PaymentModeDeleteView
# from .iou_reasons_views import IOUReasonsListView, IOUReasonsCreateView, IOUReasonsUpdateView, IOUReasonsDeleteView
# from .warranty_terms_views import WarrentyTermsListView, WarrentyTermsCreateView, WarrentyTermsUpdateView, WarrentyTermsDeleteView
# from .excisable_commodity_views import ExcisableCommodityListView, ExcisableCommodityCreateView, ExcisableCommodityUpdateView, ExcisableCommodityDeleteView
# from .paid_type_views import PaidTypeListView, PaidTypeCreateView, PaidTypeUpdateView, PaidTypeDeleteView
# from .freight_views import FreightListView, FreightCreateView, FreightUpdateView, FreightDeleteView
# from .vat_views import VATListView, VATCreateView, VATUpdateView, VATDeleteView
# from .excise_service_views import ExciseServiceListView, ExciseServiceCreateView, ExciseServiceUpdateView, ExciseServiceDeleteView
# from .interest_type_views import InterestTypeListView, InterestTypeCreateView, InterestTypeUpdateView, InterestTypeDeleteView
# from .invoice_against_views import InvoiceAgainstListView, InvoiceAgainstCreateView, InvoiceAgainstUpdateView, InvoiceAgainstDeleteView
# from .loan_type_views import LoanTypeListView, LoanTypeCreateView, LoanTypeUpdateView, LoanTypeDeleteView
# from .octroi_views import OctroiListView, OctroiCreateView, OctroiUpdateView, OctroiDeleteView
# from .accounts_masters_views import CurrencyListView, CurrencyCreateView, CurrencyUpdateView, CurrencyDeleteView, TDSCodeListView, TDSCodeCreateView, TDSCodeUpdateView, TDSCodeDeleteView, PackingListView, PackingCreateView, PackingUpdateView, PackingDeleteView
# from .bank_master_views import BankListView, BankCreateView, BankUpdateView, BankDeleteView
# from .process_master_views import ProcessListView, ProcessCreateView, ProcessUpdateView, ProcessDeleteView

