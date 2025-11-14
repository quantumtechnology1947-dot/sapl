"""
Work Order Release and Dispatch views
"""

from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, F, Sum
from django.db import transaction
from datetime import datetime

from ..models import (
    SdCustMaster,
    SdCustWorkorderMaster, SdCustWorkorderProductsDetails,
    SdCustWorkorderRelease, SdCustWorkorderDispatch
)
from ..forms import WorkOrderReleaseForm, WorkOrderDispatchForm
from ..services import WorkOrderReleaseService
from .base import FinancialYearUserMixin
from sys_admin.models import TblfinancialMaster as FinancialYear
from human_resource.models import TblhrOfficestaff


# ============================================================================
# WORK ORDER DISPATCH - Correct Workflow
# ============================================================================

class WorkOrderDispatchListView(LoginRequiredMixin, ListView):
    """
    Work Order Dispatch List View - Shows Work Releases (WR) ready for dispatch.

    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Dispatch.aspx

    Workflow:
    1. List shows Work Releases (WR), NOT Work Orders
    2. Search by: Customer Name (0), WO No (1), or WR No (2)
    3. Grid columns: SN, Fin Yrs, Customer Name, Code, WR No (link), WO No
    4. Click on WR No to go to dispatch details page
    """
    model = SdCustWorkorderRelease
    template_name = 'sales_distribution/dispatch_list.html'
    context_object_name = 'work_releases'
    paginate_by = 20

    def get_queryset(self):
        """Get work releases with search filtering."""
        queryset = SdCustWorkorderRelease.objects.all().order_by('-id')

        # Get search parameters
        search_type = self.request.GET.get('search_type', 'Select')
        search_value = self.request.GET.get('search_value', '').strip()

        if search_value and search_type != 'Select':
            if search_type == '0':  # Customer Name
                queryset = queryset.filter(
                    wono__in=SdCustWorkorderMaster.objects.filter(
                        customerid__in=SdCustMaster.objects.filter(
                            customername__icontains=search_value
                        ).values('customerid')
                    ).values('wono')
                )
            elif search_type == '1':  # WO No
                queryset = queryset.filter(wono__icontains=search_value)
            elif search_type == '2':  # WR No
                queryset = queryset.filter(wrno__icontains=search_value)

        return queryset

    def get_context_data(self, **kwargs):
        """Add metadata to work releases."""
        context = super().get_context_data(**kwargs)

        # Get dictionaries for enrichment
        fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}
        wo_dict = {}
        for wo in SdCustWorkorderMaster.objects.all():
            wo_dict[wo.wono] = {
                'customerid': wo.customerid,
                'finyearid': wo.finyearid,
            }

        customer_dict = {c.customerid: c.customername for c in SdCustMaster.objects.all()}

        # Enrich work releases
        work_releases = list(context['work_releases'])
        for wr in work_releases:
            wo_data = wo_dict.get(wr.wono, {})
            wr.finyear_name = fy_dict.get(wo_data.get('finyearid'), '-')
            wr.customerid = wo_data.get('customerid', '-')
            wr.customer_name = customer_dict.get(wr.customerid, wr.customerid if wr.customerid else '-')

        context['work_releases'] = work_releases
        context['search_type'] = self.request.GET.get('search_type', 'Select')
        context['search_value'] = self.request.GET.get('search_value', '')
        context['search_types'] = [
            ('Select', 'Select'),
            ('0', 'Customer Name'),
            ('1', 'WO No'),
            ('2', 'WR No'),
        ]

        return context


