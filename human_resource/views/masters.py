"""
Human Resource Master Views
All master entities with CRUD operations (55 views total):
- Business Group (5 views)
- Department (5 views)
- Designation (5 views)
- Grade (5 views)
- Holiday Master (5 views)
- Working Days (5 views)
- Corporate Mobile No (5 views)
- Gate Pass Reason (5 views)
- Intercom Extension (5 views)
- PF Slab (5 views)
- Swap Card (5 views)
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime

from ..models import (
    Businessgroup, TblhrDepartments, TblhrDesignation, TblhrGrade,
    TblhrHolidayMaster, TblhrWorkingdays, TblhrCoporatemobileno,
    TblgatepassReason, TblhrIntercomext, TblhrPfSlab, TblhrSwapcard
)
from ..forms import (
    BusinessGroupForm, DepartmentForm, DesignationForm, GradeForm,
    HolidayMasterForm, WorkingDaysForm, CorporateMobileNoForm,
    GatePassReasonForm, IntercomExtForm, PFSlabForm, SwapCardForm
)


# ============================================================================
# BUSINESS GROUP MASTER
# ============================================================================

class BusinessGroupListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of business groups with inline editing.
    Converted from: aspnet/Module/HR/Masters/BusinessGroup.aspx
    """
    model = Businessgroup
    template_name = 'human_resource/business_group_list.html'
    context_object_name = 'business_groups'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/business_group_list_partial.html']
        return ['human_resource/business_group_list.html']


