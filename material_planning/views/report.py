"""
Report Views
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




class PlanningReportView(MaterialPlanningBaseMixin, ListView):
    """Planning Report - List all plans"""
    model = TblmpMaterialMaster
    template_name = 'material_planning/reports/planning_report.html'
    context_object_name = 'plans'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            compid=self.get_compid(),
            finyearid=self.get_finyearid()
        ).order_by('-id')

        # Add filters
        wono = self.request.GET.get('wono', '')
        if wono:
            queryset = queryset.filter(wono__icontains=wono)
        
        return queryset