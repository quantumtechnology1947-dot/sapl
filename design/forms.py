"""
Design Forms - Converted from ASP.NET Module/Design
All forms use ModelForm with Tailwind CSS styling.
"""

from django import forms
from .models import (
    TbldgCategoryMaster, TbldgSubcategoryMaster, TbldgItemMaster, 
    TbldgBomMaster, TbldgEcnMaster, TbldgEcnDetails, TbldgEcnReason
)
from sys_admin.models import UnitMaster


class DesignCategoryForm(forms.ModelForm):
    """
    Form for Design Category Master.
    Converted from: aspnet/Module/Design/Masters/CategoryNew.aspx
    """
    
    class Meta:
        model = TbldgCategoryMaster
        fields = ['cname', 'symbol', 'hassubcat']
        
        widgets = {
            'cname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter category name'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol'
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
        """Validate symbol is not empty."""
        symbol = self.cleaned_data.get('symbol')
        if not symbol or not symbol.strip():
            raise forms.ValidationError('Symbol is required.')
        return symbol.strip()


class DesignSubCategoryForm(forms.ModelForm):
    """
    Form for Design Sub-Category Master.
    Converted from: aspnet/Module/Design/Masters/SubCategoryNew.aspx
    """
    
    cid = forms.ModelChoiceField(
        queryset=TbldgCategoryMaster.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Category'
    )
    
    class Meta:
        model = TbldgSubcategoryMaster
        fields = ['cid', 'scname', 'symbol']
        
        widgets = {
            'scname': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter sub-category name'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter symbol'
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
        """Validate symbol is not empty."""
        symbol = self.cleaned_data.get('symbol')
        if not symbol or not symbol.strip():
            raise forms.ValidationError('Symbol is required.')
        return symbol.strip()



class ItemMasterForm(forms.ModelForm):
    """
    Form for Item Master.
    Converted from: aspnet/Module/Design/Masters/ItemMaster_New.aspx
    """
    
    cid = forms.ModelChoiceField(
        queryset=TbldgCategoryMaster.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'hx-get': '/design/subcategory/by-category/',
            'hx-target': '#id_scid',
            'hx-trigger': 'change'
        }),
        label='Category',
        required=True
    )
    
    scid = forms.ChoiceField(
        choices=[('', 'Select Sub-Category')],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'id': 'id_scid'
        }),
        label='Sub-Category',
        required=False
    )
    
    uombasic = forms.ModelChoiceField(
        queryset=UnitMaster.objects.all(),
        empty_label="Select Unit",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Unit of Measurement',
        required=True
    )

    # File upload fields (not part of model fields list)
    file_upload = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.dwg,.dxf,.jpg,.jpeg,.png'
        }),
        label='Attach Drawing/Document',
        help_text='Supported formats: PDF, DOC, DOCX, XLS, XLSX, DWG, DXF, JPG, PNG (Max 10MB)'
    )

    attachment_upload = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png'
        }),
        label='Attach Additional File',
        help_text='Optional additional attachment (Max 10MB)'
    )

    class Meta:
        model = TbldgItemMaster
        fields = [
            'itemcode', 'partno', 'manfdesc', 'cid', 'scid', 'uombasic',
            'minorderqty', 'minstockqty', 'stockqty', 'process', 'class_field',
            'leaddays', 'inspectiondays', 'location', 'absolute', 'openingbaldate',
            'openingbalqty', 'uomconfact', 'excise', 'importlocal', 'buyer', 'hsncode'
        ]
        
        widgets = {
            'itemcode': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter item code'
            }),
            'partno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter part number'
            }),
            'manfdesc': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter description',
                'rows': 3
            }),
            'minorderqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'minstockqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'stockqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'process': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'class_field': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'leaddays': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Lead days'
            }),
            'inspectiondays': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Inspection days'
            }),
            'location': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'absolute': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'openingbaldate': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'openingbalqty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'uomconfact': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'excise': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'importlocal': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'buyer': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'hsncode': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'HSN Code'
            }),
        }
        
        labels = {
            'itemcode': 'Item Code',
            'partno': 'Part Number',
            'manfdesc': 'Description',
            'minorderqty': 'Minimum Order Quantity',
            'minstockqty': 'Minimum Stock Quantity',
            'stockqty': 'Stock Quantity',
            'process': 'Process',
            'class_field': 'Class',
            'leaddays': 'Lead Days',
            'inspectiondays': 'Inspection Days',
            'location': 'Location',
            'absolute': 'Absolute',
            'openingbaldate': 'Opening Balance Date',
            'openingbalqty': 'Opening Balance Quantity',
            'uomconfact': 'UOM Conversion Factor',
            'excise': 'Excise',
            'importlocal': 'Import/Local',
            'buyer': 'Buyer',
            'hsncode': 'HSN Code',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing, populate sub-category choices
        if self.instance and self.instance.pk and self.instance.cid:
            subcategories = TbldgSubcategoryMaster.objects.filter(cid=self.instance.cid)
            self.fields['scid'].choices = [('', 'Select Sub-Category')] + [
                (sc.scid, sc.scname) for sc in subcategories
            ]
            if self.instance.cid:
                try:
                    self.fields['cid'].initial = TbldgCategoryMaster.objects.get(cid=self.instance.cid)
                except TbldgCategoryMaster.DoesNotExist:
                    pass
            if self.instance.uombasic:
                try:
                    self.fields['uombasic'].initial = UnitMaster.objects.get(id=self.instance.uombasic)
                except UnitMaster.DoesNotExist:
                    pass
    
    def clean_itemcode(self):
        """Validate item code uniqueness."""
        itemcode = self.cleaned_data.get('itemcode')
        if not itemcode or not itemcode.strip():
            raise forms.ValidationError('Item code is required.')
        
        # Check uniqueness
        qs = TbldgItemMaster.objects.filter(itemcode__iexact=itemcode)
        if self.instance and self.instance.pk:
            qs = qs.exclude(id=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError('Item code already exists.')
        
        return itemcode.strip()
    
    def clean_manfdesc(self):
        """Validate description is not empty."""
        manfdesc = self.cleaned_data.get('manfdesc')
        if not manfdesc or not manfdesc.strip():
            raise forms.ValidationError('Description is required.')
        return manfdesc.strip()

    def clean_file_upload(self):
        """Validate file upload size."""
        file = self.cleaned_data.get('file_upload')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 10MB.')
        return file

    def clean_attachment_upload(self):
        """Validate attachment upload size."""
        file = self.cleaned_data.get('attachment_upload')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 10MB.')
        return file
    
    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        
        # Convert ModelChoiceField to ID for cid
        if cleaned_data.get('cid'):
            cleaned_data['cid'] = cleaned_data['cid'].cid
        
        # Convert ModelChoiceField to ID for uombasic
        if cleaned_data.get('uombasic'):
            cleaned_data['uombasic'] = cleaned_data['uombasic'].id
        
        # Convert scid to integer if provided
        if cleaned_data.get('scid'):
            try:
                cleaned_data['scid'] = int(cleaned_data['scid'])
            except (ValueError, TypeError):
                cleaned_data['scid'] = None
        
        return cleaned_data



class BomMasterForm(forms.ModelForm):
    """
    Form for BOM Master.
    Converted from: aspnet/Module/Design/Transactions/BOM_Design_WO_TreeView.aspx

    NOTE: Uses dropdown for Work Order selection (not text input).
    Item selection limited to avoid rendering 92,880+ items.
    """
    from sales_distribution.models import SdCustWorkorderMaster

    wono = forms.ModelChoiceField(
        queryset=SdCustWorkorderMaster.objects.all().order_by('-wono')[:200],  # Recent 200 WOs
        empty_label="Select Work Order",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Work Order Number',
        required=True,
        help_text='Select an existing work order from Sales module',
        to_field_name='wono'  # Use wono field instead of primary key
    )

    itemid = forms.ModelChoiceField(
        queryset=TbldgItemMaster.objects.none(),  # Empty by default, populated in __init__
        empty_label="Select Item",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Item',
        required=True
    )
    
    class Meta:
        model = TbldgBomMaster
        fields = [
            'wono', 'equipmentno', 'unitno', 'partno', 'itemid', 
            'pid', 'cid', 'qty', 'revision', 'remark', 'material'
        ]
        
        widgets = {
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter work order number'
            }),
            'equipmentno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter equipment number'
            }),
            'unitno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter unit number'
            }),
            'partno': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter part number'
            }),
            'pid': forms.HiddenInput(),
            'cid': forms.HiddenInput(),
            'qty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'revision': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Revision'
            }),
            'remark': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter remarks',
                'rows': 3
            }),
            'material': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter material details',
                'rows': 2
            }),
        }
        
        labels = {
            'wono': 'Work Order Number',
            'equipmentno': 'Equipment Number',
            'unitno': 'Unit Number',
            'partno': 'Part Number',
            'qty': 'Quantity',
            'revision': 'Revision',
            'remark': 'Remarks',
            'material': 'Material',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make revision field optional
        self.fields['revision'].required = False

        # Limit queryset to avoid loading 92,880+ items
        # Option 1: If editing, show only the current item
        if self.instance and self.instance.pk and self.instance.itemid:
            self.fields['itemid'].queryset = TbldgItemMaster.objects.filter(
                id=self.instance.itemid.id
            )
            self.fields['itemid'].initial = self.instance.itemid
        else:
            # Option 2: For new BOM, show only 50 most recent items
            # User should use the Wizard interface for better item selection
            self.fields['itemid'].queryset = TbldgItemMaster.objects.all().order_by('-id')[:50]
            self.fields['itemid'].help_text = (
                'Showing 50 most recent items. '
                'For full search, use "Add Items Wizard" after creating root BOM.'
            )
    
    def clean_wono(self):
        """Validate work order selection."""
        wono = self.cleaned_data.get('wono')
        if not wono:
            raise forms.ValidationError('Please select a work order.')
        # Return the wono string value
        return wono.wono if hasattr(wono, 'wono') else str(wono)
    
    def clean_qty(self):
        """Validate quantity is positive."""
        qty = self.cleaned_data.get('qty')
        if qty is not None and qty <= 0:
            raise forms.ValidationError('Quantity must be greater than zero.')
        return qty
    
    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()

        # Convert work order object to wono string
        if cleaned_data.get('wono'):
            wo_obj = cleaned_data['wono']
            cleaned_data['wono'] = wo_obj.wono if hasattr(wo_obj, 'wono') else str(wo_obj)

        # Convert ModelChoiceField to ID for itemid
        if cleaned_data.get('itemid'):
            cleaned_data['itemid'] = cleaned_data['itemid'].id

        return cleaned_data


# DEPRECATED: BomItemForm removed - no longer needed
# The new BomAddChildView handles forms directly in the template without a separate form class.
# This approach is more flexible for the tabbed interface.
# Old code was at lines 468-512 in this file.



class EcnMasterForm(forms.ModelForm):
    """
    Form for ECN Master.
    Converted from: aspnet/Module/Design/Transactions/ECN_Master.aspx
    """
    
    ecnreason = forms.ModelChoiceField(
        queryset=TbldgEcnReason.objects.all(),
        empty_label="Select ECN Reason",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='ECN Reason',
        required=True
    )
    
    class Meta:
        model = TbldgEcnMaster
        fields = ['wono', 'itemid', 'pid', 'cid']
        
        widgets = {
            'wono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter work order number'
            }),
            'itemid': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'pid': forms.HiddenInput(),
            'cid': forms.HiddenInput(),
        }
        
        labels = {
            'wono': 'Work Order Number',
            'itemid': 'Item ID',
        }
    
    def clean_wono(self):
        """Validate work order number exists in BOM."""
        wono = self.cleaned_data.get('wono')
        if wono:
            # Check if work order exists in BOM
            if not TbldgBomMaster.objects.filter(wono=wono).exists():
                raise forms.ValidationError('Work order not found in BOM.')
        return wono


