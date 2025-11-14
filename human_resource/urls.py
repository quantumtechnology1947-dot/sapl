"""
Human Resource URL Configuration
Converted from ASP.NET Module/HR
"""

from django.urls import path
from . import views  # Import from views package (views/__init__.py re-exports all views)

app_name = 'human_resource'

urlpatterns = [
    # Dashboard
    path('', views.HRDashboardView.as_view(), name='dashboard'),

    # Business Group Master
    path('business-group/', views.BusinessGroupListView.as_view(), name='business-group-list'),
    path('business-group/create/', views.BusinessGroupCreateView.as_view(), name='business-group-create'),
    path('business-group/<int:id>/edit/', views.BusinessGroupUpdateView.as_view(), name='business-group-edit'),
    path('business-group/<int:id>/delete/', views.BusinessGroupDeleteView.as_view(), name='business-group-delete'),
    path('business-group/<int:id>/row/', views.BusinessGroupRowView.as_view(), name='business-group-row'),

    # Department Master
    path('department/', views.DepartmentListView.as_view(), name='department-list'),
    path('department/create/', views.DepartmentCreateView.as_view(), name='department-create'),
    path('department/<int:id>/edit/', views.DepartmentUpdateView.as_view(), name='department-edit'),
    path('department/<int:id>/delete/', views.DepartmentDeleteView.as_view(), name='department-delete'),
    path('department/<int:id>/row/', views.DepartmentRowView.as_view(), name='department-row'),

    # Designation Master
    path('designation/', views.DesignationListView.as_view(), name='designation-list'),
    path('designation/create/', views.DesignationCreateView.as_view(), name='designation-create'),
    path('designation/<int:id>/edit/', views.DesignationUpdateView.as_view(), name='designation-edit'),
    path('designation/<int:id>/delete/', views.DesignationDeleteView.as_view(), name='designation-delete'),
    path('designation/<int:id>/row/', views.DesignationRowView.as_view(), name='designation-row'),

    # Grade Master
    path('grade/', views.GradeListView.as_view(), name='grade-list'),
    path('grade/create/', views.GradeCreateView.as_view(), name='grade-create'),
    path('grade/<int:id>/edit/', views.GradeUpdateView.as_view(), name='grade-edit'),
    path('grade/<int:id>/delete/', views.GradeDeleteView.as_view(), name='grade-delete'),
    path('grade/<int:id>/row/', views.GradeRowView.as_view(), name='grade-row'),

    # Holiday Master
    path('holiday/', views.HolidayMasterListView.as_view(), name='holiday-master-list'),
    path('holiday/create/', views.HolidayMasterCreateView.as_view(), name='holiday-master-create'),
    path('holiday/<int:id>/edit/', views.HolidayMasterUpdateView.as_view(), name='holiday-master-edit'),
    path('holiday/<int:id>/delete/', views.HolidayMasterDeleteView.as_view(), name='holiday-master-delete'),
    path('holiday/<int:id>/row/', views.HolidayMasterRowView.as_view(), name='holiday-master-row'),

    # Working Days Master
    path('working-days/', views.WorkingDaysListView.as_view(), name='working-days-list'),
    path('working-days/create/', views.WorkingDaysCreateView.as_view(), name='working-days-create'),
    path('working-days/<int:id>/edit/', views.WorkingDaysUpdateView.as_view(), name='working-days-edit'),
    path('working-days/<int:id>/delete/', views.WorkingDaysDeleteView.as_view(), name='working-days-delete'),
    path('working-days/<int:id>/row/', views.WorkingDaysRowView.as_view(), name='working-days-row'),

    # Corporate Mobile No Master
    path('corporate-mobile/', views.CorporateMobileNoListView.as_view(), name='corporate-mobile-list'),
    path('corporate-mobile/create/', views.CorporateMobileNoCreateView.as_view(), name='corporate-mobile-create'),
    path('corporate-mobile/<int:id>/edit/', views.CorporateMobileNoUpdateView.as_view(), name='corporate-mobile-edit'),
    path('corporate-mobile/<int:id>/delete/', views.CorporateMobileNoDeleteView.as_view(), name='corporate-mobile-delete'),
    path('corporate-mobile/<int:id>/row/', views.CorporateMobileNoRowView.as_view(), name='corporate-mobile-row'),

    # Gate Pass Reason Master
    path('gatepass-reason/', views.GatePassReasonListView.as_view(), name='gatepass-reason-list'),
    path('gatepass-reason/create/', views.GatePassReasonCreateView.as_view(), name='gatepass-reason-create'),
    path('gatepass-reason/<int:id>/edit/', views.GatePassReasonUpdateView.as_view(), name='gatepass-reason-edit'),
    path('gatepass-reason/<int:id>/delete/', views.GatePassReasonDeleteView.as_view(), name='gatepass-reason-delete'),
    path('gatepass-reason/<int:id>/row/', views.GatePassReasonRowView.as_view(), name='gatepass-reason-row'),

    # Intercom Extension Master
    path('intercom-ext/', views.IntercomExtListView.as_view(), name='intercom-ext-list'),
    path('intercom-ext/create/', views.IntercomExtCreateView.as_view(), name='intercom-ext-create'),
    path('intercom-ext/<int:id>/edit/', views.IntercomExtUpdateView.as_view(), name='intercom-ext-edit'),
    path('intercom-ext/<int:id>/delete/', views.IntercomExtDeleteView.as_view(), name='intercom-ext-delete'),
    path('intercom-ext/<int:id>/row/', views.IntercomExtRowView.as_view(), name='intercom-ext-row'),

    # PF Slab Master
    path('pf-slab/', views.PFSlabListView.as_view(), name='pf-slab-list'),
    path('pf-slab/create/', views.PFSlabCreateView.as_view(), name='pf-slab-create'),
    path('pf-slab/<int:id>/edit/', views.PFSlabUpdateView.as_view(), name='pf-slab-edit'),
    path('pf-slab/<int:id>/delete/', views.PFSlabDeleteView.as_view(), name='pf-slab-delete'),
    path('pf-slab/<int:id>/row/', views.PFSlabRowView.as_view(), name='pf-slab-row'),

    # Swap Card Master
    path('swap-card/', views.SwapCardListView.as_view(), name='swap-card-list'),
    path('swap-card/create/', views.SwapCardCreateView.as_view(), name='swap-card-create'),
    path('swap-card/<int:id>/edit/', views.SwapCardUpdateView.as_view(), name='swap-card-edit'),
    path('swap-card/<int:id>/delete/', views.SwapCardDeleteView.as_view(), name='swap-card-delete'),
    path('swap-card/<int:id>/row/', views.SwapCardRowView.as_view(), name='swap-card-row'),

    # Employee Management (Transactions)
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee-edit'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee-delete'),

    # Salary Management (Transactions - Phase 2)
    path('salary/', views.SalaryEmployeeListView.as_view(), name='salary-employee-list'),
    path('salary/create/<str:empid>/<int:month>/', views.SalaryCreateView.as_view(), name='salary-create'),
    path('salary/list/', views.SalaryListView.as_view(), name='salary-list'),
    path('salary/<int:pk>/', views.SalaryDetailView.as_view(), name='salary-detail'),
    path('salary/<int:pk>/edit/', views.SalaryUpdateView.as_view(), name='salary-edit'),
    path('salary/<int:pk>/delete/', views.SalaryDeleteView.as_view(), name='salary-delete'),
    path('salary/bank-statement/', views.SalaryBankStatementView.as_view(), name='salary-bank-statement'),
    path('salary/bank-statement/export/', views.SalaryBankStatementExportView.as_view(), name='salary-bank-statement-export'),

    # Bank Loan Management (Phase 3)
    path('bank-loan/', views.BankLoanListView.as_view(), name='bank-loan-list'),
    path('bank-loan/create/', views.BankLoanCreateView.as_view(), name='bank-loan-create'),
    path('bank-loan/<int:pk>/', views.BankLoanDetailView.as_view(), name='bank-loan-detail'),
    path('bank-loan/<int:pk>/edit/', views.BankLoanUpdateView.as_view(), name='bank-loan-edit'),
    path('bank-loan/<int:pk>/delete/', views.BankLoanDeleteView.as_view(), name='bank-loan-delete'),

    # Mobile Bill Management (Phase 3)
    path('mobile-bill/', views.MobileBillListView.as_view(), name='mobile-bill-list'),
    path('mobile-bill/create/', views.MobileBillCreateView.as_view(), name='mobile-bill-create'),
    path('mobile-bill/<int:pk>/', views.MobileBillDetailView.as_view(), name='mobile-bill-detail'),
    path('mobile-bill/<int:pk>/edit/', views.MobileBillUpdateView.as_view(), name='mobile-bill-edit'),
    path('mobile-bill/<int:pk>/delete/', views.MobileBillDeleteView.as_view(), name='mobile-bill-delete'),

    # Offer Letter Management (Phase 4)
    path('offer-letter/', views.OfferLetterListView.as_view(), name='offer-letter-list'),
    path('offer-letter/create/', views.OfferLetterCreateView.as_view(), name='offer-letter-create'),
    path('offer-letter/<int:pk>/', views.OfferLetterDetailView.as_view(), name='offer-letter-detail'),
    path('offer-letter/<int:pk>/edit/', views.OfferLetterUpdateView.as_view(), name='offer-letter-edit'),
    path('offer-letter/<int:pk>/delete/', views.OfferLetterDeleteView.as_view(), name='offer-letter-delete'),

    # Gate Pass Management (Phase 6)
    path('gatepass/', views.GatePassListView.as_view(), name='gatepass-list'),
    path('gatepass/create/', views.GatePassCreateView.as_view(), name='gatepass-create'),
    path('gatepass/<int:pk>/', views.GatePassDetailView.as_view(), name='gatepass-detail'),
    path('gatepass/<int:pk>/edit/', views.GatePassUpdateView.as_view(), name='gatepass-edit'),
    path('gatepass/<int:pk>/delete/', views.GatePassDeleteView.as_view(), name='gatepass-delete'),

    # Tour Intimation Management (Transactions - Phase 5)
    path('tour-intimation/', views.TourIntimationListView.as_view(), name='tour-intimation-list'),
    path('tour-intimation/create/', views.TourIntimationCreateView.as_view(), name='tour-intimation-create'),
    path('tour-intimation/<int:pk>/', views.TourIntimationDetailView.as_view(), name='tour-intimation-detail'),
    path('tour-intimation/<int:pk>/edit/', views.TourIntimationUpdateView.as_view(), name='tour-intimation-edit'),
    path('tour-intimation/<int:pk>/delete/', views.TourIntimationDeleteView.as_view(), name='tour-intimation-delete'),
    
    # New Simplified Master Views
    path('dept/', views.DepartmentListView.as_view(), name='dept-list'),
    path('dept/create/', views.DepartmentCreateView.as_view(), name='dept-create'),
    path('dept/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='dept-update'),
    path('dept/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='dept-delete'),
    
    path('desig/', views.DesignationListView.as_view(), name='desig-list'),
    path('desig/create/', views.DesignationCreateView.as_view(), name='desig-create'),
    path('desig/<int:pk>/update/', views.DesignationUpdateView.as_view(), name='desig-update'),
    path('desig/<int:pk>/delete/', views.DesignationDeleteView.as_view(), name='desig-delete'),
    
    path('holidays/', views.HolidayMasterListView.as_view(), name='holidays-list'),
    path('holidays/create/', views.HolidayMasterCreateView.as_view(), name='holidays-create'),
    path('holidays/<int:pk>/update/', views.HolidayMasterUpdateView.as_view(), name='holidays-update'),
    path('holidays/<int:pk>/delete/', views.HolidayMasterDeleteView.as_view(), name='holidays-delete'),

    # TODO: Implement EmployeeType views
    # path('emptype/', views.EmployeeTypeListView.as_view(), name='emptype-list'),
    # path('emptype/create/', views.EmployeeTypeCreateView.as_view(), name='emptype-create'),
    # path('emptype/<int:pk>/update/', views.EmployeeTypeUpdateView.as_view(), name='emptype-update'),
    # path('emptype/<int:pk>/delete/', views.EmployeeTypeDeleteView.as_view(), name='emptype-delete'),

    # Note: Grade views are already defined above (lines 37-41)

    # TODO: Implement Shift views
    # path('shifts/', views.ShiftListView.as_view(), name='shift-list'),
    # path('shifts/create/', views.ShiftCreateView.as_view(), name='shift-create'),
    # path('shifts/<int:pk>/update/', views.ShiftUpdateView.as_view(), name='shift-update'),
    # path('shifts/<int:pk>/delete/', views.ShiftDeleteView.as_view(), name='shift-delete'),

    # TODO: Implement Overtime views
    # path('overtime/', views.OvertimeListView.as_view(), name='overtime-list'),
    # path('overtime/create/', views.OvertimeCreateView.as_view(), name='overtime-create'),
    # path('overtime/<int:pk>/update/', views.OvertimeUpdateView.as_view(), name='overtime-update'),
    # path('overtime/<int:pk>/delete/', views.OvertimeDeleteView.as_view(), name='overtime-delete'),

    # Note: PF Slab views are already defined above (lines 79-83)

    # TODO: Implement Swapcard views
    # path('swapcard/', views.SwapcardListView.as_view(), name='swapcard-list'),
    # path('swapcard/create/', views.SwapcardCreateView.as_view(), name='swapcard-create'),
    # path('swapcard/<int:pk>/update/', views.SwapcardUpdateView.as_view(), name='swapcard-update'),
    # path('swapcard/<int:pk>/delete/', views.SwapcardDeleteView.as_view(), name='swapcard-delete'),
    
    path('working-days/', views.WorkingDaysListView.as_view(), name='working-days-list'),
    path('working-days/create/', views.WorkingDaysCreateView.as_view(), name='working-days-create'),
    path('working-days/<int:pk>/update/', views.WorkingDaysUpdateView.as_view(), name='working-days-update'),
    path('working-days/<int:pk>/delete/', views.WorkingDaysDeleteView.as_view(), name='working-days-delete'),
    
    # TODO: Implement Increment Master views
    # path('masters/increment/', views.IncrementListView.as_view(), name='increment-list'),
    # path('masters/increment/create/', views.IncrementCreateView.as_view(), name='increment-create'),
    # path('masters/increment/<int:pk>/update/', views.IncrementUpdateView.as_view(), name='increment-update'),
    # path('masters/increment/<int:pk>/delete/', views.IncrementDeleteView.as_view(), name='increment-delete'),
    
    # TODO: Implement Offer Master views
    # path('masters/offer/', views.OfferListView.as_view(), name='offer-list'),
    # path('masters/offer/create/', views.OfferCreateView.as_view(), name='offer-create'),
    # path('masters/offer/<int:offerid>/update/', views.OfferUpdateView.as_view(), name='offer-update'),
    # path('masters/offer/<int:offerid>/delete/', views.OfferDeleteView.as_view(), name='offer-delete'),
]
