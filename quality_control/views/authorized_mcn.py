"""
Authorized MCN Views

Handles Authorized MCN CRUD operations - showing Work Orders with MCN records.
"""
from django.views.generic import ListView, CreateView, DetailView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db import connection

from .base import QualityControlBaseMixin
from quality_control.models import TblqcAuthorizedmcn
from quality_control.forms import AuthorizedMCNForm


class AuthorizedMCNListView(QualityControlBaseMixin, TemplateView):
    """List Work Orders that have MCN records"""
    template_name = 'quality_control/authorized_mcn/list.html'
    paginate_by = 23  # ASP.NET GridView page size

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get search parameters
        search_query = self.request.GET.get('search', '').strip()
        search_type = self.request.GET.get('search_type', '1')  # Default: WO No (1)
        page = int(self.request.GET.get('page', 1))

        # Calculate pagination offset
        offset = (page - 1) * self.paginate_by

        # Get Work Orders that have MCN records with proper customer names
        with connection.cursor() as cursor:
            comp_id = self.get_compid()

            # Base SQL with proper JOIN to get customer names
            base_sql = """
                SELECT DISTINCT
                    wo.WONo,
                    wo.TaskWorkOrderDate,
                    wo.TaskProjectTitle,
                    COALESCE(cust.CustomerName, '') AS CustomerName,
                    COALESCE(cust.CustomerId, '') AS Code
                FROM SD_Cust_WorkOrder_Master wo
                INNER JOIN tblPM_MaterialCreditNote_Master mcn ON wo.WONo = mcn.WONo
                LEFT JOIN SD_Cust_Master cust ON wo.CustomerId = cust.CustomerId
                WHERE wo.CompId = {comp_id}
            """

            # Add search condition based on search type
            if search_query:
                search_param = search_query.replace("'", "''")  # Escape single quotes
                if search_type == '1':  # WO No
                    base_sql += f" AND wo.WONo LIKE '%{search_param}%'"
                elif search_type == '0':  # Customer
                    base_sql += f" AND cust.CustomerName LIKE '%{search_param}%'"
                elif search_type == '2':  # Project Title
                    base_sql += f" AND wo.TaskProjectTitle LIKE '%{search_param}%'"

            # Count total records for pagination
            count_sql = f"SELECT COUNT(*) FROM ({base_sql}) AS subquery"
            cursor.execute(count_sql.format(comp_id=comp_id))
            total_count = cursor.fetchone()[0]

            # Add ordering and pagination
            sql = base_sql + f"""
                ORDER BY wo.TaskWorkOrderDate DESC, wo.WONo
                LIMIT {self.paginate_by} OFFSET {offset}
            """

            cursor.execute(sql.format(comp_id=comp_id))

            work_orders = []
            for row in cursor.fetchall():
                work_orders.append({
                    'wo_no': row[0] or '',
                    'wo_date': row[1] or '',
                    'project_title': row[2] or '',
                    'customer_name': row[3] or '',
                    'code': row[4] or ''
                })

        # Calculate pagination info
        total_pages = (total_count + self.paginate_by - 1) // self.paginate_by
        has_previous = page > 1
        has_next = page < total_pages

        context['work_orders'] = work_orders
        context['search_query'] = search_query
        context['search_type'] = search_type
        context['page'] = page
        context['total_pages'] = total_pages
        context['total_count'] = total_count
        context['has_previous'] = has_previous
        context['has_next'] = has_next
        context['page_range'] = range(1, total_pages + 1)

        return context


