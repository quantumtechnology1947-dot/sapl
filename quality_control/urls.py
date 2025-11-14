"""
Quality Control Module URL Configuration
"""

from django.urls import path
from . import views

app_name = 'quality_control'

urlpatterns = [
    # Dashboard
    path('', views.QualityControlDashboardView.as_view(), name='dashboard'),

    # Rejection Reason Master
    path('rejection-reasons/', views.RejectionReasonListView.as_view(), name='rejection-reason-list'),
    path('rejection-reasons/create/', views.RejectionReasonCreateView.as_view(), name='rejection-reason-create'),
    path('rejection-reasons/<int:pk>/update/', views.RejectionReasonUpdateView.as_view(), name='rejection-reason-update'),
    path('rejection-reasons/<int:pk>/delete/', views.RejectionReasonDeleteView.as_view(), name='rejection-reason-delete'),

    # Goods Quality Note (GQN) - Multi-step workflow
    path('gqn/', views.GoodsQualityNoteListView.as_view(), name='gqn-list'),
    path('gqn/supplier-autocomplete/', views.GQNSupplierAutocompleteView.as_view(), name='gqn-supplier-autocomplete'),
    path('gqn/new/', views.GQNNewView.as_view(), name='gqn-new'),  # Step 1: List pending GRRs
    path('gqn/grr/<int:grr_id>/', views.GQNGRRDetailsView.as_view(), name='gqn-grr-details'),  # Step 2: GRR details & quality inspection
    path('gqn/create/', views.GoodsQualityNoteCreateView.as_view(), name='gqn-create'),  # Old direct create (keep for backward compat)
    path('gqn/<int:pk>/', views.GoodsQualityNoteDetailView.as_view(), name='gqn-detail'),
    path('gqn/<int:pk>/update/', views.GoodsQualityNoteUpdateView.as_view(), name='gqn-update'),
    path('gqn/<int:pk>/delete/', views.GoodsQualityNoteDeleteView.as_view(), name='gqn-delete'),
    path('gqn/<int:pk>/print/', views.GoodsQualityNotePrintView.as_view(), name='gqn-print'),

    # Material Return Quality Note (MRQN) - Multi-step workflow
    path('mrqn/', views.MaterialReturnQualityNoteListView.as_view(), name='mrqn-list'),
    path('mrqn/new/', views.MRQNNewView.as_view(), name='mrqn-new'),  # Step 1: List pending MRNs
    path('mrqn/mrn/<int:mrn_id>/', views.MRQNMRNDetailsView.as_view(), name='mrqn-mrn-details'),  # Step 2: MRN details & quality inspection
    path('mrqn/create/', views.MaterialReturnQualityNoteCreateView.as_view(), name='mrqn-create'),  # Old direct create (keep for backward compat)
    path('mrqn/create/details/', views.MaterialReturnQualityNoteCreateDetailsView.as_view(), name='mrqn-create-details'),
    path('mrqn/<int:pk>/', views.MaterialReturnQualityNoteDetailView.as_view(), name='mrqn-detail'),
    path('mrqn/<int:pk>/update/', views.MaterialReturnQualityNoteUpdateView.as_view(), name='mrqn-update'),
    path('mrqn/<int:pk>/delete/', views.MaterialReturnQualityNoteDeleteView.as_view(), name='mrqn-delete'),
    path('mrqn/<int:pk>/print/', views.MaterialReturnQualityNotePrintView.as_view(), name='mrqn-print'),

    # Authorized MCN
    path('authorized-mcn/', views.AuthorizedMCNListView.as_view(), name='authorized-mcn-list'),
    path('authorized-mcn/create/', views.AuthorizedMCNCreateView.as_view(), name='authorized-mcn-create'),
    path('authorized-mcn/<int:pk>/', views.AuthorizedMCNDetailView.as_view(), name='authorized-mcn-detail'),
    path('authorized-mcn/<int:pk>/delete/', views.AuthorizedMCNDeleteView.as_view(), name='authorized-mcn-delete'),

    # Scrap Register
    path('scrap-register/', views.ScrapRegisterListView.as_view(), name='scrap-register-list'),
    path('scrap-register/create/', views.ScrapRegisterCreateView.as_view(), name='scrap-register-create'),
    path('scrap-register/<int:pk>/', views.ScrapRegisterDetailView.as_view(), name='scrap-register-detail'),
    path('scrap-register/<int:pk>/delete/', views.ScrapRegisterDeleteView.as_view(), name='scrap-register-delete'),

    # Reports
    path('reports/quality-report/', views.QualityReportView.as_view(), name='quality-report'),
    path('reports/rejection-analysis/', views.RejectionAnalysisView.as_view(), name='rejection-analysis'),
    
    # Rejection Reason Master
    path('masters/rejection-reason/', views.RejectionReasonListView.as_view(), name='rejection-reason-list'),
    path('masters/rejection-reason/create/', views.RejectionReasonCreateView.as_view(), name='rejection-reason-create'),
    path('masters/rejection-reason/<int:pk>/update/', views.RejectionReasonUpdateView.as_view(), name='rejection-reason-update'),
    path('masters/rejection-reason/<int:pk>/delete/', views.RejectionReasonDeleteView.as_view(), name='rejection-reason-delete'),
]
