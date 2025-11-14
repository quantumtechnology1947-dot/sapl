"""
Purchase Order (PO) Views
Converted from ASP.NET Material Management PO module
Following exact business logic from:
- PO_New.aspx
- PO_PR_Items.aspx  
- PO_SPR_Items.aspx
- PO_Check.aspx
- PO_Approve.aspx
- PO_Authorize.aspx
"""

from datetime import datetime, date
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, F, Max
from django.db import transaction, connection
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import (
    Supplier, POMaster, PODetails, PRMaster, PRDetails,
    SPRMaster, SPRDetails, MmPrPoTemp, MmSprPoTemp,
    RateRegister, RateLockUnlock
)
from accounts.models import (
    TblpaymentMaster, TblwarrentyMaster, TblfreightMaster,
    TbloctroiMaster, TblpackingMaster, TblexciseserMaster,
    TblvatMaster
)
from design.models import TbldgItemMaster


# Helper function to get company and financial year from session
def get_company_and_financial_year(request):
    """Get company_id and fin_year_id from session"""
    comp_id = request.session.get('active_company_id')
    fin_year_id = request.session.get('active_finyear_id')
    
    if not comp_id or not fin_year_id:
        # Fallback to defaults if not in session
        comp_id = 1
        fin_year_id = 1
    
    return comp_id, fin_year_id


# =============================================================================
# PO CREATION VIEWS
# =============================================================================

@login_required
def po_list(request):
    """
    PO List - View all Purchase Orders
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    context = {
        'page_title': 'PO Dashboard',
        'breadcrumbs': [
            {'name': 'Material Management', 'url': '/material-management/'},
            {'name': 'PO Dashboard', 'url': ''}
        ]
    }
    
    return render(request, 'material_management/po/list.html', context)


@login_required
def po_list_api(request):
    """
    API: Get PO list data - Real database query
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    # Get search parameters
    field = request.GET.get('field', '')
    value = request.GET.get('value', '')
    
    try:
        # Base query - get non-authorized POs (SQLite compatible - format dates in Python)
        query = """
            SELECT 
                p.Id,
                p.PONo,
                p.SysDate as Date,
                p.SysTime as Time,
                p.SessionId as GenBy,
                COALESCE(s.SupplierName, '') as Sup,
                COALESCE(s.SupplierId, '') as Code,
                p.Checked,
                p.CheckedDate,
                p.Approve,
                p.ApproveDate,
                p.Authorize,
                p.AuthorizeDate,
                COALESCE(fy.FinYear, '') as FinYear
            FROM tblMM_PO_Master p
            LEFT JOIN tblMM_Supplier_master s ON p.SupplierId = s.SupplierId
            LEFT JOIN tblFinancial_master fy ON p.FinYearId = fy.FinYearId
            WHERE p.CompId = ? AND p.Authorize = 0
        """
        
        params = [comp_id]
        
        # Add search filters
        if field and value:
            if field == 'supplier':
                query += " AND s.SupplierName LIKE ?"
                params.append('%%' + value + '%%')  # Escape % for Django's SQL logging
            elif field == 'po_no':
                query += " AND p.PONo LIKE ?"
                params.append('%%' + value + '%%')  # Escape % for Django's SQL logging
        
        query += " ORDER BY p.Id DESC"
        
        # Build final query with values embedded to avoid % formatting issues
        final_query = query.replace('?', str(comp_id), 1)
        if field and value:
            final_query = final_query.replace('?', f"'%%{value}%%'")
        
        with connection.cursor() as cursor:
            cursor.execute(final_query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            pos = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                
                # Format dates in Python
                if row_dict.get('Date'):
                    try:
                        date_obj = datetime.strptime(row_dict['Date'], '%Y-%m-%d')
                        row_dict['Date'] = date_obj.strftime('%d-%m-%Y')
                    except:
                        pass
                
                # Format checked date
                if row_dict.get('Checked') == 1 and row_dict.get('CheckedDate'):
                    try:
                        date_obj = datetime.strptime(row_dict['CheckedDate'], '%Y-%m-%d')
                        row_dict['CheckedDate'] = date_obj.strftime('%d-%m-%Y')
                    except:
                        row_dict['CheckedDate'] = ''
                else:
                    row_dict['CheckedDate'] = ''
                
                # Format approved date
                if row_dict.get('Approve') == 1 and row_dict.get('ApproveDate'):
                    try:
                        date_obj = datetime.strptime(row_dict['ApproveDate'], '%Y-%m-%d')
                        row_dict['ApprovedDate'] = date_obj.strftime('%d-%m-%Y')
                    except:
                        row_dict['ApprovedDate'] = ''
                else:
                    row_dict['ApprovedDate'] = ''
                
                # Format authorized date
                if row_dict.get('Authorize') == 1 and row_dict.get('AuthorizeDate'):
                    try:
                        date_obj = datetime.strptime(row_dict['AuthorizeDate'], '%Y-%m-%d')
                        row_dict['AuthorizedDate'] = date_obj.strftime('%d-%m-%Y')
                    except:
                        row_dict['AuthorizedDate'] = ''
                else:
                    row_dict['AuthorizedDate'] = ''
                
                # Remove internal fields
                row_dict.pop('Checked', None)
                row_dict.pop('Approve', None)
                row_dict.pop('Authorize', None)
                
                pos.append(row_dict)
        
        return JsonResponse({'pos': pos})
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'pos': []
        })


@login_required
def po_new(request):
    """
    PO New - Supplier Selection
    Converted from: PO_New.aspx
    
    Two tabs:
    1. PR - Create PO from Purchase Requisitions
    2. SPR - Create PO from Special Purchase Requisitions
    
    NOTE: Page loads empty - user must click Search to load data
    This matches ASP.NET behavior for fast page load
    """
    context = {
        'page_title': 'PO - New',
        'breadcrumbs': [
            {'name': 'Material Management', 'url': '/material-management/'},
            {'name': 'PO - New', 'url': ''}
        ]
    }
    
    return render(request, 'material_management/po/new.html', context)


