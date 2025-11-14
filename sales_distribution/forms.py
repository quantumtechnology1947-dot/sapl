"""
Sales Distribution Forms - Converted from ASP.NET Module/SalesDistribution
All forms use ModelForm with Tailwind CSS styling.
"""

from django import forms
from django.forms import inlineformset_factory
from django.core.validators import EmailValidator, RegexValidator
from decimal import Decimal
from django.core.exceptions import ValidationError

# Import Tailwind widgets from core
from core.widgets import (
    TailwindTextInput, TailwindTextarea, TailwindSelect,
    TailwindNumberInput, TailwindEmailInput, TailwindDateInput,
    TailwindCheckboxInput, HTMXSelect
)

from .models import (
    SdCustMaster, TblsdWoCategory, TblsdWoSubcategory,
    SdCustEnquiryMaster, SdCustEnquiryAttachMaster,
    SdCustQuotationMaster, SdCustQuotationDetails,
    SdCustPoMaster, SdCustPoDetails,
    SdCustWorkorderMaster, SdCustWorkorderProductsDetails,
    SdCustWorkorderRelease, SdCustWorkorderDispatch
)
from sys_admin.models import Tblcountry, Tblstate, Tblcity, UnitMaster
from human_resource.models import Businessgroup


class DynamicChoiceField(forms.ChoiceField):
    """
    ChoiceField that doesn't validate against the choices list.
    Allows any value to be submitted (useful for dynamically populated dropdowns).
    """
    def validate(self, value):
        """Skip choice validation, only check if required."""
        if self.required and not value:
            from django.core.exceptions import ValidationError
            raise ValidationError(self.error_messages['required'], code='required')
        # Don't validate against choices - allow any value


