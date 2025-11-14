"""
Human Resource Salary Management Views
Handles salary calculation, generation, and bank statement export
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db import models
from datetime import datetime
import csv

from core.mixins import (
    BaseListViewMixin, BaseCreateViewMixin, BaseUpdateViewMixin,
    BaseDeleteViewMixin, BaseDetailViewMixin
)
from ..models import (
    TblhrOfficestaff, TblhrSalaryMaster, TblhrSalaryDetails,
    TblhrOfferMaster, TblhrOfferAccessories, TblhrWorkingdays
)
from ..forms import SalaryForm
from ..services.salary_service import SalaryService


class SalaryEmployeeListView(BaseListViewMixin, ListView):
    """
    Display list of employees with salary generation option.
    Converted from: aspnet/Module/HR/Transactions/SalaryMaster.aspx
    Shows employees eligible for salary generation for selected month.
    """
    model = TblhrOfficestaff
    template_name = 'human_resource/transactions/salary_employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    search_fields = ['employeename', 'empid', 'department', 'designation']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Only show active employees with offer letters
        queryset = queryset.filter(
            offerid__isnull=False
        ).exclude(
            models.Q(employeename__isnull=True) | models.Q(employeename='')
        )

        # Filter by department if specified
        department_filter = self.request.GET.get('department', '')
        if department_filter:
            queryset = queryset.filter(department=department_filter)

        return queryset.order_by('employeename')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add month selection for salary generation
        months = [
            {'id': i, 'name': SalaryService.get_month_name(i)}
            for i in range(1, 13)
        ]
        context['months'] = months
        context['selected_month'] = self.request.GET.get('month', datetime.now().month)

        return context


class SalaryCreateView(BaseCreateViewMixin, CreateView):
    """
    Generate salary for an employee for a specific month.
    Converted from: aspnet/Module/HR/Transactions/SalaryMaster.aspx (Generate Button)
    Calculates salary components, deductions, and creates salary master and details.
    """
    model = TblhrSalaryMaster
    form_class = SalaryForm
    template_name = 'human_resource/transactions/salary_form.html'
    partial_template_name = 'human_resource/partials/salary_form.html'
    success_message = 'Salary generated successfully'

    def dispatch(self, request, *args, **kwargs):
        """Get employee and month from URL parameters"""
        self.empid = kwargs.get('empid')
        self.month = kwargs.get('month')

        # Validate employee exists
        try:
            self.employee = TblhrOfficestaff.objects.get(empid=self.empid)
        except TblhrOfficestaff.DoesNotExist:
            messages.error(request, f'Employee {self.empid} not found')
            return redirect('human_resource:salary-employee-list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        context['month'] = self.month
        context['month_name'] = SalaryService.get_month_name(int(self.month))

        # Calculate salary components
        salary_components = SalaryService.calculate_salary_components(self.employee)
        context.update(salary_components)

        # Get working days
        working_days = SalaryService.get_working_days(
            self.get_compid(),
            self.get_finyearid(),
            self.month
        )
        context['working_days'] = working_days

        return context

    def form_valid(self, form):
        # Set company and financial year from session
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.sessionid = str(self.request.user.id)

        # Set employee and month
        form.instance.empid = self.empid
        form.instance.fmonth = self.month

        # Set system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        # Save salary master
        response = super().form_valid(form)

        # Create salary details record
        salary_components = SalaryService.calculate_salary_components(self.employee)

        salary_detail = TblhrSalaryDetails.objects.create(
            mid=self.object,
            gross=salary_components['gross_total'],
            ctc=salary_components['ctc_total'],
            net=salary_components['net_total'],
            workingdays=SalaryService.get_working_days(
                self.get_compid(),
                self.get_finyearid(),
                self.month
            ),
            presentdays=form.cleaned_data.get('presentdays', 0),
            installment=SalaryService.get_bank_installment(
                self.empid,
                self.get_compid(),
                self.get_finyearid()
            ),
            mobileexeamt=SalaryService.get_mobile_excess(
                self.empid,
                self.employee.mobileno,
                self.month,
                self.get_compid(),
                self.get_finyearid()
            )
        )

        return response

    def get_success_url(self):
        return reverse_lazy('human_resource:salary-detail', kwargs={'pk': self.object.pk})


class SalaryListView(BaseListViewMixin, ListView):
    """
    Display list of generated salaries with filters.
    Converted from: aspnet/Module/HR/Transactions/SalaryMaster.aspx (List View)
    """
    model = TblhrSalaryMaster
    template_name = 'human_resource/transactions/salary_list.html'
    context_object_name = 'salaries'
    paginate_by = 20
    partial_template_name = 'human_resource/partials/salary_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by month if specified
        month_filter = self.request.GET.get('month', '')
        if month_filter:
            queryset = queryset.filter(fmonth=month_filter)

        # Search by employee ID or name
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(empid__icontains=search_query)
            )

        return queryset.select_related().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add month filter options
        months = [
            {'id': i, 'name': SalaryService.get_month_name(i)}
            for i in range(1, 13)
        ]
        context['months'] = months
        context['selected_month'] = self.request.GET.get('month', '')

        # Add employee names
        salary_list = []
        for salary in context['salaries']:
            try:
                employee = TblhrOfficestaff.objects.get(empid=salary.empid)
                salary_list.append({
                    'salary': salary,
                    'employee': employee
                })
            except TblhrOfficestaff.DoesNotExist:
                salary_list.append({
                    'salary': salary,
                    'employee': None
                })

        context['salary_list'] = salary_list

        return context


class SalaryDetailView(BaseDetailViewMixin, DetailView):
    """
    Display detailed salary information for an employee.
    Converted from: aspnet/Module/HR/Transactions/SalaryMaster.aspx (View Mode)
    Shows salary components, deductions, and net pay.
    """
    model = TblhrSalaryMaster
    template_name = 'human_resource/transactions/salary_detail.html'
    context_object_name = 'salary'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Get salary details
        try:
            salary_detail = TblhrSalaryDetails.objects.get(mid=self.object)
            context['salary_detail'] = salary_detail

            # Calculate net salary
            if context['employee']:
                salary_components = SalaryService.calculate_salary_components(context['employee'])
                net_calc = SalaryService.calculate_net_salary(
                    salary_components['net_total'],
                    salary_detail
                )
                context.update(net_calc)
                context.update(salary_components)
        except TblhrSalaryDetails.DoesNotExist:
            context['salary_detail'] = None

        # Month name
        context['month_name'] = SalaryService.get_month_name(self.object.fmonth)

        return context


class SalaryUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing salary record.
    Converted from: aspnet/Module/HR/Transactions/SalaryMaster.aspx (Edit Mode)
    """
    model = TblhrSalaryMaster
    form_class = SalaryForm
    template_name = 'human_resource/transactions/salary_form.html'
    partial_template_name = 'human_resource/partials/salary_form.html'
    success_message = 'Salary updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee

            # Calculate salary components
            salary_components = SalaryService.calculate_salary_components(employee)
            context.update(salary_components)
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Get salary details
        try:
            salary_detail = TblhrSalaryDetails.objects.get(mid=self.object)
            context['salary_detail'] = salary_detail
        except TblhrSalaryDetails.DoesNotExist:
            context['salary_detail'] = None

        context['month_name'] = SalaryService.get_month_name(self.object.fmonth)

        return context

    def form_valid(self, form):
        # Update system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('human_resource:salary-detail', kwargs={'pk': self.object.pk})


class SalaryDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete salary record.
    Converted from: aspnet/Module/HR/Transactions/SalaryMaster.aspx (Delete)
    """
    model = TblhrSalaryMaster
    success_url = reverse_lazy('human_resource:salary-list')
    template_name = 'human_resource/transactions/salary_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Delete related salary details first
        try:
            salary_detail = TblhrSalaryDetails.objects.get(mid=self.object)
            salary_detail.delete()
        except TblhrSalaryDetails.DoesNotExist:
            pass

        messages.success(request, f'Salary record for {self.object.empid} deleted successfully.')
        return super().delete(request, *args, **kwargs)


class SalaryBankStatementView(BaseListViewMixin, ListView):
    """
    Display bank statement view for salary transfers.
    Converted from: aspnet/Module/HR/Transactions/BankStatement.aspx
    Shows employee salary transfer details in bank format.
    """
    model = TblhrSalaryMaster
    template_name = 'human_resource/transactions/salary_bank_statement.html'
    context_object_name = 'salary_transfers'
    paginate_by = 50

    def get_queryset(self):
        """Return empty queryset - data handled in get_context_data"""
        return TblhrSalaryMaster.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get month from request
        month = self.request.GET.get('month', datetime.now().month)

        # Generate bank statement data
        employee_list = SalaryService.generate_bank_statement_data(
            month,
            self.get_compid(),
            self.get_finyearid()
        )

        context['employee_list'] = employee_list
        context['month'] = month
        context['month_name'] = SalaryService.get_month_name(int(month))

        # Add month filter options
        months = [
            {'id': i, 'name': SalaryService.get_month_name(i)}
            for i in range(1, 13)
        ]
        context['months'] = months

        # Calculate totals
        total_amount = sum(emp['net_pay'] for emp in employee_list)
        context['total_amount'] = total_amount
        context['total_employees'] = len(employee_list)

        return context


class SalaryBankStatementExportView(BaseListViewMixin, ListView):
    """
    Export bank statement to CSV format.
    Converted from: aspnet/Module/HR/Transactions/BankStatement.aspx (Export Button)
    Generates CSV file for bank upload.
    """
    model = TblhrSalaryMaster

    def get(self, request, *args, **kwargs):
        # Get month from request
        month = request.GET.get('month', datetime.now().month)

        # Generate bank statement data
        employee_list = SalaryService.generate_bank_statement_data(
            month,
            self.get_compid(),
            self.get_finyearid()
        )

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bank_statement_{month}_{datetime.now().strftime("%Y%m%d")}.csv"'

        writer = csv.writer(response)

        # Write header
        writer.writerow([
            'Employee ID',
            'Employee Name',
            'Bank Account',
            'IFSC Code',
            'Net Pay',
            'Month',
            'Year'
        ])

        # Write data rows
        for emp_data in employee_list:
            employee = emp_data['employee']
            writer.writerow([
                employee.empid,
                employee.employeename,
                employee.bankaccno or '',
                employee.bankifsccode or '',
                f"{emp_data['net_pay']:.2f}",
                SalaryService.get_month_name(int(month)),
                datetime.now().year
            ])

        return response
