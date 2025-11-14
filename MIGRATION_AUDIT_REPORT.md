ASP.NET TO DJANGO MIGRATION AUDIT REPORT

## SUMMARY STATISTICS
----------------------------------------------------------------------------------------------------
Total Menu Items in Web.sitemap: 190
Total .aspx Files Found: 941
Total Django View Files: 119
Total Django URL Patterns: 914

## MODULE-WISE BREAKDOWN
----------------------------------------------------------------------------------------------------
ASP.NET Module                 ASPX Files      Django App                     Views      URLs       Status         
----------------------------------------------------------------------------------------------------
SysAdmin                       9               sys_admin                      4          36         🟡 In Progress  
SalesDistribution              82              sales_distribution             10         82         🟡 In Progress  
Design                         74              design                         7          59         🟡 In Progress  
MaterialPlanning               15              material_planning              7          21         🟡 In Progress  
MaterialManagement             120             material_management            10         114        🟡 In Progress  
ProjectManagement              61              project_management             5          27         🟡 In Progress  
Inventory                      149             inventory                      19         112        🟡 In Progress  
QualityControl                 30              quality_control                10         36         🟡 In Progress  
Accounts                       133             accounts                       21         220        🟡 In Progress  
HR                             76              human_resource                 8          133        🟡 In Progress  
MROffice                       3               mr_office                      1          8          🟡 In Progress  
MIS                            41              mis                            4          17         🟡 In Progress  
Machinery                      39              machinery                      5          18         🟡 In Progress  
Report                         31              reports                        1          8          🟡 In Progress  
DailyReportingSystem           27              daily_report_system            7          23         🟡 In Progress  

## DETAILED MENU ITEM ANALYSIS
----------------------------------------------------------------------------------------------------

### Module: Accounts
Django App: accounts
--------------------------------------------------------------------------------
Total Menu Items: 32
  - Home > Accounts
    URL: ~/Module/Accounts/Dashboard.aspx?ModId=11
    File: Dashboard.aspx

  - Home > Accounts > Master
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11
    File: Dashboard.aspx

  - Home > Accounts > Master > Account Heads
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=82
    File: Dashboard.aspx

  - Home > Accounts > Master > CGST/IGST
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=83
    File: Dashboard.aspx

  - Home > Accounts > Master > SGST
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=84
    File: Dashboard.aspx

  - Home > Accounts > Master > Excisable Commodity
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=88
    File: Dashboard.aspx

  - Home > Accounts > Master > Warrenty Terms
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=89
    File: Dashboard.aspx

  - Home > Accounts > Master > Payment Terms
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=90
    File: Dashboard.aspx

  - Home > Accounts > Master > Cash/Bank Entry
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=105
    File: Dashboard.aspx

  - Home > Accounts > Master > IOU Reasons
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=106
    File: Dashboard.aspx

  - Home > Accounts > Master > Bank
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=108
    File: Dashboard.aspx

  - Home > Accounts > Master > Payment Mode
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=125
    File: Dashboard.aspx

  - Home > Accounts > Master > Asset
    URL: ~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=140
    File: Dashboard.aspx

  - Home > Accounts > Transaction
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11
    File: Dashboard.aspx

  - Home > Accounts > Transaction > Sales Invoice
    URL: ~/Module/Accounts/Transactions/SalesInvoice_Dashboard.aspx?ModId=11&SubModId=51
    File: SalesInvoice_Dashboard.aspx

  - Home > Accounts > Transaction > IOU Payment/Receipt
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=112
    File: Dashboard.aspx

  - Home > Accounts > Transaction > Bill Booking
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=62
    File: Dashboard.aspx

  - Home > Accounts > Transaction > Authorize Bill Booking
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=120
    File: Dashboard.aspx

  - Home > Accounts > Transaction >  POLICY 
    URL: ~/Module/Accounts/Transactions/ACC_POLICY.aspx?
    File: ACC_POLICY.aspx

  - Home > Accounts > Transaction > Cash Voucher
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=113
    File: Dashboard.aspx

  - Home > Accounts > Transaction > Payment/Receipt Voucher
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=114
    File: Dashboard.aspx

  - Home > Accounts > Transaction > Advice
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=119
    File: Dashboard.aspx

  - Home > Accounts > Transaction > Creditors/Debitors
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=135
    File: Dashboard.aspx

  - Home > Accounts > Transaction > Bank Reconciliation
    URL: ~/Module/Accounts/Transactions/BankReconciliation_New.aspx?ModId=11&SubModId=
    File: BankReconciliation_New.aspx

  - Home > Accounts > Transaction > Balance Sheet
    URL: ~/Module/Accounts/Transactions/BalanceSheet.aspx?ModId=11&SubModId=138
    File: BalanceSheet.aspx

  - Home > Accounts > Transaction > Asset Register
    URL: ~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=141
    File: Dashboard.aspx

  - Home > Accounts > Report
    URL: ~/Module/Accounts/Reports/Dashboard.aspx?ModId=11
    File: Dashboard.aspx

  - Home > Accounts > Report > Sales Register
    URL: ~/Module/Accounts/Reports/Sales_Register.aspx?ModId=11&SubModId=
    File: Sales_Register.aspx

  - Home > Accounts > Report > Purchase Register
    URL: ~/Module/Accounts/Reports/Purchase_Reprt.aspx?ModId=11&SubModId=
    File: Purchase_Reprt.aspx

  - Home > Accounts > Report > Pending For Invoice
    URL: ~/Module/Accounts/Transactions/PendingForInvoice_Print.aspx?ModId=11&SubModId=
    File: PendingForInvoice_Print.aspx

  - Home > Accounts > Report > PVEV Search
    URL: ~/Module/Accounts/Reports/Search.aspx?ModId=11&SubModId=
    File: Search.aspx

  - Home > Accounts > Report > Cash/Bank Register
    URL: ~/Module/Accounts/Reports/Cash_Bank_Register.aspx?ModId=11&SubModId=
    File: Cash_Bank_Register.aspx


