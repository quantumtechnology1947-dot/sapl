"""
Quality Control Module Forms

Forms and Formsets for:
- Rejection Reason Master
- Goods Quality Note (GQN) with details formset
- Material Return Quality Note (MRQN) with details formset
- Authorized MCN
- Scrap Register
"""

from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import (
    TblqcRejectionReason,
    TblqcMaterialqualityMaster,
    TblqcMaterialqualityDetails,
    TblqcMaterialreturnqualityMaster,
    TblqcMaterialreturnqualityDetails,
    TblqcAuthorizedmcn,
    TblqcScrapregister,
)


# ============================================================
# Rejection Reason Master Form
# ============================================================

class RejectionReasonForm(forms.ModelForm):
    """Form for Rejection Reason Master"""

    class Meta:
        model = TblqcRejectionReason
        fields = ['description', 'symbol']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter rejection reason description'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol/code'
            }),
        }


# ============================================================
# Goods Quality Note (GQN) Forms
# ============================================================

class GoodsQualityNoteForm(forms.ModelForm):
    """Form for Goods Quality Note Master"""

    class Meta:
        model = TblqcMaterialqualityMaster
        fields = ['gqnno', 'grrno', 'grrid']
        widgets = {
            'gqnno': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Auto-generated or manual entry',
                'required': True
            }),
            'grrno': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'GRR Number'
            }),
            'grrid': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'GRR ID'
            }),
        }


class GoodsQualityNoteDetailForm(forms.ModelForm):
    """Form for Goods Quality Note Details"""

    class Meta:
        model = TblqcMaterialqualityDetails
        fields = [
            'gqnno', 'grrid', 'normalaccqty', 'acceptedqty', 'deviatedqty',
            'segregatedqty', 'rejectedqty', 'rejectionreason', 'sn', 'pn', 'remarks'
        ]
        widgets = {
            'gqnno': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'GQN No'}),
            'grrid': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'GRR ID'}),
            'normalaccqty': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Normal Accepted Qty'}),
            'acceptedqty': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Accepted Qty'}),
            'deviatedqty': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Deviated Qty'}),
            'segregatedqty': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Segregated Qty'}),
            'rejectedqty': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Rejected Qty'}),
            'rejectionreason': forms.Select(attrs={'class': 'form-select'}),
            'sn': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Serial Number'}),
            'pn': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Part Number'}),
            'remarks': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Remarks'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate rejection reason choices
        self.fields['rejectionreason'].queryset = TblqcRejectionReason.objects.all()
        self.fields['rejectionreason'].empty_label = '-- Select Rejection Reason --'


# Goods Quality Note Detail Formset
GoodsQualityNoteDetailFormSet = inlineformset_factory(
    TblqcMaterialqualityMaster,
    TblqcMaterialqualityDetails,
    form=GoodsQualityNoteDetailForm,
    extra=1,
    can_delete=True,
    fields=[
        'gqnno', 'grrid', 'normalaccqty', 'acceptedqty', 'deviatedqty',
        'segregatedqty', 'rejectedqty', 'rejectionreason', 'sn', 'pn', 'remarks'
    ]
)


# ============================================================
# Material Return Quality Note (MRQN) Forms
# ============================================================

class MaterialReturnQualityNoteForm(forms.ModelForm):
    """Form for Material Return Quality Note Master"""
    
    sysdate = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500',
        }),
        initial=timezone.now().date()
    )

    class Meta:
        model = TblqcMaterialreturnqualityMaster
        fields = ['mrqnno', 'sysdate', 'mrnno', 'mrnid']
        widgets = {
            'mrqnno': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500',
                'placeholder': 'Auto-generated or manual entry',
                'required': True
            }),
            'mrnno': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500',
                'placeholder': 'MRN Number'
            }),
            'mrnid': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500',
                'placeholder': 'MRN ID'
            }),
        }


class MaterialReturnQualityNoteDetailForm(forms.ModelForm):
    """Form for Material Return Quality Note Details"""

    class Meta:
        model = TblqcMaterialreturnqualityDetails
        fields = ['mrqnno', 'mrnid', 'acceptedqty', 'rejectedqty']
        widgets = {
            'mrqnno': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'MRQN No'}),
            'mrnid': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'MRN ID'}),
            'acceptedqty': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Accepted Qty'}),
            'rejectedqty': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Rejected Qty'}),
        }


# Material Return Quality Note Detail Formset
MaterialReturnQualityNoteDetailFormSet = inlineformset_factory(
    TblqcMaterialreturnqualityMaster,
    TblqcMaterialreturnqualityDetails,
    form=MaterialReturnQualityNoteDetailForm,
    extra=1,
    can_delete=True,
    fields=['mrqnno', 'mrnid', 'acceptedqty', 'rejectedqty']
)


# ============================================================
# Authorized MCN Form
# ============================================================

class AuthorizedMCNForm(forms.ModelForm):
    """Form for Authorized MCN"""

    class Meta:
        model = TblqcAuthorizedmcn
        fields = ['mcnid', 'mcndid', 'qaqty']
        widgets = {
            'mcnid': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'MCN ID'
            }),
            'mcndid': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'MCN Detail ID'
            }),
            'qaqty': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'placeholder': 'QA Quantity'
            }),
        }


# ============================================================
# Scrap Register Form
# ============================================================

class ScrapRegisterForm(forms.ModelForm):
    """Form for Scrap Register"""

    class Meta:
        model = TblqcScrapregister
        fields = ['mrqnid', 'mrqndid', 'itemid', 'scrapno', 'qty']
        widgets = {
            'mrqnid': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'MRQN ID'
            }),
            'mrqndid': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'MRQN Detail ID'
            }),
            'itemid': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Item ID'
            }),
            'scrapno': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Scrap Number'
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'placeholder': 'Quantity'
            }),
        }
