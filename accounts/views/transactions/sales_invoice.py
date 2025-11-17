"""
Sales Invoice Creation Views

CRITICAL: This module EXACTLY replicates ASP.NET WebForms logic from:
- SalesInvoice_New.aspx.cs (PO Selection)
- SalesInvoice_New_Details.aspx.cs (4-Tab Invoice Form)

NO deviations from source business logic.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum, F
from datetime import datetime
from decimal import Decimal
import json

from accounts.models import (
    TblaccSalesinvoiceMaster,
    TblaccSalesinvoiceDetails,
    TblaccSalesinvoiceMasterType,
    TblexcisecommodityMaster,
)
from accounts.forms_sales_invoice import (
    POSelectionSearchForm,
    SalesInvoiceHeaderForm,
    SalesInvoiceBuyerForm,
    SalesInvoiceConsigneeForm,
    SalesInvoiceGoodsFormSet,
    SalesInvoiceTaxationForm,
)
from accounts.services_sales_invoice import SalesInvoiceService, SalesInvoiceValidationService
from sales_distribution.models import (
    SdCustMaster,
    SdCustPoMaster,
    SdCustPoDetails,
    SdCustWorkorderMaster,
)
from sys_admin.models import TblfinancialMaster, Tblcountry, Tblstate, Tblcity
from core.mixins import CompanyFinancialYearMixin, BaseListViewMixin


# =============================================================================
# PO SELECTION VIEW (SalesInvoice_New.aspx)
# =============================================================================

class SalesInvoicePOSelectionView(CompanyFinancialYearMixin, ListView):
    """
    PO Selection screen for sales invoice creation.

    SOURCE: SalesInvoice_New.aspx.cs

    Workflow:
    1. User searches by Customer Name or PO No
    2. System displays POs with remaining quantity > 0
    3. User selects Work Order(s) and Invoice Type
    4. System redirects to invoice details form

    Business Logic (lines 70-209):
    - Query POs filtered by CompId and FinYearId
    - For each PO, calculate remaining quantity
    - Only show POs where at least one item has remaining qty > 0
    - Work Orders displayed in dropdown per PO
    """

    model = SdCustPoMaster
    template_name = 'accounts/transactions/sales_invoice_po_selection.html'
    context_object_name = 'po_list'
    paginate_by = 15  # ASP.NET PageSize="15"

    def get_queryset(self):
        """
        Replicate bindgrid() method from SalesInvoice_New.aspx.cs lines 70-209

        CRITICAL: Only return POs that have items with remaining quantity > 0
        """
        compid = self.request.session.get('compid', 1)
        finyear = self.request.session.get('finyear', 1)

        queryset = SdCustPoMaster.objects.filter(
            compid=compid,
            finyearid__lte=finyear  # Note: <= not =
        )

        # Search filters (lines 88-103)
        search_form = POSelectionSearchForm(self.request.GET)
        if search_form.is_valid():
            search_type = search_form.cleaned_data.get('search_type')

            if search_type == '1':  # PO No
                po_number = search_form.cleaned_data.get('po_number')
                if po_number:
                    queryset = queryset.filter(pono=po_number)

            elif search_type == '0':  # Customer Name
                customer_name = search_form.cleaned_data.get('customer_name')
                if customer_name:
                    # Extract customer ID from "Name [ID]" format
                    customer_id = self._extract_customer_id(customer_name)
                    if customer_id:
                        queryset = queryset.filter(customerid=customer_id)

        # Order by POId DESC (line 106)
        queryset = queryset.order_by('-poid')

        # Filter out POs with no remaining quantity (lines 175-194)
        po_list_with_remaining = []
        for po in queryset:
            if self._has_remaining_quantity(po):
                po_list_with_remaining.append(po.poid)

        queryset = queryset.filter(poid__in=po_list_with_remaining)

        return queryset

    def _extract_customer_id(self, customer_name_with_id):
        """Extract customer ID from 'Name [ID]' format"""
        import re
        match = re.search(r'\[([^\]]+)\]', customer_name_with_id)
        return match.group(1) if match else None

    def _has_remaining_quantity(self, po):
        """
        Check if PO has at least one item with remaining quantity > 0
        SOURCE: Lines 149-178 (loop through PO details and check remaining qty)
        """
        po_details = SdCustPoDetails.objects.filter(
            poid=po.poid
        )

        for item in po_details:
            # Calculate remaining qty (lines 154-178)
            total_qty = float(item.totalqty) if item.totalqty else 0.0

            # Get sum of already invoiced quantities
            compid = self.request.session.get('compid', 1)
            invoiced_qty_sum = TblaccSalesinvoiceDetails.objects.filter(
                itemid=item.id,
                mid__compid=compid
            ).aggregate(
                total=Sum('reqqty')
            )['total'] or 0.0

            remaining_qty = total_qty - float(invoiced_qty_sum)

            if remaining_qty > 0:
                return True

        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = POSelectionSearchForm(self.request.GET)

        # Get invoice types (line 172)
        context['invoice_types'] = TblaccSalesinvoiceMasterType.objects.all().order_by('id')

        # Get work orders for each PO (lines 43-68, getWONOInDRP method)
        po_work_orders = {}
        for po in context['po_list']:
            work_orders = SdCustWorkorderMaster.objects.filter(pono=po.pono,
                compid=self.request.session.get('compid')
            ).values('id', 'wono', 'taskprojecttitle')

            # Format: "WONo-TaskProjectTitle"
            po_work_orders[po.poid] = [
                {
                    'id': wo['id'],
                    'display': f"{wo['wono']}-{wo['taskprojecttitle']}"
                }
                for wo in work_orders
            ]

        # Attach work orders to each PO object

        for po in context['object_list']:

            po.work_orders = po_work_orders.get(po.poid, [])

            po.invoice_types = context['invoice_types']

        # Enrich PO objects with customer and financial year info
        for po in context['object_list']:
            # Add customer name
            if po.customerid:
                try:
                    customer = SdCustMaster.objects.get(customerid=po.customerid, compid=self.request.session.get('compid'))
                    po.customer_name = customer.customername
                    po.customer_id_display = po.customerid
                except:
                    po.customer_name = '-'
                    po.customer_id_display = ''
            else:
                po.customer_name = '-'
                po.customer_id_display = ''
            
            # Add financial year name
            if po.finyearid:
                try:
                    finyear = TblfinancialMaster.objects.get(pk=po.finyearid)
                    po.fin_year = finyear.finyear
                except:
                    po.fin_year = str(po.finyearid)
            else:
                po.fin_year = '-'
            
            # Format date
            po.formatted_date = po.podate if isinstance(po.podate, str) else (po.podate.strftime('%Y-%m-%d') if po.podate else '-')

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle PO selection and redirect to invoice details.
        SOURCE: GridView1_RowCommand (lines 210-249)
        """
        poid = request.POST.get('poid')
        pono = request.POST.get('pono')
        podate = request.POST.get('podate')
        invoice_type = request.POST.get('invoice_type')
        custcode = request.POST.get('custcode')

        # Work Order selection (can be multiple, comma-separated IDs)
        wono_ids = request.POST.get('wono_ids', '')

        # Validation (lines 231-242)
        if not invoice_type or invoice_type == '1':
            messages.error(request, 'Select WONo and Type.')
            return redirect('accounts:sales_invoice_po_selection')

        if not wono_ids:
            messages.error(request, 'Select WONo and Type.')
            return redirect('accounts:sales_invoice_po_selection')

        # Redirect to invoice details (line 234)
        # Pass encrypted parameters (ASP.NET uses fun.Encrypt)
        # For Django, we'll use session storage for security
        request.session['invoice_creation_context'] = {
            'poid': poid,
            'pono': pono,
            'podate': podate,
            'wono_ids': wono_ids,
            'invoice_type': invoice_type,
            'custcode': custcode,
        }

        return redirect('accounts:sales_invoice_create')


