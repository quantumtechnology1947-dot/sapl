"""
SysAdmin Configuration Views
Handles Unit Master, GST Master, and other system configuration settings.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin
)

from ..models import UnitMaster, TblgstMaster
from ..forms import UnitMasterForm


# ============================================================================
# UNIT MASTER
# ============================================================================

class UnitMasterListView(BaseListViewMixin, ListView):
    """
    Display paginated list of units.
    Uses BaseListViewMixin for auth, search, HTMX, and query optimization.
    """
    model = UnitMaster
    template_name = 'sys_admin/unit_master_list.html'
    partial_template_name = 'sys_admin/partials/unit_master_list_partial.html'
    context_object_name = 'units'
    paginate_by = 20

    def get_queryset(self):
        """Order units by ID descending (newest first)."""
        return super().get_queryset().order_by('-id')


class UnitMasterCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new unit.
    Uses BaseCreateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = UnitMaster
    form_class = UnitMasterForm
    template_name = 'sys_admin/unit_master_form.html'
    success_url = reverse_lazy('sys_admin:unit-master-list')
    success_message = 'Unit "%(unitname)s" created successfully'

    def form_valid(self, form):
        """Convert checkbox to integer for effectoninvoice."""
        if form.cleaned_data.get('effectoninvoice'):
            form.instance.effectoninvoice = 1
        else:
            form.instance.effectoninvoice = 0

        return super().form_valid(form)


class UnitMasterUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing unit.
    Uses BaseUpdateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = UnitMaster
    form_class = UnitMasterForm
    template_name = 'sys_admin/unit_master_form.html'
    success_url = reverse_lazy('sys_admin:unit-master-list')
    success_message = 'Unit "%(unitname)s" updated successfully'
    pk_url_kwarg = 'id'

    def get_form(self, form_class=None):
        """Pre-populate checkbox based on integer value."""
        form = super().get_form(form_class)
        if self.object.effectoninvoice == 1:
            form.fields['effectoninvoice'].initial = True
        else:
            form.fields['effectoninvoice'].initial = False
        return form

    def form_valid(self, form):
        """Convert checkbox to integer for effectoninvoice."""
        if form.cleaned_data.get('effectoninvoice'):
            form.instance.effectoninvoice = 1
        else:
            form.instance.effectoninvoice = 0

        return super().form_valid(form)


class UnitMasterDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete unit.
    Uses BaseDeleteViewMixin for auth and HTMX support (auto 204 response).
    """
    model = UnitMaster
    success_url = reverse_lazy('sys_admin:unit-master-list')
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        """Handle delete with success message."""
        self.object = self.get_object()
        unit_name = self.object.unitname

        messages.success(request, f'Unit {unit_name} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# GST MASTER
# ============================================================================

class GSTMasterListView(BaseListViewMixin, ListView):
    """
    Display paginated list of GST rates.
    Uses BaseListViewMixin for auth, search, HTMX, and query optimization.
    """
    model = TblgstMaster
    template_name = 'sys_admin/gst_master_list.html'
    partial_template_name = 'sys_admin/partials/gst_master_list_partial.html'
    context_object_name = 'gst_rates'
    paginate_by = 20

    def get_queryset(self):
        """Order GST rates by rate value."""
        queryset = super().get_queryset()

        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(live=1)
        elif status == 'inactive':
            queryset = queryset.filter(live=0)

        return queryset.order_by('-ratevalue')


class GSTMasterCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new GST rate.
    Auto-calculates CGST, SGST, and IGST from rate value.
    Uses BaseCreateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = TblgstMaster
    template_name = 'sys_admin/gst_master_form.html'
    success_url = reverse_lazy('sys_admin:gst-master-list')
    success_message = 'GST rate created successfully'
    fields = ['gstrate', 'ratevalue', 'hsnapplicable', 'effectivefrom', 'live']

    def form_valid(self, form):
        """Auto-calculate CGST, SGST, and IGST rates."""
        gst = form.save(commit=False)

        # Auto-calculate rates
        if gst.ratevalue:
            gst.cgstrate = gst.ratevalue / 2
            gst.sgstrate = gst.ratevalue / 2
            gst.igstrate = gst.ratevalue

        gst.save()

        messages.success(
            self.request,
            f'GST rate {gst.gstrate} created successfully. CGST: {gst.cgstrate}%, SGST: {gst.sgstrate}%, IGST: {gst.igstrate}%'
        )

        return redirect(self.success_url)


class GSTMasterUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing GST rate.
    Auto-recalculates CGST, SGST, and IGST if rate value changes.
    Uses BaseUpdateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = TblgstMaster
    template_name = 'sys_admin/gst_master_form.html'
    success_url = reverse_lazy('sys_admin:gst-master-list')
    success_message = 'GST rate updated successfully'
    fields = ['gstrate', 'ratevalue', 'hsnapplicable', 'effectivefrom', 'live']

    def form_valid(self, form):
        """Auto-recalculate CGST, SGST, and IGST rates."""
        gst = form.save(commit=False)

        # Auto-calculate rates
        if gst.ratevalue:
            gst.cgstrate = gst.ratevalue / 2
            gst.sgstrate = gst.ratevalue / 2
            gst.igstrate = gst.ratevalue

        gst.save()

        messages.success(
            self.request,
            f'GST rate {gst.gstrate} updated successfully. CGST: {gst.cgstrate}%, SGST: {gst.sgstrate}%, IGST: {gst.igstrate}%'
        )

        return redirect(self.success_url)


class GSTMasterDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Soft delete GST rate (set live=0).
    Uses BaseDeleteViewMixin for auth and HTMX support.
    """
    model = TblgstMaster
    success_url = reverse_lazy('sys_admin:gst-master-list')

    def delete(self, request, *args, **kwargs):
        """Perform soft delete by setting live=0."""
        self.object = self.get_object()

        # Soft delete: set live=0
        self.object.live = 0
        self.object.save()

        messages.success(request, f'GST rate {self.object.gstrate} deactivated successfully.')

        # BaseDeleteViewMixin handles HTMX 204 response
        return super().delete(request, *args, **kwargs)


class GSTMasterDetailView(BaseDetailViewMixin, DetailView):
    """
    View GST rate details.
    Shows calculated CGST, SGST, and IGST rates.
    """
    model = TblgstMaster
    template_name = 'sys_admin/gst_master_detail.html'
    context_object_name = 'gst_rate'
