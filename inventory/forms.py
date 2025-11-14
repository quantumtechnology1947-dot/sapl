"""
Inventory Module Forms
"""
from django import forms
from django.forms import inlineformset_factory
from .models import (
    TblinvMaterialrequisitionMaster, TblinvMaterialrequisitionDetails,
    TblinvMaterialissueMaster, TblinvMaterialissueDetails,
    TblinvMaterialreturnMaster, TblinvMaterialreturnDetails,
    TblvehProcessMaster, TblinvInwardMaster, TblinvInwardDetails,
    TblinvMaterialreceivedMaster, TblinvMaterialreceivedDetails,
    TblinvMaterialservicenoteMaster, TblinvSupplierChallanMaster, TblinvSupplierChallanDetails,
    TblinvCustomerChallanMaster, TblinvCustomerChallanDetails,
    TblinvWisMaster, TblinvWisDetails,
    TblGatepass,
    TblinvAutowisTimeschedule,
)
# NOTE: Many forms in this file reference models and fields that don't exist in inventory/models.py
# These forms need major rework to match actual database schema:
# - SupplierChallanMasterForm: uses supplierchallanno (model has scno), supplierchallandate, drivername (model has transpoter)
# - SupplierChallanDetailForm: uses itemid, qty (model has prdid, challanqty)
# - CustomerChallanMasterForm: uses customerchallanno (model has ccno), customerchallandate, wonumber (model has wono)
# - CustomerChallanDetailForm: uses qty (model has challanqty)
# - GatePassMasterForm/GatePassDetailForm: reference non-existent models (only TblGatepass exists with different fields)
# - VehicleMasterForm/VehicleTripForm: reference non-existent models (only TblvehProcessMaster, TblvehMasterDetails exist)
# - WISMasterForm: uses wisdate, productionqty, remarks (model only has wisno, wono)
# - WISDetailForm: uses requiredqty, actualqty, variance, remarks (model only has wisno, pid, cid, itemid, issuedqty)
# - ItemLocationForm: references non-existent model Tblitemlocation
# - MCNMasterForm/MCNDetailForm: reference non-existent models
# - ChallanMasterForm/ChallanDetailForm: reference non-existent models TblinvChallanMaster/Details
# - ClosingStockForm: references non-existent Tblitemmaster from inventory module


class BaseTransactionForm(forms.ModelForm):
    """Base form for transaction master records"""
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        self.compid = kwargs.pop('compid', None)
        self.finyearid = kwargs.pop('finyearid', None)
        self.sessionid = kwargs.pop('sessionid', None)
        super().__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            })


class MRSMasterForm(BaseTransactionForm):
    """Form for Material Requisition Slip Master"""
    
    class Meta:
        model = TblinvMaterialrequisitionMaster
        fields = ['mrsno']
        widgets = {
            'mrsno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 focus:outline-none'
            })
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set system fields
        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()
        
        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid
        
        if commit:
            instance.save()
        
        return instance


class MRSDetailForm(forms.ModelForm):
    """Form for Material Requisition Slip Details"""
    
    # Additional fields for display
    item_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    item_description = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    uom = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    stock_qty = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = TblinvMaterialrequisitionDetails
        fields = ['itemid', 'deptid', 'wono', 'reqqty', 'remarks']
        widgets = {
            'itemid': forms.HiddenInput(),
            'deptid': forms.Select(attrs={'class': 'form-select'}),
            'wono': forms.TextInput(attrs={'placeholder': 'Work Order Number'}),
            'reqqty': forms.NumberInput(attrs={'placeholder': 'Required Quantity', 'step': '0.001'}),
            'remarks': forms.TextInput(attrs={'placeholder': 'Remarks'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        deptid = cleaned_data.get('deptid')
        wono = cleaned_data.get('wono')
        reqqty = cleaned_data.get('reqqty')
        
        # Either deptid or wono must be provided
        if not deptid and not wono:
            raise forms.ValidationError('Either BGGroup or WO Number is required')
        
        # Required quantity must be positive
        if reqqty and reqqty <= 0:
            raise forms.ValidationError('Required quantity must be greater than 0')
        
        return cleaned_data


# Create formset for MRS details
# NOTE: Commented out due to foreign key relationship issues with managed=False models
# MRSDetailFormSet = inlineformset_factory(
#     TblinvMaterialrequisitionMaster,
#     TblinvMaterialrequisitionDetails,
#     form=MRSDetailForm,
#     extra=1,
#     can_delete=True,
#     min_num=1,
#     validate_min=True
# )


class MINMasterForm(BaseTransactionForm):
    """Form for Material Issue Note Master"""
    
    class Meta:
        model = TblinvMaterialissueMaster
        fields = ['minno', 'mrsno', 'mrsid']
        widgets = {
            'minno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 focus:outline-none'
            }),
            'mrsno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 focus:outline-none'
            }),
            'mrsid': forms.HiddenInput(),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()
        
        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid
        
        if commit:
            instance.save()
        
        return instance


