"""
Custom template filters for sales_distribution app.
"""
from django import template
from sales_distribution.models import SdCustMaster

register = template.Library()


@register.filter
def get_customer_name(customer_code):
    """
    Get customer name from customer code.

    Args:
        customer_code: Customer ID/code (e.g., 'C002')

    Returns:
        str: Customer name or the code if not found
    """
    if not customer_code:
        return '-'

    try:
        customer = SdCustMaster.objects.get(customerid=customer_code)
        return customer.customername or customer_code
    except SdCustMaster.DoesNotExist:
        return customer_code
