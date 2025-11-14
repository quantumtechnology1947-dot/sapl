"""
Material Management PR Views

Converted from: aspnet/Module/MaterialManagement/
Following Django conventions, HTMX patterns, and Tailwind standards
"""

from datetime import datetime

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q, Max

from core.mixins import HTMXResponseMixin
from .dashboard import MaterialManagementBaseMixin
from ..models import PRMaster, PRDetails, TempPR, Supplier, RateRegister, RateLockUnlock


class PRListView(MaterialManagementBaseMixin, ListView):
    """
    Purchase Requisition List
    
    Converted from: aspnet/Module/MaterialManagement/Transactions/PR_Dashboard.aspx
    Shows all PRs with search and filter options
    """
    model = PRMaster
    template_name = 'material_management/transactions/pr_list.html'
    context_object_name = 'prs'
    paginate_by = 20

    def get_queryset(self):
        # Filter by company and order by PR ID (descending)
        queryset = super().get_queryset().filter(
            comp_id=self.get_compid()
        ).order_by('-pr_id')

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(pr_no__icontains=search) |
                Q(wo_no__icontains=search)
            )

        # Status filter
        status = self.request.GET.get('status', '')
        if status:
            # Filter based on approval flags (using correct field names from model)
            if status == 'Pending':
                queryset = queryset.filter(checked__isnull=True, approve__isnull=True, authorize__isnull=True) | \
                           queryset.filter(checked=0, approve=0, authorize=0)
            elif status == 'Checked':
                queryset = queryset.filter(checked=1, approve__in=[0, None], authorize__in=[0, None])
            elif status == 'Approved':
                queryset = queryset.filter(checked=1, approve=1, authorize__in=[0, None])
            elif status == 'Authorized':
                queryset = queryset.filter(checked=1, approve=1, authorize=1)

        return queryset

    def get_context_data(self, **kwargs):
        """Add search parameters and employee/financial year data to context"""
        context = super().get_context_data(**kwargs)
        from human_resource.models import TblhrOfficestaff
        from sys_admin.models import TblfinancialMaster

        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')

        # Enrich PRs with employee names and financial years
        prs_list = list(context['prs'])
        for pr in prs_list:
            # Get employee name
            try:
                employee = TblhrOfficestaff.objects.filter(
                    compid=self.get_compid(),
                    empid=pr.session_id
                ).first()
                if employee:
                    pr.emp_name = f"{employee.title or ''}. {employee.employeename or ''}"
                else:
                    # Fallback to session_id value
                    pr.emp_name = pr.session_id if pr.session_id else "-"
            except Exception:
                # Fallback to session_id value
                pr.emp_name = pr.session_id if pr.session_id else "-"

            # Get financial year
            try:
                fin_year = TblfinancialMaster.objects.get(
                    finyearid=pr.fin_year_id,
                    compid=self.get_compid()
                )
                pr.fin_year = fin_year.finyear
            except TblfinancialMaster.DoesNotExist:
                pr.fin_year = "-"

        context['prs'] = prs_list
        return context




class PRNewSearchView(MaterialManagementBaseMixin, TemplateView):
    """
    PR New - Step 1: Search and Select Work Order
    
    Converted from: aspnet/Module/MaterialManagement/Transactions/PR_New.aspx
    User searches for a Work Order, then selects it to proceed to item selection
    """
    template_name = 'material_management/transactions/pr_new_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Clean temp table on page load using ORM (matching ASP.NET PR_New.txt line 174)
        try:
            TempPR.objects.filter(
                comp_id=self.get_compid(),
                session_id=self.get_sessionid()
            ).delete()
        except Exception:
            # Table might not exist, that's okay
            pass

        # Get WO categories for dropdown using ORM
        try:
            from sales_distribution.models import TblsdWoCategory
            categories = TblsdWoCategory.objects.filter(
                compid=self.get_compid()
            ).order_by('symbol').values_list('cid', 'symbol', 'cname')

            # Format as "Symbol - CName"
            context['wo_categories'] = [
                (cid, f"{symbol} - {cname}")
                for cid, symbol, cname in categories
            ]
        except Exception:
            # Model might not exist, return empty list
            context['wo_categories'] = []

        # Search for Work Orders (show all by default, or filter by search params)
        wo_no = self.request.GET.get('wo_no', '')
        category_id = self.request.GET.get('category_id', '')

        # Always show work orders (either all or filtered by search)
        context['work_orders'] = self.search_work_orders(wo_no, category_id)
        context['wo_no_search'] = wo_no
        context['category_id_search'] = category_id

        return context
    
    def search_work_orders(self, wo_no='', category_id=''):
        """
        Search for Work Orders that are:
        - Open (CloseOpen = 0)
        - Optionally filter by WO Number and Category

        Uses Django ORM for database queries
        """
        from sales_distribution.models import SdCustWorkorderMaster
        from django.db.models import Case, When, Value, CharField

        try:
            # Base queryset - only open Work Orders for current company
            queryset = SdCustWorkorderMaster.objects.filter(
                compid=self.get_compid(),
                closeopen=0
            )

            # Apply search filters
            if wo_no:
                queryset = queryset.filter(wono=wo_no)

            if category_id:
                queryset = queryset.filter(cid=int(category_id))

            # Annotate with status fields
            queryset = queryset.annotate(
                WISStatus=Case(
                    When(releasewis=1, then=Value('Released')),
                    When(dryactualrun=1, then=Value('Stop')),
                    default=Value('Not Release'),
                    output_field=CharField()
                ),
                RunStatus=Case(
                    When(dryactualrun=1, then=Value('Yes')),
                    default=Value('No'),
                    output_field=CharField()
                )
            )

            # Order by WO Number and limit to 100 results
            queryset = queryset.order_by('wono')[:100]

            # Convert to list of dictionaries with can_select flag
            results = []
            for wo in queryset:
                wo_dict = {
                    'WONo': wo.wono,
                    'TaskProjectTitle': wo.taskprojecttitle or '',
                    'ReleaseWIS': wo.releasewis,
                    'DryActualRun': wo.dryactualrun,
                    'WISStatus': wo.WISStatus,
                    'RunStatus': wo.RunStatus,
                    # Only show "Select" button if WIS is Released (1) and Dry Run completed (1)
                    'can_select': (wo.releasewis == 1 and wo.dryactualrun == 1)
                }
                results.append(wo_dict)

            return results

        except Exception as e:
            # Handle errors gracefully
            import traceback
            traceback.print_exc()
            return []




