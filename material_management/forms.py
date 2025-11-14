"""
Forms for the Material Management module.

Following Django conventions and Tailwind CSS standards.
All forms use Tailwind utility classes for styling.
"""

from django import forms
from .models import (
    BusinessNature,
    BusinessType,
    ServiceCoverage,
    Buyer,
    Supplier,
)


# =============================================================================
# MASTER FORMS
# =============================================================================

class BusinessNatureForm(forms.ModelForm):
    """
    Form for Business Nature master.
    Converted from: aspnet/Module/MaterialManagement/Masters/BusinessNature.aspx
    """
    class Meta:
        model = BusinessNature
        fields = ['nature']
        widgets = {
            'nature': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter business nature',
                'required': True
            })
        }
        labels = {
            'nature': 'Business Nature'
        }

    def clean_nature(self):
        """Validate nature field"""
        nature = self.cleaned_data.get('nature')
        if not nature or not nature.strip():
            raise forms.ValidationError('Business Nature is required.')

        # Check for duplicate (case-insensitive)
        if BusinessNature.objects.filter(
            nature__iexact=nature
        ).exclude(id=self.instance.id if self.instance.pk else None).exists():
            raise forms.ValidationError('This Business Nature already exists.')

        return nature.strip()


class BusinessTypeForm(forms.ModelForm):
    """
    Form for Business Type master.
    Converted from: aspnet/Module/MaterialManagement/Masters/BusinessType.aspx
    """
    class Meta:
        model = BusinessType
        fields = ['type']
        widgets = {
            'type': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter business type',
                'required': True
            })
        }
        labels = {
            'type': 'Business Type'
        }

    def clean_type(self):
        """Validate type field"""
        btype = self.cleaned_data.get('type')
        if not btype or not btype.strip():
            raise forms.ValidationError('Business Type is required.')

        # Check for duplicate (case-insensitive)
        if BusinessType.objects.filter(
            type__iexact=btype
        ).exclude(id=self.instance.id if self.instance.pk else None).exists():
            raise forms.ValidationError('This Business Type already exists.')

        return btype.strip()


class ServiceCoverageForm(forms.ModelForm):
    """
    Form for Service Coverage master.
    Converted from: aspnet/Module/MaterialManagement/Masters/ServiceCoverage.aspx
    """
    class Meta:
        model = ServiceCoverage
        fields = ['coverage']
        widgets = {
            'coverage': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter service coverage',
                'required': True
            })
        }
        labels = {
            'coverage': 'Service Coverage'
        }

    def clean_coverage(self):
        """Validate coverage field"""
        coverage = self.cleaned_data.get('coverage')
        if not coverage or not coverage.strip():
            raise forms.ValidationError('Service Coverage is required.')

        # Check for duplicate (case-insensitive)
        if ServiceCoverage.objects.filter(
            coverage__iexact=coverage
        ).exclude(id=self.instance.id if self.instance.pk else None).exists():
            raise forms.ValidationError('This Service Coverage already exists.')

        return coverage.strip()


