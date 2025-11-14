"""
Material Planning Module Models

Converted from: aspnet/Module/MaterialPlanning/
Follows Django conventions with managed=False for existing database tables.
"""

from django.db import models
# from inventory.models import TblinvItemMaster  # Commented - causing import error


class TblmpMaterialMaster(models.Model):
    """Material Planning Master - Planning header"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)
    compid = models.IntegerField(db_column='CompId')
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)
    finyearid = models.IntegerField(db_column='FinYearId')
    plno = models.TextField(db_column='PLNo')  # Planning Number
    wono = models.TextField(db_column='WONo')  # Work Order Number

    class Meta:
        managed = False
        db_table = 'tblMP_Material_Master'
        ordering = ['-id']

    def __str__(self):
        return f"Plan {self.plno} - WO {self.wono}"


class TblmpMaterialDetail(models.Model):
    """Material Planning Detail - Links items with RM/PRO/FIN flags"""
    id = models.AutoField(db_column='Id', primary_key=True)
    item = models.IntegerField(db_column='ItemId', blank=True, null=True)
    rm = models.IntegerField(db_column='RM', blank=True, null=True)  # Raw Material flag
    pro = models.IntegerField(db_column='PRO', blank=True, null=True)  # Process flag
    fin = models.IntegerField(db_column='FIN', blank=True, null=True)  # Finish flag
    master = models.ForeignKey(TblmpMaterialMaster, models.CASCADE, db_column='Mid', related_name='details', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMP_Material_Detail'

    def __str__(self):
        return f"Detail {self.id} - {self.item.itemname if self.item else 'N/A'}"

    @property
    def category_display(self):
        """Return category as string"""
        if self.rm:
            return "Raw Material"
        elif self.pro:
            return "Process"
        elif self.fin:
            return "Finish"
        return "Unknown"


class TblmpMaterialRawmaterial(models.Model):
    """Raw Material Requirements"""
    id = models.AutoField(db_column='Id', primary_key=True)
    item = models.IntegerField(db_column='ItemId', blank=True, null=True)
    supplierid = models.TextField(db_column='SupplierId', blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)
    rate = models.FloatField(db_column='Rate', blank=True, null=True)
    discount = models.FloatField(db_column='Discount', blank=True, null=True, default=0)
    deldate = models.TextField(db_column='DelDate', blank=True, null=True)
    detail = models.ForeignKey(TblmpMaterialDetail, models.CASCADE, db_column='DMid', related_name='raw_materials', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMP_Material_RawMaterial'

    def __str__(self):
        return f"RM {self.id} - Item {self.item}"

    @property
    def amount(self):
        if self.qty and self.rate:
            return (self.qty * self.rate) - (self.discount or 0)
        return 0


class TblmpMaterialProcess(models.Model):
    """Process Requirements"""
    id = models.AutoField(db_column='Id', primary_key=True)
    item = models.IntegerField(db_column='ItemId', blank=True, null=True)
    supplierid = models.TextField(db_column='SupplierId', blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)
    rate = models.FloatField(db_column='Rate', blank=True, null=True)
    discount = models.FloatField(db_column='Discount', blank=True, null=True, default=0)
    deldate = models.TextField(db_column='DelDate', blank=True, null=True)
    detail = models.ForeignKey(TblmpMaterialDetail, models.CASCADE, db_column='DMid', related_name='processes', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMP_Material_Process'

    def __str__(self):
        return f"Process {self.id} - Item {self.item}"

    @property
    def amount(self):
        if self.qty and self.rate:
            return (self.qty * self.rate) - (self.discount or 0)
        return 0


class TblmpMaterialFinish(models.Model):
    """Finished Goods Requirements"""
    id = models.AutoField(db_column='Id', primary_key=True)
    item = models.IntegerField(db_column='ItemId', blank=True, null=True)
    supplierid = models.TextField(db_column='SupplierId')
    qty = models.FloatField(db_column='Qty')
    rate = models.FloatField(db_column='Rate')
    discount = models.FloatField(db_column='Discount')
    deldate = models.TextField(db_column='DelDate')
    detail = models.ForeignKey(TblmpMaterialDetail, models.CASCADE, db_column='DMid', related_name='finishes')

    class Meta:
        managed = False
        db_table = 'tblMP_Material_Finish'

    def __str__(self):
        return f"Finish {self.id} - {self.item.itemname if self.item else 'N/A'}"

    @property
    def amount(self):
        return (self.qty * self.rate) - self.discount


# ============================================================================
# TEMPORARY PLANNING TABLES (Session-based, multi-user isolation)
# Converted from: aaspnet/Module/MaterialPlanning/Transactions/pdt.aspx.cs
# These tables are cleared on page load (Page_Load lines 95-122)
# Used for "Add to Temp" workflow before "Generate PLN"
# ============================================================================

class TblmpMaterialDetailTemp(models.Model):
    """
    Temporary planning detail records (session-based)
    Links to temporary supplier quote tables via Id (DMid foreign key)
    Cleared on page load to prevent stale data

    ASP.NET Reference: pdt.aspx.cs lines 38-70, 95-122 (cleanup)
                      pdt.aspx.cs lines 402-500 (insert on Add to Temp)
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    wono = models.TextField(db_column='WONo', blank=True, null=True)
    item = models.IntegerField(db_column='ItemId', blank=True, null=True)
    bomqty = models.FloatField(db_column='BOMQty', blank=True, null=True)
    available = models.FloatField(db_column='Available', blank=True, null=True)
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # KEY: User isolation
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMP_Material_Detail_Temp'

    def __str__(self):
        return f"Temp Detail {self.id} - WO: {self.wono}, Item: {self.item}, Session: {self.sessionid}"


