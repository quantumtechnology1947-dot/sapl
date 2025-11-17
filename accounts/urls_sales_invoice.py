"""
Sales Invoice URL Configuration

MAPS: SalesInvoice_New.aspx and SalesInvoice_New_Details.aspx to Django views
Includes all HTMX endpoints for dynamic functionality
"""
from django.urls import path
from accounts.views.transactions.sales_invoice import (
    SalesInvoiceListView,
    SalesInvoicePOSelectionView,
    SalesInvoiceCreateView,
    SalesInvoiceUpdateView,
    SalesInvoiceDeleteView,
    SalesInvoicePrintView,
    CustomerAutocompleteView,
    GetStatesView,
    GetCitiesView,
    GetCommodityTariffView,
    SearchCustomerView,
    CopyBuyerToConsigneeView,
    CalculateRemainingQuantityView,
)

urlpatterns = [
    # =============================================================================
    # Main Views
    # =============================================================================

    # Invoice List/Dashboard
    path('',
         SalesInvoiceListView.as_view(),
         name='sales_invoice_list'),

    # Step 1: PO Selection (SalesInvoice_New.aspx)
    path('select-po/',
         SalesInvoicePOSelectionView.as_view(),
         name='sales_invoice_po_selection'),

    # Step 2: Create Invoice (SalesInvoice_New_Details.aspx)
    path('create/',
         SalesInvoiceCreateView.as_view(),
         name='sales_invoice_create'),

    # Edit, Delete, Print
    path('<int:invoice_id>/edit/',
         SalesInvoiceUpdateView.as_view(),
         name='sales_invoice_edit'),

    path('<int:invoice_id>/delete/',
         SalesInvoiceDeleteView.as_view(),
         name='sales_invoice_delete'),

    path('<int:invoice_id>/print/',
         SalesInvoicePrintView.as_view(),
         name='sales_invoice_print'),

    # =============================================================================
    # HTMX Endpoints (Dynamic Functionality)
    # =============================================================================

    # Cascading Dropdowns (Country → State → City)
    path('api/get-states/',
         GetStatesView.as_view(),
         name='sales_invoice_get_states'),

    path('api/get-cities/',
         GetCitiesView.as_view(),
         name='sales_invoice_get_cities'),

    # Customer Autocomplete (for Buyer/Consignee name fields)
    path('api/customer-autocomplete/',
         CustomerAutocompleteView.as_view(),
         name='customer_autocomplete'),

    # Commodity Tariff Auto-fill
    path('api/get-commodity-tariff/',
         GetCommodityTariffView.as_view(),
         name='sales_invoice_get_tariff'),

    # Search and Populate Customer (Buyer/Consignee)
    path('api/search-customer/',
         SearchCustomerView.as_view(),
         name='sales_invoice_search_customer'),

    # Copy Buyer to Consignee (Button6_Click)
    path('api/copy-buyer-to-consignee/',
         CopyBuyerToConsigneeView.as_view(),
         name='sales_invoice_copy_buyer'),

    # Calculate Remaining Quantity (for validation)
    path('api/calculate-remaining-qty/',
         CalculateRemainingQuantityView.as_view(),
         name='sales_invoice_calc_remaining_qty'),

    # Additional HTMX endpoints from old implementation (fallback)
    path('get-states/',
         GetStatesView.as_view(),
         name='sales_invoice_get_states_old'),

    path('get-cities/',
         GetCitiesView.as_view(),
         name='sales_invoice_get_cities_old'),

    path('customer-autocomplete/',
         CustomerAutocompleteView.as_view(),
         name='sales_invoice_customer_autocomplete_old'),

    path('get-tariff/',
         GetCommodityTariffView.as_view(),
         name='sales_invoice_get_tariff_old'),

    path('copy-buyer/',
         CopyBuyerToConsigneeView.as_view(),
         name='sales_invoice_copy_buyer_old'),
]
