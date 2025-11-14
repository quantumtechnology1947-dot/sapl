"""
Goods Service Note (GSN) Views
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
from material_management.models import POMaster, TblmmSupplierMaster
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


class GSNListView(BaseListViewMixin, ListView):
    """
    Goods Service Note List View
    Displays all GSN with search and filter

    Converted from: aspnet/Module/Inventory/Transactions/GoodsServiceNote_SN_Edit.aspx
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    """
    model = TblinvMaterialservicenoteMaster
    template_name = 'inventory/transactions/gsn_list.html'
    context_object_name = 'gsn_list'
    paginate_by = 20
    search_fields = ['gsnno', 'taxinvoiceno']
    ordering = ['-id']

    def get_queryset(self):
        """
        Override to add related data from GIN, PO, and Supplier
        Matches ASP.NET Edit view display columns
        """
        # Get base queryset with company/year filtering and search from BaseListViewMixin
        queryset = super().get_queryset()

        # Build enriched queryset with all related data
        # We need to manually join since models don't have ForeignKey relationships
        gsn_list = []

        for gsn in queryset:
            # Get GIN data
            gin = None
            if gsn.ginid:
                try:
                    gin = TblinvInwardMaster.objects.get(id=gsn.ginid)
                except TblinvInwardMaster.DoesNotExist:
                    pass

            # Get PO and Supplier data
            po = None
            supplier = None
            if gin and gin.pomid:
                try:
                    po = POMaster.objects.get(po_id=gin.pomid)
                    if po.supplier_id:
                        try:
                            # supplier_id in PO is a string, supid in Supplier is AutoField
                            supplier = TblmmSupplierMaster.objects.get(supplierid=po.supplier_id)
                        except TblmmSupplierMaster.DoesNotExist:
                            pass
                except POMaster.DoesNotExist:
                    pass

            # Attach related data as attributes
            gsn.gin_data = gin
            gsn.po_data = po
            gsn.supplier_data = supplier

            gsn_list.append(gsn)

        return gsn_list



class GSNCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """
    Goods Service Note Create View
    Create new GSN for service receipts
    """
    model = TblinvMaterialservicenoteMaster
    form_class = forms.GSNMasterForm
    template_name = 'inventory/transactions/gsn_form.html'
    success_url = reverse_lazy('inventory:gsn-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.get_compid()
        kwargs['finyearid'] = self.get_finyearid()
        kwargs['sessionid'] = self.get_sessionid()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Auto-generate GSN number
        from ..services import GoodsServiceService
        context['auto_gsn_number'] = GoodsServiceService.generate_gsn_number(
            self.get_compid(),
            self.get_finyearid()
        )
        
        return context
    
    def form_valid(self, form):
        # Set auto-generated GSN number
        from ..services import GoodsServiceService
        form.instance.gsnno = GoodsServiceService.generate_gsn_number(
            self.get_compid(),
            self.get_finyearid()
        )
        
        response = super().form_valid(form)
        messages.success(self.request, f'GSN {form.instance.gsnno} created successfully!')
        return response



class GSNDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    Goods Service Note Detail View
    View GSN details
    """
    model = TblinvMaterialservicenoteMaster
    template_name = 'inventory/transactions/gsn_detail.html'
    context_object_name = 'gsn'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get service details from form fields (if stored separately)
        # For now, display what's in the model
        
        return context



class GSNDeleteView(LoginRequiredMixin, CompanyFinancialYearMixin, DeleteView):
    """
    Goods Service Note Delete View
    Delete GSN (no stock reversal needed for services)
    """
    model = TblinvMaterialservicenoteMaster
    template_name = 'inventory/transactions/gsn_confirm_delete.html'
    success_url = reverse_lazy('inventory:gsn-list')
    context_object_name = 'gsn'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        messages.success(request, f'GSN {self.object.gsnno} deleted successfully!')
        return super().delete(request, *args, **kwargs)



class GSNPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    Goods Service Note Print View
    Print-friendly GSN document
    """
    model = TblinvMaterialservicenoteMaster
    template_name = 'inventory/transactions/gsn_print.html'
    context_object_name = 'gsn'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add any additional context for printing
        
        return context



# ============================================================================
# SUPPLIER CHALLAN VIEWS
# ============================================================================


