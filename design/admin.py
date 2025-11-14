"""
Design Module Admin
Admin interface for design-related models.
"""
from django.contrib import admin
from .models import TbldgItemMaster, TbldgCategoryMaster, TbldgEcnReason


@admin.register(TbldgCategoryMaster)
class CategoryMasterAdmin(admin.ModelAdmin):
    """Admin interface for Category Master"""
    list_display = ['cid', 'compid']
    search_fields = ['categorydesc']


@admin.register(TbldgItemMaster)
class ItemMasterAdmin(admin.ModelAdmin):
    """Admin interface for Item Master"""
    list_display = ['id', 'itemcode', 'compid']
    search_fields = ['itemcode', 'itemdesc']
    ordering = ['itemcode']


@admin.register(TbldgEcnReason)
class ECNReasonAdmin(admin.ModelAdmin):
    """Admin interface for ECN Reason"""
    list_display = ['id', 'compid']
    search_fields = ['reasondesc']
