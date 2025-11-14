"""
Budget Hours Assignment Views

These views handle the Budget Hours (Time) assignment workflow:
1. Search for Work Orders
2. Assign budget hours by equipment, category, and sub-category
3. View and manage budget hour allocations

Converted from ASP.NET:
- Budget_Dist_Time.aspx -> BudgetHoursAssignView
- Budget_Dist_WONo_Time.aspx -> BudgetHoursWorkOrderSearchView
- Budget_WONo_Time.aspx -> WOBudgetHoursDetailView
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from datetime import datetime

from sales_distribution.models import (
    SdCustWorkorderMaster,
    SdCustWorkorderProductsDetails,
    SdCustMaster,
)
from mis.models import (
    TblmisBudgethrsFieldCategory,
    TblmisBudgethrsFieldSubcategory,
    TblaccBudgetWoTime,
)
from mis.forms import BudgetHoursAssignmentForm


class BudgetHoursAssignView(View):
    """
    Budget Hours Assignment Main View
    Converted from: Budget_Dist_Time.aspx

    Shows two tabs:
    1. Business Group (currently not implemented)
    2. Work Order - Search and assign budget hours
    """
    template_name = 'mis/budget_hrs/assign.html'

    def get(self, request):
        """Display the Budget Hours Assignment page"""
        context = {
            'page_title': 'Assign Budget Hours',
        }
        return render(request, self.template_name, context)


class BudgetHoursWorkOrderSearchView(View):
    """
    Work Order Search for Budget Hours Assignment
    Converted from: Budget_Dist_WONo_Time.aspx

    Allows searching work orders by:
    - Customer Name
    - Enquiry No (disabled in ASP.NET)
    - PO No (disabled in ASP.NET)
    - WO No
    """
    template_name = 'mis/budget_hrs/wo_search.html'

    def get(self, request):
        """Display search form and results"""
        search_type = request.GET.get('search_type', '0')  # 0=Customer, 3=WO No
        search_value = request.GET.get('search_value', '')

        context = {
            'search_type': search_type,
            'search_value': search_value,
            'work_orders': [],
        }

        if search_value:
            work_orders = self._search_work_orders(search_type, search_value)
            context['work_orders'] = work_orders

        return render(request, self.template_name, context)

    def _search_work_orders(self, search_type, search_value):
        """Search work orders based on type and value"""
        queryset = SdCustWorkorderMaster.objects.select_related('customerid').all()

        if search_type == '0':  # Customer Name
            queryset = queryset.filter(
                customerid__customername__icontains=search_value
            )
        elif search_type == '3':  # WO No
            queryset = queryset.filter(wono__icontains=search_value)

        return queryset.order_by('-id')[:100]


class WOBudgetHoursDetailView(View):
    """
    Work Order Budget Hours Detail View
    Converted from: Budget_WONo_Time.aspx

    Shows and manages budget hour allocations for a specific work order.
    Users can:
    - Add budget hours by selecting Equipment, Category, Sub-Category, and Hours
    - View existing budget hour allocations
    - Edit/Delete existing allocations
    """
    template_name = 'mis/budget_hrs/wo_detail.html'

    def get(self, request, wo_no):
        """Display budget hours for a work order"""
        # Get work order
        work_order = get_object_or_404(SdCustWorkorderMaster, wono=wo_no)

        # Get equipment/products for this WO
        products = SdCustWorkorderProductsDetails.objects.filter(
            mid=work_order.id
        ).select_related()

        # Get existing budget hour allocations
        budget_hours = TblaccBudgetWoTime.objects.filter(
            wo_no=wo_no
        ).select_related()

        # Calculate totals and remaining hours
        allocated_data = self._calculate_allocations(wo_no, products, budget_hours)

        # Get categories for dropdown (exclude Id=1 'Select')
        categories = TblmisBudgethrsFieldCategory.objects.exclude(id=1).order_by('id')

        context = {
            'work_order': work_order,
            'wo_no': wo_no,
            'products': products,
            'budget_hours': budget_hours,
            'allocated_data': allocated_data,
            'categories': categories,
        }

        return render(request, self.template_name, context)

    def post(self, request, wo_no):
        """Handle budget hour assignment"""
        action = request.POST.get('action')

        if action == 'add':
            return self._add_budget_hours(request, wo_no)
        elif action == 'delete':
            return self._delete_budget_hours(request, wo_no)
        elif action == 'update':
            return self._update_budget_hours(request, wo_no)

        return redirect('mis:wo_budget_hours_detail', wo_no=wo_no)

    def _add_budget_hours(self, request, wo_no):
        """Add new budget hour allocation"""
        equip_id = request.POST.get('equip_id')
        category_id = request.POST.get('category_id')
        subcategory_id = request.POST.get('subcategory_id')
        hours = request.POST.get('hours')

        try:
            # Create budget hour record
            budget_hour = TblaccBudgetWoTime()
            budget_hour.comp_id = request.session.get('compid', 1)
            budget_hour.sys_date = datetime.now().strftime('%d-%m-%Y')
            budget_hour.sys_time = datetime.now().strftime('%H:%M:%S')
            budget_hour.session_id = str(request.user.id)
            budget_hour.fin_year_id = request.session.get('finyearid', 1)
            budget_hour.wo_no = wo_no
            budget_hour.equip_id = int(equip_id) if equip_id else None
            budget_hour.hrs_budget_cat = int(category_id) if category_id else None
            budget_hour.hrs_budget_sub_cat = int(subcategory_id) if subcategory_id else None
            budget_hour.hour = float(hours) if hours else 0
            budget_hour.save()

            messages.success(request, 'Budget hours added successfully.')
        except Exception as e:
            messages.error(request, f'Error adding budget hours: {str(e)}')

        return redirect('mis:wo_budget_hours_detail', wo_no=wo_no)

    def _delete_budget_hours(self, request, wo_no):
        """Delete budget hour allocation"""
        budget_id = request.POST.get('budget_id')

        try:
            budget_hour = TblaccBudgetWoTime.objects.get(id=budget_id, wo_no=wo_no)
            budget_hour.delete()
            messages.success(request, 'Budget hours deleted successfully.')
        except TblaccBudgetWoTime.DoesNotExist:
            messages.error(request, 'Budget hour record not found.')

        return redirect('mis:wo_budget_hours_detail', wo_no=wo_no)

    def _update_budget_hours(self, request, wo_no):
        """Update budget hour allocation"""
        budget_id = request.POST.get('budget_id')
        hours = request.POST.get('hours')

        try:
            budget_hour = TblaccBudgetWoTime.objects.get(id=budget_id, wo_no=wo_no)
            budget_hour.hour = float(hours) if hours else 0
            budget_hour.save()
            messages.success(request, 'Budget hours updated successfully.')
        except TblaccBudgetWoTime.DoesNotExist:
            messages.error(request, 'Budget hour record not found.')

        return redirect('mis:wo_budget_hours_detail', wo_no=wo_no)

    def _calculate_allocations(self, wo_no, products, budget_hours):
        """Calculate budget hour allocations and remaining hours"""
        allocated_data = []

        for product in products:
            # Get total allocated hours for this equipment
            product_hours = budget_hours.filter(equip_id=product.id)
            total_allocated = sum([bh.hour or 0 for bh in product_hours])

            allocated_data.append({
                'product': product,
                'total_allocated': total_allocated,
                'allocations': product_hours,
            })

        return allocated_data


class BudgetHoursSubCategoryAPIView(View):
    """
    AJAX/HTMX endpoint to get sub-categories for a selected category
    """
    def get(self, request):
        """Return sub-categories as JSON"""
        category_id = request.GET.get('category_id')

        if not category_id:
            return JsonResponse({'subcategories': []})

        subcategories = TblmisBudgethrsFieldSubcategory.objects.filter(
            mid_id=category_id
        ).values('id', 'subcategory', 'symbol')

        return JsonResponse({
            'subcategories': list(subcategories)
        })