class MINDetailForm(forms.ModelForm):
    """Form for Material Issue Note Details"""
    
    # Additional fields for display
    item_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    item_description = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    req_qty = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    balance_qty = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = TblinvMaterialissueDetails
        fields = ['mrsid', 'issueqty']
        widgets = {
            'mrsid': forms.HiddenInput(),
            'issueqty': forms.NumberInput(attrs={'placeholder': 'Issue Quantity', 'step': '0.001'}),
        }
    
    def clean_issueqty(self):
        issueqty = self.cleaned_data.get('issueqty')
        
        if issueqty and issueqty <= 0:
            raise forms.ValidationError('Issue quantity must be greater than 0')
        
        return issueqty


# Create formset for MIN details
# NOTE: Commented out due to foreign key relationship issues with managed=False models
# MINDetailFormSet = inlineformset_factory(
#     TblinvMaterialissueMaster,
#     TblinvMaterialissueDetails,
#     form=MINDetailForm,
#     extra=0,
#     can_delete=False,
#     min_num=1,
#     validate_min=True
# )


class MRNMasterForm(BaseTransactionForm):
    """Form for Material Return Note Master"""
    
    class Meta:
        model = TblinvMaterialreturnMaster
        fields = ['mrnno']
        widgets = {
            'mrnno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 focus:outline-none'
            })
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()
        
        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid
        
        if commit:
            instance.save()
        
        return instance


class MRNDetailForm(forms.ModelForm):
    """Form for Material Return Note Details"""
    
    # Additional fields for display
    item_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    item_description = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = TblinvMaterialreturnDetails
        fields = ['itemid', 'deptid', 'wono', 'retqty', 'remarks']
        widgets = {
            'itemid': forms.HiddenInput(),
            'deptid': forms.Select(attrs={'class': 'form-select'}),
            'wono': forms.TextInput(attrs={'placeholder': 'Work Order Number'}),
            'retqty': forms.NumberInput(attrs={'placeholder': 'Return Quantity', 'step': '0.001'}),
            'remarks': forms.TextInput(attrs={'placeholder': 'Return Reason/Remarks'}),
        }
    
    def clean_retqty(self):
        retqty = self.cleaned_data.get('retqty')
        
        if retqty and retqty <= 0:
            raise forms.ValidationError('Return quantity must be greater than 0')
        
        return retqty


# Create formset for MRN details
# NOTE: Commented out due to foreign key relationship issues with managed=False models
# MRNDetailFormSet = inlineformset_factory(
#     TblinvMaterialreturnMaster,
#     TblinvMaterialreturnDetails,
#     form=MRNDetailForm,
#     extra=1,
#     can_delete=True,
#     min_num=1,
#     validate_min=True
# )