class CustomerForm(forms.ModelForm):
    """
    Form for creating/updating customers with three address types.
    Converted from: aspnet/Module/SalesDistribution/Masters/CustomerMaster_New.aspx
    Requirements: 2.1, 2.2, 2.3, 3.1-3.7, 4.1-4.7, 5.1-5.7, 6.1-6.6, 7.1-7.4
    """
    
    # Customer Name
    customername = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': "Enter customer's name"
        }),
        label="Customer's Name"
    )
    
    # ========== REGISTERED OFFICE ADDRESS ==========
    regdaddress = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter registered office address'
        }),
        label='Address'
    )
    
    # Note: regdcountry/regdstate are IntegerFields in model, not ForeignKeys
    # So we use TypedChoiceField to populate dropdown but save as integer ID
    regdcountry = forms.TypedChoiceField(
        coerce=int,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/states-by-country/',
            'hx-trigger': 'change',
            'hx-target': '#regdstate-container',
            'hx-include': '[name="regdcountry"]',
            'data-prefix': 'regd'
        }),
        label='Country'
    )

    regdstate = forms.TypedChoiceField(
        coerce=int,
        choices=[('', 'Select')],  # Initialize with empty choice
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/cities-by-state/',
            'hx-trigger': 'change',
            'hx-target': '#regdcity-container',
            'hx-include': '[name="regdstate"]',
            'data-prefix': 'regd'
        }),
        label='State'
    )

    # Note: regdcity is a ForeignKey in model, so ModelChoiceField is appropriate
    regdcity = forms.ModelChoiceField(
        queryset=Tblcity.objects.none(),
        empty_label="Select",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='City'
    )
    
    regdpinno = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter PIN code'
        }),
        label='PIN No.'
    )
    
    regdcontactno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact number'
        }),
        label='Contact No.'
    )

    # NOTE: Fax fields exist in database but excluded from form per user request
    # regdfaxno = forms.CharField(
    #     max_length=50,
    #     required=False,
    #     widget=forms.TextInput(attrs={
    #         'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
    #         'placeholder': 'Enter fax number'
    #     }),
    #     label='Fax No.'
    # )

    # ========== WORKS/FACTORY ADDRESS ==========
    workaddress = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter works/factory address'
        }),
        label='Address'
    )
    
    # Note: workcountry/workstate are IntegerFields in model, not ForeignKeys
    workcountry = forms.TypedChoiceField(
        coerce=int,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/states-by-country/',
            'hx-trigger': 'change',
            'hx-target': '#workstate-container',
            'hx-include': '[name="workcountry"]',
            'data-prefix': 'work'
        }),
        label='Country'
    )

    workstate = forms.TypedChoiceField(
        coerce=int,
        choices=[('', 'Select')],  # Initialize with empty choice
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/cities-by-state/',
            'hx-trigger': 'change',
            'hx-target': '#workcity-container',
            'hx-include': '[name="workstate"]',
            'data-prefix': 'work'
        }),
        label='State'
    )

    # Note: workcity is a ForeignKey in model
    workcity = forms.ModelChoiceField(
        queryset=Tblcity.objects.none(),
        empty_label="Select",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='City'
    )
    
    workpinno = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter PIN code'
        }),
        label='PIN No.'
    )
    
    workcontactno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact number'
        }),
        label='Contact No.'
    )

    # NOTE: Fax fields exist in database but excluded from form per user request
    # workfaxno = forms.CharField(
    #     max_length=50,
    #     required=False,
    #     widget=forms.TextInput(attrs={
    #         'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
    #         'placeholder': 'Enter fax number'
    #     }),
    #     label='Fax No.'
    # )

    # ========== MATERIAL DELIVERY ADDRESS ==========
    materialdeladdress = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter material delivery address'
        }),
        label='Address'
    )
    
    # Note: materialdelcountry/materialdelstate are IntegerFields in model, not ForeignKeys
    materialdelcountry = forms.TypedChoiceField(
        coerce=int,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/states-by-country/',
            'hx-trigger': 'change',
            'hx-target': '#materialdelstate-container',
            'hx-include': '[name="materialdelcountry"]',
            'data-prefix': 'materialdel'
        }),
        label='Country'
    )

    materialdelstate = forms.TypedChoiceField(
        coerce=int,
        choices=[('', 'Select')],  # Initialize with empty choice
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/cities-by-state/',
            'hx-trigger': 'change',
            'hx-target': '#materialdelcity-container',
            'hx-include': '[name="materialdelstate"]',
            'data-prefix': 'materialdel'
        }),
        label='State'
    )

    # Note: materialdelcity is a ForeignKey in model
    materialdelcity = forms.ModelChoiceField(
        queryset=Tblcity.objects.none(),
        empty_label="Select",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='City'
    )
    
    materialdelpinno = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter PIN code'
        }),
        label='PIN No.'
    )
    
    materialdelcontactno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact number'
        }),
        label='Contact No.'
    )
    
    # ========== CONTACT PERSON ==========
    contactperson = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact person name'
        }),
        label='Contact Person'
    )
    
    email = forms.EmailField(
        required=True,
        validators=[
            EmailValidator(),
            RegexValidator(
                regex=r'\w+([-+.\']\w+)*@\w+([-.]\\w+)*\.\w+([-.]\\w+)*',
                message='Invalid email format'
            )
        ],
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter email address'
        }),
        label='E-mail'
    )
    
    contactno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact number'
        }),
        label='Contact No.'
    )
    
    # ========== GST/TAX INFORMATION ==========
    tincstno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter GST number'
        }),
        label='GST No.'
    )
    
    # ========== REMARKS ==========
    remark = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter remarks (optional)'
        }),
        label='Remarks'
    )

    # Non-model fields for legacy tax columns (optional - not displayed in main form)
    juridictioncode = forms.CharField(max_length=100, required=False, label='Juridiction Code', widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    eccno = forms.CharField(max_length=100, required=False, label='ECC.No.', widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    range = forms.CharField(max_length=100, required=False, label='Range', widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    commissionurate = forms.CharField(max_length=100, required=False, label='Commissionurate', widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    divn = forms.CharField(max_length=100, required=False, label='Divn', widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    panno = forms.CharField(max_length=100, required=False, label='PAN No.', widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    tinvatno = forms.CharField(max_length=100, required=False, label='TIN/VAT No.', widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    tdscode = forms.CharField(max_length=100, required=False, label='TDS Code', widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))


    class Meta:
        model = SdCustMaster
        fields = [
            'customername',
            'regdaddress', 'regdcountry', 'regdstate', 'regdcity', 'regdpinno', 'regdcontactno',
            'workaddress', 'workcountry', 'workstate', 'workcity', 'workpinno', 'workcontactno',
            'materialdeladdress', 'materialdelcountry', 'materialdelstate', 'materialdelcity',
            'materialdelpinno', 'materialdelcontactno',
            'contactperson', 'email', 'contactno',
            'tincstno', 'remark',
            # Add non-model fields here to control order
            'juridictioncode', 'eccno', 'range', 'commissionurate', 'divn',
            'panno', 'tinvatno', 'tdscode'
        ]
    
    def __init__(self, *args, **kwargs):
        # IMPORTANT: Populate choices BEFORE calling super().__init__()
        # so they're available during form field validation

        # Get POST data if it exists
        data = args[0] if args else None

        # Pre-populate country choices (always needed, done before super())
        country_choices = [('', 'Select')] + [
            (c.cid, str(c)) for c in Tblcountry.objects.all().order_by('countryname')
        ]

        # Pre-populate state choices if POST data contains country selections
        regdstate_choices = [('', 'Select')]
        workstate_choices = [('', 'Select')]
        materialdelstate_choices = [('', 'Select')]

        if data:
            # Build state choices based on selected countries in POST data
            if 'regdcountry' in data and data['regdcountry']:
                regdstate_choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=data['regdcountry']
                    ).order_by('statename')
                ]

            if 'workcountry' in data and data['workcountry']:
                workstate_choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=data['workcountry']
                    ).order_by('statename')
                ]

            if 'materialdelcountry' in data and data['materialdelcountry']:
                materialdelstate_choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=data['materialdelcountry']
                    ).order_by('statename')
                ]

        # Set choices on field definitions before super().__init__()
        # This ensures they're available when the form validates
        self.base_fields['regdcountry'].choices = country_choices
        self.base_fields['workcountry'].choices = country_choices
        self.base_fields['materialdelcountry'].choices = country_choices

        self.base_fields['regdstate'].choices = regdstate_choices
        self.base_fields['workstate'].choices = workstate_choices
        self.base_fields['materialdelstate'].choices = materialdelstate_choices

        # NOW call super().__init__() with pre-populated choices
        super().__init__(*args, **kwargs)

        # After super() init, set the final choices on self.fields
        self.fields['regdcountry'].choices = country_choices
        self.fields['workcountry'].choices = country_choices
        self.fields['materialdelcountry'].choices = country_choices

        self.fields['regdstate'].choices = regdstate_choices
        self.fields['workstate'].choices = workstate_choices
        self.fields['materialdelstate'].choices = materialdelstate_choices

        # Handle POST data - populate city querysets
        if data:
            # Registered Office city
            if 'regdstate' in data and data['regdstate']:
                self.fields['regdcity'].queryset = Tblcity.objects.filter(
                    sid_id=data['regdstate']
                ).order_by('cityname')

            # Works/Factory city
            if 'workstate' in data and data['workstate']:
                self.fields['workcity'].queryset = Tblcity.objects.filter(
                    sid_id=data['workstate']
                ).order_by('cityname')

            # Material Delivery city
            if 'materialdelstate' in data and data['materialdelstate']:
                self.fields['materialdelcity'].queryset = Tblcity.objects.filter(
                    sid_id=data['materialdelstate']
                ).order_by('cityname')

        # If editing, populate dependent dropdowns from instance
        elif self.instance.pk:
            # Registered Office
            if self.instance.regdcountry:
                state_choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=self.instance.regdcountry
                    ).order_by('statename')
                ]
                self.fields['regdstate'].choices = state_choices

            if self.instance.regdstate:
                self.fields['regdcity'].queryset = Tblcity.objects.filter(
                    sid_id=self.instance.regdstate
                ).order_by('cityname')

            # Works/Factory
            if self.instance.workcountry:
                state_choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=self.instance.workcountry
                    ).order_by('statename')
                ]
                self.fields['workstate'].choices = state_choices

            if self.instance.workstate:
                self.fields['workcity'].queryset = Tblcity.objects.filter(
                    sid_id=self.instance.workstate
                ).order_by('cityname')

            # Material Delivery
            if self.instance.materialdelcountry:
                state_choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=self.instance.materialdelcountry
                    ).order_by('statename')
                ]
                self.fields['materialdelstate'].choices = state_choices

            if self.instance.materialdelstate:
                self.fields['materialdelcity'].queryset = Tblcity.objects.filter(
                    sid_id=self.instance.materialdelstate
                ).order_by('cityname')

    def full_clean(self):
        """Override full_clean to ensure choices are populated before validation."""
        # This method is called before field validation, so we can populate choices here
        if hasattr(self, 'data') and self.data:
            # Populate state choices based on submitted country values
            if 'regdcountry' in self.data and self.data['regdcountry']:
                self.fields['regdstate'].choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=self.data['regdcountry']
                    ).order_by('statename')
                ]

            if 'workcountry' in self.data and self.data['workcountry']:
                self.fields['workstate'].choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=self.data['workcountry']
                    ).order_by('statename')
                ]

            if 'materialdelcountry' in self.data and self.data['materialdelcountry']:
                self.fields['materialdelstate'].choices = [('', 'Select')] + [
                    (s.sid, str(s)) for s in Tblstate.objects.filter(
                        cid_id=self.data['materialdelcountry']
                    ).order_by('statename')
                ]

            # Populate city querysets based on submitted state values
            if 'regdstate' in self.data and self.data['regdstate']:
                self.fields['regdcity'].queryset = Tblcity.objects.filter(
                    sid_id=self.data['regdstate']
                ).order_by('cityname')

            if 'workstate' in self.data and self.data['workstate']:
                self.fields['workcity'].queryset = Tblcity.objects.filter(
                    sid_id=self.data['workstate']
                ).order_by('cityname')

            if 'materialdelstate' in self.data and self.data['materialdelstate']:
                self.fields['materialdelcity'].queryset = Tblcity.objects.filter(
                    sid_id=self.data['materialdelstate']
                ).order_by('cityname')

        # Now call parent's full_clean() which will validate fields
        super().full_clean()

    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email')
        if email:
            return email.strip()
        return email
    
    def clean_regdpinno(self):
        """Validate registered PIN code is numeric."""
        pinno = self.cleaned_data.get('regdpinno')
        if pinno and not pinno.replace(' ', '').isdigit():
            raise forms.ValidationError('PIN code must be numeric.')
        return pinno
    
    def clean_workpinno(self):
        """Validate works PIN code is numeric."""
        pinno = self.cleaned_data.get('workpinno')
        if pinno and not pinno.replace(' ', '').isdigit():
            raise forms.ValidationError('PIN code must be numeric.')
        return pinno
    
    def clean_materialdelpinno(self):
        """Validate material delivery PIN code is numeric."""
        pinno = self.cleaned_data.get('materialdelpinno')
        if pinno and not pinno.replace(' ', '').isdigit():
            raise forms.ValidationError('PIN code must be numeric.')
        return pinno
    
    def clean_customername(self):
        """Validate customer name is not empty."""
        customername = self.cleaned_data.get('customername')
        if not customername or not customername.strip():
            raise forms.ValidationError('Customer name is required.')
        return customername.strip()
    
    def clean_tincstno(self):
        """Validate GST number is not empty."""
        tincstno = self.cleaned_data.get('tincstno')
        if not tincstno or not tincstno.strip():
            raise forms.ValidationError('GST No is required.')
        return tincstno.strip()


