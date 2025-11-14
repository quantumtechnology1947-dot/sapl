"""
Custom template tags and filters for the Accounts module.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary by key.
    Usage: {{ mydict|get_item:key }}
    """
    if dictionary and key:
        return dictionary.get(key, '')
    return ''
