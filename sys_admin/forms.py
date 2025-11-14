"""
SysAdmin Forms - Converted from ASP.NET Module/SysAdmin
All forms use ModelForm with Tailwind CSS styling.
"""

from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Tblcountry, Tblstate, Tblcity, TblfinancialMaster, TblcompanyMaster, UnitMaster


class CountryForm(forms.ModelForm):
    """
    Form for Country master data.
    Converted from: aspnet/Module/SysAdmin/Country.aspx
    """
    
    class Meta:
        model = Tblcountry
        fields = ['countryname', 'currency', 'symbol', 'keyshortcut']
        widgets = {
            'countryname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter country name',
                'required': True
            }),
            'currency': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter currency',
                'required': True
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol',
                'required': True
            }),
            'keyshortcut': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter shortcut (optional)'
            }),
        }
        labels = {
            'countryname': 'Country Name',
            'currency': 'Currency',
            'symbol': 'Symbol',
            'keyshortcut': 'Key Shortcut',
        }
    
    def clean_countryname(self):
        """Validate country name is not empty and unique."""
        countryname = self.cleaned_data.get('countryname')
        if not countryname or not countryname.strip():
            raise forms.ValidationError('Country name is required.')
        
        # Check uniqueness (case-insensitive)
        qs = Tblcountry.objects.filter(countryname__iexact=countryname.strip())
        if self.instance.pk:
            qs = qs.exclude(cid=self.instance.cid)
        
        if qs.exists():
            raise forms.ValidationError('Country name already exists.')
        
        return countryname.strip()
    
    def clean_currency(self):
        """Validate currency is not empty."""
        currency = self.cleaned_data.get('currency')
        if not currency or not currency.strip():
            raise forms.ValidationError('Currency is required.')
        return currency.strip()
    
    def clean_symbol(self):
        """Validate symbol is not empty."""
        symbol = self.cleaned_data.get('symbol')
        if not symbol or not symbol.strip():
            raise forms.ValidationError('Symbol is required.')
        return symbol.strip()


class StateForm(forms.ModelForm):
    """
    Form for State master data.
    Converted from: aspnet/Module/SysAdmin/State.aspx
    """
    
    class Meta:
        model = Tblstate
        fields = ['cid', 'statename']
        widgets = {
            'cid': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'required': True
            }),
            'statename': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter state name',
                'required': True
            }),
        }
        labels = {
            'cid': 'Country',
            'statename': 'State Name',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate country dropdown
        self.fields['cid'].queryset = Tblcountry.objects.all().order_by('countryname')
        self.fields['cid'].label_from_instance = lambda obj: obj.countryname
    
    def clean_statename(self):
        """Validate state name is not empty."""
        statename = self.cleaned_data.get('statename')
        if not statename or not statename.strip():
            raise forms.ValidationError('State name is required.')
        return statename.strip()
    
    def clean_cid(self):
        """Validate country is selected."""
        cid = self.cleaned_data.get('cid')
        if not cid:
            raise forms.ValidationError('Country is required.')
        return cid


class CityForm(forms.ModelForm):
    """
    Form for City master data.
    Converted from: aspnet/Module/SysAdmin/City.aspx
    """
    
    class Meta:
        model = Tblcity
        fields = ['sid', 'cityname']
        widgets = {
            'sid': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'required': True
            }),
            'cityname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter city name',
                'required': True
            }),
        }
        labels = {
            'sid': 'State',
            'cityname': 'City Name',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate state dropdown
        self.fields['sid'].queryset = Tblstate.objects.select_related('cid').all().order_by('statename')
        self.fields['sid'].label_from_instance = lambda obj: f"{obj.statename} ({obj.cid.countryname})"
    
    def clean_cityname(self):
        """Validate city name is not empty."""
        cityname = self.cleaned_data.get('cityname')
        if not cityname or not cityname.strip():
            raise forms.ValidationError('City name is required.')
        return cityname.strip()
    
    def clean_sid(self):
        """Validate state is selected."""
        sid = self.cleaned_data.get('sid')
        if not sid:
            raise forms.ValidationError('State is required.')
        return sid


class FinancialYearForm(forms.ModelForm):
    """
    Form for creating new Financial Year.
    Converted from: aspnet/Module/SysAdmin/FinancialYear/FinYrs_New.aspx
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 7.1, 7.2, 7.3, 7.4
    """
    
    # Custom field for company selection (not part of model)
    company = forms.ModelChoiceField(
        queryset=TblcompanyMaster.objects.filter(flag=1),
        empty_label="Select Company",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label='Company'
    )
    
    # Financial year label selection (e.g., "2024-2025")
    finyear = forms.ChoiceField(
        choices=[],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'size': '5'
        }),
        label='Financial Year'
    )
    
    # Date fields with HTML5 date picker
    finyearfrom = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date',
            'placeholder': 'DD-MM-YYYY'
        }),
        label='Date From'
    )
    
    finyearto = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date',
            'placeholder': 'DD-MM-YYYY'
        }),
        label='Date To'
    )
    
    class Meta:
        model = TblfinancialMaster
        fields = ['finyear', 'finyearfrom', 'finyearto']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Generate year options (current year ± 5 years)
        current_year = datetime.now().year
        year_choices = []
        for i in range(-2, 6):
            start_year = current_year + i
            end_year = start_year + 1
            year_label = f"{start_year}-{end_year}"
            year_choices.append((year_label, year_label))
        
        self.fields['finyear'].choices = [('', 'Select Financial Year')] + year_choices
        
        # Set label_from_instance for company dropdown
        self.fields['company'].label_from_instance = lambda obj: obj.companyname
    
    def clean_finyearfrom(self):
        """Validate date from format."""
        finyearfrom = self.cleaned_data.get('finyearfrom')
        if not finyearfrom:
            raise ValidationError('Date From is required.')
        return finyearfrom
    
    def clean_finyearto(self):
        """Validate date to format."""
        finyearto = self.cleaned_data.get('finyearto')
        if not finyearto:
            raise ValidationError('Date To is required.')
        return finyearto
    
    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        finyearfrom = cleaned_data.get('finyearfrom')
        finyearto = cleaned_data.get('finyearto')
        company = cleaned_data.get('company')
        finyear = cleaned_data.get('finyear')
        
        # Validate date range
        if finyearfrom and finyearto:
            if finyearto <= finyearfrom:
                raise ValidationError('End date must be after start date.')
            
            # Check if date range is approximately 12 months (350-380 days)
            days_diff = (finyearto - finyearfrom).days
            if days_diff < 350 or days_diff > 380:
                raise ValidationError(
                    f'Financial year should be approximately 12 months. Current range is {days_diff} days.'
                )
        
        # Check for duplicate financial year for the same company
        if company and finyear:
            existing = TblfinancialMaster.objects.filter(
                compid=company.compid,
                finyear=finyear,
                flag=1
            )
            
            # Exclude current instance if updating
            if self.instance.pk:
                existing = existing.exclude(finyearid=self.instance.finyearid)
            
            if existing.exists():
                raise ValidationError(
                    f'Financial year {finyear} already exists for {company.companyname}.'
                )
        
        # Check for overlapping dates with existing financial years
        if company and finyearfrom and finyearto:
            overlapping = TblfinancialMaster.objects.filter(
                compid=company.compid,
                flag=1
            ).exclude(
                finyearid=self.instance.finyearid if self.instance.pk else None
            )
            
            for fy in overlapping:
                # Parse existing dates (they might be stored as strings)
                try:
                    if isinstance(fy.finyearfrom, str):
                        existing_from = datetime.strptime(fy.finyearfrom, '%d-%m-%Y').date()
                    else:
                        existing_from = fy.finyearfrom
                    
                    if isinstance(fy.finyearto, str):
                        existing_to = datetime.strptime(fy.finyearto, '%d-%m-%Y').date()
                    else:
                        existing_to = fy.finyearto
                    
                    # Check for overlap
                    if (finyearfrom <= existing_to and finyearto >= existing_from):
                        raise ValidationError(
                            f'Financial year dates overlap with existing year {fy.finyear} '
                            f'({fy.finyearfrom} to {fy.finyearto}) for {company.companyname}.'
                        )
                except (ValueError, AttributeError):
                    # Skip if date parsing fails
                    continue
        
        return cleaned_data