# ============================================================================
# WO CATEGORY FORM
# ============================================================================

class WoCategoryForm(forms.ModelForm):
    """
    Form for Work Order Category Master.
    Converted from: aspnet/Module/SalesDistribution/Masters/CategoryNew.aspx
    """
    
    class Meta:
        model = TblsdWoCategory
        fields = ['cname', 'symbol', 'hassubcat']
        
        widgets = {
            'cname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter category name'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol (1 character)',
                'maxlength': '1'
            }),
            'hassubcat': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500'
            }),
        }
        
        labels = {
            'cname': 'Category Name',
            'symbol': 'Symbol',
            'hassubcat': 'Has Sub-Category',
        }
    
    def clean_cname(self):
        """Validate category name is not empty."""
        cname = self.cleaned_data.get('cname')
        if not cname or not cname.strip():
            raise forms.ValidationError('Category name is required.')
        return cname.strip()
    
    def clean_symbol(self):
        """Validate symbol is exactly 1 character."""
        symbol = self.cleaned_data.get('symbol')
        if not symbol or not symbol.strip():
            raise forms.ValidationError('Symbol is required.')
        if len(symbol.strip()) != 1:
            raise forms.ValidationError('Symbol must be exactly 1 character.')
        return symbol.strip()


# ============================================================================
# WO SUB-CATEGORY FORM
# ============================================================================

class WoSubCategoryForm(forms.ModelForm):
    """
    Form for Work Order Sub-Category Master.
    Converted from: aspnet/Module/SalesDistribution/Masters/SubCategoryNew.aspx
    """
    
    cid = forms.ModelChoiceField(
        queryset=TblsdWoCategory.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Category'
    )
    
    class Meta:
        model = TblsdWoSubcategory
        fields = ['cid', 'scname', 'symbol']
        
        widgets = {
            'scname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter sub-category name'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol (1 character)',
                'maxlength': '1'
            }),
        }
        
        labels = {
            'scname': 'Sub-Category Name',
            'symbol': 'Symbol',
        }
    
    def clean_scname(self):
        """Validate sub-category name is not empty."""
        scname = self.cleaned_data.get('scname')
        if not scname or not scname.strip():
            raise forms.ValidationError('Sub-category name is required.')
        return scname.strip()
    
    def clean_symbol(self):
        """Validate symbol is exactly 1 character."""
        symbol = self.cleaned_data.get('symbol')
        if not symbol or not symbol.strip():
            raise forms.ValidationError('Symbol is required.')
        if len(symbol.strip()) != 1:
            raise forms.ValidationError('Symbol must be exactly 1 character.')
        return symbol.strip()



# ============================================================================
# CUSTOMER ENQUIRY FORM
# ============================================================================

# This is the replacement CustomerEnquiryForm that mirrors CustomerForm structure
# To be inserted at line 675 in sales_distribution/forms.py

