"""
Customer Purchase Order views and line items
"""

from django.views.generic import TemplateView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, F, Sum
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime
import io

from ..models import (
    SdCustMaster, SdCustEnquiryMaster, SdCustQuotationMaster,
    SdCustQuotationDetails, SdCustPoMaster, SdCustPoDetails
)
from ..forms import CustomerPoForm
from .base import FinancialYearUserMixin
from sys_admin.models import (
    TblfinancialMaster as FinancialYear,
    UnitMaster, TblgstMaster
)

class CustomerPoView(LoginRequiredMixin, View):
    """
    Handles CRUD operations for Customer Purchase Orders.
    """
    def get(self, request, poid=None):
        if poid:
            po = get_object_or_404(SdCustPoMaster, poid=poid)
            line_items = SdCustPoDetails.objects.filter(poid=po).select_related('unit')
            return render(request, 'sales_distribution/po_detail.html', {'po': po, 'line_items': line_items})
        else:
            from django.contrib.auth.models import User
            from core.mixins import paginate_queryset

            queryset = SdCustPoMaster.objects.select_related('enqid').all().order_by('-poid')
            search = request.GET.get('search', '')
            if search:
                queryset = SdCustPoMaster.objects.select_related('enqid').filter(
                    Q(pono__icontains=search) |
                    Q(customerid__icontains=search) |
                    Q(enqid__customername__icontains=search)
                ).order_by('-poid')

            # Paginate
            pagination = paginate_queryset(queryset, request, per_page=20)
            pos = pagination['page_obj']

            # Enrich POs with financial year and user info
            fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}

            for po in pos:
                po.finyear_name = fy_dict.get(po.finyearid, '-')
                # sessionid now stores username directly
                po.generated_by = po.sessionid if po.sessionid else '-'
                # Add customer name from enquiry if available
                if po.enqid:
                    po.customer_name = po.enqid.customername
                else:
                    po.customer_name = '-'

            context = {
                'pos': pos,
                'page_obj': pagination['page_obj'],
                'is_paginated': pagination['is_paginated'],
                'paginator': pagination['paginator'],
                'search_query': search
            }

            if request.headers.get('HX-Request'):
                return render(request, 'sales_distribution/partials/po_list_partial.html', context)
            return render(request, 'sales_distribution/po_list.html', context)

    def post(self, request):
        return redirect('sales_distribution:po-search')

    def delete(self, request, poid):
        po = get_object_or_404(SdCustPoMaster, poid=poid)
        if SdCustWorkorderMaster.objects.filter(poid=po).exists():
            messages.error(request, 'Cannot delete PO. Work orders exist for this PO.')
            return redirect('sales_distribution:po-list')
        SdCustPoDetails.objects.filter(poid=po).delete()
        pono = po.pono
        po.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        messages.success(request, f'PO {pono} deleted successfully.')
        return redirect('sales_distribution:po-list')


class CustomerPoSearchView(LoginRequiredMixin, FinancialYearUserMixin, TemplateView):
    """
    Full page view for searching enquiries to create POs.
    Shows all pending enquiries by default.
    """
    template_name = 'sales_distribution/po_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Show all pending enquiries by default (postatus=0 means no PO created yet)
        enquiries = list(SdCustEnquiryMaster.objects.filter(postatus=0).order_by('-enqid')[:50])
        
        # Enrich with metadata
        self.enrich_with_metadata(enquiries, include_quotation_count=False)
        
        context['enquiries'] = enquiries
        return context


