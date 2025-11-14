"""
Inventory Module Views
Modernized with core mixins and query optimization.
Requirements: 3.1, 3.4, 5.5, 13.1, 13.2, 13.3
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
    MRSMasterForm,  # MRSDetailFormSet,  # Commented out - formsets don't work with managed=False models
    MINMasterForm,  # MINDetailFormSet,  # Commented out
    MRNMasterForm,  # MRNDetailFormSet,  # Commented out
    VehicleProcessMasterForm,
    VehicleMasterForm,
    AutoWISTimeScheduleForm,
    StockLedgerFilterForm,
)
# NOTE: All formsets have been commented out in forms.py due to foreign key issues with managed=False models
from ..services import (
    MaterialRequisitionService,
    MaterialIssueService,
    MaterialReturnService,
    DashboardService,
)




class ItemImageDownloadView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    Download Item Image from Item Master
    Returns image file from BLOB data stored in database.
    """

    def get(self, request, item_id):
        from django.http import HttpResponse
        from django.db import connection
        from design.models import TbldgItemMaster

        try:
            # Get item from Item Master
            item = TbldgItemMaster.objects.filter(
                id=item_id,
                compid=self.get_compid()
            ).first()

            if not item or not item.filename:
                return HttpResponse('File not found', status=404)

            # Get file data from database using raw SQL (BLOB field)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT FileData, FileName FROM tblDG_Item_Master WHERE Id = %s",
                    [item_id]
                )
                row = cursor.fetchone()

                if row and row[0]:
                    file_data = row[0]
                    file_name = row[1] or 'image.png'

                    # Determine content type from file extension
                    import mimetypes
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

                    response = HttpResponse(file_data, content_type=content_type)
                    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    return response
                else:
                    return HttpResponse('File data not found', status=404)

        except Exception as e:
            return HttpResponse(f'Error downloading file: {str(e)}', status=500)




