"""
Inventory Module URL Configuration
"""
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.InventoryDashboardView.as_view(), name='dashboard'),
    
    # Material Requisition Slip (MRS)
    path('mrs/', views.MRSListView.as_view(), name='mrs-list'),
    path('mrs/create/', views.MRSCreateView.as_view(), name='mrs-create'),
    path('mrs/search-items/', views.MRSSearchItemsView.as_view(), name='mrs-search-items'),
    path('mrs/add-to-cart/', views.MRSAddToCartView.as_view(), name='mrs-add-to-cart'),
    path('mrs/remove-from-cart/', views.MRSRemoveFromCartView.as_view(), name='mrs-remove-from-cart'),
    path('mrs/<int:pk>/', views.MRSDetailView.as_view(), name='mrs-detail'),
    path('mrs/<int:pk>/delete/', views.MRSDeleteView.as_view(), name='mrs-delete'),
    path('mrs/<int:pk>/print/', views.MRSPrintView.as_view(), name='mrs-print'),

    # Material Issue Note (MIN)
    path('min/', views.MINListView.as_view(), name='min-list'),
    path('min/pending-mrs/', views.MRSPendingListView.as_view(), name='mrs-pending-list'),
    path('min/create/', views.MINCreateView.as_view(), name='min-create'),
    path('min/<int:pk>/', views.MINDetailView.as_view(), name='min-detail'),
    path('min/<int:pk>/delete/', views.MINDeleteView.as_view(), name='min-delete'),
    path('min/<int:pk>/print/', views.MINPrintView.as_view(), name='min-print'),
    
    # Material Return Note (MRN)
    path('mrn/', views.MRNListView.as_view(), name='mrn-list'),
    path('mrn/create/', views.MRNCreateView.as_view(), name='mrn-create'),
    path('mrn/add-to-cart/', views.MRNAddToCartView.as_view(), name='mrn-add-to-cart'),
    path('mrn/remove-from-cart/', views.MRNRemoveFromCartView.as_view(), name='mrn-remove-from-cart'),
    path('mrn/<int:pk>/', views.MRNDetailView.as_view(), name='mrn-detail'),
    path('mrn/<int:pk>/delete/', views.MRNDeleteView.as_view(), name='mrn-delete'),
    path('mrn/<int:pk>/print/', views.MRNPrintView.as_view(), name='mrn-print'),
    
    # Goods Inward Note (GIN)
    path('gin/', views.GINListView.as_view(), name='gin-list'),
    path('gin/create/', views.GINCreateView.as_view(), name='gin-create'),
    path('gin/<int:pk>/', views.GINDetailView.as_view(), name='gin-detail'),
    path('gin/<int:pk>/delete/', views.GINDeleteView.as_view(), name='gin-delete'),
    path('gin/<int:pk>/print/', views.GINPrintView.as_view(), name='gin-print'),
    path('gin/<int:pk>/update-master/', views.GINMasterUpdateView.as_view(), name='gin-master-update'),
    path('gin-detail/<int:detail_id>/update/', views.GINDetailUpdateView.as_view(), name='gin-detail-update'),
    path('gin/item/<int:item_id>/image/', views.ItemImageDownloadView.as_view(), name='item-image-download'),
    path('gin/item/<int:item_id>/spec/', views.ItemSpecDownloadView.as_view(), name='item-spec-download'),
    path('gin/po-search-results/', views.GINPOSearchResultsView.as_view(), name='gin-po-search-results'),
    path('gin/po-search-autocomplete/', views.GINPOSearchResultsView.as_view(), name='gin-po-search-autocomplete'),
    path('gin/po-details/', views.GINPODetailsView.as_view(), name='gin-po-details'),
    path('gin/create-from-po/', views.GINCreateFromPOView.as_view(), name='gin-create-from-po'),
    
    # Goods Received Receipt (GRR)
    path('grr/', views.GRRListView.as_view(), name='grr-list'),
    path('grr/pending-gin/', views.GINPendingListView.as_view(), name='gin-pending-list'),
    path('grr/create/', views.GRRCreateView.as_view(), name='grr-create'),
    path('grr/<int:pk>/', views.GRRDetailView.as_view(), name='grr-detail'),
    path('grr/<int:pk>/delete/', views.GRRDeleteView.as_view(), name='grr-delete'),
    path('grr/<int:pk>/print/', views.GRRPrintView.as_view(), name='grr-print'),
    path('grr/edit/', views.GRREditListView.as_view(), name='grr-edit-list'),
    path('grr/<int:pk>/edit/', views.GRREditDetailView.as_view(), name='grr-edit-detail'),
    
    # Goods Service Note (GSN)
    path('gsn/', views.GSNListView.as_view(), name='gsn-list'),
    path('gsn/create/', views.GSNCreateView.as_view(), name='gsn-create'),
    path('gsn/<int:pk>/', views.GSNDetailView.as_view(), name='gsn-detail'),
    path('gsn/<int:pk>/delete/', views.GSNDeleteView.as_view(), name='gsn-delete'),
    path('gsn/<int:pk>/print/', views.GSNPrintView.as_view(), name='gsn-print'),
    
    # Supplier Challan
    path('supplier-challan/', views.SupplierChallanListView.as_view(), name='supplier-challan-list'),
    path('supplier-challan/create/', views.SupplierChallanCreateView.as_view(), name='supplier-challan-create'),
    path('supplier-challan/<int:supplierchallanid>/', views.SupplierChallanDetailView.as_view(), name='supplier-challan-detail'),
    path('supplier-challan/<int:supplierchallanid>/delete/', views.SupplierChallanDeleteView.as_view(), name='supplier-challan-delete'),
    path('supplier-challan/<int:supplierchallanid>/print/', views.SupplierChallanPrintView.as_view(), name='supplier-challan-print'),
    path('supplier-challan/<int:supplierchallanid>/clear/', views.SupplierChallanClearView.as_view(), name='supplier-challan-clear'),
    path('supplier-challan/pending/', views.SupplierChallanPendingListView.as_view(), name='supplier-challan-pending'),
    
    # Customer Challan
    path('customer-challan/', views.CustomerChallanListView.as_view(), name='customer-challan-list'),
    path('customer-challan/create/', views.CustomerChallanCreateView.as_view(), name='customer-challan-create'),
    path('customer-challan/<int:customerchallanid>/', views.CustomerChallanDetailView.as_view(), name='customer-challan-detail'),
    path('customer-challan/<int:customerchallanid>/delete/', views.CustomerChallanDeleteView.as_view(), name='customer-challan-delete'),
    path('customer-challan/<int:customerchallanid>/print/', views.CustomerChallanPrintView.as_view(), name='customer-challan-print'),
    
    # Gate Pass
    path('gate-pass/', views.GatePassListView.as_view(), name='gate-pass-list'),
    path('gate-pass/create/', views.GatePassCreateView.as_view(), name='gate-pass-create'),
    path('gate-pass/<int:gatepassid>/', views.GatePassDetailView.as_view(), name='gate-pass-detail'),
    path('gate-pass/<int:gatepassid>/edit/', views.GatePassUpdateView.as_view(), name='gate-pass-edit'),
    path('gate-pass/<int:gatepassid>/print/', views.GatePassPrintView.as_view(), name='gate-pass-print'),
    path('gate-pass/<int:gatepassid>/return/', views.GatePassReturnView.as_view(), name='gate-pass-return'),
    path('gate-pass/pending/', views.GatePassPendingListView.as_view(), name='gate-pass-pending'),
    
    # Vehicle
    path('vehicle/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicle/create/', views.VehicleCreateView.as_view(), name='vehicle-create'),
    path('vehicle/<int:vehicleid>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicle/<int:vehicleid>/edit/', views.VehicleUpdateView.as_view(), name='vehicle-edit'),
    path('vehicle/<int:vehicleid>/trip/create/', views.VehicleTripCreateView.as_view(), name='vehicle-trip-create'),
    path('vehicle/<int:vehicleid>/history/', views.VehicleHistoryView.as_view(), name='vehicle-history'),
    
    # WIS (Work Instruction Sheet)
    path('wis/', views.WISListView.as_view(), name='wis-list'),
    path('wis/release-wo/', views.WISReleaseWOView.as_view(), name='wis-release-wo'),
    path('wis/stop-wo/', views.WISStopWOView.as_view(), name='wis-stop-wo'),
    path('wis/create/', views.WISCreateView.as_view(), name='wis-create'),
    path('wis/<int:pk>/', views.WISDetailView.as_view(), name='wis-detail'),
    path('wis/<int:pk>/release/', views.WISReleaseView.as_view(), name='wis-release'),
    path('wis/<int:pk>/actual-run/', views.WISActualRunView.as_view(), name='wis-actual-run'),
    path('wis/<int:pk>/print/', views.WISPrintView.as_view(), name='wis-print'),

    # WIS Dry Run (Material Issuance Simulation)
    path('wis/dry-run/', views.WISDryRunEntryView.as_view(), name='wis-dryrun-entry'),
    path('wis/dry-run/<str:wono>/assembly/', views.WISDryRunAssemblyView.as_view(), name='wis-dryrun-assembly'),
    path('wis/dry-run/<str:wono>/material/', views.WISDryRunMaterialView.as_view(), name='wis-dryrun-material'),
    path('wis/dry-run/<str:wono>/execute/', views.WISExecuteActualRunView.as_view(), name='wis-dryrun-execute'),

    # Item Location
    path('item-location/', views.ItemLocationListView.as_view(), name='item-location-list'),
    path('item-location/create/', views.ItemLocationCreateView.as_view(), name='item-location-create'),
    path('item-location/<int:itemlocationid>/delete/', views.ItemLocationDeleteView.as_view(), name='item-location-delete'),

    # Vehicle Master (SAP Fiori style with HTMX inline edit)
    path('vehicle-master/', views.VehicleMasterListView.as_view(), name='vehicle-master-list'),
    path('vehicle-master/create/', views.VehicleMasterCreateView.as_view(), name='vehicle-master-create'),
    path('vehicle-master/<int:pk>/edit/', views.VehicleMasterUpdateView.as_view(), name='vehicle-master-edit'),
    path('vehicle-master/<int:pk>/delete/', views.VehicleMasterDeleteView.as_view(), name='vehicle-master-delete'),
    path('vehicle-master/<int:pk>/row/', views.VehicleMasterRowView.as_view(), name='vehicle-master-row'),

    # Material Credit Note (MCN)
    path('mcn/', views.MCNListView.as_view(), name='mcn-list'),
    path('mcn/create/', views.MCNCreateView.as_view(), name='mcn-create'),
    path('mcn/<int:mcnid>/', views.MCNDetailView.as_view(), name='mcn-detail'),
    path('mcn/<int:mcnid>/delete/', views.MCNDeleteView.as_view(), name='mcn-delete'),
    path('mcn/<int:mcnid>/print/', views.MCNPrintView.as_view(), name='mcn-print'),
    
    # Closing Stock
    path('closing-stock/', views.ClosingStockView.as_view(), name='closing-stock'),

    # ============================================================================
    # AUTO WIS TIME SCHEDULE
    # ============================================================================
    path('autowis-schedule/', views.AutoWISTimeScheduleListView.as_view(), name='autowis-timeschedule-list'),
    path('autowis-schedule/create/', views.AutoWISTimeScheduleCreateView.as_view(), name='autowis-timeschedule-create'),
    path('autowis-schedule/<int:pk>/edit/', views.AutoWISTimeScheduleUpdateView.as_view(), name='autowis-timeschedule-edit'),
    path('autowis-schedule/<int:pk>/delete/', views.AutoWISTimeScheduleDeleteView.as_view(), name='autowis-timeschedule-delete'),
    path('autowis-schedule/<int:pk>/row/', views.AutoWISTimeScheduleRowView.as_view(), name='autowis-timeschedule-row'),
    
    # ============================================================================
    # REPORTS
    # ============================================================================
    
    # Stock Reports
    path('reports/stock-ledger/', views.StockLedgerSelectionView.as_view(), name='stock-ledger'),
    path('reports/stock-statement/', views.StockStatementView.as_view(), name='stock-statement'),
    
    # Analysis Reports
    path('reports/moving-items/', views.MovingNonMovingItemsView.as_view(), name='moving-items'),
    path('reports/abc-analysis/', views.ABCAnalysisView.as_view(), name='abc-analysis'),
    
    # Work Order Reports
    path('reports/work-order-shortage/', views.WorkOrderShortageView.as_view(), name='work-order-shortage'),
    path('reports/work-order-issue/', views.WorkOrderIssueView.as_view(), name='work-order-issue'),
    
    # Transaction Registers
    path('reports/inward-register/', views.InwardRegisterView.as_view(), name='inward-register'),
    path('reports/outward-register/', views.OutwardRegisterView.as_view(), name='outward-register'),
    
    # ============================================================================
    # SEARCH
    # ============================================================================
    
    path('search/', views.GlobalSearchView.as_view(), name='global-search'),
    path('search/advanced/', views.AdvancedSearchView.as_view(), name='advanced-search'),
    
    # ============================================================================
    # REGULAR CHALLAN
    # ============================================================================
    
    path('challan/', views.ChallanListView.as_view(), name='challan-list'),
    path('challan/create/', views.ChallanCreateView.as_view(), name='challan-create'),
    path('challan/<int:challanid>/', views.ChallanDetailView.as_view(), name='challan-detail'),
    path('challan/<int:challanid>/edit/', views.ChallanUpdateView.as_view(), name='challan-edit'),
    path('challan/<int:challanid>/delete/', views.ChallanDeleteView.as_view(), name='challan-delete'),
    path('challan/<int:challanid>/print/', views.ChallanPrintView.as_view(), name='challan-print'),
]