class CustomerPoSearchResultsView(LoginRequiredMixin, FinancialYearUserMixin, TemplateView):
    """
    HTMX endpoint: Return search results for enquiries with universal search.
    Searches across enquiry ID, customer name, and customer code.
    """
    template_name = 'sales_distribution/partials/po_enquiry_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_value = self.request.GET.get('search_value', '').strip()

        if not search_value:
            context['enquiries'] = []
            return context

        # Universal search across multiple fields using Q objects
        queryset = SdCustEnquiryMaster.objects.filter(postatus=0).filter(
            Q(enqid__icontains=search_value) |
            Q(customername__icontains=search_value) |
            Q(customerid__icontains=search_value)
        )

        enquiries = list(queryset.order_by('-enqid')[:20])  # Limit to 20 results

        # Add metadata using mixin
        self.enrich_with_metadata(enquiries)

        context['enquiries'] = enquiries
        return context


class CustomerPoCreateDetailView(LoginRequiredMixin, TemplateView):
    """
    Create new customer PO with tabbed interface.
    Converted from: aspnet/Module/SalesDistribution/Transactions/CustPO_New_Details.aspx

    3-Tab Workflow:
    Tab 1 - Customer Details: Display customer info, select quotation, enter PO details
    Tab 2 - Goods Details: Add/edit line items (description, qty, rate, discount, unit)
    Tab 3 - Terms & Conditions: Payment terms, taxes, file upload, remarks
    """
    template_name = 'sales_distribution/po_create_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        context['units'] = UnitMaster.objects.all()

        # Initialize empty form
        context['form'] = CustomerPoForm()

        # Initialize empty line items list
        context['line_items'] = []

        # Get enquiries for dropdown
        context['enquiries'] = SdCustEnquiryMaster.objects.filter(
            compid=self.request.session.get('company_id', 1)
        ).order_by('-enqid')[:100]

        # If creating from enquiry, pre-populate
        enqid = self.kwargs.get('enqid')
        if enqid:
            try:
                enquiry = SdCustEnquiryMaster.objects.get(enqid=enqid)
                context['enquiry'] = enquiry
                context['quotations'] = SdCustQuotationMaster.objects.filter(
                    enqid=enquiry,
                    authorize=1
                ).order_by('-id')

                # Get temporary line items from session if available
                session_key = f'po_line_items_{enqid}'
                if session_key in self.request.session:
                    context['line_items'] = self.request.session[session_key]
            except SdCustEnquiryMaster.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        """Handle PO creation with details."""
        try:
            with transaction.atomic():
                # Store username instead of session key
                username = request.user.username if request.user.is_authenticated else 'anonymous'
                compid = request.session.get('company_id', 1)
                finyearid = request.session.get('financial_year_id', 1)
                
                # Create PO Master
                po_master = SdCustPoMaster.objects.create(
                    sysdate=datetime.now().strftime('%d-%m-%Y'),
                    systime=datetime.now().strftime('%H:%M:%S'),
                    sessionid=username,
                    compid=compid,
                    finyearid=finyearid,
                    customerid=request.POST.get('customerid', ''),
                    quotationno=request.POST.get('quotationno') or None,
                    pono=request.POST.get('pono', ''),
                    podate=request.POST.get('podate', ''),
                    poreceiveddate=request.POST.get('poreceiveddate', ''),
                    vendorcode=request.POST.get('vendorcode', ''),
                    paymentterms=request.POST.get('paymentterms', ''),
                    pf=request.POST.get('pf', ''),
                    vat=request.POST.get('vat', ''),
                    excise=request.POST.get('excise', ''),
                    octroi=request.POST.get('octroi', ''),
                    warrenty=request.POST.get('warrenty', ''),
                    insurance=request.POST.get('insurance', ''),
                    transport=request.POST.get('transport', ''),
                    noteno=request.POST.get('noteno', ''),
                    registrationno=request.POST.get('registrationno', ''),
                    freight=request.POST.get('freight', ''),
                    remarks=request.POST.get('remarks', ''),
                    cst=request.POST.get('cst', ''),
                    validity=request.POST.get('validity', ''),
                    othercharges=request.POST.get('othercharges', ''),
                    enqid_id=request.POST.get('enqid') or None,
                )
                
                # Handle file upload
                po_file = request.FILES.get('attachment')
                if po_file:
                    po_master.filename = po_file.name
                    po_master.filesize = po_file.size
                    po_master.contenttype = po_file.content_type
                    po_master.filedata = po_file.read()
                    po_master.save()

                # Save PO Details (Goods Details)
                detail_count = self._save_po_details(request, po_master)

                # Clear session line items after successful creation
                session_key = f'po_line_items_{request.POST.get("enqid")}'
                if session_key in request.session:
                    del request.session[session_key]
                    request.session.modified = True

                messages.success(request, f'Customer PO {po_master.pono} created successfully with {detail_count} items!')
                return redirect('sales_distribution:po-list')

        except Exception as e:
            messages.error(request, f'Error creating PO: {str(e)}')
            enqid = kwargs.get('enqid')
            if enqid:
                return redirect('sales_distribution:po-create-detail', enqid=enqid)
            return redirect('sales_distribution:po-list')

    def _save_po_details(self, request, po_master):
        """Save PO detail items from POST data."""
        count = 0
        sessionid = request.session.session_key or 'default'
        compid = request.session.get('company_id', 1)
        finyearid = request.session.get('financial_year_id', 1)

        for key in request.POST:
            if key.startswith('detail_itemdesc_'):
                index = key.replace('detail_itemdesc_', '')
                itemdesc = request.POST.get(f'detail_itemdesc_{index}', '').strip()

                if not itemdesc:
                    continue

                totalqty = request.POST.get(f'detail_totalqty_{index}', 0)
                rate = request.POST.get(f'detail_rate_{index}', 0)
                discount = request.POST.get(f'detail_discount_{index}', 0)
                unit_id = request.POST.get(f'detail_unit_{index}')

                # Validate unit_id is provided (required field in database)
                if not unit_id:
                    raise ValueError(f'Unit is required for line item: {itemdesc[:50]}')

                SdCustPoDetails.objects.create(
                    sessionid=sessionid,
                    compid=compid,
                    finyearid=finyearid,
                    itemdesc=itemdesc,
                    totalqty=float(totalqty) if totalqty else 0,
                    rate=float(rate) if rate else 0,
                    discount=float(discount) if discount else 0,
                    poid=po_master,
                    unit_id=int(unit_id),
                )
                count += 1

        return count


