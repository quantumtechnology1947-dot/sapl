"""
Employee Service
Business logic for employee operations
"""

from datetime import datetime
from django.db.models import Q
from ..models import TblhrOfficestaff


class EmployeeService:
    """
    Service class for employee-related business logic
    """

    @staticmethod
    def generate_employee_id(company_id):
        """
        Generate next employee ID for the company
        Format: EMP0001, EMP0002, etc.
        """
        last_employee = TblhrOfficestaff.objects.filter(
            compid=company_id
        ).order_by('-userid').first()

        if last_employee and last_employee.empid:
            try:
                last_num = int(last_employee.empid.replace('EMP', ''))
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1

        return f'EMP{new_num:04d}'

    @staticmethod
    def search_employees(queryset, search_query):
        """
        Search employees by name, ID, mobile, or email
        """
        if not search_query:
            return queryset

        return queryset.filter(
            Q(employeename__icontains=search_query) |
            Q(empid__icontains=search_query) |
            Q(mobileno__icontains=search_query) |
            Q(companyemail__icontains=search_query)
        )

    @staticmethod
    def handle_file_upload(instance, file_field, field_prefix):
        """
        Handle photo/CV file upload and set related fields
        field_prefix: 'photo' or 'cv'
        """
        if file_field and hasattr(file_field, 'read'):
            setattr(instance, f'{field_prefix}filename', file_field.name)
            setattr(instance, f'{field_prefix}size', str(file_field.size))
            setattr(instance, f'{field_prefix}contenttype', file_field.content_type)
            setattr(instance, f'{field_prefix}data', file_field.read())
            return True
        return False

    @staticmethod
    def set_audit_fields(instance, user):
        """
        Set audit fields for employee record
        """
        now = datetime.now()
        instance.sysdate = now.strftime('%d-%m-%Y')
        instance.systime = now.strftime('%H:%M:%S')
        instance.sessionid = str(user.id) if user else ''