class VehicleProcessMasterForm(forms.ModelForm):
    """
    Form for Vehicle Process Master
    
    Converted from: aspnet/Module/Inventory/Masters/Vehical_Master.aspx
    """
    class Meta:
        model = TblvehProcessMaster
        fields = ['vehicalname', 'vehicalno']
        widgets = {
            'vehicalname': forms.TextInput(attrs={'placeholder': 'Vehicle Name'}),
            'vehicalno': forms.TextInput(attrs={'placeholder': 'Vehicle Number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            })



class GINMasterForm(BaseTransactionForm):
    """Form for Goods Inward Note Master"""
    
    class Meta:
        model = TblinvInwardMaster
        fields = ['ginno', 'pono', 'pomid', 'challanno', 'challandate', 
                  'gateentryno', 'gdate', 'gtime', 'modeoftransport', 'vehicleno']
        widgets = {
            'ginno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 focus:outline-none'
            }),
            'pono': forms.TextInput(attrs={
                'placeholder': 'PO Number',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'pomid': forms.HiddenInput(),
            'challanno': forms.TextInput(attrs={
                'placeholder': 'Challan Number',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'challandate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'gateentryno': forms.TextInput(attrs={
                'placeholder': 'Gate Entry Number',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'gdate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'gtime': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'modeoftransport': forms.TextInput(attrs={
                'placeholder': 'Mode of Transport',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'vehicleno': forms.TextInput(attrs={
                'placeholder': 'Vehicle Number',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()
        
        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid
        
        if commit:
            instance.save()
        
        return instance


class GINDetailForm(forms.ModelForm):
    """Form for Goods Inward Note Details"""
    
    # Additional fields for display
    item_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    item_description = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = TblinvInwardDetails
        fields = ['ginno', 'ginid', 'poid', 'qty', 'receivedqty', 'acategoyid', 'asubcategoyid']
        widgets = {
            'ginno': forms.HiddenInput(),
            'ginid': forms.HiddenInput(),
            'poid': forms.HiddenInput(),
            'qty': forms.NumberInput(attrs={'placeholder': 'Inward Quantity', 'step': '0.001'}),
            'receivedqty': forms.NumberInput(attrs={'placeholder': 'Received Quantity', 'step': '0.001', 'readonly': 'readonly'}),
            'acategoyid': forms.HiddenInput(),
            'asubcategoyid': forms.HiddenInput(),
        }
    
    def clean_qty(self):
        qty = self.cleaned_data.get('qty')
        
        if qty and qty <= 0:
            raise forms.ValidationError('Inward quantity must be greater than 0')
        
        return qty


# Create formset for GIN details
# NOTE: Commented out due to foreign key relationship issues with managed=False models
# GINDetailFormSet = inlineformset_factory(
#     TblinvInwardMaster,
#     TblinvInwardDetails,
#     form=GINDetailForm,
#     extra=1,
#     can_delete=True,
#     min_num=1,
#     validate_min=True
# )


class GRRMasterForm(BaseTransactionForm):
    """Form for Goods Received Receipt Master"""
    
    class Meta:
        model = TblinvMaterialreceivedMaster
        fields = ['grrno', 'ginno', 'ginid', 'taxinvoiceno', 'taxinvoicedate', 
                  'modvatapp', 'modvatinv']
        widgets = {
            'grrno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 focus:outline-none'
            }),
            'ginno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 focus:outline-none'
            }),
            'ginid': forms.HiddenInput(),
            'taxinvoiceno': forms.TextInput(attrs={
                'placeholder': 'Tax Invoice Number',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'taxinvoicedate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500'
            }),
            'modvatapp': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded'
            }),
            'modvatinv': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded'
            }),
        }
        labels = {
            'modvatapp': 'Modified VAT Applicable',
            'modvatinv': 'Modified VAT Invoice',
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()
        
        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid
        
        if commit:
            instance.save()
        
        return instance


class GRRDetailForm(forms.ModelForm):
    """Form for Goods Received Receipt Details"""
    
    # Additional fields for display
    item_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    item_description = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    inward_qty = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    balance_qty = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = TblinvMaterialreceivedDetails
        fields = ['poid', 'receivedqty']
        widgets = {
            'poid': forms.HiddenInput(),
            'receivedqty': forms.NumberInput(attrs={'placeholder': 'Received Quantity', 'step': '0.001'}),
        }
    
    def clean_receivedqty(self):
        receivedqty = self.cleaned_data.get('receivedqty')
        
        if receivedqty and receivedqty <= 0:
            raise forms.ValidationError('Received quantity must be greater than 0')
        
        return receivedqty


# Create formset for GRR details
# NOTE: Commented out due to foreign key relationship issues with managed=False models
# GRRDetailFormSet = inlineformset_factory(
#     TblinvMaterialreceivedMaster,
#     TblinvMaterialreceivedDetails,
#     form=GRRDetailForm,
#     extra=0,
#     can_delete=False,
#     min_num=1,
#     validate_min=True
# )



class GSNMasterForm(BaseTransactionForm):
    """
    Form for Goods Service Note Master
    
    Converted from: aspnet/Module/Inventory/Transactions/GoodsServiceNote_SN_New.aspx
    """
    
    # Additional fields not in model (will be handled separately)
    service_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter service description',
            'rows': 3,
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
        }),
        label='Service Description'
    )
    service_provider = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Service provider name',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
        }),
        label='Service Provider'
    )
    service_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Service amount',
            'step': '0.01',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
        }),
        label='Service Amount'
    )
    tax_rate = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Tax rate (%)',
            'step': '0.01',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
        }),
        label='Tax Rate (%)'
    )
    tax_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Tax amount (auto-calculated)',
            'step': '0.01',
            'readonly': 'readonly',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50'
        }),
        label='Tax Amount'
    )
    total_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Total amount (auto-calculated)',
            'step': '0.01',
            'readonly': 'readonly',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50'
        }),
        label='Total Amount'
    )
    
    class Meta:
        model = TblinvMaterialservicenoteMaster
        fields = ['gsnno', 'ginno', 'taxinvoiceno', 'taxinvoicedate']
        widgets = {
            'gsnno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50'
            }),
            'ginno': forms.TextInput(attrs={
                'placeholder': 'GIN Number (if applicable)',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
            }),
            'taxinvoiceno': forms.TextInput(attrs={
                'placeholder': 'Tax invoice number',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
            }),
            'taxinvoicedate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
            }),
        }
        labels = {
            'gsnno': 'GSN Number',
            'ginno': 'GIN Number',
            'taxinvoiceno': 'Tax Invoice Number',
            'taxinvoicedate': 'Tax Invoice Date',
        }
    
    def clean_service_amount(self):
        """Validate service amount"""
        service_amount = self.cleaned_data.get('service_amount')
        
        if service_amount and service_amount <= 0:
            raise forms.ValidationError('Service amount must be greater than 0')
        
        return service_amount
    
    def clean(self):
        """Cross-field validation and auto-calculation"""
        cleaned_data = super().clean()
        
        service_amount = cleaned_data.get('service_amount')
        tax_rate = cleaned_data.get('tax_rate', 0)
        
        if service_amount and tax_rate:
            # Auto-calculate tax amount
            from .services import GoodsServiceService
            tax_amount = GoodsServiceService.calculate_tax(service_amount, tax_rate)
            cleaned_data['tax_amount'] = tax_amount
            
            # Auto-calculate total amount
            total_amount = GoodsServiceService.calculate_total_amount(service_amount, tax_amount)
            cleaned_data['total_amount'] = total_amount
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()
        
        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid
        
        if commit:
            instance.save()
        
        return instance



