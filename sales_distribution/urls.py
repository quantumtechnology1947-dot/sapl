"""
Sales Distribution URL Configuration
Converted from ASP.NET Module/SalesDistribution
"""

from django.urls import path
from . import views

app_name = 'sales_distribution'

urlpatterns = [
    # Universal Search
    path('search/', views.UniversalSearchView.as_view(), name='universal-search'),

    # Customer Master
    path('customer/', views.CustomerView.as_view(), name='customer-list'),
    path('customer/create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customer/<int:salesid>/', views.CustomerView.as_view(), name='customer-detail'),
    path('customer/<int:salesid>/json/', views.CustomerJSONView.as_view(), name='customer-json'),
    path('customer/<int:salesid>/print/', views.CustomerMasterPrintView.as_view(), name='customer-print'),

    # HTMX Cascade Endpoints
    path('customer/states-by-country/', views.StatesByCountryView.as_view(), name='states-by-country'),
    path('customer/cities-by-state/', views.CitiesByStateView.as_view(), name='cities-by-state'),
    path('customer/search/', views.CustomerSearchView.as_view(), name='customer-search'),
    
    # WO Category Master
    path('wo-category/', views.WoCategoryView.as_view(), name='wo-category-list'),
    path('wo-category/create/', views.WoCategoryCreateView.as_view(), name='wo-category-create'),
    path('wo-category/<int:cid>/', views.WoCategoryView.as_view(), name='wo-category-detail'),
    path('wo-category/<int:cid>/edit/', views.WoCategoryView.as_view(), name='wo-category-edit'),
    path('wo-category/<int:cid>/delete/', views.WoCategoryView.as_view(), name='wo-category-delete'),
    
    # WO Sub-Category Master
    path('wo-subcategory/', views.WoSubCategoryView.as_view(), name='wo-subcategory-list'),
    path('wo-subcategory/create/', views.WoSubCategoryCreateView.as_view(), name='wo-subcategory-create'),
    path('wo-subcategory/<int:scid>/', views.WoSubCategoryView.as_view(), name='wo-subcategory-detail'),
    path('wo-subcategory/<int:scid>/edit/', views.WoSubCategoryView.as_view(), name='wo-subcategory-edit'),
    path('wo-subcategory/<int:scid>/delete/', views.WoSubCategoryView.as_view(), name='wo-subcategory-delete'),
    
    # Customer Enquiry
    path('enquiry/', views.CustomerEnquiryView.as_view(), name='enquiry-list'),
    path('enquiry/create/', views.CustomerEnquiryCreateView.as_view(), name='enquiry-create'),
    path('enquiry/<int:enqid>/', views.CustomerEnquiryView.as_view(), name='enquiry-detail'),
    path('enquiry/<int:enqid>/detail/', views.CustomerEnquiryDetailView.as_view(), name='enquiry-detail-page'),
    path('enquiry/<int:enqid>/print/', views.CustomerEnquiryPrintView.as_view(), name='enquiry-print'),
    
    # Quotation
    path('quotation/', views.QuotationView.as_view(), name='quotation-list'),
    path('quotation/search/', views.QuotationSearchView.as_view(), name='quotation-search'),
    path('quotation/search-results/', views.QuotationSearchResultsView.as_view(), name='quotation-search-results'),
    path('quotation/create/<int:enqid>/', views.QuotationCreateDetailView.as_view(), name='quotation-create-detail'),
    path('quotation/<int:id>/', views.QuotationView.as_view(), name='quotation-detail'),
    path('quotation/<int:id>/edit/', views.QuotationEditView.as_view(), name='quotation-edit'),

    # Quotation Workflow
    path('quotation/check/', views.QuotationCheckView.as_view(), name='quotation-check'),
    path('quotation/approve/', views.QuotationApproveView.as_view(), name='quotation-approve'),
    path('quotation/authorize/', views.QuotationAuthorizeView.as_view(), name='quotation-authorize'),
    path('quotation/<int:quotation_id>/delete/', views.QuotationDeleteView.as_view(), name='quotation-delete'),
    path('quotation/<int:quotation_id>/print/', views.QuotationPrintView.as_view(), name='quotation-print'),

    # Customer PO
    path('po/', views.CustomerPoView.as_view(), name='po-list'),
    path('po/search/', views.CustomerPoSearchView.as_view(), name='po-search'),
    path('po/search-results/', views.CustomerPoSearchResultsView.as_view(), name='po-search-results'),
    path('po/create/<int:enqid>/', views.CustomerPoCreateDetailView.as_view(), name='po-create-detail'),
    path('po/<int:poid>/', views.CustomerPoView.as_view(), name='po-detail'),
    path('po/<int:poid>/edit/', views.CustomerPoUpdateView.as_view(), name='po-edit'),
    path('po/<int:poid>/download/', views.CustomerPoDownloadView.as_view(), name='po-download'),
    path('po/<int:poid>/print/', views.CustomerPoPrintView.as_view(), name='po-print'),
    path('po/quotation-details/', views.QuotationDetailsForPoView.as_view(), name='po-quotation-details'),

    # Customer PO Line Items (HTMX Endpoints)
    path('po/<int:poid>/line-items/create/', views.PoLineItemCreateView.as_view(), name='po-line-create'),
    path('po/<int:poid>/line-items/<int:item_id>/row/', views.PoLineItemRowView.as_view(), name='po-line-row'),
    path('po/<int:poid>/line-items/<int:item_id>/edit/', views.PoLineItemEditFormView.as_view(), name='po-line-edit-form'),
    path('po/<int:poid>/line-items/<int:item_id>/update/', views.PoLineItemUpdateView.as_view(), name='po-line-update'),
    path('po/<int:poid>/line-items/<int:item_id>/delete/', views.PoLineItemDeleteView.as_view(), name='po-line-delete'),

    # Product Master
    path('product/', views.ProductView.as_view(), name='product-list'),
    path('product/<str:itemcode>/', views.ProductView.as_view(), name='product-detail'),
    
    # Work Order Release
    path('wo-release/', views.WorkOrderReleaseListView.as_view(), name='wo-release-list'),
    path('wo-release/<int:wo_id>/', views.WorkOrderReleaseDetailView.as_view(), name='wo-release-detail'),
    path('wo-release/<int:wo_id>/submit/', views.WorkOrderReleaseSubmitView.as_view(), name='wo-release-submit'),
    
    # Work Order Dispatch
    path('dispatch/', views.WorkOrderDispatchListView.as_view(), name='dispatch-list'),
    path('dispatch/<str:wono>/<path:wrno>/', views.WorkOrderDispatchDetailView.as_view(), name='dispatch-detail'),
    path('dispatch/<int:pk>/print/', views.WorkOrderDispatchPrintView.as_view(), name='dispatch-print'),
    
    # Work Order Management
    path('workorder/', views.WorkOrderView.as_view(), name='workorder-list'),
    path('workorder/search/', views.WorkOrderPoSearchView.as_view(), name='workorder-po-search'),
    path('workorder/search-results/', views.WorkOrderPoSearchResultsView.as_view(), name='workorder-po-search-results'),
    path('workorder/create/<int:poid>/', views.WorkOrderCreateView.as_view(), name='workorder-create'),
    path('workorder/<int:id>/print/', views.WorkOrderPrintView.as_view(), name='workorder-print'),
    path('workorder/close-open/', views.WorkOrderCloseOpenPageView.as_view(), name='workorder-close-open-page'),

    # Work Order Products Management (HTMX endpoints for Tab 3)
    path('workorder/products/add/', views.WorkOrderProductAddView.as_view(), name='workorder-product-add'),
    path('workorder/products/list/', views.WorkOrderProductListView.as_view(), name='workorder-product-list'),
    path('workorder/products/<int:id>/edit/', views.WorkOrderProductEditView.as_view(), name='workorder-product-edit'),
    path('workorder/products/<int:id>/delete/', views.WorkOrderProductDeleteView.as_view(), name='workorder-product-delete'),

    # Work Order Shipping Location Cascading Dropdowns (HTMX endpoints for Tab 2)
    path('workorder/states/', views.WorkOrderStatesByCountryView.as_view(), name='workorder-states'),
    path('workorder/cities/', views.WorkOrderCitiesByStateView.as_view(), name='workorder-cities'),

    path('workorder/<int:id>/', views.WorkOrderView.as_view(), name='workorder-detail'),
    path('workorder/<int:id>/edit/', views.WorkOrderUpdateView.as_view(), name='workorder-edit'),
    path('workorder/<int:id>/close/', views.WorkOrderCloseView.as_view(), name='workorder-close'),
    path('workorder/<int:id>/open/', views.WorkOrderOpenView.as_view(), name='workorder-open'),

    # Customer Enquiry Convert
    path('enquiry/convert/', views.CustomerEnquiryConvertView.as_view(), name='enquiry-convert'),
    
    # WO Category Master
    # TODO: Implement WOCategory and WOSubcategory views
    # path('masters/wo-category/', views.WOCategoryListView.as_view(), name='wo-category-list'),
    # path('masters/wo-category/create/', views.WOCategoryCreateView.as_view(), name='wo-category-create'),
    # path('masters/wo-category/<int:cid>/update/', views.WOCategoryUpdateView.as_view(), name='wo-category-update'),
    # path('masters/wo-category/<int:cid>/delete/', views.WOCategoryDeleteView.as_view(), name='wo-category-delete'),

    # WO Subcategory Master
    # path('masters/wo-subcategory/', views.WOSubcategoryListView.as_view(), name='wo-subcategory-list'),
    # path('masters/wo-subcategory/create/', views.WOSubcategoryCreateView.as_view(), name='wo-subcategory-create'),
    # path('masters/wo-subcategory/<int:scid>/update/', views.WOSubcategoryUpdateView.as_view(), name='wo-subcategory-update'),
    # path('masters/wo-subcategory/<int:scid>/delete/', views.WOSubcategoryDeleteView.as_view(), name='wo-subcategory-delete'),

    # ========================================================================
    # REPORTS
    # ========================================================================
    path('reports/', views.ReportsDashboardView.as_view(), name='reports-dashboard'),
    path('reports/customer-master/', views.CustomerMasterReportView.as_view(), name='report-customer-master'),
    path('reports/customer-po/', views.CustomerPOReportView.as_view(), name='report-customer-po'),
    path('reports/customer-quotation/', views.CustomerQuotationReportView.as_view(), name='report-customer-quotation'),
    path('reports/customer-enquiry/', views.CustomerEnquiryReportView.as_view(), name='report-customer-enquiry'),
]

