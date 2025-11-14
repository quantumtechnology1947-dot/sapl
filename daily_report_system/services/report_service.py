"""
Report Service

Handles report generation logic for all plan types.
"""

from django.db.models import QuerySet
from typing import Dict, Any


class ReportService:
    """
    Service class for report generation and aggregation.

    Provides methods for generating various reports across
    design, manufacturing, and vendor plans.
    """

    @staticmethod
    def get_departmental_working_plan_data() -> QuerySet:
        """
        Get data for Departmental Working Plan Report.

        Returns all design plans ordered by work order number.
        """
        from daily_report_system.models import TblpmProjectplanningDesigner

        return TblpmProjectplanningDesigner.objects.all().order_by('wo_no')

    @staticmethod
    def get_individual_working_plan_data() -> QuerySet:
        """
        Get data for Individual Working Plan Report.

        Returns all project main sheets ordered by project name.
        """
        from daily_report_system.models import TblpmProjectplanningMainsheet

        return TblpmProjectplanningMainsheet.objects.all().order_by('name_proj')

    @staticmethod
    def get_detail_project_plan_data(compid: int, finyearid: int) -> Dict[str, Any]:
        """
        Get data for Detail Project Plan Report.

        Returns projects, design plans, and manufacturing plans
        for the given company and financial year.
        """
        from daily_report_system.models import (
            TblpmProjectplanningMaster,
            TblpmProjectplanningDesigner,
            TblpmProjectManufacturingPlanDetail,
        )

        return {
            'projects': TblpmProjectplanningMaster.objects.filter(
                compid=compid, finyearid=finyearid
            ).order_by('-id'),
            'design_plans': TblpmProjectplanningDesigner.objects.all(),
            'manufacturing_plans': TblpmProjectManufacturingPlanDetail.objects.all(),
        }

    @staticmethod
    def get_project_summary_data(compid: int, finyearid: int, limit: int = 20) -> Dict[str, Any]:
        """
        Get data for Project Summary Report.

        Returns comprehensive statistics and recent projects
        for the given company and financial year.
        """
        from daily_report_system.models import (
            TblpmProjectplanningMaster,
            TblpmProjectplanningDesigner,
            TblpmProjectManufacturingPlanDetail,
            TblpmProjectVendorPlanDetail,
            TblpmProjectHardwareMasterDetail,
        )

        summary = {
            'total_projects': TblpmProjectplanningMaster.objects.filter(
                compid=compid, finyearid=finyearid
            ).count(),
            'total_designs': TblpmProjectplanningDesigner.objects.count(),
            'total_manufacturing': TblpmProjectManufacturingPlanDetail.objects.count(),
            'total_vendor': TblpmProjectVendorPlanDetail.objects.count(),
            'total_hardware': TblpmProjectHardwareMasterDetail.objects.count(),
        }

        recent_projects = TblpmProjectplanningMaster.objects.filter(
            compid=compid, finyearid=finyearid
        ).order_by('-id')[:limit]

        return {
            'summary': summary,
            'recent_projects': recent_projects,
        }