# ============================================================================
# CUSTOMER PO LINE ITEM HTMX ENDPOINTS
# ============================================================================

class PoLineItemCreateView(LoginRequiredMixin, View):
    """
    HTMX POST endpoint: Add a new line item to session storage.
    Returns HTML row to append to table.
    """
    def post(self, request, poid):
        """Add line item to session and return HTML row."""
        # Get session key for this PO (use enquiry ID)
        session_key = f'po_line_items_{poid}'

        # Get existing line items from session
        line_items = request.session.get(session_key, [])

        # Get form data
        itemdesc = request.POST.get('itemdesc', '').strip()
        totalqty = request.POST.get('totalqty', '')
        rate = request.POST.get('rate', '')
        discount = request.POST.get('discount', '0')
        unit_id = request.POST.get('unit', '')

        # Validate
        errors = []
        if not itemdesc:
            errors.append('Item description is required')
        try:
            totalqty = float(totalqty)
            if totalqty <= 0:
                errors.append('Quantity must be greater than zero')
        except (ValueError, TypeError):
            errors.append('Invalid quantity')
            totalqty = 0

        try:
            rate = float(rate)
            if rate <= 0:
                errors.append('Rate must be greater than zero')
        except (ValueError, TypeError):
            errors.append('Invalid rate')
            rate = 0

        try:
            discount = float(discount)
            if discount < 0 or discount > 100:
                errors.append('Discount must be between 0 and 100')
        except (ValueError, TypeError):
            errors.append('Invalid discount')
            discount = 0

        if not unit_id:
            errors.append('Unit is required')

        if errors:
            return HttpResponse(
                f'<tr><td colspan="8" class="px-4 py-2 text-red-600 text-sm">{"; ".join(errors)}</td></tr>',
                status=400
            )

        # Get unit details
        try:
            unit = UnitMaster.objects.get(id=unit_id)
        except UnitMaster.DoesNotExist:
            return HttpResponse(
                '<tr><td colspan="8" class="px-4 py-2 text-red-600 text-sm">Invalid unit selected</td></tr>',
                status=400
            )

        # Calculate amount
        amount = (totalqty * rate) - ((totalqty * rate * discount) / 100)

        # Create line item dict
        item_id = len(line_items) + 1
        line_item = {
            'id': item_id,
            'itemdesc': itemdesc,
            'totalqty': totalqty,
            'rate': rate,
            'discount': discount,
            'unit': unit_id,
            'unit_id': unit_id,  # Also include unit_id for consistency
            'unit_symbol': unit.symbol,
            'amount': round(amount, 2)
        }

        # Add to session
        line_items.append(line_item)
        request.session[session_key] = line_items
        request.session.modified = True

        # Render row
        from django.template.loader import render_to_string
        from types import SimpleNamespace

        # Convert dict to object for template access
        item_obj = SimpleNamespace(**line_item)
        forloop_obj = SimpleNamespace(counter=item_id)

        row_html = render_to_string('sales_distribution/partials/po_line_item_row.html', {
            'item': item_obj,
            'forloop': forloop_obj,
            'poid': poid
        })

        # Update count and hide empty row using HTMX events instead of inline scripts
        response_html = row_html

        # Add HX-Trigger header to update count
        from django.http import HttpResponse
        response = HttpResponse(response_html)

        # Use hx-trigger to run JavaScript after swap
        if len(line_items) == 1:
            # First item - remove empty row
            response['HX-Trigger-After-Swap'] = 'removeEmptyRow'

        # Always update count
        update_count_script = f'''
        <script>
        (function() {{
            const countEl = document.getElementById('line-item-count');
            if (countEl) countEl.textContent = '{len(line_items)} item(s) added';
            const emptyRow = document.getElementById('empty-row');
            if (emptyRow) emptyRow.remove();
        }})();
        </script>
        '''

        return HttpResponse(row_html + update_count_script)


