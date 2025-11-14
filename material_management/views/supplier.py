"""
Material Management Supplier Master Views

Converted from: aspnet/Module/MaterialManagement/Masters/Supplier.aspx
Following Django conventions, HTMX patterns, and Tailwind standards
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .dashboard import MaterialManagementBaseMixin
from ..models import Supplier, BusinessNature, BusinessType, ServiceCoverage
from ..forms import SupplierForm


# =============================================================================
# SUPPLIER MASTER
# =============================================================================

class SupplierListView(MaterialManagementBaseMixin, ListView):
    """
    Supplier List View with search and filter

    Converted from: aspnet/Module/MaterialManagement/Masters/Supplier.aspx
    Note: Due to 65 fields, uses separate create/edit pages instead of inline editing
    """
    model = Supplier
    template_name = 'material_management/masters/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('supplier_id')
        compid = self.get_compid()

        # Filter by company only (suppliers are master data, not year-specific)
        queryset = queryset.filter(comp_id=compid)

        # Search by supplier ID or name
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(supplier_id__icontains=search) |
                Q(supplier_name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class SupplierCreateView(MaterialManagementBaseMixin, CreateView):
    """Create Supplier"""
    model = Supplier
    form_class = SupplierForm
    template_name = 'material_management/masters/supplier_form.html'
    success_url = reverse_lazy('material_management:supplier-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from sys_admin.models import Tblcountry, Tblstate, Tblcity
        context['countries'] = Tblcountry.objects.all().order_by('countryname')
        context['states'] = Tblstate.objects.all().order_by('statename')
        context['cities'] = Tblcity.objects.all().order_by('cityname')
        context['business_natures'] = BusinessNature.objects.all()
        context['business_types'] = BusinessType.objects.all()
        context['service_coverages'] = ServiceCoverage.objects.all()
        return context

    def form_valid(self, form):
        from sys_admin.models import TblfinancialMaster
        from datetime import datetime

        # Auto-generate supplier_id if not provided
        if not form.instance.supplier_id:
            # Get the latest supplier_id and increment
            latest_supplier = Supplier.objects.filter(
                comp_id=self.get_compid()
            ).order_by('-supplier_id').first()

            if latest_supplier and latest_supplier.supplier_id:
                # Try to extract number from supplier_id (e.g., "S004" -> 4)
                try:
                    # Extract letter prefix and number
                    prefix = latest_supplier.supplier_id[0]
                    number = int(latest_supplier.supplier_id[1:])
                    form.instance.supplier_id = f"{prefix}{number + 1:03d}"
                except (ValueError, IndexError):
                    # Fallback to sequential numbering
                    count = Supplier.objects.filter(comp_id=self.get_compid()).count()
                    form.instance.supplier_id = f"S{count + 1:03d}"
            else:
                # First supplier
                form.instance.supplier_id = "S001"

        # Set session-based fields
        form.instance.comp_id = self.get_compid()

        # Get the latest financial year (where Flag=1)
        latest_finyear = TblfinancialMaster.objects.filter(
            compid=self.get_compid(),
            flag=1
        ).first()

        if latest_finyear:
            form.instance.fin_year_id = latest_finyear.finyearid
        else:
            # Fallback to session financial year if no flag is set
            form.instance.fin_year_id = self.get_finyearid()

        # Set actual logged-in user as session_id
        form.instance.session_id = str(self.request.user.username) if self.request.user.is_authenticated else str(self.request.user.id)

        # Set default values for optional fields (ASP.NET sets these to "-")
        if not form.instance.pan_no:
            form.instance.pan_no = "-"
        if not form.instance.tin_cst_no:
            form.instance.tin_cst_no = "-"
        if not form.instance.ecc_no:
            form.instance.ecc_no = "-"
        if not form.instance.juridiction_code:
            form.instance.juridiction_code = "-"
        if not form.instance.commissionurate:
            form.instance.commissionurate = "-"
        if not form.instance.divn:
            form.instance.divn = "-"
        if not form.instance.range:
            form.instance.range = "-"
        if not form.instance.tds_code:
            form.instance.tds_code = "-"

        # Set default dropdown values if not provided
        if not form.instance.pf:
            form.instance.pf = 1  # Default to first option
        if not form.instance.ex_st:
            form.instance.ex_st = 1  # Default to first option
        if not form.instance.vat:
            form.instance.vat = 1  # Default to first option

        # Set default radio button values if not provided
        if form.instance.mod_vat_applicable is None:
            form.instance.mod_vat_applicable = 0  # Default to "No"
        if form.instance.mod_vat_invoice is None:
            form.instance.mod_vat_invoice = 0  # Default to "No"

        response = super().form_valid(form)
        messages.success(self.request, f'Supplier {self.object.supplier_id} created successfully!')
        return response


class SupplierDetailView(MaterialManagementBaseMixin, DetailView):
    """View Supplier Details"""
    model = Supplier
    template_name = 'material_management/masters/supplier_detail.html'
    context_object_name = 'supplier'
    pk_url_kwarg = 'supplier_id'
    slug_field = 'supplier_id'
    slug_url_kwarg = 'supplier_id'

    def get_queryset(self):
        # Only filter by company, not financial year
        # Suppliers are master data that persist across financial years
        return super().get_queryset().filter(
            comp_id=self.get_compid()
        )


class SupplierUpdateView(MaterialManagementBaseMixin, UpdateView):
    """Update Supplier"""
    model = Supplier
    form_class = SupplierForm
    template_name = 'material_management/masters/supplier_form.html'
    success_url = reverse_lazy('material_management:supplier-list')
    pk_url_kwarg = 'supplier_id'
    slug_field = 'supplier_id'
    slug_url_kwarg = 'supplier_id'

    def get_queryset(self):
        # Only filter by company, not financial year
        # Suppliers are master data that persist across financial years
        return super().get_queryset().filter(
            comp_id=self.get_compid()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from sys_admin.models import Tblcountry, Tblstate, Tblcity
        context['countries'] = Tblcountry.objects.all().order_by('countryname')
        context['states'] = Tblstate.objects.all().order_by('statename')
        context['cities'] = Tblcity.objects.all().order_by('cityname')
        context['business_natures'] = BusinessNature.objects.all()
        context['business_types'] = BusinessType.objects.all()
        context['service_coverages'] = ServiceCoverage.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Supplier {self.object.supplier_id} updated successfully!')
        return response


class SupplierDeleteView(MaterialManagementBaseMixin, DeleteView):
    """Delete Supplier"""
    model = Supplier
    success_url = reverse_lazy('material_management:supplier-list')
    pk_url_kwarg = 'supplier_id'
    slug_field = 'supplier_id'
    slug_url_kwarg = 'supplier_id'

    def get_queryset(self):
        # Only filter by company, not financial year
        # Suppliers are master data that persist across financial years
        return super().get_queryset().filter(
            comp_id=self.get_compid()
        )

    def delete(self, request, *args, **kwargs):
        supplier = self.get_object()
        supplier_id = supplier.supplier_id
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Supplier {supplier_id} deleted successfully!')
        return response


# =============================================================================
# SCOPE OF SUPPLIER REPORT
# =============================================================================

class ScopeOfSupplierView(MaterialManagementBaseMixin, ListView):
    """
    Scope of Supplier Report - List all suppliers with scope of supply search

    ASP.NET Reference: Module/MaterialManagement/Transactions/Supply_Scope.aspx
    """
    model = Supplier
    template_name = 'material_management/transactions/scope_of_supplier.html'
    context_object_name = 'suppliers'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            comp_id=self.get_compid()
        ).order_by('supplier_name')

        # Search by scope of supply
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(scope_of_supply__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context
