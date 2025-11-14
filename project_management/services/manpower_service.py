"""
ManPower Planning Service

Business logic for manpower resource allocation and planning calculations.
Extracted from views.py for better separation of concerns.
"""

from datetime import datetime
from django.db.models import Q
from ..models import (
    TblpmManpowerplanning,
    TblpmManpowerplanningAmd,
    TblpmManpowerplanningDetails,
)


class ManpowerService:
    """Service class for ManPower Planning operations"""

    @staticmethod
    def create_amendment(old_plan):
        """
        Create an amendment record before updating a manpower plan.
        Preserves historical data.

        Args:
            old_plan: TblpmManpowerplanning instance

        Returns:
            TblpmManpowerplanningAmd: Created amendment record
        """
        amendment = TblpmManpowerplanningAmd.objects.create(
            mid=old_plan,
            compid=old_plan.compid,
            finyearid=old_plan.finyearid,
            sessionid=old_plan.sessionid,
            sysdate=old_plan.sysdate,
            systime=old_plan.systime,
            empid=old_plan.empid,
            date=old_plan.date,
            wono=old_plan.wono,
            dept=old_plan.dept,
            types=old_plan.types,
            amendmentno=old_plan.amendmentno
        )
        return amendment

    @staticmethod
    def get_next_amendment_number(plan):
        """
        Get the next amendment number for a plan.

        Args:
            plan: TblpmManpowerplanning instance

        Returns:
            int: Next amendment number
        """
        return plan.amendmentno + 1

    @staticmethod
    def enrich_plan_with_employee_info(plans, compid):
        """
        Enrich manpower plans with employee and business group information.

        Args:
            plans: QuerySet or list of TblpmManpowerplanning objects
            compid: Company ID

        Returns:
            list: Enriched plan dictionaries with employee names and BG symbols
        """
        from human_resource.models import TblhrOfficestaff, Businessgroup

        enriched_plans = []
        for plan in plans:
            emp = TblhrOfficestaff.objects.filter(
                compid=compid,
                empid=plan.empid
            ).first()

            bg_symbol = '-'
            if plan.dept and plan.dept > 0:
                bg_obj = Businessgroup.objects.filter(id=plan.dept).first()
                bg_symbol = bg_obj.symbol if bg_obj else '-'

            enriched_plans.append({
                'id': plan.id,
                'date': plan.date,
                'empid': plan.empid,
                'empname': emp.employeename if emp else plan.empid,
                'wono': plan.wono,
                'dept': plan.dept,
                'bg_symbol': bg_symbol,
                'types': plan.types,
                'amendmentno': plan.amendmentno,
            })

        return enriched_plans

    @staticmethod
    def filter_plans(queryset, filters):
        """
        Apply search filters to manpower planning queryset.

        Args:
            queryset: Base QuerySet to filter
            filters: Dict with filter parameters (wono, bg, empid, types, from_date, to_date)

        Returns:
            QuerySet: Filtered queryset
        """
        # Filter by WO Number
        if filters.get('search_wono'):
            queryset = queryset.filter(wono__icontains=filters['search_wono'])

        # Filter by BG Group (dept field)
        if filters.get('search_bg'):
            queryset = queryset.filter(dept=filters['search_bg'])

        # Filter by Employee ID
        if filters.get('search_empid'):
            queryset = queryset.filter(empid__icontains=filters['search_empid'])

        # Filter by Types
        if filters.get('search_types'):
            queryset = queryset.filter(types=filters['search_types'])

        # Filter by date range
        from_date = filters.get('from_date')
        to_date = filters.get('to_date')
        if from_date and to_date:
            # Convert DD-MM-YYYY to YYYY-MM-DD for comparison
            try:
                from_parts = from_date.split('-')
                to_parts = to_date.split('-')
                if len(from_parts) == 3 and len(to_parts) == 3:
                    db_from = f"{from_parts[2]}-{from_parts[1]}-{from_parts[0]}"
                    db_to = f"{to_parts[2]}-{to_parts[1]}-{to_parts[0]}"
                    queryset = queryset.filter(date__gte=db_from, date__lte=db_to)
            except Exception:
                pass  # Ignore date parsing errors

        return queryset

    @staticmethod
    def get_plan_details(plan):
        """
        Get all details for a manpower plan.

        Args:
            plan: TblpmManpowerplanning instance

        Returns:
            QuerySet: TblpmManpowerplanningDetails for this plan
        """
        return TblpmManpowerplanningDetails.objects.filter(mid=plan)

    @staticmethod
    def get_plan_amendments(plan):
        """
        Get amendment history for a plan.

        Args:
            plan: TblpmManpowerplanning instance

        Returns:
            QuerySet: TblpmManpowerplanningAmd ordered by amendment number
        """
        return TblpmManpowerplanningAmd.objects.filter(mid=plan).order_by('amendmentno')
