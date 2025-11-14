"""
Forms for Material Planning Module
"""

from django import forms
from .models import (
    TblmpMaterialMaster,
    TblmpMaterialDetail,
    TblmpMaterialRawmaterial,
    TblmpMaterialProcess,
    TblmpMaterialFinish,
    TblplnProcessMaster,
)


class MaterialPlanForm(forms.ModelForm):
    """Form for Material Plan Master"""
    class Meta:
        model = TblmpMaterialMaster
        fields = ['plno', 'wono']
        widgets = {
            'plno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Planning Number',
                'required': True
            }),
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Work Order Number',
                'required': True
            }),
        }


class ProcessMasterForm(forms.ModelForm):
    """Form for Process Master"""
    class Meta:
        model = TblplnProcessMaster
        fields = ['processname', 'symbol']
        widgets = {
            'processname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Process Name',
                'required': True
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Symbol',
                'required': True
            }),
        }
        labels = {
            'processname': 'Process Name',
            'symbol': 'Symbol',
        }


class PlanningSearchForm(forms.Form):
    """Form for searching Work Orders"""
    SEARCH_CHOICES = [
        ('customer', 'Customer Name'),
        ('enquiry', 'Enquiry No'),
        ('po', 'PO No'),
        ('wo', 'WO No'),
    ]
    
    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Search By'
    )
    
    search_value = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter search value...',
            'hx-get': '',  # Will be set dynamically for autocomplete
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#search-results',
        }),
        label='Search Value'
    )
    
    wo_category = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='WO Category'
    )
    
    def __init__(self, *args, **kwargs):
        wo_categories = kwargs.pop('wo_categories', [])
        super().__init__(*args, **kwargs)
        
        # Populate WO Category choices
        category_choices = [('', 'All Categories')]
        category_choices.extend([(c.cid, c.cname) for c in wo_categories])
        self.fields['wo_category'].choices = category_choices


class RawMaterialForm(forms.ModelForm):
    """Form for Raw Material"""
    class Meta:
        model = TblmpMaterialRawmaterial
        fields = ['supplierid', 'qty', 'rate', 'discount', 'deldate']
        widgets = {
            'supplierid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Supplier Name',
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'deldate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'type': 'date',
            }),
        }


class ProcessMaterialForm(forms.ModelForm):
    """Form for Process Material"""
    class Meta:
        model = TblmpMaterialProcess
        fields = ['supplierid', 'qty', 'rate', 'discount', 'deldate']
        widgets = {
            'supplierid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Supplier Name',
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'deldate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'type': 'date',
            }),
        }


class FinishMaterialForm(forms.ModelForm):
    """Form for Finish Material"""
    class Meta:
        model = TblmpMaterialFinish
        fields = ['supplierid', 'qty', 'rate', 'discount', 'deldate']
        widgets = {
            'supplierid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Supplier Name',
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'step': '0.01',
            }),
            'deldate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'type': 'date',
            }),
        }
