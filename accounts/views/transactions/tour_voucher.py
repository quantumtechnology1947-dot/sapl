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

# Tour Voucher Transaction Views

class TourVoucherListView(BaseListViewMixin, ListView):
    """
    Display paginated list of tour vouchers with search functionality.
    Converted from: aspnet/Module/Accounts/Transactions/TourVoucher.aspx
    """
    model = TblaccTourvoucherMaster
    template_name = 'accounts/transactions/tour_voucher_list.html'
    partial_template_name = 'accounts/transactions/partials/tour_voucher_list_partial.html'
    context_object_name = 'vouchers'
    paginate_by = 20
    search_fields = ['tvno', 'timid']

    def get_queryset(self):
        """Filter tour vouchers with ordering."""
        return super().get_queryset().order_by('-id')

class TourVoucherCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new tour voucher.
    Converted from: aspnet/Module/Accounts/Transactions/TourVoucher.aspx (create mode)
    """
    model = TblaccTourvoucherMaster
    template_name = 'accounts/transactions/tour_voucher_form.html'
    partial_template_name = 'accounts/transactions/partials/tour_voucher_form_partial.html'
    fields = ['timid', 'tvno', 'amtbaltowardscompany', 'amtbaltowardsemployee']
    success_url = reverse_lazy('accounts:tour-voucher-list')
    success_message = 'Tour voucher created successfully.'

    def form_valid(self, form):
        """Set audit fields before saving."""
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessionid = str(self.request.user.id)
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()

        return super().form_valid(form)

class TourVoucherUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing tour voucher.
    Converted from: aspnet/Module/Accounts/Transactions/TourVoucher_Edit.aspx
    """
    model = TblaccTourvoucherMaster
    template_name = 'accounts/transactions/tour_voucher_form.html'
    partial_template_name = 'accounts/transactions/partials/tour_voucher_form_partial.html'
    fields = ['timid', 'tvno', 'amtbaltowardscompany', 'amtbaltowardsemployee']
    success_url = reverse_lazy('accounts:tour-voucher-list')
    success_message = 'Tour voucher updated successfully.'
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        """Update audit fields."""
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessionid = str(self.request.user.id)

        return super().form_valid(form)

class TourVoucherDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete tour voucher.
    Converted from: aspnet/Module/Accounts/Transactions/TourVoucher (delete action)
    """
    model = TblaccTourvoucherMaster
    template_name = 'accounts/transactions/tour_voucher_confirm_delete.html'
    success_url = reverse_lazy('accounts:tour-voucher-list')
    pk_url_kwarg = 'id'

class TourVoucherPrintView(LoginRequiredMixin, DetailView):
    """
    Generate professional PDF for Tour Voucher.
    Converted from: aspnet/Module/Accounts/Transactions/TourVoucher_Print.aspx
    """
    model = TblaccTourvoucherMaster
    pk_url_kwarg = 'id'
    template_name = 'accounts/transactions/tour_voucher_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()

        # Get voucher details
        details = TblaccTourvoucheradvanceDetails.objects.filter(mid=voucher.id)

        # Get Tour Intimation info
        try:
            tour_intimation = TblaccTourintimationMaster.objects.get(id=voucher.timid)
        except:
            tour_intimation = None

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
            'details': details,
            'tour_intimation': tour_intimation,
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
        voucher_no = context['voucher'].tvno if context['voucher'].tvno else f'TV_{context["voucher"].id}'
        filename = f'Tour_Voucher_{voucher_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response


# ============================================================================
# IOU Payment/Receipt Transaction Views
# Converted from: aspnet/Module/Accounts/Transactions/IOU_PaymentReceipt.aspx
# ============================================================================

