"""
Forms for the Accounts module.
Converted from ASP.NET Module/Accounts/Masters/*.aspx

CONSOLIDATED FILE - Contains all forms from:
- forms.py (original)
- forms_sales_invoice.py (merged)
"""

from django import forms
from django.forms import inlineformset_factory, formset_factory, BaseFormSet
from django.core.validators import RegexValidator, EmailValidator
from decimal import Decimal
import re

# Import Tailwind widgets from core
from core.widgets import (
    TailwindTextInput, TailwindTextarea, TailwindSelect,
    TailwindNumberInput, TailwindEmailInput, TailwindDateInput,
    TailwindCheckboxInput, HTMXSelect
)

from .models import (
    Acchead, TblaccBank, TblaccCurrencyMaster, TblaccPaymentmode,
    TblaccTdscodeMaster, TblaccBankvoucherPaymentMaster,
    TblaccBankvoucherPaymentDetails, TblaccCashvoucherPaymentMaster,
    TblaccCashvoucherPaymentDetails, TblaccCashvoucherReceiptMaster,
    TblaccContraEntry, TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails,
    TblaccBillbookingMaster, TblaccBillbookingDetails, TblaccBillbookingAttachMaster,
    TblaccProformainvoiceMaster, TblaccProformainvoiceDetails,
    TblaccDebitnote, TblaccAssetRegister, TblaccAssetCategory, TblaccAssetSubcategory,
    TblaccAdvicePaymentMaster, TblaccAdvicePaymentDetails,
    TblaccCapitalMaster, TblaccCapitalDetails,
    TblaccLoanmaster, TblaccLoandetails,
    TblaccCreditorsMaster, TblaccDebitorsMaster,
    # Additional models from separate form files
    TblexciseserMaster, TblexcisecommodityMaster, TblvatMaster,
    TblfreightMaster, TbloctroiMaster, TblaccIntresttype,
    TblaccLoantype, TblaccPaidtype, TblaccInvoiceagainst,
    TblaccIouReasons, TblwarrentyMaster, AccPolicy,
    # Sales Invoice specific models
    TblaccSalesinvoiceMasterType, TblaccServiceCategory,
    TblaccTransportmode, TblaccRemovableNature
)
from sys_admin.models import Tblcountry, Tblstate, Tblcity
from sales_distribution.models import SdCustMaster, SdCustPoMaster, SdCustWorkorderMaster


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


class AccHeadForm(forms.ModelForm):
    """
    Form for Account Head (AccHead) management.
    Converted from: aspnet/Module/Accounts/Masters/AccHead.aspx
    """

    CATEGORY_CHOICES = [
        ('', 'Select Category'),
        ('Labour', 'Labour'),
        ('With Material', 'With Material'),
        ('Expenses', 'Expenses'),
        ('Service Provider', 'Service Provider'),
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=True,
        widget=TailwindSelect()
    )

    class Meta:
        model = Acchead
        fields = ['category', 'description', 'symbol', 'abbrivation']

        widgets = {
            'description': TailwindTextInput(attrs={'placeholder': 'Enter description'}),
            'symbol': TailwindTextInput(attrs={'placeholder': 'Enter symbol'}),
            'abbrivation': TailwindTextInput(attrs={'placeholder': 'Enter abbreviation'}),
        }

        labels = {
            'category': 'Category',
            'description': 'Description',
            'symbol': 'Symbol',
            'abbrivation': 'Abbreviation',
        }

    def clean_description(self):
        """Validate description is not empty."""
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise forms.ValidationError('Description is required.')
        return description.strip()

    def clean_category(self):
        """Validate category is selected."""
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('Please select a category.')
        return category



