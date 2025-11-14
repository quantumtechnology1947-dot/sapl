"""
Inventory Dashboard Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse

# Import core mixins instead of inventory-specific mixins
from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
    LoginRequiredMixin,
    CompanyFinancialYearMixin,
    HTMXResponseMixin,
    QueryOptimizationMixin,
)

from ..models import (
    TblGatepass,
    TblinvMaterialrequisitionMaster, TblinvMaterialrequisitionDetails,
    TblinvMaterialissueMaster, TblinvMaterialissueDetails,
    TblinvMaterialreturnMaster, TblinvMaterialreturnDetails,
    TblinvInwardMaster, TblinvInwardDetails,
    TblinvMaterialreceivedMaster, TblinvMaterialreceivedDetails,
    TblinvMaterialservicenoteMaster, TblinvMaterialservicenoteDetails,
    TblinvSupplierChallanMaster, TblinvSupplierChallanDetails,
    TblinvCustomerChallanMaster, TblinvCustomerChallanDetails,
    TblinvWisMaster, TblinvWisDetails,
    TblvehProcessMaster,
    TblinvAutowisTimeschedule,
)
from .. import forms
from ..forms import (
    MRSMasterForm,
    MINMasterForm,
    MRNMasterForm,
    VehicleProcessMasterForm,
    VehicleMasterForm,
    AutoWISTimeScheduleForm,
    StockLedgerFilterForm,
)
from ..services import (
    MaterialRequisitionService,
    MaterialIssueService,
    MaterialReturnService,
    DashboardService,
)


class InventoryDashboardView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Inventory Dashboard View
    Displays key metrics and recent transactions.
    Optimized: Uses core mixins instead of InventoryBaseMixin.
    Requirements: 3.1, 4.1, 4.2
    """
    template_name = 'inventory/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get dashboard metrics
        context['metrics'] = DashboardService.get_dashboard_metrics(compid, finyearid)
        
        # Get recent MRS (last 5) - optimized query
        context['recent_mrs'] = TblinvMaterialrequisitionMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-id')[:5]
        
        # Get recent MIN (last 5) - optimized query
        context['recent_min'] = TblinvMaterialissueMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-id')[:5]
        
        return context



