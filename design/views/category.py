"""
Design Category Master Views
Converted from: aspnet/Module/Design/Masters/CategoryNew.aspx, CategoryEdit.aspx, CategoryDelete.aspx
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime

from ..models import TbldgCategoryMaster
from ..forms import DesignCategoryForm


class DesignCategoryListView(LoginRequiredMixin, ListView):
    """
    Display list of all design categories (no pagination).
    Converted from: aspnet/Module/Design/Masters/CategoryNew.aspx
    """
    model = TbldgCategoryMaster
    template_name = 'design/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        """Order categories by name - show all records."""
        return TbldgCategoryMaster.objects.all().order_by('cname')

    def get_template_names(self):
        """Return partial template for HTMX requests."""
        if self.request.headers.get('HX-Request'):
            return ['design/partials/category_list_partial.html']
        return ['design/category_list.html']


class DesignCategoryCreateView(LoginRequiredMixin, CreateView):
    """
    Create new design category.
    Converted from: aspnet/Module/Design/Masters/CategoryNew.aspx
    """
    model = TbldgCategoryMaster
    form_class = DesignCategoryForm
    template_name = 'design/category_form.html'
    success_url = reverse_lazy('design:category-list')

    def form_valid(self, form):
        """Add system fields before saving."""
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessinid = str(self.request.user.id)
        form.instance.compid = 1
        form.instance.finyearid = 1

        # Convert checkbox to string
        if form.cleaned_data.get('hassubcat'):
            form.instance.hassubcat = 'Y'
        else:
            form.instance.hassubcat = 'N'

        messages.success(self.request, f'Category {form.instance.cname} created successfully.')
        return super().form_valid(form)


class DesignCategoryUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing design category.
    Converted from: aspnet/Module/Design/Masters/CategoryEdit.aspx
    """
    model = TbldgCategoryMaster
    form_class = DesignCategoryForm
    template_name = 'design/category_form.html'
    success_url = reverse_lazy('design:category-list')
    pk_url_kwarg = 'cid'

    def get_form(self, form_class=None):
        """Pre-populate checkbox based on string value."""
        form = super().get_form(form_class)
        if self.object.hassubcat == 'Y':
            form.fields['hassubcat'].initial = True
        else:
            form.fields['hassubcat'].initial = False
        return form

    def form_valid(self, form):
        """Convert checkbox to string."""
        if form.cleaned_data.get('hassubcat'):
            form.instance.hassubcat = 'Y'
        else:
            form.instance.hassubcat = 'N'

        messages.success(self.request, f'Category {form.instance.cname} updated successfully.')
        return super().form_valid(form)


class DesignCategoryDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete design category.
    Converted from: aspnet/Module/Design/Masters/CategoryDelete.aspx
    """
    model = TbldgCategoryMaster
    success_url = reverse_lazy('design:category-list')
    pk_url_kwarg = 'cid'

    def delete(self, request, *args, **kwargs):
        """Handle delete with HTMX support."""
        self.object = self.get_object()
        category_name = self.object.cname

        self.object.delete()

        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)

        messages.success(request, f'Category {category_name} deleted successfully.')
        return redirect(self.success_url)
