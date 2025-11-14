"""
Plan Detail Views
"""

from datetime import datetime
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q

from .base import MaterialPlanningBaseMixin
from material_planning.models import (
    TblmpMaterialMaster, TblmpMaterialDetail, TblmpMaterialRawmaterial,
    TblmpMaterialProcess, TblmpMaterialFinish, TblplnProcessMaster,
    TblmpMaterialDetailTemp, TblmpMaterialRawmaterialTemp,
    TblmpMaterialProcessTemp, TblmpMaterialFinishTemp,
)
from material_planning.services import BOMService, PlanningService, PRService
from design.models import TbldgItemMaster
from sales_distribution.models import SdCustWorkorderMaster
from sys_admin.models import TblfinancialMaster
from material_management.models import PRMaster, PRDetails, Supplier




class PlanningEditView(MaterialPlanningBaseMixin, ListView):
    """
    Edit existing planning records with search and inline editing
    Converted from: Planning_Edit.txt
    """
    model = TblmpMaterialMaster
    template_name = 'material_planning/transactions/planning_edit.html'
    context_object_name = 'plans'
    paginate_by = 15

    def get_queryset(self):
        from material_management.models import Supplier
        from django.db import connection

        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get search parameters
        search_field = self.request.GET.get('search_field', '')
        search_value = self.request.GET.get('search_value', '').strip()

        # Base queryset
        queryset = TblmpMaterialMaster.objects.filter(
            compid=compid,
            finyearid__lte=finyearid
        ).order_by('-id')

        # Apply search filters
        if search_value:
            if search_field == 'supplier':  # Supplier Name
                # Extract supplier ID from "Name [ID]" format
                if '[' in search_value and ']' in search_value:
                    supplier_id = search_value.split('[')[1].split(']')[0]
                    queryset = queryset.filter(supplier_id=supplier_id)
                else:
                    # Search by supplier name
                    suppliers = Supplier.objects.filter(
                        supplier_name__icontains=search_value,
                        comp_id=compid
                    ).values_list('supplierid', flat=True)
                    queryset = queryset.filter(supplierid__in=suppliers)

            elif search_field == 'plno':  # PL No
                queryset = queryset.filter(plno__icontains=search_value)

        return queryset

    def get_context_data(self, **kwargs):
        from material_management.models import Supplier

        context = super().get_context_data(**kwargs)
        context['search_field'] = self.request.GET.get('search_field', '')
        context['search_value'] = self.request.GET.get('search_value', '')

        # Enrich plans with supplier names and financial year
        for plan in context['plans']:
            # Supplier info is in detail tables, not master
            plan.supplier_name = "-"

            # Get financial year
            try:
                fy = TblfinancialMaster.objects.get(finyearid=plan.finyearid)
                plan.finyear_name = fy.finyear
            except TblfinancialMaster.DoesNotExist:
                plan.finyear_name = str(plan.finyearid)

            # Completion date is in detail tables, not master
            plan.compdate_display = "-"

            # Check if already in PR (disable edit if yes)
            plan.can_edit = self._check_can_edit(plan)

        return context

    def _check_can_edit(self, plan):
        """Check if plan items are already in PR"""
        from material_management.models import PRDetails, PRMaster

        # Check if any item from this plan is in PR
        pr_exists = PRDetails.objects.filter(
            pr__comp_id=self.get_compid(),
            item=plan.itemid
        ).exists() if plan.itemid else False

        return not pr_exists

    # POST method removed - supplier/compdate are in detail tables, not master