class BankForm(forms.ModelForm):
    """
    Form for Bank master management with cascading country→state→city dropdowns.
    Converted from: aspnet/Module/Accounts/Masters/Bank.aspx
    """

    country = forms.ModelChoiceField(
        queryset=Tblcountry.objects.all().order_by('countryname'),
        required=True,
        empty_label="Select Country",
        widget=HTMXSelect(attrs={
            'hx-get': '/accounts/ajax/get-states/',
            'hx-target': '#id_state_container',
            'hx-trigger': 'change',
            'hx-include': '[name="country"]'
        })
    )

    state = forms.ModelChoiceField(
        queryset=Tblstate.objects.none(),
        required=False,
        empty_label="Select State",
        widget=HTMXSelect(attrs={
            'hx-get': '/accounts/ajax/get-cities/',
            'hx-target': '#id_city_container',
            'hx-trigger': 'change',
            'hx-include': '[name="state"]'
        })
    )

    city = forms.ModelChoiceField(
        queryset=Tblcity.objects.none(),
        required=False,
        empty_label="Select City",
        widget=TailwindSelect()
    )

    class Meta:
        model = TblaccBank
        fields = ['name', 'address', 'country', 'state', 'city', 'pinno', 'contactno', 'faxno', 'ifsc']

        widgets = {
            'name': TailwindTextInput(attrs={'placeholder': 'Enter bank name'}),
            'address': TailwindTextarea(attrs={'placeholder': 'Enter address', 'rows': 3}),
            'pinno': TailwindTextInput(attrs={'placeholder': 'Enter PIN code'}),
            'contactno': TailwindTextInput(attrs={'placeholder': 'Enter contact number'}),
            'faxno': TailwindTextInput(attrs={'placeholder': 'Enter fax number'}),
            'ifsc': TailwindTextInput(attrs={'placeholder': 'Enter IFSC code'}),
        }

        labels = {
            'name': 'Bank Name',
            'address': 'Address',
            'pinno': 'PIN Code',
            'contactno': 'Contact Number',
            'faxno': 'Fax Number',
            'ifsc': 'IFSC Code',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing bank, populate state and city dropdowns
        if self.instance and self.instance.pk:
            if self.instance.country:
                self.fields['country'].initial = self.instance.country
                self.fields['state'].queryset = Tblstate.objects.filter(
                    cid=self.instance.country
                ).order_by('statename')
                
            if self.instance.state:
                self.fields['state'].initial = self.instance.state
                self.fields['city'].queryset = Tblcity.objects.filter(
                    sid=self.instance.state
                ).order_by('cityname')
                
            if self.instance.city:
                self.fields['city'].initial = self.instance.city
    
    def clean_name(self):
        """Validate bank name is not empty."""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError('Bank name is required.')
        return name.strip()
    
    def clean_ifsc(self):
        """Validate IFSC code format."""
        ifsc = self.cleaned_data.get('ifsc')
        if ifsc and len(ifsc.strip()) > 0:
            ifsc = ifsc.strip().upper()
            if len(ifsc) != 11:
                raise forms.ValidationError('IFSC code must be 11 characters.')
        return ifsc
    
    def save(self, commit=True):
        """Save bank with proper country/state/city IDs."""
        instance = super().save(commit=False)
        
        # Convert ModelChoiceField objects to IDs
        if self.cleaned_data.get('country'):
            instance.country = self.cleaned_data['country'].cid
        if self.cleaned_data.get('state'):
            instance.state = self.cleaned_data['state'].sid
        if self.cleaned_data.get('city'):
            instance.city = self.cleaned_data['city'].cityid
            
        if commit:
            instance.save()
        return instance



class CurrencyForm(forms.ModelForm):
    """
    Form for Currency master management.
    Converted from: aspnet/Module/Accounts/Masters/Currency.aspx
    """

    country = forms.ModelChoiceField(
        queryset=Tblcountry.objects.all().order_by('countryname'),
        required=False,
        empty_label="Select Country",
        widget=TailwindSelect()
    )

    class Meta:
        model = TblaccCurrencyMaster
        fields = ['country', 'name', 'symbol']

        widgets = {
            'name': TailwindTextInput(attrs={
                'placeholder': 'Enter currency name (e.g., US Dollar, Indian Rupee)'
            }),
            'symbol': TailwindTextInput(attrs={
                'placeholder': 'Enter currency symbol (e.g., $, ₹, €)'
            }),
        }

        labels = {
            'country': 'Country',
            'name': 'Currency Name',
            'symbol': 'Currency Symbol',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing currency, set country
        if self.instance and self.instance.pk and self.instance.country:
            self.fields['country'].initial = self.instance.country
    
    def clean_name(self):
        """Validate currency name is not empty."""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError('Currency name is required.')
        return name.strip()
    
    def clean_symbol(self):
        """Validate currency symbol."""
        symbol = self.cleaned_data.get('symbol')
        if symbol:
            symbol = symbol.strip()
            if len(symbol) > 5:
                raise forms.ValidationError('Currency symbol should be 5 characters or less.')
        return symbol
    
    def save(self, commit=True):
        """Save currency with proper country ID."""
        instance = super().save(commit=False)
        
        # Convert ModelChoiceField object to ID
        if self.cleaned_data.get('country'):
            instance.country = self.cleaned_data['country'].cid
        else:
            instance.country = None
            
        if commit:
            instance.save()
        return instance



class PaymentTermsForm(forms.ModelForm):
    """
    Form for Payment Terms (Payment Mode) management.
    Converted from: aspnet/Module/Accounts/Masters/PaymentTerms.aspx
    """

    class Meta:
        model = TblaccPaymentmode
        fields = ['terms']

        widgets = {
            'terms': TailwindTextarea(attrs={
                'placeholder': 'Enter payment terms (e.g., Net 30 Days, 50% Advance, COD)',
                'rows': 3
            }),
        }

        labels = {
            'terms': 'Payment Terms',
        }

    def clean_terms(self):
        """Validate payment terms is not empty."""
        terms = self.cleaned_data.get('terms')
        if not terms or not terms.strip():
            raise forms.ValidationError('Payment terms is required.')
        return terms.strip()



class TDSCodeForm(forms.ModelForm):
    """
    Form for TDS Code management.
    Converted from: aspnet/Module/Accounts/Masters/TDS_Code.aspx
    """

    class Meta:
        model = TblaccTdscodeMaster
        fields = ['sectionno', 'natureofpayment', 'paymentrange', 'paytoindividual', 'others', 'withoutpan']

        widgets = {
            'sectionno': TailwindTextInput(attrs={
                'placeholder': 'Enter section number (e.g., 194C, 194J)'
            }),
            'natureofpayment': TailwindTextarea(attrs={
                'placeholder': 'Enter nature of payment',
                'rows': 2
            }),
            'paymentrange': TailwindNumberInput(attrs={
                'placeholder': 'Enter payment range',
                'step': '0.01'
            }),
            'paytoindividual': TailwindNumberInput(attrs={
                'placeholder': 'Enter rate for individuals (%)',
                'step': '0.01'
            }),
            'others': TailwindNumberInput(attrs={
                'placeholder': 'Enter rate for others (%)',
                'step': '0.01'
            }),
            'withoutpan': TailwindNumberInput(attrs={
                'placeholder': 'Enter rate without PAN (%)',
                'step': '0.01'
            }),
        }

        labels = {
            'sectionno': 'Section Number',
            'natureofpayment': 'Nature of Payment',
            'paymentrange': 'Payment Range',
            'paytoindividual': 'Rate for Individual (%)',
            'others': 'Rate for Others (%)',
            'withoutpan': 'Rate Without PAN (%)',
        }

    def clean_sectionno(self):
        """Validate section number is not empty."""
        sectionno = self.cleaned_data.get('sectionno')
        if not sectionno or not sectionno.strip():
            raise forms.ValidationError('Section number is required.')
        return sectionno.strip()



# ============================================================================
# Bank Voucher Forms
# ============================================================================

class BankVoucherMasterForm(forms.ModelForm):
    """Form for Bank Voucher header."""
    
    TRANSACTION_TYPE_CHOICES = [
        ('', 'Select Type'),
        (1, 'RTGS'),
        (2, 'NEFT'),
        (3, 'DD'),
        (4, 'CHEQUE'),
    ]
    
    bank = forms.ModelChoiceField(
        queryset=TblaccBank.objects.all().order_by('name'),
        required=True,
        empty_label="Select Bank",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    transactiontype = forms.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    class Meta:
        model = TblaccBankvoucherPaymentMaster
        fields = ['bvpno', 'payto', 'chequeno', 'chequedate', 'bank', 'transactiontype', 'payamt']
        
        widgets = {
            'bvpno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Voucher Number (auto-generated)'
            }),
            'payto': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Pay to'
            }),
            'chequeno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Cheque/DD Number'
            }),
            'chequedate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'payamt': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Payment Amount',
                'step': '0.01'
            }),
        }
        
        labels = {
            'bvpno': 'Voucher Number',
            'payto': 'Pay To',
            'chequeno': 'Cheque/DD Number',
            'chequedate': 'Cheque Date',
            'bank': 'Bank',
            'transactiontype': 'Transaction Type',
            'payamt': 'Payment Amount',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.bank:
            self.fields['bank'].initial = self.instance.bank
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('bank'):
            instance.bank = self.cleaned_data['bank'].id
        if self.cleaned_data.get('transactiontype'):
            instance.transactiontype = int(self.cleaned_data['transactiontype'])
        if commit:
            instance.save()
        return instance


class BankVoucherDetailForm(forms.ModelForm):
    """Form for Bank Voucher line items."""
    
    class Meta:
        model = TblaccBankvoucherPaymentDetails
        fields = ['proformainvno', 'invdate', 'pono', 'particular', 'amount']
        
        widgets = {
            'proformainvno': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Invoice No'
            }),
            'invdate': forms.DateInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'type': 'date'
            }),
            'pono': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'PO No'
            }),
            'particular': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Particulars'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
        }


# Create formset for bank voucher details
BankVoucherDetailFormSet = inlineformset_factory(
    TblaccBankvoucherPaymentMaster,
    TblaccBankvoucherPaymentDetails,
    form=BankVoucherDetailForm,
    fields=['proformainvno', 'invdate', 'pono', 'particular', 'amount'],
    extra=3,
    can_delete=True
)


# ============================================================================
# Cash Voucher Forms
# ============================================================================

class CashVoucherPaymentForm(forms.ModelForm):
    """Form for Cash Voucher Payment header."""
    
    class Meta:
        model = TblaccCashvoucherPaymentMaster
        fields = ['cvpno', 'paidto', 'receivedby', 'codetype']
        
        widgets = {
            'cvpno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Voucher Number (auto-generated)',
                'readonly': 'readonly'
            }),
            'paidto': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Paid To',
                'required': 'required'
            }),
            'receivedby': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Received By'
            }),
            'codetype': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Code Type'
            }),
        }
        
        labels = {
            'cvpno': 'Voucher Number',
            'paidto': 'Paid To',
            'receivedby': 'Received By',
            'codetype': 'Code Type',
        }


class CashVoucherPaymentDetailForm(forms.ModelForm):
    """Form for Cash Voucher Payment line items."""
    
    class Meta:
        model = TblaccCashvoucherPaymentDetails
        fields = ['billno', 'billdate', 'pono', 'particulars', 'achead', 'amount']
        
        widgets = {
            'billno': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Bill No'
            }),
            'billdate': forms.DateInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'type': 'date'
            }),
            'pono': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'PO No'
            }),
            'particulars': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Particulars'
            }),
            'achead': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Account Head'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
        }