class PoLineItemRowView(LoginRequiredMixin, View):
    """
    HTMX GET endpoint: Get line item row in view mode (for cancel edit).
    """
    def get(self, request, poid, item_id):
        """Return line item row in view mode."""
        session_key = f'po_line_items_{poid}'
        line_items = request.session.get(session_key, [])

        # Find item
        item_dict = next((item for item in line_items if item['id'] == int(item_id)), None)
        if not item_dict:
            return HttpResponse(
                '<tr><td colspan="8" class="px-4 py-2 text-red-600 text-sm">Item not found</td></tr>',
                status=404
            )

        # Get item index for counter
        item_index = line_items.index(item_dict) + 1

        # Render row
        from django.template.loader import render_to_string
        row_html = render_to_string('sales_distribution/partials/po_line_item_row.html', {
            'item': type('obj', (object,), item_dict)(),
            'forloop': type('obj', (object,), {'counter': item_index})(),
            'poid': poid
        })

        return HttpResponse(row_html)


class PoLineItemEditFormView(LoginRequiredMixin, View):
    """
    HTMX GET endpoint: Get line item row in edit mode.
    """
    def get(self, request, poid, item_id):
        """Return line item row in edit mode."""
        session_key = f'po_line_items_{poid}'
        line_items = request.session.get(session_key, [])

        # Find item
        item_dict = next((item for item in line_items if item['id'] == int(item_id)), None)
        if not item_dict:
            return HttpResponse(
                '<tr><td colspan="8" class="px-4 py-2 text-red-600 text-sm">Item not found</td></tr>',
                status=404
            )

        # Get item index for counter
        item_index = line_items.index(item_dict) + 1

        # Get all units for dropdown
        units = UnitMaster.objects.all().order_by('symbol')

        # Render edit row
        from django.template.loader import render_to_string
        row_html = render_to_string('sales_distribution/partials/po_line_item_edit_row.html', {
            'item': type('obj', (object,), item_dict)(),
            'forloop': type('obj', (object,), {'counter': item_index})(),
            'poid': poid,
            'units': units
        })

        return HttpResponse(row_html)


