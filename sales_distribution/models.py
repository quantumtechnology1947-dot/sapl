from django.db import models
from sys_admin.models import Tblcountry, Tblcity, TblfinancialMaster, UnitMaster, Tblstate
# Create your models here. 


class SdCustEnquiryAttachMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    enqid = models.IntegerField(db_column='EnqId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    filename = models.TextField(db_column='FileName', blank=True, null=True)  # Field name made lowercase.
    filesize = models.FloatField(db_column='FileSize', blank=True, null=True)  # Field name made lowercase.
    contenttype = models.TextField(db_column='ContentType', blank=True, null=True)  # Field name made lowercase.
    filedata = models.BinaryField(db_column='FileData', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_Enquiry_Attach_Master'


class SdCustEnquiryMaster(models.Model):
    enqid = models.AutoField(db_column='EnqId', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    customerid = models.CharField(db_column='CustomerId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    customername = models.TextField(db_column='CustomerName', blank=True, null=True)  # Field name made lowercase.
    regdaddress = models.TextField(db_column='RegdAddress', blank=True, null=True)  # Field name made lowercase.
    regdcountry = models.TextField(db_column='RegdCountry', blank=True, null=True)  # Field name made lowercase.
    regdstate = models.TextField(db_column='RegdState', blank=True, null=True)  # Field name made lowercase.
    regdcity = models.TextField(db_column='RegdCity', blank=True, null=True)  # Field name made lowercase.
    regdpinno = models.TextField(db_column='RegdPinNo', blank=True, null=True)  # Field name made lowercase.
    regdcontactno = models.TextField(db_column='RegdContactNo', blank=True, null=True)  # Field name made lowercase.
    regdfaxno = models.TextField(db_column='RegdFaxNo', blank=True, null=True)  # Field name made lowercase.
    workaddress = models.TextField(db_column='WorkAddress', blank=True, null=True)  # Field name made lowercase.
    workcountry = models.TextField(db_column='WorkCountry', blank=True, null=True)  # Field name made lowercase.
    workstate = models.TextField(db_column='WorkState', blank=True, null=True)  # Field name made lowercase.
    workcity = models.TextField(db_column='WorkCity', blank=True, null=True)  # Field name made lowercase.
    workpinno = models.TextField(db_column='WorkPinNo', blank=True, null=True)  # Field name made lowercase.
    workcontactno = models.TextField(db_column='WorkContactNo', blank=True, null=True)  # Field name made lowercase.
    workfaxno = models.TextField(db_column='WorkFaxNo', blank=True, null=True)  # Field name made lowercase.
    materialdeladdress = models.TextField(db_column='MaterialDelAddress', blank=True, null=True)  # Field name made lowercase.
    materialdelcountry = models.TextField(db_column='MaterialDelCountry', blank=True, null=True)  # Field name made lowercase.
    materialdelstate = models.TextField(db_column='MaterialDelState', blank=True, null=True)  # Field name made lowercase.
    materialdelcity = models.TextField(db_column='MaterialDelCity', blank=True, null=True)  # Field name made lowercase.
    materialdelpinno = models.TextField(db_column='MaterialDelPinNo', blank=True, null=True)  # Field name made lowercase.
    materialdelcontactno = models.TextField(db_column='MaterialDelContactNo', blank=True, null=True)  # Field name made lowercase.
    materialdelfaxno = models.TextField(db_column='MaterialDelFaxNo', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.TextField(db_column='ContactPerson', blank=True, null=True)  # Field name made lowercase.
    juridictioncode = models.TextField(db_column='JuridictionCode', blank=True, null=True)  # Field name made lowercase.
    commissionurate = models.TextField(db_column='Commissionurate', blank=True, null=True)  # Field name made lowercase.
    tinvatno = models.TextField(db_column='TinVatNo', blank=True, null=True)  # Field name made lowercase.
    email = models.TextField(db_column='Email', blank=True, null=True)  # Field name made lowercase.
    eccno = models.TextField(db_column='EccNo', blank=True, null=True)  # Field name made lowercase.
    divn = models.TextField(db_column='Divn', blank=True, null=True)  # Field name made lowercase.
    tincstno = models.TextField(db_column='TinCstNo', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    range = models.TextField(db_column='Range', blank=True, null=True)  # Field name made lowercase.
    panno = models.TextField(db_column='PanNo', blank=True, null=True)  # Field name made lowercase.
    tdscode = models.TextField(db_column='TDSCode', blank=True, null=True)  # Field name made lowercase.
    remark = models.TextField(db_column='Remark', blank=True, null=True)  # Field name made lowercase.
    enquiryfor = models.TextField(db_column='EnquiryFor', blank=True, null=True)  # Field name made lowercase.
    flag = models.IntegerField(db_column='Flag', blank=True, null=True)  # Field name made lowercase.
    postatus = models.IntegerField(db_column='POStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_Enquiry_Master'


class SdCustPoDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    itemdesc = models.TextField(db_column='ItemDesc')  # Field name made lowercase.
    totalqty = models.FloatField(db_column='TotalQty')  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate')  # Field name made lowercase.
    discount = models.FloatField(db_column='Discount')  # Field name made lowercase.
    poid = models.ForeignKey('SdCustPoMaster', models.DO_NOTHING, db_column='POId')  # Field name made lowercase.
    unit = models.ForeignKey(UnitMaster, models.DO_NOTHING, db_column='Unit')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_PO_Details'


class SdCustPoMaster(models.Model):
    poid = models.AutoField(db_column='POId', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    customerid = models.TextField(db_column='CustomerId', blank=True, null=True)  # Field name made lowercase.
    quotationno = models.IntegerField(db_column='QuotationNo', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    podate = models.TextField(db_column='PODate', blank=True, null=True)  # Field name made lowercase.
    poreceiveddate = models.TextField(db_column='POReceivedDate', blank=True, null=True)  # Field name made lowercase.
    vendorcode = models.TextField(db_column='VendorCode', blank=True, null=True)  # Field name made lowercase.
    paymentterms = models.TextField(db_column='PaymentTerms', blank=True, null=True)  # Field name made lowercase.
    pf = models.TextField(db_column='PF', blank=True, null=True)  # Field name made lowercase.
    vat = models.TextField(db_column='VAT', blank=True, null=True)  # Field name made lowercase.
    excise = models.TextField(db_column='Excise', blank=True, null=True)  # Field name made lowercase.
    octroi = models.TextField(db_column='Octroi', blank=True, null=True)  # Field name made lowercase.
    warrenty = models.TextField(db_column='Warrenty', blank=True, null=True)  # Field name made lowercase.
    insurance = models.TextField(db_column='Insurance', blank=True, null=True)  # Field name made lowercase.
    transport = models.TextField(db_column='Transport', blank=True, null=True)  # Field name made lowercase.
    noteno = models.TextField(db_column='NoteNo', blank=True, null=True)  # Field name made lowercase.
    registrationno = models.TextField(db_column='RegistrationNo', blank=True, null=True)  # Field name made lowercase.
    freight = models.TextField(db_column='Freight', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.
    cst = models.TextField(db_column='CST', blank=True, null=True)  # Field name made lowercase.
    validity = models.TextField(db_column='Validity', blank=True, null=True)  # Field name made lowercase.
    othercharges = models.TextField(db_column='OtherCharges', blank=True, null=True)  # Field name made lowercase.
    filename = models.TextField(db_column='FileName', blank=True, null=True)  # Field name made lowercase.
    filesize = models.FloatField(db_column='FileSize', blank=True, null=True)  # Field name made lowercase.
    contenttype = models.TextField(db_column='ContentType', blank=True, null=True)  # Field name made lowercase.
    filedata = models.BinaryField(db_column='FileData', blank=True, null=True)  # Field name made lowercase.
    enqid = models.ForeignKey(SdCustEnquiryMaster, models.DO_NOTHING, db_column='EnqId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_PO_Master'


class SdCustQuotationDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    itemdesc = models.TextField(db_column='ItemDesc')  # Field name made lowercase.
    totalqty = models.FloatField(db_column='TotalQty')  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate')  # Field name made lowercase.
    discount = models.FloatField(db_column='Discount', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('SdCustQuotationMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.
    unit = models.ForeignKey(UnitMaster, models.DO_NOTHING, db_column='Unit')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_Quotation_Details'


class SdCustQuotationMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    customerid = models.TextField(db_column='CustomerId')  # Field name made lowercase.
    quotationno = models.TextField(db_column='QuotationNo')  # Field name made lowercase.
    paymentterms = models.TextField(db_column='PaymentTerms', blank=True, null=True)  # Field name made lowercase.
    pftype = models.IntegerField(db_column='PFType', blank=True, null=True)  # Field name made lowercase.
    pf = models.FloatField(db_column='PF', blank=True, null=True)  # Field name made lowercase.
    vatcst = models.IntegerField(db_column='VATCST', blank=True, null=True)  # Field name made lowercase.
    excise = models.IntegerField(db_column='Excise', blank=True, null=True)  # Field name made lowercase.
    octroitype = models.IntegerField(db_column='OctroiType', blank=True, null=True)  # Field name made lowercase.
    octroi = models.FloatField(db_column='Octroi', blank=True, null=True)  # Field name made lowercase.
    warrenty = models.TextField(db_column='Warrenty', blank=True, null=True)  # Field name made lowercase.
    insurance = models.FloatField(db_column='Insurance', blank=True, null=True)  # Field name made lowercase.
    validity = models.TextField(db_column='Validity', blank=True, null=True)  # Field name made lowercase.
    otherchargestype = models.IntegerField(db_column='OtherChargesType', blank=True, null=True)  # Field name made lowercase.
    othercharges = models.FloatField(db_column='otherCharges', blank=True, null=True)  # Field name made lowercase.
    transport = models.TextField(db_column='Transport', blank=True, null=True)  # Field name made lowercase.
    noteno = models.TextField(db_column='NoteNo', blank=True, null=True)  # Field name made lowercase.
    registrationno = models.TextField(db_column='RegistrationNo', blank=True, null=True)  # Field name made lowercase.
    freighttype = models.IntegerField(db_column='FreightType', blank=True, null=True)  # Field name made lowercase.
    freight = models.FloatField(db_column='Freight', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.
    deliveryterms = models.TextField(db_column='DeliveryTerms', blank=True, null=True)  # Field name made lowercase.
    duedate = models.TextField(db_column='DueDate', blank=True, null=True)  # Field name made lowercase.
    checked = models.IntegerField(db_column='Checked', blank=True, null=True)  # Field name made lowercase.
    checkedby = models.TextField(db_column='CheckedBy', blank=True, null=True)  # Field name made lowercase.
    checkeddate = models.TextField(db_column='CheckedDate', blank=True, null=True)  # Field name made lowercase.
    checkedtime = models.TextField(db_column='CheckedTime', blank=True, null=True)  # Field name made lowercase.
    approve = models.IntegerField(db_column='Approve', blank=True, null=True)  # Field name made lowercase.
    approvedby = models.TextField(db_column='ApprovedBy', blank=True, null=True)  # Field name made lowercase.
    approvedate = models.TextField(db_column='ApproveDate', blank=True, null=True)  # Field name made lowercase.
    approvetime = models.TextField(db_column='ApproveTime', blank=True, null=True)  # Field name made lowercase.
    authorize = models.IntegerField(db_column='Authorize', blank=True, null=True)  # Field name made lowercase.
    authorizedby = models.TextField(db_column='AuthorizedBy', blank=True, null=True)  # Field name made lowercase.
    authorizedate = models.TextField(db_column='AuthorizeDate', blank=True, null=True)  # Field name made lowercase.
    authorizetime = models.TextField(db_column='AuthorizeTime', blank=True, null=True)  # Field name made lowercase.
    enqid = models.ForeignKey(SdCustEnquiryMaster, models.DO_NOTHING, db_column='EnqId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_Quotation_Master'


class SdCustWorkorderDispatch(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    dano = models.TextField(db_column='DANo', blank=True, null=True)  # Field name made lowercase. Dispatch number
    wrno = models.TextField(db_column='WRNo', blank=True, null=True)  # Field name made lowercase. Release number (denormalized for reference)
    wrid = models.TextField(db_column='WRId', blank=True, null=True)  # Field name made lowercase.
    itemid = models.TextField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    issuedqty = models.FloatField(db_column='IssuedQty', blank=True, null=True)  # Field name made lowercase.
    dispatchqty = models.FloatField(db_column='DispatchQty', blank=True, null=True)  # Field name made lowercase.
    freightcharges = models.TextField(db_column='FreightCharges', blank=True, null=True)  # Field name made lowercase.
    vehicleby = models.TextField(db_column='Vehicleby', blank=True, null=True)  # Field name made lowercase.
    octroicharges = models.TextField(db_column='OctroiCharges', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_WorkOrder_Dispatch'


class SdCustWorkorderMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    customerid = models.TextField(db_column='CustomerId')  # Field name made lowercase.
    enqid = models.IntegerField(db_column='EnqId', blank=True, null=True)  # Field name made lowercase.
    pono = models.TextField(db_column='PONo', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    scid = models.IntegerField(db_column='SCId', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    taskworkorderdate = models.TextField(db_column='TaskWorkOrderDate', blank=True, null=True)  # Field name made lowercase.
    taskprojecttitle = models.TextField(db_column='TaskProjectTitle', blank=True, null=True)  # Field name made lowercase.
    taskprojectleader = models.TextField(db_column='TaskProjectLeader', blank=True, null=True)  # Field name made lowercase.
    taskbusinessgroup = models.IntegerField(db_column='TaskBusinessGroup', blank=True, null=True)  # Field name made lowercase.
    tasktargetdap_fdate = models.TextField(db_column='TaskTargetDAP_FDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetdap_tdate = models.TextField(db_column='TaskTargetDAP_TDate', blank=True, null=True)  # Field name made lowercase.
    taskdesignfinalization_fdate = models.TextField(db_column='TaskDesignFinalization_FDate', blank=True, null=True)  # Field name made lowercase.
    taskdesignfinalization_tdate = models.TextField(db_column='TaskDesignFinalization_TDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetmanufg_fdate = models.TextField(db_column='TaskTargetManufg_FDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetmanufg_tdate = models.TextField(db_column='TaskTargetManufg_TDate', blank=True, null=True)  # Field name made lowercase.
    tasktargettryout_fdate = models.TextField(db_column='TaskTargetTryOut_FDate', blank=True, null=True)  # Field name made lowercase.
    tasktargettryout_tdate = models.TextField(db_column='TaskTargetTryOut_TDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetdespach_fdate = models.TextField(db_column='TaskTargetDespach_FDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetdespach_tdate = models.TextField(db_column='TaskTargetDespach_TDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetassembly_fdate = models.TextField(db_column='TaskTargetAssembly_FDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetassembly_tdate = models.TextField(db_column='TaskTargetAssembly_TDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetinstalation_fdate = models.TextField(db_column='TaskTargetInstalation_FDate', blank=True, null=True)  # Field name made lowercase.
    tasktargetinstalation_tdate = models.TextField(db_column='TaskTargetInstalation_TDate', blank=True, null=True)  # Field name made lowercase.
    taskcustinspection_fdate = models.TextField(db_column='TaskCustInspection_FDate', blank=True, null=True)  # Field name made lowercase.
    taskcustinspection_tdate = models.TextField(db_column='TaskCustInspection_TDate', blank=True, null=True)  # Field name made lowercase.
    shippingadd = models.TextField(db_column='ShippingAdd', blank=True, null=True)  # Field name made lowercase.
    shippingcountry = models.TextField(db_column='ShippingCountry', blank=True, null=True)  # Field name made lowercase.
    shippingstate = models.TextField(db_column='ShippingState', blank=True, null=True)  # Field name made lowercase.
    shippingcity = models.TextField(db_column='ShippingCity', blank=True, null=True)  # Field name made lowercase.
    shippingcontactperson1 = models.TextField(db_column='ShippingContactPerson1', blank=True, null=True)  # Field name made lowercase.
    shippingcontactno1 = models.TextField(db_column='ShippingContactNo1', blank=True, null=True)  # Field name made lowercase.
    shippingemail1 = models.TextField(db_column='ShippingEmail1', blank=True, null=True)  # Field name made lowercase.
    shippingcontactperson2 = models.TextField(db_column='ShippingContactPerson2', blank=True, null=True)  # Field name made lowercase.
    shippingcontactno2 = models.TextField(db_column='ShippingContactNo2', blank=True, null=True)  # Field name made lowercase.
    shippingemail2 = models.TextField(db_column='ShippingEmail2', blank=True, null=True)  # Field name made lowercase.
    shippingfaxno = models.TextField(db_column='ShippingFaxNo', blank=True, null=True)  # Field name made lowercase.
    shippingeccno = models.TextField(db_column='ShippingEccNo', blank=True, null=True)  # Field name made lowercase.
    shippingtincstno = models.TextField(db_column='ShippingTinCstNo', blank=True, null=True)  # Field name made lowercase.
    shippingtinvatno = models.TextField(db_column='ShippingTinVatNo', blank=True, null=True)  # Field name made lowercase.
    instractionprimerpainting = models.IntegerField(db_column='InstractionPrimerPainting', blank=True, null=True)  # Field name made lowercase.
    instractionpainting = models.IntegerField(db_column='InstractionPainting', blank=True, null=True)  # Field name made lowercase.
    instractionselfcertrept = models.IntegerField(db_column='InstractionSelfCertRept', blank=True, null=True)  # Field name made lowercase.
    instractionother = models.TextField(db_column='InstractionOther', blank=True, null=True)  # Field name made lowercase.
    instractionexportcasemark = models.TextField(db_column='InstractionExportCaseMark', blank=True, null=True)  # Field name made lowercase.
    instractionattachannexure = models.TextField(db_column='InstractionAttachAnnexure', blank=True, null=True)  # Field name made lowercase.
    releasewis = models.IntegerField(db_column='ReleaseWIS', blank=True, null=True)  # Field name made lowercase.
    dryactualrun = models.IntegerField(db_column='DryActualRun', blank=True, null=True)  # Field name made lowercase.
    updatewo = models.IntegerField(db_column='UpdateWO', blank=True, null=True)  # Field name made lowercase.
    batches = models.FloatField(db_column='Batches', blank=True, null=True)  # Field name made lowercase.
    closeopen = models.IntegerField(db_column='CloseOpen', blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.
    manufmaterialdate = models.TextField(db_column='ManufMaterialDate', blank=True, null=True)  # Field name made lowercase.
    boughtoutmaterialdate = models.TextField(db_column='BoughtoutMaterialDate', blank=True, null=True)  # Field name made lowercase.
    buyer = models.IntegerField(db_column='Buyer', blank=True, null=True)  # Field name made lowercase.
    r_person = models.TextField(blank=True, null=True)
    critics = models.TextField(db_column='Critics', blank=True, null=True)  # Field name made lowercase.
    poid = models.ForeignKey(SdCustPoMaster, models.DO_NOTHING, db_column='POId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_WorkOrder_Master'

    def __str__(self):
        """Return readable representation of work order"""
        wono = self.wono or f"WO-{self.id}"
        title = self.taskprojecttitle[:40] if self.taskprojecttitle else "No Title"
        return f"{wono} - {title}"


class SdCustWorkorderProductsDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_WorkOrder_Products_Details'


class SdCustWorkorderRelease(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    wrno = models.TextField(db_column='WRNo', blank=True, null=True)  # Field name made lowercase. Release number
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase. Work order number (denormalized for reference)
    itemid = models.TextField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    issuedqty = models.FloatField(db_column='IssuedQty', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_WorkOrder_Release'


class SdCustMaster(models.Model):
    salesid = models.AutoField(db_column='SalesId', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    enqid = models.IntegerField(db_column='EnqId', blank=True, null=True)  # Field name made lowercase.
    customerid = models.TextField(db_column='CustomerId', blank=True, null=True)  # Field name made lowercase.
    customername = models.TextField(db_column='CustomerName', blank=True, null=True)  # Field name made lowercase.
    regdaddress = models.TextField(db_column='RegdAddress', blank=True, null=True)  # Field name made lowercase.
    regdcountry = models.IntegerField(db_column='RegdCountry', blank=True, null=True)  # Field name made lowercase.
    regdstate = models.IntegerField(db_column='RegdState', blank=True, null=True)  # Field name made lowercase.
    regdpinno = models.TextField(db_column='RegdPinNo', blank=True, null=True)  # Field name made lowercase.
    regdcontactno = models.TextField(db_column='RegdContactNo', blank=True, null=True)  # Field name made lowercase.
    regdfaxno = models.TextField(db_column='RegdFaxNo', blank=True, null=True)  # Field name made lowercase.
    workaddress = models.TextField(db_column='WorkAddress', blank=True, null=True)  # Field name made lowercase.
    workcountry = models.IntegerField(db_column='WorkCountry', blank=True, null=True)  # Field name made lowercase.
    workstate = models.IntegerField(db_column='WorkState', blank=True, null=True)  # Field name made lowercase.
    workpinno = models.TextField(db_column='WorkPinNo', blank=True, null=True)  # Field name made lowercase.
    workcontactno = models.TextField(db_column='WorkContactNo', blank=True, null=True)  # Field name made lowercase.
    workfaxno = models.TextField(db_column='WorkFaxNo', blank=True, null=True)  # Field name made lowercase.
    materialdeladdress = models.TextField(db_column='MaterialDelAddress', blank=True, null=True)  # Field name made lowercase.
    materialdelcountry = models.IntegerField(db_column='MaterialDelCountry', blank=True, null=True)  # Field name made lowercase.
    materialdelstate = models.IntegerField(db_column='MaterialDelState', blank=True, null=True)  # Field name made lowercase.
    materialdelpinno = models.TextField(db_column='MaterialDelPinNo', blank=True, null=True)  # Field name made lowercase.
    materialdelcontactno = models.TextField(db_column='MaterialDelContactNo', blank=True, null=True)  # Field name made lowercase.
    materialdelfaxno = models.TextField(db_column='MaterialDelFaxNo', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.TextField(db_column='ContactPerson', blank=True, null=True)  # Field name made lowercase.
    juridictioncode = models.TextField(db_column='JuridictionCode', blank=True, null=True)  # Field name made lowercase.
    commissionurate = models.TextField(db_column='Commissionurate', blank=True, null=True)  # Field name made lowercase.
    tinvatno = models.TextField(db_column='TinVatNo', blank=True, null=True)  # Field name made lowercase.
    email = models.TextField(db_column='Email', blank=True, null=True)  # Field name made lowercase.
    eccno = models.TextField(db_column='EccNo', blank=True, null=True)  # Field name made lowercase.
    divn = models.TextField(db_column='Divn', blank=True, null=True)  # Field name made lowercase.
    tincstno = models.TextField(db_column='TinCstNo', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    range = models.TextField(db_column='Range', blank=True, null=True)  # Field name made lowercase.
    panno = models.TextField(db_column='PanNo', blank=True, null=True)  # Field name made lowercase.
    tdscode = models.TextField(db_column='TDSCode', blank=True, null=True)  # Field name made lowercase.
    remark = models.TextField(db_column='Remark', blank=True, null=True)  # Field name made lowercase.
    materialdelcity = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='MaterialDelCity', blank=True, null=True)  # Field name made lowercase.
    regdcity = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='RegdCity', related_name='sdcustmaster_regdcity_set', blank=True, null=True)  # Field name made lowercase.
    workcity = models.ForeignKey('sys_admin.Tblcity', models.DO_NOTHING, db_column='WorkCity', related_name='sdcustmaster_workcity_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SD_Cust_master'



class TblsdWoCategory(models.Model):
    cid = models.AutoField(db_column='CId', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    cname = models.TextField(db_column='CName', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.
    hassubcat = models.TextField(db_column='HasSubCat', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSD_WO_Category'


class TblsdWoSubcategory(models.Model):
    scid = models.AutoField(db_column='SCId', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId')  # Field name made lowercase.
    scname = models.TextField(db_column='SCName')  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSD_WO_SubCategory'
