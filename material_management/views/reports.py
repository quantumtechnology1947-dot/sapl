"""
Material Management REPORTS Views

Converted from: aspnet/Module/MaterialManagement/
Following Django conventions, HTMX patterns, and Tailwind standards
"""

from datetime import datetime

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q, Max

from core.mixins import HTMXResponseMixin
from .dashboard import MaterialManagementBaseMixin
from ..models import RateRegister, Supplier, POMaster


class RateRegisterReportView(MaterialManagementBaseMixin, TemplateView):
    """
    Rate Register Report - Item-wise rate history
    Converted from: aspnet/Module/MaterialManagement/Reports/RateRegister.aspx
    """
    template_name = 'material_management/reports/rate_register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get filter parameters
        item_id = self.request.GET.get('item_id')
        supplier_id = self.request.GET.get('supplier_id')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # Build query
        rates = RateRegister.objects.filter(
            comp_id=compid,
            fin_year_id=finyearid
        ).select_related('item').order_by('-effective_date')

        if item_id:
            rates = rates.filter(item_id=item_id)
        if supplier_id:
            rates = rates.filter(supplier_id=supplier_id)
        if from_date:
            rates = rates.filter(effective_date__gte=from_date)
        if to_date:
            rates = rates.filter(effective_date__lte=to_date)

        context['rates'] = rates[:100]  # Limit to 100 records
        context['item_id'] = item_id
        context['supplier_id'] = supplier_id
        context['from_date'] = from_date
        context['to_date'] = to_date
        return context




class SupplierRatingReportView(MaterialManagementBaseMixin, TemplateView):
    """
    Supplier Rating Report - Quality/delivery rating analysis
    Converted from: aspnet/Module/MaterialManagement/Reports/SupplierRating.aspx
    """
    template_name = 'material_management/reports/supplier_rating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get all suppliers with their PO data
        suppliers = Supplier.objects.filter(
            comp_id=compid,
            fin_year_id=finyearid
        ).order_by('supplier_name')

        # Note: Actual rating calculation would require GRN data
        # This is a placeholder for the report structure
        context['suppliers'] = suppliers
        return context




class MaterialForecastingReportView(MaterialManagementBaseMixin, TemplateView):
    """
    Material Forecasting Report - Consumption analysis and forecasting
    Converted from: aspnet/Module/MaterialManagement/Reports/MaterialForecasting.aspx
    """
    template_name = 'material_management/reports/material_forecasting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get parameters
        item_id = self.request.GET.get('item_id')
        months = int(self.request.GET.get('months', 6))

        # Placeholder for forecasting logic
        # Actual implementation would analyze consumption patterns
        context['item_id'] = item_id
        context['months'] = months
        context['forecast_data'] = []
        return context




class MaterialSearchView(MaterialManagementBaseMixin, TemplateView):
    """
    Material Search - Advanced search across suppliers, items, rates
    Converted from: aspnet/Module/MaterialManagement/Reports/Search.aspx
    """
    template_name = 'material_management/reports/material_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        search_query = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', 'all')  # all, supplier, item, rate

        results = {
            'suppliers': [],
            'items': [],
            'rates': []
        }

        if search_query:
            if search_type in ['all', 'supplier']:
                results['suppliers'] = Supplier.objects.filter(
                    Q(supplier_id__icontains=search_query) |
                    Q(supplier_name__icontains=search_query),
                    comp_id=compid,
                    fin_year_id=finyearid
                )[:20]

            if search_type in ['all', 'item']:
                from design.models import TbldgItemMaster
                results['items'] = TbldgItemMaster.objects.filter(
                    Q(itemname__icontains=search_query) |
                    Q(itemcode__icontains=search_query)
                )[:20]

            if search_type in ['all', 'rate']:
                results['rates'] = RateRegister.objects.filter(
                    comp_id=compid,
                    fin_year_id=finyearid
                ).select_related('item').filter(
                    Q(item__itemname__icontains=search_query)
                )[:20]

        context['search_query'] = search_query
        context['search_type'] = search_type
        context['results'] = results
        return context


# =============================================================================
# API ENDPOINTS
# =============================================================================



