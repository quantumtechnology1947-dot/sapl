"""
Material Management Rate Register and Rate Lock/Unlock Views

Converted from: aspnet/Module/MaterialManagement/Masters/RateSet.aspx
                aspnet/Module/MaterialManagement/Transactions/RateLockUnLock.aspx
Following Django conventions, HTMX patterns, and Tailwind standards
"""

from datetime import datetime

from django.views.generic import ListView, DetailView, View
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q

from core.mixins import HTMXResponseMixin
from .dashboard import MaterialManagementBaseMixin
from ..models import RateRegister, RateLockUnlock, POMaster, Supplier


# =============================================================================
# RATE REGISTER (READ-ONLY REPORT)
# =============================================================================

class RateSetSearchView(MaterialManagementBaseMixin, ListView):
    """
    Rate Set - Step 1: Search and select item from inventory
    Converted from: aaspnet/Module/MaterialManagement/Masters/RateSet.aspx
    """
    template_name = 'material_management/masters/rate_set_search.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        from design.models import TbldgItemMaster, TbldgCategoryMaster

        queryset = TbldgItemMaster.objects.filter(compid=self.get_compid()).select_related('cid')

        # Get search parameters
        search_type = self.request.GET.get('search_type', '')
        category_id = self.request.GET.get('category_id', '')
        search_field = self.request.GET.get('search_field', '')
        search_value = self.request.GET.get('search_value', '')
        location = self.request.GET.get('location', '')

        # Filter by search type
        if search_type == 'Category' and category_id and category_id != 'Select':
            queryset = queryset.filter(cid=category_id)

            # Apply field-specific search
            if search_field and search_value:
                if search_field == 'ItemCode':
                    queryset = queryset.filter(itemcode__istartswith=search_value)
                elif search_field == 'ManfDesc':
                    queryset = queryset.filter(manfdesc__icontains=search_value)

            # Apply location filter
            if search_field == 'Location' and location and location != 'Select':
                queryset = queryset.filter(location=location)

        elif search_type == 'WOItems':
            # Search in WO items
            if search_field and search_value:
                if search_field == 'ItemCode':
                    queryset = queryset.filter(itemcode__icontains=search_value)
                elif search_field == 'ManfDesc':
                    queryset = queryset.filter(manfdesc__icontains=search_value)

        return queryset.order_by('itemcode')

    def get_context_data(self, **kwargs):
        from design.models import TbldgCategoryMaster
        context = super().get_context_data(**kwargs)

        # Get all categories for dropdown
        context['categories'] = TbldgCategoryMaster.objects.filter(
            compid=self.get_compid()
        ).order_by('symbol', 'cname')

        # Get unique locations
        from design.models import TbldgItemMaster
        context['locations'] = TbldgItemMaster.objects.filter(
            compid=self.get_compid()
        ).values_list('location', flat=True).distinct().order_by('location')

        # Preserve search parameters
        context['search_type'] = self.request.GET.get('search_type', 'Select')
        context['category_id'] = self.request.GET.get('category_id', 'Select')
        context['search_field'] = self.request.GET.get('search_field', 'Select')
        context['search_value'] = self.request.GET.get('search_value', '')
        context['location'] = self.request.GET.get('location', 'Select')

        return context


