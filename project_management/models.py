"""
Project Management Module Models

Converted from: aspnet/Module/ProjectManagement/
Follows Django conventions with managed=False for existing database tables.
"""

from django.db import models


class TblonsiteattendanceMaster(models.Model):
    """OnSite Attendance Master - Track employee onsite attendance"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)
    systime = models.TextField(db_column='SysTime', blank=True, null=True)
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)
    onsitedate = models.TextField(db_column='OnSiteDate', blank=True, null=True)
    empid = models.TextField(db_column='EmpId', blank=True, null=True)
    shift = models.IntegerField(db_column='Shift', blank=True, null=True)
    status = models.IntegerField(db_column='Status', blank=True, null=True)
    onsite = models.TextField(db_column='Onsite', blank=True, null=True)
    fromtime = models.TextField(db_column='FromTime', blank=True, null=True)
    totime = models.TextField(db_column='ToTime', blank=True, null=True)
    upsysdate = models.TextField(db_column='UpSysDate', blank=True, null=True)
    upsystime = models.TextField(db_column='UpSysTime', blank=True, null=True)
    upsessionid = models.TextField(db_column='UpSessionId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblOnSiteAttendance_Master'
        ordering = ['-id']

    def __str__(self):
        return f"OnSite Attendance {self.id} - Emp: {self.empid} - {self.onsitedate}"

    @property
    def shift_display(self):
        shifts = {1: "Day Shift", 2: "Night Shift", 3: "General"}
        return shifts.get(self.shift, "Unknown")

    @property
    def status_display(self):
        statuses = {1: "Present", 0: "Absent"}
        return statuses.get(self.status, "Unknown")


class TblpmForcustomerDetails(models.Model):
    """For Customer Details - Customer communication with attachments"""
    id = models.AutoField(db_column='Id', primary_key=True)
    mid = models.IntegerField(db_column='MId')
    mailto = models.TextField(db_column='MailTo', blank=True, null=True)
    message = models.TextField(db_column='Message', blank=True, null=True)
    filename = models.TextField(db_column='FileName', blank=True, null=True)
    filesize = models.FloatField(db_column='FileSize', blank=True, null=True)
    contenttype = models.TextField(db_column='ContentType', blank=True, null=True)
    filedata = models.BinaryField(db_column='FileData', blank=True, null=True)
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPM_ForCustomer_Details'

    def __str__(self):
        return f"Customer Doc {self.id} - {self.filename or 'No file'}"


class TblpmManpowerplanning(models.Model):
    """ManPower Planning Master - Planning with amendment tracking"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)
    systime = models.TextField(db_column='SysTime', blank=True, null=True)
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)
    empid = models.TextField(db_column='EmpId', blank=True, null=True)
    date = models.TextField(db_column='Date', blank=True, null=True)
    wono = models.TextField(db_column='WONo', blank=True, null=True)
    dept = models.IntegerField(db_column='Dept', blank=True, null=True)
    types = models.IntegerField(db_column='Types', blank=True, null=True)
    amendmentno = models.IntegerField(db_column='AmendmentNo')

    class Meta:
        managed = False
        db_table = 'tblPM_ManPowerPlanning'
        ordering = ['-id']

    def __str__(self):
        return f"ManPower Plan {self.id} - WO: {self.wono} - Amd: {self.amendmentno}"


class TblpmManpowerplanningAmd(models.Model):
    """ManPower Planning Amendment - Historical amendments"""
    id = models.AutoField(db_column='Id', primary_key=True)
    mid = models.ForeignKey(TblpmManpowerplanning, on_delete=models.CASCADE, db_column='MId', related_name='amendments')
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)
    systime = models.TextField(db_column='SysTime', blank=True, null=True)
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)
    empid = models.TextField(db_column='EmpId', blank=True, null=True)
    date = models.TextField(db_column='Date', blank=True, null=True)
    wono = models.TextField(db_column='WONo', blank=True, null=True)
    dept = models.IntegerField(db_column='Dept', blank=True, null=True)
    types = models.IntegerField(db_column='Types', blank=True, null=True)
    amendmentno = models.IntegerField(db_column='AmendmentNo')

    class Meta:
        managed = False
        db_table = 'tblPM_ManPowerPlanning_Amd'
        ordering = ['amendmentno']

    def __str__(self):
        return f"Amendment {self.amendmentno} - WO: {self.wono}"


