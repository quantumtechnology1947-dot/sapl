"""
Design Reports Views
Includes Item History BOM and Amendment History reports
Converted from: aspnet/Module/Design/Reports/ItemHistory_BOM_View.aspx
"""

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

from ..models import TbldgItemMaster, TbldgBomMaster, TbldgBomAmd
from ..services import BomHistoryService
from sys_admin.models import UnitMaster
from sales_distribution.models import SdCustWorkorderMaster


class ItemHistoryBomSearchView(LoginRequiredMixin, ListView):
    """
    Item History BOM - Search and List View
    Shows searchable list of items with filtering by category, search type, etc.

    ASP.NET Reference: aaspnet/Module/Design/Reports/ItemHistory_BOM.aspx
    """
    model = TbldgItemMaster
    template_name = 'design/reports/item_history_bom_search.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        """Get filtered queryset based on search parameters"""
        queryset = TbldgItemMaster.objects.all()

        # Get session filters
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Base filter: company and financial year
        queryset = queryset.filter(
            compid=compid,
            finyearid__lte=finyearid
        )

        # Get search parameters
        search_type = self.request.GET.get('type', 'Category')
        category_id = self.request.GET.get('category')
        search_field = self.request.GET.get('search_field')
        search_value = self.request.GET.get('search_value', '').strip()
        location_id = self.request.GET.get('location')

        if search_type == 'Category':
            # Category mode: filter by category first
            if category_id:
                queryset = queryset.filter(cid=category_id)

            # Then apply search field filters
            if search_field and search_value:
                if search_field == 'ItemCode':
                    queryset = queryset.filter(itemcode__icontains=search_value)
                elif search_field == 'ManfDesc':
                    queryset = queryset.filter(manfdesc__icontains=search_value)

            if search_field == 'Location' and location_id:
                queryset = queryset.filter(location=location_id)

        elif search_type == 'WOItems':
            # WO Items mode: only show items used in BOMs
            bom_item_ids = TbldgBomMaster.objects.filter(
                compid=compid,
                pid__isnull=False
            ).exclude(
                pid=0
            ).values_list('itemid', flat=True).distinct()
            queryset = queryset.filter(id__in=bom_item_ids)

            # Apply search filters
            if search_field and search_value:
                if search_field == 'ItemCode':
                    queryset = queryset.filter(itemcode__icontains=search_value)
                elif search_field == 'ManfDesc':
                    queryset = queryset.filter(manfdesc__icontains=search_value)

        return queryset.order_by('itemcode')

    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)

        # Get all categories for dropdown
        from ..models import TbldgCategoryMaster
        context['categories'] = TbldgCategoryMaster.objects.filter(
            compid=self.request.session.get('compid', 1)
        ).order_by('symbol')

        # Get all locations for dropdown
        from ..models import TbldgLocationMaster
        context['locations'] = TbldgLocationMaster.objects.filter(
            compid=self.request.session.get('compid', 1)
        ).order_by('locationlabel')

        # Get search parameters for form state
        context['search_type'] = self.request.GET.get('type', 'Category')
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_field'] = self.request.GET.get('search_field', '')
        context['search_value'] = self.request.GET.get('search_value', '')
        context['selected_location'] = self.request.GET.get('location', '')

        # Enrich items with related data
        from sys_admin.models import UnitMaster
        from ..models import TbldgCategoryMaster, TbldgLocationMaster

        # Pre-fetch all categories, locations, and UOMs for efficiency
        categories = {cat.cid: cat for cat in TbldgCategoryMaster.objects.all()}
        locations = {loc.id: loc for loc in TbldgLocationMaster.objects.all()}
        uoms = {uom.id: uom for uom in UnitMaster.objects.all()}

        for item in context['items']:
            # Get category object
            if item.cid and item.cid in categories:
                item.category_obj = categories[item.cid]
            else:
                item.category_obj = None

            # Get UOM object
            if item.uombasic and item.uombasic in uoms:
                item.uom_obj = uoms[item.uombasic]
            else:
                item.uom_obj = None

            # Get location object
            if item.location and item.location in locations:
                item.location_obj = locations[item.location]
            else:
                item.location_obj = None

        return context