class WorkOrderDispatchDetailView(LoginRequiredMixin, View):
    """
    Work Order Dispatch Detail View - Shows items from selected WR for dispatch.

    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Dispatch_Details.aspx

    Workflow:
    1. Shows GridView of items from the Work Release (WR)
    2. Each row has: Checkbox, "To DA Qty" input, Item Code, Description, Qty, Released Qty, etc.
    3. User selects items and enters dispatch quantities
    4. Submit creates dispatch records

    URL Parameters:
    - WONo: Work Order Number
    - WRNo: Work Release Number
    """
    template_name = 'sales_distribution/dispatch_detail.html'

    def get(self, request, wono, wrno):
        """Display work release items ready for dispatch."""
        # Get Work Order
        work_order = get_object_or_404(SdCustWorkorderMaster, wono=wono)

        # Verify work release exists (can be multiple records, one per item)
        if not SdCustWorkorderRelease.objects.filter(wono=wono, wrno=wrno).exists():
            messages.error(request, f'Work Release {wrno} not found for Work Order {wono}')
            return redirect('sales_distribution:dispatch-list')

        # Get products from work order (mid = master id)
        products = SdCustWorkorderProductsDetails.objects.filter(mid=work_order.id).order_by('id')

        # Get customer details
        customer = SdCustMaster.objects.filter(customerid=work_order.customerid).first()

        # Calculate released and remaining quantities
        for product in products:
            # Get total released quantity for this product (from all releases)
            # ItemId in release table stores the product's ID, not itemcode
            released_qty = SdCustWorkorderRelease.objects.filter(
                wono=wono,
                itemid=str(product.id)
            ).aggregate(total=Sum('issuedqty'))['total'] or 0

            # Get already dispatched quantity from this specific release
            dispatched_qty = SdCustWorkorderDispatch.objects.filter(
                wrno=wrno,
                itemid=str(product.id)
            ).aggregate(total=Sum('dispatchqty'))['total'] or 0

            product.released_qty = released_qty
            product.dispatched_qty = dispatched_qty
            product.remain_qty = product.qty - released_qty if product.qty else 0
            product.available_for_dispatch = released_qty - dispatched_qty

        context = {
            'work_order': work_order,
            'products': products,
            'customer': customer,
            'wono': wono,
            'wrno': wrno,
        }

        return render(request, self.template_name, context)

    def post(self, request, wono, wrno):
        """Process dispatch form submission."""
        work_order = get_object_or_404(SdCustWorkorderMaster, wono=wono)

        # Verify work release exists
        if not SdCustWorkorderRelease.objects.filter(wono=wono, wrno=wrno).exists():
            messages.error(request, f'Work Release {wrno} not found for Work Order {wono}')
            return redirect('sales_distribution:dispatch-list')

        # Get form data
        selected_items = request.POST.getlist('selected_items')

        if not selected_items:
            messages.error(request, 'Please select at least one item to dispatch.')
            return redirect('sales_distribution:dispatch-detail', wono=wono, wrno=wrno)

        try:
            with transaction.atomic():
                # Get dispatch number (DA No) - generate based on existing pattern
                last_dispatch = SdCustWorkorderDispatch.objects.filter(
                    compid=request.session.get('compid', 1),
                    finyearid=request.session.get('finyearid', 1)
                ).order_by('-id').first()

                if last_dispatch and last_dispatch.dano:
                    # Extract number from DA/YYYY-YY/XXXX format
                    parts = last_dispatch.dano.split('/')
                    if len(parts) == 3:
                        last_num = int(parts[2])
                        new_num = last_num + 1
                    else:
                        new_num = 1
                else:
                    new_num = 1

                # Get financial year for DA number
                finyear = FinancialYear.objects.filter(
                    finyearid=request.session.get('finyearid', 1)
                ).first()
                finyear_str = finyear.finyear if finyear else '2024-25'

                dano = f"DA/{finyear_str}/{new_num:04d}"

                # Common fields
                now = datetime.now()
                sysdate = now.strftime('%d-%m-%Y')
                systime = now.strftime('%H:%M:%S')
                sessionid = str(request.user.id)
                compid = request.session.get('compid', 1)
                finyearid = request.session.get('finyearid', 1)

                # Create dispatch records for each selected item
                for item_id in selected_items:
                    da_qty = request.POST.get(f'da_qty_{item_id}', '').strip()

                    if not da_qty or float(da_qty) <= 0:
                        continue

                    product = SdCustWorkorderProductsDetails.objects.filter(
                        id=item_id,
                        mid=work_order.id
                    ).first()

                    if not product:
                        continue

                    # Get the work release record for this item
                    release_record = SdCustWorkorderRelease.objects.filter(
                        wono=wono,
                        wrno=wrno,
                        itemid=str(product.id)
                    ).first()

                    # Create dispatch record
                    dispatch = SdCustWorkorderDispatch(
                        dano=dano,
                        wrno=wrno,
                        wrid=str(release_record.id) if release_record else '',  # Work Release ID
                        itemid=str(product.id),  # ItemId field references product ID
                        dispatchqty=float(da_qty),  # Dispatch quantity
                        sysdate=sysdate,
                        systime=systime,
                        sessionid=sessionid,
                        compid=compid,
                        finyearid=finyearid,
                    )
                    dispatch.save()

                messages.success(request, f'Dispatch {dano} created successfully for WR No: {wrno}')
                return redirect('sales_distribution:dispatch-list')

        except Exception as e:
            messages.error(request, f'Error creating dispatch: {str(e)}')
            return redirect('sales_distribution:dispatch-detail', wono=wono, wrno=wrno)