### Module: Chatting
Django App: UNMAPPED
--------------------------------------------------------------------------------
Total Menu Items: 1
  - Home > ChatRoom
    URL: ~/Module/Chatting/Chatroom.aspx?roomId=1
    File: Chatroom.aspx


### Module: Design
Django App: design
--------------------------------------------------------------------------------
Total Menu Items: 12
  - Home > Design
    URL: ~/Module/Design/Dashboard.aspx?ModId=3
    File: Dashboard.aspx

  - Home > Design > Master
    URL: ~/Module/Design/Masters/Dashboard.aspx?ModId=3
    File: Dashboard.aspx

  - Home > Design > Master > BoughtOut Category
    URL: ~/Module/Design/Masters/Dashboard.aspx?ModId=3&SubModId=19
    File: Dashboard.aspx

  - Home > Design > Master > Item Master
    URL: ~/Module/Design/Masters/Dashboard.aspx?ModId=3&SubModId=21
    File: Dashboard.aspx

  - Home > Design > Master > Unit Master
    URL: ~/Module/Design/Masters/Dashboard.aspx?ModId=3&SubModId=76
    File: Dashboard.aspx

  - Home > Design > Master > ECN Reason
    URL: ~/Module/Design/Masters/Dashboard.aspx?ModId=3&SubModId=122
    File: Dashboard.aspx

  - Home > Design > Transaction
    URL: ~/Module/Design/Transactions/Dashboard.aspx?ModId=3
    File: Dashboard.aspx

  - Home > Design > Transaction > BOM
    URL: ~/Module/Design/Transactions/Dashboard_BOM.aspx?ModId=3&SubModId=26
    File: Dashboard_BOM.aspx

  - Home > Design > Transaction > Slido Gunrail
    URL: ~/Module/Design/Transactions/Dashboard_Slido.aspx?ModId=3&SubModId=131
    File: Dashboard_Slido.aspx

  - Home > Design > Transaction > ECN Unlock
    URL: ~/Module/Design/Transactions/Dashboard_BOM.aspx?ModId=3&SubModId=137
    File: Dashboard_BOM.aspx

  - Home > Design > Report
    URL: ~/Module/Design/Reports/Dashboard.aspx?ModId=3
    File: Dashboard.aspx

  - Home > Design > Report > Item history
    URL: ~/Module/Design/Reports/ItemHistory_BOM.aspx?ModId=3&
    File: ItemHistory_BOM.aspx