@login_required
def po_pr_suppliers_api(request):
    """
    API: Get all suppliers (regardless of PR status or financial year)
    Used in PO_New PR tab
    Shows all suppliers with count of approved PR items (if any)
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    search = request.GET.get('search', '')

    # Get ALL suppliers with count of approved PR items
    # User requirement: Show all suppliers regardless of financial year or PR status
    query = """
        SELECT
            s.SupplierId AS Code,
            s.SupplierName AS Supplier,
            COALESCE(COUNT(DISTINCT CASE WHEN prm.Authorize = 1 THEN prd.Id END), 0) AS Items
        FROM tblMM_Supplier_master s
        LEFT JOIN tblMM_PR_Details prd ON s.SupplierId = prd.SupplierId
        LEFT JOIN tblMM_PR_Master prm ON prd.MId = prm.Id AND prd.PRNo = prm.PRNo AND prm.CompId = %s
        WHERE 1=1
    """

    params = [comp_id]

    # Add search filter only if search term is provided
    if search:
        query += " AND (s.SupplierName LIKE %s OR s.SupplierId LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    query += " GROUP BY s.SupplierId, s.SupplierName ORDER BY s.SupplierName"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({'suppliers': results})


@login_required
def po_spr_suppliers_api(request):
    """
    API: Get all suppliers (regardless of SPR status or financial year)
    Used in PO_New SPR tab
    Shows all suppliers with count of approved SPR items (if any)
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    search = request.GET.get('search', '')

    # Get ALL suppliers with count of approved SPR items
    # User requirement: Show all suppliers regardless of financial year or SPR status
    query = """
        SELECT
            s.SupplierId AS Code,
            s.SupplierName AS Supplier,
            COALESCE(COUNT(DISTINCT CASE WHEN sprm.Authorize = 1 THEN sprd.Id END), 0) AS Items
        FROM tblMM_Supplier_master s
        LEFT JOIN tblMM_SPR_Details sprd ON s.SupplierId = sprd.SupplierId
        LEFT JOIN tblMM_SPR_Master sprm ON sprd.MId = sprm.Id AND sprd.SPRNo = sprm.SPRNo AND sprm.CompId = %s
        WHERE 1=1
    """

    params = [comp_id]

    # Add search filter only if search term is provided
    if search:
        query += " AND (s.SupplierName LIKE %s OR s.SupplierId LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    query += " GROUP BY s.SupplierId, s.SupplierName ORDER BY s.SupplierName"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({'suppliers': results})


@login_required
def po_pr_suppliers_htmx(request):
    """
    HTMX endpoint: Get PR suppliers with real-time search
    Returns HTML partial for live filtering
    Shows only suppliers that have PR items (regardless of authorization status)
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    search = request.GET.get('search', '').strip()

    # Get only suppliers that have PR items with their item count
    # Note: No Authorize filter - show all PR items available for PO creation
    query = """
        SELECT
            s.SupplierId AS Code,
            s.SupplierName AS Supplier,
            COUNT(DISTINCT prd.Id) AS Items
        FROM tblMM_Supplier_master s
        INNER JOIN tblMM_PR_Details prd ON s.SupplierId = prd.SupplierId
        INNER JOIN tblMM_PR_Master prm ON prd.MId = prm.Id AND prd.PRNo = prm.PRNo
        WHERE prm.CompId = %s
    """

    params = [comp_id]

    # Add search filter if provided
    if search:
        query += " AND (s.SupplierName LIKE %s OR s.SupplierId LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    query += " GROUP BY s.SupplierId, s.SupplierName HAVING COUNT(DISTINCT prd.Id) > 0 ORDER BY s.SupplierName"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Transform to template-friendly format
    suppliers = [{'code': r['Code'], 'name': r['Supplier'], 'items': r['Items']} for r in results]

    return render(request, 'material_management/po/partials/supplier_grid.html', {
        'suppliers': suppliers,
        'search_query': search,
        'tab_type': 'pr'
    })


@login_required
def po_spr_suppliers_htmx(request):
    """
    HTMX endpoint: Get SPR suppliers with real-time search
    Returns HTML partial for live filtering
    Shows only suppliers that have SPR items (regardless of authorization status)
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    search = request.GET.get('search', '').strip()

    # Get only suppliers that have SPR items with their item count
    # Note: No Authorize filter - show all SPR items available for PO creation
    query = """
        SELECT
            s.SupplierId AS Code,
            s.SupplierName AS Supplier,
            COUNT(DISTINCT sprd.Id) AS Items
        FROM tblMM_Supplier_master s
        INNER JOIN tblMM_SPR_Details sprd ON s.SupplierId = sprd.SupplierId
        INNER JOIN tblMM_SPR_Master sprm ON sprd.MId = sprm.Id AND sprd.SPRNo = sprm.SPRNo
        WHERE sprm.CompId = %s
    """

    params = [comp_id]

    # Add search filter if provided
    if search:
        query += " AND (s.SupplierName LIKE %s OR s.SupplierId LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    query += " GROUP BY s.SupplierId, s.SupplierName HAVING COUNT(DISTINCT sprd.Id) > 0 ORDER BY s.SupplierName"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Transform to template-friendly format
    suppliers = [{'code': r['Code'], 'name': r['Supplier'], 'items': r['Items']} for r in results]

    return render(request, 'material_management/po/partials/supplier_grid.html', {
        'suppliers': suppliers,
        'search_query': search,
        'tab_type': 'spr'
    })


@login_required
def po_pr_suppliers_count_htmx(request):
    """
    HTMX endpoint: Get count of PR suppliers (that have PR items)
    Returns just the number for the tab counter
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)

    query = """
        SELECT COUNT(DISTINCT s.SupplierId)
        FROM tblMM_Supplier_master s
        INNER JOIN tblMM_PR_Details prd ON s.SupplierId = prd.SupplierId
        INNER JOIN tblMM_PR_Master prm ON prd.MId = prm.Id AND prd.PRNo = prm.PRNo
        WHERE prm.CompId = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [comp_id])
        count = cursor.fetchone()[0]

    from django.http import HttpResponse
    return HttpResponse(str(count))


@login_required
def po_spr_suppliers_count_htmx(request):
    """
    HTMX endpoint: Get count of SPR suppliers (that have SPR items)
    Returns just the number for the tab counter
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)

    query = """
        SELECT COUNT(DISTINCT s.SupplierId)
        FROM tblMM_Supplier_master s
        INNER JOIN tblMM_SPR_Details sprd ON s.SupplierId = sprd.SupplierId
        INNER JOIN tblMM_SPR_Master sprm ON sprd.MId = sprm.Id AND sprd.SPRNo = sprm.SPRNo
        WHERE sprm.CompId = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [comp_id])
        count = cursor.fetchone()[0]

    from django.http import HttpResponse
    return HttpResponse(str(count))


