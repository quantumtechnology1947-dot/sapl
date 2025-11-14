"""
Custom Model Managers

Provides automatic filtering by financial year and company context.
"""

from django.db import models
from django.db.models import QuerySet


class FinancialYearQuerySet(QuerySet):
    """
    QuerySet that automatically filters by active financial year context.
    
    Usage:
        # In model:
        objects = FinancialYearManager()
        
        # In view:
        MyModel.objects.for_active_context(request)
    """
    
    def for_active_context(self, request):
        """
        Filter queryset by active company and financial year from request.
        
        Args:
            request: Django request object with financial_context
            
        Returns:
            Filtered queryset
        """
        if not hasattr(request, 'financial_context') or not request.financial_context:
            # No context available, return empty queryset
            return self.none()
        
        context = request.financial_context
        
        if not context.has_context():
            return self.none()
        
        # Filter by company and financial year
        filters = {}
        
        # Check if model has compid field
        if hasattr(self.model, 'compid'):
            filters['compid'] = context.company_id
        
        # Check if model has finyearid field
        if hasattr(self.model, 'finyearid'):
            filters['finyearid'] = context.finyear_id
        
        if filters:
            return self.filter(**filters)
        
        # Model doesn't have context fields, return unfiltered
        return self
    
    def for_company(self, company_id):
        """
        Filter by specific company.
        
        Args:
            company_id: Company ID
            
        Returns:
            Filtered queryset
        """
        if hasattr(self.model, 'compid'):
            return self.filter(compid=company_id)
        return self
    
    def for_finyear(self, finyear_id):
        """
        Filter by specific financial year.
        
        Args:
            finyear_id: Financial Year ID
            
        Returns:
            Filtered queryset
        """
        if hasattr(self.model, 'finyearid'):
            return self.filter(finyearid=finyear_id)
        return self
    
    def for_context(self, company_id, finyear_id):
        """
        Filter by specific company and financial year.
        
        Args:
            company_id: Company ID
            finyear_id: Financial Year ID
            
        Returns:
            Filtered queryset
        """
        return self.for_company(company_id).for_finyear(finyear_id)
    
    def active_only(self):
        """
        Filter to active records only (flag=1).
        
        Returns:
            Filtered queryset
        """
        if hasattr(self.model, 'flag'):
            return self.filter(flag=1)
        return self
    
    def inactive_only(self):
        """
        Filter to inactive records only (flag=0).
        
        Returns:
            Filtered queryset
        """
        if hasattr(self.model, 'flag'):
            return self.filter(flag=0)
        return self


class FinancialYearManager(models.Manager):
    """
    Manager that provides FinancialYearQuerySet.
    
    Usage in model:
        class MyModel(models.Model):
            compid = models.IntegerField()
            finyearid = models.IntegerField()
            
            objects = FinancialYearManager()
            
            class Meta:
                managed = False
                db_table = 'tblMyModel'
    
    Usage in view:
        # Automatic filtering
        records = MyModel.objects.for_active_context(request)
        
        # Manual filtering
        records = MyModel.objects.for_company(1).for_finyear(5)
        
        # Active records only
        records = MyModel.objects.active_only()
    """
    
    def get_queryset(self):
        """Return FinancialYearQuerySet"""
        return FinancialYearQuerySet(self.model, using=self._db)
    
    def for_active_context(self, request):
        """Filter by active context from request"""
        return self.get_queryset().for_active_context(request)
    
    def for_company(self, company_id):
        """Filter by company"""
        return self.get_queryset().for_company(company_id)
    
    def for_finyear(self, finyear_id):
        """Filter by financial year"""
        return self.get_queryset().for_finyear(finyear_id)
    
    def for_context(self, company_id, finyear_id):
        """Filter by company and financial year"""
        return self.get_queryset().for_context(company_id, finyear_id)
    
    def active_only(self):
        """Filter to active records"""
        return self.get_queryset().active_only()
    
    def inactive_only(self):
        """Filter to inactive records"""
        return self.get_queryset().inactive_only()


class CompanyScopedManager(models.Manager):
    """
    Manager that ONLY returns records for active company.
    
    This is more restrictive than FinancialYearManager - it prevents
    cross-company data leakage by default.
    
    Usage:
        class MyModel(models.Model):
            compid = models.IntegerField()
            
            objects = CompanyScopedManager()
            all_objects = models.Manager()  # Unfiltered access
    """
    
    def get_queryset(self):
        """Return queryset filtered by active company"""
        # This requires middleware to set thread-local context
        # For now, return unfiltered - will be enhanced in Phase 3
        return super().get_queryset()


# Convenience function for adding to existing models
def add_context_manager(model_class):
    """
    Add FinancialYearManager to an existing model class.
    
    Usage:
        from core.managers import add_context_manager
        from myapp.models import MyModel
        
        add_context_manager(MyModel)
        
        # Now can use:
        MyModel.objects.for_active_context(request)
    
    Args:
        model_class: Model class to enhance
    """
    if not hasattr(model_class, 'objects') or type(model_class.objects) == models.Manager:
        model_class.add_to_class('objects', FinancialYearManager())
    
    return model_class
