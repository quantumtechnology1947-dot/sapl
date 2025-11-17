"""
Views for Creditors/Debitors Management.
Converted from ASP.NET Module/Accounts/Transactions/CreditorsDebitors.aspx
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.contrib import messages
from datetime import datetime

# Import core mixins for standardized view behavior
from core.mixins import (
    BaseListViewMixin, BaseCreateViewMixin, BaseUpdateViewMixin,
    BaseDeleteViewMixin, BaseDetailViewMixin, HTMXResponseMixin,
    CompanyFinancialYearMixin, AuditMixin
)

from ..models import (
    TblaccCreditorsMaster, TblaccDebitorsMaster
)
from ..forms import (
    CreditorForm, DebitorForm, DateRangeFilterForm
)
from ..services import CreditorService, DebitorService, SundryCreditorService


# ============================================================================
# Creditors/Debitors List View - Dual Tab Interface
# ============================================================================

class CreditorsDebitorsListView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Main Creditors/Debitors list page with dual-tab interface.
    Matches ASP.NET CreditorsDebitors.aspx

    Shows:
    - Creditors tab: All suppliers with opening, booked bills, TDS, payments, closing
    - Debitors tab: All customers with opening, sales invoices, service invoices, closing
    """
    template_name = 'accounts/creditors_debitors/list.html'

    def get_context_data(self, **kwargs):
        """Get both creditors and debitors data."""
        context = super().get_context_data(**kwargs)

        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # DEBUG: Print session values
        print(f"DEBUG: CompId={company_id}, FinYearId={financial_year_id}")

        # Get all creditors with balances
        creditors = CreditorService.get_all_creditors(
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        # DEBUG: Print counts
        print(f"DEBUG: Creditors count={len(creditors)}")

        # Get all debitors with balances
        debitors = DebitorService.get_all_debitors(
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        # DEBUG: Print counts
        print(f"DEBUG: Debitors count={len(debitors)}")

        context['creditors'] = creditors
        context['debitors'] = debitors

        # Calculate totals
        context['creditors_total'] = sum(c['closing'] for c in creditors)
        context['debitors_total'] = sum(d['closing'] for d in debitors)

        return context


# ============================================================================
# HTMX Endpoints for Tab Content
# ============================================================================

class CreditorsTabView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint for creditors tab content.
    Returns partial HTML for creditors grid.
    """
    template_name = 'accounts/creditors_debitors/partials/creditors_tab.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # Get all creditors with balances
        creditors = CreditorService.get_all_creditors(
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        context['creditors'] = creditors
        context['creditors_total'] = sum(c['closing'] for c in creditors)

        return context


class DebitorsTabView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint for debitors tab content.
    Returns partial HTML for debitors grid.
    """
    template_name = 'accounts/creditors_debitors/partials/debitors_tab.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # Get all debitors with balances
        debitors = DebitorService.get_all_debitors(
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        context['debitors'] = debitors
        context['debitors_total'] = sum(d['closing'] for d in debitors)

        return context


# ============================================================================
# Creditor Create/Delete Views
# ============================================================================

class CreditorCreateView(CompanyFinancialYearMixin, LoginRequiredMixin, AuditMixin, CreateView):
    """
    Create new creditor opening balance.
    """
    model = TblaccCreditorsMaster
    form_class = CreditorForm
    template_name = 'accounts/creditors_debitors/creditor_form.html'
    success_url = reverse_lazy('accounts:creditors-debitors')

    def form_valid(self, form):
        """Set company and financial year before saving."""
        creditor = form.save(commit=False)

        # Set audit fields
        creditor.compid = self.get_compid()
        creditor.finyearid = self.get_finyearid()
        self.set_audit_fields(creditor, self.request)

        creditor.save()

        messages.success(self.request, 'Creditor opening balance created successfully.')
        return HttpResponseRedirect(self.success_url)


class CreditorDeleteView(CompanyFinancialYearMixin, LoginRequiredMixin, DeleteView):
    """
    Delete creditor opening balance.
    """
    model = TblaccCreditorsMaster
    success_url = reverse_lazy('accounts:creditors-debitors')

    def get_queryset(self):
        """Filter by company and financial year."""
        return super().get_queryset().filter(
            compid=self.get_compid(),
            finyearid=self.get_finyearid()
        )

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Creditor opening balance deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# Debitor Create/Delete Views
# ============================================================================

class DebitorCreateView(CompanyFinancialYearMixin, LoginRequiredMixin, AuditMixin, CreateView):
    """
    Create new debitor opening balance.
    """
    model = TblaccDebitorsMaster
    form_class = DebitorForm
    template_name = 'accounts/creditors_debitors/debitor_form.html'
    success_url = reverse_lazy('accounts:creditors-debitors')

    def form_valid(self, form):
        """Set company and financial year before saving."""
        debitor = form.save(commit=False)

        # Set audit fields
        debitor.compid = self.get_compid()
        debitor.finyearid = self.get_finyearid()
        self.set_audit_fields(debitor, self.request)

        debitor.save()

        messages.success(self.request, 'Debitor opening balance created successfully.')
        return HttpResponseRedirect(self.success_url)


class DebitorDeleteView(CompanyFinancialYearMixin, LoginRequiredMixin, DeleteView):
    """
    Delete debitor opening balance.
    """
    model = TblaccDebitorsMaster
    success_url = reverse_lazy('accounts:creditors-debitors')

    def get_queryset(self):
        """Filter by company and financial year."""
        return super().get_queryset().filter(
            compid=self.get_compid(),
            finyearid=self.get_finyearid()
        )

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Debitor opening balance deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# Detail Views - Transaction History
# ============================================================================

class CreditorsDetailView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Show detailed transaction history for a specific creditor.
    Matches ASP.NET CreditorsDebitors_InDetailList.aspx

    Shows:
    - Bill bookings
    - Payments (bank and cash)
    - TDS deductions
    - Running balance
    """
    template_name = 'accounts/creditors_debitors/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        supplier_id = kwargs.get('supplier_id')
        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # Get date filters if provided
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # Get supplier info
        from material_management.models import TblmmSupplierMaster
        supplier = get_object_or_404(TblmmSupplierMaster, supplierid=supplier_id)

        # Get summary
        summary = CreditorService.get_creditor_summary(
            supplier_id=supplier_id,
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        # Get transactions
        transactions = CreditorService.get_creditor_transactions(
            supplier_id=supplier_id,
            company_id=company_id,
            financial_year_id=financial_year_id,
            from_date=from_date,
            to_date=to_date
        )

        # Calculate running balance
        running_balance = summary['opening']
        for txn in transactions:
            running_balance += txn['debit']
            running_balance -= txn['credit']
            txn['balance'] = running_balance

        context['supplier'] = supplier
        context['summary'] = summary
        context['transactions'] = transactions
        context['from_date'] = from_date
        context['to_date'] = to_date
        context['filter_form'] = DateRangeFilterForm(initial={
            'from_date': from_date,
            'to_date': to_date
        })

        return context


class DebitorsDetailView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Show detailed transaction history for a specific debitor.

    Shows:
    - Sales invoices
    - Service tax invoices
    - Proforma invoices
    - Running balance
    """
    template_name = 'accounts/creditors_debitors/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        customer_id = kwargs.get('customer_id')
        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # Get date filters if provided
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # Get customer info
        from sales_distribution.models import SdCustMaster
        customer = get_object_or_404(SdCustMaster, salesid=customer_id)

        # Get summary
        summary = DebitorService.get_debitor_summary(
            customer_id=customer_id,
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        # Get transactions
        transactions = DebitorService.get_debitor_transactions(
            customer_id=customer_id,
            company_id=company_id,
            financial_year_id=financial_year_id,
            from_date=from_date,
            to_date=to_date
        )

        # Calculate running balance
        running_balance = summary['opening']
        for txn in transactions:
            running_balance += txn['debit']
            running_balance -= txn['credit']
            txn['balance'] = running_balance

        context['customer'] = customer
        context['summary'] = summary
        context['transactions'] = transactions
        context['from_date'] = from_date
        context['to_date'] = to_date
        context['filter_form'] = DateRangeFilterForm(initial={
            'from_date': from_date,
            'to_date': to_date
        })
        context['is_debitor'] = True  # Flag to differentiate in template

        return context


# ============================================================================
# Sundry Creditors Views
# ============================================================================

class SundryCreditorsView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Sundry creditors summary grouped by category.
    Matches ASP.NET SundryCreditors.aspx

    Shows balance sheet view with categories:
    - Opening balance
    - Debit (payments + TDS)
    - Credit (booked bills)
    - Closing balance
    """
    template_name = 'accounts/creditors_debitors/sundry/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # Get category summary
        category_data = SundryCreditorService.get_category_summary(
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        context['categories'] = category_data

        # Calculate grand totals
        context['grand_opening'] = sum(cat['opening'] for cat in category_data)
        context['grand_debit'] = sum(cat['debit'] for cat in category_data)
        context['grand_credit'] = sum(cat['credit'] for cat in category_data)
        context['grand_closing'] = sum(cat['closing'] for cat in category_data)

        return context


class SundryCreditorsCategoryView(CompanyFinancialYearMixin, LoginRequiredMixin, TemplateView):
    """
    Show detailed supplier list for a specific category.
    """
    template_name = 'accounts/creditors_debitors/sundry/category_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_name = kwargs.get('category')
        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        # Get supplier details for this category
        suppliers = SundryCreditorService.get_category_details(
            category_name=category_name,
            company_id=company_id,
            financial_year_id=financial_year_id
        )

        context['category'] = category_name
        context['suppliers'] = suppliers

        # Calculate totals
        context['total_opening'] = sum(s['opening'] for s in suppliers)
        context['total_booked_bills'] = sum(s['booked_bills'] for s in suppliers)
        context['total_tds'] = sum(s['tds'] for s in suppliers)
        context['total_payments'] = sum(s['payments'] for s in suppliers)
        context['total_closing'] = sum(s['closing'] for s in suppliers)

        return context
