"""
Scrap Register Views

Handles Scrap Register CRUD operations.
"""
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .base import QualityControlBaseMixin
from quality_control.models import TblqcScrapregister
from quality_control.forms import ScrapRegisterForm


class ScrapRegisterListView(QualityControlBaseMixin, ListView):
    """List all scrap registers"""
    model = TblqcScrapregister
    template_name = 'quality_control/scrap_register/list.html'
    context_object_name = 'scraps'
    paginate_by = 20

    def get_queryset(self):
        queryset = TblqcScrapregister.objects.filter(
            compid=self.get_compid(),
            finyearid=self.get_finyearid()
        ).order_by('-id')

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(scrapno__icontains=search) | Q(itemid__icontains=search)
            )
        return queryset


class ScrapRegisterCreateView(QualityControlBaseMixin, CreateView):
    """Create new scrap register"""
    model = TblqcScrapregister
    form_class = ScrapRegisterForm
    template_name = 'quality_control/scrap_register/form.html'
    success_url = reverse_lazy('quality_control:scrap-register-list')

    def form_valid(self, form):
        # Set session metadata
        for field, value in self.get_session_metadata().items():
            setattr(form.instance, field, value)
        messages.success(self.request, f'Scrap {form.instance.scrapno} registered successfully')
        return super().form_valid(form)


class ScrapRegisterDetailView(QualityControlBaseMixin, DetailView):
    """View scrap register details"""
    model = TblqcScrapregister
    template_name = 'quality_control/scrap_register/detail.html'
    context_object_name = 'scrap'


class ScrapRegisterDeleteView(QualityControlBaseMixin, DeleteView):
    """Delete scrap register"""
    model = TblqcScrapregister
    template_name = 'quality_control/scrap_register/delete.html'
    success_url = reverse_lazy('quality_control:scrap-register-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Scrap register deleted successfully')
        return super().delete(request, *args, **kwargs)
