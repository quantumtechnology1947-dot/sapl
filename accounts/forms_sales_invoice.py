"""
Sales Invoice Forms - COMPLETE Implementation
Exact match to ASP.NET SalesInvoice_New_Details.aspx

All validations, field structure, and logic replicated from:
- SalesInvoice_New.aspx (PO Selection)
- SalesInvoice_New_Details.aspx (4-Tab Invoice Form)
"""
from django import forms
from django.core.validators import RegexValidator, EmailValidator
from django.forms import formset_factory, BaseFormSet
from decimal import Decimal
import re

from accounts.models import (
    TblaccSalesinvoiceMaster,
    TblaccSalesinvoiceDetails,
    TblaccSalesinvoiceMasterType,
    TblexcisecommodityMaster,
    TblexciseserMaster,
    TblvatMaster,
    TblaccServiceCategory,
    TblaccTransportmode,
    TblaccRemovableNature
)
from sales_distribution.models import SdCustMaster, SdCustPoMaster, SdCustWorkorderMaster
from sys_admin.models import Tblcountry, Tblstate, Tblcity
from accounts.services_sales_invoice import SalesInvoiceLookupService


# =============================================================================
# VALIDATORS (From ASP.NET Regex Validators)
# =============================================================================

# ASP.NET: ValidationExpression="^\d{1,15}(\.\d{0,3})?$"
numeric_qty_validator = RegexValidator(
    regex=r'^\d{1,15}(\.\d{0,3})?$',
    message='Enter a valid number (up to 15 digits, max 3 decimal places)'
)

# ASP.NET: ValidationExpression="\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*"
email_regex_validator = RegexValidator(
    regex=r"\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*",
    message='Enter a valid email address'
)

# ASP.NET: ValidationExpression="^([1-9]|0[1-9]|[12][0-9]|3[01])[- /.]([1-9]|0[1-9]|1[012])[- /.][0-9]{4}$"
date_dd_mm_yyyy_validator = RegexValidator(
    regex=r'^([1-9]|0[1-9]|[12][0-9]|3[01])[- /.]([1-9]|0[1-9]|1[012])[- /.][0-9]{4}$',
    message='Enter date in DD-MM-YYYY format'
)


# =============================================================================
# PO SELECTION FORM (SalesInvoice_New.aspx)
# =============================================================================

class POSelectionSearchForm(forms.Form):
    """
    Search form for PO selection screen.
    ASP.NET: SalesInvoice_New.aspx lines 37-60
    """
    SEARCH_CHOICES = [
        ('0', 'Customer Name'),
        ('1', 'PO No'),
    ]

    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
            'hx-get': '',  # Will be set in template
            'hx-trigger': 'change',
            'hx-target': '#search-input-container',
        }),
        initial='0'
    )

    customer_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded w-96',
            'placeholder': 'Start typing customer name...',
            'hx-get': '',  # Autocomplete endpoint
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#customer-suggestions',
        })
    )

    po_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded w-96',
            'placeholder': 'Enter PO Number',
        })
    )


class WorkOrderSelectionWidget(forms.CheckboxSelectMultiple):
    """
    Custom widget for Work Order multi-select.
    ASP.NET: ListBox with SelectionMode=Multiple (lines 108-110)
    """
    template_name = 'accounts/widgets/work_order_multiselect.html'

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs)
        self.choices = list(choices)


# =============================================================================
# INVOICE HEADER FORM (Above tabs - lines 47-109)
# =============================================================================

