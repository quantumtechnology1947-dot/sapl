"""
Quality Control Master Data Views

Handles Rejection Reason master CRUD operations.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .base import QualityControlBaseMixin
from quality_control.models import TblqcRejectionReason
from quality_control.forms import RejectionReasonForm


class RejectionReasonListView(QualityControlBaseMixin, ListView):
    """List all rejection reasons"""
    model = TblqcRejectionReason
    template_name = 'quality_control/rejection_reason/list.html'
    context_object_name = 'reasons'
    paginate_by = 20

    def get_queryset(self):
        queryset = TblqcRejectionReason.objects.all().order_by('id')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) | Q(symbol__icontains=search)
            )
        return queryset


class RejectionReasonCreateView(QualityControlBaseMixin, CreateView):
    """Create new rejection reason"""
    model = TblqcRejectionReason
    form_class = RejectionReasonForm
    template_name = 'quality_control/rejection_reason/form.html'
    success_url = reverse_lazy('quality_control:rejection-reason-list')

    def form_valid(self, form):
        messages.success(self.request, 'Rejection reason created successfully')
        return super().form_valid(form)


class RejectionReasonUpdateView(QualityControlBaseMixin, UpdateView):
    """Update existing rejection reason"""
    model = TblqcRejectionReason
    form_class = RejectionReasonForm
    template_name = 'quality_control/rejection_reason/form.html'
    success_url = reverse_lazy('quality_control:rejection-reason-list')

    def form_valid(self, form):
        messages.success(self.request, 'Rejection reason updated successfully')
        return super().form_valid(form)


class RejectionReasonDeleteView(QualityControlBaseMixin, DeleteView):
    """Delete rejection reason"""
    model = TblqcRejectionReason
    template_name = 'quality_control/rejection_reason/delete.html'
    success_url = reverse_lazy('quality_control:rejection-reason-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Rejection reason deleted successfully')
        return super().delete(request, *args, **kwargs)


class RejectionReasonDetailView(QualityControlBaseMixin, DetailView):
    """View rejection reason details"""
    model = TblqcRejectionReason
    template_name = 'quality_control/rejection_reason/detail.html'
    context_object_name = 'reason'
