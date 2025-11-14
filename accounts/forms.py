"""
Forms for the Accounts module.
Converted from ASP.NET Module/Accounts/Masters/*.aspx
"""

from django import forms
from django.forms import inlineformset_factory
from decimal import Decimal

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
    # Additional models from separate form files
    TblexciseserMaster, TblexcisecommodityMaster, TblvatMaster,
    TblfreightMaster, TbloctroiMaster, TblaccIntresttype,
    TblaccLoantype, TblaccPaidtype, TblaccInvoiceagainst,
    TblaccIouReasons, TblwarrentyMaster
)
from sys_admin.models import Tblcountry, Tblstate, Tblcity


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
