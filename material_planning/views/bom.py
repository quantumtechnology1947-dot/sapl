"""
Bom Views
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




class PlanningSearchView(MaterialPlanningBaseMixin, TemplateView):
    """
    Search Work Orders for creating material planning
    Converted from: aaspnet/Module/MaterialPlanning/Transactions/Planning_New.aspx
    """
    template_name = 'material_planning/transactions/planning_search.html'

    def get(self, request, *args, **kwargs):
        """
        Override get() to clear temp tables on page load
        ASP.NET Reference: Planning_New.aspx.cs Page_Load lines 38-70
        """
        # Clear temp tables for current user (session-based cleanup)
        user_id = str(request.user.id)

        # Step 1: Get all temp detail records for this user
        detail_temps = TblmpMaterialDetailTemp.objects.filter(sessionid=user_id)

        # Step 2: Delete related records from all 3 temp quote tables
        for detail_temp in detail_temps:
            TblmpMaterialRawmaterialTemp.objects.filter(dmid=detail_temp.id).delete()
            TblmpMaterialProcessTemp.objects.filter(dmid=detail_temp.id).delete()
            TblmpMaterialFinishTemp.objects.filter(dmid=detail_temp.id).delete()

        # Step 3: Delete all detail temp records for this user
        detail_temps.delete()

        # Continue with normal template rendering
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get search parameters
        search_type = self.request.GET.get('search_type', 'customer')
        search_value = self.request.GET.get('search_value', '')
        wo_category = self.request.GET.get('wo_category', '')

        context['search_type'] = search_type
        context['search_value'] = search_value
        context['wo_category'] = wo_category

        # Get WO Categories for filter
        from sales_distribution.models import TblsdWoCategory
        context['wo_categories'] = TblsdWoCategory.objects.filter(
            compid=self.get_compid()
        ).order_by('cname')

        # Always show work orders (even without search criteria)
        # This matches ASP.NET behavior where BindDataCust() is called on page load
        work_orders = self.search_work_orders(search_type, search_value, wo_category)
        context['work_orders'] = work_orders

        return context

    def search_work_orders(self, search_type, search_value, wo_category):
        """
        Search for Work Orders based on criteria
        Replicates: Sp_WONO_NotInBom stored procedure logic from Planning_New.aspx.cs
        """
        from sales_distribution.models import SdCustMaster
        from design.models import TbldgBomMaster
        from django.db.models import Q

        # Base query: Work Orders for current company
        # Show all financial years (ASP.NET shows historical records too)
        work_orders = SdCustWorkorderMaster.objects.filter(
            compid=self.get_compid()
        )

        # Filter by search type
        if search_value:
            if search_type == 'customer':
                # Extract customer code from "[CODE]" format
                if '[' in search_value and ']' in search_value:
                    customer_id = search_value.split('[')[1].split(']')[0]
                    work_orders = work_orders.filter(customerid=customer_id)
                else:
                    # Search by name
                    customers = SdCustMaster.objects.filter(
                        customername__icontains=search_value
                    ).values_list('customerid', flat=True)
                    work_orders = work_orders.filter(customerid__in=customers)

            elif search_type == 'enquiry':
                work_orders = work_orders.filter(enqid=search_value)

            elif search_type == 'po':
                work_orders = work_orders.filter(pono__icontains=search_value)

            elif search_type == 'wo':
                work_orders = work_orders.filter(wono__icontains=search_value)

        # Filter by WO Category
        if wo_category:
            work_orders = work_orders.filter(cid=wo_category)

        # Only show WOs that have BOM (L filter in ASP.NET)
        bom_wonos = list(TbldgBomMaster.objects.values_list('wono', flat=True).distinct())
        work_orders = work_orders.filter(wono__in=bom_wonos)

        # Exclude WOs that already have planning
        planned_wonos = list(TblmpMaterialMaster.objects.values_list('wono', flat=True).distinct())
        work_orders = work_orders.exclude(wono__in=planned_wonos)

        # Get financial year names
        fy_dict = {fy.finyearid: fy.finyear
                   for fy in TblfinancialMaster.objects.all()}

        # Get customer names
        customer_dict = {cust.customerid: cust.customername
                        for cust in SdCustMaster.objects.all()}

        # Get employee names from OfficeStaff
        from human_resource.models import TblhrOfficestaff
        employee_dict = {emp.empid: emp.employeename
                        for emp in TblhrOfficestaff.objects.filter(compid=self.get_compid())}

        # Enrich with financial year, customer name, and employee name
        # Order by financial year (most recent first), then by ID (most recent first)
        work_orders_list = list(work_orders.order_by('-finyearid', '-id')[:50])
        for wo in work_orders_list:
            wo.finyear_name = fy_dict.get(wo.finyearid, '-')
            wo.customername = customer_dict.get(wo.customerid, '-')
            # Map sessionid to employee name (e.g., 'Sapl0005' -> 'Employee Name')
            wo.employee_name = employee_dict.get(wo.sessionid, wo.sessionid)

        return work_orders_list

class PlanningCreateView(MaterialPlanningBaseMixin, TemplateView):
    """
    Create material planning from Work Order (PDT page).
    Loads BOM data, categorizes materials, and allows editing before save.
    Converted from: aaspnet/Module/MaterialPlanning/Transactions/pdt.aspx
    """
    template_name = 'material_planning/transactions/planning_create_new.html'

    def get(self, request, *args, **kwargs):
        """
        Override get() to clear temp tables on page load
        ASP.NET Reference: pdt.aspx.cs Page_Load lines 95-122

        IMPORTANT: Temp data deletion is commented out to allow data to persist
        across "Add to Temp" operations. Temp data should only be cleared:
        1. After successful plan generation (PlanningSaveView)
        2. On explicit user action (Cancel/Clear button)
        3. NOT on every page load (breaks Add to Temp workflow)
        """
        # COMMENTED OUT: This was deleting temp data on every page load,
        # causing "No temporary data found" error after "Add to Temp"

        # user_id = str(request.user.id)
        # detail_temps = TblmpMaterialDetailTemp.objects.filter(sessionid=user_id)
        # for detail_temp in detail_temps:
        #     TblmpMaterialRawmaterialTemp.objects.filter(dmid=detail_temp.id).delete()
        #     TblmpMaterialProcessTemp.objects.filter(dmid=detail_temp.id).delete()
        #     TblmpMaterialFinishTemp.objects.filter(dmid=detail_temp.id).delete()
        # detail_temps.delete()

        # Continue with normal template rendering
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wono = kwargs.get('wono')
        context['wono'] = wono

        # Get distinct BOM items for this WO
        bom_items = BOMService.get_bom_items(wono, self.get_compid(), self.get_finyearid())

        if not bom_items:
            context['has_bom'] = False
            messages.error(self.request, f'No BOM data found for Work Order {wono}')
        else:
            context['has_bom'] = True
            context['bom_items'] = bom_items

        return context


class BomLoadView(MaterialPlanningBaseMixin, View):
    """Load BOM data for a Work Order"""
    def get(self, request, wono):
        from django.http import JsonResponse
        from design.models import TbldgBomMaster, TbldgBomDetails
        
        try:
            bom = TbldgBomMaster.objects.get(wono=wono)
            details = TbldgBomDetails.objects.filter(mid=bom.id)
            
            data = {
                'bom_id': bom.id,
                'items': [
                    {
                        'id': d.id,
                        'item_code': d.itemid.itemcode if d.itemid else '',
                        'description': d.itemid.itemname if d.itemid else '',
                        'qty': float(d.qty) if d.qty else 0,
                        'unit': d.itemid.unit.symbol if d.itemid and d.itemid.unit else '',
                    }
                    for d in details
                ]
            }
            
            return JsonResponse(data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=404)


# ============================================================================
# REPORTS
# ============================================================================

class SupplierAutocompleteView(MaterialPlanningBaseMixin, View):
    """
    Autocomplete search for suppliers via HTMX.
    Returns JSON with supplier data formatted as "Name [ID]".
    """
    def get(self, request):
        from django.http import JsonResponse
        from material_management.models import Supplier
        
        query = request.GET.get('q', '').strip()
        
        # Require at least 1 character
        if len(query) < 1:
            return JsonResponse({'results': []})
        
        # Filter suppliers by name or ID, limit to company
        suppliers = Supplier.objects.filter(
            Q(supplier_name__icontains=query) | Q(supplier_id__icontains=query),
            comp_id=self.get_compid()
        ).values('supplier_id', 'supplier_name')[:10]
        
        # Format as "SupplierName [SupplierID]"
        results = [
            {
                'id': s['supplier_id'],
                'text': f"{s['supplier_name']} [{s['supplier_id']}]"
            }
            for s in suppliers
        ]
        
        return JsonResponse({'results': results})


# Keep old name for backward compatibility
SupplierSearchView = SupplierAutocompleteView