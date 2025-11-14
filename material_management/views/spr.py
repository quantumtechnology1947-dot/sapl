"""
Material Management SPR Views

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
from ..models import SPRMaster, SPRDetails, MmSprPoTemp, Supplier


def get_user_display_name(user_identifier, compid=None):
    """
    Helper function to get user display name from user ID or username

    Args:
        user_identifier: User ID (int/str) or username (str)
        compid: Optional company ID for filtering employees

    Returns:
        Formatted display name (e.g., "Mr. John Doe") or fallback value
    """
    if not user_identifier:
        return "-"

    from django.contrib.auth.models import User
    from human_resource.models import TblhrOfficestaff

    try:
        # Try to get user by ID first
        try:
            user_id = int(user_identifier)
            user = User.objects.filter(id=user_id).first()
        except (ValueError, TypeError):
            # If not an integer, treat as username
            user = User.objects.filter(username=user_identifier).first()

        if not user:
            # Fallback: Try direct employee lookup by empid
            employee_query = TblhrOfficestaff.objects.filter(empid=user_identifier)
            if compid:
                employee_query = employee_query.filter(compid=compid)
            employee = employee_query.first()

            if employee:
                title = employee.title or ''
                name = employee.employeename or ''
                return f"{title}. {name}".strip() if title and name else (name or str(user_identifier))
            return str(user_identifier)

        # Got user - now look up employee by username
        employee_query = TblhrOfficestaff.objects.filter(empid=user.username)
        if compid:
            employee_query = employee_query.filter(compid=compid)
        employee = employee_query.first()

        if employee:
            title = employee.title or ''
            name = employee.employeename or ''
            return f"{title}. {name}".strip() if title and name else (name or user.username)

        # No employee found - return username
        return user.username

    except Exception as e:
        # Ultimate fallback
        return str(user_identifier) if user_identifier else "-"


class SPRListView(MaterialManagementBaseMixin, ListView):
    """
    Special Purpose Requisition List
    Mirrors: aaspnet/MaterialManagement/Transactions/SPR_Dashboard.aspx
    """
    model = SPRMaster
    template_name = 'material_management/transactions/spr_list.html'
    context_object_name = 'sprs'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter SPRs:
        - By Company and Financial Year (less than or equal to current FY)
        - Show ALL SPRs (authorized and non-authorized)
        - Search by Employee Name or SPR No
        """
        from human_resource.models import TblhrOfficestaff
        from sys_admin.models import TblfinancialMaster

        queryset = SPRMaster.objects.filter(
            comp_id=self.get_compid(),
            fin_year_id__lte=self.get_finyearid()  # Less than or equal to current FY
            # Removed: authorize=0 filter to show ALL SPRs
        )
        
        # Search functionality
        search_field = self.request.GET.get('field', '0')  # Default: Employee Name
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query:
            if search_field == '1':  # Search by SPR No
                queryset = queryset.filter(spr_no__icontains=search_query)
            else:  # Search by Employee Name (field='0')
                # Extract employee ID from autocomplete format: "Name [EmpId]"
                if '[' in search_query and ']' in search_query:
                    emp_id = search_query.split('[')[1].split(']')[0]
                    queryset = queryset.filter(session_id=emp_id)
                else:
                    # Direct employee ID search
                    queryset = queryset.filter(session_id__icontains=search_query)
        
        return queryset.order_by('-spr_id')  # Descending order by ID
    
    def get_context_data(self, **kwargs):
        """Add search parameters and employee/financial year data to context"""
        context = super().get_context_data(**kwargs)
        from human_resource.models import TblhrOfficestaff
        from sys_admin.models import TblfinancialMaster
        
        # Add search field and query
        context['search_field'] = self.request.GET.get('field', '0')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Enrich SPRs with employee names and financial years
        sprs_list = list(context['sprs'])
        for spr in sprs_list:
            # Get employee name
            try:
                employee = TblhrOfficestaff.objects.filter(
                    compid=self.get_compid(),
                    empid=spr.session_id
                ).first()
                if employee:
                    spr.employee_name = f"{employee.title or ''}. {employee.employeename or ''}"
                else:
                    spr.employee_name = "-"
            except Exception:
                spr.employee_name = "-"
            
            # Get financial year
            try:
                fin_year = TblfinancialMaster.objects.get(
                    finyearid=spr.fin_year_id,
                    compid=self.get_compid()
                )
                spr.fin_year_name = fin_year.finyear
            except TblfinancialMaster.DoesNotExist:
                spr.fin_year_name = "-"
            
            # Format dates for display
            spr.checked_display = spr.checked_date if spr.checked == 1 else "NO"
            spr.approved_display = spr.approve_date if spr.approve == 1 else "NO"
            spr.authorized_display = spr.authorize_date if spr.authorize == 1 else "NO"
        
        context['sprs'] = sprs_list
        return context




