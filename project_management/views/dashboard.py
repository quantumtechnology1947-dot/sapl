"""
Project Management Dashboard View

Single dashboard view showing statistics for all project management modules.
Extracted from monolithic views.py.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models import (
    TblonsiteattendanceMaster,
    TblpmManpowerplanning,
    TblpmMaterialcreditnoteMaster,
    TblpmProjectplanningMaster,
)


class ProjectManagementDashboardView(LoginRequiredMixin, TemplateView):
    """Project Management Dashboard with module statistics"""
    template_name = 'project_management/dashboard.html'
    login_url = '/login/'

    def get_compid(self):
        return self.request.session.get('company_id', 1)

    def get_finyearid(self):
        return self.request.session.get('financial_year_id', 1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # ManPower Planning stats
        manpower = TblpmManpowerplanning.objects.filter(compid=compid, finyearid=finyearid)
        context['manpower_count'] = manpower.count()
        context['recent_manpower'] = manpower.order_by('-id')[:5]

        # Material Credit Notes stats
        mcn = TblpmMaterialcreditnoteMaster.objects.filter(compid=compid, finyearid=finyearid)
        context['mcn_count'] = mcn.count()
        context['recent_mcn'] = mcn.order_by('-id')[:5]

        # Project Planning stats
        projects = TblpmProjectplanningMaster.objects.filter(compid=compid, finyearid=finyearid)
        context['project_count'] = projects.count()
        context['recent_projects'] = projects.order_by('-id')[:5]

        # OnSite Attendance stats
        attendance = TblonsiteattendanceMaster.objects.filter(compid=compid, finyearid=finyearid)
        context['attendance_count'] = attendance.count()

        # Add session context
        context['compid'] = compid
        context['finyearid'] = finyearid

        return context
