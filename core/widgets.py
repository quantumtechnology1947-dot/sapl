"""
Reusable form widgets with Tailwind CSS styling
Provides consistent, SAP-themed form widgets across all modules
"""
from django import forms
from django.forms import widgets


# Base Tailwind CSS classes for form inputs
BASE_INPUT_CLASSES = (
    'w-full px-3 py-2 border border-gray-300 rounded-md '
    'focus:outline-none focus:ring-2 focus:ring-sap-blue focus:border-transparent '
    'transition duration-150 ease-in-out'
)

ERROR_INPUT_CLASSES = 'border-red-500 focus:ring-red-500'
DISABLED_INPUT_CLASSES = 'bg-gray-100 cursor-not-allowed'


class TailwindTextInput(forms.TextInput):
    """Text input with Tailwind CSS styling"""

    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': BASE_INPUT_CLASSES}
        if attrs:
            default_attrs.update(attrs)
            # Merge class attributes if both exist
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} {attrs['class']}"
        super().__init__(attrs=default_attrs, **kwargs)


class TailwindEmailInput(forms.EmailInput):
    """Email input with Tailwind CSS styling"""

    def __init__(self, attrs=None, **kwargs):
        default_attrs = {
            'class': BASE_INPUT_CLASSES,
            'type': 'email',
            'placeholder': 'name@company.com'
        }
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} {attrs['class']}"
        super().__init__(attrs=default_attrs, **kwargs)


class TailwindNumberInput(forms.NumberInput):
    """Number input with Tailwind CSS styling"""

    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': BASE_INPUT_CLASSES}
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} {attrs['class']}"
        super().__init__(attrs=default_attrs, **kwargs)


class TailwindPasswordInput(forms.PasswordInput):
    """Password input with Tailwind CSS styling"""

    def __init__(self, attrs=None, **kwargs):
        default_attrs = {
            'class': BASE_INPUT_CLASSES,
            'placeholder': '••••••••'
        }
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} {attrs['class']}"
        super().__init__(attrs=default_attrs, **kwargs)


class TailwindTextarea(forms.Textarea):
    """Textarea with Tailwind CSS styling"""

    def __init__(self, attrs=None, **kwargs):
        default_attrs = {
            'class': f"{BASE_INPUT_CLASSES} min-h-[100px]",
            'rows': 4
        }
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} min-h-[100px] {attrs['class']}"
        super().__init__(attrs=default_attrs, **kwargs)


class TailwindSelect(forms.Select):
    """Select dropdown with Tailwind CSS styling"""

    def __init__(self, attrs=None, choices=(), **kwargs):
        default_attrs = {
            'class': f"{BASE_INPUT_CLASSES} cursor-pointer"
        }
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} cursor-pointer {attrs['class']}"
        super().__init__(attrs=default_attrs, choices=choices, **kwargs)


class TailwindSelectMultiple(forms.SelectMultiple):
    """Multiple select with Tailwind CSS styling"""

    def __init__(self, attrs=None, choices=(), **kwargs):
        default_attrs = {
            'class': f"{BASE_INPUT_CLASSES} min-h-[150px]",
            'size': 6
        }
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} min-h-[150px] {attrs['class']}"
        super().__init__(attrs=default_attrs, choices=choices, **kwargs)


class TailwindCheckboxInput(forms.CheckboxInput):
    """Checkbox with Tailwind CSS styling"""

    def __init__(self, attrs=None, **kwargs):
        default_attrs = {
            'class': (
                'h-4 w-4 text-sap-blue border-gray-300 rounded '
                'focus:ring-2 focus:ring-sap-blue cursor-pointer'
            )
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class TailwindCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """Multiple checkboxes with Tailwind CSS styling"""

    def __init__(self, attrs=None, choices=(), **kwargs):
        default_attrs = {
            'class': (
                'h-4 w-4 text-sap-blue border-gray-300 rounded '
                'focus:ring-2 focus:ring-sap-blue cursor-pointer'
            )
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices, **kwargs)


class TailwindRadioSelect(forms.RadioSelect):
    """Radio buttons with Tailwind CSS styling"""

    def __init__(self, attrs=None, choices=(), **kwargs):
        default_attrs = {
            'class': (
                'h-4 w-4 text-sap-blue border-gray-300 '
                'focus:ring-2 focus:ring-sap-blue cursor-pointer'
            )
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices, **kwargs)


class TailwindDateInput(forms.DateInput):
    """Date input with Tailwind CSS styling (compatible with Flatpickr)"""

    def __init__(self, attrs=None, format='%d-%m-%Y', **kwargs):
        default_attrs = {
            'class': BASE_INPUT_CLASSES,
            'type': 'text',
            'placeholder': 'dd-mm-yyyy',
            'data-date-picker': 'true'
        }
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} {attrs['class']}"
        super().__init__(attrs=default_attrs, format=format, **kwargs)


