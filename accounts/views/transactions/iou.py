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

# IOU Transaction Views

class IOUListView(BaseListViewMixin, ListView):
    """
    Display paginated list of IOU payments with search and filter functionality.
    Supports both Payment and Receipt views via tab parameter.
    Converted from: aspnet/Module/Accounts/Transactions/IOU_PaymentReceipt.aspx
    """
    model = TblaccIouMaster
    template_name = 'accounts/transactions/iou_payment_receipt_list.html'
    partial_template_name = 'accounts/transactions/partials/iou_payment_receipt_list_partial.html'
    context_object_name = 'ious'
    paginate_by = 20
    search_fields = ['empid', 'amount', 'narration']

    def get_queryset(self):
        """Filter IOUs based on search query and payment/receipt status."""
        queryset = super().get_queryset().order_by('-id')
        tab = self.request.GET.get('tab', 'payment')  # payment or receipt

        # Filter by payment/receipt status
        if tab == 'receipt':
            # Show only received IOUs
            queryset = queryset.filter(recieved=1)

        return queryset

    def get_context_data(self, **kwargs):
        """Add employee/reason lookups and active tab to context."""
        context = super().get_context_data(**kwargs)
        context['active_tab'] = self.request.GET.get('tab', 'payment')

        # Get IOU reasons for display
        reasons_dict = {}
        try:
            reasons = TblaccIouReasons.objects.all()
            for reason in reasons:
                reasons_dict[reason.id] = reason.terms
        except:
            pass
        context['reasons_dict'] = reasons_dict

        # Get employee names (cross-module integration with HR)
        employees_dict = {}
        try:
            from human_resource.models import Employeemaster
            employees = Employeemaster.objects.all()
            for emp in employees:
                employees_dict[str(emp.empid)] = emp.empname
        except:
            pass
        context['employees_dict'] = employees_dict

        return context

class IOUCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new IOU payment.
    Converted from: aspnet/Module/Accounts/Transactions/IOU_PaymentReceipt.aspx (create mode)
    """
    model = TblaccIouMaster
    template_name = 'accounts/transactions/iou_payment_receipt_form.html'
    partial_template_name = 'accounts/transactions/partials/iou_payment_receipt_form_partial.html'
    fields = ['empid', 'paymentdate', 'amount', 'reason', 'narration']
    success_url = reverse_lazy('accounts:iou-list')
    success_message = 'IOU payment created successfully.'

    def get_context_data(self, **kwargs):
        """Add IOU reasons and employees to context."""
        context = super().get_context_data(**kwargs)

        # Get IOU reasons
        try:
            context['reasons'] = TblaccIouReasons.objects.all()
        except:
            context['reasons'] = []

        # Get employees (cross-module integration with HR)
        try:
            from human_resource.models import Employeemaster
            context['employees'] = Employeemaster.objects.all()
        except:
            context['employees'] = []

        return context

    def form_valid(self, form):
        """Set audit fields and default authorization status before saving."""
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessionid = str(self.request.user.id)
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()

        # Default authorization status
        form.instance.authorize = 0  # Not authorized by default
        form.instance.recieved = 0   # Not received by default

        return super().form_valid(form)

class IOUUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing IOU payment.
    Converted from: aspnet/Module/Accounts/Transactions/IOU_PaymentReceipt.aspx (edit mode)
    """
    model = TblaccIouMaster
    template_name = 'accounts/transactions/iou_payment_receipt_form.html'
    partial_template_name = 'accounts/transactions/partials/iou_payment_receipt_form_partial.html'
    fields = ['empid', 'paymentdate', 'amount', 'reason', 'narration']
    success_url = reverse_lazy('accounts:iou-list')
    success_message = 'IOU payment updated successfully.'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        """Add IOU reasons and employees to context."""
        context = super().get_context_data(**kwargs)

        # Get IOU reasons
        try:
            context['reasons'] = TblaccIouReasons.objects.all()
        except:
            context['reasons'] = []

        # Get employees (cross-module integration with HR)
        try:
            from human_resource.models import Employeemaster
            context['employees'] = Employeemaster.objects.all()
        except:
            context['employees'] = []

        return context

    def form_valid(self, form):
        """Update audit fields."""
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessionid = str(self.request.user.id)

        return super().form_valid(form)

class IOUDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete IOU payment.
    Converted from: aspnet/Module/Accounts/Transactions/IOU_PaymentReceipt.aspx (delete action)
    """
    model = TblaccIouMaster
    template_name = 'accounts/transactions/iou_payment_receipt_confirm_delete.html'
    success_url = reverse_lazy('accounts:iou-list')
    pk_url_kwarg = 'id'

class IOUAuthorizeView(CompanyFinancialYearMixin, LoginRequiredMixin, View):
    """
    Handle IOU authorization workflow.
    Allows authorized users to approve/reject IOUs.
    Converted from: aspnet/Module/Accounts/Transactions/IOU_PaymentReceipt.aspx (authorize checkbox)
    """
    def post(self, request, id):
        """Authorize or unauthorize an IOU."""
        iou = TblaccIouMaster.objects.get(pk=id)

        # Toggle authorization status
        now = datetime.now()
        if iou.authorize == 0:
            iou.authorize = 1
            iou.authorizeddate = now.strftime('%d-%m-%Y')
            iou.authorizedtime = now.strftime('%H:%M:%S')
            iou.authorizedby = str(request.user.id)
        else:
            iou.authorize = 0
            iou.authorizeddate = None
            iou.authorizedtime = None
            iou.authorizedby = None

        iou.save()

        # Redirect back to list
        return HttpResponseRedirect(reverse_lazy('accounts:iou-list'))

class IOUReceiveView(CompanyFinancialYearMixin, LoginRequiredMixin, View):
    """
    Mark IOU as received/returned by employee.
    Updates the 'recieved' status to move IOU from Payment to Receipt tab.
    Converted from: aspnet/Module/Accounts/Transactions/IOU_PaymentReceipt.aspx (Receipt tab)
    """
    def post(self, request, id):
        """Mark IOU as received."""
        iou = TblaccIouMaster.objects.get(pk=id)

        # Toggle received status
        if iou.recieved == 0 or iou.recieved is None:
            iou.recieved = 1
        else:
            iou.recieved = 0

        iou.save()

        # Redirect back to list
        return HttpResponseRedirect(reverse_lazy('accounts:iou-list'))


# ============================================================================
# Print Views for Vouchers and Invoices
# ============================================================================

