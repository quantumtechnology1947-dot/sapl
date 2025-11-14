"""
OnSite Attendance Views

Employee onsite attendance tracking with create, edit, delete, and reporting.
Uses ProjectService for business logic.
Extracted from monolithic views.py.
"""

from datetime import datetime
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from ..models import TblonsiteattendanceMaster
from ..services import ProjectService


class ProjectManagementBaseMixin(LoginRequiredMixin):
    """Base mixin for all Project Management views"""
    login_url = '/login/'

    def get_compid(self):
        return self.request.session.get('company_id', 1)

    def get_finyearid(self):
        return self.request.session.get('financial_year_id', 1)

    def get_sessionid(self):
        return self.request.session.session_key or 'default'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compid'] = self.get_compid()
        context['finyearid'] = self.get_finyearid()
        return context


class OnSiteAttendanceListView(ProjectManagementBaseMixin, ListView):
    """
    OnSite Attendance List View - Display all attendance records with search filters
    Uniform list view matching material_planning pattern
    """
    model = TblonsiteattendanceMaster
    template_name = 'project_management/attendance/list_view.html'
    context_object_name = 'attendances'
    paginate_by = 20

    def get_queryset(self):
        compid = self.get_compid()
        queryset = TblonsiteattendanceMaster.objects.filter(compid=compid).order_by('-onsitedate', 'empid')

        # Apply search filters
        search_date = self.request.GET.get('search_date', '')
        search_empid = self.request.GET.get('search_empid', '')
        search_bg = self.request.GET.get('search_bg', '')

        if search_date:
            queryset = queryset.filter(onsitedate=search_date)
        if search_empid:
            queryset = queryset.filter(empid__icontains=search_empid)
        if search_bg:
            queryset = ProjectService.filter_attendance_by_bg_group(queryset, compid, search_bg)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup

        compid = self.get_compid()
        context['bg_groups'] = Businessgroup.objects.all().order_by('symbol')

        # Enrich attendance data using service
        context['attendances'] = ProjectService.enrich_attendance_with_employee_info(
            context['attendances'], compid
        )

        return context


class OnSiteAttendanceNewView(ProjectManagementBaseMixin, TemplateView):
    """
    OnSite Attendance New - Create attendance for employees
    Converted from: OnSiteAttendance_New.aspx
    Filters by Date and BG Group, shows employees not yet marked for the date
    """
    template_name = 'project_management/attendance/new.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup

        compid = self.get_compid()
        context['bg_groups'] = Businessgroup.objects.all().order_by('symbol')

        # Get filter values
        selected_date = self.request.GET.get('selected_date', datetime.now().strftime('%d-%m-%Y'))
        bg_group = self.request.GET.get('bg_group', '')

        context['selected_date'] = selected_date
        context['bg_group'] = bg_group

        # Get employees if filters are applied
        if selected_date and bg_group:
            # Get unmarked employees using service
            context['employees'] = ProjectService.get_unmarked_employees(compid, selected_date, bg_group)

        return context

    def post(self, request):
        """Handle bulk attendance creation"""
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        sessionid = self.get_sessionid()
        sysdate = datetime.now().strftime('%d-%m-%Y')
        systime = datetime.now().strftime('%H:%M:%S')

        selected_date = request.POST.get('selected_date')

        # Validate date using service
        is_valid, error_msg = ProjectService.validate_attendance_date(selected_date, allow_past=False)
        if not is_valid:
            messages.error(request, error_msg)
            return self.render_to_response(self.get_context_data())

        # Process each checked employee
        created_count = 0
        for key in request.POST.keys():
            if key.startswith('check_'):
                empid = key.replace('check_', '')
                shift = request.POST.get(f'shift_{empid}', '0')
                status = request.POST.get(f'status_{empid}', '0')
                onsite = request.POST.get(f'onsite_{empid}', '')
                fromtime = request.POST.get(f'fromtime_{empid}', '09:00:00 AM')

                if onsite:
                    existing = TblonsiteattendanceMaster.objects.filter(
                        compid=compid, onsitedate=selected_date, empid=empid
                    ).first()

                    if not existing:
                        TblonsiteattendanceMaster.objects.create(
                            compid=compid, finyearid=finyearid, sessionid=sessionid,
                            sysdate=sysdate, systime=systime, onsitedate=selected_date,
                            empid=empid, shift=int(shift), status=int(status),
                            onsite=onsite, fromtime=fromtime, totime=''
                        )
                        created_count += 1

        if created_count > 0:
            messages.success(request, f'Successfully created {created_count} attendance record(s)!')
        else:
            messages.warning(request, 'No attendance records created. Please check your selections.')

        return self.render_to_response(self.get_context_data())