@login_required
def po_pr_items(request, supplier_code):
    """
    PO from PR Items
    Converted from: PO_PR_Items.aspx
    
    Three tabs:
    1. PR Items - Select items from approved PRs
    2. Selected Items - Review selected items
    3. Terms & Conditions - Enter PO terms
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    # Get supplier details
    supplier = get_object_or_404(
        Supplier,
        supplier_id=supplier_code,
        comp_id=comp_id
    )

    # Format supplier address
    supplier_address = format_supplier_address(supplier)

    # Get company address for Ship To
    company_address = get_company_address(comp_id)

    # Get default terms & conditions
    default_tc = get_default_po_terms()

    # Get master data for dropdowns
    references = get_po_references()
    payment_terms = TblpaymentMaster.objects.all()
    warrenty_terms = TblwarrentyMaster.objects.all()
    freight_terms = TblfreightMaster.objects.all()
    octroi_terms = TbloctroiMaster.objects.all()

    context = {
        'page_title': 'PO - For PR Items',
        'supplier': supplier,
        'supplier_code': supplier_code,
        'supplier_address': supplier_address,
        'company_address': company_address,
        'default_tc': default_tc,
        'references': references,
        'payment_terms': payment_terms,
        'warrenty_terms': warrenty_terms,
        'freight_terms': freight_terms,
        'octroi_terms': octroi_terms,
        'breadcrumbs': [
            {'name': 'Material Management', 'url': '/material-management/'},
            {'name': 'PO - New', 'url': '/material-management/po/new/'},
            {'name': 'PR Items', 'url': ''}
        ]
    }
    
    return render(request, 'material_management/po/pr_items.html', context)


@login_required
def po_spr_items(request, supplier_code):
    """
    PO from SPR Items
    Converted from: PO_SPR_Items.aspx
    
    Three tabs:
    1. SPR Items - Select items from approved SPRs
    2. Selected Items - Review selected items
    3. Terms & Conditions - Enter PO terms
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    # Get supplier details
    supplier = get_object_or_404(
        Supplier,
        supplier_id=supplier_code,
        comp_id=comp_id
    )
    
    # Get company address for Ship To
    company_address = get_company_address(comp_id)
    
    # Get default terms & conditions
    default_tc = get_default_po_terms()
    
    # Get master data for dropdowns
    references = get_po_references()
    payment_terms = TblpaymentMaster.objects.all()
    warrenty_terms = TblwarrentyMaster.objects.all()
    freight_terms = TblfreightMaster.objects.all()
    octroi_terms = TbloctroiMaster.objects.all()
    
    context = {
        'page_title': 'PO - For SPR Items',
        'supplier': supplier,
        'supplier_code': supplier_code,
        'company_address': company_address,
        'default_tc': default_tc,
        'references': references,
        'payment_terms': payment_terms,
        'warrenty_terms': warrenty_terms,
        'freight_terms': freight_terms,
        'octroi_terms': octroi_terms,
        'breadcrumbs': [
            {'name': 'Material Management', 'url': '/material-management/'},
            {'name': 'PO - New', 'url': '/material-management/po/new/'},
            {'name': 'SPR Items', 'url': ''}
        ]
    }
    
    return render(request, 'material_management/po/spr_items.html', context)


# =============================================================================
# PO ITEMS API
# =============================================================================

@login_required
def po_pr_items_grid(request):
    """
    PR Items Grid Iframe
    Converted from: PO_PR_ItemGrid.aspx
    """
    response = render(request, 'material_management/po/pr_items_grid.html')
    # Prevent browser caching of this template
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required
def po_pr_items_grid_api(request):
    """
    API: Get PR items for selected supplier
    Converted from: PO_PR_ItemGrid.aspx
    Shows items not yet added to PO (not in temp table)
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    supplier_code = request.GET.get('supplier')
    session_id = request.user.username
    
    if not supplier_code:
        return JsonResponse({'error': 'Supplier code required'}, status=400)
    
    # Get PR items for this supplier that are not in temp table
    # Note: No Authorize or FinYearId filters - show all available PR items like ASP.NET
    query = """
        SELECT
            prd.Id,
            prm.PRNo,
            prm.WONo,
            item.ItemCode,
            item.ManfDesc AS PurchDesc,
            unit.Symbol AS UOMPurch,
            prd.Qty AS PRQty,
            (prd.Qty - COALESCE((
                SELECT SUM(pod.Qty)
                FROM tblMM_PO_Details pod
                WHERE pod.PRId = prd.Id
            ), 0)) AS RemainQty,
            prd.Rate,
            prd.Discount,
            prd.DelDate,
            COALESCE(ah.Symbol || ' ' || ah.Description, '') AS AcHead,
            prd.AHId,
            prd.ItemId
        FROM tblMM_PR_Details prd
        INNER JOIN tblMM_PR_Master prm ON prd.MId = prm.Id AND prd.PRNo = prm.PRNo
        INNER JOIN tblDG_Item_Master item ON prd.ItemId = item.Id
        INNER JOIN Unit_Master unit ON item.UOMBasic = unit.Id
        LEFT JOIN AccHead ah ON prd.AHId = ah.Id
        WHERE prm.CompId = %s
            AND prd.SupplierId = %s
            AND prd.Id NOT IN (
                SELECT PRId FROM tblMM_PR_Po_Temp
                WHERE CompId = %s AND SessionId = %s AND PRId IS NOT NULL
            )
            AND (prd.Qty - COALESCE((
                SELECT SUM(pod.Qty)
                FROM tblMM_PO_Details pod
                WHERE pod.PRId = prd.Id
            ), 0)) > 0
        ORDER BY prm.PRNo, item.ItemCode
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [comp_id, supplier_code, comp_id, session_id])
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse({'items': results})


@login_required
def po_spr_items_grid(request):
    """
    SPR Items Grid Iframe
    Converted from: PO_SPR_ItemGrid.aspx
    """
    return render(request, 'material_management/po/spr_items_grid.html')


@login_required
def po_spr_items_grid_api(request):
    """
    API: Get SPR items for selected supplier
    Converted from: PO_SPR_ItemGrid.aspx
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    supplier_code = request.GET.get('supplier_code')
    
    if not supplier_code:
        return JsonResponse({'error': 'Supplier code required'}, status=400)
    
    # Get SPR items for this supplier that haven't been added to PO yet
    # Note: No Authorize or FinYearId filters - show all available SPR items like ASP.NET
    query = """
        SELECT
            sprd.Id,
            sprm.SPRNo,
            sprd.WONo,
            item.ItemCode,
            item.ManfDesc AS PurchDesc,
            unit.Symbol AS UOMPurch,
            sprd.Qty,
            sprd.Rate,
            sprd.Discount,
            sprd.DelDate,
            COALESCE(ah.Symbol || ' ' || ah.Description, '') AS AcHead,
            sprd.AHId,
            sprd.ItemId,
            dept.DeptName AS Dept
        FROM tblMM_SPR_Details sprd
        INNER JOIN tblMM_SPR_Master sprm ON sprd.MId = sprm.Id AND sprd.SPRNo = sprm.SPRNo
        INNER JOIN tblDG_Item_Master item ON sprd.ItemId = item.Id
        INNER JOIN Unit_Master unit ON item.UOMBasic = unit.Id
        LEFT JOIN AccHead ah ON sprd.AHId = ah.Id
        LEFT JOIN tblHR_Department dept ON sprd.DeptId = dept.Id
        WHERE sprm.CompId = %s
            AND sprd.SupplierId = %s
            AND sprd.Id NOT IN (
                SELECT SPRId FROM tblMM_PO_Details WHERE SPRId IS NOT NULL
            )
        ORDER BY sprm.SPRNo, item.ItemCode
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [comp_id, supplier_code])
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse({'items': results})


