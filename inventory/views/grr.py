"""
Goods Received Receipt (GRR) Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse

# Import core mixins instead of inventory-specific mixins
from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
    LoginRequiredMixin,
    CompanyFinancialYearMixin,
    HTMXResponseMixin,
    QueryOptimizationMixin,
)

from ..models import (
    TblGatepass,
    TblinvMaterialrequisitionMaster, TblinvMaterialrequisitionDetails,
    TblinvMaterialissueMaster, TblinvMaterialissueDetails,
    TblinvMaterialreturnMaster, TblinvMaterialreturnDetails,
    TblinvInwardMaster, TblinvInwardDetails,
    TblinvMaterialreceivedMaster, TblinvMaterialreceivedDetails,
    TblinvMaterialservicenoteMaster, TblinvMaterialservicenoteDetails,
    TblinvSupplierChallanMaster, TblinvSupplierChallanDetails,
    TblinvCustomerChallanMaster, TblinvCustomerChallanDetails,
    TblinvWisMaster, TblinvWisDetails,
    TblvehProcessMaster,
    TblinvAutowisTimeschedule,
)
from .. import forms
from ..forms import (
    MRSMasterForm,
    MINMasterForm,
    MRNMasterForm,
    VehicleProcessMasterForm,
    VehicleMasterForm,
    AutoWISTimeScheduleForm,
    StockLedgerFilterForm,
)
from ..services import (
    MaterialRequisitionService,
    MaterialIssueService,
    MaterialReturnService,
    DashboardService,
)


class GRRListView(BaseListViewMixin, ListView):
    """
    Goods Received Receipt List View
    Displays all GRR with full details including supplier, PO, GIN, and challan information.

    Converted from: aspnet/Module/Inventory/Transactions/GoodsReceivedReceipt_GRR_Edit.aspx
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    Requirements: 3.1, 3.4, 4.1, 5.5, 13.1
    """
    model = TblinvMaterialreceivedMaster
    template_name = 'inventory/transactions/grr_list.html'
    partial_template_name = 'inventory/transactions/partials/grr_list_partial.html'
    context_object_name = 'grr_list'
    paginate_by = 20
    search_fields = ['grrno', 'ginno']
    ordering = ['-id']

    def get_queryset(self):
        """Filter by company, financial year, and optional supplier search."""
        queryset = super().get_queryset()

        # Get supplier search parameter
        supplier_search = self.request.GET.get('supplier', '').strip()

        if supplier_search:
            # Search in GIN's PO supplier
            from django.db import connection
            with connection.cursor() as cursor:
                # Get supplier ID from search text (format: "Supplier Name [CODE]")
                supplier_id = None
                if '[' in supplier_search and ']' in supplier_search:
                    supplier_id = supplier_search.split('[')[-1].replace(']', '').strip()

                if supplier_id:
                    # Filter GRR by supplier through GIN and PO
                    queryset = queryset.extra(
                        where=["""
                            EXISTS (
                                SELECT 1 FROM tblInv_Inward_Master gin
                                INNER JOIN tblMM_PO_Master po ON gin.POMId = po.Id
                                WHERE gin.Id = tblinv_MaterialReceived_Master.GINId
                                AND po.SupplierId = %s
                            )
                        """],
                        params=[supplier_id]
                    )

        return queryset

    def get_context_data(self, **kwargs):
        """Add enriched GRR data with supplier, PO, GIN, and challan information using Django ORM."""
        context = super().get_context_data(**kwargs)
        context['supplier_search'] = self.request.GET.get('supplier', '')

        from sys_admin.models import TblfinancialMaster
        from material_management.models import POMaster, Supplier

        # Enrich each GRR with additional data using Django ORM
        enriched_grr_list = []
        for grr in context['grr_list']:
            enriched_grr = {
                'id': grr.id,
                'grrno': grr.grrno,
                'sysdate': grr.sysdate if isinstance(grr.sysdate, str) else (grr.sysdate.strftime('%d-%m-%Y') if grr.sysdate else ''),
                'ginno': grr.ginno or '-',
                'ginid': grr.ginid,
                'finyearid': grr.finyearid,
                'finyear_name': '2022-2023',
                'pono': '-',
                'supplier_name': '-',
                'supplier_id': '',
                'challan_no': '-',
                'challan_date': '-',
            }

            # Get financial year using ORM
            try:
                finyear = TblfinancialMaster.objects.get(finyearid=grr.finyearid)
                enriched_grr['finyear_name'] = finyear.finyear
            except TblfinancialMaster.DoesNotExist:
                pass

            # Get GIN and related PO/Supplier data using ORM
            try:
                gin = TblinvInwardMaster.objects.get(id=grr.ginid)
                enriched_grr['challan_no'] = gin.challanno or '-'
                if gin.challandate:
                    # Handle both string and date object
                    if isinstance(gin.challandate, str):
                        enriched_grr['challan_date'] = gin.challandate
                    else:
                        enriched_grr['challan_date'] = gin.challandate.strftime('%d-%m-%Y')

                # Get PO using ORM - match by PONo and CompId
                if gin.pono:
                    try:
                        po = POMaster.objects.filter(
                            po_no=gin.pono,
                            comp_id=self.get_compid()
                        ).first()

                        if po:
                            enriched_grr['pono'] = po.po_no or '-'

                            # Get Supplier using ORM
                            if po.supplier_id:
                                try:
                                    supplier = Supplier.objects.get(supplier_id=po.supplier_id)
                                    enriched_grr['supplier_name'] = f"{supplier.supplier_name} [{supplier.supplier_id}]"
                                    enriched_grr['supplier_id'] = supplier.supplier_id
                                except Supplier.DoesNotExist:
                                    pass
                    except Exception:
                        pass
            except TblinvInwardMaster.DoesNotExist:
                pass

            enriched_grr_list.append(enriched_grr)

        context['enriched_grr_list'] = enriched_grr_list
        return context



class GRRCreateView(BaseCreateViewMixin, CreateView):
    """
    Goods Received Receipt Create View
    Create new GRR from pending GIN.

    Optimized: Uses BaseCreateViewMixin with automatic audit fields and success messages.
    Requirements: 3.1, 3.2, 4.1, 4.2, 13.2
    """
    model = TblinvMaterialreceivedMaster
    form_class = forms.GRRMasterForm
    template_name = 'inventory/transactions/grr_form.html'
    partial_template_name = 'inventory/transactions/partials/grr_form_partial.html'
    success_url = reverse_lazy('inventory:grr-list')
    success_message = 'GRR %(grrno)s created successfully! Stock updated.'

    def get_form_kwargs(self):
        """Pass company, financial year, and session to form."""
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.get_compid()
        kwargs['finyearid'] = self.get_finyearid()
        kwargs['sessionid'] = self.get_sessionid()
        return kwargs

    def get_context_data(self, **kwargs):
        """Add auto-generated GRR number and GIN details with balance calculations."""
        from inventory.services import GoodsReceiptService, GoodsInwardService
        from material_management.models import PODetails, PRDetails, SPRDetails
        from design.models import TbldgItemMaster

        context = super().get_context_data(**kwargs)

        # Auto-generate GRR number
        context['auto_grr_number'] = GoodsReceiptService.generate_grr_number(
            self.get_compid(),
            self.get_finyearid()
        )

        # Get GIN details if gin_id is provided
        gin_id = self.request.GET.get('gin_id') or self.kwargs.get('gin_id')
        if not gin_id:
            messages.error(self.request, 'No GIN selected. Please select a GIN from the pending list.')
            return context

        try:
            gin = TblinvInwardMaster.objects.get(id=gin_id, compid=self.get_compid())
            context['selected_gin'] = gin

            # Get all GIN detail items
            gin_details = TblinvInwardDetails.objects.filter(ginid=gin.id).order_by('id')

            # Enrich each item with balance calculation and item details
            enriched_items = []
            for gin_detail in gin_details:
                # Calculate balance quantity
                inward_qty = gin_detail.qty or 0

                # Get all GRR master IDs for this GIN
                grr_master_ids = TblinvMaterialreceivedMaster.objects.filter(
                    ginid=gin.id
                ).values_list('id', flat=True)

                # Get received quantity for this PO detail
                received_qty = TblinvMaterialreceivedDetails.objects.filter(
                    poid=gin_detail.poid,
                    mid__in=grr_master_ids
                ).aggregate(total=Sum('receivedqty'))['total'] or 0
                balance_qty = inward_qty - received_qty

                # Only include items with balance > 0
                if balance_qty <= 0:
                    continue

                # Get PO details
                try:
                    po_detail = PODetails.objects.get(id=gin_detail.poid)
                    po_qty = po_detail.qty or 0

                    # Get basic item info from PO
                    item_code = f"PO-{po_detail.id}"
                    item_description = po_detail.add_desc or f"PO Detail #{po_detail.id}"
                    uom = "PCS"  # Default UOM

                    enriched_items.append({
                        'gin_detail_id': gin_detail.id,
                        'po_detail_id': gin_detail.poid,
                        'item_code': item_code or '-',
                        'item_description': item_description or '-',
                        'uom': uom or '-',
                        'po_qty': po_qty,
                        'inward_qty': inward_qty,
                        'received_qty': received_qty,
                        'balance_qty': balance_qty,
                    })
                except PODetails.DoesNotExist:
                    pass

            context['gin_items'] = enriched_items

        except TblinvInwardMaster.DoesNotExist:
            messages.error(self.request, f'GIN with ID {gin_id} not found.')

        return context

    def form_valid(self, form):
        """Save GRR master and detail records atomically."""
        from django.db import transaction
        from inventory.services import GoodsReceiptService
        from datetime import datetime

        # Validate that at least one item is selected
        selected_items = [
            key for key in self.request.POST.keys()
            if key.startswith('item_selected_')
        ]

        if not selected_items:
            messages.error(self.request, 'Please select at least one item to receive.')
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                # Generate GRR number
                form.instance.grrno = GoodsReceiptService.generate_grr_number(
                    self.get_compid(),
                    self.get_finyearid()
                )

                # Get GIN details
                gin_id = self.request.GET.get('gin_id') or self.kwargs.get('gin_id')
                gin = TblinvInwardMaster.objects.get(id=gin_id)
                form.instance.ginno = gin.ginno
                form.instance.ginid = gin.id

                # Save master record
                grr_master = form.save()

                # Save detail records for selected items
                detail_count = 0
                for item_key in selected_items:
                    # Extract po_detail_id from key (format: item_selected_XXX)
                    po_detail_id = item_key.replace('item_selected_', '')
                    received_qty_key = f'received_qty_{po_detail_id}'
                    received_qty = self.request.POST.get(received_qty_key)

                    if received_qty:
                        try:
                            received_qty = float(received_qty)
                            if received_qty > 0:
                                # Validate against balance
                                is_valid, error_msg, balance = GoodsReceiptService.validate_receive_quantity(
                                    int(po_detail_id),  # This is actually gin_detail_id passed as poid
                                    received_qty
                                )

                                if not is_valid:
                                    raise ValueError(f"Item {po_detail_id}: {error_msg}")

                                # Create detail record
                                TblinvMaterialreceivedDetails.objects.create(
                                    mid=grr_master.id,
                                    grrno=grr_master.grrno,
                                    poid=po_detail_id,
                                    receivedqty=received_qty
                                )
                                detail_count += 1
                        except (ValueError, TypeError) as e:
                            raise ValueError(f"Invalid received quantity for item {po_detail_id}: {str(e)}")

                if detail_count == 0:
                    raise ValueError("No valid items with received quantities found.")

                # Update stock ledger
                GoodsReceiptService.update_stock_ledger(grr_master)

                messages.success(
                    self.request,
                    f'GRR {grr_master.grrno} created successfully with {detail_count} item(s)! Stock updated.'
                )
                return redirect(self.success_url)

        except Exception as e:
            messages.error(self.request, f'Error creating GRR: {str(e)}')
            return self.form_invalid(form)



class GRRDetailView(BaseDetailViewMixin, DetailView):
    """
    Goods Received Receipt Detail View
    View GRR details with line items.
    
    Optimized: Uses BaseDetailViewMixin with automatic company filtering.
    Requirements: 3.1, 4.1, 13.1
    """
    model = TblinvMaterialreceivedMaster
    template_name = 'inventory/transactions/grr_detail.html'
    context_object_name = 'grr'
    
    def get_context_data(self, **kwargs):
        """Add GRR details, GIN info, and totals to context."""
        context = super().get_context_data(**kwargs)
        
        # Get GRR details
        context['grr_details'] = TblinvMaterialreceivedDetails.objects.filter(
            mid=self.object.id
        )
        
        # Get GIN information
        try:
            context['gin'] = TblinvInwardMaster.objects.get(id=self.object.ginid)
        except:
            context['gin'] = None
        
        # Calculate totals
        total_qty = sum(detail.receivedqty or 0 for detail in context['grr_details'])
        context['total_qty'] = total_qty
        
        return context



class GRRDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Goods Received Receipt Delete View
    Delete GRR with stock reversal.
    
    Optimized: Uses BaseDeleteViewMixin with automatic HTMX support.
    Requirements: 3.1, 4.1, 13.2
    """
    model = TblinvMaterialreceivedMaster
    template_name = 'inventory/transactions/grr_confirm_delete.html'
    success_url = reverse_lazy('inventory:grr-list')
    context_object_name = 'grr'
    
    def delete(self, request, *args, **kwargs):
        """Delete and reverse stock entries."""
        self.object = self.get_object()
        
        # Reverse stock entries
        from inventory.services import GoodsReceiptService
        GoodsReceiptService.reverse_stock_on_delete(self.object.id)
        
        messages.success(request, f'GRR {self.object.grrno} deleted successfully! Stock reversed.')
        return super().delete(request, *args, **kwargs)



