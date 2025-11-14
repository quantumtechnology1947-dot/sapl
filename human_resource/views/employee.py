"""
Human Resource Employee Views
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models
from datetime import datetime

from ..models import (
    TblhrOfficestaff, TblhrDepartments, TblhrDesignation, TblhrGrade,
    Businessgroup, TblhrSwapcard, TblhrSalaryMaster, TblhrSalaryDetails,
    TblhrBankloan, TblhrMobilebill, TblhrOfferMaster, TblhrOfferAccessories,
    TblgatePass, TblaccTourintimationMaster, TblgatepassReason
)
from ..forms import (
    EmployeeForm, SalaryForm, BankLoanForm, MobileBillForm,
    OfferLetterForm, GatePassForm, TourIntimationForm
)

# EMPLOYEE (OFFICE STAFF) TRANSACTIONS
# ============================================================================

class EmployeeListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of employees with search and filter.
    Converted from: aspnet/Module/HR/Transactions/OfficeStaff.aspx
    Filters by company and financial year from session.
    """
    model = TblhrOfficestaff
    template_name = 'human_resource/transactions/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        # Filter by company and financial year from session
        company_id = self.request.session.get('company_id')
        fy_id = self.request.session.get('financial_year_id')

        queryset = super().get_queryset()
        if company_id:
            queryset = queryset.filter(compid=company_id)
        if fy_id:
            queryset = queryset.filter(finyearid=fy_id)

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(employeename__icontains=search_query) |
                models.Q(empid__icontains=search_query) |
                models.Q(mobileno__icontains=search_query) |
                models.Q(companyemail__icontains=search_query)
            )

        # Filter by department
        department_filter = self.request.GET.get('department', '')
        if department_filter:
            queryset = queryset.filter(department=department_filter)

        return queryset.order_by('-userid')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = TblhrDepartments.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['department_filter'] = self.request.GET.get('department', '')
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """
    Display employee details with tabbed layout.
    Converted from: aspnet/Module/HR/Transactions/OfficeStaff.aspx (View Mode)
    """
    model = TblhrOfficestaff
    template_name = 'human_resource/transactions/employee_detail.html'
    context_object_name = 'employee'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get department, designation, grade names
        if self.object.department:
            context['department_name'] = TblhrDepartments.objects.filter(id=self.object.department).first()
        if self.object.designation:
            context['designation_name'] = TblhrDesignation.objects.filter(id=self.object.designation).first()
        if self.object.grade:
            context['grade_name'] = TblhrGrade.objects.filter(id=self.object.grade).first()
        if self.object.bggroup:
            context['bggroup_name'] = Businessgroup.objects.filter(id=self.object.bggroup).first()
        if self.object.swapcardno:
            context['swapcard_name'] = TblhrSwapcard.objects.filter(id=self.object.swapcardno).first()
        return context


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    """
    Create new employee with multi-tab form and file uploads.
    Converted from: aspnet/Module/HR/Transactions/OfficeStaff.aspx (Create Mode)
    """
    model = TblhrOfficestaff
    form_class = EmployeeForm
    template_name = 'human_resource/transactions/employee_form.html'
    
    def get_success_url(self):
        return reverse_lazy('human_resource:employee-detail', kwargs={'pk': self.object.userid})

    def form_valid(self, form):
        from datetime import datetime
        
        # Set company and financial year from session
        form.instance.compid = self.request.session.get('company_id')
        form.instance.finyearid = self.request.session.get('financial_year_id')
        form.instance.sessionid = str(self.request.user)

        # Set system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        # Generate employee ID if not provided
        if not form.instance.empid:
            # Get the last employee ID
            last_employee = TblhrOfficestaff.objects.filter(
                compid=form.instance.compid
            ).order_by('-userid').first()
            
            if last_employee and last_employee.empid:
                try:
                    last_num = int(last_employee.empid.replace('EMP', ''))
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            
            form.instance.empid = f'EMP{new_num:04d}'

        # Handle photo upload
        photo = form.cleaned_data.get('photodata')
        if photo:
            form.instance.photofilename = photo.name
            form.instance.photosize = str(photo.size)
            form.instance.photocontenttype = photo.content_type
            form.instance.photodata = photo.read()

        # Handle CV upload
        cv = form.cleaned_data.get('cvdata')
        if cv:
            form.instance.cvfilename = cv.name
            form.instance.cvsize = str(cv.size)
            form.instance.cvcontenttype = cv.content_type
            form.instance.cvdata = cv.read()

        response = super().form_valid(form)
        messages.success(self.request, f'Employee {form.instance.employeename} created successfully with ID: {form.instance.empid}')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing employee.
    Converted from: aspnet/Module/HR/Transactions/OfficeStaff.aspx (Edit Mode)
    """
    model = TblhrOfficestaff
    form_class = EmployeeForm
    template_name = 'human_resource/transactions/employee_form.html'
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        return reverse_lazy('human_resource:employee-detail', kwargs={'pk': self.object.userid})

    def form_valid(self, form):
        from datetime import datetime
        
        # Update system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        # Handle photo upload (only if new file is uploaded)
        photo = form.cleaned_data.get('photodata')
        if photo and hasattr(photo, 'read'):
            form.instance.photofilename = photo.name
            form.instance.photosize = str(photo.size)
            form.instance.photocontenttype = photo.content_type
            form.instance.photodata = photo.read()

        # Handle CV upload (only if new file is uploaded)
        cv = form.cleaned_data.get('cvdata')
        if cv and hasattr(cv, 'read'):
            form.instance.cvfilename = cv.name
            form.instance.cvsize = str(cv.size)
            form.instance.cvcontenttype = cv.content_type
            form.instance.cvdata = cv.read()

        response = super().form_valid(form)
        messages.success(self.request, f'Employee {form.instance.employeename} updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete employee (soft delete by marking inactive).
    Converted from: aspnet/Module/HR/Transactions/OfficeStaff.aspx (Delete Mode)
    """
    model = TblhrOfficestaff
    success_url = reverse_lazy('human_resource:employee-list')
    pk_url_kwarg = 'pk'
    template_name = 'human_resource/transactions/employee_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Employee {self.object.employeename} (ID: {self.object.empid}) deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