class PoLineItemUpdateView(LoginRequiredMixin, View):
    """
    HTMX PUT endpoint: Update existing line item in session.
    """
    def put(self, request, poid, item_id):
        """Update line item and return view mode row."""
        from django.http import QueryDict

        # Parse PUT data
        put_data = QueryDict(request.body)

        session_key = f'po_line_items_{poid}'
        line_items = request.session.get(session_key, [])

        # Find item
        item_dict = next((item for item in line_items if item['id'] == int(item_id)), None)
        if not item_dict:
            return HttpResponse(
                '<tr><td colspan="8" class="px-4 py-2 text-red-600 text-sm">Item not found</td></tr>',
                status=404
            )

        # Get form data
        itemdesc = put_data.get('itemdesc', '').strip()
        totalqty = put_data.get('totalqty', '')
        rate = put_data.get('rate', '')
        discount = put_data.get('discount', '0')
        unit_id = put_data.get('unit', '')

        # Validate
        errors = []
        if not itemdesc:
            errors.append('Item description is required')
        try:
            totalqty = float(totalqty)
            if totalqty <= 0:
                errors.append('Quantity must be greater than zero')
        except (ValueError, TypeError):
            errors.append('Invalid quantity')
            totalqty = 0

        try:
            rate = float(rate)
            if rate <= 0:
                errors.append('Rate must be greater than zero')
        except (ValueError, TypeError):
            errors.append('Invalid rate')
            rate = 0

        try:
            discount = float(discount)
            if discount < 0 or discount > 100:
                errors.append('Discount must be between 0 and 100')
        except (ValueError, TypeError):
            errors.append('Invalid discount')
            discount = 0

        if not unit_id:
            errors.append('Unit is required')

        if errors:
            return HttpResponse(
                f'<tr><td colspan="8" class="px-4 py-2 text-red-600 text-sm">{"; ".join(errors)}</td></tr>',
                status=400
            )

        # Get unit details
        try:
            unit = UnitMaster.objects.get(id=unit_id)
        except UnitMaster.DoesNotExist:
            return HttpResponse(
                '<tr><td colspan="8" class="px-4 py-2 text-red-600 text-sm">Invalid unit selected</td></tr>',
                status=400
            )

        # Calculate amount
        amount = (totalqty * rate) - ((totalqty * rate * discount) / 100)

        # Update item in session
        item_dict['itemdesc'] = itemdesc
        item_dict['totalqty'] = totalqty
        item_dict['rate'] = rate
        item_dict['discount'] = discount
        item_dict['unit'] = unit_id
        item_dict['unit_symbol'] = unit.symbol
        item_dict['amount'] = round(amount, 2)

        request.session[session_key] = line_items
        request.session.modified = True

        # Get item index for counter
        item_index = line_items.index(item_dict) + 1

        # Render view mode row
        from django.template.loader import render_to_string
        row_html = render_to_string('sales_distribution/partials/po_line_item_row.html', {
            'item': type('obj', (object,), item_dict)(),
            'forloop': type('obj', (object,), {'counter': item_index})(),
            'poid': poid
        })

        return HttpResponse(row_html)


