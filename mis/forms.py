"""
MIS Module Forms

Forms for Budget Codes, Time Codes, Categories, and Sub-Categories
"""

from django import forms
from .models import (
    TblmisBudgetcode,
    TblmisBudgetcodeTime,
    TblmisBudgethrsFieldCategory,
    TblmisBudgethrsFieldSubcategory,
    TblaccBudgetWoTime,
)


class BudgetCodeForm(forms.ModelForm):
    """Form for Budget Code Master"""

    class Meta:
        model = TblmisBudgetcode
        fields = ['symbol', 'description']
        widgets = {
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter budget code symbol',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter budget code description'
            }),
        }


class BudgetCodeTimeForm(forms.ModelForm):
    """Form for Budget Code Time Master"""

    class Meta:
        model = TblmisBudgetcodeTime
        fields = ['symbol', 'description']
        widgets = {
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter time code symbol',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter time code description'
            }),
        }


class BudgetHrsFieldCategoryForm(forms.ModelForm):
    """Form for Budget Hours Field Category"""

    class Meta:
        model = TblmisBudgethrsFieldCategory
        fields = ['symbol', 'category']
        widgets = {
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter category symbol',
                'required': True
            }),
            'category': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter category description'
            }),
        }


class BudgetHrsFieldSubCategoryForm(forms.ModelForm):
    """Form for Budget Hours Field Sub-Category"""

    class Meta:
        model = TblmisBudgethrsFieldSubcategory
        fields = ['mid', 'symbol', 'subcategory']
        widgets = {
            'mid': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'required': True
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter sub-category symbol',
                'required': True
            }),
            'subcategory': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter sub-category description'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mid'].queryset = TblmisBudgethrsFieldCategory.objects.all()
        self.fields['mid'].empty_label = '-- Select Category --'


class BudgetHoursAssignmentForm(forms.ModelForm):
    """Form for assigning budget hours to work orders"""

    class Meta:
        model = TblaccBudgetWoTime
        fields = ['equip_id', 'hrs_budget_cat', 'hrs_budget_sub_cat', 'hour']
        widgets = {
            'equip_id': forms.Select(attrs={
                'class': 'h-8 px-3 text-xs border border-gray-300 rounded focus:outline-none focus:border-sap-blue focus:ring-1 focus:ring-sap-blue',
                'required': True
            }),
            'hrs_budget_cat': forms.Select(attrs={
                'class': 'h-8 px-3 text-xs border border-gray-300 rounded focus:outline-none focus:border-sap-blue focus:ring-1 focus:ring-sap-blue',
                'required': True
            }),
            'hrs_budget_sub_cat': forms.Select(attrs={
                'class': 'h-8 px-3 text-xs border border-gray-300 rounded focus:outline-none focus:border-sap-blue focus:ring-1 focus:ring-sap-blue',
                'required': True
            }),
            'hour': forms.NumberInput(attrs={
                'class': 'h-8 px-3 text-xs border border-gray-300 rounded focus:outline-none focus:border-sap-blue focus:ring-1 focus:ring-sap-blue',
                'placeholder': 'Enter hours',
                'min': '0',
                'step': '0.01',
                'required': True
            }),
        }
        labels = {
            'equip_id': 'Equipment No [Description]',
            'hrs_budget_cat': 'Category',
            'hrs_budget_sub_cat': 'Sub Category',
            'hour': 'Hours',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Categories excluding Id=1 (Select)
        self.fields['hrs_budget_cat'].queryset = TblmisBudgethrsFieldCategory.objects.exclude(id=1)
        self.fields['hrs_budget_cat'].empty_label = '-- Select Category --'

        # Sub-categories will be populated via HTMX based on category selection
        self.fields['hrs_budget_sub_cat'].queryset = TblmisBudgethrsFieldSubcategory.objects.none()
        self.fields['hrs_budget_sub_cat'].empty_label = '-- Select Sub-Category --'