class PlanningEditDetailsView(MaterialPlanningBaseMixin, TemplateView):
    """
    Edit planning item details - Raw Material & Processing Material
    Converted from: Planning_Edit_Details.txt
    """
    template_name = 'material_planning/transactions/planning_edit_details.html'

    def get_context_data(self, **kwargs):
        from design.models import TbldgItemMaster
        from sys_admin.models import UnitMaster
        from material_management.models import Supplier, PRDetails

        context = super().get_context_data(**kwargs)
        plno = kwargs.get('plno')
        mid = kwargs.get('mid')

        context['plno'] = plno
        context['mid'] = mid

        # Get WO number from master record
        try:
            master = TblmpMaterialMaster.objects.get(id=mid)
            context['wono'] = master.wono
        except TblmpMaterialMaster.DoesNotExist:
            context['wono'] = '-'

        # Get Raw Material items
        raw_materials = TblmpMaterialRawmaterial.objects.filter(
            detail__master__id=plan_id
        ).order_by('-id')

        # Enrich raw material data
        raw_materials_enriched = []
        for rm in raw_materials:
            try:
                item = TbldgItemMaster.objects.get(id=rm.item)
                unit = UnitMaster.objects.get(id=item.uombasic) if item.uombasic else None

                # Get supplier name
                supplier_name = "-"
                if rm.supplierid:
                    try:
                        supplier = Supplier.objects.get(
                            supplier_id=rm.supplierid,
                            comp_id=self.get_compid()
                        )
                        supplier_name = f"{supplier.supplier_name} [{supplier.supplier_id}]"
                    except:
                        supplier_name = rm.supplierid

                # Check if in PR
                in_pr = PRDetails.objects.filter(
                    m_id__in=PRMaster.objects.filter(comp_id=self.get_compid()).values_list('pr_id', flat=True),
                    item_id=rm.item
                ).exists()

                raw_materials_enriched.append({
                    'id': rm.id,
                    'plno': rm.plno,
                    'item_id': rm.item,
                    'item_code': item.itemcode if item else '',
                    'description': item.manfdesc if item else '',
                    'uom': unit.symbol if unit else '',
                    'qty': rm.qty or 0,
                    'supplier_name': supplier_name,
                    'compdate': rm.compdate or '',
                    'compdate_display': self._format_date(rm.compdate),
                    'pid': rm.pid,
                    'cid': rm.cid,
                    'in_pr': in_pr,
                    'can_edit': not in_pr
                })
            except Exception as e:
                continue

        context['raw_materials'] = raw_materials_enriched

        # Get Process items
        process_items = TblmpMaterialProcess.objects.filter(
            detail__master__id=plan_id
        ).order_by('-id')

        # Enrich process data
        process_items_enriched = []
        for proc in process_items:
            try:
                item = TbldgItemMaster.objects.get(id=proc.item)
                unit = UnitMaster.objects.get(id=item.uombasic) if item.uombasic else None

                # Get supplier name
                supplier_name = "-"
                if proc.supplierid:
                    try:
                        supplier = Supplier.objects.get(
                            supplier_id=proc.supplierid,
                            comp_id=self.get_compid()
                        )
                        supplier_name = f"{supplier.supplier_name} [{supplier.supplier_id}]"
                    except:
                        supplier_name = proc.supplierid

                # Check if in PR
                in_pr = PRDetails.objects.filter(
                    pr__comp_id=self.get_compid(),
                    item=proc.item
                ).exists()

                process_items_enriched.append({
                    'id': proc.id,
                    'plno': proc.plno,
                    'item_id': proc.item,
                    'item_code': item.itemcode if item else '',
                    'description': item.manfdesc if item else '',
                    'uom': unit.symbol if unit else '',
                    'qty': proc.qty or 0,
                    'supplier_name': supplier_name,
                    'compdate': proc.compdate or '',
                    'compdate_display': self._format_date(proc.compdate),
                    'pid': proc.pid,
                    'cid': proc.cid,
                    'in_pr': in_pr,
                    'can_edit': not in_pr
                })
            except Exception as e:
                continue

        context['process_items'] = process_items_enriched

        return context

    def _format_date(self, date_str):
        """Convert YYYY-MM-DD to DD-MM-YYYY"""
        if not date_str:
            return "-"
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except:
            return date_str

    def post(self, request, plno, mid):
        """Handle bulk update of selected items"""
        from datetime import datetime

        update_type = request.POST.get('update_type')  # 'raw' or 'process'

        updated_count = 0

        try:
            if update_type == 'raw':
                # Get selected items and update data
                selected_ids = request.POST.getlist('raw_items')
                supplier_text = request.POST.get('raw_supplier', '').strip()
                compdate = request.POST.get('raw_compdate', '')

                if not selected_ids:
                    messages.warning(request, 'Please select at least one item to update.')
                    return redirect('material_planning:planning-edit-details', plno=plno, mid=mid)

                if not supplier_text and not compdate:
                    messages.warning(request, 'Please enter either supplier name or completion date.')
                    return redirect('material_planning:planning-edit-details', plno=plno, mid=mid)

                # Update each selected raw material item
                for item_id in selected_ids:
                    rm = TblmpMaterialRawmaterial.objects.get(id=item_id)

                    # Update supplier if provided
                    if supplier_text:
                        # Extract supplier ID from "Name [ID]" format if present
                        if '[' in supplier_text and ']' in supplier_text:
                            supplier_id = supplier_text.split('[')[1].split(']')[0]
                            rm.supplierid = supplier_id
                        else:
                            rm.supplierid = supplier_text

                    # Update completion date if provided
                    if compdate:
                        # Date comes from input type="date" in YYYY-MM-DD format
                        rm.compdate = compdate

                    rm.save()
                    updated_count += 1

            elif update_type == 'process':
                # Get selected items and update data
                selected_ids = request.POST.getlist('process_items')
                supplier_text = request.POST.get('process_supplier', '').strip()
                compdate = request.POST.get('process_compdate', '')

                if not selected_ids:
                    messages.warning(request, 'Please select at least one item to update.')
                    return redirect('material_planning:planning-edit-details', plno=plno, mid=mid)

                if not supplier_text and not compdate:
                    messages.warning(request, 'Please enter either supplier name or completion date.')
                    return redirect('material_planning:planning-edit-details', plno=plno, mid=mid)

                # Update each selected process item
                for item_id in selected_ids:
                    proc = TblmpMaterialProcess.objects.get(id=item_id)

                    # Update supplier if provided
                    if supplier_text:
                        # Extract supplier ID from "Name [ID]" format if present
                        if '[' in supplier_text and ']' in supplier_text:
                            supplier_id = supplier_text.split('[')[1].split(']')[0]
                            proc.supplierid = supplier_id
                        else:
                            proc.supplierid = supplier_text

                    # Update completion date if provided
                    if compdate:
                        # Date comes from input type="date" in YYYY-MM-DD format
                        proc.compdate = compdate

                    proc.save()
                    updated_count += 1

            if updated_count > 0:
                messages.success(request, f'Successfully updated {updated_count} items!')
                return redirect('material_planning:planning-edit-details', plno=plno, mid=mid)
            else:
                messages.warning(request, 'No items were updated.')
                return redirect('material_planning:planning-edit-details', plno=plno, mid=mid)

        except Exception as e:
            messages.error(request, f'Error updating items: {str(e)}')
            return redirect('material_planning:planning-edit-details', plno=plno, mid=mid)


