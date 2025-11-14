"""
Human Resource Loan and Mobile Bill Management Views
Handles bank loan tracking and mobile bill management
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models
from datetime import datetime

from core.mixins import (
    BaseListViewMixin, BaseCreateViewMixin, BaseUpdateViewMixin,
    BaseDeleteViewMixin, BaseDetailViewMixin
)
from ..models import (
    TblhrBankloan, TblhrMobilebill, TblhrOfficestaff, TblhrCoporatemobileno
)
from ..forms import BankLoanForm, MobileBillForm
from ..services.loan_service import LoanService


# =============================================================================
# BANK LOAN VIEWS
# =============================================================================

class BankLoanListView(BaseListViewMixin, ListView):
    """
    Display list of bank loans with search and filters.
    Converted from: aspnet/Module/HR/Transactions/BankLoan.aspx
    Shows all employee bank loans with filtering options.
    """
    model = TblhrBankloan
    template_name = 'human_resource/transactions/bank_loan_list.html'
    context_object_name = 'loans'
    paginate_by = 20
    search_fields = ['empid', 'loanfrom']
    partial_template_name = 'human_resource/partials/bank_loan_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search by employee ID
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(empid__icontains=search_query) |
                models.Q(loanfrom__icontains=search_query)
            )

        # Filter by status (active/paid)
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(installment__gt=0)
        elif status_filter == 'paid':
            queryset = queryset.filter(installment=0)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Enhance loans with employee information and calculations
        loan_list = []
        for loan in context['loans']:
            try:
                employee = TblhrOfficestaff.objects.get(empid=loan.empid)
                remaining = LoanService.get_remaining_installments(loan)

                loan_list.append({
                    'loan': loan,
                    'employee': employee,
                    'remaining_installments': remaining
                })
            except TblhrOfficestaff.DoesNotExist:
                loan_list.append({
                    'loan': loan,
                    'employee': None,
                    'remaining_installments': 0
                })

        context['loan_list'] = loan_list
        context['status_filter'] = self.request.GET.get('status', '')

        return context


class BankLoanCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new bank loan record.
    Converted from: aspnet/Module/HR/Transactions/BankLoan.aspx (Create Mode)
    """
    model = TblhrBankloan
    form_class = BankLoanForm
    template_name = 'human_resource/transactions/bank_loan_form.html'
    partial_template_name = 'human_resource/partials/bank_loan_form.html'
    success_message = 'Bank loan created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get list of employees for dropdown
        employees = TblhrOfficestaff.objects.filter(
            compid=self.get_compid()
        ).order_by('employeename')
        context['employees'] = employees

        return context

    def form_valid(self, form):
        # Set company and financial year from session
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.sessionid = str(self.request.user.id)

        # Set system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        # Calculate installment if not provided
        if not form.instance.installment and form.instance.loanamt and form.instance.noofinstallment:
            form.instance.installment = LoanService.calculate_loan_installment(
                form.instance.loanamt,
                form.instance.noofinstallment
            )

        # Validate loan application
        is_valid, message = LoanService.validate_loan_application(
            form.instance.empid,
            form.instance.loanamt,
            self.get_compid(),
            self.get_finyearid()
        )

        if not is_valid:
            messages.error(self.request, message)
            return self.form_invalid(form)

        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse_lazy('human_resource:bank-loan-detail', kwargs={'pk': self.object.pk})


class BankLoanUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing bank loan record.
    Converted from: aspnet/Module/HR/Transactions/BankLoan.aspx (Edit Mode)
    """
    model = TblhrBankloan
    form_class = BankLoanForm
    template_name = 'human_resource/transactions/bank_loan_form.html'
    partial_template_name = 'human_resource/partials/bank_loan_form.html'
    success_message = 'Bank loan updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Calculate remaining installments
        remaining = LoanService.get_remaining_installments(self.object)
        context['remaining_installments'] = remaining

        return context

    def form_valid(self, form):
        # Update system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        # Recalculate installment if loan amount or tenure changed
        if form.instance.loanamt and form.instance.noofinstallment:
            form.instance.installment = LoanService.calculate_loan_installment(
                form.instance.loanamt,
                form.instance.noofinstallment
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('human_resource:bank-loan-detail', kwargs={'pk': self.object.pk})


class BankLoanDetailView(BaseDetailViewMixin, DetailView):
    """
    Display detailed bank loan information.
    Converted from: aspnet/Module/HR/Transactions/BankLoan.aspx (View Mode)
    """
    model = TblhrBankloan
    template_name = 'human_resource/transactions/bank_loan_detail.html'
    context_object_name = 'loan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Calculate loan details
        remaining = LoanService.get_remaining_installments(self.object)
        context['remaining_installments'] = remaining

        # Calculate total outstanding
        total_outstanding = (remaining or 0) * (self.object.installment or 0)
        context['total_outstanding'] = total_outstanding

        # Calculate total paid
        total_installments = self.object.noofinstallment or 0
        paid_installments = total_installments - (remaining or 0)
        total_paid = paid_installments * (self.object.installment or 0)
        context['total_paid'] = total_paid
        context['paid_installments'] = paid_installments

        return context


class BankLoanDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete bank loan record.
    Converted from: aspnet/Module/HR/Transactions/BankLoan.aspx (Delete)
    """
    model = TblhrBankloan
    success_url = reverse_lazy('human_resource:bank-loan-list')
    template_name = 'human_resource/transactions/bank_loan_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Bank loan record for {self.object.empid} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# =============================================================================
