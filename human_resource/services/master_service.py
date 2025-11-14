"""
Master Service
Business logic for master data validations and common operations
"""

from datetime import datetime


class MasterService:
    """
    Service class for master data business logic
    """

    @staticmethod
    def set_audit_fields(instance, user, company_id=None, fy_id=None):
        """
        Set standard audit fields on any model instance
        """
        now = datetime.now()
        instance.sysdate = now.strftime('%d-%m-%Y')
        instance.systime = now.strftime('%H:%M:%S')
        instance.sessionid = str(user.id) if user else ''

        if company_id and hasattr(instance, 'compid'):
            instance.compid = company_id
        if fy_id and hasattr(instance, 'finyearid'):
            instance.finyearid = fy_id

    @staticmethod
    def validate_unique_code(model, code_field, code_value, exclude_id=None):
        """
        Validate that a code is unique within a model
        """
        queryset = model.objects.filter(**{code_field: code_value})
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        if queryset.exists():
            return False, f"{code_field} '{code_value}' already exists"
        return True, ""

    @staticmethod
    def validate_date_range(start_date, end_date):
        """
        Validate that end date is after start date
        """
        if end_date and start_date and end_date < start_date:
            return False, "End date must be after start date"
        return True, ""

    @staticmethod
    def get_next_sequence(model, field_name, prefix='', company_id=None):
        """
        Generate next sequence number for a field
        Example: prefix='EMP' returns 'EMP0001', 'EMP0002', etc.
        """
        queryset = model.objects.all()
        if company_id and hasattr(model, 'compid'):
            queryset = queryset.filter(compid=company_id)

        last_record = queryset.order_by(f'-{field_name}').first()

        if last_record:
            last_value = getattr(last_record, field_name)
            if last_value:
                try:
                    # Extract numeric part
                    numeric_part = ''.join(filter(str.isdigit, last_value))
                    next_num = int(numeric_part) + 1
                    return f"{prefix}{next_num:04d}"
                except ValueError:
                    pass

        # Default to first number
        return f"{prefix}0001"

    @staticmethod
    def validate_working_days(days):
        """
        Validate working days (must be between 0 and 31)
        """
        if days < 0 or days > 31:
            return False, "Working days must be between 0 and 31"
        return True, ""

    @staticmethod
    def validate_mobile_number(mobile_no):
        """
        Validate mobile number format
        """
        if not mobile_no:
            return True, ""

        # Remove spaces and dashes
        cleaned = mobile_no.replace(' ', '').replace('-', '')

        # Check length (assuming 10 digits for India)
        if len(cleaned) < 10 or len(cleaned) > 13:
            return False, "Mobile number must be 10-13 digits"

        # Check if all digits
        if not cleaned.isdigit():
            return False, "Mobile number must contain only digits"

        return True, ""

    @staticmethod
    def validate_email(email):
        """
        Basic email validation
        """
        import re

        if not email:
            return True, ""

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Invalid email format"

        return True, ""

    @staticmethod
    def validate_salary_range(min_salary, max_salary):
        """
        Validate salary range for grade/designation
        """
        if max_salary and min_salary and max_salary < min_salary:
            return False, "Maximum salary must be greater than minimum salary"
        return True, ""
