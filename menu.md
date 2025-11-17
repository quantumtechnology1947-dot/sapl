# ERP System Menu Structure (ASP.NET Legacy System)

## Module ID & SubModule ID Mapping

**ModId** = Main Module Identifier (e.g., 1=Administrator, 2=Sales, 3=Design, etc.)
**SubModId** = Sub-menu/Feature Identifier within a module (unique across system)

The IDs are defined in `Web.sitemap` and used for:
- Access control/permissions
- Navigation tracking
- Breadcrumb generation
- Menu state management

---

## 1. Administrator (ModId=1)
**Dashboard URL**: `~/Module/SysAdmin/Dashboard.aspx?ModId=1&SubModId=`

- **Role Management** (SubModId=empty)
  - URL: `~/Admin/Access/access_rules.aspx?ModId=1&SubModId=`
  
- **Financial Year** (SubModId=1)
  - URL: `~/Module/SysAdmin/FinancialYear/Dashboard.aspx?ModId=1&SubModId=1`
  - Files:
    - `aaspnet/Module/SysAdmin/FinancialYear/Dashboard.aspx`
    - `aaspnet/Module/SysAdmin/FinancialYear/Dashboard.aspx.cs`
    - `aaspnet/Module/SysAdmin/FinancialYear/FinYear_New_Details.aspx`
    - `aaspnet/Module/SysAdmin/FinancialYear/FinYear_New_Details.aspx.cs`
    - `aaspnet/Module/SysAdmin/FinancialYear/FinYrs_Delete.aspx`
    - `aaspnet/Module/SysAdmin/FinancialYear/FinYrs_Delete.aspx.cs`
    - `aaspnet/Module/SysAdmin/FinancialYear/FinYrs_New.aspx`
    - `aaspnet/Module/SysAdmin/FinancialYear/FinYrs_New.aspx.cs`
    - `aaspnet/Module/SysAdmin/FinancialYear/FinYrs_Update.aspx`
    - `aaspnet/Module/SysAdmin/FinancialYear/FinYrs_Update.aspx.cs`
    
- **Country** (SubModId=empty)
  - URL: `~/Module/SysAdmin/Country.aspx?ModId=1&SubModId=`
  - Files:
    - `aaspnet/Module/SysAdmin/Country.aspx`
    - `aaspnet/Module/SysAdmin/Country.aspx.cs`
    
- **State** (SubModId=empty)
  - URL: `~/Module/SysAdmin/State.aspx?ModId=1&SubModId=`
  - Files:
    - `aaspnet/Module/SysAdmin/State.aspx`
    - `aaspnet/Module/SysAdmin/State.aspx.cs`
    
- **City** (SubModId=empty)
  - URL: `~/Module/SysAdmin/City.aspx?ModId=1&SubModId=`
  - Files:
    - `aaspnet/Module/SysAdmin/City.aspx`
    - `aaspnet/Module/SysAdmin/City.aspx.cs`

## 2. Sales (ModId=2)
**Dashboard URL**: `~/Module/SalesDistribution/Dashboard.aspx?ModId=2`

### Master
- **Customer** (SubModId=7)
  - URL: `~/Module/SalesDistribution/Masters/Dashboard.aspx?ModId=2&SubModId=7`
  - Files:
    - `aaspnet/Module/SalesDistribution/Masters/CustomerMaster_New.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CustomerMaster_Edit.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CustomerMaster_Edit_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CustomerMaster_Delete.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CustomerMaster_Delete_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CustomerMaster_Print.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CustomerMaster_Print_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/Customer_Details_Print_All.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/Dashboard.aspx`

- **Category of Work Order** (SubModId=71)
  - URL: `~/Module/SalesDistribution/Masters/WO_Category_Dashboard.aspx?ModId=2&SubModId=71`
  - Files:
    - `aaspnet/Module/SalesDistribution/Masters/WO_Category_Dashboard.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CategoryNew.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CategoryEdit.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/CategoryDelete.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/WOTypes.aspx`

- **WO Release & Dispatch Authority** (SubModId=75)
  - URL: `~/Module/SalesDistribution/Masters/Dashboard.aspx?ModId=2&SubModId=75`
  - Files:
    - `aaspnet/Module/SalesDistribution/Masters/WO_Release_DA.aspx`
    - `aaspnet/Module/SalesDistribution/Masters/Dashboard.aspx`

### Transaction
- **Enquiry** (SubModId=10)
  - URL: `~/Module/SalesDistribution/Transactions/CustEnquiry_Dashboard.aspx?ModId=2&SubModId=10`
  - Files:
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Dashboard.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_New.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Edit.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Edit_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Delete.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Delete_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Print.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Print_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Convert.aspx`

- **Quotation** (SubModId=63)
  - URL: `~/Module/SalesDistribution/Transactions/Quotation_Dashboard.aspx?ModId=2&SubModId=63`
  - Files:
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Dashboard.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_New.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_New_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Edit.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Edit_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Delete.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Delete_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Print.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Print_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Check_Dashboard.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Check.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Approve_Dashboard.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Approve.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Authorize_Dashboard.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Quotation_Authorize.aspx`

- **Customer PO** (SubModId=11)
  - URL: `~/Module/SalesDistribution/Transactions/Dashboard.aspx?ModId=2&SubModId=11`
  - Files:
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_New.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_New_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_Edit.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_Edit_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_Delete.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_Delete_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_Print.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_Print_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/CustPO_PrintFrame.aspx`

- **Work Order** (SubModId=13)
  - URL: `~/Module/SalesDistribution/Transactions/Dashboard.aspx?ModId=2&SubModId=13`
  - Files:
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_New.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_New_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Edit.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Edit_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Delete.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Delete_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Print.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Print_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Print1.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_close.aspx`