class TblmpMaterialRawmaterialTemp(models.Model):
    """
    Temporary raw material supplier quotes (session-based)
    Links to TblmpMaterialDetailTemp via DMid foreign key
    Represents Raw Material [A] procurement strategy

    ASP.NET Reference: pdt.aspx.cs lines 46-56 (cleanup)
                      pdt.aspx.cs lines 402-500 (insert from GridView3)
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    dmid = models.IntegerField(db_column='DMid', blank=True, null=True)  # FK to TblmpMaterialDetailTemp.Id
    supplier = models.CharField(db_column='Supplier', max_length=100, blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)
    rate = models.FloatField(db_column='Rate', blank=True, null=True)
    discount = models.FloatField(db_column='Discount', blank=True, null=True)
    deliverydate = models.CharField(db_column='DeliveryDate', max_length=50, blank=True, null=True)
    total = models.FloatField(db_column='Total', blank=True, null=True)
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # KEY: User isolation

    class Meta:
        managed = False
        db_table = 'tblMP_Material_RawMaterial_Temp'

    def __str__(self):
        return f"Temp Raw Material {self.id} - DMid: {self.dmid}, Supplier: {self.supplier}"


class TblmpMaterialProcessTemp(models.Model):
    """
    Temporary process supplier quotes (session-based)
    Links to TblmpMaterialDetailTemp via DMid foreign key
    Represents Process [O] procurement strategy (outsource processing/machining)

    ASP.NET Reference: pdt.aspx.cs lines 52-56 (cleanup)
                      pdt.aspx.cs lines 402-500 (insert from GridView4)
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    dmid = models.IntegerField(db_column='DMid', blank=True, null=True)  # FK to TblmpMaterialDetailTemp.Id
    supplier = models.CharField(db_column='Supplier', max_length=100, blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)
    rate = models.FloatField(db_column='Rate', blank=True, null=True)
    discount = models.FloatField(db_column='Discount', blank=True, null=True)
    deliverydate = models.CharField(db_column='DeliveryDate', max_length=50, blank=True, null=True)
    total = models.FloatField(db_column='Total', blank=True, null=True)
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # KEY: User isolation

    class Meta:
        managed = False
        db_table = 'tblMP_Material_Process_Temp'

    def __str__(self):
        return f"Temp Process {self.id} - DMid: {self.dmid}, Supplier: {self.supplier}"


class TblmpMaterialFinishTemp(models.Model):
    """
    Temporary finish supplier quotes (session-based)
    Links to TblmpMaterialDetailTemp via DMid foreign key
    Represents Finish [F] procurement strategy (outsource finishing like coating, painting)

    ASP.NET Reference: pdt.aspx.cs lines 58-62 (cleanup)
                      pdt.aspx.cs lines 402-500 (insert from GridView5)
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    dmid = models.IntegerField(db_column='DMid', blank=True, null=True)  # FK to TblmpMaterialDetailTemp.Id
    supplier = models.CharField(db_column='Supplier', max_length=100, blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)
    rate = models.FloatField(db_column='Rate', blank=True, null=True)
    discount = models.FloatField(db_column='Discount', blank=True, null=True)
    deliverydate = models.CharField(db_column='DeliveryDate', max_length=50, blank=True, null=True)
    total = models.FloatField(db_column='Total', blank=True, null=True)
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # KEY: User isolation

    class Meta:
        managed = False
        db_table = 'tblMP_Material_Finish_Temp'

    def __str__(self):
        return f"Temp Finish {self.id} - DMid: {self.dmid}, Supplier: {self.supplier}"


# ============================================================================
# OTHER MATERIAL PLANNING RELATED TABLES
# ============================================================================

class TblplnProcessMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    processname = models.TextField(db_column='ProcessName', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPln_Process_Master'
