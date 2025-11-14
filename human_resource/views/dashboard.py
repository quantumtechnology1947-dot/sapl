"""
Human Resource Dashboard View
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models import (
    Businessgroup, TblhrDepartments, TblhrDesignation, TblhrGrade
)


class HRDashboardView(LoginRequiredMixin, TemplateView):
    """
    HR module dashboard.
    Converted from: aspnet/Module/HR/Masters/Dashboard.aspx
    """
    template_name = 'human_resource/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Human Resource Management'
        context['department_count'] = TblhrDepartments.objects.count()
        context['designation_count'] = TblhrDesignation.objects.count()
        context['business_group_count'] = Businessgroup.objects.count()
        context['grade_count'] = TblhrGrade.objects.count()
        return context