# Create formset for cash voucher payment details
CashVoucherPaymentDetailFormSet = inlineformset_factory(
    TblaccCashvoucherPaymentMaster,
    TblaccCashvoucherPaymentDetails,
    form=CashVoucherPaymentDetailForm,
    fields=['billno', 'billdate', 'pono', 'particulars', 'achead', 'amount'],
    extra=3,
    can_delete=True
)


class CashVoucherReceiptForm(forms.ModelForm):
    """Form for Cash Voucher Receipt."""
    
    class Meta:
        model = TblaccCashvoucherReceiptMaster
        fields = ['cvrno', 'cashreceivedagainst', 'cashreceivedby', 'wono', 'achead', 'amount']
        
        widgets = {
            'cvrno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Voucher Number (auto-generated)',
                'readonly': 'readonly'
            }),
            'cashreceivedagainst': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Cash Received Against',
                'required': 'required'
            }),
            'cashreceivedby': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Cash Received By'
            }),
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Work Order No'
            }),
            'achead': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Account Head'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Amount',
                'step': '0.01',
                'required': 'required'
            }),
        }
        
        labels = {
            'cvrno': 'Voucher Number',
            'cashreceivedagainst': 'Cash Received Against',
            'cashreceivedby': 'Cash Received By',
            'wono': 'Work Order No',
            'achead': 'Account Head',
            'amount': 'Amount',
        }



# ============================================================================
# Journal Entry / Contra Entry Forms
# ============================================================================

class JournalEntryForm(forms.ModelForm):
    """Form for Journal Entry and Contra Entry."""
    
    class Meta:
        model = TblaccContraEntry
        fields = ['date', 'cr', 'dr', 'amount', 'narration']
        
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'cr': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Credit Account ID'
            }),
            'dr': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Debit Account ID'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
            'narration': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Narration/Description',
                'rows': 3
            }),
        }
        
        labels = {
            'date': 'Entry Date',
            'cr': 'Credit Account',
            'dr': 'Debit Account',
            'amount': 'Amount',
            'narration': 'Narration',
        }
    
    def clean_amount(self):
        """Validate amount is positive."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount


# ============================================================================
# Sales Invoice Forms
# ============================================================================

class SalesInvoiceMasterForm(forms.ModelForm):
    """Form for Sales Invoice header."""
    
    class Meta:
        model = TblaccSalesinvoiceMaster
        fields = [
            'invoiceno', 'pono', 'wono', 'dateofissueinvoice', 
            'customercode', 'buyer_name', 'buyer_add', 'buyer_ph',
            'buyer_email', 'buyer_tin', 'buyer_vat',
            'addamt', 'deduction', 'freight', 'insurance', 'otheramt'
        ]
        
        widgets = {
            'invoiceno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Invoice Number (auto-generated)',
                'readonly': 'readonly'
            }),
            'pono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'PO Number'
            }),
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Work Order Number'
            }),
            'dateofissueinvoice': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'type': 'date'
            }),
            'customercode': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Customer Code',
                'required': 'required'
            }),
            'buyer_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Buyer Name'
            }),
            'buyer_add': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Buyer Address',
                'rows': 2
            }),
            'buyer_ph': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Phone'
            }),
            'buyer_email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Email'
            }),
            'buyer_tin': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'TIN'
            }),
            'buyer_vat': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'VAT Number'
            }),
            'addamt': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Additional Amount',
                'step': '0.01'
            }),
            'deduction': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Deduction',
                'step': '0.01'
            }),
            'freight': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Freight',
                'step': '0.01'
            }),
            'insurance': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Insurance',
                'step': '0.01'
            }),
            'otheramt': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Other Amount',
                'step': '0.01'
            }),
        }
        
        labels = {
            'invoiceno': 'Invoice Number',
            'pono': 'PO Number',
            'wono': 'Work Order Number',
            'dateofissueinvoice': 'Invoice Date',
            'customercode': 'Customer Code',
            'buyer_name': 'Buyer Name',
            'buyer_add': 'Buyer Address',
            'buyer_ph': 'Phone',
            'buyer_email': 'Email',
            'buyer_tin': 'TIN',
            'buyer_vat': 'VAT Number',
            'addamt': 'Additional Amount',
            'deduction': 'Deduction',
            'freight': 'Freight',
            'insurance': 'Insurance',
            'otheramt': 'Other Amount',
        }


class SalesInvoiceDetailForm(forms.ModelForm):
    """Form for Sales Invoice line items."""
    
    class Meta:
        model = TblaccSalesinvoiceDetails
        fields = ['itemid', 'qty', 'rate', 'amtinper']
        
        widgets = {
            'itemid': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Item ID'
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Quantity',
                'step': '0.01'
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Rate',
                'step': '0.01'
            }),
            'amtinper': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
        }


# Create formset for sales invoice details
SalesInvoiceDetailFormSet = inlineformset_factory(
    TblaccSalesinvoiceMaster,
    TblaccSalesinvoiceDetails,
    form=SalesInvoiceDetailForm,
    fields=['itemid', 'qty', 'rate', 'amtinper'],
    extra=3,
    can_delete=True
)


# ============================================================================
# Bill Booking Forms
# ============================================================================

class BillBookingMasterForm(forms.ModelForm):
    """Form for Bill Booking header."""
    
    class Meta:
        model = TblaccBillbookingMaster
        fields = [
            'pvevno', 'supplierid', 'poid', 'billno', 'billdate',
            'narration', 'debitamt', 'discount', 'othercharges',
            'otherchadesc', 'ahid', 'tdscode', 'authorize'
        ]
        
        widgets = {
            'pvevno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Bill Number (auto-generated)',
                'readonly': 'readonly'
            }),
            'supplierid': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Supplier ID',
                'required': 'required'
            }),
            'poid': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'PO ID'
            }),
            'billno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Bill Number'
            }),
            'billdate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'type': 'date'
            }),
            'narration': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Narration/Description',
                'rows': 3
            }),
            'debitamt': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Debit Amount',
                'step': '0.01'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Discount',
                'step': '0.01'
            }),
            'othercharges': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Other Charges',
                'step': '0.01'
            }),
            'otherchadesc': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Other Charges Description'
            }),
            'ahid': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Account Head ID',
                'required': 'required'
            }),
            'tdscode': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'TDS Code'
            }),
            'authorize': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Authorization Status (0=Pending, 1=Authorized)'
            }),
        }
        
        labels = {
            'pvevno': 'Bill Booking Number',
            'supplierid': 'Supplier ID',
            'poid': 'Purchase Order ID',
            'billno': 'Bill Number',
            'billdate': 'Bill Date',
            'narration': 'Narration',
            'debitamt': 'Debit Amount',
            'discount': 'Discount',
            'othercharges': 'Other Charges',
            'otherchadesc': 'Other Charges Description',
            'ahid': 'Account Head',
            'tdscode': 'TDS Code',
            'authorize': 'Authorization Status',
        }


class BillBookingDetailForm(forms.ModelForm):
    """Form for Bill Booking line items (simplified)."""
    
    class Meta:
        model = TblaccBillbookingDetails
        fields = ['itemid', 'debitvalue', 'vat', 'cst', 'freight']
        
        widgets = {
            'itemid': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Item ID'
            }),
            'debitvalue': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
            'vat': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'VAT',
                'step': '0.01'
            }),
            'cst': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'CST',
                'step': '0.01'
            }),
            'freight': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Freight',
                'step': '0.01'
            }),
        }


# Create formset for bill booking details
BillBookingDetailFormSet = inlineformset_factory(
    TblaccBillbookingMaster,
    TblaccBillbookingDetails,
    form=BillBookingDetailForm,
    fields=['itemid', 'debitvalue', 'vat', 'cst', 'freight'],
    extra=3,
    can_delete=True
)


# ============================================================================
# Contra Entry Forms
# ============================================================================

class ContraEntryForm(forms.ModelForm):
    """
    Form for Contra Entry (Cash-Bank transfers).
    Simplified two-line entry for transfers between cash and bank accounts.
    """
    
    # Custom fields for account selection
    from_account = forms.ModelChoiceField(
        queryset=Acchead.objects.filter(
            category__in=['Cash', 'Bank']
        ).order_by('description'),
        required=True,
        empty_label="Select From Account",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/accounts/ajax/exclude-account/',
            'hx-target': '#id_to_account',
            'hx-trigger': 'change'
        }),
        label='From Account (Debit)'
    )
    
    to_account = forms.ModelChoiceField(
        queryset=Acchead.objects.filter(
            category__in=['Cash', 'Bank']
        ).order_by('description'),
        required=True,
        empty_label="Select To Account",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='To Account (Credit)'
    )
    
    class Meta:
        model = TblaccContraEntry
        fields = ['date', 'amount', 'narration']
        
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter amount',
                'step': '0.01',
                'min': '0.01'
            }),
            'narration': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter narration/description',
                'rows': 3
            }),
        }
        
        labels = {
            'date': 'Transaction Date',
            'amount': 'Amount',
            'narration': 'Narration',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing entry, set from/to accounts
        if self.instance and self.instance.pk:
            if self.instance.dr:
                self.fields['from_account'].initial = self.instance.dr
            if self.instance.cr:
                self.fields['to_account'].initial = self.instance.cr
    
    def clean_amount(self):
        """Validate amount is positive."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount
    
    def clean(self):
        """Validate from and to accounts are different."""
        cleaned_data = super().clean()
        from_account = cleaned_data.get('from_account')
        to_account = cleaned_data.get('to_account')
        
        if from_account and to_account and from_account.id == to_account.id:
            raise forms.ValidationError('From Account and To Account must be different.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save contra entry with debit and credit accounts."""
        instance = super().save(commit=False)
        
        # Set debit (from) and credit (to) accounts
        if self.cleaned_data.get('from_account'):
            instance.dr = self.cleaned_data['from_account'].id
        if self.cleaned_data.get('to_account'):
            instance.cr = self.cleaned_data['to_account'].id
        
        if commit:
            instance.save()
        return instance



# ============================================================================
# Bill Booking Attachment Form
# ============================================================================

class BillBookingAttachmentForm(forms.ModelForm):
    """
    Form for uploading attachments to bill bookings.
    Supports PDF, images, and document files.
    """
    
    file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500',
            'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx'
        }),
        label='Select File',
        help_text='Supported formats: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX (Max 10MB)'
    )
    
    class Meta:
        model = TblaccBillbookingAttachMaster
        fields = []  # We'll handle file manually
    
    def clean_file(self):
        """Validate file size and type."""
        file = self.cleaned_data.get('file')
        
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB.')
            
            # Check file type
            allowed_types = [
                'application/pdf',
                'image/jpeg',
                'image/jpg',
                'image/png',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ]
            
            if file.content_type not in allowed_types:
                raise forms.ValidationError('Invalid file type. Please upload PDF, image, or document files.')
        
        return file