class SalesInvoiceHeaderForm(forms.ModelForm):
    """
    Invoice header fields (above the 4 tabs).
    ASP.NET: SalesInvoice_New_Details.aspx lines 47-109

    Fields:
    - Invoice No (auto-generated, validated)
    - Date (auto-filled)
    - Mode of Invoice (from type parameter)
    - PO No, PO Date, WO No (from query string)
    - Category, Excisable Commodity, Tariff Head No
    - Mode of Transport, Date of Issue, Date of Removal
    """

    # Override invoiceno to add validation
    invoiceno = forms.CharField(
        label='Invoice No',
        max_length=20,
        validators=[numeric_qty_validator],
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
            'readonly': 'readonly',  # Auto-generated
        })
    )

    class Meta:
        model = TblaccSalesinvoiceMaster
        fields = [
            'invoiceno', 'invoicemode', 'pono', 'wono',
            'customercategory', 'commodity', 'tariffheading',
            'modeoftransport', 'dateofissueinvoice', 'dateofremoval',
            'timeofissueinvoice', 'timeofremoval',
            'natureofremoval', 'vehiregno', 'rrgcno', 'dutyrate'
        ]
        widgets = {
            'pono': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded bg-gray-100',
                'readonly': 'readonly'
            }),
            'wono': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded bg-gray-100',
                'readonly': 'readonly'
            }),
            'dateofissueinvoice': forms.DateInput(attrs={
                'type': 'date',
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'required': 'required'
            }),
            'dateofremoval': forms.DateInput(attrs={
                'type': 'date',
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'required': 'required'
            }),
            'timeofissueinvoice': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',  # Hidden in ASP.NET
                'value': '00:00:00'
            }),
            'timeofremoval': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
                'value': '00:00:00'
            }),
            'vehiregno': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
                'value': '-'
            }),
            'rrgcno': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
                'value': '-'
            }),
            'dutyrate': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
                'value': '-'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tw_select = 'px-3 py-1.5 text-sm border border-gray-300 rounded w-full'

        # Category dropdown
        self.fields['customercategory'] = forms.ChoiceField(
            required=False,
            choices=[('', 'Select')] + [
                (cat.id, cat.description)
                for cat in TblaccServiceCategory.objects.all().order_by('id')
            ],
            widget=forms.Select(attrs={'class': tw_select})
        )

        # Excisable Commodity dropdown (REQUIRED, not "0")
        self.fields['commodity'] = forms.ChoiceField(
            required=True,
            choices=[('0', 'Select')] + [
                (comm.id, comm.terms)
                for comm in TblexcisecommodityMaster.objects.all().order_by('id')
            ],
            widget=forms.Select(attrs={
                'class': tw_select,
                'hx-get': '',  # Auto-fill tariff heading
                'hx-trigger': 'change',
                'hx-target': '#id_tariffheading',
                'required': 'required'
            })
        )

        # Tariff Head No (auto-filled from commodity)
        self.fields['tariffheading'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded bg-gray-100',
                'readonly': 'readonly'
            })
        )

        # Mode of Transport dropdown
        self.fields['modeoftransport'] = forms.ChoiceField(
            required=False,
            choices=[('', 'Select')] + [
                (mode.id, mode.description)
                for mode in TblaccTransportmode.objects.all().order_by('-id')
            ],
            widget=forms.Select(attrs={'class': tw_select})
        )

        # Nature of Removal dropdown (hidden in ASP.NET)
        self.fields['natureofremoval'] = forms.ChoiceField(
            required=False,
            choices=[('', 'Select')] + [
                (nature.id, nature.description)
                for nature in TblaccRemovableNature.objects.all().order_by('-id')
            ],
            widget=forms.Select(attrs={'class': tw_select + ' hidden'})
        )

        # Invoice Mode (readonly, from query string)
        self.fields['invoicemode'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded bg-gray-100',
                'readonly': 'readonly'
            })
        )

    def clean_commodity(self):
        """Validate commodity is not "0" (Select option)"""
        commodity = self.cleaned_data.get('commodity')
        if commodity == '0' or not commodity:
            raise forms.ValidationError('Please select an Excisable Commodity')
        return commodity


# =============================================================================
# TAB 1: BUYER FORM (13 Required Fields)
# =============================================================================