# ============================================================================
# CHALLAN FORMS
# ============================================================================

# NOTE: Schema verified - matches database (scno, transpoter, etc.)
class SupplierChallanMasterForm(BaseTransactionForm):
    """
    Form for Supplier Challan Master

    Handles job work tracking - materials sent to suppliers for processing.
    Converted from: aspnet/Module/Inventory/Transactions/SupplierChallan_New.aspx
    """

    class Meta:
        model = TblinvSupplierChallanMaster
        fields = [
            'scno', 'supplierid', 'vehicleno', 'transpoter', 'remarks'
        ]
        widgets = {
            'scno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50'
            }),
            'supplierid': forms.TextInput(attrs={
                'placeholder': 'Supplier ID',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'vehicleno': forms.TextInput(attrs={
                'placeholder': 'Vehicle number',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'transpoter': forms.TextInput(attrs={
                'placeholder': 'Transporter name',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'remarks': forms.Textarea(attrs={
                'placeholder': 'Additional remarks',
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
        }
        labels = {
            'scno': 'Challan Number',
            'supplierid': 'Supplier',
            'vehicleno': 'Vehicle Number',
            'transpoter': 'Transporter',
            'remarks': 'Remarks',
        }

    def clean_supplierid(self):
        """Validate supplier is selected"""
        supplierid = self.cleaned_data.get('supplierid')

        if not supplierid:
            raise forms.ValidationError('Supplier is required')

        return supplierid

    def save(self, commit=True):
        instance = super().save(commit=False)

        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()

        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid

        if commit:
            instance.save()

        return instance


# NOTE: Schema verified - matches database (prdid, challanqty)
class SupplierChallanDetailForm(forms.ModelForm):
    """
    Form for Supplier Challan Detail (line items)
    """

    class Meta:
        model = TblinvSupplierChallanDetails
        fields = ['prdid', 'challanqty']
        widgets = {
            'prdid': forms.NumberInput(attrs={
                'placeholder': 'Product ID',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'challanqty': forms.NumberInput(attrs={
                'placeholder': 'Quantity',
                'step': '0.001',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
        }
        labels = {
            'prdid': 'Product ID',
            'challanqty': 'Quantity',
        }

    def clean_challanqty(self):
        """Validate quantity"""
        challanqty = self.cleaned_data.get('challanqty')

        if challanqty and challanqty <= 0:
            raise forms.ValidationError('Quantity must be greater than 0')

        return challanqty


# Formset for Supplier Challan Details
# NOTE: Commented out due to foreign key relationship issues with managed=False models
# SupplierChallanDetailFormSet = forms.inlineformset_factory(
#     Tblsupplierchallanmaster,
#     Tblsupplierchallandetail,
#     form=SupplierChallanDetailForm,
#     extra=5,
#     can_delete=True,
#     min_num=1,
#     validate_min=True
# )


# NOTE: Commented out due to schema mismatch - see FORMS_SCHEMA_MISMATCH.md
# class SupplierChallanClearForm(forms.Form):
#     """
#     Form for clearing supplier challan (recording received quantities)
#     """
    
#     def __init__(self, *args, challan_details=None, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         if challan_details:
#             for detail in challan_details:
#                 field_name = f'received_qty_{detail.supplierchallandetailid}'
#                 self.fields[field_name] = forms.DecimalField(
#                     required=False,
#                     initial=0,
#                     max_digits=18,
#                     decimal_places=3,
#                     widget=forms.NumberInput(attrs={
#                         'placeholder': 'Received qty',
#                         'step': '0.001',
#                         'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500'
#                     }),
#                     label=f'Received Qty for {detail.itemid.itemname if detail.itemid else "Item"}'
#                 )
    
#     def clean(self):
#         """Validate received quantities"""
#         cleaned_data = super().clean()
        
#         for field_name, value in cleaned_data.items():
#             if field_name.startswith('received_qty_') and value:
#                 if value < 0:
#                     raise forms.ValidationError(f'{field_name}: Received quantity cannot be negative')
        
#         return cleaned_data


# NOTE: Schema verified and fixed - uses ccno, wono (NOT customerchallanno, wonumber)
class CustomerChallanMasterForm(BaseTransactionForm):
    """
    Form for Customer Challan Master

    Handles materials sent to customers for delivery or work order fulfillment.
    Converted from: aspnet/Module/Inventory/Transactions/CustomerChallan_New.aspx
    """

    class Meta:
        model = TblinvCustomerChallanMaster
        fields = [
            'ccno', 'customerid', 'wono'
        ]
        widgets = {
            'ccno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50'
            }),
            'customerid': forms.TextInput(attrs={
                'placeholder': 'Customer ID',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'wono': forms.TextInput(attrs={
                'placeholder': 'Work order number (optional)',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
        }
        labels = {
            'ccno': 'Challan Number',
            'customerid': 'Customer',
            'wono': 'Work Order Number',
        }

    def clean_customerid(self):
        """Validate customer is selected"""
        customerid = self.cleaned_data.get('customerid')

        if not customerid:
            raise forms.ValidationError('Customer is required')

        return customerid

    def save(self, commit=True):
        instance = super().save(commit=False)

        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()

        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid

        if commit:
            instance.save()

        return instance


# NOTE: Schema verified and fixed - uses challanqty (NOT qty), no remarks field
class CustomerChallanDetailForm(forms.ModelForm):
    """
    Form for Customer Challan Detail (line items)
    """

    class Meta:
        model = TblinvCustomerChallanDetails
        fields = ['itemid', 'challanqty']
        widgets = {
            'itemid': forms.NumberInput(attrs={
                'placeholder': 'Item ID',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
            'challanqty': forms.NumberInput(attrs={
                'placeholder': 'Quantity',
                'step': '0.001',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500'
            }),
        }
        labels = {
            'itemid': 'Item',
            'challanqty': 'Quantity',
        }

    def clean_challanqty(self):
        """Validate quantity"""
        challanqty = self.cleaned_data.get('challanqty')

        if challanqty and challanqty <= 0:
            raise forms.ValidationError('Quantity must be greater than 0')

        return challanqty


# Formset for Customer Challan Details
# NOTE: Commented out due to foreign key relationship issues with managed=False models
# CustomerChallanDetailFormSet = forms.inlineformset_factory(
#     Tblcustomerchallanmaster,
#     Tblcustomerchallandetail,
#     form=CustomerChallanDetailForm,
#     extra=5,
#     can_delete=True,
#     min_num=1,
#     validate_min=True
# )



# ============================================================================
# GATE PASS FORMS
# ============================================================================

class GatePassForm(forms.ModelForm):
    """
    Form for Gate Pass (Flat Table Structure)

    Database: tbl_Gatepass (single flat table, not Master/Detail split)
    Handles material movement authorization - outgoing and return tracking.
    Converted from: aspnet/Module/Inventory/Transactions/GatePass_Insert.aspx
    """

    class Meta:
        model = TblGatepass
        fields = [
            'srno', 'chalanno', 'date', 'wono', 'des_name',
            'codeno', 'description', 'unit', 'qty', 'total_qty',
            'issueto', 'athoriseby', 'rec_date', 'qty_recd',
            'qty_pend', 'recdby', 'remark'
        ]
        widgets = {
            'srno': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Serial number'
            }),
            'chalanno': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Challan number'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Work order number'
            }),
            'des_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Destination name'
            }),
            'codeno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Code number'
            }),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Item description'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Unit of measure'
            }),
            'qty': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Quantity'
            }),
            'total_qty': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Total quantity'
            }),
            'issueto': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Issued to'
            }),
            'athoriseby': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Authorized by'
            }),
            'rec_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'qty_recd': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Quantity received'
            }),
            'qty_pend': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Quantity pending'
            }),
            'recdby': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Received by'
            }),
            'remark': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Remarks'
            }),
        }
        labels = {
            'srno': 'Serial Number',
            'chalanno': 'Challan Number',
            'date': 'Date',
            'wono': 'Work Order Number',
            'des_name': 'Destination Name',
            'codeno': 'Code Number',
            'description': 'Description',
            'unit': 'Unit',
            'qty': 'Quantity',
            'total_qty': 'Total Quantity',
            'issueto': 'Issue To',
            'athoriseby': 'Authorized By',
            'rec_date': 'Received Date',
            'qty_recd': 'Quantity Received',
            'qty_pend': 'Quantity Pending',
            'recdby': 'Received By',
            'remark': 'Remark',
        }