class PoLineItemDeleteView(LoginRequiredMixin, View):
    """
    HTMX DELETE endpoint: Delete line item from session.
    """
    def delete(self, request, poid, item_id):
        """Delete line item and return empty response (row will be removed by HTMX)."""
        session_key = f'po_line_items_{poid}'
        line_items = request.session.get(session_key, [])

        # Find and remove item
        item_dict = next((item for item in line_items if item['id'] == int(item_id)), None)
        if item_dict:
            line_items.remove(item_dict)
            request.session[session_key] = line_items
            request.session.modified = True

        # Update count
        update_count = f'<script>const countEl = document.getElementById("line-item-count"); if(countEl) countEl.innerHTML = \'<span class="font-medium">{len(line_items)}</span> item(s) added\';</script>'

        # If no more items, show empty row and warning banner
        if len(line_items) == 0:
            empty_row = '<tr id="empty-row" class="empty-row"><td colspan="8" class="px-6 py-8 text-center text-sm text-gray-500">No line items added yet. Use the form above to add items.</td></tr>'
            warning_banner = '''
            <div id="no-items-warning" class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-yellow-700">
                            <strong>Note:</strong> Please add at least one line item in the "Goods Details" tab before submitting the PO.
                        </p>
                    </div>
                </div>
            </div>
            '''
            script = f'''
            <script>
                document.getElementById("line-items-tbody").innerHTML = '{empty_row.replace("'", "\\'")}';
                const warningContainer = document.querySelector('[x-show="activeTab === \\'goods\\'"]');
                if (warningContainer && !document.getElementById('no-items-warning')) {{
                    const warningDiv = document.createElement('div');
                    warningDiv.innerHTML = `{warning_banner.replace("`", "\\`").replace("'", "\\'")}`;
                    warningContainer.insertBefore(warningDiv.firstElementChild, warningContainer.firstElementChild);
                }}
            </script>
            '''
            return HttpResponse(update_count + script)

        return HttpResponse(update_count)  # Just update count - row will be removed by hx-swap="outerHTML swap:1s"


