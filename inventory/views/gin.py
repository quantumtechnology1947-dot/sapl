"""
Goods Inward Note (GIN) Views
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


class GINListView(BaseListViewMixin, ListView):
    """
    Goods Inward Note List View
    Displays all GIN with search and filter.

    Converted from: aspnet/Module/Inventory/Transactions/GoodsInwardNote_GIN_Edit.aspx
    Uses stored procedure Sp_GIN_Edit logic for data enrichment
    Optimized: Uses BaseListViewMixin with built-in search, pagination, and query optimization.
    Requirements: 3.1, 3.4, 4.1, 5.5, 13.1
    """
    model = TblinvInwardMaster
    template_name = 'inventory/transactions/gin_list.html'
    partial_template_name = 'inventory/transactions/partials/gin_list_partial.html'
    context_object_name = 'gin_list'
    paginate_by = 20
    search_fields = ['ginno', 'pono', 'challanno']
    ordering = ['-id']

    def get_queryset(self):
        """Enhanced queryset with dropdown search support"""
        queryset = super().get_queryset()

        # Handle dropdown search fields
        search_field = self.request.GET.get('search_field', '')
        search_value = self.request.GET.get('search_value', '')

        if search_field and search_value:
            if search_field == 'supplier':
                # Search by supplier name - will need to join with PO
                from material_management.models import Supplier
                # Extract supplier ID from format "Name [ID]" if provided
                supplier_id = None
                if '[' in search_value and ']' in search_value:
                    supplier_id = search_value.split('[')[-1].strip(']')

                if supplier_id:
                    # Filter by exact supplier ID through PO
                    queryset = queryset.filter(
                        pono__in=Supplier.objects.filter(
                            supplier_id=supplier_id,
                            comp_id=self.get_compid()
                        ).values_list('supplier_id', flat=True)
                    )
                else:
                    # Search by supplier name contains
                    supplier_ids = Supplier.objects.filter(
                        supplier_name__icontains=search_value,
                        comp_id=self.get_compid()
                    ).values_list('supplier_id', flat=True)
                    queryset = queryset.filter(pono__in=supplier_ids)
            elif search_field == 'pono':
                queryset = queryset.filter(pono__icontains=search_value)
            elif search_field == 'ginno':
                queryset = queryset.filter(ginno__icontains=search_value)

        return queryset

    def get_context_data(self, **kwargs):
        """Enrich GIN data with Financial Year, Supplier Name, and GRR/GSN status"""
        context = super().get_context_data(**kwargs)

        # Import required models
        from sys_admin.models import TblfinancialMaster
        from django.db import connection

        # Get financial year lookup from session
        finyearid = self.request.session.get('finyearid', 1)
        try:
            finyear_obj = TblfinancialMaster.objects.get(finyearid=finyearid)
            finyear_name = finyear_obj.finyear if hasattr(finyear_obj, 'finyear') else ""
        except:
            finyear_name = ""

        # Enrich each GIN record
        enriched_gins = []
        for gin in context['gin_list']:
            # Get Supplier Name through raw SQL query (since we don't have MM_PO model defined)
            supplier_name = ""
            if gin.pono:
                with connection.cursor() as cursor:
                    try:
                        cursor.execute("""
                            SELECT s.SupplierName, s.SupplierId
                            FROM tblMM_Supplier_master s
                            INNER JOIN tblMM_PO_Master p ON s.SupplierId = p.SupplierId
                            WHERE p.PONo = %s AND p.CompId = %s
                            LIMIT 1
                        """, [gin.pono, self.get_compid()])
                        row = cursor.fetchone()
                        if row:
                            supplier_name = f"{row[0]} [{row[1]}]"
                    except Exception:
                        pass  # Silently handle if PO or Supplier not found

            # Check GRR status
            has_grr = TblinvMaterialreceivedMaster.objects.filter(
                ginid=gin.id,
                compid=self.get_compid()
            ).exists()

            # Check GSN status
            has_gsn = TblinvMaterialservicenoteMaster.objects.filter(
                ginid=gin.id,
                compid=self.get_compid()
            ).exists()

            # Format dates
            gin_date = gin.sysdate if gin.sysdate else (gin.gdate if gin.gdate else "")
            challan_date = gin.challandate if gin.challandate else ""

            enriched_gins.append({
                'id': gin.id,
                'ginno': gin.ginno,
                'pono': gin.pono,
                'challanno': gin.challanno,
                'challandate': challan_date,
                'gin_date': gin_date,
                'finyear_name': finyear_name,
                'supplier_name': supplier_name,
                'has_grr': has_grr,
                'has_gsn': has_gsn,
                'can_edit': not (has_grr or has_gsn),  # Can't edit if GRR or GSN exists
            })

        context['gin_list'] = enriched_gins
        context['search_field'] = self.request.GET.get('search_field', '')
        context['search_value'] = self.request.GET.get('search_value', '')

        return context



class GINCreateView(BaseCreateViewMixin, CreateView):
    """
    Goods Inward Note Create View
    Create new GIN with line items.
    
    Optimized: Uses BaseCreateViewMixin with automatic audit fields and success messages.
    Requirements: 3.1, 3.2, 4.1, 4.2, 13.2
    """
    model = TblinvInwardMaster
    form_class = forms.GINMasterForm
    template_name = 'inventory/transactions/gin_form.html'
    partial_template_name = 'inventory/transactions/partials/gin_form_partial.html'
    success_url = reverse_lazy('inventory:gin-list')
    success_message = 'GIN %(ginno)s created successfully!'
    
    def get_form_kwargs(self):
        """Pass company, financial year, and session to form."""
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.get_compid()
        kwargs['finyearid'] = self.get_finyearid()
        kwargs['sessionid'] = self.get_sessionid()
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add auto-generated GIN number to context."""
        context = super().get_context_data(**kwargs)

        # Auto-generate GIN number
        from ..services import GoodsInwardService
        context['auto_gin_number'] = GoodsInwardService.generate_gin_number(
            self.get_compid(),
            self.get_finyearid()
        )

        return context

    def form_valid(self, form):
        """Set auto-generated GIN number before saving."""
        from ..services import GoodsInwardService
        form.instance.ginno = GoodsInwardService.generate_gin_number(
            self.get_compid(),
            self.get_finyearid()
        )

        return super().form_valid(form)



