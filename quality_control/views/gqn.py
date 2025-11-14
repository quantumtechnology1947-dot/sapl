"""
Goods Quality Note (GQN) Views

Multi-step workflow for GQN creation and management:
1. List pending GRR records
2. Select GRR and enter quality inspection data
3. Create GQN
4. Manage existing GQNs (CRUD)
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.db.models import Subquery, OuterRef, CharField, Value
from django.db.models.functions import Coalesce
from datetime import datetime

from .base import QualityControlBaseMixin
from quality_control.models import TblqcMaterialqualityMaster, TblqcRejectionReason
from quality_control.forms import GoodsQualityNoteForm, GoodsQualityNoteDetailFormSet
from quality_control.services import GQNGRRService, GQNCreationService


class GQNNewView(QualityControlBaseMixin, TemplateView):
    """
    GQN Step 1: List pending GRR records for quality inspection
    Converted from: GoodsQualityNote_GQN_New.aspx
    """
    template_name = 'quality_control/gqn/grr_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get search parameters
        search_type = self.request.GET.get('search_type', '0')  # 0=Supplier, 1=GRR No, 2=PO No
        search_value = self.request.GET.get('search_value', '')

        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get pending GRR records using service
        pending_grrs = GQNGRRService.get_pending_grr_records(
            compid,
            finyearid,
            search_type if search_value else None,
            search_value if search_value else None
        )

        context['pending_grrs'] = pending_grrs
        context['search_type'] = search_type
        context['search_value'] = search_value

        return context


class GQNGRRDetailsView(QualityControlBaseMixin, TemplateView):
    """
    GQN Step 2: Show GRR details and quality inspection form
    Converted from: GoodsQualityNote_GQN_New_Details.aspx
    """
    template_name = 'quality_control/gqn/grr_details.html'

    def get(self, request, grr_id):
        from inventory.models import TblinvInwardMaster
        from material_management.models import Supplier, POMaster

        try:
            # Get GRR with details using service
            grr_master, grr_details = GQNGRRService.get_grr_with_details(grr_id)

            # Get related GIN info
            gin = None
            supplier = None
            po_no = None
            challan_no = None
            challan_date = None

            if grr_master.ginid:
                try:
                    gin = TblinvInwardMaster.objects.get(id=grr_master.ginid)
                    if gin.pomid:
                        po = POMaster.objects.get(po_id=gin.pomid)
                        po_no = po.po_no
                        if po.supplier_id:
                            supplier = Supplier.objects.get(supplier_id=po.supplier_id)
                    challan_no = gin.challanno
                    challan_date = gin.challandate
                except Exception as e:
                    print(f"Warning: Could not get GIN/PO/Supplier info: {e}")
                    po_no = "TEST-PO"
                    challan_no = "TEST-CHALLAN"
                    challan_date = grr_master.sysdate

            # Get rejection reasons for dropdown
            rejection_reasons = TblqcRejectionReason.objects.all()

            # Enrich GRR details with item information
            enriched_details = []
            for detail in grr_details:
                enriched_detail = {
                    'id': detail.id,
                    'receivedqty': detail.receivedqty,
                    'poid': detail.poid,
                    'item_code': 'TEST-ITEM',
                    'description': 'Test Item Description',
                    'uom': 'NOS',
                    'po_qty': detail.receivedqty,
                    'inward_qty': detail.receivedqty,
                }

                # Try to get real item information if PO exists
                try:
                    from material_management.models import PODetails
                    from design.models import TbldgItemMaster

                    po_detail = PODetails.objects.get(po_detail_id=detail.poid)
                    if po_detail.item_id:
                        item = TbldgItemMaster.objects.get(id=po_detail.item_id)
                        enriched_detail.update({
                            'item_code': item.itemcode or 'N/A',
                            'description': item.manfdesc or 'N/A',
                            'uom': 'NOS',
                            'po_qty': po_detail.qty or 0,
                        })
                except Exception as e:
                    print(f"Warning: Could not get item info for detail {detail.id}: {e}")
                    pass

                enriched_details.append(enriched_detail)

            context = {
                'grr_master': grr_master,
                'grr_details': enriched_details,
                'gin': gin,
                'supplier': supplier,
                'po_no': po_no,
                'challan_no': challan_no,
                'challan_date': challan_date,
                'rejection_reasons': rejection_reasons,
            }

            return self.render_to_response(context)

        except Exception as e:
            messages.error(request, f'Error loading GRR details: {str(e)}')
            return redirect('quality_control:gqn-new')

    def post(self, request, grr_id):
        """Save GQN with quality inspection data"""
        from inventory.models import TblinvMaterialreceivedMaster

        # Get GRR info
        grr = TblinvMaterialreceivedMaster.objects.get(id=grr_id)

        # Parse quality inspection data from form
        quality_data = []
        item_ids = request.POST.getlist('item_id')

        for item_id in item_ids:
            # Check if this item was selected (checked)
            if request.POST.get(f'selected_{item_id}'):
                # Get all quantity values
                normal_acc_qty = float(request.POST.get(f'normal_acc_qty_{item_id}', 0) or 0)
                accepted_qty = float(request.POST.get(f'accepted_qty_{item_id}', 0) or 0)
                deviated_qty = float(request.POST.get(f'deviated_qty_{item_id}', 0) or 0)
                segregated_qty = float(request.POST.get(f'segregated_qty_{item_id}', 0) or 0)
                rejected_qty = float(request.POST.get(f'rejected_qty_{item_id}', 0) or 0)
                
                quality_data.append({
                    'grr_detail_id': int(item_id),
                    'normal_acc_qty': normal_acc_qty,
                    'accepted_qty': accepted_qty,
                    'deviated_qty': deviated_qty,
                    'segregated_qty': segregated_qty,
                    'rejected_qty': rejected_qty,
                    'rejection_reason': int(request.POST.get(f'rejection_reason_{item_id}') or 0) if request.POST.get(f'rejection_reason_{item_id}') else None,
                    'sn': request.POST.get(f'sn_{item_id}', ''),
                    'pn': request.POST.get(f'pn_{item_id}', ''),
                    'remarks': request.POST.get(f'remarks_{item_id}', ''),
                })

        if not quality_data:
            messages.error(request, 'Please select at least one item and enter quality inspection data!')
            return redirect('quality_control:gqn-grr-details', grr_id=grr_id)

        try:
            # Create GQN using service
            gqn = GQNCreationService.create_gqn_from_grr(
                self.get_compid(),
                self.get_finyearid(),
                request.user.id,
                grr_id,
                grr.grrno,
                quality_data
            )

            messages.success(request, f'GQN {gqn.gqnno} created successfully!')
            return redirect('quality_control:gqn-list')

        except Exception as e:
            messages.error(request, f'Error creating GQN: {str(e)}')
            return redirect('quality_control:gqn-grr-details', grr_id=grr_id)


class GoodsQualityNoteListViewOLD(QualityControlBaseMixin, ListView):
    """
    List all Goods Quality Notes
    Converted from: aaspnet/QualityControl/Transactions/GoodsQualityNote_GQN_Edit.aspx
    
    Columns match ASP.NET exactly:
    - SN (Serial Number)
    - Select (NA - not editable in this view)
    - Fin Year
    - GQN No
    - Date
    - GRR No
    - GIN No
    - PO No
    - Name of Supplier
    - Challan No
    - Challan Date
    """
    model = TblqcMaterialqualityMaster
    template_name = 'quality_control/gqn/list.html'
    context_object_name = 'gqns'
    paginate_by = 20

    def get_template_names(self):
        """Return partial template for HTMX requests"""
        if self.request.headers.get('HX-Request'):
            return ['quality_control/gqn/partials/gqn_table_partial.html']
        return [self.template_name]

    def get_queryset(self):
        """
        Get GQN records with related data using Django ORM subqueries.
        
        CRITICAL: Relationship chain discovered through reverse engineering:
        - GQN.GRRId -> GRR.Id
        - GRR.GINId -> GIN.Id  
        - GIN.PONo -> PO.PONo (NOT GIN.POMId -> PO.Id! POMId values don't match PO.Id range)
        - PO.SupplierId -> Supplier.SupplierId
        """
        from inventory.models import TblinvMaterialreceivedMaster, TblinvInwardMaster
        from material_management.models import POMaster, Supplier
        from sys_admin.models import TblfinancialMaster

        # Base queryset filtered by company  
        # PERFORMANCE: Only select needed fields to speed up query
        queryset = TblqcMaterialqualityMaster.objects.filter(
            compid=self.get_compid()
        ).only('id', 'gqnno', 'sysdate', 'grrno', 'grrid', 'finyearid', 'compid')

        # Don't filter by financial year for now - show all records
        # TODO: Add financial year filter once we confirm data exists
        # finyearid = self.request.session.get('finyearid')
        # if finyearid and finyearid != 'all':
        #     queryset = queryset.filter(finyearid=finyearid)

        # Step 1: Get Financial Year name
        finyear_subquery = TblfinancialMaster.objects.filter(
            finyearid=OuterRef('finyearid')
        ).values('finyear')[:1]

        # Step 2: Get GIN Number and GIN ID from GRR
        grr_ginno_subquery = TblinvMaterialreceivedMaster.objects.filter(
            id=OuterRef('grrid')
        ).values('ginno')[:1]

        grr_ginid_subquery = TblinvMaterialreceivedMaster.objects.filter(
            id=OuterRef('grrid')
        ).values('ginid')[:1]

        # First annotation: Financial Year and GIN info from GRR
        queryset = queryset.annotate(
            finyearname=Coalesce(
                Subquery(finyear_subquery, output_field=CharField()),
                Value('-')
            ),
            ginno=Coalesce(
                Subquery(grr_ginno_subquery, output_field=CharField()),
                Value('-')
            ),
            ginid_from_grr=Subquery(grr_ginid_subquery),
        )

        # Step 3: Get PO Number and Challan info from GIN
        gin_pono_subquery = TblinvInwardMaster.objects.filter(
            id=OuterRef('ginid_from_grr')
        ).values('pono')[:1]

        gin_challanno_subquery = TblinvInwardMaster.objects.filter(
            id=OuterRef('ginid_from_grr')
        ).values('challanno')[:1]

        gin_challandate_subquery = TblinvInwardMaster.objects.filter(
            id=OuterRef('ginid_from_grr')
        ).values('challandate')[:1]

        # Second annotation: PO Number and Challan info from GIN
        queryset = queryset.annotate(
            pono_from_gin=Coalesce(
                Subquery(gin_pono_subquery, output_field=CharField()),
                Value('-')
            ),
            challanno=Coalesce(
                Subquery(gin_challanno_subquery, output_field=CharField()),
                Value('-')
            ),
            challandate=Coalesce(
                Subquery(gin_challandate_subquery, output_field=CharField()),
                Value('-')
            ),
        )

        # Step 4: Get Supplier ID from PO using PONo (NOT POMId!)
        # CRITICAL FIX: Link GIN.PONo to PO.PONo, not GIN.POMId to PO.Id
        po_supplierid_subquery = POMaster.objects.filter(
            po_no=OuterRef('pono_from_gin'),
            comp_id=self.get_compid()
        ).values('supplier_id')[:1]

        # Third annotation: Supplier ID from PO
        queryset = queryset.annotate(
            supplierid_from_po=Subquery(po_supplierid_subquery, output_field=CharField()),
        )

        # Step 5: Get Supplier Name from Supplier
        supplier_name_subquery = Supplier.objects.filter(
            supplier_id=OuterRef('supplierid_from_po')
        ).values('supplier_name')[:1]

        # Final annotation: Supplier Name
        queryset = queryset.annotate(
            suppliername=Coalesce(
                Subquery(supplier_name_subquery, output_field=CharField()),
                Value('-')
            ),
        )

        # Order by ID descending (newest first)
        queryset = queryset.order_by('-id')

        # Handle search filters
        search_by = self.request.GET.get('search_by', '0')
        search_value = self.request.GET.get('search_value', '').strip()

        if search_value:
            if search_by == '0':  # Supplier Name
                queryset = queryset.filter(suppliername__icontains=search_value)
            elif search_by == '1':  # GQN No
                queryset = queryset.filter(gqnno__icontains=search_value)
            elif search_by == '2':  # GRR No
                queryset = queryset.filter(grrno__icontains=search_value)
            elif search_by == '3':  # PO No
                queryset = queryset.filter(pono_from_gin__icontains=search_value)

        return queryset

    def get_context_data(self, **kwargs):
        """Add table headers and formatted rows matching ASP.NET structure"""
        context = super().get_context_data(**kwargs)
        
        # Define table headers matching ASP.NET GoodsQualityNote_GQN_Edit.aspx
        context['table_headers'] = [
            {'text': 'SN', 'align': 'right', 'width': 'w-12'},
            {'text': 'Select', 'align': 'center', 'width': 'w-16'},
            {'text': 'Fin Year', 'align': 'center', 'width': 'w-24'},
            {'text': 'GQN No', 'align': 'center', 'width': 'w-28'},
            {'text': 'Date', 'align': 'center', 'width': 'w-24'},
            {'text': 'GRR No', 'align': 'center', 'width': 'w-28'},
            {'text': 'GIN No', 'align': 'center', 'width': 'w-28'},
            {'text': 'PO No', 'align': 'center', 'width': 'w-28'},
            {'text': 'Name of Supplier', 'align': 'left', 'width': 'w-64'},
            {'text': 'Challan No', 'align': 'center', 'width': 'w-28'},
            {'text': 'Challan Date', 'align': 'center', 'width': 'w-28'},
        ]
        
        # Format rows for table component
        rows = []
        page_obj = context.get('page_obj')
        start_index = (page_obj.number - 1) * self.paginate_by if page_obj else 0
        
        for idx, gqn in enumerate(context['gqns'], start=start_index + 1):
            rows.append({
                'cells': [
                    idx,  # SN
                    'NA',  # Select (not editable in list view)
                    getattr(gqn, 'finyearname', '-'),  # Fin Year
                    gqn.gqnno or '-',  # GQN No
                    gqn.sysdate or '-',  # Date
                    gqn.grrno or '-',  # GRR No
                    getattr(gqn, 'ginno', '-'),  # GIN No
                    getattr(gqn, 'pono_from_gin', '-'),  # PO No
                    getattr(gqn, 'suppliername', '-'),  # Name of Supplier
                    getattr(gqn, 'challanno', '-'),  # Challan No
                    getattr(gqn, 'challandate', '-'),  # Challan Date
                ]
            })
        
        context['rows'] = rows
        
        # Search options for dropdown
        context['search_options'] = [
            {'value': '0', 'label': 'Supplier Name'},
            {'value': '1', 'label': 'GQN No'},
            {'value': '2', 'label': 'GRR No'},
            {'value': '3', 'label': 'PO No'},
        ]
        
        context['gqn_list_url'] = '/quality/gqn/'
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class GQNSupplierAutocompleteView(View):
    """HTMX endpoint for supplier name autocomplete"""

    def get(self, request):
        from material_management.models import Supplier

        # Get search value from multiple possible parameter names
        search_value = (
            request.GET.get('search_value_supplier', '').strip() or
            request.GET.get('search_value', '').strip() or
            request.GET.get('q', '').strip()
        )

        if len(search_value) < 1:
            return HttpResponse('')

        # Get distinct suppliers
        suppliers = Supplier.objects.filter(
            supplier_name__icontains=search_value
        ).values_list('supplier_name', flat=True).distinct().order_by('supplier_name')[:10]

        if not suppliers:
            return HttpResponse('<div class="text-gray-500 px-3 py-2 text-sm">No suppliers found</div>')

        # Render HTML for autocomplete dropdown
        html = ''
        for supplier in suppliers:
            html += f'<div class="autocomplete-item px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm border-b border-gray-200 last:border-b-0">{supplier}</div>'

        return HttpResponse(html)


class GoodsQualityNoteCreateView(QualityControlBaseMixin, CreateView):
    """Create new Goods Quality Note with details (legacy direct create)"""
    model = TblqcMaterialqualityMaster
    form_class = GoodsQualityNoteForm
    template_name = 'quality_control/gqn/form.html'
    success_url = reverse_lazy('quality_control:gqn-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['details'] = GoodsQualityNoteDetailFormSet(self.request.POST)
        else:
            context['details'] = GoodsQualityNoteDetailFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        details = context['details']

        # Set session metadata
        for field, value in self.get_session_metadata().items():
            setattr(form.instance, field, value)

        if details.is_valid():
            self.object = form.save()
            details.instance = self.object
            details.save()
            messages.success(self.request, f'GQN {self.object.gqnno} created successfully')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class GoodsQualityNoteUpdateView(QualityControlBaseMixin, UpdateView):
    """Update existing Goods Quality Note"""
    model = TblqcMaterialqualityMaster
    form_class = GoodsQualityNoteForm
    template_name = 'quality_control/gqn/form.html'
    success_url = reverse_lazy('quality_control:gqn-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['details'] = GoodsQualityNoteDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['details'] = GoodsQualityNoteDetailFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        details = context['details']

        if details.is_valid():
            self.object = form.save()
            details.instance = self.object
            details.save()
            messages.success(self.request, f'GQN {self.object.gqnno} updated successfully')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class GoodsQualityNoteDetailView(QualityControlBaseMixin, DetailView):
    """View Goods Quality Note details"""
    model = TblqcMaterialqualityMaster
    template_name = 'quality_control/gqn/detail.html'
    context_object_name = 'gqn'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.all()
        return context


class GoodsQualityNoteDeleteView(QualityControlBaseMixin, DeleteView):
    """Delete Goods Quality Note"""
    model = TblqcMaterialqualityMaster
    template_name = 'quality_control/gqn/delete.html'
    success_url = reverse_lazy('quality_control:gqn-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'GQN deleted successfully')
        return super().delete(request, *args, **kwargs)


class GoodsQualityNotePrintView(QualityControlBaseMixin, DetailView):
    """Print Goods Quality Note"""
    model = TblqcMaterialqualityMaster
    template_name = 'quality_control/gqn/print.html'
    context_object_name = 'gqn'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.all()
        context['print_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return context
