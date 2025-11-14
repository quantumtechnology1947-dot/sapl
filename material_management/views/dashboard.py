"""
Material Management Dashboard View

Converted from: aspnet/Module/MaterialManagement/Dashboard.aspx
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from core.mixins import CompanyFinancialYearMixin
from ..models import BusinessNature, BusinessType, ServiceCoverage, Buyer, Supplier


class MaterialManagementBaseMixin(LoginRequiredMixin, CompanyFinancialYearMixin):
    """
    Base mixin for all Material Management views
    Inherits from CompanyFinancialYearMixin for company/financial year context
    """
    login_url = '/login/'


class MaterialManagementDashboardView(MaterialManagementBaseMixin, TemplateView):
    """
    Material Management Dashboard
    Displays key metrics and quick links

    Converted from: aspnet/Module/MaterialManagement/Dashboard.aspx
    """
    template_name = 'material_management/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()

        # Get counts for dashboard metrics
        context['business_nature_count'] = BusinessNature.objects.count()
        context['business_type_count'] = BusinessType.objects.count()
        context['service_coverage_count'] = ServiceCoverage.objects.count()
        context['buyer_count'] = Buyer.objects.count()
        context['supplier_count'] = Supplier.objects.count()

        return context