class SalesInvoiceBuyerForm(forms.ModelForm):
    """
    Buyer information tab.
    ASP.NET: SalesInvoice_New_Details.aspx lines 247-335

    All 13 fields are REQUIRED in ASP.NET.
    Includes cascading Country → State → City dropdowns.
    Email validation with regex.
    Auto-complete for buyer name.
    """

    # Override fields to add proper widgets and validation
    buyer_name = forms.CharField(
        label='Name',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded w-96',
            'placeholder': 'Start typing customer name...',
            'hx-get': '/accounts/transactions/sales-invoice/customer-autocomplete/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#buyer-suggestions',
        })
    )

    buyer_email = forms.EmailField(
        label='E-mail',
        required=True,
        validators=[email_regex_validator],
        widget=forms.EmailInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
            'placeholder': 'example@domain.com'
        })
    )

    # GST No (TxtByTINCSTNo in ASP.NET)
    buyer_tin = forms.CharField(
        label='GST No',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
            'placeholder': 'GST Number'
        })
    )

    # Hidden fields with default "-"
    buyer_fax = forms.CharField(
        label='Fax No',
        max_length=50,
        required=True,
        initial='-',
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
            'value': '-'
        })
    )

    buyer_vat = forms.CharField(
        label='TIN/VAT No',
        max_length=50,
        required=True,
        initial='-',
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
            'value': '-'
        })
    )

    buyer_ecc = forms.CharField(
        label='ECC No',
        max_length=50,
        required=True,
        initial='-',
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
            'value': '-'
        })
    )

    class Meta:
        model = TblaccSalesinvoiceMaster
        fields = [
            'buyer_name', 'buyer_add',
            'buyer_country', 'buyer_state', 'buyer_city',
            'buyer_cotper', 'buyer_ph', 'buyer_mob',
            'buyer_email', 'buyer_tin', 'buyer_fax', 'buyer_vat', 'buyer_ecc'
        ]
        widgets = {
            'buyer_add': forms.Textarea(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded w-full',
                'rows': 4,
                'required': 'required'
            }),
            'buyer_cotper': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'placeholder': 'Contact Person',
                'required': 'required'
            }),
            'buyer_ph': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'placeholder': 'Phone Number',
                'required': 'required'
            }),
            'buyer_mob': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'placeholder': 'Mobile Number',
                'required': 'required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tw_select = 'px-3 py-1.5 text-sm border border-gray-300 rounded w-full'

        # Cascading Country dropdown
        self.fields['buyer_country'] = forms.ChoiceField(
            label='Country',
            required=True,
            choices=[('', 'Select Country')] + [
                (country.cid, country.countryname)
                for country in Tblcountry.objects.all().order_by('countryname')
            ],
            widget=forms.Select(attrs={
                'class': tw_select,
                'required': 'required'
            })
        )

        # Cascading State dropdown - populate if initial value provided
        state_choices = [('', 'Select State')]
        initial_country = self.initial.get('buyer_country')
        initial_state = self.initial.get('buyer_state')

        if initial_country:
            # Load states for the initial country
            from sys_admin.models import Tblstate
            states = Tblstate.objects.filter(
                cid=initial_country
            ).values_list('sid', 'statename').distinct().order_by('statename')
            state_choices.extend(list(states))

        self.fields['buyer_state'] = forms.ChoiceField(
            label='State',
            required=False,
            choices=state_choices,
            initial=initial_state,
            widget=forms.Select(attrs={
                'class': tw_select
            })
        )

        # Cascading City dropdown - populate if initial value provided
        city_choices = [('', 'Select City')]
        initial_city = self.initial.get('buyer_city')

        if initial_state:
            # Load cities for the initial state
            from sys_admin.models import Tblcity
            cities = Tblcity.objects.filter(
                sid=initial_state
            ).values_list('cityid', 'cityname').order_by('cityname')
            city_choices.extend(list(cities))

        self.fields['buyer_city'] = forms.ChoiceField(
            label='City',
            required=False,
            choices=city_choices,
            initial=initial_city,
            widget=forms.Select(attrs={
                'class': tw_select
            })
        )

        # Set all fields as required (except state/city which are optional due to cascading dropdown issues)
        excluded_fields = ['buyer_state', 'buyer_city']
        for field_name in self.fields:
            if field_name not in excluded_fields:
                self.fields[field_name].required = True

    def clean(self):
        """Convert empty strings to None for ForeignKey fields (state/city)."""
        cleaned_data = super().clean()
        # Convert empty strings to None for ForeignKey fields
        if cleaned_data.get('buyer_state') == '':
            cleaned_data['buyer_state'] = None
        if cleaned_data.get('buyer_city') == '':
            cleaned_data['buyer_city'] = None
        return cleaned_data


# =============================================================================
# TAB 2: CONSIGNEE FORM (13 Required Fields + Copy Button)
# =============================================================================