- **WO Release** (SubModId=15)
  - URL: `~/Module/SalesDistribution/Transactions/WORelease_Dashbord.aspx?ModId=2&SubModId=15`
  - Files:
    - `aaspnet/Module/SalesDistribution/Transactions/WORelease_Dashbord.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Release.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_ReleaseRPT.aspx`

- **WO Dispatch** (SubModId=54)
  - URL: `~/Module/SalesDistribution/Transactions/WorkOrder_Dispatch_Dashbord.aspx?ModId=2&SubModId=54`
  - Files:
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Dispatch_Dashbord.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Dispatch.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_Dispatch_Details.aspx`

- **Dispatch GunRail** (SubModId=132)
  - URL: `~/Module/SalesDistribution/Transactions/Dispatch_Gunrail_Dashbord.aspx?ModId=2&SubModId=132`
  - Files:
    - `aaspnet/Module/SalesDistribution/Transactions/Dispatch_Gunrail_Dashbord.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Dispatch_Gunrail_Details.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Dispatch_Gunrail_WO_Grid.aspx`

- **WO Open/Close** (SubModId=73)
  - URL: `~/Module/SalesDistribution/Transactions/Dashboard.aspx?ModId=2&SubModId=73`
  - Files:
    - `aaspnet/Module/SalesDistribution/Transactions/WorkOrder_close.aspx`
    - `aaspnet/Module/SalesDistribution/Transactions/Dashboard.aspx`

## 3. Design (ModId=3)
**Dashboard URL**: `~/Module/Design/Dashboard.aspx?ModId=3`

### Master
- **BoughtOut Category** (SubModId=19)
  - URL: `~/Module/Design/Masters/Dashboard.aspx?ModId=3&SubModId=19`
  - Files:
    - `aaspnet/Module/Design/Masters/Category.aspx`
    - `aaspnet/Module/Design/Masters/CategoryDelete.aspx`
    - `aaspnet/Module/Design/Masters/CategoryEdit.aspx`
    - `aaspnet/Module/Design/Masters/CategoryNew.aspx`

- **Item Master** (SubModId=21)
  - URL: `~/Module/Design/Masters/Dashboard.aspx?ModId=3&SubModId=21`
  - Files:
    - `aaspnet/Module/Design/Masters/ItemMaster_Delete.aspx`
    - `aaspnet/Module/Design/Masters/ItemMaster_Edit.aspx`
    - `aaspnet/Module/Design/Masters/ItemMaster_Edit_Details.aspx`
    - `aaspnet/Module/Design/Masters/ItemMaster_New.aspx`
    - `aaspnet/Module/Design/Masters/ItemMaster_Print.aspx`
    - `aaspnet/Module/Design/Masters/ItemMaster_Print_Details.aspx`

- **Unit Master** (SubModId=76)
  - URL: `~/Module/Design/Masters/Dashboard.aspx?ModId=3&SubModId=76`
  - Files:
    - `aaspnet/Module/Design/Masters/Unit_Master.aspx`

- **ECN Reason** (SubModId=122)
  - URL: `~/Module/Design/Masters/ECNReasonTypes.aspx?ModId=3&SubModId=122`
  - Files:
    - `aaspnet/Module/Design/Masters/ECNReasonTypes.aspx`

### Transaction
- **BOM** (SubModId=26)
  - URL: `~/Module/Design/Transactions/Dashboard_BOM.aspx?ModId=3&SubModId=26`
  - Files:
    - `aaspnet/Module/Design/Transactions/BOM_Amd.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_Assembly_Edit.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_Assembly_New.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_CopyWo.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_Copy_Tree.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_Delete.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_Item_Edit.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_PrintWo.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_Print_Cry.aspx`
    - `aaspnet/Module/Design/Transactions/BOM_Design_Print_Tree.aspx`
    - ... and 10 more BOM files

- **Slido Gunrail** (SubModId=131)
  - URL: `~/Module/Design/Transactions/Dashboard_Slido.aspx?ModId=3&SubModId=131`
  - Files:
    - `aaspnet/Module/Design/Transactions/Dashboard_Slido.aspx`
    - `aaspnet/Module/Design/Transactions/Slido_Gunrail_Details.aspx`
    - `aaspnet/Module/Design/Transactions/Slido_Gunrail_WO_Grid.aspx`

- **ECN Unlock** (SubModId=137)
  - URL: `~/Module/Design/Transactions/Dashboard_BOM.aspx?ModId=3&SubModId=137`
  - Files:
    - `aaspnet/Module/Design/Transactions/ECNUnlock.aspx`
    - `aaspnet/Module/Design/Transactions/ECN_Master.aspx`
    - `aaspnet/Module/Design/Transactions/ECN_Master_Edit.aspx`
    - `aaspnet/Module/Design/Transactions/ECN_WO.aspx`

### Report
- **Item history**
  - Files:
    - `aaspnet/Module/Design/Reports/ItemHistory_BOM.aspx`

## 4. Planning (ModId=4)
**Dashboard URL**: `~/Module/MaterialPlanning/Dashboard.aspx?ModId=4`

### Master
- **Material Process** (SubModId=28)
  - URL: `~/Module/MaterialPlanning/Masters/Dashboard.aspx?ModId=4&SubModId=28`
  - Files:
    - `aaspnet/Module/MaterialPlanning/Masters/Dashboard.aspx`
    - `aaspnet/Module/MaterialPlanning/Masters/ItemProcess.aspx`

### Transaction
- **BOM** (SubModId=33)
  - URL: `~/Module/MaterialPlanning/Transactions/Dashboard.aspx?ModId=4&SubModId=33`
  - Files:
    - `aaspnet/Module/MaterialPlanning/Transactions/Dashboard.aspx`
    - `aaspnet/Module/MaterialPlanning/Transactions/Planning_Delete.aspx`
    - `aaspnet/Module/MaterialPlanning/Transactions/Planning_Delete_Plan.aspx`
    - `aaspnet/Module/MaterialPlanning/Transactions/Planning_Edit.aspx`
    - `aaspnet/Module/MaterialPlanning/Transactions/Planning_New.aspx`

## 5. Material (ModId=6)
**Dashboard URL**: `~/Module/MaterialManagement/Dashboard.aspx?ModId=6`

### Master
- **Business Nature** (SubModId=77)
  - URL: `~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=77`
  - Files:
    - `aaspnet/Module/MaterialManagement/Masters/BusinessNature.aspx`

- **Business Type** (SubModId=78)
  - URL: `~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=78`
  - Files:
    - `aaspnet/Module/MaterialManagement/Masters/BusinessType.aspx`

- **Service Coverage** (SubModId=79)
  - URL: `~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=79`
  - Files:
    - `aaspnet/Module/MaterialManagement/Masters/ServiceCoverage.aspx`

- **Buyer** (SubModId=80)
  - URL: `~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=80`
  - Files:
    - `aaspnet/Module/MaterialManagement/Masters/Buyer.aspx`

- **Supplier** (SubModId=22)
  - URL: `~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=22`
  - Files:
    - `aaspnet/Module/MaterialManagement/Masters/SupplierMaster_New.aspx`
    - `aaspnet/Module/MaterialManagement/Masters/SupplierMaster_Edit.aspx`
    - `aaspnet/Module/MaterialManagement/Masters/SupplierMaster_Edit_Details.aspx`
    - `aaspnet/Module/MaterialManagement/Masters/SupplierMaster_Delete.aspx`
    - `aaspnet/Module/MaterialManagement/Masters/SupplierMaster_Delete_Details.aspx`
    - `aaspnet/Module/MaterialManagement/Masters/SupplierMaster_Print.aspx`
    - `aaspnet/Module/MaterialManagement/Masters/SupplierMaster_Print_Details.aspx`

- **Set Rate** (SubModId=139)
  - URL: `~/Module/MaterialManagement/Masters/Dashboard.aspx?ModId=6&SubModId=139`
  - Files:
    - `aaspnet/Module/MaterialManagement/Masters/RateSet.aspx`
    - `aaspnet/Module/MaterialManagement/Masters/RateSet_details.aspx`

### Transaction
- **Scope Of Supplier** (SubModId=empty)
  - URL: `~/Module/MaterialManagement/Transactions/Supply_Scope.aspx?ModId=6&SubModId=`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/Supply_Scope.aspx`

