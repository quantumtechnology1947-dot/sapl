"""
Project Planning Service

Business logic for project scheduling, status tracking, and file management.
Extracted from views.py for better separation of concerns.
"""

from datetime import datetime, timedelta
from django.db.models import Q
from ..models import (
    TblpmProjectplanningMaster,
    TblpmProjectstatus,
    TblonsiteattendanceMaster,
)


class ProjectService:
    """Service class for Project Planning and Status operations"""

    @staticmethod
    def enrich_work_orders_with_planning_files(work_orders, compid):
        """
        Enrich work orders with financial year and planning file information.

        Args:
            work_orders: QuerySet of SdCustWorkorderMaster objects
            compid: Company ID

        Returns:
            list: Enriched work order dictionaries with financial year names
        """
        from sys_admin.models import TblfinancialMaster

        enriched_wos = []
        for wo in work_orders:
            finyear = TblfinancialMaster.objects.filter(finyearid=wo.finyearid).first()
            enriched_wos.append({
                'id': wo.id,
                'wono': wo.wono,
                'date': wo.taskworkorderdate,
                'title': wo.taskprojecttitle or '-',
                'finyear': finyear.finyear if finyear else '-'
            })

        return enriched_wos

    @staticmethod
    def get_planning_files_for_wo(compid, wono):
        """
        Get all planning files for a work order.

        Args:
            compid: Company ID
            wono: Work Order Number

        Returns:
            QuerySet: TblpmProjectplanningMaster records for this WO
        """
        return TblpmProjectplanningMaster.objects.filter(
            compid=compid,
            wono=wono
        ).order_by('-id')

    @staticmethod
    def create_planning_file(compid, finyearid, sessionid, wono, uploaded_file):
        """
        Create a new project planning file record.

        Args:
            compid: Company ID
            finyearid: Financial Year ID
            sessionid: Session ID
            wono: Work Order Number
            uploaded_file: Django UploadedFile object

        Returns:
            TblpmProjectplanningMaster: Created planning record
        """
        planning = TblpmProjectplanningMaster()
        planning.compid = compid
        planning.finyearid = finyearid
        planning.sessionid = sessionid
        planning.sysdate = datetime.now().strftime('%Y-%m-%d')
        planning.systime = datetime.now().strftime('%H:%M:%S')
        planning.wono = wono
        planning.filename = uploaded_file.name
        planning.filesize = uploaded_file.size
        planning.contenttype = uploaded_file.content_type
        planning.filedata = uploaded_file.read()
        planning.save()

        return planning

    @staticmethod
    def delete_planning_file(file_id, compid):
        """
        Delete a planning file.

        Args:
            file_id: Planning file ID
            compid: Company ID

        Returns:
            bool: True if deleted, False otherwise
        """
        deleted_count, _ = TblpmProjectplanningMaster.objects.filter(
            id=file_id,
            compid=compid
        ).delete()
        return deleted_count > 0

    @staticmethod
    def enrich_attendance_with_employee_info(attendances, compid):
        """
        Enrich attendance records with employee names and business group symbols.

        Args:
            attendances: QuerySet or list of TblonsiteattendanceMaster objects
            compid: Company ID

        Returns:
            list: Enriched attendance dictionaries
        """
        from human_resource.models import Businessgroup, TblhrOfficestaff

        enriched_attendances = []
        for att in attendances:
            emp = TblhrOfficestaff.objects.filter(
                compid=compid,
                empid=att.empid
            ).first()

            bg_symbol = ''
            if emp and emp.bggroup:
                bg_obj = Businessgroup.objects.filter(id=emp.bggroup).first()
                bg_symbol = bg_obj.symbol if bg_obj else ''

            enriched_attendances.append({
                'id': att.id,
                'onsitedate': att.onsitedate,
                'empid': att.empid,
                'empname': emp.employeename if emp else att.empid,
                'bg_symbol': bg_symbol,
                'shift': att.shift,
                'shift_display': 'Day' if att.shift == 0 else 'Night',
                'status': att.status,
                'status_display': 'Present' if att.status == 0 else 'Absent',
                'onsite': att.onsite or '',
                'fromtime': att.fromtime or '',
                'totime': att.totime or '',
            })

        return enriched_attendances

    @staticmethod
    def get_unmarked_employees(compid, selected_date, bg_group=None):
        """
        Get employees not yet marked for attendance on a specific date.

        Args:
            compid: Company ID
            selected_date: Date string (DD-MM-YYYY)
            bg_group: Optional BG Group ID filter

        Returns:
            list: Unmarked employee dictionaries with default values
        """
        from human_resource.models import Businessgroup, TblhrOfficestaff

        # Get all employees from BG group
        query = TblhrOfficestaff.objects.filter(compid=compid)
        if bg_group and bg_group != '0':
            query = query.filter(bggroup=bg_group)

        all_employees = query.values('userid', 'empid', 'employeename', 'bggroup')

        # Get employees already marked for this date
        marked_empids = TblonsiteattendanceMaster.objects.filter(
            compid=compid,
            onsitedate=selected_date
        ).values_list('empid', flat=True)

        # Filter out already marked employees
        employees = []
        for emp in all_employees:
            if emp['empid'] not in marked_empids:
                bg_symbol = ''
                if emp.get('bggroup'):
                    bg_obj = Businessgroup.objects.filter(id=emp['bggroup']).first()
                    bg_symbol = bg_obj.symbol if bg_obj else ''

                employees.append({
                    'userid': emp['userid'],
                    'empid': emp['empid'],
                    'empname': emp['employeename'],
                    'bg_symbol': bg_symbol,
                    'hours': '8'  # Default hours
                })

        return employees

    @staticmethod
    def validate_attendance_date(selected_date, allow_past=False):
        """
        Validate attendance date (must be >= current date for creation).

        Args:
            selected_date: Date string (DD-MM-YYYY)
            allow_past: Allow past dates (for editing)

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            date_parts = selected_date.split('-')
            if len(date_parts) == 3:
                entered_date = datetime.strptime(selected_date, '%d-%m-%Y')
                current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

                if not allow_past and entered_date < current_date:
                    return False, 'Invalid date! Cannot create attendance for past dates.'

                return True, None
        except Exception:
            return False, 'Invalid date format. Use DD-MM-YYYY.'

    @staticmethod
    def can_edit_attendance_date(selected_date):
        """
        Check if attendance for a date can be edited.
        Allow editing for yesterday, today, or future dates.
        Allow 2 days ago only if previous day was Sunday.

        Args:
            selected_date: Date string (DD-MM-YYYY)

        Returns:
            bool: True if editable, False otherwise
        """
        try:
            date_parts = selected_date.split('-')
            if len(date_parts) == 3:
                entered_date = datetime.strptime(selected_date, '%d-%m-%Y')
                current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                diff_days = (entered_date - current_date).days

                # Allow editing if date is yesterday (-1), today (0), or future (>0)
                if diff_days >= -1:
                    return True

                # If 2 days ago (-2), only allow if previous day was Sunday
                if diff_days == -2:
                    previous_day = entered_date + timedelta(days=1)
                    if previous_day.weekday() == 6:  # 6 = Sunday
                        return True

                return False
        except Exception:
            return False

    @staticmethod
    def filter_attendance_by_bg_group(queryset, compid, bg_group):
        """
        Filter attendance queryset by business group.

        Args:
            queryset: Base QuerySet of TblonsiteattendanceMaster
            compid: Company ID
            bg_group: Business Group ID

        Returns:
            QuerySet: Filtered queryset
        """
        from human_resource.models import TblhrOfficestaff

        if bg_group and bg_group != '0':
            empids = TblhrOfficestaff.objects.filter(
                compid=compid,
                bggroup=bg_group
            ).values_list('empid', flat=True)
            queryset = queryset.filter(empid__in=empids)

        return queryset

    @staticmethod
    def build_attendance_report_query(compid, filters):
        """
        Build attendance report query based on multiple filter options.

        Args:
            compid: Company ID
            filters: Dict with filter parameters (year, month, from_date, to_date, employee_name, bg_group)

        Returns:
            QuerySet: Filtered attendance queryset
        """
        from human_resource.models import TblhrOfficestaff

        query = TblonsiteattendanceMaster.objects.filter(compid=compid)

        # Year and Month filter
        selected_year = filters.get('year')
        selected_month = filters.get('month')
        if selected_year and selected_month and selected_month != '0':
            month_pattern = f'-{selected_month.zfill(2)}-'
            query = query.filter(onsitedate__contains=month_pattern, finyearid=selected_year)

        # Date range filter
        from_date = filters.get('from_date')
        to_date = filters.get('to_date')
        if from_date and to_date:
            query = query.filter(onsitedate__gte=from_date, onsitedate__lte=to_date)

        # Employee filter
        employee_name = filters.get('employee_name')
        if employee_name and '[' in employee_name:
            empid = employee_name.split('[')[-1].split(']')[0]
            query = query.filter(empid=empid)

        # BG Group filter
        bg_group = filters.get('bg_group')
        if bg_group and bg_group != 'Select':
            empids = TblhrOfficestaff.objects.filter(
                compid=compid,
                bggroup=bg_group
            ).values_list('empid', flat=True)
            query = query.filter(empid__in=empids)

        return query.order_by('-onsitedate', 'empid')
