"""
Project Management Module Forms

Model forms for Project Management transactions.
"""

from django import forms
from .models import (
    TblonsiteattendanceMaster,
    TblpmManpowerplanning,
    TblpmMaterialcreditnoteMaster,
    TblpmProjectplanningMaster,
    TblpmProjectstatus,
)


class ManPowerPlanningForm(forms.ModelForm):
    """ManPower Planning Form"""
    class Meta:
        model = TblpmManpowerplanning
        fields = ['empid', 'date', 'wono', 'dept', 'types', 'amendmentno']
        widgets = {
            'empid': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Employee ID'}),
            'date': forms.TextInput(attrs={'class': 'form-input', 'type': 'date'}),
            'wono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Work Order Number'}),
            'dept': forms.NumberInput(attrs={'class': 'form-input'}),
            'types': forms.NumberInput(attrs={'class': 'form-input'}),
            'amendmentno': forms.NumberInput(attrs={'class': 'form-input', 'value': '0'}),
        }

    def clean_amendmentno(self):
        amendmentno = self.cleaned_data.get('amendmentno')
        if amendmentno is None or amendmentno < 0:
            return 0
        return amendmentno


class MaterialCreditNoteForm(forms.ModelForm):
    """Material Credit Note Form"""
    class Meta:
        model = TblpmMaterialcreditnoteMaster
        fields = ['mcnno', 'wono']
        widgets = {
            'mcnno': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'MCN Number'}),
            'wono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Work Order Number'}),
        }


class OnSiteAttendanceForm(forms.ModelForm):
    """OnSite Attendance Form"""

    SHIFT_CHOICES = [
        (1, 'Day Shift'),
        (2, 'Night Shift'),
        (3, 'General'),
    ]

    STATUS_CHOICES = [
        (1, 'Present'),
        (0, 'Absent'),
    ]

    shift = forms.ChoiceField(choices=SHIFT_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = TblonsiteattendanceMaster
        fields = ['onsitedate', 'empid', 'shift', 'status', 'onsite', 'fromtime', 'totime']
        widgets = {
            'onsitedate': forms.TextInput(attrs={'class': 'form-input', 'type': 'date'}),
            'empid': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Employee ID'}),
            'onsite': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'OnSite Location'}),
            'fromtime': forms.TextInput(attrs={'class': 'form-input', 'type': 'time'}),
            'totime': forms.TextInput(attrs={'class': 'form-input', 'type': 'time'}),
        }


class ProjectPlanningForm(forms.ModelForm):
    """Project Planning Form with File Upload"""

    filedata = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx,.xls,.xlsx'})
    )

    class Meta:
        model = TblpmProjectplanningMaster
        fields = ['wono']
        widgets = {
            'wono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Work Order Number'}),
        }


class ProjectStatusForm(forms.ModelForm):
    """Project Status Form"""
    class Meta:
        model = TblpmProjectstatus
        fields = ['srno', 'wono', 'activities']
        widgets = {
            'srno': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Serial Number'}),
            'wono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Work Order Number'}),
            'activities': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Activities'}),
        }