# ============================================================================
# VEHICLE FORMS
# ============================================================================

# NOTE: Commented out due to schema mismatch - see FORMS_SCHEMA_MISMATCH.md
# class VehicleMasterForm(forms.ModelForm):
#     """
#     Form for Vehicle Master
    
#     Converted from: aspnet/Module/Inventory/Masters/Vehical_Master.aspx
#     """
    
#     OWNER_TYPE_CHOICES = [
#         ('Company', 'Company Owned'),
#         ('Hired', 'Hired'),
#     ]
    
#     ownertype = forms.ChoiceField(
#         choices=OWNER_TYPE_CHOICES,
#         widget=forms.Select(attrs={
#             'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#         }),
#         label='Owner Type'
#     )
    
#     class Meta:
#         model = Tblvehiclemaster
#         fields = [
#             'vehicleno', 'vehiclename', 'ownertype', 'ownername',
#             'registrationno', 'model', 'capacity', 'remarks'
#         ]
#         widgets = {
#             'vehicleno': forms.TextInput(attrs={
#                 'placeholder': 'Vehicle number',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'vehiclename': forms.TextInput(attrs={
#                 'placeholder': 'Vehicle name/description',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'ownername': forms.TextInput(attrs={
#                 'placeholder': 'Owner name',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'registrationno': forms.TextInput(attrs={
#                 'placeholder': 'Registration number',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'model': forms.TextInput(attrs={
#                 'placeholder': 'Vehicle model',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'capacity': forms.TextInput(attrs={
#                 'placeholder': 'Capacity (e.g., 5 tons)',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'remarks': forms.Textarea(attrs={
#                 'placeholder': 'Additional remarks',
#                 'rows': 3,
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#         }


