"""
MIS (Management Information System) Module Models

This module handles budgeting, budget allocation, and MIS reports.
All models use managed=False to access existing database tables.
"""

from django.db import models


class TblmisBudgetcode(models.Model):
    """Budget Code Master - Budget categories and codes"""
    id = models.AutoField(db_column='Id', primary_key=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMIS_BudgetCode'
        verbose_name = 'Budget Code'
        verbose_name_plural = 'Budget Codes'

    def __str__(self):
        if self.symbol and self.description:
            return f"{self.symbol} - {self.description}"
        return str(self.symbol or self.description or f"Budget Code {self.id}")


class TblmisBudgetcodeTime(models.Model):
    """Budget Code Time - Time-based budget categories"""
    id = models.AutoField(db_column='Id', primary_key=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMIS_BudgetCode_Time'
        verbose_name = 'Budget Code Time'
        verbose_name_plural = 'Budget Codes Time'

    def __str__(self):
        if self.symbol and self.description:
            return f"{self.symbol} - {self.description}"
        return str(self.symbol or self.description or f"Time Code {self.id}")


class TblmisBudgethrsFieldCategory(models.Model):
    """Budget Hours Field Category - Main categories for budget hour fields"""
    id = models.AutoField(db_column='Id', primary_key=True)
    category = models.TextField(db_column='Category', blank=True, null=True)
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMIS_BudgetHrs_Field_Category'
        verbose_name = 'Budget Hours Field Category'
        verbose_name_plural = 'Budget Hours Field Categories'

    def __str__(self):
        if self.symbol and self.category:
            return f"{self.symbol} - {self.category}"
        return str(self.category or self.symbol or f"Category {self.id}")


class TblmisBudgethrsFieldSubcategory(models.Model):
    """Budget Hours Field Sub-Category - Sub-categories under main categories"""
    id = models.AutoField(db_column='Id', primary_key=True)
    subcategory = models.TextField(db_column='SubCategory', blank=True, null=True)
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)
    mid = models.ForeignKey(
        TblmisBudgethrsFieldCategory,
        on_delete=models.CASCADE,
        db_column='MId',
        related_name='subcategories'
    )

    class Meta:
        managed = False
        db_table = 'tblMIS_BudgetHrs_Field_SubCategory'
        verbose_name = 'Budget Hours Field Sub-Category'
        verbose_name_plural = 'Budget Hours Field Sub-Categories'

    def __str__(self):
        if self.symbol and self.subcategory:
            return f"{self.symbol} - {self.subcategory}"
        return str(self.subcategory or self.symbol or f"Sub-Category {self.id}")


# Budget Transaction Models

class TblaccBudgetWo(models.Model):
    """Budget allocation for work orders"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sys_date = models.DateField(db_column='SysDate')
    sys_time = models.TimeField(db_column='SysTime')
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    session_id = models.CharField(db_column='SessionId', max_length=50)
    wo_no = models.CharField(db_column='WONo', max_length=50)
    budget_code_id = models.ForeignKey(
        TblmisBudgetcode,
        on_delete=models.DO_NOTHING,
        db_column='BudgetCodeId',
        related_name='budget_allocations'
    )
    amount = models.DecimalField(
        db_column='Amount',
        max_digits=18,
        decimal_places=2
    )

    class Meta:
        managed = False
        db_table = 'tblACC_Budget_WO'
        verbose_name = 'Work Order Budget'
        verbose_name_plural = 'Work Order Budgets'

    def __str__(self):
        return f"Budget {self.wo_no} - {self.budget_code_id} - {self.amount}"


class TblaccBudgetWoTime(models.Model):
    """Budget Hours allocation for work orders

    Tracks budget hours assigned to work orders by equipment, category, and sub-category.
    This is the time/hours equivalent of TblaccBudgetWo (which tracks financial budget).
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    comp_id = models.IntegerField(db_column='CompId')
    sys_date = models.CharField(db_column='SysDate', max_length=50)
    sys_time = models.CharField(db_column='SysTime', max_length=50)
    session_id = models.CharField(db_column='SessionId', max_length=50)
    fin_year_id = models.IntegerField(db_column='FinYearId')
    wo_no = models.TextField(db_column='WONo', blank=True, null=True)
    equip_id = models.IntegerField(db_column='EquipId', blank=True, null=True)
    hrs_budget_cat = models.IntegerField(db_column='HrsBudgetCat', blank=True, null=True)
    hrs_budget_sub_cat = models.IntegerField(db_column='HrsBudgetSubCat', blank=True, null=True)
    hour = models.FloatField(db_column='Hour', blank=True, null=True)
    budget_amt_hrs = models.FloatField(db_column='BudgetAmtHrs', blank=True, null=True)
    budget_code_id = models.IntegerField(db_column='BudgetCodeId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblACC_Budget_WO_Time'
        verbose_name = 'Work Order Budget Hours'
        verbose_name_plural = 'Work Order Budget Hours'

    def __str__(self):
        return f"Budget Hours {self.wo_no} - {self.hour}hrs"


# Purchase Order Models

class TblmmPoMaster(models.Model):
    """Purchase Order Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    po_no = models.CharField(db_column='PONo', max_length=50)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    pr_spr_flag = models.IntegerField(db_column='PRSPRFlag')  # 0=PR, 1=SPR
    authorize = models.IntegerField(db_column='Authorize')  # 0=Non-Auth, 1=Auth

    class Meta:
        managed = False
        db_table = 'tblMM_PO_Master'
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'

    def __str__(self):
        return self.po_no


class TblmmPoDetails(models.Model):
    """Purchase Order Details"""
    id = models.AutoField(db_column='Id', primary_key=True)
    po_no = models.CharField(db_column='PONo', max_length=50)
    pr_id = models.IntegerField(db_column='PRId', null=True, blank=True)
    pr_no = models.CharField(db_column='PRNo', max_length=50, null=True, blank=True)
    spr_id = models.IntegerField(db_column='SPRId', null=True, blank=True)
    spr_no = models.CharField(db_column='SPRNo', max_length=50, null=True, blank=True)
    budget_code = models.IntegerField(db_column='BudgetCode')
    qty = models.DecimalField(db_column='Qty', max_digits=18, decimal_places=3)
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2)
    discount = models.DecimalField(db_column='Discount', max_digits=18, decimal_places=2, default=0)
    pf = models.IntegerField(db_column='PF')  # Packing & Forwarding ID
    ex_st = models.IntegerField(db_column='ExST')  # Excise/Service Tax ID
    vat = models.IntegerField(db_column='VAT')  # VAT ID

    class Meta:
        managed = False
        db_table = 'tblMM_PO_Details'
        verbose_name = 'PO Detail'
        verbose_name_plural = 'PO Details'

    def __str__(self):
        return f"{self.po_no} - Item {self.id}"


# Purchase Requisition Models

class TblmmPrMaster(models.Model):
    """Purchase Requisition Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    pr_no = models.CharField(db_column='PRNo', max_length=50)
    wo_no = models.CharField(db_column='WONo', max_length=50, null=True, blank=True)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')

    class Meta:
        managed = False
        db_table = 'tblMM_PR_Master'
        verbose_name = 'Purchase Requisition'
        verbose_name_plural = 'Purchase Requisitions'

    def __str__(self):
        return self.pr_no


class TblmmPrDetails(models.Model):
    """Purchase Requisition Details"""
    id = models.AutoField(db_column='Id', primary_key=True)
    m_id = models.ForeignKey(
        TblmmPrMaster,
        on_delete=models.DO_NOTHING,
        db_column='MId',
        related_name='details'
    )
    pr_no = models.CharField(db_column='PRNo', max_length=50)
    wo_no = models.CharField(db_column='WONo', max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tblMM_PR_Details'
        verbose_name = 'PR Detail'
        verbose_name_plural = 'PR Details'

    def __str__(self):
        return f"{self.pr_no} - Item {self.id}"


# Service Purchase Requisition Models

class TblmmSprMaster(models.Model):
    """Service Purchase Requisition Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    spr_no = models.CharField(db_column='SPRNo', max_length=50)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')

    class Meta:
        managed = False
        db_table = 'tblMM_SPR_Master'
        verbose_name = 'Service Purchase Requisition'
        verbose_name_plural = 'Service Purchase Requisitions'

    def __str__(self):
        return self.spr_no


class TblmmSprDetails(models.Model):
    """Service Purchase Requisition Details"""
    id = models.AutoField(db_column='Id', primary_key=True)
    m_id = models.ForeignKey(
        TblmmSprMaster,
        on_delete=models.DO_NOTHING,
        db_column='MId',
        related_name='details'
    )
    spr_no = models.CharField(db_column='SPRNo', max_length=50)
    wo_no = models.CharField(db_column='WONo', max_length=50, null=True, blank=True)
    dept_id = models.IntegerField(db_column='DeptId', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tblMM_SPR_Details'
        verbose_name = 'SPR Detail'
        verbose_name_plural = 'SPR Details'

    def __str__(self):
        return f"{self.spr_no} - Item {self.id}"


# Cash Voucher Models

class TblaccCashVoucherPaymentMaster(models.Model):
    """Cash Voucher Payment Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')

    class Meta:
        managed = False
        db_table = 'tblACC_CashVoucher_Payment_Master'
        verbose_name = 'Cash Payment Voucher'
        verbose_name_plural = 'Cash Payment Vouchers'

    def __str__(self):
        return f"Cash Payment {self.id}"


class TblaccCashVoucherPaymentDetails(models.Model):
    """Cash Voucher Payment Details"""
    id = models.AutoField(db_column='Id', primary_key=True)
    m_id = models.ForeignKey(
        TblaccCashVoucherPaymentMaster,
        on_delete=models.DO_NOTHING,
        db_column='MId',
        related_name='details'
    )
    wo_no = models.CharField(db_column='WONo', max_length=50)
    budget_code = models.IntegerField(db_column='BudgetCode')
    amount = models.DecimalField(db_column='Amount', max_digits=18, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'tblACC_CashVoucher_Payment_Details'
        verbose_name = 'Cash Payment Detail'
        verbose_name_plural = 'Cash Payment Details'

    def __str__(self):
        return f"Payment {self.m_id_id} - {self.amount}"


class TblaccCashVoucherReceiptMaster(models.Model):
    """Cash Voucher Receipt Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    comp_id = models.IntegerField(db_column='CompId')
    fin_year_id = models.IntegerField(db_column='FinYearId')
    wo_no = models.CharField(db_column='WONo', max_length=50)
    budget_code = models.IntegerField(db_column='BudgetCode')
    amount = models.DecimalField(db_column='Amount', max_digits=18, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'tblACC_CashVoucher_Receipt_Master'
        verbose_name = 'Cash Receipt Voucher'
        verbose_name_plural = 'Cash Receipt Vouchers'

    def __str__(self):
        return f"Cash Receipt {self.id} - {self.amount}"


# Tax Master Models

class TblPackingMaster(models.Model):
    """Packing & Forwarding Charges Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    value = models.DecimalField(db_column='Value', max_digits=18, decimal_places=3)

    class Meta:
        managed = False
        db_table = 'tblPacking_Master'
        verbose_name = 'Packing Charge'
        verbose_name_plural = 'Packing Charges'

    def __str__(self):
        return f"PF {self.value}%"


class TblExciseserMaster(models.Model):
    """Excise/Service Tax Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    value = models.DecimalField(db_column='Value', max_digits=18, decimal_places=3)

    class Meta:
        managed = False
        db_table = 'tblExciseser_Master'
        verbose_name = 'Excise/Service Tax'
        verbose_name_plural = 'Excise/Service Taxes'

    def __str__(self):
        return f"ExST {self.value}%"


class TblVatMaster(models.Model):
    """VAT Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    value = models.DecimalField(db_column='Value', max_digits=18, decimal_places=3)

    class Meta:
        managed = False
        db_table = 'tblVAT_Master'
        verbose_name = 'VAT'
        verbose_name_plural = 'VAT'

    def __str__(self):
        return f"VAT {self.value}%"
