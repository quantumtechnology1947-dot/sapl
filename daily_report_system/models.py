"""
Daily Reporting System Module Models

This module uses project planning models from project_management app.
All models reference existing database tables with managed=False.

Note: Models are imported from project_management to avoid duplication.
"""

from project_management.models import (
    TblpmProjectplanningMaster,
    TblpmProjectplanningDesign,
    TblpmProjectplanningDesigner,
    TblpmProjectplanningMainsheet,
    TblpmProjectstatus,
    TblpmProjectManufacturingPlanDetail,
    TblpmProjectVendorPlanDetail,
    TblpmProjectHardwareMasterd,
    TblpmProjectHardwareMasterDetail,
    TblpmProjectHardwareAssemlyMaster,
    TblpmProjectHardwareAssemlyDetail,
    TblpmProjectManufacturingAssemlyMaster,
    TblpmProjectManufacturingAssemlyDetail,
)

# Re-export models for convenient access
__all__ = [
    'TblpmProjectplanningMaster',
    'TblpmProjectplanningDesign',
    'TblpmProjectplanningDesigner',
    'TblpmProjectplanningMainsheet',
    'TblpmProjectstatus',
    'TblpmProjectManufacturingPlanDetail',
    'TblpmProjectVendorPlanDetail',
    'TblpmProjectHardwareMasterd',
    'TblpmProjectHardwareMasterDetail',
    'TblpmProjectHardwareAssemlyMaster',
    'TblpmProjectHardwareAssemlyDetail',
    'TblpmProjectManufacturingAssemlyMaster',
    'TblpmProjectManufacturingAssemlyDetail',
]