class AuthorizedMCNAutocompleteView(QualityControlBaseMixin, TemplateView):
    """Autocomplete endpoint for customer search"""
    template_name = 'quality_control/authorized_mcn/autocomplete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('q', '').strip()
        search_type = self.request.GET.get('search_type', '1')

        suggestions = []

        if search_query and len(search_query) >= 2:  # Minimum 2 characters
            with connection.cursor() as cursor:
                comp_id = self.get_compid()
                search_param = search_query.replace("'", "''")

                if search_type == '1':  # WO No
                    sql = f"""
                        SELECT DISTINCT wo.WONo
                        FROM SD_Cust_WorkOrder_Master wo
                        INNER JOIN tblPM_MaterialCreditNote_Master mcn ON wo.WONo = mcn.WONo
                        WHERE wo.CompId = {comp_id}
                          AND wo.WONo LIKE '%{search_param}%'
                        ORDER BY wo.WONo
                        LIMIT 10
                    """
                elif search_type == '0':  # Customer
                    sql = f"""
                        SELECT DISTINCT cust.CustomerName
                        FROM SD_Cust_WorkOrder_Master wo
                        INNER JOIN tblPM_MaterialCreditNote_Master mcn ON wo.WONo = mcn.WONo
                        LEFT JOIN SD_Cust_Master cust ON wo.CustomerId = cust.CustomerId
                        WHERE wo.CompId = {comp_id}
                          AND cust.CustomerName LIKE '%{search_param}%'
                        ORDER BY cust.CustomerName
                        LIMIT 10
                    """
                elif search_type == '2':  # Project Title
                    sql = f"""
                        SELECT DISTINCT wo.TaskProjectTitle
                        FROM SD_Cust_WorkOrder_Master wo
                        INNER JOIN tblPM_MaterialCreditNote_Master mcn ON wo.WONo = mcn.WONo
                        WHERE wo.CompId = {comp_id}
                          AND wo.TaskProjectTitle LIKE '%{search_param}%'
                        ORDER BY wo.TaskProjectTitle
                        LIMIT 10
                    """
                else:
                    context['suggestions'] = []
                    return context

                cursor.execute(sql)
                suggestions = [row[0] for row in cursor.fetchall() if row[0]]

        context['suggestions'] = suggestions
        return context


class AuthorizedMCNCreateView(QualityControlBaseMixin, CreateView):
    """Create new Authorized MCN"""
    model = TblqcAuthorizedmcn
    form_class = AuthorizedMCNForm
    template_name = 'quality_control/authorized_mcn/form.html'
    success_url = reverse_lazy('quality_control:authorized-mcn-list')

    def form_valid(self, form):
        # Set session metadata
        for field, value in self.get_session_metadata().items():
            setattr(form.instance, field, value)
        messages.success(self.request, 'Authorized MCN created successfully')
        return super().form_valid(form)