@login_required
@require_http_methods(["POST"])
def po_add_pr_item_to_temp(request):
    """
    Add PR item to temporary table
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    session_id = request.user.username
    
    pr_id = request.POST.get('pr_id')
    pr_no = request.POST.get('pr_no')
    qty = request.POST.get('qty')
    rate = request.POST.get('rate')
    discount = request.POST.get('discount', 0)
    add_desc = request.POST.get('add_desc', '')
    pf = request.POST.get('pf') or None
    ex_st = request.POST.get('ex_st') or None
    vat = request.POST.get('vat') or None
    del_date = request.POST.get('del_date')
    budget_code = request.POST.get('budget_code')
    
    try:
        MmPrPoTemp.objects.create(
            comp_id=comp_id,
            session_id=session_id,
            pr_no=pr_no,
            pr_id=pr_id,
            qty=qty,
            rate=rate,
            discount=discount,
            add_desc=add_desc,
            pf=pf,
            ex_st=ex_st,
            vat=vat,
            del_date=del_date,
            budget_code=budget_code
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def po_add_spr_item_to_temp(request):
    """
    Add SPR item to temporary table
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    session_id = request.user.username
    
    spr_id = request.POST.get('spr_id')
    spr_no = request.POST.get('spr_no')
    qty = request.POST.get('qty')
    rate = request.POST.get('rate')
    discount = request.POST.get('discount', 0)
    add_desc = request.POST.get('add_desc', '')
    pf = request.POST.get('pf') or None
    ex_st = request.POST.get('ex_st') or None
    vat = request.POST.get('vat') or None
    del_date = request.POST.get('del_date')
    budget_code = request.POST.get('budget_code')
    
    try:
        MmSprPoTemp.objects.create(
            comp_id=comp_id,
            session_id=session_id,
            spr_no=spr_no,
            spr_id=spr_id,
            qty=qty,
            rate=rate,
            discount=discount,
            add_desc=add_desc,
            pf=pf,
            ex_st=ex_st,
            vat=vat,
            del_date=del_date,
            budget_code=budget_code
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def po_selected_pr_items_api(request):
    """
    API: Get selected PR items from temp table - Using Django ORM
    """
    from django.db.models import F, Q, Value, CharField, DecimalField, ExpressionWrapper
    from django.db.models.functions import Coalesce, Concat
    from decimal import Decimal

    comp_id, fin_year_id = get_company_and_financial_year(request)
    session_id = request.user.username

    # Get temp items using Django ORM
    temp_items = MmPrPoTemp.objects.filter(
        comp_id=comp_id,
        session_id=session_id
    ).order_by('pr_no')

    results = []
    for temp in temp_items:
        # Manually fetch related objects since pr_id is IntegerField, not ForeignKey
        try:
            pr_detail = PRDetails.objects.get(id=temp.pr_id)
            pr_master = pr_detail.m_id
            item = pr_detail.item_id
            unit = item.uom_basic if item else None
            ah = pr_detail.ah_id
        except:
            continue  # Skip if related objects not found

        # Get related masters for PF, ExST, VAT
        pf_term = ''
        exst_term = ''
        vat_term = ''
        pf_value = Decimal('0')
        exst_value = Decimal('0')
        vat_value = Decimal('0')

        if temp.pf:
            try:
                from material_management.models import PackingMaster
                pf_obj = PackingMaster.objects.get(id=temp.pf)
                pf_term = pf_obj.terms
                pf_value = Decimal(pf_obj.value) if pf_obj.value else Decimal('0')
            except:
                pass

        if temp.ex_st:
            try:
                from material_management.models import ExciseserMaster
                exst_obj = ExciseserMaster.objects.get(id=temp.ex_st)
                exst_term = exst_obj.terms
                exst_value = Decimal(exst_obj.value) if exst_obj.value else Decimal('0')
            except:
                pass

        if temp.vat:
            try:
                from material_management.models import VatMaster
                vat_obj = VatMaster.objects.get(id=temp.vat)
                vat_term = vat_obj.terms
                vat_value = Decimal(vat_obj.value) if vat_obj.value else Decimal('0')
            except:
                pass

        # Calculate amounts
        basic_amt = temp.qty * temp.rate
        disc_amt = basic_amt * temp.discount / Decimal('100')
        taxable_amt = basic_amt - disc_amt
        total_amt = taxable_amt * (Decimal('1') + pf_value/Decimal('100') + exst_value/Decimal('100') + vat_value/Decimal('100'))

        # Build account head string
        ac_head = ''
        if ah:
            ac_head = f"{ah.symbol} {ah.description}" if ah.symbol and ah.description else ''

        results.append({
            'Id': temp.id,
            'PRNo': temp.pr_no or '',
            'WONo': pr_master.wo_no if pr_master else '',
            'ItemCode': item.item_code if item else '',
            'PurchDesc': item.manf_desc if item else '',
            'UOMPurch': unit.symbol if unit else '',
            'Qty': float(temp.qty),
            'Rate': float(temp.rate),
            'Discount': float(temp.discount),
            'AddDesc': temp.add_desc or '',
            'PF': pf_term,
            'ExST': exst_term,
            'VAT': vat_term,
            'DelDate': temp.del_date or '',
            'AcHead': ac_head,
            'BasicAmt': float(basic_amt),
            'DiscAmt': float(disc_amt),
            'TotalAmt': float(total_amt),
        })

    return JsonResponse({'items': results})


@login_required
def po_selected_spr_items_api(request):
    """
    API: Get selected SPR items from temp table - Using Django ORM
    """
    from decimal import Decimal

    comp_id, fin_year_id = get_company_and_financial_year(request)
    session_id = request.user.username

    # Get temp items using Django ORM
    temp_items = MmSprPoTemp.objects.filter(
        comp_id=comp_id,
        session_id=session_id
    ).order_by('spr_no')

    results = []
    for temp in temp_items:
        # Manually fetch related objects since spr_id is IntegerField, not ForeignKey
        try:
            spr_detail = SPRDetails.objects.get(id=temp.spr_id)
            spr_master = spr_detail.m_id if spr_detail else None
            item = spr_detail.item_id if spr_detail else None
            unit = item.uom_basic if item else None
            ah = spr_detail.ah_id if spr_detail else None
            dept = spr_detail.dept_id if spr_detail else None
        except:
            continue  # Skip if related objects not found

        # Get related masters for PF, ExST, VAT
        pf_term = ''
        exst_term = ''
        vat_term = ''
        pf_value = Decimal('0')
        exst_value = Decimal('0')
        vat_value = Decimal('0')

        if temp.pf:
            try:
                from material_management.models import PackingMaster
                pf_obj = PackingMaster.objects.get(id=temp.pf)
                pf_term = pf_obj.terms
                pf_value = Decimal(pf_obj.value) if pf_obj.value else Decimal('0')
            except:
                pass

        if temp.ex_st:
            try:
                from material_management.models import ExciseserMaster
                exst_obj = ExciseserMaster.objects.get(id=temp.ex_st)
                exst_term = exst_obj.terms
                exst_value = Decimal(exst_obj.value) if exst_obj.value else Decimal('0')
            except:
                pass

        if temp.vat:
            try:
                from material_management.models import VatMaster
                vat_obj = VatMaster.objects.get(id=temp.vat)
                vat_term = vat_obj.terms
                vat_value = Decimal(vat_obj.value) if vat_obj.value else Decimal('0')
            except:
                pass

        # Calculate amounts
        basic_amt = temp.qty * temp.rate
        disc_amt = basic_amt * temp.discount / Decimal('100')
        taxable_amt = basic_amt - disc_amt
        total_amt = taxable_amt * (Decimal('1') + pf_value/Decimal('100') + exst_value/Decimal('100') + vat_value/Decimal('100'))

        # Build account head string
        ac_head = ''
        if ah:
            ac_head = f"{ah.symbol} {ah.description}" if ah.symbol and ah.description else ''

        results.append({
            'Id': temp.id,
            'SPRNo': temp.spr_no or '',
            'WONo': spr_detail.wo_no if spr_detail else '',
            'ItemCode': item.item_code if item else '',
            'PurchDesc': item.manf_desc if item else '',
            'UOMPurch': unit.symbol if unit else '',
            'Qty': float(temp.qty),
            'Rate': float(temp.rate),
            'Discount': float(temp.discount),
            'AddDesc': temp.add_desc or '',
            'PF': pf_term,
            'ExST': exst_term,
            'VAT': vat_term,
            'DelDate': temp.del_date or '',
            'AcHead': ac_head,
            'Dept': dept.dept_name if dept else '',
            'BasicAmt': float(basic_amt),
            'DiscAmt': float(disc_amt),
            'TotalAmt': float(total_amt),
        })

    return JsonResponse({'items': results})


@login_required
@require_http_methods(["DELETE"])
def po_remove_item_from_temp(request, item_id, item_type):
    """
    Remove item from temp table
    item_type: 'pr' or 'spr'
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    session_id = request.user.username
    
    try:
        if item_type == 'pr':
            MmPrPoTemp.objects.filter(
                id=item_id,
                comp_id=comp_id,
                session_id=session_id
            ).delete()
        else:
            MmSprPoTemp.objects.filter(
                id=item_id,
                comp_id=comp_id,
                session_id=session_id
            ).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# =============================================================================
# PO GENERATION
# =============================================================================

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def po_generate(request):
    """
    Generate PO from temp table
    Includes budget validation
    Converted from: PO_PR_Items.aspx.cs btnProceed_Click
    """
    try:
        comp_id, fin_year_id = get_company_and_financial_year(request)
        session_id = request.user.username

        # Get form data
        supplier_code = request.POST.get('supplier_code')
        pr_spr_flag = request.POST.get('pr_spr_flag')  # 0=PR, 1=SPR
        reference = request.POST.get('reference')
        reference_date = request.POST.get('reference_date')
        reference_desc = request.POST.get('reference_desc', '')
        payment_terms = request.POST.get('payment_terms') or None
        warrenty = request.POST.get('warrenty') or None
        freight = request.POST.get('freight') or None
        octroi = request.POST.get('octroi') or None
        mode_of_dispatch = request.POST.get('mode_of_dispatch', '')
        inspection = request.POST.get('inspection', '')
        ship_to = request.POST.get('ship_to', '')
        remarks = request.POST.get('remarks', '')
        insurance = request.POST.get('insurance', '')
        tc = request.POST.get('tc', '')

        # Handle file upload
        annexure = request.FILES.get('annexure')
        filename = annexure.name if annexure else None
        filesize = annexure.size if annexure else None
        contenttype = annexure.content_type if annexure else None
        filedata = annexure.read() if annexure else None

        # Validate budget
        budget_valid, budget_errors = validate_po_budget(
            comp_id, fin_year_id, session_id, pr_spr_flag
        )

        if not budget_valid:
            return JsonResponse({
                'success': False,
                'budget_errors': budget_errors
            }, status=400)

        # Generate PO Number
        po_no = generate_po_number(comp_id, fin_year_id)

        # Get current date/time
        sys_date = datetime.now().strftime('%Y-%m-%d')
        sys_time = datetime.now().strftime('%H:%M:%S')

        # Create PO Master
        po_master = POMaster.objects.create(
            po_no=po_no,
            comp_id=comp_id,
            fin_year_id=fin_year_id,
            supplier_id=supplier_code,
            sys_date=sys_date,
            sys_time=sys_time,
            session_id=session_id,
            pr_spr_flag=pr_spr_flag,
            amendment_no=0,
            reference=reference,
            reference_date=reference_date,
            reference_desc=reference_desc,
            payment_terms=payment_terms,
            warrenty=warrenty,
            freight=freight,
            octroi=octroi,
            mode_of_dispatch=mode_of_dispatch,
            inspection=inspection,
            ship_to=ship_to,
            remarks=remarks,
            insurance=insurance,
            tc=tc,
            filename=filename,
            filesize=filesize,
            contenttype=contenttype,
            filedata=filedata,
            checked=0,
            approve=0,
            authorize=0
        )

        # Create PO Details from temp table
        if pr_spr_flag == '0':  # PR
            temp_items = MmPrPoTemp.objects.filter(
                comp_id=comp_id,
                session_id=session_id
            )

            for item in temp_items:
                PODetails.objects.create(
                    m_id=po_master.po_id,
                    po_no=po_no,
                    pr_no=item.pr_no,
                    pr_id=item.pr_id,
                    qty=item.qty,
                    rate=item.rate,
                    discount=item.discount,
                    add_desc=item.add_desc,
                    pf=item.pf,
                    ex_st=item.ex_st,
                    vat=item.vat,
                    del_date=item.del_date,
                    budget_code=item.budget_code,
                    amendment_no=0
                )

                # Lock item rates
                lock_item_rate(comp_id, fin_year_id, session_id, item.pr_id, po_no, sys_date, sys_time, 'PR')

            # Clear temp table
            temp_items.delete()

        else:  # SPR
            temp_items = MmSprPoTemp.objects.filter(
                comp_id=comp_id,
                session_id=session_id
            )

            for item in temp_items:
                PODetails.objects.create(
                    m_id=po_master.po_id,
                    po_no=po_no,
                    spr_no=item.spr_no,
                    spr_id=item.spr_id,
                    qty=item.qty,
                    rate=item.rate,
                    discount=item.discount,
                    add_desc=item.add_desc,
                    pf=item.pf,
                    ex_st=item.ex_st,
                    vat=item.vat,
                    del_date=item.del_date,
                    budget_code=item.budget_code,
                    amendment_no=0
                )

                # Lock item rates
                lock_item_rate(comp_id, fin_year_id, session_id, item.spr_id, po_no, sys_date, sys_time, 'SPR')

            # Clear temp table
            temp_items.delete()
    
        messages.success(request, f'PO {po_no} generated successfully!')
        return JsonResponse({
            'success': True,
            'po_no': po_no,
            'po_id': po_master.po_id
        })

    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error generating PO: {error_msg}")
        print(traceback_str)
        return JsonResponse({
            'success': False,
            'error': error_msg,
            'traceback': traceback_str
        }, status=500)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_company_address(comp_id):
    """Get company address for Ship To field"""
    query = """
        SELECT PlantAddress, PlantPinCode
        FROM tblCompany_Master
        WHERE CompId = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [comp_id])
        row = cursor.fetchone()
        if row and row[0]:
            address = row[0]
            if row[1]:
                address += f" - {row[1]}"
            return address
    return ""


