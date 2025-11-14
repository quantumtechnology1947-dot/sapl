"""
Design BOM (Bill of Materials) Management Views
Converted from: aspnet/Module/Design/BOM_Master_Edit.aspx, BOM_WoItems.aspx, BOM_Design_Assembly_New.aspx
Includes tree view, assembly creation, 4-tab wizard, and API endpoints
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView, View, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from datetime import datetime
from django.db import transaction
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

from ..models import (
    TbldgBomMaster, TbldgBomAmd, TbldgItemMaster,
    TbldgCategoryMaster, TbldgSubcategoryMaster
)
from ..forms import BomMasterForm
from ..services import BomService
from sales_distribution.models import SdCustWorkorderMaster, SdCustMaster
from sys_admin.models import UnitMaster


class BomListView(LoginRequiredMixin, ListView):
    """
    Display BOMs grouped by work order with customer information.
    Converted from: aspnet/Module/Design/Transactions/BOM_Design_WO_Grid.aspx
    """
    model = TbldgBomMaster
    template_name = 'design/bom_list.html'
    context_object_name = 'boms'
    paginate_by = 50
    
    def get_queryset(self):
        """Get unique work orders with BOM data, with search filtering."""
        from sales_distribution.models import SdCustWorkorderMaster
        from django.db.models import Q
        
        compid = self.request.session.get('compid', 1)
        
        # Get ALL distinct work orders that have BOM records (any financial year)
        bom_wonos = TbldgBomMaster.objects.filter(
            compid=compid
        ).values_list('wono', flat=True).distinct()
        
        # Get work orders (no financial year barrier)
        work_orders = SdCustWorkorderMaster.objects.filter(
            wono__in=bom_wonos,
            compid=compid
        )
        
        # Apply search filters
        search_type = self.request.GET.get('search_type', 'customer')
        search_value = self.request.GET.get('search_value', '').strip()
        wo_category = self.request.GET.get('wo_category', '').strip()
        
        if search_value:
            if search_type == 'customer':
                # Search by customer name - need to join with customer table
                from sales_distribution.models import SdCustMaster
                customer_ids = SdCustMaster.objects.filter(
                    customername__icontains=search_value,
                    compid=compid
                ).values_list('customerid', flat=True)
                work_orders = work_orders.filter(customerid__in=customer_ids)
            elif search_type == 'wono':
                # Search by WO number
                work_orders = work_orders.filter(wono__icontains=search_value)
        
        # Filter by WO category (first letter of WO number)
        if wo_category:
            work_orders = work_orders.filter(wono__istartswith=wo_category)
        
        return work_orders.order_by('-wono')
    
    def get_context_data(self, **kwargs):
        """Add BOM details for each work order."""
        from sys_admin.models import TblfinancialMaster
        from sales_distribution.models import SdCustMaster
        from django.contrib.auth.models import User
        
        context = super().get_context_data(**kwargs)
        
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)
        
        # Get current financial year name for display
        try:
            current_finyear_obj = TblfinancialMaster.objects.get(finyearid=finyearid, compid=compid)
            current_finyear_name = current_finyear_obj.finyear
        except:
            current_finyear_name = 'N/A'
        
        # Build detailed info for each work order
        wo_details = []
        for wo in context['boms']:
            # Get customer info
            try:
                customer_obj = SdCustMaster.objects.get(customerid=wo.customerid, compid=compid)
                customer_name = customer_obj.customername
                customer_code = customer_obj.customerid
            except:
                customer_name = 'N/A'
                customer_code = wo.customerid if wo.customerid else 'N/A'
            
            # Get ALL BOM records for this work order (any financial year)
            bom_count = TbldgBomMaster.objects.filter(
                compid=compid,
                wono=wo.wono
            ).count()
            
            # Get first BOM record for generation info (any financial year)
            first_bom = TbldgBomMaster.objects.filter(
                compid=compid,
                wono=wo.wono
            ).order_by('id').first()
            
            # Get username for "Gen. By" column
            gen_by_name = 'N/A'
            if first_bom and first_bom.sessionid:
                try:
                    user = User.objects.get(id=int(first_bom.sessionid))
                    gen_by_name = user.username
                except (User.DoesNotExist, ValueError):
                    gen_by_name = first_bom.sessionid
            
            wo_details.append({
                'wono': wo.wono,
                'finyear': current_finyear_name,  # Always show current FY
                'customer_name': customer_name,
                'customer_code': customer_code,
                'gen_date': first_bom.sysdate if first_bom else 'N/A',
                'gen_by': gen_by_name,
                'total_items': bom_count
            })
        
        context['wo_details'] = wo_details
        return context


class BomCreateSelectWoView(LoginRequiredMixin, ListView):
    """
    Display work orders WITHOUT BOMs for creating new BOMs.
    Converted from: aspnet/Module/Design/Transactions/BOM_Design_WO_Grid.aspx (BOM Design - New)
    """
    model = SdCustWorkorderMaster
    template_name = 'design/bom_create_select_wo.html'
    context_object_name = 'work_orders'
    paginate_by = 50

    def get_queryset(self):
        """Get work orders that DON'T have BOM records yet."""
        from sales_distribution.models import SdCustWorkorderMaster, SdCustMaster
        from django.db.models import Q

        compid = self.request.session.get('compid', 1)

        # Get distinct work orders that ALREADY have BOMs (any financial year)
        existing_bom_wonos = TbldgBomMaster.objects.filter(
            compid=compid
        ).values_list('wono', flat=True).distinct()

        # Get all work orders that DON'T have BOMs (no financial year barrier)
        work_orders = SdCustWorkorderMaster.objects.filter(
            compid=compid
        ).exclude(wono__in=existing_bom_wonos)

        # Apply search filters
        search_type = self.request.GET.get('search_type', 'customer')
        search_value = self.request.GET.get('search_value', '').strip()
        wo_category = self.request.GET.get('wo_category', '').strip()

        if search_value:
            if search_type == 'customer':
                # Search by customer name
                customer_ids = SdCustMaster.objects.filter(
                    customername__icontains=search_value,
                    compid=compid
                ).values_list('customerid', flat=True)
                work_orders = work_orders.filter(customerid__in=customer_ids)
            elif search_type == 'wono':
                # Search by WO number
                work_orders = work_orders.filter(wono__icontains=search_value)

        # Filter by WO category (first letter of WO number)
        if wo_category:
            work_orders = work_orders.filter(wono__istartswith=wo_category)

        return work_orders.order_by('-wono')

    def get_context_data(self, **kwargs):
        """Add work order details with customer information."""
        from sys_admin.models import TblfinancialMaster
        from sales_distribution.models import SdCustMaster

        context = super().get_context_data(**kwargs)

        compid = self.request.session.get('compid', 1)

        # Build detailed info for each work order
        wo_details = []
        for wo in context['work_orders']:
            # Get financial year name
            try:
                finyear_obj = TblfinancialMaster.objects.get(finyearid=wo.finyearid, compid=compid)
                finyear_name = finyear_obj.finyear
            except:
                finyear_name = 'N/A'

            # Get customer info
            try:
                customer_obj = SdCustMaster.objects.get(customerid=wo.customerid, compid=compid)
                customer_name = customer_obj.customername
                customer_code = customer_obj.customerid
            except:
                customer_name = 'N/A'
                customer_code = wo.customerid if wo.customerid else 'N/A'

            wo_details.append({
                'wono': wo.wono,
                'finyear': finyear_name,
                'customer_name': customer_name,
                'customer_code': customer_code,
                'gen_date': wo.sysdate if wo.sysdate else 'N/A',
                'gen_by': wo.sessionid if wo.sessionid else 'N/A',
            })

        context['wo_details'] = wo_details
        return context


