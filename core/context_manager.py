"""
Financial Year Context Manager

Automatically detects and manages financial year context for the application.
Ensures all queries are scoped to the correct company and financial year.
"""

from datetime import datetime, date
from typing import Optional, Dict, Tuple
from django.core.exceptions import ImproperlyConfigured


class FinancialYearContextManager:
    """
    Manages financial year and company context for the application.
    
    Features:
    - Auto-detects current financial year based on today's date
    - Session-based context storage
    - Company and FY switching
    - Automatic query filtering
    """
    
    SESSION_KEY_COMPANY = 'active_company_id'
    SESSION_KEY_FINYEAR = 'active_finyear_id'
    SESSION_KEY_COMPANY_NAME = 'active_company_name'
    SESSION_KEY_FINYEAR_NAME = 'active_finyear_name'
    
    def __init__(self, request=None):
        """
        Initialize context manager.
        
        Args:
            request: Django request object (optional)
        """
        self.request = request
        self._company_id = None
        self._finyear_id = None
    
    def get_current_financial_year(self, company_id: Optional[int] = None) -> Optional['TblfinancialMaster']:
        """
        Get default financial year (highest FinYearId with transaction data).

        Mimics ASP.NET behavior: dropdownFinYear() orders by FinYearId DESC,
        then SelectedIndex=1 selects the first item (highest ID).

        Enhancement: Only selects FYs that have transaction data (PRs) to avoid
        defaulting to empty future financial years.

        Args:
            company_id: Optional company ID to filter by

        Returns:
            TblfinancialMaster object or None
        """
        from sys_admin.models import TblfinancialMaster
        from material_management.models import PRMaster

        # Build query - get ALL financial years (not just active)
        queryset = TblfinancialMaster.objects.all()

        if company_id:
            queryset = queryset.filter(compid=company_id)

        # Order by FinYearId DESC
        queryset = queryset.order_by('-finyearid')

        # Find the first FY that has significant transaction data (PRs)
        # Use a threshold to avoid selecting test/future years with minimal data
        MIN_PR_THRESHOLD = 10  # Minimum PRs to consider FY as "active"

        for fy in queryset:
            pr_count = PRMaster.objects.filter(
                fin_year_id=fy.finyearid,
                comp_id=company_id if company_id else fy.compid
            ).count()

            if pr_count >= MIN_PR_THRESHOLD:
                return fy

        # Fallback: return highest FY if no significant transaction data found
        return queryset.first()
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """
        Parse date string in various formats.
        
        Args:
            date_str: Date string (DD-MM-YYYY, YYYY-MM-DD, etc.)
            
        Returns:
            date object or None
        """
        if not date_str:
            return None
        
        # Try common formats
        formats = [
            '%d-%m-%Y',  # 01-04-2024
            '%Y-%m-%d',  # 2024-04-01
            '%d/%m/%Y',  # 01/04/2024
            '%Y/%m/%d',  # 2024/04/01
            '%d.%m.%Y',  # 01.04.2024
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except (ValueError, AttributeError):
                continue
        
        return None
    
    def get_user_default_company(self, user) -> Optional['TblcompanyMaster']:
        """
        Get user's default company.
        
        For now, returns the first active company.
        TODO: Add user-company relationship in future.
        
        Args:
            user: Django user object
            
        Returns:
            TblcompanyMaster object or None
        """
        from sys_admin.models import TblcompanyMaster

        # For now, return first company (active or inactive)
        # In future, this should check user's assigned company
        # Note: Flag filter removed because production data may have inactive companies
        return TblcompanyMaster.objects.first()
    
    def initialize_context(self, user) -> Tuple[Optional[int], Optional[int]]:
        """
        Initialize context for a user session.
        
        Auto-detects company and financial year if not already set.
        
        Args:
            user: Django user object
            
        Returns:
            Tuple of (company_id, finyear_id)
        """
        if not self.request or not self.request.session:
            raise ImproperlyConfigured("Request with session required for context initialization")
        
        # Check if context already exists in session
        company_id = self.request.session.get(self.SESSION_KEY_COMPANY)
        finyear_id = self.request.session.get(self.SESSION_KEY_FINYEAR)
        
        if company_id and finyear_id:
            # Context already set
            self._company_id = company_id
            self._finyear_id = finyear_id
            return (company_id, finyear_id)
        
        # Auto-detect company
        if not company_id:
            company = self.get_user_default_company(user)
            if company:
                company_id = company.compid
                self.request.session[self.SESSION_KEY_COMPANY] = company_id
                self.request.session[self.SESSION_KEY_COMPANY_NAME] = company.companyname
        
        # Auto-detect financial year
        if not finyear_id and company_id:
            finyear = self.get_current_financial_year(company_id)
            print(f"DEBUG: get_current_financial_year returned: {finyear}")
            if finyear:
                finyear_id = finyear.finyearid
                print(f"DEBUG: Setting FY ID {finyear_id} - {finyear.finyear}")
                self.request.session[self.SESSION_KEY_FINYEAR] = finyear_id
                self.request.session[self.SESSION_KEY_FINYEAR_NAME] = finyear.finyear
            else:
                print("DEBUG: get_current_financial_year returned None!")
        
        self._company_id = company_id
        self._finyear_id = finyear_id
        
        return (company_id, finyear_id)
    
    def set_context(self, company_id: int, finyear_id: int):
        """
        Manually set context (for switching).
        
        Args:
            company_id: Company ID
            finyear_id: Financial Year ID
        """
        if not self.request or not self.request.session:
            raise ImproperlyConfigured("Request with session required for setting context")
        
        from sys_admin.models import TblcompanyMaster, TblfinancialMaster
        
        # Validate company
        company = TblcompanyMaster.objects.filter(compid=company_id).first()
        if not company:
            raise ValueError(f"Invalid company ID: {company_id}")
        
        # Validate financial year
        finyear = TblfinancialMaster.objects.filter(finyearid=finyear_id).first()
        if not finyear:
            raise ValueError(f"Invalid financial year ID: {finyear_id}")
        
        # Set in session
        self.request.session[self.SESSION_KEY_COMPANY] = company_id
        self.request.session[self.SESSION_KEY_FINYEAR] = finyear_id
        self.request.session[self.SESSION_KEY_COMPANY_NAME] = company.companyname
        self.request.session[self.SESSION_KEY_FINYEAR_NAME] = finyear.finyear
        
        self._company_id = company_id
        self._finyear_id = finyear_id
    
    def get_context(self) -> Dict:
        """
        Get current context.
        
        Returns:
            Dict with company_id, finyear_id, company_name, finyear_name
        """
        if not self.request or not self.request.session:
            return {
                'company_id': self._company_id,
                'finyear_id': self._finyear_id,
                'company_name': None,
                'finyear_name': None,
            }
        
        return {
            'company_id': self.request.session.get(self.SESSION_KEY_COMPANY),
            'finyear_id': self.request.session.get(self.SESSION_KEY_FINYEAR),
            'company_name': self.request.session.get(self.SESSION_KEY_COMPANY_NAME),
            'finyear_name': self.request.session.get(self.SESSION_KEY_FINYEAR_NAME),
        }
    
    def clear_context(self):
        """Clear context from session."""
        if self.request and self.request.session:
            self.request.session.pop(self.SESSION_KEY_COMPANY, None)
            self.request.session.pop(self.SESSION_KEY_FINYEAR, None)
            self.request.session.pop(self.SESSION_KEY_COMPANY_NAME, None)
            self.request.session.pop(self.SESSION_KEY_FINYEAR_NAME, None)
        
        self._company_id = None
        self._finyear_id = None
    
    @property
    def company_id(self) -> Optional[int]:
        """Get active company ID."""
        if self.request and self.request.session:
            return self.request.session.get(self.SESSION_KEY_COMPANY)
        return self._company_id
    
    @property
    def finyear_id(self) -> Optional[int]:
        """Get active financial year ID."""
        if self.request and self.request.session:
            return self.request.session.get(self.SESSION_KEY_FINYEAR)
        return self._finyear_id
    
    def has_context(self) -> bool:
        """Check if context is set."""
        return self.company_id is not None and self.finyear_id is not None


# Convenience function
def get_context_manager(request=None) -> FinancialYearContextManager:
    """
    Get a context manager instance.
    
    Args:
        request: Django request object (optional)
        
    Returns:
        FinancialYearContextManager instance
    """
    return FinancialYearContextManager(request)

