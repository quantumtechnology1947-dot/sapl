"""
Plan Service

Handles common business logic for Design, Manufacturing, and Vendor plans.
"""

from django.db.models import Q, Count, QuerySet
from typing import Optional


class PlanService:
    """
    Service class for common plan operations.

    Provides reusable methods for searching, filtering, and
    retrieving statistics across all plan types.
    """

    @staticmethod
    def search_design_plans(queryset: QuerySet, search_term: Optional[str] = None) -> QuerySet:
        """
        Filter design plans by search term.

        Searches across project name, work order number, and design leader.
        """
        if not search_term:
            return queryset

        return queryset.filter(
            Q(name_proj__icontains=search_term) |
            Q(wo_no__icontains=search_term) |
            Q(des_lea__icontains=search_term)
        )

    @staticmethod
    def search_manufacturing_plans(queryset: QuerySet, search_term: Optional[str] = None) -> QuerySet:
        """
        Filter manufacturing plans by search term.

        Searches across work order, item code, and description.
        """
        if not search_term:
            return queryset

        return queryset.filter(
            Q(wono__icontains=search_term) |
            Q(itemcode__icontains=search_term) |
            Q(description__icontains=search_term)
        )

    @staticmethod
    def search_vendor_plans(queryset: QuerySet, search_term: Optional[str] = None) -> QuerySet:
        """
        Filter vendor plans by search term.

        Searches across work order, item code, description, and vendor plan.
        """
        if not search_term:
            return queryset

        return queryset.filter(
            Q(wono__icontains=search_term) |
            Q(itemcode__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(vendorplan__icontains=search_term)
        )

    @staticmethod
    def search_hardware_plans(queryset: QuerySet, search_term: Optional[str] = None) -> QuerySet:
        """
        Filter hardware plans by search term.

        Searches across work order, item code, and description.
        """
        if not search_term:
            return queryset

        return queryset.filter(
            Q(wono__icontains=search_term) |
            Q(itemcode__icontains=search_term) |
            Q(description__icontains=search_term)
        )

    @staticmethod
    def search_mainsheet(queryset: QuerySet, search_term: Optional[str] = None) -> QuerySet:
        """
        Filter project main sheet by search term.

        Searches across project name, work order, and customer name.
        """
        if not search_term:
            return queryset

        return queryset.filter(
            Q(name_proj__icontains=search_term) |
            Q(wo_no__icontains=search_term) |
            Q(cust_name__icontains=search_term)
        )

    @staticmethod
    def get_plan_statistics(compid: int, finyearid: int) -> dict:
        """
        Get comprehensive statistics for all plan types.

        Returns counts for projects, designs, manufacturing plans,
        vendor plans, and activities.
        """
        from daily_report_system.models import (
            TblpmProjectplanningMaster,
            TblpmProjectplanningDesigner,
            TblpmProjectManufacturingPlanDetail,
            TblpmProjectVendorPlanDetail,
            TblpmProjectplanningMainsheet,
        )

        return {
            'total_projects': TblpmProjectplanningMaster.objects.filter(
                compid=compid, finyearid=finyearid
            ).count(),
            'total_designs': TblpmProjectplanningDesigner.objects.count(),
            'total_manufacturing': TblpmProjectManufacturingPlanDetail.objects.count(),
            'total_vendor_plans': TblpmProjectVendorPlanDetail.objects.count(),
            'total_activities': TblpmProjectplanningMainsheet.objects.count(),
        }

    @staticmethod
    def get_recent_projects(compid: int, finyearid: int, limit: int = 10) -> QuerySet:
        """
        Get recent projects for the given company and financial year.

        Returns the most recent projects ordered by ID (descending).
        """
        from daily_report_system.models import TblpmProjectplanningMaster

        return TblpmProjectplanningMaster.objects.filter(
            compid=compid, finyearid=finyearid
        ).order_by('-id')[:limit]