# NOTE: Commented out due to schema mismatch - see FORMS_SCHEMA_MISMATCH.md
# class VehicleTripForm(forms.ModelForm):
#     """Form for recording vehicle trips"""
    
#     class Meta:
#         model = Tblvehicletrip
#         fields = [
#             'tripdate', 'startingkm', 'endingkm', 'distance',
#             'fuelconsumed', 'fuelefficiency', 'drivername', 'purpose', 'remarks'
#         ]
#         widgets = {
#             'tripdate': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'startingkm': forms.NumberInput(attrs={
#                 'placeholder': 'Starting KM',
#                 'step': '0.01',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'endingkm': forms.NumberInput(attrs={
#                 'placeholder': 'Ending KM',
#                 'step': '0.01',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'distance': forms.NumberInput(attrs={
#                 'placeholder': 'Distance (auto-calculated)',
#                 'step': '0.01',
#                 'readonly': 'readonly',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50'
#             }),
#             'fuelconsumed': forms.NumberInput(attrs={
#                 'placeholder': 'Fuel consumed (liters)',
#                 'step': '0.01',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'fuelefficiency': forms.NumberInput(attrs={
#                 'placeholder': 'KM/L (auto-calculated)',
#                 'step': '0.01',
#                 'readonly': 'readonly',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50'
#             }),
#             'drivername': forms.TextInput(attrs={
#                 'placeholder': 'Driver name',
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'purpose': forms.Textarea(attrs={
#                 'placeholder': 'Trip purpose',
#                 'rows': 2,
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#             'remarks': forms.Textarea(attrs={
#                 'placeholder': 'Additional remarks',
#                 'rows': 2,
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-700'
#             }),
#         }
    
#     def clean(self):
#         """Auto-calculate distance and fuel efficiency"""
#         cleaned_data = super().clean()
        
#         starting_km = cleaned_data.get('startingkm')
#         ending_km = cleaned_data.get('endingkm')
#         fuel_consumed = cleaned_data.get('fuelconsumed')
        
#         if starting_km and ending_km:
#             from .services import VehicleService
#             distance = VehicleService.calculate_distance(starting_km, ending_km)
#             cleaned_data['distance'] = distance
            
#             if fuel_consumed:
#                 efficiency = VehicleService.calculate_fuel_efficiency(distance, fuel_consumed)
#                 cleaned_data['fuelefficiency'] = efficiency
        
#         return cleaned_data


# ============================================================================
# WIS (WORK INSTRUCTION SHEET) FORMS
# ============================================================================

# NOTE: Schema verified and fixed - WIS Master is MINIMAL (only wisno, wono, audit fields)
# All quantity tracking is in WIS Details table, not Master
class WISMasterForm(BaseTransactionForm):
    """
    Form for WIS Master

    WIS Master is minimal - just links WIS number to Work Order.
    All material tracking is in WIS Details.

    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Material.aspx
    """

    class Meta:
        model = TblinvWisMaster
        fields = ['wisno', 'wono']
        widgets = {
            'wisno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'placeholder': 'Auto-generated',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50'
            }),
            'wono': forms.TextInput(attrs={
                'placeholder': 'Work order number',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500'
            }),
        }
        labels = {
            'wisno': 'WIS Number',
            'wono': 'Work Order Number',
        }

    def clean_wono(self):
        """Validate work order is provided"""
        wono = self.cleaned_data.get('wono')

        if not wono:
            raise forms.ValidationError('Work Order Number is required')

        return wono

    def save(self, commit=True):
        instance = super().save(commit=False)

        from .services import BaseTransactionService
        sysdate, systime = BaseTransactionService.get_current_datetime()

        instance.sysdate = sysdate
        instance.systime = systime
        instance.compid = self.compid
        instance.finyearid = self.finyearid
        instance.sessionid = self.sessionid

        if commit:
            instance.save()

        return instance