class ItemHistoryBomDetailView(LoginRequiredMixin, DetailView):
    """
    Item History BOM - Detail View
    Shows where a specific item is used in BOMs with recursive quantity calculations.

    ASP.NET Reference: aaspnet/Module/Design/Reports/ItemHistory_BOM_View.aspx
    """
    model = TbldgItemMaster
    template_name = 'design/reports/item_history_bom_detail.html'
    context_object_name = 'item'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        """Add BOM usage data"""
        context = super().get_context_data(**kwargs)

        item = self.object
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Get UOM symbol
        from sys_admin.models import UnitMaster
        from ..models import TbldgCategoryMaster, TbldgLocationMaster

        if item.uombasic:
            try:
                uom = UnitMaster.objects.get(id=item.uombasic)
                context['uom_symbol'] = uom.symbol
            except UnitMaster.DoesNotExist:
                context['uom_symbol'] = '-'
        else:
            context['uom_symbol'] = '-'

        # Get category object
        if item.cid:
            try:
                category = TbldgCategoryMaster.objects.get(cid=item.cid)
                context['category'] = category
            except TbldgCategoryMaster.DoesNotExist:
                context['category'] = None
        else:
            context['category'] = None

        # Get location object
        if item.location:
            try:
                location = TbldgLocationMaster.objects.get(id=item.location)
                context['location'] = location
            except TbldgLocationMaster.DoesNotExist:
                context['location'] = None
        else:
            context['location'] = None

        # Get BOM usage using service
        from ..services import BomHistoryService
        usage_list = BomHistoryService.get_item_bom_usage(item.id, compid, finyearid)

        context['bom_usage'] = usage_list

        # Calculate total recursive quantity
        total_qty = sum(usage['recursive_qty'] for usage in usage_list)
        context['total_recursive_qty'] = total_qty

        return context


# ============================================================================
# BOM AMENDMENT HISTORY
# ============================================================================

class BomAmendmentHistoryView(LoginRequiredMixin, ListView):
    """
    Display amendment history for a BOM item.
    Shows all changes made to the item over time.
    Converted from: aspnet/Module/Design/Transactions/BOM_Amd.aspx
    """
    model = TbldgBomAmd
    template_name = 'design/bom/amendment_history.html'
    context_object_name = 'amendments'
    paginate_by = 50

    def get_queryset(self):
        """Get amendment records for specific BOM item or work order."""
        compid = self.request.session.get('compid', 1)

        # Get filter parameters
        wono = self.request.GET.get('wono', '').strip()
        bom_id = self.request.GET.get('bom_id', '').strip()

        queryset = TbldgBomAmd.objects.filter(compid=compid)

        if wono:
            queryset = queryset.filter(wono=wono)

        if bom_id:
            queryset = queryset.filter(bomid=bom_id)

        # Order by most recent first
        return queryset.order_by('-sysdate', '-systime')

    def get_context_data(self, **kwargs):
        """Add filter parameters and BOM item info to context."""
        context = super().get_context_data(**kwargs)

        wono = self.request.GET.get('wono', '').strip()
        bom_id = self.request.GET.get('bom_id', '').strip()

        context['wono'] = wono
        context['bom_id'] = bom_id

        # Get BOM item details if bom_id is provided
        if bom_id:
            try:
                bom_item = TbldgBomMaster.objects.get(id=bom_id)
                context['bom_item'] = bom_item
                context['current_wono'] = bom_item.wono
            except TbldgBomMaster.DoesNotExist:
                pass

        # Get work order info if wono is provided
        if wono and not bom_id:
            from sales_distribution.models import SdCustWorkorderMaster
            try:
                wo = SdCustWorkorderMaster.objects.get(
                    wono=wono,
                    compid=self.request.session.get('compid', 1)
                )
                context['work_order'] = wo
            except SdCustWorkorderMaster.DoesNotExist:
                pass

        # Get count of amendments for current filters
        context['total_amendments'] = self.get_queryset().count()

        return context


# ============================================================================
# AJAX API ENDPOINTS FOR BOM TREE
# ============================================================================
