"""
URL Configuration for Material Management Module

Following Django URL naming conventions: <model>-<action>
"""

from django.urls import path
from . import views
from . import po_views

app_name = 'material_management'

urlpatterns = [
    # Dashboard
    path('', views.MaterialManagementDashboardView.as_view(), name='dashboard'),

    # Business Nature Master
    path('business-nature/', views.BusinessNatureListView.as_view(), name='business-nature-list'),
    path('business-nature/create/', views.BusinessNatureCreateView.as_view(), name='business-nature-create'),
    path('business-nature/<int:id>/update/', views.BusinessNatureUpdateView.as_view(), name='business-nature-update'),
    path('business-nature/<int:id>/delete/', views.BusinessNatureDeleteView.as_view(), name='business-nature-delete'),

    # Business Type Master (inline editing with HTMX)
    path('business-type/', views.BusinessTypeListView.as_view(), name='business-type-list'),
    path('business-type/create/', views.BusinessTypeCreateView.as_view(), name='business-type-create'),
    path('business-type/<int:pk>/edit/', views.BusinessTypeUpdateView.as_view(), name='business-type-edit'),
    path('business-type/<int:pk>/update/', views.BusinessTypeUpdateView.as_view(), name='business-type-update'),
    # TODO: Implement BusinessTypeCancelEditView
    # path('business-type/<int:pk>/cancel/', views.BusinessTypeCancelEditView.as_view(), name='business-type-cancel'),
    path('business-type/<int:pk>/delete/', views.BusinessTypeDeleteView.as_view(), name='business-type-delete'),

    # Service Coverage Master
    path('service-coverage/', views.ServiceCoverageListView.as_view(), name='service-coverage-list'),
    path('service-coverage/create/', views.ServiceCoverageCreateView.as_view(), name='service-coverage-create'),
    path('service-coverage/<int:id>/update/', views.ServiceCoverageUpdateView.as_view(), name='service-coverage-update'),
    path('service-coverage/<int:id>/delete/', views.ServiceCoverageDeleteView.as_view(), name='service-coverage-delete'),

    # Buyer Master
    path('buyer/', views.BuyerListView.as_view(), name='buyer-list'),
    path('buyer/create/', views.BuyerCreateView.as_view(), name='buyer-create'),
    path('buyer/<int:id>/update/', views.BuyerUpdateView.as_view(), name='buyer-update'),
    path('buyer/<int:id>/delete/', views.BuyerDeleteView.as_view(), name='buyer-delete'),
    path('api/employee-autocomplete/', views.EmployeeAutocompleteView.as_view(), name='employee-autocomplete'),
    path('api/search-items/', views.ItemSearchAPIView.as_view(), name='api-search-items'),
    path('api/supplier-autocomplete/', views.SupplierAutocompleteAPIView.as_view(), name='api-supplier-autocomplete'),
    path('api/get-supplier-rate/', views.SupplierRateAPIView.as_view(), name='api-supplier-rate'),

    # Supplier Master
    path('supplier/', views.SupplierListView.as_view(), name='supplier-list'),
    path('supplier/create/', views.SupplierCreateView.as_view(), name='supplier-create'),
    path('supplier/<str:supplier_id>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    path('supplier/<str:supplier_id>/update/', views.SupplierUpdateView.as_view(), name='supplier-update'),
    path('supplier/<str:supplier_id>/delete/', views.SupplierDeleteView.as_view(), name='supplier-delete'),

    # Scope of Supplier Report
    path('scope-of-supplier/', views.ScopeOfSupplierView.as_view(), name='scope-of-supplier'),

    # Rate Set - Set Minimum Rate for Items
    path('rate-set/', views.RateSetSearchView.as_view(), name='rate-set-search'),
    path('rate-set/details/', views.RateSetDetailsView.as_view(), name='rate-set-details'),

    # Rate Register (Read-Only Report)
    path('rate-register/', views.RateRegisterListView.as_view(), name='rate-register-list'),
    path('rate-register/<int:item_id>/', views.RateRegisterDetailView.as_view(), name='rate-register-detail'),

    # Rate Management Transactions
    path('rate-lock-unlock/', views.RateLockUnlockListView.as_view(), name='rate_lock_unlock_list'),
    path('rate-lock-unlock/action/', views.RateLockUnlockActionView.as_view(), name='rate_lock_unlock_action'),
    path('rate-lock-unlock/report/', views.RateLockUnlockReportView.as_view(), name='rate_lock_unlock_report'),

    # Purchase Requisition (PR) Transactions
    path('pr/', views.PRListView.as_view(), name='pr-list'),
    path('pr/new/', views.PRNewSearchView.as_view(), name='pr-new-search'),  # Step 1: Search WO
    path('pr/new/<str:wo_no>/', views.PRNewDetailsView.as_view(), name='pr-new-details'),  # Step 2: Add items
    path('pr/<int:pr_id>/', views.PRDetailView.as_view(), name='pr-detail'),
    path('pr/<int:pr_id>/update/', views.PRUpdateView.as_view(), name='pr-update'),
    path('pr/<int:pr_id>/delete/', views.PRDeleteView.as_view(), name='pr-delete'),

    # PR Approval Workflow
    path('pr/check/', views.PRCheckView.as_view(), name='pr-check-list'),
    path('pr/approve/', views.PRApproveView.as_view(), name='pr-approve-list'),
    path('pr/authorize/', views.PRAuthorizeView.as_view(), name='pr-authorize-list'),

    # Special Purpose Requisition (SPR) Transactions
    path('spr/', views.SPRListView.as_view(), name='spr-list'),
    path('spr/new/', views.SPRNewView.as_view(), name='spr-new'),  # Step 1: Select Department/WO and AH Category
    path('spr/new/<int:dept_id>/<str:ah_category>/', views.SPRNewDetailsView.as_view(), name='spr-new-details'),  # Step 2: AI-suggested items for department
    path('spr/new/<int:dept_id>/<str:ah_category>/<str:wo_no>/', views.SPRNewDetailsView.as_view(), name='spr-new-details-wo'),  # Step 2: With WO number
    path('spr/create/', views.SPRNewView.as_view(), name='spr-create'),  # Alias for spr-new
    path('spr/<int:spr_id>/', views.SPRDetailView.as_view(), name='spr-detail'),
    path('spr/<int:spr_id>/update/', views.SPRUpdateView.as_view(), name='spr-update'),
    path('spr/<int:spr_id>/delete/', views.SPRDeleteView.as_view(), name='spr-delete'),

    # SPR Approval Workflow
    path('spr/check/', views.SPRCheckView.as_view(), name='spr-check-list'),
    path('spr/approve/', views.SPRApproveView.as_view(), name='spr-approve-list'),
    path('spr/authorize/', views.SPRAuthorizeView.as_view(), name='spr-authorize-list'),

    # Purchase Order (PO) Transactions - DISABLED: Using function-based views from po_views.py instead
    # path('po/', views.POListView.as_view(), name='po-list'),

    # PO Multi-Step Wizard - DISABLED: Using function-based views from po_views.py instead
    # path('po/new/', views.PONewView.as_view(), name='po-new'),  # Step 1: Supplier selection (PR/SPR tabs)
    # path('po/pr-items/<str:supplier_code>/', views.POPRItemsView.as_view(), name='po-pr-items'),  # Step 2: PR item grid
    # path('po/spr-items/<str:supplier_code>/', views.POSPRItemsView.as_view(), name='po-spr-items'),  # Step 2: SPR item grid
    # path('po/pr-item-select/<str:supplier_code>/<int:pr_detail_id>/', views.POPRItemSelectView.as_view(), name='po-pr-item-select'),  # Step 3: PR item entry
    # path('po/spr-item-select/<str:supplier_code>/<int:spr_detail_id>/', views.POSPRItemSelectView.as_view(), name='po-spr-item-select'),  # Step 3: SPR item entry
    # path('po/header/<str:supplier_code>/<int:pr_spr_flag>/', views.POHeaderView.as_view(), name='po-header'),  # Step 4: Final PO creation

    # PO Details & Management
    path('po/<int:po_id>/', views.PODetailView.as_view(), name='po-detail'),
    path('po/<int:po_id>/update/', views.POUpdateView.as_view(), name='po-update'),
    path('po/<int:po_id>/delete/', views.PODeleteView.as_view(), name='po-delete'),

    # PO Approval Workflow - Check Stage
    # TODO: Implement POCheckListView, POCheckDetailView, POCheckedListView
    # Note: POCheckView and POCheckActionView exist but not the List/Detail views
    # path('po/workflow/check/', views.POCheckListView.as_view(), name='po-check-list'),
    # path('po/workflow/check/<int:po_id>/', views.POCheckDetailView.as_view(), name='po-check-detail'),
    path('po/workflow/check/<int:po_id>/action/', views.POCheckActionView.as_view(), name='po-check-action'),
    # path('po/workflow/checked/', views.POCheckedListView.as_view(), name='po-checked-list'),

    # PO Approval Workflow - Approve Stage
    # TODO: Implement POApproveListView, POApproveDetailView, POApprovedListView
    # Note: POApproveView and POApproveActionView exist but not the List/Detail views
    # path('po/workflow/approve/', views.POApproveListView.as_view(), name='po-approve-list'),
    # path('po/workflow/approve/<int:po_id>/', views.POApproveDetailView.as_view(), name='po-approve-detail'),
    path('po/workflow/approve/<int:po_id>/action/', views.POApproveActionView.as_view(), name='po-approve-action'),
    # path('po/workflow/approved/', views.POApprovedListView.as_view(), name='po-approved-list'),

    # PO Approval Workflow - Authorize Stage
    # TODO: Implement POAuthorizeListView, POAuthorizeDetailView, POAuthorizedListView
    # Note: POAuthorizeView and POAuthorizeActionView exist but not the List/Detail views
    # path('po/workflow/authorize/', views.POAuthorizeListView.as_view(), name='po-authorize-list'),
    # path('po/workflow/authorize/<int:po_id>/', views.POAuthorizeDetailView.as_view(), name='po-authorize-detail'),
    path('po/workflow/authorize/<int:po_id>/action/', views.POAuthorizeActionView.as_view(), name='po-authorize-action'),
    # path('po/workflow/authorized/', views.POAuthorizedListView.as_view(), name='po-authorized-list'),

    # Reports
    path('reports/rate-register/', views.RateRegisterReportView.as_view(), name='report-rate-register'),
    path('reports/rate-lock/', views.RateLockUnlockReportView.as_view(), name='report-rate-lock'),
    path('reports/supplier-rating/', views.SupplierRatingReportView.as_view(), name='report-supplier-rating'),
    path('reports/material-forecasting/', views.MaterialForecastingReportView.as_view(), name='report-material-forecasting'),
    path('reports/search/', views.MaterialSearchView.as_view(), name='report-search'),

    # =========================================================================
    # PURCHASE ORDER (PO) URLS
    # =========================================================================
    
    # PO List & Creation
    path('po/', po_views.po_list, name='po-list'),
    path('po/new/', po_views.po_new, name='po-new'),
    path('po/pr-items/<str:supplier_code>/', po_views.po_pr_items, name='po-pr-items'),
    path('po/spr-items/<str:supplier_code>/', po_views.po_spr_items, name='po-spr-items'),
    
    # PO APIs
    path('api/po/list/', po_views.po_list_api, name='api-po-list'),
    path('api/po/pr-suppliers/', po_views.po_pr_suppliers_api, name='api-po-pr-suppliers'),
    path('api/po/spr-suppliers/', po_views.po_spr_suppliers_api, name='api-po-spr-suppliers'),

    # PO HTMX endpoints (real-time search)
    path('htmx/po/pr-suppliers/', po_views.po_pr_suppliers_htmx, name='htmx-po-pr-suppliers'),
    path('htmx/po/spr-suppliers/', po_views.po_spr_suppliers_htmx, name='htmx-po-spr-suppliers'),
    path('htmx/po/pr-suppliers-count/', po_views.po_pr_suppliers_count_htmx, name='htmx-po-pr-suppliers-count'),
    path('htmx/po/spr-suppliers-count/', po_views.po_spr_suppliers_count_htmx, name='htmx-po-spr-suppliers-count'),

    path('po/pr-items-grid/', po_views.po_pr_items_grid, name='po-pr-items-grid'),
    path('po/spr-items-grid/', po_views.po_spr_items_grid, name='po-spr-items-grid'),
    path('api/po/pr-items-grid/', po_views.po_pr_items_grid_api, name='api-po-pr-items-grid'),
    path('api/po/spr-items-grid/', po_views.po_spr_items_grid_api, name='api-po-spr-items-grid'),
    path('api/po/selected-pr-items/', po_views.po_selected_pr_items_api, name='api-po-selected-pr-items'),
    path('api/po/selected-spr-items/', po_views.po_selected_spr_items_api, name='api-po-selected-spr-items'),
    path('api/po/add-pr-item/', po_views.po_add_pr_item_to_temp, name='api-po-add-pr-item'),
    path('api/po/add-spr-item/', po_views.po_add_spr_item_to_temp, name='api-po-add-spr-item'),
    path('api/po/remove-item/<int:item_id>/<str:item_type>/', po_views.po_remove_item_from_temp, name='api-po-remove-item'),
    path('po/generate/', po_views.po_generate, name='po-generate'),
    
    # PO Approval Chain
    path('po/check/', po_views.po_check_list, name='po-check-list'),
    path('api/po/check-list/', po_views.po_check_list_api, name='api-po-check-list'),
    path('po/check/action/', po_views.po_check_action, name='po-check-action'),
    
    path('po/approve/', po_views.po_approve_list, name='po-approve-list'),
    path('api/po/approve-list/', po_views.po_approve_list_api, name='api-po-approve-list'),
    path('po/approve/action/', po_views.po_approve_action, name='po-approve-action'),
    
    path('po/authorize/', po_views.po_authorize_list, name='po-authorize-list'),
    path('api/po/authorize-list/', po_views.po_authorize_list_api, name='api-po-authorize-list'),
    path('po/authorize/action/', po_views.po_authorize_action, name='po-authorize-action'),
    
    # PO View/Print
    path('po/<int:po_id>/detail/', po_views.po_detail, name='po-detail'),
    path('po/<int:po_id>/print/', po_views.po_print, name='po-print'),
]
