"""
Project Planning and Status Views

Project file management, status tracking, and download functionality.
Uses ProjectService for business logic.
Extracted from monolithic views.py.
"""

from datetime import datetime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.db.models import Q

from ..models import TblpmProjectplanningMaster, TblpmProjectstatus
from ..services import ProjectService


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


# ==============================================================================
# Project Planning Views (with File Upload)
# ==============================================================================

class ProjectPlanningListView(ProjectManagementBaseMixin, ListView):
    """Project Planning List"""
    model = TblpmProjectplanningMaster
    template_name = 'project_management/project/list.html'
    context_object_name = 'projects'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            compid=self.get_compid(),
            finyearid=self.get_finyearid()
        ).order_by('-id')

        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(Q(wono__icontains=search) | Q(filename__icontains=search))

        return queryset


class ProjectPlanningListViewUniform(ProjectManagementBaseMixin, TemplateView):
    """
    Project Planning - Uniform view with Work Order list and file management
    Based on ASP.NET ProjectPlanning.aspx pattern
    Uses ProjectService for file operations
    """
    template_name = 'project_management/project/list_uniform.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from sales_distribution.models import SdCustWorkorderMaster, TblsdWoCategory

        compid = self.get_compid()

        # Search parameters
        search_wono = self.request.GET.get('search_wono', '')
        search_category = self.request.GET.get('search_category', '')
        selected_wono = self.request.GET.get('wono', '')

        # Get WO Categories
        context['wo_categories'] = TblsdWoCategory.objects.filter(compid=compid).order_by('symbol')

        # Get Work Orders
        work_orders_query = SdCustWorkorderMaster.objects.filter(
            compid=compid, closeopen=0
        ).order_by('wono')

        # Apply filters
        if search_wono:
            work_orders_query = work_orders_query.filter(wono__icontains=search_wono)
        if search_category:
            work_orders_query = work_orders_query.filter(cid=search_category)

        # Enrich work orders using service
        context['work_orders'] = ProjectService.enrich_work_orders_with_planning_files(
            work_orders_query[:100], compid
        )
        context['selected_wono'] = selected_wono

        # Get planning files if WO is selected
        if selected_wono:
            context['planning_files'] = ProjectService.get_planning_files_for_wo(compid, selected_wono)
            context['show_files_panel'] = True
        else:
            context['show_files_panel'] = False

        return context

    def post(self, request, *args, **kwargs):
        """Handle file upload and delete using service"""
        from django.http import QueryDict

        redirect_params = QueryDict(mutable=True)

        if 'upload_file' in request.POST:
            wono = request.POST.get('wono')
            uploaded_file = request.FILES.get('file')

            if wono and uploaded_file:
                # Create planning file using service
                ProjectService.create_planning_file(
                    self.get_compid(), self.get_finyearid(),
                    self.get_sessionid(), wono, uploaded_file
                )
                messages.success(request, f'File "{uploaded_file.name}" uploaded successfully for WO: {wono}')

                # Preserve parameters
                redirect_params['wono'] = wono
                if request.POST.get('search_wono'):
                    redirect_params['search_wono'] = request.POST.get('search_wono')
                if request.POST.get('search_category'):
                    redirect_params['search_category'] = request.POST.get('search_category')
            else:
                messages.error(request, 'Please select a file to upload')

            redirect_url = f"{request.path}?{redirect_params.urlencode()}" if redirect_params else request.path
            return HttpResponseRedirect(redirect_url)

        elif 'delete_file' in request.POST:
            file_id = request.POST.get('file_id')
            wono = request.POST.get('wono')

            if file_id:
                # Delete file using service
                if ProjectService.delete_planning_file(file_id, self.get_compid()):
                    messages.success(request, 'File deleted successfully')
                else:
                    messages.error(request, 'File not found')

            # Preserve parameters
            if wono:
                redirect_params['wono'] = wono
            if request.POST.get('search_wono'):
                redirect_params['search_wono'] = request.POST.get('search_wono')
            if request.POST.get('search_category'):
                redirect_params['search_category'] = request.POST.get('search_category')

            redirect_url = f"{request.path}?{redirect_params.urlencode()}" if redirect_params else request.path
            return HttpResponseRedirect(redirect_url)

        return HttpResponseRedirect(request.path)


