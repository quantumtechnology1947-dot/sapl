from django.db import models

# Create your models here.



class TblinvqcStockadjlog(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    logno = models.TextField(db_column='LogNo', blank=True, null=True)  # Field name made lowercase.
    transtype = models.IntegerField(db_column='TransType', blank=True, null=True)  # Field name made lowercase.
    transno = models.TextField(db_column='TransNo', blank=True, null=True)  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInvQc_StockAdjLog'


class TblinvClosingstck(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    fromdt = models.TextField(db_column='FromDt', blank=True, null=True)  # Field name made lowercase.
    todt = models.TextField(db_column='ToDt', blank=True, null=True)  # Field name made lowercase.
    clstock = models.FloatField(db_column='ClStock', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_ClosingStck'


class TblinvCustomerChallanDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    challanqty = models.FloatField(db_column='ChallanQty', blank=True, null=True)  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblinvCustomerChallanMaster', models.DO_NOTHING, db_column='MId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_Customer_Challan_Details'


class TblinvCustomerChallanMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    ccno = models.CharField(db_column='CCNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    customerid = models.TextField(db_column='CustomerId', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_Customer_Challan_Master'


class TblinvInwardDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    ginno = models.TextField(db_column='GINNo', blank=True, null=True)  # Field name made lowercase.
    ginid = models.IntegerField(db_column='GINId', blank=True, null=True)  # Field name made lowercase.
    poid = models.IntegerField(db_column='POId', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    receivedqty = models.FloatField(db_column='ReceivedQty', blank=True, null=True)  # Field name made lowercase.
    acategoyid = models.IntegerField(db_column='ACategoyId', blank=True, null=True)  # Field name made lowercase.
    asubcategoyid = models.IntegerField(db_column='ASubCategoyId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_Inward_Details'


class TblinvInwardMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    ginno = models.TextField(db_column='GINNo', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    pomid = models.IntegerField(db_column='POMId', blank=True, null=True)  # Field name made lowercase.
    challanno = models.TextField(db_column='ChallanNo', blank=True, null=True)  # Field name made lowercase.
    challandate = models.TextField(db_column='ChallanDate', blank=True, null=True)  # Field name made lowercase.
    gateentryno = models.TextField(db_column='GateEntryNo', blank=True, null=True)  # Field name made lowercase.
    gdate = models.TextField(db_column='GDate', blank=True, null=True)  # Field name made lowercase.
    gtime = models.TextField(db_column='GTime', blank=True, null=True)  # Field name made lowercase.
    modeoftransport = models.TextField(db_column='ModeofTransport', blank=True, null=True)  # Field name made lowercase.
    vehicleno = models.TextField(db_column='VehicleNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_Inward_Master'


class TblinvMaterialissueDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    minno = models.TextField(db_column='MINNo', blank=True, null=True)  # Field name made lowercase.
    mrsid = models.IntegerField(db_column='MRSId', blank=True, null=True)  # Field name made lowercase.
    issueqty = models.FloatField(db_column='IssueQty', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_MaterialIssue_Details'


class TblinvMaterialissueMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    minno = models.TextField(db_column='MINNo', blank=True, null=True)  # Field name made lowercase.
    mrsno = models.TextField(db_column='MRSNo', blank=True, null=True)  # Field name made lowercase.
    mrsid = models.IntegerField(db_column='MRSId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_MaterialIssue_Master'


class TblinvMaterialrequisitionDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mrsno = models.TextField(db_column='MRSNo', blank=True, null=True)  # Field name made lowercase.
    itemid = models.TextField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    deptid = models.IntegerField(db_column='DeptId', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    reqqty = models.FloatField(db_column='ReqQty', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_MaterialRequisition_Details'


class TblinvMaterialrequisitionMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    mrsno = models.TextField(db_column='MRSNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_MaterialRequisition_Master'


class TblinvMaterialreturnDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mrnno = models.TextField(db_column='MRNNo', blank=True, null=True)  # Field name made lowercase.
    itemid = models.TextField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    deptid = models.IntegerField(db_column='DeptId', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    retqty = models.FloatField(db_column='RetQty', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_MaterialReturn_Details'


class TblinvMaterialreturnMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    mrnno = models.TextField(db_column='MRNNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_MaterialReturn_Master'


class TblinvSupplierChallanClear(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    clearedqty = models.FloatField(db_column='ClearedQty', blank=True, null=True)  # Field name made lowercase.
    did = models.ForeignKey('TblinvSupplierChallanDetails', models.DO_NOTHING, db_column='DId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_Supplier_Challan_Clear'


class TblinvSupplierChallanDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    prdid = models.IntegerField(db_column='PRDId', blank=True, null=True)  # Field name made lowercase.
    challanqty = models.FloatField(db_column='ChallanQty', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblinvSupplierChallanMaster', models.DO_NOTHING, db_column='MId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_Supplier_Challan_Details'


class TblinvSupplierChallanMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    scno = models.CharField(db_column='SCNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    supplierid = models.TextField(db_column='SupplierId', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.
    vehicleno = models.TextField(db_column='VehicleNo', blank=True, null=True)  # Field name made lowercase.
    transpoter = models.TextField(db_column='Transpoter', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_Supplier_Challan_Master'


class TblinvWisDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    wisno = models.TextField(db_column='WISNo', blank=True, null=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='PId', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    issuedqty = models.FloatField(db_column='IssuedQty', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblinvWisMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_WIS_Details'


class TblinvWisMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    wisno = models.TextField(db_column='WISNo', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_WIS_Master'


class TblinvWoreleaseWis(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    releasesysdate = models.TextField(db_column='ReleaseSysDate', blank=True, null=True)  # Field name made lowercase.
    releasesystime = models.TextField(db_column='ReleaseSysTime', blank=True, null=True)  # Field name made lowercase.
    releaseby = models.TextField(db_column='ReleaseBy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInv_WORelease_WIS'



class TblvehMasterDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    vehno = models.TextField(db_column='VehNo', blank=True, null=True)  # Field name made lowercase.
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    vehical_name = models.TextField(db_column='Vehical_Name', blank=True, null=True)  # Field name made lowercase.
    contact = models.TextField(db_column='Contact', blank=True, null=True)  # Field name made lowercase.
    destination = models.TextField(db_column='Destination', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    fromkm = models.IntegerField(db_column='FromKM', blank=True, null=True)  # Field name made lowercase.
    fromto = models.IntegerField(db_column='FromTo', blank=True, null=True)  # Field name made lowercase.
    avg = models.IntegerField(db_column='Avg', blank=True, null=True)  # Field name made lowercase.
    fluel_date = models.TextField(db_column='Fluel_Date', blank=True, null=True)  # Field name made lowercase.
    fluel_rs = models.TextField(db_column='Fluel_Rs', blank=True, null=True)  # Field name made lowercase.
    material = models.TextField(db_column='Material', blank=True, null=True)  # Field name made lowercase.
    emp = models.TextField(db_column='Emp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblVeh_Master_Details'


class TblvehProcessMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    vehicalname = models.TextField(db_column='VehicalName', blank=True, null=True)  # Field name made lowercase.
    vehicalno = models.TextField(db_column='VehicalNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblVeh_Process_Master'




class TblGatepass(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    srno = models.IntegerField(db_column='SrNo')  # Field name made lowercase.
    chalanno = models.IntegerField(db_column='ChalanNo')  # Field name made lowercase.
    date = models.TextField(db_column='Date')  # Field name made lowercase.
    wono = models.TextField(db_column='WoNo')  # Field name made lowercase.
    des_name = models.TextField(db_column='Des_Name')  # Field name made lowercase.
    codeno = models.TextField(db_column='CodeNo')  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.
    unit = models.TextField(db_column='Unit')  # Field name made lowercase.
    qty = models.TextField(db_column='Qty')  # Field name made lowercase.
    total_qty = models.TextField(db_column='Total_qty')  # Field name made lowercase.
    issueto = models.TextField(db_column='IssueTo')  # Field name made lowercase.
    athoriseby = models.TextField(db_column='AthoriseBy')  # Field name made lowercase.
    rec_date = models.TextField(db_column='Rec_Date')  # Field name made lowercase.
    qty_recd = models.TextField(db_column='Qty_Recd')  # Field name made lowercase.
    qty_pend = models.TextField(db_column='Qty_pend')  # Field name made lowercase.
    recdby = models.TextField(db_column='RecdBy')  # Field name made lowercase.
    remark = models.TextField(db_column='Remark')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tbl_Gatepass'


class TblStockMonth(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    srno = models.IntegerField(db_column='SrNO')  # Field name made lowercase.
    item_code = models.TextField(db_column='Item_code')  # Field name made lowercase.
    group = models.TextField(db_column='Group')  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.
    unit = models.TextField(db_column='Unit')  # Field name made lowercase.
    qty_month = models.TextField(db_column='Qty_month')  # Field name made lowercase.
    reorder = models.TextField(db_column='ReOrder')  # Field name made lowercase.
    min_order = models.TextField(db_column='Min_order')  # Field name made lowercase.
    day = models.TextField(db_column='Day')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tbl_Stock_Month'


class TblinvAutowisTimeschedule(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    timeauto = models.TextField(db_column='TimeAuto', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    timetoorder = models.DateTimeField(db_column='TimeToOrder', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblinv_AutoWIS_TimeSchedule'


class TblinvMaterialreceivedDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    grrno = models.TextField(db_column='GRRNo', blank=True, null=True)  # Field name made lowercase.
    poid = models.IntegerField(db_column='POId', blank=True, null=True)  # Field name made lowercase.
    receivedqty = models.FloatField(db_column='ReceivedQty', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblinv_MaterialReceived_Details'


class TblinvMaterialreceivedMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    grrno = models.TextField(db_column='GRRNo', blank=True, null=True)  # Field name made lowercase.
    ginno = models.TextField(db_column='GINNo', blank=True, null=True)  # Field name made lowercase.
    ginid = models.IntegerField(db_column='GINId', blank=True, null=True)  # Field name made lowercase.
    taxinvoiceno = models.TextField(db_column='TaxInvoiceNo', blank=True, null=True)  # Field name made lowercase.
    taxinvoicedate = models.TextField(db_column='TaxInvoiceDate', blank=True, null=True)  # Field name made lowercase.
    modvatapp = models.IntegerField(db_column='ModVatApp', blank=True, null=True)  # Field name made lowercase.
    modvatinv = models.IntegerField(db_column='ModVatInv', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblinv_MaterialReceived_Master'


class TblinvMaterialservicenoteDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    gsnno = models.TextField(db_column='GSNNo', blank=True, null=True)  # Field name made lowercase.
    poid = models.IntegerField(db_column='POId', blank=True, null=True)  # Field name made lowercase.
    receivedqty = models.FloatField(db_column='ReceivedQty', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblinv_MaterialServiceNote_Details'


class TblinvMaterialservicenoteMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    gsnno = models.TextField(db_column='GSNNo', blank=True, null=True)  # Field name made lowercase.
    ginid = models.IntegerField(db_column='GINId', blank=True, null=True)  # Field name made lowercase.
    ginno = models.TextField(db_column='GINNo', blank=True, null=True)  # Field name made lowercase.
    taxinvoiceno = models.TextField(db_column='TaxInvoiceNo', blank=True, null=True)  # Field name made lowercase.
    taxinvoicedate = models.TextField(db_column='TaxInvoiceDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblinv_MaterialServiceNote_Master'

