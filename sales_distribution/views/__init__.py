"""
Sales Distribution Views Package
Modularized from monolithic views.py (4,380 lines → focused modules)
"""

# Import shared mixin
from .base import FinancialYearUserMixin

# Customer Master views (6 views)
from .customer import (
    CustomerCreateView,
    CustomerView,
    CustomerSearchView,
    CustomerJSONView,
    StatesByCountryView,
    CitiesByStateView,
    CustomerMasterPrintView
)

# WO Category & Subcategory views (4 views)
from .wo_category import (
    WoCategoryView,
    WoCategoryCreateView,
    WoSubCategoryView,
    WoSubCategoryCreateView
)

# Customer Enquiry views (6 views)
from .enquiry import (
    CustomerEnquiryView,
    CustomerEnquiryCreateView,
    CustomerEnquiryDetailView,
    CustomerEnquiryPrintView,
    CustomerEnquiryConvertView
)

# Quotation views (10 views)
from .quotation import (
    QuotationView,
    QuotationSearchView,
    QuotationSearchResultsView,
    QuotationCreateDetailView,
    QuotationEditView,
    QuotationWorkflowBaseView,
    QuotationCheckView,
    QuotationApproveView,
    QuotationAuthorizeView,
    QuotationDeleteView,
    QuotationPrintView
)

# Customer PO views (10 views)
from .customer_po import (
    CustomerPoView,
    CustomerPoSearchView,
    CustomerPoSearchResultsView,
    CustomerPoCreateDetailView,
    PoLineItemCreateView,
    PoLineItemRowView,
    PoLineItemEditFormView,
    PoLineItemUpdateView,
    PoLineItemDeleteView,
    CustomerPoUpdateView,
    CustomerPoDownloadView,
    QuotationDetailsForPoView,
    CustomerPoPrintView
)

# Work Order views (14 views)
from .work_order import (
    WorkOrderView,
    WorkOrderPoSearchView,
    WorkOrderPoSearchResultsView,
    WorkOrderProductAddView,
    WorkOrderProductListView,
    WorkOrderProductEditView,
    WorkOrderProductDeleteView,
    WorkOrderStatesByCountryView,
    WorkOrderCitiesByStateView,
    WorkOrderCreateView,
    WorkOrderUpdateView,
    WorkOrderCloseView,
    WorkOrderOpenView,
    WorkOrderCloseOpenPageView,
    WorkOrderPrintView
)

# WO Release & Dispatch views (5 views)
from .wo_release import (
    WorkOrderReleaseListView,
    WorkOrderReleaseDetailView,
    WorkOrderReleaseSubmitView,
    WorkOrderDispatchListView,
    WorkOrderDispatchDetailView,
    WorkOrderDispatchView,
    WorkOrderDispatchPrintView
)

# Product Master views (1 view)
from .product import ProductView

# Universal Search views (1 view)
from .search import UniversalSearchView


__all__ = [
    # Shared
    'FinancialYearUserMixin',

    # Customer
    'CustomerCreateView',
    'CustomerView',
    'CustomerSearchView',
    'CustomerJSONView',
    'StatesByCountryView',
    'CitiesByStateView',
    'CustomerMasterPrintView',

    # WO Category
    'WoCategoryView',
    'WoCategoryCreateView',
    'WoSubCategoryView',
    'WoSubCategoryCreateView',

    # Enquiry
    'CustomerEnquiryView',
    'CustomerEnquiryCreateView',
    'CustomerEnquiryDetailView',
    'CustomerEnquiryPrintView',
    'CustomerEnquiryConvertView',

    # Quotation
    'QuotationView',
    'QuotationSearchView',
    'QuotationSearchResultsView',
    'QuotationCreateDetailView',
    'QuotationEditView',
    'QuotationWorkflowBaseView',
    'QuotationCheckView',
    'QuotationApproveView',
    'QuotationAuthorizeView',
    'QuotationDeleteView',
    'QuotationPrintView',

    # Customer PO
    'CustomerPoView',
    'CustomerPoSearchView',
    'CustomerPoSearchResultsView',
    'CustomerPoCreateDetailView',
    'PoLineItemCreateView',
    'PoLineItemRowView',
    'PoLineItemEditFormView',
    'PoLineItemUpdateView',
    'PoLineItemDeleteView',
    'CustomerPoUpdateView',
    'CustomerPoDownloadView',
    'QuotationDetailsForPoView',
    'CustomerPoPrintView',

    # Work Order
    'WorkOrderView',
    'WorkOrderPoSearchView',
    'WorkOrderPoSearchResultsView',
    'WorkOrderProductAddView',
    'WorkOrderProductListView',
    'WorkOrderProductEditView',
    'WorkOrderProductDeleteView',
    'WorkOrderStatesByCountryView',
    'WorkOrderCitiesByStateView',
    'WorkOrderCreateView',
    'WorkOrderUpdateView',
    'WorkOrderCloseView',
    'WorkOrderOpenView',
    'WorkOrderCloseOpenPageView',
    'WorkOrderPrintView',

    # WO Release
    'WorkOrderReleaseListView',
    'WorkOrderReleaseDetailView',
    'WorkOrderReleaseSubmitView',
    'WorkOrderDispatchListView',
    'WorkOrderDispatchDetailView',
    'WorkOrderDispatchView',
    'WorkOrderDispatchPrintView',

    # Product
    'ProductView',

    # Search
    'UniversalSearchView',
]