class CustomerPoUpdateView(LoginRequiredMixin, TemplateView):
    """
    Update existing Customer PO with tabbed interface.
    Converted from: CustPO_Edit.aspx
    Requirements: 2.3, 2.6, 2.7
    """
    template_name = 'sales_distribution/po_create_detail.html'
    
    def get_context_data(self, **kwargs):
        """Get PO and related data."""
        context = super().get_context_data(**kwargs)
        poid = kwargs.get('poid')

        # Get PO Master
        po_master = get_object_or_404(SdCustPoMaster, poid=poid)
        context['po'] = po_master
        context['is_edit'] = True

        # Get enquiry details if exists
        if po_master.enqid:
            context['enquiry'] = po_master.enqid
        else:
            context['enquiry'] = None

        # Get PO Details and convert to list format expected by template
        po_details = SdCustPoDetails.objects.filter(poid=po_master).order_by('id')
        line_items = []
        for detail in po_details:
            line_items.append({
                'id': detail.id,
                'itemdesc': detail.itemdesc,
                'totalqty': detail.totalqty,
                'rate': detail.rate,
                'discount': detail.discount,
                'unit_id': detail.unit_id,
                'unit_symbol': detail.unit.symbol if detail.unit else '',
                'amount': detail.amount if hasattr(detail, 'amount') else ((detail.totalqty * detail.rate) - ((detail.totalqty * detail.rate * detail.discount) / 100))
            })
        context['line_items'] = line_items

        # Initialize form with PO data
        context['form'] = CustomerPoForm(instance=po_master)

        # Get units for dropdown
        context['units'] = UnitMaster.objects.all()

        # Get enquiries for dropdown
        context['enquiries'] = SdCustEnquiryMaster.objects.filter(
            compid=self.request.session.get('company_id', 1)
        ).order_by('-enqid')[:100]

        # Get quotations for dropdown
        if po_master.enqid:
            context['quotations'] = SdCustQuotationMaster.objects.filter(
                enqid=po_master.enqid,
                authorize=1
            ).order_by('-id')
        else:
            context['quotations'] = SdCustQuotationMaster.objects.none()

        return context
    
    def post(self, request, *args, **kwargs):
        """Handle PO update with tabbed data."""
        poid = kwargs.get('poid')

        try:
            with transaction.atomic():
                po_master = get_object_or_404(SdCustPoMaster, poid=poid)
                
                # Update PO Master
                po_master.customerid = request.POST.get('customerid', '')
                po_master.quotationno = request.POST.get('quotationno') or None
                po_master.pono = request.POST.get('pono', '')
                po_master.podate = request.POST.get('podate', '')
                po_master.poreceiveddate = request.POST.get('poreceiveddate', '')
                po_master.vendorcode = request.POST.get('vendorcode', '')
                po_master.paymentterms = request.POST.get('paymentterms', '')
                po_master.pf = request.POST.get('pf', '')
                po_master.vat = request.POST.get('vat', '')
                po_master.excise = request.POST.get('excise', '')
                po_master.octroi = request.POST.get('octroi', '')
                po_master.warrenty = request.POST.get('warrenty', '')
                po_master.insurance = request.POST.get('insurance', '')
                po_master.transport = request.POST.get('transport', '')
                po_master.noteno = request.POST.get('noteno', '')
                po_master.registrationno = request.POST.get('registrationno', '')
                po_master.freight = request.POST.get('freight', '')
                po_master.remarks = request.POST.get('remarks', '')
                po_master.cst = request.POST.get('cst', '')
                po_master.validity = request.POST.get('validity', '')
                po_master.othercharges = request.POST.get('othercharges', '')
                po_master.enqid_id = request.POST.get('enqid') or None
                
                # Handle file upload
                po_file = request.FILES.get('attachment')
                if po_file:
                    po_master.filename = po_file.name
                    po_master.filesize = po_file.size
                    po_master.contenttype = po_file.content_type
                    po_master.filedata = po_file.read()
                
                po_master.save()

                # Delete existing details and recreate
                SdCustPoDetails.objects.filter(poid=po_master).delete()
                detail_count = self._save_po_details(request, po_master)

                messages.success(request, f'Customer PO {po_master.pono} updated successfully!')
                return redirect('sales_distribution:po-list')

        except Exception as e:
            messages.error(request, f'Error updating PO: {str(e)}')
            return redirect('sales_distribution:po-edit', poid=poid)
    
    def _save_po_details(self, request, po_master):
        """Save PO detail items from POST data."""
        count = 0
        sessionid = request.session.session_key or 'default'
        compid = request.session.get('company_id', 1)
        finyearid = request.session.get('financial_year_id', 1)

        for key in request.POST:
            if key.startswith('detail_itemdesc_'):
                index = key.replace('detail_itemdesc_', '')
                itemdesc = request.POST.get(f'detail_itemdesc_{index}', '').strip()

                if not itemdesc:
                    continue

                totalqty = request.POST.get(f'detail_totalqty_{index}', 0)
                rate = request.POST.get(f'detail_rate_{index}', 0)
                discount = request.POST.get(f'detail_discount_{index}', 0)
                unit_id = request.POST.get(f'detail_unit_{index}')

                # Validate unit_id is provided (required field in database)
                if not unit_id:
                    raise ValueError(f'Unit is required for line item: {itemdesc[:50]}')

                SdCustPoDetails.objects.create(
                    sessionid=sessionid,
                    compid=compid,
                    finyearid=finyearid,
                    itemdesc=itemdesc,
                    totalqty=float(totalqty) if totalqty else 0,
                    rate=float(rate) if rate else 0,
                    discount=float(discount) if discount else 0,
                    poid=po_master,
                    unit_id=int(unit_id),
                )
                count += 1

        return count


