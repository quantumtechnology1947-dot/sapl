"""
Material Management API Views

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
from ..models import Supplier, RateRegister, POMaster, PODetails


class ItemSearchAPIView(View):
    """
    API endpoint for searching items (for SPR manual item selection)
    Returns JSON with item results
    """
    def get(self, request):
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return JsonResponse({'items': []})

        from design.models import TbldgItemMaster
        from sys_admin.models import UnitMaster

        items_qs = TbldgItemMaster.objects.filter(
            Q(itemcode__icontains=query) | Q(manfdesc__icontains=query)
        )[:20]

        # Get all UOMs for efficiency
        uom_dict = {uom.id: uom.symbol for uom in UnitMaster.objects.all()}

        # Transform queryset to list of dicts with correct field names
        items = []
        for item in items_qs:
            # Get UOM symbol from uombasic ID, fallback to 'PCS'
            uom_symbol = uom_dict.get(item.uombasic, 'PCS') if item.uombasic else 'PCS'

            items.append({
                'itemid': item.id,
                'itemcode': item.itemcode or '',
                'manfdesc': item.manfdesc or '',
                'uombasic': uom_symbol
            })

        return JsonResponse({'items': items})




class SupplierAutocompleteAPIView(View):
    """
    API endpoint for supplier autocomplete (for Rate Set supplier filter)
    Returns JSON array of supplier names in format: "Name [Code]"
    """
    def get(self, request):
        query = request.GET.get('q', '').strip()

        if len(query) < 1:
            return JsonResponse({'suppliers': []})

        # Get company from session
        compid = request.session.get('compid', 1)

        # Search suppliers by name
        suppliers_qs = Supplier.objects.filter(
            comp_id=compid
        ).filter(
            Q(supplier_name__icontains=query) | Q(supplier_id__icontains=query)
        ).order_by('supplier_name')[:20]

        # Format as "Name [Code]"
        suppliers = [
            f"{s.supplier_name} [{s.supplier_id}]"
            for s in suppliers_qs
        ]

        return JsonResponse({'suppliers': suppliers})




class SupplierRateAPIView(View):
    """
    API endpoint for getting supplier rate from Rate Register
    Returns JSON with rate and discount
    """
    def get(self, request):
        item_id = request.GET.get('item_id')
        supplier_id = request.GET.get('supplier_id')

        if not item_id or not supplier_id:
            return JsonResponse({'rate': 0, 'discount': 0})

        # Get company and fin year from session
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)

        # Try to get rate from Rate Register
        try:
            rate_record = RateRegister.objects.filter(
                item_id=item_id,
                supplier_id=supplier_id,
                comp_id=compid,
                fin_year_id=finyearid
            ).order_by('-rate_date').first()

            if rate_record:
                return JsonResponse({
                    'rate': float(rate_record.rate),
                    'discount': float(rate_record.discount or 0)
                })
        except:
            pass

        # Fallback: Get last PO rate for this item-supplier combination
        try:
            last_po_detail = PODetails.objects.filter(
                item_id=item_id,
                po__supplier_id=supplier_id,
                po__comp_id=compid
            ).order_by('-po__po_date').first()

            if last_po_detail:
                return JsonResponse({
                    'rate': float(last_po_detail.rate),
                    'discount': float(last_po_detail.discount or 0)
                })
        except:
            pass

        return JsonResponse({'rate': 0, 'discount': 0})


# ============================================================================
# Scope of Supplier Report
# ============================================================================