# ============================================================================
# Proforma Invoice Forms
# ============================================================================

class ProformaInvoiceHeaderForm(forms.ModelForm):
    """
    Form for Proforma Invoice header (simplified version).
    Proforma invoices are quotations without accounting entries.
    """
    
    class Meta:
        model = TblaccProformainvoiceMaster
        fields = ['invoiceno', 'pono', 'wono', 'dateofissueinvoice', 'buyer_name', 
                  'buyer_add', 'buyer_ph', 'buyer_email']
        
        widgets = {
            'invoiceno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Proforma Invoice Number (auto-generated)',
                'readonly': 'readonly'
            }),
            'pono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'PO Number'
            }),
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Work Order Number'
            }),
            'dateofissueinvoice': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'type': 'date'
            }),
            'buyer_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Customer Name',
                'required': 'required'
            }),
            'buyer_add': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Customer Address',
                'rows': 2
            }),
            'buyer_ph': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Phone Number'
            }),
            'buyer_email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Email Address'
            }),
        }
        
        labels = {
            'invoiceno': 'Proforma Invoice Number',
            'pono': 'PO Number',
            'wono': 'Work Order Number',
            'dateofissueinvoice': 'Invoice Date',
            'buyer_name': 'Customer Name',
            'buyer_add': 'Customer Address',
            'buyer_ph': 'Phone',
            'buyer_email': 'Email',
        }


class ProformaInvoiceDetailForm(forms.ModelForm):
    """Form for Proforma Invoice line items."""
    
    class Meta:
        model = TblaccProformainvoiceDetails
        fields = ['itemid', 'qty', 'rate']
        
        widgets = {
            'itemid': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Item ID'
            }),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Quantity',
                'step': '0.01'
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Rate',
                'step': '0.01'
            }),
        }


# Create formset for proforma invoice details
ProformaInvoiceDetailFormSet = inlineformset_factory(
    TblaccProformainvoiceMaster,
    TblaccProformainvoiceDetails,
    form=ProformaInvoiceDetailForm,
    fields=['itemid', 'qty', 'rate'],
    extra=3,
    can_delete=True
)



# ============================================================================
# Credit/Debit Note Forms
# ============================================================================

class DebitNoteForm(forms.ModelForm):
    """
    Form for Debit Note (issued to suppliers for returns/adjustments).
    Creates reversal accounting entries.
    """
    
    class Meta:
        model = TblaccDebitnote
        fields = ['debitno', 'date', 'sce', 'refrence', 'particulars', 'amount', 'types']
        
        widgets = {
            'debitno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Debit Note Number (auto-generated)',
                'readonly': 'readonly'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'type': 'date'
            }),
            'sce': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Supplier/Customer/Employee'
            }),
            'refrence': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Reference Invoice/Bill Number',
                'required': 'required'
            }),
            'particulars': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Reason for debit note (e.g., goods returned, price adjustment)',
                'rows': 3
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Amount',
                'step': '0.01',
                'required': 'required'
            }),
            'types': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'
            }, choices=[
                ('', 'Select Type'),
                (1, 'Purchase Return'),
                (2, 'Price Adjustment'),
                (3, 'Other')
            ]),
        }
        
        labels = {
            'debitno': 'Debit Note Number',
            'date': 'Date',
            'sce': 'Supplier/Party Name',
            'refrence': 'Reference Bill Number',
            'particulars': 'Particulars/Reason',
            'amount': 'Amount',
            'types': 'Type',
        }
    
    def clean_amount(self):
        """Validate amount is positive."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount


class CreditNoteForm(forms.ModelForm):
    """
    Form for Credit Note (issued to customers for returns/adjustments).
    Uses same model as Debit Note but with different type.
    Creates reversal accounting entries.
    """
    
    class Meta:
        model = TblaccDebitnote  # Using same model, differentiated by type
        fields = ['debitno', 'date', 'sce', 'refrence', 'particulars', 'amount', 'types']
        
        widgets = {
            'debitno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Credit Note Number (auto-generated)',
                'readonly': 'readonly'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'type': 'date'
            }),
            'sce': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Customer Name'
            }),
            'refrence': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Reference Sales Invoice Number',
                'required': 'required'
            }),
            'particulars': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Reason for credit note (e.g., sales return, discount adjustment)',
                'rows': 3
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Amount',
                'step': '0.01',
                'required': 'required'
            }),
            'types': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'
            }, choices=[
                ('', 'Select Type'),
                (10, 'Sales Return'),
                (11, 'Discount Adjustment'),
                (12, 'Other')
            ]),
        }
        
        labels = {
            'debitno': 'Credit Note Number',
            'date': 'Date',
            'sce': 'Customer Name',
            'refrence': 'Reference Invoice Number',
            'particulars': 'Particulars/Reason',
            'amount': 'Amount',
            'types': 'Type',
        }
    
    def clean_amount(self):
        """Validate amount is positive."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount



