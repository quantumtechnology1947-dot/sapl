"""
Design ECN (Engineering Change Notice) Management Views
Converted from: aspnet/Module/Design/ECN_New.aspx, ECN_Edit.aspx, ECN_Unlock.aspx
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from datetime import datetime
from django.db import transaction
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

from ..models import TbldgEcnMaster, TbldgEcnDetails, TbldgEcnReason, TbldgBomMaster, TbldgItemMaster
from ..forms import EcnMasterForm, EcnDetailsForm
from ..services import BomService
from sales_distribution.models import SdCustWorkorderMaster


class EcnListView(LoginRequiredMixin, ListView):
    """
    Display list of ECNs.
    Converted from: aspnet/Module/Design/Transactions/ECN_Master.aspx
    """
    model = TbldgEcnMaster
    template_name = 'design/ecn_list.html'
    context_object_name = 'ecns'
    paginate_by = 20
    
    def get_queryset(self):
        """Order ECNs by date descending."""
        return TbldgEcnMaster.objects.all().order_by('-id')
    
    def get_context_data(self, **kwargs):
        """Add ECN details to context."""
        context = super().get_context_data(**kwargs)
        
        # For each ECN, get its details
        ecn_data = []
        for ecn in context['ecns']:
            details = TbldgEcnDetails.objects.filter(mid=ecn.id)
            ecn_data.append({
                'ecn': ecn,
                'details': details,
                'status': 'Closed' if ecn.flag == 1 else 'Open'
            })
        
        context['ecn_data'] = ecn_data
        return context


class EcnDetailView(LoginRequiredMixin, DetailView):
    """
    Display ECN details with affected items.
    Converted from: aspnet/Module/Design/Transactions/ECN_Master_Edit.aspx
    """
    model = TbldgEcnMaster
    template_name = 'design/ecn_detail.html'
    context_object_name = 'ecn'
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        """Add ECN details and affected BOM items."""
        context = super().get_context_data(**kwargs)
        
        # Get ECN details (reasons and remarks)
        context['details'] = TbldgEcnDetails.objects.filter(mid=self.object.id)
        
        # Get affected BOM items
        if self.object.wono:
            context['affected_items'] = TbldgBomMaster.objects.filter(
                wono=self.object.wono,
                ecn=self.object.id
            ).select_related('itemid')
        
        # Get status
        context['status'] = 'Closed' if self.object.flag == 1 else 'Open'
        
        return context


class EcnCreateView(LoginRequiredMixin, CreateView):
    """
    Create new ECN.
    Converted from: aspnet/Module/Design/Transactions/ECN_Master.aspx
    """
    model = TbldgEcnMaster
    form_class = EcnMasterForm
    template_name = 'design/ecn_form.html'
    
    def get_context_data(self, **kwargs):
        """Add details formset to context."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['details_form'] = EcnDetailsForm(self.request.POST)
        else:
            context['details_form'] = EcnDetailsForm()
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        """Save ECN master and details."""
        # Add system fields
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessionid = str(self.request.user.id)
        form.instance.compid = 1
        form.instance.finyearid = 1
        form.instance.flag = 0  # Open status
        
        # Save ECN master
        self.object = form.save()
        
        # Save ECN details
        details_form = EcnDetailsForm(self.request.POST)
        if details_form.is_valid():
            detail = details_form.save(commit=False)
            detail.mid = self.object
            
            # Convert ModelChoiceField to ID
            if details_form.cleaned_data.get('ecnreason'):
                detail.ecnreason = details_form.cleaned_data['ecnreason'].id
            
            detail.save()
        
        messages.success(self.request, f'ECN created successfully for work order {self.object.wono}.')
        return redirect('design:ecn-detail', id=self.object.id)


class EcnUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing ECN.
    Converted from: aspnet/Module/Design/Transactions/ECN_Master_Edit.aspx
    """
    model = TbldgEcnMaster
    form_class = EcnMasterForm
    template_name = 'design/ecn_form.html'
    pk_url_kwarg = 'id'
    
    def get_success_url(self):
        """Return to ECN detail."""
        return reverse_lazy('design:ecn-detail', kwargs={'id': self.object.id})
    
    def form_valid(self, form):
        """Update ECN."""
        messages.success(self.request, 'ECN updated successfully.')
        return super().form_valid(form)


class EcnApplyView(LoginRequiredMixin, View):
    """
    Apply ECN to BOM (increment amendment numbers).
    Converted from: aspnet/Module/Design/Transactions/ECN_Master.aspx
    """
    
    @transaction.atomic
    def post(self, request, id):
        """Apply ECN changes to BOM."""
        try:
            ecn = TbldgEcnMaster.objects.get(id=id)
            
            if ecn.flag == 1:
                messages.warning(request, 'ECN is already closed.')
                return redirect('design:ecn-detail', id=id)
            
            # Get all BOM items for this work order
            bom_items = TbldgBomMaster.objects.filter(wono=ecn.wono)
            
            # Increment amendment number for all items
            for item in bom_items:
                item.amdno += 1
                item.ecn = ecn.id
                item.ecnflag = 1
                item.save()
            
            # Mark ECN as closed
            ecn.flag = 1
            ecn.save()
            
            messages.success(
                request, 
                f'ECN applied successfully. {bom_items.count()} items updated.'
            )
            
        except TbldgEcnMaster.DoesNotExist:
            messages.error(request, 'ECN not found.')
        
        return redirect('design:ecn-detail', id=id)


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