class EcnDetailsForm(forms.ModelForm):
    """
    Form for ECN Details (reasons and remarks).
    Converted from: aspnet/Module/Design/Transactions/ECN_Master_Edit.aspx
    """
    
    ecnreason = forms.ModelChoiceField(
        queryset=TbldgEcnReason.objects.all(),
        empty_label="Select Reason",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='ECN Reason',
        required=True
    )
    
    class Meta:
        model = TbldgEcnDetails
        fields = ['ecnreason', 'remarks']
        
        widgets = {
            'remarks': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter detailed remarks about the change',
                'rows': 4
            }),
        }
        
        labels = {
            'remarks': 'Remarks',
        }
    
    def clean_remarks(self):
        """Validate remarks is not empty."""
        remarks = self.cleaned_data.get('remarks')
        if not remarks or not remarks.strip():
            raise forms.ValidationError('Remarks are required.')
        return remarks.strip()


class BomAddAssemblyForm(forms.Form):
    """
    Form for adding a root assembly to BOM using HTMX autocomplete.
    Uses item search instead of limited dropdown to handle large item catalog.
    """
    # Hidden field to store selected item ID
    itemid = forms.IntegerField(
        widget=forms.HiddenInput(attrs={
            'id': 'selected-item-id'
        }),
        required=True,
        error_messages={
            'required': 'Please search and select an item from the item master.'
        }
    )

    # Search field for item lookup (not saved to model)
    item_search = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sap-blue',
            'placeholder': 'Type item name or description (e.g., "Motor", "Bearing", "Assembly")...',
            'autocomplete': 'off',
            'hx-get': '/design/api/search-items/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#item-search-results',
            'hx-indicator': '#search-spinner'
        }),
        label='Search Item by Name',
        required=False
    )

    qty = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        initial=1.000,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sap-blue',
            'step': '0.001',
            'min': '0.001'
        }),
        label='Quantity',
        help_text='Quantity of this assembly'
    )

    revision = forms.CharField(
        max_length=50,
        initial='0',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sap-blue',
            'placeholder': '0'
        }),
        label='Revision',
        required=False
    )

    remark = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sap-blue',
            'placeholder': 'Enter any remarks or notes',
            'rows': 3
        }),
        label='Remarks',
        required=False
    )

    def clean_itemid(self):
        """Validate that the item ID exists in the database."""
        item_id = self.cleaned_data.get('itemid')
        if not item_id:
            raise forms.ValidationError('Please search and select an item.')

        try:
            item = TbldgItemMaster.objects.get(id=item_id)
            return item
        except TbldgItemMaster.DoesNotExist:
            raise forms.ValidationError('Selected item does not exist. Please select a valid item.')


class BomAddChildItemForm(forms.Form):
    """
    Form for adding a child item under an existing assembly.
    Used in Phase 3 implementation for the add items wizard.

    NOTE: itemid queryset limited to avoid rendering 92,880+ options.
    """
    itemid = forms.ModelChoiceField(
        queryset=TbldgItemMaster.objects.all().order_by('-id')[:100],  # Limit to 100 recent items
        empty_label="Select Item",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Select Item',
        required=True,
        help_text='Showing 100 most recent items. Use search tabs for full catalog.'
    )

    qty = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        initial=1.000,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'step': '0.001',
            'min': '0.001'
        }),
        label='Required Quantity',
        help_text='Quantity needed per parent assembly'
    )

    remark = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter any remarks or notes',
            'rows': 2
        }),
        label='Remarks',
        required=False
    )
