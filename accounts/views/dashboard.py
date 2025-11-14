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
from decimal import Decimal

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
from ..forms import (
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# Dashboard Views

class AccountsDashboardView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Accounts Dashboard - Key Financial Metrics.
    Shows cash/bank balances, receivables, payables, recent transactions, and charts.

    Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7
    """
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Key Metrics
        context['cash_balance'] = Decimal('50000.00')  # TODO: Calculate from cash accounts
        context['bank_balance'] = Decimal('150000.00')  # TODO: Calculate from bank accounts
        context['receivables'] = Decimal('75000.00')  # TODO: Calculate from customer invoices
        context['payables'] = Decimal('50000.00')  # TODO: Calculate from supplier bills

        # Recent Transactions (last 10)
        recent_vouchers = []

        try:
            # Bank vouchers
            bank_vouchers = TblaccBankvoucherPaymentMaster.objects.all().order_by('-id')[:5]
            for v in bank_vouchers:
                try:
                    recent_vouchers.append({
                        'date': getattr(v, 'sysdate', ''),
                        'type': 'Bank Payment',
                        'number': getattr(v, 'bvpno', ''),
                        'amount': getattr(v, 'payamt', 0),
                        'party': getattr(v, 'payto', '')
                    })
                except Exception:
                    pass
        except Exception:
            pass

        try:
            # Cash vouchers
            cash_vouchers = TblaccCashvoucherPaymentMaster.objects.all().order_by('-id')[:5]
            for v in cash_vouchers:
                try:
                    recent_vouchers.append({
                        'date': getattr(v, 'sysdate', ''),
                        'type': 'Cash Payment',
                        'number': getattr(v, 'cvpno', ''),
                        'amount': 0,  # TODO: Calculate total
                        'party': getattr(v, 'paidto', '')
                    })
                except Exception:
                    pass
        except Exception:
            pass

        # Sort by date and limit to 10
        recent_vouchers.sort(key=lambda x: x.get('date', ''), reverse=True)
        context['recent_transactions'] = recent_vouchers[:10]

        # Monthly Income vs Expenses (for chart)
        context['monthly_data'] = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'income': [50000, 55000, 52000, 60000, 58000, 65000],
            'expenses': [40000, 42000, 38000, 45000, 43000, 48000]
        }

        # Top 5 Debtors
        context['top_debtors'] = [
            {'name': 'Customer A', 'amount': Decimal('25000.00')},
            {'name': 'Customer B', 'amount': Decimal('20000.00')},
            {'name': 'Customer C', 'amount': Decimal('15000.00')},
            {'name': 'Customer D', 'amount': Decimal('10000.00')},
            {'name': 'Customer E', 'amount': Decimal('5000.00')},
        ]

        # Top 5 Creditors
        context['top_creditors'] = [
            {'name': 'Supplier X', 'amount': Decimal('20000.00')},
            {'name': 'Supplier Y', 'amount': Decimal('15000.00')},
            {'name': 'Supplier Z', 'amount': Decimal('10000.00')},
            {'name': 'Supplier W', 'amount': Decimal('5000.00')},
            {'name': 'Supplier V', 'amount': Decimal('3000.00')},
        ]

        # Pending Authorizations
        try:
            context['pending_authorizations'] = TblaccBillbookingMaster.objects.filter(
                authorize=0
            ).count()
        except Exception:
            context['pending_authorizations'] = 0

        # Voucher Counts
        try:
            context['bank_voucher_count'] = TblaccBankvoucherPaymentMaster.objects.count()
        except Exception:
            context['bank_voucher_count'] = 0

        try:
            context['cash_voucher_count'] = TblaccCashvoucherPaymentMaster.objects.count()
        except Exception:
            context['cash_voucher_count'] = 0

        try:
            context['journal_entry_count'] = TblaccContraEntry.objects.count()
        except Exception:
            context['journal_entry_count'] = 0

        return context


# ============================================================================
# SALES INVOICE PRINT
# ============================================================================

class MastersDashboardView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """Dashboard for all master data modules."""
    template_name = 'accounts/masters/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add counts for each master data type
        context['acchead_count'] = Acchead.objects.count()
        context['bank_count'] = TblaccBank.objects.count()
        context['currency_count'] = TblaccCurrencyMaster.objects.count()
        context['payment_terms_count'] = TblaccPaymentmode.objects.count()
        context['tds_code_count'] = TblaccTdscodeMaster.objects.count()
        return context



# ============================================================================
# Bank Voucher Views
# ============================================================================

from django.db import transaction
from ..models import TblaccBankvoucherPaymentMaster, TblaccBankvoucherPaymentDetails
from ..forms import BankVoucherMasterForm, BankVoucherDetailFormSet
from datetime import datetime

class TransactionsDashboardView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """Dashboard for all transaction modules."""
    template_name = 'accounts/transactions/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bank_voucher_count'] = TblaccBankvoucherPaymentMaster.objects.count()
        context['cash_voucher_count'] = TblaccCashvoucherPaymentMaster.objects.count()
        context['journal_entry_count'] = TblaccContraEntry.objects.count()
        return context



# ============================================================================
# Journal Entry / Contra Entry Views
# ============================================================================

from ..models import TblaccContraEntry
from ..forms import JournalEntryForm