class GINDetailView(BaseDetailViewMixin, DetailView):
    """
    Goods Inward Note Detail View
    View GIN details with line items - enriched with full traceability.

    Converted from: aspnet/Module/Inventory/Transactions/GoodsInwardNote_GIN_Edit_Details.aspx
    Traces: GIN Detail → PO Detail → PR/SPR Detail → Item Master
    Optimized: Uses BaseDetailViewMixin with automatic company filtering.
    Requirements: 3.1, 4.1, 13.1
    """
    model = TblinvInwardMaster
    template_name = 'inventory/transactions/gin_detail.html'
    context_object_name = 'gin'

    def get_context_data(self, **kwargs):
        """Add enriched GIN details with full traceability chain using Django ORM."""
        context = super().get_context_data(**kwargs)

        from design.models import TbldgItemMaster
        from sys_admin.models import UnitMaster
        from mis.models import (
            TblmmPoMaster, TblmmPoDetails,
            TblmmPrMaster, TblmmPrDetails,
            TblmmSprMaster, TblmmSprDetails
        )
        from django.db.models import Sum, Q
        from django.db import connection

        # Get GIN details
        gin_details = TblinvInwardDetails.objects.filter(ginid=self.object.id)

        # Enrich each detail with item info, PO qty, total received, categories
        enriched_details = []

        for detail in gin_details:
            enriched_item = {
                'id': detail.id,
                'ginid': detail.ginid,
                'poid': detail.poid,
                'qty': detail.qty or 0,
                'receivedqty': detail.receivedqty or 0,
                'acategoryid': detail.acategoyid,
                'asubcategoryid': detail.asubcategoyid,
                'item_code': '',
                'description': '',
                'uom': '',
                'po_qty': 0,
                'total_recd_qty': 0,
                'category': '',
                'subcategory': '',
                'has_grr': False,
                'has_gsn': False,
                'has_image': False,
                'has_spec': False,
                'item_id': None,
                'ah_id': None,
            }

            try:
                # Get PO details using ORM
                po_detail = TblmmPoDetails.objects.filter(id=detail.poid).first()

                if po_detail:
                    enriched_item['po_qty'] = po_detail.qty or 0

                    item_id = None
                    ah_id = None

                    # Data-driven approach: Check what data exists in PO Detail, not the flag
                    # This handles mixed POs where flag doesn't match individual items
                    if po_detail.pr_id and po_detail.pr_no:
                        # PR Path: PO Detail has PR data
                        pr_detail = TblmmPrDetails.objects.filter(
                            id=po_detail.pr_id
                        ).first()

                        if pr_detail:
                            # Get PR Master using pr_no
                            pr_master = TblmmPrMaster.objects.filter(
                                pr_no=pr_detail.pr_no,
                                comp_id=self.get_compid()
                            ).first()
                            if pr_master:
                                # Access fields via raw SQL or direct attribute access
                                # Since model may not have these fields defined
                                from django.db import connection
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        "SELECT ItemId, AHId FROM tblMM_PR_Details WHERE Id = %s",
                                        [po_detail.pr_id]
                                    )
                                    row = cursor.fetchone()
                                    if row:
                                        item_id = row[0]
                                        ah_id = row[1]

                    elif po_detail.spr_id and po_detail.spr_no:
                        # SPR Path: PO Detail has SPR data
                        spr_detail = TblmmSprDetails.objects.filter(
                            id=po_detail.spr_id
                        ).first()

                        if spr_detail:
                            # Get SPR Master using spr_no
                            spr_master = TblmmSprMaster.objects.filter(
                                spr_no=spr_detail.spr_no,
                                comp_id=self.get_compid()
                            ).first()
                            if spr_master:
                                # Access fields via raw SQL
                                from django.db import connection
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        "SELECT ItemId, AHId FROM tblMM_SPR_Details WHERE Id = %s",
                                        [po_detail.spr_id]
                                    )
                                    row = cursor.fetchone()
                                    if row:
                                        item_id = row[0]
                                        ah_id = row[1]

                    # Get item details from Item Master using ORM
                    if item_id:
                        enriched_item['item_id'] = item_id
                        enriched_item['ah_id'] = ah_id

                        try:
                            item = TbldgItemMaster.objects.filter(
                                id=item_id,
                                compid=self.get_compid()
                            ).first()

                            if item:
                                # Get item code with part no
                                item_code = item.itemcode or ''
                                if hasattr(item, 'partno') and item.partno:
                                    item_code = f"{item_code} / {item.partno}"
                                enriched_item['item_code'] = item_code
                                enriched_item['description'] = item.manfdesc or ''
                                enriched_item['has_image'] = bool(item.filename)
                                enriched_item['has_spec'] = bool(item.attname)

                                # Get UOM using ORM
                                if item.uombasic:
                                    unit = UnitMaster.objects.filter(id=item.uombasic).first()
                                    if unit:
                                        enriched_item['uom'] = unit.symbol or ''
                        except Exception:
                            pass

                        # Get Category/Sub-Category if AHId = 33 (Assets) using ORM
                        if ah_id == 33 and detail.acategoyid and detail.asubcategoyid:
                            try:
                                category = TblinvAssetCategory.objects.filter(
                                    categoryid=detail.acategoyid,
                                    compid=self.get_compid()
                                ).first()
                                if category:
                                    enriched_item['category'] = category.categoryname or ''
                            except Exception:
                                pass

                            try:
                                subcategory = TblinvAssetSubcategory.objects.filter(
                                    subcategoryid=detail.asubcategoyid,
                                    compid=self.get_compid()
                                ).first()
                                if subcategory:
                                    enriched_item['subcategory'] = subcategory.subcategoryname or ''
                            except Exception:
                                pass

                        # Calculate Total Received Qty using ORM aggregation
                        total_recd = TblinvInwardDetails.objects.filter(
                            poid=detail.poid
                        ).aggregate(total=Sum('receivedqty'))['total']
                        enriched_item['total_recd_qty'] = total_recd or 0

                    # Check GRR status using ORM
                    # Get GRR master IDs for this GIN and company
                    grr_master_ids = TblinvMaterialreceivedMaster.objects.filter(
                        ginid=self.object.id,
                        compid=self.get_compid()
                    ).values_list('id', flat=True)

                    grr_exists = TblinvMaterialreceivedDetails.objects.filter(
                        mid__in=grr_master_ids,
                        poid=detail.poid
                    ).exists()
                    enriched_item['has_grr'] = grr_exists

                    # Check GSN status using ORM
                    # Get GSN master IDs for this GIN and company
                    from inventory.models import TblinvMaterialservicenoteMaster
                    gsn_master_ids = TblinvMaterialservicenoteMaster.objects.filter(
                        ginid=self.object.id,
                        compid=self.get_compid()
                    ).values_list('id', flat=True)

                    gsn_exists = TblinvMaterialservicenoteDetails.objects.filter(
                        mid__in=gsn_master_ids,
                        poid=detail.poid
                    ).exists()
                    enriched_item['has_gsn'] = gsn_exists

            except Exception as e:
                # Log error but continue
                import traceback
                print(f"Error enriching GIN detail {detail.id}: {e}")
                print(f"Detail POId: {detail.poid}")
                traceback.print_exc()

            enriched_details.append(enriched_item)

        context['gin_details'] = enriched_details

        # Calculate totals
        total_challan_qty = sum(d['qty'] for d in enriched_details)
        total_received_qty = sum(d['receivedqty'] for d in enriched_details)
        context['total_challan_qty'] = total_challan_qty
        context['total_received_qty'] = total_received_qty

        # Get Business Group (WO Department) using raw SQL
        # Note: Department field not properly modeled in PR Master, using raw SQL
        business_group = ""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT d.Description
                    FROM tblMM_PO_Master pom
                    INNER JOIN tblMM_PO_Details pod ON pom.Id = pod.MId
                    LEFT JOIN tblMM_PR_Master prm ON pod.PRNo = prm.PRNo AND pom.CompId = prm.CompId
                    LEFT JOIN tblHR_Departments d ON prm.DeptId = d.Id
                    WHERE pom.PONo = %s AND pom.CompId = %s
                    LIMIT 1
                """, [self.object.pono, self.get_compid()])
                row = cursor.fetchone()
                if row:
                    business_group = row[0] or ''
        except Exception:
            pass

        context['business_group'] = business_group

        # Get Supplier Name and PO Date from PO Master
        supplier_name = ""
        po_date = ""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT pom.SupplierId, pom.SysDate, sm.SupplierName
                    FROM tblMM_PO_Master pom
                    LEFT JOIN SD_Supp_master sm ON pom.SupplierId = sm.SupplierId AND pom.CompId = sm.CompId
                    WHERE pom.PONo = %s AND pom.CompId = %s
                    LIMIT 1
                """, [self.object.pono, self.get_compid()])
                row = cursor.fetchone()
                if row:
                    supplier_name = row[2] or ''
                    po_date = row[1] or ''
        except Exception:
            pass

        context['supplier_name'] = supplier_name
        context['po_date'] = po_date

        return context



