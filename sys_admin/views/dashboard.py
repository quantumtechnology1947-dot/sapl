"""
SysAdmin Dashboard View
"""

from django.views.generic import TemplateView
from core.mixins import LoginRequiredMixin
from ..models import Tblcountry, Tblstate, Tblcity


class SysAdminDashboardView(LoginRequiredMixin, TemplateView):
    """
    SysAdmin module dashboard.
    Converted from: aspnet/Module/SysAdmin/Dashboard.aspx
    """
    template_name = 'sys_admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'System Administration'
        context['country_count'] = Tblcountry.objects.count()
        context['state_count'] = Tblstate.objects.count()
        context['city_count'] = Tblcity.objects.count()
        return context
