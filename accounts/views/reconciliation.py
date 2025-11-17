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
from ..models import (
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
    TblaccBank, TblaccBankamtMaster, TblpackingMaster, TblaccContraEntry,
    TblaccCurrencyMaster, TblaccTdscodeMaster, TblvatMaster, TblwarrentyMaster,
    TblaccAssetRegister, TblaccDebitnote,
    # Simple lookup masters
    TblaccIntresttype, TblaccInvoiceagainst, TblaccIouReasons, TblaccLoantype,
    TblaccPaidtype, TblaccPaymentmode, TblaccReceiptagainst, TblaccTourexpencesstype,
    TblexcisecommodityMaster, TblexciseserMaster, TblfreightMaster, TbloctroiMaster,
)

# Import services
from ..services import ReconciliationService

# Import GST views
# TODO: Implement GST views
# from .gst_views import GSTListView, GSTCreateView, GSTUpdateView, GSTDeleteView

# Import new master views
# TODO: Create these view files
# from .invoice_type_views import InvoiceTypeListView, InvoiceTypeCreateView, InvoiceTypeUpdateView, InvoiceTypeDeleteView
# from .taxable_services_views import TaxableServicesListView, TaxableServicesCreateView, TaxableServicesUpdateView, TaxableServicesDeleteView
# from .loan_master_views import LoanMasterListView, LoanMasterCreateView, LoanMasterUpdateView, LoanMasterDeleteView
from ..forms import (
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Bank Reconciliation Views

class BankReconciliationView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Bank reconciliation view with unreconciled transactions list.
    Uses ReconciliationService for all reconciliation operations.

    Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8
    """
    template_name = 'accounts/reconciliation/bank_reconciliation.html'

    def get_context_data(self, **kwargs):
        """Get unreconciled transactions and reconciliation summary."""
        context = super().get_context_data(**kwargs)

        bank_id = self.kwargs.get('bank_id')
        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # Get bank details
        from ..models import TblaccBank
        bank = TblaccBank.objects.filter(id=bank_id).first()
        context['bank'] = bank

        # Get reconciled voucher IDs
        reconciled_payment_ids = set(
            TblaccBankrecanciliation.objects.filter(
                bvpid__isnull=False,
                compid=company_id,
                finyearid=financial_year_id
            ).values_list('bvpid', flat=True)
        )

        reconciled_receipt_ids = set(
            TblaccBankrecanciliation.objects.filter(
                bvrid__isnull=False,
                compid=company_id,
                finyearid=financial_year_id
            ).values_list('bvrid', flat=True)
        )

        # Get unreconciled payments
        unreconciled_payments = TblaccBankvoucherPaymentMaster.objects.filter(
            bank=bank_id,
            compid=company_id,
            finyearid=financial_year_id
        ).exclude(id__in=reconciled_payment_ids).order_by('-sysdate')

        # Get unreconciled receipts
        unreconciled_receipts = TblaccBankvoucherReceivedMasters.objects.filter(
            drawnat=bank_id,
            compid=company_id,
            finyearid=financial_year_id
        ).exclude(id__in=reconciled_receipt_ids).order_by('-sysdate')

        context['unreconciled_payments'] = unreconciled_payments
        context['unreconciled_receipts'] = unreconciled_receipts

        # Get reconciliation summary using ReconciliationService
        from datetime import datetime
        summary = ReconciliationService.calculate_reconciliation_summary(
            bank_id=bank_id,
            as_of_date=datetime.now().strftime('%Y-%m-%d'),
            company_id=company_id,
            financial_year_id=financial_year_id
        )
        context['reconciliation_summary'] = summary

        return context

class MarkAsReconciledView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint to mark transactions as reconciled.
    Uses ReconciliationService.mark_as_reconciled()

    Requirements: 9.4
    """

    def post(self, request, *args, **kwargs):
        """Handle HTMX POST request to mark vouchers as reconciled."""
        voucher_ids = request.POST.getlist('voucher_ids[]')
        voucher_type = request.POST.get('voucher_type', 'payment')
        bank_date = request.POST.get('bank_date')

        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()
        user_id = request.user.id

        # Use ReconciliationService to mark as reconciled
        result = ReconciliationService.mark_as_reconciled(
            voucher_ids=[int(vid) for vid in voucher_ids],
            voucher_type=voucher_type,
            bank_date=bank_date,
            user_id=user_id,
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        if request.headers.get('HX-Request'):
            # Return success message for HTMX
            return HttpResponse(
                f'<div class="bg-green-50 border-l-4 border-green-400 p-4">'
                f'<p class="text-sm text-green-700">'
                f'Successfully reconciled {result["reconciled_count"]} transactions '
                f'totaling {result["total_amount"]}'
                f'</p></div>'
            )

        return JsonResponse(result)

class ReconciliationSummaryView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    View to display reconciliation summary.
    Uses ReconciliationService.calculate_reconciliation_summary()

    Requirements: 9.7
    """
    template_name = 'accounts/reconciliation/summary.html'

    def get_context_data(self, **kwargs):
        """Get reconciliation summary."""
        context = super().get_context_data(**kwargs)

        bank_id = self.kwargs.get('bank_id')
        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        from datetime import datetime
        as_of_date = self.request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Use ReconciliationService to calculate summary
        summary = ReconciliationService.calculate_reconciliation_summary(
            bank_id=bank_id,
            as_of_date=as_of_date,
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        context['summary'] = summary

        # Get bank details
        from ..models import TblaccBank
        bank = TblaccBank.objects.filter(id=bank_id).first()
        context['bank'] = bank
        context['as_of_date'] = as_of_date

        return context


# ============================================================================
# Sales Invoice Views
# ============================================================================

from ..models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails
from ..forms import SalesInvoiceMasterForm, SalesInvoiceDetailFormSet

class BankReconciliationMarkView(CompanyFinancialYearMixin, LoginRequiredMixin, View):
    """
    Mark selected transactions as reconciled.
    AJAX endpoint for HTMX.

    Requirements: 9.4
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Mark transactions as reconciled."""
        bank_id = request.POST.get('bank_id')
        bank_date = request.POST.get('bank_date')
        payment_ids = request.POST.getlist('payment_ids[]')
        receipt_ids = request.POST.getlist('receipt_ids[]')

        # Mark payments as reconciled
        if payment_ids:
            ReconciliationService.mark_as_reconciled(
                voucher_ids=payment_ids,
                voucher_type='payment',
                bank_date=bank_date,
                user_id=request.user.id,
                company_id=self.get_compid(),
                financial_year_id=self.get_finyearid()
            )

        # Mark receipts as reconciled
        if receipt_ids:
            ReconciliationService.mark_as_reconciled(
                voucher_ids=receipt_ids,
                voucher_type='receipt',
                bank_date=bank_date,
                user_id=request.user.id,
                company_id=self.get_compid(),
                financial_year_id=self.get_finyearid()
            )

        # Return success response for HTMX
        if request.headers.get('HX-Request'):
            return HttpResponse('<div class="text-green-600">Transactions marked as reconciled</div>')

        return HttpResponseRedirect(reverse_lazy('accounts:bank-reconciliation', kwargs={'bank_id': bank_id}))

class BankChargesAddView(CompanyFinancialYearMixin, LoginRequiredMixin, CreateView):
    """
    Add bank charges and create journal entry.
    Uses ReconciliationService.add_bank_charges()

    Requirements: 9.5
    """
    template_name = 'accounts/reconciliation/bank_charges_form.html'
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bank_id = self.kwargs.get('bank_id')
        context['bank'] = TblaccBank.objects.get(id=bank_id)
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Add bank charges."""
        bank_id = self.kwargs.get('bank_id')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        narration = request.POST.get('narration')

        # Add bank charges using service
        result = ReconciliationService.add_bank_charges(
            bank_id=bank_id,
            amount=float(amount),
            date=date,
            narration=narration,
            user_id=request.user.id,
            company_id=self.get_compid(),
            financial_year_id=self.get_finyearid()
        )

        return HttpResponseRedirect(reverse_lazy('accounts:bank-reconciliation', kwargs={'bank_id': bank_id}))

class BankReconciliationListView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    List all banks with opening and closing amounts for reconciliation.
    Matches ASP.NET BankReconciliation_New.aspx

    Requirements: 9.1
    """
    template_name = 'accounts/reconciliation/bank_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # Get all banks with their amounts
        banks_data = []

        # Get banks (excluding Cash which has OrdNo=0)
        banks = TblaccBank.objects.filter(ordno__gt=0).order_by('ordno')

        # Always include Cash first
        cash_bank = TblaccBank.objects.filter(ordno=0).first()
        if cash_bank:
            # Get cash amounts from BankAmt_Master
            cash_amt = TblaccBankamtMaster.objects.filter(
                bankid=cash_bank.id,
                compid=company_id,
                finyearid=financial_year_id
            ).first()

            banks_data.append({
                'id': cash_bank.id,
                'trans': 'Cash',
                'opamt': cash_amt.amt if cash_amt else 0,
                'clamt': cash_amt.amt if cash_amt else 0,  # TODO: Calculate closing based on transactions
            })

        # Add other banks
        for idx, bank in enumerate(banks, start=2):
            # Get bank amounts from BankAmt_Master
            bank_amt = TblaccBankamtMaster.objects.filter(
                bankid=bank.id,
                compid=company_id,
                finyearid=financial_year_id
            ).first()

            banks_data.append({
                'id': bank.id,
                'trans': bank.name,
                'opamt': bank_amt.amt if bank_amt else 0,
                'clamt': bank_amt.amt if bank_amt else 0,  # TODO: Calculate closing based on transactions
            })

        context['banks_data'] = banks_data

        return context



# ============================================================================
# Asset Register Views
# ============================================================================

from ..models import TblaccAssetRegister, TblaccAssetCategory, TblaccAssetSubcategory
from ..forms import AssetRegisterForm, AssetDisposalForm

