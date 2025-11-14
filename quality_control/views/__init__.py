"""
Quality Control Views Package

Re-exports all views for backward compatibility with urls.py.
Views are organized by functional area:
- dashboard: Dashboard view
- masters: Rejection Reason CRUD
- gqn: Goods Quality Note workflow and CRUD
- mrqn: Material Return Quality Note workflow and CRUD
- authorized_mcn: Authorized MCN CRUD
- scrap: Scrap Register CRUD
- reports: Quality reports
"""

# Dashboard
from .dashboard import QualityControlDashboardView

# Masters
from .masters import (
    RejectionReasonListView,
    RejectionReasonCreateView,
    RejectionReasonUpdateView,
    RejectionReasonDeleteView,
    RejectionReasonDetailView,
)

# Goods Quality Note (GQN)
from .gqn import (
    GQNNewView,
    GQNGRRDetailsView,
    GQNSupplierAutocompleteView,
    GoodsQualityNoteCreateView,
    GoodsQualityNoteUpdateView,
    GoodsQualityNoteDetailView,
    GoodsQualityNoteDeleteView,
    GoodsQualityNotePrintView,
)
from .gqn_optimized import GoodsQualityNoteListViewOptimized as GoodsQualityNoteListView

# Material Return Quality Note (MRQN)
from .mrqn import (
    MaterialReturnQualityNoteListView,
    MaterialReturnQualityNoteCreateView,
    MaterialReturnQualityNoteCreateDetailsView,
    MaterialReturnQualityNoteUpdateView,
    MaterialReturnQualityNoteDetailView,
    MaterialReturnQualityNoteDeleteView,
    MaterialReturnQualityNotePrintView,
)
from .mrqn_new import (
    MRQNNewView,
    MRQNMRNDetailsView,
)

# Authorized MCN
from .authorized_mcn import (
    AuthorizedMCNListView,
    AuthorizedMCNCreateView,
    AuthorizedMCNDetailView,
    AuthorizedMCNDeleteView,
)

# Scrap Register
from .scrap import (
    ScrapRegisterListView,
    ScrapRegisterCreateView,
    ScrapRegisterDetailView,
    ScrapRegisterDeleteView,
)

# Reports
from .reports import (
    QualityReportView,
    RejectionAnalysisView,
)

# Export all for backward compatibility
__all__ = [
    # Dashboard
    'QualityControlDashboardView',

    # Masters
    'RejectionReasonListView',
    'RejectionReasonCreateView',
    'RejectionReasonUpdateView',
    'RejectionReasonDeleteView',
    'RejectionReasonDetailView',

    # GQN
    'GQNNewView',
    'GQNGRRDetailsView',
    'GoodsQualityNoteListView',
    'GQNSupplierAutocompleteView',
    'GoodsQualityNoteCreateView',
    'GoodsQualityNoteUpdateView',
    'GoodsQualityNoteDetailView',
    'GoodsQualityNoteDeleteView',
    'GoodsQualityNotePrintView',

    # MRQN
    'MRQNNewView',
    'MRQNMRNDetailsView',
    'MaterialReturnQualityNoteListView',
    'MaterialReturnQualityNoteCreateView',
    'MaterialReturnQualityNoteCreateDetailsView',
    'MaterialReturnQualityNoteUpdateView',
    'MaterialReturnQualityNoteDetailView',
    'MaterialReturnQualityNoteDeleteView',
    'MaterialReturnQualityNotePrintView',

    # Authorized MCN
    'AuthorizedMCNListView',
    'AuthorizedMCNCreateView',
    'AuthorizedMCNDetailView',
    'AuthorizedMCNDeleteView',

    # Scrap Register
    'ScrapRegisterListView',
    'ScrapRegisterCreateView',
    'ScrapRegisterDetailView',
    'ScrapRegisterDeleteView',

    # Reports
    'QualityReportView',
    'RejectionAnalysisView',
]