# ============================================================================
# Asset Register Forms
# ============================================================================

class AssetRegisterForm(forms.ModelForm):
    """
    Form for Asset Register with category/subcategory cascading.
    Tracks fixed assets with depreciation.
    """
    
    category = forms.ModelChoiceField(
        queryset=TblaccAssetCategory.objects.all().order_by('category'),
        required=True,
        empty_label="Select Category",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/accounts/ajax/get-asset-subcategories/',
            'hx-target': '#id_subcategory_container',
            'hx-trigger': 'change',
            'hx-include': '[name="category"]'
        })
    )
    
    subcategory = forms.ModelChoiceField(
        queryset=TblaccAssetSubcategory.objects.none(),
        required=False,
        empty_label="Select Subcategory",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    class Meta:
        model = TblaccAssetRegister
        fields = ['assetno']
        
        widgets = {
            'assetno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Asset Number',
                'required': 'required'
            }),
        }
        
        labels = {
            'assetno': 'Asset Number',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing asset, populate subcategory dropdown
        if self.instance and self.instance.pk:
            if self.instance.acategoyid:
                self.fields['category'].initial = self.instance.acategoyid
                self.fields['subcategory'].queryset = TblaccAssetSubcategory.objects.filter(
                    mid=self.instance.acategoyid
                ).order_by('subcategory')
                
            if self.instance.asubcategoyid:
                self.fields['subcategory'].initial = self.instance.asubcategoyid
    
    def save(self, commit=True):
        """Save asset with category/subcategory IDs."""
        instance = super().save(commit=False)
        
        # Set category and subcategory IDs
        if self.cleaned_data.get('category'):
            instance.acategoyid = self.cleaned_data['category'].id
        if self.cleaned_data.get('subcategory'):
            instance.asubcategoyid = self.cleaned_data['subcategory'].id
        
        if commit:
            instance.save()
        return instance


class AssetDisposalForm(forms.Form):
    """
    Form for asset disposal with gain/loss calculation.
    """
    
    disposal_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
            'type': 'date'
        }),
        label='Disposal Date'
    )
    
    disposal_amount = forms.DecimalField(
        required=True,
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
            'placeholder': 'Sale/Disposal Amount',
            'step': '0.01'
        }),
        label='Disposal Amount'
    )
    
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
            'placeholder': 'Remarks about disposal',
            'rows': 3
        }),
        label='Remarks'
    )


# ============================================================================
# Advice Payment Forms
# ============================================================================

class AdvicePaymentMasterForm(forms.ModelForm):
    """
    Form for Advice Payment header.
    Converted from: aspnet/Module/Accounts/Transactions/Advice.aspx
    """

    TYPE_CHOICES = [
        ('', 'Select Type'),
        (1, 'Employee'),
        (2, 'Customer'),
        (3, 'Supplier'),
    ]

    ECS_TYPE_CHOICES = [
        ('', 'Select ECS Type'),
        (1, 'Advance'),
        (2, 'Against Bill'),
    ]

    bank = forms.ModelChoiceField(
        queryset=TblaccBank.objects.all().order_by('name'),
        required=False,
        empty_label="Select Bank",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    ecstype = forms.ChoiceField(
        choices=ECS_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    class Meta:
        model = TblaccAdvicePaymentMaster
        fields = ['adno', 'type', 'ecstype', 'payto', 'chequeno', 'chequedate', 'payat', 'bank']

        widgets = {
            'adno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Advice Number (auto-generated)',
                'readonly': 'readonly'
            }),
            'payto': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Pay To'
            }),
            'chequeno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Cheque/DD Number'
            }),
            'chequedate': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'payat': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Payable At'
            }),
        }

        labels = {
            'adno': 'Advice Number',
            'type': 'Pay To Type',
            'ecstype': 'Payment Against',
            'payto': 'Pay To',
            'chequeno': 'Cheque/DD Number',
            'chequedate': 'Cheque Date',
            'payat': 'Payable At',
            'bank': 'Drawn On Bank',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.bank:
            self.fields['bank'].initial = self.instance.bank
            self.fields['type'].initial = self.instance.type
            self.fields['ecstype'].initial = self.instance.ecstype

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('bank'):
            instance.bank = self.cleaned_data['bank'].id
        if self.cleaned_data.get('type'):
            instance.type = int(self.cleaned_data['type']) if self.cleaned_data['type'] else None
        if self.cleaned_data.get('ecstype'):
            instance.ecstype = int(self.cleaned_data['ecstype']) if self.cleaned_data['ecstype'] else None
        if commit:
            instance.save()
        return instance


class AdvicePaymentDetailForm(forms.ModelForm):
    """Form for Advice Payment line items."""

    class Meta:
        model = TblaccAdvicePaymentDetails
        fields = ['proformainvno', 'invdate', 'pono', 'amount', 'particular', 'withingroup', 'wono', 'bg', 'pvevno', 'billagainst']

        widgets = {
            'proformainvno': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Proforma Inv No'
            }),
            'invdate': forms.DateInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'type': 'date'
            }),
            'pono': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'PO No'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
            'particular': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Particular'
            }),
            'withingroup': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Within Group'
            }),
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'WO No'
            }),
            'bg': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'BG'
            }),
            'pvevno': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'PV/EV No'
            }),
            'billagainst': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Bill Against'
            }),
        }


# Create formset for advice payment details
AdvicePaymentDetailFormSet = inlineformset_factory(
    TblaccAdvicePaymentMaster,
    TblaccAdvicePaymentDetails,
    form=AdvicePaymentDetailForm,
    fields=['proformainvno', 'invdate', 'pono', 'amount', 'particular', 'withingroup', 'wono', 'bg', 'pvevno', 'billagainst'],
    extra=3,
    can_delete=True
)


# ============================================================================
# Capital Particulars Forms
# ============================================================================

class CapitalMasterForm(forms.ModelForm):
    """Form for Capital Master (header)."""

    class Meta:
        model = TblaccCapitalMaster
        fields = ['particulars']

        widgets = {
            'particulars': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter capital particulars',
                'rows': 3
            }),
        }

        labels = {
            'particulars': 'Capital Particulars',
        }


class CapitalDetailForm(forms.ModelForm):
    """Form for Capital Details line items."""

    class Meta:
        model = TblaccCapitalDetails
        fields = ['particulars', 'creditamt']

        widgets = {
            'particulars': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Particulars'
            }),
            'creditamt': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
        }


# Create formset for capital details
# Note: Since models use managed=False and mid is IntegerField, not ForeignKey,
# we cannot use inlineformset_factory. Handle master-detail relationship manually in view.
# CapitalDetailFormSet = inlineformset_factory(
#     TblaccCapitalMaster,
#     TblaccCapitalDetails,
#     form=CapitalDetailForm,
#     fields=['particulars', 'creditamt'],
#     extra=3,
#     can_delete=True
# )


# ============================================================================
# Loan Particulars Forms
# ============================================================================

