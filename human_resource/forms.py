"""
Human Resource Forms - Converted from ASP.NET Module/HR
Django forms for all HR masters with proper validation.
"""

from django import forms
from datetime import datetime
from .models import (
    Businessgroup, TblhrDepartments, TblhrDesignation, TblhrGrade,
    TblhrHolidayMaster, TblhrWorkingdays, TblhrCoporatemobileno,
    TblgatepassReason, TblhrIntercomext, TblhrPfSlab, TblhrSwapcard,
    TblhrOfficestaff, TblhrSalaryMaster, TblhrSalaryDetails, TblhrOfferMaster,
    TblhrOfferAccessories, TblhrBankloan, TblhrMobilebill, TblgatePass,
    TblaccTourintimationMaster
)


class BusinessGroupForm(forms.ModelForm):
    """
    Form for Business Group master.
    Converted from: aspnet/Module/HR/Masters/BusinessGroup.aspx
    """
    class Meta:
        model = Businessgroup
        fields = ['name', 'symbol', 'incharge']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter business group name',
                'required': True
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol',
                'required': True
            }),
            'incharge': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter incharge name',
                'required': True
            }),
        }
        labels = {
            'name': 'Name',
            'symbol': 'Symbol',
            'incharge': 'Incharge',
        }


class DepartmentForm(forms.ModelForm):
    """
    Form for Department master.
    Converted from: aspnet/Module/HR/Masters/Department.aspx
    """
    class Meta:
        model = TblhrDepartments
        fields = ['description', 'symbol']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter department description',
                'required': True
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol',
                'required': True
            }),
        }
        labels = {
            'description': 'Description',
            'symbol': 'Symbol',
        }


class DesignationForm(forms.ModelForm):
    """
    Form for Designation master.
    Converted from: aspnet/Module/HR/Masters/Designation.aspx
    """
    class Meta:
        model = TblhrDesignation
        fields = ['type', 'symbol']
        widgets = {
            'type': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter designation type',
                'required': True
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol',
                'required': True
            }),
        }
        labels = {
            'type': 'Type',
            'symbol': 'Symbol',
        }


class GradeForm(forms.ModelForm):
    """
    Form for Grade master.
    Converted from: aspnet/Module/HR/Masters/Grade.aspx
    """
    class Meta:
        model = TblhrGrade
        fields = ['description', 'symbol']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter grade description',
                'required': True
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol',
                'required': True
            }),
        }
        labels = {
            'description': 'Description',
            'symbol': 'Symbol',
        }


class HolidayMasterForm(forms.ModelForm):
    """
    Form for Holiday Master.
    Converted from: aspnet/Module/HR/Masters/HolidayMaster.aspx
    """
    class Meta:
        model = TblhrHolidayMaster
        fields = ['hdate', 'title']
        widgets = {
            'hdate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter holiday title',
                'required': True
            }),
        }
        labels = {
            'hdate': 'Date',
            'title': 'Title',
        }

    def clean_hdate(self):
        """Convert date to DD-MM-YYYY format for database storage."""
        hdate = self.cleaned_data.get('hdate')
        if hdate:
            return hdate.strftime('%d-%m-%Y')
        return hdate


class WorkingDaysForm(forms.ModelForm):
    """
    Form for Working Days master.
    Converted from: aspnet/Module/HR/Masters/WorkingDays.aspx
    """

    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    monthid = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'required': True
        }),
        label='Month'
    )

    class Meta:
        model = TblhrWorkingdays
        fields = ['monthid', 'days']
        widgets = {
            'days': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter working days',
                'step': '0.5',
                'min': '0',
                'max': '31',
                'required': True
            }),
        }
        labels = {
            'days': 'Working Days',
        }


class CorporateMobileNoForm(forms.ModelForm):
    """
    Form for Corporate Mobile Number master.
    Converted from: aspnet/Module/HR/Masters/CorporateMobileNo.aspx
    """
    class Meta:
        model = TblhrCoporatemobileno
        fields = ['mobileno', 'limitamt']
        widgets = {
            'mobileno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter mobile number',
                'pattern': '[0-9]{10}',
                'title': 'Enter 10-digit mobile number',
                'required': True
            }),
            'limitamt': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter limit amount',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
        }
        labels = {
            'mobileno': 'Mobile No',
            'limitamt': 'Amount Limit',
        }