def format_supplier_address(supplier):
    """
    Format supplier's registered address for display
    Format: [address], [city],[state], [country]. [pincode]

    Note: City/State/Country fields store IDs, need to lookup names from master tables
    """
    from sys_admin.models import Tblcity, Tblstate, Tblcountry

    parts = []

    # Add registered address
    if supplier.regd_address:
        parts.append(str(supplier.regd_address))

    # Add city, state, country - lookup names from master tables
    location_parts = []

    # Lookup city name
    if supplier.regd_city:
        try:
            city_id = int(supplier.regd_city) if isinstance(supplier.regd_city, str) else supplier.regd_city
            city = Tblcity.objects.filter(cityid=city_id).first()
            if city and city.cityname:
                location_parts.append(city.cityname)
        except (ValueError, TypeError):
            pass

    # Lookup state name
    if supplier.regd_state:
        try:
            state_id = int(supplier.regd_state) if isinstance(supplier.regd_state, str) else supplier.regd_state
            state = Tblstate.objects.filter(sid=state_id).first()
            if state and state.statename:
                location_parts.append(state.statename)
        except (ValueError, TypeError):
            pass

    # Lookup country name
    if supplier.regd_country:
        try:
            country_id = int(supplier.regd_country) if isinstance(supplier.regd_country, str) else supplier.regd_country
            country = Tblcountry.objects.filter(cid=country_id).first()
            if country and country.countryname:
                location_parts.append(country.countryname)
        except (ValueError, TypeError):
            pass

    if location_parts:
        parts.append(', '.join(location_parts))

    # Join with comma and add pincode at the end
    address = ', '.join(parts) if parts else ''

    if supplier.regd_pin_no:
        address += f'. {str(supplier.regd_pin_no)}'

    return address if address else ', ,'


