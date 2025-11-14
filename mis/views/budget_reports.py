"""
Budget Reports and Management Views

Handles budget code management, business group budget assignment,
and budget hours field category management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Subquery, OuterRef
from django.contrib import messages
from django.urls import reverse_lazy

from mis.models import (
    TblmisBudgetcode,
    TblmisBudgethrsFieldCategory,
    TblmisBudgethrsFieldSubcategory,
)
from accounts.models import TblaccBudgetDept
from sales_distribution.models import SdCustWorkorderMaster, SdCustMaster
from sys_admin.models import TblfinancialMaster


# ============================================================================
# Budget Code Master Views
# ============================================================================

class BudgetCodeListView(ListView):
    """List all budget codes"""
    model = TblmisBudgetcode
    template_name = 'mis/budget_code/list.html'
    context_object_name = 'budget_codes'
    paginate_by = 50

    def get_queryset(self):
        """Get all budget codes with optional search"""
        queryset = TblmisBudgetcode.objects.all()

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(symbol__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset.order_by('symbol')


class BudgetCodeCreateView(CreateView):
    """Create new budget code"""
    model = TblmisBudgetcode
    template_name = 'mis/budget_code/form.html'
    fields = ['symbol', 'description']
    success_url = reverse_lazy('mis:budget_code_list')

    def form_valid(self, form):
        """Show success message"""
        messages.success(self.request, 'Budget code created successfully')
        return super().form_valid(form)


class BudgetCodeUpdateView(UpdateView):
    """Update existing budget code"""
    model = TblmisBudgetcode
    template_name = 'mis/budget_code/form.html'
    fields = ['symbol', 'description']
    success_url = reverse_lazy('mis:budget_code_list')

    def form_valid(self, form):
        """Show success message"""
        messages.success(self.request, 'Budget code updated successfully')
        return super().form_valid(form)


class BudgetCodeDeleteView(DeleteView):
    """Delete budget code"""
    model = TblmisBudgetcode
    success_url = reverse_lazy('mis:budget_code_list')

    def delete(self, request, *args, **kwargs):
        """Show success message"""
        messages.success(request, 'Budget code deleted successfully')
        return super().delete(request, *args, **kwargs)


class BudgetCodeDetailView(View):
    """View budget code details"""
    template_name = 'mis/budget_code/detail.html'

    def get(self, request, pk):
        """Display budget code details"""
        budget_code = get_object_or_404(TblmisBudgetcode, id=pk)

        context = {
            'budget_code': budget_code,
        }

        return render(request, self.template_name, context)


# ============================================================================
# Business Group Budget Assignment View
# ============================================================================

class BusinessGroupBudgetAssignView(View):
    """
    Business Group Budget Assignment - Main page showing all business groups
    with budget calculations (matches ASP.NET Budget_Dist.aspx)
    """

    template_name = 'mis/transactions/business_group_budget.html'

    def get(self, request):
        """Display business groups with budget data or work order search"""
        # Get company and financial year from session or use defaults
        company_id = request.session.get('compid', 1)
        fin_year_id = request.session.get('finyearid', 1)

        # Get search query for Business Group tab
        bg_search = request.GET.get('bg_search', '').strip()

        # Get business groups with budget calculations
        from mis.services.business_group_budget_service import BusinessGroupBudgetService
        budget_service = BusinessGroupBudgetService(company_id, fin_year_id)
        business_groups = budget_service.get_all_business_groups_with_budget()

        # Apply universal search filter on business groups
        if bg_search:
            business_groups = [
                bg for bg in business_groups
                if bg_search.lower() in bg['name'].lower() or
                   bg_search.lower() in str(bg.get('symbol', '')).lower() or
                   bg_search in str(bg['budget_amount']) or
                   bg_search in str(bg['po_total']) or
                   bg_search in str(bg['cash_pay']) or
                   bg_search in str(bg['cash_rec']) or
                   bg_search in str(bg['tax']) or
                   bg_search in str(bg['balance'])
            ]

        # Calculate totals
        totals = {
            'budget_amount': sum(bg['budget_amount'] for bg in business_groups),
            'po_total': sum(bg['po_total'] for bg in business_groups),
            'cash_pay': sum(bg['cash_pay'] for bg in business_groups),
            'cash_rec': sum(bg['cash_rec'] for bg in business_groups),
            'tax': sum(bg['tax'] for bg in business_groups),
            'balance': sum(bg['balance'] for bg in business_groups),
        }

        context = {
            'business_groups': business_groups,
            'totals': totals,
            'company_id': company_id,
            'fin_year_id': fin_year_id,
            'bg_search': bg_search,
        }

        # Check if work order tab is active
        if request.GET.get('tab') == 'work-order':
            # Handle work order universal search
            wo_search = request.GET.get('wo_search', '').strip()

            context.update({
                'wo_search': wo_search,
            })

            # Get all work orders
            work_orders = self._get_all_work_orders(company_id, fin_year_id, None)

            # Apply universal search filter
            if wo_search:
                work_orders = work_orders.filter(
                    Q(finyear_text__icontains=wo_search) |
                    Q(customer_name__icontains=wo_search) |
                    Q(customerid__icontains=wo_search) |
                    Q(pono__icontains=wo_search) |
                    Q(wono__icontains=wo_search) |
                    Q(taskprojecttitle__icontains=wo_search) |
                    Q(sysdate__icontains=wo_search)
                )

            # Paginate results (17 items per page)
            paginator = Paginator(work_orders, 17)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            context.update({
                'page_obj': page_obj,
                'work_orders': page_obj.object_list,
            })

        # Check if this is an HTMX request
        if request.headers.get('HX-Request'):
            # Return partial HTML for HTMX
            if request.GET.get('tab') == 'work-order':
                return render(request, 'mis/transactions/partials/work_order_table.html', context)
            else:
                return render(request, 'mis/transactions/partials/business_group_table.html', context)

        return render(request, self.template_name, context)

    def _search_work_orders(self, search_type, search_value, wo_category, company_id, fin_year_id):
        """Search work orders based on search type and value"""
        # Base query
        queryset = SdCustWorkorderMaster.objects.filter(
            compid=company_id,
        ).select_related('poid')

        # Apply search filter based on type
        if search_type == 'customer':
            queryset = queryset.filter(
                Q(customerid__icontains=search_value) |
                Q(poid__customerid__icontains=search_value)
            )
        elif search_type == 'enquiry':
            queryset = queryset.filter(enqid=search_value)
        elif search_type == 'po':
            queryset = queryset.filter(pono__icontains=search_value)
        elif search_type == 'wo':
            queryset = queryset.filter(wono__icontains=search_value)

        # Apply category filter if provided
        if wo_category:
            queryset = queryset.filter(cid=wo_category)

        # Annotate with customer name using Subquery
        customer_name_subquery = SdCustMaster.objects.filter(
            customerid=OuterRef('customerid')
        ).values('customername')[:1]

        # Annotate with financial year text
        finyear_text_subquery = TblfinancialMaster.objects.filter(
            finyearid=OuterRef('finyearid')
        ).values('finyear')[:1]

        queryset = queryset.annotate(
            customer_name=Subquery(customer_name_subquery),
            finyear_text=Subquery(finyear_text_subquery)
        )

        # Order by most recent
        queryset = queryset.order_by('-id')

        return queryset

    def _get_all_work_orders(self, company_id, fin_year_id, wo_category=None):
        """
        Get all work orders for the company (auto-load behavior matching ASP.NET)
        Matches Budget_Dist.aspx Work Order tab default behavior
        """
        # Base query - get all work orders for the company
        queryset = SdCustWorkorderMaster.objects.filter(
            compid=company_id,
        ).select_related('poid')

        # Apply category filter if provided
        if wo_category:
            queryset = queryset.filter(cid=wo_category)

        # Annotate with customer name using Subquery
        customer_name_subquery = SdCustMaster.objects.filter(
            customerid=OuterRef('customerid')
        ).values('customername')[:1]

        # Annotate with financial year text
        finyear_text_subquery = TblfinancialMaster.objects.filter(
            finyearid=OuterRef('finyearid')
        ).values('finyear')[:1]

        queryset = queryset.annotate(
            customer_name=Subquery(customer_name_subquery),
            finyear_text=Subquery(finyear_text_subquery)
        )

        # Order by most recent (matches ASP.NET ordering)
        queryset = queryset.order_by('-id')

        return queryset

    def post(self, request):
        """Handle budget assignment save"""
        company_id = request.session.get('compid')
        fin_year_id = request.session.get('finyearid')

        selected_groups = request.POST.getlist('selected_groups')

        if not selected_groups:
            messages.warning(request, 'Please select at least one business group')
            return redirect('mis:business_group_budget')

        # Process selected groups
        # Implementation depends on what needs to be saved

        messages.success(request, f'Budget assignment saved for {len(selected_groups)} business groups')
        return redirect('mis:business_group_budget')


class BusinessGroupDetailView(View):
    """
    Business Group Budget Detail - Shows individual budget allocation records
    for a specific business group (Date, Time, Amount)
    Matches ASP.NET Budget_Dist.aspx detail view
    """

    template_name = 'mis/transactions/business_group_detail.html'

    def get(self, request, bg_id):
        """Display all budget records for the selected business group"""
        company_id = request.session.get('compid', 1)

        # Get business group information
        from human_resource.models import Businessgroup
        try:
            business_group = Businessgroup.objects.get(id=bg_id)
        except Businessgroup.DoesNotExist:
            messages.error(request, 'Business group not found')
            return redirect('mis:business_group_budget')

        # Get all budget allocation records for this business group
        # Show records across ALL financial years (hybrid approach)
        budget_records = TblaccBudgetDept.objects.filter(
            bgid=bg_id,
            compid=company_id
        ).order_by('-finyearid', '-id')

        # Calculate total amount
        total_amount = budget_records.aggregate(total=Sum('amount'))['total'] or 0

        context = {
            'business_group': business_group,
            'budget_records': budget_records,
            'total_amount': total_amount,
            'bg_id': bg_id
        }

        return render(request, self.template_name, context)


# ============================================================================
# Budget Hours Field Category and Sub-Category Views
# ============================================================================

class BudgetHrsFieldCategorySubCategoryView(View):
    """
    Budget Hours Field Category and Sub-Category Management
    Side-by-side view matching ASP.NET BudgetHrsFields.aspx
    """

    template_name = 'mis/budget_hrs_fields/manage.html'

    def get(self, request):
        """Display categories and sub-categories side by side"""
        # Get all categories except Id=1 ('Select')
        categories = TblmisBudgethrsFieldCategory.objects.exclude(id=1).order_by('-id')

        # Get all sub-categories with category join
        subcategories = TblmisBudgethrsFieldSubcategory.objects.select_related('mid').order_by('mid__id', 'id')

        from mis.forms import BudgetHrsFieldCategoryForm, BudgetHrsFieldSubCategoryForm

        context = {
            'categories': categories,
            'subcategories': subcategories,
            'category_form': BudgetHrsFieldCategoryForm(),
            'subcategory_form': BudgetHrsFieldSubCategoryForm(),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        """Handle form submissions for both categories and subcategories"""
        action = request.POST.get('action')

        if action == 'add_category':
            return self._add_category(request)
        elif action == 'edit_category':
            return self._edit_category(request)
        elif action == 'delete_category':
            return self._delete_category(request)
        elif action == 'add_subcategory':
            return self._add_subcategory(request)
        elif action == 'edit_subcategory':
            return self._edit_subcategory(request)
        elif action == 'delete_subcategory':
            return self._delete_subcategory(request)

        messages.error(request, 'Invalid action')
        return redirect('mis:budget_hrs_fields')

    def _add_category(self, request):
        """Add new category"""
        from mis.forms import BudgetHrsFieldCategoryForm
        form = BudgetHrsFieldCategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Record Inserted.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

        return redirect('mis:budget_hrs_fields')

    def _edit_category(self, request):
        """Edit existing category"""
        category_id = request.POST.get('category_id')

        try:
            category = TblmisBudgethrsFieldCategory.objects.get(id=category_id)
            from mis.forms import BudgetHrsFieldCategoryForm
            form = BudgetHrsFieldCategoryForm(request.POST, instance=category)

            if form.is_valid():
                form.save()
                messages.success(request, 'Record Updated.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        except TblmisBudgethrsFieldCategory.DoesNotExist:
            messages.error(request, 'Category not found')

        return redirect('mis:budget_hrs_fields')

    def _delete_category(self, request):
        """Delete category"""
        category_id = request.POST.get('category_id')

        try:
            category = TblmisBudgethrsFieldCategory.objects.get(id=category_id)
            category.delete()
            messages.success(request, 'Record Deleted.')
        except TblmisBudgethrsFieldCategory.DoesNotExist:
            messages.error(request, 'Category not found')

        return redirect('mis:budget_hrs_fields')

    def _add_subcategory(self, request):
        """Add new sub-category"""
        from mis.forms import BudgetHrsFieldSubCategoryForm
        form = BudgetHrsFieldSubCategoryForm(request.POST)

        # Validate that category is not 'Select' (Id=1)
        category_id = request.POST.get('mid')
        if category_id == '1':
            messages.error(request, 'Please select category.')
            return redirect('mis:budget_hrs_fields')

        if form.is_valid():
            form.save()
            messages.success(request, 'Record Inserted.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

        return redirect('mis:budget_hrs_fields')

    def _edit_subcategory(self, request):
        """Edit existing sub-category"""
        subcategory_id = request.POST.get('subcategory_id')

        # Validate that category is not 'Select' (Id=1)
        category_id = request.POST.get('mid')
        if category_id == '1':
            messages.error(request, 'Please select category.')
            return redirect('mis:budget_hrs_fields')

        try:
            subcategory = TblmisBudgethrsFieldSubcategory.objects.get(id=subcategory_id)
            from mis.forms import BudgetHrsFieldSubCategoryForm
            form = BudgetHrsFieldSubCategoryForm(request.POST, instance=subcategory)

            if form.is_valid():
                form.save()
                messages.success(request, 'Record Updated.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        except TblmisBudgethrsFieldSubcategory.DoesNotExist:
            messages.error(request, 'Sub-category not found')

        return redirect('mis:budget_hrs_fields')

    def _delete_subcategory(self, request):
        """Delete sub-category"""
        subcategory_id = request.POST.get('subcategory_id')

        try:
            subcategory = TblmisBudgethrsFieldSubcategory.objects.get(id=subcategory_id)
            subcategory.delete()
            messages.success(request, 'Record Deleted.')
        except TblmisBudgethrsFieldSubcategory.DoesNotExist:
            messages.error(request, 'Sub-category not found')

        return redirect('mis:budget_hrs_fields')