class SPRNewView(MaterialManagementBaseMixin, TemplateView):
    """
    SPR New - Step 1: Select Department and Account Head Category

    Similar to PR New (Work Order selection), but for departments
    User selects:
    - Business Group (Department) OR Work Order
    - Account Head Category (Labour, With Material, Expenses, Service Provider)

    Converted from: aaspnet/MaterialManagement/Transactions/SPR_New.aspx
    """
    template_name = 'material_management/transactions/spr_new.html'

    def get_context_data(self, **kwargs):
        """Prepare selection options"""
        context = super().get_context_data(**kwargs)
        from human_resource.models import Businessgroup
        from accounts.models import Acchead
        from sales_distribution.models import SdCustWorkorderMaster

        compid = self.get_compid()

        # Get Business Groups (Departments)
        context['business_groups'] = Businessgroup.objects.all().order_by('name')

        # Get Account Head Categories
        context['ah_categories'] = [
            {'value': 'Labour', 'label': 'Labour'},
            {'value': 'With Material', 'label': 'With Material'},
            {'value': 'Expenses', 'label': 'Expenses'},
            {'value': 'Ser. Provider', 'label': 'Service Provider'}
        ]

        # Get open Work Orders (for WO-based SPR)
        context['work_orders'] = SdCustWorkorderMaster.objects.filter(
            compid=compid,
            closeopen=0  # Open work orders only
        ).order_by('-wono')[:50]

        return context