class CustomerEnquiryForm(forms.ModelForm):
    """
    Form for Customer Enquiry with full customer address fields.
    Allows creating NEW customer or selecting EXISTING customer.
    Converted from: aspnet/Module/SalesDistribution/Transactions/CustEnquiry_New.aspx

    Key difference from CustomerForm: Saves to SdCustEnquiryMaster, not SdCustMaster
    """

    # Customer Name
    customername = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': "Enter customer's name"
        }),
        label="Customer's Name"
    )

    # ========== REGISTERED OFFICE ADDRESS ==========
    regdaddress = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter registered office address'
        }),
        label='Address'
    )

    # Note: In enquiry model, country/state/city are ALL TextFields (not ForeignKey)
    # So we use ChoiceField for all dropdowns but save as text
    regdcountry = forms.ChoiceField(
        choices=[('', 'Select')],  # Populated in __init__
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/states-by-country/?use_names=true',
            'hx-trigger': 'change',
            'hx-target': '#regdstate-container',
            'hx-include': '[name="regdcountry"]',
            'data-prefix': 'regd'
        }),
        label='Country'
    )

    regdstate = DynamicChoiceField(
        choices=[('', 'Select')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/cities-by-state/?use_names=true',
            'hx-trigger': 'change',
            'hx-target': '#regdcity-container',
            'hx-include': '[name="regdstate"]',
            'data-prefix': 'regd'
        }),
        label='State'
    )

    regdcity = DynamicChoiceField(
        choices=[('', 'Select')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='City'
    )

    regdpinno = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter PIN code'
        }),
        label='PIN No.'
    )

    regdcontactno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact number'
        }),
        label='Contact No.'
    )

    # ========== WORKS/FACTORY ADDRESS ==========
    workaddress = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter works/factory address'
        }),
        label='Address'
    )

    workcountry = forms.ChoiceField(
        choices=[('', 'Select')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/states-by-country/?use_names=true',
            'hx-trigger': 'change',
            'hx-target': '#workstate-container',
            'hx-include': '[name="workcountry"]',
            'data-prefix': 'work'
        }),
        label='Country'
    )

    workstate = DynamicChoiceField(
        choices=[('', 'Select')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/cities-by-state/?use_names=true',
            'hx-trigger': 'change',
            'hx-target': '#workcity-container',
            'hx-include': '[name="workstate"]',
            'data-prefix': 'work'
        }),
        label='State'
    )

    workcity = DynamicChoiceField(
        choices=[('', 'Select')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='City'
    )

    workpinno = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter PIN code'
        }),
        label='PIN No.'
    )

    workcontactno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact number'
        }),
        label='Contact No.'
    )

    # ========== MATERIAL DELIVERY ADDRESS ==========
    materialdeladdress = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter material delivery address'
        }),
        label='Address'
    )

    materialdelcountry = forms.ChoiceField(
        choices=[('', 'Select')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/states-by-country/?use_names=true',
            'hx-trigger': 'change',
            'hx-target': '#materialdelstate-container',
            'hx-include': '[name="materialdelcountry"]',
            'data-prefix': 'materialdel'
        }),
        label='Country'
    )

    materialdelstate = DynamicChoiceField(
        choices=[('', 'Select')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/customer/cities-by-state/?use_names=true',
            'hx-trigger': 'change',
            'hx-target': '#materialdelcity-container',
            'hx-include': '[name="materialdelstate"]',
            'data-prefix': 'materialdel'
        }),
        label='State'
    )

    materialdelcity = DynamicChoiceField(
        choices=[('', 'Select')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='City'
    )

    materialdelpinno = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter PIN code'
        }),
        label='PIN No.'
    )

    materialdelcontactno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact number'
        }),
        label='Contact No.'
    )

    # ========== CONTACT PERSON ==========
    contactperson = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact person name'
        }),
        label='Contact Person'
    )

    email = forms.EmailField(
        required=True,
        validators=[
            EmailValidator(),
            RegexValidator(
                regex=r'\w+([-+.\']\w+)*@\w+([-.]\\w+)*\.\w+([-.]\\w+)*',
                message='Invalid email format'
            )
        ],
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter email address'
        }),
        label='E-mail'
    )

    contactno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter contact number'
        }),
        label='Contact No.'
    )

    # ========== GST/TAX INFORMATION ==========
    tincstno = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter GST number'
        }),
        label='GST No.'
    )

    # ========== ENQUIRY SPECIFIC FIELDS ==========
    enquiryfor = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Describe what the customer is enquiring about'
        }),
        label='Enquiry For'
    )

    remark = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter remarks (optional)'
        }),
        label='Remarks'
    )

    class Meta:
        model = SdCustEnquiryMaster
        fields = [
            'customername',
            'regdaddress', 'regdcountry', 'regdstate', 'regdcity', 'regdpinno', 'regdcontactno',
            'workaddress', 'workcountry', 'workstate', 'workcity', 'workpinno', 'workcontactno',
            'materialdeladdress', 'materialdelcountry', 'materialdelstate', 'materialdelcity',
            'materialdelpinno', 'materialdelcontactno',
            'contactperson', 'email', 'contactno',
            'tincstno', 'enquiryfor', 'remark'
        ]

    def __init__(self, *args, **kwargs):
        """
        Initialize form with country/state/city choices.
        Similar to CustomerForm but saves names instead of IDs.
        """
        # Get POST data if it exists
        data = args[0] if args else None

        # Pre-populate country choices (always needed)
        country_choices = [('', 'Select')] + [
            (c.countryname, c.countryname) for c in Tblcountry.objects.all().order_by('countryname')
        ]

        # Pre-populate state choices if POST data contains country selections
        regdstate_choices = [('', 'Select')]
        workstate_choices = [('', 'Select')]
        materialdelstate_choices = [('', 'Select')]

        if data:
            # Build state choices based on selected countries in POST data
            if 'regdcountry' in data and data['regdcountry']:
                country = Tblcountry.objects.filter(countryname=data['regdcountry']).first()
                if country:
                    regdstate_choices = [('', 'Select')] + [
                        (s.statename, s.statename) for s in Tblstate.objects.filter(
                            cid_id=country.cid
                        ).order_by('statename')
                    ]

            if 'workcountry' in data and data['workcountry']:
                country = Tblcountry.objects.filter(countryname=data['workcountry']).first()
                if country:
                    workstate_choices = [('', 'Select')] + [
                        (s.statename, s.statename) for s in Tblstate.objects.filter(
                            cid_id=country.cid
                        ).order_by('statename')
                    ]

            if 'materialdelcountry' in data and data['materialdelcountry']:
                country = Tblcountry.objects.filter(countryname=data['materialdelcountry']).first()
                if country:
                    materialdelstate_choices = [('', 'Select')] + [
                        (s.statename, s.statename) for s in Tblstate.objects.filter(
                            cid_id=country.cid
                        ).order_by('statename')
                    ]

        # Set choices on field definitions before super().__init__()
        self.base_fields['regdcountry'].choices = country_choices
        self.base_fields['workcountry'].choices = country_choices
        self.base_fields['materialdelcountry'].choices = country_choices

        self.base_fields['regdstate'].choices = regdstate_choices
        self.base_fields['workstate'].choices = workstate_choices
        self.base_fields['materialdelstate'].choices = materialdelstate_choices

        # NOW call super().__init__()
        super().__init__(*args, **kwargs)

        # After super() init, set the final choices on self.fields
        self.fields['regdcountry'].choices = country_choices
        self.fields['workcountry'].choices = country_choices
        self.fields['materialdelcountry'].choices = country_choices

        self.fields['regdstate'].choices = regdstate_choices
        self.fields['workstate'].choices = workstate_choices
        self.fields['materialdelstate'].choices = materialdelstate_choices

        # Handle POST data - populate city choices
        regdcity_choices = [('', 'Select')]
        workcity_choices = [('', 'Select')]
        materialdelcity_choices = [('', 'Select')]

        if data:
            # Registered Office city
            if 'regdstate' in data and data['regdstate']:
                state = Tblstate.objects.filter(statename=data['regdstate']).first()
                if state:
                    regdcity_choices = [('', 'Select')] + [
                        (c.cityname, c.cityname) for c in Tblcity.objects.filter(
                            sid_id=state.sid
                        ).order_by('cityname')
                    ]

            # Works/Factory city
            if 'workstate' in data and data['workstate']:
                state = Tblstate.objects.filter(statename=data['workstate']).first()
                if state:
                    workcity_choices = [('', 'Select')] + [
                        (c.cityname, c.cityname) for c in Tblcity.objects.filter(
                            sid_id=state.sid
                        ).order_by('cityname')
                    ]

            # Material Delivery city
            if 'materialdelstate' in data and data['materialdelstate']:
                state = Tblstate.objects.filter(statename=data['materialdelstate']).first()
                if state:
                    materialdelcity_choices = [('', 'Select')] + [
                        (c.cityname, c.cityname) for c in Tblcity.objects.filter(
                            sid_id=state.sid
                        ).order_by('cityname')
                    ]

        self.fields['regdcity'].choices = regdcity_choices
        self.fields['workcity'].choices = workcity_choices
        self.fields['materialdelcity'].choices = materialdelcity_choices

        # If editing, populate dependent dropdowns from instance
        if self.instance.pk:
            # Registered Office
            if self.instance.regdcountry:
                country = Tblcountry.objects.filter(countryname=self.instance.regdcountry).first()
                if country:
                    state_choices = [('', 'Select')] + [
                        (s.statename, s.statename) for s in Tblstate.objects.filter(
                            cid_id=country.cid
                        ).order_by('statename')
                    ]
                    self.fields['regdstate'].choices = state_choices

            if self.instance.regdstate:
                state = Tblstate.objects.filter(statename=self.instance.regdstate).first()
                if state:
                    city_choices = [('', 'Select')] + [
                        (c.cityname, c.cityname) for c in Tblcity.objects.filter(
                            sid_id=state.sid
                        ).order_by('cityname')
                    ]
                    self.fields['regdcity'].choices = city_choices

            # Works/Factory
            if self.instance.workcountry:
                country = Tblcountry.objects.filter(countryname=self.instance.workcountry).first()
                if country:
                    state_choices = [('', 'Select')] + [
                        (s.statename, s.statename) for s in Tblstate.objects.filter(
                            cid_id=country.cid
                        ).order_by('statename')
                    ]
                    self.fields['workstate'].choices = state_choices

            if self.instance.workstate:
                state = Tblstate.objects.filter(statename=self.instance.workstate).first()
                if state:
                    city_choices = [('', 'Select')] + [
                        (c.cityname, c.cityname) for c in Tblcity.objects.filter(
                            sid_id=state.sid
                        ).order_by('cityname')
                    ]
                    self.fields['workcity'].choices = city_choices

            # Material Delivery
            if self.instance.materialdelcountry:
                country = Tblcountry.objects.filter(countryname=self.instance.materialdelcountry).first()
                if country:
                    state_choices = [('', 'Select')] + [
                        (s.statename, s.statename) for s in Tblstate.objects.filter(
                            cid_id=country.cid
                        ).order_by('statename')
                    ]
                    self.fields['materialdelstate'].choices = state_choices

            if self.instance.materialdelstate:
                state = Tblstate.objects.filter(statename=self.instance.materialdelstate).first()
                if state:
                    city_choices = [('', 'Select')] + [
                        (c.cityname, c.cityname) for c in Tblcity.objects.filter(
                            sid_id=state.sid
                        ).order_by('cityname')
                    ]
                    self.fields['materialdelcity'].choices = city_choices

    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email')
        if email:
            return email.strip()
        return email

    def clean_customername(self):
        """Validate customer name is not empty."""
        customername = self.cleaned_data.get('customername')
        if not customername or not customername.strip():
            raise forms.ValidationError('Customer name is required.')
        return customername.strip()

    def clean_enquiryfor(self):
        """Validate enquiry details."""
        enquiryfor = self.cleaned_data.get('enquiryfor')
        if not enquiryfor or not enquiryfor.strip():
            raise forms.ValidationError('Enquiry details are required.')
        return enquiryfor.strip()

    def clean_tincstno(self):
        """Validate GST number is not empty."""
        tincstno = self.cleaned_data.get('tincstno')
        if not tincstno or not tincstno.strip():
            raise forms.ValidationError('GST No is required.')
        return tincstno.strip()