### Module: HR
Django App: human_resource
--------------------------------------------------------------------------------
Total Menu Items: 25
  - Home > HR
    URL: ~/Module/HR/Dashboard.aspx?ModId=12
    File: Dashboard.aspx

  - Home > HR > Master
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12
    File: Dashboard.aspx

  - Home > HR > Master > Business Group
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=91
    File: Dashboard.aspx

  - Home > HR > Master > Designation
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=92
    File: Dashboard.aspx

  - Home > HR > Master > Department
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=93
    File: Dashboard.aspx

  - Home > HR > Master > Grade
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=94
    File: Dashboard.aspx

  - Home > HR > Master > SwapCard No
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=95
    File: Dashboard.aspx

  - Home > HR > Master > Corporate Mobile
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=96
    File: Dashboard.aspx

  - Home > HR > Master > Intercom Ext
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=97
    File: Dashboard.aspx

  - Home > HR > Master > Gate Pass Types
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=102
    File: Dashboard.aspx

  - Home > HR > Master > Holiday
    URL: ~/Module/HR/Masters/HolidayMaster.aspx
    File: HolidayMaster.aspx

  - Home > HR > Master > PF Slab
    URL: ~/Module/HR/Masters/PF_Slab.aspx
    File: PF_Slab.aspx

  - Home > HR > Master > Working Days
    URL: ~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=134
    File: Dashboard.aspx

  - Home > HR > Transaction
    URL: ~/Module/HR/Transactions/Dashboard.aspx?ModId=12
    File: Dashboard.aspx

  - Home > HR > Transaction > News And  Notices
    URL: ~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=29
    File: Dashboard.aspx

  - Home > HR > Transaction > Offer Letter
    URL: ~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=25
    File: Dashboard.aspx

  - Home > HR > Transaction > Staff
    URL: ~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=24
    File: Dashboard.aspx

  - Home > HR > Transaction > DOCUMENTS
    URL: ~/Module/HR/Transactions/HR_POLICY.aspx?
    File: HR_POLICY.aspx

  - Home > HR > Transaction > Mobile Bill
    URL: ~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=50
    File: Dashboard.aspx

  - Home > HR > Transaction > ASSET LIST
    URL: ~/Module/HR/Transactions/ASSET_LIST.aspx?
    File: ASSET_LIST.aspx

  - Home > HR > Transaction > Authorize Gate Pass
    URL: ~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=103
    File: Dashboard.aspx

  - Home > HR > Transaction > Bank Loan
    URL: ~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=129
    File: Dashboard.aspx

  - Home > HR > Transaction > PayRoll
    URL: ~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=133
    File: Dashboard.aspx

  - Home > HR > Report
    URL: ~/Module/HR/Reports/Dashboard.aspx?ModId=12
    File: Dashboard.aspx

  - Home > HR > Report > Staff
    URL: ~/Module/HR/Reports/MultipleReports.aspx?ModId=12
    File: MultipleReports.aspx


### Module: Inventory
Django App: inventory
--------------------------------------------------------------------------------
Total Menu Items: 24
  - Home > Inventory
    URL: ~/Module/Inventory/Dashboard.aspx?ModId=9
    File: Dashboard.aspx

  - Home > Inventory > Master
    URL: ~/Module/Inventory/Masters/Dashboard.aspx?ModId=9
    File: Dashboard.aspx

  - Home > Inventory > Master > Item location
    URL: ~/Module/Inventory/Masters/Dashboard.aspx?ModId=9&SubModId=18
    File: Dashboard.aspx

  - Home > Inventory > Master > VEHICLE ENTRY
    URL: ~/Module/Inventory/Masters/Vehical_Master.aspx?
    File: Vehical_Master.aspx

  - Home > Inventory > Transaction
    URL: ~/Module/Inventory/Transactions/Dashboard.aspx?ModId=9
    File: Dashboard.aspx

  - Home > Inventory > Transaction > VEHICLE REGISTRATION FORM
    URL: ~/Module/Inventory/Transactions/DashBoard.aspx?ModId=9&SubModId=166
    File: DashBoard.aspx

  - Home > Inventory > Transaction > Goods Inward Note [GIN]
    URL: ~/Module/Inventory/Transactions/Inward_DashBoard.aspx?ModId=9&SubModId=37
    File: Inward_DashBoard.aspx

  - Home > Inventory > Transaction > Goods Received Receipt [GRR]
    URL: ~/Module/Inventory/Transactions/RecievedReciept_Dashboard.aspx?ModId=9&SubModId=38
    File: RecievedReciept_Dashboard.aspx

  - Home > Inventory > Transaction > Goods Service Note [GSN]
    URL: ~/Module/Inventory/Transactions/ServiceNote_Dashboard.aspx?ModId=9&SubModId=39
    File: ServiceNote_Dashboard.aspx

  - Home > Inventory > Transaction > Material Requisition Slip [MRS]
    URL: ~/Module/Inventory/Transactions/MaterialRequisitionSlip_Dashboard.aspx?ModId=9&SubModId=40
    File: MaterialRequisitionSlip_Dashboard.aspx

  - Home > Inventory > Transaction > Material Issue Note [MIN]
    URL: ~/Module/Inventory/Transactions/MaterialIssueNote_Dashboard.aspx?ModId=9&SubModId=41
    File: MaterialIssueNote_Dashboard.aspx

  - Home > Inventory > Transaction > Material Return Note [MRN]
    URL: ~/Module/Inventory/Transactions/MaterialReturnNote_Dashboard.aspx?ModId=9&SubModId=48
    File: MaterialReturnNote_Dashboard.aspx

  - Home > Inventory > Transaction > Delivery Challan
    URL: ~/Module/Inventory/Transactions/Dashboard.aspx?ModId=9&SubModId=147
    File: Dashboard.aspx

  - Home > Inventory > Transaction > Challan Summary
    URL: ~/Module/Inventory/Transactions/ChallanInfo.aspx?ModId=9&SubModId=52
    File: ChallanInfo.aspx

  - Home > Inventory > Transaction > Release WIS
    URL: ~/Module/Inventory/Transactions/Dashboard.aspx?ModId=9&SubModId=81
    File: Dashboard.aspx

  - Home > Inventory > Transaction > Dry / Actual WIS Run
    URL: ~/Module/Inventory/Transactions/Dashboard.aspx?ModId=9&SubModId=53
    File: Dashboard.aspx

  - Home > Inventory > Transaction > Closing Stock
    URL: ~/Module/Inventory/Transactions/ClosingStock.aspx?ModId=&SubModId=
    File: ClosingStock.aspx

  - Home > Inventory > Reports
    URL: ~/Module/Inventory/Reports/Dashboard.aspx?ModId=9
    File: Dashboard.aspx

  - Home > Inventory > Reports > Stock Ledger
    URL: ~/Module/Inventory/Reports/StockLedger.aspx?ModId=9
    File: StockLedger.aspx

  - Home > Inventory > Reports > Stock Statement
    URL: ~/Module/Inventory/Reports/Stock_Statement.aspx?ModId=9
    File: Stock_Statement.aspx

  - Home > Inventory > Reports > Material Issue/Shortage list
    URL: ~/Module/Inventory/Reports/WorkOrder_Issue.aspx?ModId=9
    File: WorkOrder_Issue.aspx

  - Home > Inventory > Reports > Moving-Non Moving Items
    URL: ~/Module/Inventory/Reports/Moving_NonMoving_Items.aspx?ModId=9
    File: Moving_NonMoving_Items.aspx

  - Home > Inventory > Reports > Inward/Outward Register
    URL: ~/Module/Inventory/Reports/InwardOutwardRegister.aspx?ModId=9
    File: InwardOutwardRegister.aspx

  - Home > Inventory > Reports > Search
    URL: ~/Module/Inventory/Reports/Search.aspx?ModId=9
    File: Search.aspx