- **Rate Lock/UnLock** (SubModId=61)
  - URL: `~/Module/MaterialManagement/Transactions/Dashboard.aspx?ModId=6&SubModId=61`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/RateLockUnLock.aspx`

- **Purchase Requisition [PR]** (SubModId=34)
  - URL: `~/Module/MaterialManagement/Transactions/PR_Dashboard.aspx?ModId=6&SubModId=34`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/PR_Dashboard.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PR_New.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PR_Edit.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PR_Delete.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PR_Print.aspx`

- **Special Purpose Requisition [SPR]** (SubModId=31)
  - URL: `~/Module/MaterialManagement/Transactions/SPR_Dashboard.aspx?ModId=6&SubModId=31`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_Dashboard.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_New.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_Edit.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_Delete.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_Print.aspx`

- **Check SPR** (SubModId=58)
  - URL: `~/Module/MaterialManagement/Transactions/SPR_Check_Dashboard.aspx?ModId=6&SubModId=58`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_Check_Dashboard.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_Check.aspx`

- **Approve SPR** (SubModId=59)
  - URL: `~/Module/MaterialManagement/Transactions/SPR_Approve_Dashboard.aspx?ModId=6&SubModId=59`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_Approve_Dashboard.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/SPR_Approve.aspx`

- **Purchase Order [PO]** (SubModId=35)
  - URL: `~/Module/MaterialManagement/Transactions/PO_Dashboard.aspx?ModId=6&SubModId=35`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Dashboard.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PO_New.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Edit.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Delete.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Print.aspx`

- **Check PO** (SubModId=55)
  - URL: `~/Module/MaterialManagement/Transactions/PO_Check_Dashboard.aspx?ModId=6&SubModId=55`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Check_Dashboard.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Check.aspx`

- **Approve PO** (SubModId=56)
  - URL: `~/Module/MaterialManagement/Transactions/PO_Approve_Dashboard.aspx?ModId=6&SubModId=56`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Approve_Dashboard.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Approve.aspx`