class BuyerForm(forms.ModelForm):
    """
    Form for Buyer master.
    Converted from: aspnet/Module/MaterialManagement/Masters/Buyer.aspx
    Features: Category dropdown (A-Z), employee selection
    """
    CATEGORY_CHOICES = [('', 'Select Category')] + [(chr(i), chr(i)) for i in range(65, 91)]  # A-Z

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
        })
    )
    
    emp_id = forms.ChoiceField(
        label='Employee',
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
        })
    )

    class Meta:
        model = Buyer
        fields = ['category', 'nos', 'emp_id']
        widgets = {
            'nos': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter number',
                'min': '1'
            }),
        }
        labels = {
            'category': 'Category',
            'nos': 'Number',
            'emp_id': 'Employee'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate employee choices
        from human_resource.models import TblhrOfficestaff
        employees = TblhrOfficestaff.objects.all().order_by('employeename')
        self.fields['emp_id'].choices = [('', 'Select Employee')] + [
            (emp.empid, f"{emp.employeename} ({emp.empid})") 
            for emp in employees
        ]

    def clean(self):
        """Validate buyer data"""
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        nos = cleaned_data.get('nos')
        emp_id = cleaned_data.get('emp_id')

        if not category:
            raise forms.ValidationError('Category is required.')
        if not nos:
            raise forms.ValidationError('Number is required.')
        if not emp_id:
            raise forms.ValidationError('Employee is required.')

        # Check for duplicate combination
        if Buyer.objects.filter(
            category=category,
            nos=nos
        ).exclude(id=self.instance.id if self.instance.pk else None).exists():
            raise forms.ValidationError('This Category and Number combination already exists.')

        return cleaned_data

        return cleaned_data


class SupplierForm(forms.ModelForm):
    """
    Form for Supplier master with 65 fields organized in sections.
    Converted from: aspnet/Module/MaterialManagement/Masters/Supplier.aspx

    Sections:
    - Basic Info
    - Registered Address
    - Work Address
    - Material Delivery Address
    - Contact & Tax Details
    - Bank Details
    - Business Details
    """
    class Meta:
        model = Supplier
        fields = [
            # Basic Info
            'supplier_id', 'supplier_name', 'scope_of_supply',
            # Registered Address
            'regd_address', 'regd_country', 'regd_state', 'regd_city',
            'regd_pin_no', 'regd_contact_no', 'regd_fax_no',
            # Work Address
            'work_address', 'work_country', 'work_state', 'work_city',
            'work_pin_no', 'work_contact_no', 'work_fax_no',
            # Material Delivery Address
            'material_del_address', 'material_del_country', 'material_del_state',
            'material_del_city', 'material_del_pin_no', 'material_del_contact_no',
            'material_del_fax_no',
            # Contact & Tax Details
            'contact_person', 'email', 'contact_no', 'pan_no', 'tin_vat_no',
            'tin_cst_no', 'ecc_no', 'juridiction_code', 'commissionurate',
            'divn', 'range', 'tds_code', 'remark',
            # Bank Details
            'bank_acc_no', 'bank_name', 'bank_branch', 'bank_address', 'bank_acc_type',
            # Business Details
            'business_type', 'business_nature', 'service_coverage',
            'pf', 'ex_st', 'vat', 'mod_vat_applicable', 'mod_vat_invoice'
        ]
        widgets = {
            # Basic Info
            'supplier_id': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Supplier ID (auto-generated if left blank)',
                'required': False  # Auto-generated if not provided
            }),
            'supplier_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Supplier Name',
                'required': True
            }),
            'scope_of_supply': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Scope of Supply',
                'rows': 3
            }),
            # Address fields - using consistent styling
            'regd_address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Registered Address',
                'rows': 3
            }),
            'work_address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Work Address',
                'rows': 3
            }),
            'material_del_address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Material Delivery Address',
                'rows': 3
            }),
            # Bank details
            'bank_address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Bank Address',
                'rows': 2
            }),
            'remark': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Remarks',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text_fields = [
            'regd_country', 'regd_state', 'regd_city', 'regd_pin_no', 'regd_contact_no', 'regd_fax_no',
            'work_country', 'work_state', 'work_city', 'work_pin_no', 'work_contact_no', 'work_fax_no',
            'material_del_country', 'material_del_state', 'material_del_city',
            'material_del_pin_no', 'material_del_contact_no', 'material_del_fax_no',
            'contact_person', 'email', 'contact_no', 'pan_no', 'tin_vat_no', 'tin_cst_no',
            'ecc_no', 'juridiction_code', 'commissionurate', 'divn', 'range', 'tds_code',
            'bank_acc_no', 'bank_name', 'bank_branch', 'bank_acc_type',
            'business_type', 'business_nature', 'service_coverage'
        ]

        for field_name in text_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                    'placeholder': self.fields[field_name].label or field_name.replace('_', ' ').title()
                })

        # Hidden fields (these are rendered as hidden inputs in template)
        # Note: In ASP.NET these are dropdowns for P&F, CGST/IGST, SGST and radio buttons for Mod GST
        # But for now we hide them with default values since they're not critical
        hidden_fields = ['pf', 'ex_st', 'vat', 'mod_vat_applicable', 'mod_vat_invoice']
        for field_name in hidden_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.HiddenInput()
                self.fields[field_name].required = False

    def clean_supplier_id(self):
        """Validate supplier ID - allow empty (will be auto-generated)"""
        supplier_id = self.cleaned_data.get('supplier_id')
        # Allow empty - will be auto-generated by view
        if not supplier_id or not supplier_id.strip():
            return ''  # Return empty string, view will auto-generate

        # Check for duplicate
        if Supplier.objects.filter(
            supplier_id=supplier_id
        ).exclude(supplier_id=self.instance.supplier_id if self.instance.pk else None).exists():
            raise forms.ValidationError('This Supplier ID already exists.')

        return supplier_id.strip()

    def clean_supplier_name(self):
        """Validate supplier name"""
        name = self.cleaned_data.get('supplier_name')
        if not name or not name.strip():
            raise forms.ValidationError('Supplier Name is required.')
        return name.strip()

    def clean_email(self):
        """Validate email format"""
        email = self.cleaned_data.get('email')
        if email and email.strip():
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise forms.ValidationError('Invalid email format.')
        return email