class GINDetailUpdateView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    GIN Detail Update View
    Updates Challan Qty and Received Qty for individual GIN line items.
    Uses JSON API for inline editing.
    """

    def post(self, request, detail_id):
        """Update GIN detail quantities"""
        import json
        from datetime import datetime
        from django.http import JsonResponse

        try:
            # Parse JSON request
            data = json.loads(request.body)
            challan_qty = float(data.get('challan_qty', 0))
            received_qty = float(data.get('received_qty', 0))

            # Validation
            if challan_qty < 0 or received_qty < 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Quantities cannot be negative'
                }, status=400)

            if received_qty > challan_qty:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Received Quantity cannot exceed Challan Quantity'
                }, status=400)

            # Get GIN detail record
            detail = TblinvInwardDetails.objects.filter(id=detail_id).first()

            if not detail:
                return JsonResponse({
                    'status': 'error',
                    'message': 'GIN detail not found'
                }, status=404)

            # Verify the GIN belongs to the current company
            gin_master = TblinvInwardMaster.objects.filter(
                id=detail.ginid,
                compid=self.get_compid()
            ).first()

            if not gin_master:
                return JsonResponse({
                    'status': 'error',
                    'message': 'GIN detail not found or access denied'
                }, status=404)

            # Check if GRR or GSN exists (cannot edit if already processed)
            # Get GRR master IDs for this GIN
            grr_master_ids = TblinvMaterialreceivedMaster.objects.filter(
                ginid=detail.ginid,
                compid=self.get_compid()
            ).values_list('id', flat=True)

            grr_exists = TblinvMaterialreceivedDetails.objects.filter(
                mid__in=grr_master_ids,
                poid=detail.poid
            ).exists()

            # Get GSN master IDs for this GIN
            from inventory.models import TblinvMaterialservicenoteMaster
            gsn_master_ids = TblinvMaterialservicenoteMaster.objects.filter(
                ginid=detail.ginid,
                compid=self.get_compid()
            ).values_list('id', flat=True)

            gsn_exists = TblinvMaterialservicenoteDetails.objects.filter(
                mid__in=gsn_master_ids,
                poid=detail.poid
            ).exists()

            if grr_exists or gsn_exists:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Cannot edit: GRR or GSN already exists for this item'
                }, status=400)

            # Update quantities
            detail.qty = challan_qty
            detail.receivedqty = received_qty

            # Update audit fields
            now = datetime.now()
            detail.sysdate = now.strftime('%d-%m-%Y')
            detail.systime = now.strftime('%H:%M:%S')
            detail.sessionid = str(request.user.id)

            detail.save()

            return JsonResponse({
                'status': 'success',
                'message': 'GIN detail updated successfully',
                'data': {
                    'challan_qty': float(detail.qty),
                    'received_qty': float(detail.receivedqty)
                }
            })

        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid quantity value: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Update failed: {str(e)}'
            }, status=500)



class GINMasterUpdateView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    GIN Master Update View
    Updates GIN master fields (Gate Entry, Date, Time, Mode of Transport, Vehicle No).
    Uses JSON API.
    """

    def post(self, request, pk):
        """Update GIN master fields"""
        import json
        from datetime import datetime
        from django.http import JsonResponse

        try:
            # Parse JSON request
            data = json.loads(request.body)
            gateentryno = data.get('gateentryno', '').strip()
            gdate = data.get('gdate', '')
            gtime = data.get('gtime', '')
            modeoftransport = data.get('modeoftransport', '').strip()
            vehicleno = data.get('vehicleno', '').strip()

            # Validation
            if not gateentryno:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Gate Entry No is required'
                }, status=400)

            if not gdate:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Date is required'
                }, status=400)

            if not gtime:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Time is required'
                }, status=400)

            if not modeoftransport:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Mode of Transport is required'
                }, status=400)

            if not vehicleno:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Vehicle No is required'
                }, status=400)

            # Get GIN master record
            gin = TblinvInwardMaster.objects.filter(
                id=pk,
                compid=self.get_compid()
            ).first()

            if not gin:
                return JsonResponse({
                    'status': 'error',
                    'message': 'GIN not found'
                }, status=404)

            # Update fields
            gin.gateentryno = gateentryno
            gin.gdate = gdate
            gin.gtime = gtime
            gin.modeoftransport = modeoftransport
            gin.vehicleno = vehicleno

            # Update audit fields
            now = datetime.now()
            gin.sysdate = now.strftime('%d-%m-%Y')
            gin.systime = now.strftime('%H:%M:%S')
            gin.sessionid = str(request.user.id)

            gin.save()

            return JsonResponse({
                'status': 'success',
                'message': 'GIN master information updated successfully'
            })

        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid value: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Update failed: {str(e)}'
            }, status=500)



class GINDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Goods Inward Note Delete View
    Delete GIN with GRR dependency check.
    
    Optimized: Uses BaseDeleteViewMixin with automatic HTMX support.
    Requirements: 3.1, 4.1, 13.2
    """
    model = TblinvInwardMaster
    template_name = 'inventory/transactions/gin_confirm_delete.html'
    success_url = reverse_lazy('inventory:gin-list')
    context_object_name = 'gin'
    
    def delete(self, request, *args, **kwargs):
        """Delete with GRR dependency check."""
        self.object = self.get_object()
        
        # Check GRR dependency
        from .services import GoodsInwardService
        has_grr, grr_count = GoodsInwardService.check_grr_dependency(self.object.id)
        
        if has_grr:
            messages.error(
                request,
                f'Cannot delete GIN {self.object.ginno}. '
                f'{grr_count} GRR record(s) exist for this GIN.'
            )
            if request.headers.get('HX-Request'):
                return HttpResponse(status=409, reason="GIN has GRR records")
            return redirect('inventory:gin-detail', pk=self.object.pk)
        
        ginno = self.object.ginno
        messages.success(request, f'GIN {ginno} deleted successfully!')
        return super().delete(request, *args, **kwargs)



class GINPrintView(BaseDetailViewMixin, DetailView):
    """
    Goods Inward Note Print View
    Print-friendly GIN document.
    
    Optimized: Uses BaseDetailViewMixin with automatic company filtering.
    Requirements: 3.1, 4.1
    """
    model = TblinvInwardMaster
    template_name = 'inventory/transactions/gin_print.html'
    context_object_name = 'gin'
    
    def get_context_data(self, **kwargs):
        """Add GIN details and totals to context."""
        context = super().get_context_data(**kwargs)
        
        # Get GIN details
        context['gin_details'] = TblinvInwardDetails.objects.filter(
            ginid=self.object.id
        )
        
        # Calculate totals
        total_qty = sum(detail.qty or 0 for detail in context['gin_details'])
        context['total_qty'] = total_qty
        
        return context



class GINPendingListView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Pending GIN List View
    Shows GIN with pending quantities for GRR.
    
    Displays GIN where (Inward Qty - Received Qty) > 0
    Optimized: Uses core mixins instead of InventoryBaseMixin.
    Requirements: 3.1, 4.1, 4.2
    """
    template_name = 'inventory/transactions/gin_pending_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get pending GIN
        from inventory.services import GoodsInwardService
        context['pending_gin'] = GoodsInwardService.get_pending_gin_for_receipt(
            self.get_compid(),
            self.get_finyearid()
        )
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            context['pending_gin'] = [
                item for item in context['pending_gin']
                if search.lower() in item['gin'].ginno.lower() or
                   search.lower() in (item['gin'].pono or '').lower()
            ]
        
        context['search_query'] = search
        
        return context


