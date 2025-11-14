"""
Plan Views
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




class MaterialPlanListView(MaterialPlanningBaseMixin, ListView):
    """
    Material Plan List - Based on Planning_Edit.aspx
    Lists all material planning records with search functionality
    """
    model = TblmpMaterialMaster
    template_name = 'material_planning/transactions/plan_list.html'
    context_object_name = 'plans'
    paginate_by = 15

    def get_queryset(self):
        from material_management.models import Supplier

        compid = self.get_compid()

        # Get search parameters
        search_field = self.request.GET.get('search_field', '')
        search_value = self.request.GET.get('search_value', '').strip()

        # Base queryset - show ALL plans regardless of financial year
        queryset = TblmpMaterialMaster.objects.filter(
            compid=compid
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
                    ).values_list('supplier_id', flat=True)
                    queryset = queryset.filter(supplierid__in=suppliers)

            elif search_field == 'plno':  # PL No
                queryset = queryset.filter(plno__icontains=search_value)

        return queryset

    def get_context_data(self, **kwargs):
        from material_management.models import Supplier, PRDetails, PRMaster
        from sys_admin.models import TblfinancialMaster
        from datetime import datetime

        context = super().get_context_data(**kwargs)
        context['search_field'] = self.request.GET.get('search_field', '')
        context['search_value'] = self.request.GET.get('search_value', '')

        compid = self.get_compid()

        # Get current financial year name for display
        try:
            current_fy = TblfinancialMaster.objects.get(finyearid=self.get_finyearid())
            current_fy_name = current_fy.finyear
        except TblfinancialMaster.DoesNotExist:
            current_fy_name = str(self.get_finyearid())

        # Enrich plans with supplier names and financial year
        for plan in context['plans']:
            # Supplier info is in detail tables (RM, Process, Finish), not master
            # Collect all unique suppliers from all detail records
            supplier_ids = set()

            # Get all details for this plan
            details = TblmpMaterialDetail.objects.filter(master=plan)

            # Collect suppliers from Raw Material, Process, and Finish tables
            for detail in details:
                # Raw materials
                rm_suppliers = TblmpMaterialRawmaterial.objects.filter(detail=detail).values_list('supplierid', flat=True)
                supplier_ids.update([sid for sid in rm_suppliers if sid])

                # Process
                pro_suppliers = TblmpMaterialProcess.objects.filter(detail=detail).values_list('supplierid', flat=True)
                supplier_ids.update([sid for sid in pro_suppliers if sid])

                # Finish
                fin_suppliers = TblmpMaterialFinish.objects.filter(detail=detail).values_list('supplierid', flat=True)
                supplier_ids.update([sid for sid in fin_suppliers if sid])

            # Look up supplier names from Supplier table
            if supplier_ids:
                # Create a mapping of supplier_id to supplier_name
                supplier_map = {}
                suppliers = Supplier.objects.filter(
                    supplier_id__in=supplier_ids,
                    comp_id=compid
                ).values_list('supplier_id', 'supplier_name')

                for sid, name in suppliers:
                    supplier_map[sid] = name

                # Format as "Name [ID]" for found suppliers, or just "ID" for not found
                supplier_list = []
                for sid in supplier_ids:
                    if sid in supplier_map:
                        # Found in Supplier table
                        supplier_list.append(f"{supplier_map[sid]} [{sid}]")
                    else:
                        # Not found - display the ID/text directly (handles free text entries)
                        supplier_list.append(str(sid))

                plan.supplier_name = ", ".join(supplier_list) if supplier_list else ""
            else:
                plan.supplier_name = ""

            # Display current financial year (normalized)
            plan.finyear_name = current_fy_name

            # Completion date is in detail tables, not master
            plan.compdate_display = ""

            # Check if already in PR (disable edit if yes)
            # Check if any items from this plan are in PR
            # Simplified: Just check if there are any PR details with items from this plan's raw materials
            plan.in_pr = False
            try:
                # Get raw materials through the detail relationship: Master -> Detail -> RawMaterial
                raw_items = TblmpMaterialRawmaterial.objects.filter(detail__master=plan).values_list('item', flat=True)
                if raw_items:
                    # Check if any of these items appear in PRDetails
                    # PRDetails has item_id field directly, no need for pr__ lookup
                    plan.in_pr = PRDetails.objects.filter(item_id__in=raw_items).exists()
            except Exception:
                # If there's any error, default to not in PR
                plan.in_pr = False

        return context
    
    # POST method removed - supplier/compdate are in detail tables, not master

class MaterialPlanCreateView(MaterialPlanningBaseMixin, CreateView):
    """Create Material Plan"""
    model = TblmpMaterialMaster
    fields = ['plno', 'wono']
    template_name = 'material_planning/transactions/plan_form.html'
    success_url = reverse_lazy('material_planning:plan-list')

    def form_valid(self, form):
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.sessionid = self.get_sessionid()
        form.instance.sysdate = datetime.now().strftime('%Y-%m-%d')
        form.instance.systime = datetime.now().strftime('%H:%M:%S')
        response = super().form_valid(form)
        messages.success(self.request, f'Material Plan {self.object.plno} created!')
        return response

class MaterialPlanDetailView(MaterialPlanningBaseMixin, TemplateView):
    """
    View Material Plan Details - Based on Planning_Edit_Details.aspx
    Shows Raw Material and Processing Material items for editing
    """
    template_name = 'material_planning/transactions/plan_detail.html'

    def get_context_data(self, **kwargs):
        from design.models import TbldgItemMaster
        from sys_admin.models import UnitMaster
        from material_management.models import Supplier, PRDetails, PRMaster
        from datetime import datetime

        context = super().get_context_data(**kwargs)
        plan_id = kwargs.get('plan_id')

        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"===== MaterialPlanDetailView GET: plan_id={plan_id}, kwargs={kwargs}")

        context['mid'] = plan_id

        # Get plan number and WO number from master record
        try:
            master = TblmpMaterialMaster.objects.get(id=plan_id)
            context['plno'] = master.plno
            context['wono'] = master.wono
            plno = master.plno
        except TblmpMaterialMaster.DoesNotExist:
            context['plno'] = '-'
            context['wono'] = '-'
            plno = '-'

        # Get Raw Material items
        raw_materials = TblmpMaterialRawmaterial.objects.filter(
            detail__master__id=plan_id
        ).order_by('-id')

        logger.error(f"DEBUG RAW: query={raw_materials.query}, count={raw_materials.count()}")

        # Enrich raw material data
        raw_materials_enriched = []
        for rm in raw_materials:
            try:
                item = TbldgItemMaster.objects.get(id=rm.item)
                unit = UnitMaster.objects.get(id=item.uombasic) if item.uombasic else None

                # Get supplier name
                supplier_name = ""
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

                # Format date
                compdate_display = ""
                if rm.deldate:
                    try:
                        if '-' in rm.deldate and rm.deldate.count('-') == 2:
                            parts = rm.deldate.split('-')
                            if len(parts[0]) == 4:  # YYYY-MM-DD
                                date_obj = datetime.strptime(rm.deldate, '%Y-%m-%d')
                                compdate_display = date_obj.strftime('%d-%m-%Y')
                            else:  # Already DD-MM-YYYY
                                compdate_display = rm.deldate
                        else:
                            compdate_display = rm.deldate
                    except:
                        compdate_display = rm.deldate

                raw_materials_enriched.append({
                    'id': rm.id,
                    'plno': plno,  # From master record, not rm
                    'item_id': rm.item,
                    'item_code': item.itemcode if item else '',
                    'description': item.manfdesc if item else '',
                    'uom': unit.symbol if unit else '',
                    'supplier_name': supplier_name,
                    'compdate': rm.deldate or '',  # DelDate is the completion date field
                    'compdate_display': compdate_display,
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
                supplier_name = ""
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

                # Format date
                compdate_display = ""
                if proc.deldate:
                    try:
                        if '-' in proc.deldate and proc.deldate.count('-') == 2:
                            parts = proc.deldate.split('-')
                            if len(parts[0]) == 4:  # YYYY-MM-DD
                                date_obj = datetime.strptime(proc.deldate, '%Y-%m-%d')
                                compdate_display = date_obj.strftime('%d-%m-%Y')
                            else:  # Already DD-MM-YYYY
                                compdate_display = proc.deldate
                        else:
                            compdate_display = proc.deldate
                    except:
                        compdate_display = proc.deldate

                process_items_enriched.append({
                    'id': proc.id,
                    'plno': plno,  # From master record
                    'item_id': proc.item,
                    'item_code': item.itemcode if item else '',
                    'description': item.manfdesc if item else '',
                    'uom': unit.symbol if unit else '',
                    'supplier_name': supplier_name,
                    'compdate': proc.deldate or '',  # DelDate is the completion date field
                    'compdate_display': compdate_display,
                    'in_pr': in_pr,
                    'can_edit': not in_pr
                })
            except Exception as e:
                continue

        context['process_items'] = process_items_enriched

        # Get Finish items
        finish_items = TblmpMaterialFinish.objects.filter(
            detail__master__id=plan_id
        ).order_by('-id')

        # Enrich finish data
        finish_items_enriched = []
        for fin in finish_items:
            try:
                item = TbldgItemMaster.objects.get(id=fin.item)
                unit = UnitMaster.objects.get(id=item.uombasic) if item.uombasic else None

                # Get supplier name
                supplier_name = ""
                if fin.supplierid:
                    try:
                        supplier = Supplier.objects.get(
                            supplier_id=fin.supplierid,
                            comp_id=self.get_compid()
                        )
                        supplier_name = f"{supplier.supplier_name} [{supplier.supplier_id}]"
                    except:
                        supplier_name = fin.supplierid

                # Check if in PR
                in_pr = PRDetails.objects.filter(
                    m_id__in=PRMaster.objects.filter(comp_id=self.get_compid()).values_list('pr_id', flat=True),
                    item_id=fin.item
                ).exists()

                # Format date
                compdate_display = ""
                if fin.deldate:
                    try:
                        if '-' in fin.deldate and fin.deldate.count('-') == 2:
                            parts = fin.deldate.split('-')
                            if len(parts[0]) == 4:  # YYYY-MM-DD
                                date_obj = datetime.strptime(fin.deldate, '%Y-%m-%d')
                                compdate_display = date_obj.strftime('%d-%m-%Y')
                            else:  # Already DD-MM-YYYY
                                compdate_display = fin.deldate
                        else:
                            compdate_display = fin.deldate
                    except:
                        compdate_display = fin.deldate

                finish_items_enriched.append({
                    'id': fin.id,
                    'plno': plno,  # From master record
                    'item_id': fin.item,
                    'item_code': item.itemcode if item else '',
                    'description': item.manfdesc if item else '',
                    'uom': unit.symbol if unit else '',
                    'supplier_name': supplier_name,
                    'compdate': fin.deldate or '',  # DelDate is the completion date field
                    'compdate_display': compdate_display,
                    'in_pr': in_pr,
                    'can_edit': not in_pr
                })
            except Exception as e:
                continue

        context['finish_items'] = finish_items_enriched

        return context

    def post(self, request, plan_id):
        """Handle bulk update of selected items - Based on ASP.NET GridView1_RowCommand and GridView2_RowCommand"""
        from datetime import datetime

        update_type = request.POST.get('update_type')  # 'raw', 'process', or 'finish'
        updated_count = 0

        try:
            if update_type == 'raw':
                # Get all checked items
                for key in request.POST:
                    if key.startswith('check_raw_'):
                        item_id = key.replace('check_raw_', '')
                        supplier_text = request.POST.get(f'supplier_raw_{item_id}', '').strip()
                        compdate = request.POST.get(f'compdate_raw_{item_id}', '').strip()

                        if supplier_text and compdate:
                            rm = TblmpMaterialRawmaterial.objects.get(id=item_id)

                            # Extract supplier ID from "Name [ID]" format
                            if '[' in supplier_text and ']' in supplier_text:
                                supplier_id = supplier_text.split('[')[1].split(']')[0]
                                rm.supplierid = supplier_id
                            else:
                                rm.supplierid = supplier_text

                            # Convert date from DD-MM-YYYY to YYYY-MM-DD for storage
                            try:
                                date_obj = datetime.strptime(compdate, '%d-%m-%Y')
                                rm.compdate = date_obj.strftime('%Y-%m-%d')
                            except:
                                rm.compdate = compdate

                            rm.save()
                            updated_count += 1

            elif update_type == 'process':
                # Get all checked items
                for key in request.POST:
                    if key.startswith('check_process_'):
                        item_id = key.replace('check_process_', '')
                        supplier_text = request.POST.get(f'supplier_process_{item_id}', '').strip()
                        compdate = request.POST.get(f'compdate_process_{item_id}', '').strip()

                        if supplier_text and compdate:
                            proc = TblmpMaterialProcess.objects.get(id=item_id)

                            # Extract supplier ID from "Name [ID]" format
                            if '[' in supplier_text and ']' in supplier_text:
                                supplier_id = supplier_text.split('[')[1].split(']')[0]
                                proc.supplierid = supplier_id
                            else:
                                proc.supplierid = supplier_text

                            # Convert date from DD-MM-YYYY to YYYY-MM-DD for storage
                            try:
                                date_obj = datetime.strptime(compdate, '%d-%m-%Y')
                                proc.compdate = date_obj.strftime('%Y-%m-%d')
                            except:
                                proc.compdate = compdate

                            proc.save()
                            updated_count += 1

            if updated_count > 0:
                messages.success(request, f'Successfully updated {updated_count} items!')
            else:
                messages.warning(request, 'Please select at least one item and provide supplier and date.')

            return redirect('material_planning:plan-list')

        except Exception as e:
            messages.error(request, f'Error updating items: {str(e)}')
            return redirect('material_planning:plan-detail', plno=plno, plan_id=plan_id)

class MaterialPlanUpdateView(MaterialPlanningBaseMixin, UpdateView):
    """Update Material Plan"""
    model = TblmpMaterialMaster
    fields = ['plno', 'wono']
    template_name = 'material_planning/transactions/plan_form.html'
    success_url = reverse_lazy('material_planning:plan-list')
    pk_url_kwarg = 'plan_id'

class MaterialPlanDeleteView(MaterialPlanningBaseMixin, View):
    """
    Delete Material Plan with safety checks.
    Prevents deletion if items are in Purchase Requisition.
    Performs cascade delete of all related records.
    """
    
    def post(self, request, plan_id):
        """Handle planning deletion with safety checks"""
        from django.db import transaction
        from .utils import check_planning_in_pr
        
        try:
            plan = get_object_or_404(
                TblmpMaterialMaster,
                id=plan_id,
                compid=self.get_compid()
            )
            
            # Safety check: Verify items are not in PR
            if check_planning_in_pr(plan):
                messages.error(
                    request,
                    f'Cannot delete Planning {plan.plno}: Items are already in Purchase Requisition'
                )
                return redirect('material_planning:plan-list')
            
            # Perform cascade delete with transaction
            with transaction.atomic():
                plno = plan.plno
                
                # Delete related records
                TblmpMaterialDetail.objects.filter(master=plan).delete()
                TblmpMaterialRawmaterial.objects.filter(mid=plan.id).delete()
                TblmpMaterialProcess.objects.filter(mid=plan.id).delete()
                
                # Try to delete finish materials if they exist
                try:
                    TblmpMaterialFinish.objects.filter(detail__master=plan).delete()
                except:
                    pass  # Finish materials may not exist
                
                # Delete master record
                plan.delete()
                
                messages.success(request, f'Planning record {plno} deleted successfully')
                logger.info(f"Planning {plno} deleted by {request.user.username}")
            
            return redirect('material_planning:plan-list')
            
        except TblmpMaterialMaster.DoesNotExist:
            messages.error(request, 'Planning record not found')
            return redirect('material_planning:plan-list')
        except Exception as e:
            logger.error(f"Error deleting planning: {e}", exc_info=True)
            messages.error(request, f'Error deleting planning: {str(e)}')
            return redirect('material_planning:plan-list')


# ============================================================================
# PROCESS MASTER (ITEM PROCESS) VIEWS
# ============================================================================

class PlanningPrintView(MaterialPlanningBaseMixin, DetailView):
    """Print planning details"""
    model = TblmpMaterialMaster
    template_name = 'material_planning/reports/planning_print.html'
    context_object_name = 'plan'
    pk_url_kwarg = 'plan_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan = self.object
        
        # Get all details
        details = TblmpMaterialDetail.objects.filter(master=plan)
        context['raw_materials'] = TblmpMaterialRawmaterial.objects.filter(
            detail__in=details
        )
        context['processes'] = TblmpMaterialProcess.objects.filter(
            detail__in=details
        )
        context['finishes'] = TblmpMaterialFinish.objects.filter(
            detail__in=details
        )
        
        return context