class GRRPrintView(BaseDetailViewMixin, DetailView):
    """
    Goods Received Receipt Print View
    Print-friendly GRR document.
    
    Optimized: Uses BaseDetailViewMixin with automatic company filtering.
    Requirements: 3.1, 4.1
    """
    model = TblinvMaterialreceivedMaster
    template_name = 'inventory/transactions/grr_print.html'
    context_object_name = 'grr'
    
    def get_context_data(self, **kwargs):
        """Add GRR details, GIN info, and totals to context."""
        context = super().get_context_data(**kwargs)
        
        # Get GRR details
        context['grr_details'] = TblinvMaterialreceivedDetails.objects.filter(
            mid=self.object.id
        )
        
        # Get GIN information
        try:
            context['gin'] = TblinvInwardMaster.objects.get(id=self.object.ginid)
        except:
            context['gin'] = None
        
        # Calculate totals
        total_qty = sum(detail.receivedqty or 0 for detail in context['grr_details'])
        context['total_qty'] = total_qty
        
        return context



class GRREditListView(BaseListViewMixin, ListView):
    """
    Goods Received Receipt Edit List View
    Shows all GRR records with search by supplier for editing.

    Converted from: aspnet/Module/Inventory/Transactions/GoodsReceivedReceipt_GRR_Edit.aspx
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    Requirements: 3.1, 3.4, 4.1, 5.5, 13.1
    """
    model = TblinvMaterialreceivedMaster
    template_name = 'inventory/transactions/grr_edit_list.html'
    partial_template_name = 'inventory/transactions/partials/grr_edit_list_partial.html'
    context_object_name = 'grr_list'
    paginate_by = 20
    ordering = ['-id']

    def get_queryset(self):
        """Filter by company, financial year, and optional supplier search."""
        queryset = super().get_queryset()

        # Get supplier search parameter
        supplier_search = self.request.GET.get('supplier', '').strip()

        if supplier_search:
            # Search in GIN's PO supplier
            # We need to join through GIN -> PO -> Supplier
            from django.db import connection
            with connection.cursor() as cursor:
                # Get supplier ID from search text (format: "Supplier Name [CODE]")
                supplier_id = None
                if '[' in supplier_search and ']' in supplier_search:
                    supplier_id = supplier_search.split('[')[-1].replace(']', '').strip()

                if supplier_id:
                    # Filter GRR by supplier through GIN and PO
                    queryset = queryset.extra(
                        where=["""
                            EXISTS (
                                SELECT 1 FROM tblInv_Inward_Master gin
                                INNER JOIN tblMM_PO_Master po ON gin.POMId = po.Id
                                WHERE gin.Id = tblinv_MaterialReceived_Master.GINId
                                AND po.SupplierId = %s
                            )
                        """],
                        params=[supplier_id]
                    )

        return queryset

    def get_context_data(self, **kwargs):
        """Add enriched GRR data with supplier, PO, GIN, and challan information using Django ORM."""
        context = super().get_context_data(**kwargs)
        context['supplier_search'] = self.request.GET.get('supplier', '')

        from sys_admin.models import TblfinancialMaster
        from material_management.models import POMaster, Supplier

        # Enrich each GRR with additional data using Django ORM
        enriched_grr_list = []
        for grr in context['grr_list']:
            enriched_grr = {
                'id': grr.id,
                'grrno': grr.grrno,
                'sysdate': grr.sysdate if isinstance(grr.sysdate, str) else (grr.sysdate.strftime('%d-%m-%Y') if grr.sysdate else ''),
                'ginno': grr.ginno or '-',
                'ginid': grr.ginid,
                'finyearid': grr.finyearid,
                'finyear_name': '2022-2023',
                'pono': '-',
                'supplier_name': '-',
                'supplier_id': '',
                'challan_no': '-',
                'challan_date': '-',
            }

            # Get financial year using ORM
            try:
                finyear = TblfinancialMaster.objects.get(finyearid=grr.finyearid)
                enriched_grr['finyear_name'] = finyear.finyear
            except TblfinancialMaster.DoesNotExist:
                pass

            # Get GIN and related PO/Supplier data using ORM
            try:
                gin = TblinvInwardMaster.objects.get(id=grr.ginid)
                enriched_grr['challan_no'] = gin.challanno or '-'
                if gin.challandate:
                    # Handle both string and date object
                    if isinstance(gin.challandate, str):
                        enriched_grr['challan_date'] = gin.challandate
                    else:
                        enriched_grr['challan_date'] = gin.challandate.strftime('%d-%m-%Y')

                # Get PO using ORM - match by PONo and CompId
                if gin.pono:
                    try:
                        po = POMaster.objects.filter(
                            po_no=gin.pono,
                            comp_id=self.get_compid()
                        ).first()

                        if po:
                            enriched_grr['pono'] = po.po_no or '-'

                            # Get Supplier using ORM
                            if po.supplier_id:
                                try:
                                    supplier = Supplier.objects.get(supplier_id=po.supplier_id)
                                    enriched_grr['supplier_name'] = f"{supplier.supplier_name} [{supplier.supplier_id}]"
                                    enriched_grr['supplier_id'] = supplier.supplier_id
                                except Supplier.DoesNotExist:
                                    pass
                    except Exception:
                        pass
            except TblinvInwardMaster.DoesNotExist:
                pass

            enriched_grr_list.append(enriched_grr)

        context['enriched_grr_list'] = enriched_grr_list
        return context



