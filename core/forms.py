"""
Core Form Classes

Base form classes with Tailwind CSS styling for consistent UI.
Requirements: 3.2, 3.3, 10.4, 11.1
"""

from django import forms
from django.core.exceptions import ValidationError


# Tailwind CSS classes for form elements
TAILWIND_INPUT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
TAILWIND_SELECT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
TAILWIND_TEXTAREA_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
TAILWIND_CHECKBOX_CLASSES = 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
TAILWIND_RADIO_CLASSES = 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300'
TAILWIND_FILE_CLASSES = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'


class BaseForm(forms.Form):
    """
    Base form with Tailwind CSS styling.
    
    Automatically applies Tailwind classes to all form fields.
    Requirements: 10.4, 11.1
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind_classes()
    
    def _apply_tailwind_classes(self):
        """Apply Tailwind CSS classes to all fields"""
        for field_name, field in self.fields.items():
            widget = field.widget
            
            # Get existing classes
            existing_classes = widget.attrs.get('class', '')
            
            # Apply appropriate Tailwind classes based on widget type
            if isinstance(widget, forms.TextInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
            
            elif isinstance(widget, forms.EmailInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
            
            elif isinstance(widget, forms.NumberInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
            
            elif isinstance(widget, forms.DateInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
                widget.attrs['type'] = 'date'
            
            elif isinstance(widget, forms.TimeInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
                widget.attrs['type'] = 'time'
            
            elif isinstance(widget, forms.DateTimeInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
                widget.attrs['type'] = 'datetime-local'
            
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_SELECT_CLASSES}'.strip()
            
            elif isinstance(widget, forms.Textarea):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_TEXTAREA_CLASSES}'.strip()
                if 'rows' not in widget.attrs:
                    widget.attrs['rows'] = 3
            
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_CHECKBOX_CLASSES}'.strip()
            
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_RADIO_CLASSES}'.strip()
            
            elif isinstance(widget, forms.FileInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_FILE_CLASSES}'.strip()
            
            # Add placeholder if field has help_text
            if field.help_text and isinstance(widget, (forms.TextInput, forms.EmailInput, forms.NumberInput)):
                widget.attrs['placeholder'] = field.help_text


class BaseModelForm(forms.ModelForm):
    """
    Base ModelForm with Tailwind CSS styling.
    
    Automatically applies Tailwind classes to all form fields.
    Requirements: 3.2, 3.3, 10.4, 11.1
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tailwind_classes()
    
    def _apply_tailwind_classes(self):
        """Apply Tailwind CSS classes to all fields"""
        for field_name, field in self.fields.items():
            widget = field.widget
            
            # Get existing classes
            existing_classes = widget.attrs.get('class', '')
            
            # Apply appropriate Tailwind classes based on widget type
            if isinstance(widget, forms.TextInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
            
            elif isinstance(widget, forms.EmailInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
            
            elif isinstance(widget, forms.NumberInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
            
            elif isinstance(widget, forms.DateInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
                widget.attrs['type'] = 'date'
            
            elif isinstance(widget, forms.TimeInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
                widget.attrs['type'] = 'time'
            
            elif isinstance(widget, forms.DateTimeInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_INPUT_CLASSES}'.strip()
                widget.attrs['type'] = 'datetime-local'
            
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_SELECT_CLASSES}'.strip()
            
            elif isinstance(widget, forms.Textarea):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_TEXTAREA_CLASSES}'.strip()
                if 'rows' not in widget.attrs:
                    widget.attrs['rows'] = 3
            
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_CHECKBOX_CLASSES}'.strip()
            
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_RADIO_CLASSES}'.strip()
            
            elif isinstance(widget, forms.FileInput):
                widget.attrs['class'] = f'{existing_classes} {TAILWIND_FILE_CLASSES}'.strip()
            
            # Add placeholder if field has help_text
            if field.help_text and isinstance(widget, (forms.TextInput, forms.EmailInput, forms.NumberInput)):
                widget.attrs['placeholder'] = field.help_text


class BaseSearchForm(BaseForm):
    """
    Base search form with common search field.
    
    Requirements: 3.2
    """
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search...',
            'hx-get': '',  # Set by view
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#results',
            'hx-indicator': '#search-indicator',
        })
    )


class BaseFilterForm(BaseForm):
    """
    Base filter form for list views.
    
    Requirements: 3.2
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add HTMX attributes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'hx-get': '',  # Set by view
                'hx-trigger': 'change',
                'hx-target': '#results',
            })


class DateRangeForm(BaseForm):
    """
    Form for date range filtering.
    
    Requirements: 3.2
    """
    
    date_from = forms.DateField(
        required=False,
        label='From Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    date_to = forms.DateField(
        required=False,
        label='To Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def clean(self):
        """Validate date range"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError('From date must be before to date')
        
        return cleaned_data


# Common field widgets with Tailwind styling
class TailwindTextInput(forms.TextInput):
    """TextInput with Tailwind classes"""
    def __init__(self, attrs=None):
        default_attrs = {'class': TAILWIND_INPUT_CLASSES}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindEmailInput(forms.EmailInput):
    """EmailInput with Tailwind classes"""
    def __init__(self, attrs=None):
        default_attrs = {'class': TAILWIND_INPUT_CLASSES}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindNumberInput(forms.NumberInput):
    """NumberInput with Tailwind classes"""
    def __init__(self, attrs=None):
        default_attrs = {'class': TAILWIND_INPUT_CLASSES}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindSelect(forms.Select):
    """Select with Tailwind classes"""
    def __init__(self, attrs=None, choices=()):
        default_attrs = {'class': TAILWIND_SELECT_CLASSES}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices)


class TailwindTextarea(forms.Textarea):
    """Textarea with Tailwind classes"""
    def __init__(self, attrs=None):
        default_attrs = {'class': TAILWIND_TEXTAREA_CLASSES, 'rows': 3}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindCheckboxInput(forms.CheckboxInput):
    """CheckboxInput with Tailwind classes"""
    def __init__(self, attrs=None):
        default_attrs = {'class': TAILWIND_CHECKBOX_CLASSES}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindDateInput(forms.DateInput):
    """DateInput with Tailwind classes"""
    def __init__(self, attrs=None):
        default_attrs = {'class': TAILWIND_INPUT_CLASSES, 'type': 'date'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindTimeInput(forms.TimeInput):
    """TimeInput with Tailwind classes"""
    def __init__(self, attrs=None):
        default_attrs = {'class': TAILWIND_INPUT_CLASSES, 'type': 'time'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindFileInput(forms.FileInput):
    """FileInput with Tailwind classes"""
    def __init__(self, attrs=None):
        default_attrs = {'class': TAILWIND_FILE_CLASSES}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    