def get_default_po_terms():
    """Get default PO terms & conditions"""
    query = "SELECT Terms FROM tbl_PO_terms"
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        return '\n'.join([row[0] for row in rows])


def get_po_references():
    """Get PO reference types"""
    query = "SELECT Id, RefDesc FROM tblMM_PO_Reference"
    with connection.cursor() as cursor:
        cursor.execute(query)
        return [{'id': row[0], 'desc': row[1]} for row in cursor.fetchall()]


def generate_po_number(comp_id, fin_year_id):
    """Generate next PO number"""
    last_po = POMaster.objects.filter(
        comp_id=comp_id,
        fin_year_id=fin_year_id
    ).aggregate(Max('po_no'))
    
    if last_po['po_no__max']:
        next_no = int(last_po['po_no__max']) + 1
    else:
        next_no = 1
    
    return str(next_no).zfill(4)


def validate_po_budget(comp_id, fin_year_id, session_id, pr_spr_flag):
    """
    Validate budget availability for PO items
    Returns: (is_valid, error_list)
    """
    # This is a simplified version
    # Full implementation would check budget per WO + Budget Code
    return True, []


def lock_item_rate(comp_id, fin_year_id, session_id, item_ref_id, po_no, sys_date, sys_time, item_type):
    """
    Lock item rate in rate lock/unlock table

    Args:
        comp_id: Company ID
        fin_year_id: Financial Year ID
        session_id: Session ID (username)
        item_ref_id: PR or SPR detail ID
        po_no: PO number
        sys_date: System date (YYYY-MM-DD format)
        sys_time: System time (HH:MM:SS format)
        item_type: 'PR' or 'SPR'
    """
    # Get item_id from PR or SPR details
    if item_type == 'PR':
        query = "SELECT ItemId FROM tblMM_PR_Details WHERE Id = %s"
    else:
        query = "SELECT ItemId FROM tblMM_SPR_Details WHERE Id = %s"

    with connection.cursor() as cursor:
        cursor.execute(query, [item_ref_id])
        row = cursor.fetchone()
        if row:
            item_id = row[0]

            # Update or create lock record
            # Fixed: Added missing required fields (sys_date, sys_time, fin_year_id, session_id)
            RateLockUnlock.objects.update_or_create(
                comp_id=comp_id,
                item_id=item_id,
                type=2,  # Type 2 for PO
                defaults={
                    'sys_date': sys_date,
                    'sys_time': sys_time,
                    'fin_year_id': fin_year_id,
                    'session_id': session_id,
                    'lock_unlock': 0,  # 0 = Locked
                    'locked_by_transaction': po_no,
                    'lock_date': sys_date,
                    'lock_time': sys_time
                }
            )



# =============================================================================
# PO APPROVAL CHAIN VIEWS
# =============================================================================