# NOTE: Schema verified and fixed - WIS Details only has wisno, pid, cid, itemid, issuedqty
# No requiredqty, actualqty, variance, or remarks fields exist
class WISDetailForm(forms.ModelForm):
    """
    Form for WIS Detail (material issued)

    WIS Details tracks issued quantities only.
    No "required" or "actual" quantities - just what was issued.
    """

    class Meta:
        model = TblinvWisDetails
        fields = ['wisno', 'pid', 'cid', 'itemid', 'issuedqty']
        widgets = {
            'wisno': forms.TextInput(attrs={
                'readonly': 'readonly',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded bg-gray-50'
            }),
            'pid': forms.NumberInput(attrs={
                'placeholder': 'Part ID',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-pink-500'
            }),
            'cid': forms.NumberInput(attrs={
                'placeholder': 'Category ID',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-pink-500'
            }),
            'itemid': forms.NumberInput(attrs={
                'placeholder': 'Item ID',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-pink-500'
            }),
            'issuedqty': forms.NumberInput(attrs={
                'placeholder': 'Issued quantity',
                'step': '0.001',
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-pink-500'
            }),
        }
        labels = {
            'wisno': 'WIS Number',
            'pid': 'Part ID',
            'cid': 'Category ID',
            'itemid': 'Item',
            'issuedqty': 'Issued Quantity',
        }

    def clean_issuedqty(self):
        """Validate issued quantity"""
        issuedqty = self.cleaned_data.get('issuedqty')

        if issuedqty and issuedqty <= 0:
            raise forms.ValidationError('Issued quantity must be greater than 0')

        return issuedqty


# NOTE: Commented out due to foreign key relationship issues with managed=False models
# WISDetailFormSet = forms.inlineformset_factory(
#     Tblwismaster,
#     Tblwisdetail,
#     form=WISDetailForm,
#     extra=5,
#     can_delete=True,
#     min_num=1,
#     validate_min=True
# )



# ============================================================================
# ITEM LOCATION FORMS
# ============================================================================