class SPRNewDetailsView(MaterialManagementBaseMixin, TemplateView):
    """
    SPR New - Step 2: AI-Suggested Items for Department

    Similar to PR New Details (Work Order items), but for departments
    Shows AI-suggested items commonly used by this department/AH category

    Converted from: aaspnet/MaterialManagement/Transactions/SPR_New.aspx + SPR_NoCode.aspx
    """
    template_name = 'material_management/transactions/spr_new_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dept_id = self.kwargs.get('dept_id')  # Can be 0 for WO-based SPR
        ah_category = self.kwargs.get('ah_category')
        wo_no = self.kwargs.get('wo_no', '')  # Optional WO number

        context['dept_id'] = dept_id
        context['ah_category'] = ah_category
        context['wo_no'] = wo_no

        # Get department name
        if dept_id and int(dept_id) > 0:
            try:
                from human_resource.models import Businessgroup
                dept = Businessgroup.objects.get(id=dept_id)
                context['dept_name'] = dept.name
            except:
                context['dept_name'] = f"Department {dept_id}"
        else:
            context['dept_name'] = f"Work Order {wo_no}"

        # AI-POWERED: Get AI suggestions for items
        use_ai = self.request.GET.get('ai', 'true').lower() == 'true'

        if use_ai:
            try:
                context['items'] = self.get_ai_suggested_items(dept_id, ah_category)
                context['ai_enabled'] = True
                context['ai_message'] = f'Items suggested by AI based on {context["dept_name"]} history and {ah_category} category'
            except Exception as e:
                print(f"SPR AI failed: {e}")
                import traceback
                traceback.print_exc()
                context['items'] = []
                context['ai_enabled'] = False
                context['ai_message'] = f'AI unavailable. Error: {str(e)}'
        else:
            context['items'] = []
            context['ai_enabled'] = False
            context['ai_message'] = 'AI disabled'

        # Get temp SPR items already added by this user
        context['temp_items'] = self.get_temp_spr_items(dept_id, ah_category)

        # Get suppliers for autocomplete
        context['suppliers'] = self.get_suppliers()

        # Get account heads for this category
        from accounts.models import Acchead
        context['account_heads'] = Acchead.objects.filter(category=ah_category)

        return context

    def get_ai_suggested_items(self, dept_id, ah_category):
        """
        AI-POWERED METHOD: Use Gemini 2.0 Flash to analyze and suggest items
        """
        from material_management.ai_service_spr import EnhancedSPRIntelligenceService

        ai_service = EnhancedSPRIntelligenceService()
        suggestions = ai_service.analyze_department_for_spr(
            dept_id=int(dept_id) if dept_id else None,
            ah_category=ah_category,
            comp_id=self.get_compid()
        )

        # Transform to template format (similar to PR)
        enriched_items = []
        for suggestion in suggestions:
            enriched_item = {
                'ItemId': suggestion['item_id'],
                'ItemCode': suggestion['item_code'],
                'ManfDesc': suggestion['item_desc'],
                'UOMBasic': suggestion.get('uom', 'PCS'),
                'SuggestedQty': suggestion['suggested_qty'],
                'SuggestedSupplier': suggestion.get('suggested_supplier_name', ''),
                'SuggestedSupplierId': suggestion.get('suggested_supplier_id', ''),
                'SuggestedRate': suggestion.get('suggested_rate', 0),
                'SuggestedDiscount': suggestion.get('suggested_discount', 0),
                'AIConfidence': suggestion.get('confidence', 0),
                'AIReasoning': suggestion.get('reasoning', ''),
                'AlternativeSuppliers': suggestion.get('alternative_suppliers', []),
                'UsageCount': suggestion.get('usage_count', 0),
                'RateSource': 'Historical Department Usage'
            }
            enriched_items.append(enriched_item)

        return enriched_items

    def get_suppliers(self):
        """Get all suppliers for autocomplete"""
        suppliers = Supplier.objects.filter(
            comp_id=self.get_compid()
        ).order_by('supplier_name').values('supplier_id', 'supplier_name')
        return list(suppliers)

    def get_temp_spr_items(self, dept_id, ah_category):
        """Get temporary SPR items added by this user (session-based for now)"""
        # For now, use session storage (similar to old cart system)
        # In future, could use a TempSPR model like PR
        temp_key = f'spr_temp_{dept_id}_{ah_category}'
        return self.request.session.get(temp_key, [])

    def post(self, request, *args, **kwargs):
        """Handle adding item to temp or generating SPR"""
        action = request.POST.get('action')

        if action == 'add_item':
            return self.add_item_to_temp(request)
        elif action == 'generate_spr':
            return self.generate_spr(request)
        elif action == 'generate_spr_bulk':
            return self.generate_spr_bulk(request)
        elif action == 'delete_temp':
            return self.delete_temp_item(request)

        return self.get(request, *args, **kwargs)

    def add_item_to_temp(self, request):
        """Add item with supplier/qty/rate to temporary storage"""
        dept_id = self.kwargs.get('dept_id')
        ah_category = self.kwargs.get('ah_category')
        wo_no = self.kwargs.get('wo_no', '')

        item_id = request.POST.get('item_id')
        supplier_input = request.POST.get('supplier')
        qty = float(request.POST.get('qty', 1))
        rate = float(request.POST.get('rate', 0))
        discount = float(request.POST.get('discount', 0))
        delivery_date = request.POST.get('delivery_date')
        ah_id = request.POST.get('ah_id')
        remarks = request.POST.get('remarks', '')

        # Extract supplier ID
        supplier_id = ''
        if supplier_input:
            if '[' in supplier_input and ']' in supplier_input:
                supplier_id = supplier_input.split('[')[1].split(']')[0]
            else:
                try:
                    supplier = Supplier.objects.filter(
                        supplier_name=supplier_input,
                        comp_id=self.get_compid()
                    ).first()
                    if supplier:
                        supplier_id = supplier.supplier_id
                except:
                    pass

        if not supplier_id:
            messages.error(request, 'Invalid supplier selected')
            return self.get(request)

        # Store in session (temp storage)
        temp_key = f'spr_temp_{dept_id}_{ah_category}'
        temp_items = request.session.get(temp_key, [])

        temp_items.append({
            'item_id': item_id,
            'supplier_id': supplier_id,
            'qty': qty,
            'rate': rate,
            'discount': discount,
            'delivery_date': delivery_date,
            'ah_id': ah_id,
            'remarks': remarks
        })

        request.session[temp_key] = temp_items
        request.session.modified = True

        messages.success(request, 'Item added to SPR')
        return self.get(request)

    def generate_spr_bulk(self, request):
        """Generate SPR directly from table input (bulk mode) - matches PR bulk generation"""
        import json
        from decimal import Decimal
        from datetime import datetime as dt_module

        dept_id = self.kwargs.get('dept_id')
        ah_category = self.kwargs.get('ah_category')
        wo_no = self.kwargs.get('wo_no', '')

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
            messages.error(request, 'No items selected for SPR generation')
            return self.get(request)

        # Generate SPR Number
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        employee_id = self.get_employee_id()  # Use employee_id instead of session_id

        # Get max SPR number by parsing actual spr_no values
        max_spr_obj = SPRMaster.objects.filter(
            comp_id=compid,
            fin_year_id=finyearid,
            spr_no__isnull=False
        ).exclude(spr_no='').order_by('-spr_no').first()

        if max_spr_obj and max_spr_obj.spr_no:
            try:
                # Parse the spr_no as integer (removing leading zeros)
                max_spr_num = int(max_spr_obj.spr_no)
            except (ValueError, TypeError):
                max_spr_num = 0
        else:
            max_spr_num = 0

        next_spr_num = max_spr_num + 1
        next_spr_no = f'{next_spr_num:04d}'

        # Create SPR Master
        now = dt_module.now()
        spr_master = SPRMaster.objects.create(
            spr_no=next_spr_no,
            comp_id=compid,
            fin_year_id=finyearid,
            session_id=employee_id,  # Store employee ID, not session key
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S'),
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
            ah_id = item_data.get('ah_id')
            remarks = item_data.get('remarks', '')

            # Extract supplier ID
            supplier_id = ''
            if supplier_input:
                try:
                    supplier = Supplier.objects.filter(
                        supplier_name=supplier_input,
                        comp_id=compid
                    ).first()
                    if supplier:
                        supplier_id = supplier.supplier_id
                    else:
                        if ' - ' in supplier_input:
                            supplier_id = supplier_input.split(' - ')[0].strip()
                        else:
                            supplier_id = supplier_input
                except:
                    if ' - ' in supplier_input:
                        supplier_id = supplier_input.split(' - ')[0].strip()
                    else:
                        supplier_id = supplier_input

            # Format delivery date
            if delivery_date:
                try:
                    date_obj = dt_module.strptime(delivery_date, '%Y-%m-%d')
                    del_date_str = date_obj.strftime('%d-%m-%Y')
                except:
                    del_date_str = delivery_date
            else:
                del_date_str = now.strftime('%d-%m-%Y')

            # Create SPR Detail
            SPRDetails.objects.create(
                m_id=spr_master.spr_id,
                spr_no=next_spr_no,
                item_id=item_id,
                supplier_id=supplier_id,
                qty=Decimal(str(qty)),
                rate=Decimal(str(rate)),
                discount=Decimal(str(discount)),
                del_date=del_date_str,
                ah_id=ah_id,
                wo_no=wo_no if wo_no else '',
                dept_id=int(dept_id) if dept_id and int(dept_id) > 0 else 0,
                remarks=remarks
            )

        messages.success(request, f'SPR {next_spr_no} generated successfully with {len(items_data)} item(s)!')
        return redirect('material_management:spr-list')

    def generate_spr(self, request):
        """Generate SPR from temp items (session storage)"""
        from decimal import Decimal
        from datetime import datetime as dt_module
        
        dept_id = self.kwargs.get('dept_id')
        ah_category = self.kwargs.get('ah_category')
        wo_no = self.kwargs.get('wo_no', '')
        
        # Get temp items from session
        temp_key = f'spr_temp_{dept_id}_{ah_category}'
        temp_items = request.session.get(temp_key, [])
        
        if not temp_items:
            messages.error(request, 'No items in basket. Please add items before generating SPR.')
            return self.get(request)
        
        # Generate SPR Number
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        employee_id = self.get_employee_id()  # Use employee_id instead of session_id

        # Get max SPR number by parsing actual spr_no values
        max_spr_obj = SPRMaster.objects.filter(
            comp_id=compid,
            fin_year_id=finyearid,
            spr_no__isnull=False
        ).exclude(spr_no='').order_by('-spr_no').first()

        if max_spr_obj and max_spr_obj.spr_no:
            try:
                # Parse the spr_no as integer (removing leading zeros)
                max_spr_num = int(max_spr_obj.spr_no)
            except (ValueError, TypeError):
                max_spr_num = 0
        else:
            max_spr_num = 0

        next_spr_num = max_spr_num + 1
        next_spr_no = f'{next_spr_num:04d}'

        # Create SPR Master
        now = dt_module.now()
        spr_master = SPRMaster.objects.create(
            spr_no=next_spr_no,
            comp_id=compid,
            fin_year_id=finyearid,
            session_id=employee_id,  # Store employee ID, not session key
            sys_date=now.strftime('%d-%m-%Y'),
            sys_time=now.strftime('%H:%M:%S'),
            checked=0,
            approve=0,
            authorize=0
        )
        
        # Create SPR Details from temp items
        for item in temp_items:
            SPRDetails.objects.create(
                m_id=spr_master.spr_id,
                spr_no=next_spr_no,
                item_id=item['item_id'],
                supplier_id=item['supplier_id'],
                qty=Decimal(str(item['qty'])),
                rate=Decimal(str(item['rate'])),
                discount=Decimal(str(item['discount'])),
                del_date=item['delivery_date'],
                ah_id=item['ah_id'],
                wo_no=wo_no if wo_no else '',
                dept_id=int(dept_id) if dept_id and int(dept_id) > 0 else 0,
                remarks=item.get('remarks', '')
            )
        
        # Clear temp basket
        request.session[temp_key] = []
        request.session.modified = True
        
        messages.success(request, f'SPR {next_spr_no} generated successfully with {len(temp_items)} item(s)!')
        return redirect('material_management:spr-detail', spr_id=spr_master.spr_id)

    def delete_temp_item(self, request):
        """Delete item from temp storage"""
        dept_id = self.kwargs.get('dept_id')
        ah_category = self.kwargs.get('ah_category')
        temp_id = int(request.POST.get('temp_id', -1))

        temp_key = f'spr_temp_{dept_id}_{ah_category}'
        temp_items = request.session.get(temp_key, [])

        if 0 <= temp_id < len(temp_items):
            temp_items.pop(temp_id)
            request.session[temp_key] = temp_items
            request.session.modified = True
            messages.success(request, 'Item removed from SPR')

        return self.get(request)






class SPRDetailView(MaterialManagementBaseMixin, DetailView):
    """View SPR Details"""
    model = SPRMaster
    template_name = 'material_management/transactions/spr_detail.html'
    context_object_name = 'spr'
    pk_url_kwarg = 'spr_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['spr_details'] = SPRDetails.objects.filter(
            m_id=self.object.spr_id,
            spr_no=self.object.spr_no
        )

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




