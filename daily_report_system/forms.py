"""
Daily Report System Forms

ModelForms for all plan types with Tailwind styling.
Note: Currently using model fields directly in views.
This file is created for future form customization.
"""

from django import forms
from .models import (
    TblpmProjectplanningDesigner,
    TblpmProjectManufacturingPlanDetail,
    TblpmProjectVendorPlanDetail,
)


class DesignPlanForm(forms.ModelForm):
    """
    Form for Design Plan creation and updates.

    Future enhancement: Add Tailwind classes and HTMX attributes.
    """
    class Meta:
        model = TblpmProjectplanningDesigner
        fields = [
            'name_proj', 'wo_no', 'no_fix_rqu', 'des_lea', 'des_mem',
            'sr_no', 'name_act', 'rev_no', 'no_days', 'as_plan_from',
            'as_plan_to', 'ac_from'
        ]


class ManufacturingPlanForm(forms.ModelForm):
    """
    Form for Manufacturing Plan creation and updates.

    Future enhancement: Add Tailwind classes and HTMX attributes.
    """
    class Meta:
        model = TblpmProjectManufacturingPlanDetail
        fields = [
            'prjctno', 'itemcode', 'description', 'uom', 'bomq',
            'design', 'vendorplandate', 'vendoract', 'wono', 'vendorplan'
        ]


class VendorPlanForm(forms.ModelForm):
    """
    Form for Vendor Plan creation and updates.

    Future enhancement: Add Tailwind classes and HTMX attributes.
    """
    class Meta:
        model = TblpmProjectVendorPlanDetail
        fields = [
            'prjctno', 'itemcode', 'description', 'uom', 'bomq',
            'design', 'vendorplandate', 'vendoract', 'wono', 'vendorplan'
        ]