class ItemLocationForm(forms.ModelForm):
    """Form for Item Location Master - warehouse location management"""
    
    LOCATION_LABEL_CHOICES = [(chr(i), chr(i)) for i in range(65, 91)]  # A-Z
    
    locationlabel = forms.ChoiceField(
        choices=[('', 'Select')] + LOCATION_LABEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-slate-500 focus:ring-slate-500'
        }),
        label='Location Label'
    )
    
    class Meta:
        from design.models import TbldgLocationMaster
        model = TbldgLocationMaster
        fields = ['locationlabel', 'locationno', 'description']
        widgets = {
            'locationno': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-slate-500 focus:ring-slate-500',
                'placeholder': 'Enter location number'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-slate-500 focus:ring-slate-500',
                'rows': 3,
                'placeholder': 'Enter location description'
            })
        }
        labels = {
            'locationno': 'Location Number',
            'description': 'Description'
        }
#             'itemid': forms.Select(attrs={
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500'
#             }),
#             'locationid': forms.Select(attrs={
#                 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500'
#             }),
#             'isprimary': forms.CheckboxInput(attrs={
#                 'class': 'w-4 h-4 text-slate-600 border-gray-300 rounded focus:ring-2 focus:ring-slate-500'
#             }),
#         }
#         labels = {
#             'itemid': 'Item',
#             'locationid': 'Location',
#             'isprimary': 'Primary Location',
#         }


# ============================================================================
# CLOSING STOCK FORMS
# ============================================================================

# NOTE: Commented out due to schema mismatch - see FORMS_SCHEMA_MISMATCH.md
# class ClosingStockForm(forms.Form):
#     """Form for closing stock physical count entry"""
    
#     item = forms.ModelChoiceField(
#         queryset=None,
#         widget=forms.Select(attrs={
#             'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
#         }),
#         label='Item'
#     )
    
#     system_qty = forms.DecimalField(
#         disabled=True,
#         widget=forms.NumberInput(attrs={
#             'class': 'w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50',
#             'readonly': 'readonly'
#         }),
#         label='System Quantity'
#     )
    
#     physical_qty = forms.DecimalField(
#         max_digits=18,
#         decimal_places=3,
#         widget=forms.NumberInput(attrs={
#             'placeholder': 'Physical count',
#             'step': '0.001',
#             'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
#         }),
#         label='Physical Quantity'
#     )
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         from inventory.models import Tblitemmaster
#         self.fields['item'].queryset = Tblitemmaster.objects.all()



# ============================================================================
# AUTO WIS TIME SCHEDULE FORM
# ============================================================================

class StockLedgerFilterForm(forms.Form):
    """
    Form for filtering items for the Stock Ledger report.
    """
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    filter_type = forms.ChoiceField(choices=[('', 'Select'), ('Category', 'Category'), ('WOItems', 'WO Items')], required=False)
    category = forms.ChoiceField(required=False) # Populated dynamically
    search_by = forms.ChoiceField(choices=[('', 'Select'), ('ItemCode', 'Item Code'), ('ManfDesc', 'Description'), ('Location', 'Location')], required=False)
    search_term = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', None)
        super().__init__(*args, **kwargs)
        if categories:
            self.fields['category'].choices = [('', 'Select')] + list(categories)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            })


# ============================================================================
# AUTO WIS TIME SCHEDULE FORM
# ============================================================================

class AutoWISTimeScheduleForm(forms.ModelForm):
    """
    Form for Auto WIS Time Schedule
    Converted from: aspnet/Module/Inventory/Masters/AutoWIS_Time_Set.aspx
    """
    class Meta:
        model = TblinvAutowisTimeschedule
        fields = ['timeauto']
        widgets = {
            'timeauto': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            })
        }
        labels = {
            'timeauto': 'Scheduled Time'
        }


# ============================================================================
# VEHICLE MASTER FORM
# ============================================================================

class VehicleMasterForm(forms.ModelForm):
    """
    Form for Vehicle Master

    Manages vehicle information (name and number) for material transport tracking.
    Converted from: aaspnet/Module/Inventory/Masters/Vehical_Master.aspx

    Features: Inline GridView-style editing with Create/Edit/Delete operations
    Database: tblVeh_Process_Master
    """

    class Meta:
        model = TblvehProcessMaster
        fields = ['vehicalname', 'vehicalno']
        widgets = {
            'vehicalname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter vehicle name'
            }),
            'vehicalno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter vehicle number'
            }),
        }
        labels = {
            'vehicalname': 'Name of Vehicle',
            'vehicalno': 'Number',
        }