class RateSetDetailsView(MaterialManagementBaseMixin, ListView):
    """
    Rate Set - Step 2: View rates for item and set minimum rate
    Converted from: aaspnet/Module/MaterialManagement/Masters/RateSet_details.aspx
    """
    model = RateRegister
    template_name = 'material_management/masters/rate_set_details.html'
    context_object_name = 'rates'
    paginate_by = 20

    def get_queryset(self):
        item_id = self.request.GET.get('item_id')
        supplier_search = self.request.GET.get('supplier', '')

        if not item_id:
            return RateRegister.objects.none()

        # Get all rates for this item across all financial years
        queryset = RateRegister.objects.filter(
            item_id=item_id,
            comp_id=self.get_compid()
        ).select_related().order_by('-sys_date', '-id')

        # Filter by supplier if provided
        if supplier_search:
            # Extract supplier code from "Name [Code]" format
            if '[' in supplier_search and ']' in supplier_search:
                supplier_code = supplier_search.split('[')[1].split(']')[0]
            else:
                supplier_code = supplier_search

            # Filter by supplier through PO
            queryset = queryset.filter(po_id__in=POMaster.objects.filter(
                supplier_id=supplier_code
            ).values_list('po_id', flat=True))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from design.models import TbldgItemMaster
        from sys_admin.models import TblfinancialMaster

        item_id = self.request.GET.get('item_id')
        supplier_search = self.request.GET.get('supplier', '')

        # Get item details
        if item_id:
            try:
                context['item'] = TbldgItemMaster.objects.get(id=item_id, compid=self.get_compid())
            except TbldgItemMaster.DoesNotExist:
                context['item'] = None

            # Enrich rate data with PO and supplier information
            enriched_rates = []
            for rate in context['rates']:
                rate_data = {
                    'id': rate.id,
                    'item_id': rate.item_id,
                    'rate': rate.rate,
                    'discount': rate.discount,
                    'pf': rate.pf,
                    'ex_st': rate.ex_st,
                    'vat': rate.vat,
                    'flag': rate.flag,
                    'amount': float(rate.rate) - (float(rate.rate) * float(rate.discount or 0) / 100) if rate.rate else 0,
                }

                # Get financial year
                try:
                    finyear = TblfinancialMaster.objects.get(
                        finyearid=rate.fin_year_id,
                        compid=self.get_compid()
                    )
                    rate_data['finyear'] = finyear.finyear
                except:
                    rate_data['finyear'] = f"FY-{rate.fin_year_id}"

                # Get PO details
                if rate.po_id:
                    try:
                        po = POMaster.objects.get(po_id=rate.po_id)
                        rate_data['po_no'] = po.po_no

                        # Get supplier details
                        if po.supplier_id:
                            try:
                                supplier = Supplier.objects.get(
                                    supplier_id=po.supplier_id,
                                    comp_id=self.get_compid()
                                )
                                rate_data['supplier_name'] = f"{supplier.supplier_name} [{po.supplier_id}]"
                            except Supplier.DoesNotExist:
                                rate_data['supplier_name'] = f"[{po.supplier_id}]"
                        else:
                            rate_data['supplier_name'] = "-"
                    except POMaster.DoesNotExist:
                        rate_data['po_no'] = "-"
                        rate_data['supplier_name'] = "-"
                else:
                    rate_data['po_no'] = "-"
                    rate_data['supplier_name'] = "-"

                enriched_rates.append(rate_data)

            context['enriched_rates'] = enriched_rates

        context['item_id'] = item_id
        context['supplier_search'] = supplier_search

        return context

    def post(self, request, *args, **kwargs):
        """Handle setting the minimum rate (Flag=1)"""
        rate_id = request.POST.get('rate_id')
        item_id = request.POST.get('item_id')

        if rate_id and item_id:
            # First, unset all flags for this item
            RateRegister.objects.filter(item_id=item_id).update(flag=0)

            # Then set the selected rate as minimum
            RateRegister.objects.filter(id=rate_id).update(flag=1)

            messages.success(request, 'Minimum rate is Set.')

        # Redirect back to same page with parameters
        return redirect(f"{reverse('material_management:rate-set-details')}?item_id={item_id}")