@login_required
def po_check_list(request):
    """
    PO Check List - First level verification
    Converted from: PO_Check.aspx
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    context = {
        'page_title': 'PO Check',
        'breadcrumbs': [
            {'name': 'Material Management', 'url': '/material-management/'},
            {'name': 'PO Check', 'url': ''}
        ]
    }
    
    return render(request, 'material_management/po/check_list.html', context)


@login_required
def po_check_list_api(request):
    """API: Get POs for checking"""
    comp_id, fin_year_id = get_company_and_financial_year(request)
    search_field = request.GET.get('field', 'supplier')  # 'supplier' or 'po_no'
    search_value = request.GET.get('search', '')
    
    query = """
        SELECT
            pom.Id,
            pom.PONo,
            pom.SysDate AS Date,
            pom.AmendmentNo AS AmdNo,
            COALESCE(emp.Title || '. ' || emp.EmployeeName, pom.SessionId) AS GenBy,
            s.SupplierName AS Sup,
            s.SupplierId AS Code,
            pom.CheckedDate,
            pom.ApproveDate AS ApprovedDate,
            pom.AuthorizeDate AS AuthorizedDate,
            fy.FinYear
        FROM tblMM_PO_Master pom
        INNER JOIN tblMM_Supplier_master s ON pom.SupplierId = s.SupplierId
        LEFT JOIN tblHR_OfficeStaff emp ON pom.SessionId = emp.EmpId
        INNER JOIN tblFinancial_master fy ON pom.FinYearId = fy.FinYearId
        WHERE pom.CompId = %s
            AND pom.Checked = 0
    """

    params = [comp_id]
    
    if search_value:
        if search_field == 'po_no':
            query += " AND pom.PONo LIKE %s"
            params.append(f'%{search_value}%')
        else:
            query += " AND (s.SupplierName LIKE %s OR s.SupplierId LIKE %s)"
            params.extend([f'%{search_value}%', f'%{search_value}%'])
    
    query += " ORDER BY pom.Id DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse({'pos': results})


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def po_check_action(request):
    """Mark selected POs as checked"""
    comp_id, fin_year_id = get_company_and_financial_year(request)
    session_id = request.user.username
    po_ids = request.POST.getlist('po_ids[]')
    
    if not po_ids:
        return JsonResponse({'success': False, 'error': 'No POs selected'}, status=400)
    
    sys_date = datetime.now().strftime('%Y-%m-%d')
    sys_time = datetime.now().strftime('%H:%M:%S')
    
    updated = POMaster.objects.filter(
        po_id__in=po_ids,
        comp_id=comp_id,
        checked=0
    ).update(
        checked=1,
        checked_by=session_id,
        checked_date=sys_date,
        checked_time=sys_time
    )
    
    messages.success(request, f'{updated} PO(s) marked as checked')
    return JsonResponse({'success': True, 'count': updated})


@login_required
def po_approve_list(request):
    """
    PO Approve List - Second level approval
    Converted from: PO_Approve.aspx
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    context = {
        'page_title': 'PO Approve',
        'breadcrumbs': [
            {'name': 'Material Management', 'url': '/material-management/'},
            {'name': 'PO Approve', 'url': ''}
        ]
    }
    
    return render(request, 'material_management/po/approve_list.html', context)


@login_required
def po_approve_list_api(request):
    """API: Get POs for approval"""
    comp_id, fin_year_id = get_company_and_financial_year(request)
    search_field = request.GET.get('field', 'supplier')
    search_value = request.GET.get('search', '')
    
    query = """
        SELECT
            pom.Id,
            pom.PONo,
            pom.SysDate AS Date,
            pom.AmendmentNo AS AmdNo,
            COALESCE(emp.Title || '. ' || emp.EmployeeName, pom.SessionId) AS GenBy,
            s.SupplierName AS Sup,
            s.SupplierId AS Code,
            pom.CheckedDate,
            pom.ApproveDate AS ApprovedDate,
            pom.AuthorizeDate AS AuthorizedDate,
            fy.FinYear
        FROM tblMM_PO_Master pom
        INNER JOIN tblMM_Supplier_master s ON pom.SupplierId = s.SupplierId
        LEFT JOIN tblHR_OfficeStaff emp ON pom.SessionId = emp.EmpId
        INNER JOIN tblFinancial_master fy ON pom.FinYearId = fy.FinYearId
        WHERE pom.CompId = %s
            AND pom.Checked = 1
            AND pom.Approve = 0
    """

    params = [comp_id]
    
    if search_value:
        if search_field == 'po_no':
            query += " AND pom.PONo LIKE %s"
            params.append(f'%{search_value}%')
        else:
            query += " AND (s.SupplierName LIKE %s OR s.SupplierId LIKE %s)"
            params.extend([f'%{search_value}%', f'%{search_value}%'])
    
    query += " ORDER BY pom.Id DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse({'pos': results})


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def po_approve_action(request):
    """Mark selected POs as approved"""
    comp_id, fin_year_id = get_company_and_financial_year(request)
    session_id = request.user.username
    po_ids = request.POST.getlist('po_ids[]')
    
    if not po_ids:
        return JsonResponse({'success': False, 'error': 'No POs selected'}, status=400)
    
    sys_date = datetime.now().strftime('%Y-%m-%d')
    sys_time = datetime.now().strftime('%H:%M:%S')
    
    updated = POMaster.objects.filter(
        po_id__in=po_ids,
        comp_id=comp_id,
        checked=1,
        approve=0
    ).update(
        approve=1,
        approved_by=session_id,
        approve_date=sys_date,
        approve_time=sys_time
    )
    
    messages.success(request, f'{updated} PO(s) marked as approved')
    return JsonResponse({'success': True, 'count': updated})