class GatePassReasonForm(forms.ModelForm):
    """
    Form for Gate Pass Reason master.
    Converted from: aspnet/Module/HR/Masters/GatePassReason.aspx
    """
    class Meta:
        model = TblgatepassReason
        fields = ['reason', 'wono', 'enquiry', 'other']
        widgets = {
            'reason': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter reason',
                'required': True
            }),
            'wono': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'enquiry': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'other': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }
        labels = {
            'reason': 'Reason',
            'wono': 'Work Order No',
            'enquiry': 'Enquiry',
            'other': 'Other',
        }

    def clean_wono(self):
        """Convert checkbox to integer."""
        return 1 if self.cleaned_data.get('wono') else 0

    def clean_enquiry(self):
        """Convert checkbox to integer."""
        return 1 if self.cleaned_data.get('enquiry') else 0

    def clean_other(self):
        """Convert checkbox to integer."""
        return 1 if self.cleaned_data.get('other') else 0


class IntercomExtForm(forms.ModelForm):
    """
    Form for Intercom Extension master.
    Converted from: aspnet/Module/HR/Masters/IntercomExtNo.aspx
    """

    department = forms.ModelChoiceField(
        queryset=TblhrDepartments.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'required': True
        }),
        label='Department',
        empty_label='Select Department'
    )

    class Meta:
        model = TblhrIntercomext
        fields = ['extno', 'department']
        widgets = {
            'extno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter extension number',
                'required': True
            }),
        }
        labels = {
            'extno': 'Extension No',
        }


class PFSlabForm(forms.ModelForm):
    """
    Form for PF Slab master.
    Converted from: aspnet/Module/HR/Masters/PF_Slab.aspx
    """
    class Meta:
        model = TblhrPfSlab
        fields = ['pfemployee', 'pfcompany', 'active']
        widgets = {
            'pfemployee': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter employee PF %',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'required': True
            }),
            'pfcompany': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter company PF %',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'required': True
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }
        labels = {
            'pfemployee': 'PF Employee (%)',
            'pfcompany': 'PF Company (%)',
            'active': 'Active',
        }

    def clean_active(self):
        """Convert checkbox to integer."""
        return 1 if self.cleaned_data.get('active') else 0


class SwapCardForm(forms.ModelForm):
    """
    Form for Swap Card master.
    Converted from: aspnet/Module/HR/Masters/SwapCardNo.aspx
    """
    class Meta:
        model = TblhrSwapcard
        fields = ['swapcardno']
        widgets = {
            'swapcardno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter swap card number',
                'required': True
            }),
        }
        labels = {
            'swapcardno': 'Swap Card No',
        }