class BusinessGroupCreateView(LoginRequiredMixin, CreateView):
    """
    Create new business group.
    Converted from: aspnet/Module/HR/Masters/BusinessGroup.aspx (Footer Insert)
    """
    model = Businessgroup
    form_class = BusinessGroupForm
    template_name = 'human_resource/partials/business_group_form.html'
    success_url = reverse_lazy('human_resource:business-group-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/business_group_row.html'
            return render(self.request, self.template_name, {'business_group': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/business_group_form.html', {'form': form})
        return super().form_invalid(form)


class BusinessGroupUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing business group (inline editing).
    Converted from: aspnet/Module/HR/Masters/BusinessGroup.aspx (Edit Button)
    """
    model = Businessgroup
    form_class = BusinessGroupForm
    template_name = 'human_resource/partials/business_group_edit_row.html'
    success_url = reverse_lazy('human_resource:business-group-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'business_group': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/business_group_row.html', {'business_group': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'business_group': self.object})
        return super().form_invalid(form)


class BusinessGroupDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete business group.
    Converted from: aspnet/Module/HR/Masters/BusinessGroup.aspx (Delete Button)
    """
    model = Businessgroup
    success_url = reverse_lazy('human_resource:business-group-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class BusinessGroupRowView(LoginRequiredMixin, DetailView):
    """
    Return single business group row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = Businessgroup
    template_name = 'human_resource/partials/business_group_row.html'
    context_object_name = 'business_group'
    pk_url_kwarg = 'id'


# ============================================================================
# DEPARTMENT MASTER
# ============================================================================

class DepartmentListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of departments with inline editing.
    Converted from: aspnet/Module/HR/Masters/Department.aspx
    """
    model = TblhrDepartments
    template_name = 'human_resource/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/department_list_partial.html']
        return ['human_resource/department_list.html']


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    """
    Create new department.
    Converted from: aspnet/Module/HR/Masters/Department.aspx (Footer Insert)
    """
    model = TblhrDepartments
    form_class = DepartmentForm
    template_name = 'human_resource/partials/department_form.html'
    success_url = reverse_lazy('human_resource:department-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/department_row.html'
            return render(self.request, self.template_name, {'department': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/department_form.html', {'form': form})
        return super().form_invalid(form)


class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing department (inline editing).
    Converted from: aspnet/Module/HR/Masters/Department.aspx (Edit Button)
    """
    model = TblhrDepartments
    form_class = DepartmentForm
    template_name = 'human_resource/partials/department_edit_row.html'
    success_url = reverse_lazy('human_resource:department-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'department': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/department_row.html', {'department': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'department': self.object})
        return super().form_invalid(form)


class DepartmentDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete department.
    Converted from: aspnet/Module/HR/Masters/Department.aspx (Delete Button)
    """
    model = TblhrDepartments
    success_url = reverse_lazy('human_resource:department-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class DepartmentRowView(LoginRequiredMixin, DetailView):
    """
    Return single department row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrDepartments
    template_name = 'human_resource/partials/department_row.html'
    context_object_name = 'department'
    pk_url_kwarg = 'id'


# ============================================================================
# DESIGNATION MASTER
# ============================================================================

class DesignationListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of designations with inline editing.
    Converted from: aspnet/Module/HR/Masters/Designation.aspx
    """
    model = TblhrDesignation
    template_name = 'human_resource/designation_list.html'
    context_object_name = 'designations'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/designation_list_partial.html']
        return ['human_resource/designation_list.html']


class DesignationCreateView(LoginRequiredMixin, CreateView):
    """
    Create new designation.
    Converted from: aspnet/Module/HR/Masters/Designation.aspx (Footer Insert)
    """
    model = TblhrDesignation
    form_class = DesignationForm
    template_name = 'human_resource/partials/designation_form.html'
    success_url = reverse_lazy('human_resource:designation-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/designation_row.html'
            return render(self.request, self.template_name, {'designation': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/designation_form.html', {'form': form})
        return super().form_invalid(form)


class DesignationUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing designation (inline editing).
    Converted from: aspnet/Module/HR/Masters/Designation.aspx (Edit Button)
    """
    model = TblhrDesignation
    form_class = DesignationForm
    template_name = 'human_resource/partials/designation_edit_row.html'
    success_url = reverse_lazy('human_resource:designation-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'designation': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/designation_row.html', {'designation': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'designation': self.object})
        return super().form_invalid(form)


class DesignationDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete designation.
    Converted from: aspnet/Module/HR/Masters/Designation.aspx (Delete Button)
    """
    model = TblhrDesignation
    success_url = reverse_lazy('human_resource:designation-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class DesignationRowView(LoginRequiredMixin, DetailView):
    """
    Return single designation row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrDesignation
    template_name = 'human_resource/partials/designation_row.html'
    context_object_name = 'designation'
    pk_url_kwarg = 'id'


# ============================================================================
# GRADE MASTER
# ============================================================================

class GradeListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of grades with inline editing.
    Converted from: aspnet/Module/HR/Masters/Grade.aspx
    """
    model = TblhrGrade
    template_name = 'human_resource/grade_list.html'
    context_object_name = 'grades'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/grade_list_partial.html']
        return ['human_resource/grade_list.html']


class GradeCreateView(LoginRequiredMixin, CreateView):
    """
    Create new grade.
    Converted from: aspnet/Module/HR/Masters/Grade.aspx (Footer Insert)
    """
    model = TblhrGrade
    form_class = GradeForm
    template_name = 'human_resource/partials/grade_form.html'
    success_url = reverse_lazy('human_resource:grade-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/grade_row.html'
            return render(self.request, self.template_name, {'grade': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/grade_form.html', {'form': form})
        return super().form_invalid(form)


class GradeUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing grade (inline editing).
    Converted from: aspnet/Module/HR/Masters/Grade.aspx (Edit Button)
    """
    model = TblhrGrade
    form_class = GradeForm
    template_name = 'human_resource/partials/grade_edit_row.html'
    success_url = reverse_lazy('human_resource:grade-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'grade': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/grade_row.html', {'grade': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'grade': self.object})
        return super().form_invalid(form)


class GradeDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete grade.
    Converted from: aspnet/Module/HR/Masters/Grade.aspx (Delete Button)
    """
    model = TblhrGrade
    success_url = reverse_lazy('human_resource:grade-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class GradeRowView(LoginRequiredMixin, DetailView):
    """
    Return single grade row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrGrade
    template_name = 'human_resource/partials/grade_row.html'
    context_object_name = 'grade'
    pk_url_kwarg = 'id'


# ============================================================================
# HOLIDAY MASTER
# ============================================================================

class HolidayMasterListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of holidays with inline editing.
    Converted from: aspnet/Module/HR/Masters/HolidayMaster.aspx
    Filters by company and financial year from session.
    """
    model = TblhrHolidayMaster
    template_name = 'human_resource/holiday_master_list.html'
    context_object_name = 'holidays'
    paginate_by = 17

    def get_queryset(self):
        # Filter by company and financial year from session
        company_id = self.request.session.get('company_id')
        fy_id = self.request.session.get('financial_year_id')

        queryset = super().get_queryset()
        if company_id:
            queryset = queryset.filter(compid=company_id)
        if fy_id:
            queryset = queryset.filter(finyearid=fy_id)

        return queryset.order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/holiday_master_list_partial.html']
        return ['human_resource/holiday_master_list.html']


class HolidayMasterCreateView(LoginRequiredMixin, CreateView):
    """
    Create new holiday.
    Converted from: aspnet/Module/HR/Masters/HolidayMaster.aspx (Footer Insert)
    """
    model = TblhrHolidayMaster
    form_class = HolidayMasterForm
    template_name = 'human_resource/partials/holiday_master_form.html'
    success_url = reverse_lazy('human_resource:holiday-master-list')

    def form_valid(self, form):
        # Set company and financial year from session
        form.instance.compid = self.request.session.get('company_id')
        form.instance.finyearid = self.request.session.get('financial_year_id')
        form.instance.sessionid = str(self.request.user)

        # Set system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/holiday_master_row.html'
            return render(self.request, self.template_name, {'holiday': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/holiday_master_form.html', {'form': form})
        return super().form_invalid(form)


class HolidayMasterUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing holiday (inline editing).
    Converted from: aspnet/Module/HR/Masters/HolidayMaster.aspx (Edit Button)
    """
    model = TblhrHolidayMaster
    form_class = HolidayMasterForm
    template_name = 'human_resource/partials/holiday_master_edit_row.html'
    success_url = reverse_lazy('human_resource:holiday-master-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'holiday': self.object})

    def form_valid(self, form):
        # Update system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/holiday_master_row.html', {'holiday': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'holiday': self.object})
        return super().form_invalid(form)


class HolidayMasterDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete holiday.
    Converted from: aspnet/Module/HR/Masters/HolidayMaster.aspx (Delete Button)
    """
    model = TblhrHolidayMaster
    success_url = reverse_lazy('human_resource:holiday-master-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class HolidayMasterRowView(LoginRequiredMixin, DetailView):
    """
    Return single holiday row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrHolidayMaster
    template_name = 'human_resource/partials/holiday_master_row.html'
    context_object_name = 'holiday'
    pk_url_kwarg = 'id'


# ============================================================================
# WORKING DAYS MASTER
# ============================================================================

class WorkingDaysListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of working days with inline editing.
    Converted from: aspnet/Module/HR/Masters/WorkingDays.aspx
    Filters by company and financial year from session.
    """
    model = TblhrWorkingdays
    template_name = 'human_resource/working_days_list.html'
    context_object_name = 'working_days'
    paginate_by = 17

    def get_queryset(self):
        # Filter by company and financial year from session
        company_id = self.request.session.get('company_id')
        fy_id = self.request.session.get('financial_year_id')

        queryset = super().get_queryset()
        if company_id:
            queryset = queryset.filter(compid=company_id)
        if fy_id:
            queryset = queryset.filter(finyearid=fy_id)

        return queryset.order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/working_days_list_partial.html']
        return ['human_resource/working_days_list.html']


class WorkingDaysCreateView(LoginRequiredMixin, CreateView):
    """
    Create new working days entry.
    Converted from: aspnet/Module/HR/Masters/WorkingDays.aspx (Footer Insert)
    """
    model = TblhrWorkingdays
    form_class = WorkingDaysForm
    template_name = 'human_resource/partials/working_days_form.html'
    success_url = reverse_lazy('human_resource:working-days-list')

    def form_valid(self, form):
        # Set company and financial year from session
        form.instance.compid = self.request.session.get('company_id')
        form.instance.finyearid = self.request.session.get('financial_year_id')

        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/working_days_row.html'
            return render(self.request, self.template_name, {'working_day': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/working_days_form.html', {'form': form})
        return super().form_invalid(form)


class WorkingDaysUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing working days entry (inline editing).
    Converted from: aspnet/Module/HR/Masters/WorkingDays.aspx (Edit Button)
    """
    model = TblhrWorkingdays
    form_class = WorkingDaysForm
    template_name = 'human_resource/partials/working_days_edit_row.html'
    success_url = reverse_lazy('human_resource:working-days-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'working_day': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/working_days_row.html', {'working_day': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'working_day': self.object})
        return super().form_invalid(form)


class WorkingDaysDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete working days entry.
    Converted from: aspnet/Module/HR/Masters/WorkingDays.aspx (Delete Button)
    """
    model = TblhrWorkingdays
    success_url = reverse_lazy('human_resource:working-days-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class WorkingDaysRowView(LoginRequiredMixin, DetailView):
    """
    Return single working days row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrWorkingdays
    template_name = 'human_resource/partials/working_days_row.html'
    context_object_name = 'working_day'
    pk_url_kwarg = 'id'


# ============================================================================
# CORPORATE MOBILE NO MASTER
# ============================================================================

class CorporateMobileNoListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of corporate mobile numbers.
    Converted from: aspnet/Module/HR/Masters/CorporateMobileNo.aspx
    """
    model = TblhrCoporatemobileno
    template_name = 'human_resource/corporate_mobile_list.html'
    context_object_name = 'mobile_numbers'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/corporate_mobile_list_partial.html']
        return ['human_resource/corporate_mobile_list.html']


class CorporateMobileNoCreateView(LoginRequiredMixin, CreateView):
    """
    Create new corporate mobile number.
    Converted from: aspnet/Module/HR/Masters/CorporateMobileNo.aspx (Footer Insert)
    """
    model = TblhrCoporatemobileno
    form_class = CorporateMobileNoForm
    template_name = 'human_resource/partials/corporate_mobile_form.html'
    success_url = reverse_lazy('human_resource:corporate-mobile-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/corporate_mobile_row.html'
            return render(self.request, self.template_name, {'mobile': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/corporate_mobile_form.html', {'form': form})
        return super().form_invalid(form)


class CorporateMobileNoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing corporate mobile number (inline editing).
    Converted from: aspnet/Module/HR/Masters/CorporateMobileNo.aspx (Edit Button)
    """
    model = TblhrCoporatemobileno
    form_class = CorporateMobileNoForm
    template_name = 'human_resource/partials/corporate_mobile_edit_row.html'
    success_url = reverse_lazy('human_resource:corporate-mobile-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'mobile': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/corporate_mobile_row.html', {'mobile': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'mobile': self.object})
        return super().form_invalid(form)


class CorporateMobileNoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete corporate mobile number.
    Converted from: aspnet/Module/HR/Masters/CorporateMobileNo.aspx (Delete Button)
    """
    model = TblhrCoporatemobileno
    success_url = reverse_lazy('human_resource:corporate-mobile-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class CorporateMobileNoRowView(LoginRequiredMixin, DetailView):
    """
    Return single corporate mobile number row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrCoporatemobileno
    template_name = 'human_resource/partials/corporate_mobile_row.html'
    context_object_name = 'mobile'
    pk_url_kwarg = 'id'


# ============================================================================
# GATE PASS REASON MASTER
# ============================================================================

class GatePassReasonListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of gate pass reasons.
    Converted from: aspnet/Module/HR/Masters/GatePassReason.aspx
    """
    model = TblgatepassReason
    template_name = 'human_resource/gatepass_reason_list.html'
    context_object_name = 'reasons'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/gatepass_reason_list_partial.html']
        return ['human_resource/gatepass_reason_list.html']


class GatePassReasonCreateView(LoginRequiredMixin, CreateView):
    """
    Create new gate pass reason.
    Converted from: aspnet/Module/HR/Masters/GatePassReason.aspx (Footer Insert)
    """
    model = TblgatepassReason
    form_class = GatePassReasonForm
    template_name = 'human_resource/partials/gatepass_reason_form.html'
    success_url = reverse_lazy('human_resource:gatepass-reason-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/gatepass_reason_row.html'
            return render(self.request, self.template_name, {'reason': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/gatepass_reason_form.html', {'form': form})
        return super().form_invalid(form)


class GatePassReasonUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing gate pass reason (inline editing).
    Converted from: aspnet/Module/HR/Masters/GatePassReason.aspx (Edit Button)
    """
    model = TblgatepassReason
    form_class = GatePassReasonForm
    template_name = 'human_resource/partials/gatepass_reason_edit_row.html'
    success_url = reverse_lazy('human_resource:gatepass-reason-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'reason': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/gatepass_reason_row.html', {'reason': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'reason': self.object})
        return super().form_invalid(form)


class GatePassReasonDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete gate pass reason.
    Converted from: aspnet/Module/HR/Masters/GatePassReason.aspx (Delete Button)
    """
    model = TblgatepassReason
    success_url = reverse_lazy('human_resource:gatepass-reason-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class GatePassReasonRowView(LoginRequiredMixin, DetailView):
    """
    Return single gate pass reason row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblgatepassReason
    template_name = 'human_resource/partials/gatepass_reason_row.html'
    context_object_name = 'reason'
    pk_url_kwarg = 'id'


# ============================================================================
# INTERCOM EXT MASTER
# ============================================================================

class IntercomExtListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of intercom extensions.
    Converted from: aspnet/Module/HR/Masters/IntercomExtNo.aspx
    """
    model = TblhrIntercomext
    template_name = 'human_resource/intercom_ext_list.html'
    context_object_name = 'extensions'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/intercom_ext_list_partial.html']
        return ['human_resource/intercom_ext_list.html']


class IntercomExtCreateView(LoginRequiredMixin, CreateView):
    """
    Create new intercom extension.
    Converted from: aspnet/Module/HR/Masters/IntercomExtNo.aspx (Footer Insert)
    """
    model = TblhrIntercomext
    form_class = IntercomExtForm
    template_name = 'human_resource/partials/intercom_ext_form.html'
    success_url = reverse_lazy('human_resource:intercom-ext-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/intercom_ext_row.html'
            return render(self.request, self.template_name, {'extension': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/intercom_ext_form.html', {'form': form})
        return super().form_invalid(form)


class IntercomExtUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing intercom extension (inline editing).
    Converted from: aspnet/Module/HR/Masters/IntercomExtNo.aspx (Edit Button)
    """
    model = TblhrIntercomext
    form_class = IntercomExtForm
    template_name = 'human_resource/partials/intercom_ext_edit_row.html'
    success_url = reverse_lazy('human_resource:intercom-ext-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'extension': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/intercom_ext_row.html', {'extension': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'extension': self.object})
        return super().form_invalid(form)


class IntercomExtDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete intercom extension.
    Converted from: aspnet/Module/HR/Masters/IntercomExtNo.aspx (Delete Button)
    """
    model = TblhrIntercomext
    success_url = reverse_lazy('human_resource:intercom-ext-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class IntercomExtRowView(LoginRequiredMixin, DetailView):
    """
    Return single intercom extension row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrIntercomext
    template_name = 'human_resource/partials/intercom_ext_row.html'
    context_object_name = 'extension'
    pk_url_kwarg = 'id'


# ============================================================================
# PF SLAB MASTER
# ============================================================================

class PFSlabListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of PF slabs.
    Converted from: aspnet/Module/HR/Masters/PF_Slab.aspx
    """
    model = TblhrPfSlab
    template_name = 'human_resource/pf_slab_list.html'
    context_object_name = 'pf_slabs'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/pf_slab_list_partial.html']
        return ['human_resource/pf_slab_list.html']


class PFSlabCreateView(LoginRequiredMixin, CreateView):
    """
    Create new PF slab.
    Converted from: aspnet/Module/HR/Masters/PF_Slab.aspx (Footer Insert)
    """
    model = TblhrPfSlab
    form_class = PFSlabForm
    template_name = 'human_resource/partials/pf_slab_form.html'
    success_url = reverse_lazy('human_resource:pf-slab-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/pf_slab_row.html'
            return render(self.request, self.template_name, {'pf_slab': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/pf_slab_form.html', {'form': form})
        return super().form_invalid(form)


class PFSlabUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing PF slab (inline editing).
    Converted from: aspnet/Module/HR/Masters/PF_Slab.aspx (Edit Button)
    """
    model = TblhrPfSlab
    form_class = PFSlabForm
    template_name = 'human_resource/partials/pf_slab_edit_row.html'
    success_url = reverse_lazy('human_resource:pf-slab-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'pf_slab': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/pf_slab_row.html', {'pf_slab': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'pf_slab': self.object})
        return super().form_invalid(form)


class PFSlabDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete PF slab.
    Converted from: aspnet/Module/HR/Masters/PF_Slab.aspx (Delete Button)
    """
    model = TblhrPfSlab
    success_url = reverse_lazy('human_resource:pf-slab-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class PFSlabRowView(LoginRequiredMixin, DetailView):
    """
    Return single PF slab row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrPfSlab
    template_name = 'human_resource/partials/pf_slab_row.html'
    context_object_name = 'pf_slab'
    pk_url_kwarg = 'id'


# ============================================================================
# SWAP CARD MASTER
# ============================================================================

class SwapCardListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of swap cards.
    Converted from: aspnet/Module/HR/Masters/SwapCardNo.aspx
    """
    model = TblhrSwapcard
    template_name = 'human_resource/swap_card_list.html'
    context_object_name = 'swap_cards'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['human_resource/partials/swap_card_list_partial.html']
        return ['human_resource/swap_card_list.html']


class SwapCardCreateView(LoginRequiredMixin, CreateView):
    """
    Create new swap card.
    Converted from: aspnet/Module/HR/Masters/SwapCardNo.aspx (Footer Insert)
    """
    model = TblhrSwapcard
    form_class = SwapCardForm
    template_name = 'human_resource/partials/swap_card_form.html'
    success_url = reverse_lazy('human_resource:swap-card-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            self.template_name = 'human_resource/partials/swap_card_row.html'
            return render(self.request, self.template_name, {'swap_card': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/swap_card_form.html', {'form': form})
        return super().form_invalid(form)


class SwapCardUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing swap card (inline editing).
    Converted from: aspnet/Module/HR/Masters/SwapCardNo.aspx (Edit Button)
    """
    model = TblhrSwapcard
    form_class = SwapCardForm
    template_name = 'human_resource/partials/swap_card_edit_row.html'
    success_url = reverse_lazy('human_resource:swap-card-list')
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'swap_card': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'human_resource/partials/swap_card_row.html', {'swap_card': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'swap_card': self.object})
        return super().form_invalid(form)


class SwapCardDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete swap card.
    Converted from: aspnet/Module/HR/Masters/SwapCardNo.aspx (Delete Button)
    """
    model = TblhrSwapcard
    success_url = reverse_lazy('human_resource:swap-card-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response


class SwapCardRowView(LoginRequiredMixin, DetailView):
    """
    Return single swap card row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblhrSwapcard
    template_name = 'human_resource/partials/swap_card_row.html'
    context_object_name = 'swap_card'
    pk_url_kwarg = 'id'