class ItemSpecDownloadView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    Download Item Spec Sheet from Item Master
    Returns spec sheet file from BLOB data stored in database.
    """

    def get(self, request, item_id):
        from django.http import HttpResponse
        from django.db import connection
        from design.models import TbldgItemMaster

        try:
            # Get item from Item Master
            item = TbldgItemMaster.objects.filter(
                id=item_id,
                compid=self.get_compid()
            ).first()

            if not item or not item.attname:
                return HttpResponse('File not found', status=404)

            # Get file data from database using raw SQL (BLOB field)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT AttData, AttName, AttContentType FROM tblDG_Item_Master WHERE Id = %s",
                    [item_id]
                )
                row = cursor.fetchone()

                if row and row[0]:
                    file_data = row[0]
                    file_name = row[1] or 'spec_sheet.pdf'
                    content_type = row[2] or 'application/octet-stream'

                    response = HttpResponse(file_data, content_type=content_type)
                    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    return response
                else:
                    return HttpResponse('File data not found', status=404)

        except Exception as e:
            return HttpResponse(f'Error downloading file: {str(e)}', status=500)




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
        from django.db import connection

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

        # Load PO line items
        po_items = []

        try:
            with connection.cursor() as cursor:
                # Query PO Details joined with PO Master
                cursor.execute("""
                    SELECT
                        pod.Id,
                        pod.ItemId,
                        pod.Qty,
                        pod.AHId,
                        pom.PRSPRFlag
                    FROM tblMM_PO_Details pod
                    INNER JOIN tblMM_PO_Master pom ON pod.MId = pom.Id
                    WHERE pod.MId = %s AND pom.CompId = %s
                """, [mid, self.get_compid()])

                po_details = cursor.fetchall()

                for po_detail in po_details:
                    pod_id = po_detail[0]
                    item_id = po_detail[1]
                    qty = po_detail[2]
                    ahid = po_detail[3]
                    pr_spr_flag = po_detail[4]

                    # Determine if PR or SPR
                    if pr_spr_flag == 0:
                        # PR: Query tblMM_PR_Details
                        cursor.execute("""
                            SELECT ItemId, AHId
                            FROM tblMM_PR_Details
                            WHERE Id = %s
                        """, [ahid])
                        pr_row = cursor.fetchone()
                        if pr_row:
                            item_id = pr_row[0]
                            ahid = pr_row[1]
                    else:
                        # SPR: Query tblMM_SPR_Details
                        cursor.execute("""
                            SELECT ItemId, AHId
                            FROM tblMM_SPR_Details
                            WHERE Id = %s
                        """, [ahid])
                        spr_row = cursor.fetchone()
                        if spr_row:
                            item_id = spr_row[0]
                            ahid = spr_row[1]

                    # Get Item details from Item Master
                    cursor.execute("""
                        SELECT
                            ItemCode,
                            ManfDesc,
                            UOMBasic,
                            FileName,
                            AttName
                        FROM tblDG_Item_Master
                        WHERE Id = %s
                    """, [item_id])
                    item_row = cursor.fetchone()

                    if item_row:
                        item_code = item_row[0]
                        description = item_row[1]
                        uom = item_row[2]
                        has_image = bool(item_row[3])
                        has_spec = bool(item_row[4])

                        # Calculate total received quantity for this PO detail
                        cursor.execute("""
                            SELECT COALESCE(SUM(RecdQty), 0)
                            FROM tblInv_Inward_details
                            WHERE POId = %s AND CompId = %s
                        """, [pod_id, self.get_compid()])
                        tot_recd_qty = cursor.fetchone()[0] or 0

                        # Calculate remaining quantity
                        remain_qty = float(qty) - float(tot_recd_qty)

                        po_items.append({
                            'id': pod_id,
                            'item_id': item_id,
                            'ahid': ahid,
                            'item_code': item_code,
                            'description': description,
                            'uom': uom,
                            'qty': qty,
                            'tot_recd_qty': tot_recd_qty,
                            'remain_qty': remain_qty,
                            'has_image': has_image,
                            'has_spec': has_spec
                        })

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading PO items: {str(e)}")

        context['po_items'] = po_items
        return context

    def post(self, request):
        """Create GIN with selected items"""
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        from django.db import connection, transaction
        from datetime import datetime

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

                # Create GIN Master record
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO tblInv_Inward_master (
                            GINNo, PONo, ChallanNo, ChallanDate,
                            ModeofTransport, VehicleNo, GateEntryNo, GateDate, GateTime,
                            SysDate, SysTime, SessionId, CompId, FinYearId
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        gin_no,
                        pono,
                        challan_no,
                        challan_date,
                        mode_of_transport,
                        vehicle_no,
                        gate_entry_no,
                        gate_date,
                        gate_time,
                        sysdate,
                        systime,
                        str(request.user.id),
                        self.get_compid(),
                        fyid
                    ])

                    # Get the inserted GIN ID
                    cursor.execute("SELECT last_insert_rowid()")
                    gin_id = cursor.fetchone()[0]

                    # Create GIN Detail records for selected items
                    for item_id in selected_items:
                        challan_qty = request.POST.get(f'item_{item_id}_challan_qty', 0)
                        recd_qty = request.POST.get(f'item_{item_id}_recd_qty', 0)
                        poid = request.POST.get(f'item_{item_id}_poid')
                        itemid = request.POST.get(f'item_{item_id}_itemid')
                        ahid = request.POST.get(f'item_{item_id}_ahid')

                        cursor.execute("""
                            INSERT INTO tblInv_Inward_details (
                                MId, POId, ItemId, AHId, ChallanQty, RecdQty,
                                SysDate, SysTime, SessionId, CompId, FinYearId
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, [
                            gin_id,
                            poid,
                            itemid,
                            ahid,
                            challan_qty,
                            recd_qty,
                            sysdate,
                            systime,
                            str(request.user.id),
                            self.get_compid(),
                            fyid
                        ])

                from django.contrib import messages
                messages.success(request, f'GIN {gin_no} created successfully')

                # Redirect to GIN detail page
                return HttpResponseRedirect(reverse('inventory:gin-detail', kwargs={'pk': gin_id}))

        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error creating GIN: {str(e)}')
            return HttpResponseRedirect(request.path + '?' + request.GET.urlencode())

    def _generate_gin_number(self):
        """Generate next GIN number in sequence"""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT GINNo
                FROM tblInv_Inward_master
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


