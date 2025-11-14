"""
Work Order views and management
"""

from django.views.generic import (
    CreateView, UpdateView, TemplateView, View, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q, F, Sum
from django.db import transaction
from datetime import datetime
from io import BytesIO

from ..models import (
    SdCustMaster, SdCustPoMaster, SdCustPoDetails,
    SdCustWorkorderMaster, SdCustWorkorderProductsDetails
)
from ..forms import WorkOrderForm
from sys_admin.models import (
    Tblcountry, Tblstate, Tblcity,
    TblfinancialMaster as FinancialYear,
    UnitMaster, TblgstMaster
)

class WorkOrderPoSearchView(LoginRequiredMixin, TemplateView):
    """
    Search and select a Customer PO for creating a Work Order.
    Exact mirror of ASP.NET WorkOrder_New.aspx logic.

    Business Logic (from ASP.NET):
    - Show POs from current and past financial years (FinYearId <= current)
    - Exclude POs that already have an OPEN work order (CloseOpen = 0)
    - Allow POs with NO work order or with CLOSED work orders only
    """
    template_name = 'sales_distribution/workorder_po_search.html'

    def get_context_data(self, **kwargs):
        from django.contrib.auth.models import User

        context = super().get_context_data(**kwargs)
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Get POs without open work orders (mirror of ASP.NET count == 0 logic)
        queryset = SdCustPoMaster.objects.filter(
            compid=compid,
            finyearid__lte=finyearid
        ).select_related('enqid').order_by('-poid')

        # Exclude POs that have an open work order
        open_wo_po_ids = SdCustWorkorderMaster.objects.filter(
            closeopen=0,
            compid=compid,
            finyearid__lte=finyearid
        ).values_list('poid', flat=True)

        queryset = queryset.exclude(poid__in=open_wo_po_ids)

        # Enrich with metadata (financial year, customer name, employee name)
        fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}
        user_dict = {str(user.id): user.username for user in User.objects.all()}
        customer_dict = {c.customerid: c.customername for c in SdCustMaster.objects.all()}

        pos = list(queryset[:20])
        for po in pos:
            po.finyear_name = fy_dict.get(po.finyearid, '-')
            if po.sessionid and po.sessionid.isdigit():
                po.generated_by = user_dict.get(po.sessionid, po.sessionid)
            else:
                po.generated_by = po.sessionid if po.sessionid else '-'
            po.customer_name = customer_dict.get(po.customerid, po.customerid)

        context['purchase_orders'] = pos
        return context