### Module: MIS
Django App: mis
--------------------------------------------------------------------------------
Total Menu Items: 10
  - Home > MIS
    URL: ~/Module/MIS/Dashboard.aspx?ModId=14
    File: Dashboard.aspx

  - Home > MIS > Transaction
    URL: ~/Module/MIS/Transactions/Dashboard.aspx?ModId=14
    File: Dashboard.aspx

  - Home > MIS > Transaction > Financial Budget
    URL: ~/Module/MIS/Transactions/Menu.aspx?ModId=14&SubModId=
    File: Menu.aspx

  - Home > MIS > Report
    URL: ~/Module/MIS/Reports/Dashboard.aspx?ModId=14
    File: Dashboard.aspx

  - Home > MIS > Report > Sales Distribution
    URL: ~/Module/MIS/Reports/SalesDistribution.aspx?ModId=14&SubModId=
    File: SalesDistribution.aspx

  - Home > MIS > Report > Purchase
    URL: ~/Module/MIS/Reports/CPurchaseReport.aspx?ModId=14&SubModId=
    File: CPurchaseReport.aspx

  - Home > MIS > Report > Sales
    URL: ~/Module/MIS/Reports/CSalesReport.aspx?ModId=14&SubModId=
    File: CSalesReport.aspx

  - Home > MIS > Report > BOM Costing
    URL: ~/Module/MIS/Reports/BOMCosting.aspx?ModId=14&SubModId=
    File: BOMCosting.aspx

  - Home > MIS > Report > Purchase/Sales Computation
    URL: ~/Module/MIS/Reports/Excise_VAT_CST_Compute.aspx?ModId=14&SubModId=
    File: Excise_VAT_CST_Compute.aspx

  - Home > MIS > Report > QA Report
    URL: ~/Module/MIS/Reports/QA_POwise.aspx?ModId=14&Key='xyz'&SubModId=
    File: QA_POwise.aspx