class TblpmManpowerplanningDetails(models.Model):
    """ManPower Planning Details - Equipment/resource details"""
    id = models.AutoField(db_column='Id', primary_key=True)
    equipid = models.CharField(db_column='EquipId', max_length=50, blank=True, null=True)
    category = models.IntegerField(db_column='Category', blank=True, null=True)
    subcategory = models.IntegerField(db_column='SubCategory', blank=True, null=True)
    planneddesc = models.TextField(db_column='PlannedDesc', blank=True, null=True)
    actualdesc = models.TextField(db_column='ActualDesc', blank=True, null=True)
    hour = models.FloatField(db_column='Hour', blank=True, null=True)
    mid = models.ForeignKey(TblpmManpowerplanning, on_delete=models.CASCADE, db_column='MId', related_name='details')

    class Meta:
        managed = False
        db_table = 'tblPM_ManPowerPlanning_Details'

    def __str__(self):
        return f"Detail {self.id} - Equip: {self.equipid} - {self.hour}hrs"


class TblpmManpowerplanningDetailsAmd(models.Model):
    """ManPower Planning Details Amendment - Historical detail changes"""
    id = models.AutoField(db_column='Id', primary_key=True)
    mid = models.IntegerField(db_column='MId', blank=True, null=True)
    dmid = models.IntegerField(db_column='DMId', blank=True, null=True)
    equipid = models.CharField(db_column='EquipId', max_length=50, blank=True, null=True)
    category = models.IntegerField(db_column='Category', blank=True, null=True)
    subcategory = models.IntegerField(db_column='SubCategory', blank=True, null=True)
    planneddesc = models.TextField(db_column='PlannedDesc', blank=True, null=True)
    actualdesc = models.TextField(db_column='ActualDesc', blank=True, null=True)
    hour = models.FloatField(db_column='Hour', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPM_ManPowerPlanning_Details_Amd'

    def __str__(self):
        return f"Detail Amendment {self.id} - Equip: {self.equipid}"


class TblpmMaterialcreditnoteMaster(models.Model):
    """Material Credit Note Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50)
    systime = models.CharField(db_column='SysTime', max_length=50)
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    sessionid = models.CharField(db_column='SessionId', max_length=50)
    mcnno = models.TextField(db_column='MCNNo', blank=True, null=True)
    wono = models.TextField(db_column='WONo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPM_MaterialCreditNote_Master'
        ordering = ['-id']

    def __str__(self):
        return f"MCN {self.mcnno} - WO: {self.wono}"


class TblpmMaterialcreditnoteDetails(models.Model):
    """Material Credit Note Details"""
    id = models.AutoField(db_column='Id', primary_key=True)
    mid = models.ForeignKey(TblpmMaterialcreditnoteMaster, on_delete=models.CASCADE, db_column='MId', related_name='details')
    pid = models.IntegerField(db_column='PId', blank=True, null=True)
    cid = models.IntegerField(db_column='CId', blank=True, null=True)
    mcnqty = models.FloatField(db_column='MCNQty', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPM_MaterialCreditNote_Details'

    def __str__(self):
        return f"MCN Detail {self.id} - Qty: {self.mcnqty}"


class TblpmProjectplanningDesign(models.Model):
    """Project Planning Design Activities"""
    id = models.AutoField(db_column='Id', primary_key=True)
    activities = models.TextField(db_column='Activities')

    class Meta:
        managed = False
        db_table = 'tblPM_ProjectPlanning_Design'

    def __str__(self):
        return f"Design Activity {self.id}"


class TblpmProjectplanningDesigner(models.Model):
    """Project Planning Designer - Design team planning"""
    id = models.AutoField(db_column='Id', primary_key=True)
    name_proj = models.TextField(db_column='Name_Proj')
    wo_no = models.CharField(db_column='Wo_No', max_length=50)
    no_fix_rqu = models.TextField(db_column='No_Fix_Rqu')
    des_lea = models.TextField(db_column='Des_Lea')
    des_mem = models.TextField(db_column='Des_Mem')
    sr_no = models.TextField(db_column='Sr_No')
    name_act = models.TextField(db_column='Name_Act')
    rev_no = models.TextField(db_column='Rev_No')
    no_days = models.TextField(db_column='No_Days')
    as_plan_from = models.TextField(db_column='As_Plan_From')
    as_plan_to = models.TextField(db_column='As_Plan_To')
    ac_from = models.TextField(db_column='Ac_From')

    class Meta:
        managed = False
        db_table = 'tblPM_ProjectPlanning_Designer'

    def __str__(self):
        return f"{self.name_proj} - WO: {self.wo_no}"


class TblpmProjectplanningMainsheet(models.Model):
    """Project Planning MainSheet - Main planning sheet"""
    id = models.AutoField(db_column='Id', primary_key=True)
    name_proj = models.TextField(db_column='Name_Proj')
    wo_no = models.TextField(db_column='Wo_No')
    cust_name = models.TextField(db_column='Cust_Name')
    proj_leader = models.TextField(db_column='Proj_Leader')
    no_fix_rqu = models.TextField(db_column='No_Fix_Rqu')
    sr_no = models.TextField(db_column='Sr.No')
    name_acti = models.TextField(db_column='Name_Acti')
    rev_no = models.TextField(db_column='Rev_No')
    no_days = models.TextField(db_column='No_Days')
    from_field = models.DateTimeField(db_column='From')
    to = models.DateTimeField(db_column='To')
    reason_delay = models.TextField(db_column='Reason_Delay')

    class Meta:
        managed = False
        db_table = 'tblPM_ProjectPlanning_MainSheet'

    def __str__(self):
        return f"{self.name_proj} - {self.cust_name}"


class TblpmProjectplanningMaster(models.Model):
    """Project Planning Master - With file upload support"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50)
    systime = models.CharField(db_column='SysTime', max_length=50)
    compid = models.IntegerField(db_column='CompId')
    sessionid = models.TextField(db_column='SessionId')
    finyearid = models.IntegerField(db_column='FinYearId')
    wono = models.TextField(db_column='WONo')
    filename = models.TextField(db_column='FileName', blank=True, null=True)
    filesize = models.FloatField(db_column='FileSize', blank=True, null=True)
    contenttype = models.TextField(db_column='ContentType', blank=True, null=True)
    filedata = models.BinaryField(db_column='FileData', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPM_ProjectPlanning_Master'
        ordering = ['-id']

    def __str__(self):
        return f"Project Plan {self.id} - WO: {self.wono}"

    @property
    def has_file(self):
        return bool(self.filedata)


class TblpmProjectstatus(models.Model):
    """Project Status - Track project activities status"""
    id = models.AutoField(db_column='Id', primary_key=True)
    srno = models.TextField(db_column='SrNo')
    wono = models.TextField(db_column='WONo')
    activities = models.TextField(db_column='Activities')

    class Meta:
        managed = False
        db_table = 'tblPM_ProjectStatus'

    def __str__(self):
        return f"Project Status {self.srno} - WO: {self.wono}"


class TblpmProjectHardwareAssemlyMaster(models.Model):
    """Hardware Assembly Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)
    prjctno = models.TextField(db_column='PRJCTNO', blank=True, null=True)
    wono = models.TextField(db_column='WONo', blank=True, null=True)
    gendate = models.TextField(db_column='GenDate', blank=True, null=True)
    vendorplan = models.TextField(db_column='VendorPlan', blank=True, null=True)
    vendordate = models.TextField(db_column='VendorDate', blank=True, null=True)
    assemlydate = models.TextField(db_column='AssemlyDate', blank=True, null=True)
    assemlyno = models.TextField(db_column='AssemlyNo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Hardware_Assemly_Master'
        ordering = ['-id']

    def __str__(self):
        return f"HW Assembly {self.assemlyno} - WO: {self.wono}"


class TblpmProjectHardwareAssemlyDetail(models.Model):
    """Hardware Assembly Detail"""
    id = models.AutoField(db_column='Id', primary_key=True)
    prjctno = models.IntegerField(db_column='PRJCTNO', blank=True, null=True)
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    uom = models.TextField(db_column='UOM', blank=True, null=True)
    bomq = models.FloatField(db_column='BOMQ', blank=True, null=True)
    design = models.TextField(db_column='Design', blank=True, null=True)
    vendorplandate = models.TextField(db_column='VendorPlanDate', blank=True, null=True)
    vendoract = models.TextField(db_column='VendorAct', blank=True, null=True)
    wono = models.TextField(db_column='WONo', blank=True, null=True)
    vendorplan = models.TextField(db_column='VendorPlan', blank=True, null=True)
    assemlydate = models.TextField(db_column='AssemlyDate', blank=True, null=True)
    remark = models.TextField(db_column='Remark', blank=True, null=True)
    assemlyno = models.TextField(db_column='AssemlyNo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Hardware_Assemly_Detail'

    def __str__(self):
        return f"HW Assembly Detail - {self.itemcode}: {self.description}"


class TblpmProjectHardwareMasterd(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    prjctno = models.TextField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    gendate = models.TextField(db_column='GenDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Hardware_MasterD'


class TblpmProjectHardwareMasterDetail(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    prjctno = models.IntegerField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    uom = models.TextField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    bomq = models.FloatField(db_column='BOMQ', blank=True, null=True)  # Field name made lowercase.
    rdesign = models.IntegerField(db_column='Rdesign', blank=True, null=True)  # Field name made lowercase.
    design = models.TextField(db_column='Design', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    remark = models.TextField(db_column='Remark', blank=True, null=True)  # Field name made lowercase.
    vendor1 = models.TextField(db_column='Vendor1', blank=True, null=True)  # Field name made lowercase.
    vendor2 = models.TextField(db_column='Vendor2', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Hardware_Master_Detail'


class TblpmProjectHardwareVendord(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    prjctno = models.TextField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    gendate = models.TextField(db_column='GenDate', blank=True, null=True)  # Field name made lowercase.
    vendorplan = models.TextField(db_column='VendorPlan', blank=True, null=True)  # Field name made lowercase.
    vendordate = models.TextField(db_column='VendorDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Hardware_VendorD'


class TblpmProjectManufacturingAssemlyDetail(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    prjctno = models.IntegerField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    uom = models.TextField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    bomq = models.FloatField(db_column='BOMQ', blank=True, null=True)  # Field name made lowercase.
    design = models.TextField(db_column='Design', blank=True, null=True)  # Field name made lowercase.
    vendorplandate = models.TextField(db_column='VendorPlanDate', blank=True, null=True)  # Field name made lowercase.
    vendoract = models.TextField(db_column='VendorAct', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    vendorplan = models.TextField(db_column='VendorPlan', blank=True, null=True)  # Field name made lowercase.
    assemlydate = models.TextField(db_column='AssemlyDate', blank=True, null=True)  # Field name made lowercase.
    remark = models.TextField(db_column='Remark', blank=True, null=True)  # Field name made lowercase.
    assemlyno = models.TextField(db_column='AssemlyNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Manufacturing_Assemly_Detail'


class TblpmProjectManufacturingAssemlyMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    prjctno = models.TextField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    gendate = models.TextField(db_column='GenDate', blank=True, null=True)  # Field name made lowercase.
    vendorplan = models.TextField(db_column='VendorPlan', blank=True, null=True)  # Field name made lowercase.
    vendordate = models.TextField(db_column='VendorDate', blank=True, null=True)  # Field name made lowercase.
    assemlydate = models.TextField(db_column='AssemlyDate', blank=True, null=True)  # Field name made lowercase.
    assemlyno = models.TextField(db_column='AssemlyNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Manufacturing_Assemly_Master'


class TblpmProjectManufacturingPlanDetail(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    prjctno = models.IntegerField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    uom = models.TextField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    bomq = models.FloatField(db_column='BOMQ', blank=True, null=True)  # Field name made lowercase.
    design = models.TextField(db_column='Design', blank=True, null=True)  # Field name made lowercase.
    vendorplandate = models.TextField(db_column='VendorPlanDate', blank=True, null=True)  # Field name made lowercase.
    vendoract = models.TextField(db_column='VendorAct', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    vendorplan = models.TextField(db_column='VendorPlan', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Manufacturing_Plan_Detail'


class TblpmProjectManufacturingVendord(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    prjctno = models.TextField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    gendate = models.TextField(db_column='GenDate', blank=True, null=True)  # Field name made lowercase.
    vendorplan = models.TextField(db_column='VendorPlan', blank=True, null=True)  # Field name made lowercase.
    vendordate = models.TextField(db_column='VendorDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Manufacturing_VendorD'


class TblpmProjectSiteMasterd(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    prjctno = models.TextField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    gendate = models.TextField(db_column='GenDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Site_MasterD'


class TblpmProjectSiteMasterDetail(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    prjctno = models.IntegerField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    uom = models.TextField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    bomq = models.FloatField(db_column='BOMQ', blank=True, null=True)  # Field name made lowercase.
    design = models.TextField(db_column='Design', blank=True, null=True)  # Field name made lowercase.
    manf = models.TextField(db_column='Manf', blank=True, null=True)  # Field name made lowercase.
    bop = models.TextField(db_column='BOP', blank=True, null=True)  # Field name made lowercase.
    assemly = models.TextField(db_column='Assemly', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    gendate = models.TextField(db_column='GenDate', blank=True, null=True)  # Field name made lowercase.
    hrs = models.FloatField(db_column='Hrs', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Site_Master_Detail'


class TblpmProjectVendorPlanDetail(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    prjctno = models.IntegerField(db_column='PRJCTNO', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.TextField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    uom = models.TextField(db_column='UOM', blank=True, null=True)  # Field name made lowercase.
    bomq = models.FloatField(db_column='BOMQ', blank=True, null=True)  # Field name made lowercase.
    design = models.TextField(db_column='Design', blank=True, null=True)  # Field name made lowercase.
    vendorplandate = models.TextField(db_column='VendorPlanDate', blank=True, null=True)  # Field name made lowercase.
    vendoract = models.TextField(db_column='VendorAct', blank=True, null=True)  # Field name made lowercase.
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    vendorplan = models.TextField(db_column='VendorPlan', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPM_Project_Vendor_Plan_Detail'
