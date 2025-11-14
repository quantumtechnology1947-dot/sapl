"""
ManPower Planning Views

CRUD operations and amendment tracking for manpower resource planning.
Uses ManpowerService for business logic.
Extracted from monolithic views.py.
"""

from datetime import datetime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from ..models import TblpmManpowerplanning, TblpmManpowerplanningDetails, TblpmManpowerplanningAmd
from ..services import ManpowerService


class ProjectManagementBaseMixin(LoginRequiredMixin):
    """Base mixin for all Project Management views"""
    login_url = '/login/'

    def get_compid(self):
        return self.request.session.get('company_id', 1)

    def get_finyearid(self):
        return self.request.session.get('financial_year_id', 1)

    def get_sessionid(self):
        return self.request.session.session_key or 'default'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compid'] = self.get_compid()
        context['finyearid'] = self.get_finyearid()
        return context


class ManPowerPlanningListViewUniform(ProjectManagementBaseMixin, ListView):
    """
    ManPower Planning List View - Uniform display with comprehensive search filters
    Based on ASP.NET ManPowerPlanning_Edit.aspx pattern
    Uses ManpowerService for filtering and enrichment
    """
    model = TblpmManpowerplanning
    template_name = 'project_management/manpower/list.html'
    context_object_name = 'plans'
    paginate_by = 20

    def get_queryset(self):
        compid = self.get_compid()

        # Base query - show all records for the company regardless of financial year
        queryset = TblpmManpowerplanning.objects.filter(
            compid=compid
        ).order_by('-date', 'empid')

        # Apply search filters using service
        filters = {
            'search_wono': self.request.GET.get('search_wono', ''),
            'search_bg': self.request.GET.get('search_bg', ''),
            'search_empid': self.request.GET.get('search_empid', ''),
            'search_types': self.request.GET.get('search_types', ''),
            'from_date': self.request.GET.get('from_date', ''),
            'to_date': self.request.GET.get('to_date', ''),
        }

        queryset = ManpowerService.filter_plans(queryset, filters)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup

        compid = self.get_compid()

        # Get BG Groups for dropdown
        context['bg_groups'] = Businessgroup.objects.all().order_by('symbol')

        # Enrich planning data with employee names and BG symbols using service
        context['plans'] = ManpowerService.enrich_plan_with_employee_info(
            context['plans'], compid
        )

        return context


class ManPowerPlanningCreateView(ProjectManagementBaseMixin, CreateView):
    """Create ManPower Planning"""
    model = TblpmManpowerplanning
    fields = ['empid', 'date', 'wono', 'dept', 'types', 'amendmentno']
    template_name = 'project_management/manpower/form.html'
    success_url = reverse_lazy('project_management:manpower-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup
        context['bg_groups'] = Businessgroup.objects.all().order_by('symbol')
        return context

    def form_valid(self, form):
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.sessionid = self.get_sessionid()
        form.instance.sysdate = datetime.now().strftime('%Y-%m-%d')
        form.instance.systime = datetime.now().strftime('%H:%M:%S')
        response = super().form_valid(form)
        messages.success(self.request, f'ManPower Plan created successfully!')
        return response


class ManPowerPlanningDetailView(ProjectManagementBaseMixin, DetailView):
    """View ManPower Planning Details with amendment history"""
    model = TblpmManpowerplanning
    template_name = 'project_management/manpower/detail.html'
    context_object_name = 'plan'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan = self.object

        # Get details and amendments using service
        context['details'] = ManpowerService.get_plan_details(plan)
        context['amendments'] = ManpowerService.get_plan_amendments(plan)

        return context


class ManPowerPlanningUpdateView(ProjectManagementBaseMixin, UpdateView):
    """Update ManPower Planning with automatic amendment tracking"""
    model = TblpmManpowerplanning
    fields = ['empid', 'date', 'wono', 'dept', 'types', 'amendmentno']
    template_name = 'project_management/manpower/form.html'
    success_url = reverse_lazy('project_management:manpower-list')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup
        context['bg_groups'] = Businessgroup.objects.all().order_by('symbol')
        return context

    def form_valid(self, form):
        # Save old data to amendment table using service
        old_plan = TblpmManpowerplanning.objects.get(pk=self.object.pk)
        ManpowerService.create_amendment(old_plan)

        # Increment amendment number using service
        form.instance.amendmentno = ManpowerService.get_next_amendment_number(old_plan)
        form.instance.sysdate = datetime.now().strftime('%Y-%m-%d')
        form.instance.systime = datetime.now().strftime('%H:%M:%S')

        response = super().form_valid(form)
        messages.success(self.request, f'ManPower Plan updated! Amendment #{form.instance.amendmentno}')
        return response


class ManPowerPlanningDeleteView(ProjectManagementBaseMixin, DeleteView):
    """Delete ManPower Planning"""
    model = TblpmManpowerplanning
    success_url = reverse_lazy('project_management:manpower-list')
    pk_url_kwarg = 'pk'