class RateRegisterListView(MaterialManagementBaseMixin, ListView):
    """Rate Register List View - Search items to view their rate history"""
    model = RateRegister
    template_name = 'material_management/masters/rate_register_list.html'
    context_object_name = 'rates'
    paginate_by = 20

    def get_queryset(self):
        # Show all historical rates across all financial years for rate lookup
        queryset = super().get_queryset().filter(
            comp_id=self.get_compid()
        ).order_by('-id')

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(item_id__icontains=search) |
                Q(po_no__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class RateRegisterDetailView(MaterialManagementBaseMixin, ListView):
    """Rate Register Detail View - Show all rates for a specific item and set minimum rate"""
    model = RateRegister
    template_name = 'material_management/masters/rate_register_detail.html'
    context_object_name = 'rates'
    paginate_by = 20

    def get_queryset(self):
        item_id = self.kwargs.get('item_id')
        # Show all historical rates for this item across all financial years
        queryset = super().get_queryset().filter(
            comp_id=self.get_compid(),
            item_id=item_id
        ).order_by('-sys_date', '-id')

        # Supplier filter
        supplier = self.request.GET.get('supplier', '')
        if supplier:
            queryset = queryset.filter(supplier_code__icontains=supplier)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from design.models import TbldgItemMaster
        from sys_admin.models import TblfinancialMaster

        item_id = self.kwargs.get('item_id')
        supplier_filter = self.request.GET.get('supplier', '')

        # Get item details
        if item_id:
            try:
                context['item'] = TbldgItemMaster.objects.get(id=item_id, compid=self.get_compid())
            except TbldgItemMaster.DoesNotExist:
                context['item'] = None

            # Enrich rate data with PO and supplier information
            enriched_rates = []
            for rate in context['rates']:
                rate_data = {
                    'id': rate.id,
                    'item_id': rate.item_id,
                    'rate': rate.rate,
                    'discount': rate.discount,
                    'pf': rate.pf,
                    'ex_st': rate.ex_st,
                    'vat': rate.vat,
                    'flag': rate.flag,
                    'sys_date': rate.sys_date,
                    'amount': float(rate.rate) - (float(rate.rate) * float(rate.discount or 0) / 100) if rate.rate else 0,
                }

                # Get financial year
                try:
                    finyear = TblfinancialMaster.objects.get(
                        finyearid=rate.fin_year_id,
                        compid=self.get_compid()
                    )
                    rate_data['finyear'] = finyear.finyear
                except:
                    rate_data['finyear'] = f"FY-{rate.fin_year_id}"

                # Get PO details
                if rate.po_id:
                    try:
                        po = POMaster.objects.get(po_id=rate.po_id)
                        rate_data['po_no'] = po.po_no

                        # Get supplier details
                        if po.supplier_id:
                            try:
                                supplier = Supplier.objects.get(
                                    supplier_id=po.supplier_id,
                                    comp_id=self.get_compid()
                                )
                                rate_data['supplier_name'] = f"{supplier.supplier_name} [{po.supplier_id}]"
                            except Supplier.DoesNotExist:
                                rate_data['supplier_name'] = f"[{po.supplier_id}]"
                        else:
                            rate_data['supplier_name'] = "-"
                    except POMaster.DoesNotExist:
                        rate_data['po_no'] = "-"
                        rate_data['supplier_name'] = "-"
                else:
                    rate_data['po_no'] = "-"
                    rate_data['supplier_name'] = "-"

                enriched_rates.append(rate_data)

            context['enriched_rates'] = enriched_rates

        context['item_id'] = item_id
        context['supplier_filter'] = supplier_filter
        return context

    def post(self, request, *args, **kwargs):
        """Handle setting the minimum rate (Flag=1)"""
        selected_rate_id = request.POST.get('selected_rate')
        item_id = self.kwargs.get('item_id')

        if selected_rate_id and item_id:
            # First, unset all flags for this item
            RateRegister.objects.filter(item_id=item_id).update(flag=0)

            # Then set the selected rate as minimum
            RateRegister.objects.filter(id=selected_rate_id).update(flag=1)

            messages.success(request, 'Minimum rate has been set successfully.')

        return self.get(request, *args, **kwargs)


# =============================================================================
# RATE MANAGEMENT TRANSACTIONS
# =============================================================================

class RateLockUnlockView(MaterialManagementBaseMixin, ListView):
    """
    Rate Lock/Unlock - Main transaction page

    Converted from: aaspnet/Module/MaterialManagement/Transactions/RateLockUnLock.aspx

    This replicates the stored procedure GetRateLockUnlockItem which:
    1. Fetches items from tblDG_Item_Master based on search criteria
    2. For each item, LEFT JOINs with tblMM_RateLockUnLock_Master to get lock status
    3. Returns: Id, ItemCode, ManfDesc, UOMBasic, LockUnlock (the lock record ID or NULL)

    Workflow:
    1. User selects Type (Category or WOItems)
    2. If Category selected, show category dropdown
    3. User selects Search Code (ItemCode or ManfDesc)
    4. User enters search value
    5. Grid shows items from Item Master
    6. For each item, check if locked in RateLockUnlock table (lock_unlock=1)
    7. User can lock item with Type 0/1/2 or unlock existing locks
    """
    template_name = 'material_management/transactions/rate_lock_unlock.html'
    context_object_name = 'items_data'
    paginate_by = 20

    def get_queryset(self):
        from design.models import TbldgItemMaster

        # Get filter parameters
        search_type = self.request.GET.get('type', '')
        category = self.request.GET.get('category', '')
        search_code = self.request.GET.get('search_code', '')
        search_value = self.request.GET.get('search_value', '').strip()

        # Return empty if no search criteria
        if not (search_type and search_code and search_value):
            return []

        # Start with all items from Item Master
        queryset = TbldgItemMaster.objects.filter(
            compid=self.get_compid(),
            finyearid__lte=self.get_finyearid()
        )

        # Apply Type filter
        if search_type == 'Category' and category:
            queryset = queryset.filter(cid=category)

        # Apply Search Code filter
        if search_code == 'ItemCode':
            queryset = queryset.filter(itemcode__istartswith=search_value)
        elif search_code == 'ManfDesc':
            queryset = queryset.filter(manfdesc__icontains=search_value)

        # Order by item code
        return queryset.select_related('cid').order_by('itemcode')

    def get_context_data(self, **kwargs):
        from design.models import TbldgCategoryMaster
        from sys_admin.models import UnitMaster

        context = super().get_context_data(**kwargs)

        # Get filter parameters
        search_type = self.request.GET.get('type', '')
        category = self.request.GET.get('category', '')
        search_code = self.request.GET.get('search_code', '')
        search_value = self.request.GET.get('search_value', '').strip()

        # Store in context for form preservation
        context['search_type'] = search_type
        context['category'] = category
        context['search_code'] = search_code
        context['search_value'] = search_value

        # Load categories for dropdown
        context['categories'] = TbldgCategoryMaster.objects.filter(
            compid=self.get_compid()
        ).order_by('symbol', 'cname')

        # Get all UOM symbols in one query for efficiency
        uom_dict = {uom.id: uom.symbol for uom in UnitMaster.objects.all()}

        # Enrich items with lock status and UOM
        items_data = []
        for item in context['object_list']:
            # Get UOM symbol
            uom_symbol = uom_dict.get(item.uombasic, '-')

            # Get lock status from RateLockUnlock table
            # Check if item has a lock record with LockUnlock=1 (currently locked)
            lock_record = RateLockUnlock.objects.filter(
                comp_id=self.get_compid(),
                item_id=item.id,
                lock_unlock=1
            ).order_by('-id').first()

            items_data.append({
                'item': item,
                'uom_symbol': uom_symbol,
                'lock_record': lock_record,
                'is_locked': lock_record is not None,
                'lock_type': lock_record.type if lock_record else None
            })

        context['items_data'] = items_data

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle lock/unlock actions

        ASP.NET Logic (counter-intuitive naming):
        - "Unlock" button (CommandName="Sel"): INSERTS record with LockUnlock=1 → LOCKS item
        - "Lock" button (CommandName="Sel1"): UPDATES record to LockUnlock=0 → UNLOCKS item
        """
        action = request.POST.get('action')  # 'unlock' or 'lock'
        item_id = request.POST.get('item_id')
        lock_type = request.POST.get('lock_type')  # 0=PR, 1=SPR, 2=PO
        lock_record_id = request.POST.get('lock_record_id')

        now = datetime.now()

        # "Unlock" button clicked → LOCK the item (insert record with LockUnlock=1)
        if action == 'unlock' and item_id and lock_type is not None:
            RateLockUnlock.objects.create(
                sys_date=now.strftime('%d-%m-%Y'),
                sys_time=now.strftime('%H:%M:%S'),
                session_id=str(request.user.username) if request.user.is_authenticated else str(request.user.id),
                comp_id=self.get_compid(),
                fin_year_id=self.get_finyearid(),
                item_id=int(item_id),
                type=int(lock_type),
                lock_unlock=1,  # 1 = Locked
                locked_by_transaction=str(request.user.username) if request.user.is_authenticated else str(request.user.id),
                lock_date=now.strftime('%d-%m-%Y'),
                lock_time=now.strftime('%H:%M:%S')
            )
            messages.success(request, 'Rate locked successfully!')

        # "Lock" button clicked → UNLOCK the item (update record to LockUnlock=0)
        elif action == 'lock' and lock_record_id:
            RateLockUnlock.objects.filter(
                id=int(lock_record_id),
                comp_id=self.get_compid()
            ).update(
                lock_unlock=0,  # 0 = Unlocked
                locked_by_transaction=str(request.user.username) if request.user.is_authenticated else str(request.user.id),
                lock_date=now.strftime('%d-%m-%Y'),
                lock_time=now.strftime('%H:%M:%S')
            )
            messages.success(request, 'Rate unlocked successfully!')

        # Preserve search parameters in redirect
        query_params = request.GET.copy()
        redirect_url = f"{request.path}?{query_params.urlencode()}" if query_params else request.path
        return redirect(redirect_url)


class RateLockUnlockListView(MaterialManagementBaseMixin, HTMXResponseMixin, ListView):
    """
    Rate Lock/Unlock Transaction View
    Allows users to lock/unlock item rates for PR, SPR, or PO

    Converted from: aaspnet/Module/MaterialManagement/Transactions/RateLockUnLock.aspx
    """
    model = RateLockUnlock
    template_name = 'material_management/rate_lock_unlock/list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        """
        Get items based on search criteria
        Mimics the Fillgrid() method from ASP.NET
        """
        from design.models import TbldgItemMaster, TbldgCategoryMaster

        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        queryset = TbldgItemMaster.objects.filter(
            compid=company_id,
            finyearid__lte=financial_year_id
        ).select_related()

        # Get search parameters
        search_type = self.request.GET.get('type', '')
        category_id = self.request.GET.get('category', '')
        search_field = self.request.GET.get('search_field', '')
        search_text = self.request.GET.get('search_text', '')

        # Filter by category
        if search_type == 'Category' and category_id:
            queryset = queryset.filter(cid=category_id)

        # Filter by search field
        if search_field and search_text:
            if search_field == 'ItemCode':
                queryset = queryset.filter(itemcode__icontains=search_text)
            elif search_field == 'Description':
                queryset = queryset.filter(manfdesc__icontains=search_text)

        # Annotate with lock status
        queryset = queryset.extra(
            select={
                'lock_id': '''
                    SELECT Id FROM tblMM_RateLockUnLock_Master
                    WHERE ItemId = tblDG_Item_Master.Id
                    AND CompId = %s
                    ORDER BY Id DESC LIMIT 1
                ''',
                'lock_status': '''
                    SELECT LockUnlock FROM tblMM_RateLockUnLock_Master
                    WHERE ItemId = tblDG_Item_Master.Id
                    AND CompId = %s
                    ORDER BY Id DESC LIMIT 1
                ''',
                'lock_type': '''
                    SELECT Type FROM tblMM_RateLockUnLock_Master
                    WHERE ItemId = tblDG_Item_Master.Id
                    AND CompId = %s
                    ORDER BY Id DESC LIMIT 1
                '''
            },
            select_params=[company_id, company_id, company_id]
        )

        return queryset.order_by('itemcode')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from design.models import TbldgCategoryMaster

        company_id = self.get_compid()

        # Get categories for dropdown
        context['categories'] = TbldgCategoryMaster.objects.filter(
            compid=company_id
        ).order_by('symbol')

        # Pass search parameters
        context['search_type'] = self.request.GET.get('type', '')
        context['category_id'] = self.request.GET.get('category', '')
        context['search_field'] = self.request.GET.get('search_field', '')
        context['search_text'] = self.request.GET.get('search_text', '')

        return context


class RateLockUnlockActionView(MaterialManagementBaseMixin, View):
    """
    Handle lock/unlock actions
    Mimics GridView2_RowCommand from ASP.NET
    """

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')  # 'lock' or 'unlock'
        item_id = request.POST.get('item_id')
        lock_type = request.POST.get('lock_type')  # 0=PR, 1=SPR, 2=PO
        lock_id = request.POST.get('lock_id')  # For unlock action

        company_id = self.get_compid()
        financial_year_id = self.get_finyearid()

        if action == 'lock':
            # Validate lock_type is provided
            if not lock_type:
                messages.error(request, 'Please select unlock type (PR/SPR/PO)')
                return redirect('material_management:rate_lock_unlock_list')

            # Create new lock record
            RateLockUnlock.objects.create(
                sys_date=datetime.now().strftime('%d-%m-%Y'),
                sys_time=datetime.now().strftime('%H:%M:%S'),
                comp_id=company_id,
                fin_year_id=financial_year_id,
                session_id=request.user.username,
                item_id=item_id,
                type=int(lock_type),
                lock_unlock=1  # 1 = Locked
            )
            messages.success(request, 'Rate locked successfully')

        elif action == 'unlock':
            # Update existing lock record
            if lock_id:
                RateLockUnlock.objects.filter(
                    id=lock_id,
                    comp_id=company_id
                ).update(
                    lock_unlock=0,  # 0 = Unlocked
                    locked_by_transaction=request.user.username,
                    lock_date=datetime.now().strftime('%d-%m-%Y'),
                    lock_time=datetime.now().strftime('%H:%M:%S')
                )
                messages.success(request, 'Rate unlocked successfully')

        # Redirect back with search parameters
        query_params = request.GET.urlencode()
        redirect_url = reverse_lazy('material_management:rate_lock_unlock_list')
        if query_params:
            redirect_url = f"{redirect_url}?{query_params}"

        return redirect(redirect_url)


class RateLockUnlockToggleView(MaterialManagementBaseMixin, DetailView):
    """Toggle Rate Lock Status"""
    model = RateLockUnlock

    def post(self, request, *args, **kwargs):
        rate_lock = self.get_object()
        # Toggle lock status
        new_lock_value = 0 if rate_lock.lock_unlock == 1 else 1
        rate_lock.lock_unlock = new_lock_value

        if new_lock_value == 1:
            rate_lock.lock_date = datetime.now().strftime('%Y-%m-%d')
            rate_lock.lock_time = datetime.now().strftime('%I:%M:%S %p')
            rate_lock.locked_by_transaction = request.session.session_key or 'system'
        else:
            rate_lock.lock_date = None
            rate_lock.lock_time = None
            rate_lock.locked_by_transaction = None

        rate_lock.save()

        status = 'locked' if new_lock_value == 1 else 'unlocked'
        messages.success(request, f'Rate {status} successfully!')
        return HttpResponse(status=200)


class RateLockUnlockReportView(MaterialManagementBaseMixin, ListView):
    """
    Rate Lock/Unlock Report View
    Shows history of lock/unlock actions

    Converted from: aaspnet/Module/MaterialManagement/Reports/RateLockUnlock.aspx
    """
    model = RateLockUnlock
    template_name = 'material_management/rate_lock_unlock/report.html'
    context_object_name = 'records'
    paginate_by = 50

    def get_queryset(self):
        """Get lock/unlock records based on filters"""
        from design.models import TbldgItemMaster

        company_id = self.get_compid()

        queryset = RateLockUnlock.objects.filter(
            comp_id=company_id
        ).select_related()

        # Get filter parameters
        search_type = self.request.GET.get('type', '')
        category_id = self.request.GET.get('category', '')
        search_field = self.request.GET.get('search_field', '')
        search_text = self.request.GET.get('search_text', '')
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        locked_by = self.request.GET.get('locked_by', '')

        # Filter by date range
        if from_date:
            queryset = queryset.filter(sys_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(sys_date__lte=to_date)

        # Filter by locked by user
        if locked_by:
            queryset = queryset.filter(session_id__icontains=locked_by)

        # Filter by item (via category or search)
        if search_type == 'Category' and category_id:
            item_ids = TbldgItemMaster.objects.filter(
                cid=category_id,
                compid=company_id
            ).values_list('id', flat=True)
            queryset = queryset.filter(item_id__in=item_ids)

        if search_field and search_text:
            if search_field == 'ItemCode':
                item_ids = TbldgItemMaster.objects.filter(
                    itemcode__icontains=search_text,
                    compid=company_id
                ).values_list('id', flat=True)
                queryset = queryset.filter(item_id__in=item_ids)
            elif search_field == 'Description':
                item_ids = TbldgItemMaster.objects.filter(
                    manfdesc__icontains=search_text,
                    compid=company_id
                ).values_list('id', flat=True)
                queryset = queryset.filter(item_id__in=item_ids)

        return queryset.order_by('-sys_date', '-sys_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from design.models import TbldgCategoryMaster

        company_id = self.get_compid()

        # Get categories for dropdown
        context['categories'] = TbldgCategoryMaster.objects.filter(
            compid=company_id
        ).order_by('symbol')

        # Pass filter parameters
        context['search_type'] = self.request.GET.get('type', '')
        context['category_id'] = self.request.GET.get('category', '')
        context['search_field'] = self.request.GET.get('search_field', '')
        context['search_text'] = self.request.GET.get('search_text', '')
        context['from_date'] = self.request.GET.get('from_date', '')
        context['to_date'] = self.request.GET.get('to_date', '')
        context['locked_by'] = self.request.GET.get('locked_by', '')

        return context
