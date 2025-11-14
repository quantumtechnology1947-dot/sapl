"""
Inventory Module Utilities
Helper functions and utilities
"""
from datetime import datetime
from django.utils import timezone


def format_date_dmy(date_obj):
    """Format date as DD/MM/YYYY"""
    if not date_obj:
        return ''
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime('%d/%m/%Y')


def parse_date_dmy(date_str):
    """Parse DD/MM/YYYY date string"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%d/%m/%Y')
    except:
        return None


def get_financial_year_display(finyear_str):
    """Convert financial year string to display format"""
    # Input: "2024-2025" or "2024"
    # Output: "FY 2024-25"
    if not finyear_str:
        return ''
    
    if '-' in finyear_str:
        years = finyear_str.split('-')
        return f"FY {years[0]}-{years[1][-2:]}"
    return f"FY {finyear_str}"


def calculate_percentage(part, whole):
    """Calculate percentage safely"""
    if not whole or whole == 0:
        return 0
    return round((part / whole) * 100, 2)


def format_number(value, decimals=2):
    """Format number with specified decimals"""
    if value is None:
        return '0.00'
    try:
        return f"{float(value):.{decimals}f}"
    except:
        return '0.00'
