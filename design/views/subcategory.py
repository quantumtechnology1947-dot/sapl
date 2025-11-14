"""
Design Sub-Category Master Views
Converted from: aspnet/Module/Design/Masters/SubCategoryNew.aspx, SubCategoryEdit.aspx, SubCategoryDelete.aspx
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime

from ..models import TbldgCategoryMaster, TbldgSubcategoryMaster
from ..forms import DesignSubCategoryForm


class DesignSubCategoryListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of design sub-categories.
    Converted from: aspnet/Module/Design/Masters/SubCategoryNew.aspx
    """
    model = TbldgSubcategoryMaster
    template_name = 'design/subcategory_list.html'
    context_object_name = 'subcategories'
    paginate_by = 20

    def get_queryset(self):
        """Order sub-categories by name."""
        return TbldgSubcategoryMaster.objects.all().order_by('scname')

    def get_context_data(self, **kwargs):
        """Add categories to context."""
        context = super().get_context_data(**kwargs)
        context['categories'] = TbldgCategoryMaster.objects.all().order_by('cname')
        return context

    def get_template_names(self):
        """Return partial template for HTMX requests."""
        if self.request.headers.get('HX-Request'):
            return ['design/partials/subcategory_list_partial.html']
        return ['design/subcategory_list.html']


class DesignSubCategoryCreateView(LoginRequiredMixin, CreateView):
    """
    Create new design sub-category.
    Converted from: aspnet/Module/Design/Masters/SubCategoryNew.aspx
    """
    model = TbldgSubcategoryMaster
    form_class = DesignSubCategoryForm
    template_name = 'design/subcategory_form.html'
    success_url = reverse_lazy('design:subcategory-list')

    def form_valid(self, form):
        """Add system fields before saving."""
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessionid = str(self.request.user.id)
        form.instance.compid = 1
        form.instance.finyearid = 1

        # Convert ModelChoiceField to ID
        if form.cleaned_data.get('cid'):
            form.instance.cid = form.cleaned_data['cid'].cid

        messages.success(self.request, f'Sub-category {form.instance.scname} created successfully.')
        return super().form_valid(form)


class DesignSubCategoryUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing design sub-category.
    Converted from: aspnet/Module/Design/Masters/SubCategoryEdit.aspx
    """
    model = TbldgSubcategoryMaster
    form_class = DesignSubCategoryForm
    template_name = 'design/subcategory_form.html'
    success_url = reverse_lazy('design:subcategory-list')
    pk_url_kwarg = 'scid'

    def get_form(self, form_class=None):
        """Pre-populate category field."""
        form = super().get_form(form_class)
        if self.object.cid:
            try:
                form.fields['cid'].initial = TbldgCategoryMaster.objects.get(cid=self.object.cid)
            except TbldgCategoryMaster.DoesNotExist:
                pass
        return form

    def form_valid(self, form):
        """Convert ModelChoiceField to ID."""
        if form.cleaned_data.get('cid'):
            form.instance.cid = form.cleaned_data['cid'].cid

        messages.success(self.request, f'Sub-category {form.instance.scname} updated successfully.')
        return super().form_valid(form)


class DesignSubCategoryDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete design sub-category.
    Converted from: aspnet/Module/Design/Masters/SubCategoryDelete.aspx
    """
    model = TbldgSubcategoryMaster
    success_url = reverse_lazy('design:subcategory-list')
    pk_url_kwarg = 'scid'

    def delete(self, request, *args, **kwargs):
        """Handle delete with HTMX support."""
        self.object = self.get_object()
        subcategory_name = self.object.scname

        self.object.delete()

        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)

        messages.success(request, f'Sub-category {subcategory_name} deleted successfully.')
        return redirect(self.success_url)