# Legacy view for backward compatibility
class WorkOrderDispatchView(WorkOrderDispatchListView):
    """Legacy view - redirects to new dispatch list."""
    pass


class WorkOrderDispatchPrintView(LoginRequiredMixin, DetailView):
    """
    Print dispatch advice.
    """
    model = SdCustWorkorderDispatch
    template_name = 'sales_distribution/dispatch_print.html'
    context_object_name = 'dispatch'


# ============================================================================
# WORK ORDER RELEASE
# ============================================================================

class WorkOrderReleaseListView(LoginRequiredMixin, FinancialYearUserMixin, ListView):
    """
    Work Order Release List View - Shows all work orders available for release.

    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Release.aspx
    Features:
    - Search by Customer Name, Enquiry No, PO No, WO No
    - 9 columns: SN, Fin Yrs, CustomerName, Code, Enquiry No, PO No, WO No, Gen. Date, Gen. By
    - Pagination (20 items per page)
    - Click on WO No to go to release detail page
    """
    model = SdCustWorkorderMaster
    template_name = 'sales_distribution/wo_release/list.html'
    context_object_name = 'work_orders'
    paginate_by = 20

    def get_queryset(self):
        """Get work orders with search filtering."""
        compid = None
        finyearid = None

        # Get search parameters
        search_term = self.request.GET.get('search', '').strip()
        search_field = self.request.GET.get('search_field', 'CustomerName')

        # Get work orders using service layer
        queryset = WorkOrderReleaseService.get_releaseable_work_orders(
            compid=compid,
            finyearid=finyearid,
            search_term=search_term,
            search_field=search_field
        )

        return queryset

    def get_context_data(self, **kwargs):
        """Add metadata and search context."""
        context = super().get_context_data(**kwargs)

        # Enrich with financial year and user data
        work_orders = list(context['work_orders'])
        self.enrich_with_metadata(work_orders)
        context['work_orders'] = work_orders

        # Add search parameters
        context['search'] = self.request.GET.get('search', '')
        context['search_field'] = self.request.GET.get('search_field', 'CustomerName')
        context['search_fields'] = [
            ('CustomerName', 'Customer Name'),
            ('EnquiryNo', 'Enquiry No'),
            ('PONo', 'PO No'),
            ('WONo', 'WO No')
        ]

        return context


class WorkOrderReleaseDetailView(LoginRequiredMixin, DetailView):
    """
    Work Order Release Detail/Submit View - Shows work order details and release form.

    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_ReleaseRPT.aspx
    Features:
    - GridView 1: Products with checkboxes, To Release Qty input, Item Code, Description, Qty, Released Qty, Remain Qty
    - GridView 2: Email recipients (HR staff with WR=1 permission)
    - Submit button to process release
    """
    model = SdCustWorkorderMaster
    template_name = 'sales_distribution/wo_release/detail.html'
    context_object_name = 'work_order'
    pk_url_kwarg = 'wo_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        work_order = self.object

        # Get customer
        customer = SdCustMaster.objects.filter(customerid=work_order.customerid).first()

        # Add work order header info
        context['wo_no'] = work_order.wono
        context['customer_name'] = customer.customername if customer else '-'
        context['enquiry_no'] = work_order.enqid if hasattr(work_order, 'enqid') and work_order.enqid else '-'
        context['po_no'] = work_order.pono if hasattr(work_order, 'pono') and work_order.pono else '-'
        context['customer'] = customer

        # Get products for this work order (mid = master id)
        products = SdCustWorkorderProductsDetails.objects.filter(mid=work_order.id)

        # Calculate released and remaining quantities for each product
        for product in products:
            # ItemId in release table stores the product's ID, not itemcode
            released_qty = SdCustWorkorderRelease.objects.filter(
                wono=work_order.wono,
                itemid=str(product.id)
            ).aggregate(total=Sum('issuedqty'))['total'] or 0

            product.released_qty = released_qty
            product.remain_qty = (product.qty or 0) - released_qty
            product.show_controls = product.remain_qty > 0  # Only show controls if quantity remaining

        context['products'] = products

        # Get eligible employees for email notifications (HR staff with WR=1 permission)
        context['eligible_employees'] = TblhrOfficestaff.objects.filter(wr='1').order_by('employeename')

        # Get release history for this work order
        context['release_history'] = SdCustWorkorderRelease.objects.filter(
            wono=work_order.wono
        ).order_by('-id')[:10]  # Last 10 releases

        return context