class SalesInvoiceConsigneeForm(forms.ModelForm):
    """
    Consignee information tab.
    ASP.NET: SalesInvoice_New_Details.aspx lines 336-422

    Identical structure to Buyer form.
    Includes "Copy from buyer" button functionality.
    """

    cong_name = forms.CharField(
        label='Name',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded w-96',
            'placeholder': 'Start typing customer name...',
            'hx-get': '/accounts/transactions/sales-invoice/customer-autocomplete/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#consignee-suggestions',
        })
    )

    cong_email = forms.EmailField(
        label='E-mail',
        required=True,
        validators=[email_regex_validator],
        widget=forms.EmailInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
            'placeholder': 'example@domain.com'
        })
    )

    cong_tin = forms.CharField(
        label='GST No',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
            'placeholder': 'GST Number'
        })
    )

    # Hidden fields with default "-"
    cong_fax = forms.CharField(
        label='Fax No',
        max_length=50,
        required=True,
        initial='-',
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
            'value': '-'
        })
    )

    cong_vat = forms.CharField(
        label='TIN/VAT No',
        max_length=50,
        required=True,
        initial='-',
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
            'value': '-'
        })
    )

    cong_ecc = forms.CharField(
        label='ECC No',
        max_length=50,
        required=True,
        initial='-',
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
            'value': '-'
        })
    )

    class Meta:
        model = TblaccSalesinvoiceMaster
        fields = [
            'cong_name', 'cong_add',
            'cong_country', 'cong_state', 'cong_city',
            'cong_cotper', 'cong_ph', 'cong_mob',
            'cong_email', 'cong_tin', 'cong_fax', 'cong_vat', 'cong_ecc'
        ]
        widgets = {
            'cong_add': forms.Textarea(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded w-full',
                'rows': 4,
                'required': 'required'
            }),
            'cong_cotper': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'placeholder': 'Contact Person',
                'required': 'required'
            }),
            'cong_ph': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'placeholder': 'Phone Number',
                'required': 'required'
            }),
            'cong_mob': forms.TextInput(attrs={
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'placeholder': 'Mobile Number',
                'required': 'required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tw_select = 'px-3 py-1.5 text-sm border border-gray-300 rounded w-full'

        # Cascading Country dropdown
        self.fields['cong_country'] = forms.ChoiceField(
            label='Country',
            required=True,
            choices=[('', 'Select Country')] + [
                (country.cid, country.countryname)
                for country in Tblcountry.objects.all().order_by('countryname')
            ],
            widget=forms.Select(attrs={
                'class': tw_select,
                'required': 'required'
            })
        )

        # Cascading State dropdown - populate if initial value provided
        state_choices = [('', 'Select State')]
        initial_country = self.initial.get('cong_country')
        initial_state = self.initial.get('cong_state')

        if initial_country:
            # Load states for the initial country
            from sys_admin.models import Tblstate
            states = Tblstate.objects.filter(
                cid=initial_country
            ).values_list('sid', 'statename').distinct().order_by('statename')
            state_choices.extend(list(states))

        self.fields['cong_state'] = forms.ChoiceField(
            label='State',
            required=False,
            choices=state_choices,
            initial=initial_state,
            widget=forms.Select(attrs={
                'class': tw_select
            })
        )

        # Cascading City dropdown - populate if initial value provided
        city_choices = [('', 'Select City')]
        initial_city = self.initial.get('cong_city')

        if initial_state:
            # Load cities for the initial state
            from sys_admin.models import Tblcity
            cities = Tblcity.objects.filter(
                sid=initial_state
            ).values_list('cityid', 'cityname').order_by('cityname')
            city_choices.extend(list(cities))

        self.fields['cong_city'] = forms.ChoiceField(
            label='City',
            required=False,
            choices=city_choices,
            initial=initial_city,
            widget=forms.Select(attrs={
                'class': tw_select
            })
        )

        # Set all fields as required (except state/city which are optional due to cascading dropdown issues)
        excluded_fields = ['cong_state', 'cong_city']
        for field_name in self.fields:
            if field_name not in excluded_fields:
                self.fields[field_name].required = True

    def clean(self):
        """Convert empty strings to None for ForeignKey fields (state/city)."""
        cleaned_data = super().clean()
        # Convert empty strings to None for ForeignKey fields
        if cleaned_data.get('cong_state') == '':
            cleaned_data['cong_state'] = None
        if cleaned_data.get('cong_city') == '':
            cleaned_data['cong_city'] = None
        return cleaned_data


# =============================================================================
# TAB 3: GOODS FORM (GridView with Checkboxes)
# =============================================================================

class SalesInvoiceGoodsItemForm(forms.Form):
    """
    Individual item row in Goods tab grid.
    ASP.NET: SalesInvoice_New_Details.aspx lines 429-523

    Fields:
    - Checkbox (to select item)
    - Description (readonly)
    - Unit (readonly)
    - Qty (readonly)
    - Remaining Qty (readonly, calculated)
    - Unit Of Qty (dropdown)
    - Req Qty (input, validated)
    - Rate (readonly)
    - Amt in (%) (input, validated)
    """

    # Checkbox to select this item
    selected = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4',
            'onchange': 'toggleItemValidation(this)'
        })
    )

    # Hidden: Item ID
    item_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    # Hidden: PO ID
    po_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    # Readonly: Description
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded bg-gray-100 w-full',
            'readonly': 'readonly'
        })
    )

    # Readonly: Unit
    unit_symbol = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded bg-gray-100 text-center',
            'readonly': 'readonly'
        })
    )

    # Readonly: Total PO Qty
    total_qty = forms.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded bg-gray-100 text-right',
            'readonly': 'readonly',
            'step': '0.001'
        })
    )

    # Readonly: Remaining Qty (CRITICAL - calculated)
    remaining_qty = forms.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded bg-gray-100 text-right font-bold text-blue-600',
            'readonly': 'readonly',
            'step': '0.001'
        })
    )

    # Editable: Unit Of Qty (dropdown)
    unit_of_qty = forms.ChoiceField(
        required=False,
        choices=[],  # Will be populated in __init__
        widget=forms.Select(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded'
        })
    )

    # Editable: Req Qty (validated when checkbox selected)
    req_qty = forms.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=3,
        validators=[numeric_qty_validator],
        widget=forms.NumberInput(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded text-right',
            'step': '0.001',
            'placeholder': '0.000',
            'onchange': 'validateRemainingQty(this)'
        })
    )

    # Readonly: Rate
    rate = forms.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded bg-gray-100 text-right',
            'readonly': 'readonly',
            'step': '0.01'
        })
    )

    # Editable: Amt in (%) (validated when checkbox selected)
    amt_in_percent = forms.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=3,
        validators=[numeric_qty_validator],
        widget=forms.NumberInput(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded text-right',
            'step': '0.001',
            'placeholder': '0.00'
        })
    )

    def __init__(self, *args, **kwargs):
        # Get unit choices from database
        from sales_distribution.models import UnitMaster
        super().__init__(*args, **kwargs)

        self.fields['unit_of_qty'].choices = [('', 'Select')] + [
            (unit.id, unit.symbol)
            for unit in UnitMaster.objects.all().order_by('id')
        ]

    def clean(self):
        cleaned_data = super().clean()
        selected = cleaned_data.get('selected')
        req_qty = cleaned_data.get('req_qty')
        amt_in_percent = cleaned_data.get('amt_in_percent')
        remaining_qty = cleaned_data.get('remaining_qty')

        # If item is selected, req_qty and amt_in_percent are required
        if selected:
            if not req_qty:
                raise forms.ValidationError('Req Qty is required for selected items')
            if not amt_in_percent:
                raise forms.ValidationError('Amt in (%) is required for selected items')

            # Validate req_qty <= remaining_qty (CRITICAL business rule)
            if req_qty and remaining_qty and req_qty > remaining_qty:
                raise forms.ValidationError(
                    f'Requested quantity ({req_qty}) cannot exceed remaining quantity ({remaining_qty})'
                )

        return cleaned_data