class WorkOrderPoSearchResultsView(LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint: Return search results for Customer POs.
    Exact mirror of ASP.NET WorkOrder_New.aspx search logic.

    Search Types:
    0 = Customer Name (autocomplete)
    1 = Enquiry No
    2 = PO No
    """
    template_name = 'sales_distribution/partials/workorder_po_search_results.html'

    def get_context_data(self, **kwargs):
        from django.contrib.auth.models import User

        context = super().get_context_data(**kwargs)
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        search_type = self.request.GET.get('search_type', '0')
        search_customer = self.request.GET.get('search-customer', '').strip()
        search_enq = self.request.GET.get('search-enq', '').strip()

        # Base queryset: POs from current and past years without open work orders
        queryset = SdCustPoMaster.objects.filter(
            compid=compid,
            finyearid__lte=finyearid
        ).select_related('enqid').order_by('-poid')

        # Exclude POs with open work orders
        open_wo_po_ids = SdCustWorkorderMaster.objects.filter(
            closeopen=0,
            compid=compid,
            finyearid__lte=finyearid
        ).values_list('poid', flat=True)

        queryset = queryset.exclude(poid__in=open_wo_po_ids)

        # Apply search filters based on search_type (mirror of ASP.NET DropDownList1_SelectedIndexChanged)
        if search_type == '0' and search_customer:
            # Customer Name search - extract customer ID from customer name or search directly
            customer_ids = SdCustMaster.objects.filter(
                customername__icontains=search_customer,
                compid=compid
            ).values_list('customerid', flat=True)
            queryset = queryset.filter(customerid__in=customer_ids)

        elif search_type == '1' and search_enq:
            # Enquiry No search
            queryset = queryset.filter(enqid=search_enq)

        elif search_type == '2' and search_enq:
            # PO No search
            queryset = queryset.filter(pono__icontains=search_enq)

        # Enrich with metadata (financial year, customer name, employee name)
        fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}
        user_dict = {str(user.id): user.username for user in User.objects.all()}
        customer_dict = {c.customerid: c.customername for c in SdCustMaster.objects.all()}

        pos = list(queryset[:20])
        for po in pos:
            po.finyear_name = fy_dict.get(po.finyearid, '-')
            if po.sessionid and po.sessionid.isdigit():
                po.generated_by = user_dict.get(po.sessionid, po.sessionid)
            else:
                po.generated_by = po.sessionid if po.sessionid else '-'
            po.customer_name = customer_dict.get(po.customerid, po.customerid)

        context['purchase_orders'] = pos
        return context


# ============================================================================
# WORK ORDER PRODUCTS HTMX ENDPOINTS (Tab 3)
# ============================================================================

class WorkOrderProductAddView(LoginRequiredMixin, View):
    """
    HTMX endpoint: Add product to session.
    Django approach using session storage instead of temp table.
    """
    def post(self, request):
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        session_key = f'workorder_products_{request.user.id}_{compid}_{finyearid}'

        itemcode = request.POST.get('itemcode', '').strip()
        description = request.POST.get('description', '').strip()
        qty = request.POST.get('qty', 0)

        if itemcode and description and qty:
            # Get existing products from session
            products = request.session.get(session_key, [])

            # Add new product with unique ID
            new_product = {
                'id': len(products) + 1,  # Simple incrementing ID for session
                'itemcode': itemcode,
                'description': description,
                'qty': float(qty)
            }
            products.append(new_product)

            # Save back to session
            request.session[session_key] = products
            request.session.modified = True

        # Return updated grid
        products = request.session.get(session_key, [])
        return render(request, 'sales_distribution/partials/workorder_products_grid.html', {'products': products})


class WorkOrderProductListView(LoginRequiredMixin, View):
    """
    HTMX endpoint: List products from session.
    Django approach using session storage.
    """
    def get(self, request):
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        session_key = f'workorder_products_{request.user.id}_{compid}_{finyearid}'

        products = request.session.get(session_key, [])
        return render(request, 'sales_distribution/partials/workorder_products_grid.html', {'products': products})


class WorkOrderProductEditView(LoginRequiredMixin, View):
    """
    HTMX endpoint: Edit product in session.
    Django approach using session storage.
    """
    def get(self, request, id):
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        session_key = f'workorder_products_{request.user.id}_{compid}_{finyearid}'

        products = request.session.get(session_key, [])
        product = next((p for p in products if p['id'] == id), None)

        if product:
            return render(request, 'sales_distribution/partials/workorder_product_edit_modal.html', {'product': product})
        else:
            return HttpResponse('<div class="text-red-600">Product not found</div>')

    def post(self, request, id):
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        session_key = f'workorder_products_{request.user.id}_{compid}_{finyearid}'

        products = request.session.get(session_key, [])

        # Find and update the product
        for product in products:
            if product['id'] == id:
                product['itemcode'] = request.POST.get('itemcode', product['itemcode'])
                product['description'] = request.POST.get('description', product['description'])
                product['qty'] = float(request.POST.get('qty', product['qty']))
                break

        # Save back to session
        request.session[session_key] = products
        request.session.modified = True

        # Return updated grid
        return render(request, 'sales_distribution/partials/workorder_products_grid.html', {'products': products})


class WorkOrderProductDeleteView(LoginRequiredMixin, View):
    """
    HTMX endpoint: Delete product from session.
    Django approach using session storage.
    """
    def post(self, request, id):
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        session_key = f'workorder_products_{request.user.id}_{compid}_{finyearid}'

        products = request.session.get(session_key, [])

        # Remove the product with matching ID
        products = [p for p in products if p['id'] != id]

        # Save back to session
        request.session[session_key] = products
        request.session.modified = True

        # Return updated grid
        return render(request, 'sales_distribution/partials/workorder_products_grid.html', {'products': products})


class WorkOrderStatesByCountryView(LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint: Return states dropdown for selected country in Work Order shipping.
    """
    template_name = 'sales_distribution/partials/workorder_state_dropdown.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get country from shipping section
        country_id = self.request.GET.get('shippingcountry')

        if country_id:
            try:
                country_id = int(country_id)
                context['states'] = Tblstate.objects.filter(cid=country_id).order_by('statename')
            except (ValueError, TypeError):
                context['states'] = Tblstate.objects.none()
        else:
            context['states'] = Tblstate.objects.none()

        return context


class WorkOrderCitiesByStateView(LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint: Return cities dropdown for selected state in Work Order shipping.
    """
    template_name = 'sales_distribution/partials/workorder_city_dropdown.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get state from shipping section
        state_id = self.request.GET.get('shippingstate')

        if state_id:
            try:
                state_id = int(state_id)
                context['cities'] = Tblcity.objects.filter(sid=state_id).order_by('cityname')
            except (ValueError, TypeError):
                context['cities'] = Tblcity.objects.none()
        else:
            context['cities'] = Tblcity.objects.none()

        return context


class WorkOrderView(LoginRequiredMixin, View):
    """
    Handles CRUD operations for Work Orders.
    """
    def get(self, request, id=None):
        if id:
            workorder = get_object_or_404(SdCustWorkorderMaster, id=id)
            products = SdCustWorkorderProductsDetails.objects.filter(mid=workorder.id)
            try:
                from design.models import TbldgBomMaster
                bom_count = TbldgBomMaster.objects.filter(wono=workorder.wono).count()
            except:
                bom_count = 0
            return render(request, 'sales_distribution/workorder_detail.html', {'workorder': workorder, 'products': products, 'bom_count': bom_count})
        else:
            from django.contrib.auth.models import User

            workorders = SdCustWorkorderMaster.objects.all().order_by('-id')
            search = request.GET.get('search', '')
            if search:
                workorders = workorders.filter(Q(wono__icontains=search) | Q(customerid__icontains=search))

            # Enrich workorders with metadata (financial year, customer name, employee name, WR number)
            fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}
            user_dict = {str(user.id): user.username for user in User.objects.all()}
            customer_dict = {c.customerid: c.customername for c in SdCustMaster.objects.all()}

            # Build WR number dictionary (latest release for each work order)
            # Get the latest release for each work order number
            wr_dict = {}
            from sales_distribution.models import SdCustWorkorderRelease
            for release in SdCustWorkorderRelease.objects.all().order_by('wono', '-id'):
                if release.wono and release.wono not in wr_dict:
                    wr_dict[release.wono] = release.wrno

            for wo in workorders:
                wo.finyear_name = fy_dict.get(wo.finyearid, '-')
                if wo.sessionid and wo.sessionid.isdigit():
                    wo.generated_by = user_dict.get(wo.sessionid, wo.sessionid)
                else:
                    wo.generated_by = wo.sessionid if wo.sessionid else '-'
                wo.customer_name = customer_dict.get(wo.customerid, wo.customerid)
                wo.wr_no = wr_dict.get(wo.wono, '-')

            return render(request, 'sales_distribution/workorder_list.html', {'workorders': workorders, 'search_query': search})




# WORK ORDER MANAGEMENT
# ============================================================================

class WorkOrderCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new Work Order from a selected Customer PO.
    Exact mirror of ASP.NET WorkOrder_New_Details.aspx Page_Load and Submit logic.
    """
    model = SdCustWorkorderMaster
    form_class = WorkOrderForm
    template_name = 'sales_distribution/workorder_form.html'
    success_url = reverse_lazy('sales_distribution:workorder-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po_id = self.kwargs.get('poid')
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        try:
            po = SdCustPoMaster.objects.select_related('enqid').get(poid=po_id)
            context['po'] = po
            context['enquiry'] = po.enqid
            context['line_items'] = SdCustPoDetails.objects.filter(poid=po).select_related('unit')

            # Django approach: Clear products from session (instead of temp table)
            # This ensures a clean slate when creating a new work order
            session_key = f'workorder_products_{self.request.user.id}_{compid}_{finyearid}'
            self.request.session[session_key] = []
            self.request.session.modified = True

        except SdCustPoMaster.DoesNotExist:
            messages.error(self.request, 'Purchase Order not found.')
            context['po'] = None

        return context

    def get_initial(self):
        """
        Pre-populate the form with data from the PO.
        Mirror of ASP.NET Page_Load field population.
        """
        initial = super().get_initial()
        po_id = self.kwargs.get('poid')

        try:
            po = SdCustPoMaster.objects.select_related('enqid').get(poid=po_id)
            initial['customerid'] = po.customerid
            initial['pono'] = po.pono
            initial['enqid'] = po.enqid_id if po.enqid else None

            # Set today's date for WO Date (mirror of ASP.NET)
            today = datetime.now()
            initial['taskworkorderdate'] = today.strftime('%d-%m-%Y')

        except SdCustPoMaster.DoesNotExist:
            pass

        return initial

    def form_valid(self, form):
        """
        Save Work Order and copy products from temp table.
        Exact mirror of ASP.NET Submit button logic.
        """
        print("\n" + "="*80)
        print("FORM_VALID() CALLED - VALIDATION PASSED!")
        print("="*80)

        try:
            po_id = self.request.POST.get('poid')
            print(f"PO ID: {po_id}")
            po = SdCustPoMaster.objects.get(poid=po_id)
            print(f"PO Found: {po.pono}")
            compid = self.request.session.get('compid', 1)
            finyearid = self.request.session.get('finyearid', 1)
            print(f"CompID: {compid}, FinYearID: {finyearid}")

            # Set system fields (mirror of ASP.NET)
            now = datetime.now()
            form.instance.sysdate = now.strftime('%d-%m-%Y')
            form.instance.systime = now.strftime('%H:%M:%S')
            form.instance.sessionid = str(self.request.user.id)
            form.instance.compid = compid
            form.instance.finyearid = finyearid
            form.instance.enqid = po.enqid_id
            form.instance.poid = po
            form.instance.closeopen = 0  # 0 = Open

            # Convert checkbox values to 1/0 (mirror of ASP.NET checkbox behavior)
            form.instance.instractionprimerpainting = 1 if form.cleaned_data.get('instractionprimerpainting') else 0
            form.instance.instractionpainting = 1 if form.cleaned_data.get('instractionpainting') else 0
            form.instance.instractionselfcertrept = 1 if form.cleaned_data.get('instractionselfcertrept') else 0

            # Generate Work Order Number based on Category
            # Mirror of ASP.NET: CategorySymbol + Sequential Number (e.g., DT0001, JF0023)
            category_id = form.cleaned_data.get('cid')
            subcategory_id = form.cleaned_data.get('scid')

            if category_id:
                try:
                    category = TblsdWoCategory.objects.get(cid=category_id)
                    category_symbol = category.symbol if category.symbol else 'WO'

                    # Find last WO number for this category+subcategory combination
                    last_wo = SdCustWorkorderMaster.objects.filter(
                        cid=category_id,
                        scid=subcategory_id,
                        compid=compid,
                        finyearid=finyearid
                    ).order_by('-id').first()

                    if last_wo and last_wo.wono:
                        # Extract number from WO number (e.g., "DT0023" → 23)
                        try:
                            last_num = int(last_wo.wono.replace(category_symbol, ''))
                            new_num = last_num + 1
                        except:
                            new_num = 1
                    else:
                        new_num = 1

                    form.instance.wono = f'{category_symbol}{new_num:04d}'

                except TblsdWoCategory.DoesNotExist:
                    # Fallback to simple WO numbering
                    form.instance.wono = f'WO{datetime.now().timestamp()}'
            else:
                form.instance.wono = f'WO{datetime.now().timestamp()}'

            # Save the Work Order Master
            print("Saving work order...")
            work_order = form.save()
            print(f"[SUCCESS] Work Order Saved!")
            print(f"  ID: {work_order.id}")
            print(f"  WO Number: {work_order.wono}")
            print(f"  Project Title: {work_order.taskprojecttitle}")

            # Django approach: Copy products from session to permanent table
            session_key = f'workorder_products_{self.request.user.id}_{compid}_{finyearid}'
            products_from_session = self.request.session.get(session_key, [])
            print(f"Products in session: {len(products_from_session)}")

            for product in products_from_session:
                SdCustWorkorderProductsDetails.objects.create(
                    mid=work_order.id,
                    sessionid=str(self.request.user.id),
                    compid=compid,
                    finyearid=finyearid,
                    itemcode=product.get('itemcode', ''),
                    description=product.get('description', ''),
                    qty=product.get('qty', 0)
                )
                print(f"  Product added: {product.get('itemcode')}")

            # Clean up session (Django approach instead of deleting from temp table)
            self.request.session[session_key] = []
            self.request.session.modified = True

            print(f"[SUCCESS] Redirecting to: {self.success_url}")
            print("="*80 + "\n")
            messages.success(self.request, f'Work order {work_order.wono} is generated.')
            return redirect(self.success_url)

        except SdCustPoMaster.DoesNotExist:
            print("[ERROR] Purchase Order not found.")
            messages.error(self.request, 'Purchase Order not found.')
            return self.form_invalid(form)
        except Exception as e:
            print(f"[ERROR] Exception in form_valid(): {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'Error creating Work Order: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Handle form validation errors with detailed logging.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.error("="*80)
        logger.error("WORK ORDER FORM VALIDATION FAILED")
        logger.error("="*80)
        logger.error(f"Form errors: {form.errors}")
        logger.error(f"Form non-field errors: {form.non_field_errors()}")

        # Log each field error
        for field, errors in form.errors.items():
            logger.error(f"Field '{field}': {errors}")

        # Print to console as well for immediate visibility
        print("\n" + "="*80)
        print("WORK ORDER FORM VALIDATION FAILED")
        print("="*80)
        print(f"Form errors: {form.errors}")
        print(f"Form non-field errors: {form.non_field_errors()}")
        for field, errors in form.errors.items():
            print(f"Field '{field}': {errors}")
        print("="*80 + "\n")

        messages.error(self.request, f'Form validation failed. Please check the highlighted fields.')
        return super().form_invalid(form)




class WorkOrderUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing Work Order.
    Uses the same form and template structure as WorkOrderCreateView.
    """
    model = SdCustWorkorderMaster
    form_class = WorkOrderForm
    template_name = 'sales_distribution/workorder_form.html'
    success_url = reverse_lazy('sales_distribution:workorder-list')
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        work_order = self.get_object()
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Get PO details for context
        if work_order.poid:
            context['po'] = work_order.poid
            context['enquiry'] = work_order.poid.enqid
            context['line_items'] = SdCustPoDetails.objects.filter(poid=work_order.poid).select_related('unit')
        else:
            context['po'] = None

        # Load existing products into session for editing
        session_key = f'workorder_products_{self.request.user.id}_{compid}_{finyearid}'

        # Check if we need to load products from DB (first GET request)
        if self.request.method == 'GET' and not self.request.session.get(session_key):
            existing_products = SdCustWorkorderProductsDetails.objects.filter(mid=work_order.id)
            products_list = []
            for idx, product in enumerate(existing_products, start=1):
                products_list.append({
                    'id': idx,
                    'itemcode': product.itemcode,
                    'description': product.description,
                    'qty': product.qty
                })
            self.request.session[session_key] = products_list
            self.request.session.modified = True

        context['is_edit'] = True
        context['work_order'] = work_order

        return context

    def get_form_kwargs(self):
        """Pass the work order instance to the form."""
        kwargs = super().get_form_kwargs()
        # The instance is automatically passed by UpdateView, but we ensure it's there
        return kwargs

    def get_initial(self):
        """Pre-populate form with existing work order data."""
        initial = super().get_initial()
        work_order = self.get_object()

        if work_order.poid:
            initial['customerid'] = work_order.customerid
            initial['pono'] = work_order.pono
            initial['enqid'] = work_order.enqid

        # Convert integer checkboxes back to boolean for form display
        initial['instractionprimerpainting'] = bool(work_order.instractionprimerpainting)
        initial['instractionpainting'] = bool(work_order.instractionpainting)
        initial['instractionselfcertrept'] = bool(work_order.instractionselfcertrept)

        return initial

    def form_valid(self, form):
        """Update Work Order and sync products."""
        try:
            compid = self.request.session.get('compid', 1)
            finyearid = self.request.session.get('finyearid', 1)

            # Update system fields
            now = datetime.now()
            form.instance.sysdate = now.strftime('%d-%m-%Y')
            form.instance.systime = now.strftime('%H:%M:%S')
            form.instance.sessionid = str(self.request.user.id)

            # Ensure compid and finyearid are preserved
            form.instance.compid = compid
            form.instance.finyearid = finyearid

            # Convert checkbox values to 1/0
            form.instance.instractionprimerpainting = 1 if form.cleaned_data.get('instractionprimerpainting') else 0
            form.instance.instractionpainting = 1 if form.cleaned_data.get('instractionpainting') else 0
            form.instance.instractionselfcertrept = 1 if form.cleaned_data.get('instractionselfcertrept') else 0

            # Save the Work Order Master
            work_order = form.save()

            # Sync products: Delete existing and create new from session
            SdCustWorkorderProductsDetails.objects.filter(mid=work_order.id).delete()

            session_key = f'workorder_products_{self.request.user.id}_{compid}_{finyearid}'
            products_from_session = self.request.session.get(session_key, [])

            for product in products_from_session:
                SdCustWorkorderProductsDetails.objects.create(
                    mid=work_order.id,
                    sessionid=str(self.request.user.id),
                    compid=compid,
                    finyearid=finyearid,
                    itemcode=product.get('itemcode', ''),
                    description=product.get('description', ''),
                    qty=product.get('qty', 0)
                )

            # Clean up session
            self.request.session[session_key] = []
            self.request.session.modified = True

            messages.success(self.request, f'Work order {work_order.wono} updated successfully.')
            return redirect(self.success_url)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error updating Work Order: {error_details}")
            messages.error(self.request, f'Error updating Work Order: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle form validation errors."""
        print(f"Form errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class WorkOrderCloseView(LoginRequiredMixin, View):
    """
    Close work order.
    
    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_close.aspx
    Requirements: 3.11
    """

    def post(self, request, id):
        from ..services import WorkOrderService

        try:
            result = WorkOrderService.close_work_order(id)
            messages.success(request, result['message'])
        except ValidationError as e:
            messages.error(request, str(e))

        # Check if request came from close-open list page
        # Use both from_list parameter AND referer URL as fallback
        from_list = request.POST.get('from_list')
        referer = request.META.get('HTTP_REFERER', '')

        if from_list or 'close-open' in referer:
            return redirect('sales_distribution:workorder-close-open-page')

        # Otherwise redirect back to detail page
        return redirect('sales_distribution:workorder-detail', id=id)


class WorkOrderOpenView(LoginRequiredMixin, View):
    """
    Open (reopen) a closed work order.
    
    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_close.aspx
    Spec: .kiro/specs/wo-open-close/requirements.md
    """

    def post(self, request, id):
        from ..services import WorkOrderService

        try:
            result = WorkOrderService.open_work_order(id)
            messages.success(request, result['message'])
        except ValidationError as e:
            messages.error(request, str(e))

        # Check if request came from close-open list page
        # Use both from_list parameter AND referer URL as fallback
        from_list = request.POST.get('from_list')
        referer = request.META.get('HTTP_REFERER', '')

        if from_list or 'close-open' in referer:
            return redirect('sales_distribution:workorder-close-open-page')

        # Otherwise redirect back to detail page
        return redirect('sales_distribution:workorder-detail', id=id)


class WorkOrderCloseOpenPageView(LoginRequiredMixin, View):
    """
    Work Order - Open/Close page
    Shows searchable list of work orders with close/open actions.

    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_close.aspx
    """

    def get(self, request):
        # Get search parameters
        search_type = request.GET.get('search_type', '')
        search_value = request.GET.get('search_value', '')

        # Start with all work orders
        workorders = SdCustWorkorderMaster.objects.all().order_by('-id')

        # Apply search filter if provided
        if search_type and search_value:
            if search_type == '0':  # Customer Name
                customer_ids = SdCustMaster.objects.filter(
                    customername__icontains=search_value
                ).values_list('customerid', flat=True)
                workorders = workorders.filter(customerid__in=customer_ids)
            elif search_type == '1':  # Enquiry No
                workorders = workorders.filter(enqid__icontains=search_value)
            elif search_type == '2':  # PO No
                workorders = workorders.filter(pono__icontains=search_value)
            elif search_type == '3':  # WO No
                workorders = workorders.filter(wono__icontains=search_value)

        # Enrich with related data
        fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}
        user_dict = {str(user.id): user.username for user in User.objects.all()}
        customer_dict = {c.customerid: c.customername for c in SdCustMaster.objects.all()}

        for wo in workorders:
            wo.finyear_name = fy_dict.get(wo.finyearid, '-')
            wo.customer_name = customer_dict.get(wo.customerid, wo.customerid)
            if wo.sessionid and wo.sessionid.isdigit():
                wo.generated_by = user_dict.get(wo.sessionid, wo.sessionid)
            else:
                wo.generated_by = wo.sessionid if wo.sessionid else '-'
            wo.status_text = 'Open' if wo.closeopen == 0 else 'Closed'

        context = {
            'workorders': workorders,
            'search_type': search_type,
            'search_value': search_value,
        }

        # Return partial template for HTMX requests
        if request.headers.get('HX-Request'):
            return render(request, 'sales_distribution/partials/workorder_close_open_table.html', context)

        return render(request, 'sales_distribution/workorder_close_open.html', context)




class WorkOrderPrintView(LoginRequiredMixin, DetailView):
    """
    Generate professional PDF for Work Order.
    Converted from: D:/inetpub/NewERP/Module/SalesDistribution/Transactions/WorkOrder_Print_Details.aspx

    Note: Uses xhtml2pdf instead of Crystal Reports for Windows compatibility
    """
    model = SdCustWorkorderMaster
    pk_url_kwarg = 'id'
    template_name = 'sales_distribution/workorder_print_pdf.html'

    def get_context_data(self, **kwargs):
        from django.conf import settings

        context = super().get_context_data(**kwargs)
        workorder = self.get_object()

        # Get work order products
        products = SdCustWorkorderProductsDetails.objects.filter(mid=workorder.id)

        # Get customer info
        customer = None
        try:
            customer = SdCustMaster.objects.get(customerid=workorder.customerid)
        except SdCustMaster.DoesNotExist:
            pass

        # Get WO category and subcategory
        category_name = None
        subcategory_name = None
        if workorder.cid:
            try:
                category = TblsdWoCategory.objects.get(cid=workorder.cid)
                category_name = category.cname
            except TblsdWoCategory.DoesNotExist:
                pass

        if workorder.scid:
            try:
                subcategory = TblsdWoSubcategory.objects.get(scid=workorder.scid)
                subcategory_name = subcategory.scname
            except TblsdWoSubcategory.DoesNotExist:
                pass

        # Get financial year
        finyear_name = None
        try:
            finyear = FinancialYear.objects.get(pk=workorder.finyearid)
            finyear_name = finyear.finyear
        except FinancialYear.DoesNotExist:
            finyear_name = str(workorder.finyearid)

        # Get employee name
        employee_name = None
        try:
            user = User.objects.get(pk=int(workorder.sessionid))
            employee_name = user.username
        except (User.DoesNotExist, ValueError):
            employee_name = workorder.sessionid

        context.update({
            'workorder': workorder,
            'products': products,
            'customer': customer,
            'category_name': category_name,
            'subcategory_name': subcategory_name,
            'finyear_name': finyear_name,
            'employee_name': employee_name,
            'company_name': 'Synergytech Automation Pvt. Ltd.',
            'company_address': 'Pune, Maharashtra, India',
            'company_phone': '+91-XXX-XXXXXXX',
            'company_email': 'sales@synergytechs.com',
            'company_website': 'www.synergytechs.com',
        })

        return context

    def render_to_response(self, context, **response_kwargs):
        """Render as PDF using xhtml2pdf"""
        from xhtml2pdf import pisa
        from django.template.loader import render_to_string
        from io import BytesIO

        # Render HTML template
        html_string = render_to_string(self.template_name, context)

        # Generate PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

        if pdf.err:
            return HttpResponse(f'Error generating PDF: {pdf.err}', content_type='text/html')

        # Return as PDF response
        wo_no = context['workorder'].wono if context['workorder'].wono else f'WO_{context["workorder"].id}'
        filename = f'Work_Order_{wo_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response