# MOBILE BILL VIEWS
# =============================================================================

class MobileBillListView(BaseListViewMixin, ListView):
    """
    Display list of mobile bills with search and filters.
    Converted from: aspnet/Module/HR/Transactions/MobileBill.aspx
    Shows all employee mobile bills with excess calculations.
    """
    model = TblhrMobilebill
    template_name = 'human_resource/transactions/mobile_bill_list.html'
    context_object_name = 'bills'
    paginate_by = 20
    search_fields = ['empid']
    partial_template_name = 'human_resource/partials/mobile_bill_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by month
        month_filter = self.request.GET.get('month', '')
        if month_filter:
            queryset = queryset.filter(billmonth=month_filter)

        # Search by employee ID
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(empid__icontains=search_query)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Enhance bills with employee information and excess calculation
        bill_list = []
        for bill in context['bills']:
            try:
                employee = TblhrOfficestaff.objects.get(empid=bill.empid)

                # Get mobile limit
                mobile_limit = 0
                excess_amount = 0
                if employee.mobileno:
                    mobile_limit = LoanService.get_employee_mobile_limit(employee.mobileno)
                    excess_amount = LoanService.calculate_mobile_excess(
                        bill.billamt or 0,
                        mobile_limit
                    )

                bill_list.append({
                    'bill': bill,
                    'employee': employee,
                    'mobile_limit': mobile_limit,
                    'excess_amount': excess_amount
                })
            except TblhrOfficestaff.DoesNotExist:
                bill_list.append({
                    'bill': bill,
                    'employee': None,
                    'mobile_limit': 0,
                    'excess_amount': 0
                })

        context['bill_list'] = bill_list

        # Add month filter options
        from ..services.salary_service import SalaryService
        months = [
            {'id': i, 'name': SalaryService.get_month_name(i)}
            for i in range(1, 13)
        ]
        context['months'] = months
        context['selected_month'] = self.request.GET.get('month', '')

        return context


class MobileBillCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new mobile bill record.
    Converted from: aspnet/Module/HR/Transactions/MobileBill.aspx (Create Mode)
    """
    model = TblhrMobilebill
    form_class = MobileBillForm
    template_name = 'human_resource/transactions/mobile_bill_form.html'
    partial_template_name = 'human_resource/partials/mobile_bill_form.html'
    success_message = 'Mobile bill created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get list of employees with corporate mobile numbers
        employees = TblhrOfficestaff.objects.filter(
            compid=self.get_compid(),
            mobileno__isnull=False
        ).exclude(mobileno='').order_by('employeename')
        context['employees'] = employees

        # Get corporate mobile numbers with limits
        corporate_mobiles = TblhrCoporatemobileno.objects.all()
        context['corporate_mobiles'] = corporate_mobiles

        return context

    def form_valid(self, form):
        # Set company and financial year from session
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.sessionid = str(self.request.user.id)

        # Set system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse_lazy('human_resource:mobile-bill-detail', kwargs={'pk': self.object.pk})


class MobileBillUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing mobile bill record.
    Converted from: aspnet/Module/HR/Transactions/MobileBill.aspx (Edit Mode)
    """
    model = TblhrMobilebill
    form_class = MobileBillForm
    template_name = 'human_resource/transactions/mobile_bill_form.html'
    partial_template_name = 'human_resource/partials/mobile_bill_form.html'
    success_message = 'Mobile bill updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee

            # Calculate excess
            if employee.mobileno:
                mobile_limit = LoanService.get_employee_mobile_limit(employee.mobileno)
                excess_amount = LoanService.calculate_mobile_excess(
                    self.object.billamt or 0,
                    mobile_limit
                )
                context['mobile_limit'] = mobile_limit
                context['excess_amount'] = excess_amount
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        return context

    def form_valid(self, form):
        # Update system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('human_resource:mobile-bill-detail', kwargs={'pk': self.object.pk})


class MobileBillDetailView(BaseDetailViewMixin, DetailView):
    """
    Display detailed mobile bill information.
    Converted from: aspnet/Module/HR/Transactions/MobileBill.aspx (View Mode)
    """
    model = TblhrMobilebill
    template_name = 'human_resource/transactions/mobile_bill_detail.html'
    context_object_name = 'bill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee

            # Calculate excess amount
            if employee.mobileno:
                mobile_limit = LoanService.get_employee_mobile_limit(employee.mobileno)
                excess_amount = LoanService.calculate_mobile_excess(
                    self.object.billamt or 0,
                    mobile_limit
                )
                context['mobile_limit'] = mobile_limit
                context['excess_amount'] = excess_amount
                context['will_deduct'] = excess_amount > 0
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Get month name
        from ..services.salary_service import SalaryService
        context['month_name'] = SalaryService.get_month_name(self.object.billmonth)

        return context


class MobileBillDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete mobile bill record.
    Converted from: aspnet/Module/HR/Transactions/MobileBill.aspx (Delete)
    """
    model = TblhrMobilebill
    success_url = reverse_lazy('human_resource:mobile-bill-list')
    template_name = 'human_resource/transactions/mobile_bill_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Mobile bill record for {self.object.empid} deleted successfully.')
        return super().delete(request, *args, **kwargs)
