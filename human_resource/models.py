from django.db import models

# Create your models here.

class Businessgroup(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.
    incharge = models.TextField(db_column='Incharge', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BusinessGroup'


class TblcvDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    fromdate = models.TextField(db_column='FromDate', blank=True, null=True)  # Field name made lowercase.
    fromtime = models.TextField(db_column='FromTime', blank=True, null=True)  # Field name made lowercase.
    totime = models.TextField(db_column='ToTime', blank=True, null=True)  # Field name made lowercase.
    type = models.TextField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    typeof = models.TextField(db_column='TypeOf', blank=True, null=True)  # Field name made lowercase.
    typefor = models.TextField(db_column='TypeFor', blank=True, null=True)  # Field name made lowercase.
    place = models.TextField(db_column='Place', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.TextField(db_column='ContactPerson', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', blank=True, null=True)  # Field name made lowercase.
    feedback = models.TextField(db_column='Feedback', blank=True, null=True)  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.
    adharcard = models.TextField(db_column='Adharcard', blank=True, null=True)  # Field name made lowercase.
    pan = models.TextField(db_column='PAN', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCV_Details'


class TblcvReason(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', blank=True, null=True)  # Field name made lowercase.
    wono = models.IntegerField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    enquiry = models.IntegerField(db_column='Enquiry', blank=True, null=True)  # Field name made lowercase.
    other = models.IntegerField(db_column='Other', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCV_Reason'


class TblcvPass(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    gpno = models.TextField(db_column='GPNo', blank=True, null=True)  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.
    authorize = models.IntegerField(db_column='Authorize', blank=True, null=True)  # Field name made lowercase.
    authorizedby = models.TextField(db_column='AuthorizedBy', blank=True, null=True)  # Field name made lowercase.
    authorizedate = models.TextField(db_column='AuthorizeDate', blank=True, null=True)  # Field name made lowercase.
    authorizetime = models.TextField(db_column='AuthorizeTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCV_pass'


class TblgatepassDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    fromdate = models.TextField(db_column='FromDate', blank=True, null=True)  # Field name made lowercase.
    fromtime = models.TextField(db_column='FromTime', blank=True, null=True)  # Field name made lowercase.
    totime = models.TextField(db_column='ToTime', blank=True, null=True)  # Field name made lowercase.
    type = models.IntegerField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    typeof = models.IntegerField(db_column='TypeOf', blank=True, null=True)  # Field name made lowercase.
    typefor = models.TextField(db_column='TypeFor', blank=True, null=True)  # Field name made lowercase.
    place = models.TextField(db_column='Place', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.TextField(db_column='ContactPerson', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', blank=True, null=True)  # Field name made lowercase.
    feedback = models.TextField(db_column='Feedback', blank=True, null=True)  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblGatePass_Details'


class TblgatepassReason(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', blank=True, null=True)  # Field name made lowercase.
    wono = models.IntegerField(db_column='WONo', blank=True, null=True)  # Field name made lowercase.
    enquiry = models.IntegerField(db_column='Enquiry', blank=True, null=True)  # Field name made lowercase.
    other = models.IntegerField(db_column='Other', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblGatePass_Reason'


class TblgatePass(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    gpno = models.TextField(db_column='GPNo', blank=True, null=True)  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.
    authorize = models.IntegerField(db_column='Authorize', blank=True, null=True)  # Field name made lowercase.
    authorizedby = models.TextField(db_column='AuthorizedBy', blank=True, null=True)  # Field name made lowercase.
    authorizedate = models.TextField(db_column='AuthorizeDate', blank=True, null=True)  # Field name made lowercase.
    authorizetime = models.TextField(db_column='AuthorizeTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblGate_Pass'


class TblhrAssetCamera(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    location = models.TextField(db_column='LOCATION', blank=True, null=True)  # Field name made lowercase.
    camera_num = models.TextField(db_column='CAMERA_NUM', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_CAMERA'


class TblhrAssetDesktop(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    ip_add = models.TextField(db_column='IP_add', blank=True, null=True)  # Field name made lowercase.
    pcno = models.TextField(db_column='PCNO', blank=True, null=True)  # Field name made lowercase.
    username = models.TextField(db_column='UserName', blank=True, null=True)  # Field name made lowercase.
    model = models.TextField(db_column='MODEL', blank=True, null=True)  # Field name made lowercase.
    processor = models.TextField(db_column='Processor', blank=True, null=True)  # Field name made lowercase.
    motherboard = models.TextField(db_column='MotherBoard', blank=True, null=True)  # Field name made lowercase.
    hdd = models.TextField(db_column='HDD', blank=True, null=True)  # Field name made lowercase.
    ram = models.TextField(db_column='RAM', blank=True, null=True)  # Field name made lowercase.
    cd_dvd = models.TextField(db_column='CD_DVD', blank=True, null=True)  # Field name made lowercase.
    mouse = models.TextField(db_column='MOUSE', blank=True, null=True)  # Field name made lowercase.
    keyboard = models.TextField(db_column='KEYBOARD', blank=True, null=True)  # Field name made lowercase.
    monitor = models.TextField(db_column='MONITOR', blank=True, null=True)  # Field name made lowercase.
    cabinet = models.TextField(db_column='CABINET', blank=True, null=True)  # Field name made lowercase.
    graphic_card = models.TextField(db_column='GRAPHIC_CARD', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_DESKTOP'


class TblhrAssetLaptop(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    asset_no = models.TextField(db_column='ASSET_NO', blank=True, null=True)  # Field name made lowercase.
    ip_add = models.TextField(db_column='IP_ADD', blank=True, null=True)  # Field name made lowercase.
    pcno = models.TextField(db_column='PCNO', blank=True, null=True)  # Field name made lowercase.
    user_name = models.TextField(db_column='USER_NAME', blank=True, null=True)  # Field name made lowercase.
    model = models.TextField(db_column='MODEL', blank=True, null=True)  # Field name made lowercase.
    processor = models.TextField(db_column='PROCESSOR', blank=True, null=True)  # Field name made lowercase.
    mother_board = models.TextField(db_column='MOTHER_BOARD', blank=True, null=True)  # Field name made lowercase.
    hdd = models.TextField(db_column='HDD', blank=True, null=True)  # Field name made lowercase.
    ram = models.TextField(db_column='RAM', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_LAPTOP'


class TblhrAssetPrinter(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    printer_name = models.TextField(db_column='PRINTER_NAME', blank=True, null=True)  # Field name made lowercase.
    asset_no = models.TextField(db_column='ASSET_NO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_PRINTER'


class TblhrAssetProjector(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    asset_no = models.TextField(db_column='ASSET_NO', blank=True, null=True)  # Field name made lowercase.
    projector = models.TextField(db_column='PROJECTOR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_PROJECTOR'


class TblhrAssetPunching(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    asset_no = models.TextField(db_column='ASSET_NO', blank=True, null=True)  # Field name made lowercase.
    punching_machine = models.TextField(db_column='PUNCHING_MACHINE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_PUNCHING'


class TblhrAssetRouter(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    asset_no = models.TextField(db_column='ASSET_NO', blank=True, null=True)  # Field name made lowercase.
    router = models.TextField(db_column='ROUTER', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_ROUTER'


class TblhrAssetSaplnas(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    asset_no = models.TextField(db_column='ASSET_NO', blank=True, null=True)  # Field name made lowercase.
    storage = models.TextField(db_column='STORAGE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_SAPLNAS'


class TblhrAssetSwitches(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    dept = models.TextField(db_column='DEPT', blank=True, null=True)  # Field name made lowercase.
    asset_no = models.TextField(db_column='ASSET_NO', blank=True, null=True)  # Field name made lowercase.
    switches = models.TextField(db_column='SWITCHES', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_ASSET_SWITCHES'


class TblhrBankloan(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId', blank=True, null=True)  # Field name made lowercase.
    bankname = models.TextField(db_column='BankName', blank=True, null=True)  # Field name made lowercase.
    branch = models.TextField(db_column='Branch', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    installment = models.FloatField(db_column='Installment', blank=True, null=True)  # Field name made lowercase.
    fromdate = models.TextField(db_column='fromDate', blank=True, null=True)  # Field name made lowercase.
    todate = models.TextField(db_column='ToDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_BankLoan'


class TblhrCoporatemobileno(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mobileno = models.TextField(db_column='MobileNo', blank=True, null=True)  # Field name made lowercase.
    limitamt = models.FloatField(db_column='LimitAmt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_CoporateMobileNo'


class TblhrDepartments(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Departments'


class TblhrDesignation(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    type = models.TextField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Designation'


class TblhrDutyhour(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    hours = models.FloatField(db_column='Hours', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_DutyHour'


class TblhrEmptype(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_EmpType'


class TblhrGrade(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Grade'


class TblhrHolidayMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    hdate = models.TextField(db_column='HDate', blank=True, null=True)  # Field name made lowercase.
    title = models.TextField(db_column='Title', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Holiday_Master'


class TblhrIncludesin(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    includesin = models.TextField(db_column='IncludesIn', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_IncludesIn'


class TblhrIncrementAccessories(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId')  # Field name made lowercase.
    offermid = models.IntegerField(db_column='OfferMId')  # Field name made lowercase.
    perticulars = models.TextField(db_column='Perticulars', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    includesin = models.IntegerField(db_column='IncludesIn', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Increment_Accessories'


class TblhrIncrementMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    offerid = models.IntegerField(db_column='OfferId')  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    employeename = models.TextField(db_column='EmployeeName', blank=True, null=True)  # Field name made lowercase.
    stafftype = models.IntegerField(db_column='StaffType', blank=True, null=True)  # Field name made lowercase.
    typeof = models.IntegerField(db_column='TypeOf', blank=True, null=True)  # Field name made lowercase.
    salary = models.FloatField(blank=True, null=True)
    dutyhrs = models.FloatField(db_column='DutyHrs', blank=True, null=True)  # Field name made lowercase.
    othrs = models.FloatField(db_column='OTHrs', blank=True, null=True)  # Field name made lowercase.
    overtime = models.IntegerField(db_column='OverTime', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    emailid = models.TextField(db_column='EmailId', blank=True, null=True)  # Field name made lowercase.
    interviewedby = models.TextField(db_column='InterviewedBy', blank=True, null=True)  # Field name made lowercase.
    authorizedby = models.TextField(db_column='AuthorizedBy', blank=True, null=True)  # Field name made lowercase.
    referenceby = models.TextField(db_column='ReferenceBy', blank=True, null=True)  # Field name made lowercase.
    designation = models.IntegerField(db_column='Designation', blank=True, null=True)  # Field name made lowercase.
    exgratia = models.FloatField(db_column='ExGratia', blank=True, null=True)  # Field name made lowercase.
    vehicleallowance = models.FloatField(db_column='VehicleAllowance', blank=True, null=True)  # Field name made lowercase.
    lta = models.FloatField(db_column='LTA', blank=True, null=True)  # Field name made lowercase.
    loyalty = models.FloatField(db_column='Loyalty', blank=True, null=True)  # Field name made lowercase.
    paidleaves = models.FloatField(db_column='PaidLeaves', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=50, blank=True, null=True)  # Field name made lowercase.
    headertext = models.TextField(db_column='HeaderText', blank=True, null=True)  # Field name made lowercase.
    footertext = models.TextField(db_column='FooterText', blank=True, null=True)  # Field name made lowercase.
    bonus = models.FloatField(db_column='Bonus', blank=True, null=True)  # Field name made lowercase.
    attbonusper1 = models.FloatField(db_column='AttBonusPer1', blank=True, null=True)  # Field name made lowercase.
    attbonusper2 = models.FloatField(db_column='AttBonusPer2', blank=True, null=True)  # Field name made lowercase.
    pfemployee = models.FloatField(db_column='PFEmployee', blank=True, null=True)  # Field name made lowercase.
    pfcompany = models.FloatField(db_column='PFCompany', blank=True, null=True)  # Field name made lowercase.
    increment = models.IntegerField(db_column='Increment', blank=True, null=True)  # Field name made lowercase.
    incrementfortheyear = models.TextField(db_column='IncrementForTheYear', blank=True, null=True)  # Field name made lowercase.
    effectfrom = models.TextField(db_column='EffectFrom', blank=True, null=True)  # Field name made lowercase.
    esi = models.FloatField(db_column='ESI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Increment_Master'


class TblhrIntercomext(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    extno = models.TextField(db_column='ExtNo', blank=True, null=True)  # Field name made lowercase.
    department = models.IntegerField(db_column='Department', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_IntercomExt'


class TblhrMobilebill(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    empid = models.CharField(db_column='EmpId', max_length=50)  # Field name made lowercase.
    billmonth = models.FloatField(db_column='BillMonth', blank=True, null=True)  # Field name made lowercase.
    billamt = models.FloatField(db_column='BillAmt', blank=True, null=True)  # Field name made lowercase.
    taxes = models.FloatField(db_column='Taxes', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_MobileBill'


class TblhrNewsNotices(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    title = models.TextField(db_column='Title', blank=True, null=True)  # Field name made lowercase.
    indetails = models.TextField(db_column='InDetails', blank=True, null=True)  # Field name made lowercase.
    fromdate = models.CharField(db_column='FromDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    todate = models.CharField(db_column='ToDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    filename = models.TextField(db_column='FileName', blank=True, null=True)  # Field name made lowercase.
    filesize = models.FloatField(db_column='FileSize', blank=True, null=True)  # Field name made lowercase.
    contenttype = models.TextField(db_column='ContentType', blank=True, null=True)  # Field name made lowercase.
    filedata = models.BinaryField(db_column='FileData', blank=True, null=True)  # Field name made lowercase.
    flag = models.IntegerField(db_column='Flag', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_News_Notices'


class TblhrOthour(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    hours = models.FloatField(db_column='Hours', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_OTHour'


class TblhrOfferAccessories(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId')  # Field name made lowercase.
    perticulars = models.TextField(db_column='Perticulars', blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    includesin = models.IntegerField(db_column='IncludesIn', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Offer_Accessories'


class TblhrOfferMaster(models.Model):
    offerid = models.AutoField(db_column='OfferId', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate', blank=True, null=True)  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    employeename = models.TextField(db_column='EmployeeName', blank=True, null=True)  # Field name made lowercase.
    stafftype = models.IntegerField(db_column='StaffType', blank=True, null=True)  # Field name made lowercase.
    typeof = models.IntegerField(db_column='TypeOf', blank=True, null=True)  # Field name made lowercase.
    salary = models.FloatField(blank=True, null=True)
    dutyhrs = models.FloatField(db_column='DutyHrs', blank=True, null=True)  # Field name made lowercase.
    othrs = models.FloatField(db_column='OTHrs', blank=True, null=True)  # Field name made lowercase.
    overtime = models.IntegerField(db_column='OverTime', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    emailid = models.TextField(db_column='EmailId', blank=True, null=True)  # Field name made lowercase.
    interviewedby = models.TextField(db_column='InterviewedBy', blank=True, null=True)  # Field name made lowercase.
    authorizedby = models.TextField(db_column='AuthorizedBy', blank=True, null=True)  # Field name made lowercase.
    referenceby = models.TextField(db_column='ReferenceBy', blank=True, null=True)  # Field name made lowercase.
    designation = models.IntegerField(db_column='Designation', blank=True, null=True)  # Field name made lowercase.
    exgratia = models.FloatField(db_column='ExGratia', blank=True, null=True)  # Field name made lowercase.
    vehicleallowance = models.FloatField(db_column='VehicleAllowance', blank=True, null=True)  # Field name made lowercase.
    lta = models.FloatField(db_column='LTA', blank=True, null=True)  # Field name made lowercase.
    loyalty = models.FloatField(db_column='Loyalty', blank=True, null=True)  # Field name made lowercase.
    paidleaves = models.FloatField(db_column='PaidLeaves', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=50, blank=True, null=True)  # Field name made lowercase.
    headertext = models.TextField(db_column='HeaderText', blank=True, null=True)  # Field name made lowercase.
    footertext = models.TextField(db_column='FooterText', blank=True, null=True)  # Field name made lowercase.
    bonus = models.FloatField(db_column='Bonus', blank=True, null=True)  # Field name made lowercase.
    attbonusper1 = models.FloatField(db_column='AttBonusPer1', blank=True, null=True)  # Field name made lowercase.
    attbonusper2 = models.FloatField(db_column='AttBonusPer2', blank=True, null=True)  # Field name made lowercase.
    pfemployee = models.FloatField(db_column='PFEmployee', blank=True, null=True)  # Field name made lowercase.
    pfcompany = models.FloatField(db_column='PFCompany', blank=True, null=True)  # Field name made lowercase.
    increment = models.IntegerField(db_column='Increment', blank=True, null=True)  # Field name made lowercase.
    incrementfortheyear = models.TextField(db_column='IncrementForTheYear', blank=True, null=True)  # Field name made lowercase.
    effectfrom = models.TextField(db_column='EffectFrom', blank=True, null=True)  # Field name made lowercase.
    esi = models.FloatField(db_column='ESI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Offer_Master'


class TblhrOfficestaff(models.Model):
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    offerid = models.IntegerField(db_column='OfferId', blank=True, null=True)  # Field name made lowercase.
    empid = models.CharField(db_column='EmpId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    sessionid = models.CharField(db_column='SessionId', max_length=50)  # Field name made lowercase.
    title = models.TextField(db_column='Title', blank=True, null=True)  # Field name made lowercase.
    employeename = models.TextField(db_column='EmployeeName', blank=True, null=True)  # Field name made lowercase.
    swapcardno = models.TextField(db_column='SwapCardNo', blank=True, null=True)  # Field name made lowercase.
    department = models.IntegerField(db_column='Department', blank=True, null=True)  # Field name made lowercase.
    bggroup = models.IntegerField(db_column='BGGroup', blank=True, null=True)  # Field name made lowercase.
    directorsname = models.TextField(db_column='DirectorsName', blank=True, null=True)  # Field name made lowercase.
    depthead = models.TextField(db_column='DeptHead', blank=True, null=True)  # Field name made lowercase.
    groupleader = models.TextField(db_column='GroupLeader', blank=True, null=True)  # Field name made lowercase.
    designation = models.TextField(db_column='Designation', blank=True, null=True)  # Field name made lowercase.
    grade = models.TextField(db_column='Grade', blank=True, null=True)  # Field name made lowercase.
    mobileno = models.TextField(db_column='MobileNo', blank=True, null=True)  # Field name made lowercase.
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)  # Field name made lowercase.
    companyemail = models.TextField(db_column='CompanyEmail', blank=True, null=True)  # Field name made lowercase.
    emailid1 = models.TextField(db_column='EmailId1', blank=True, null=True)  # Field name made lowercase.
    extensionno = models.TextField(db_column='ExtensionNo', blank=True, null=True)  # Field name made lowercase.
    joiningdate = models.CharField(db_column='JoiningDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    resignationdate = models.CharField(db_column='ResignationDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    photofilename = models.TextField(db_column='PhotoFileName', blank=True, null=True)  # Field name made lowercase.
    photosize = models.TextField(db_column='PhotoSize', blank=True, null=True)  # Field name made lowercase.
    photocontenttype = models.TextField(db_column='PhotoContentType', blank=True, null=True)  # Field name made lowercase.
    photodata = models.BinaryField(db_column='PhotoData', blank=True, null=True)  # Field name made lowercase.
    permanentaddress = models.TextField(db_column='PermanentAddress', blank=True, null=True)  # Field name made lowercase.
    correspondenceaddress = models.TextField(db_column='CorrespondenceAddress', blank=True, null=True)  # Field name made lowercase.
    emailid2 = models.TextField(db_column='EmailId2', blank=True, null=True)  # Field name made lowercase.
    dateofbirth = models.TextField(db_column='DateOfBirth', blank=True, null=True)  # Field name made lowercase.
    gender = models.TextField(db_column='Gender', blank=True, null=True)  # Field name made lowercase.
    martialstatus = models.TextField(db_column='MartialStatus', blank=True, null=True)  # Field name made lowercase.
    bloodgroup = models.TextField(db_column='BloodGroup', blank=True, null=True)  # Field name made lowercase.
    height = models.TextField(db_column='Height', blank=True, null=True)  # Field name made lowercase.
    weight = models.TextField(db_column='Weight', blank=True, null=True)  # Field name made lowercase.
    physicallyhandycapped = models.TextField(db_column='PhysicallyHandycapped', blank=True, null=True)  # Field name made lowercase.
    religion = models.TextField(db_column='Religion', blank=True, null=True)  # Field name made lowercase.
    cast = models.TextField(db_column='Cast', blank=True, null=True)  # Field name made lowercase.
    educationalqualification = models.TextField(db_column='EducationalQualification', blank=True, null=True)  # Field name made lowercase.
    additionalqualification = models.TextField(db_column='AdditionalQualification', blank=True, null=True)  # Field name made lowercase.
    lastcompanyname = models.TextField(db_column='LastCompanyName', blank=True, null=True)  # Field name made lowercase.
    workingduration = models.TextField(db_column='WorkingDuration', blank=True, null=True)  # Field name made lowercase.
    totalexperience = models.TextField(db_column='TotalExperience', blank=True, null=True)  # Field name made lowercase.
    currentctc = models.TextField(db_column='CurrentCTC', blank=True, null=True)  # Field name made lowercase.
    cvfilename = models.TextField(db_column='CVFileName', blank=True, null=True)  # Field name made lowercase.
    cvsize = models.TextField(db_column='CVSize', blank=True, null=True)  # Field name made lowercase.
    cvcontenttype = models.TextField(db_column='CVContentType', blank=True, null=True)  # Field name made lowercase.
    cvdata = models.BinaryField(db_column='CVData', blank=True, null=True)  # Field name made lowercase.
    bankaccountno = models.TextField(db_column='BankAccountNo', blank=True, null=True)  # Field name made lowercase.
    pfno = models.TextField(db_column='PFNo', blank=True, null=True)  # Field name made lowercase.
    panno = models.TextField(db_column='PANNo', blank=True, null=True)  # Field name made lowercase.
    passportno = models.TextField(db_column='PassPortNo', blank=True, null=True)  # Field name made lowercase.
    expirydate = models.CharField(db_column='ExpiryDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    additionalinformation = models.TextField(db_column='AdditionalInformation', blank=True, null=True)  # Field name made lowercase.
    wr = models.TextField(db_column='WR', blank=True, null=True)  # Field name made lowercase.
    da = models.TextField(db_column='DA', blank=True, null=True)  # Field name made lowercase.
    custlogin = models.TextField(db_column='CustLogin', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_OfficeStaff'


class TblhrOvertime(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_OverTime'


class TblhrPfSlab(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    pfemployee = models.FloatField(db_column='PFEmployee', blank=True, null=True)  # Field name made lowercase.
    pfcompany = models.FloatField(db_column='PFCompany', blank=True, null=True)  # Field name made lowercase.
    active = models.IntegerField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_PF_Slab'


class TblhrPolicy(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId', blank=True, null=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)  # Field name made lowercase.
    cvfilename = models.TextField(db_column='CVFileName', blank=True, null=True)  # Field name made lowercase.
    cvsize = models.TextField(db_column='CVSize', blank=True, null=True)  # Field name made lowercase.
    cvcontenttype = models.TextField(db_column='CVContentType', blank=True, null=True)  # Field name made lowercase.
    cvdata = models.BinaryField(db_column='CVData', blank=True, null=True)  # Field name made lowercase.
    cvdate = models.TextField(db_column='CVDate', blank=True, null=True)  # Field name made lowercase.
    cvname = models.TextField(db_column='CVName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_POLICY'


class TblhrSalaryDetails(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    present = models.FloatField(db_column='Present', blank=True, null=True)  # Field name made lowercase.
    absent = models.FloatField(db_column='Absent', blank=True, null=True)  # Field name made lowercase.
    latein = models.FloatField(db_column='LateIn', blank=True, null=True)  # Field name made lowercase.
    halfday = models.FloatField(db_column='HalfDay', blank=True, null=True)  # Field name made lowercase.
    sunday = models.FloatField(db_column='Sunday', blank=True, null=True)  # Field name made lowercase.
    coff = models.FloatField(db_column='Coff', blank=True, null=True)  # Field name made lowercase.
    pl = models.FloatField(db_column='PL', blank=True, null=True)  # Field name made lowercase.
    overtimehrs = models.FloatField(db_column='OverTimeHrs', blank=True, null=True)  # Field name made lowercase.
    overtimerate = models.FloatField(db_column='OverTimeRate', blank=True, null=True)  # Field name made lowercase.
    installment = models.FloatField(db_column='Installment', blank=True, null=True)  # Field name made lowercase.
    mobileexeamt = models.FloatField(db_column='MobileExeAmt', blank=True, null=True)  # Field name made lowercase.
    addition = models.FloatField(db_column='Addition', blank=True, null=True)  # Field name made lowercase.
    remarks1 = models.TextField(db_column='Remarks1', blank=True, null=True)  # Field name made lowercase.
    deduction = models.FloatField(db_column='Deduction', blank=True, null=True)  # Field name made lowercase.
    remarks2 = models.TextField(db_column='Remarks2', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('TblhrSalaryMaster', models.DO_NOTHING, db_column='MId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Salary_Details'


class TblhrSalaryMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sysdate = models.TextField(db_column='SysDate')  # Field name made lowercase.
    systime = models.TextField(db_column='SysTime')  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearId')  # Field name made lowercase.
    empid = models.TextField(db_column='EmpId')  # Field name made lowercase.
    fmonth = models.IntegerField(db_column='FMonth')  # Field name made lowercase.
    increment = models.IntegerField(db_column='Increment', blank=True, null=True)  # Field name made lowercase.
    releaseflag = models.IntegerField(db_column='ReleaseFlag', blank=True, null=True)  # Field name made lowercase.
    chequeno = models.TextField(db_column='ChequeNo', blank=True, null=True)  # Field name made lowercase.
    chequenodate = models.TextField(db_column='ChequeNoDate', blank=True, null=True)  # Field name made lowercase.
    bankid = models.IntegerField(db_column='BankId', blank=True, null=True)  # Field name made lowercase.
    empdirect = models.TextField(db_column='EmpDirect', blank=True, null=True)  # Field name made lowercase.
    transno = models.IntegerField(db_column='TransNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_Salary_Master'


class TblhrSwapcard(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    swapcardno = models.TextField(db_column='SwapCardNo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_SwapCard'


class TblhrWorkingdays(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)  # Field name made lowercase.
    finyearid = models.IntegerField(db_column='FinYearid', blank=True, null=True)  # Field name made lowercase.
    monthid = models.IntegerField(db_column='MonthId', blank=True, null=True)  # Field name made lowercase.
    days = models.FloatField(db_column='Days', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHR_WorkingDays'



class TblApprisalform1(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    dept = models.TextField(db_column='Dept', blank=True, null=True)  # Field name made lowercase.
    designation = models.TextField(db_column='Designation', blank=True, null=True)  # Field name made lowercase.
    aperiod = models.TextField(db_column='Aperiod', blank=True, null=True)  # Field name made lowercase.
    grade = models.TextField(db_column='Grade', blank=True, null=True)  # Field name made lowercase.
    joiningdate = models.TextField(db_column='JoiningDate', blank=True, null=True)  # Field name made lowercase.
    jobr = models.TextField(db_column='JobR', blank=True, null=True)  # Field name made lowercase.
    speciachv = models.TextField(db_column='SpeciAchv', blank=True, null=True)  # Field name made lowercase.
    losscomp = models.TextField(blank=True, null=True)
    part = models.TextField(db_column='Part', blank=True, null=True)  # Field name made lowercase.
    deniedonsite = models.TextField(db_column='Deniedonsite', blank=True, null=True)  # Field name made lowercase.
    leavewp = models.TextField(db_column='LeaveWP', blank=True, null=True)  # Field name made lowercase.
    strength = models.TextField(db_column='Strength', blank=True, null=True)  # Field name made lowercase.
    weekness = models.TextField(db_column='Weekness', blank=True, null=True)  # Field name made lowercase.
    trainr = models.TextField(db_column='TrainR', blank=True, null=True)  # Field name made lowercase.
    currctc = models.TextField(db_column='CurrCTC', blank=True, null=True)  # Field name made lowercase.
    expectedctc = models.TextField(db_column='ExpectedCTC', blank=True, null=True)  # Field name made lowercase.
    totalhrs = models.TextField(db_column='TotalHrs', blank=True, null=True)  # Field name made lowercase.
    totalhrspref = models.TextField(db_column='TotalHrsPref', blank=True, null=True)  # Field name made lowercase.
    lastincdate = models.TextField(db_column='LastIncDate', blank=True, null=True)  # Field name made lowercase.
    totalyrsexp = models.TextField(db_column='TotalYrsExp', blank=True, null=True)  # Field name made lowercase.
    totalyrsexpsapl = models.TextField(db_column='TotalYrsExpSAPL', blank=True, null=True)  # Field name made lowercase.
    homesalmon = models.TextField(db_column='HomeSalMon', blank=True, null=True)  # Field name made lowercase.
    highqua = models.TextField(db_column='HighQua', blank=True, null=True)  # Field name made lowercase.
    empcom = models.TextField(db_column='EmpCom', blank=True, null=True)  # Field name made lowercase.
    noticeperoffletr = models.TextField(db_column='NoticePerOffletr', blank=True, null=True)  # Field name made lowercase.
    plpend = models.TextField(db_column='PLpend', blank=True, null=True)  # Field name made lowercase.
    coffpend = models.TextField(db_column='COffPend', blank=True, null=True)  # Field name made lowercase.
    rollocas = models.TextField(db_column='RollOCas', blank=True, null=True)  # Field name made lowercase.
    apptimeletter = models.TextField(db_column='AppTimeLetter', blank=True, null=True)  # Field name made lowercase.
    eligiblefasi = models.TextField(db_column='EligibleFasi', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tbl_ApprisalForm1'


class TblaccTourintimationMaster(models.Model):
    """
    Tour Intimation Master - Employee tour requests and tracking
    Source: Accounts module (tblACC_TourIntimation_Master)
    Used in HR Transactions for tour management
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.TextField(db_column='SysDate')
    systime = models.TextField(db_column='SysTime')
    sessionid = models.TextField(db_column='SessionId')
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    tino = models.TextField(db_column='TINo', blank=True, null=True)  # Tour Intimation Number
    empid = models.TextField(db_column='EmpId', blank=True, null=True)
    type = models.IntegerField(db_column='Type', blank=True, null=True)
    wono = models.TextField(db_column='WONo', blank=True, null=True)  # Work Order Number
    bggroupid = models.IntegerField(db_column='BGGroupId', blank=True, null=True)  # Business Group
    projectname = models.TextField(db_column='ProjectName', blank=True, null=True)
    tourstartdate = models.TextField(db_column='TourStartDate', blank=True, null=True)
    tourstarttime = models.TextField(db_column='TourStartTime', blank=True, null=True)
    tourenddate = models.TextField(db_column='TourEndDate', blank=True, null=True)
    tourendtime = models.TextField(db_column='TourEndTime', blank=True, null=True)
    noofdays = models.IntegerField(db_column='NoOfDays', blank=True, null=True)
    nameaddressserprovider = models.TextField(db_column='NameAddressSerProvider', blank=True, null=True)  # Service Provider
    contactperson = models.TextField(db_column='ContactPerson', blank=True, null=True)
    contactno = models.TextField(db_column='ContactNo', blank=True, null=True)
    email = models.TextField(db_column='Email', blank=True, null=True)
    placeoftourcountry = models.IntegerField(db_column='PlaceOfTourCountry')
    placeoftourstate = models.IntegerField(db_column='PlaceOfTourState')
    placeoftourcity = models.IntegerField(db_column='PlaceOfTourCity')

    class Meta:
        managed = False
        db_table = 'tblACC_TourIntimation_Master'