class CustomerEnquiryAttachmentForm(forms.ModelForm):
    """
    Form for uploading attachments to enquiry.
    """
    
    file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png'
        }),
        label='Attachment'
    )
    
    class Meta:
        model = SdCustEnquiryAttachMaster
        fields = []
    
    def clean_file(self):
        """Validate file size (max 10MB)."""
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError('File size must be less than 10MB.')
        return file



# ============================================================================
# QUOTATION FORMS
# ============================================================================

class QuotationMasterForm(forms.ModelForm):
    """
    Form for Quotation Master.
    Converted from: aspnet/Module/SalesDistribution/Transactions/Quotation_New.aspx
    Note: enqid is passed as hidden field, not part of form validation
    """

    class Meta:
        model = SdCustQuotationMaster
        fields = ['paymentterms', 'deliveryterms', 'validity', 'warrenty', 'duedate', 'remarks']
        
        widgets = {
            'quotationno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Auto-generated'
            }),
            'paymentterms': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'deliveryterms': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'validity': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., 30 days'
            }),
            'warrenty': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., 12 months'
            }),
            'duedate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
        }
        
        labels = {
            'quotationno': 'Quotation No',
            'paymentterms': 'Payment Terms',
            'deliveryterms': 'Delivery Terms',
            'validity': 'Validity',
            'warrenty': 'Warranty',
            'duedate': 'Due Date',
            'remarks': 'Remarks',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # enquiry and quotationno are passed as hidden fields, not part of form


class QuotationDetailForm(forms.ModelForm):
    """
    Form for Quotation Line Items.
    """
    
    unit = forms.ModelChoiceField(
        queryset=UnitMaster.objects.all(),
        empty_label="Select Unit",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Unit'
    )
    
    class Meta:
        model = SdCustQuotationDetails
        fields = ['itemdesc', 'totalqty', 'unit', 'rate', 'discount']
        
        widgets = {
            'itemdesc': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 2,
                'placeholder': 'Item description'
            }),
            'totalqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'value': '0'
            }),
        }
        
        labels = {
            'itemdesc': 'Item Description',
            'totalqty': 'Quantity',
            'rate': 'Rate',
            'discount': 'Discount (%)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].label_from_instance = lambda obj: f"{obj.unitname} ({obj.symbol})"
        self.fields['discount'].required = False



# ============================================================================
# CUSTOMER PO FORMS
# ============================================================================

class CustomerPoForm(forms.ModelForm):
    """
    Form for Customer Purchase Order.
    Converted from: aspnet/Module/SalesDistribution/Transactions/CustPO_New.aspx
    Requirements: 1.1, 1.2, 1.5, 1.6, 1.7
    """
    
    # Quotation selection with HTMX auto-populate
    quotation = forms.ModelChoiceField(
        queryset=SdCustQuotationMaster.objects.filter(authorize=1),
        empty_label="Select Quotation",
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/sales/po/quotation-details/',
            'hx-trigger': 'change',
            'hx-target': '#quotation-details',
            'hx-include': '[name="quotation"]'
        }),
        label='Quotation (Optional)'
    )
    
    enquiry = forms.ModelChoiceField(
        queryset=SdCustEnquiryMaster.objects.all(),
        empty_label="Select Enquiry",
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Enquiry (Optional)'
    )
    
    # File upload for PO document
    po_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx'
        }),
        label='PO Document (Optional)'
    )
    
    class Meta:
        model = SdCustPoMaster
        fields = ['quotation', 'enquiry', 'customerid', 'pono', 'podate', 'poreceiveddate', 'vendorcode', 'paymentterms', 'pf', 'vat', 'excise', 'octroi', 'cst', 'warrenty', 'insurance', 'transport', 'noteno', 'registrationno', 'freight', 'validity', 'othercharges', 'remarks']
        
        widgets = {
            'customerid': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': 'Customer ID',
                'readonly': 'readonly'
            }),
            'pono': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': 'PO Number'
            }),
            'podate': forms.DateInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'type': 'date'
            }),
            'poreceiveddate': forms.DateInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'type': 'date'
            }),
            'vendorcode': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': 'Vendor Code'
            }),
            'paymentterms': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'rows': 2,
                'placeholder': 'Enter payment terms'
            }),
            'pf': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'vat': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'excise': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': 'GST/Excise'
            }),
            'octroi': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'cst': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'warrenty': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'insurance': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'transport': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'noteno': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'registrationno': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'freight': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'validity': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'othercharges': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'placeholder': '-'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded px-2 py-1 text-xs',
                'rows': 3,
                'placeholder': 'Enter remarks (optional)'
            }),
        }
        
        labels = {
            'pono': 'PO Number',
            'podate': 'PO Date',
            'poreceiveddate': 'PO Received Date',
            'customerid': 'Customer ID',
            'vendorcode': 'Vendor Code',
            'paymentterms': 'Payment Terms',
            'pf': 'P&F',
            'vat': 'VAT',
            'excise': 'Excise',
            'octroi': 'Octroi',
            'cst': 'CST',
            'warrenty': 'Warranty',
            'insurance': 'Insurance',
            'transport': 'Transport',
            'noteno': 'GC Note No',
            'registrationno': 'Registration No',
            'freight': 'Freight',
            'validity': 'Validity',
            'othercharges': 'Other Charges',
            'remarks': 'Remarks',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enquiry'].label_from_instance = lambda obj: f"ENQ-{obj.enqid} - {obj.customername}"
        self.fields['quotation'].label_from_instance = lambda obj: f"QT-{obj.id} - {obj.customerid}"
    
    def clean_po_file(self):
        """Validate file size and type."""
        file = self.cleaned_data.get('po_file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB.')
            
            # Check file type
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'application/vnd.ms-excel',
                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
            if file.content_type not in allowed_types:
                raise forms.ValidationError('Only PDF, DOC, DOCX, XLS, XLSX files are allowed.')
        return file
    
    def clean_pono(self):
        """Validate PO number is not empty."""
        pono = self.cleaned_data.get('pono')
        if not pono or not pono.strip():
            raise forms.ValidationError('PO Number is required.')
        return pono.strip()
    
    def clean_customerid(self):
        """Validate customer ID format if provided (auto-populated from enquiry)."""
        customerid = self.cleaned_data.get('customerid')
        if customerid:
            return customerid.strip()
        # Allow empty - will be set from enquiry in view's form_valid()
        return customerid

    def clean_vendorcode(self):
        """Validate vendor code is required (matches ASP.NET behavior)."""
        vendorcode = self.cleaned_data.get('vendorcode')
        if not vendorcode or not vendorcode.strip():
            raise forms.ValidationError('Vendor Code is required.')
        return vendorcode.strip()


class CustomerPoDetailForm(forms.ModelForm):
    """
    Form for Customer PO Line Items.
    Converted from: aspnet/Module/SalesDistribution/Transactions/CustPO_New_Details.aspx
    Requirements: 1.3, 1.4
    """
    
    unit = forms.ModelChoiceField(
        queryset=UnitMaster.objects.all(),
        empty_label="Select Unit",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Unit'
    )
    
    class Meta:
        model = SdCustPoDetails
        fields = ['itemdesc', 'totalqty', 'unit', 'rate', 'discount']
        
        widgets = {
            'itemdesc': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 2,
                'placeholder': 'Item description'
            }),
            'totalqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'value': '0'
            }),
        }
        
        labels = {
            'itemdesc': 'Item Description',
            'totalqty': 'Quantity',
            'rate': 'Rate',
            'discount': 'Discount (%)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].label_from_instance = lambda obj: f"{obj.unitname} ({obj.symbol})"
        self.fields['discount'].required = False
    
    def clean_totalqty(self):
        """Validate quantity is positive."""
        qty = self.cleaned_data.get('totalqty')
        if qty is not None and qty <= 0:
            raise forms.ValidationError('Quantity must be greater than zero.')
        return qty
    
    def clean_rate(self):
        """Validate rate is positive."""
        rate = self.cleaned_data.get('rate')
        if rate is not None and rate <= 0:
            raise forms.ValidationError('Rate must be greater than zero.')
        return rate


# Create formset for PO line items
CustomerPoDetailFormSet = inlineformset_factory(
    SdCustPoMaster,
    SdCustPoDetails,
    form=CustomerPoDetailForm,
    extra=0,  # Don't add extra empty forms in edit mode
    can_delete=True,
    min_num=1,
    validate_min=True
)



# ============================================================================
# PRODUCT MASTER FORM
# ============================================================================

class ProductForm(forms.Form):
    """
    Simple form for Product Master (item code and description).
    Note: Using Form instead of ModelForm as there's no dedicated Product model.
    Products are stored in SdCustWorkorderProductsDetails.
    Converted from: aspnet/Module/SalesDistribution/Masters/Product.aspx
    Requirements: 2.1, 2.2
    """
    
    itemcode = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter item code'
        }),
        label='Item Code'
    )
    
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter product description'
        }),
        label='Description'
    )
    
    def clean_itemcode(self):
        """Validate item code is not empty."""
        itemcode = self.cleaned_data.get('itemcode')
        if not itemcode or not itemcode.strip():
            raise forms.ValidationError('Item code is required.')
        return itemcode.strip()
    
    def clean_description(self):
        """Validate description is not empty."""
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise forms.ValidationError('Description is required.')
        return description.strip()



