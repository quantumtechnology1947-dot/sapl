"""
Inventory Views - Modular Structure
All views organized by functional area.
"""

# Dashboard
from .dashboard import InventoryDashboardView

# Material Requisition Slip (MRS)
from .mrs import (
    MRSListView,
    MRSCreateView,
    MRSSearchItemsView,
    MRSAddToCartView,
    MRSRemoveFromCartView,
    MRSDetailView,
    MRSDeleteView,
    MRSPrintView,
    MRSPendingListView,
)

# Material Issue Note (MIN)
from .min import (
    MINListView,
    MINCreateView,
    MINDetailView,
    MINDeleteView,
    MINPrintView,
)

# Material Return Note (MRN)
from .mrn import (
    MRNListView,
    MRNCreateView,
    MRNDetailView,
    MRNDeleteView,
    MRNPrintView,
)

# Goods Inward Note (GIN)
from .gin import (
    GINListView,
    GINCreateView,
    GINDetailView,
    GINDetailUpdateView,
    GINMasterUpdateView,
    GINDeleteView,
    GINPrintView,
    GINPendingListView,
    GINPOSearchResultsView,
    GINCreateFromPOView,
    GINPODetailsView,
)

# Goods Received Receipt (GRR)
from .grr import (
    GRRListView,
    GRRCreateView,
    GRRDetailView,
    GRRDeleteView,
    GRRPrintView,
    GRREditListView,
    GRREditDetailView,
)

# Goods Service Note (GSN)
from .gsn import (
    GSNListView,
    GSNCreateView,
    GSNDetailView,
    GSNDeleteView,
    GSNPrintView,
)

# Challans (Supplier, Customer, and Generic)
from .challan import (
    SupplierChallanListView,
    SupplierChallanCreateView,
    SupplierChallanDetailView,
    SupplierChallanDeleteView,
    SupplierChallanPrintView,
    SupplierChallanClearView,
    SupplierChallanPendingListView,
    CustomerChallanListView,
    CustomerChallanCreateView,
    CustomerChallanDetailView,
    CustomerChallanDeleteView,
    CustomerChallanPrintView,
    ChallanListView,
    ChallanCreateView,
    ChallanDetailView,
    ChallanUpdateView,
    ChallanDeleteView,
    ChallanPrintView,
)

# Gate Pass
from .gate_pass import (
    GatePassListView,
    GatePassCreateView,
    GatePassDetailView,
    GatePassUpdateView,
    GatePassPrintView,
    GatePassReturnView,
    GatePassPendingListView,
)

# Vehicle Management
from .vehicle import (
    VehicleListView,
    VehicleCreateView,
    VehicleDetailView,
    VehicleUpdateView,
    VehicleTripCreateView,
    VehicleHistoryView,
    VehicleProcessMasterListView,
    VehicleProcessMasterCreateView,
    VehicleProcessMasterUpdateView,
    VehicleProcessMasterDeleteView,
    VehicleMasterListView,
    VehicleMasterCreateView,
    VehicleMasterUpdateView,
    VehicleMasterDeleteView,
    VehicleMasterRowView,
)

# WIS (Work Instruction Sheet)
from .wis import (
    WISListView,
    WISCreateView,
    WISDetailView,
    WISReleaseView,
    WISActualRunView,
    WISPrintView,
    AutoWISTimeScheduleListView,
    AutoWISTimeScheduleCreateView,
    AutoWISTimeScheduleUpdateView,
    AutoWISTimeScheduleDeleteView,
    AutoWISTimeScheduleRowView,
)

# Item Location
from .item_location import (
    ItemLocationListView,
    ItemLocationCreateView,
    ItemLocationDeleteView,
)

# Reports and MCN
from .reports import (
    MCNListView,
    MCNCreateView,
    MCNDetailView,
    MCNDeleteView,
    MCNPrintView,
    ClosingStockView,
    ClosingStockReportView,
    OutwardRegisterView,
    StockStatementView,
    ABCAnalysisView,
    MovingNonMovingItemsView,
    WorkOrderIssueView,
    WorkOrderShortageView,
    InwardRegisterView,
    StockLedgerSelectionView,
)

