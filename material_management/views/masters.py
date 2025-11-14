"""
Material Management Master Views
Business Nature, Business Type, Service Coverage

Converted from: aspnet/Module/MaterialManagement/Masters/
Following Django conventions, HTMX patterns, and Tailwind standards
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib import messages

from core.mixins import HTMXResponseMixin
from .dashboard import MaterialManagementBaseMixin
from ..models import BusinessNature, BusinessType, ServiceCoverage
from ..forms import BusinessNatureForm, BusinessTypeForm, ServiceCoverageForm


# =============================================================================
# BUSINESS NATURE MASTER
# =============================================================================

class BusinessNatureListView(MaterialManagementBaseMixin, HTMXResponseMixin, ListView):
    """
    Business Nature List View with inline editing

    Converted from: aspnet/Module/MaterialManagement/Masters/BusinessNature.aspx
    ASP.NET Pattern: GridView with footer insert, inline edit/delete
    """
    model = BusinessNature
    template_name = 'material_management/masters/business_nature_list.html'
    htmx_template_name = 'material_management/partials/business_nature_table.html'
    context_object_name = 'business_natures'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(nature__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class BusinessNatureCreateView(MaterialManagementBaseMixin, CreateView):
    """
    Create Business Nature (HTMX inline create)

    Converted from: GridView footer insert functionality
    """
    model = BusinessNature
    form_class = BusinessNatureForm
    success_url = reverse_lazy('material_management:business-nature-list')

    def form_valid(self, form):
        response = super().form_valid(form)

        # For HTMX requests, return the new row HTML
        if self.request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/business_nature_row.html',
                {'business_nature': self.object}
            )
            return HttpResponse(html)

        messages.success(self.request, 'Business Nature created successfully!')
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="text-red-500 text-sm">Error: Nature is required</div>',
                status=400
            )
        return super().form_invalid(form)


class BusinessNatureUpdateView(MaterialManagementBaseMixin, UpdateView):
    """
    Update Business Nature (HTMX inline edit)

    Converted from: GridView inline edit functionality
    """
    model = BusinessNature
    form_class = BusinessNatureForm
    success_url = reverse_lazy('material_management:business-nature-list')
    pk_url_kwarg = 'id'
    template_name = 'material_management/partials/business_nature_edit_row.html'

    def get(self, request, *args, **kwargs):
        """Return edit form row for HTMX inline editing"""
        self.object = self.get_object()

        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/business_nature_edit_row.html',
                {'business_nature': self.object, 'forloop': {'counter': 1}}
            )
            return HttpResponse(html)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        # For HTMX requests, return the updated row HTML
        if self.request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/business_nature_row.html',
                {'business_nature': self.object, 'forloop': {'counter': 1}}
            )
            return HttpResponse(html)

        messages.success(self.request, 'Business Nature updated successfully!')
        return response


class BusinessNatureDeleteView(MaterialManagementBaseMixin, DeleteView):
    """
    Delete Business Nature

    Converted from: GridView delete button
    """
    model = BusinessNature
    success_url = reverse_lazy('material_management:business-nature-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        # For HTMX requests, return 204 No Content to remove the row
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)

        messages.success(request, 'Business Nature deleted successfully!')
        return response


# =============================================================================
# BUSINESS TYPE MASTER
# =============================================================================

class BusinessTypeListView(MaterialManagementBaseMixin, HTMXResponseMixin, ListView):
    """
    Business Type List View with inline editing

    Converted from: aspnet/Module/MaterialManagement/Masters/BusinessType.aspx
    """
    model = BusinessType
    template_name = 'material_management/masters/business_type_list.html'
    htmx_template_name = 'material_management/partials/business_type_table.html'
    context_object_name = 'business_types'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(type__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class BusinessTypeCreateView(MaterialManagementBaseMixin, CreateView):
    """Create Business Type (HTMX inline create)"""
    model = BusinessType
    form_class = BusinessTypeForm
    success_url = reverse_lazy('material_management:business-type-list')

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/business_type_row.html',
                {'business_type': self.object}
            )
            return HttpResponse(html)

        messages.success(self.request, 'Business Type created successfully!')
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="text-red-500 text-sm">Error: Type is required</div>',
                status=400
            )
        return super().form_invalid(form)


class BusinessTypeUpdateView(MaterialManagementBaseMixin, UpdateView):
    """Update Business Type (HTMX inline edit)"""
    model = BusinessType
    form_class = BusinessTypeForm
    success_url = reverse_lazy('material_management:business-type-list')
    pk_url_kwarg = 'id'
    template_name = 'material_management/partials/business_type_edit_row.html'

    def get(self, request, *args, **kwargs):
        """Return edit form row for HTMX inline editing"""
        self.object = self.get_object()

        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/business_type_edit_row.html',
                {'business_type': self.object, 'forloop': {'counter': 1}}
            )
            return HttpResponse(html)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/business_type_row.html',
                {'business_type': self.object, 'forloop': {'counter': 1}}
            )
            return HttpResponse(html)

        messages.success(self.request, 'Business Type updated successfully!')
        return response


class BusinessTypeDeleteView(MaterialManagementBaseMixin, DeleteView):
    """Delete Business Type"""
    model = BusinessType
    success_url = reverse_lazy('material_management:business-type-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)

        messages.success(request, 'Business Type deleted successfully!')
        return response


# =============================================================================
# SERVICE COVERAGE MASTER
# =============================================================================

class ServiceCoverageListView(MaterialManagementBaseMixin, HTMXResponseMixin, ListView):
    """
    Service Coverage List View with inline editing

    Converted from: aspnet/Module/MaterialManagement/Masters/ServiceCoverage.aspx
    """
    model = ServiceCoverage
    template_name = 'material_management/masters/service_coverage_list.html'
    htmx_template_name = 'material_management/partials/service_coverage_table.html'
    context_object_name = 'service_coverages'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(coverage__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ServiceCoverageCreateView(MaterialManagementBaseMixin, CreateView):
    """Create Service Coverage (HTMX inline create)"""
    model = ServiceCoverage
    form_class = ServiceCoverageForm
    success_url = reverse_lazy('material_management:service-coverage-list')

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/service_coverage_row.html',
                {'service_coverage': self.object}
            )
            return HttpResponse(html)

        messages.success(self.request, 'Service Coverage created successfully!')
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="text-red-500 text-sm">Error: Coverage is required</div>',
                status=400
            )
        return super().form_invalid(form)


class ServiceCoverageUpdateView(MaterialManagementBaseMixin, UpdateView):
    """Update Service Coverage (HTMX inline edit)"""
    model = ServiceCoverage
    form_class = ServiceCoverageForm
    success_url = reverse_lazy('material_management:service-coverage-list')
    pk_url_kwarg = 'id'
    template_name = 'material_management/partials/service_coverage_edit_row.html'

    def get(self, request, *args, **kwargs):
        """Return edit form row for HTMX inline editing"""
        self.object = self.get_object()

        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/service_coverage_edit_row.html',
                {'service_coverage': self.object, 'forloop': {'counter': 1}}
            )
            return HttpResponse(html)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/service_coverage_row.html',
                {'service_coverage': self.object, 'forloop': {'counter': 1}}
            )
            return HttpResponse(html)

        messages.success(self.request, 'Service Coverage updated successfully!')
        return response


class ServiceCoverageDeleteView(MaterialManagementBaseMixin, DeleteView):
    """Delete Service Coverage"""
    model = ServiceCoverage
    success_url = reverse_lazy('material_management:service-coverage-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)

        messages.success(request, 'Service Coverage deleted successfully!')
        return response