class LoanMasterForm(forms.ModelForm):
    """Form for Loan Master (header)."""

    class Meta:
        model = TblaccLoanmaster
        fields = ['particulars']

        widgets = {
            'particulars': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter loan particulars',
                'rows': 3
            }),
        }

        labels = {
            'particulars': 'Loan Particulars',
        }


class LoanDetailForm(forms.ModelForm):
    """Form for Loan Details line items."""

    class Meta:
        model = TblaccLoandetails
        fields = ['particulars', 'creditamt']

        widgets = {
            'particulars': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Particulars'
            }),
            'creditamt': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
        }


# Create formset for loan details
LoanDetailFormSet = inlineformset_factory(
    TblaccLoanmaster,
    TblaccLoandetails,
    form=LoanDetailForm,
    fields=['particulars', 'creditamt'],
    extra=3,
    can_delete=True
)


# ============================================================================
# CONSOLIDATED FORMS FROM SEPARATE FILES
# All forms below were previously in separate *_forms.py files
# Now consolidated here and migrated to use Tailwind widgets from core/widgets.py
# ============================================================================


# ============================================================================
# SECTION 1: MASTERS - TAX & COMPLIANCE
# ============================================================================

class ExciseServiceForm(forms.ModelForm):
    """
    Form for Excise Service Master
    Consolidated from: excise_service_forms.py
    """

    class Meta:
        model = TblexciseserMaster
        fields = ['terms']
        widgets = {
            'terms': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter excise service description'
            }),
        }
        labels = {
            'terms': 'Excise Service Description',
        }

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms or not terms.strip():
            raise forms.ValidationError('Excise service description is required.')
        return terms.strip()


class ExcisableCommodityForm(forms.ModelForm):
    """
    Form for Excisable Commodity Master
    Consolidated from: excisable_commodity_forms.py
    """

    class Meta:
        model = TblexcisecommodityMaster
        fields = ['terms', 'chaphead']
        widgets = {
            'terms': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter commodity description'
            }),
            'chaphead': TailwindTextInput(attrs={
                'placeholder': 'Enter chapter heading'
            }),
        }
        labels = {
            'terms': 'Commodity Description',
            'chaphead': 'Chapter Heading',
        }

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms or not terms.strip():
            raise forms.ValidationError('Commodity description is required.')
        return terms.strip()


class VATForm(forms.ModelForm):
    """
    Form for VAT/CST Master
    Consolidated from: vat_forms.py
    """

    class Meta:
        model = TblvatMaster
        fields = ['terms', 'value', 'live', 'isvat', 'iscst']
        widgets = {
            'terms': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter VAT/CST description'
            }),
            'value': TailwindNumberInput(attrs={
                'placeholder': 'Enter percentage value',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'live': TailwindSelect(choices=[(1, 'Active'), (0, 'Inactive')]),
            'isvat': TailwindSelect(choices=[(1, 'Yes'), (0, 'No')]),
            'iscst': TailwindSelect(choices=[(1, 'Yes'), (0, 'No')]),
        }
        labels = {
            'terms': 'Description',
            'value': 'Percentage Value',
            'live': 'Status',
            'isvat': 'Is VAT',
            'iscst': 'Is CST',
        }

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms or not terms.strip():
            raise forms.ValidationError('Description is required.')
        return terms.strip()

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value is not None and (value < 0 or value > 100):
            raise forms.ValidationError('Percentage value must be between 0 and 100.')
        return value


class OctroiForm(forms.ModelForm):
    """
    Form for Octroi Master
    Consolidated from: octroi_forms.py
    """

    class Meta:
        model = TbloctroiMaster
        fields = ['terms']
        widgets = {
            'terms': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter octroi terms'
            }),
        }
        labels = {
            'terms': 'Octroi Terms',
        }

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms or not terms.strip():
            raise forms.ValidationError('Octroi terms are required.')
        return terms.strip()


class FreightForm(forms.ModelForm):
    """
    Form for Freight Master
    Consolidated from: freight_forms.py
    """

    class Meta:
        model = TblfreightMaster
        fields = ['terms']
        widgets = {
            'terms': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter freight terms'
            }),
        }
        labels = {
            'terms': 'Freight Terms',
        }

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms or not terms.strip():
            raise forms.ValidationError('Freight terms are required.')
        return terms.strip()


# ============================================================================
# SECTION 2: MASTERS - PAYMENT & TERMS
# ============================================================================

class PaymentModeForm(forms.ModelForm):
    """
    Form for Payment Mode Master
    Consolidated from: payment_mode_forms.py
    Note: This uses TextInput vs PaymentTermsForm which uses Textarea
    """

    class Meta:
        model = TblaccPaymentmode
        fields = ['terms']
        widgets = {
            'terms': TailwindTextInput(attrs={
                'placeholder': 'Enter payment mode/terms',
                'maxlength': '200'
            }),
        }
        labels = {
            'terms': 'Payment Mode / Terms',
        }

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if terms:
            terms = terms.strip()
            if len(terms) < 2:
                raise forms.ValidationError("Payment mode must be at least 2 characters long.")
        return terms


class InterestTypeForm(forms.ModelForm):
    """
    Form for Interest Type Master
    Consolidated from: interest_type_forms.py
    """

    class Meta:
        model = TblaccIntresttype
        fields = ['description']
        widgets = {
            'description': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter interest type description'
            }),
        }
        labels = {
            'description': 'Interest Type Description',
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise forms.ValidationError('Interest type description is required.')
        return description.strip()


class LoanTypeForm(forms.ModelForm):
    """
    Form for Loan Type Master
    Consolidated from: loan_type_forms.py
    """

    class Meta:
        model = TblaccLoantype
        fields = ['description']
        widgets = {
            'description': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter loan type description'
            }),
        }
        labels = {
            'description': 'Loan Type Description',
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise forms.ValidationError('Loan type description is required.')
        return description.strip()


class PaidTypeForm(forms.ModelForm):
    """
    Form for Paid Type Master
    Consolidated from: paid_type_forms.py
    """

    class Meta:
        model = TblaccPaidtype
        fields = ['particulars']
        widgets = {
            'particulars': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter paid type particulars'
            }),
        }
        labels = {
            'particulars': 'Paid Type Particulars',
        }

    def clean_particulars(self):
        particulars = self.cleaned_data.get('particulars')
        if not particulars or not particulars.strip():
            raise forms.ValidationError('Paid type particulars are required.')
        return particulars.strip()


class WarrantyTermsForm(forms.ModelForm):
    """
    Form for Warranty Terms Master
    Consolidated from: warranty_terms_forms.py
    """

    class Meta:
        model = TblwarrentyMaster
        fields = ['terms']
        widgets = {
            'terms': TailwindTextInput(attrs={
                'placeholder': 'Enter warranty terms',
                'maxlength': '200'
            }),
        }
        labels = {
            'terms': 'Warranty Terms',
        }

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if terms:
            terms = terms.strip()
            if len(terms) < 2:
                raise forms.ValidationError("Warranty terms must be at least 2 characters long.")
        return terms


# ============================================================================
# SECTION 3: MASTERS - TRANSACTION REFERENCES
# ============================================================================

class InvoiceAgainstForm(forms.ModelForm):
    """
    Form for Invoice Against Master
    Consolidated from: invoice_against_forms.py
    """

    class Meta:
        model = TblaccInvoiceagainst
        fields = ['against']
        widgets = {
            'against': TailwindTextarea(attrs={
                'rows': 2,
                'placeholder': 'Enter invoice against description'
            }),
        }
        labels = {
            'against': 'Invoice Against',
        }

    def clean_against(self):
        against = self.cleaned_data.get('against')
        if not against or not against.strip():
            raise forms.ValidationError('Invoice against field is required.')
        return against.strip()


