"""
Service Tax Invoice Views
Implements service tax invoice management with PO selection and multi-tab form

Similar to Sales Invoice but for service-based transactions
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.db import transaction
from django.db.models import Sum, Q, F
from datetime import datetime
from decimal import Decimal
import json

from accounts.models import (
    TblaccServicetaxinvoiceMaster,
    TblaccServicetaxinvoiceDetails,
    TblaccServiceCategory,
)
from sales_distribution.models import (
    SdCustMaster,
    SdCustPoMaster,
    SdCustPoDetails,
    SdCustWorkorderMaster,
)
from sys_admin.models import (
    TblfinancialMaster,
    Tblcountry,
    Tblstate,
    Tblcity,
)
from core.mixins import CompanyFinancialYearMixin


# =============================================================================
# SERVICE TAX INVOICE LIST
# =============================================================================

@login_required
def service_tax_invoice_list(request):
    """
    List all service tax invoices with search and pagination
    """
    compid = request.session.get('compid', 1)
    finyearid = request.session.get('finyearid', 1)

    # Get search parameters
    search = request.GET.get('search', '')

    # Base queryset
    invoices = TblaccServicetaxinvoiceMaster.objects.filter(
        compid=compid,
        finyearid=finyearid
    ).order_by('-id')

    # Apply search
    if search:
        invoices = invoices.filter(
            Q(invoiceno__icontains=search) |
            Q(pono__icontains=search) |
            Q(wono__icontains=search) |
            Q(buyer_name__icontains=search)
        )

    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
    }

    return render(request, 'accounts/transactions/service_tax_invoice_list.html', context)


# =============================================================================
# SERVICE TAX INVOICE CREATE
# =============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def service_tax_invoice_create(request):
    """
    Create service tax invoice with PO selection and multi-tab form
    """
    compid = request.session.get('compid', 1)
    finyearid = request.session.get('finyearid', 1)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Generate invoice number
                last_invoice = TblaccServicetaxinvoiceMaster.objects.filter(
                    compid=compid,
                    finyearid=finyearid
                ).order_by('-id').first()

                if last_invoice and last_invoice.invoiceno:
                    try:
                        # Extract number from format: STI/YYYY-YY/XXXX
                        parts = last_invoice.invoiceno.split('/')
                        if len(parts) == 3:
                            last_num = int(parts[2])
                            new_num = last_num + 1
                        else:
                            new_num = 1
                    except (ValueError, IndexError):
                        new_num = 1
                else:
                    new_num = 1

                # Get financial year
                finyear = TblfinancialMaster.objects.filter(finyearid=finyearid).first()
                finyear_str = finyear.finyear if finyear else '2025-26'

                invoiceno = f"STI/{finyear_str}/{new_num:04d}"

                # Get form data
                poid = request.POST.get('poid')
                pono = request.POST.get('pono')
                wono = request.POST.get('wono')

                # Create master record
                now = datetime.now()
                master = TblaccServicetaxinvoiceMaster(
                    sysdate=now.strftime('%d-%m-%Y'),
                    systime=now.strftime('%H:%M:%S'),
                    compid=compid,
                    finyearid=finyearid,
                    sessionid=str(request.user.id),
                    invoiceno=invoiceno,
                    poid=int(poid) if poid else None,
                    pono=pono,
                    wono=wono,
                    dateofissueinvoice=request.POST.get('dateofissueinvoice', now.strftime('%d-%m-%Y')),
                    timeofissueinvoice=request.POST.get('timeofissueinvoice', now.strftime('%H:%M:%S')),
                    customercode=request.POST.get('customercode', ''),
                    # Buyer details
                    buyer_name=request.POST.get('buyer_name'),
                    buyer_add=request.POST.get('buyer_add'),
                    buyer_state=int(request.POST.get('buyer_state')) if request.POST.get('buyer_state') else None,
                    buyer_country=int(request.POST.get('buyer_country')) if request.POST.get('buyer_country') else None,
                    buyer_city_id=int(request.POST.get('buyer_city')) if request.POST.get('buyer_city') else None,
                    buyer_cotper=request.POST.get('buyer_cotper'),
                    buyer_ph=request.POST.get('buyer_ph'),
                    buyer_email=request.POST.get('buyer_email'),
                    buyer_ecc=request.POST.get('buyer_ecc'),
                    buyer_tin=request.POST.get('buyer_tin'),
                    buyer_mob=request.POST.get('buyer_mob'),
                    buyer_fax=request.POST.get('buyer_fax'),
                    buyer_vat=request.POST.get('buyer_vat'),
                    # Consignee details
                    cong_name=request.POST.get('cong_name'),
                    cong_add=request.POST.get('cong_add'),
                    cong_state=int(request.POST.get('cong_state')) if request.POST.get('cong_state') else None,
                    cong_country=int(request.POST.get('cong_country')) if request.POST.get('cong_country') else None,
                    cong_city_id=int(request.POST.get('cong_city')) if request.POST.get('cong_city') else None,
                    cong_cotper=request.POST.get('cong_cotper', ''),
                    cong_ph=request.POST.get('cong_ph'),
                    cong_email=request.POST.get('cong_email', ''),
                    cong_ecc=request.POST.get('cong_ecc', ''),
                    cong_tin=request.POST.get('cong_tin'),
                    cong_mob=request.POST.get('cong_mob'),
                    cong_fax=request.POST.get('cong_fax'),
                    cong_vat=request.POST.get('cong_vat'),
                    # Tax details
                    servicetax=int(request.POST.get('servicetax')) if request.POST.get('servicetax') else None,
                    taxableservices=int(request.POST.get('taxableservices')) if request.POST.get('taxableservices') else None,
                    addtype=int(request.POST.get('addtype')) if request.POST.get('addtype') else None,
                    addamt=float(request.POST.get('addamt', 0)),
                    deductiontype=int(request.POST.get('deductiontype')) if request.POST.get('deductiontype') else None,
                    deduction=float(request.POST.get('deduction', 0)),
                )
                master.save()

                # Create detail records
                item_ids = request.POST.getlist('item_id[]')
                qtys = request.POST.getlist('qty[]')
                rates = request.POST.getlist('rate[]')
                units = request.POST.getlist('unit[]')

                for i, item_id in enumerate(item_ids):
                    if item_id and qtys[i]:
                        detail = TblaccServicetaxinvoiceDetails(
                            mid=master,
                            invoiceno=invoiceno,
                            itemid=int(item_id),
                            qty=float(qtys[i]),
                            reqqty=float(qtys[i]),  # Default to same as qty
                            rate=float(rates[i]) if i < len(rates) and rates[i] else 0,
                            unit=int(units[i]) if i < len(units) and units[i] else None,
                            amtinper=0,  # Can be calculated
                        )
                        detail.save()

                messages.success(request, f'Service Tax Invoice {invoiceno} created successfully!')
                return redirect('accounts:service-tax-invoice-list')

        except Exception as e:
            messages.error(request, f'Error creating service tax invoice: {str(e)}')
            return redirect('accounts:service-tax-invoice-create')

    # GET request - show form
    # Get pending POs for selection
    pos = SdCustPoMaster.objects.filter(
        compid=compid,
        finyearid=finyearid
    ).order_by('-id')[:50]

    context = {
        'pos': pos,
        'countries': Tblcountry.objects.all(),
    }

    return render(request, 'accounts/transactions/service_tax_invoice_create.html', context)


# =============================================================================
# SERVICE TAX INVOICE EDIT
# =============================================================================

@login_required
@require_http_methods(["GET", "POST"])
def service_tax_invoice_edit(request, invoice_id):
    """
    Edit existing service tax invoice
    """
    invoice = get_object_or_404(TblaccServicetaxinvoiceMaster, id=invoice_id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update master
                invoice.dateofissueinvoice = request.POST.get('dateofissueinvoice')
                invoice.buyer_name = request.POST.get('buyer_name')
                invoice.buyer_add = request.POST.get('buyer_add')
                invoice.buyer_state = int(request.POST.get('buyer_state')) if request.POST.get('buyer_state') else None
                invoice.buyer_country = int(request.POST.get('buyer_country')) if request.POST.get('buyer_country') else None
                invoice.buyer_city_id = int(request.POST.get('buyer_city')) if request.POST.get('buyer_city') else None
                invoice.buyer_ph = request.POST.get('buyer_ph')
                invoice.buyer_email = request.POST.get('buyer_email')
                invoice.cong_name = request.POST.get('cong_name')
                invoice.cong_add = request.POST.get('cong_add')
                invoice.cong_state = int(request.POST.get('cong_state')) if request.POST.get('cong_state') else None
                invoice.cong_country = int(request.POST.get('cong_country')) if request.POST.get('cong_country') else None
                invoice.cong_city_id = int(request.POST.get('cong_city')) if request.POST.get('cong_city') else None
                invoice.servicetax = int(request.POST.get('servicetax')) if request.POST.get('servicetax') else None
                invoice.save()

                messages.success(request, 'Service Tax Invoice updated successfully!')
                return redirect('accounts:service-tax-invoice-list')

        except Exception as e:
            messages.error(request, f'Error updating service tax invoice: {str(e)}')

    # GET request - show form
    details = TblaccServicetaxinvoiceDetails.objects.filter(mid=invoice)

    context = {
        'invoice': invoice,
        'details': details,
        'countries': Tblcountry.objects.all(),
    }

    return render(request, 'accounts/transactions/service_tax_invoice_edit.html', context)


# =============================================================================
# SERVICE TAX INVOICE DELETE
# =============================================================================

@login_required
@require_POST
def service_tax_invoice_delete(request, invoice_id):
    """
    Delete service tax invoice
    """
    invoice = get_object_or_404(TblaccServicetaxinvoiceMaster, id=invoice_id)

    try:
        # Delete details first (foreign key)
        TblaccServicetaxinvoiceDetails.objects.filter(mid=invoice).delete()
        # Delete master
        invoiceno = invoice.invoiceno
        invoice.delete()

        messages.success(request, f'Service Tax Invoice {invoiceno} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting service tax invoice: {str(e)}')

    return redirect('accounts:service-tax-invoice-list')


# =============================================================================
# SERVICE TAX INVOICE PRINT
# =============================================================================

@login_required
def service_tax_invoice_print(request, invoice_id):
    """
    Print service tax invoice
    """
    invoice = get_object_or_404(TblaccServicetaxinvoiceMaster, id=invoice_id)
    details = TblaccServicetaxinvoiceDetails.objects.filter(mid=invoice)

    context = {
        'invoice': invoice,
        'details': details,
    }

    return render(request, 'accounts/transactions/service_tax_invoice_print.html', context)


# =============================================================================
# HTMX ENDPOINTS
# =============================================================================

@login_required
@require_GET
def get_states_by_country(request):
    """Get states by country for cascade dropdown"""
    country_id = request.GET.get('country_id')
    states = Tblstate.objects.filter(countryid=country_id).order_by('state')

    return JsonResponse({
        'states': [{'id': s.stateid, 'name': s.state} for s in states]
    })


@login_required
@require_GET
def get_cities_by_state(request):
    """Get cities by state for cascade dropdown"""
    state_id = request.GET.get('state_id')
    cities = Tblcity.objects.filter(stateid=state_id).order_by('city')

    return JsonResponse({
        'cities': [{'id': c.cityid, 'name': c.city} for c in cities]
    })


@login_required
@require_GET
def customer_autocomplete(request):
    """Autocomplete for customer search"""
    term = request.GET.get('term', '')
    customers = SdCustMaster.objects.filter(
        customername__icontains=term
    )[:10]

    return JsonResponse({
        'results': [{'id': c.customerid, 'text': c.customername} for c in customers]
    })


@login_required
@require_POST
def copy_buyer_to_consignee(request):
    """Copy buyer details to consignee"""
    # This is handled client-side via JavaScript
    # Returning success for HTMX
    return JsonResponse({'status': 'success'})