@login_required
def po_authorize_list(request):
    """
    PO Authorize List - Final authorization
    Converted from: PO_Authorize.aspx
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    context = {
        'page_title': 'PO Authorize',
        'breadcrumbs': [
            {'name': 'Material Management', 'url': '/material-management/'},
            {'name': 'PO Authorize', 'url': ''}
        ]
    }
    
    return render(request, 'material_management/po/authorize_list.html', context)


@login_required
def po_authorize_list_api(request):
    """API: Get POs for authorization"""
    comp_id, fin_year_id = get_company_and_financial_year(request)
    search_field = request.GET.get('field', 'supplier')
    search_value = request.GET.get('search', '')
    
    query = """
        SELECT
            pom.Id,
            pom.PONo,
            pom.SysDate AS Date,
            pom.AmendmentNo AS AmdNo,
            COALESCE(emp.Title || '. ' || emp.EmployeeName, pom.SessionId) AS GenBy,
            s.SupplierName AS Sup,
            s.SupplierId AS Code,
            pom.CheckedDate,
            pom.ApproveDate AS ApprovedDate,
            pom.AuthorizeDate AS AuthorizedDate,
            fy.FinYear
        FROM tblMM_PO_Master pom
        INNER JOIN tblMM_Supplier_master s ON pom.SupplierId = s.SupplierId
        LEFT JOIN tblHR_OfficeStaff emp ON pom.SessionId = emp.EmpId
        INNER JOIN tblFinancial_master fy ON pom.FinYearId = fy.FinYearId
        WHERE pom.CompId = %s
            AND pom.Approve = 1
            AND pom.Authorize = 0
    """

    params = [comp_id]
    
    if search_value:
        if search_field == 'po_no':
            query += " AND pom.PONo LIKE %s"
            params.append(f'%{search_value}%')
        else:
            query += " AND (s.SupplierName LIKE %s OR s.SupplierId LIKE %s)"
            params.extend([f'%{search_value}%', f'%{search_value}%'])
    
    query += " ORDER BY pom.Id DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse({'pos': results})


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def po_authorize_action(request):
    """
    Mark selected POs as authorized
    Also creates rate register entries
    Converted from: PO_Authorize.aspx.cs Auth_Click
    """
    comp_id, fin_year_id = get_company_and_financial_year(request)
    session_id = request.user.username
    po_ids = request.POST.getlist('po_ids[]')
    
    if not po_ids:
        return JsonResponse({'success': False, 'error': 'No POs selected'}, status=400)
    
    sys_date = datetime.now().strftime('%Y-%m-%d')
    sys_time = datetime.now().strftime('%H:%M:%S')
    
    authorized_count = 0
    
    for po_id in po_ids:
        po = POMaster.objects.filter(
            po_id=po_id,
            comp_id=comp_id,
            approve=1,
            authorize=0
        ).first()
        
        if not po:
            continue
        
        # Mark as authorized
        po.authorize = 1
        po.authorized_by = session_id
        po.authorize_date = sys_date
        po.authorize_time = sys_time
        po.save()
        
        # Create rate register entries
        create_rate_register_entries(po, comp_id, fin_year_id, session_id, sys_date, sys_time)
        
        authorized_count += 1
    
    messages.success(request, f'{authorized_count} PO(s) authorized successfully')
    return JsonResponse({'success': True, 'count': authorized_count})


def create_rate_register_entries(po, comp_id, fin_year_id, session_id, sys_date, sys_time):
    """
    Create rate register entries for all items in PO
    Converted from: PO_Authorize.aspx.cs rate registration logic
    """
    try:
        po_details = PODetails.objects.filter(m_id=po.po_id, po_no=po.po_no)

        for detail in po_details:
            try:
                if po.pr_spr_flag == 0:  # PR-based PO
                    # Get item_id from PR details
                    pr_detail = PRDetails.objects.filter(id=detail.pr_id).first()
                    if pr_detail:
                        RateRegister.objects.create(
                            sys_date=sys_date,
                            sys_time=sys_time,
                            comp_id=comp_id,
                            fin_year_id=fin_year_id,
                            session_id=session_id,
                            po_no=po.po_no,
                            item_id=pr_detail.item_id,
                            rate=detail.rate,
                            discount=detail.discount or 0,
                            pf=detail.pf or 0,
                            ex_st=detail.ex_st or 0,
                            vat=detail.vat or 0,
                            amendment_no=po.amendment_no or 0,
                            po_id=po.po_id,
                            pr_id=detail.pr_id,
                            flag=0  # Fixed: Added missing required Flag field
                        )

                        # Lock item
                        # Fixed: Added missing required fields (sys_date, sys_time, fin_year_id, session_id)
                        RateLockUnlock.objects.update_or_create(
                            comp_id=comp_id,
                            item_id=pr_detail.item_id,
                            type=2,
                            defaults={
                                'sys_date': sys_date,
                                'sys_time': sys_time,
                                'fin_year_id': fin_year_id,
                                'session_id': session_id,
                                'lock_unlock': 0,
                                'locked_by_transaction': session_id,
                                'lock_date': sys_date,
                                'lock_time': sys_time
                            }
                        )

                else:  # SPR-based PO
                    # Get item_id from SPR details
                    spr_detail = SPRDetails.objects.filter(id=detail.spr_id).first()
                    if spr_detail:
                        RateRegister.objects.create(
                            sys_date=sys_date,
                            sys_time=sys_time,
                            comp_id=comp_id,
                            fin_year_id=fin_year_id,
                            session_id=session_id,
                            po_no=po.po_no,
                            item_id=spr_detail.item_id,
                            rate=detail.rate,
                            discount=detail.discount or 0,
                            pf=detail.pf or 0,
                            ex_st=detail.ex_st or 0,
                            vat=detail.vat or 0,
                            amendment_no=po.amendment_no or 0,
                            po_id=po.po_id,
                            spr_id=detail.spr_id,
                            flag=0  # Fixed: Added missing required Flag field
                        )

                        # Lock item
                        # Fixed: Added missing required fields (sys_date, sys_time, fin_year_id, session_id)
                        RateLockUnlock.objects.update_or_create(
                            comp_id=comp_id,
                            item_id=spr_detail.item_id,
                            type=2,
                            defaults={
                                'sys_date': sys_date,
                                'sys_time': sys_time,
                                'fin_year_id': fin_year_id,
                                'session_id': session_id,
                                'lock_unlock': 0,
                                'locked_by_transaction': session_id,
                                'lock_date': sys_date,
                                'lock_time': sys_time
                            }
                        )
            except Exception as detail_error:
                # Log but continue with next detail
                print(f"Error creating rate register for detail {detail.detail_id}: {detail_error}")
                continue

    except Exception as e:
        # Log error but don't fail the authorization
        print(f"Error in create_rate_register_entries: {e}")
        pass


# =============================================================================
# PO VIEW/DETAIL
# =============================================================================

@login_required
def po_detail(request, po_id):
    """View PO details"""
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    po = get_object_or_404(POMaster, po_id=po_id, comp_id=comp_id)
    po_details = PODetails.objects.filter(m_id=po_id, po_no=po.po_no)
    
    # Get supplier
    supplier = Supplier.objects.filter(
        supplier_id=po.supplier_id,
        comp_id=comp_id
    ).first()
    
    # Get enriched details with item info
    enriched_details = []
    for detail in po_details:
        if po.pr_spr_flag == 0:  # PR
            pr_detail = PRDetails.objects.filter(id=detail.pr_id).first()
            if pr_detail:
                item = TbldgItemMaster.objects.filter(id=pr_detail.item_id).first()
                pr_master = PRMaster.objects.filter(pr_no=detail.pr_no).first()
                enriched_details.append({
                    'detail': detail,
                    'item': item,
                    'wo_no': pr_master.wo_no if pr_master else '',
                    'ref_no': detail.pr_no,
                    'ref_type': 'PR'
                })
        else:  # SPR
            spr_detail = SPRDetails.objects.filter(id=detail.spr_id).first()
            if spr_detail:
                item = TbldgItemMaster.objects.filter(id=spr_detail.item_id).first()
                enriched_details.append({
                    'detail': detail,
                    'item': item,
                    'wo_no': spr_detail.wo_no,
                    'ref_no': detail.spr_no,
                    'ref_type': 'SPR'
                })
    
    context = {
        'page_title': f'PO - {po.po_no}',
        'po': po,
        'supplier': supplier,
        'details': enriched_details,
        'breadcrumbs': [
            {'name': 'Material Management', 'url': '/material-management/'},
            {'name': 'PO Detail', 'url': ''}
        ]
    }
    
    return render(request, 'material_management/transactions/po_detail.html', context)


@login_required
def po_print(request, po_id):
    """Print PO"""
    comp_id, fin_year_id = get_company_and_financial_year(request)
    
    po = get_object_or_404(POMaster, po_id=po_id, comp_id=comp_id)
    po_details = PODetails.objects.filter(m_id=po_id, po_no=po.po_no)
    
    # Similar to po_detail but with print template
    context = {
        'po': po,
        'details': po_details
    }
    
    return render(request, 'material_management/po/print.html', context)