# ============================================================================
# WORK ORDER RELEASE FORM
# ============================================================================

class WorkOrderReleaseForm(forms.ModelForm):
    """
    Form for Work Order Release.
    Converted from: aspnet/Module/SalesDistribution/Transactions/WorkOrder_Release.aspx
    Requirements: 4.1, 4.2, 4.3
    """
    
    wono = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Work Order Number'
        }),
        label='Work Order Number'
    )
    
    class Meta:
        model = SdCustWorkorderRelease
        fields = ['wrno', 'wono', 'itemid', 'issuedqty']
        
        widgets = {
            'wrno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Work Release Number'
            }),
            'itemid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Item ID'
            }),
            'issuedqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
        }
        
        labels = {
            'wrno': 'WR Number',
            'wono': 'WO Number',
            'itemid': 'Item ID',
            'issuedqty': 'Issued Quantity',
        }
    
    def clean_issuedqty(self):
        """Validate issued quantity is positive."""
        qty = self.cleaned_data.get('issuedqty')
        if qty is not None and qty <= 0:
            raise forms.ValidationError('Issued quantity must be greater than zero.')
        return qty


# ============================================================================
# WORK ORDER DISPATCH FORM
# ============================================================================

class WorkOrderDispatchForm(forms.ModelForm):
    """
    Form for Work Order Dispatch.
    Converted from: aspnet/Module/SalesDistribution/Transactions/WorkOrder_Dispatch.aspx
    Requirements: 5.1, 5.2, 5.3
    """
    
    wrno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Work Release Number'
        }),
        label='WR Number'
    )
    
    class Meta:
        model = SdCustWorkorderDispatch
        fields = ['dano', 'wrno', 'wrid', 'itemid', 'issuedqty', 'dispatchqty', 'freightcharges', 'vehicleby', 'octroicharges']
        
        widgets = {
            'dano': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Dispatch Advice Number'
            }),
            'wrid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'WR ID'
            }),
            'itemid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Item ID'
            }),
            'issuedqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'readonly': 'readonly'
            }),
            'dispatchqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'freightcharges': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Freight charges'
            }),
            'vehicleby': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Vehicle details'
            }),
            'octroicharges': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Octroi charges'
            }),
        }
        
        labels = {
            'dano': 'DA Number',
            'wrno': 'WR Number',
            'wrid': 'WR ID',
            'itemid': 'Item ID',
            'issuedqty': 'Issued Quantity',
            'dispatchqty': 'Dispatch Quantity',
            'freightcharges': 'Freight Charges',
            'vehicleby': 'Vehicle By',
            'octroicharges': 'Octroi Charges',
        }
    
    def clean_dispatchqty(self):
        """Validate dispatch quantity doesn't exceed issued quantity."""
        dispatch_qty = self.cleaned_data.get('dispatchqty')
        issued_qty = self.cleaned_data.get('issuedqty')
        
        if dispatch_qty and issued_qty and dispatch_qty > issued_qty:
            raise forms.ValidationError('Dispatch quantity cannot exceed issued quantity.')
        
        if dispatch_qty is not None and dispatch_qty <= 0:
            raise forms.ValidationError('Dispatch quantity must be greater than zero.')
        
        return dispatch_qty



# ============================================================================
# WORK ORDER FORMS
# ============================================================================