class WorkOrderReleaseSubmitView(LoginRequiredMixin, View):
    """
    Submit Work Order Release - Process release form submission.

    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_ReleaseRPT.aspx

    Logic:
    1. Generate WR number in format: WR/YYYY-YY/XXXX
    2. Create SdCustWorkorderRelease records for each product with quantity > 0
    3. Send email notifications to selected employees (TODO)
    """
    def post(self, request, wo_id):
        # Get work order
        work_order = get_object_or_404(SdCustWorkorderMaster, id=wo_id)

        # Get form data
        product_ids = request.POST.getlist('product_id[]')
        release_qtys = request.POST.getlist('to_release_qty[]')
        item_codes = request.POST.getlist('item_code[]')

        # Validate - check if at least one product has quantity > 0
        has_releases = False
        for qty in release_qtys:
            try:
                if float(qty) > 0:
                    has_releases = True
                    break
            except (ValueError, TypeError):
                continue

        if not has_releases:
            messages.error(request, 'Please enter release quantities for at least one product.')
            return redirect('sales_distribution:wo-release-detail', wo_id=wo_id)

        try:
            with transaction.atomic():
                # Generate WR number
                compid = request.session.get('compid', 1)
                finyearid = request.session.get('finyearid', 1)

                # Get last WR number for this company/financial year
                last_release = SdCustWorkorderRelease.objects.filter(
                    compid=compid,
                    finyearid=finyearid
                ).order_by('-id').first()

                if last_release and last_release.wrno:
                    # Extract number from WR/YYYY-YY/XXXX format
                    parts = last_release.wrno.split('/')
                    if len(parts) == 3:
                        try:
                            last_num = int(parts[2])
                            new_num = last_num + 1
                        except ValueError:
                            new_num = 1
                    else:
                        new_num = 1
                else:
                    new_num = 1

                # Get financial year for WR number
                finyear = FinancialYear.objects.filter(finyearid=finyearid).first()
                finyear_str = finyear.finyear if finyear else '2025-26'

                wrno = f"WR/{finyear_str}/{new_num:04d}"

                # Audit fields
                now = datetime.now()
                sysdate = now.strftime('%d-%m-%Y')
                systime = now.strftime('%H:%M:%S')
                sessionid = str(request.user.id)

                # Create release records
                releases_created = 0
                for i, product_id in enumerate(product_ids):
                    try:
                        release_qty = float(release_qtys[i])
                    except (ValueError, TypeError, IndexError):
                        continue

                    if release_qty <= 0:
                        continue

                    # Get product to verify it exists and get remaining quantity
                    try:
                        product = SdCustWorkorderProductsDetails.objects.get(
                            id=product_id,
                            mid=work_order.id
                        )
                    except SdCustWorkorderProductsDetails.DoesNotExist:
                        continue

                    # Verify release quantity doesn't exceed remaining quantity
                    released_qty = SdCustWorkorderRelease.objects.filter(
                        wono=work_order.wono,
                        itemid=str(product.id)
                    ).aggregate(total=Sum('issuedqty'))['total'] or 0

                    remain_qty = (product.qty or 0) - released_qty

                    if release_qty > remain_qty:
                        messages.warning(
                            request,
                            f'Release quantity for {product.itemcode} ({release_qty}) exceeds remaining quantity ({remain_qty}). Adjusted to {remain_qty}.'
                        )
                        release_qty = remain_qty

                    if release_qty <= 0:
                        continue

                    # Create release record
                    release = SdCustWorkorderRelease(
                        wrno=wrno,
                        wono=work_order.wono,
                        itemid=str(product.id),  # Store product ID, not itemcode
                        issuedqty=release_qty,
                        sysdate=sysdate,
                        systime=systime,
                        sessionid=sessionid,
                        compid=compid,
                        finyearid=finyearid,
                    )
                    release.save()
                    releases_created += 1

                if releases_created == 0:
                    messages.error(request, 'No valid releases could be created.')
                    return redirect('sales_distribution:wo-release-detail', wo_id=wo_id)

                # TODO: Send email notifications to selected employees
                # email_recipients = request.POST.getlist('email_recipients[]')

                messages.success(
                    request,
                    f'Work Order Release {wrno} created successfully for WO No: {work_order.wono}. {releases_created} product(s) released.'
                )
                return redirect('sales_distribution:wo-release-list')

        except Exception as e:
            messages.error(request, f'Error creating release: {str(e)}')
            return redirect('sales_distribution:wo-release-detail', wo_id=wo_id)
