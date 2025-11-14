"""
Material Management Buyer Master Views

Converted from: aspnet/Module/MaterialManagement/Masters/Buyer.aspx
Following Django conventions, HTMX patterns, and Tailwind standards
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q

from core.mixins import HTMXResponseMixin
from .dashboard import MaterialManagementBaseMixin
from ..models import Buyer
from ..forms import BuyerForm


# =============================================================================
# BUYER MASTER
# =============================================================================

class BuyerListView(MaterialManagementBaseMixin, HTMXResponseMixin, ListView):
    """
    Buyer List View with inline editing

    Converted from: aspnet/Module/MaterialManagement/Masters/Buyer.aspx
    Features: Category filter, employee autocomplete search
    """
    model = Buyer
    template_name = 'material_management/masters/buyer_list.html'
    htmx_template_name = 'material_management/partials/buyer_table.html'
    context_object_name = 'buyers'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('category', 'nos')

        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)

        # Search by employee ID or number
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(nos__icontains=search) |
                Q(emp_id__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        # Category choices A-Z
        context['categories'] = [chr(i) for i in range(65, 91)]
        return context


class BuyerCreateView(MaterialManagementBaseMixin, CreateView):
    """Create Buyer (HTMX inline create)"""
    model = Buyer
    form_class = BuyerForm
    success_url = reverse_lazy('material_management:buyer-list')

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/buyer_row.html',
                {'buyer': self.object}
            )
            return HttpResponse(html)

        messages.success(self.request, 'Buyer created successfully!')
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            errors = '<br>'.join([f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()])
            return HttpResponse(
                f'<div class="text-red-500 text-sm">Error: {errors}</div>',
                status=400
            )
        return super().form_invalid(form)


class BuyerUpdateView(MaterialManagementBaseMixin, UpdateView):
    """Update Buyer (HTMX inline edit)"""
    model = Buyer
    form_class = BuyerForm
    success_url = reverse_lazy('material_management:buyer-list')
    pk_url_kwarg = 'id'
    template_name = 'material_management/partials/buyer_form.html'

    def get(self, request, *args, **kwargs):
        """Return edit form for HTMX inline editing"""
        self.object = self.get_object()
        form = self.get_form()

        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/buyer_form.html',
                {'form': form, 'buyer': self.object}
            )
            return HttpResponse(html)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                'material_management/partials/buyer_row.html',
                {'buyer': self.object}
            )
            return HttpResponse(html)

        messages.success(self.request, 'Buyer updated successfully!')
        return response


class BuyerDeleteView(MaterialManagementBaseMixin, DeleteView):
    """Delete Buyer"""
    model = Buyer
    success_url = reverse_lazy('material_management:buyer-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)

        messages.success(request, 'Buyer deleted successfully!')
        return response


class EmployeeAutocompleteView(MaterialManagementBaseMixin, ListView):
    """
    HTMX endpoint for employee autocomplete in Buyer form
    Returns JSON list of employees matching search term
    """
    def get(self, request, *args, **kwargs):
        search_term = request.GET.get('q', '')
        from human_resource.models import TblhrOfficestaff

        employees = TblhrOfficestaff.objects.filter(
            Q(employeename__icontains=search_term) |
            Q(employeeid__icontains=search_term)
        )[:10]

        results = [
            {'id': emp.employeeid, 'text': f"{emp.employeeid} - {emp.employeename}"}
            for emp in employees
        ]

        return JsonResponse({'results': results})