class FinancialYearUpdateForm(forms.ModelForm):
    """
    Simplified form for updating only dates of existing Financial Year.
    Converted from: aspnet/Module/SysAdmin/FinancialYear/FinYrs_Update.aspx
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """
    
    finyearfrom = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        }),
        label='Date From'
    )
    
    finyearto = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        }),
        label='Date To'
    )
    
    class Meta:
        model = TblfinancialMaster
        fields = ['finyearfrom', 'finyearto']
    
    def clean(self):
        """Validate date range."""
        cleaned_data = super().clean()
        finyearfrom = cleaned_data.get('finyearfrom')
        finyearto = cleaned_data.get('finyearto')
        
        if finyearfrom and finyearto:
            if finyearto <= finyearfrom:
                raise ValidationError('End date must be after start date.')
            
            # Check if date range is approximately 12 months
            days_diff = (finyearto - finyearfrom).days
            if days_diff < 350 or days_diff > 380:
                raise ValidationError(
                    f'Financial year should be approximately 12 months. Current range is {days_diff} days.'
                )
        
        return cleaned_data



class UnitMasterForm(forms.ModelForm):
    """
    Form for Unit Master.
    Converted from: aspnet/Module/Design/Masters/Unit_Master.aspx
    """
    
    class Meta:
        model = UnitMaster
        fields = ['unitname', 'symbol', 'effectoninvoice']
        
        widgets = {
            'unitname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter unit name'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol'
            }),
            'effectoninvoice': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500'
            }),
        }
        
        labels = {
            'unitname': 'Unit Name',
            'symbol': 'Symbol',
            'effectoninvoice': 'Effect On Invoice',
        }
    
    def clean_unitname(self):
        """Validate unit name is not empty."""
        unitname = self.cleaned_data.get('unitname')
        if not unitname or not unitname.strip():
            raise forms.ValidationError('Unit name is required.')
        return unitname.strip()
    
    def clean_symbol(self):
        """Validate symbol is not empty."""
        symbol = self.cleaned_data.get('symbol')
        if not symbol or not symbol.strip():
            raise forms.ValidationError('Symbol is required.')
        return symbol.strip()
