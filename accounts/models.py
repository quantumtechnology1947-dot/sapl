from django.db import models

# Create your models here.

class Acchead(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=50, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50, blank=True, null=True)  # Field name made lowercase.
    symbol = models.CharField(db_column='Symbol', max_length=50, blank=True, null=True)  # Field name made lowercase.
    abbrivation = models.CharField(db_column='Abbrivation', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AccHead'



class CategoryMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Category_Master'


class Challan(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    customername = models.TextField(db_column='CustomerName', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    gst = models.TextField(db_column='GST', blank=True, null=True)  # Field name made lowercase.
    dcno = models.TextField(db_column='DCNo', blank=True, null=True)  # Field name made lowercase.
    dcdate = models.TextField(db_column='DCDate', blank=True, null=True)  # Field name made lowercase.
    attention = models.TextField(db_column='Attention', blank=True, null=True)  # Field name made lowercase.
    contact = models.TextField(db_column='Contact', blank=True, null=True)  # Field name made lowercase.
    responsible_by = models.TextField(db_column='Responsible_By', blank=True, null=True)  # Field name made lowercase.
    type = models.TextField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    hsn = models.TextField(db_column='HSN', blank=True, null=True)  # Field name made lowercase.
    quantity = models.TextField(db_column='Quantity', blank=True, null=True)  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    tqty = models.FloatField(db_column='TQty', blank=True, null=True)  # Field name made lowercase.
    tamt = models.FloatField(db_column='TAmt', blank=True, null=True)  # Field name made lowercase.
    gst_per = models.FloatField(db_column='Gst_per', blank=True, null=True)  # Field name made lowercase.
    gtotal = models.FloatField(db_column='GTotal', blank=True, null=True)  # Field name made lowercase.
    remark = models.TextField(db_column='Remark', blank=True, null=True)  # Field name made lowercase.
    transport = models.TextField(db_column='Transport', blank=True, null=True)  # Field name made lowercase.
    vehicleno = models.TextField(db_column='vehicleNo', blank=True, null=True)  # Field name made lowercase.
    lrno = models.TextField(db_column='LRNo', blank=True, null=True)  # Field name made lowercase.
    acknowledgement = models.TextField(db_column='Acknowledgement', blank=True, null=True)  # Field name made lowercase.
    uom = models.TextField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    grandtotal = models.FloatField(db_column='GrandTotal', blank=True, null=True)  # Field name made lowercase.
    gstwords = models.TextField(db_column='GSTWORDS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Challan'


class ChallanDetails(models.Model):
    no = models.AutoField(db_column='No', primary_key=True)  # Field name made lowercase.
    dcno = models.TextField(db_column='DCNo', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    hsn = models.TextField(db_column='HSN', blank=True, null=True)  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity', blank=True, null=True)  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    uom = models.TextField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Challan_Details'


class ChallanMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    customername = models.TextField(db_column='CustomerName', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    gst = models.TextField(db_column='GST', blank=True, null=True)  # Field name made lowercase.
    dcno = models.TextField(db_column='DCNo', blank=True, null=True)  # Field name made lowercase.
    dcdate = models.TextField(db_column='DCDate', blank=True, null=True)  # Field name made lowercase.
    attention = models.TextField(db_column='Attention', blank=True, null=True)  # Field name made lowercase.
    contact = models.TextField(db_column='Contact', blank=True, null=True)  # Field name made lowercase.
    responsible_by = models.TextField(db_column='Responsible_By', blank=True, null=True)  # Field name made lowercase.
    type = models.TextField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    tqty = models.FloatField(db_column='TQty', blank=True, null=True)  # Field name made lowercase.
    tamt = models.FloatField(db_column='TAmt', blank=True, null=True)  # Field name made lowercase.
    gst_per = models.FloatField(db_column='Gst_per', blank=True, null=True)  # Field name made lowercase.
    gtotal = models.FloatField(db_column='GTotal', blank=True, null=True)  # Field name made lowercase.
    remark = models.TextField(db_column='Remark', blank=True, null=True)  # Field name made lowercase.
    transport = models.TextField(db_column='Transport', blank=True, null=True)  # Field name made lowercase.
    vehicleno = models.TextField(db_column='vehicleNo', blank=True, null=True)  # Field name made lowercase.
    lrno = models.TextField(db_column='LRNo', blank=True, null=True)  # Field name made lowercase.
    acknowledgement = models.TextField(db_column='Acknowledgement', blank=True, null=True)  # Field name made lowercase.
    uom = models.TextField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    grandtotal = models.FloatField(db_column='GrandTotal', blank=True, null=True)  # Field name made lowercase.
    gstwords = models.TextField(db_column='GSTWORDS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Challan_Master'



class TblaccAdvicePaymentDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    proformainvno = models.TextField(db_column='ProformaInvNo', blank=True, null=True)  # Field name made lowercase.
    invdate = models.TextField(db_column='InvDate', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    particular = models.TextField(db_column='Particular', blank=True, null=True)  # Field name made lowercase.
    withingroup = models.TextField(db_column='WithinGroup', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    bg = models.IntegerField(db_column='BG', blank=True, null=True)  # Field name made lowercase.
    pvevno = models.IntegerField(db_column='PVEVNO', blank=True, null=True)  # Field name made lowercase.
    billagainst = models.TextField(db_column='BillAgainst', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblaccAdvicePaymentMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Advice_Payment_Details'


class TblaccAdvicePaymentMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    adno = models.TextField(db_column='ADNo')  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    type = models.IntegerField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    ecstype = models.IntegerField(db_column='ECSType', blank=True, null=True)  # Field name made lowercase.
    payto = models.TextField(db_column='PayTo', blank=True, null=True)  # Field name made lowercase.
    chequeno = models.TextField(db_column='ChequeNo', blank=True, null=True)  # Field name made lowercase.
    chequedate = models.TextField(db_column='ChequeDate', blank=True, null=True)  # Field name made lowercase.
    payat = models.TextField(db_column='PayAt', blank=True, null=True)  # Field name made lowercase.
    bank = models.IntegerField(db_column='Bank', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Advice_Payment_Master'


class TblaccAsset(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    category = models.TextField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    abbrivation = models.CharField(db_column='Abbrivation', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Asset'


class TblaccAssetCategory(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    category = models.TextField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    abbrivation = models.CharField(db_column='Abbrivation', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Asset_Category'


class TblaccAssetRegister(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    did = models.IntegerField(db_column='DId', blank=True, null=True)  # Field name made lowercase.
    acategoyid = models.IntegerField(db_column='ACategoyId', blank=True, null=True)  # Field name made lowercase.
    asubcategoyid = models.IntegerField(db_column='ASubCategoyId', blank=True, null=True)  # Field name made lowercase.
    assetno = models.CharField(db_column='AssetNo', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Asset_Register'


class TblaccAssetSubcategory(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    subcategory = models.TextField(db_column='SubCategory', blank=True, null=True)  # Field name made lowercase.
    abbrivation = models.CharField(db_column='Abbrivation', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey(TblaccAssetCategory, models.DO_NOTHING, db_column='MId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Asset_SubCategory'


class TblaccBank(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    ordno = models.IntegerField(db_column='OrdNo', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    country = models.IntegerField(db_column='Country', blank=True, null=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State', blank=True, null=True)  # Field name made lowercase.
    city = models.IntegerField(db_column='City', blank=True, null=True)  # Field name made lowercase.
    pinno = models.TextField(db_column='PINNo', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    faxno = models.TextField(db_column='FaxNo', blank=True, null=True)  # Field name made lowercase.
    ifsc = models.TextField(db_column='IFSC', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Bank'


class TblaccBank1(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    ordno = models.IntegerField(db_column='OrdNo', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    country = models.IntegerField(db_column='Country', blank=True, null=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State', blank=True, null=True)  # Field name made lowercase.
    city = models.IntegerField(db_column='City', blank=True, null=True)  # Field name made lowercase.
    pinno = models.TextField(db_column='PINNo', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    faxno = models.TextField(db_column='FaxNo', blank=True, null=True)  # Field name made lowercase.
    ifsc = models.TextField(db_column='IFSC', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Bank1'


class TblaccBankamtMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    amt = models.FloatField(db_column='Amt', blank=True, null=True)  # Field name made lowercase.
    bankid = models.IntegerField(db_column='BankId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BankAmt_Master'


class TblaccBankrecanciliation(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    bvpid = models.IntegerField(db_column='BVPId', blank=True, null=True)  # Field name made lowercase.
    bvrid = models.IntegerField(db_column='BVRId', blank=True, null=True)  # Field name made lowercase.
    bankdate = models.TextField(db_column='BankDate', blank=True, null=True)  # Field name made lowercase.
    addcharges = models.FloatField(db_column='AddCharges', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BankRecanciliation'


class TblaccBankreceivedMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    bank = models.TextField(db_column='Bank', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BankReceived_Master'


class TblaccBankvoucherPaymentDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    proformainvno = models.TextField(db_column='ProformaInvNo', blank=True, null=True)  # Field name made lowercase.
    invdate = models.TextField(db_column='InvDate', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    particular = models.TextField(db_column='Particular', blank=True, null=True)  # Field name made lowercase.
    withingroup = models.TextField(db_column='WithinGroup', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    bg = models.IntegerField(db_column='BG', blank=True, null=True)  # Field name made lowercase.
    pvevno = models.IntegerField(db_column='PVEVNO', blank=True, null=True)  # Field name made lowercase.
    billagainst = models.TextField(db_column='BillAgainst', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblaccBankvoucherPaymentMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BankVoucher_Payment_Details'


class TblaccBankvoucherPaymentMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    bvpno = models.TextField(db_column='BVPNo')  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    type = models.IntegerField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    ecstype = models.IntegerField(db_column='ECSType', blank=True, null=True)  # Field name made lowercase.
    payto = models.TextField(db_column='PayTo', blank=True, null=True)  # Field name made lowercase.
    chequeno = models.TextField(db_column='ChequeNo', blank=True, null=True)  # Field name made lowercase.
    chequedate = models.TextField(db_column='ChequeDate', blank=True, null=True)  # Field name made lowercase.
    bank = models.IntegerField(db_column='Bank', blank=True, null=True)  # Field name made lowercase.
    payat = models.TextField(db_column='PayAt', blank=True, null=True)  # Field name made lowercase.
    payatcountry = models.IntegerField(db_column='PayAtCountry', blank=True, null=True)  # Field name made lowercase.
    payatstate = models.IntegerField(db_column='PayAtState', blank=True, null=True)  # Field name made lowercase.
    payatcity = models.IntegerField(db_column='PayAtCity', blank=True, null=True)  # Field name made lowercase.
    payamt = models.FloatField(db_column='PayAmt', blank=True, null=True)  # Field name made lowercase.
    addamt = models.FloatField(db_column='AddAmt', blank=True, null=True)  # Field name made lowercase.
    transactiontype = models.IntegerField(db_column='TransactionType', blank=True, null=True)  # Field name made lowercase.
    paidtype = models.TextField(db_column='PaidType', blank=True, null=True)  # Field name made lowercase.
    nameoncheque = models.TextField(db_column='NameOnCheque', blank=True, null=True)  # Field name made lowercase.
    loantype = models.IntegerField(db_column='LoanType', blank=True, null=True)  # Field name made lowercase.
    intresttype = models.IntegerField(db_column='IntrestType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BankVoucher_Payment_Master'


class TblaccBankvoucherReceivedMasters(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    bvrno = models.TextField(db_column='BVRNo', blank=True, null=True)  # Field name made lowercase.
    types = models.IntegerField(db_column='Types', blank=True, null=True)  # Field name made lowercase.
    receivetype = models.IntegerField(db_column='ReceiveType', blank=True, null=True)  # Field name made lowercase.
    receivedfrom = models.TextField(db_column='ReceivedFrom', blank=True, null=True)  # Field name made lowercase.
    invoiceno = models.TextField(db_column='InvoiceNo', blank=True, null=True)  # Field name made lowercase.
    chequeno = models.TextField(db_column='ChequeNo', blank=True, null=True)  # Field name made lowercase.
    chequedate = models.TextField(db_column='ChequeDate', blank=True, null=True)  # Field name made lowercase.
    chequereceivedby = models.TextField(db_column='ChequeReceivedBy', blank=True, null=True)  # Field name made lowercase.
    bankname = models.TextField(db_column='BankName', blank=True, null=True)  # Field name made lowercase.
    bankaccno = models.TextField(db_column='BankAccNo', blank=True, null=True)  # Field name made lowercase.
    chequeclearancedate = models.TextField(db_column='ChequeClearanceDate', blank=True, null=True)  # Field name made lowercase.
    narration = models.TextField(db_column='Narration', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    drawnat = models.IntegerField(db_column='DrawnAt', blank=True, null=True)  # Field name made lowercase.
    transactiontype = models.IntegerField(db_column='TransactionType', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    bggroup = models.IntegerField(db_column='BGGroup', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BankVoucher_Received_Masters'


class TblaccBillbookingAttachMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    filename = models.TextField(db_column='FileName', blank=True, null=True)  # Field name made lowercase.
    filesize = models.FloatField(db_column='FileSize', blank=True, null=True)  # Field name made lowercase.
    contenttype = models.TextField(db_column='ContentType', blank=True, null=True)  # Field name made lowercase.
    filedata = models.BinaryField(db_column='FileData', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BillBooking_Attach_Master'


class TblaccBillbookingDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    podid = models.IntegerField(db_column='PODId')  # Field name made lowercase.
    gqnid = models.IntegerField(db_column='GQNId')  # Field name made lowercase.
    gsnid = models.IntegerField(db_column='GSNId')  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId')  # Field name made lowercase.
    debittype = models.IntegerField(db_column='DebitType', blank=True, null=True)  # Field name made lowercase.
    debitvalue = models.FloatField(db_column='DebitValue', blank=True, null=True)  # Field name made lowercase.
    pfamt = models.FloatField(db_column='PFAmt', blank=True, null=True)  # Field name made lowercase.
    exstbasicinper = models.FloatField(db_column='ExStBasicInPer', blank=True, null=True)  # Field name made lowercase.
    exsteducessinper = models.FloatField(db_column='ExStEducessInPer', blank=True, null=True)  # Field name made lowercase.
    exstshecessinper = models.FloatField(db_column='ExStShecessInPer', blank=True, null=True)  # Field name made lowercase.
    exstbasic = models.FloatField(db_column='ExStBasic', blank=True, null=True)  # Field name made lowercase.
    exsteducess = models.FloatField(db_column='ExStEducess', blank=True, null=True)  # Field name made lowercase.
    exstshecess = models.FloatField(db_column='ExStShecess', blank=True, null=True)  # Field name made lowercase.
    customduty = models.FloatField(db_column='CustomDuty', blank=True, null=True)  # Field name made lowercase.
    vat = models.FloatField(db_column='VAT', blank=True, null=True)  # Field name made lowercase.
    cst = models.FloatField(db_column='CST', blank=True, null=True)  # Field name made lowercase.
    freight = models.FloatField(db_column='Freight', blank=True, null=True)  # Field name made lowercase.
    tarrifno = models.TextField(db_column='TarrifNo', blank=True, null=True)  # Field name made lowercase.
    bcdopt = models.IntegerField(db_column='BCDOpt', blank=True, null=True)  # Field name made lowercase.
    bcd = models.FloatField(db_column='BCD', blank=True, null=True)  # Field name made lowercase.
    bcdvalue = models.FloatField(db_column='BCDValue', blank=True, null=True)  # Field name made lowercase.
    valueforcvd = models.FloatField(db_column='ValueForCVD', blank=True, null=True)  # Field name made lowercase.
    valueforedcesscd = models.FloatField(db_column='ValueForEdCessCD', blank=True, null=True)  # Field name made lowercase.
    edcessoncdopt = models.IntegerField(db_column='EdCessOnCDOpt', blank=True, null=True)  # Field name made lowercase.
    edcessoncd = models.FloatField(db_column='EdCessOnCD', blank=True, null=True)  # Field name made lowercase.
    edcessoncdvalue = models.FloatField(db_column='EdCessOnCDValue', blank=True, null=True)  # Field name made lowercase.
    shedcessopt = models.IntegerField(db_column='SHEDCessOpt', blank=True, null=True)  # Field name made lowercase.
    shedcess = models.FloatField(db_column='SHEDCess', blank=True, null=True)  # Field name made lowercase.
    shedcessvalue = models.FloatField(db_column='SHEDCessValue', blank=True, null=True)  # Field name made lowercase.
    totduty = models.FloatField(db_column='TotDuty', blank=True, null=True)  # Field name made lowercase.
    totdutyedshed = models.FloatField(db_column='TotDutyEDSHED', blank=True, null=True)  # Field name made lowercase.
    insurance = models.FloatField(db_column='Insurance', blank=True, null=True)  # Field name made lowercase.
    valuewithduty = models.FloatField(db_column='ValueWithDuty', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblaccBillbookingMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BillBooking_Details'


class TblaccBillbookingMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    pvevno = models.TextField(db_column='PVEVNo', blank=True, null=True)  # Field name made lowercase.
    supplierid = models.TextField(db_column='SupplierId', blank=True, null=True)  # Field name made lowercase.
    poid = models.IntegerField(db_column='POId', blank=True, null=True)  # Field name made lowercase.
    billno = models.TextField(db_column='BillNo', blank=True, null=True)  # Field name made lowercase.
    billdate = models.TextField(db_column='BillDate', blank=True, null=True)  # Field name made lowercase.
    cenvatentryno = models.TextField(db_column='CENVATEntryNo', blank=True, null=True)  # Field name made lowercase.
    cenvatentrydate = models.TextField(db_column='CENVATEntryDate', blank=True, null=True)  # Field name made lowercase.
    othercharges = models.FloatField(db_column='OtherCharges', blank=True, null=True)  # Field name made lowercase.
    otherchadesc = models.TextField(db_column='OtherChaDesc', blank=True, null=True)  # Field name made lowercase.
    narration = models.TextField(db_column='Narration', blank=True, null=True)  # Field name made lowercase.
    debitamt = models.FloatField(db_column='DebitAmt', blank=True, null=True)  # Field name made lowercase.
    discounttype = models.IntegerField(db_column='DiscountType', blank=True, null=True)  # Field name made lowercase.
    discount = models.FloatField(db_column='Discount', blank=True, null=True)  # Field name made lowercase.
    authorize = models.IntegerField(db_column='Authorize', blank=True, null=True)  # Field name made lowercase.
    authorizeby = models.TextField(db_column='AuthorizeBy', blank=True, null=True)  # Field name made lowercase.
    authorizedate = models.TextField(db_column='AuthorizeDate', blank=True, null=True)  # Field name made lowercase.
    authorizetime = models.TextField(db_column='AuthorizeTime', blank=True, null=True)  # Field name made lowercase.
    invoicetype = models.IntegerField(db_column='InvoiceType', blank=True, null=True)  # Field name made lowercase.
    ahid = models.IntegerField(db_column='AHId')  # Field name made lowercase.
    tdscode = models.IntegerField(db_column='TDSCode', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_BillBooking_Master'


class TblaccBudgetDept(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    deptid = models.IntegerField(db_column='DeptId', blank=True, null=True)  # Field name made lowercase.
    accid = models.IntegerField(db_column='AccId', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    bgid = models.IntegerField(db_column='BGId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Budget_Dept'


class TblaccBudgetDept1(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    deptid = models.IntegerField(db_column='DeptId', blank=True, null=True)  # Field name made lowercase.
    accid = models.IntegerField(db_column='AccId', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    bgid = models.IntegerField(db_column='BGId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Budget_Dept1'


class TblaccBudgetDeptTime(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    bggroup = models.IntegerField(db_column='BGGroup', blank=True, null=True)  # Field name made lowercase.
    budgetcodeid = models.IntegerField(db_column='BudgetCodeId', blank=True, null=True)  # Field name made lowercase.
    hour = models.FloatField(db_column='Hour', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Budget_Dept_Time'


class TblaccBudgetWo(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    accid = models.IntegerField(db_column='AccId', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    budgetcodeid = models.IntegerField(db_column='BudgetCodeId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Budget_WO'


class TblaccBudgetWoTime(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    equipid = models.IntegerField(db_column='EquipId', blank=True, null=True)  # Field name made lowercase.
    hrsbudgetcat = models.IntegerField(db_column='HrsBudgetCat', blank=True, null=True)  # Field name made lowercase.
    hrsbudgetsubcat = models.IntegerField(db_column='HrsBudgetSubCat', blank=True, null=True)  # Field name made lowercase.
    hour = models.FloatField(db_column='Hour', blank=True, null=True)  # Field name made lowercase.
    budgetamthrs = models.FloatField(db_column='BudgetAmtHrs', blank=True, null=True)  # Field name made lowercase.
    budgetcodeid = models.IntegerField(db_column='BudgetCodeId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Budget_WO_Time'


class TblaccCapitalDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    particulars = models.TextField(db_column='Particulars', blank=True, null=True)  # Field name made lowercase.
    creditamt = models.FloatField(db_column='CreditAmt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Capital_Details'


class TblaccCapitalMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    particulars = models.TextField(db_column='Particulars', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Capital_Master'


class TblaccCashamtlimit(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    active = models.IntegerField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_CashAmtLimit'


class TblaccCashamtMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    amt = models.FloatField(db_column='Amt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_CashAmt_Master'


class TblaccCashvoucherPaymentDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    billno = models.TextField(db_column='BillNo', blank=True, null=True)  # Field name made lowercase.
    billdate = models.TextField(db_column='BillDate', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    podate = models.TextField(db_column='PODate', blank=True, null=True)  # Field name made lowercase.
    particulars = models.TextField(db_column='Particulars', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    bggroup = models.IntegerField(db_column='BGGroup', blank=True, null=True)  # Field name made lowercase.
    achead = models.IntegerField(db_column='AcHead', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    budgetcode = models.IntegerField(db_column='BudgetCode', blank=True, null=True)  # Field name made lowercase.
    pvevno = models.TextField(db_column='PVEVNo', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblaccCashvoucherPaymentMaster', models.DO_NOTHING, db_column='MId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_CashVoucher_Payment_Details'


class TblaccCashvoucherPaymentDetails2(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    billno = models.TextField(db_column='BillNo', blank=True, null=True)  # Field name made lowercase.
    billdate = models.TextField(db_column='BillDate', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    podate = models.TextField(db_column='PODate', blank=True, null=True)  # Field name made lowercase.
    particulars = models.TextField(db_column='Particulars', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    bggroup = models.IntegerField(db_column='BGGroup', blank=True, null=True)  # Field name made lowercase.
    achead = models.IntegerField(db_column='AcHead', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    budgetcode = models.IntegerField(db_column='BudgetCode', blank=True, null=True)  # Field name made lowercase.
    pvevno = models.TextField(db_column='PVEVNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_CashVoucher_Payment_Details2'


class TblaccCashvoucherPaymentMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    cvpno = models.TextField(db_column='CVPNo', blank=True, null=True)  # Field name made lowercase.
    paidto = models.TextField(db_column='PaidTo', blank=True, null=True)  # Field name made lowercase.
    receivedby = models.TextField(db_column='ReceivedBy', blank=True, null=True)  # Field name made lowercase.
    codetype = models.IntegerField(db_column='CodeType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_CashVoucher_Payment_Master'


class TblaccCashvoucherPaymentMaster2(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    cvpno = models.TextField(db_column='CVPNo', blank=True, null=True)  # Field name made lowercase.
    paidto = models.TextField(db_column='PaidTo', blank=True, null=True)  # Field name made lowercase.
    receivedby = models.TextField(db_column='ReceivedBy', blank=True, null=True)  # Field name made lowercase.
    codetype = models.IntegerField(db_column='CodeType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_CashVoucher_Payment_Master2'


class TblaccCashvoucherReceiptMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    cvrno = models.TextField(db_column='CVRNo', blank=True, null=True)  # Field name made lowercase.
    cashreceivedagainst = models.TextField(db_column='CashReceivedAgainst', blank=True, null=True)  # Field name made lowercase.
    cashreceivedby = models.TextField(db_column='CashReceivedBy', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    bggroup = models.IntegerField(db_column='BGGroup', blank=True, null=True)  # Field name made lowercase.
    achead = models.IntegerField(db_column='AcHead', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    others = models.TextField(db_column='Others', blank=True, null=True)  # Field name made lowercase.
    codetypera = models.IntegerField(db_column='CodeTypeRA', blank=True, null=True)  # Field name made lowercase.
    codetyperb = models.IntegerField(db_column='CodeTypeRB', blank=True, null=True)  # Field name made lowercase.
    budgetcode = models.IntegerField(db_column='BudgetCode')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_CashVoucher_Receipt_Master'


class TblaccContraEntry(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    date = models.CharField(db_column='Date', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cr = models.IntegerField(db_column='Cr', blank=True, null=True)  # Field name made lowercase.
    dr = models.IntegerField(db_column='Dr', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    narration = models.TextField(db_column='Narration', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Contra_Entry'


class TblaccCreditorsMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    supplierid = models.TextField(db_column='SupplierId', blank=True, null=True)  # Field name made lowercase.
    openingamt = models.FloatField(db_column='OpeningAmt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Creditors_Master'


class TblaccCurrencyMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    country = models.IntegerField(db_column='Country', blank=True, null=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Currency_Master'


class TblaccDebitnote(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    debitno = models.TextField(db_column='DebitNo', blank=True, null=True)  # Field name made lowercase.
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    sce = models.TextField(db_column='SCE', blank=True, null=True)  # Field name made lowercase.
    refrence = models.TextField(db_column='Refrence', blank=True, null=True)  # Field name made lowercase.
    particulars = models.TextField(db_column='Particulars', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    types = models.IntegerField(db_column='Types', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_DebitNote'


class TblaccDebittype(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_DebitType'


class TblaccDebitorsMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    customerid = models.TextField(db_column='CustomerId', blank=True, null=True)  # Field name made lowercase.
    openingamt = models.FloatField(db_column='OpeningAmt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Debitors_Master'


class TblaccIouMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.
    paymentdate = models.TextField(db_column='PaymentDate', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    reason = models.IntegerField(db_column='Reason', blank=True, null=True)  # Field name made lowercase.
    narration = models.TextField(db_column='Narration', blank=True, null=True)  # Field name made lowercase.
    authorize = models.IntegerField(db_column='Authorize')  # Field name made lowercase.
    authorizeddate = models.TextField(db_column='AuthorizedDate', blank=True, null=True)  # Field name made lowercase.
    authorizedby = models.TextField(db_column='AuthorizedBy', blank=True, null=True)  # Field name made lowercase.
    authorizedtime = models.TextField(db_column='AuthorizedTime', blank=True, null=True)  # Field name made lowercase.
    recieved = models.IntegerField(db_column='Recieved', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_IOU_Master'


class TblaccIouReasons(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_IOU_Reasons'


class TblaccIntresttype(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_IntrestType'


class TblaccInvoiceagainst(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    against = models.TextField(db_column='Against', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_InvoiceAgainst'


class TblaccLoantype(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_LoanType'


class TblaccPaidtype(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    particulars = models.TextField(db_column='Particulars', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_PaidType'


class TblaccPaymentmode(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_PaymentMode'


class TblaccProformainvoiceDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    invoiceno = models.TextField(db_column='InvoiceNo')  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId')  # Field name made lowercase.
    reqqty = models.FloatField(db_column='ReqQty')  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    amtinper = models.FloatField(db_column='AmtInPer')  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate')  # Field name made lowercase.
    mid = models.ForeignKey('TblaccProformainvoiceMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.
    unit = models.IntegerField(db_column='Unit', blank=True, null=True)  # Changed from FK to IntegerField

    class Meta:
        managed = False
        db_table = 'tblACC_ProformaInvoice_Details'


class TblaccProformainvoiceMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    invoiceno = models.TextField(db_column='InvoiceNo', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    invoicemode = models.TextField(db_column='InvoiceMode', blank=True, null=True)  # Field name made lowercase.
    dateofissueinvoice = models.TextField(db_column='DateOfIssueInvoice', blank=True, null=True)  # Field name made lowercase.
    timeofissueinvoice = models.TextField(db_column='TimeOfIssueInvoice', blank=True, null=True)  # Field name made lowercase.
    customercode = models.TextField(db_column='CustomerCode', blank=True, null=True)  # Field name made lowercase.
    buyer_name = models.TextField(db_column='Buyer_name', blank=True, null=True)  # Field name made lowercase.
    buyer_add = models.TextField(db_column='Buyer_add', blank=True, null=True)  # Field name made lowercase.
    buyer_state = models.IntegerField(db_column='Buyer_state', blank=True, null=True)  # Field name made lowercase.
    buyer_country = models.IntegerField(db_column='Buyer_country', blank=True, null=True)  # Field name made lowercase.
    buyer_cotper = models.TextField(db_column='Buyer_cotper', blank=True, null=True)  # Field name made lowercase.
    buyer_ph = models.TextField(db_column='Buyer_ph', blank=True, null=True)  # Field name made lowercase.
    buyer_email = models.TextField(db_column='Buyer_email', blank=True, null=True)  # Field name made lowercase.
    buyer_ecc = models.TextField(db_column='Buyer_ecc', blank=True, null=True)  # Field name made lowercase.
    buyer_tin = models.TextField(db_column='Buyer_tin', blank=True, null=True)  # Field name made lowercase.
    buyer_mob = models.TextField(db_column='Buyer_mob', blank=True, null=True)  # Field name made lowercase.
    buyer_fax = models.TextField(db_column='Buyer_fax', blank=True, null=True)  # Field name made lowercase.
    buyer_vat = models.TextField(db_column='Buyer_vat', blank=True, null=True)  # Field name made lowercase.
    cong_name = models.TextField(db_column='Cong_name', blank=True, null=True)  # Field name made lowercase.
    cong_add = models.TextField(db_column='Cong_add', blank=True, null=True)  # Field name made lowercase.
    cong_state = models.IntegerField(db_column='Cong_state', blank=True, null=True)  # Field name made lowercase.
    cong_country = models.IntegerField(db_column='Cong_country', blank=True, null=True)  # Field name made lowercase.
    cong_cotper = models.TextField(db_column='Cong_cotper', blank=True, null=True)  # Field name made lowercase.
    cong_ph = models.TextField(db_column='Cong_ph', blank=True, null=True)  # Field name made lowercase.
    cong_email = models.TextField(db_column='Cong_email')  # Field name made lowercase.
    cong_ecc = models.TextField(db_column='Cong_ecc')  # Field name made lowercase.
    cong_tin = models.TextField(db_column='Cong_tin', blank=True, null=True)  # Field name made lowercase.
    cong_mob = models.TextField(db_column='Cong_mob', blank=True, null=True)  # Field name made lowercase.
    cong_fax = models.TextField(db_column='Cong_fax', blank=True, null=True)  # Field name made lowercase.
    cong_vat = models.TextField(db_column='Cong_vat', blank=True, null=True)  # Field name made lowercase.
    addtype = models.IntegerField(db_column='AddType', blank=True, null=True)  # Field name made lowercase.
    addamt = models.FloatField(db_column='AddAmt', blank=True, null=True)  # Field name made lowercase.
    deductiontype = models.IntegerField(db_column='DeductionType', blank=True, null=True)  # Field name made lowercase.
    deduction = models.FloatField(db_column='Deduction', blank=True, null=True)  # Field name made lowercase.
    poid = models.IntegerField(db_column='POId', blank=True, null=True)  # Field name made lowercase.
    buyer_city = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='Buyer_city', blank=True, null=True)  # Field name made lowercase.
    cong_city = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='Cong_city', related_name='tblaccproformainvoicemaster_cong_city_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_ProformaInvoice_Master'


class TblaccReceiptagainst(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_ReceiptAgainst'


class TblaccRemovableNature(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Removable_Nature'


class TblaccSalesinvoiceDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    invoiceno = models.TextField(db_column='InvoiceNo')  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId')  # Field name made lowercase.
    reqqty = models.FloatField(db_column='ReqQty')  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    amtinper = models.FloatField(db_column='AmtInPer')  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate')  # Field name made lowercase.
    mid = models.ForeignKey('TblaccSalesinvoiceMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.
    unit = models.IntegerField(db_column='Unit', blank=True, null=True)  # Changed from FK to IntegerField

    class Meta:
        managed = False
        db_table = 'tblACC_SalesInvoice_Details'


class TblaccSalesinvoiceMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    invoiceno = models.TextField(db_column='InvoiceNo', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    invoicemode = models.TextField(db_column='InvoiceMode', blank=True, null=True)  # Field name made lowercase.
    dateofissueinvoice = models.TextField(db_column='DateOfIssueInvoice', blank=True, null=True)  # Field name made lowercase.
    dateofremoval = models.CharField(db_column='DateOfRemoval', max_length=50, blank=True, null=True)  # Field name made lowercase.
    timeofissueinvoice = models.TextField(db_column='TimeOfIssueInvoice')  # Field name made lowercase.
    timeofremoval = models.CharField(db_column='TimeOfRemoval', max_length=50, blank=True, null=True)  # Field name made lowercase.
    natureofremoval = models.IntegerField(db_column='NatureOfRemoval', blank=True, null=True)  # Field name made lowercase.
    commodity = models.IntegerField(db_column='Commodity', blank=True, null=True)  # Field name made lowercase.
    tariffheading = models.TextField(db_column='TariffHeading', blank=True, null=True)  # Field name made lowercase.
    modeoftransport = models.IntegerField(db_column='ModeOfTransport', blank=True, null=True)  # Field name made lowercase.
    rrgcno = models.TextField(db_column='RRGCNo', blank=True, null=True)  # Field name made lowercase.
    vehiregno = models.TextField(db_column='VehiRegNo', blank=True, null=True)  # Field name made lowercase.
    dutyrate = models.TextField(db_column='DutyRate', blank=True, null=True)  # Field name made lowercase.
    customercode = models.TextField(db_column='CustomerCode')  # Field name made lowercase.
    customercategory = models.IntegerField(db_column='CustomerCategory', blank=True, null=True)  # Field name made lowercase.
    buyer_name = models.TextField(db_column='Buyer_name', blank=True, null=True)  # Field name made lowercase.
    buyer_add = models.TextField(db_column='Buyer_add', blank=True, null=True)  # Field name made lowercase.
    buyer_state = models.IntegerField(db_column='Buyer_state', blank=True, null=True)  # Field name made lowercase.
    buyer_country = models.IntegerField(db_column='Buyer_country', blank=True, null=True)  # Field name made lowercase.
    buyer_cotper = models.TextField(db_column='Buyer_cotper', blank=True, null=True)  # Field name made lowercase.
    buyer_ph = models.TextField(db_column='Buyer_ph', blank=True, null=True)  # Field name made lowercase.
    buyer_email = models.TextField(db_column='Buyer_email', blank=True, null=True)  # Field name made lowercase.
    buyer_ecc = models.TextField(db_column='Buyer_ecc', blank=True, null=True)  # Field name made lowercase.
    buyer_tin = models.TextField(db_column='Buyer_tin', blank=True, null=True)  # Field name made lowercase.
    buyer_mob = models.TextField(db_column='Buyer_mob', blank=True, null=True)  # Field name made lowercase.
    buyer_fax = models.TextField(db_column='Buyer_fax', blank=True, null=True)  # Field name made lowercase.
    buyer_vat = models.TextField(db_column='Buyer_vat', blank=True, null=True)  # Field name made lowercase.
    cong_name = models.TextField(db_column='Cong_name', blank=True, null=True)  # Field name made lowercase.
    cong_add = models.TextField(db_column='Cong_add', blank=True, null=True)  # Field name made lowercase.
    cong_state = models.IntegerField(db_column='Cong_state', blank=True, null=True)  # Field name made lowercase.
    cong_country = models.IntegerField(db_column='Cong_country', blank=True, null=True)  # Field name made lowercase.
    cong_cotper = models.TextField(db_column='Cong_cotper', blank=True, null=True)  # Field name made lowercase.
    cong_ph = models.TextField(db_column='Cong_ph', blank=True, null=True)  # Field name made lowercase.
    cong_email = models.TextField(db_column='Cong_email')  # Field name made lowercase.
    cong_ecc = models.TextField(db_column='Cong_ecc')  # Field name made lowercase.
    cong_tin = models.TextField(db_column='Cong_tin', blank=True, null=True)  # Field name made lowercase.
    cong_mob = models.TextField(db_column='Cong_mob', blank=True, null=True)  # Field name made lowercase.
    cong_fax = models.TextField(db_column='Cong_fax', blank=True, null=True)  # Field name made lowercase.
    cong_vat = models.TextField(db_column='Cong_vat', blank=True, null=True)  # Field name made lowercase.
    addtype = models.IntegerField(db_column='AddType', blank=True, null=True)  # Field name made lowercase.
    addamt = models.FloatField(db_column='AddAmt', blank=True, null=True)  # Field name made lowercase.
    deductiontype = models.IntegerField(db_column='DeductionType', blank=True, null=True)  # Field name made lowercase.
    deduction = models.FloatField(db_column='Deduction', blank=True, null=True)  # Field name made lowercase.
    pftype = models.IntegerField(db_column='PFType', blank=True, null=True)  # Field name made lowercase.
    pf = models.FloatField(db_column='PF', blank=True, null=True)  # Field name made lowercase.
    cenvat = models.IntegerField(db_column='CENVAT', blank=True, null=True)  # Field name made lowercase.
    sedtype = models.IntegerField(db_column='SEDType', blank=True, null=True)  # Field name made lowercase.
    sed = models.FloatField(db_column='SED', blank=True, null=True)  # Field name made lowercase.
    aedtype = models.IntegerField(db_column='AEDType', blank=True, null=True)  # Field name made lowercase.
    aed = models.FloatField(db_column='AED', blank=True, null=True)  # Field name made lowercase.
    vat = models.IntegerField(db_column='VAT', blank=True, null=True)  # Field name made lowercase.
    selectedcst = models.IntegerField(db_column='SelectedCST', blank=True, null=True)  # Field name made lowercase.
    cst = models.IntegerField(db_column='CST')  # Field name made lowercase.
    freighttype = models.IntegerField(db_column='FreightType', blank=True, null=True)  # Field name made lowercase.
    freight = models.FloatField(db_column='Freight', blank=True, null=True)  # Field name made lowercase.
    insurancetype = models.IntegerField(db_column='InsuranceType', blank=True, null=True)  # Field name made lowercase.
    insurance = models.FloatField(db_column='Insurance', blank=True, null=True)  # Field name made lowercase.
    poid = models.IntegerField(db_column='POId', blank=True, null=True)  # Field name made lowercase.
    otheramt = models.FloatField(db_column='OtherAmt', blank=True, null=True)  # Field name made lowercase.
    buyer_city = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='Buyer_city', blank=True, null=True)  # Field name made lowercase.
    cong_city = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='Cong_city', related_name='tblaccsalesinvoicemaster_cong_city_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_SalesInvoice_Master'


class TblaccSalesinvoiceMasterType(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    live = models.IntegerField(db_column='Live', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_SalesInvoice_Master_Type'


class TblaccServicetaxinvoiceDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    invoiceno = models.CharField(db_column='InvoiceNo', max_length=50)  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId')  # Field name made lowercase.
    reqqty = models.FloatField(db_column='ReqQty')  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    amtinper = models.FloatField(db_column='AmtInPer')  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate')  # Field name made lowercase.
    mid = models.ForeignKey('TblaccServicetaxinvoiceMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.
    unit = models.IntegerField(db_column='Unit', blank=True, null=True)  # Changed from FK to IntegerField

    class Meta:
        managed = False
        db_table = 'tblACC_ServiceTaxInvoice_Details'


class TblaccServicetaxinvoiceMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    invoiceno = models.TextField(db_column='InvoiceNo', blank=True, null=True)  # Field name made lowercase.
    poid = models.IntegerField(db_column='POId', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    dateofissueinvoice = models.CharField(db_column='DateOfIssueInvoice', max_length=50, blank=True, null=True)  # Field name made lowercase.
    timeofissueinvoice = models.CharField(db_column='TimeOfIssueInvoice', max_length=50)  # Field name made lowercase.
    dutyrate = models.CharField(db_column='DutyRate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    customercode = models.TextField(db_column='CustomerCode')  # Field name made lowercase.
    customercategory = models.IntegerField(db_column='CustomerCategory', blank=True, null=True)  # Field name made lowercase.
    buyer_name = models.TextField(db_column='Buyer_name', blank=True, null=True)  # Field name made lowercase.
    buyer_add = models.TextField(db_column='Buyer_add', blank=True, null=True)  # Field name made lowercase.
    buyer_state = models.IntegerField(db_column='Buyer_state', blank=True, null=True)  # Field name made lowercase.
    buyer_country = models.IntegerField(db_column='Buyer_country', blank=True, null=True)  # Field name made lowercase.
    buyer_cotper = models.TextField(db_column='Buyer_cotper', blank=True, null=True)  # Field name made lowercase.
    buyer_ph = models.TextField(db_column='Buyer_ph', blank=True, null=True)  # Field name made lowercase.
    buyer_email = models.TextField(db_column='Buyer_email', blank=True, null=True)  # Field name made lowercase.
    buyer_ecc = models.TextField(db_column='Buyer_ecc', blank=True, null=True)  # Field name made lowercase.
    buyer_tin = models.TextField(db_column='Buyer_tin', blank=True, null=True)  # Field name made lowercase.
    buyer_mob = models.TextField(db_column='Buyer_mob', blank=True, null=True)  # Field name made lowercase.
    buyer_fax = models.TextField(db_column='Buyer_fax', blank=True, null=True)  # Field name made lowercase.
    buyer_vat = models.TextField(db_column='Buyer_vat', blank=True, null=True)  # Field name made lowercase.
    cong_name = models.TextField(db_column='Cong_name', blank=True, null=True)  # Field name made lowercase.
    cong_add = models.TextField(db_column='Cong_add', blank=True, null=True)  # Field name made lowercase.
    cong_state = models.IntegerField(db_column='Cong_state', blank=True, null=True)  # Field name made lowercase.
    cong_country = models.IntegerField(db_column='Cong_country', blank=True, null=True)  # Field name made lowercase.
    cong_cotper = models.TextField(db_column='Cong_cotper', blank=True, null=True)  # Field name made lowercase.
    cong_ph = models.TextField(db_column='Cong_ph', blank=True, null=True)  # Field name made lowercase.
    cong_email = models.TextField(db_column='Cong_email')  # Field name made lowercase.
    cong_ecc = models.TextField(db_column='Cong_ecc')  # Field name made lowercase.
    cong_tin = models.TextField(db_column='Cong_tin', blank=True, null=True)  # Field name made lowercase.
    cong_mob = models.TextField(db_column='Cong_mob', blank=True, null=True)  # Field name made lowercase.
    cong_fax = models.TextField(db_column='Cong_fax', blank=True, null=True)  # Field name made lowercase.
    cong_vat = models.TextField(db_column='Cong_vat', blank=True, null=True)  # Field name made lowercase.
    addtype = models.IntegerField(db_column='AddType', blank=True, null=True)  # Field name made lowercase.
    addamt = models.FloatField(db_column='AddAmt', blank=True, null=True)  # Field name made lowercase.
    deductiontype = models.IntegerField(db_column='DeductionType', blank=True, null=True)  # Field name made lowercase.
    deduction = models.FloatField(db_column='Deduction', blank=True, null=True)  # Field name made lowercase.
    servicetax = models.IntegerField(db_column='ServiceTax', blank=True, null=True)  # Field name made lowercase.
    taxableservices = models.IntegerField(db_column='TaxableServices', blank=True, null=True)  # Field name made lowercase.
    buyer_city = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='Buyer_city', blank=True, null=True)  # Field name made lowercase.
    cong_city = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='Cong_city', related_name='tblaccservicetaxinvoicemaster_cong_city_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_ServiceTaxInvoice_Master'


class TblaccServiceCategory(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_Service_Category'


class TblaccTaxableservices(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_TaxableServices'


class TblaccTouradvance(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId')  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_TourAdvance'


class TblaccTouradvanceDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId')  # Field name made lowercase.
    expencessid = models.IntegerField(db_column='ExpencessId', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_TourAdvance_Details'


class TblaccTourexpencesstype(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_TourExpencessType'


class TblaccTourintimationMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    tino = models.TextField(db_column='TINo', blank=True, null=True)  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.
    type = models.IntegerField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    bggroupid = models.IntegerField(db_column='BGGroupId', blank=True, null=True)  # Field name made lowercase.
    projectname = models.TextField(db_column='ProjectName', blank=True, null=True)  # Field name made lowercase.
    tourstartdate = models.TextField(db_column='TourStartDate', blank=True, null=True)  # Field name made lowercase.
    tourstarttime = models.TextField(db_column='TourStartTime', blank=True, null=True)  # Field name made lowercase.
    tourenddate = models.TextField(db_column='TourEndDate', blank=True, null=True)  # Field name made lowercase.
    tourendtime = models.TextField(db_column='TourEndTime', blank=True, null=True)  # Field name made lowercase.
    noofdays = models.IntegerField(db_column='NoOfDays', blank=True, null=True)  # Field name made lowercase.
    nameaddressserprovider = models.TextField(db_column='NameAddressSerProvider', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.TextField(db_column='ContactPerson', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    email = models.TextField(db_column='Email', blank=True, null=True)  # Field name made lowercase.
    placeoftourcountry = models.IntegerField(db_column='PlaceOfTourCountry')  # Field name made lowercase.
    placeoftourstate = models.IntegerField(db_column='PlaceOfTourState')  # Field name made lowercase.
    placeoftourcity = models.IntegerField(db_column='PlaceOfTourCity')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_TourIntimation_Master'


class TblaccTourvoucheradvanceDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId')  # Field name made lowercase.
    tdmid = models.IntegerField(db_column='TDMId')  # Field name made lowercase.
    sanctionedamount = models.FloatField(db_column='SanctionedAmount', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_TourVoucherAdvance_Details'


class TblaccTourvoucherMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    timid = models.IntegerField(db_column='TIMId')  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    tvno = models.TextField(db_column='TVNo', blank=True, null=True)  # Field name made lowercase.
    amtbaltowardscompany = models.FloatField(db_column='AmtBalTowardsCompany', blank=True, null=True)  # Field name made lowercase.
    amtbaltowardsemployee = models.FloatField(db_column='AmtBalTowardsEmployee', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_TourVoucher_Master'


class TblaccTransportmode(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblACC_TransportMode'


class TblaccLoandetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    particulars = models.TextField(db_column='Particulars', blank=True, null=True)  # Field name made lowercase.
    creditamt = models.FloatField(db_column='CreditAmt', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblaccLoanmaster', models.DO_NOTHING, db_column='MId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblAcc_LoanDetails'


class TblaccLoanmaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    particulars = models.TextField(db_column='Particulars', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblAcc_LoanMaster'


class TblaccTdscodeMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sectionno = models.TextField(db_column='SectionNo', blank=True, null=True)  # Field name made lowercase.
    natureofpayment = models.TextField(db_column='NatureOfPayment', blank=True, null=True)  # Field name made lowercase.
    paymentrange = models.FloatField(db_column='PaymentRange', blank=True, null=True)  # Field name made lowercase.
    paytoindividual = models.FloatField(db_column='PayToIndividual', blank=True, null=True)  # Field name made lowercase.
    others = models.FloatField(db_column='Others', blank=True, null=True)  # Field name made lowercase.
    withoutpan = models.FloatField(db_column='WithOutPAN', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblAcc_TDSCode_Master'


class TblaccessMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.
    accesstype = models.IntegerField(db_column='AccessType', blank=True, null=True)  # Field name made lowercase.
    access = models.IntegerField(db_column='Access', blank=True, null=True)  # Field name made lowercase.
    modid = models.IntegerField(db_column='ModId')  # Changed from ForeignKey - TblmoduleMaster doesnt exist  # Field name made lowercase.
    submodid = models.IntegerField(db_column='SubModId')  # Changed from ForeignKey - TblsubmoduleMaster doesnt exist  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblAccess_Master'




class TblexcisecommodityMaster(models.Model):
    """
    Excisable Commodity Master
    Converted from: D:/inetpub/NewERP/Module/Accounts/Masters/ExcisableCommodity.aspx (lines 119-122)
    """
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.
    chaphead = models.CharField(db_column='ChapHead', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblExciseCommodity_Master'

    def __str__(self):
        return self.terms or ''


class TblexciseserMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.
    value = models.FloatField(db_column='Value', blank=True, null=True)  # Field name made lowercase.
    accessablevalue = models.FloatField(db_column='AccessableValue', blank=True, null=True)  # Field name made lowercase.
    educess = models.FloatField(db_column='EDUCess', blank=True, null=True)  # Field name made lowercase.
    shecess = models.FloatField(db_column='SHECess', blank=True, null=True)  # Field name made lowercase.
    live = models.IntegerField(db_column='Live', blank=True, null=True)  # Field name made lowercase.
    livesertax = models.IntegerField(db_column='LiveSerTax', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblExciseser_Master'


class TblfreightMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFreight_Master'




class TbloctroiMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.
    value = models.FloatField(db_column='Value', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblOctroi_Master'



class TblpackingMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.CharField(db_column='Terms', max_length=50, blank=True, null=True)  # Field name made lowercase.
    value = models.FloatField(db_column='Value', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPacking_Master'


class TblpaymentMaster(models.Model):
    """
    Payment Terms Master
    Converted from: D:/inetpub/NewERP/Module/Accounts/Masters/PaymentTerms.aspx (lines 112-115)
    """
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPayment_Master'

    def __str__(self):
        return self.terms or ''


class TblplnProcessMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    processname = models.TextField(db_column='ProcessName', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPln_Process_Master'



class Tblstktranstype(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    transactions = models.TextField(db_column='Transactions', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblStkTransType'


class TblvatMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.
    value = models.FloatField(db_column='Value', blank=True, null=True)  # Field name made lowercase.
    live = models.IntegerField(db_column='Live', blank=True, null=True)  # Field name made lowercase.
    isvat = models.IntegerField(db_column='IsVAT')  # Field name made lowercase.
    iscst = models.IntegerField(db_column='IsCST')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblVAT_Master'


class TblwarrentyMaster(models.Model):
    """
    Warranty Terms Master
    Converted from: D:/inetpub/NewERP/Module/Accounts/Masters/WarrentyTerms.aspx (lines 111-114)
    """
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    terms = models.TextField(db_column='Terms', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblWarrenty_Master'

    def __str__(self):
        return self.terms or ''