class ProjectPlanningCreateView(ProjectManagementBaseMixin, CreateView):
    """Create Project Planning with File Upload"""
    model = TblpmProjectplanningMaster
    fields = ['wono']
    template_name = 'project_management/project/form.html'
    success_url = reverse_lazy('project_management:project-list')

    def form_valid(self, form):
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.sessionid = self.get_sessionid()
        form.instance.sysdate = datetime.now().strftime('%Y-%m-%d')
        form.instance.systime = datetime.now().strftime('%H:%M:%S')

        # Handle file upload
        uploaded_file = self.request.FILES.get('filedata')
        if uploaded_file:
            form.instance.filename = uploaded_file.name
            form.instance.filesize = uploaded_file.size
            form.instance.contenttype = uploaded_file.content_type
            form.instance.filedata = uploaded_file.read()

        response = super().form_valid(form)
        messages.success(self.request, f'Project Plan created for WO: {self.object.wono}!')
        return response


class ProjectPlanningDetailView(ProjectManagementBaseMixin, DetailView):
    """View Project Planning Details"""
    model = TblpmProjectplanningMaster
    template_name = 'project_management/project/detail.html'
    context_object_name = 'project'
    pk_url_kwarg = 'pk'


class ProjectPlanningUpdateView(ProjectManagementBaseMixin, UpdateView):
    """Update Project Planning"""
    model = TblpmProjectplanningMaster
    fields = ['wono']
    template_name = 'project_management/project/form.html'
    success_url = reverse_lazy('project_management:project-list')
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        # Handle file upload (if new file)
        uploaded_file = self.request.FILES.get('filedata')
        if uploaded_file:
            form.instance.filename = uploaded_file.name
            form.instance.filesize = uploaded_file.size
            form.instance.contenttype = uploaded_file.content_type
            form.instance.filedata = uploaded_file.read()

        response = super().form_valid(form)
        messages.success(self.request, f'Project Plan updated!')
        return response


class ProjectPlanningDeleteView(ProjectManagementBaseMixin, DeleteView):
    """Delete Project Planning"""
    model = TblpmProjectplanningMaster
    success_url = reverse_lazy('project_management:project-list')
    pk_url_kwarg = 'pk'


class ProjectPlanningDownloadFileView(ProjectManagementBaseMixin, DetailView):
    """Download Project Planning File"""
    model = TblpmProjectplanningMaster
    pk_url_kwarg = 'pk'

    def render_to_response(self, context, **response_kwargs):
        project = self.object
        if not project.filedata:
            messages.error(self.request, 'No file attached to this project.')
            return HttpResponse(status=404)

        response = HttpResponse(
            bytes(project.filedata),
            content_type=project.contenttype or 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{project.filename}"'
        return response


# ==============================================================================
# Project Status Views
# ==============================================================================

class ProjectStatusListView(ProjectManagementBaseMixin, ListView):
    """Project Status List"""
    model = TblpmProjectstatus
    template_name = 'project_management/status/list.html'
    context_object_name = 'statuses'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')

        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(Q(wono__icontains=search) | Q(activities__icontains=search))

        return queryset


class ProjectStatusCreateView(ProjectManagementBaseMixin, CreateView):
    """Create Project Status"""
    model = TblpmProjectstatus
    fields = ['srno', 'wono', 'activities']
    template_name = 'project_management/status/form.html'
    success_url = reverse_lazy('project_management:status-list')


class ProjectStatusDetailView(ProjectManagementBaseMixin, DetailView):
    """View Project Status Details"""
    model = TblpmProjectstatus
    template_name = 'project_management/status/detail.html'
    context_object_name = 'status'
    pk_url_kwarg = 'pk'


class ProjectStatusUpdateView(ProjectManagementBaseMixin, UpdateView):
    """Update Project Status"""
    model = TblpmProjectstatus
    fields = ['srno', 'wono', 'activities']
    template_name = 'project_management/status/form.html'
    success_url = reverse_lazy('project_management:status-list')
    pk_url_kwarg = 'pk'


class ProjectStatusDeleteView(ProjectManagementBaseMixin, DeleteView):
    """Delete Project Status"""
    model = TblpmProjectstatus
    success_url = reverse_lazy('project_management:status-list')
    pk_url_kwarg = 'pk'