class GINPOSearchResultsView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    HTMX View: Search for POs by Supplier Name or PO Number
    Returns partial HTML with PO list for GIN creation
    """

    def get(self, request):
        from django.shortcuts import render
        from django.db import connection

        search_type = request.GET.get('search-type', 'supplier')
        search_value = request.GET.get('search-input', '').strip()

        po_list = []

        if search_value:
            with connection.cursor() as cursor:
                if search_type == 'supplier':
                    # Search by Supplier Name
                    cursor.execute("""
                        SELECT
                            pom.Id,
                            pom.FinYearId,
                            fy.FinYear,
                            pom.PONo,
                            pom.SysDate as PODate,
                            sm.SupplierName || ' [' || sm.SupplierId || ']' as Supplier
                        FROM tblMM_PO_Master pom
                        LEFT JOIN tblFinancial_master fy ON pom.FinYearId = fy.FinYearId
                        LEFT JOIN tblMM_Supplier_master sm ON pom.SupplierId = sm.SupplierId AND pom.CompId = sm.CompId
                        WHERE pom.CompId = %s
                          AND sm.SupplierName LIKE %s
                        ORDER BY pom.SysDate DESC
                        LIMIT 50
                    """, [self.get_compid(), f'%{search_value}%'])
                else:
                    # Search by PO Number
                    cursor.execute("""
                        SELECT
                            pom.Id,
                            pom.FinYearId,
                            fy.FinYear,
                            pom.PONo,
                            pom.SysDate as PODate,
                            sm.SupplierName || ' [' || sm.SupplierId || ']' as Supplier
                        FROM tblMM_PO_Master pom
                        LEFT JOIN tblFinancial_master fy ON pom.FinYearId = fy.FinYearId
                        LEFT JOIN tblMM_Supplier_master sm ON pom.SupplierId = sm.SupplierId AND pom.CompId = sm.CompId
                        WHERE pom.CompId = %s
                          AND pom.PONo LIKE %s
                        ORDER BY pom.SysDate DESC
                        LIMIT 50
                    """, [self.get_compid(), f'%{search_value}%'])

                rows = cursor.fetchall()
                for row in rows:
                    po_list.append({
                        'id': row[0],
                        'finyearid': row[1],
                        'finyear': row[2],
                        'pono': row[3],
                        'podate': row[4],
                        'supplier_name': row[5],
                    })

        return render(request, 'inventory/transactions/partials/gin_po_search_results.html', {
            'po_list': po_list
        })



class GINCreateFromPOView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    Create GIN from selected PO
    Accepts PO ID, Challan No, and Challan Date
    Returns new GIN ID for redirect
    """

    def post(self, request):
        from django.http import HttpResponse, JsonResponse
        from django.db import connection, transaction
        from datetime import datetime

        po_id = request.POST.get('po_id')
        pono = request.POST.get('pono')
        challan_no = request.POST.get(f'challan-no-{po_id}', '0')
        challan_date = request.POST.get(f'challan-date-{po_id}', '')

        if not po_id or not pono:
            return JsonResponse({'error': 'PO ID and PO Number required'}, status=400)

        try:
            with transaction.atomic():
                # Generate new GIN number
                gin_no = self._generate_gin_number()

                # Get current datetime
                now = datetime.now()
                sysdate = now.strftime('%d-%m-%Y')
                systime = now.strftime('%H:%M:%S')

                # Create GIN Master record
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO tblInv_Inward_master (
                            GINNo, PONo, ChallanNo, ChallanDate, 
                            SysDate, SysTime, SessionId, CompId, FinYearId
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        gin_no,
                        pono,
                        challan_no,
                        challan_date if challan_date else None,
                        sysdate,
                        systime,
                        str(request.user.id),
                        self.get_compid(),
                        self.get_finyearid()
                    ])

                    # Get the newly created GIN ID
                    cursor.execute("SELECT last_insert_rowid()")
                    gin_id = cursor.fetchone()[0]

                # Return GIN ID for redirect
                return HttpResponse(str(gin_id), content_type='text/plain')

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def _generate_gin_number(self):
        """Generate next GIN number in sequence"""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT GINNo FROM tblInv_Inward_master 
                WHERE CompId = %s 
                ORDER BY Id DESC 
                LIMIT 1
            """, [self.get_compid()])
            row = cursor.fetchone()

            if row and row[0]:
                last_gin = row[0]
                # Extract numeric part and increment
                try:
                    if isinstance(last_gin, str) and last_gin.isdigit():
                        next_num = int(last_gin) + 1
                        return str(next_num).zfill(4)
                except:
                    pass

        # Default starting number
        return '0001'



class GINPODetailsView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Page 2: Display PO line items and create GIN
    Converted from: aaspnet/Module/Inventory/Transactions/GoodsInwardNote_GIN_New_PO_Details.aspx
    """
    template_name = 'inventory/transactions/gin_po_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Sum, Q, F, Value, Case, When
        from django.db.models.functions import Coalesce
        from material_management.models import PODetails, POMaster, PRDetails, SPRDetails
        from design.models import TbldgItemMaster

        # Get query parameters from Page 1
        mid = self.request.GET.get('mid')  # PO Master ID
        pono = self.request.GET.get('pono')  # PO Number
        challan_no = self.request.GET.get('chno')  # Challan No
        challan_date = self.request.GET.get('chdate')  # Challan Date
        fyid = self.request.GET.get('fyid')  # Financial Year ID

        context['mid'] = mid
        context['pono'] = pono
        context['challan_no'] = challan_no
        context['challan_date'] = challan_date
        context['fyid'] = fyid

        # Load PO line items using Django ORM
        po_items = []

        try:
            # Get PO Master to check PRSPRFlag
            po_master = POMaster.objects.filter(
                po_id=mid,
                comp_id=self.get_compid()
            ).first()

            if not po_master:
                context['error_message'] = f"PO not found"
                context['po_items'] = []
                return context

            # Get PO Details with related data
            po_details = PODetails.objects.filter(m_id=po_master.po_id)

            for pod in po_details:
                # Get item info from PR or SPR based on flag
                item = None
                ahid = None
                item_id = None

                if po_master.pr_spr_flag == 0 and pod.pr_id:
                    # PR-based PO
                    pr_detail = PRDetails.objects.filter(id=pod.pr_id).first()
                    if pr_detail:
                        item_id = pr_detail.item_id
                        ahid = pr_detail.ah_id

                elif po_master.pr_spr_flag == 1 and pod.spr_id:
                    # SPR-based PO
                    spr_detail = SPRDetails.objects.filter(id=pod.spr_id).first()
                    if spr_detail:
                        item_id = spr_detail.item_id
                        ahid = spr_detail.ah_id

                if not item_id:
                    continue  # Skip items without proper item reference

                # Fetch the item master record
                item = TbldgItemMaster.objects.filter(id=item_id).first()
                if not item:
                    continue  # Skip if item not found

                # Calculate total received quantity
                from ..models import TblinvInwardDetails
                tot_recd_qty = TblinvInwardDetails.objects.filter(
                    poid=pod.id
                ).aggregate(
                    total=Sum('receivedqty')
                )['total'] or 0

                # Calculate remaining quantity
                remain_qty = float(pod.qty or 0) - float(tot_recd_qty)

                po_items.append({
                    'id': pod.id,
                    'item_id': item.id,
                    'ahid': ahid or '',
                    'item_code': item.itemcode or '',
                    'description': item.manfdesc or '',
                    'uom': item.uombasic or '',
                    'qty': pod.qty or 0,
                    'tot_recd_qty': tot_recd_qty,
                    'remain_qty': remain_qty,
                    'has_image': bool(item.filename),
                    'has_spec': bool(item.attname)
                })

        except Exception as e:
            # Log error but continue - show user the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading PO items: {str(e)}")
            context['error_message'] = f"Error loading PO items: {str(e)}"

        context['po_items'] = po_items
        return context

    def post(self, request):
        """Create GIN with selected items"""
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        from django.db import transaction
        from datetime import datetime
        from ..models import TblinvInwardMaster, TblinvInwardDetails

        # Get form data
        mid = request.POST.get('mid')
        pono = request.POST.get('pono')
        challan_no = request.POST.get('challan_no')
        challan_date = request.POST.get('challan_date')
        fyid = request.POST.get('fyid')

        mode_of_transport = request.POST.get('mode_of_transport')
        vehicle_no = request.POST.get('vehicle_no')
        gate_entry_no = request.POST.get('gate_entry_no')
        gate_date = request.POST.get('gate_date')
        gate_time = request.POST.get('gate_time')

        selected_items = request.POST.getlist('selected_items')

        if not selected_items:
            from django.contrib import messages
            messages.error(request, 'Please select at least one item')
            return HttpResponseRedirect(request.path + '?' + request.GET.urlencode())

        try:
            with transaction.atomic():
                # Generate new GIN number
                gin_no = self._generate_gin_number()

                # Get current datetime
                now = datetime.now()
                sysdate = now.strftime('%d-%m-%Y')
                systime = now.strftime('%H:%M:%S')

                # Create GIN Master record using Django ORM
                gin_master = TblinvInwardMaster.objects.create(
                    ginno=gin_no,
                    pono=pono,
                    pomid=mid,
                    challanno=challan_no,
                    challandate=challan_date,
                    modeoftransport=mode_of_transport,
                    vehicleno=vehicle_no,
                    gateentryno=gate_entry_no,
                    gdate=gate_date,
                    gtime=gate_time,
                    sysdate=sysdate,
                    systime=systime,
                    sessionid=str(request.user.id),
                    compid=self.get_compid(),
                    finyearid=fyid
                )

                # Create GIN Detail records for selected items
                for item_id in selected_items:
                    challan_qty = request.POST.get(f'item_{item_id}_challan_qty', 0)
                    recd_qty = request.POST.get(f'item_{item_id}_recd_qty', 0)
                    poid = request.POST.get(f'item_{item_id}_poid')
                    itemid = request.POST.get(f'item_{item_id}_itemid')
                    ahid = request.POST.get(f'item_{item_id}_ahid')

                    TblinvInwardDetails.objects.create(
                        ginid=gin_master.id,
                        ginno=gin_no,
                        poid=poid,
                        qty=challan_qty,
                        receivedqty=recd_qty,
                        acategoyid=ahid or None
                    )

                from django.contrib import messages
                messages.success(request, f'GIN {gin_no} created successfully')

                # Redirect to GIN detail page
                return HttpResponseRedirect(reverse('inventory:gin-detail', kwargs={'pk': gin_master.id}))

        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error creating GIN: {str(e)}')
            return HttpResponseRedirect(request.path + '?' + request.GET.urlencode())

    def _generate_gin_number(self):
        """Generate next GIN number in sequence using Django ORM"""
        from ..models import TblinvInwardMaster

        # Get last GIN number for this company
        last_gin = TblinvInwardMaster.objects.filter(
            compid=self.get_compid()
        ).order_by('-id').values_list('ginno', flat=True).first()

        if last_gin:
            # Extract numeric part and increment
            try:
                if isinstance(last_gin, str) and last_gin.isdigit():
                    next_num = int(last_gin) + 1
                    return str(next_num).zfill(4)
            except:
                pass

        # Default starting number
        return '0001'