### Module: MROffice
Django App: mr_office
--------------------------------------------------------------------------------
Total Menu Items: 5
  - Home > MR
    URL: ~/Module/MROffice/Dashboard.aspx?ModId=13&SubModId=
    File: Dashboard.aspx

  - Home > MR > Master
    URL: ~/Module/MROffice/Masters/Dashboard.aspx?ModId=13
    File: Dashboard.aspx

  - Home > MR > Transaction
    URL: ~/Module/MROffice/Transactions/Dashboard.aspx?ModId=13
    File: Dashboard.aspx

  - Home > MR > Transaction > Format/Documents
    URL: ~/Module/MROffice/Transactions/Dashboard.aspx?ModId=13&SubModId=130
    File: Dashboard.aspx

  - Home > MR > Report
    URL: ~/Module/MROffice/Reports/Dashboard.aspx?ModId=13
    File: Dashboard.aspx


### Module: MaterialManagement
Django App: material_management
--------------------------------------------------------------------------------
Total Menu Items: 25
  - Home > Material
    URL: ~/Module/MaterialManagement/Dashboard.aspx?ModId=6
    File: Dashboard.aspx

  - Home > Material > Master
    URL: ~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6
    File: Dashboard.aspx

  - Home > Material > Master > Business Nature
    URL: ~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=77
    File: Dashboard.aspx

  - Home > Material > Master > Business Type
    URL: ~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=78
    File: Dashboard.aspx

  - Home > Material > Master > Service Coverage
    URL: ~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=79
    File: Dashboard.aspx

  - Home > Material > Master >  Buyer
    URL: ~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=80
    File: Dashboard.aspx

  - Home > Material > Master > Supplier
    URL: ~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=22
    File: Dashboard.aspx

  - Home > Material > Master > Set Rate
    URL: ~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=139
    File: Dashboard.aspx

  - Home > Material > Transaction
    URL: ~/Module/MaterialManagement/Transactions/Dashboard.aspx?ModId=6
    File: Dashboard.aspx

  - Home > Material > Transaction > Scope Of Supplier
    URL: ~/Module/MaterialManagement/Transactions/Supply_Scope.aspx?ModId=6
    File: Supply_Scope.aspx

  - Home > Material > Transaction > Rate Lock/UnLock
    URL: ~/Module/MaterialManagement/Transactions/Dashboard.aspx?ModId=6&SubModId=61
    File: Dashboard.aspx

  - Home > Material > Transaction > Purchase Requisition [PR]
    URL: ~/Module/MaterialManagement/Transactions/PR_Dashboard.aspx?ModId=6&SubModId=34
    File: PR_Dashboard.aspx

  - Home > Material > Transaction > Special Purpose Requisition [SPR]
    URL: ~/Module/MaterialManagement/Transactions/SPR_Dashboard.aspx?ModId=6&SubModId=31
    File: SPR_Dashboard.aspx

  - Home > Material > Transaction > Check SPR
    URL: ~/Module/MaterialManagement/Transactions/SPR_Check_Dashboard.aspx?ModId=6&SubModId=58
    File: SPR_Check_Dashboard.aspx

  - Home > Material > Transaction > Approve SPR
    URL: ~/Module/MaterialManagement/Transactions/SPR_Approve_Dashboard.aspx?ModId=6&SubModId=59
    File: SPR_Approve_Dashboard.aspx

  - Home > Material > Transaction > Purchase Order [PO]
    URL: ~/Module/MaterialManagement/Transactions/PO_Dashboard.aspx?ModId=6&SubModId=35
    File: PO_Dashboard.aspx

  - Home > Material > Transaction > Check PO
    URL: ~/Module/MaterialManagement/Transactions/PO_Check_Dashboard.aspx?ModId=6&SubModId=55
    File: PO_Check_Dashboard.aspx

  - Home > Material > Transaction > Approve PO
    URL: ~/Module/MaterialManagement/Transactions/PO_Approve_Dashboard.aspx?ModId=6&SubModId=56
    File: PO_Approve_Dashboard.aspx

  - Home > Material > Transaction > Authorize PO
    URL: ~/Module/MaterialManagement/Transactions/PO_Authorize_Dashboard.aspx?ModId=6&SubModId=57
    File: PO_Authorize_Dashboard.aspx

  - Home > Material > Report
    URL: ~/Module/MaterialManagement/Reports/Dashboard.aspx?ModId=6
    File: Dashboard.aspx

  - Home > Material > Report > Rate Register
    URL: ~/Module/MaterialManagement/Reports/RateRegister.aspx?ModId=6&SubModId=
    File: RateRegister.aspx

  - Home > Material > Report > Rate Lock/UnLock
    URL: ~/Module/MaterialManagement/Reports/RateLockUnlock.aspx?ModId=6&SubModId=
    File: RateLockUnlock.aspx

  - Home > Material > Report > Material Forecasting
    URL: ~/Module/MaterialManagement/Reports/MaterialForecasting.aspx?ModId=6&SubModId=
    File: MaterialForecasting.aspx

  - Home > Material > Report > Inward/Outward Regsiter
    URL: ~/Module/MaterialManagement/Reports/InwardOutwardRegister.aspx?ModId=6&SubModId=
    File: InwardOutwardRegister.aspx

  - Home > Material > Report > Search
    URL: ~/Module/MaterialManagement/Reports/Search.aspx?ModId=6&SubModId=
    File: Search.aspx