- **Authorize PO** (SubModId=57)
  - URL: `~/Module/MaterialManagement/Transactions/PO_Authorize_Dashboard.aspx?ModId=6&SubModId=57`
  - Files:
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Authorize_Dashboard.aspx`
    - `aaspnet/Module/MaterialManagement/Transactions/PO_Authorize.aspx`

### Report
- **Rate Register** (SubModId=empty)
  - URL: `~/Module/MaterialManagement/Reports/RateRegister.aspx?ModId=6&SubModId=`
  - Files:
    - `aaspnet/Module/MaterialManagement/Reports/RateRegister.aspx`
    - `aaspnet/Module/MaterialManagement/Reports/RateRegister_Details.aspx`

- **Rate Lock/UnLock** (SubModId=empty)
  - URL: `~/Module/MaterialManagement/Reports/RateLockUnlock.aspx?ModId=6&SubModId=`
  - Files:
    - `aaspnet/Module/MaterialManagement/Reports/RateLockUnlock.aspx`
    - `aaspnet/Module/MaterialManagement/Reports/RateLockUnlock_Details.aspx`

- **Material Forecasting** (SubModId=empty)
  - URL: `~/Module/MaterialManagement/Reports/MaterialForecasting.aspx?ModId=6&SubModId=`
  - Files:
    - `aaspnet/Module/MaterialManagement/Reports/MaterialForecasting.aspx`

- **Inward/Outward Register** (SubModId=empty)
  - URL: `~/Module/MaterialManagement/Reports/InwardOutwardRegister.aspx?ModId=6&SubModId=`
  - Files:
    - `aaspnet/Module/MaterialManagement/Reports/InwardOutwardRegister.aspx`

- **Search** (SubModId=empty)
  - URL: `~/Module/MaterialManagement/Reports/Search.aspx?ModId=6&SubModId=`
  - Files:
    - `aaspnet/Module/MaterialManagement/Reports/Search.aspx`
    - `aaspnet/Module/MaterialManagement/Reports/SearchViewField.aspx`

## 6. Project (ModId=7)
**Dashboard URL**: `~/Module/ProjectManagement/Dashboard.aspx?ModId=7`

### Transaction
- **Man Power Planning** (SubModId=117)
  - URL: `~/Module/ProjectManagement/Transactions/Dashboard.aspx?ModId=7&SubModId=117`
  - Files:
    - `aaspnet/Module/ProjectManagement/Transactions/ManPowerPlanning.aspx`
    - `aaspnet/Module/ProjectManagement/Transactions/ManPowerPlanning_Details.aspx`

- **Project Planning** (SubModId=116)
  - URL: `~/Module/ProjectManagement/Transactions/Dashboard.aspx?ModId=7&SubModId=116`
  - Files:
    - `aaspnet/Module/ProjectManagement/Transactions/ProjectPlanning.aspx`
    - `aaspnet/Module/ProjectManagement/Transactions/ProjectPlanning_Details.aspx`
    - `aaspnet/Module/ProjectManagement/Transactions/ProjectPlanning_Edit.aspx`
    - `aaspnet/Module/ProjectManagement/Transactions/ProjectPlanning_New.aspx`

### Report
- **Project Summary**
  - URL: `~/Module/ProjectManagement/Reports/ProjectSummary.aspx?ModId=7`
  - Files:
    - `aaspnet/Module/ProjectManagement/Reports/ProjectSummary.aspx`
    - `aaspnet/Module/ProjectManagement/Reports/ProjectSummary_Details.aspx`
    - `aaspnet/Module/ProjectManagement/Reports/ProjectSummary_Details_Bought.aspx`
    - `aaspnet/Module/ProjectManagement/Reports/ProjectSummary_Details_Grid.aspx`
    - `aaspnet/Module/ProjectManagement/Reports/ProjectSummary_Details_Hard.aspx`

## 7. Reports
### Reports
- Boughtout Design
- Boughtout Vendor
- Boughtout Assembly
- Manufacturing Design
- Manufacturing Vendor
- Manufacturing Assembly

## 8. Inventory (ModId=9)
**Dashboard URL**: `~/Module/Inventory/Dashboard.aspx?ModId=9`

### Master
- **Item location** (SubModId=18)
  - URL: `~/Module/Inventory/Masters/Dashboard.aspx?ModId=9&SubModId=18`
  - Files:
    - `aaspnet/Module/Inventory/Masters/ItemLocation_New.aspx`
    - `aaspnet/Module/Inventory/Masters/ItemLocation_Edit.aspx`
    - `aaspnet/Module/Inventory/Masters/ItemLocation_Delete.aspx`

- **VEHICLE ENTRY** (SubModId=empty)
  - URL: `~/Module/Inventory/Masters/Vehical_Master.aspx?ModId=9&SubModId=`
  - Files:
    - `aaspnet/Module/Inventory/Masters/Vehical_Master.aspx`

### Transaction
- **VEHICLE REGISTRATION FORM** (SubModId=166)
  - URL: `~/Module/Inventory/Transactions/DashBoard.aspx?ModId=9&SubModId=166`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/Vehical_Registration_Form.aspx`

- **Goods Inward Note [GIN]** (SubModId=37)
  - URL: `~/Module/Inventory/Transactions/Inward_DashBoard.aspx?ModId=9&SubModId=37`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/Inward_DashBoard.aspx`
    - `aaspnet/Module/Inventory/Transactions/Inward_New.aspx`
    - `aaspnet/Module/Inventory/Transactions/Inward_Edit.aspx`
    - `aaspnet/Module/Inventory/Transactions/Inward_Delete.aspx`
    - `aaspnet/Module/Inventory/Transactions/Inward_Print.aspx`

- **Goods Received Receipt [GRR]** (SubModId=38)
  - URL: `~/Module/Inventory/Transactions/RecievedReciept_Dashboard.aspx?ModId=9&SubModId=38`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/RecievedReciept_Dashboard.aspx`
    - `aaspnet/Module/Inventory/Transactions/RecievedReciept_New.aspx`
    - `aaspnet/Module/Inventory/Transactions/RecievedReciept_Edit.aspx`
    - `aaspnet/Module/Inventory/Transactions/RecievedReciept_Delete.aspx`
    - `aaspnet/Module/Inventory/Transactions/RecievedReciept_Print.aspx`

- **Goods Service Note [GSN]** (SubModId=39)
  - URL: `~/Module/Inventory/Transactions/ServiceNote_Dashboard.aspx?ModId=9&SubModId=39`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/ServiceNote_Dashboard.aspx`
    - `aaspnet/Module/Inventory/Transactions/ServiceNote_New.aspx`
    - `aaspnet/Module/Inventory/Transactions/ServiceNote_Edit.aspx`
    - `aaspnet/Module/Inventory/Transactions/ServiceNote_Delete.aspx`

- **Material Requisition Slip [MRS]** (SubModId=40)
  - URL: `~/Module/Inventory/Transactions/MaterialRequisitionSlip_Dashboard.aspx?ModId=9&SubModId=40`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/MaterialRequisitionSlip_Dashboard.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialRequisitionSlip_New.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialRequisitionSlip_Edit.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialRequisitionSlip_Delete.aspx`