class SPRUpdateView(MaterialManagementBaseMixin, UpdateView):
    """Update SPR"""
    model = SPRMaster
    fields = ['spr_no']
    template_name = 'material_management/transactions/spr_form.html'
    success_url = reverse_lazy('material_management:spr-list')
    pk_url_kwarg = 'spr_id'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'SPR {self.object.spr_no} updated successfully!')
        return response




class SPRDeleteView(MaterialManagementBaseMixin, DeleteView):
    """Delete SPR"""
    model = SPRMaster
    success_url = reverse_lazy('material_management:spr-list')
    pk_url_kwarg = 'spr_id'

    def delete(self, request, *args, **kwargs):
        spr = self.get_object()
        messages.success(request, f'SPR {spr.spr_no} deleted successfully!')
        return super().delete(request, *args, **kwargs)


class SPRCheckView(MaterialManagementBaseMixin, ListView):
    """SPR Check Dashboard - List Pending SPRs for checking"""
    model = SPRMaster
    template_name = 'material_management/transactions/spr_check.html'
    context_object_name = 'sprs'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().filter(
            comp_id=self.get_compid()
        )
        # Filter for unchecked SPRs (checked is None, 0, or null)
        return qs.filter(Q(checked__isnull=True) | Q(checked=0)).order_by('-spr_id')

    def get_context_data(self, **kwargs):
        """Add WO number, item count, employee names and fin year to each SPR"""
        context = super().get_context_data(**kwargs)
        from material_management.models import SPRDetails
        from sys_admin.models import TblfinancialMaster

        sprs_list = list(context['sprs'])
        compid = self.get_compid()

        for spr in sprs_list:
            # Get first WO number from SPR details
            first_detail = SPRDetails.objects.filter(m_id=spr.spr_id).first()
            spr.wo_no = first_detail.wo_no if first_detail else None
            # Get item count
            spr.item_count = SPRDetails.objects.filter(m_id=spr.spr_id).count()

            # Enrich user names using helper function
            spr.created_by_name = get_user_display_name(spr.session_id, compid)
            spr.checked_by_name = get_user_display_name(spr.checked_by, compid)
            spr.approved_by_name = get_user_display_name(spr.approved_by, compid)
            spr.authorized_by_name = get_user_display_name(spr.authorized_by, compid)

            # Get financial year
            try:
                fin_year = TblfinancialMaster.objects.get(
                    finyearid=spr.fin_year_id,
                    compid=compid
                )
                spr.fin_year_name = fin_year.finyear
            except TblfinancialMaster.DoesNotExist:
                spr.fin_year_name = "-"

        context['sprs'] = sprs_list
        return context

    def post(self, request, *args, **kwargs):
        """Check an SPR"""
        spr_id = request.POST.get('spr_id')
        spr = get_object_or_404(SPRMaster, spr_id=spr_id)
        spr.checked = 1
        spr.checked_by = str(request.user.id)
        spr.checked_date = datetime.now().strftime('%d-%m-%Y')
        spr.checked_time = datetime.now().strftime('%H:%M:%S')
        spr.save()
        messages.success(request, f'SPR {spr.spr_no} checked successfully!')
        return redirect('material_management:spr-check-list')




