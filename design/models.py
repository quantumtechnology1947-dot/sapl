from django.db import models

# Create your models here.


class Allitems(models.Model):
    itemcode = models.CharField(db_column='ItemCode', max_length=255, blank=True, null=True)  # Field name made lowercase.
    n = models.CharField(db_column='N', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AllItems'


class Allrates(models.Model):
    itemcode = models.CharField(db_column='ItemCode', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rate = models.CharField(db_column='Rate', max_length=255, blank=True, null=True)  # Field name made lowercase.
    discount = models.CharField(db_column='Discount', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AllRates'


class TbldgBomAmd(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    bomid = models.TextField(db_column='BOMId', blank=True, null=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='PId', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    uom = models.IntegerField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    amdno = models.IntegerField(db_column='AmdNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_BOM_Amd'


class TbldgBomMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    equipmentno = models.TextField(db_column='EquipmentNo', blank=True, null=True)  # Field name made lowercase.
    unitno = models.CharField(db_column='UnitNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    partno = models.TextField(db_column='PartNo', blank=True, null=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='PId', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    ecn = models.IntegerField(db_column='ECN', blank=True, null=True)  # Field name made lowercase.
    ecnflag = models.IntegerField(db_column='ECNFlag', blank=True, null=True)  # Field name made lowercase.
    amdno = models.IntegerField(db_column='AmdNo')  # Field name made lowercase.
    revision = models.CharField(db_column='Revision', max_length=50)  # Field name made lowercase.
    remark = models.TextField(db_column='Remark', blank=True, null=True)  # Field name made lowercase.
    material = models.TextField(db_column='Material', blank=True, null=True)  # Field name made lowercase.
    itemid = models.ForeignKey('TbldgItemMaster', models.DO_NOTHING, db_column='ItemId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_BOM_Master'


class TbldgBomitemTemp(models.Model):
    """Temporary storage for BOM items before final commit"""
    id = models.AutoField(db_column='Id', primary_key=True)
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)
    wono = models.TextField(db_column='WONo', blank=True, null=True)
    itemid = models.ForeignKey('TbldgItemMaster', models.DO_NOTHING, db_column='ItemId', blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)
    childid = models.IntegerField(db_column='ChildId', blank=True, null=True)
    partno = models.TextField(db_column='PartNo', blank=True, null=True)
    manfdesc = models.TextField(db_column='ManfDesc', blank=True, null=True)
    uombasic = models.IntegerField(db_column='UOMBasic', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblDG_BOMItem_Temp'


class TbldgCategoryMaster(models.Model):
    cid = models.AutoField(db_column='CId', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessinid = models.CharField(db_column='SessinId', max_length=50)  # Field name made lowercase.
    cname = models.TextField(db_column='CName')  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol')  # Field name made lowercase.
    hassubcat = models.CharField(db_column='HasSubCat', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Category_Master'


class TbldgEcnDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    ecnreason = models.IntegerField(db_column='ECNReason', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TbldgEcnMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_ECN_Details'


class TbldgEcnMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='PId', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    flag = models.IntegerField(db_column='Flag', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_ECN_Master'


class TbldgEcnReason(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    types = models.TextField(db_column='Types', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_ECN_Reason'


class TbldgGunrailBomMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    equipmentno = models.TextField(db_column='EquipmentNo', blank=True, null=True)  # Field name made lowercase.
    unitno = models.CharField(db_column='UnitNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    partno = models.TextField(db_column='PartNo', blank=True, null=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='PId', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_GUNRAIL_BOM_Master'


class TbldgGunrailCrossrail(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    length = models.FloatField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
    no = models.FloatField(db_column='No', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TbldgGunrailPitchMaster', models.DO_NOTHING, db_column='MId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Gunrail_CrossRail'


class TbldgGunrailCrossrailDispatch(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    length = models.FloatField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
    no = models.FloatField(db_column='No', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TbldgGunrailPitchDispatchMaster', models.DO_NOTHING, db_column='MId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Gunrail_CrossRail_Dispatch'


class TbldgGunrailLongrail(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    length = models.FloatField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
    no = models.FloatField(db_column='No', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TbldgGunrailPitchMaster', models.DO_NOTHING, db_column='MId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Gunrail_LongRail'


class TbldgGunrailLongrailDispatch(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    length = models.FloatField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
    no = models.FloatField(db_column='No', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TbldgGunrailPitchDispatchMaster', models.DO_NOTHING, db_column='MId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Gunrail_LongRail_Dispatch'


class TbldgGunrailPitchDispatchMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    wono = models.CharField(db_column='WONo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pitch = models.FloatField(db_column='Pitch', blank=True, null=True)  # Field name made lowercase.
    type = models.IntegerField(db_column='Type', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Gunrail_Pitch_Dispatch_Master'


class TbldgGunrailPitchMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    wono = models.CharField(db_column='WONo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pitch = models.FloatField(db_column='Pitch', blank=True, null=True)  # Field name made lowercase.
    type = models.IntegerField(db_column='Type', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Gunrail_Pitch_Master'


class TbldgItemClass(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    class_field = models.TextField(db_column='Class', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Item_Class'


class TbldgItemMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    partno = models.TextField(db_column='PartNo', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    manfdesc = models.TextField(db_column='ManfDesc', blank=True, null=True)  # Field name made lowercase.
    uombasic = models.IntegerField(db_column='UOMBasic', blank=True, null=True)  # Field name made lowercase.
    minorderqty = models.FloatField(db_column='MinOrderQty', blank=True, null=True)  # Field name made lowercase.
    minstockqty = models.FloatField(db_column='MinStockQty', blank=True, null=True)  # Field name made lowercase.
    stockqty = models.FloatField(db_column='StockQty')  # Field name made lowercase.
    process = models.IntegerField(db_column='Process', blank=True, null=True)  # Field name made lowercase.
    class_field = models.IntegerField(db_column='Class', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    leaddays = models.TextField(db_column='LeadDays', blank=True, null=True)  # Field name made lowercase.
    inspectiondays = models.TextField(db_column='InspectionDays', blank=True, null=True)  # Field name made lowercase.
    location = models.IntegerField(db_column='Location', blank=True, null=True)  # Field name made lowercase.
    filename = models.TextField(db_column='FileName', blank=True, null=True)  # Field name made lowercase.
    filesize = models.FloatField(db_column='FileSize', blank=True, null=True)  # Field name made lowercase.
    contenttype = models.TextField(db_column='ContentType', blank=True, null=True)  # Field name made lowercase.
    filedata = models.BinaryField(db_column='FileData', blank=True, null=True)  # Field name made lowercase.
    absolute = models.IntegerField(db_column='Absolute', blank=True, null=True)  # Field name made lowercase.
    openingbaldate = models.TextField(db_column='OpeningBalDate')  # Field name made lowercase.
    openingbalqty = models.FloatField(db_column='OpeningBalQty')  # Field name made lowercase.
    uomconfact = models.IntegerField(db_column='UOMConFact', blank=True, null=True)  # Field name made lowercase.
    excise = models.IntegerField(db_column='Excise')  # Field name made lowercase.
    importlocal = models.IntegerField(db_column='ImportLocal')  # Field name made lowercase.
    attname = models.TextField(db_column='AttName', blank=True, null=True)  # Field name made lowercase.
    attsize = models.FloatField(db_column='AttSize', blank=True, null=True)  # Field name made lowercase.
    attcontenttype = models.TextField(db_column='AttContentType', blank=True, null=True)  # Field name made lowercase.
    attdata = models.BinaryField(db_column='AttData', blank=True, null=True)  # Field name made lowercase.
    buyer = models.IntegerField(db_column='Buyer', blank=True, null=True)  # Field name made lowercase.
    ahid = models.IntegerField(db_column='AHId', blank=True, null=True)  # Field name made lowercase.
    hsncode = models.CharField(db_column='HSNcode', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Item_Master'

    def __str__(self):
        """Return readable representation of item"""
        # Use itemcode and description for display
        itemcode = self.itemcode or self.partno or f"ID-{self.id}"
        manfdesc = self.manfdesc[:50] if self.manfdesc else "No description"
        return f"{itemcode} - {manfdesc}"


class TbldgLocationMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    locationlabel = models.TextField(db_column='LocationLabel', blank=True, null=True)  # Field name made lowercase.
    locationno = models.TextField(db_column='LocationNo', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_Location_Master'


class TbldgSubcategoryMaster(models.Model):
    scid = models.AutoField(db_column='SCId', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId')  # Field name made lowercase.
    scname = models.TextField(db_column='SCName')  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDG_SubCategory_Master'
