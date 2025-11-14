"""
Audit Service - Manages audit field population across all modules

Provides centralized utilities for populating standard audit fields:
- sysdate (format: 'dd-MM-yyyy')
- systime (format: 'HH:MM:SS')
- sessionid (user ID as string)
- compid (company ID from session)
- finyearid (financial year ID from session)
"""
from datetime import datetime
from typing import Any, Dict, Optional
from django.http import HttpRequest


class AuditService:
    """
    Service class for managing audit field population
    """

    @staticmethod
    def get_audit_data(request: HttpRequest) -> Dict[str, Any]:
        """
        Get all audit field values for the current request

        Args:
            request: Django HTTP request object

        Returns:
            Dictionary with audit field values
        """
        now = datetime.now()

        return {
            'sysdate': now.strftime('%d-%m-%Y'),
            'systime': now.strftime('%H:%M:%S'),
            'sessionid': str(request.user.id) if request.user.is_authenticated else '0',
            'compid': request.session.get('compid', 1),
            'finyearid': request.session.get('finyearid', 1)
        }

    @staticmethod
    def populate_audit_fields(obj: Any, request: HttpRequest, update: bool = False) -> None:
        """
        Populate audit fields on a model instance

        Args:
            obj: Model instance to populate
            request: Django HTTP request object
            update: If True, only update modification fields (if they exist)
        """
        audit_data = AuditService.get_audit_data(request)

        # Always set these fields on create
        if not update:
            if hasattr(obj, 'sysdate'):
                obj.sysdate = audit_data['sysdate']
            if hasattr(obj, 'systime'):
                obj.systime = audit_data['systime']
            if hasattr(obj, 'sessionid'):
                obj.sessionid = audit_data['sessionid']
            if hasattr(obj, 'compid'):
                obj.compid = audit_data['compid']
            if hasattr(obj, 'finyearid'):
                obj.finyearid = audit_data['finyearid']

        # Update modification fields if they exist
        if update:
            if hasattr(obj, 'moddate'):
                obj.moddate = audit_data['sysdate']
            if hasattr(obj, 'modtime'):
                obj.modtime = audit_data['systime']
            if hasattr(obj, 'modby'):
                obj.modby = audit_data['sessionid']

    @staticmethod
    def get_current_date() -> str:
        """Get current date in 'dd-MM-yyyy' format"""
        return datetime.now().strftime('%d-%m-%Y')

    @staticmethod
    def get_current_time() -> str:
        """Get current time in 'HH:MM:SS' format"""
        return datetime.now().strftime('%H:%M:%S')

    @staticmethod
    def get_current_datetime() -> str:
        """Get current datetime in 'dd-MM-yyyy HH:MM:SS' format"""
        now = datetime.now()
        return f"{now.strftime('%d-%m-%Y')} {now.strftime('%H:%M:%S')}"

    @staticmethod
    def get_user_id(request: HttpRequest) -> str:
        """Get user ID as string for sessionid field"""
        return str(request.user.id) if request.user.is_authenticated else '0'

    @staticmethod
    def get_company_id(request: HttpRequest, default: int = 1) -> int:
        """Get company ID from session"""
        return request.session.get('compid', default)

    @staticmethod
    def get_financial_year_id(request: HttpRequest, default: int = 1) -> int:
        """Get financial year ID from session"""
        return request.session.get('finyearid', default)


class AuditMixin:
    """
    Mixin for views that need to populate audit fields

    Usage:
        class CustomerCreateView(AuditMixin, CreateView):
            model = SdCustMaster
            # ... rest of view

            def form_valid(self, form):
                self.populate_audit_fields(form.instance)
                return super().form_valid(form)
    """

    def populate_audit_fields(self, obj: Any, update: bool = False) -> None:
        """
        Populate audit fields on object

        Args:
            obj: Model instance
            update: If True, populate update fields instead of create fields
        """
        AuditService.populate_audit_fields(obj, self.request, update=update)

    def get_audit_data(self) -> Dict[str, Any]:
        """Get audit data for current request"""
        return AuditService.get_audit_data(self.request)