- **Material Issue Note [MIN]** (SubModId=41)
  - URL: `~/Module/Inventory/Transactions/MaterialIssueNote_Dashboard.aspx?ModId=9&SubModId=41`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/MaterialIssueNote_Dashboard.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialIssueNote_New.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialIssueNote_Edit.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialIssueNote_Delete.aspx`

- **Material Return Note [MRN]** (SubModId=48)
  - URL: `~/Module/Inventory/Transactions/MaterialReturnNote_Dashboard.aspx?ModId=9&SubModId=48`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/MaterialReturnNote_Dashboard.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialReturnNote_New.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialReturnNote_Edit.aspx`
    - `aaspnet/Module/Inventory/Transactions/MaterialReturnNote_Delete.aspx`

- **Delivery Challan** (SubModId=147)
  - URL: `~/Module/Inventory/Transactions/Dashboard.aspx?ModId=9&SubModId=147`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/Challan_New.aspx`
    - `aaspnet/Module/Inventory/Transactions/Challan_Edit.aspx`
    - `aaspnet/Module/Inventory/Transactions/Challan_Delete.aspx`

- **Challan Summary** (SubModId=52)
  - URL: `~/Module/Inventory/Transactions/ChallanInfo.aspx?ModId=9&SubModId=52`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/ChallanInfo.aspx`

- **Release WIS** (SubModId=81)
  - URL: `~/Module/Inventory/Transactions/Dashboard.aspx?ModId=9&SubModId=81`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/WIS_Release.aspx`

- **Dry / Actual WIS Run** (SubModId=53)
  - URL: `~/Module/Inventory/Transactions/Dashboard.aspx?ModId=9&SubModId=53`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/WIS_Dry_Run.aspx`
    - `aaspnet/Module/Inventory/Transactions/WIS_Actual_Run.aspx`

- **Closing Stock** (SubModId=empty)
  - URL: `~/Module/Inventory/Transactions/ClosingStock.aspx?ModId=9&SubModId=`
  - Files:
    - `aaspnet/Module/Inventory/Transactions/ClosingStock.aspx`

### Reports
- **Stock Ledger**
  - URL: `~/Module/Inventory/Reports/StockLedger.aspx?ModId=9`
  - Files:
    - `aaspnet/Module/Inventory/Reports/StockLedger.aspx`

- **Stock Statement**
  - URL: `~/Module/Inventory/Reports/Stock_Statement.aspx?ModId=9`
  - Files:
    - `aaspnet/Module/Inventory/Reports/Stock_Statement.aspx`

- **Material Issue/Shortage list**
  - URL: `~/Module/Inventory/Reports/WorkOrder_Issue.aspx?ModId=9`
  - Files:
    - `aaspnet/Module/Inventory/Reports/WorkOrder_Issue.aspx`

- **Moving-Non Moving Items**
  - URL: `~/Module/Inventory/Reports/Moving_NonMoving_Items.aspx?ModId=9`
  - Files:
    - `aaspnet/Module/Inventory/Reports/Moving_NonMoving_Items.aspx`

- **Inward/Outward Register**
  - URL: `~/Module/Inventory/Reports/InwardOutwardRegister.aspx?ModId=9`
  - Files:
    - `aaspnet/Module/Inventory/Reports/InwardOutwardRegister.aspx`

- **Search**
  - URL: `~/Module/Inventory/Reports/Search.aspx?ModId=9`
  - Files:
    - `aaspnet/Module/Inventory/Reports/Search.aspx`

## 9. QC (ModId=10)
**Dashboard URL**: `~/Module/QualityControl/Dashboard.aspx?ModId=10`

### Transaction
- **Goods Quality Note [GQN]** (SubModId=46)
  - URL: `~/Module/QualityControl/Transactions/QualityNote_Dashboard.aspx?ModId=10&SubModId=46`
  - Files:
    - `aaspnet/Module/QualityControl/Transactions/QualityNote_Dashboard.aspx`
    - `aaspnet/Module/QualityControl/Transactions/QualityNote_New.aspx`
    - `aaspnet/Module/QualityControl/Transactions/QualityNote_Edit.aspx`
    - `aaspnet/Module/QualityControl/Transactions/QualityNote_Delete.aspx`
    - `aaspnet/Module/QualityControl/Transactions/QualityNote_Print.aspx`

- **Material Return Quality Note [MRQN]** (SubModId=49)
  - URL: `~/Module/QualityControl/Transactions/MaterialReturnNote_Dashboard.aspx?ModId=10&SubModId=49`
  - Files:
    - `aaspnet/Module/QualityControl/Transactions/MaterialReturnNote_Dashboard.aspx`
    - `aaspnet/Module/QualityControl/Transactions/MaterialReturnNote_New.aspx`
    - `aaspnet/Module/QualityControl/Transactions/MaterialReturnNote_Edit.aspx`
    - `aaspnet/Module/QualityControl/Transactions/MaterialReturnNote_Delete.aspx`

- **Authorize MCN** (SubModId=128)
  - URL: `~/Module/QualityControl/Transactions/Dashboard.aspx?ModId=10&SubModId=128`
  - Files:
    - `aaspnet/Module/QualityControl/Transactions/AuthorizedMCN.aspx`
    - `aaspnet/Module/QualityControl/Transactions/AuthorizedMCN_Details.aspx`

### Report
- **Goods Rejection Note [GRN]**
  - URL: `~/Module/QualityControl/Reports/GoodsRejection_GRN.aspx?ModId=10&SubModId=`
  - Files:
    - `aaspnet/Module/QualityControl/Reports/GoodsRejection_GRN.aspx`
    - `aaspnet/Module/QualityControl/Reports/GoodsRejection_GRN_Print_Details.aspx`

- **Scrap Material**
  - URL: `~/Module/QualityControl/Reports/ScrapMaterial_Report.aspx?ModId=10&SubModId=`
  - Files:
    - `aaspnet/Module/QualityControl/Reports/ScrapMaterial_Report.aspx`
    - `aaspnet/Module/QualityControl/Reports/ScrapMaterial_Report_Details.aspx`