class SPRApproveView(MaterialManagementBaseMixin, ListView):
    """SPR Approve Dashboard - List Checked SPRs for approval"""
    model = SPRMaster
    template_name = 'material_management/transactions/spr_approve.html'
    context_object_name = 'sprs'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().filter(
            comp_id=self.get_compid(),
            checked=1
        )
        # Filter for unapproved SPRs (approve is None, 0, or null)
        return qs.filter(Q(approve__isnull=True) | Q(approve=0)).order_by('-spr_id')

    def get_context_data(self, **kwargs):
        """Add WO number, item count, employee names and fin year to each SPR"""
        context = super().get_context_data(**kwargs)
        from material_management.models import SPRDetails
        from sys_admin.models import TblfinancialMaster

        sprs_list = list(context['sprs'])
        compid = self.get_compid()

        for spr in sprs_list:
            # Get first WO number from SPR details
            first_detail = SPRDetails.objects.filter(m_id=spr.spr_id).first()
            spr.wo_no = first_detail.wo_no if first_detail else None
            # Get item count
            spr.item_count = SPRDetails.objects.filter(m_id=spr.spr_id).count()

            # Enrich user names using helper function
            spr.created_by_name = get_user_display_name(spr.session_id, compid)
            spr.checked_by_name = get_user_display_name(spr.checked_by, compid)
            spr.approved_by_name = get_user_display_name(spr.approved_by, compid)
            spr.authorized_by_name = get_user_display_name(spr.authorized_by, compid)

            # Get financial year
            try:
                fin_year = TblfinancialMaster.objects.get(
                    finyearid=spr.fin_year_id,
                    compid=compid
                )
                spr.fin_year_name = fin_year.finyear
            except TblfinancialMaster.DoesNotExist:
                spr.fin_year_name = "-"

        context['sprs'] = sprs_list
        return context

    def post(self, request, *args, **kwargs):
        """Approve an SPR"""
        spr_id = request.POST.get('spr_id')
        spr = get_object_or_404(SPRMaster, spr_id=spr_id)
        spr.approve = 1
        spr.approved_by = str(request.user.id)
        spr.approve_date = datetime.now().strftime('%d-%m-%Y')
        spr.approve_time = datetime.now().strftime('%H:%M:%S')
        spr.save()
        messages.success(request, f'SPR {spr.spr_no} approved successfully!')
        return redirect('material_management:spr-approve-list')




