"""
Work Order Search and Budget Allocation Views

Handles work order search, budget allocation, and work order budget detail.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from datetime import datetime
from decimal import Decimal

from sales_distribution.models import SdCustWorkorderMaster
from mis.models import TblaccBudgetWo
from mis.services.budget_service import BudgetCalculationService
from mis.services.wo_budget_service import WOBudgetService


class WorkOrderBudgetSearchView(View):
    """
    Work order search view for budget allocation
    Supports multiple search types: customer name, enquiry no, PO no, WO no
    """

    template_name = 'mis/transactions/wo_search.html'

    def get(self, request):
        """Display search form and results"""
        context = self._get_context(request)

        # Get search parameters
        search_type = request.GET.get('search_type', '')
        search_value = request.GET.get('search_value', '')
        wo_category = request.GET.get('wo_category', '')

        if search_value:
            # Perform search
            work_orders = self._search_work_orders(
                search_type, search_value, wo_category, request
            )

            # Paginate results (17 items per page as per requirements)
            paginator = Paginator(work_orders, 17)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            context.update({
                'search_type': search_type,
                'search_value': search_value,
                'wo_category': wo_category,
                'page_obj': page_obj,
                'work_orders': page_obj.object_list,
            })

        return render(request, self.template_name, context)

    def _get_context(self, request):
        """Get base context for the view"""
        return {
            'search_types': [
                ('customer', 'Customer Name'),
                ('enquiry', 'Enquiry No'),
                ('po', 'PO No'),
                ('wo', 'WO No'),
            ],
            'company_id': request.session.get('compid'),
            'fin_year_id': request.session.get('finyearid'),
        }

    def _search_work_orders(self, search_type, search_value, wo_category, request):
        """
        Search work orders based on search type and value

        Args:
            search_type: Type of search (customer, enquiry, po, wo)
            search_value: Search value
            wo_category: Work order category filter (optional)
            request: HTTP request object

        Returns:
            QuerySet of work orders
        """
        company_id = request.session.get('compid')
        fin_year_id = request.session.get('finyearid')

        # Base query
        queryset = SdCustWorkorderMaster.objects.filter(
            compid=company_id,
        ).select_related('poid')

        # Apply search filter based on type
        if search_type == 'customer':
            # Search by customer name
            queryset = queryset.filter(
                Q(customerid__icontains=search_value) |
                Q(poid__customerid__icontains=search_value)
            )
        elif search_type == 'enquiry':
            # Search by enquiry number
            queryset = queryset.filter(enqid=search_value)
        elif search_type == 'po':
            # Search by PO number
            queryset = queryset.filter(pono__icontains=search_value)
        elif search_type == 'wo':
            # Search by WO number
            queryset = queryset.filter(wono__icontains=search_value)

        # Apply category filter if provided
        if wo_category:
            queryset = queryset.filter(cid=wo_category)

        # Order by most recent
        queryset = queryset.order_by('-id')

        return queryset


class BudgetAllocationView(View):
    """
    Budget allocation view for a specific work order
    Displays all budget codes with calculations and allows budget entry
    """

    template_name = 'mis/transactions/budget_allocation.html'

    def get(self, request):
        """Display budget allocation page for a work order"""
        wo_no = request.GET.get('wo_no')

        if not wo_no:
            messages.error(request, 'Work order number is required')
            return redirect('mis:wo_search')

        # Get context
        company_id = request.session.get('compid')
        fin_year_id = request.session.get('finyearid')

        if not company_id or not fin_year_id:
            messages.error(request, 'Company and financial year context required')
            return redirect('mis:wo_search')

        # Get work order details
        try:
            work_order = SdCustWorkorderMaster.objects.get(
                wono=wo_no,
                compid=company_id
            )
        except SdCustWorkorderMaster.DoesNotExist:
            messages.error(request, f'Work order {wo_no} not found')
            return redirect('mis:wo_search')

        # Calculate budget summary
        budget_service = BudgetCalculationService(company_id, fin_year_id)
        summary_list = budget_service.get_budget_summary_for_wo(wo_no)
        totals = budget_service.get_budget_totals(summary_list)

        context = {
            'work_order': work_order,
            'wo_no': wo_no,
            'summary_list': summary_list,
            'totals': totals,
            'company_id': company_id,
            'fin_year_id': fin_year_id,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        """Handle budget allocation submission"""
        wo_no = request.POST.get('wo_no')
        selected_codes = request.POST.getlist('selected_codes')

        if not wo_no:
            messages.error(request, 'Work order number is required')
            return redirect('mis:wo_search')

        if not selected_codes:
            messages.error(request, 'Please select at least one budget code')
            return redirect(f'?wo_no={wo_no}')

        # Get context
        company_id = request.session.get('compid')
        fin_year_id = request.session.get('finyearid')
        session_id = request.session.session_key or 'default'

        try:
            saved_count = 0
            updated_count = 0

            for budget_code_id in selected_codes:
                amount_key = f'amount_{budget_code_id}'
                amount = request.POST.get(amount_key)

                if not amount:
                    continue

                try:
                    amount_decimal = Decimal(amount)
                    if amount_decimal < 0:
                        continue
                except (ValueError, TypeError):
                    continue

                # Check if allocation already exists
                existing = TblaccBudgetWo.objects.filter(
                    budget_code_id=budget_code_id,
                    wo_no=wo_no,
                    fin_year_id=fin_year_id,
                    comp_id=company_id
                ).first()

                if existing:
                    # Update existing allocation
                    existing.amount = amount_decimal
                    existing.sys_date = datetime.now().date()
                    existing.sys_time = datetime.now().time()
                    existing.session_id = session_id
                    existing.save()
                    updated_count += 1
                else:
                    # Create new allocation
                    TblaccBudgetWo.objects.create(
                        sys_date=datetime.now().date(),
                        sys_time=datetime.now().time(),
                        comp_id=company_id,
                        fin_year_id=fin_year_id,
                        session_id=session_id,
                        wo_no=wo_no,
                        budget_code_id_id=budget_code_id,
                        amount=amount_decimal
                    )
                    saved_count += 1

            if saved_count > 0 or updated_count > 0:
                msg = f'Budget allocation saved: {saved_count} new, {updated_count} updated'
                messages.success(request, msg)
            else:
                messages.warning(request, 'No valid budget allocations to save')

        except Exception as e:
            messages.error(request, f'Error saving budget allocation: {str(e)}')

        return redirect(f'?wo_no={wo_no}')


class WOBudgetDetailView(View):
    """
    Work Order Budget Detail - Shows budget codes for a specific work order
    (matches ASP.NET Budget_WONo.aspx)
    """

    template_name = 'mis/transactions/budget_wo_detail.html'

    def get(self, request, wo_no):
        """Display budget codes with data for the work order"""
        # Get company from session or use default
        company_id = request.session.get('compid', 1)
        session_fin_year_id = request.session.get('finyearid', 1)

        # Get work order details - HYBRID APPROACH
        # Try to find in current financial year first, then search all years
        work_order = None
        fin_year_id = session_fin_year_id

        try:
            # First attempt: Find in current session financial year
            work_order = SdCustWorkorderMaster.objects.get(
                wono=wo_no,
                compid=company_id,
                finyearid=session_fin_year_id
            )
        except SdCustWorkorderMaster.DoesNotExist:
            # Second attempt: Search across ALL financial years for this company
            work_orders = SdCustWorkorderMaster.objects.filter(
                wono=wo_no,
                compid=company_id
            ).order_by('-finyearid')  # Get most recent first

            if work_orders.exists():
                work_order = work_orders.first()
                fin_year_id = work_order.finyearid
                messages.info(request,
                    f'Work Order {wo_no} found in a different financial year. '
                    f'Showing data for that period.')
            else:
                messages.error(request, f'Work Order {wo_no} not found')
                return redirect('mis:business_group_budget')
        except SdCustWorkorderMaster.MultipleObjectsReturned:
            # If multiple in current year, just get the first one
            work_order = SdCustWorkorderMaster.objects.filter(
                wono=wo_no,
                compid=company_id,
                finyearid=session_fin_year_id
            ).first()

        # Get budget codes with calculations using the work order's actual financial year
        budget_service = WOBudgetService(company_id, fin_year_id, wo_no)
        budget_codes = budget_service.get_all_budget_codes_with_data()

        # Calculate totals
        totals = {
            'budget_amount': sum(code['budget_amount'] for code in budget_codes),
            'po_total': sum(code['po_total'] for code in budget_codes),
            'cash_pay': sum(code['cash_pay'] for code in budget_codes),
            'cash_rec': sum(code['cash_rec'] for code in budget_codes),
            'tax': sum(code['tax'] for code in budget_codes),
            'balance': sum(code['balance'] for code in budget_codes),
            'invoice': sum(code['invoice'] for code in budget_codes),
            'actual_amount': sum(code['actual_amount'] for code in budget_codes),
        }

        context = {
            'wo_no': wo_no,
            'work_order': work_order,
            'budget_codes': budget_codes,
            'totals': totals,
            'company_id': company_id,
            'fin_year_id': fin_year_id,
            'session_fin_year_id': session_fin_year_id,
            'is_different_year': fin_year_id != session_fin_year_id,
        }

        return render(request, self.template_name, context)

    def post(self, request, wo_no):
        """Handle budget code assignment save"""
        company_id = request.session.get('compid', 1)
        fin_year_id = request.session.get('finyearid', 1)
        session_id = request.user.username

        selected_codes = request.POST.getlist('selected_codes')

        if not selected_codes:
            messages.warning(request, 'Please select at least one budget code')
            return redirect('mis:wo_budget_detail', wo_no=wo_no)

        # Save budget allocations
        from django.utils import timezone

        saved_count = 0
        for code_id in selected_codes:
            amount_key = f'amount_{code_id}'
            amount = request.POST.get(amount_key)

            if amount and float(amount) > 0:
                TblaccBudgetWo.objects.create(
                    sys_date=timezone.now().date(),
                    sys_time=timezone.now().time(),
                    comp_id=company_id,
                    fin_year_id=fin_year_id,
                    session_id=session_id,
                    wo_no=wo_no,
                    budget_code_id=int(code_id),
                    amount=float(amount)
                )
                saved_count += 1

        messages.success(request, f'Budget saved for {saved_count} budget codes')
        return redirect('mis:wo_budget_detail', wo_no=wo_no)