class EmployeeForm(forms.ModelForm):
    """
    Form for Employee (Office Staff) transaction.
    Converted from: aspnet/Module/HR/Transactions/OfficeStaff.aspx
    Multi-tab form with photo and CV uploads.
    """

    # ModelChoiceField for foreign key relationships
    department = forms.ModelChoiceField(
        queryset=TblhrDepartments.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Department',
        empty_label='Select Department',
        required=False
    )

    designation = forms.ModelChoiceField(
        queryset=TblhrDesignation.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Designation',
        empty_label='Select Designation',
        required=False
    )

    grade = forms.ModelChoiceField(
        queryset=TblhrGrade.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Grade',
        empty_label='Select Grade',
        required=False
    )

    bggroup = forms.ModelChoiceField(
        queryset=Businessgroup.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Business Group',
        empty_label='Select Business Group',
        required=False
    )

    swapcardno = forms.ModelChoiceField(
        queryset=TblhrSwapcard.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Swap Card',
        empty_label='Select Swap Card',
        required=False
    )

    # File upload fields
    photodata = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': 'image/*',
            'onchange': 'previewPhoto(event)'
        }),
        label='Employee Photo',
        required=False
    )

    cvdata = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': '.pdf,.doc,.docx',
            'onchange': 'showCVFileName(event)'
        }),
        label='Upload CV',
        required=False
    )

    class Meta:
        model = TblhrOfficestaff
        fields = [
            # Official Info
            'offerid', 'empid', 'title', 'employeename', 'swapcardno', 'department',
            'bggroup', 'directorsname', 'depthead', 'groupleader', 'designation', 'grade',
            'mobileno', 'contactno', 'companyemail', 'emailid1', 'extensionno',
            'joiningdate', 'resignationdate',
            # Personal Info
            'permanentaddress', 'correspondenceaddress', 'emailid2', 'dateofbirth',
            'gender', 'martialstatus', 'bloodgroup', 'height', 'weight',
            'physicallyhandycapped', 'religion', 'cast',
            # Education & Experience
            'educationalqualification', 'additionalqualification', 'lastcompanyname',
            'workingduration', 'totalexperience', 'currentctc',
            # Others
            'bankaccountno', 'pfno', 'panno', 'passportno', 'expirydate',
            'additionalinformation', 'wr', 'da', 'custlogin'
        ]
        # Note: photodata and cvdata are handled as separate FileField instances above

        widgets = {
            # Official Info
            'offerid': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Offer ID'
            }),
            'empid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Auto-generated or enter manually',
                'readonly': 'readonly'
            }),
            'title': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            }, choices=[('', 'Select Title'), ('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.')]),
            'employeename': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter employee name',
                'required': True
            }),
            'directorsname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter director name'
            }),
            'depthead': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter department head'
            }),
            'groupleader': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter group leader'
            }),
            'mobileno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter mobile number',
                'pattern': '[0-9]{10}',
                'title': '10-digit mobile number'
            }),
            'contactno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter contact number'
            }),
            'companyemail': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter company email'
            }),
            'emailid1': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter personal email'
            }),
            'extensionno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Extension number'
            }),
            'joiningdate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'resignationdate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),

            # Personal Info
            'permanentaddress': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter permanent address',
                'rows': 3
            }),
            'correspondenceaddress': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter correspondence address',
                'rows': 3
            }),
            'emailid2': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter alternate email'
            }),
            'dateofbirth': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            }, choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]),
            'martialstatus': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            }, choices=[('', 'Select Status'), ('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')]),
            'bloodgroup': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            }, choices=[('', 'Select Blood Group'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')]),
            'height': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Height (e.g., 5.8 ft)'
            }),
            'weight': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Weight (e.g., 65 kg)'
            }),
            'physicallyhandycapped': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            }, choices=[('', 'Select'), ('Yes', 'Yes'), ('No', 'No')]),
            'religion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter religion'
            }),
            'cast': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter caste'
            }),

            # Education & Experience
            'educationalqualification': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter educational qualifications',
                'rows': 3
            }),
            'additionalqualification': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter additional qualifications',
                'rows': 2
            }),
            'lastcompanyname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter last company name'
            }),
            'workingduration': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Working duration (e.g., 2 years)'
            }),
            'totalexperience': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Total experience (e.g., 5 years)'
            }),
            'currentctc': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Current CTC'
            }),

            # Others
            'bankaccountno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter bank account number'
            }),
            'pfno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter PF number'
            }),
            'panno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter PAN number'
            }),
            'passportno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter passport number'
            }),
            'expirydate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'additionalinformation': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter additional information',
                'rows': 3
            }),
            'wr': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'WR'
            }),
            'da': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'DA'
            }),
            'custlogin': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Customer login'
            }),
        }

        labels = {
            'offerid': 'Offer ID',
            'empid': 'Employee ID',
            'title': 'Title',
            'employeename': 'Employee Name',
            'directorsname': 'Directors Name',
            'depthead': 'Department Head',
            'groupleader': 'Group Leader',
            'mobileno': 'Mobile No',
            'contactno': 'Contact No',
            'companyemail': 'Company Email',
            'emailid1': 'Personal Email',
            'extensionno': 'Extension No',
            'joiningdate': 'Joining Date',
            'resignationdate': 'Resignation Date',
            'permanentaddress': 'Permanent Address',
            'correspondenceaddress': 'Correspondence Address',
            'emailid2': 'Alternate Email',
            'dateofbirth': 'Date of Birth',
            'gender': 'Gender',
            'martialstatus': 'Marital Status',
            'bloodgroup': 'Blood Group',
            'height': 'Height',
            'weight': 'Weight',
            'physicallyhandycapped': 'Physically Handicapped',
            'religion': 'Religion',
            'cast': 'Caste',
            'educationalqualification': 'Educational Qualification',
            'additionalqualification': 'Additional Qualification',
            'lastcompanyname': 'Last Company Name',
            'workingduration': 'Working Duration',
            'totalexperience': 'Total Experience',
            'currentctc': 'Current CTC',
            'bankaccountno': 'Bank Account No',
            'pfno': 'PF No',
            'panno': 'PAN No',
            'passportno': 'Passport No',
            'expirydate': 'Expiry Date',
            'additionalinformation': 'Additional Information',
            'wr': 'WR',
            'da': 'DA',
            'custlogin': 'Customer Login',
        }

    def clean_joiningdate(self):
        """Convert joining date to DD-MM-YYYY format."""
        joiningdate = self.cleaned_data.get('joiningdate')
        if joiningdate:
            from datetime import datetime
            if isinstance(joiningdate, str):
                return joiningdate
            return joiningdate.strftime('%d-%m-%Y')
        return joiningdate

    def clean_resignationdate(self):
        """Convert resignation date to DD-MM-YYYY format."""
        resignationdate = self.cleaned_data.get('resignationdate')
        if resignationdate:
            from datetime import datetime
            if isinstance(resignationdate, str):
                return resignationdate
            return resignationdate.strftime('%d-%m-%Y')
        return resignationdate

    def clean_dateofbirth(self):
        """Convert date of birth to DD-MM-YYYY format."""
        dateofbirth = self.cleaned_data.get('dateofbirth')
        if dateofbirth:
            from datetime import datetime
            if isinstance(dateofbirth, str):
                return dateofbirth
            return dateofbirth.strftime('%d-%m-%Y')
        return dateofbirth

    def clean_expirydate(self):
        """Convert expiry date to DD-MM-YYYY format."""
        expirydate = self.cleaned_data.get('expirydate')
        if expirydate:
            from datetime import datetime
            if isinstance(expirydate, str):
                return expirydate
            return expirydate.strftime('%d-%m-%Y')
        return expirydate

    def clean_photodata(self):
        """Validate and process photo upload."""
        photo = self.cleaned_data.get('photodata')
        if photo:
            # Check file size (max 2MB)
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Photo file size must be under 2MB.')

            # Check file type
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError('Photo must be an image file.')

        return photo

    def clean_cvdata(self):
        """Validate and process CV upload."""
        cv = self.cleaned_data.get('cvdata')
        if cv:
            # Check file size (max 5MB)
            if cv.size > 5 * 1024 * 1024:
                raise forms.ValidationError('CV file size must be under 5MB.')

            # Check file type
            allowed_types = ['application/pdf', 'application/msword',
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if cv.content_type not in allowed_types:
                raise forms.ValidationError('CV must be a PDF or Word document.')

        return cv


class SalaryForm(forms.ModelForm):
    """
    Form for Salary/Payroll processing transaction.
    Converted from: aspnet/Module/HR/Transactions/Salary_New_Details.aspx
    Handles master-detail relationship (TblhrSalaryMaster + TblhrSalaryDetails).
    """

    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    fmonth = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'required': True
        }),
        label='Salary Month'
    )

    # Attendance fields (from TblhrSalaryDetails)
    present = forms.DecimalField(
        max_digits=5, decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'step': '0.5',
            'min': '0',
            'max': '31'
        }),
        label='Present',
        initial=0,
        required=False
    )

    absent = forms.DecimalField(
        max_digits=5, decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'step': '0.5',
            'min': '0',
            'max': '31'
        }),
        label='Absent',
        initial=0,
        required=False
    )

    latein = forms.DecimalField(
        max_digits=5, decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'step': '0.5',
            'min': '0',
            'max': '31'
        }),
        label='Late In',
        initial=0,
        required=False
    )

    halfday = forms.DecimalField(
        max_digits=5, decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'step': '0.5',
            'min': '0',
            'max': '31'
        }),
        label='Half Day',
        initial=0,
        required=False
    )

    sunday = forms.DecimalField(
        max_digits=5, decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'step': '0.5',
            'min': '0',
            'max': '31'
        }),
        label='Sunday',
        initial=0,
        required=False
    )

    coff = forms.DecimalField(
        max_digits=5, decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'step': '0.5',
            'min': '0',
            'max': '31'
        }),
        label='C-Off',
        initial=0,
        required=False
    )

    pl = forms.DecimalField(
        max_digits=5, decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'step': '0.5',
            'min': '0',
            'max': '31'
        }),
        label='PL',
        initial=0,
        required=False
    )

    overtimehrs = forms.DecimalField(
        max_digits=5, decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'step': '0.5',
            'min': '0'
        }),
        label='Overtime Hours',
        initial=0,
        required=False
    )

    overtimerate = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0',
            'readonly': 'readonly'
        }),
        label='Overtime Rate',
        initial=0,
        required=False
    )

    # Deduction fields
    installment = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0',
            'readonly': 'readonly'
        }),
        label='Installment (ESI)',
        initial=0,
        required=False
    )

    mobileexeamt = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0',
            'readonly': 'readonly'
        }),
        label='Mobile Bill Excess',
        initial=0,
        required=False
    )

    deduction = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        }),
        label='Other Deduction',
        initial=0,
        required=False
    )

    remarks2 = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Deduction remarks',
            'rows': 2
        }),
        label='Deduction Remarks',
        required=False
    )

    # Addition fields
    addition = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        }),
        label='Addition',
        initial=0,
        required=False
    )

    remarks1 = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Addition remarks',
            'rows': 2
        }),
        label='Addition Remarks',
        required=False
    )

    # Master record fields
    increment = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '0',
            'min': '0'
        }),
        label='Increment',
        initial=0,
        required=False
    )

    releaseflag = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
        }),
        label='Release Salary',
        initial=False,
        required=False
    )

    class Meta:
        model = TblhrSalaryMaster
        fields = ['fmonth', 'increment', 'releaseflag']

    def clean_present(self):
        """Validate present days."""
        present = self.cleaned_data.get('present', 0)
        if present and (present < 0 or present > 31):
            raise forms.ValidationError('Present days must be between 0 and 31.')
        return present or 0

    def clean_absent(self):
        """Validate absent days."""
        absent = self.cleaned_data.get('absent', 0)
        if absent and (absent < 0 or absent > 31):
            raise forms.ValidationError('Absent days must be between 0 and 31.')
        return absent or 0

    def clean_overtimehrs(self):
        """Validate overtime hours."""
        overtimehrs = self.cleaned_data.get('overtimehrs', 0)
        if overtimehrs and overtimehrs < 0:
            raise forms.ValidationError('Overtime hours cannot be negative.')
        return overtimehrs or 0

    def clean_addition(self):
        """Validate addition amount."""
        addition = self.cleaned_data.get('addition', 0)
        if addition and addition < 0:
            raise forms.ValidationError('Addition amount cannot be negative.')
        return addition or 0

    def clean_deduction(self):
        """Validate deduction amount."""
        deduction = self.cleaned_data.get('deduction', 0)
        if deduction and deduction < 0:
            raise forms.ValidationError('Deduction amount cannot be negative.')
        return deduction or 0


# ============================================================================
# PHASE 3: BANK LOAN & MOBILE BILLS FORMS
# ============================================================================

class BankLoanForm(forms.ModelForm):
    """
    Form for Bank Loan transaction.
    Converted from: aspnet/Module/HR/Transactions/BankLoan.aspx
    Tracks employee bank loans with installment management.
    """

    # Employee selection
    empid = forms.ModelChoiceField(
        queryset=TblhrOfficestaff.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'required': True
        }),
        label='Employee',
        empty_label='Select Employee',
        to_field_name='empid'
    )

    class Meta:
        model = TblhrBankloan
        fields = ['empid', 'bankname', 'branch', 'amount', 'installment', 'fromdate', 'todate']
        widgets = {
            'bankname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter bank name',
                'required': True
            }),
            'branch': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter branch name',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Loan amount',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'installment': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Monthly installment',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'fromdate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date',
                'required': True
            }),
            'todate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date',
                'required': True
            }),
        }
        labels = {
            'empid': 'Employee',
            'bankname': 'Bank Name',
            'branch': 'Branch',
            'amount': 'Loan Amount',
            'installment': 'Monthly Installment',
            'fromdate': 'From Date',
            'todate': 'To Date',
        }

    def clean_fromdate(self):
        """Convert from date to DD-MM-YYYY format."""
        fromdate = self.cleaned_data.get('fromdate')
        if fromdate:
            from datetime import datetime
            if isinstance(fromdate, str):
                return fromdate
            return fromdate.strftime('%d-%m-%Y')
        return fromdate

    def clean_todate(self):
        """Convert to date to DD-MM-YYYY format."""
        todate = self.cleaned_data.get('todate')
        if todate:
            from datetime import datetime
            if isinstance(todate, str):
                return todate
            return todate.strftime('%d-%m-%Y')
        return todate


class MobileBillForm(forms.ModelForm):
    """
    Form for Mobile Bill transaction.
    Converted from: aspnet/Module/HR/Transactions/MobileBill.aspx
    Tracks employee mobile bill records.
    """

    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    # Employee selection
    empid = forms.ModelChoiceField(
        queryset=TblhrOfficestaff.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'required': True
        }),
        label='Employee',
        empty_label='Select Employee',
        to_field_name='empid'
    )

    billmonth = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'required': True
        }),
        label='Bill Month'
    )

    class Meta:
        model = TblhrMobilebill
        fields = ['empid', 'billmonth', 'billamt', 'taxes']
        widgets = {
            'billamt': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Bill amount',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'taxes': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Taxes',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'empid': 'Employee',
            'billmonth': 'Bill Month',
            'billamt': 'Bill Amount',
            'taxes': 'Taxes',
        }


# ============================================================================
# PHASE 4: OFFER LETTER MANAGEMENT FORM
# ============================================================================

class OfferLetterForm(forms.ModelForm):
    """
    Form for Offer Letter transaction.
    Converted from: aspnet/Module/HR/Transactions/OfferLetter.aspx
    Creates offer letters with salary breakdown.
    """

    SALARY_TYPE_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Annual', 'Annual'),
        ('Hourly', 'Hourly'),
    ]

    DUTY_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Contract', 'Contract'),
    ]

    salary_type = forms.ChoiceField(
        choices=SALARY_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Salary Type',
        required=False
    )

    dutytype = forms.ChoiceField(
        choices=DUTY_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Duty Type',
        required=False
    )

    designation = forms.ModelChoiceField(
        queryset=TblhrDesignation.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Designation',
        empty_label='Select Designation',
        required=False
    )

    # File upload for photo
    photodata = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': 'image/*'
        }),
        label='Candidate Photo',
        required=False
    )

    class Meta:
        model = TblhrOfferMaster
        fields = ['employeename', 'designation', 'othrs', 'address', 'contactno', 'remarks']
        # Note: photodata, salary_type, and dutytype are handled as separate field instances above
        # Model uses 'employeename' not 'offername', 'contactno' not 'phone', 'remarks' not 'remark'
        widgets = {
            'employeename': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter candidate name',
                'required': True
            }),
            'othrs': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'OT rate per hour',
                'step': '0.01',
                'min': '0'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter address',
                'rows': 3
            }),
            'contactno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Contact number'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Remarks',
                'rows': 2
            }),
        }
        labels = {
            'employeename': 'Candidate Name',
            'designation': 'Designation',
            'othrs': 'OT Rate (per hour)',
            'address': 'Address',
            'contactno': 'Contact Number',
            'remarks': 'Remarks',
        }


# ============================================================================
# PHASE 5: TOUR INTIMATION FORM
# ============================================================================

class TourIntimationForm(forms.ModelForm):
    """
    Form for Tour Intimation transaction.
    Converted from: aspnet/Module/HR/Transactions/TourIntimation.aspx
    Tracks employee tour/travel requests.
    """

    # Employee selection
    empid = forms.ModelChoiceField(
        queryset=TblhrOfficestaff.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'required': True
        }),
        label='Employee',
        empty_label='Select Employee',
        to_field_name='empid'
    )

    # Business Group selection
    bggroupid = forms.ModelChoiceField(
        queryset=Businessgroup.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Business Group',
        empty_label='Select Business Group',
        required=False
    )

    class Meta:
        model = TblaccTourintimationMaster
        fields = ['empid', 'type', 'wono', 'bggroupid', 'projectname',
                  'tourstartdate', 'tourstarttime', 'tourenddate', 'tourendtime',
                  'noofdays', 'nameaddressserprovider', 'contactperson', 'contactno',
                  'email', 'placeoftourcountry', 'placeoftourstate', 'placeoftourcity']

        widgets = {
            'type': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Type (numeric)'
            }),
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Work Order Number'
            }),
            'projectname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter project name'
            }),
            'tourstartdate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'tourstarttime': forms.TimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'time'
            }),
            'tourenddate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'tourendtime': forms.TimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'time'
            }),
            'noofdays': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Number of days',
                'min': '0'
            }),
            'nameaddressserprovider': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Service Provider Name and Address',
                'rows': 3
            }),
            'contactperson': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Contact Person'
            }),
            'contactno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Contact Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Email Address'
            }),
            'placeoftourcountry': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Country ID'
            }),
            'placeoftourstate': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'State ID'
            }),
            'placeoftourcity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'City ID'
            }),
        }

        labels = {
            'empid': 'Employee',
            'type': 'Type',
            'wono': 'Work Order No',
            'bggroupid': 'Business Group',
            'projectname': 'Project Name',
            'tourstartdate': 'Tour Start Date',
            'tourstarttime': 'Tour Start Time',
            'tourenddate': 'Tour End Date',
            'tourendtime': 'Tour End Time',
            'noofdays': 'No of Days',
            'nameaddressserprovider': 'Service Provider Name/Address',
            'contactperson': 'Contact Person',
            'contactno': 'Contact No',
            'email': 'Email',
            'placeoftourcountry': 'Place of Tour (Country)',
            'placeoftourstate': 'Place of Tour (State)',
            'placeoftourcity': 'Place of Tour (City)',
        }

    def clean_tourstartdate(self):
        """Convert tour start date to DD-MM-YYYY format."""
        date = self.cleaned_data.get('tourstartdate')
        if date:
            from datetime import datetime
            if isinstance(date, str):
                return date
            return date.strftime('%d-%m-%Y')
        return date

    def clean_tourenddate(self):
        """Convert tour end date to DD-MM-YYYY format."""
        date = self.cleaned_data.get('tourenddate')
        if date:
            from datetime import datetime
            if isinstance(date, str):
                return date
            return date.strftime('%d-%m-%Y')
        return date


# ============================================================================
# PHASE 6: GATE PASS MANAGEMENT FORM
# ============================================================================

class GatePassForm(forms.ModelForm):
    """
    Form for Gate Pass transaction.
    Converted from: aspnet/Module/HR/Transactions/GatePass.aspx
    Manages employee gate pass authorization.

    Note: This model only has basic fields (gpno, empid, authorize, authorizedby).
    The detailed gate pass information is stored in TblgatepassDetails model.
    """

    class Meta:
        model = TblgatePass
        fields = ['gpno', 'empid', 'authorizedby']
        widgets = {
            'gpno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Gate Pass Number'
            }),
            'empid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Employee ID'
            }),
            'authorizedby': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Authorized By'
            }),
        }
        labels = {
            'gpno': 'Gate Pass Number',
            'empid': 'Employee ID',
            'authorizedby': 'Authorized By',
        }