## 10. Accounts (ModId=11)
**Dashboard URL**: `~/Module/Accounts/Dashboard.aspx?ModId=11`

### Master
- **Account Heads** (SubModId=82)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=82`
  - Files:
    - `aaspnet/Module/Accounts/Masters/AccHead.aspx`

- **CGST/IGST** (SubModId=83)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=83`
  - Files:
    - `aaspnet/Module/Accounts/Masters/ExcisableCommodity.aspx`

- **SGST** (SubModId=84)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=84`
  - Files:
    - `aaspnet/Module/Accounts/Masters/VAT.aspx`

- **Excisable Commodity** (SubModId=88)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=88`
  - Files:
    - `aaspnet/Module/Accounts/Masters/ExcisableCommodity.aspx`

- **Warrenty Terms** (SubModId=89)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=89`
  - Files:
    - `aaspnet/Module/Accounts/Masters/WarrentyTerms.aspx`

- **Payment Terms** (SubModId=90)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=90`
  - Files:
    - `aaspnet/Module/Accounts/Masters/PaymentTerms.aspx`

- **Cash/Bank Entry** (SubModId=105)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=105`
  - Files:
    - `aaspnet/Module/Accounts/Masters/Cash_Bank_Entry.aspx`

- **IOU Reasons** (SubModId=106)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=106`
  - Files:
    - `aaspnet/Module/Accounts/Masters/IOU_Reasons.aspx`

- **Bank** (SubModId=108)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=108`
  - Files:
    - `aaspnet/Module/Accounts/Masters/Bank.aspx`

- **Payment Mode** (SubModId=125)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=125`
  - Files:
    - `aaspnet/Module/Accounts/Masters/PaymentMode.aspx`

- **Asset** (SubModId=140)
  - URL: `~/Module/Accounts/Masters/Dashboard.aspx?ModId=11&SubModId=140`
  - Files:
    - `aaspnet/Module/Accounts/Masters/Asset.aspx`

### Transaction
- **Sales Invoice** (SubModId=51)
  - URL: `~/Module/Accounts/Transactions/SalesInvoice_Dashboard.aspx?ModId=11&SubModId=51`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/SalesInvoice_Dashboard.aspx`
    - `aaspnet/Module/Accounts/Transactions/SalesInvoice_New.aspx`
    - `aaspnet/Module/Accounts/Transactions/SalesInvoice_Edit.aspx`
    - `aaspnet/Module/Accounts/Transactions/SalesInvoice_Delete.aspx`
    - `aaspnet/Module/Accounts/Transactions/SalesInvoice_Print.aspx`

- **IOU Payment/Receipt** (SubModId=112)
  - URL: `~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=112`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/IOU_Payment_Receipt.aspx`

- **Bill Booking** (SubModId=62)
  - URL: `~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=62`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/BillBooking_Dashboard.aspx`
    - `aaspnet/Module/Accounts/Transactions/BillBooking_New.aspx`
    - `aaspnet/Module/Accounts/Transactions/BillBooking_Edit.aspx`
    - `aaspnet/Module/Accounts/Transactions/BillBooking_Delete.aspx`

- **Authorize Bill Booking** (SubModId=120)
  - URL: `~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=120`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/BillBooking_Authorize.aspx`

- **Cash Voucher** (SubModId=113)
  - URL: `~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=113`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/CashVoucher.aspx`

- **Payment/Receipt Voucher** (SubModId=114)
  - URL: `~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=114`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/PaymentVoucher.aspx`
    - `aaspnet/Module/Accounts/Transactions/ReceiptVoucher.aspx`

- **Advice** (SubModId=119)
  - URL: `~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=119`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/Advice.aspx` (Main UI - 431 lines)
    - `aaspnet/Module/Accounts/Transactions/Advice.aspx.cs` (Business Logic - 1778 lines)
    - `aaspnet/Module/Accounts/Transactions/Advice_Delete.aspx` (Delete functionality)
    - `aaspnet/Module/Accounts/Transactions/Advice_Print.aspx` (Print list)
    - `aaspnet/Module/Accounts/Transactions/Advice_Print_Details.aspx` (Print details with Crystal Reports)
    - `aaspnet/Module/Accounts/Reports/Advice_Print.rpt` (Crystal Report template)
    - `aaspnet/Module/Accounts/Reports/BankVoucher_Payment_Advice.rpt` (Bank voucher report)
  - Database Tables:
    - `tblACC_Advice_Payment_Master` (Header table)
    - `tblACC_Advice_Payment_Details` (Line items)
    - `tblACC_Advice_Payment_Temp` (Session-based temporary storage)
    - `tblACC_Advice_Payment_Creditor_Temp` (Creditors payment temp storage)

- **Creditors/Debitors** (SubModId=135)
  - URL: `~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=135`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/Creditors_Debitors.aspx`

- **Bank Reconciliation** (SubModId=empty)
  - URL: `~/Module/Accounts/Transactions/BankReconciliation_New.aspx?ModId=11&SubModId=`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/BankReconciliation_New.aspx`

- **Balance Sheet** (SubModId=138)
  - URL: `~/Module/Accounts/Transactions/BalanceSheet.aspx?ModId=11&SubModId=138`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/BalanceSheet.aspx`

