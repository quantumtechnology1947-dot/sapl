"""
MIS URL Configuration
"""

from django.urls import path
from mis import views

app_name = 'mis'

urlpatterns = [
    # MIS Transaction Menu
    path('transactions/menu/', views.MISTransactionMenuView.as_view(), name='transaction_menu'),
    
    # Business Group Budget Assignment (main assign page)
    path('transactions/business-group-budget/', views.BusinessGroupBudgetAssignView.as_view(), name='business_group_budget'),

    # Business Group Budget Detail (shows individual records for a BG)
    path('transactions/business-group-detail/<int:bg_id>/', views.BusinessGroupDetailView.as_view(), name='business_group_detail'),

    # Work order search and budget allocation
    path('transactions/wo-search/', views.WorkOrderBudgetSearchView.as_view(), name='wo_search'),
    path('transactions/budget-allocation/', views.BudgetAllocationView.as_view(), name='budget_allocation'),
    
    # Work Order Budget Detail (Budget_WONo.aspx equivalent)
    path('transactions/budget-wo/<str:wo_no>/', views.WOBudgetDetailView.as_view(), name='wo_budget_detail'),
    
    # Budget Code Master
    path('masters/budget-code/', views.BudgetCodeListView.as_view(), name='budget_code_list'),
    path('masters/budget-code/create/', views.BudgetCodeCreateView.as_view(), name='budget_code_create'),
    path('masters/budget-code/<int:pk>/', views.BudgetCodeDetailView.as_view(), name='budget_code_detail'),
    path('masters/budget-code/<int:pk>/edit/', views.BudgetCodeUpdateView.as_view(), name='budget_code_update'),
    path('masters/budget-code/<int:pk>/delete/', views.BudgetCodeDeleteView.as_view(), name='budget_code_delete'),
    
    # AJAX endpoints
    path('api/autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),

    # Budget Hours Field Category and Sub-Category Management
    path('transactions/budget-hrs-fields/', views.BudgetHrsFieldCategorySubCategoryView.as_view(), name='budget_hrs_fields'),

    # Budget Hours Assignment (Time-based budget allocation)
    path('transactions/budget-hrs-assign/', views.BudgetHoursAssignView.as_view(), name='budget_hours_assign'),
    path('transactions/budget-hrs-wo-search/', views.BudgetHoursWorkOrderSearchView.as_view(), name='budget_hours_wo_search'),
    path('transactions/budget-hrs-wo/<str:wo_no>/', views.WOBudgetHoursDetailView.as_view(), name='wo_budget_hours_detail'),

    # AJAX API for subcategories
    path('api/subcategories/', views.BudgetHoursSubCategoryAPIView.as_view(), name='api_subcategories'),
]