### Module: MaterialPlanning
Django App: material_planning
--------------------------------------------------------------------------------
Total Menu Items: 5
  - Home > Planning
    URL: ~/Module/MaterialPlanning/Dashboard.aspx?ModId=4
    File: Dashboard.aspx

  - Home > Planning > Master
    URL: ~/Module/MaterialPlanning/Masters/Dashboard.aspx?ModId=4
    File: Dashboard.aspx

  - Home > Planning > Master > Material Process
    URL: ~/Module/MaterialPlanning/Masters/Dashboard.aspx?ModId=4&SubModId=28
    File: Dashboard.aspx

  - Home > Planning > Transaction
    URL: ~/Module/MaterialPlanning/Transactions/Dashboard.aspx?ModId=4
    File: Dashboard.aspx

  - Home > Planning > Transaction > BOM
    URL: ~/Module/MaterialPlanning/Transactions/Dashboard.aspx?ModId=4&SubModId=33
    File: Dashboard.aspx


### Module: ProjectManagement
Django App: project_management
--------------------------------------------------------------------------------
Total Menu Items: 6
  - Home > Project
    URL: ~/Module/ProjectManagement/Dashboard.aspx?ModId=7
    File: Dashboard.aspx

  - Home > Project > Transaction
    URL: ~/Module/ProjectManagement/Transactions/Dashboard.aspx?ModId=7
    File: Dashboard.aspx

  - Home > Project > Transaction > Man Power Planning
    URL: ~/Module/ProjectManagement/Transactions/Dashboard.aspx?ModId=7&SubModId=117
    File: Dashboard.aspx

  - Home > Project > Transaction > Project Planning
    URL: ~/Module/ProjectManagement/Transactions/Dashboard.aspx?ModId=7&SubModId=116
    File: Dashboard.aspx

  - Home > Project > Report
    URL: ~/Module/ProjectManagement/Reports/Dashboard.aspx?ModId=7
    File: Dashboard.aspx

  - Home > Project > Report > Project Summary
    URL: ~/Module/ProjectManagement/Reports/ProjectSummary.aspx?ModId=7
    File: ProjectSummary.aspx


### Module: QualityControl
Django App: quality_control
--------------------------------------------------------------------------------
Total Menu Items: 8
  - Home > QC
    URL: ~/Module/QualityControl/Dashboard.aspx?ModId=10
    File: Dashboard.aspx

  - Home > QC > Transaction
    URL: ~/Module/QualityControl/Transactions/Dashboard.aspx?ModId=10
    File: Dashboard.aspx

  - Home > QC > Transaction > Goods Quality Note [GQN]
    URL: ~/Module/QualityControl/Transactions/QualityNote_Dashboard.aspx?ModId=10&SubModId=46
    File: QualityNote_Dashboard.aspx

  - Home > QC > Transaction > Material Return Quality Note [MRQN]
    URL: ~/Module/QualityControl/Transactions/MaterialReturnNote_Dashboard.aspx?ModId=10&SubModId=49
    File: MaterialReturnNote_Dashboard.aspx

  - Home > QC > Transaction > Authorize MCN
    URL: ~/Module/QualityControl/Transactions/Dashboard.aspx?ModId=10&SubModId=128
    File: Dashboard.aspx

  - Home > QC > Report
    URL: ~/Module/QualityControl/Reports/Dashboard.aspx?ModId=10
    File: Dashboard.aspx

  - Home > QC > Report > Goods Rejection Note [GRN]
    URL: ~/Module/QualityControl/Reports/GoodsRejection_GRN.aspx?ModId=10&SubModId=
    File: GoodsRejection_GRN.aspx

  - Home > QC > Report > Scrap Material
    URL: ~/Module/QualityControl/Reports/ScrapMaterial_Report.aspx?ModId=10&SubModId=
    File: ScrapMaterial_Report.aspx


