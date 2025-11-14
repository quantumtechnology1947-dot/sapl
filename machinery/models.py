"""
Machinery Module Models

This module uses vehicle and scheduling models from inventory app.
All models reference existing database tables with managed=False.

Note: Models are imported from inventory to avoid duplication.
"""

from inventory.models import (
    TblvehMasterDetails,
    TblvehProcessMaster,
    TblinvAutowisTimeschedule,
)

# Re-export models for convenient access
__all__ = [
    'TblvehMasterDetails',
    'TblvehProcessMaster',
    'TblinvAutowisTimeschedule',
]
