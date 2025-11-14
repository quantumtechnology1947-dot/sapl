"""
Custom template filters for design app
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key.
    Usage: {{ categories_dict|get_item:item.cid }}
    """
    if dictionary and key is not None:
        result = dictionary.get(key)
        if result:
            return result
    return '<span class="text-gray-400 italic">Not Assigned</span>'