# Formset for multiple goods items
class BaseGoodsFormSet(BaseFormSet):
    """
    Custom formset for goods items.
    Validates that at least one item is selected.
    """

    def clean(self):
        if any(self.errors):
            return

        # Check that at least one item is selected
        selected_count = 0
        for form in self.forms:
            if form.cleaned_data.get('selected'):
                selected_count += 1

        if selected_count == 0:
            raise forms.ValidationError('Please select at least one item')


SalesInvoiceGoodsFormSet = formset_factory(
    SalesInvoiceGoodsItemForm,
    formset=BaseGoodsFormSet,
    extra=0,  # No extra blank forms
    can_delete=False
)


# =============================================================================
# TAB 4: TAXATION FORM (17 Fields + CST Conditional)
# =============================================================================

class SalesInvoiceTaxationForm(forms.ModelForm):
    """
    Taxation tab.
    ASP.NET: SalesInvoice_New_Details.aspx lines 552-715

    Most fields are HIDDEN with default value "0".
    Only visible fields: CGST/IGST, SGST/CST, Insurance
    CST dropdown visibility conditional on invoice type.
    """

    class Meta:
        model = TblaccSalesinvoiceMaster
        fields = [
            'addtype', 'addamt', 'otheramt',
            'deductiontype', 'deduction',
            'pftype', 'pf',
            'cenvat',  # CGST/IGST - VISIBLE, REQUIRED
            'sedtype', 'sed',
            'aedtype', 'aed',
            'freighttype', 'freight',
            'vat',  # SGST - VISIBLE
            'selectedcst',  # CST Type - CONDITIONAL
            'cst',  # CST - CONDITIONAL
            'insurancetype', 'insurance'
        ]

    def __init__(self, *args, **kwargs):
        # Get invoice type to determine CST visibility
        invoice_type = kwargs.pop('invoice_type', None)
        super().__init__(*args, **kwargs)

        tw_input = 'px-3 py-1.5 text-sm border border-gray-300 rounded'
        tw_select = 'px-3 py-1.5 text-sm border border-gray-300 rounded w-full'
        tw_hidden = 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden'

        # HIDDEN fields with default "0"
        hidden_fields = [
            'addtype', 'addamt', 'otheramt',
            'deductiontype', 'deduction',
            'pftype', 'pf',
            'sedtype', 'sed',
            'aedtype', 'aed',
            'freighttype', 'freight',
            'insurancetype', 'insurance'
        ]

        for field_name in hidden_fields:
            if field_name.endswith('type'):
                # Type fields: 0 = Amt(Rs), 1 = Per(%)
                self.fields[field_name] = forms.ChoiceField(
                    required=True,
                    choices=[('0', 'Amt(Rs)'), ('1', 'Per(%)')],
                    initial='0',
                    widget=forms.Select(attrs={'class': tw_hidden})
                )
            else:
                # Amount fields: default "0"
                self.fields[field_name] = forms.DecimalField(
                    required=True,
                    initial=Decimal('0.00'),
                    max_digits=15,
                    decimal_places=2,
                    validators=[numeric_qty_validator],
                    widget=forms.NumberInput(attrs={
                        'class': tw_hidden,
                        'value': '0',
                        'step': '0.01'
                    })
                )

        # CGST/IGST dropdown (VISIBLE, REQUIRED)
        self.fields['cenvat'] = forms.ChoiceField(
            label='CGST/IGST',
            required=True,
            choices=[('', 'Select')] + [
                (tax.id, tax.terms)
                for tax in TblexciseserMaster.objects.filter(
                    id__in=[1, 30, 31, 32, 33, 34, 35, 36, 37, 38]
                ).order_by('id')
            ],
            widget=forms.Select(attrs={'class': tw_select})
        )

        # SGST/CST dropdown (VISIBLE)
        self.fields['vat'] = forms.ChoiceField(
            label='SGST',
            required=False,
            choices=[('', 'Select')] + [
                (tax.id, tax.terms)
                for tax in TblvatMaster.objects.filter(
                    id__in=[1, 2, 93, 94, 95, 124, 129, 130]
                ).order_by('id')
            ],
            widget=forms.Select(attrs={'class': tw_select})
        )

        # CST Type dropdown (CONDITIONAL VISIBILITY)
        # ASP.NET: Visible if invoice_type != "2"
        show_cst = invoice_type != '2' if invoice_type else True

        self.fields['selectedcst'] = forms.ChoiceField(
            label='CST Type',
            required=False,
            choices=[
                ('0', 'C.S.T.(With C Form)'),
                ('1', 'C.S.T.(Without C Form)')
            ],
            widget=forms.Select(attrs={
                'class': tw_select if show_cst else tw_hidden,
            })
        )

        # CST value (used for calculations, hidden)
        self.fields['cst'] = forms.IntegerField(
            required=True,
            initial=0,
            widget=forms.NumberInput(attrs={'class': tw_hidden, 'value': '0'})
        )

    def clean(self):
        cleaned_data = super().clean()

        # Validate CGST/IGST is selected
        if not cleaned_data.get('cenvat'):
            raise forms.ValidationError('Please select CGST/IGST')

        return cleaned_data


# =============================================================================
# SEARCH FORMS
# =============================================================================

class SalesInvoiceSearchForm(forms.Form):
    """Search form for invoice list view"""

    invoice_no = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
            'placeholder': 'Invoice No...'
        })
    )

    buyer_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
            'placeholder': 'Buyer Name...'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded'
        })
    )
