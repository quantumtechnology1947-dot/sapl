from django.db import models

class TblaccessMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)
    sessionid = models.CharField(db_column='SessionId', max_length=50)
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    empid = models.CharField(db_column='EmpId', max_length=50)
    modid = models.IntegerField(db_column='ModId')
    submodid = models.IntegerField(db_column='SubModId')
    accesstype = models.IntegerField(db_column='AccessType', blank=True, null=True)
    access = models.IntegerField(db_column='Access', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblAccess_Master'