# Utilities (Search, Download)
from .utilities import (
    GlobalSearchView,
    AdvancedSearchView,
    ItemImageDownloadView,
    ItemSpecDownloadView,
)

__all__ = [
    # Dashboard
    'InventoryDashboardView',
    # MRS
    'MRSListView',
    'MRSCreateView',
    'MRSSearchItemsView',
    'MRSAddToCartView',
    'MRSRemoveFromCartView',
    'MRSDetailView',
    'MRSDeleteView',
    'MRSPrintView',
    'MRSPendingListView',
    # MIN
    'MINListView',
    'MINCreateView',
    'MINDetailView',
    'MINDeleteView',
    'MINPrintView',
    # MRN
    'MRNListView',
    'MRNCreateView',
    'MRNDetailView',
    'MRNDeleteView',
    'MRNPrintView',
    # GIN
    'GINListView',
    'GINCreateView',
    'GINDetailView',
    'GINDetailUpdateView',
    'GINMasterUpdateView',
    'GINDeleteView',
    'GINPrintView',
    'GINPendingListView',
    'GINPOSearchResultsView',
    'GINCreateFromPOView',
    'GINPODetailsView',
    # GRR
    'GRRListView',
    'GRRCreateView',
    'GRRDetailView',
    'GRRDeleteView',
    'GRRPrintView',
    'GRREditListView',
    'GRREditDetailView',
    # GSN
    'GSNListView',
    'GSNCreateView',
    'GSNDetailView',
    'GSNDeleteView',
    'GSNPrintView',
    # Challans
    'SupplierChallanListView',
    'SupplierChallanCreateView',
    'SupplierChallanDetailView',
    'SupplierChallanDeleteView',
    'SupplierChallanPrintView',
    'SupplierChallanClearView',
    'SupplierChallanPendingListView',
    'CustomerChallanListView',
    'CustomerChallanCreateView',
    'CustomerChallanDetailView',
    'CustomerChallanDeleteView',
    'CustomerChallanPrintView',
    'ChallanListView',
    'ChallanCreateView',
    'ChallanDetailView',
    'ChallanUpdateView',
    'ChallanDeleteView',
    'ChallanPrintView',
    # Gate Pass
    'GatePassListView',
    'GatePassCreateView',
    'GatePassDetailView',
    'GatePassUpdateView',
    'GatePassPrintView',
    'GatePassReturnView',
    'GatePassPendingListView',
    # Vehicle
    'VehicleListView',
    'VehicleCreateView',
    'VehicleDetailView',
    'VehicleUpdateView',
    'VehicleTripCreateView',
    'VehicleHistoryView',
    'VehicleProcessMasterListView',
    'VehicleProcessMasterCreateView',
    'VehicleProcessMasterUpdateView',
    'VehicleProcessMasterDeleteView',
    'VehicleMasterListView',
    'VehicleMasterCreateView',
    'VehicleMasterUpdateView',
    'VehicleMasterDeleteView',
    'VehicleMasterRowView',
    # WIS
    'WISListView',
    'WISCreateView',
    'WISDetailView',
    'WISReleaseView',
    'WISActualRunView',
    'WISPrintView',
    'AutoWISTimeScheduleListView',
    'AutoWISTimeScheduleCreateView',
    'AutoWISTimeScheduleUpdateView',
    'AutoWISTimeScheduleDeleteView',
    'AutoWISTimeScheduleRowView',
    # Item Location
    'ItemLocationListView',
    'ItemLocationCreateView',
    'ItemLocationDeleteView',
    # Reports
    'MCNListView',
    'MCNCreateView',
    'MCNDetailView',
    'MCNDeleteView',
    'MCNPrintView',
    'ClosingStockView',
    'ClosingStockReportView',
    'OutwardRegisterView',
    'StockStatementView',
    'ABCAnalysisView',
    'MovingNonMovingItemsView',
    'WorkOrderIssueView',
    'WorkOrderShortageView',
    'InwardRegisterView',
    'StockLedgerSelectionView',
    # Utilities
    'GlobalSearchView',
    'AdvancedSearchView',
    'ItemImageDownloadView',
    'ItemSpecDownloadView',
]
