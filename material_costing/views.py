"""
Material Costing Module Views

Converted from: aspnet/Module/MaterialCosting/
Manages material live costs with effective dates.
"""

from datetime import datetime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import TbldgMaterial, TblmlcLivecost


class MaterialCostingBaseMixin(LoginRequiredMixin):
    """Base mixin for all Material Costing views"""
    login_url = '/login/'

    def get_compid(self):
        return self.request.session.get('company_id', 1)

    def get_finyearid(self):
        return self.request.session.get('financial_year_id', 1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compid'] = self.get_compid()
        context['finyearid'] = self.get_finyearid()
        return context


class MaterialCostingDashboardView(MaterialCostingBaseMixin, TemplateView):
    """
    Material Costing Dashboard
    Converted from: Dashboard.aspx
    """
    template_name = 'material_costing/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics
        context['total_materials'] = TbldgMaterial.objects.count()
        context['total_costs'] = TblmlcLivecost.objects.count()
        context['recent_costs'] = TblmlcLivecost.objects.select_related('material').order_by('-id')[:10]

        return context


class MaterialCategoryView(MaterialCostingBaseMixin, ListView):
    """
    Material Category/Master List
    Converted from: Masters/Material_Category.aspx
    """
    model = TbldgMaterial
    template_name = 'material_costing/masters/material_category.html'
    context_object_name = 'materials'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(material__icontains=search)
        return queryset.order_by('material')


class LiveCostListView(MaterialCostingBaseMixin, ListView):
    """
    Live Cost List
    Converted from: Masters/Material_New.aspx (includes list view)
    """
    model = TblmlcLivecost
    template_name = 'material_costing/masters/live_cost_list.html'
    context_object_name = 'costs'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('material').order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materials'] = TbldgMaterial.objects.all().order_by('material')
        return context


class LiveCostCreateView(MaterialCostingBaseMixin, CreateView):
    """
    Create Live Cost Entry
    Converted from: Masters/Material_New.aspx
    """
    model = TblmlcLivecost
    fields = ['material', 'live_cost', 'eff_date']
    template_name = 'material_costing/masters/live_cost_form.html'
    success_url = reverse_lazy('material_costing:live-cost-list')

    def form_valid(self, form):
        form.instance.comp_id = self.get_compid()
        form.instance.fin_year_id = self.get_finyearid()
        form.instance.sys_date = datetime.now().strftime('%Y-%m-%d')
        form.instance.sys_time = datetime.now().strftime('%H:%M:%S')
        
        response = super().form_valid(form)
        messages.success(self.request, f'Live cost for {self.object.material.material} added successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materials'] = TbldgMaterial.objects.all().order_by('material')
        return context


class LiveCostUpdateView(MaterialCostingBaseMixin, UpdateView):
    """
    Update Live Cost Entry
    Converted from: Masters/Material_Edit.aspx
    """
    model = TblmlcLivecost
    fields = ['material', 'live_cost', 'eff_date']
    template_name = 'material_costing/masters/live_cost_form.html'
    success_url = reverse_lazy('material_costing:live-cost-list')
    pk_url_kwarg = 'cost_id'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Live cost for {self.object.material.material} updated successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materials'] = TbldgMaterial.objects.all().order_by('material')
        context['is_edit'] = True
        return context


class LiveCostDeleteView(MaterialCostingBaseMixin, DeleteView):
    """
    Delete Live Cost Entry
    Converted from: Masters/Material_Delete.aspx
    """
    model = TblmlcLivecost
    success_url = reverse_lazy('material_costing:live-cost-list')
    pk_url_kwarg = 'cost_id'
    template_name = 'material_costing/masters/live_cost_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        cost = self.get_object()
        material_name = cost.material.material
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Live cost for {material_name} deleted successfully!')
        return response