class IOUReasonsForm(forms.ModelForm):
    """
    Form for IOU Reasons Master
    Consolidated from: iou_reasons_forms.py
    """

    class Meta:
        model = TblaccIouReasons
        fields = ['terms']
        widgets = {
            'terms': TailwindTextInput(attrs={
                'placeholder': 'Enter IOU reason',
                'maxlength': '200'
            }),
        }
        labels = {
            'terms': 'IOU Reason',
        }

    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if terms:
            terms = terms.strip()
            if len(terms) < 2:
                raise forms.ValidationError("IOU reason must be at least 2 characters long.")
        return terms


# ============================================================================
# END OF CONSOLIDATED FORMS
# All forms from separate *_forms.py files have been consolidated above
# Note: InvoiceForm and InvoiceDetailForm from invoice_forms.py were already
# present in the main forms.py file, so they are not duplicated here
# ============================================================================


# ============================================================================
# Creditors/Debitors Forms
# Converted from ASP.NET CreditorsDebitors.aspx
# ============================================================================

from .models import TblaccCreditorsMaster, TblaccDebitorsMaster


class CreditorForm(forms.ModelForm):
    """
    Form for Creditor (Supplier) opening balance management.
    Converted from: aspnet/Module/Accounts/Transactions/CreditorsDebitors.aspx
    """

    class Meta:
        model = TblaccCreditorsMaster
        fields = ['supplierid', 'openingamt']

        widgets = {
            'supplierid': HTMXSelect(attrs={
                'placeholder': 'Select Supplier',
                'hx-get': '/accounts/api/supplier-details/',
                'hx-trigger': 'change',
                'hx-target': '#supplier-info'
            }),
            'openingamt': TailwindNumberInput(attrs={
                'placeholder': 'Enter opening amount',
                'step': '0.01',
                'min': '0'
            }),
        }

        labels = {
            'supplierid': 'Supplier Name',
            'openingamt': 'Opening Amount',
        }

    def clean_openingamt(self):
        """Validate opening amount is not negative."""
        openingamt = self.cleaned_data.get('openingamt')
        if openingamt and openingamt < 0:
            raise forms.ValidationError('Opening amount cannot be negative.')
        return openingamt


class DebitorForm(forms.ModelForm):
    """
    Form for Debitor (Customer) opening balance management.
    Converted from: aspnet/Module/Accounts/Transactions/CreditorsDebitors.aspx
    """

    class Meta:
        model = TblaccDebitorsMaster
        fields = ['customerid', 'openingamt']

        widgets = {
            'customerid': HTMXSelect(attrs={
                'placeholder': 'Select Customer',
                'hx-get': '/accounts/api/customer-details/',
                'hx-trigger': 'change',
                'hx-target': '#customer-info'
            }),
            'openingamt': TailwindNumberInput(attrs={
                'placeholder': 'Enter opening amount',
                'step': '0.01',
                'min': '0'
            }),
        }

        labels = {
            'customerid': 'Customer Name',
            'openingamt': 'Opening Amount',
        }

    def clean_openingamt(self):
        """Validate opening amount is not negative."""
        openingamt = self.cleaned_data.get('openingamt')
        if openingamt and openingamt < 0:
            raise forms.ValidationError('Opening amount cannot be negative.')
        return openingamt


class DateRangeFilterForm(forms.Form):
    """
    Form for filtering creditors/debitors transactions by date range.
    Used in detail views for filtering transaction history.
    """

    from_date = forms.DateField(
        required=False,
        widget=TailwindDateInput(attrs={
            'placeholder': 'From Date'
        }),
        label='From Date'
    )

    to_date = forms.DateField(
        required=False,
        widget=TailwindDateInput(attrs={
            'placeholder': 'To Date'
        }),
        label='To Date'
    )

    def clean(self):
        """Validate date range."""
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        if from_date and to_date:
            if from_date > to_date:
                raise forms.ValidationError('From date cannot be after to date.')

        return cleaned_data


# ============================================================================
# SECTION 5: POLICY DOCUMENTS
# ============================================================================

class PolicyForm(forms.ModelForm):
    """
    Form for Accounting Policy Documents Upload
    Converted from: aaspnet/Module/Accounts/Transactions/ACC_POLICY.aspx
    """
    # File upload field
    file_upload = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png'
        }),
        label='Select File'
    )

    class Meta:
        model = AccPolicy
        fields = ['cvname', 'cvdate']
        widgets = {
            'cvname': TailwindTextInput(attrs={
                'placeholder': 'Enter remark/description',
                'maxlength': '200'
            }),
            'cvdate': TailwindDateInput(attrs={
                'placeholder': 'dd-mm-yyyy'
            }),
        }
        labels = {
            'cvname': 'Remark',
            'cvdate': 'Date',
        }

    def clean_cvdate(self):
        cvdate = self.cleaned_data.get('cvdate')
        if cvdate:
            return cvdate.strftime('%d-%m-%Y') if hasattr(cvdate, 'strftime') else cvdate
        return cvdate



