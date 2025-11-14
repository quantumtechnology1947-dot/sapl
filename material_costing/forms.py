"""
Forms for Material Costing Module
"""

from django import forms
from .models import TblmlcLivecost


class LiveCostForm(forms.ModelForm):
    """Form for Live Cost Management"""
    class Meta:
        model = TblmlcLivecost
        fields = ['material', 'live_cost', 'eff_date']
        widgets = {
            'material': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'required': True
            }),
            'live_cost': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter cost',
                'step': '0.001',
                'required': True
            }),
            'eff_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date',
                'required': True
            }),
        }
        labels = {
            'material': 'Material',
            'live_cost': 'Live Cost',
            'eff_date': 'Effective Date'
        }

    def clean_live_cost(self):
        cost = self.cleaned_data.get('live_cost')
        if cost and cost <= 0:
            raise forms.ValidationError('Cost must be greater than 0.')
        return cost
