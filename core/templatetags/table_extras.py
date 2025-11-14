"""
Custom template filters for table component
"""
from django import template

register = template.Library()


@register.filter
def lookup(obj, field_name):
    """
    Dynamically lookup a field value from an object or dictionary.

    Usage: {{ row|lookup:"field_name" }}

    Args:
        obj: Object or dictionary to lookup from
        field_name: Field name or dictionary key to lookup

    Returns:
        Field value or None if not found
    """
    if hasattr(obj, field_name):
        return getattr(obj, field_name)
    elif isinstance(obj, dict):
        return obj.get(field_name)
    return None