### Module: Report
Django App: reports
--------------------------------------------------------------------------------
Total Menu Items: 8
  - Home > Reports
    URL: ~/Module/Report/Dashboard.aspx?ModId=18
    File: Dashboard.aspx

  - Home > Reports > Reports
    URL: ~/Module/Report/Reports/Dashboard.aspx?ModId=18
    File: Dashboard.aspx

  - Home > Reports > Reports > Boughtout Design
    URL: ~/Module/Report/Reports/Dashboard.aspx?ModId=18&SubModId=154
    File: Dashboard.aspx

  - Home > Reports > Reports >  Boughtout Vendor 
    URL: ~/Module/Report/Reports/Dashboard.aspx?ModId=18&SubModId=155
    File: Dashboard.aspx

  - Home > Reports > Reports > Boughtout Assemly 
    URL: ~/Module/Report/Reports/Dashboard.aspx?ModId=18&SubModId=156
    File: Dashboard.aspx

  - Home > Reports > Reports > Manufacturing Design
    URL: ~/Module/Report/Reports/Dashboard.aspx?ModId=18&SubModId=158
    File: Dashboard.aspx

  - Home > Reports > Reports > Manufacturing Vendor
    URL: ~/Module/Report/Reports/Manufacturing_Report_Info.aspx?ModId=18&SubModId=159
    File: Manufacturing_Report_Info.aspx

  - Home > Reports > Reports > Manufacturing Assemly
    URL: ~/Module/Report/Reports/Manufacturing_Assemly_New_Report_Info.aspx?ModId=18&SubModId=160
    File: Manufacturing_Assemly_New_Report_Info.aspx


### Module: SalesDistribution
Django App: sales_distribution
--------------------------------------------------------------------------------
Total Menu Items: 14
  - Home > Sales
    URL: ~/Module/SalesDistribution/Dashboard.aspx?ModId=2
    File: Dashboard.aspx

  - Home > Sales > Master
    URL: ~/Module/SalesDistribution/Masters/Dashboard.aspx?ModId=2
    File: Dashboard.aspx

  - Home > Sales > Master > Customer
    URL: ~/Module/SalesDistribution/Masters/Dashboard.aspx?ModId=2&SubModId=7
    File: Dashboard.aspx

  - Home > Sales > Master > Category of Work Order
    URL: ~/Module/SalesDistribution/Masters/WO_Category_Dashboard.aspx?ModId=2 &SubModId=71
    File: WO_Category_Dashboard.aspx

  - Home > Sales > Master > WO Release & Dispatch Authority
    URL: ~/Module/SalesDistribution/Masters/Dashboard.aspx?ModId=2&SubModId=75
    File: Dashboard.aspx

  - Home > Sales > Transaction
    URL: ~/Module/SalesDistribution/Transactions/Dashboard.aspx?ModId=2
    File: Dashboard.aspx

  - Home > Sales > Transaction > Enquiry
    URL: ~/Module/SalesDistribution/Transactions/CustEnquiry_Dashboard.aspx?ModId=2&SubModId=10
    File: CustEnquiry_Dashboard.aspx

  - Home > Sales > Transaction > Quotation
    URL: ~/Module/SalesDistribution/Transactions/Quotation_Dashboard.aspx?ModId=2&SubModId=63
    File: Quotation_Dashboard.aspx

  - Home > Sales > Transaction > Customer PO
    URL: ~/Module/SalesDistribution/Transactions/Dashboard.aspx?ModId=2&SubModId=11
    File: Dashboard.aspx

  - Home > Sales > Transaction > Work Order
    URL: ~/Module/SalesDistribution/Transactions/Dashboard.aspx?ModId=2&SubModId=13
    File: Dashboard.aspx

  - Home > Sales > Transaction > WO Release
    URL: ~/Module/SalesDistribution/Transactions/WORelease_Dashbord.aspx?ModId=2&SubModId=15
    File: WORelease_Dashbord.aspx

  - Home > Sales > Transaction > WO Dispatch
    URL: ~/Module/SalesDistribution/Transactions/WorkOrder_Dispatch_Dashbord.aspx?ModId=2&SubModId=54
    File: WorkOrder_Dispatch_Dashbord.aspx

  - Home > Sales > Transaction >  Dispatch GunRail
    URL: ~/Module/SalesDistribution/Transactions/Dispatch_Gunrail_Dashbord.aspx?ModId=2&SubModId=132
    File: Dispatch_Gunrail_Dashbord.aspx

  - Home > Sales > Transaction >  WO Open/Close
    URL: ~/Module/SalesDistribution/Transactions/Dashboard.aspx?ModId=2&SubModId=73
    File: Dashboard.aspx


### Module: Scheduler
Django App: UNMAPPED
--------------------------------------------------------------------------------
Total Menu Items: 3
  - Home > GatePass
    URL: ~/Module/Scheduler/GatePass_New.aspx
    File: GatePass_New.aspx

  - Home > MyScheduler
    URL: ~/Module/Scheduler/Scheduling.aspx
    File: Scheduling.aspx

  - Home > IOU
    URL: ~/Module/Scheduler/IOU.aspx
    File: IOU.aspx