# =============================================================================
# INVOICE CREATION VIEW (SalesInvoice_New_Details.aspx)
# =============================================================================

class SalesInvoiceCreateView(CompanyFinancialYearMixin, View):
    """
    4-Tab Sales Invoice Creation Form

    SOURCE: SalesInvoice_New_Details.aspx.cs

    Tabs:
    1. Buyer Information
    2. Consignee Information
    3. Goods/Items Selection
    4. Taxation

    Key Methods:
    - Page_Load (lines 31-177): Initialize form, auto-generate invoice number
    - BtnSubmit_Click (lines 287-469): Validate and save invoice
    - Button5_Click (lines 551-614): Search and populate buyer
    - Button4_Click (lines 615-677): Search and populate consignee
    - Button6_Click (lines 678-730): Copy buyer to consignee
    """

    template_name = 'accounts/transactions/sales_invoice_create.html'

    def get(self, request, *args, **kwargs):
        """
        Initialize invoice creation form.
        SOURCE: Page_Load (lines 31-177)
        """
        # Get context from PO selection (lines 40-47)
        # Accept both session data (from POST) and query params (from JavaScript redirect)
        context_data = request.session.get('invoice_creation_context')

        if context_data:
            # From POST handler
            poid = context_data['poid']
            pono = context_data['pono']
            podate = context_data['podate']
            wono_ids = context_data['wono_ids']
            invoice_type = context_data['invoice_type']
            custcode = context_data['custcode']
        else:
            # From JavaScript redirect with query params (template selectPO function)
            # Query params: poid, wn, pn, date, ty, cid
            poid = request.GET.get('poid')
            wono_ids = request.GET.get('wn', '')
            pono = request.GET.get('pn', '')
            podate = request.GET.get('date', '')
            invoice_type = request.GET.get('ty')
            custcode = request.GET.get('cid', '')

            # Validation
            if not poid or not invoice_type or not wono_ids:
                messages.error(request, 'Invalid access. Please select a PO first.')
                return redirect('accounts:sales_invoice_po_selection')

            # Store in session for POST handler
            request.session['invoice_creation_context'] = {
                'poid': poid,
                'pono': pono,
                'podate': podate,
                'wono_ids': wono_ids,
                'invoice_type': invoice_type,
                'custcode': custcode,
            }

        # Get work order numbers (lines 54-70)
        wono_id_list = [int(x) for x in wono_ids.split(',') if x]
        work_orders = SdCustWorkorderMaster.objects.filter(
            id__in=wono_id_list,
            compid=request.session.get('compid')
        ).values_list('wono', flat=True)
        wono_display = ','.join(work_orders)

        # Get invoice type description (lines 75-80)
        invoice_type_obj = TblaccSalesinvoiceMasterType.objects.get(id=invoice_type)
        invoice_mode_display = invoice_type_obj.description

        # Auto-generate invoice number (lines 96-111)
        next_invoice_no = SalesInvoiceService.generate_invoice_number(
            request.session.get('compid'),
            request.session.get('finyear')
        )

        # Initialize forms
        header_form = SalesInvoiceHeaderForm(initial={
            'invoiceno': next_invoice_no,
            'pono': pono,
            'wono': wono_display,
            'invoicemode': invoice_mode_display,
        })

        # Pre-fill buyer info from customer (lines 139-171)
        customer = SdCustMaster.objects.filter(
            customerid=custcode,
            compid=request.session.get('compid')
        ).first()

        buyer_initial = {}
        if customer:
            # Convert city string to city ID for cascading dropdown
            buyer_city_id = None
            if customer.materialdelcity and customer.materialdelstate:
                from sys_admin.models import Tblcity
                city_obj = Tblcity.objects.filter(
                    cityname=customer.materialdelcity,
                    sid=customer.materialdelstate
                ).first()
                if city_obj:
                    buyer_city_id = city_obj.cityid

            buyer_initial = {
                'buyer_name': f"{customer.customername} [{customer.customerid}]",
                'buyer_add': customer.materialdeladdress,
                'buyer_country': customer.materialdelcountry,
                'buyer_state': customer.materialdelstate,
                'buyer_city': buyer_city_id,  # Use city ID instead of string
                'buyer_fax': customer.materialdelfaxno or '-',
                'buyer_cotper': customer.contactperson,
                'buyer_ph': customer.materialdelcontactno,
                'buyer_tin': customer.tincstno,
                'buyer_vat': customer.tinvatno or '-',
                'buyer_mob': customer.contactno,
                'buyer_email': customer.email,
                'buyer_ecc': customer.eccno or '-',
            }

        buyer_form = SalesInvoiceBuyerForm(initial=buyer_initial)
        consignee_form = SalesInvoiceConsigneeForm()

        # Populate goods formset from PO details (fillgrid, lines 196-281)
        goods_items = self._get_goods_items_for_po(poid, request)

        goods_formset = SalesInvoiceGoodsFormSet(initial=goods_items)

        # Taxation form (lines 115-135)
        taxation_initial = {
            'addamt': 0,
            'addtype': 0,
            'deduction': 0,
            'deductiontype': 0,
            'pf': 0,
            'pftype': 0,
            'sed': 0,
            'sedtype': 0,
            'aed': 0,
            'aedtype': 0,
            'freight': 0,
            'freighttype': 0,
            'insurance': 0,
            'insurancetype': 0,
            'rrgcno': '-',
            'vehiregno': '-',
            'dutyrate': '-',
            'otheramt': 0,
        }

        taxation_form = SalesInvoiceTaxationForm(
            initial=taxation_initial,
            invoice_type=invoice_type  # For CST visibility
        )

        # Determine SGST/CST label based on invoice type (lines 115-125)
        vat_label = 'SGST'
        show_cst = True
        if invoice_type == '2':  # Within MH
            show_cst = False

        context = {
            'header_form': header_form,
            'buyer_form': buyer_form,
            'consignee_form': consignee_form,
            'goods_formset': goods_formset,
            'taxation_form': taxation_form,
            'poid': poid,
            'pono': pono,
            'podate': podate,
            'wono_display': wono_display,
            'work_order_ids': wono_ids,  # Fixed: Added missing work_order_ids
            'invoice_type': invoice_type,
            'invoice_mode_display': invoice_mode_display,
            'next_invoice_no': next_invoice_no,
            'customer_id': custcode,  # Fixed: Renamed from custcode to customer_id
            'custcode': custcode,  # Keep for backward compatibility
            'vat_label': vat_label,
            'show_cst': show_cst,
            'current_date': datetime.now().strftime('%d-%m-%Y'),
        }

        return render(request, self.template_name, context)

    def _get_goods_items_for_po(self, poid, request):
        """
        Get goods items from PO with remaining quantities.
        SOURCE: fillgrid method (lines 196-281)

        CRITICAL: Only return items with remaining quantity > 0
        """
        po_details = SdCustPoDetails.objects.filter(
            poid=poid
        ).select_related('unit')

        items_data = []

        for item in po_details:
            # Calculate remaining quantity (lines 238-256)
            total_qty = float(item.totalqty) if item.totalqty else 0.0

            # Get sum of already invoiced quantities for this item
            invoiced_qty_sum = TblaccSalesinvoiceDetails.objects.filter(
                itemid=item.id,
                mid__compid=request.session.get('compid')
            ).aggregate(
                total=Sum('reqqty')
            )['total'] or 0.0

            remaining_qty = round(total_qty - float(invoiced_qty_sum), 3)

            # Only include items with remaining qty > 0 (lines 256-273)
            if remaining_qty > 0:
                # Get unit symbol
                unit_symbol = item.unit.symbol if item.unit else ''

                items_data.append({
                    'selected': False,
                    'item_id': item.id,
                    'po_id': poid,
                    'item_desc': item.itemdesc,  # Fixed: Template expects item_desc
                    'description': item.itemdesc,  # Keep for backward compatibility
                    'unit': unit_symbol,  # Fixed: Template expects unit
                    'unit_symbol': unit_symbol,  # Keep for backward compatibility
                    'total_qty': round(total_qty, 3),
                    'remaining_qty': remaining_qty,
                    'remaining_percentage': 100.0,  # Fixed: Added remaining_percentage
                    'unit_of_qty': item.unit.id if item.unit else None,
                    'req_qty': None,
                    'rate': round(float(item.rate), 2) if item.rate else 0.0,
                    'amt_in_percent': 0.0,
                })

        return items_data

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handle invoice submission.
        SOURCE: BtnSubmit_Click (lines 287-469)

        CRITICAL VALIDATION (lines 301-302):
        - All dropdown selections must be valid
        - All required text fields must be filled
        - Date fields must be in DD-MM-YYYY format
        - Email fields must match regex
        - At least one item must be selected
        - Req Qty must be <= Remaining Qty for all selected items
        - All numeric fields must match ^\\d{1,15}(\\.\\d{0,3})?$
        """
        # Get context
        context_data = request.session.get('invoice_creation_context')
        if not context_data:
            messages.error(request, 'Session expired. Please select a PO again.')
            return redirect('accounts:sales_invoice_po_selection')

        poid = context_data['poid']
        pono = context_data['pono']
        wono_ids = context_data['wono_ids']
        invoice_type = context_data['invoice_type']
        custcode = context_data['custcode']

        # Get work order display
        wono_id_list = [int(x) for x in wono_ids.split(',') if x]
        work_orders = SdCustWorkorderMaster.objects.filter(
            id__in=wono_id_list,
            compid=request.session.get('compid')
        ).values_list('wono', flat=True)
        wono_display = ','.join(work_orders)

        # Bind forms with POST data
        header_form = SalesInvoiceHeaderForm(request.POST)
        buyer_form = SalesInvoiceBuyerForm(request.POST)
        consignee_form = SalesInvoiceConsigneeForm(request.POST)
        goods_formset = SalesInvoiceGoodsFormSet(request.POST)
        taxation_form = SalesInvoiceTaxationForm(
            request.POST,
            invoice_type=invoice_type
        )

        # Validate all forms (lines 301-454)
        forms_valid = all([
            header_form.is_valid(),
            buyer_form.is_valid(),
            consignee_form.is_valid(),
            goods_formset.is_valid(),
            taxation_form.is_valid(),
        ])

        if not forms_valid:
            # Collect all errors
            all_errors = []
            for form in [header_form, buyer_form, consignee_form, taxation_form]:
                all_errors.extend(form.errors.values())
            if goods_formset.errors:
                all_errors.extend(goods_formset.errors)

            messages.error(request, 'Input data is invalid. Please check all fields.')

            # Re-render with errors
            context = {
                'header_form': header_form,
                'buyer_form': buyer_form,
                'consignee_form': consignee_form,
                'goods_formset': goods_formset,
                'taxation_form': taxation_form,
                'poid': poid,
                'pono': pono,
                'invoice_type': invoice_type,
            }
            return render(request, self.template_name, context)

        # Additional business validation (lines 304-346)
        # Check remaining quantities for all selected items
        selected_items = [
            form.cleaned_data
            for form in goods_formset
            if form.cleaned_data.get('selected')
        ]

        if not selected_items:
            messages.error(request, 'Please select at least one item')
            return self.get(request, *args, **kwargs)

        # Validate remaining quantities (lines 308-344)
        for item_data in selected_items:
            item_id = item_data['item_id']
            req_qty = item_data['req_qty']

            # Recalculate remaining quantity to ensure data integrity
            po_detail = SdCustPoDetails.objects.get(id=item_id)
            total_qty = float(po_detail.totalqty) if po_detail.totalqty else 0.0

            invoiced_qty = TblaccSalesinvoiceDetails.objects.filter(
                itemid=item_id,
                mid__compid=request.session.get('compid')
            ).aggregate(
                total=Sum('reqqty')
            )['total'] or 0.0

            remaining_qty = total_qty - float(invoiced_qty)

            if float(req_qty) > remaining_qty:
                messages.error(
                    request,
                    f'Requested quantity for item {po_detail.itemdesc} '
                    f'exceeds remaining quantity ({remaining_qty})'
                )
                return self.get(request, *args, **kwargs)

            # Validate amount percentage (prevent exceeding 100%)
            amount_percent = item_data.get('amtinper', 0) or 0
            if amount_percent and float(amount_percent) > 0:
                try:
                    SalesInvoiceValidationService.validate_amount_percentage(
                        po_detail_id=item_id,
                        requested_percentage=amount_percent,
                        company_id=request.session.get('compid')
                    )
                except ValidationError as e:
                    messages.error(request, str(e))
                    return self.get(request, *args, **kwargs)

        # Save invoice master (lines 398-420)
        invoice_master = TblaccSalesinvoiceMaster()

        # Audit fields
        invoice_master.sysdate = datetime.now().strftime('%d-%m-%Y')
        invoice_master.systime = datetime.now().strftime('%H:%M:%S')
        invoice_master.compid = request.session.get('compid')
        invoice_master.finyearid = request.session.get('finyear')
        invoice_master.sessionid = str(request.user.id)

        # Header fields
        # Generate invoice number fresh at save time to prevent collisions
        invoice_master.invoiceno = SalesInvoiceService.generate_invoice_number(
            request.session.get('compid'),
            request.session.get('finyear')
        )
        invoice_master.pono = pono
        invoice_master.wono = wono_display
        invoice_master.invoicemode = invoice_type
        invoice_master.poid = poid
        invoice_master.customercode = custcode

        # Map header form fields
        for field in header_form.cleaned_data:
            if hasattr(invoice_master, field):
                setattr(invoice_master, field, header_form.cleaned_data[field])

        # Map buyer form fields
        for field in buyer_form.cleaned_data:
            if hasattr(invoice_master, field):
                setattr(invoice_master, field, buyer_form.cleaned_data[field])

        # Map consignee form fields
        for field in consignee_form.cleaned_data:
            if hasattr(invoice_master, field):
                setattr(invoice_master, field, consignee_form.cleaned_data[field])

        # Map taxation form fields (lines 417)
        for field in taxation_form.cleaned_data:
            if hasattr(invoice_master, field):
                setattr(invoice_master, field, taxation_form.cleaned_data[field])

        # Handle VAT/CST based on invoice type (lines 407-415)
        if invoice_type == '2':  # Within MH
            invoice_master.vat = taxation_form.cleaned_data.get('vat', 0)
            invoice_master.selectedcst = 0
            invoice_master.cst = 0
        else:  # Out of MH
            invoice_master.selectedcst = taxation_form.cleaned_data.get('selectedcst', 0)
            invoice_master.cst = taxation_form.cleaned_data.get('vat', 0)
            invoice_master.vat = 0

        # Save master record
        invoice_master.save()

        # Save invoice details (lines 430-435)
        for item_data in selected_items:
            detail = TblaccSalesinvoiceDetails()
            detail.invoiceno = invoice_master.invoiceno
            detail.mid = invoice_master
            detail.itemid = item_data['item_id']
            detail.unit = item_data['unit_of_qty']
            detail.qty = item_data['total_qty']
            detail.reqqty = item_data['req_qty']
            detail.amtinper = item_data['amt_in_percent']
            detail.rate = item_data['rate']
            detail.save()

        # Clear session context (line 457)
        if 'invoice_creation_context' in request.session:
            del request.session['invoice_creation_context']

        # Success message and redirect (line 457)
        messages.success(
            request,
            f'Sales Invoice {invoice_master.invoiceno} created successfully!'
        )

        return redirect('accounts:sales_invoice_po_selection')


# =============================================================================
# HTMX ENDPOINTS (Dynamic Functionality)
# =============================================================================

class CustomerAutocompleteView(View):
    """
    Customer autocomplete for buyer/consignee name fields.
    SOURCE: sql() method (lines 302-328)
    """

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        if len(query) < 1:
            return JsonResponse({'results': []})

        # Query customers (lines 311-313)
        customers = SdCustMaster.objects.filter(
            Q(customername__istartswith=query),
            compid=request.session.get('compid')
        ).values('customerid', 'customername')[:10]

        # Format: "CustomerName [CustomerId]" (line 321)
        results = [
            {
                'id': f"{c['customername']} [{c['customerid']}]",
                'text': f"{c['customername']} [{c['customerid']}]"
            }
            for c in customers
        ]

        return JsonResponse({'results': results})


class GetStatesView(View):
    """
    Get states for selected country (cascading dropdown).
    SOURCE: DrpByCountry_SelectedIndexChanged (lines 479-483)
    """

    def get(self, request, *args, **kwargs):
        country_id = request.GET.get('country_id')

        if not country_id:
            return JsonResponse({'states': []})

        states = Tblstate.objects.filter(
            cid=country_id
        ).values('sid', 'statename').order_by('statename')

        return JsonResponse({
            'states': list(states)
        })


class GetCitiesView(View):
    """
    Get cities for selected state (cascading dropdown).
    SOURCE: DrpByState_SelectedIndexChanged (lines 485-488)
    """

    def get(self, request, *args, **kwargs):
        state_id = request.GET.get('state_id')

        if not state_id:
            return JsonResponse({'cities': []})

        cities = Tblcity.objects.filter(
            sid=state_id
        ).values('cityid', 'cityname').order_by('cityname')

        return JsonResponse({
            'cities': list(cities)
        })


class GetCommodityTariffView(View):
    """
    Get tariff heading for selected commodity (auto-fill).
    SOURCE: DrpCommodity_SelectedIndexChanged (lines 732-734)
    """

    def get(self, request, *args, **kwargs):
        commodity_id = request.GET.get('commodity_id')

        if not commodity_id:
            return JsonResponse({'tariff': ''})

        try:
            commodity = TblexcisecommodityMaster.objects.get(id=commodity_id)
            # ExciseCommodity method would return tariff heading
            # Assuming it's stored in a field (adjust as needed)
            tariff = commodity.tariffheading if hasattr(commodity, 'tariffheading') else ''

            return JsonResponse({'tariff': tariff})
        except TblexcisecommodityMaster.DoesNotExist:
            return JsonResponse({'tariff': ''})


class SearchCustomerView(View):
    """
    Search and populate buyer/consignee information.
    SOURCE: Button5_Click (lines 551-614) - Buyer search
    SOURCE: Button4_Click (lines 615-677) - Consignee search
    """

    def post(self, request, *args, **kwargs):
        customer_name_with_id = request.POST.get('customer_name', '')
        target = request.POST.get('target', 'buyer')  # 'buyer' or 'consignee'

        # Extract customer ID from "Name [ID]" format
        import re
        match = re.search(r'\[([^\]]+)\]', customer_name_with_id)
        customer_id = match.group(1) if match else None

        if not customer_id:
            return JsonResponse({'error': 'Invalid customer selection'}, status=400)

        # Query customer (lines 557-562)
        try:
            customer = SdCustMaster.objects.get(
                customerid=customer_id,
                compid=request.session.get('compid')
            )
        except SdCustMaster.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        # Return customer data (lines 566-589)
        customer_data = {
            'address': customer.materialdeladdress,
            'country': customer.materialdelcountry,
            'state': customer.materialdelstate,
            'city': customer.materialdelcity,
            'fax': customer.materialdelfaxno or '-',
            'contact_person': customer.contactperson,
            'phone': customer.materialdelcontactno,
            'tin_cst': customer.tincstno,
            'tin_vat': customer.tinvatno or '-',
            'mobile': customer.contactno,
            'email': customer.email,
            'ecc': customer.eccno or '-',
        }

        return JsonResponse({'customer': customer_data})


class CopyBuyerToConsigneeView(View):
    """
    Copy buyer information to consignee fields.
    SOURCE: Button6_Click (lines 678-730)
    """

    def post(self, request, *args, **kwargs):
        """
        Return buyer form data to populate consignee form.
        Frontend will handle the copying via JavaScript.
        """
        # In HTMX implementation, this is handled client-side
        # or by returning the populated consignee form partial
        return JsonResponse({'status': 'copy_initiated'})


# =============================================================================
# UTILITY VIEWS
# =============================================================================

class CalculateRemainingQuantityView(View):
    """
    Calculate remaining quantity for a specific item.
    Used for real-time validation in goods tab.
    """

    def get(self, request, *args, **kwargs):
        item_id = request.GET.get('item_id')

        if not item_id:
            return JsonResponse({'error': 'Item ID required'}, status=400)

        try:
            po_detail = SdCustPoDetails.objects.get(id=item_id)
            total_qty = float(po_detail.totalqty) if po_detail.totalqty else 0.0

            invoiced_qty = TblaccSalesinvoiceDetails.objects.filter(
                itemid=item_id,
                mid__compid=request.session.get('compid')
            ).aggregate(
                total=Sum('reqqty')
            )['total'] or 0.0

            remaining_qty = round(total_qty - float(invoiced_qty), 3)

            return JsonResponse({
                'item_id': item_id,
                'total_qty': total_qty,
                'invoiced_qty': float(invoiced_qty),
                'remaining_qty': remaining_qty
            })
        except SdCustPoDetails.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)


# =============================================================================
# INVOICE LIST VIEW (For accessing/editing existing invoices)
# =============================================================================

class SalesInvoiceListView(BaseListViewMixin, ListView):
    """
    List view for all sales invoices with search and pagination.

    Features:
    - Display all invoices for current company/financial year
    - Search by customer name, PO number, invoice number
    - Pagination (15 items per page)
    - Action buttons: Edit, Delete, Print
    """
    model = TblaccSalesinvoiceMaster
    template_name = 'accounts/transactions/sales_invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 15

    def get_queryset(self):
        """
        Get filtered queryset based on search parameters.
        Automatically filtered by company/year via CompanyFinancialYearMixin.
        """
        queryset = super().get_queryset()

        # Search by customer name
        customer_name = self.request.GET.get('customer_name', '').strip()
        if customer_name:
            queryset = queryset.filter(
                customercode__icontains=customer_name
            ) | queryset.filter(
                poid__customerid__customername__icontains=customer_name
            )

        # Search by PO number
        po_number = self.request.GET.get('po_number', '').strip()
        if po_number:
            queryset = queryset.filter(pono__icontains=po_number)

        # Search by invoice number
        invoice_number = self.request.GET.get('invoice_number', '').strip()
        if invoice_number:
            queryset = queryset.filter(invoiceno__icontains=invoice_number)

        # Order by invoice number descending (newest first)
        return queryset.order_by('-invoiceno')


# =============================================================================
# INVOICE UPDATE/EDIT VIEW
# =============================================================================

class SalesInvoiceUpdateView(CompanyFinancialYearMixin, View):
    """
    Update/Edit existing sales invoice.
    Reuses create template but pre-populates all 4 tabs with existing data.
    """

    def get(self, request, *args, **kwargs):
        """Display invoice edit form with pre-populated data"""
        invoice_id = kwargs.get('invoice_id')

        try:
            # Get invoice (filter by company for security)
            invoice = TblaccSalesinvoiceMaster.objects.get(
                id=invoice_id,
                compid=request.session.get('compid')
            )
        except TblaccSalesinvoiceMaster.DoesNotExist:
            messages.error(request, 'Invoice not found')
            return redirect('accounts:sales_invoice_list')

        # Get invoice details (line items)
        invoice_details = TblaccSalesinvoiceDetails.objects.filter(mid=invoice)

        # Pre-populate header form
        header_form = SalesInvoiceHeaderForm(initial={
            'invoiceno': invoice.invoiceno,
            'pono': invoice.pono,
            'wono': invoice.wono,
            'category': invoice.customercategory if hasattr(invoice, 'customercategory') else None,
            'commodity': invoice.commodity if hasattr(invoice, 'commodity') else None,
            'tariffheading': invoice.tariffheading,
            'dutyrate': invoice.dutyrate,
            'transportmode': invoice.modeoftransport if hasattr(invoice, 'modeoftransport') else None,
            'rrgcno': invoice.rrgcno,
            'registrationno': invoice.vehiregno if hasattr(invoice, 'vehiregno') else None,
            'removalnature': invoice.natureofremoval if hasattr(invoice, 'natureofremoval') else None,
            'dateofissueinvoice': invoice.dateofissueinvoice,
            'timeofissueinvoice': invoice.timeofissueinvoice,
            'dateofremoval': invoice.dateofremoval,
        })

        # Pre-populate buyer form
        buyer_form = SalesInvoiceBuyerForm(initial={
            'buyer_name': invoice.buyer_name,
            'buyer_address': invoice.buyer_address,
            'buyer_country': invoice.buyer_country_id if hasattr(invoice, 'buyer_country_id') else None,
            'buyer_state': invoice.buyer_state_id if hasattr(invoice, 'buyer_state_id') else None,
            'buyer_city': invoice.buyer_city_id if hasattr(invoice, 'buyer_city_id') else None,
            'buyer_fax': invoice.buyer_fax,
            'buyer_contact_person': invoice.buyer_contact_person,
            'buyer_phone': invoice.buyer_phone,
            'buyer_tin_cst': invoice.buyer_tin_cst,
            'buyer_tin_vat': invoice.buyer_tin_vat,
            'buyer_mobile': invoice.buyer_mobile,
            'buyer_email': invoice.buyer_email,
            'buyer_ecc_no': invoice.buyer_ecc_no,
        })

        # Pre-populate consignee form
        consignee_form = SalesInvoiceConsigneeForm(initial={
            'cong_name': invoice.cong_name,
            'cong_address': invoice.cong_address,
            'cong_country': invoice.cong_country_id if hasattr(invoice, 'cong_country_id') else None,
            'cong_state': invoice.cong_state_id if hasattr(invoice, 'cong_state_id') else None,
            'cong_city': invoice.cong_city_id if hasattr(invoice, 'cong_city_id') else None,
            'cong_fax': invoice.cong_fax,
            'cong_contact_person': invoice.cong_contact_person,
            'cong_phone': invoice.cong_phone,
            'cong_tin_cst': invoice.cong_tin_cst,
            'cong_tin_vat': invoice.cong_tin_vat,
            'cong_mobile': invoice.cong_mobile,
            'cong_email': invoice.cong_email,
            'cong_ecc_no': invoice.cong_ecc_no,
        })

        # Pre-populate goods formset
        goods_initial_data = []
        for detail in invoice_details:
            goods_initial_data.append({
                'item_id': detail.itemid_id,
                'item_desc': detail.itemdesc if hasattr(detail, 'itemdesc') else '',
                'reqqty': detail.reqqty,
                'rate': detail.rate,
                'amount': detail.amount,
                'selected': True,
            })

        goods_formset = SalesInvoiceGoodsFormSet(initial=goods_initial_data)

        # Pre-populate taxation form (calculate totals)
        total_amount = sum([float(d.amount or 0) for d in invoice_details])

        taxation_form = SalesInvoiceTaxationForm(initial={
            'total_taxable_value': total_amount,
            # Add other tax fields as needed
        })

        context = {
            'invoice': invoice,
            'mode': 'edit',
            'header_form': header_form,
            'buyer_form': buyer_form,
            'consignee_form': consignee_form,
            'goods_formset': goods_formset,
            'taxation_form': taxation_form,
            'invoice_mode_display': 'Edit Mode',
        }

        return render(request, 'accounts/transactions/sales_invoice_create.html', context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Save updated invoice"""
        invoice_id = kwargs.get('invoice_id')

        try:
            invoice = TblaccSalesinvoiceMaster.objects.get(
                id=invoice_id,
                compid=request.session.get('compid')
            )
        except TblaccSalesinvoiceMaster.DoesNotExist:
            messages.error(request, 'Invoice not found')
            return redirect('accounts:sales_invoice_list')

        # Get forms
        header_form = SalesInvoiceHeaderForm(request.POST)
        buyer_form = SalesInvoiceBuyerForm(request.POST)
        consignee_form = SalesInvoiceConsigneeForm(request.POST)
        goods_formset = SalesInvoiceGoodsFormSet(request.POST)
        taxation_form = SalesInvoiceTaxationForm(request.POST)

        # Validate
        if not all([header_form.is_valid(), buyer_form.is_valid(), consignee_form.is_valid(),
                    goods_formset.is_valid(), taxation_form.is_valid()]):
            messages.error(request, 'Please correct the errors in the form')
            return self.get(request, *args, **kwargs)

        # Update invoice master
        for field, value in header_form.cleaned_data.items():
            if hasattr(invoice, field):
                setattr(invoice, field, value)

        for field, value in buyer_form.cleaned_data.items():
            if hasattr(invoice, field):
                setattr(invoice, field, value)

        for field, value in consignee_form.cleaned_data.items():
            if hasattr(invoice, field):
                setattr(invoice, field, value)

        # Update audit fields
        invoice.systime = datetime.now().strftime('%H:%M:%S')
        invoice.sessionid = str(request.user.id)

        invoice.save()

        # Update invoice details - delete old, create new
        TblaccSalesinvoiceDetails.objects.filter(mid=invoice).delete()

        for form in goods_formset:
            if form.cleaned_data.get('selected'):
                TblaccSalesinvoiceDetails.objects.create(
                    mid=invoice,
                    itemid_id=form.cleaned_data['item_id'],
                    reqqty=form.cleaned_data['reqqty'],
                    rate=form.cleaned_data['rate'],
                    amount=form.cleaned_data['amount'],
                )

        messages.success(request, f'Invoice {invoice.invoiceno} updated successfully')
        return redirect('accounts:sales_invoice_list')


