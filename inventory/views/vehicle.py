"""
Vehicle Management Views
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


class VehicleListView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    Vehicle List View
    Display all vehicles with search
    
    Converted from: aspnet/Module/Inventory/Masters/Vehical_Master.aspx
    """
    # model = Tblvehiclemaster  # Model does not exist
    template_name = 'inventory/masters/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(vehicleno__icontains=search) |
                Q(vehiclename__icontains=search) |
                Q(registrationno__icontains=search)
            )
        
        return queryset.order_by('vehicleno')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context



class VehicleCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """Vehicle Create View"""
    # model = Tblvehiclemaster  # Model does not exist
    # form_class = VehicleMasterForm  # Form commented out
    template_name = 'inventory/masters/vehicle_form.html'
    success_url = reverse_lazy('inventory:vehicle-list')
    
    def form_valid(self, form):
        self.object = form.save()
        
        messages.success(
            self.request,
            f'Vehicle {self.object.vehicleno} created successfully!'
        )
        
        return HttpResponseRedirect(self.get_success_url())



class VehicleDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """Vehicle Detail View with trip history"""
    # model = Tblvehiclemaster  # Model does not exist
    template_name = 'inventory/masters/vehicle_detail.html'
    context_object_name = 'vehicle'
    pk_url_kwarg = 'vehicleid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent trips
        from .services import VehicleService
        history = VehicleService.get_vehicle_history(self.object.vehicleid)
        
        context['trips'] = history['trips'][:10]  # Last 10 trips
        context['total_distance'] = history['total_distance']
        context['total_fuel'] = history['total_fuel']
        context['avg_efficiency'] = history['avg_efficiency']
        
        return context



class VehicleUpdateView(LoginRequiredMixin, CompanyFinancialYearMixin, UpdateView):
    """Vehicle Update View"""
    # model = Tblvehiclemaster  # Model does not exist
    # form_class = VehicleMasterForm  # Form commented out
    template_name = 'inventory/masters/vehicle_form.html'
    success_url = reverse_lazy('inventory:vehicle-list')
    pk_url_kwarg = 'vehicleid'

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f'Vehicle {self.object.vehicleno} updated successfully!')
        return HttpResponseRedirect(self.get_success_url())



class VehicleTripCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """Vehicle Trip Create View"""
    model = TblvehProcessMaster  # NOTE: Tblvehicletrip does not exist
    # form_class = VehicleTripForm  # Form commented out
    template_name = 'inventory/masters/vehicle_trip_form.html'
    
    def get_vehicle(self):
        vehicleid = self.kwargs.get('vehicleid')
        return get_object_or_404(TblvehProcessMaster, vehicleid=vehicleid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle'] = self.get_vehicle()
        return context
    
    def form_valid(self, form):
        vehicle = self.get_vehicle()
        form.instance.vehicleid = vehicle
        
        self.object = form.save()
        
        messages.success(
            self.request,
            f'Trip recorded for vehicle {vehicle.vehicleno}!'
        )
        
        return HttpResponseRedirect(
            reverse_lazy('inventory:vehicle-detail', kwargs={'vehicleid': vehicle.vehicleid})
        )



class VehicleHistoryView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """Vehicle History View - Complete trip history"""
    # model = Tblvehiclemaster  # Model does not exist
    template_name = 'inventory/masters/vehicle_history.html'
    context_object_name = 'vehicle'
    pk_url_kwarg = 'vehicleid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from .services import VehicleService
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        
        history = VehicleService.get_vehicle_history(
            self.object.vehicleid,
            from_date,
            to_date
        )
        
        context['trips'] = history['trips']
        context['total_distance'] = history['total_distance']
        context['total_fuel'] = history['total_fuel']
        context['avg_efficiency'] = history['avg_efficiency']
        context['from_date'] = from_date
        context['to_date'] = to_date
        
        return context


# ============================================================================
# WIS (WORK INSTRUCTION SHEET) VIEWS
# ============================================================================


class VehicleProcessMasterListView(BaseListViewMixin, ListView):
    """
    Vehicle Process Master List View

    Converted from: aspnet/Module/Inventory/Masters/Vehical_Master.aspx
    """
    model = TblvehProcessMaster
    template_name = 'inventory/masters/vehicle_process_master_list.html'
    context_object_name = 'vehicles'
    paginate_by = 15
    ordering = ['vehicalname']



class VehicleProcessMasterCreateView(BaseCreateViewMixin, CreateView):
    """
    Vehicle Process Master Create View
    """
    model = TblvehProcessMaster
    form_class = VehicleProcessMasterForm
    template_name = 'inventory/masters/partials/vehicle_process_master_form.html'
    success_url = reverse_lazy('inventory:vehicle-process-master-list')
    success_message = 'Vehicle created successfully!'



class VehicleProcessMasterUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Vehicle Process Master Update View
    """
    model = TblvehProcessMaster
    form_class = VehicleProcessMasterForm
    template_name = 'inventory/masters/partials/vehicle_process_master_form.html'
    success_url = reverse_lazy('inventory:vehicle-process-master-list')
    success_message = 'Vehicle updated successfully!'



class VehicleProcessMasterDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Vehicle Process Master Delete View
    """
    model = TblvehProcessMaster
    success_url = reverse_lazy('inventory:vehicle-process-master-list')
    success_message = 'Vehicle deleted successfully!'


# ============================================================================
# AUTO WIS TIME SCHEDULE VIEWS
# ============================================================================


class VehicleMasterListView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    Vehicle Master List with HTMX Inline Editing

    Converted from: aaspnet/Module/Inventory/Masters/Vehical_Master.aspx
    Implements SAP Fiori-style inline editing pattern with HTMX
    """
    model = TblvehProcessMaster
    template_name = 'inventory/vehicle_master_list.html'
    context_object_name = 'vehicles'
    paginate_by = 15

    def get_queryset(self):
        queryset = TblvehProcessMaster.objects.all().order_by('id')

        # Search functionality
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(vehicalname__icontains=search_query) |
                Q(vehicalno__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        # Return partial template for HTMX requests
        if self.request.headers.get('HX-Request'):
            self.template_name = 'inventory/partials/vehicle_master_list_partial.html'
        return super().render_to_response(context, **response_kwargs)



class VehicleMasterCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """Create new vehicle via HTMX"""
    model = TblvehProcessMaster
    form_class = VehicleMasterForm
    template_name = 'inventory/partials/vehicle_master_form.html'
    success_url = reverse_lazy('inventory:vehicle-master-list')

    def form_valid(self, form):
        self.object = form.save()

        if self.request.headers.get('HX-Request'):
            # Return the new row
            return render(
                self.request,
                'inventory/partials/vehicle_master_row.html',
                {'vehicle': self.object, 'forloop': {'counter': 1}}
            )
        return redirect(self.success_url)

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(
                self.request,
                self.template_name,
                {'form': form}
            )
        return super().form_invalid(form)



class VehicleMasterUpdateView(LoginRequiredMixin, CompanyFinancialYearMixin, UpdateView):
    """Update vehicle via HTMX - returns to row view on success"""
    model = TblvehProcessMaster
    form_class = VehicleMasterForm
    template_name = 'inventory/partials/vehicle_master_edit_row.html'
    success_url = reverse_lazy('inventory:vehicle-master-list')

    def get(self, request, *args, **kwargs):
        """Show edit form as table row"""
        self.object = self.get_object()
        form = self.get_form()

        if request.headers.get('HX-Request'):
            return render(
                request,
                'inventory/partials/vehicle_master_edit_row.html',
                {'vehicle': self.object, 'form': form}
            )
        return redirect(self.success_url)

    def form_valid(self, form):
        self.object = form.save()

        if self.request.headers.get('HX-Request'):
            # Return the updated row
            return render(
                self.request,
                'inventory/partials/vehicle_master_row.html',
                {'vehicle': self.object, 'forloop': {'counter': 1}}
            )
        return redirect(self.success_url)

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(
                self.request,
                'inventory/partials/vehicle_master_edit_row.html',
                {'vehicle': self.object, 'form': form}
            )
        return super().form_invalid(form)



class VehicleMasterDeleteView(LoginRequiredMixin, CompanyFinancialYearMixin, DeleteView):
    """Delete vehicle via HTMX"""
    model = TblvehProcessMaster
    success_url = reverse_lazy('inventory:vehicle-master-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get('HX-Request'):
            # Return empty response (row will be removed by HTMX swap)
            return HttpResponse('')
        return redirect(self.success_url)



class VehicleMasterRowView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """Return single vehicle row (for cancel operation)"""
    model = TblvehProcessMaster
    template_name = 'inventory/partials/vehicle_master_row.html'
    context_object_name = 'vehicle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forloop'] = {'counter': 1}  # Will be recalculated by JS
        return context


# ============================================================================
# NOTE: All transaction views (GIN, MRS, MIN, GRR, MRN) are defined above in this file
# ============================================================================
# from .gin_views import GINListView, GINCreateView, GINDetailView
# from .mrs_views import MRSListView, MRSCreateView, MRSDetailView
# from .min_views import MINListView, MINCreateView, MINDetailView
# from .grr_views import GRRListView, GRRCreateView, GRRDetailView
# from .mrn_views import MRNListView, MRNCreateView, MRNDetailView


# ============================================================================
# FILE DOWNLOAD VIEWS
# ============================================================================


