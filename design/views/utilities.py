"""
Design Utilities and Master Views
Includes Unit Master, ECN Reason Master, and helper views
Converted from various ASP.NET masters
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime

from ..models import TbldgEcnReason, TbldgSubcategoryMaster, TbldgCategoryMaster
from sys_admin.models import UnitMaster
from sys_admin.forms import UnitMasterForm


class SubCategoryByCategoryView(LoginRequiredMixin, View):
    """
    Return sub-categories for a given category (for cascading dropdown).
    HTMX endpoint.
    """
    def get(self, request):
        category_id = request.GET.get('cid')
        if not category_id:
            return JsonResponse({'subcategories': []})

        try:
            subcategories = TbldgSubcategoryMaster.objects.filter(cid=int(category_id)).order_by('scname')
            data = {
                'subcategories': [
                    {'id': sc.scid, 'name': sc.scname}
                    for sc in subcategories
                ]
            }
            return JsonResponse(data)
        except (ValueError, TbldgSubcategoryMaster.DoesNotExist):
            return JsonResponse({'subcategories': []})


# ============================================================================
# UNIT MASTER (Design > Master section)
# ============================================================================

class UnitMasterListView(LoginRequiredMixin, ListView):
    """
    Display list of units with inline add/edit/delete functionality.
    Converted from: aspnet/Module/Design/Masters/Unit_Master.aspx
    Uses GridView pattern from ASP.NET with inline editing.
    """
    model = UnitMaster
    template_name = 'design/unit_master_list.html'
    context_object_name = 'units'
    paginate_by = 20

    def get_queryset(self):
        """Order units by ID descending (as per ASP.NET)."""
        return UnitMaster.objects.all().order_by('-id')


class UnitMasterCreateView(LoginRequiredMixin, CreateView):
    """
    Create new unit via HTMX inline form.
    Converted from: aspnet/Module/Design/Masters/Unit_Master.aspx
    """
    model = UnitMaster
    fields = ['unitname', 'symbol', 'effectoninvoice']
    template_name = 'design/partials/unit_master_form.html'

    def form_valid(self, form):
        """Save unit and return updated list."""
        form.save()

        if self.request.headers.get('HX-Request'):
            # Return updated table rows
            units = UnitMaster.objects.all().order_by('-id')[:20]
            from django.template.loader import render_to_string
            html = render_to_string(
                'design/partials/unit_master_table_rows.html',
                {'units': units},
                request=self.request
            )
            return HttpResponse(html)

        messages.success(self.request, f'Unit "{form.instance.unitname}" created successfully.')
        return redirect('design:unit-master-list')

    def form_invalid(self, form):
        """Return form with errors for HTMX."""
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                f'<div class="text-red-600 text-sm">{"; ".join([str(e) for errors in form.errors.values() for e in errors])}</div>',
                status=400
            )
        return super().form_invalid(form)


class UnitMasterUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update unit via HTMX inline editing.
    Converted from: aspnet/Module/Design/Masters/Unit_Master.aspx
    """
    model = UnitMaster
    fields = ['unitname', 'symbol', 'effectoninvoice']
    template_name = 'design/partials/unit_master_edit_row.html'
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        """Return edit form row for HTMX."""
        self.object = self.get_object()
        form = self.get_form()

        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                self.template_name,
                {'form': form, 'unit': self.object},
                request=request
            )
            return HttpResponse(html)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """Save unit and return updated row."""
        form.save()

        if self.request.headers.get('HX-Request'):
            # Return updated table row
            from django.template.loader import render_to_string
            html = render_to_string(
                'design/partials/unit_master_row.html',
                {'unit': self.object, 'counter': 1},
                request=self.request
            )
            messages.success(self.request, 'Unit updated successfully.')
            return HttpResponse(html)

        messages.success(self.request, f'Unit "{form.instance.unitname}" updated successfully.')
        return redirect('design:unit-master-list')


class UnitMasterDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete unit with HTMX support.
    Converted from: aspnet/Module/Design/Masters/Unit_Master.aspx
    """
    model = UnitMaster
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        """Handle delete with HTMX support."""
        self.object = self.get_object()
        unitname = self.object.unitname

        try:
            self.object.delete()

            if request.headers.get('HX-Request'):
                messages.success(request, f'Unit "{unitname}" deleted successfully.')
                return HttpResponse(status=204)

            messages.success(request, f'Unit "{unitname}" deleted successfully.')
            return redirect('design:unit-master-list')

        except Exception as e:
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="text-red-600">Error deleting unit: {str(e)}</div>',
                    status=400
                )
            messages.error(request, f'Error deleting unit: {str(e)}')
            return redirect('design:unit-master-list')


# ============================================================================
# ECN REASONS MASTER (Design > Master section)
# ============================================================================

class EcnReasonListView(LoginRequiredMixin, ListView):
    """
    Display list of ECN reasons with inline add/edit/delete functionality.
    Converted from: aspnet/Module/Design/Masters/ECNReasonTypes.aspx
    Uses GridView pattern from ASP.NET with inline editing.
    """
    model = TbldgEcnReason
    template_name = 'design/ecn_reason_list.html'
    context_object_name = 'reasons'
    paginate_by = 20

    def get_queryset(self):
        """Filter by company and order by ID ascending (as per ASP.NET)."""
        compid = self.request.session.get('compid', 1)
        return TbldgEcnReason.objects.filter(compid=compid).order_by('id')


class EcnReasonCreateView(LoginRequiredMixin, CreateView):
    """
    Create new ECN reason via HTMX inline form.
    Converted from: aspnet/Module/Design/Masters/ECNReasonTypes.aspx
    """
    model = TbldgEcnReason
    fields = ['types']
    template_name = 'design/partials/ecn_reason_form.html'

    def form_valid(self, form):
        """Save ECN reason with company ID."""
        compid = self.request.session.get('compid', 1)
        form.instance.compid = compid
        form.save()

        if self.request.headers.get('HX-Request'):
            # Return updated table rows
            reasons = TbldgEcnReason.objects.filter(compid=compid).order_by('id')[:20]
            from django.template.loader import render_to_string
            html = render_to_string(
                'design/partials/ecn_reason_table_rows.html',
                {'reasons': reasons},
                request=self.request
            )
            return HttpResponse(html)

        messages.success(self.request, f'ECN Reason "{form.instance.types}" created successfully.')
        return redirect('design:ecn-reason-list')

    def form_invalid(self, form):
        """Return form with errors for HTMX."""
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                f'<div class="text-red-600 text-sm">{"; ".join([str(e) for errors in form.errors.values() for e in errors])}</div>',
                status=400
            )
        return super().form_invalid(form)


class EcnReasonUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update ECN reason via HTMX inline editing.
    Converted from: aspnet/Module/Design/Masters/ECNReasonTypes.aspx
    """
    model = TbldgEcnReason
    fields = ['types']
    template_name = 'design/partials/ecn_reason_edit_row.html'
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        """Return edit form row for HTMX."""
        self.object = self.get_object()
        form = self.get_form()

        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            html = render_to_string(
                self.template_name,
                {'form': form, 'reason': self.object},
                request=request
            )
            return HttpResponse(html)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """Save ECN reason and return updated row."""
        form.save()

        if self.request.headers.get('HX-Request'):
            # Return updated table row
            from django.template.loader import render_to_string
            html = render_to_string(
                'design/partials/ecn_reason_row.html',
                {'reason': self.object, 'counter': 1},
                request=self.request
            )
            messages.success(self.request, 'ECN Reason updated successfully.')
            return HttpResponse(html)

        messages.success(self.request, f'ECN Reason "{form.instance.types}" updated successfully.')
        return redirect('design:ecn-reason-list')


class EcnReasonDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete ECN reason with HTMX support.
    Converted from: aspnet/Module/Design/Masters/ECNReasonTypes.aspx
    """
    model = TbldgEcnReason
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        """Handle delete with HTMX support."""
        self.object = self.get_object()
        types = self.object.types

        try:
            self.object.delete()

            if request.headers.get('HX-Request'):
                messages.success(request, f'ECN Reason "{types}" deleted successfully.')
                return HttpResponse(status=204)

            messages.success(request, f'ECN Reason "{types}" deleted successfully.')
            return redirect('design:ecn-reason-list')

        except Exception as e:
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="text-red-600">Error deleting ECN reason: {str(e)}</div>',
                    status=400
                )
            messages.error(request, f'Error deleting ECN reason: {str(e)}')
            return redirect('design:ecn-reason-list')


# ============================================================================
# ECN UNLOCK - Work Order List
# ============================================================================

class EcnWoListView(LoginRequiredMixin, ListView):
    """
    Display work orders with pending ECN for unlock.
    Converted from: aaspnet/Module/Design/Transactions/ECN_WO.aspx
    """
    model = None  # Using raw SQL for complex joins
    template_name = 'design/ecn_wo_list.html'
    context_object_name = 'work_orders'
    paginate_by = 20

    def get_queryset(self):
        """Get work orders with pending ECN."""
        from django.db import connection
        import logging

        logger = logging.getLogger(__name__)
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Get search parameters
        search_type = self.request.GET.get('search_type', '0')
        search_value = self.request.GET.get('search_value', '').strip()
        wo_category = self.request.GET.get('wo_category', '').strip()

        # Build WHERE clause
        # Note: CloseOpen = 1 means OPEN (active), CloseOpen = 0 means CLOSED
        where_clauses = [
            f"wo.CompId = {compid}",
            "(wo.CloseOpen = 1 OR wo.CloseOpen IS NULL)",
            "wo.WONo IN (SELECT DISTINCT WONo FROM tblDG_ECN_Master WHERE Flag = 0)"
        ]

        # Add search filters
        if search_type == '1' and search_value:  # WO No
            where_clauses.append(f"wo.WONo LIKE '%{search_value}%'")
        elif search_type == '0' and search_value:  # Customer Name
            where_clauses.append(f"c.CustomerName LIKE '%{search_value}%'")

        if wo_category:
            try:
                category_int = int(wo_category)
                where_clauses.append(f"wo.CId = {category_int}")
            except ValueError:
                pass

        where_sql = " AND ".join(where_clauses)

        # Modified query for better compatibility
        query = f"""
            SELECT
                wo.WONo,
                wo.CustomerId,
                COALESCE(wo.TaskProjectTitle, '') AS TaskProjectTitle,
                COALESCE(wo.SysDate, '') AS SysDate,
                COALESCE(wo.SessionId, '') AS SessionId,
                wo.FinYearId,
                COALESCE(c.CustomerName, '') AS CustomerName,
                COALESCE(fy.FinYear, '') AS FinYear,
                COALESCE(e.Title || '.' || e.EmployeeName, e.EmployeeName, '') AS EmployeeName
            FROM SD_Cust_WorkOrder_Master wo
            LEFT JOIN SD_Cust_Master c ON wo.CustomerId = c.CustomerId AND c.CompId = {compid}
            LEFT JOIN tblFinancial_master fy ON wo.FinYearId = fy.FinYearId
            LEFT JOIN tblHR_OfficeStaff e ON wo.SessionId = e.EmpId AND e.CompId = {compid}
            WHERE {where_sql}
            ORDER BY wo.WONo DESC
        """

        try:
            with connection.cursor() as cursor:
                logger.debug(f"Executing ECN WO List query: {query}")
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                logger.debug(f"Found {len(results)} work orders with pending ECN")
                return results
        except Exception as e:
            logger.error(f"Error fetching ECN work orders: {str(e)}")
            logger.error(f"Query was: {query}")
            messages.error(self.request, f"Error loading work orders: {str(e)}")
            return []
    
    def get_context_data(self, **kwargs):
        """Add WO categories to context."""
        context = super().get_context_data(**kwargs)
        from sales_distribution.models import TblsdWoCategory
        
        compid = self.request.session.get('compid', 1)
        context['wo_categories'] = TblsdWoCategory.objects.filter(compid=compid).order_by('symbol')
        context['search_type'] = self.request.GET.get('search_type', '0')
        context['search_value'] = self.request.GET.get('search_value', '')
        context['wo_category'] = self.request.GET.get('wo_category', '')
        
        return context
    
    def get_template_names(self):
        """Return partial template for HTMX requests."""
        if self.request.headers.get('HX-Request'):
            return ['design/partials/ecn_wo_list_partial.html']
        return ['design/ecn_wo_list.html']


# ============================================================================
# ECN UNLOCK - Unlock Page
# ============================================================================

class EcnUnlockView(LoginRequiredMixin, View):
    """
    Display and unlock ECN items for a work order.
    Converted from: aaspnet/Module/Design/Transactions/ECNUnlock.aspx
    """
    template_name = 'design/ecn_unlock.html'
    
    def get(self, request, wono):
        """Display ECN items for unlock."""
        from django.db import connection
        from django.shortcuts import render
        import logging

        logger = logging.getLogger(__name__)
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)

        # Get ECN items for this work order
        query = """
            SELECT DISTINCT
                ecn.ItemId,
                COALESCE(item.ItemCode, '') AS ItemCode,
                COALESCE(item.ManfDesc, '') AS ManfDesc,
                COALESCE(unit.Symbol, '') AS UOM
            FROM tblDG_ECN_Master ecn
            INNER JOIN tblDG_Item_Master item ON ecn.ItemId = item.Id
            LEFT JOIN Unit_Master unit ON item.UOMBasic = unit.Id
            WHERE ecn.WONo = %s AND ecn.Flag = 0
            ORDER BY ecn.ItemId DESC
        """

        try:
            with connection.cursor() as cursor:
                logger.debug(f"Fetching ECN items for WO: {wono}")
                cursor.execute(query, [wono])
                columns = [col[0] for col in cursor.description]
                items = []

                for row in cursor.fetchall():
                    item_dict = dict(zip(columns, row))
                    item_id = item_dict['ItemId']

                    # Get BOM Qty
                    bom_qty = self._get_bom_qty(compid, wono, item_id, finyearid)
                    item_dict['BOMQty'] = bom_qty

                    # Get reasons and remarks
                    reasons, remarks = self._get_ecn_reasons_remarks(wono, item_id)
                    item_dict['Reason'] = reasons
                    item_dict['Remarks'] = remarks

                    items.append(item_dict)

                logger.debug(f"Found {len(items)} ECN items for WO {wono}")

        except Exception as e:
            logger.error(f"Error fetching ECN items for WO {wono}: {str(e)}")
            messages.error(request, f"Error loading ECN items: {str(e)}")
            items = []

        context = {
            'wono': wono,
            'items': items
        }

        if request.headers.get('HX-Request'):
            return render(request, 'design/partials/ecn_unlock_partial.html', context)
        return render(request, self.template_name, context)
    
    def post(self, request, wono):
        """Unlock selected ECN items."""
        from django.db import connection, transaction as db_transaction
        
        compid = request.session.get('compid', 1)
        selected_items = request.POST.getlist('selected_items')
        
        if not selected_items:
            messages.warning(request, 'Please select at least one item to unlock.')
            return redirect('design:ecn-unlock-detail', wono=wono)
        
        unlocked_items = []
        
        try:
            with db_transaction.atomic():
                with connection.cursor() as cursor:
                    for item_id in selected_items:
                        # Update BOM Master - set ECNFlag to 0
                        cursor.execute("""
                            UPDATE tblDG_BOM_Master 
                            SET ECNFlag = 0 
                            WHERE ItemId = %s AND WONo = %s AND CompId = %s
                        """, [item_id, wono, compid])
                        
                        # Update ECN Master - set Flag to 1 (unlocked)
                        cursor.execute("""
                            UPDATE tblDG_ECN_Master 
                            SET Flag = 1 
                            WHERE ItemId = %s AND WONo = %s AND CompId = %s
                        """, [item_id, wono, compid])
                        
                        # Get item details for email
                        cursor.execute("""
                            SELECT 
                                item.ItemCode,
                                item.ManfDesc,
                                unit.Symbol AS UOM
                            FROM tblDG_Item_Master item
                            INNER JOIN Unit_Master unit ON item.UOMBasic = unit.Id
                            WHERE item.Id = %s
                        """, [item_id])
                        
                        row = cursor.fetchone()
                        if row:
                            unlocked_items.append({
                                'ItemId': item_id,
                                'ItemCode': row[0],
                                'ManfDesc': row[1],
                                'UOM': row[2]
                            })
            
            messages.success(request, f'Successfully unlocked {len(selected_items)} ECN item(s).')
            
            # TODO: Send email notification (implement email service)
            # self._send_unlock_email(wono, unlocked_items, compid)
            
            return redirect('design:ecn-wo-list')
            
        except Exception as e:
            messages.error(request, f'Error unlocking ECN: {str(e)}')
            return redirect('design:ecn-unlock-detail', wono=wono)
    
    def _get_bom_qty(self, compid, wono, item_id, finyearid):
        """Calculate total BOM quantity for an item."""
        from django.db import connection
        import logging

        logger = logging.getLogger(__name__)

        # Use COALESCE instead of ISNULL for better database compatibility
        query = """
            SELECT COALESCE(SUM(Qty), 0) AS TotalQty
            FROM tblDG_BOM_Master
            WHERE CompId = %s AND WONo = %s AND ItemId = %s AND FinYearId = %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [compid, wono, item_id, finyearid])
                row = cursor.fetchone()
                qty = row[0] if row else 0
                logger.debug(f"BOM Qty for Item {item_id} in WO {wono}: {qty}")
                return qty
        except Exception as e:
            logger.error(f"Error getting BOM qty for item {item_id}: {str(e)}")
            return 0

    def _get_ecn_reasons_remarks(self, wono, item_id):
        """Get concatenated reasons and remarks for an item."""
        from django.db import connection
        import logging

        logger = logging.getLogger(__name__)

        query = """
            SELECT
                COALESCE(reason.Types, '') AS Types,
                COALESCE(detail.Remarks, '') AS Remarks
            FROM tblDG_ECN_Master master
            INNER JOIN tblDG_ECN_Details detail ON master.Id = detail.MId
            LEFT JOIN tblDG_ECN_Reason reason ON detail.ECNReason = reason.Id
            WHERE master.WONo = %s AND master.ItemId = %s
        """

        reasons = []
        remarks = []

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [wono, item_id])
                for row in cursor.fetchall():
                    if row[0]:
                        reasons.append(str(row[0]))
                    if row[1]:
                        remarks.append(str(row[1]))

                logger.debug(f"Found {len(reasons)} reasons and {len(remarks)} remarks for item {item_id}")
        except Exception as e:
            logger.error(f"Error getting ECN reasons for item {item_id}: {str(e)}")

        return ', '.join(reasons) if reasons else '-', ', '.join(remarks) if remarks else '-'


# ============================================================================
# ITEM HISTORY BOM REPORTS
# ============================================================================