class SalesInvoiceDeleteView(CompanyFinancialYearMixin, View):
    """Delete existing sales invoice and restore quantities to PO."""

    def get(self, request, *args, **kwargs):
        """Display delete confirmation page."""
        invoice_id = kwargs.get('invoice_id')

        try:
            # Get invoice filtered by company (security)
            invoice = TblaccSalesinvoiceMaster.objects.get(
                id=invoice_id,
                compid=request.session.get('compid')
            )
        except TblaccSalesinvoiceMaster.DoesNotExist:
            messages.error(request, 'Invoice not found or access denied')
            return redirect('accounts:sales_invoice_list')

        # Get invoice details for display
        invoice_details = TblaccSalesinvoiceDetails.objects.filter(mid=invoice)

        context = {
            'invoice': invoice,
            'invoice_details': invoice_details,
            'total_amount': sum(detail.amount or 0 for detail in invoice_details),
            'total_items': invoice_details.count(),
        }

        return render(request, 'accounts/transactions/sales_invoice_delete.html', context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Confirm deletion and restore quantities."""
        invoice_id = kwargs.get('invoice_id')

        try:
            # Get invoice filtered by company (security)
            invoice = TblaccSalesinvoiceMaster.objects.get(
                id=invoice_id,
                compid=request.session.get('compid')
            )
        except TblaccSalesinvoiceMaster.DoesNotExist:
            messages.error(request, 'Invoice not found or access denied')
            return redirect('accounts:sales_invoice_list')

        invoice_number = invoice.invoiceno

        # Delete invoice details first (cascade)
        # Note: Quantities are automatically restored because when we delete invoice details,
        # the remaining quantity calculation will no longer include them
        TblaccSalesinvoiceDetails.objects.filter(mid=invoice).delete()

        # Delete invoice master
        invoice.delete()

        messages.success(request, f'Invoice {invoice_number} deleted successfully. Quantities restored to PO.')
        return redirect('accounts:sales_invoice_list')


class SalesInvoicePrintView(CompanyFinancialYearMixin, View):
    """Generate print-friendly view of sales invoice."""

    def get(self, request, *args, **kwargs):
        """Display invoice in print format."""
        invoice_id = kwargs.get('invoice_id')

        try:
            # Get invoice filtered by company (security)
            invoice = TblaccSalesinvoiceMaster.objects.select_related('poid').get(
                id=invoice_id,
                compid=request.session.get('compid')
            )
        except TblaccSalesinvoiceMaster.DoesNotExist:
            messages.error(request, 'Invoice not found or access denied')
            return redirect('accounts:sales_invoice_list')

        # Get invoice details with related item information
        invoice_details = TblaccSalesinvoiceDetails.objects.filter(mid=invoice).select_related(
            'itemid__itemid'
        )

        # Calculate totals
        subtotal = sum(detail.amount or 0 for detail in invoice_details)
        total_qty = sum(detail.reqqty or 0 for detail in invoice_details)

        # Tax calculations (if applicable)
        # These fields might exist in the model - adapt as needed
        tax_amount = getattr(invoice, 'taxamount', 0) or 0
        excise_duty = getattr(invoice, 'exciseduty', 0) or 0
        freight = getattr(invoice, 'freight', 0) or 0

        grand_total = subtotal + tax_amount + excise_duty + freight

        context = {
            'invoice': invoice,
            'invoice_details': invoice_details,
            'subtotal': subtotal,
            'total_qty': total_qty,
            'tax_amount': tax_amount,
            'excise_duty': excise_duty,
            'freight': freight,
            'grand_total': grand_total,
            'total_items': invoice_details.count(),
        }

        return render(request, 'accounts/transactions/sales_invoice_print.html', context)