class OnSiteAttendanceEditView(ProjectManagementBaseMixin, TemplateView):
    """
    OnSite Attendance Edit - Edit existing attendance records with inline editing
    Converted from: OnSiteAttendance_Edit.aspx
    """
    template_name = 'project_management/attendance/edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup

        compid = self.get_compid()
        context['bg_groups'] = Businessgroup.objects.all().order_by('symbol')

        # Get filter values
        selected_date = self.request.GET.get('selected_date', datetime.now().strftime('%d-%m-%Y'))
        bg_group = self.request.GET.get('bg_group', '')

        context['selected_date'] = selected_date
        context['bg_group'] = bg_group

        # Validate date for editing using service
        context['can_edit'] = ProjectService.can_edit_attendance_date(selected_date)

        # Get attendance records if filters are applied
        if selected_date and context['can_edit']:
            query = TblonsiteattendanceMaster.objects.filter(compid=compid, onsitedate=selected_date)
            query = ProjectService.filter_attendance_by_bg_group(query, compid, bg_group)

            # Enrich with employee details using service
            context['attendances'] = ProjectService.enrich_attendance_with_employee_info(
                query.order_by('id'), compid
            )

        return context

    def post(self, request):
        """Handle inline update"""
        compid = self.get_compid()
        sessionid = self.get_sessionid()
        sysdate = datetime.now().strftime('%d-%m-%Y')
        systime = datetime.now().strftime('%H:%M:%S')

        att_id = request.POST.get('att_id')
        shift = request.POST.get('shift', '0')
        status = request.POST.get('status', '0')
        onsite = request.POST.get('onsite', '')
        fromtime = request.POST.get('fromtime', '')
        totime = request.POST.get('totime', '')

        if att_id and onsite and fromtime and totime:
            attendance = TblonsiteattendanceMaster.objects.filter(id=att_id, compid=compid).first()

            if attendance:
                attendance.shift = int(shift)
                attendance.status = int(status)
                attendance.onsite = onsite
                attendance.fromtime = fromtime
                attendance.totime = totime
                attendance.upsysdate = sysdate
                attendance.upsystime = systime
                attendance.upsessionid = sessionid
                attendance.save()
                messages.success(request, 'Attendance updated successfully!')
            else:
                messages.error(request, 'Attendance record not found!')
        else:
            messages.error(request, 'Please provide all required information!')

        return self.render_to_response(self.get_context_data())


class OnSiteAttendanceDeleteView(ProjectManagementBaseMixin, TemplateView):
    """OnSite Attendance Delete - Delete attendance records"""
    template_name = 'project_management/attendance/delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup

        compid = self.get_compid()
        context['bg_groups'] = Businessgroup.objects.all().order_by('symbol')

        # Get filter values
        selected_date = self.request.GET.get('selected_date', datetime.now().strftime('%d-%m-%Y'))
        bg_group = self.request.GET.get('bg_group', '')

        context['selected_date'] = selected_date
        context['bg_group'] = bg_group

        # Get attendance records if filters are applied
        if selected_date:
            query = TblonsiteattendanceMaster.objects.filter(compid=compid, onsitedate=selected_date)
            query = ProjectService.filter_attendance_by_bg_group(query, compid, bg_group)

            # Enrich with employee details using service
            context['attendances'] = ProjectService.enrich_attendance_with_employee_info(
                query.order_by('id'), compid
            )

        return context

    def post(self, request):
        """Handle delete"""
        compid = self.get_compid()
        att_id = request.POST.get('att_id')

        if att_id:
            attendance = TblonsiteattendanceMaster.objects.filter(id=att_id, compid=compid).first()
            if attendance:
                attendance.delete()
                messages.success(request, 'Attendance record deleted successfully!')
            else:
                messages.error(request, 'Attendance record not found!')

        return self.render_to_response(self.get_context_data())


class OnSiteAttendancePrintView(ProjectManagementBaseMixin, TemplateView):
    """
    OnSite Attendance Print - Filter and generate attendance report
    Multiple filter options: Year, Month, Date Range, Employee, BG Group
    """
    template_name = 'project_management/attendance/print.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup
        from core.models import TblfinancialMaster

        compid = self.get_compid()

        # Get financial years and BG Groups
        context['financial_years'] = TblfinancialMaster.objects.filter(compid=compid).order_by('-finyearid')
        context['bg_groups'] = Businessgroup.objects.all().order_by('symbol')

        # Get filter values
        context['selected_year'] = self.request.GET.get('year', '')
        context['selected_month'] = self.request.GET.get('month', '')
        context['from_date'] = self.request.GET.get('from_date', '')
        context['to_date'] = self.request.GET.get('to_date', '')
        context['employee_name'] = self.request.GET.get('employee_name', '')
        context['bg_group'] = self.request.GET.get('bg_group', '')

        return context

    def post(self, request):
        """Generate report based on filters using service"""
        compid = self.get_compid()

        filters = {
            'year': request.POST.get('year', ''),
            'month': request.POST.get('month', ''),
            'from_date': request.POST.get('from_date', ''),
            'to_date': request.POST.get('to_date', ''),
            'employee_name': request.POST.get('employee_name', ''),
            'bg_group': request.POST.get('bg_group', ''),
        }

        # Build query using service
        attendances = ProjectService.build_attendance_report_query(compid, filters)

        context = self.get_context_data()
        context['report_data'] = attendances[:100]  # Limit to 100 records

        return self.render_to_response(context)
