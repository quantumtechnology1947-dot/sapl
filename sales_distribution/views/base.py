"""
Base classes and shared mixins for Sales Distribution views
"""

from django.contrib.auth.models import User
from ..models import SdCustMaster, SdCustQuotationMaster
from sys_admin.models import TblfinancialMaster as FinancialYear


class FinancialYearUserMixin:
    """
    Mixin to add financial year and user information to queryset objects.
    Eliminates duplicate code across multiple views.
    """
    def enrich_with_metadata(self, objects, include_quotation_count=False):
        """
        Add finyear_name, generated_by, and customer_name to objects.
        Optionally add quotation_count for enquiries.
        """
        # Create lookup dictionaries once
        fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}
        user_dict = {str(user.id): user.username for user in User.objects.all()}

        # Create customer name dictionary
        customer_dict = {c.customerid: c.customername for c in SdCustMaster.objects.all()}

        for obj in objects:
            obj.finyear_name = fy_dict.get(obj.finyearid, '-')
            if obj.sessionid and obj.sessionid.isdigit():
                obj.generated_by = user_dict.get(obj.sessionid, obj.sessionid)
            else:
                obj.generated_by = obj.sessionid if obj.sessionid else '-'

            # Add customer name if object has customerid
            if hasattr(obj, 'customerid') and obj.customerid:
                obj.customer_name = customer_dict.get(obj.customerid, obj.customerid)
            else:
                obj.customer_name = '-'

            # Add quotation count if requested (for enquiries)
            if include_quotation_count and hasattr(obj, 'enqid'):
                obj.quotation_count = SdCustQuotationMaster.objects.filter(enqid=obj).count()

        return objects
