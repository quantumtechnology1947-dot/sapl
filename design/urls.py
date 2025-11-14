"""
Design URL Configuration
Converted from ASP.NET Module/Design
Updated: 2025-10-26
"""

from django.urls import path
from . import views
# from . import bom_add_child_views  # Module doesn't exist

app_name = 'design'

urlpatterns = [
    # Design Category Master
    path('category/', views.DesignCategoryListView.as_view(), name='category-list'),
    path('category/create/', views.DesignCategoryCreateView.as_view(), name='category-create'),
    path('category/<int:cid>/edit/', views.DesignCategoryUpdateView.as_view(), name='category-edit'),
    path('category/<int:cid>/delete/', views.DesignCategoryDeleteView.as_view(), name='category-delete'),

    # Design Sub-Category Master
    path('subcategory/', views.DesignSubCategoryListView.as_view(), name='subcategory-list'),
    path('subcategory/create/', views.DesignSubCategoryCreateView.as_view(), name='subcategory-create'),
    path('subcategory/<int:scid>/edit/', views.DesignSubCategoryUpdateView.as_view(), name='subcategory-edit'),
    path('subcategory/<int:scid>/delete/', views.DesignSubCategoryDeleteView.as_view(), name='subcategory-delete'),

    # Unit Master
    path('unit-master/', views.UnitMasterListView.as_view(), name='unit-master-list'),
    path('unit-master/create/', views.UnitMasterCreateView.as_view(), name='unit-master-create'),
    path('unit-master/<int:id>/edit/', views.UnitMasterUpdateView.as_view(), name='unit-master-edit'),
    path('unit-master/<int:id>/delete/', views.UnitMasterDeleteView.as_view(), name='unit-master-delete'),

    # ECN Reasons Master
    path('ecn-reason/', views.EcnReasonListView.as_view(), name='ecn-reason-list'),
    path('ecn-reason/create/', views.EcnReasonCreateView.as_view(), name='ecn-reason-create'),
    path('ecn-reason/<int:id>/edit/', views.EcnReasonUpdateView.as_view(), name='ecn-reason-edit'),
    path('ecn-reason/<int:id>/delete/', views.EcnReasonDeleteView.as_view(), name='ecn-reason-delete'),

    # Item Master
    path('item/', views.ItemMasterListView.as_view(), name='item-list'),
    path('item/create/', views.ItemMasterCreateView.as_view(), name='item-create'),
    path('item/<int:id>/', views.ItemMasterDetailView.as_view(), name='item-detail'),
    path('item/<int:id>/edit/', views.ItemMasterUpdateView.as_view(), name='item-edit'),
    path('item/<int:id>/delete/', views.ItemMasterDeleteView.as_view(), name='item-delete'),
    path('item/<int:id>/download-file/', views.ItemFileDownloadView.as_view(), name='item-download-file'),
    path('item/<int:id>/download-attachment/', views.ItemAttachmentDownloadView.as_view(), name='item-download-attachment'),

    # BOM Management
    path('bom/', views.BomListView.as_view(), name='bom-list'),
    path('bom/create/select/', views.BomCreateSelectWoView.as_view(), name='bom-create-select'),
    path('bom/create/', views.BomCreateView.as_view(), name='bom-create'),
    path('bom/copy/', views.BomCopyView.as_view(), name='bom-copy'),
    path('bom/<str:wono>/tree/', views.BomTreeView.as_view(), name='bom-tree'),

    # Phase 2: Assembly and Item Addition
    path('bom/<str:wono>/add-assembly/', views.BomCreateAssemblyView.as_view(), name='bom-add-assembly'),

    # Phase 3: 4-Tab Wizard for Adding Items
    path('bom/<str:wono>/<int:parent_cid>/add-items/', views.BomAddItemsWizardView.as_view(), name='bom-wizard'),
    path('bom/<str:wono>/<int:parent_cid>/wizard-search/', views.BomWizardSearchItemsView.as_view(), name='bom-wizard-search'),
    path('bom/<str:wono>/<int:parent_cid>/wizard-add-existing/', views.BomWizardAddExistingItemView.as_view(), name='bom-wizard-add-existing'),
    path('bom/<str:wono>/<int:parent_cid>/wizard-add-new/', views.BomWizardAddNewItemView.as_view(), name='bom-wizard-add-new'),
    path('bom/<str:wono>/<int:parent_cid>/wizard-remove/', views.BomWizardRemoveItemView.as_view(), name='bom-wizard-remove'),
    path('bom/<str:wono>/<int:parent_cid>/wizard-commit/', views.BomWizardCommitView.as_view(), name='bom-wizard-commit'),
    path('bom/<str:wono>/<int:parent_cid>/wizard-cancel/', views.BomWizardCancelView.as_view(), name='bom-wizard-cancel'),

    # Legacy (kept for backward compatibility)
    path('bom/<int:parent_id>/add-child/', views.BomAddChildView.as_view(), name='bom-add-child'),

    path('bom/<int:id>/edit/', views.BomUpdateView.as_view(), name='bom-edit'),
    path('bom/<int:id>/delete/', views.BomDeleteView.as_view(), name='bom-delete'),
    path('bom/amendment-history/', views.BomAmendmentHistoryView.as_view(), name='bom-amendment-history'),

    # ECN Management
    path('ecn/', views.EcnListView.as_view(), name='ecn-list'),
    path('ecn/create/', views.EcnCreateView.as_view(), name='ecn-create'),
    path('ecn/<int:id>/', views.EcnDetailView.as_view(), name='ecn-detail'),
    path('ecn/<int:id>/edit/', views.EcnUpdateView.as_view(), name='ecn-edit'),
    path('ecn/<int:id>/apply/', views.EcnApplyView.as_view(), name='ecn-apply'),
    
    # ECN Unlock (Work Order based)
    path('ecn-unlock/', views.EcnWoListView.as_view(), name='ecn-wo-list'),
    path('ecn-unlock/<str:wono>/', views.EcnUnlockView.as_view(), name='ecn-unlock-detail'),

    # Item History BOM Reports
    path('reports/item-history-bom/', views.ItemHistoryBomSearchView.as_view(), name='item-history-bom-search'),
    path('reports/item-history-bom/<int:id>/', views.ItemHistoryBomDetailView.as_view(), name='item-history-bom-detail'),

    # HTMX Helper Endpoints
    path('subcategory/by-category/', views.SubCategoryByCategoryView.as_view(), name='subcategory-by-category'),
    path('api/search-items/', views.ItemSearchApiView.as_view(), name='api-search-items'),
    
    # BOM Tree AJAX API Endpoints
    path('api/bom/update-quantity/', views.BomUpdateQuantityApiView.as_view(), name='api-bom-update-quantity'),
    
    # BOM Wizard AJAX API Endpoints
    path('api/bom/search-items/', views.BomSearchItemsApiView.as_view(), name='api-bom-search-items'),
    path('api/bom/stage-item/', views.BomStageItemApiView.as_view(), name='api-bom-stage-item'),
    path('api/bom/staged-items/', views.BomGetStagedItemsApiView.as_view(), name='api-bom-get-staged-items'),
    path('api/bom/unstage-item/', views.BomUnstagItemApiView.as_view(), name='api-bom-unstage-item'),
    path('api/bom/commit-staged-items/', views.BomCommitStagedItemsApiView.as_view(), name='api-bom-commit-staged-items'),
    path('api/bom/clear-staged-items/', views.BomClearStagedItemsApiView.as_view(), name='api-bom-clear-staged-items'),
    path('api/bom/bulk-delete/', views.BomBulkDeleteApiView.as_view(), name='api-bom-bulk-delete'),
]