class GRREditDetailView(BaseUpdateViewMixin, UpdateView):
    """
    Goods Received Receipt Edit Detail View
    Edit received quantities for GRR line items with inline editing.
    
    Converted from: aspnet/Module/Inventory/Transactions/GoodsReceivedReceipt_GRR_Edit_Details.aspx
    Optimized: Uses HTMX for inline editing of received quantities.
    Requirements: 3.1, 3.2, 4.1, 4.2, 13.2
    """
    model = TblinvMaterialreceivedMaster
    template_name = 'inventory/transactions/grr_edit_detail.html'
    context_object_name = 'grr'
    fields = []  # No form fields needed, we handle details separately
    success_url = reverse_lazy('inventory:grr-edit-list')
    
    def get_context_data(self, **kwargs):
        """Add GRR details with enriched item information for editing."""
        context = super().get_context_data(**kwargs)
        
        # Get GIN information
        gin = None
        try:
            gin = TblinvInwardMaster.objects.get(id=self.object.ginid)
            context['gin'] = gin
            context['challan_no'] = gin.challanno
            context['challan_date'] = gin.challandate
        except:
            context['gin'] = None
            context['challan_no'] = ''
            context['challan_date'] = ''
        
        # Get supplier information
        supplier_name = ''
        if gin and gin.pomid:
            try:
                from material_management.models import TblmmPoMaster, TblmmSupplierMaster
                po = TblmmPoMaster.objects.get(po_id=gin.pomid)
                if po.supplier_id:
                    try:
                        supplier = TblmmSupplierMaster.objects.get(supplierid=po.supplier_id)
                        supplier_name = f"{supplier.suppliername} [{supplier.supplierid}]"
                    except:
                        pass
            except:
                pass
        context['supplier_name'] = supplier_name
        
        # Get GRR details with enriched item information
        grr_details = TblinvMaterialreceivedDetails.objects.filter(mid=self.object.id)
        enriched_details = []
        
        for detail in grr_details:
            enriched_item = {
                'id': detail.id,
                'poid': detail.poid,
                'receivedqty': detail.receivedqty or 0,
                'item_code': '',
                'description': '',
                'uom': '',
                'po_qty': 0,
                'inward_qty': 0,
                'total_recd_qty': 0,
                'image_filename': '',
                'spec_filename': '',
            }
            
            # Get PO detail information
            if detail.poid:
                try:
                    from material_management.models import TblmmPoDetails, TblmmItemMaster
                    po_detail = TblmmPoDetails.objects.get(id=detail.poid)
                    enriched_item['po_qty'] = po_detail.qty or 0
                    
                    # Get item information
                    if po_detail.itemid:
                        try:
                            item = TblmmItemMaster.objects.get(itemid=po_detail.itemid)
                            enriched_item['item_code'] = item.itemcode or ''
                            enriched_item['description'] = item.purchasedescription or ''
                            enriched_item['uom'] = item.uompurch or ''
                            enriched_item['image_filename'] = item.filename or ''
                            enriched_item['spec_filename'] = item.attname or ''
                        except:
                            pass
                except:
                    pass
            
            # Get inward quantity from GIN details
            if gin:
                try:
                    gin_detail = TblinvInwardDetails.objects.get(
                        ginid=gin.id,
                        poid=detail.poid
                    )
                    enriched_item['inward_qty'] = gin_detail.qty or 0
                except:
                    pass
            
            # Calculate total received quantity (sum of all GRR for this PO item)
            total_recd = TblinvMaterialreceivedDetails.objects.filter(
                poid=detail.poid
            ).aggregate(Sum('receivedqty'))['receivedqty__sum'] or 0
            enriched_item['total_recd_qty'] = total_recd
            
            enriched_details.append(enriched_item)
        
        context['grr_details'] = enriched_details
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle HTMX inline edit of received quantity."""
        self.object = self.get_object()
        
        # Check if this is an HTMX request for inline edit
        if request.headers.get('HX-Request'):
            detail_id = request.POST.get('detail_id')
            new_qty = request.POST.get('receivedqty')
            
            if detail_id and new_qty:
                try:
                    detail = TblinvMaterialreceivedDetails.objects.get(
                        id=detail_id,
                        mid=self.object.id
                    )
                    
                    # Validate quantity
                    try:
                        new_qty = float(new_qty)
                        if new_qty < 0:
                            return HttpResponse(
                                '<span class="text-red-600">Quantity cannot be negative</span>',
                                status=400
                            )
                    except ValueError:
                        return HttpResponse(
                            '<span class="text-red-600">Invalid quantity format</span>',
                            status=400
                        )
                    
                    # Update the quantity
                    old_qty = detail.receivedqty or 0
                    detail.receivedqty = new_qty
                    detail.save()
                    
                    # Update stock ledger (reverse old, add new)
                    from inventory.services import GoodsReceiptService
                    GoodsReceiptService.update_stock_on_edit(
                        detail.poid,
                        old_qty,
                        new_qty,
                        self.get_compid(),
                        self.get_finyearid()
                    )
                    
                    messages.success(request, f'Received quantity updated successfully!')
                    
                    # Return the updated row
                    return render(request, 'inventory/transactions/partials/grr_edit_row.html', {
                        'detail': detail,
                        'grr': self.object,
                    })
                    
                except TblinvMaterialreceivedDetails.DoesNotExist:
                    return HttpResponse(
                        '<span class="text-red-600">Detail not found</span>',
                        status=404
                    )
        
        # Regular form submission (redirect to list)
        messages.success(request, f'GRR {self.object.grrno} updated successfully!')
        return redirect(self.success_url)