- **Asset Register** (SubModId=141)
  - URL: `~/Module/Accounts/Transactions/Dashboard.aspx?ModId=11&SubModId=141`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/AssetRegister.aspx`

### Report
- **Sales Register**
  - URL: `~/Module/Accounts/Reports/Sales_Register.aspx?ModId=11&SubModId=`
  - Files:
    - `aaspnet/Module/Accounts/Reports/Sales_Register.aspx`

- **Purchase Register**
  - URL: `~/Module/Accounts/Reports/Purchase_Reprt.aspx?ModId=11&SubModId=`
  - Files:
    - `aaspnet/Module/Accounts/Reports/Purchase_Reprt.aspx`

- **Pending For Invoice**
  - URL: `~/Module/Accounts/Transactions/PendingForInvoice_Print.aspx?ModId=11&SubModId=`
  - Files:
    - `aaspnet/Module/Accounts/Transactions/PendingForInvoice_Print.aspx`

- **PVEV Search**
  - URL: `~/Module/Accounts/Reports/Search.aspx?ModId=11&SubModId=`
  - Files:
    - `aaspnet/Module/Accounts/Reports/Search.aspx`

- **Cash/Bank Register**
  - URL: `~/Module/Accounts/Reports/Cash_Bank_Register.aspx?ModId=11&SubModId=`
  - Files:
    - `aaspnet/Module/Accounts/Reports/Cash_Bank_Register.aspx`

## 11. HR (ModId=12)
**Dashboard URL**: `~/Module/HR/Dashboard.aspx?ModId=12`

### Master
- **Business Group** (SubModId=91)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=91`
  - Files:
    - `aaspnet/Module/HR/Masters/BusinessGroup.aspx`

- **Designation** (SubModId=92)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=92`
  - Files:
    - `aaspnet/Module/HR/Masters/Designation.aspx`

- **Department** (SubModId=93)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=93`
  - Files:
    - `aaspnet/Module/HR/Masters/Department.aspx`

- **Grade** (SubModId=94)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=94`
  - Files:
    - `aaspnet/Module/HR/Masters/Grade.aspx`

- **SwapCard No** (SubModId=95)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=95`
  - Files:
    - `aaspnet/Module/HR/Masters/SwapCardNo.aspx`

- **Corporate Mobile** (SubModId=96)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=96`
  - Files:
    - `aaspnet/Module/HR/Masters/CorporateMobileNo.aspx`

- **Intercom Ext** (SubModId=97)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=97`
  - Files:
    - `aaspnet/Module/HR/Masters/IntercomExtNo.aspx`

