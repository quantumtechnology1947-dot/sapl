"""
Quality Control Module Models

Converted from: aspnet/Module/QualityControl/
Follows Django conventions with managed=False for existing database tables.
"""

from django.db import models


class TblqcRejectionReason(models.Model):
    """Rejection Reason Master - Standard rejection reasons"""
    id = models.AutoField(db_column='Id', primary_key=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    symbol = models.TextField(db_column='Symbol', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblQc_Rejection_Reason'
        ordering = ['id']

    def __str__(self):
        return f"{self.symbol} - {self.description}" if self.symbol else str(self.description)


class TblqcMaterialqualityMaster(models.Model):
    """Goods Quality Note (GQN) Master - Quality inspection of incoming goods"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50)
    systime = models.CharField(db_column='SysTime', max_length=50)
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    sessionid = models.TextField(db_column='SessionId')
    gqnno = models.TextField(db_column='GQNNo', blank=True, null=True)
    grrno = models.TextField(db_column='GRRNo', blank=True, null=True)
    grrid = models.IntegerField(db_column='GRRId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblQc_MaterialQuality_Master'
        ordering = ['-id']

    def __str__(self):
        return f"GQN {self.gqnno} - GRR: {self.grrno}"


class TblqcMaterialqualityDetails(models.Model):
    """Goods Quality Note Details - Line items for quality inspection"""
    id = models.AutoField(db_column='Id', primary_key=True)
    gqnno = models.TextField(db_column='GQNNo', blank=True, null=True)
    grrid = models.IntegerField(db_column='GRRId', blank=True, null=True)
    normalaccqty = models.FloatField(db_column='NormalAccQty', blank=True, null=True)
    acceptedqty = models.FloatField(db_column='AcceptedQty', blank=True, null=True)
    deviatedqty = models.FloatField(db_column='DeviatedQty', blank=True, null=True)
    segregatedqty = models.FloatField(db_column='SegregatedQty', blank=True, null=True)
    rejectedqty = models.FloatField(db_column='RejectedQty', blank=True, null=True)
    rejectionreason = models.IntegerField(db_column='RejectionReason', blank=True, null=True)
    sn = models.TextField(db_column='SN', blank=True, null=True)
    pn = models.TextField(db_column='PN', blank=True, null=True)
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)
    mid = models.ForeignKey(TblqcMaterialqualityMaster, on_delete=models.CASCADE, db_column='MId', related_name='details')

    class Meta:
        managed = False
        db_table = 'tblQc_MaterialQuality_Details'

    def __str__(self):
        return f"GQN Detail {self.id} - Accepted: {self.acceptedqty}, Rejected: {self.rejectedqty}"

    @property
    def total_qty(self):
        """Total quantity inspected"""
        return (self.normalaccqty or 0) + (self.acceptedqty or 0) + (self.deviatedqty or 0) + (self.segregatedqty or 0) + (self.rejectedqty or 0)


class TblqcMaterialreturnqualityMaster(models.Model):
    """Material Return Quality Note (MRQN) Master - Quality inspection of returned materials"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50)
    systime = models.CharField(db_column='SysTime', max_length=50)
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    sessionid = models.TextField(db_column='SessionId')
    mrqnno = models.TextField(db_column='MRQNNo', blank=True, null=True)
    mrnno = models.TextField(db_column='MRNNo', blank=True, null=True)
    mrnid = models.IntegerField(db_column='MRNId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblQc_MaterialReturnQuality_Master'
        ordering = ['-id']

    def __str__(self):
        return f"MRQN {self.mrqnno} - MRN: {self.mrnno}"


class TblqcMaterialreturnqualityDetails(models.Model):
    """Material Return Quality Note Details - Line items for return inspection"""
    id = models.AutoField(db_column='Id', primary_key=True)
    mrqnno = models.TextField(db_column='MRQNNo', blank=True, null=True)
    mrnid = models.IntegerField(db_column='MRNId', blank=True, null=True)
    acceptedqty = models.FloatField(db_column='AcceptedQty', blank=True, null=True)
    rejectedqty = models.FloatField(db_column='RejectedQty', blank=True, null=True)
    mid = models.ForeignKey(TblqcMaterialreturnqualityMaster, on_delete=models.CASCADE, db_column='MId', related_name='details')

    class Meta:
        managed = False
        db_table = 'tblQc_MaterialReturnQuality_Details'

    def __str__(self):
        return f"MRQN Detail {self.id} - Accepted: {self.acceptedqty}, Rejected: {self.rejectedqty}"

    @property
    def total_qty(self):
        """Total quantity inspected"""
        return (self.acceptedqty or 0) + (self.rejectedqty or 0)


class TblqcAuthorizedmcn(models.Model):
    """Authorized Material Credit Note - Authorization tracking for MCN"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50)
    systime = models.CharField(db_column='SysTime', max_length=50)
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    sessionid = models.CharField(db_column='SessionId', max_length=50)
    mcnid = models.IntegerField(db_column='MCNId', blank=True, null=True)
    mcndid = models.IntegerField(db_column='MCNDId', blank=True, null=True)
    qaqty = models.FloatField(db_column='QAQty', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblQc_AuthorizedMCN'
        ordering = ['-id']

    def __str__(self):
        return f"Authorized MCN {self.mcnid} - QA Qty: {self.qaqty}"


class TblqcScrapregister(models.Model):
    """Scrap Register - Track scrapped materials"""
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50)
    systime = models.CharField(db_column='SysTime', max_length=50)
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    sessionid = models.CharField(db_column='SessionId', max_length=50)
    mrqnid = models.IntegerField(db_column='MRQNId', blank=True, null=True)
    mrqndid = models.IntegerField(db_column='MRQNDId', blank=True, null=True)
    itemid = models.CharField(db_column='ItemId', max_length=50, blank=True, null=True)
    scrapno = models.TextField(db_column='ScrapNo', blank=True, null=True)
    qty = models.FloatField(db_column='Qty', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblQC_Scrapregister'
        ordering = ['-id']

    def __str__(self):
        return f"Scrap {self.scrapno} - Item: {self.itemid} - Qty: {self.qty}"