class BomTreeView(LoginRequiredMixin, DetailView):
    """
    Display hierarchical BOM tree for a work order using Alpine.js.
    Converted from: aspnet/Module/Design/Transactions/BOM_Design_WO_TreeView.aspx
    """
    model = TbldgBomMaster
    template_name = 'design/bom_tree_alpine.html'
    context_object_name = 'bom'
    
    def get_object(self):
        """Get BOM by work order number - can return None if no BOM exists yet"""
        wono = self.kwargs.get('wono')
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Get the first root item for this work order (returns None if doesn't exist)
        return TbldgBomMaster.objects.filter(
            wono=wono,
            compid=compid,
            finyearid__lte=finyearid
        ).first()

    def get(self, request, *args, **kwargs):
        """Override get to handle case where object might not exist (ASP.NET pattern)"""
        self.object = self.get_object()
        # Continue rendering even if object is None - template shows "Add Assembly" button
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        """Build hierarchical tree structure with filtering."""
        from ..bom_services import BomService
        from sales_distribution.models import SdCustWorkorderMaster, SdCustMaster

        context = super().get_context_data(**kwargs)
        wono = self.kwargs.get('wono')

        # Get filter type from query params
        filter_type = self.request.GET.get('filter', 'all')

        # Get company from session
        compid = self.request.session.get('compid', 1)

        logger.info(f"BomTreeView: Loading WO {wono}, CompID: {compid}")

        # Get work order to use its finyearid (CRITICAL: DO NOT use session finyearid!)
        try:
            wo = SdCustWorkorderMaster.objects.get(wono=wono, compid=compid)
            context['work_order'] = wo
            finyearid = wo.finyearid  # Use work order's finyearid!
            logger.info(f"Found WO: {wo.wono}, FinYearId: {finyearid}, CustomerID: {wo.customerid}")

            # Get customer info
            if wo.customerid:
                logger.info(f"Looking for customer: {wo.customerid}, CompID: {compid}")
                customer = SdCustMaster.objects.filter(
                    customerid=wo.customerid,
                    compid=compid
                ).first()

                if customer:
                    context['customer'] = customer
                    logger.info(f"✓ Customer found: {customer.customername}")
                else:
                    logger.error(f"✗ Customer NOT FOUND: {wo.customerid}")
                    # Try without compid to debug
                    any_cust = SdCustMaster.objects.filter(customerid=wo.customerid).first()
                    if any_cust:
                        logger.error(f"  Customer exists with CompID: {any_cust.compid}, Name: {any_cust.customername}")
            else:
                logger.warning(f"WO {wono} has no customerid")

        except SdCustWorkorderMaster.DoesNotExist:
            logger.error(f"✗ Work order {wono} not found in database")
            finyearid = self.request.session.get('finyearid', 1)  # Fallback only
        except Exception as e:
            logger.error(f"✗ Error loading WO/Customer: {str(e)}")
            finyearid = self.request.session.get('finyearid', 1)  # Fallback only

        # Get all BOM items for this work order (use work order's finyearid!)
        all_items = TbldgBomMaster.objects.filter(
            wono=wono,
            compid=compid,
            finyearid__lte=finyearid
        ).select_related('itemid')

        logger.info(f"BOM query: wono={wono}, compid={compid}, finyearid__lte={finyearid}, items_found={all_items.count()}")

        # Build tree structure using enhanced service with levels
        tree = BomService.build_bom_tree_with_levels(wono, compid, finyearid, filter_type)
        context['tree_data'] = tree  # For Alpine.js template
        context['wono'] = wono
        context['all_items'] = all_items
        context['filter_type'] = filter_type

        # Get BOM statistics
        context['statistics'] = BomService.get_bom_statistics(wono, compid, finyearid)

        return context

    def _convert_to_jstree_json(self, tree_nodes):
        """
        Convert Django BOM tree to jsTree JSON format with level metadata.

        jsTree expects:
        [{
            "id": "node_id",
            "text": "Node display text",
            "icon": "icon-class",
            "type": "assembly" or "part",
            "children": [...]
        }]
        """
        import json

        def build_jstree_node(node):
            item = node['item']
            level = node.get('level', 0)
            can_add_children = node.get('can_add_children', True)

            # Build display text with badges
            item_code = item.itemid.itemcode if item.itemid else item.partno
            description = item.itemid.manfdesc if item.itemid else 'No description'
            qty = node.get('bom_qty', item.qty)

            # Truncate description for readability
            if description and len(description) > 50:
                description = description[:50] + '...'

            # Get level name
            level_name = BomService.get_level_name(level)

            # Create display text with HTML badges including level badge
            text = f'<strong>{item_code}</strong> - {description}'
            text += f' <span class="node-badge level-badge level-{level}">{level_name}</span>'
            if qty:
                text += f' <span class="node-badge qty-badge">Qty: {qty:.3f}</span>'
            if item.revision:
                text += f' <span class="node-badge rev-badge">Rev: {item.revision}</span>'
            if item.ecnflag:
                text += f' <span class="node-badge ecn-badge">ECN</span>'

            # Determine node type based on level
            if level == 0:
                node_type = 'assembly'
            elif level == 1:
                node_type = 'subassembly'
            else:
                node_type = 'part'

            jstree_node = {
                'id': str(item.id),
                'text': text,
                'type': node_type,
                'data': {
                    'partno': item.partno or '',
                    'qty': float(qty) if qty else 1.0,
                    'revision': item.revision or '',
                    'cid': item.cid,
                    'pid': item.pid or 0,
                    'level': level,
                    'level_name': level_name,
                    'can_add_children': can_add_children
                }
            }

            # Recursively build children
            if node.get('children'):
                jstree_node['children'] = [
                    build_jstree_node(child) for child in node['children']
                ]

            return jstree_node

        # Convert all root nodes
        jstree_data = [build_jstree_node(node) for node in tree_nodes]

        return json.dumps(jstree_data)

class ItemSearchApiView(LoginRequiredMixin, View):
    """
    HTMX endpoint for searching items by code or description.
    Returns HTML partial with search results.
    """
    def get(self, request):
        query = request.GET.get('item_search', '').strip()
        compid = request.session.get('compid', 1)

        if len(query) < 2:
            return HttpResponse('')

        # Search items by description (manfdesc) or code (itemcode)
        # Sort by description for user-friendliness
        items = TbldgItemMaster.objects.filter(
            compid=compid
        ).filter(
            Q(manfdesc__icontains=query) |
            Q(itemcode__icontains=query) |
            Q(partno__icontains=query)
        ).order_by('manfdesc', 'itemcode')[:20]

        html = '<div class="max-h-60 overflow-y-auto border border-gray-300 rounded-md mt-1 bg-white shadow-lg">'
        if items:
            for item in items:
                # Escape single quotes in descriptions to prevent JavaScript errors
                safe_desc = (item.manfdesc or 'No description').replace("'", "\\'").replace('"', '&quot;')
                safe_code = (item.itemcode or item.partno or '').replace("'", "\\'").replace('"', '&quot;')

                html += f'''
                <div class="p-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0 transition-colors"
                     onclick="selectItem({item.id}, '{safe_code}', '{safe_desc}')">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <div class="font-semibold text-sm text-gray-900">{item.manfdesc or 'No description'}</div>
                            <div class="text-xs text-blue-600 mt-0.5">Code: {item.itemcode or item.partno or 'N/A'}</div>
                        </div>
                    </div>
                </div>
                '''
        else:
            html += '<div class="p-4 text-sm text-gray-500 text-center">No items found matching "{}"</div>'.format(query)
        html += '</div>'

        return HttpResponse(html)


class BomCreateAssemblyView(LoginRequiredMixin, FormView):
    """
    Create a new root assembly for a work order's BOM.
    Phase 2 implementation using temporary storage pattern.

    Converted from: aspnet/Module/Design/Transactions/BOM_Design_Assembly_New.aspx
    """
    template_name = 'design/bom_add_assembly.html'
    form_class = None  # Will import after forms are defined

    def get_form_class(self):
        from .forms import BomAddAssemblyForm
        return BomAddAssemblyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wono = self.kwargs.get('wono')
        context['wono'] = wono

        # Get work order details
        from sales_distribution.models import SdCustWorkorderMaster
        try:
            context['work_order'] = SdCustWorkorderMaster.objects.get(
                wono=wono,
                compid=self.request.session.get('compid', 1)
            )
        except SdCustWorkorderMaster.DoesNotExist:
            pass

        return context

    def form_valid(self, form):
        from ..services import BomService, BomTempService
        from datetime import datetime
        from sales_distribution.models import SdCustWorkorderMaster

        wono = self.kwargs.get('wono')
        compid = self.request.session.get('compid', 1)
        sessionid = str(self.request.user.id)

        # Get work order to use its finyearid (CRITICAL: DO NOT use session finyearid!)
        try:
            work_order = SdCustWorkorderMaster.objects.get(wono=wono, compid=compid)
            finyearid = work_order.finyearid
        except SdCustWorkorderMaster.DoesNotExist:
            messages.error(self.request, f'Work order {wono} not found')
            return redirect('design:bom-list')

        # Get form data
        item = form.cleaned_data['itemid']
        qty = form.cleaned_data['qty']
        revision = form.cleaned_data.get('revision', '0')
        remark = form.cleaned_data.get('remark', '')

        # Generate equipment number
        equipment_no = BomService.generate_equipment_no(wono, compid)
        next_cid = BomService.generate_next_cid(wono, compid)

        # Create root assembly directly (no temp storage for root)
        now = datetime.now()
        bom_item = TbldgBomMaster.objects.create(
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S'),
            compid=compid,
            finyearid=finyearid,  # Use work order's finyearid, not session
            sessionid=sessionid,
            wono=wono,
            equipmentno=equipment_no,
            unitno=None,  # Root level has no unit
            partno='00',  # Root level uses '00' as part number (ASP.NET pattern)
            pid=0,  # Root has no parent
            cid=next_cid,
            qty=qty,
            ecn=0,
            ecnflag=0,
            amdno=0,
            revision=revision,
            remark=remark,
            material='',
            itemid=item
        )

        messages.success(
            self.request,
            f'Root assembly {equipment_no} added successfully with item {item.itemcode}'
        )
        return redirect('design:bom-tree', wono=wono)


class BomAddItemsWizardView(LoginRequiredMixin, TemplateView):
    """
    4-Tab Wizard for adding items to BOM assembly.
    Implements complete ASP.NET BOM_WoItems.aspx functionality.

    Tabs:
    1. Item Master - Search and add existing items
    2. New Items - Create new manufacturing items
    3. Copy From - Copy from other work orders (future)
    4. Selected Items - Review and commit

    Converted from: aaspnet/Module/Design/Transactions/BOM_WoItems.aspx
    """
    template_name = 'design/bom_wizard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wono = self.kwargs.get('wono')
        parent_cid = self.kwargs.get('parent_cid')

        context['wono'] = wono
        context['parent_cid'] = parent_cid

        # Get parent assembly details
        try:
            parent_bom = TbldgBomMaster.objects.select_related('itemid').get(
                wono=wono,
                cid=parent_cid,
                compid=self.request.session.get('compid', 1)
            )
            context['parent_bom'] = parent_bom
            context['parent_item'] = parent_bom.itemid
            context['parent_partno'] = parent_bom.partno or ''

            # Generate next part number for Tab 2
            if parent_bom.partno:
                next_part_no = BomService.get_next_part_no(
                    parent_bom.partno,
                    wono,
                    self.request.session.get('compid', 1)
                )

                # Parse parent part number
                parts = parent_bom.partno.split('-')
                if len(parts) >= 2:
                    context['equip_no'] = parts[0]
                    context['unit_no'] = parts[1]
                    context['next_part_no'] = next_part_no

        except TbldgBomMaster.DoesNotExist:
            messages.error(self.request, 'Parent assembly not found')

        # Get work order details
        from sales_distribution.models import SdCustWorkorderMaster
        try:
            work_order = SdCustWorkorderMaster.objects.get(
                wono=wono,
                compid=self.request.session.get('compid', 1)
            )
            context['work_order'] = work_order
        except SdCustWorkorderMaster.DoesNotExist:
            pass

        # Get temp items for Tab 4
        from ..services import BOMSessionService
        context['temp_items'] = BOMSessionService.get_temp_items_with_details(self.request)
        context['temp_count'] = len(context['temp_items'])

        # Get categories for Tab 1 search
        from ..models import TbldgDesignCategoryMaster
        context['categories'] = TbldgDesignCategoryMaster.objects.filter(
            compid=self.request.session.get('compid', 1)
        ).order_by('categoryname')

        # Get UOM list for Tab 2
        from sys_admin.models import UnitMaster
        context['uom_list'] = UnitMaster.objects.all().order_by('symbol')

        return context


class BomAddChildView(LoginRequiredMixin, FormView):
    """
    DEPRECATED: Use BomAddItemsWizardView instead.
    Kept for backward compatibility only.

    Add a child item under an existing BOM assembly.
    Uses temporary storage pattern for review before commit.

    Phase 2/3 implementation.
    """
    template_name = 'design/bom_add_child.html'
    form_class = None

    def get_form_class(self):
        from .forms import BomAddChildItemForm
        return BomAddChildItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent_id = self.kwargs.get('parent_id')

        # Get parent assembly
        try:
            parent = TbldgBomMaster.objects.get(id=parent_id)
            context['parent'] = parent
            context['wono'] = parent.wono
        except TbldgBomMaster.DoesNotExist:
            messages.error(self.request, 'Parent assembly not found')

        return context

    def form_valid(self, form):
        from ..services import BomService, BomTempService

        parent_id = self.kwargs.get('parent_id')
        try:
            parent = TbldgBomMaster.objects.get(id=parent_id)
        except TbldgBomMaster.DoesNotExist:
            messages.error(self.request, 'Parent assembly not found')
            return redirect('design:bom-list')

        compid = self.request.session.get('compid', 1)
        sessionid = str(self.request.user.id)

        # Get form data
        item = form.cleaned_data['itemid']
        qty = form.cleaned_data['qty']
        remark = form.cleaned_data.get('remark', '')

        # Add to temporary storage
        temp_item = BomTempService.add_to_temp(
            wono=parent.wono,
            parent_cid=parent.cid,  # Use parent's CId, not database ID
            item_id=item.id,
            qty=qty,
            sessionid=sessionid,
            compid=compid
        )

        if temp_item:
            messages.success(
                self.request,
                f'Item {item.itemcode} added to pending list. Click "Commit" to save permanently.'
            )
        else:
            messages.warning(
                self.request,
                f'Item {item.itemcode} is already in the pending list or BOM.'
            )

        # Redirect back to tree view
        return redirect('design:bom-tree', wono=parent.wono)


class BomAddItemsView(LoginRequiredMixin, RedirectView):
    """
    Placeholder view for full 4-tab wizard - redirects to tree view for now.

    TODO Phase 3: Implement full 4-tab wizard (Search Items, New Items, Copy From, Review)
    """
    def get_redirect_url(self, *args, **kwargs):
        wono = kwargs.get('wono')
        messages.info(self.request, 'Full Add Items wizard coming in Phase 3. Use "Add Assembly" button for now.')
        return reverse('design:bom-tree', kwargs={'wono': wono})


class BomCreateView(LoginRequiredMixin, CreateView):
    """
    Create new BOM (root assembly).
    Converted from: aspnet/Module/Design/Transactions/BOM_Design_Assembly_New.aspx
    """
    model = TbldgBomMaster
    form_class = BomMasterForm
    template_name = 'design/bom_form.html'
    success_url = reverse_lazy('design:bom-list')
    
    def form_valid(self, form):
        """Add system fields before saving."""
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessionid = str(self.request.user.id)
        form.instance.compid = 1
        form.instance.finyearid = 1
        
        # Set default values
        form.instance.amdno = 0
        form.instance.ecn = 0
        form.instance.ecnflag = 0
        
        # This is a root item, so pid should be null
        form.instance.pid = None
        form.instance.cid = 0
        
        messages.success(self.request, f'BOM for work order {form.instance.wono} created successfully.')
        return super().form_valid(form)


class BomUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing BOM item.
    Converted from: aspnet/Module/Design/Transactions/BOM_Design_Assembly_Edit.aspx

    Implements ECN workflow and amendment tracking:
    - Before design date: Direct modification allowed
    - After design date: Creates ECN and amendment record
    """
    model = TbldgBomMaster
    form_class = BomMasterForm
    template_name = 'design/bom_form.html'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        """Return to tree view for this work order."""
        return reverse_lazy('design:bom-tree', kwargs={'wono': self.object.wono})

    def form_valid(self, form):
        """
        Update BOM item with ECN workflow and amendment tracking.

        Logic:
        1. Check if design finalization date has passed
        2. If YES: Create amendment record + trigger ECN workflow
        3. If NO: Allow direct modification
        """
        from ..bom_services import BomService

        # Get original item before changes
        original_item = TbldgBomMaster.objects.get(pk=self.object.pk)

        # Get company and session info
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)
        sessionid = str(self.request.user.id)

        # Check if design finalization date has passed
        design_date_passed, design_date = BomService.check_design_date(
            original_item.wono,
            compid
        )

        if design_date_passed:
            # Design date has passed - ECN workflow required
            logger.info(f"Design date passed for WO {original_item.wono}. Triggering ECN workflow.")

            # Create amendment record to preserve old values
            amendment = BomService.create_amendment(original_item)
            logger.info(f"Amendment record created: {amendment.id}")

            # Increment amendment number
            form.instance.amdno = (original_item.amdno or 0) + 1

            # Set ECN flag
            form.instance.ecnflag = 1

            # Save the updated item
            response = super().form_valid(form)

            # Note: ECN Master/Details should be created via separate ECN workflow
            # This is typically done through the ECN Master form where user selects reasons

            messages.warning(
                self.request,
                f'BOM item updated. Design date ({design_date}) has passed. '
                f'ECN workflow triggered. Amendment #{form.instance.amdno} created. '
                f'Please create ECN record with reasons.'
            )

            return response
        else:
            # Design date not reached - direct modification allowed
            logger.info(f"Design date not passed for WO {original_item.wono}. Direct modification allowed.")

            messages.success(self.request, f'BOM item updated successfully.')
            return super().form_valid(form)


# ============================================================================
# BOM WIZARD HTMX ENDPOINTS
# ============================================================================

class BomWizardSearchItemsView(LoginRequiredMixin, View):
    """
    Tab 1: Search items from Item Master.
    HTMX endpoint for item search functionality.
    """
    def get(self, request, wono, parent_cid):
        compid = request.session.get('compid', 1)

        # Get search parameters
        search_term = request.GET.get('search', '').strip()
        category_id = request.GET.get('category', '')
        search_by = request.GET.get('search_by', 'itemcode')  # itemcode, description

        # Build query
        from sys_admin.models import UnitMaster
        items_query = TbldgItemMaster.objects.filter(compid=compid)

        if category_id:
            items_query = items_query.filter(cid=category_id)

        if search_term:
            if search_by == 'description':
                items_query = items_query.filter(manfdesc__icontains=search_term)
            else:
                items_query = items_query.filter(itemcode__icontains=search_term)

        # Limit results
        items = items_query.select_related('cid').order_by('itemcode')[:50]

        # Get UOM for each item
        items_data = []
        for item in items:
            uom = UnitMaster.objects.filter(id=item.uombasic_id).first()
            items_data.append({
                'id': item.id,
                'itemcode': item.itemcode or '',
                'partno': item.partno or '',
                'manfdesc': item.manfdesc or '',
                'uom': uom.symbol if uom else '',
                'category': item.cid.categoryname if item.cid else ''
            })

        return render(request, 'design/partials/bom_wizard_search_results.html', {
            'items': items_data,
            'wono': wono,
            'parent_cid': parent_cid
        })


class BomWizardAddExistingItemView(LoginRequiredMixin, View):
    """
    Tab 1: Add existing item to temp storage.
    """
    def post(self, request, wono, parent_cid):
        from ..services import BOMSessionService

        item_id = request.POST.get('item_id')
        qty = request.POST.get('qty', 1)

        try:
            qty = float(qty)
            if qty <= 0:
                messages.error(request, 'Quantity must be greater than 0')
                return redirect('design:bom-wizard', wono=wono, parent_cid=parent_cid)

            # Add to session temp
            BOMSessionService.add_existing_item(request, int(item_id), qty, parent_cid)

            messages.success(request, 'Item added to pending list')

        except (ValueError, TypeError):
            messages.error(request, 'Invalid quantity')

        return redirect('design:bom-wizard', wono=wono, parent_cid=parent_cid)


class BomWizardAddNewItemView(LoginRequiredMixin, View):
    """
    Tab 2: Add new item to temp storage.
    """
    def post(self, request, wono, parent_cid):
        from ..services import BOMSessionService, BomService
        from sys_admin.models import UnitMaster

        compid = request.session.get('compid', 1)

        # Get form data
        equip_no = request.POST.get('equip_no', '')
        unit_no = request.POST.get('unit_no', '')
        part_no = request.POST.get('part_no', '')
        manfdesc = request.POST.get('manfdesc', '')
        uombasic = request.POST.get('uombasic')
        qty = request.POST.get('qty', 1)
        material = request.POST.get('material', '')
        remark = request.POST.get('remark', '')

        try:
            qty = float(qty)
            if qty <= 0:
                messages.error(request, 'Quantity must be greater than 0')
                return redirect('design:bom-wizard', wono=wono, parent_cid=parent_cid)

            # Generate itemcode
            itemcode = BomService.generate_item_code(equip_no, unit_no, part_no, '0')
            partno_full = f'{equip_no}-{unit_no}-{part_no}'

            # Check if itemcode already exists
            if TbldgItemMaster.objects.filter(itemcode=itemcode, compid=compid).exists():
                messages.error(request, f'Item code {itemcode} already exists')
                return redirect('design:bom-wizard', wono=wono, parent_cid=parent_cid)

            # Get UOM symbol for display
            uom = UnitMaster.objects.filter(id=uombasic).first()
            uom_symbol = uom.symbol if uom else ''

            # Build item data
            item_data = {
                'partno': partno_full,
                'itemcode': itemcode,
                'process': '0',
                'manfdesc': manfdesc,
                'uombasic': int(uombasic),
                'uom_symbol': uom_symbol,
                'material': material,
                'equipmentno': equip_no,
                'unitno': unit_no,
                'ecnflag': 0,
                'revision': ''
            }

            # Handle file uploads if present
            if 'drawing_file' in request.FILES:
                file = request.FILES['drawing_file']
                item_data['filename'] = file.name
                item_data['filesize'] = file.size
                item_data['contenttype'] = file.content_type
                item_data['filedata'] = file.read()

            if 'spec_file' in request.FILES:
                file = request.FILES['spec_file']
                item_data['attname'] = file.name
                item_data['attsize'] = file.size
                item_data['attcontenttype'] = file.content_type
                item_data['attdata'] = file.read()

            # Add to session temp
            BOMSessionService.add_new_item(request, item_data, qty, parent_cid, remark)

            messages.success(request, f'New item {itemcode} added to pending list')

        except (ValueError, TypeError) as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('design:bom-wizard', wono=wono, parent_cid=parent_cid)


class BomWizardRemoveItemView(LoginRequiredMixin, View):
    """
    Tab 4: Remove item from temp storage.
    """
    def post(self, request, wono, parent_cid):
        from ..services import BOMSessionService

        index = request.POST.get('index')

        try:
            BOMSessionService.remove_item(request, int(index))
            messages.success(request, 'Item removed from pending list')
        except (ValueError, TypeError, IndexError):
            messages.error(request, 'Invalid item index')

        return redirect('design:bom-wizard', wono=wono, parent_cid=parent_cid)


class BomWizardCommitView(LoginRequiredMixin, View):
    """
    Tab 4: Commit all temp items to permanent BOM.
    """
    def post(self, request, wono, parent_cid):
        from ..services import BOMSessionService

        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        sessionid = str(request.user.id)

        try:
            count = BOMSessionService.commit_to_bom(
                request, wono, parent_cid, compid, finyearid, sessionid
            )

            messages.success(request, f'{count} item(s) added to BOM successfully')
            return redirect('design:bom-tree', wono=wono)

        except Exception as e:
            messages.error(request, f'Error committing items: {str(e)}')
            return redirect('design:bom-wizard', wono=wono, parent_cid=parent_cid)


class BomWizardCancelView(LoginRequiredMixin, View):
    """
    Cancel wizard and clear temp items.
    """
    def post(self, request, wono, parent_cid):
        from ..services import BOMSessionService

        BOMSessionService.clear_temp_items(request)
        messages.info(request, 'Wizard cancelled. Pending items cleared.')
        return redirect('design:bom-tree', wono=wono)


class BomDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete BOM item and all its children.
    Converted from: aspnet/Module/Design/Transactions/BOM_Design_Delete.aspx
    """
    model = TbldgBomMaster
    pk_url_kwarg = 'id'
    
    def get_success_url(self):
        """Return to BOM list."""
        return reverse_lazy('design:bom-list')
    
    def delete(self, request, *args, **kwargs):
        """Delete item and all children recursively."""
        self.object = self.get_object()
        wono = self.object.wono
        
        # Delete this item and all children
        self._delete_children(self.object.id)
        self.object.delete()
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        
        messages.success(request, f'BOM item deleted successfully.')
        return redirect(self.get_success_url())
    
    def _delete_children(self, parent_id):
        """Recursively delete all children."""
        children = TbldgBomMaster.objects.filter(pid=parent_id)
        for child in children:
            self._delete_children(child.id)
            child.delete()


class BomCopyView(LoginRequiredMixin, FormView):
    """
    Copy BOM from one work order to another.
    Converted from: aaspnet/Module/Design/Transactions/BOM_Design_CopyWo.aspx
    """
    template_name = 'design/bom_copy.html'
    form_class = None  # Will create inline

    def get(self, request):
        """Display BOM copy form."""
        context = {
            'page_title': 'Copy BOM'
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Process BOM copy."""
        source_wono = request.POST.get('source_wono', '').strip()
        target_wono = request.POST.get('target_wono', '').strip()

        # Validation
        if not source_wono or not target_wono:
            messages.error(request, 'Both source and target work order numbers are required.')
            return render(request, self.template_name, {
                'page_title': 'Copy BOM',
                'source_wono': source_wono,
                'target_wono': target_wono
            })

        if source_wono == target_wono:
            messages.error(request, 'Source and target work orders cannot be the same.')
            return render(request, self.template_name, {
                'page_title': 'Copy BOM',
                'source_wono': source_wono,
                'target_wono': target_wono
            })

        # Check if source BOM exists
        source_items = TbldgBomMaster.objects.filter(wono=source_wono)
        if not source_items.exists():
            messages.error(request, f'No BOM found for work order: {source_wono}')
            return render(request, self.template_name, {
                'page_title': 'Copy BOM',
                'source_wono': source_wono,
                'target_wono': target_wono
            })

        # Check if target already has BOM
        target_items = TbldgBomMaster.objects.filter(wono=target_wono)
        if target_items.exists():
            messages.error(request, f'Target work order {target_wono} already has a BOM. Please delete it first.')
            return render(request, self.template_name, {
                'page_title': 'Copy BOM',
                'source_wono': source_wono,
                'target_wono': target_wono
            })

        # Perform copy using service
        try:
            count = BomService.copy_bom(
                source_wono=source_wono,
                target_wono=target_wono,
                user_id=request.user.id
            )

            messages.success(request, f'Successfully copied {count} items from {source_wono} to {target_wono}')
            return redirect('design:bom-tree', wono=target_wono)

        except Exception as e:
            messages.error(request, f'Error copying BOM: {str(e)}')
            return render(request, self.template_name, {
                'page_title': 'Copy BOM',
                'source_wono': source_wono,
                'target_wono': target_wono
            })


class BomUpdateQuantityApiView(LoginRequiredMixin, View):
    """
    AJAX endpoint for inline quantity editing in BOM tree.
    Updates quantity for a BOM item and recalculates dependent nodes.
    """
    
    def post(self, request, *args, **kwargs):
        """Handle quantity update request."""
        try:
            import json
            from decimal import Decimal, InvalidOperation
            
            # Parse request data
            data = json.loads(request.body)
            cid = data.get('cid')
            new_qty = data.get('qty')
            
            # Validate inputs
            if not cid:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing BOM item ID (cid)'
                }, status=400)
            
            if new_qty is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing quantity value'
                }, status=400)
            
            # Convert and validate quantity
            try:
                new_qty = Decimal(str(new_qty))
                if new_qty <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'Quantity must be greater than zero'
                    }, status=400)
            except (ValueError, InvalidOperation):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid quantity format'
                }, status=400)
            
            # Get company and financial year from session
            compid = request.session.get('compid', 1)
            finyearid = request.session.get('finyearid', 1)
            
            # Find the BOM item
            try:
                bom_item = TbldgBomMaster.objects.get(
                    cid=cid,
                    compid=compid
                )
            except TbldgBomMaster.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'BOM item with CId {cid} not found'
                }, status=404)
            
            # Store old quantity for logging
            old_qty = bom_item.qty
            
            # Update quantity
            with transaction.atomic():
                bom_item.qty = float(new_qty)
                bom_item.save()
                
                # Log the change (optional - could create amendment record)
                logger.info(
                    f"Quantity updated for BOM item CId={cid}, "
                    f"WO={bom_item.wono}, "
                    f"Old Qty={old_qty}, New Qty={new_qty}, "
                    f"User={request.user.username}"
                )
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Quantity updated successfully',
                'data': {
                    'cid': cid,
                    'old_qty': float(old_qty) if old_qty else 0,
                    'new_qty': float(new_qty),
                    'item_code': bom_item.itemid.itemcode if bom_item.itemid else bom_item.partno
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error updating BOM quantity: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


# ============================================================================
# BOM WIZARD API ENDPOINTS
# ============================================================================

class BomSearchItemsApiView(LoginRequiredMixin, View):
    """
    AJAX endpoint for searching items in the Add Items wizard.
    Returns JSON with item list filtered by search query and category.
    """
    
    def get(self, request, *args, **kwargs):
        """Handle item search request."""
        try:
            # Get search parameters
            search_query = request.GET.get('q', '').strip()
            category_filter = request.GET.get('category', '').strip()
            
            compid = request.session.get('compid', 1)
            
            # Build query - TbldgItemMaster doesn't have ForeignKey to UOM, just stores ID
            items = TbldgItemMaster.objects.filter(compid=compid)
            
            # Apply search filter
            if search_query:
                items = items.filter(
                    Q(itemcode__icontains=search_query) |
                    Q(manfdesc__icontains=search_query) |
                    Q(partno__icontains=search_query)
                )
            
            # Apply category filter
            if category_filter:
                try:
                    items = items.filter(class_field=int(category_filter))
                except ValueError:
                    pass
            
            # Limit results and order
            items = items.order_by('manfdesc', 'itemcode')[:50]
            
            # Build response data
            items_data = []
            for item in items:
                # uombasic is just an integer ID, not a ForeignKey
                # We'll just use 'EA' as default for now
                # TODO: Join with UOM master table if needed
                uom_symbol = 'EA'
                
                items_data.append({
                    'id': item.id,
                    'itemcode': item.itemcode or item.partno or '',
                    'manfdesc': item.manfdesc or 'No description',
                    'class_field': item.class_field,
                    'uom': uom_symbol
                })
            
            return JsonResponse({
                'success': True,
                'items': items_data,
                'count': len(items_data)
            })
            
        except Exception as e:
            logger.error(f"Error searching items: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Search error: {str(e)}'
            }, status=500)


class BomStageItemApiView(LoginRequiredMixin, View):
    """
    AJAX endpoint to stage an item for addition to BOM.
    Stores item in session for review before committing.
    """
    
    def post(self, request, *args, **kwargs):
        """Handle stage item request."""
        try:
            import json
            
            # Parse request data
            data = json.loads(request.body)
            parent_cid = data.get('parent_cid')
            wono = data.get('wono')
            item_id = data.get('item_id')
            qty = data.get('qty', 1)
            
            # Validate inputs
            if not all([parent_cid, wono, item_id]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters'
                }, status=400)
            
            # Validate quantity
            try:
                qty = float(qty)
                if qty <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'Quantity must be greater than zero'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid quantity format'
                }, status=400)
            
            # Get item details
            try:
                item = TbldgItemMaster.objects.get(id=item_id)
            except TbldgItemMaster.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Item with ID {item_id} not found'
                }, status=404)
            
            # Check for duplicates in current BOM
            compid = request.session.get('compid', 1)
            existing = TbldgBomMaster.objects.filter(
                wono=wono,
                pid=parent_cid,
                itemid=item_id,
                compid=compid
            ).exists()
            
            if existing:
                return JsonResponse({
                    'success': False,
                    'error': f'Item {item.itemcode} is already in this BOM level',
                    'duplicate': True
                }, status=400)
            
            # Store in session
            session_key = f'bom_staged_{wono}_{parent_cid}'
            staged_items = request.session.get(session_key, [])
            
            # Check for duplicates in staged items
            for staged in staged_items:
                if staged.get('item_id') == item_id:
                    return JsonResponse({
                        'success': False,
                        'error': f'Item {item.itemcode} is already staged',
                        'duplicate': True
                    }, status=400)
            
            # Add to staged items
            # Note: uombasic is just an integer ID, not a ForeignKey
            # We'll use 'EA' as default for now
            staged_item = {
                'item_id': item_id,
                'itemcode': item.itemcode or item.partno,
                'manfdesc': item.manfdesc,
                'uom': 'EA',  # Default UOM since uombasic is just an ID
                'qty': qty,
                'class_field': item.class_field
            }
            staged_items.append(staged_item)
            request.session[session_key] = staged_items
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Item staged successfully',
                'staged_item': staged_item,
                'total_staged': len(staged_items)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error staging item: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


class BomGetStagedItemsApiView(LoginRequiredMixin, View):
    """
    AJAX endpoint to retrieve staged items for a parent.
    """
    
    def get(self, request, *args, **kwargs):
        """Handle get staged items request."""
        try:
            parent_cid = request.GET.get('parent_cid')
            wono = request.GET.get('wono')
            
            if not all([parent_cid, wono]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters'
                }, status=400)
            
            # Get from session
            session_key = f'bom_staged_{wono}_{parent_cid}'
            staged_items = request.session.get(session_key, [])
            
            return JsonResponse({
                'success': True,
                'staged_items': staged_items,
                'count': len(staged_items)
            })
            
        except Exception as e:
            logger.error(f"Error getting staged items: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


class BomUnstagItemApiView(LoginRequiredMixin, View):
    """
    AJAX endpoint to remove an item from staging.
    """
    
    def post(self, request, *args, **kwargs):
        """Handle unstage item request."""
        try:
            import json
            
            # Parse request data
            data = json.loads(request.body)
            parent_cid = data.get('parent_cid')
            wono = data.get('wono')
            item_index = data.get('item_index')
            
            # Validate inputs
            if not all([parent_cid, wono]) or item_index is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters'
                }, status=400)
            
            # Get from session
            session_key = f'bom_staged_{wono}_{parent_cid}'
            staged_items = request.session.get(session_key, [])
            
            # Remove item
            try:
                item_index = int(item_index)
                if 0 <= item_index < len(staged_items):
                    removed_item = staged_items.pop(item_index)
                    request.session[session_key] = staged_items
                    request.session.modified = True
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Item removed from staging',
                        'removed_item': removed_item,
                        'remaining_count': len(staged_items)
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid item index'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid item index format'
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error unstaging item: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


class BomCommitStagedItemsApiView(LoginRequiredMixin, View):
    """
    AJAX endpoint to commit all staged items to the BOM permanently.
    """
    
    def post(self, request, *args, **kwargs):
        """Handle commit staged items request."""
        try:
            import json
            from datetime import datetime
            
            # Parse request data
            data = json.loads(request.body)
            parent_cid = data.get('parent_cid')
            wono = data.get('wono')
            
            # Validate inputs
            if not all([parent_cid, wono]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters'
                }, status=400)
            
            # Get from session
            session_key = f'bom_staged_{wono}_{parent_cid}'
            staged_items = request.session.get(session_key, [])
            
            if not staged_items:
                return JsonResponse({
                    'success': False,
                    'error': 'No items to commit'
                }, status=400)
            
            # Get session data
            compid = request.session.get('compid', 1)
            finyearid = request.session.get('finyearid', 1)
            sessionid = str(request.user.id)
            now = datetime.now()
            
            # Get parent BOM item to inherit wono and finyearid
            try:
                parent_bom = TbldgBomMaster.objects.filter(
                    cid=parent_cid,
                    wono=wono,
                    compid=compid
                ).first()
                if not parent_bom:
                    return JsonResponse({
                        'success': False,
                        'error': f'Parent BOM item with CId {parent_cid} not found for WO {wono}'
                    }, status=404)
                wono = parent_bom.wono
                finyearid = parent_bom.finyearid
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error retrieving parent BOM: {str(e)}'
                }, status=500)

            # Validate level constraints
            from ..bom_services import BomService
            bom_service = BomService()
            parent_level = bom_service._calculate_node_level(parent_bom, wono, compid)
            
            logger.info(f"Commit validation: parent_cid={parent_cid}, parent_level={parent_level}, parent_pid={parent_bom.pid}")
            
            if parent_level >= 2:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot add items to Level {parent_level} (Parts). Maximum depth is 3 levels. Parent CId={parent_cid}, PId={parent_bom.pid}'
                }, status=400)
            
            # Commit items to database
            created_items = []
            with transaction.atomic():
                for item_data in staged_items:
                    # Get next CId
                    max_cid = TbldgBomMaster.objects.filter(compid=compid).aggregate(
                        max_cid=models.Max('cid')
                    )['max_cid'] or 0
                    next_cid = max_cid + 1
                    
                    # Create BOM item
                    bom_item = TbldgBomMaster.objects.create(
                        cid=next_cid,
                        pid=parent_cid,
                        wono=wono,
                        itemid_id=item_data['item_id'],
                        qty=item_data['qty'],
                        compid=compid,
                        finyearid=finyearid,
                        sysdate=now.strftime('%d-%m-%Y'),
                        systime=now.strftime('%H:%M:%S'),
                        sessionid=sessionid,
                        amdno=0,
                        revision='A',
                        ecn=0,
                        ecnflag=0
                    )
                    
                    created_items.append({
                        'cid': bom_item.cid,
                        'itemcode': item_data['itemcode'],
                        'manfdesc': item_data['manfdesc'],
                        'qty': item_data['qty']
                    })
            
            # Clear staged items from session
            del request.session[session_key]
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully added {len(created_items)} item(s) to BOM',
                'created_items': created_items,
                'count': len(created_items)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error committing staged items: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


class BomClearStagedItemsApiView(LoginRequiredMixin, View):
    """
    AJAX endpoint to clear all staged items without committing.
    """
    
    def post(self, request, *args, **kwargs):
        """Handle clear staged items request."""
        try:
            import json
            
            # Parse request data
            data = json.loads(request.body)
            parent_cid = data.get('parent_cid')
            wono = data.get('wono')
            
            # Validate inputs
            if not all([parent_cid, wono]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters'
                }, status=400)
            
            # Clear from session
            session_key = f'bom_staged_{wono}_{parent_cid}'
            if session_key in request.session:
                del request.session[session_key]
                request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Staged items cleared'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error clearing staged items: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


class BomBulkDeleteApiView(LoginRequiredMixin, View):
    """
    AJAX endpoint for bulk deletion of BOM items.
    Deletes multiple items and their children in a single transaction.
    """
    
    def post(self, request, *args, **kwargs):
        """Handle bulk delete request."""
        try:
            import json
            
            # Parse request data
            data = json.loads(request.body)
            cid_list = data.get('cid_list', [])
            wono = data.get('wono')
            
            # Validate inputs
            if not cid_list or not isinstance(cid_list, list):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing or invalid CID list'
                }, status=400)
            
            if not wono:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing work order number'
                }, status=400)
            
            # Get company from session
            compid = request.session.get('compid', 1)
            
            # Delete items and their children
            deleted_count = 0
            with transaction.atomic():
                for cid in cid_list:
                    # Get the item
                    try:
                        item = TbldgBomMaster.objects.get(
                            cid=cid,
                            wono=wono,
                            compid=compid
                        )
                        
                        # Delete this item and all its descendants
                        descendants = self._get_all_descendants(cid, wono, compid)
                        descendant_cids = [d.cid for d in descendants]
                        
                        # Delete descendants first
                        TbldgBomMaster.objects.filter(
                            cid__in=descendant_cids,
                            wono=wono,
                            compid=compid
                        ).delete()
                        
                        # Delete the item itself
                        item.delete()
                        
                        deleted_count += 1 + len(descendant_cids)
                        
                    except TbldgBomMaster.DoesNotExist:
                        logger.warning(f"BOM item CId={cid} not found, skipping")
                        continue
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully deleted {deleted_count} item(s)',
                'deleted_count': deleted_count
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in bulk delete: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)
    
    def _get_all_descendants(self, parent_cid, wono, compid):
        """Recursively get all descendants of a BOM item."""
        descendants = []
        children = TbldgBomMaster.objects.filter(
            pid=parent_cid,
            wono=wono,
            compid=compid
        )
        
        for child in children:
            descendants.append(child)
            descendants.extend(self._get_all_descendants(child.cid, wono, compid))
        
        return descendants