class AuthorizedMCNDetailView(QualityControlBaseMixin, TemplateView):
    """View MCN items for a Work Order and authorize them"""
    template_name = 'quality_control/authorized_mcn/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wo_no = self.kwargs.get('wo_no')

        # Get Work Order details
        with connection.cursor() as cursor:
            comp_id = self.get_compid()

            # Get WO header info
            sql = f"""
                SELECT
                    wo.WONo,
                    wo.TaskProjectTitle,
                    COALESCE(cust.CustomerName, '') AS CustomerName
                FROM SD_Cust_WorkOrder_Master wo
                LEFT JOIN SD_Cust_Master cust ON wo.CustomerId = cust.CustomerId
                WHERE wo.WONo = '{wo_no}' AND wo.CompId = {comp_id}
            """
            cursor.execute(sql)
            wo_row = cursor.fetchone()

            if wo_row:
                context['wo_no'] = wo_row[0]
                context['project_title'] = wo_row[1]
                context['customer_name'] = wo_row[2]
            else:
                context['wo_no'] = wo_no
                context['project_title'] = ''
                context['customer_name'] = ''

            # Get MCN line items for this Work Order
            # Note: tblPM_MaterialCreditNote_Details has: Id, MId (Master Id), PId, CId, MCNQty
            sql = f"""
                SELECT
                    mcn_det.Id,
                    mcn_det.MId,
                    mcn_det.PId,
                    mcn_det.CId,
                    mcn_mas.MCNNo,
                    mcn_mas.SysDate AS MCNDate,
                    COALESCE(item.ItemCode, '') AS ItemCode,
                    COALESCE(item.Description, '') AS Description,
                    COALESCE(item.UOM, '') AS UOM,
                    COALESCE(mcn_det.MCNQty, 0) AS MCNQty,
                    COALESCE(
                        (SELECT SUM(auth.QAQty)
                         FROM tblQc_AuthorizedMCN auth
                         WHERE auth.MCNDId = mcn_det.Id
                         AND auth.MCNId = mcn_det.MId), 0
                    ) AS TotQAQty,
                    COALESCE(item.DrawingNo, '') AS DrawingNo,
                    COALESCE(item.SpecSheet, '') AS SpecSheet
                FROM tblPM_MaterialCreditNote_Details mcn_det
                INNER JOIN tblPM_MaterialCreditNote_Master mcn_mas ON mcn_det.MId = mcn_mas.Id
                LEFT JOIN MM_Cust_Master item ON mcn_det.PId = item.ItemId
                WHERE mcn_mas.WONo = '{wo_no}'
                ORDER BY mcn_mas.SysDate DESC, mcn_det.Id
            """
            cursor.execute(sql)

            mcn_items = []
            for row in cursor.fetchall():
                mcn_items.append({
                    'id': row[0],          # mcn_det.Id (Detail Id)
                    'mcn_id': row[1],      # mcn_det.MId (Master Id)
                    'p_id': row[2],        # mcn_det.PId
                    'c_id': row[3],        # mcn_det.CId
                    'mcn_no': row[4] or '',      # MCNNo
                    'mcn_date': row[5] or '',    # MCNDate
                    'item_code': row[6] or '',   # ItemCode
                    'description': row[7] or '', # Description
                    'uom': row[8] or '',         # UOM
                    'mcn_qty': row[9] or 0,      # MCNQty
                    'tot_qa_qty': row[10] or 0,  # TotQAQty
                    'has_drawing': bool(row[11]), # DrawingNo
                    'has_spec': bool(row[12]),    # SpecSheet
                    'item_id': row[2],     # Use PId as item_id for item downloads
                })

        context['mcn_items'] = mcn_items

        return context

    def post(self, request, *args, **kwargs):
        """Handle authorization submission"""
        wo_no = self.kwargs.get('wo_no')

        # Get selected items and quantities
        selected_items = []
        for key in request.POST:
            if key.startswith('check_'):
                item_id = key.replace('check_', '')
                qa_qty = request.POST.get(f'qa_qty_{item_id}', '0')

                try:
                    qa_qty = float(qa_qty)
                    if qa_qty > 0:
                        # Get MCN details from hidden fields (using Master Id, not detail Id)
                        mcn_master_id = request.POST.get(f'mcn_master_id_{item_id}')
                        mcn_detail_id = request.POST.get(f'mcn_detail_id_{item_id}')

                        selected_items.append({
                            'mcn_master_id': mcn_master_id,
                            'mcn_detail_id': mcn_detail_id,
                            'qa_qty': qa_qty,
                        })
                except (ValueError, TypeError):
                    continue

        if not selected_items:
            messages.error(request, 'Please select at least one item and enter QA quantity')
            return self.get(request, *args, **kwargs)

        # Save authorized MCN records
        from datetime import datetime
        from quality_control.models import TblqcAuthorizedmcn

        for item in selected_items:
            auth_mcn = TblqcAuthorizedmcn()
            # Use the correct field names that exist in the database table
            auth_mcn.mcnid = item['mcn_master_id']  # Master table Id
            auth_mcn.mcndid = item['mcn_detail_id']  # Detail table Id
            auth_mcn.qaqty = item['qa_qty']

            # Set audit fields
            auth_mcn.sysdate = datetime.now().strftime('%d-%m-%Y')
            auth_mcn.systime = datetime.now().strftime('%H:%M:%S')
            auth_mcn.sessionid = str(request.user.id)
            auth_mcn.compid = request.session.get('compid', 1)
            auth_mcn.finyearid = request.session.get('finyearid', 1)

            auth_mcn.save()

        messages.success(request, f'Successfully authorized {len(selected_items)} MCN items')
        return redirect('quality_control:authorized-mcn-list')


class OriginalAuthorizedMCNDetailView(QualityControlBaseMixin, DetailView):
    """View Authorized MCN details (old implementation)"""
    model = TblqcAuthorizedmcn
    template_name = 'quality_control/authorized_mcn/record_detail.html'
    context_object_name = 'authorized_mcn'


class AuthorizedMCNDeleteView(QualityControlBaseMixin, DeleteView):
    """Delete Authorized MCN"""
    model = TblqcAuthorizedmcn
    template_name = 'quality_control/authorized_mcn/delete.html'
    success_url = reverse_lazy('quality_control:authorized-mcn-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Authorized MCN deleted successfully')
        return super().delete(request, *args, **kwargs)
