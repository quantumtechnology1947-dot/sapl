"""
Material Costing Module Models

Converted from: aspnet/Module/MaterialCosting/
Tracks live material costs with effective dates.

Structure:
- Material: Material master data (from Design module tblDG_Material)
- LiveCost: Material cost tracking with effective dates
"""

from django.db import models


class TbldgMaterial(models.Model):
    """
    Material Master
    Converted from: tblDG_Material
    Referenced from Design module
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    material = models.TextField(db_column='Material')
    uom = models.CharField(db_column='UOM', max_length=50, blank=True, null=True)
    comp_id = models.IntegerField(db_column='CompId', blank=True, null=True)
    fin_year_id = models.IntegerField(db_column='FinYearId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblDG_Material'
        ordering = ['material']

    def __str__(self):
        return self.material


class TblmlcLivecost(models.Model):
    """
    Live Cost Tracking
    Converted from: tblMLC_LiveCost
    Tracks material costs with effective dates
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    material = models.ForeignKey(
        TbldgMaterial,
        on_delete=models.CASCADE,
        db_column='Material',
        related_name='live_costs'
    )
    live_cost = models.DecimalField(db_column='LiveCost', max_digits=18, decimal_places=3)
    eff_date = models.CharField(db_column='EffDate', max_length=50)  # Stored as string in ASP.NET
    comp_id = models.IntegerField(db_column='CompId', blank=True, null=True)
    fin_year_id = models.IntegerField(db_column='FinYearId', blank=True, null=True)
    sys_date = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    sys_time = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMLC_LiveCost'
        ordering = ['-id']

    def __str__(self):
        return f"{self.material.material} - {self.live_cost} ({self.eff_date})"

    @property
    def formatted_date(self):
        """Format date for display (DD-MM-YYYY)"""
        return self.eff_date