class CustomerPoDownloadView(LoginRequiredMixin, View):
    """
    Download PO attachment file.
    Requirements: 2.5
    """
    
    def get(self, request, poid):
        """Stream file from database."""
        po = get_object_or_404(SdCustPoMaster, poid=poid)
        
        if not po.filedata:
            messages.error(request, 'No file attached to this PO.')
            return redirect('sales_distribution:po-detail', poid=poid)
        
        # Create file response
        file_data = io.BytesIO(po.filedata)
        response = FileResponse(file_data, content_type=po.contenttype)
        response['Content-Disposition'] = f'attachment; filename="{po.filename}"'
        response['Content-Length'] = po.filesize
        
        return response


class QuotationDetailsForPoView(LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint: Return quotation details for auto-populating PO form.
    Requirements: 2.7
    """
    template_name = 'sales_distribution/partials/quotation_details_partial.html'
    
    def get_context_data(self, **kwargs):
        """Get quotation details."""
        context = super().get_context_data(**kwargs)
        
        quotation_id = self.request.GET.get('quotation')
        if quotation_id:
            try:
                quotation = SdCustQuotationMaster.objects.select_related('enqid').get(id=quotation_id)
                context['quotation'] = quotation
                context['enquiry'] = quotation.enqid
            except SdCustQuotationMaster.DoesNotExist:
                pass
        
        return context




class CustomerPoPrintView(LoginRequiredMixin, DetailView):
    """
    Generate professional PDF for Customer Purchase Order.
    Converted from: D:/inetpub/NewERP/Module/SalesDistribution/Transactions/CustPO_Print_Details.aspx

    Note: Uses xhtml2pdf instead of Crystal Reports for Windows compatibility
    """
    model = SdCustPoMaster
    pk_url_kwarg = 'poid'
    template_name = 'sales_distribution/po_print_pdf.html'

    def get_context_data(self, **kwargs):
        from django.conf import settings

        context = super().get_context_data(**kwargs)
        po = self.get_object()

        # Get PO line items with unit info
        line_items = SdCustPoDetails.objects.filter(poid=po).select_related('unit')

        # Get customer info
        try:
            customer = SdCustMaster.objects.get(customerid=po.customerid)
        except SdCustMaster.DoesNotExist:
            customer = None

        # Get quotation info if linked
        quotation = None
        if po.quotationno:
            try:
                quotation = SdCustQuotationMaster.objects.get(quotationno=po.quotationno)
            except SdCustQuotationMaster.DoesNotExist:
                pass

        # Calculate line item totals
        subtotal = 0
        for item in line_items:
            line_total = item.totalqty * item.rate
            if item.discount:
                line_total -= (line_total * item.discount / 100)
            subtotal += line_total
            item.line_total = line_total

        # Apply charges (note: PO model stores these as text, need to convert)
        pf_amount = 0
        if po.pf:
            try:
                pf_amount = float(po.pf)
            except (ValueError, TypeError):
                pf_amount = 0

        freight_amount = 0
        if po.freight:
            try:
                freight_amount = float(po.freight)
            except (ValueError, TypeError):
                freight_amount = 0

        other_charges = 0
        if po.othercharges:
            try:
                other_charges = float(po.othercharges)
            except (ValueError, TypeError):
                other_charges = 0

        insurance = 0
        if po.insurance:
            try:
                insurance = float(po.insurance)
            except (ValueError, TypeError):
                insurance = 0

        octroi_amount = 0
        if po.octroi:
            try:
                octroi_amount = float(po.octroi)
            except (ValueError, TypeError):
                octroi_amount = 0

        grand_total = subtotal + pf_amount + freight_amount + other_charges + insurance + octroi_amount

        context.update({
            'po': po,
            'line_items': line_items,
            'customer': customer,
            'quotation': quotation,
            'subtotal': subtotal,
            'pf_amount': pf_amount,
            'freight_amount': freight_amount,
            'other_charges': other_charges,
            'insurance': insurance,
            'octroi_amount': octroi_amount,
            'grand_total': grand_total,
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
        po_no = context['po'].pono.replace('/', '_') if context['po'].pono else f'PO_{context["po"].poid}'
        filename = f'Purchase_Order_{po_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response