class WorkOrderForm(forms.ModelForm):
    """
    Complete Work Order Form - Exact mirror of ASP.NET WorkOrder_New_Details.aspx
    Includes ALL fields from the 4-tab interface:
    - Tab 1: Task Execution (43 fields)
    - Tab 2: Shipping (14 fields)
    - Tab 3: Products (handled separately via temp table)
    - Tab 4: Instructions (5 fields)
    """

    # Override cid and scid as ChoiceFields since they're IntegerFields in model
    cid = forms.TypedChoiceField(
        coerce=int,
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'hx-get': '/sales/workorder/subcategory/',
            'hx-target': '#id_scid_container',
            'hx-swap': 'innerHTML'
        })
    )

    scid = forms.TypedChoiceField(
        coerce=int,
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )

    # Override taskbusinessgroup as ChoiceField since it's an IntegerField in model
    taskbusinessgroup = forms.TypedChoiceField(
        coerce=int,
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        label="Business Group"
    )

    # Override shipping location fields as ChoiceFields for cascading dropdowns
    shippingcountry = forms.TypedChoiceField(
        coerce=int,
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'hx-get': '/sales/workorder/states/',
            'hx-trigger': 'change',
            'hx-target': '#id_shippingstate_container',
            'hx-include': '[name="shippingcountry"]',
            'hx-swap': 'innerHTML'
        }),
        label="Country"
    )

    shippingstate = forms.TypedChoiceField(
        coerce=int,
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'hx-get': '/sales/workorder/cities/',
            'hx-trigger': 'change',
            'hx-target': '#id_shippingcity_container',
            'hx-include': '[name="shippingstate"]',
            'hx-swap': 'innerHTML'
        }),
        label="State"
    )

    shippingcity = forms.TypedChoiceField(
        coerce=int,
        required=False,
        empty_value=None,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        label="City"
    )

    # Override instruction checkbox fields as BooleanField (will convert to int in clean methods)
    # Model uses IntegerField but CheckboxInput needs BooleanField for proper validation
    instractionprimerpainting = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500'
        })
    )

    instractionpainting = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500'
        })
    )

    instractionselfcertrept = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate category choices
        self.fields['cid'].choices = [('', 'Select Category')] + [
            (cat.cid, cat.cname) for cat in TblsdWoCategory.objects.all().order_by('cname')
        ]

        # Populate business group choices
        self.fields['taskbusinessgroup'].choices = [('', 'Select Business Group')] + [
            (bg.id, bg.name) for bg in Businessgroup.objects.all().order_by('name')
        ]

        # Populate country choices (use 'cid' not 'countryid')
        self.fields['shippingcountry'].choices = [('', 'Select Country')] + [
            (country.cid, country.countryname)
            for country in Tblcountry.objects.all().order_by('countryname')
        ]

        # Get data and instance for conditional population
        # Use self.data if bound, otherwise try args[0]
        data = self.data if self.is_bound else (args[0] if args else None)
        instance = kwargs.get('instance')

        # Populate state and city choices based on instance or POST data
        if instance and instance.shippingcountry:
            # Edit mode: populate states for the selected country (use 'sid' and filter by 'cid')
            self.fields['shippingstate'].choices = [('', 'Select State')] + [
                (state.sid, state.statename)
                for state in Tblstate.objects.filter(cid=instance.shippingcountry).order_by('statename')
            ]
        elif data and data.get('shippingcountry'):
            # Form submission: populate based on selected country (use 'sid' and filter by 'cid')
            country_id = int(data.get('shippingcountry'))
            self.fields['shippingstate'].choices = [('', 'Select State')] + [
                (state.sid, state.statename)
                for state in Tblstate.objects.filter(cid=country_id).order_by('statename')
            ]
        else:
            # New form: empty state choices
            self.fields['shippingstate'].choices = [('', 'Select State')]

        if instance and instance.shippingstate:
            # Edit mode: populate cities for the selected state (filter by 'sid')
            self.fields['shippingcity'].choices = [('', 'Select City')] + [
                (city.cityid, city.cityname)
                for city in Tblcity.objects.filter(sid=instance.shippingstate).order_by('cityname')
            ]
        elif data and data.get('shippingstate'):
            # Form submission: populate based on selected state (filter by 'sid')
            state_id = int(data.get('shippingstate'))
            self.fields['shippingcity'].choices = [('', 'Select City')] + [
                (city.cityid, city.cityname)
                for city in Tblcity.objects.filter(sid=state_id).order_by('cityname')
            ]
        else:
            # New form: empty city choices
            self.fields['shippingcity'].choices = [('', 'Select City')]

        # Populate subcategory choices based on instance or POST data

        if instance and instance.cid:
            # Edit mode: populate subcategories for the selected category
            self.fields['scid'].choices = [('', 'Select Sub-Category')] + [
                (subcat.scid, subcat.scname)
                for subcat in TblsdWoSubcategory.objects.filter(cid=instance.cid).order_by('scname')
            ]
        elif data and data.get('cid'):
            # Form submission: populate based on selected category
            self.fields['scid'].choices = [('', 'Select Sub-Category')] + [
                (subcat.scid, subcat.scname)
                for subcat in TblsdWoSubcategory.objects.filter(cid=data.get('cid')).order_by('scname')
            ]
        else:
            # New form: empty subcategory choices
            self.fields['scid'].choices = [('', 'Select Sub-Category')]

    class Meta:
        model = SdCustWorkorderMaster
        fields = [
            # Read-only context fields (displayed as labels)
            'customerid', 'pono', 'enqid',

            # Tab 1: Task Execution - Category & Basic Info
            'cid', 'scid', 'taskworkorderdate', 'taskprojecttitle', 'taskprojectleader', 'taskbusinessgroup',

            # Tab 1: Task Execution - Date Ranges (8 ranges = 16 fields)
            'tasktargetdap_fdate', 'tasktargetdap_tdate',
            'taskdesignfinalization_fdate', 'taskdesignfinalization_tdate',
            'tasktargetmanufg_fdate', 'tasktargetmanufg_tdate',
            'tasktargettryout_fdate', 'tasktargettryout_tdate',
            'tasktargetdespach_fdate', 'tasktargetdespach_tdate',
            'tasktargetassembly_fdate', 'tasktargetassembly_tdate',
            'tasktargetinstalation_fdate', 'tasktargetinstalation_tdate',
            'taskcustinspection_fdate', 'taskcustinspection_tdate',

            # Tab 1: Task Execution - Material Procurement
            'manufmaterialdate', 'buyer', 'boughtoutmaterialdate',

            # Tab 2: Shipping - Address & Location
            'shippingadd', 'shippingcountry', 'shippingstate', 'shippingcity',

            # Tab 2: Shipping - Contact Information
            'shippingcontactperson1', 'shippingcontactno1', 'shippingemail1',
            'shippingcontactperson2', 'shippingcontactno2', 'shippingemail2',

            # Tab 2: Shipping - Tax & Regulatory
            'shippingfaxno', 'shippingeccno', 'shippingtincstno', 'shippingtinvatno',

            # Tab 4: Instructions
            'instractionprimerpainting', 'instractionpainting', 'instractionselfcertrept',
            'instractionother', 'instractionexportcasemark',
        ]

        widgets = {
            # Context fields (read-only, displayed as labels in template)
            'customerid': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'readonly': 'readonly'}),
            'pono': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'readonly': 'readonly'}),
            'enqid': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'readonly': 'readonly'}),

            # Note: cid and scid are defined as form fields above, not in widgets

            # Tab 1: Basic fields
            'taskworkorderdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'taskprojecttitle': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'taskprojectleader': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'taskbusinessgroup': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),

            # Tab 1: Date ranges (all read-only, populated via date picker)
            'tasktargetdap_fdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetdap_tdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'taskdesignfinalization_fdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'taskdesignfinalization_tdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetmanufg_fdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetmanufg_tdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargettryout_fdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargettryout_tdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetdespach_fdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetdespach_tdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetassembly_fdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetassembly_tdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetinstalation_fdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'tasktargetinstalation_tdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'taskcustinspection_fdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'taskcustinspection_tdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),

            # Tab 1: Material procurement
            'manufmaterialdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),
            'buyer': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'boughtoutmaterialdate': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100', 'placeholder': 'dd-MM-yyyy', 'readonly': 'readonly'}),

            # Tab 2: Shipping address
            'shippingadd': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent', 'rows': 3}),
            'shippingcountry': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'hx-get': '/sales/workorder/states/',
                'hx-target': '#id_shippingstate_container',
                'hx-swap': 'innerHTML'
            }),
            'shippingstate': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'hx-get': '/sales/workorder/cities/',
                'hx-target': '#id_shippingcity_container',
                'hx-swap': 'innerHTML'
            }),
            'shippingcity': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),

            # Tab 2: Contact information
            'shippingcontactperson1': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'shippingcontactno1': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'shippingemail1': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'shippingcontactperson2': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'shippingcontactno2': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'shippingemail2': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),

            # Tab 2: Tax fields
            'shippingfaxno': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'shippingeccno': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'shippingtincstno': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'shippingtinvatno': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),

            # Tab 4: Instructions (checkboxes and text)
            'instractionprimerpainting': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500'}),
            'instractionpainting': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500'}),
            'instractionselfcertrept': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500'}),
            'instractionother': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'instractionexportcasemark': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
        }

    def clean_instractionprimerpainting(self):
        """Convert checkbox value to integer: checked=1, unchecked=None"""
        value = self.cleaned_data.get('instractionprimerpainting')
        if value in ('on', True, 1, '1'):
            return 1
        return None

    def clean_instractionpainting(self):
        """Convert checkbox value to integer: checked=1, unchecked=None"""
        value = self.cleaned_data.get('instractionpainting')
        if value in ('on', True, 1, '1'):
            return 1
        return None

    def clean_instractionselfcertrept(self):
        """Convert checkbox value to integer: checked=1, unchecked=None"""
        value = self.cleaned_data.get('instractionselfcertrept')
        if value in ('on', True, 1, '1'):
            return 1
        return None


class WorkOrderProductForm(forms.ModelForm):
    """Form for Work Order Product line items (final storage)."""

    class Meta:
        model = SdCustWorkorderProductsDetails
        fields = ['itemcode', 'description', 'qty']

        widgets = {
            'itemcode': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Item Code'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Description'
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.001',
                'min': '0'
            }),
        }


# Create formset for work order products
# NOTE: Commented out due to foreign key relationship issues with managed=False models
# from django.forms import inlineformset_factory
#
# WorkOrderProductFormSet = inlineformset_factory(
#     SdCustWorkorderMaster,
#     SdCustWorkorderProductsDetails,
#     form=WorkOrderProductForm,
#     extra=1,
#     can_delete=True,
#     min_num=1,
#     validate_min=True
# )