# ============================================================================
# SALES INVOICE FORMS - CONSOLIDATED FROM forms_sales_invoice.py
# Complete implementation matching ASP.NET SalesInvoice_New_Details.aspx
# ============================================================================


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
            # CRITICAL: Model fields are TextField/CharField, not DateField
            # Database stores dates as DD-MM-YYYY strings (ASP.NET format)
            # But HTML5 date inputs need value in YYYY-MM-DD format
            # Conversion handled in clean() method
            'dateofissueinvoice': forms.TextInput(attrs={
                'type': 'date',
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'required': 'required'
            }),
            'dateofremoval': forms.TextInput(attrs={
                'type': 'date',
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded',
                'required': 'required'
            }),
            'timeofissueinvoice': forms.TextInput(attrs={
                'type': 'time',
                'class': 'px-3 py-1.5 text-sm border border-gray-300 rounded hidden',
                'value': '00:00:00'
            }),
            'timeofremoval': forms.TextInput(attrs={
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

    def clean_dateofissueinvoice(self):
        """
        Convert HTML5 date input (YYYY-MM-DD) to ASP.NET format (DD-MM-YYYY)
        Database stores dates as strings in DD-MM-YYYY format
        """
        date_str = self.cleaned_data.get('dateofissueinvoice')
        if not date_str:
            raise forms.ValidationError('Date of Issue is required')

        try:
            from datetime import datetime
            # Parse YYYY-MM-DD from HTML5 input
            if isinstance(date_str, str):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                # Convert to DD-MM-YYYY for database
                return date_obj.strftime('%d-%m-%Y')
        except ValueError:
            raise forms.ValidationError('Invalid date format. Please select a valid date from the date picker.')
        except AttributeError:
            raise forms.ValidationError('Invalid date value. Please select a date.')

        return date_str

    def clean_dateofremoval(self):
        """
        Convert HTML5 date input (YYYY-MM-DD) to ASP.NET format (DD-MM-YYYY)
        Database stores dates as strings in DD-MM-YYYY format
        """
        date_str = self.cleaned_data.get('dateofremoval')
        if not date_str:
            raise forms.ValidationError('Date of Removal is required')

        try:
            from datetime import datetime
            # Parse YYYY-MM-DD from HTML5 input
            if isinstance(date_str, str):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                # Convert to DD-MM-YYYY for database
                return date_obj.strftime('%d-%m-%Y')
        except ValueError:
            raise forms.ValidationError('Invalid date format. Please select a valid date from the date picker.')
        except AttributeError:
            raise forms.ValidationError('Invalid date value. Please select a date.')

        return date_str


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
            'buyer_country', 'buyer_state',
            # buyer_city excluded - ForeignKey handled manually in view
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

        # Get country value (from POST data if bound, otherwise from initial)
        country_value = None
        if self.is_bound:
            country_value = self.data.get('buyer_country')
        elif self.initial:
            country_value = self.initial.get('buyer_country')

        # Cascading State dropdown - populate based on country
        state_choices = [('', 'Select State')]
        if country_value and str(country_value).strip():
            from sys_admin.models import Tblstate
            states = Tblstate.objects.filter(
                cid=country_value
            ).values_list('sid', 'statename').distinct().order_by('statename')
            state_choices.extend([(str(sid), sname) for sid, sname in states])

        self.fields['buyer_state'] = forms.ChoiceField(
            label='State',
            required=True,
            choices=state_choices,
            widget=forms.Select(attrs={'class': tw_select})
        )

        # Get state value (from POST data if bound, otherwise from initial)
        state_value = None
        if self.is_bound:
            state_value = self.data.get('buyer_state')
        elif self.initial:
            state_value = self.initial.get('buyer_state')

        # Cascading City dropdown - populate based on state
        city_choices = [('', 'Select City')]
        if state_value and str(state_value).strip():
            from sys_admin.models import Tblcity
            cities = Tblcity.objects.filter(
                sid=state_value
            ).values_list('cityid', 'cityname').order_by('cityname')
            city_choices.extend([(str(cid), cname) for cid, cname in cities])

        self.fields['buyer_city'] = forms.ChoiceField(
            label='City',
            required=True,
            choices=city_choices,
            widget=forms.Select(attrs={'class': tw_select})
        )

        # Set all fields as required
        for field_name in self.fields:
            self.fields[field_name].required = True

    def clean(self):
        """Validate state and city are selected."""
        cleaned_data = super().clean()

        # Validate state is selected
        buyer_state = cleaned_data.get('buyer_state')
        if not buyer_state or buyer_state == '':
            raise forms.ValidationError('Please select a state for the buyer')

        # Validate city is selected
        buyer_city = cleaned_data.get('buyer_city')
        if not buyer_city or buyer_city == '':
            raise forms.ValidationError('Please select a city for the buyer')

        return cleaned_data

    def save(self, commit=True):
        """
        Override save to convert city string ID to Tblcity instance.
        buyer_city is a ForeignKey in the model but a ChoiceField in the form.
        """
        instance = super().save(commit=False)

        # Convert buyer_city string ID to Tblcity instance
        buyer_city_id = self.cleaned_data.get('buyer_city')
        if buyer_city_id:
            try:
                instance.buyer_city = Tblcity.objects.get(cityid=int(buyer_city_id))
            except Tblcity.DoesNotExist:
                instance.buyer_city = None

        if commit:
            instance.save()
        return instance


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
            'cong_country', 'cong_state',
            # cong_city excluded - ForeignKey handled manually in view
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

        # Get country value (from POST data if bound, otherwise from initial)
        country_value = None
        if self.is_bound:
            country_value = self.data.get('cong_country')
        elif self.initial:
            country_value = self.initial.get('cong_country')

        # Cascading State dropdown - populate based on country
        state_choices = [('', 'Select State')]
        if country_value and str(country_value).strip():
            from sys_admin.models import Tblstate
            states = Tblstate.objects.filter(
                cid=country_value
            ).values_list('sid', 'statename').distinct().order_by('statename')
            state_choices.extend([(str(sid), sname) for sid, sname in states])

        self.fields['cong_state'] = forms.ChoiceField(
            label='State',
            required=True,
            choices=state_choices,
            widget=forms.Select(attrs={'class': tw_select})
        )

        # Get state value (from POST data if bound, otherwise from initial)
        state_value = None
        if self.is_bound:
            state_value = self.data.get('cong_state')
        elif self.initial:
            state_value = self.initial.get('cong_state')

        # Cascading City dropdown - populate based on state
        city_choices = [('', 'Select City')]
        if state_value and str(state_value).strip():
            from sys_admin.models import Tblcity
            cities = Tblcity.objects.filter(
                sid=state_value
            ).values_list('cityid', 'cityname').order_by('cityname')
            city_choices.extend([(str(cid), cname) for cid, cname in cities])

        self.fields['cong_city'] = forms.ChoiceField(
            label='City',
            required=True,
            choices=city_choices,
            widget=forms.Select(attrs={'class': tw_select})
        )

        # Set all fields as required
        for field_name in self.fields:
            self.fields[field_name].required = True

    def clean(self):
        """Validate required fields including state and city."""
        cleaned_data = super().clean()

        # Validate consignee state is selected
        cong_state = cleaned_data.get('cong_state')
        if not cong_state or cong_state == '':
            raise forms.ValidationError('Please select a state for the consignee')

        # Validate consignee city is selected
        cong_city = cleaned_data.get('cong_city')
        if not cong_city or cong_city == '':
            raise forms.ValidationError('Please select a city for the consignee')

        return cleaned_data

    def save(self, commit=True):
        """
        Override save to convert city string ID to Tblcity instance.
        cong_city is a ForeignKey in the model but a ChoiceField in the form.
        """
        instance = super().save(commit=False)

        # Convert cong_city string ID to Tblcity instance
        cong_city_id = self.cleaned_data.get('cong_city')
        if cong_city_id:
            try:
                instance.cong_city = Tblcity.objects.get(cityid=int(cong_city_id))
            except Tblcity.DoesNotExist:
                instance.cong_city = None

        if commit:
            instance.save()
        return instance


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
            'class': 'w-4 h-4'
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
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded text-right w-full',
            'step': '0.001',
            'placeholder': '0.000'
        })
    )

    # Readonly: Rate
    rate = forms.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded bg-gray-100 text-right w-full',
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
            'class': 'px-2 py-1 text-sm border border-gray-300 rounded text-right w-full',
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
        cenvat_choices = [
            (tax.id, tax.terms)
            for tax in TblexciseserMaster.objects.filter(
                id__in=[1, 30, 31, 32, 33, 34, 35, 36, 37, 38]
            ).order_by('id')
        ]
        # Add blank option only if no choices available
        if cenvat_choices:
            self.fields['cenvat'] = forms.ChoiceField(
                label='CGST/IGST',
                required=True,
                choices=cenvat_choices,
                widget=forms.Select(attrs={'class': tw_select})
            )
        else:
            self.fields['cenvat'] = forms.ChoiceField(
                label='CGST/IGST',
                required=True,
                choices=[('', 'No tax options available')],
                widget=forms.Select(attrs={'class': tw_select})
            )

        # SGST/CST dropdown (VISIBLE, REQUIRED)
        vat_choices = [
            (tax.id, tax.terms)
            for tax in TblvatMaster.objects.filter(
                id__in=[1, 2, 93, 94, 95, 124, 129, 130]
            ).order_by('id')
        ]
        # Add blank option only if no choices available
        if vat_choices:
            self.fields['vat'] = forms.ChoiceField(
                label='SGST/CST',
                required=True,
                choices=vat_choices,
                widget=forms.Select(attrs={'class': tw_select})
            )
        else:
            self.fields['vat'] = forms.ChoiceField(
                label='SGST/CST',
                required=True,
                choices=[('', 'No tax options available')],
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
        cenvat = cleaned_data.get('cenvat')
        if not cenvat or cenvat == '':
            raise forms.ValidationError('Please select CGST/IGST')

        # Validate SGST/CST is selected
        vat = cleaned_data.get('vat')
        if not vat or vat == '':
            raise forms.ValidationError('Please select SGST/CST')

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