class SPRAuthorizeView(MaterialManagementBaseMixin, ListView):
    """SPR Authorize Dashboard - List Approved SPRs for authorization"""
    model = SPRMaster
    template_name = 'material_management/transactions/spr_authorize.html'
    context_object_name = 'sprs'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().filter(
            comp_id=self.get_compid(),
            approve=1
        )
        # Filter for unauthorized SPRs (authorize is None, 0, or null)
        return qs.filter(Q(authorize__isnull=True) | Q(authorize=0)).order_by('-spr_id')

    def get_context_data(self, **kwargs):
        """Add WO number, item count, employee names and fin year to each SPR"""
        context = super().get_context_data(**kwargs)
        from material_management.models import SPRDetails
        from sys_admin.models import TblfinancialMaster

        sprs_list = list(context['sprs'])
        compid = self.get_compid()

        for spr in sprs_list:
            # Get first WO number from SPR details
            first_detail = SPRDetails.objects.filter(m_id=spr.spr_id).first()
            spr.wo_no = first_detail.wo_no if first_detail else None
            # Get item count
            spr.item_count = SPRDetails.objects.filter(m_id=spr.spr_id).count()

            # Enrich user names using helper function
            spr.created_by_name = get_user_display_name(spr.session_id, compid)
            spr.checked_by_name = get_user_display_name(spr.checked_by, compid)
            spr.approved_by_name = get_user_display_name(spr.approved_by, compid)
            spr.authorized_by_name = get_user_display_name(spr.authorized_by, compid)

            # Get financial year
            try:
                fin_year = TblfinancialMaster.objects.get(
                    finyearid=spr.fin_year_id,
                    compid=compid
                )
                spr.fin_year_name = fin_year.finyear
            except TblfinancialMaster.DoesNotExist:
                spr.fin_year_name = "-"

        context['sprs'] = sprs_list
        return context

    def post(self, request, *args, **kwargs):
        """Authorize an SPR"""
        spr_id = request.POST.get('spr_id')
        spr = get_object_or_404(SPRMaster, spr_id=spr_id)
        spr.authorize = 1
        spr.authorized_by = str(request.user.id)
        spr.authorize_date = datetime.now().strftime('%d-%m-%Y')
        spr.authorize_time = datetime.now().strftime('%H:%M:%S')
        spr.save()
        messages.success(request, f'SPR {spr.spr_no} authorized successfully!')
        return redirect('material_management:spr-authorize-list')