# ============================================================================
# CONSOLIDATED FORMS FROM SEPARATE FILES
# Forms consolidated from po_forms.py and release_forms.py
# Migrated to use Tailwind widgets from core/widgets.py
# ============================================================================

from core.widgets import (
    TailwindTextInput, TailwindTextarea, TailwindSelect,
    TailwindNumberInput, TailwindDateInput, TailwindCheckboxInput
)
from decimal import Decimal
from django.core.exceptions import ValidationError


# ============================================================================
# CUSTOMER PO FORMS (from po_forms.py)
# Specialized forms for multi-tab PO entry
# ============================================================================

class CustomerPOMasterForm(forms.ModelForm):
    """
    Form for Customer PO Master (Customer Details Tab)
    Consolidated from: po_forms.py
    """

    class Meta:
        model = SdCustPoMaster
        fields = [
            'customerid', 'enqid', 'pono', 'podate', 'poreceiveddate',
            'vendorcode', 'quotationno'
        ]
        widgets = {
            'customerid': TailwindTextInput(attrs={
                'placeholder': 'Customer ID',
            }),
            'enqid': TailwindSelect(),
            'pono': TailwindTextInput(attrs={
                'placeholder': 'PO Number',
            }),
            'podate': TailwindDateInput(),
            'poreceiveddate': TailwindDateInput(),
            'vendorcode': TailwindTextInput(attrs={
                'placeholder': 'Vendor Code',
            }),
            'quotationno': TailwindNumberInput(attrs={
                'placeholder': 'Quotation No',
            }),
        }
        labels = {
            'customerid': 'Customer ID',
            'enqid': 'Enquiry',
            'pono': 'PO Number',
            'podate': 'PO Date',
            'poreceiveddate': 'PO Received Date',
            'vendorcode': 'Vendor Code',
            'quotationno': 'Quotation Number',
        }


class CustomerPOTermsForm(forms.ModelForm):
    """
    Form for Customer PO Terms & Conditions Tab
    Consolidated from: po_forms.py
    """

    class Meta:
        model = SdCustPoMaster
        fields = [
            'paymentterms', 'pf', 'vat', 'excise', 'octroi',
            'warrenty', 'insurance', 'transport', 'noteno',
            'registrationno', 'freight', 'cst', 'validity',
            'othercharges', 'remarks'
        ]
        widgets = {
            'paymentterms': TailwindTextarea(attrs={
                'rows': 3,
                'placeholder': 'Payment Terms',
            }),
            'pf': TailwindTextInput(attrs={'placeholder': 'PF'}),
            'vat': TailwindTextInput(attrs={'placeholder': 'VAT'}),
            'excise': TailwindTextInput(attrs={'placeholder': 'Excise'}),
            'octroi': TailwindTextInput(attrs={'placeholder': 'Octroi'}),
            'warrenty': TailwindTextInput(attrs={'placeholder': 'Warranty'}),
            'insurance': TailwindTextInput(attrs={'placeholder': 'Insurance'}),
            'transport': TailwindTextInput(attrs={'placeholder': 'Transport'}),
            'noteno': TailwindTextInput(attrs={'placeholder': 'Note No'}),
            'registrationno': TailwindTextInput(attrs={'placeholder': 'Registration No'}),
            'freight': TailwindTextInput(attrs={'placeholder': 'Freight'}),
            'cst': TailwindTextInput(attrs={'placeholder': 'CST'}),
            'validity': TailwindTextInput(attrs={'placeholder': 'Validity'}),
            'othercharges': TailwindTextInput(attrs={'placeholder': 'Other Charges'}),
            'remarks': TailwindTextarea(attrs={
                'rows': 3,
                'placeholder': 'Remarks',
            }),
        }
        labels = {
            'paymentterms': 'Payment Terms',
            'pf': 'PF',
            'vat': 'VAT',
            'excise': 'Excise',
            'octroi': 'Octroi',
            'warrenty': 'Warranty',
            'insurance': 'Insurance',
            'transport': 'Transport',
            'noteno': 'Note No',
            'registrationno': 'Registration No',
            'freight': 'Freight',
            'cst': 'CST',
            'validity': 'Validity',
            'othercharges': 'Other Charges',
            'remarks': 'Remarks',
        }


class CustomerPODetailForm(forms.ModelForm):
    """
    Form for Customer PO Details (Goods Details Tab)
    Consolidated from: po_forms.py
    """

    class Meta:
        model = SdCustPoDetails
        fields = ['itemdesc', 'totalqty', 'rate', 'discount', 'unit']
        widgets = {
            'itemdesc': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Description',
            }),
            'totalqty': TailwindNumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Quantity',
            }),
            'rate': TailwindNumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Rate',
            }),
            'discount': TailwindNumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Discount',
            }),
            'unit': TailwindSelect(),
        }
        labels = {
            'itemdesc': 'Item Description',
            'totalqty': 'Total Quantity',
            'rate': 'Rate',
            'discount': 'Discount',
            'unit': 'Unit',
        }


# ============================================================================
# WORK ORDER RELEASE FORMS (from release_forms.py)
# Specialized forms for work order release process
# ============================================================================

class WorkOrderSearchForm(forms.Form):
    """
    Form for searching work orders to release
    Consolidated from: release_forms.py
    """

    SEARCH_CHOICES = [
        ('', 'Select Search Type'),
        ('customer', 'Customer Name'),
        ('enquiry', 'Enquiry No'),
        ('po', 'PO No'),
        ('wo', 'WO No'),
    ]

    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=TailwindSelect()
    )

    search_value = forms.CharField(
        required=False,
        max_length=350,
        widget=TailwindTextInput(attrs={
            'placeholder': 'Enter search value...'
        })
    )


class WorkOrderReleaseItemForm(forms.Form):
    """
    Form for individual release item
    Consolidated from: release_forms.py
    """

    item_id = forms.IntegerField(widget=forms.HiddenInput())
    selected = forms.BooleanField(
        required=False,
        widget=TailwindCheckboxInput()
    )
    release_qty = forms.DecimalField(
        max_digits=15,
        decimal_places=3,
        required=False,
        widget=TailwindNumberInput(attrs={
            'class': 'text-sm',
            'step': '0.001',
            'min': '0'
        })
    )

    def __init__(self, *args, **kwargs):
        self.item_code = kwargs.pop('item_code', '')
        self.description = kwargs.pop('description', '')
        self.qty = kwargs.pop('qty', 0)
        self.released_qty = kwargs.pop('released_qty', 0)
        self.remain_qty = kwargs.pop('remain_qty', 0)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        selected = cleaned_data.get('selected')
        release_qty = cleaned_data.get('release_qty')

        if selected:
            if not release_qty or release_qty <= 0:
                raise ValidationError('Release quantity must be greater than 0 for selected items')

            if release_qty > Decimal(str(self.remain_qty)):
                raise ValidationError(f'Release quantity cannot exceed remaining quantity ({self.remain_qty})')

        return cleaned_data


class WorkOrderReleaseFormDetailed(forms.Form):
    """
    Detailed form for work order release (from separate file)
    Consolidated from: release_forms.py
    Note: Renamed to avoid conflict with existing WorkOrderReleaseForm in forms.py
    """

    wo_id = forms.IntegerField(widget=forms.HiddenInput())
    wo_no = forms.CharField(widget=forms.HiddenInput())

    # Employee selection (for notification)
    notify_employees = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        label='Notify Employees'
    )

    def __init__(self, *args, **kwargs):
        employees = kwargs.pop('employees', [])
        super().__init__(*args, **kwargs)

        if employees:
            self.fields['notify_employees'].choices = [
                (emp['empid'], f"{emp['employeename']} ({emp['empid']})")
                for emp in employees
            ]


# ============================================================================
# END OF CONSOLIDATED FORMS
# ============================================================================