class TailwindTimeInput(forms.TimeInput):
    """Time input with Tailwind CSS styling"""

    def __init__(self, attrs=None, format='%H:%M:%S', **kwargs):
        default_attrs = {
            'class': BASE_INPUT_CLASSES,
            'type': 'time'
        }
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} {attrs['class']}"
        super().__init__(attrs=default_attrs, format=format, **kwargs)


class TailwindDateTimeInput(forms.DateTimeInput):
    """DateTime input with Tailwind CSS styling (compatible with Flatpickr)"""

    def __init__(self, attrs=None, format='%d-%m-%Y %H:%M:%S', **kwargs):
        default_attrs = {
            'class': BASE_INPUT_CLASSES,
            'type': 'text',
            'placeholder': 'dd-mm-yyyy HH:MM:SS',
            'data-date-picker': 'true',
            'data-enable-time': 'true'
        }
        if attrs:
            default_attrs.update(attrs)
            if 'class' in attrs:
                default_attrs['class'] = f"{BASE_INPUT_CLASSES} {attrs['class']}"
        super().__init__(attrs=default_attrs, format=format, **kwargs)


class TailwindFileInput(forms.FileInput):
    """File input with Tailwind CSS styling"""

    def __init__(self, attrs=None, **kwargs):
        default_attrs = {
            'class': (
                'block w-full text-sm text-gray-900 border border-gray-300 rounded-md cursor-pointer '
                'bg-gray-50 focus:outline-none focus:ring-2 focus:ring-sap-blue '
                'file:mr-4 file:py-2 file:px-4 file:rounded-l-md file:border-0 '
                'file:text-sm file:font-semibold file:bg-sap-blue file:text-white '
                'hover:file:bg-sap-blue-dark'
            )
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class TailwindClearableFileInput(forms.ClearableFileInput):
    """Clearable file input with Tailwind CSS styling"""

    def __init__(self, attrs=None, **kwargs):
        default_attrs = {
            'class': (
                'block w-full text-sm text-gray-900 border border-gray-300 rounded-md cursor-pointer '
                'bg-gray-50 focus:outline-none focus:ring-2 focus:ring-sap-blue '
                'file:mr-4 file:py-2 file:px-4 file:rounded-l-md file:border-0 '
                'file:text-sm file:font-semibold file:bg-sap-blue file:text-white '
                'hover:file:bg-sap-blue-dark'
            )
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class HTMXSelect(TailwindSelect):
    """
    Select dropdown with HTMX support for cascading dropdowns

    Usage:
        HTMXSelect(
            hx_get='/api/states/',
            hx_trigger='change',
            hx_target='#state-container',
            hx_include='[name="country"]'
        )
    """

    def __init__(self, attrs=None, choices=(), hx_get=None, hx_trigger='change',
                 hx_target=None, hx_include=None, hx_swap='innerHTML', **kwargs):
        htmx_attrs = {}
        if hx_get:
            htmx_attrs['hx-get'] = hx_get
        if hx_trigger:
            htmx_attrs['hx-trigger'] = hx_trigger
        if hx_target:
            htmx_attrs['hx-target'] = hx_target
        if hx_include:
            htmx_attrs['hx-include'] = hx_include
        if hx_swap:
            htmx_attrs['hx-swap'] = hx_swap

        if attrs:
            attrs.update(htmx_attrs)
        else:
            attrs = htmx_attrs

        super().__init__(attrs=attrs, choices=choices, **kwargs)


class SearchInput(TailwindTextInput):
    """
    Search input with HTMX support

    Usage:
        SearchInput(
            hx_get='/api/search/',
            hx_trigger='input changed delay:500ms',
            hx_target='#results'
        )
    """

    def __init__(self, attrs=None, hx_get=None, hx_trigger='input changed delay:500ms',
                 hx_target='#results', hx_swap='innerHTML', placeholder='Search...', **kwargs):
        htmx_attrs = {
            'type': 'search',
            'placeholder': placeholder
        }
        if hx_get:
            htmx_attrs['hx-get'] = hx_get
        if hx_trigger:
            htmx_attrs['hx-trigger'] = hx_trigger
        if hx_target:
            htmx_attrs['hx-target'] = hx_target
        if hx_swap:
            htmx_attrs['hx-swap'] = hx_swap

        if attrs:
            attrs.update(htmx_attrs)
        else:
            attrs = htmx_attrs

        super().__init__(attrs=attrs, **kwargs)


# Convenience mapping for easy imports
TAILWIND_WIDGETS = {
    'text': TailwindTextInput,
    'email': TailwindEmailInput,
    'number': TailwindNumberInput,
    'password': TailwindPasswordInput,
    'textarea': TailwindTextarea,
    'select': TailwindSelect,
    'select_multiple': TailwindSelectMultiple,
    'checkbox': TailwindCheckboxInput,
    'checkbox_multiple': TailwindCheckboxSelectMultiple,
    'radio': TailwindRadioSelect,
    'date': TailwindDateInput,
    'time': TailwindTimeInput,
    'datetime': TailwindDateTimeInput,
    'file': TailwindFileInput,
    'clearable_file': TailwindClearableFileInput,
}
