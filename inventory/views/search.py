"""
Inventory Module Views
Modernized with core mixins and query optimization.
Requirements: 3.1, 3.4, 5.5, 13.1, 13.2, 13.3
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
    MRSMasterForm,  # MRSDetailFormSet,  # Commented out - formsets don't work with managed=False models
    MINMasterForm,  # MINDetailFormSet,  # Commented out
    MRNMasterForm,  # MRNDetailFormSet,  # Commented out
    VehicleProcessMasterForm,
    VehicleMasterForm,
    AutoWISTimeScheduleForm,
    StockLedgerFilterForm,
)
# NOTE: All formsets have been commented out in forms.py due to foreign key issues with managed=False models
from ..services import (
    MaterialRequisitionService,
    MaterialIssueService,
    MaterialReturnService,
    DashboardService,
)




class GlobalSearchView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Global Search View
    
    Search across all inventory transactions.
    
    Converted from: aspnet/Module/Inventory/Reports/Search.aspx
    Requirements: 10.1, 10.2, 10.3
    """
    template_name = 'inventory/search/global_search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get search query
        query = self.request.GET.get('q', '').strip()
        context['query'] = query
        
        # Perform search if query provided
        if query and len(query) >= 3:  # Minimum 3 characters
            try:
                from ..services import SearchService
                
                results = SearchService.global_search(query, compid, finyearid)
                context['results'] = results
                context['total_results'] = len(results)
                
                # Group results by transaction type
                grouped_results = {}
                for result in results:
                    trans_type = result['type']
                    if trans_type not in grouped_results:
                        grouped_results[trans_type] = []
                    grouped_results[trans_type].append(result)
                
                context['grouped_results'] = grouped_results
                
            except Exception as e:
                messages.error(self.request, f'Search error: {str(e)}')
        elif query and len(query) < 3:
            messages.warning(self.request, 'Please enter at least 3 characters to search.')
        
        return context




class AdvancedSearchView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Advanced Search View
    
    Search with multiple criteria across inventory transactions.
    
    Converted from: aspnet/Module/Inventory/Reports/Search_Details.aspx
    Requirements: 10.4, 10.5, 10.6, 10.7, 10.8
    """
    template_name = 'inventory/search/advanced_search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get filter parameters
        transaction_type = self.request.GET.get('transaction_type', '')
        item_id = self.request.GET.get('item_id', '')
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        supplier_id = self.request.GET.get('supplier_id', '')
        
        context['transaction_type'] = transaction_type
        context['item_id'] = item_id
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['supplier_id'] = supplier_id
        
        # Get dropdown data
        from sys_admin.models import TblitemMaster, TblsupplierMaster
        context['items'] = TblitemMaster.objects.filter(compid=compid).order_by('itemname')[:100]
        context['suppliers'] = TblsupplierMaster.objects.filter(compid=compid).order_by('suppliername')[:100]
        
        # Perform search if any criteria provided
        if any([transaction_type, item_id, start_date, end_date, supplier_id]):
            try:
                from ..services import SearchService
                from datetime import datetime
                
                # Build criteria dict
                criteria = {}
                if transaction_type:
                    criteria['transaction_type'] = transaction_type
                if item_id:
                    criteria['item_id'] = int(item_id)
                if start_date:
                    criteria['start_date'] = datetime.strptime(start_date, '%Y-%m-%d').date()
                if end_date:
                    criteria['end_date'] = datetime.strptime(end_date, '%Y-%m-%d').date()
                if supplier_id:
                    criteria['supplier_id'] = int(supplier_id)
                
                results = SearchService.advanced_search(criteria, compid, finyearid)
                context['results'] = results
                context['total_results'] = len(results)
                
                # Group results by transaction type
                grouped_results = {}
                for result in results:
                    trans_type = result['type']
                    if trans_type not in grouped_results:
                        grouped_results[trans_type] = []
                    grouped_results[trans_type].append(result)
                
                context['grouped_results'] = grouped_results
                
            except ValueError as e:
                messages.error(self.request, 'Invalid date format.')
            except Exception as e:
                messages.error(self.request, f'Search error: {str(e)}')
        
        return context



# ============================================================================
# CHALLAN VIEWS
# ============================================================================