### Module: SysAdmin
Django App: sys_admin
--------------------------------------------------------------------------------
Total Menu Items: 5
  - Home > Administrator
    URL: ~/Module/SysAdmin/Dashboard.aspx?ModId=1&SubModId=
    File: Dashboard.aspx

  - Home > Administrator > Financial Year
    URL: ~/Module/SysAdmin/FinancialYear/Dashboard.aspx?ModId=1&SubModId=1
    File: Dashboard.aspx

  - Home > Administrator > Country
    URL: ~/Module/SysAdmin/Country.aspx?ModId=1&SubModId=
    File: Country.aspx

  - Home > Administrator > State
    URL: ~/Module/SysAdmin/State.aspx?ModId=1&SubModId=
    File: State.aspx

  - Home > Administrator > City
    URL: ~/Module/SysAdmin/City.aspx?ModId=1&SubModId=
    File: City.aspx


### Module: SysSupport
Django App: UNMAPPED
--------------------------------------------------------------------------------
Total Menu Items: 4
  - Home > Support
    URL: ~/Module/SysSupport/Dashboard.aspx?ModId=17
    File: Dashboard.aspx

  - Home > Support > Change Password
    URL: ~/Module/SysSupport/ChangePassword.aspx
    File: ChangePassword.aspx

  - Home > Support > System Credentials
    URL: ~/Module/SysSupport/DashBord_Credentials.aspx?ModId=17&SubModId=145
    File: DashBord_Credentials.aspx

  - Home > Support > ECN
    URL: ~/Module/SysSupport/ECN_WO_ViewAll.aspx
    File: ECN_WO_ViewAll.aspx


## ASPX FILES NOT IN SITEMAP
----------------------------------------------------------------------------------------------------
(These are supporting pages like _New, _Edit, _Delete, _Print, etc.)


### ASSET (13 files)
  Create: 3 files
  Print: 6 files
  Other: 4 files

### Accounts (119 files)
  Dashboard: 1 files
  Create: 10 files
  Edit: 10 files
  Delete: 13 files
  Print: 26 files
  Other: 59 files

### Appriatiate (3 files)
  Other: 3 files

### Chatting (1 files)
  Other: 1 files

### DailyReportingSystem (26 files)
  Create: 2 files
  Edit: 4 files
  Delete: 4 files
  Other: 16 files

### Design (67 files)
  Create: 4 files
  Edit: 10 files
  Delete: 5 files
  Print: 8 files
  Other: 40 files

### ForgotPassword (1 files)
  Other: 1 files

### HR (67 files)
  Create: 7 files
  Edit: 13 files
  Delete: 8 files
  Print: 14 files
  Other: 25 files

### Inventory (130 files)
  Dashboard: 1 files
  Create: 18 files
  Edit: 19 files
  Delete: 21 files
  Print: 27 files
  Other: 44 files

### MIS (30 files)
  Print: 4 files
  Other: 26 files

### MROffice (1 files)
  Other: 1 files

### Machinery (35 files)
  Dashboard: 5 files
  Create: 10 files
  Edit: 8 files
  Delete: 6 files
  Print: 6 files

### MaterialCosting (4 files)
  Create: 1 files
  Edit: 1 files
  Delete: 1 files
  Other: 1 files

### MaterialManagement (100 files)
  Dashboard: 2 files
  Create: 9 files
  Edit: 12 files
  Delete: 9 files
  Print: 28 files
  Other: 40 files

### MaterialPlanning (11 files)
  Create: 2 files
  Edit: 2 files
  Delete: 2 files
  Print: 2 files
  Other: 3 files

### News_Scrolling_Data.aspx (1 files)
  Other: 1 files

### PopUpNews.aspx (1 files)
  Other: 1 files

### ProjectManagement (56 files)
  Create: 9 files
  Edit: 6 files
  Delete: 4 files
  Print: 14 files
  Other: 23 files

### QualityControl (21 files)
  Create: 4 files
  Edit: 4 files
  Delete: 4 files
  Print: 6 files
  Other: 3 files

### Report (26 files)
  Create: 8 files
  Edit: 3 files
  Print: 11 files
  Other: 4 files

### SalesDistribution (72 files)
  Dashboard: 4 files
  Create: 9 files
  Edit: 10 files
  Delete: 10 files
  Print: 13 files
  Other: 26 files

### Scheduler (2 files)
  Print: 1 files
  Other: 1 files

### SysAdmin (4 files)
  Create: 2 files
  Delete: 1 files
  Other: 1 files

### SysSupport (5 files)
  Print: 1 files
  Other: 4 files

### VISITOR (1 files)
  Print: 1 files