# ============================================================================
# HTMX ENDPOINTS
# ============================================================================

class BomItemDetailView(MaterialPlanningBaseMixin, TemplateView):
    """
    Load detail panel for a BOM item (Raw Material/Processing/Finish grids).
    This is triggered when user clicks on item code.
    """
    template_name = 'material_planning/transactions/partials/bom_item_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wono = kwargs.get('wono')
        item_id = kwargs.get('item_id')

        from design.models import TbldgItemMaster

        try:
            item = TbldgItemMaster.objects.get(id=item_id)
            context['item_id'] = item_id
            context['item_code'] = item.itemcode or item.partno or ''

            # Calculate BOM qty using BOMService
            from material_planning.services import BOMService
            bom_qty = BOMService.all_component_bom_qty(
                self.get_compid(),
                wono,
                item_id,
                self.get_finyearid()
            )
            context['bom_qty'] = bom_qty
            context['wono'] = wono
            context['available'] = bom_qty  # For now, set available = bom_qty (will be refined later)

        except TbldgItemMaster.DoesNotExist:
            context['item_id'] = item_id
            context['item_code'] = 'Unknown'
            context['bom_qty'] = 0
            context['wono'] = wono
            context['available'] = 0

        return context

class AddToTempView(MaterialPlanningBaseMixin, View):
    """
    Save procurement data to temporary tables (Add to Temp button)
    Converted from: aaspnet/Module/MaterialPlanning/Transactions/pdt.aspx.cs btnAddToTemp_Click (lines 402-500)

    Workflow:
    1. User selects an item from BOM grid
    2. User selects procurement strategy (RM/Process/Finish)
    3. User enters supplier quotes in grid
    4. Click "Add to Temp" → Save to temp tables
    5. Repeat for other items
    6. Click "Generate PLN" → Migrate temp → permanent
    """
    def post(self, request, wono):
        """
        CRITICAL FIX: Support MULTIPLE procurement types in one submission
        ASP.NET allows checking RM + Process + Finish simultaneously (lines 1613-1920)
        Creates ONE detail_temp record with MULTIPLE child records in different temp tables
        """
        try:
            # Get audit fields
            user_id = str(request.user.id)
            compid = request.session.get('company_id', 1)
            finyearid = request.session.get('financial_year_id', 1)
            now = datetime.now()
            sysdate = now.strftime('%d-%m-%Y')
            systime = now.strftime('%H:%M:%S')

            # Get posted data
            item_id = request.POST.get('item_id')
            bom_qty = request.POST.get('bom_qty')
            available = request.POST.get('available')

            if not item_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required field: item_id'
                }, status=400)

            # Check which procurement types are checked
            rm_checked = request.POST.get('rm_checked') == 'true'
            pro_checked = request.POST.get('pro_checked') == 'true'
            fin_checked = request.POST.get('fin_checked') == 'true'

            # DEBUG: Log ALL POST data to file (bypass buffering)
            import os
            debug_file = os.path.join('debug_post.txt')
            with open(debug_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"TIMESTAMP: {datetime.now()}\n")
                f.write(f"WONO: {wono}, ITEM_ID: {item_id}\n")
                f.write(f"DEBUG POST DATA:\n")
                for key, values in request.POST.lists():
                    f.write(f"  {key}: {values}\n")
                f.write(f"DEBUG FLAGS: rm={rm_checked}, pro={pro_checked}, fin={fin_checked}\n")
                f.write(f"{'='*80}\n")

            if not (rm_checked or pro_checked or fin_checked):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please select at least one procurement type (Raw Material, Process, or Finish)'
                }, status=400)

            saved_count = 0
            detail_temp_ids = []

            # Step 1: Process Raw Material [A] if checked (pdt.aspx.cs lines 1613-1710)
            if rm_checked:
                suppliers = request.POST.getlist('rm_supplier[]')
                quantities = request.POST.getlist('rm_qty[]')
                rates = request.POST.getlist('rm_rate[]')
                discounts = request.POST.getlist('rm_discount[]')
                dates = request.POST.getlist('rm_deldate[]')

                # DEBUG
                with open('debug_post.txt', 'a') as f:
                    f.write(f"DEBUG RM: suppliers={suppliers}, quantities={quantities}, rates={rates}\n")

                # Check if we have valid data
                has_rm_data = any(s.strip() for s in suppliers if s)
                with open('debug_post.txt', 'a') as f:
                    f.write(f"DEBUG RM: has_rm_data={has_rm_data}\n")

                if has_rm_data:
                    try:
                        with open('debug_post.txt', 'a') as f:
                            f.write(f"DEBUG RM: About to create detail_temp...\n")

                        # Create detail temp with RM flag
                        detail_temp = TblmpMaterialDetailTemp.objects.create(
                            wono=wono,
                            item=int(item_id),
                            bomqty=float(bom_qty) if bom_qty else 0,
                            available=float(available) if available else 0,
                            sessionid=user_id,
                            compid=compid,
                            finyearid=finyearid,
                            sysdate=sysdate,
                            systime=systime
                        )
                        detail_temp_ids.append(detail_temp.id)

                        with open('debug_post.txt', 'a') as f:
                            f.write(f"DEBUG RM: Created detail_temp with ID={detail_temp.id}\n")

                        # Save supplier quotes
                        for i in range(len(suppliers)):
                            if suppliers[i] and suppliers[i].strip():
                                qty = float(quantities[i]) if i < len(quantities) and quantities[i] else 0
                                rate = float(rates[i]) if i < len(rates) and rates[i] else 0
                                discount = float(discounts[i]) if i < len(discounts) and discounts[i] else 0
                                total = (qty * rate) - discount

                                TblmpMaterialRawmaterialTemp.objects.create(
                                    dmid=detail_temp.id,
                                    supplier=suppliers[i],
                                    qty=qty,
                                    rate=rate,
                                    discount=discount,
                                    deliverydate=dates[i] if i < len(dates) else '',
                                    total=total,
                                    sessionid=user_id
                                )
                                saved_count += 1
                                with open('debug_post.txt', 'a') as f:
                                    f.write(f"DEBUG RM: Saved supplier quote, saved_count={saved_count}\n")
                    except Exception as e:
                        with open('debug_post.txt', 'a') as f:
                            f.write(f"DEBUG RM: EXCEPTION: {str(e)}\n")
                        raise

            # Step 2: Process Process [O] if checked (pdt.aspx.cs lines 1711-1815)
            if pro_checked:
                suppliers = request.POST.getlist('pro_supplier[]')
                quantities = request.POST.getlist('pro_qty[]')
                rates = request.POST.getlist('pro_rate[]')
                discounts = request.POST.getlist('pro_discount[]')
                dates = request.POST.getlist('pro_deldate[]')

                # DEBUG
                with open('debug_post.txt', 'a') as f:
                    f.write(f"DEBUG PRO: suppliers={suppliers}, quantities={quantities}, rates={rates}\n")

                # Check if we have valid data
                has_pro_data = any(s.strip() for s in suppliers if s)
                with open('debug_post.txt', 'a') as f:
                    f.write(f"DEBUG PRO: has_pro_data={has_pro_data}\n")

                if has_pro_data:
                    try:
                        with open('debug_post.txt', 'a') as f:
                            f.write(f"DEBUG PRO: About to create detail_temp...\n")

                        # Create detail temp with PRO flag
                        detail_temp = TblmpMaterialDetailTemp.objects.create(
                            wono=wono,
                            item=int(item_id),
                            bomqty=float(bom_qty) if bom_qty else 0,
                            available=float(available) if available else 0,
                            sessionid=user_id,
                            compid=compid,
                            finyearid=finyearid,
                            sysdate=sysdate,
                            systime=systime
                        )
                        detail_temp_ids.append(detail_temp.id)

                        with open('debug_post.txt', 'a') as f:
                            f.write(f"DEBUG PRO: Created detail_temp with ID={detail_temp.id}\n")

                        # Save supplier quotes
                        for i in range(len(suppliers)):
                            if suppliers[i] and suppliers[i].strip():
                                qty = float(quantities[i]) if i < len(quantities) and quantities[i] else 0
                                rate = float(rates[i]) if i < len(rates) and rates[i] else 0
                                discount = float(discounts[i]) if i < len(discounts) and discounts[i] else 0
                                total = (qty * rate) - discount

                                TblmpMaterialProcessTemp.objects.create(
                                    dmid=detail_temp.id,
                                    supplier=suppliers[i],
                                    qty=qty,
                                    rate=rate,
                                    discount=discount,
                                    deliverydate=dates[i] if i < len(dates) else '',
                                    total=total,
                                    sessionid=user_id
                                )
                                saved_count += 1
                                with open('debug_post.txt', 'a') as f:
                                    f.write(f"DEBUG PRO: Saved supplier quote, saved_count={saved_count}\n")
                    except Exception as e:
                        with open('debug_post.txt', 'a') as f:
                            f.write(f"DEBUG PRO: EXCEPTION: {str(e)}\n")
                        raise

            # Step 3: Process Finish [F] if checked (pdt.aspx.cs lines 1816-1920)
            if fin_checked:
                suppliers = request.POST.getlist('fin_supplier[]')
                quantities = request.POST.getlist('fin_qty[]')
                rates = request.POST.getlist('fin_rate[]')
                discounts = request.POST.getlist('fin_discount[]')
                dates = request.POST.getlist('fin_deldate[]')

                # DEBUG
                with open('debug_post.txt', 'a') as f:
                    f.write(f"DEBUG FIN: suppliers={suppliers}, quantities={quantities}, rates={rates}\n")

                # Check if we have valid data
                has_fin_data = any(s.strip() for s in suppliers if s)
                with open('debug_post.txt', 'a') as f:
                    f.write(f"DEBUG FIN: has_fin_data={has_fin_data}\n")

                if has_fin_data:
                    # Create detail temp with FIN flag
                    detail_temp = TblmpMaterialDetailTemp.objects.create(
                        wono=wono,
                        item=int(item_id),
                        bomqty=float(bom_qty) if bom_qty else 0,
                        available=float(available) if available else 0,
                        sessionid=user_id,
                        compid=compid,
                        finyearid=finyearid,
                        sysdate=sysdate,
                        systime=systime
                    )
                    detail_temp_ids.append(detail_temp.id)

                    # Save supplier quotes
                    for i in range(len(suppliers)):
                        if suppliers[i] and suppliers[i].strip():
                            qty = float(quantities[i]) if i < len(quantities) and quantities[i] else 0
                            rate = float(rates[i]) if i < len(rates) and rates[i] else 0
                            discount = float(discounts[i]) if i < len(discounts) and discounts[i] else 0
                            total = (qty * rate) - discount

                            TblmpMaterialFinishTemp.objects.create(
                                dmid=detail_temp.id,
                                supplier=suppliers[i],
                                qty=qty,
                                rate=rate,
                                discount=discount,
                                deliverydate=dates[i] if i < len(dates) else '',
                                total=total,
                                sessionid=user_id
                            )
                            saved_count += 1

            if saved_count == 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No supplier data entered. Please fill in at least one row.'
                }, status=400)

            return JsonResponse({
                'status': 'success',
                'message': f'Added to temporary planning ({saved_count} supplier quotes saved)',
                'detail_temp_ids': detail_temp_ids,
                'saved_count': saved_count
            })

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in AddToTempView: {e}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class PlanningSaveView(MaterialPlanningBaseMixin, View):
    """
    Generate PLN from temporary tables (Generate PLN button)
    Converted from: aaspnet/Module/MaterialPlanning/Transactions/pdt.aspx.cs btnGenerate_Click (lines 502-650)

    Workflow:
    1. Generate PLN number in format PLN/YYYY-YY/XXXX
    2. Get all temp detail records for current user
    3. For each temp detail:
       - Create permanent detail record
       - Check which temp table has quotes (RM/Process/Finish)
       - Copy quotes to permanent table
       - Set RM='A' or PRO='O' or FIN='F' flag
    4. Create master record with PLN number
    5. Delete all temp records for user
    """
    def post(self, request, wono):
        from django.http import JsonResponse
        from django.db import transaction
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Get audit fields
            user_id = str(request.user.id)
            compid = request.session.get('company_id', 1)
            finyearid = request.session.get('financial_year_id', 1)
            now = datetime.now()
            sysdate = now.strftime('%d-%m-%Y')
            systime = now.strftime('%H:%M:%S')

            # Step 1: Generate PLN number
            pln_no = PlanningService.generate_pln_number(compid, finyearid)

            # Step 2: Atomic transaction
            with transaction.atomic():
                # Get all temp detail records for this user and WO
                temp_details = TblmpMaterialDetailTemp.objects.filter(
                    sessionid=user_id,
                    wono=wono
                )

                if not temp_details.exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No temporary data found. Please add items to temp first.'
                    }, status=400)

                # Step 3: Create master record first
                master = TblmpMaterialMaster.objects.create(
                    plno=pln_no,
                    wono=wono,
                    sysdate=sysdate,
                    systime=systime,
                    sessionid=user_id,
                    compid=compid,
                    finyearid=finyearid
                )

                # Step 4: Process each temp detail record
                for temp_detail in temp_details:
                    # Create permanent detail record
                    # Note: TblmpMaterialDetail only has: id, item, rm, pro, fin, master
                    perm_detail = TblmpMaterialDetail.objects.create(
                        master=master,  # Link to master record
                        item=temp_detail.item,
                        # RM/PRO/FIN flags will be set below based on which temp tables have data
                        rm=None,
                        pro=None,
                        fin=None
                    )

                    # Check which temp table has quotes and copy them

                    # Raw Material?
                    raw_temps = TblmpMaterialRawmaterialTemp.objects.filter(
                        dmid=temp_detail.id,
                        sessionid=user_id
                    )
                    if raw_temps.exists():
                        # Set RM flag (IntegerField: 1 = true, NULL = false)
                        perm_detail.rm = 1
                        perm_detail.save()

                        # Copy all raw material rows
                        for raw_temp in raw_temps:
                            TblmpMaterialRawmaterial.objects.create(
                                detail=perm_detail,  # Foreign key to TblmpMaterialDetail
                                item=temp_detail.item,
                                supplierid=raw_temp.supplier,
                                qty=raw_temp.qty,
                                rate=raw_temp.rate,
                                discount=raw_temp.discount,
                                deldate=raw_temp.deliverydate
                            )

                    # Process?
                    pro_temps = TblmpMaterialProcessTemp.objects.filter(
                        dmid=temp_detail.id,
                        sessionid=user_id
                    )
                    if pro_temps.exists():
                        # Set PRO flag (IntegerField: 1 = true, NULL = false)
                        perm_detail.pro = 1
                        perm_detail.save()

                        # Copy all process rows
                        for pro_temp in pro_temps:
                            TblmpMaterialProcess.objects.create(
                                detail=perm_detail,  # Foreign key to TblmpMaterialDetail
                                item=temp_detail.item,
                                supplierid=pro_temp.supplier,
                                qty=pro_temp.qty,
                                rate=pro_temp.rate,
                                discount=pro_temp.discount,
                                deldate=pro_temp.deliverydate
                            )

                    # Finish?
                    fin_temps = TblmpMaterialFinishTemp.objects.filter(
                        dmid=temp_detail.id,
                        sessionid=user_id
                    )
                    if fin_temps.exists():
                        # Set FIN flag (IntegerField: 1 = true, NULL = false)
                        perm_detail.fin = 1
                        perm_detail.save()

                        # Copy all finish rows
                        for fin_temp in fin_temps:
                            TblmpMaterialFinish.objects.create(
                                detail=perm_detail,  # Foreign key to TblmpMaterialDetail
                                item=temp_detail.item,
                                supplierid=fin_temp.supplier,
                                qty=fin_temp.qty,
                                rate=fin_temp.rate,
                                discount=fin_temp.discount,
                                deldate=fin_temp.deliverydate
                            )

                # Step 5: Delete all temp records for this user
                # Delete in reverse order (quotes first, then details)
                TblmpMaterialRawmaterialTemp.objects.filter(sessionid=user_id).delete()
                TblmpMaterialProcessTemp.objects.filter(sessionid=user_id).delete()
                TblmpMaterialFinishTemp.objects.filter(sessionid=user_id).delete()
                TblmpMaterialDetailTemp.objects.filter(sessionid=user_id).delete()

            # Redirect to plan list instead of detail page to avoid URL encoding issues
            # Plan numbers contain slashes (PLN/2013-14/0001) which cause routing problems
            return JsonResponse({
                'status': 'success',
                'message': f'PLN {pln_no} generated successfully',
                'pln_no': pln_no,
                'plan_id': master.id,
                'redirect_url': '/material-planning/plans/'  # Redirect to plan list page
            })

        except Exception as e:
            logger.error(f"Error in PlanningSaveView: {e}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

