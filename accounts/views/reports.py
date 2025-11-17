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
    TblaccBank, TblpackingMaster, TblaccContraEntry,
    TblaccCurrencyMaster, TblaccTdscodeMaster, TblvatMaster, TblwarrentyMaster,
    TblaccAssetRegister, TblaccDebitnote,
    # Simple lookup masters
    TblaccIntresttype, TblaccInvoiceagainst, TblaccIouReasons, TblaccLoantype,
    TblaccPaidtype, TblaccPaymentmode, TblaccReceiptagainst, TblaccTourexpencesstype,
    TblexcisecommodityMaster, TblexciseserMaster, TblfreightMaster, TbloctroiMaster,
)

# Import services
from ..services import ReportService

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

# Financial Report Views

class BalanceSheetView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Balance Sheet Report - Financial Position.
    Shows Assets, Liabilities, and Equity as of a specific date.

    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
    """
    template_name = 'accounts/reports/balance_sheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date parameter (default to today)
        as_of_date = self.request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Generate report
        report_data = ReportService.generate_balance_sheet(
            as_of_date=as_of_date,
            company_id=self.get_compid(),
            financial_year_id=self.get_finyearid()
        )

        context['report'] = report_data
        context['as_of_date'] = as_of_date

        return context

class ProfitLossView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Profit & Loss Report - Financial Performance.
    Shows Income and Expenses for a period.

    Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
    """
    template_name = 'accounts/reports/profit_loss.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date range parameters
        from_date = self.request.GET.get('from_date', datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        to_date = self.request.GET.get('to_date', datetime.now().strftime('%Y-%m-%d'))

        # Generate report
        report_data = ReportService.generate_profit_loss(
            from_date=from_date,
            to_date=to_date,
            company_id=self.get_compid(),
            financial_year_id=self.get_finyearid()
        )

        context['report'] = report_data
        context['from_date'] = from_date
        context['to_date'] = to_date

        return context

class TrialBalanceView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Trial Balance Report - Account Verification.
    Shows all accounts with debit/credit totals.

    Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7
    """
    template_name = 'accounts/reports/trial_balance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date parameter
        as_of_date = self.request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Generate report
        report_data = ReportService.generate_trial_balance(
            as_of_date=as_of_date,
            company_id=self.get_compid(),
            financial_year_id=self.get_finyearid()
        )

        context['report'] = report_data
        context['as_of_date'] = as_of_date

        return context

class LedgerView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Ledger Report - Account Transaction Details.
    Shows all transactions for a specific account.

    Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7
    """
    template_name = 'accounts/reports/ledger.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get parameters
        account_id = self.request.GET.get('account_id')
        from_date = self.request.GET.get('from_date', datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        to_date = self.request.GET.get('to_date', datetime.now().strftime('%Y-%m-%d'))

        # Get all accounts for dropdown
        context['accounts'] = Acchead.objects.all().order_by('description')
        context['selected_account'] = account_id
        context['from_date'] = from_date
        context['to_date'] = to_date

        # Generate report if account selected
        if account_id:
            report_data = ReportService.generate_ledger(
                account_id=int(account_id),
                from_date=from_date,
                to_date=to_date,
                company_id=self.get_compid(),
                financial_year_id=self.get_finyearid()
            )
            context['report'] = report_data

        return context

class AgingReportView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Aging Report - Creditors/Debtors Analysis.
    Shows outstanding amounts in aging buckets.

    Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7
    """
    template_name = 'accounts/reports/aging_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get parameters
        report_type = self.request.GET.get('type', 'debtors')
        as_of_date = self.request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Generate report
        report_data = ReportService.generate_aging_report(
            report_type=report_type,
            as_of_date=as_of_date,
            company_id=self.get_compid(),
            financial_year_id=self.get_finyearid()
        )

        context['report'] = report_data
        context['report_type'] = report_type
        context['as_of_date'] = as_of_date

        return context



# ============================================================================
# Dashboard View
# ============================================================================

