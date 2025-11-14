
from django.db import models


class Tblcountry(models.Model):
    cid = models.AutoField(db_column='CId', primary_key=True)  # Field name made lowercase.
    countryname = models.TextField(db_column='CountryName', blank=True, null=True)  # Field name made lowercase.
    currency = models.TextField(db_column='Currency', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.
    keyshortcut = models.TextField(db_column='KeyShortcut', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCountry'

    def __str__(self):
        return self.countryname or f"Country {self.cid}"


class Tblstate(models.Model):
    sid = models.AutoField(db_column='SId', primary_key=True)  # Field name made lowercase.
    statename = models.TextField(db_column='StateName', blank=True, null=True)  # Field name made lowercase.
    cid = models.ForeignKey(Tblcountry, models.DO_NOTHING, db_column='CId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblState'

    def __str__(self):
        return self.statename or f"State {self.sid}"


class Tblcity(models.Model):
    cityid = models.AutoField(db_column='CityId', primary_key=True)  # Field name made lowercase.
    cityname = models.TextField(db_column='CityName', blank=True, null=True)  # Field name made lowercase.
    sid = models.ForeignKey('Tblstate', models.DO_NOTHING, db_column='SId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCity'

    def __str__(self):
        return self.cityname or f"City {self.cityid}"



class TblcompanyMaster(models.Model):
    compid = models.AutoField(db_column='CompId', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    companyname = models.TextField(db_column='CompanyName')  # Field name made lowercase.
    regdaddress = models.TextField(db_column='RegdAddress', blank=True, null=True)  # Field name made lowercase.
    regdstate = models.IntegerField(db_column='RegdState')  # Field name made lowercase.
    regdcountry = models.IntegerField(db_column='RegdCountry')  # Field name made lowercase.
    regdpincode = models.TextField(db_column='RegdPinCode', blank=True, null=True)  # Field name made lowercase.
    regdcontactno = models.TextField(db_column='RegdContactNo', blank=True, null=True)  # Field name made lowercase.
    regdfaxno = models.TextField(db_column='RegdFaxNo', blank=True, null=True)  # Field name made lowercase.
    regdemail = models.TextField(db_column='RegdEmail', blank=True, null=True)  # Field name made lowercase.
    plantaddress = models.TextField(db_column='PlantAddress', blank=True, null=True)  # Field name made lowercase.
    plantstate = models.IntegerField(db_column='PlantState')  # Field name made lowercase.
    plantcountry = models.IntegerField(db_column='PlantCountry')  # Field name made lowercase.
    plantpincode = models.TextField(db_column='PlantPinCode', blank=True, null=True)  # Field name made lowercase.
    plantcontactno = models.TextField(db_column='PlantContactNo', blank=True, null=True)  # Field name made lowercase.
    plantfaxno = models.TextField(db_column='PlantFaxNo', blank=True, null=True)  # Field name made lowercase.
    plantemail = models.TextField(db_column='PlantEmail', blank=True, null=True)  # Field name made lowercase.
    eccno = models.TextField(db_column='ECCNo', blank=True, null=True)  # Field name made lowercase.
    commissionerate = models.TextField(db_column='Commissionerate', blank=True, null=True)  # Field name made lowercase.
    range = models.TextField(db_column='Range', blank=True, null=True)  # Field name made lowercase.
    division = models.TextField(db_column='Division', blank=True, null=True)  # Field name made lowercase.
    locationno = models.TextField(db_column='LocationNo', blank=True, null=True)  # Field name made lowercase.
    vat = models.TextField(db_column='VAT', blank=True, null=True)  # Field name made lowercase.
    cstno = models.TextField(db_column='CSTNo', blank=True, null=True)  # Field name made lowercase.
    panno = models.TextField(db_column='PANNo', blank=True, null=True)  # Field name made lowercase.
    logoimage = models.BinaryField(db_column='LogoImage', blank=True, null=True)  # Field name made lowercase.
    logofilename = models.TextField(db_column='LogoFileName', blank=True, null=True)  # Field name made lowercase.
    prefix = models.TextField(db_column='Prefix', blank=True, null=True)  # Field name made lowercase.
    licencenos = models.TextField(db_column='LicenceNos', blank=True, null=True)  # Field name made lowercase.
    defaultcomp = models.IntegerField(db_column='DefaultComp', blank=True, null=True)  # Field name made lowercase.
    mailserverip = models.TextField(db_column='MailServerIp', blank=True, null=True)  # Field name made lowercase.
    serverip = models.TextField(db_column='ServerIp', blank=True, null=True)  # Field name made lowercase.
    flag = models.IntegerField(db_column='Flag', blank=True, null=True)  # Field name made lowercase.
    itemcodelimit = models.IntegerField(db_column='ItemCodeLimit', blank=True, null=True)  # Field name made lowercase.
    erpsysmail = models.TextField(db_column='ErpSysmail', blank=True, null=True)  # Field name made lowercase.
    mobileno = models.TextField(db_column='MobileNo', blank=True, null=True)  # Field name made lowercase.
    password = models.TextField(db_column='Password', blank=True, null=True)  # Field name made lowercase.
    plantcity = models.ForeignKey(Tblcity, models.DO_NOTHING, db_column='PlantCity')  # Field name made lowercase.
    regdcity = models.ForeignKey(Tblcity, models.DO_NOTHING, db_column='RegdCity', related_name='tblcompanymaster_regdcity_set')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCompany_master'



class TblfinancialMaster(models.Model):
    finyearid = models.AutoField(db_column='FinYearId', primary_key=True)  # Field name made lowercase.
    sysdate = models.CharField(db_column='SysDate', max_length=50)  # Field name made lowercase.
    systime = models.CharField(db_column='SysTime', max_length=50)  # Field name made lowercase.
    sessionid = models.TextField(db_column='SessionId')  # Field name made lowercase.
    compid = models.IntegerField(db_column='CompId')  # Field name made lowercase.
    finyearfrom = models.CharField(db_column='FinYearFrom', max_length=50, blank=True, null=True)  # Field name made lowercase.
    finyearto = models.CharField(db_column='FinYearTo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    finyear = models.CharField(db_column='FinYear', max_length=50, blank=True, null=True)  # Field name made lowercase.
    flag = models.IntegerField(db_column='Flag', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFinancial_master'
        ordering = ['-finyearfrom']
    
    def __str__(self):
        return f"{self.finyear} ({self.finyearfrom} - {self.finyearto})"
    
    def get_company(self):
        """Get the company object for this financial year."""
        return TblcompanyMaster.objects.filter(compid=self.compid).first()
    
    def is_closed(self):
        """Check if this financial year is closed (flag=0 means closed)."""
        return self.flag == 0
    
    def get_from_date(self):
        """Parse and return the from date as a date object."""
        from datetime import datetime
        try:
            return datetime.strptime(self.finyearfrom, '%d/%m/%Y').date()
        except (ValueError, TypeError):
            return None
    
    def get_to_date(self):
        """Parse and return the to date as a date object."""
        from datetime import datetime
        try:
            return datetime.strptime(self.finyearto, '%d/%m/%Y').date()
        except (ValueError, TypeError):
            return None


class UnitMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    unitname = models.TextField(db_column='UnitName', blank=True, null=True)  # Field name made lowercase.
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)  # Field name made lowercase.
    effectoninvoice = models.IntegerField(db_column='EffectOnInvoice', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Unit_Master'

    def __str__(self):
        return self.symbol or self.unitname or f"Unit {self.id}"


class TblexciseserMaster(models.Model):
    """Excise/CGST/IGST Tax Master"""
    id = models.AutoField(db_column='Id', primary_key=True)
    terms = models.TextField(db_column='Terms', blank=True, null=True)
    value = models.FloatField(db_column='Value', blank=True, null=True)
    accessablevalue = models.FloatField(db_column='AccessableValue', blank=True, null=True)
    educess = models.FloatField(db_column='EDUCess', blank=True, null=True)
    shecess = models.FloatField(db_column='SHECess', blank=True, null=True)
    live = models.IntegerField(db_column='Live', blank=True, null=True)
    livesertax = models.IntegerField(db_column='LiveSerTax', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblExciseser_Master'

    def __str__(self):
        return self.terms or f"Tax {self.id}"


class TblvatMaster(models.Model):
    """VAT/SGST Tax Master - Legacy (Pre-GST 2.0)"""
    id = models.AutoField(db_column='Id', primary_key=True)
    terms = models.TextField(db_column='Terms', blank=True, null=True)
    value = models.FloatField(db_column='Value', blank=True, null=True)
    live = models.IntegerField(db_column='Live', blank=True, null=True)
    isvat = models.IntegerField(db_column='IsVAT', default=1)
    iscst = models.IntegerField(db_column='IsCST', default=1)

    class Meta:
        managed = False
        db_table = 'tblVAT_Master'

    def __str__(self):
        return self.terms or f"VAT/SGST {self.id}"


class TblgstMaster(models.Model):
    """
    GST 2.0 Master Table (Effective Sep 2025)
    Unified GST rate table with auto-calculated CGST/SGST/IGST splits.
    Replaces separate CGST/IGST and SGST tables for new transactions.
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    gstrate = models.TextField(db_column='GSTRate', blank=True, null=True)  # e.g., "GST @ 18% (Standard)"
    ratevalue = models.FloatField(db_column='RateValue', blank=True, null=True)  # e.g., 18.0
    cgstrate = models.FloatField(db_column='CGSTRate', blank=True, null=True)  # Auto-calculated: RateValue/2
    sgstrate = models.FloatField(db_column='SGSTRate', blank=True, null=True)  # Auto-calculated: RateValue/2
    igstrate = models.FloatField(db_column='IGSTRate', blank=True, null=True)  # Equals RateValue
    hsnapplicable = models.TextField(db_column='HSNApplicable', blank=True, null=True)  # Applicable HSN codes/categories
    live = models.IntegerField(db_column='Live', default=1)  # 1=Active, 0=Inactive
    effectivefrom = models.TextField(db_column='EffectiveFrom', blank=True, null=True)  # e.g., "2025-09-22"

    class Meta:
        managed = False
        db_table = 'tblGST_Master'

    def __str__(self):
        return self.gstrate or f"GST {self.ratevalue}%"


