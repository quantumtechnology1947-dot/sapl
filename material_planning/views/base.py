"""
Base Mixin for Material Planning Views

Provides common functionality for all Material Planning views.
"""

from django.contrib.auth.mixins import LoginRequiredMixin


class MaterialPlanningBaseMixin(LoginRequiredMixin):
    """Base mixin for all Material Planning views"""
    login_url = '/login/'

    def get_compid(self):
        """Get company ID from session"""
        return self.request.session.get('company_id', 1)

    def get_finyearid(self):
        """Get financial year ID from session"""
        return self.request.session.get('financial_year_id', 1)

    def get_sessionid(self):
        """Get session ID for user isolation"""
        return self.request.session.session_key or 'default'

    def get_context_data(self, **kwargs):
        """Add company and financial year to context"""
        context = super().get_context_data(**kwargs)
        context['compid'] = self.get_compid()
        context['finyearid'] = self.get_finyearid()
        return context