- **Gate Pass Types** (SubModId=102)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=102`
  - Files:
    - `aaspnet/Module/HR/Masters/GatePassReason.aspx`

- **Holiday** (SubModId=empty)
  - URL: `~/Module/HR/Masters/HolidayMaster.aspx?ModId=12&SubModId=`
  - Files:
    - `aaspnet/Module/HR/Masters/HolidayMaster.aspx`

- **PF Slab** (SubModId=empty)
  - URL: `~/Module/HR/Masters/PF_Slab.aspx?ModId=12&SubModId=`
  - Files:
    - `aaspnet/Module/HR/Masters/PF_Slab.aspx`

- **Working Days** (SubModId=134)
  - URL: `~/Module/HR/Masters/Dashboard.aspx?ModId=12&SubModId=134`
  - Files:
    - `aaspnet/Module/HR/Masters/WorkingDays.aspx`

### Transaction
- **News And Notices** (SubModId=29)
  - URL: `~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=29`
  - Files:
    - `aaspnet/Module/HR/Transactions/NewsAndNotices.aspx`

- **Offer Letter** (SubModId=25)
  - URL: `~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=25`
  - Files:
    - `aaspnet/Module/HR/Transactions/OfferLetter.aspx`

- **Staff** (SubModId=24)
  - URL: `~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=24`
  - Files:
    - `aaspnet/Module/HR/Transactions/Staff_New.aspx`
    - `aaspnet/Module/HR/Transactions/Staff_Edit.aspx`
    - `aaspnet/Module/HR/Transactions/Staff_Delete.aspx`
    - `aaspnet/Module/HR/Transactions/Staff_Print.aspx`

- **Mobile Bill** (SubModId=50)
  - URL: `~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=50`
  - Files:
    - `aaspnet/Module/HR/Transactions/MobileBill.aspx`

- **Authorize Gate Pass** (SubModId=103)
  - URL: `~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=103`
  - Files:
    - `aaspnet/Module/HR/Transactions/AuthorizeGatePass.aspx`

- **Bank Loan** (SubModId=129)
  - URL: `~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=129`
  - Files:
    - `aaspnet/Module/HR/Transactions/BankLoan.aspx`

- **PayRoll** (SubModId=133)
  - URL: `~/Module/HR/Transactions/Dashboard.aspx?ModId=12&SubModId=133`
  - Files:
    - `aaspnet/Module/HR/Transactions/PayRoll.aspx`

### Report
- **Staff**
  - URL: `~/Module/HR/Reports/MultipleReports.aspx?ModId=12`
  - Files:
    - `aaspnet/Module/HR/Reports/MultipleReports.aspx`

## 12. MR (ModId=13)
**Dashboard URL**: `~/Module/MROffice/Dashboard.aspx?ModId=13&SubModId=`

### Transaction
- **Format/Documents** (SubModId=130)
  - URL: `~/Module/MROffice/Transactions/Dashboard.aspx?ModId=13&SubModId=130`
  - Files:
    - `aaspnet/Module/MROffice/Transactions/MROffice.aspx`
    - `aaspnet/Module/MROffice/Transactions/Dashboard.aspx`

## 13. MIS (ModId=14)
**Dashboard URL**: `~/Module/MIS/Dashboard.aspx?ModId=14`

### Transaction
- **Financial Budget**
  - URL: `~/Module/MIS/Transactions/Menu.aspx?ModId=14&SubModId=`
  - Files:
    - `aaspnet/Module/MIS/Transactions/Menu.aspx`
    - `aaspnet/Module/MIS/Transactions/Budget_New.aspx`
    - `aaspnet/Module/MIS/Transactions/Budget_Edit.aspx`

### Report
- **Sales Distribution**
  - URL: `~/Module/MIS/Reports/SalesDistribution.aspx?ModId=14&SubModId=`
  - Files:
    - `aaspnet/Module/MIS/Reports/SalesDistribution.aspx`

- **Purchase**
  - URL: `~/Module/MIS/Reports/CPurchaseReport.aspx?ModId=14&SubModId=`
  - Files:
    - `aaspnet/Module/MIS/Reports/CPurchaseReport.aspx`

- **Sales**
  - URL: `~/Module/MIS/Reports/CSalesReport.aspx?ModId=14&SubModId=`
  - Files:
    - `aaspnet/Module/MIS/Reports/CSalesReport.aspx`

- **BOM Costing**
  - URL: `~/Module/MIS/Reports/BOMCosting.aspx?ModId=14&SubModId=`
  - Files:
    - `aaspnet/Module/MIS/Reports/BOMCosting.aspx`
    - `aaspnet/Module/MIS/Reports/BOMCosting_Report.aspx`

- **Purchase/Sales Computation**
  - URL: `~/Module/MIS/Reports/Excise_VAT_CST_Compute.aspx?ModId=14&SubModId=`
  - Files:
    - `aaspnet/Module/MIS/Reports/Excise_VAT_CST_Compute.aspx`

- **QA Report**
  - URL: `~/Module/MIS/Reports/QA_POwise.aspx?ModId=14&Key='xyz'&SubModId=`
  - Files:
    - `aaspnet/Module/MIS/Reports/QA_POwise.aspx`

## 14. Support (ModId=17)
**Dashboard URL**: `~/Module/SysSupport/Dashboard.aspx?ModId=17`

- **Change Password**
  - URL: `~/Module/SysSupport/ChangePassword.aspx`
  - Files:
    - `aaspnet/Module/SysSupport/ChangePassword.aspx`

- **System Credentials** (SubModId=145)
  - URL: `~/Module/SysSupport/DashBord_Credentials.aspx?ModId=17&SubModId=145`
  - Files:
    - `aaspnet/Module/SysSupport/DashBord_Credentials.aspx`
    - `aaspnet/Module/SysSupport/SystemCredentials.aspx`
    - `aaspnet/Module/SysSupport/SystemCredentialsPrint.aspx`

- **ECN**
  - URL: `~/Module/SysSupport/ECN_WO_ViewAll.aspx`
  - Files:
    - `aaspnet/Module/SysSupport/ECN_ViewAll.aspx`
    - `aaspnet/Module/SysSupport/ECN_WO_ViewAll.aspx`

## 15. Reports (ModId=18)
**Dashboard URL**: `~/Module/Report/Dashboard.aspx?ModId=18`

### Reports
- **Boughtout Design** (SubModId=154)
  - URL: `~/Module/Report/Reports/Dashboard.aspx?ModId=18&SubModId=154`
  - Files:
    - `aaspnet/Module/Report/Reports/Boughtout_Report_Info_Edit.aspx`
    - `aaspnet/Module/Report/Reports/Boughtout_Report_Info_Print.aspx`
    - `aaspnet/Module/Report/Reports/Boughtout_Report_Print_Detail.aspx`

- **Boughtout Vendor** (SubModId=155)
  - URL: `~/Module/Report/Reports/Dashboard.aspx?ModId=18&SubModId=155`
  - Files:
    - `aaspnet/Module/Report/Reports/Vendor_Report_Info.aspx`
    - `aaspnet/Module/Report/Reports/Vendor_Report_Info_Print.aspx`

- **Boughtout Assembly** (SubModId=156)
  - URL: `~/Module/Report/Reports/Dashboard.aspx?ModId=18&SubModId=156`
  - Files:
    - `aaspnet/Module/Report/Reports/Assemly_New_Details.aspx`
    - `aaspnet/Module/Report/Reports/Assemly_Report_Info_Print.aspx`
    - `aaspnet/Module/Report/Reports/Assemly_Report_Print_Detail.aspx`

- **Manufacturing Design** (SubModId=158)
  - URL: `~/Module/Report/Reports/Dashboard.aspx?ModId=18&SubModId=158`
  - Files:
    - `aaspnet/Module/Report/Reports/Manufacturing_Report_Info.aspx`
    - `aaspnet/Module/Report/Reports/Manufacturing_Report_Info_Print.aspx`

- **Manufacturing Vendor** (SubModId=159)
  - URL: `~/Module/Report/Reports/Manufacturing_Report_Info.aspx?ModId=18&SubModId=159`
  - Files:
    - `aaspnet/Module/Report/Reports/Manufacturing_Vendor_Report_Info.aspx`

- **Manufacturing Assembly** (SubModId=160)
  - URL: `~/Module/Report/Reports/Manufacturing_Assemly_New_Report_Info.aspx?ModId=18&SubModId=160`
  - Files:
    - `aaspnet/Module/Report/Reports/Manufacturing_Assemly_New_Report_Info.aspx`
    - `aaspnet/Module/Report/Reports/Manufacturing_Assemly_Report_Info_Print.aspx`

## 16. Standalone Features
- **GatePass**
  - URL: `~/Module/Scheduler/GatePass_New.aspx`
  - Files:
    - `aaspnet/Module/Scheduler/GatePass_New.aspx`

- **MyScheduler**
  - URL: `~/Module/Scheduler/Scheduling.aspx`
  - Files:
    - `aaspnet/Module/Scheduler/Scheduling.aspx`

- **IOU**
  - URL: `~/Module/Scheduler/IOU.aspx`
  - Files:
    - `aaspnet/Module/Scheduler/IOU.aspx`

- **ChatRoom**
  - URL: `~/Module/Chatting/Chatroom.aspx?roomId=1`
  - Files:
    - `aaspnet/Module/Chatting/Chatroom.aspx`

- **ModuleList**
  - URL: `~/Others/ERP Module List.rar`
  - Files:
    - `aaspnet/Others/ERP Module List.rar`
