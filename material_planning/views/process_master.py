"""
Process Master Views
"""

from datetime import datetime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q

from .base import MaterialPlanningBaseMixin
from material_planning.models import (
    TblmpMaterialMaster, TblmpMaterialDetail, TblmpMaterialRawmaterial,
    TblmpMaterialProcess, TblmpMaterialFinish, TblplnProcessMaster,
    TblmpMaterialDetailTemp, TblmpMaterialRawmaterialTemp,
    TblmpMaterialProcessTemp, TblmpMaterialFinishTemp,
)
from material_planning.services import BOMService, PlanningService, PRService
from design.models import TbldgItemMaster
from sales_distribution.models import SdCustWorkorderMaster
from sys_admin.models import TblfinancialMaster
from material_management.models import PRMaster, PRDetails, Supplier




class ProcessMasterListView(MaterialPlanningBaseMixin, ListView):
    """List all Process Masters"""
    model = TblplnProcessMaster
    template_name = 'material_planning/masters/process_list.html'
    context_object_name = 'processes'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('processname')
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(processname__icontains=search) | Q(symbol__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add debug info
        context['debug_info'] = {
            'total_processes': TblplnProcessMaster.objects.count(),
            'queryset_count': self.get_queryset().count(),
        }
        return context

class ProcessMasterCreateView(MaterialPlanningBaseMixin, CreateView):
    """Create new Process Master"""
    model = TblplnProcessMaster
    form_class = None  # Will be set in get_form_class()
    template_name = 'material_planning/masters/process_form.html'
    success_url = reverse_lazy('material_planning:process-list')

    def get_form_class(self):
        from .forms import ProcessMasterForm
        return ProcessMasterForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Process "{self.object.processname}" created successfully!')
        
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'material_planning/masters/partials/process_row.html', 
                         {'process': self.object})
        return response

class ProcessMasterUpdateView(MaterialPlanningBaseMixin, UpdateView):
    """Update Process Master"""
    model = TblplnProcessMaster
    form_class = None  # Will be set in get_form_class()
    template_name = 'material_planning/masters/process_form.html'
    success_url = reverse_lazy('material_planning:process-list')
    pk_url_kwarg = 'id'

    def get_form_class(self):
        from .forms import ProcessMasterForm
        return ProcessMasterForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Process "{self.object.processname}" updated successfully!')
        
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'material_planning/masters/partials/process_row.html', 
                         {'process': self.object})
        return response

class ProcessMasterDeleteView(MaterialPlanningBaseMixin, DeleteView):
    """Delete Process Master"""
    model = TblplnProcessMaster
    success_url = reverse_lazy('material_planning:process-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        process_name = self.object.processname
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Process "{process_name}" deleted successfully!')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response

class ProcessMasterRowView(MaterialPlanningBaseMixin, DetailView):
    """Return single process row (for cancel operation)"""
    model = TblplnProcessMaster
    template_name = 'material_planning/masters/partials/process_row.html'
    context_object_name = 'process'
    pk_url_kwarg = 'id'


# ============================================================================
# PLANNING SEARCH & CREATE VIEWS
# ============================================================================