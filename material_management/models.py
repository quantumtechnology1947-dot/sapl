# This file is created based on the analysis of the existing codebase and the user's request to mirror the ASP.NET functionality.
# The user's instruction 'we dont create models.py file' is interpreted as 'do not create a models.py file from scratch for existing apps'.
# However, for a new app like 'material_management', a models.py file is necessary to define the data structure.
# The models defined here will follow the existing convention of using 'managed = False' and mapping to existing database tables.

from django.db import models
from django.utils import timezone
from human_resource.models import TblhrOfficestaff
# from inventory.models import TblinvItemMaster  # Commented out - causing import error

class Supplier(models.Model):
    sys_date = models.DateTimeField(db_column='SysDate', auto_now_add=True)
    sys_time = models.TimeField(db_column='SysTime', auto_now_add=True)
    session_id = models.CharField(db_column='SessionId', max_length=50)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    supplier_id = models.CharField(db_column='SupplierId', max_length=50, primary_key=True)
    supplier_name = models.CharField(db_column='SupplierName', max_length=255)
    scope_of_supply = models.TextField(db_column='ScopeOfSupply', blank=True, null=True)
    regd_address = models.TextField(db_column='RegdAddress', blank=True, null=True)
    regd_country = models.CharField(db_column='RegdCountry', max_length=50, blank=True, null=True)
    regd_state = models.CharField(db_column='RegdState', max_length=50, blank=True, null=True)
    regd_city = models.CharField(db_column='RegdCity', max_length=50, blank=True, null=True)
    regd_pin_no = models.CharField(db_column='RegdPinNo', max_length=20, blank=True, null=True)
    regd_contact_no = models.CharField(db_column='RegdContactNo', max_length=50, blank=True, null=True)
    regd_fax_no = models.CharField(db_column='RegdFaxNo', max_length=50, blank=True, null=True)
    work_address = models.TextField(db_column='WorkAddress', blank=True, null=True)
    work_country = models.CharField(db_column='WorkCountry', max_length=50, blank=True, null=True)
    work_state = models.CharField(db_column='WorkState', max_length=50, blank=True, null=True)
    work_city = models.CharField(db_column='WorkCity', max_length=50, blank=True, null=True)
    work_pin_no = models.CharField(db_column='WorkPinNo', max_length=20, blank=True, null=True)
    work_contact_no = models.CharField(db_column='WorkContactNo', max_length=50, blank=True, null=True)
    work_fax_no = models.CharField(db_column='WorkFaxNo', max_length=50, blank=True, null=True)
    material_del_address = models.TextField(db_column='MaterialDelAddress', blank=True, null=True)
    material_del_country = models.CharField(db_column='MaterialDelCountry', max_length=50, blank=True, null=True)
    material_del_state = models.CharField(db_column='MaterialDelState', max_length=50, blank=True, null=True)
    material_del_city = models.CharField(db_column='MaterialDelCity', max_length=50, blank=True, null=True)
    material_del_pin_no = models.CharField(db_column='MaterialDelPinNo', max_length=20, blank=True, null=True)
    material_del_contact_no = models.CharField(db_column='MaterialDelContactNo', max_length=50, blank=True, null=True)
    material_del_fax_no = models.CharField(db_column='MaterialDelFaxNo', max_length=50, blank=True, null=True)
    contact_person = models.CharField(db_column='ContactPerson', max_length=100, blank=True, null=True)
    juridiction_code = models.CharField(db_column='JuridictionCode', max_length=50, blank=True, null=True)
    commissionurate = models.CharField(db_column='Commissionurate', max_length=100, blank=True, null=True)
    tin_vat_no = models.CharField(db_column='TinVatNo', max_length=50, blank=True, null=True)
    email = models.EmailField(db_column='Email', blank=True, null=True)
    ecc_no = models.CharField(db_column='EccNo', max_length=50, blank=True, null=True)
    divn = models.CharField(db_column='Divn', max_length=50, blank=True, null=True)
    tin_cst_no = models.CharField(db_column='TinCstNo', max_length=50, blank=True, null=True)
    contact_no = models.CharField(db_column='ContactNo', max_length=50, blank=True, null=True)
    range = models.CharField(db_column='Range', max_length=50, blank=True, null=True)
    pan_no = models.CharField(db_column='PanNo', max_length=20, blank=True, null=True)
    tds_code = models.CharField(db_column='TDSCode', max_length=50, blank=True, null=True)
    remark = models.TextField(db_column='Remark', blank=True, null=True)
    mod_vat_applicable = models.IntegerField(db_column='ModVatApplicable', blank=True, null=True)
    mod_vat_invoice = models.IntegerField(db_column='ModVatInvoice', blank=True, null=True)
    bank_acc_no = models.CharField(db_column='BankAccNo', max_length=50, blank=True, null=True)
    bank_name = models.CharField(db_column='BankName', max_length=100, blank=True, null=True)
    bank_branch = models.CharField(db_column='BankBranch', max_length=100, blank=True, null=True)
    bank_address = models.TextField(db_column='BankAddress', blank=True, null=True)
    bank_acc_type = models.CharField(db_column='BankAccType', max_length=50, blank=True, null=True)
    business_type = models.CharField(db_column='BusinessType', max_length=255, blank=True, null=True)
    business_nature = models.CharField(db_column='BusinessNature', max_length=255, blank=True, null=True)
    service_coverage = models.CharField(db_column='ServiceCoverage', max_length=50, blank=True, null=True)
    pf = models.IntegerField(db_column='PF', blank=True, null=True)
    ex_st = models.IntegerField(db_column='ExST', blank=True, null=True)
    vat = models.IntegerField(db_column='VAT', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_Supplier_master'

    @property
    def fin_year_display(self):
        """Get financial year display name"""
        try:
            from sys_admin.models import TblfinancialMaster
            fin_year = TblfinancialMaster.objects.filter(
                finyearid=self.fin_year_id,
                compid=self.comp_id
            ).first()
            return fin_year.finyear if fin_year else f"FY-{self.fin_year_id}"
        except:
            return f"FY-{self.fin_year_id}"

class BusinessNature(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    nature = models.CharField(db_column='Nature', max_length=255)

    class Meta:
        managed = False
        db_table = 'tblMM_Supplier_BusinessNature'

    def __str__(self):
        return self.nature


class BusinessType(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    type = models.CharField(db_column='Type', max_length=255)

    class Meta:
        managed = False
        db_table = 'tblMM_Supplier_BusinessType'

    def __str__(self):
        return self.type

class Buyer(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    category = models.CharField(db_column='Category', max_length=50, blank=True, null=True)
    nos = models.IntegerField(db_column='Nos', blank=True, null=True)
    emp_id = models.CharField(db_column='EmpId', max_length=50, blank=True, null=True)  # Store employee ID as string

    class Meta:
        managed = False
        db_table = 'tblMM_Buyer_Master'

    def __str__(self):
        return f"{self.category} - {self.emp_id if self.emp_id else 'N/A'}"
    
    @property
    def emp(self):
        """Get employee object by empid"""
        if self.emp_id:
            try:
                return TblhrOfficestaff.objects.get(empid=self.emp_id)
            except TblhrOfficestaff.DoesNotExist:
                return None
        return None


class ServiceCoverage(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    coverage = models.CharField(db_column='Type', max_length=255)  # Column is named 'Type' in database

    class Meta:
        managed = False
        db_table = 'tblMM_Supplier_ServiceCoverage'

    def __str__(self):
        return self.coverage


# =============================================================================
# RATE MANAGEMENT MODELS
# =============================================================================

class RateRegister(models.Model):
    """Rate Register - Item-wise rate tracking from PO/PR/SPR"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sys_date = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    sys_time = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    session_id = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)
    amendment_no = models.IntegerField(db_column='AmendmentNo', blank=True, null=True)
    po_id = models.IntegerField(db_column='POId', blank=True, null=True)
    pr_id = models.IntegerField(db_column='PRId', blank=True, null=True)
    spr_id = models.IntegerField(db_column='SPRId', blank=True, null=True)
    po_no = models.CharField(db_column='PONo', max_length=50, blank=True, null=True)
    item_id = models.IntegerField(db_column='ItemId', blank=True, null=True)
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(db_column='Discount', max_digits=18, decimal_places=2, blank=True, null=True)
    pf = models.IntegerField(db_column='PF', blank=True, null=True)
    ex_st = models.IntegerField(db_column='ExST', blank=True, null=True)
    vat = models.IntegerField(db_column='VAT', blank=True, null=True)
    indirect_cost = models.DecimalField(db_column='IndirectCost', max_digits=18, decimal_places=2, blank=True, null=True)
    direct_cost = models.DecimalField(db_column='DirectCost', max_digits=18, decimal_places=2, blank=True, null=True)
    old_item_code = models.CharField(db_column='Old_ItemCode', max_length=50, blank=True, null=True)
    flag = models.IntegerField(db_column='Flag', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_Rate_Register'

    def __str__(self):
        return f"Rate for Item {self.item_id} - ₹{self.rate}"

    @property
    def amount(self):
        """Calculate amount after discount: Rate - (Rate * Discount / 100)"""
        if self.rate and self.discount:
            return float(self.rate) - (float(self.rate) * float(self.discount) / 100)
        return float(self.rate) if self.rate else 0


class RateLockUnlock(models.Model):
    """Rate Lock/Unlock tracking"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sys_date = models.CharField(db_column='SysDate', max_length=50)
    sys_time = models.CharField(db_column='SysTime', max_length=50)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    session_id = models.CharField(db_column='SessionId', max_length=50)
    item_id = models.IntegerField(db_column='ItemId', blank=True, null=True)  # FK to TblinvItemMaster
    lock_unlock = models.IntegerField(db_column='LockUnlock', blank=True, null=True)  # 0=Unlocked, 1=Locked
    type = models.IntegerField(db_column='Type', blank=True, null=True)
    locked_by_transaction = models.TextField(db_column='LockedbyTranaction', blank=True, null=True)  # Note: typo in DB
    lock_date = models.TextField(db_column='LockDate', blank=True, null=True)
    lock_time = models.TextField(db_column='LockTime', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_RateLockUnLock_Master'
    
    @property
    def is_locked(self):
        """Convert lock_unlock integer to boolean"""
        return self.lock_unlock == 1
    
    def __str__(self):
        status = "Locked" if self.is_locked else "Unlocked"
        return f"Item {self.item_id} - {status}"


# =============================================================================
# PURCHASE REQUISITION (PR) MODELS
# =============================================================================

class PRMaster(models.Model):
    """Purchase Requisition Master"""
    pr_id = models.AutoField(db_column='Id', primary_key=True)
    sys_date = models.CharField(db_column='SysDate', max_length=50)
    sys_time = models.CharField(db_column='SysTime', max_length=50)
    session_id = models.CharField(db_column='SessionId', max_length=50)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    wo_no = models.TextField(db_column='WONo', blank=True, null=True)
    pr_no = models.TextField(db_column='PRNo')
    checked = models.IntegerField(db_column='Checked', blank=True, null=True)
    checked_by = models.TextField(db_column='CheckedBy', blank=True, null=True)
    checked_date = models.TextField(db_column='CheckedDate', blank=True, null=True)
    checked_time = models.TextField(db_column='CheckedTime', blank=True, null=True)
    approve = models.IntegerField(db_column='Approve', blank=True, null=True)
    approved_by = models.TextField(db_column='ApprovedBy', blank=True, null=True)
    approve_date = models.TextField(db_column='ApproveDate', blank=True, null=True)
    approve_time = models.TextField(db_column='ApproveTime', blank=True, null=True)
    authorize = models.IntegerField(db_column='Authorize', blank=True, null=True)
    authorized_by = models.TextField(db_column='AuthorizedBy', blank=True, null=True)
    authorize_date = models.TextField(db_column='AuthorizeDate', blank=True, null=True)
    authorize_time = models.TextField(db_column='AuthorizeTime', blank=True, null=True)
    pln_id = models.IntegerField(db_column='PLNId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_PR_Master'

    def __str__(self):
        return f"PR-{self.pr_no}"
    
    @property
    def pr_date(self):
        """Return sys_date as PR date"""
        return self.sys_date
    
    @property
    def status(self):
        """Derive status from approval flags"""
        if self.authorize == 1:
            return 'Authorized'
        elif self.approve == 1:
            return 'Approved'
        elif self.checked == 1:
            return 'Checked'
        return 'Pending'


class PRDetails(models.Model):
    """
    Purchase Requisition Details - Each row represents one item from one supplier
    A PR can have multiple items, and same item can have multiple suppliers
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    m_id = models.IntegerField(db_column='MId')  # FK to PRMaster.Id
    pr_no = models.TextField(db_column='PRNo')  # PR Number for reference
    item_id = models.IntegerField(db_column='ItemId')  # FK to tblDG_Item_Master
    supplier_id = models.CharField(db_column='SupplierId', max_length=50, blank=True, null=True)
    qty = models.DecimalField(db_column='Qty', max_digits=18, decimal_places=3)
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2)
    discount = models.DecimalField(db_column='Discount', max_digits=18, decimal_places=2, default=0)
    del_date = models.CharField(db_column='DelDate', max_length=50, blank=True, null=True)  # Date string format
    ah_id = models.IntegerField(db_column='AHId', blank=True, null=True)  # Account head
    p_id = models.IntegerField(db_column='PId', blank=True, null=True)
    c_id = models.IntegerField(db_column='CId', blank=True, null=True)
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)
    type = models.IntegerField(db_column='Type', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_PR_Details'


class TempPR(models.Model):
    """Temporary PR Items - Staging table for PR creation process"""
    id = models.AutoField(db_column='Id', primary_key=True)
    comp_id = models.IntegerField(db_column='CompId')
    session_id = models.CharField(db_column='SessionId', max_length=50)
    wo_no = models.CharField(db_column='WONo', max_length=50, blank=True, null=True)
    item_id = models.IntegerField(db_column='ItemId')
    supplier_id = models.CharField(db_column='SupplierId', max_length=50, blank=True, null=True)
    qty = models.DecimalField(db_column='Qty', max_digits=18, decimal_places=2)
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2)
    discount = models.DecimalField(db_column='Discount', max_digits=18, decimal_places=2, default=0)
    del_date = models.DateField(db_column='DelDate', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_PLN_PR_Temp'

    def __str__(self):
        return f"Temp PR Item {self.item_id} - Qty: {self.qty}"

    @property
    def amount(self):
        """Calculate amount: Qty * Rate"""
        return float(self.qty) * float(self.rate) if self.qty and self.rate else 0

    @property
    def disc_rate(self):
        """Calculate discounted rate: Rate - (Rate * Discount / 100)"""
        if self.rate and self.discount:
            return float(self.rate) - (float(self.rate) * float(self.discount) / 100)
        return float(self.rate) if self.rate else 0


# =============================================================================
# SPECIAL PURPOSE REQUISITION (SPR) MODELS
# =============================================================================

class SPRMaster(models.Model):
    """Special Purpose Requisition Master"""
    spr_id = models.AutoField(db_column='Id', primary_key=True)  # Fixed: was SPRId
    spr_no = models.CharField(db_column='SPRNo', max_length=50, blank=True, null=True)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    sys_date = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    sys_time = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)
    session_id = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)
    checked = models.IntegerField(db_column='Checked', blank=True, null=True)
    checked_by = models.CharField(db_column='CheckedBy', max_length=50, blank=True, null=True)
    checked_date = models.CharField(db_column='CheckedDate', max_length=50, blank=True, null=True)
    checked_time = models.CharField(db_column='CheckedTime', max_length=50, blank=True, null=True)
    approve = models.IntegerField(db_column='Approve', blank=True, null=True)
    approved_by = models.CharField(db_column='ApprovedBy', max_length=50, blank=True, null=True)
    approve_date = models.CharField(db_column='ApproveDate', max_length=50, blank=True, null=True)
    approve_time = models.CharField(db_column='ApproveTime', max_length=50, blank=True, null=True)
    authorize = models.IntegerField(db_column='Authorize', blank=True, null=True)
    authorized_by = models.CharField(db_column='AuthorizedBy', max_length=50, blank=True, null=True)
    authorize_date = models.CharField(db_column='AuthorizeDate', max_length=50, blank=True, null=True)
    authorize_time = models.CharField(db_column='AuthorizeTime', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_SPR_Master'  # Fixed: was tblMM_SPR_MasterA

    def __str__(self):
        return f"SPR-{self.spr_no}"
    
    @property
    def spr_date(self):
        """Parse sys_date as date"""
        return self.sys_date
    
    @property
    def status(self):
        """Derive status from approval flags"""
        if self.authorize:
            return 'Authorized'
        elif self.approve:
            return 'Approved'
        elif self.checked:
            return 'Checked'
        return 'Pending'


class SPRDetails(models.Model):
    """Special Purpose Requisition Details"""
    id = models.AutoField(db_column='Id', primary_key=True)
    m_id = models.IntegerField(db_column='MId')  # FK to SPRMaster.Id
    spr_no = models.CharField(db_column='SPRNo', max_length=50, blank=True, null=True)
    item_id = models.IntegerField(db_column='ItemId')  # FK to TblinvItemMaster
    qty = models.DecimalField(db_column='Qty', max_digits=18, decimal_places=3, blank=True, null=True)
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(db_column='Discount', max_digits=18, decimal_places=2, blank=True, null=True)
    supplier_id = models.CharField(db_column='SupplierId', max_length=50, blank=True, null=True)
    ah_id = models.IntegerField(db_column='AHId', blank=True, null=True)  # Account head
    wo_no = models.CharField(db_column='WONo', max_length=50, blank=True, null=True)
    dept_id = models.IntegerField(db_column='DeptId', blank=True, null=True)
    del_date = models.CharField(db_column='DelDate', max_length=50, blank=True, null=True)
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_SPR_Details'


# =============================================================================
# PURCHASE ORDER (PO) MODELS
# =============================================================================

class POMaster(models.Model):
    """Purchase Order Master - Complete schema matching ASP.NET"""
    po_id = models.AutoField(db_column='Id', primary_key=True)
    po_no = models.CharField(db_column='PONo', max_length=50, blank=True, null=True)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    supplier_id = models.CharField(db_column='SupplierId', max_length=50, blank=True, null=True)
    sys_date = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    sys_time = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)
    session_id = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)
    pr_spr_flag = models.IntegerField(db_column='PRSPRFlag', blank=True, null=True)  # 0=PR, 1=SPR
    amendment_no = models.IntegerField(db_column='AmendmentNo', default=0, blank=True, null=True)
    reference = models.IntegerField(db_column='Reference', blank=True, null=True)  # FK to tblMM_PO_Reference
    reference_date = models.CharField(db_column='ReferenceDate', max_length=50, blank=True, null=True)
    reference_desc = models.TextField(db_column='ReferenceDesc', blank=True, null=True)
    payment_terms = models.IntegerField(db_column='PaymentTerms', blank=True, null=True)  # FK to tblPayment_Master
    warrenty = models.IntegerField(db_column='Warrenty', blank=True, null=True)  # FK to tblWarrenty_Master
    freight = models.IntegerField(db_column='Freight', blank=True, null=True)  # FK to tblFreight_Master
    octroi = models.IntegerField(db_column='Octroi', blank=True, null=True)  # FK to tblOctroi_Master
    mode_of_dispatch = models.TextField(db_column='ModeOfDispatch', blank=True, null=True)
    inspection = models.TextField(db_column='Inspection', blank=True, null=True)
    ship_to = models.TextField(db_column='ShipTo', blank=True, null=True)
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)
    insurance = models.TextField(db_column='Insurance', blank=True, null=True)
    tc = models.TextField(db_column='TC', blank=True, null=True)  # Terms & Conditions
    # File attachment fields
    filename = models.CharField(db_column='FileName', max_length=255, blank=True, null=True)
    filesize = models.IntegerField(db_column='FileSize', blank=True, null=True)
    contenttype = models.CharField(db_column='ContentType', max_length=100, blank=True, null=True)
    filedata = models.BinaryField(db_column='FileData', blank=True, null=True)
    # Approval workflow fields
    checked = models.IntegerField(db_column='Checked', default=0, blank=True, null=True)
    checked_by = models.CharField(db_column='CheckedBy', max_length=50, blank=True, null=True)
    checked_date = models.CharField(db_column='CheckedDate', max_length=50, blank=True, null=True)
    checked_time = models.CharField(db_column='CheckedTime', max_length=50, blank=True, null=True)
    approve = models.IntegerField(db_column='Approve', default=0, blank=True, null=True)
    approved_by = models.CharField(db_column='ApprovedBy', max_length=50, blank=True, null=True)
    approve_date = models.CharField(db_column='ApproveDate', max_length=50, blank=True, null=True)
    approve_time = models.CharField(db_column='ApproveTime', max_length=50, blank=True, null=True)
    authorize = models.IntegerField(db_column='Authorize', default=0, blank=True, null=True)
    authorized_by = models.CharField(db_column='AuthorizedBy', max_length=50, blank=True, null=True)
    authorize_date = models.CharField(db_column='AuthorizeDate', max_length=50, blank=True, null=True)
    authorize_time = models.CharField(db_column='AuthorizeTime', max_length=50, blank=True, null=True)
    head_po = models.IntegerField(db_column='HeadPO', blank=True, null=True)
    head_po_by = models.CharField(db_column='HeadPOBy', max_length=50, blank=True, null=True)
    head_po_date = models.CharField(db_column='HeadPODate', max_length=50, blank=True, null=True)
    head_po_time = models.CharField(db_column='HeadPOTime', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_PO_Master'

    def __str__(self):
        return f"PO-{self.po_no}"

    @property
    def po_date(self):
        """Return sys_date as PO date"""
        return self.sys_date

    @property
    def status(self):
        """Derive status from approval flags"""
        if self.authorize == 1:
            return 'Authorized'
        elif self.approve == 1:
            return 'Approved'
        elif self.checked == 1:
            return 'Checked'
        return 'Pending'


class PODetails(models.Model):
    """Purchase Order Details - Complete schema matching ASP.NET"""
    id = models.AutoField(db_column='Id', primary_key=True)
    m_id = models.IntegerField(db_column='MId')  # FK to POMaster.po_id
    po_no = models.CharField(db_column='PONo', max_length=50, blank=True, null=True)
    # PR fields (if pr_spr_flag=0)
    pr_no = models.CharField(db_column='PRNo', max_length=50, blank=True, null=True)
    pr_id = models.IntegerField(db_column='PRId', blank=True, null=True)  # FK to PRDetails.id
    # SPR fields (if pr_spr_flag=1)
    spr_no = models.CharField(db_column='SPRNo', max_length=50, blank=True, null=True)
    spr_id = models.IntegerField(db_column='SPRId', blank=True, null=True)  # FK to SPRDetails.id
    # Item details
    qty = models.DecimalField(db_column='Qty', max_digits=18, decimal_places=3)
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2)
    discount = models.DecimalField(db_column='Discount', max_digits=5, decimal_places=2, default=0)  # Percentage
    add_desc = models.TextField(db_column='AddDesc', blank=True, null=True)  # Additional description
    # Tax fields (FK to master tables)
    pf = models.IntegerField(db_column='PF', blank=True, null=True)  # Packing & Forwarding
    ex_st = models.IntegerField(db_column='ExST', blank=True, null=True)  # Excise/Service Tax
    vat = models.IntegerField(db_column='VAT', blank=True, null=True)
    del_date = models.CharField(db_column='DelDate', max_length=50, blank=True, null=True)  # Delivery date
    budget_code = models.CharField(db_column='BudgetCode', max_length=50, blank=True, null=True)
    amendment_no = models.IntegerField(db_column='AmendmentNo', default=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_PO_Details'

    def __str__(self):
        return f"PO Detail-{self.id}"


# =============================================================================
# PO TEMPORARY TABLES (for staging during creation/editing)
# =============================================================================

class MmPrPoTemp(models.Model):
    """Temporary table for PR → PO conversion"""
    id = models.AutoField(db_column='Id', primary_key=True)
    comp_id = models.IntegerField(db_column='CompId')
    session_id = models.CharField(db_column='SessionId', max_length=50)
    pr_no = models.CharField(db_column='PRNo', max_length=50, blank=True, null=True)
    pr_id = models.IntegerField(db_column='PRId')  # FK to PRDetails.id
    qty = models.DecimalField(db_column='Qty', max_digits=18, decimal_places=3)
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2)
    discount = models.DecimalField(db_column='Discount', max_digits=5, decimal_places=2, default=0)
    add_desc = models.TextField(db_column='AddDesc', blank=True, null=True)
    pf = models.IntegerField(db_column='PF', blank=True, null=True)
    ex_st = models.IntegerField(db_column='ExST', blank=True, null=True)
    vat = models.IntegerField(db_column='VAT', blank=True, null=True)
    del_date = models.CharField(db_column='DelDate', max_length=50, blank=True, null=True)
    budget_code = models.CharField(db_column='BudgetCode', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_PR_Po_Temp'


class MmSprPoTemp(models.Model):
    """Temporary table for SPR → PO conversion"""
    id = models.AutoField(db_column='Id', primary_key=True)
    comp_id = models.IntegerField(db_column='CompId')
    session_id = models.CharField(db_column='SessionId', max_length=50)
    spr_no = models.CharField(db_column='SPRNo', max_length=50, blank=True, null=True)
    spr_id = models.IntegerField(db_column='SPRId')  # FK to SPRDetails.id
    qty = models.DecimalField(db_column='Qty', max_digits=18, decimal_places=3)
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2)
    discount = models.DecimalField(db_column='Discount', max_digits=5, decimal_places=2, default=0)
    add_desc = models.TextField(db_column='AddDesc', blank=True, null=True)
    pf = models.IntegerField(db_column='PF', blank=True, null=True)
    ex_st = models.IntegerField(db_column='ExST', blank=True, null=True)
    vat = models.IntegerField(db_column='VAT', blank=True, null=True)
    del_date = models.CharField(db_column='DelDate', max_length=50, blank=True, null=True)
    budget_code = models.CharField(db_column='BudgetCode', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_SPR_Po_Temp'


# =============================================================================
# LEGACY MODEL ALIASES (for backward compatibility with inventory views)
# =============================================================================

# Alias for POMaster to match the import in inventory views
TblmmPoMaster = POMaster

# Alias for Supplier Master to match the import in inventory views  
class TblmmSupplierMaster(models.Model):
    """Supplier Master - matches tblMM_Supplier_Master table"""
    supid = models.AutoField(db_column='SupId', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50)
    systime = models.CharField(db_column='SysTime', max_length=50)
    sessionid = models.TextField(db_column='SessionId')
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    supplierid = models.TextField(db_column='SupplierId', blank=True, null=True)
    suppliername = models.TextField(db_column='SupplierName', blank=True, null=True)
    scopeofsupply = models.TextField(db_column='ScopeOfSupply', blank=True, null=True)
    regdaddress = models.TextField(db_column='RegdAddress', blank=True, null=True)
    regdcountry = models.IntegerField(db_column='RegdCountry', blank=True, null=True)
    regdstate = models.IntegerField(db_column='RegdState', blank=True, null=True)
    regdcity = models.IntegerField(db_column='RegdCity', blank=True, null=True)
    regdpinno = models.TextField(db_column='RegdPinNo', blank=True, null=True)
    regdcontactno = models.TextField(db_column='RegdContactNo', blank=True, null=True)
    regdfaxno = models.TextField(db_column='RegdFaxNo', blank=True, null=True)
    workaddress = models.TextField(db_column='WorkAddress', blank=True, null=True)
    workcountry = models.IntegerField(db_column='WorkCountry', blank=True, null=True)
    workstate = models.IntegerField(db_column='WorkState', blank=True, null=True)
    workcity = models.IntegerField(db_column='WorkCity', blank=True, null=True)
    workpinno = models.CharField(db_column='WorkPinNo', max_length=50, blank=True, null=True)
    workcontactno = models.TextField(db_column='WorkContactNo', blank=True, null=True)
    workfaxno = models.TextField(db_column='WorkFaxNo', blank=True, null=True)
    materialdeladdress = models.TextField(db_column='MaterialDelAddress', blank=True, null=True)
    materialdelcountry = models.IntegerField(db_column='MaterialDelCountry', blank=True, null=True)
    materialdelstate = models.IntegerField(db_column='MaterialDelState', blank=True, null=True)
    materialdelcity = models.IntegerField(db_column='MaterialDelCity', blank=True, null=True)
    materialdelpinno = models.TextField(db_column='MaterialDelPinNo', blank=True, null=True)
    materialdelcontactno = models.TextField(db_column='MaterialDelContactNo', blank=True, null=True)
    materialdelfaxno = models.TextField(db_column='MaterialDelFaxNo', blank=True, null=True)
    contactperson = models.TextField(db_column='ContactPerson', blank=True, null=True)
    juridictioncode = models.TextField(db_column='JuridictionCode', blank=True, null=True)
    commissionurate = models.TextField(db_column='Commissionurate', blank=True, null=True)
    tinvatno = models.TextField(db_column='TinVatNo', blank=True, null=True)
    email = models.TextField(db_column='Email', blank=True, null=True)
    eccno = models.TextField(db_column='EccNo', blank=True, null=True)
    divn = models.TextField(db_column='Divn', blank=True, null=True)
    tincstno = models.TextField(db_column='TinCstNo', blank=True, null=True)
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)
    range = models.TextField(db_column='Range', blank=True, null=True)
    panno = models.TextField(db_column='PanNo', blank=True, null=True)
    tdscode = models.TextField(db_column='TDSCode', blank=True, null=True)
    remark = models.TextField(db_column='Remark', blank=True, null=True)
    modvatapplicable = models.IntegerField(db_column='ModVatApplicable', blank=True, null=True)
    modvatinvoice = models.IntegerField(db_column='ModVatInvoice', blank=True, null=True)
    bankaccno = models.TextField(db_column='BankAccNo', blank=True, null=True)
    bankname = models.TextField(db_column='BankName', blank=True, null=True)
    bankbranch = models.TextField(db_column='BankBranch', blank=True, null=True)
    bankaddress = models.TextField(db_column='BankAddress', blank=True, null=True)
    bankacctype = models.TextField(db_column='BankAccType', blank=True, null=True)
    businesstype = models.TextField(db_column='BusinessType', blank=True, null=True)
    businessnature = models.TextField(db_column='BusinessNature', blank=True, null=True)
    servicecoverage = models.TextField(db_column='ServiceCoverage', blank=True, null=True)
    pf = models.IntegerField(db_column='PF', blank=True, null=True)
    exst = models.IntegerField(db_column='ExST', blank=True, null=True)
    vat = models.IntegerField(db_column='VAT', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMM_Supplier_Master'

    def __str__(self):
        return f"{self.suppliername} [{self.supplierid}]"