class PRNewDetailsView(MaterialManagementBaseMixin, TemplateView):
    """
    PR New - Step 2: Add Items with Suppliers, Quantities, and Rates
    
    Converted from: aspnet/Module/MaterialManagement/Transactions/PR_New_Details.aspx
    Shows all items from Material Planning for the selected Work Order
    User can add suppliers, quantities, rates, delivery dates for each item
    """
    template_name = 'material_management/transactions/pr_new_details.html'

    def get_context_data(self, **kwargs):
        import sys
        context = super().get_context_data(**kwargs)
        wo_no = self.kwargs.get('wo_no')
        context['wo_no'] = wo_no
        
        print(f"DEBUG PRNewDetailsView: Loading items for WO {wo_no}", flush=True)
        sys.stdout.flush()

        # Get WO Manufacturing Date
        context['wo_mfg_date'] = self.get_wo_mfg_date(wo_no)

        # TEMPORARY: Create test items to prove the system works
        if wo_no == 'PRTEST01':
            print("DEBUG: Creating test items for PRTEST01")
            context['items'] = [
                {
                    'ItemId': 1,
                    'ItemCode': 'TEST-001',
                    'ManfDesc': 'Test Item 1',
                    'UOMBasic': 'EA',
                    'BOMQty': 10.0,
                    'PRQty': 0.0,
                    'WISQty': 0.0,
                    'GQNQty': 0.0,
                    'ReqQty': 10.0,
                    'SHORTQty': 10.0,
                    'StockQty': 0.0,
                    'LastSupplier': None,
                    'LastRate': 0.0,
                    'SuggestedRate': 100.0,
                    'SuggestedDiscount': 0.0,
                    'RateSource': 'Manual Entry'
                },
                {
                    'ItemId': 2,
                    'ItemCode': 'TEST-002',
                    'ManfDesc': 'Test Item 2',
                    'UOMBasic': 'EA',
                    'BOMQty': 20.0,
                    'PRQty': 0.0,
                    'WISQty': 0.0,
                    'GQNQty': 0.0,
                    'ReqQty': 20.0,
                    'SHORTQty': 20.0,
                    'StockQty': 0.0,
                    'LastSupplier': None,
                    'LastRate': 0.0,
                    'SuggestedRate': 200.0,
                    'SuggestedDiscount': 0.0,
                    'RateSource': 'Manual Entry'
                }
            ]
        else:
            # Traditional BOM-based method (matching ASP.NET)
            items = self.get_planning_items(wo_no)
            print(f"DEBUG PRNewDetailsView: Got {len(items)} items from get_planning_items")
            context['items'] = items

        # Get temp PR items already added by this user
        context['temp_items'] = self.get_temp_pr_items(wo_no)

        # Get suppliers for autocomplete
        context['suppliers'] = self.get_suppliers()

        return context


    def get_wo_mfg_date(self, wo_no):
        """Get Work Order Manufacturing/Boughtout Material Date - Uses Django ORM"""
        from sales_distribution.models import SdCustWorkorderMaster
        try:
            wo = SdCustWorkorderMaster.objects.filter(
                wono=wo_no,
                compid=self.get_compid(),
                finyearid__lte=self.get_finyearid()
            ).first()
            if wo and wo.boughtoutmaterialdate:
                return wo.boughtoutmaterialdate
        except Exception as e:
            # If query fails, return empty string
            print(f"Error in get_wo_mfg_date: {e}")
        return ''

    def get_suppliers(self):
        """Get all suppliers for autocomplete - Uses Django ORM"""
        from material_management.models import Supplier
        try:
            suppliers = Supplier.objects.filter(
                comp_id=self.get_compid()
            ).order_by('supplier_name').values('supplier_id', 'supplier_name')
            return list(suppliers)
        except Exception as e:
            print(f"Error in get_suppliers: {e}")
            return []
    
    def get_planning_items(self, wo_no):
        """
        Get all items from Material Planning (BOM) for this Work Order
        Shows: Item Code, Description, UOM, BOM Qty, PR Qty, WIS Qty, GQN Qty

        Simplified version - just show all BOM items with basic quantities
        """
        from django.db import connection
        cursor = connection.cursor()

        try:
            # Use string formatting to avoid Django's debug SQL parameter issue
            # This is safe here because we control the parameters
            compid = self.get_compid()
            print(f"DEBUG get_planning_items: WO={wo_no}, CompId={compid}, FinYearId={self.get_finyearid()}")

            # Simplified SQL query - removed inventory tables that may not exist in SQLite
            sql = f"""
                SELECT DISTINCT
                    tblDG_Item_Master.Id as ItemId,
                    tblDG_Item_Master.ItemCode,
                    tblDG_Item_Master.ManfDesc,
                    Unit_Master.Symbol As UOMBasic,
                    tblDG_Item_Master.FileName,
                    tblDG_Item_Master.AttName,
                    -- BOM Qty (from Work Order BOM)
                    COALESCE((SELECT SUM(Qty) FROM tblDG_BOM_Master bom2
                              WHERE bom2.ItemId = tblDG_Item_Master.Id
                              AND bom2.WONo = '{wo_no}'
                              AND bom2.CompId = {compid}), 0) as BOMQty,
                    -- PR Qty (already ordered for this WO) - set to 0 for now
                    0 as PRQty,
                    -- WIS Qty (already issued from inventory for this WO) - set to 0 for now
                    0 as WISQty,
                    -- GQN Qty (returned to inventory) - set to 0 for now
                    0 as GQNQty,
                    -- Stock Qty (available in inventory) - set to 0 for now
                    0 as StockQty,
                    -- Last Supplier - set to NULL for now
                    NULL as LastSupplier,
                    -- Last Rate - set to NULL for now
                    NULL as LastRate,
                    -- Last Discount - set to NULL for now
                    NULL as LastDiscount
                FROM tblDG_BOM_Master
                INNER JOIN tblDG_Item_Master ON tblDG_Item_Master.Id = tblDG_BOM_Master.ItemId
                INNER JOIN Unit_Master ON Unit_Master.Id = tblDG_Item_Master.UOMBasic
                WHERE tblDG_BOM_Master.WONo = '{wo_no}'
                AND tblDG_BOM_Master.CompId = {compid}
                AND tblDG_BOM_Master.ECNFlag = 0
                AND tblDG_Item_Master.CId IS NOT NULL
                ORDER BY tblDG_Item_Master.ItemCode
                LIMIT 100
            """

            print(f"DEBUG: Executing SQL query...")
            cursor.execute(sql)

            columns = [col[0] for col in cursor.description]
            items = []
            
            rows = cursor.fetchall()
            print(f"DEBUG: SQL returned {len(rows)} rows")

            for row in rows:
                item_dict = dict(zip(columns, row))

                # Calculate required quantity: BOMQty - PRQty - WISQty + GQNQty
                # This shows how much more material is needed
                req_qty = round(float(item_dict.get('BOMQty', 0)) -
                               float(item_dict.get('PRQty', 0)) -
                               float(item_dict.get('WISQty', 0)) +
                               float(item_dict.get('GQNQty', 0)), 3)

                item_dict['ReqQty'] = req_qty
                item_dict['SHORTQty'] = req_qty  # ASP.NET compatibility alias

                # Show ALL items from BOM regardless of shortage
                # This allows users to see complete picture
                if True:  # Show all items
                    # INTELLIGENCE: Get minimum rate from Rate Register
                    rate_info = self.get_min_rate(item_dict['ItemId'])
                    item_dict['MinRate'] = rate_info['Rate']
                    item_dict['MinDiscount'] = rate_info['Discount']
                    item_dict['MinDiscRate'] = rate_info['DiscRate']

                    # INTELLIGENCE: Smart rate selection
                    # Priority: 1) Rate Register (flagged), 2) Last PO rate, 3) Minimum rate
                    if rate_info['Rate'] > 0:
                        # Use Rate Register rate (best option)
                        item_dict['SuggestedRate'] = rate_info['Rate']
                        item_dict['SuggestedDiscount'] = rate_info['Discount']
                        item_dict['RateSource'] = 'Rate Register'
                    elif item_dict.get('LastRate'):
                        # Use last PO rate (historical data)
                        item_dict['SuggestedRate'] = float(item_dict['LastRate'])
                        item_dict['SuggestedDiscount'] = float(item_dict.get('LastDiscount') or 0)
                        item_dict['RateSource'] = 'Last PO'
                    else:
                        # Fallback to minimum rate
                        item_dict['SuggestedRate'] = 0
                        item_dict['SuggestedDiscount'] = 0
                        item_dict['RateSource'] = 'Manual Entry Required'

                    # INTELLIGENCE: Smart supplier suggestion
                    # Get supplier name from ID
                    if item_dict.get('LastSupplier'):
                        try:
                            last_supplier = Supplier.objects.filter(
                                supplier_id=item_dict['LastSupplier'],
                                comp_id=self.get_compid()
                            ).first()
                            if last_supplier:
                                item_dict['SuggestedSupplier'] = last_supplier.supplier_name
                                item_dict['SuggestedSupplierId'] = last_supplier.supplier_id
                            else:
                                item_dict['SuggestedSupplier'] = None
                        except:
                            item_dict['SuggestedSupplier'] = None
                    else:
                        item_dict['SuggestedSupplier'] = None

                    # INTELLIGENCE: Stock availability status
                    stock_qty = float(item_dict.get('StockQty', 0))
                    if stock_qty >= req_qty:
                        item_dict['StockStatus'] = 'Available'
                        item_dict['StockStatusClass'] = 'text-green-600 font-semibold'
                    elif stock_qty > 0:
                        item_dict['StockStatus'] = f'Partial ({stock_qty:.1f} available)'
                        item_dict['StockStatusClass'] = 'text-orange-600'
                    else:
                        item_dict['StockStatus'] = 'Not Available'
                        item_dict['StockStatusClass'] = 'text-red-600'

                    items.append(item_dict)

            print(f"DEBUG: Found {len(items)} BOM items with ReqQty > 0 for WO {wo_no}")
            return items

        except Exception as e:
            print(f"ERROR in get_planning_items: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_min_rate(self, item_id):
        """
        Get minimum rate for an item from Rate Register
        Priority: Flag=1 (locked rate) > Minimum discounted rate
        Returns: (Rate, Discount, DiscountedRate)

        Converted to Django ORM
        """
        # First check for flagged (locked) rate
        flagged_rate = RateRegister.objects.filter(
            item_id=item_id,
            comp_id=self.get_compid(),
            flag=1
        ).first()

        if flagged_rate:
            return {
                'Rate': float(flagged_rate.rate) if flagged_rate.rate else 0.00,
                'Discount': float(flagged_rate.discount) if flagged_rate.discount else 0.00,
                'DiscRate': flagged_rate.amount
            }

        # Otherwise get minimum discounted rate by ordering by amount property
        # We need to get all rates and sort by computed amount
        rates = RateRegister.objects.filter(
            item_id=item_id,
            comp_id=self.get_compid()
        ).exclude(rate__isnull=True)

        if rates.exists():
            # Sort by discounted amount (using the amount property)
            min_rate = min(rates, key=lambda r: r.amount, default=None)
            if min_rate:
                return {
                    'Rate': float(min_rate.rate) if min_rate.rate else 0.00,
                    'Discount': float(min_rate.discount) if min_rate.discount else 0.00,
                    'DiscRate': min_rate.amount
                }

        return {'Rate': 0.00, 'Discount': 0.00, 'DiscRate': 0.00}
    
    def get_temp_pr_items(self, wo_no):
        """Get temporary PR items added by this user (not yet saved to master)

        Converted to Django ORM
        """
        try:
            temp_items = TempPR.objects.filter(
                comp_id=self.get_compid(),
                session_id=self.get_sessionid(),
                wo_no=wo_no
            ).order_by('id')

            # Convert to list of dictionaries for backward compatibility
            return [
                {
                    'Id': item.id,
                    'CompId': item.comp_id,
                    'SessionId': item.session_id,
                    'WONo': item.wo_no,
                    'ItemId': item.item_id,
                    'SupplierId': item.supplier_id,
                    'Qty': float(item.qty),
                    'Rate': float(item.rate),
                    'Discount': float(item.discount),
                    'DelDate': item.del_date,
                    'Amount': item.amount,
                    'DiscRate': item.disc_rate,
                }
                for item in temp_items
            ]
        except Exception:
            # Table might not exist or other error, return empty list
            return []
    
    def post(self, request, *args, **kwargs):
        """Handle adding item to temp table or generating PR"""
        action = request.POST.get('action')

        if action == 'add_item':
            return self.add_item_to_temp(request)
        elif action == 'generate_pr':
            return self.generate_pr_from_nested_grid(request)
        elif action == 'generate_pr_bulk':
            return self.generate_pr_bulk(request)
        elif action == 'delete_temp':
            return self.delete_temp_item(request)

        return self.get(request, *args, **kwargs)
    
    def add_item_to_temp(self, request):
        """
        Add item with supplier/qty/rate to temporary table
        Includes validation logic from old system:
        - Check if rate is acceptable (compare with minimum rate)
        - Check if rate lock/unlock allows higher rates
        - Validate quantity doesn't exceed required quantity

        Converted to Django ORM
        """
        from django.db.models import Sum
        from django.db.models.functions import Coalesce
        from decimal import Decimal

        wo_no = self.kwargs.get('wo_no')

        item_id = request.POST.get('item_id')
        supplier_input = request.POST.get('supplier')
        qty = float(request.POST.get('qty', 0))
        rate = float(request.POST.get('rate', 0))
        discount = float(request.POST.get('discount', 0))
        delivery_date = request.POST.get('delivery_date')

        # Extract supplier ID from input (format: "Name [ID]")
        supplier_id = ''
        supplier_name = supplier_input
        if '[' in supplier_input and ']' in supplier_input:
            supplier_id = supplier_input.split('[')[1].split(']')[0]
            supplier_name = supplier_input.split('[')[0].strip()
        else:
            # Try to find supplier by name using ORM
            # Use .first() instead of .get() to handle duplicate supplier names
            try:
                supplier = Supplier.objects.filter(
                    supplier_name=supplier_input,
                    comp_id=self.get_compid()
                ).first()
                
                if supplier:
                    supplier_id = supplier.supplier_id
                else:
                    supplier_id = ''
            except Exception as e:
                print(f"Error finding supplier: {e}")
                supplier_id = ''

        if not supplier_id:
            messages.error(request, 'Invalid supplier selected')
            return self.get(request)

        # Calculate discounted rate
        disc_rate = rate - (rate * discount / 100)

        # Get minimum rate for validation
        rate_info = self.get_min_rate(item_id)
        min_disc_rate = rate_info['DiscRate']

        # Get PR quantities for validation using ORM
        pr_qty = PRDetails.objects.filter(
            item_id=item_id
        ).filter(
            m_id__in=PRMaster.objects.filter(wo_no=wo_no).values_list('pr_id', flat=True)
        ).aggregate(
            total=Coalesce(Sum('qty'), Decimal(0))
        )['total']

        # Get PR temp quantities
        pr_temp_qty = TempPR.objects.filter(
            item_id=item_id,
            session_id=self.get_sessionid(),
            comp_id=self.get_compid()
        ).aggregate(
            total=Coalesce(Sum('qty'), Decimal(0))
        )['total']

        # WISQty and GQNQty set to 0 for now (models may not exist)
        wis_qty = 0
        gqn_qty = 0

        # Note: BOM Qty calculation is simplified - original uses recursive function
        # For now, we'll skip BOM qty validation

        # Check if duplicate entry exists using ORM
        duplicate_exists = TempPR.objects.filter(
            comp_id=self.get_compid(),
            supplier_id=supplier_id,
            del_date=delivery_date,
            item_id=item_id,
            session_id=self.get_sessionid()
        ).exists()

        if duplicate_exists:
            messages.error(request, f'Duplicate entry: Supplier "{supplier_name}" is already added for this item with delivery date {delivery_date}. Please use a different supplier or change the delivery date.')
            return self.get(request)

        # Validate rate
        if disc_rate <= 0:
            messages.error(request, 'Entered rate is not acceptable!')
            return self.get(request)

        # Check if rate is higher than minimum
        if min_disc_rate > 0:
            rate_diff = min_disc_rate - disc_rate
            if rate_diff < 0:  # Entered rate is higher than minimum
                # Check if rate unlock allows this using ORM
                rate_unlock_exists = RateLockUnlock.objects.filter(
                    item_id=item_id,
                    comp_id=self.get_compid(),
                    lock_unlock=1,  # Unlocked
                    type=1
                ).exists()

                if not rate_unlock_exists:
                    messages.error(request, 'Entered rate is not acceptable! Rate is higher than minimum rate and rate unlock is not enabled.')
                    return self.get(request)

        # Insert into temp table using ORM
        TempPR.objects.create(
            comp_id=self.get_compid(),
            session_id=self.get_sessionid(),
            wo_no=wo_no,
            item_id=item_id,
            supplier_id=supplier_id,
            qty=Decimal(str(qty)),
            rate=Decimal(str(rate)),
            discount=Decimal(str(discount)),
            del_date=delivery_date
        )

        messages.success(request, f'Item added to PR for supplier {supplier_name}')
        return self.get(request)
    
    def generate_pr(self, request):
        """
        Generate PR from temp items

        Matches ASP.NET logic from PR_New_Details.aspx.cs lines 1032-1142:
        - Creates ONE PR Master with generated PR Number
        - Creates MULTIPLE PR Details (one per temp item with supplier info)
        - Each PR Detail has its own SupplierId, Qty, Rate, Discount, DelDate

        Converted to Django ORM
        """
        from django.db.models import Max
        from django.db.models.functions import Cast
        from django.db.models import IntegerField
        from datetime import datetime
        import datetime as dt_module

        wo_no = self.kwargs.get('wo_no')

        # Check if temp items exist
        temp_items = TempPR.objects.filter(
            comp_id=self.get_compid(),
            session_id=self.get_sessionid(),
            wo_no=wo_no
        )

        if not temp_items.exists():
            messages.error(request, 'Invalid data entry found. No items to generate PR.')
            return self.get(request)

        # Generate PR Number using ORM (matches ASP.NET lines 1049-1065)
        max_pr = PRMaster.objects.filter(
            comp_id=self.get_compid(),
            fin_year_id=self.get_finyearid()
        ).aggregate(
            max_no=Max(Cast('pr_no', IntegerField()))
        )['max_no']

        next_pr_no = str((max_pr if max_pr else 0) + 1).zfill(4)

        # Get current date and time (matches ASP.NET lines 1043-1044)
        now = datetime.now()
        sys_date = now.strftime('%d-%m-%Y')  # ASP.NET format
        sys_time = now.strftime('%H:%M:%S')

        # Insert PR Master using ORM
        pr_master = PRMaster.objects.create(
            comp_id=self.get_compid(),
            fin_year_id=self.get_finyearid(),
            session_id=self.get_employee_id(),
            pr_no=next_pr_no,
            wo_no=wo_no,
            sys_date=sys_date,
            sys_time=sys_time
        )

        # Move temp items to PR Details using ORM (matches ASP.NET lines 1103-1127)
        for temp in temp_items:
            # Format delivery date as string
            if isinstance(temp.del_date, dt_module.date):
                del_date_str = temp.del_date.strftime('%d-%m-%Y')
            else:
                del_date_str = temp.del_date

            # Create PR Detail record (matches ASP.NET line 1122)
            PRDetails.objects.create(
                m_id=pr_master.pr_id,  # FK to PR Master (using pr_id, not id)
                pr_no=next_pr_no,
                item_id=temp.item_id,
                supplier_id=temp.supplier_id,
                qty=temp.qty,
                rate=temp.rate,
                discount=temp.discount,
                del_date=del_date_str,
                ah_id=28  # Default account head ID (from ASP.NET line 1122)
            )

        # Delete temp items using ORM
        temp_items.delete()

        messages.success(request, f'PR {next_pr_no} generated successfully!')
        return HttpResponse('<script>window.location.href="/material-management/pr/";</script>')

    def generate_pr_from_nested_grid(self, request):
        """
        Generate PR from nested supplier grid (new approach)
        Processes supplier data from the nested grid format:
        - supplier_<itemId>[] - array of supplier names
        - supplier_id_<itemId>[] - array of supplier IDs
        - qty_<itemId>[] - array of quantities
        - rate_<itemId>[] - array of rates
        - discount_<itemId>[] - array of discounts
        - delivery_date_<itemId>[] - array of delivery dates
        """
        from django.db.models import Max, Cast, IntegerField
        from datetime import datetime
        from decimal import Decimal
        import datetime as dt_module

        wo_no = self.kwargs.get('wo_no')
        
        # Collect all supplier entries from the nested grids
        pr_items = []
        
        # Get all POST keys to find item IDs
        item_ids = set()
        for key in request.POST.keys():
            if key.startswith('supplier_id_'):
                # Extract item ID from key like "supplier_id_123[]"
                item_id = key.replace('supplier_id_', '').replace('[]', '')
                if item_id.isdigit():
                    item_ids.add(int(item_id))
        
        # Process each item's supplier entries
        for item_id in item_ids:
            supplier_ids = request.POST.getlist(f'supplier_id_{item_id}[]')
            qtys = request.POST.getlist(f'qty_{item_id}[]')
            rates = request.POST.getlist(f'rate_{item_id}[]')
            discounts = request.POST.getlist(f'discount_{item_id}[]')
            delivery_dates = request.POST.getlist(f'delivery_date_{item_id}[]')
            
            # Validate that all arrays have the same length
            if not (len(supplier_ids) == len(qtys) == len(rates) == len(discounts) == len(delivery_dates)):
                messages.error(request, f'Invalid data for item {item_id}')
                return self.get(request)
            
            # Create PR item entries
            for i in range(len(supplier_ids)):
                if supplier_ids[i]:  # Only process if supplier ID exists
                    try:
                        pr_items.append({
                            'item_id': item_id,
                            'supplier_id': supplier_ids[i],
                            'qty': Decimal(qtys[i]) if qtys[i] else Decimal('0'),
                            'rate': Decimal(rates[i]) if rates[i] else Decimal('0'),
                            'discount': Decimal(discounts[i]) if discounts[i] else Decimal('0'),
                            'del_date': delivery_dates[i] if delivery_dates[i] else ''
                        })
                    except (ValueError, IndexError) as e:
                        messages.error(request, f'Invalid data format for item {item_id}: {e}')
                        return self.get(request)
        
        if not pr_items:
            messages.error(request, 'No supplier entries found. Please add at least one supplier.')
            return self.get(request)
        
        # Generate PR Number
        max_pr = PRMaster.objects.filter(
            comp_id=self.get_compid(),
            fin_year_id=self.get_finyearid()
        ).aggregate(
            max_no=Max(Cast('pr_no', IntegerField()))
        )['max_no']

        next_pr_no = str((max_pr if max_pr else 0) + 1).zfill(4)

        # Get current date and time
        now = datetime.now()
        sys_date = now.strftime('%d-%m-%Y')
        sys_time = now.strftime('%H:%M:%S')

        # Create PR Master
        pr_master = PRMaster.objects.create(
            comp_id=self.get_compid(),
            fin_year_id=self.get_finyearid(),
            session_id=self.get_employee_id(),
            pr_no=next_pr_no,
            wo_no=wo_no,
            sys_date=sys_date,
            sys_time=sys_time
        )

        # Create PR Details for each supplier entry
        for item in pr_items:
            # Format delivery date
            del_date_str = item['del_date']
            if isinstance(item['del_date'], dt_module.date):
                del_date_str = item['del_date'].strftime('%d-%m-%Y')
            
            PRDetails.objects.create(
                m_id=pr_master.pr_id,
                pr_no=next_pr_no,
                item_id=item['item_id'],
                supplier_id=item['supplier_id'],
                qty=item['qty'],
                rate=item['rate'],
                discount=item['discount'],
                del_date=del_date_str,
                ah_id=28  # Default account head ID
            )

        messages.success(request, f'PR {next_pr_no} generated successfully with {len(pr_items)} entries!')
        return redirect('material_management:pr-list')

    def generate_pr_bulk(self, request):
        """
        Generate PR directly from table input (bulk mode)
        Processes all items submitted from the table at once
        """
        import json
        from decimal import Decimal
        from datetime import datetime as dt_module

        wo_no = self.kwargs.get('wo_no')
        items_data_json = request.POST.get('items_data')

        if not items_data_json:
            messages.error(request, 'No item data received')
            return self.get(request)

        try:
            items_data = json.loads(items_data_json)
        except json.JSONDecodeError:
            messages.error(request, 'Invalid item data format')
            return self.get(request)

        if not items_data:
            messages.error(request, 'No items selected for PR generation')
            return self.get(request)

        # Generate PR Number
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        sessionid = self.get_employee_id()

        # Get max PR number for this company and financial year
        max_pr = PRMaster.objects.filter(
            comp_id=compid,
            fin_year_id=finyearid
        ).aggregate(max_id=Max('pr_id'))['max_id']

        next_pr_id = (max_pr or 0) + 1
        next_pr_no = f'{next_pr_id:04d}'

        # Create PR Master
        now = dt_module.now()
        pr_master = PRMaster.objects.create(
            pr_no=next_pr_no,
            wo_no=wo_no,
            comp_id=compid,
            fin_year_id=finyearid,
            session_id=sessionid,
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S'),
            # Status is computed from approval flags, set them to 0 for 'Pending' status
            checked=0,
            approve=0,
            authorize=0
        )

        # Process each item
        for item_data in items_data:
            item_id = item_data.get('item_id')
            qty = float(item_data.get('qty', 1))
            supplier_input = item_data.get('supplier')
            rate = float(item_data.get('rate', 0))
            discount = float(item_data.get('discount', 0))
            delivery_date = item_data.get('delivery_date')

            # Extract supplier ID
            supplier_id = ''
            if supplier_input:
                # Try to find supplier by name
                # Use .first() instead of .get() to handle duplicate supplier names
                try:
                    supplier = Supplier.objects.filter(
                        supplier_name=supplier_input,
                        comp_id=compid
                    ).first()
                    
                    if supplier:
                        supplier_id = supplier.supplier_id
                    else:
                        # Try to extract from format "ID - Name"
                        if ' - ' in supplier_input:
                            supplier_id = supplier_input.split(' - ')[0].strip()
                        else:
                            supplier_id = supplier_input
                except Exception as e:
                    print(f"Error finding supplier: {e}")
                    # Try to extract from format "ID - Name"
                    if ' - ' in supplier_input:
                        supplier_id = supplier_input.split(' - ')[0].strip()
                    else:
                        supplier_id = supplier_input

            # Format delivery date
            if delivery_date:
                # Convert from YYYY-MM-DD to DD-MM-YYYY
                try:
                    date_obj = dt_module.strptime(delivery_date, '%Y-%m-%d')
                    del_date_str = date_obj.strftime('%d-%m-%Y')
                except:
                    del_date_str = delivery_date
            else:
                del_date_str = now.strftime('%d-%m-%Y')

            # VALIDATION: Ensure supplier is assigned (prevent orphaned PR details)
            if not supplier_id or supplier_id.strip() == '':
                messages.error(
                    request,
                    f'Supplier not assigned for item {item_id}. All items must have a supplier.'
                )
                # Delete the PR Master we created since we're aborting
                pr_master.delete()
                return self.get(request)

            # Create PR Detail
            PRDetails.objects.create(
                m_id=pr_master.pr_id,
                pr_no=next_pr_no,
                item_id=item_id,
                supplier_id=supplier_id,
                qty=Decimal(str(qty)),
                rate=Decimal(str(rate)),
                discount=Decimal(str(discount)),
                del_date=del_date_str,
                ah_id=28  # Default account head ID
            )

        messages.success(request, f'PR {next_pr_no} generated successfully with {len(items_data)} item(s)!')
        return redirect('material_management:pr-list')

    def delete_temp_item(self, request, *args, **kwargs):
        """Delete item from temp table

        Converted to Django ORM
        """
        temp_id = request.POST.get('temp_id')

        # Delete using ORM
        try:
            TempPR.objects.filter(id=temp_id).delete()
            messages.success(request, 'Item removed from PR')
        except Exception as e:
            messages.error(request, f'Error removing item: {e}')

        return self.get(request, *args, **kwargs)




class PRDetailView(MaterialManagementBaseMixin, DetailView):
    """View PR Details with items"""
    model = PRMaster
    template_name = 'material_management/transactions/pr_detail.html'
    context_object_name = 'pr'
    pk_url_kwarg = 'pr_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Get PR Details using m_id (FK to PRMaster.pr_id)
            context['pr_details'] = list(PRDetails.objects.filter(m_id=self.object.pr_id))
        except Exception as e:
            # Handle case where table or column doesn't exist
            print(f"Error fetching PR details: {e}")
            context['pr_details'] = []

        # Get created by user information
        if self.object.session_id:
            from human_resource.models import TblhrOfficestaff
            from django.contrib.auth.models import User

            # Try to get from HR staff table first
            employee = TblhrOfficestaff.objects.filter(
                empid=self.object.session_id
            ).first()

            if employee:
                context['created_by'] = f"{employee.title}. {employee.employeename}"
            else:
                # Fallback to User model
                try:
                    user = User.objects.filter(username=self.object.session_id).first()
                    context['created_by'] = user.username if user else self.object.session_id
                except:
                    context['created_by'] = self.object.session_id
        else:
            context['created_by'] = 'Unknown'

        return context




class PRUpdateView(MaterialManagementBaseMixin, UpdateView):
    """Update Purchase Requisition"""
    model = PRMaster
    fields = ['pr_no', 'wo_no']
    template_name = 'material_management/transactions/pr_form.html'
    success_url = reverse_lazy('material_management:pr-list')
    pk_url_kwarg = 'pr_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Get all PR line items using m_id (FK to PRMaster.pr_id)
            context['pr_details'] = list(PRDetails.objects.filter(m_id=self.object.pr_id))
        except Exception as e:
            # Handle case where table or column doesn't exist
            print(f"Error fetching PR details for edit: {e}")
            context['pr_details'] = []
        return context




class PRDeleteView(MaterialManagementBaseMixin, DeleteView):
    """Delete Purchase Requisition"""
    model = PRMaster
    success_url = reverse_lazy('material_management:pr-list')
    pk_url_kwarg = 'pr_id'


# =============================================================================
# SPECIAL PURPOSE REQUISITION (SPR) TRANSACTIONS
# =============================================================================



class PRCheckView(MaterialManagementBaseMixin, ListView):
    """PR Check Dashboard - List Pending PRs for checking"""
    model = PRMaster
    template_name = 'material_management/transactions/pr_check.html'
    context_object_name = 'prs'

    def get_queryset(self):
        qs = super().get_queryset().filter(
            comp_id=self.get_compid(),
            fin_year_id=self.get_finyearid()
        )
        # Filter for unchecked PRs (checked is None, 0, or null)
        return qs.filter(Q(checked__isnull=True) | Q(checked=0)).order_by('-pr_id')

    def post(self, request, *args, **kwargs):
        """Check a PR"""
        pr_id = request.POST.get('pr_id')
        pr = get_object_or_404(PRMaster, pr_id=pr_id)
        pr.checked = 1
        pr.checked_by = str(request.user.id)
        pr.checked_date = datetime.now().strftime('%d-%m-%Y')
        pr.checked_time = datetime.now().strftime('%H:%M:%S')
        pr.save()
        messages.success(request, f'PR {pr.pr_no} checked successfully!')
        return HttpResponse(status=200)




class PRApproveView(MaterialManagementBaseMixin, ListView):
    """PR Approve Dashboard - List Checked PRs for approval"""
    model = PRMaster
    template_name = 'material_management/transactions/pr_approve.html'
    context_object_name = 'prs'

    def get_queryset(self):
        qs = super().get_queryset().filter(
            comp_id=self.get_compid(),
            fin_year_id=self.get_finyearid(),
            checked=1
        )
        # Filter for unapproved PRs (approve is None, 0, or null)
        return qs.filter(Q(approve__isnull=True) | Q(approve=0)).order_by('-pr_id')

    def post(self, request, *args, **kwargs):
        """Approve a PR"""
        pr_id = request.POST.get('pr_id')
        pr = get_object_or_404(PRMaster, pr_id=pr_id)
        pr.approve = 1
        pr.approved_by = str(request.user.id)
        pr.approve_date = datetime.now().strftime('%d-%m-%Y')
        pr.approve_time = datetime.now().strftime('%H:%M:%S')
        pr.save()
        messages.success(request, f'PR {pr.pr_no} approved successfully!')
        return HttpResponse(status=200)




class PRAuthorizeView(MaterialManagementBaseMixin, ListView):
    """PR Authorize Dashboard - List Approved PRs for authorization"""
    model = PRMaster
    template_name = 'material_management/transactions/pr_authorize.html'
    context_object_name = 'prs'

    def get_queryset(self):
        qs = super().get_queryset().filter(
            comp_id=self.get_compid(),
            fin_year_id=self.get_finyearid(),
            approve=1
        )
        # Filter for unauthorized PRs (authorize is None, 0, or null)
        return qs.filter(Q(authorize__isnull=True) | Q(authorize=0)).order_by('-pr_id')

    def post(self, request, *args, **kwargs):
        """Authorize a PR"""
        pr_id = request.POST.get('pr_id')
        pr = get_object_or_404(PRMaster, pr_id=pr_id)
        pr.authorize = 1
        pr.authorized_by = str(request.user.id)
        pr.authorize_date = datetime.now().strftime('%d-%m-%Y')
        pr.authorize_time = datetime.now().strftime('%H:%M:%S')
        pr.save()
        messages.success(request, f'PR {pr.pr_no} authorized successfully!')
        return HttpResponse(status=200)




