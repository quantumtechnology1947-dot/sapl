"""
DataLoader - Loads transformed data into Django database
"""
import logging
from typing import Dict, List, Optional
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError


class DataLoader:
    """
    Loads validated and transformed data into Django database
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'suppliers_created': 0,
            'suppliers_updated': 0,
            'suppliers_failed': 0,
            'items_created': 0,
            'items_updated': 0,
            'items_failed': 0,
            'pr_masters_created': 0,
            'pr_masters_updated': 0,
            'pr_masters_failed': 0,
            'pr_details_created': 0,
            'pr_details_updated': 0,
            'pr_details_failed': 0,
            'spr_masters_created': 0,
            'spr_masters_updated': 0,
            'spr_masters_failed': 0,
            'spr_details_created': 0,
            'spr_details_updated': 0,
            'spr_details_failed': 0,
        }
        self.failed_records = []
    
    def load_suppliers(self, suppliers: List[Dict]) -> int:
        """
        Load supplier records using update_or_create
        
        Args:
            suppliers: List of transformed supplier records
        
        Returns:
            Number of successfully loaded suppliers
        """
        from material_management.models import Supplier
        
        success_count = 0
        
        for supplier_data in suppliers:
            try:
                supplier_id = supplier_data.pop('supplier_id')
                
                obj, created = Supplier.objects.update_or_create(
                    supplier_id=supplier_id,
                    defaults=supplier_data
                )
                
                if created:
                    self.stats['suppliers_created'] += 1
                    self.logger.debug(f"Created supplier: {supplier_id}")
                else:
                    self.stats['suppliers_updated'] += 1
                    self.logger.debug(f"Updated supplier: {supplier_id}")
                
                success_count += 1
                
            except (IntegrityError, ValidationError) as e:
                self.stats['suppliers_failed'] += 1
                self.logger.error(f"Failed to load supplier {supplier_data.get('supplier_id')}: {e}")
                self.failed_records.append({
                    'type': 'supplier',
                    'id': supplier_data.get('supplier_id'),
                    'error': str(e)
                })
            except Exception as e:
                self.stats['suppliers_failed'] += 1
                self.logger.error(f"Unexpected error loading supplier: {e}")
                self.failed_records.append({
                    'type': 'supplier',
                    'id': supplier_data.get('supplier_id'),
                    'error': str(e)
                })
        
        self.logger.info(f"Loaded {success_count} suppliers "
                        f"({self.stats['suppliers_created']} created, "
                        f"{self.stats['suppliers_updated']} updated, "
                        f"{self.stats['suppliers_failed']} failed)")
        
        return success_count
    
    def load_items(self, items: List[Dict]) -> int:
        """
        Load item master records using update_or_create
        
        Args:
            items: List of transformed item records
        
        Returns:
            Number of successfully loaded items
        """
        from design.models import TbldgItemMaster
        
        success_count = 0
        
        for item_data in items:
            try:
                item_id = item_data.get('id')
                
                obj, created = TbldgItemMaster.objects.update_or_create(
                    id=item_id,
                    defaults=item_data
                )
                
                if created:
                    self.stats['items_created'] += 1
                    self.logger.debug(f"Created item: {item_id}")
                else:
                    self.stats['items_updated'] += 1
                    self.logger.debug(f"Updated item: {item_id}")
                
                success_count += 1
                
            except (IntegrityError, ValidationError) as e:
                self.stats['items_failed'] += 1
                self.logger.error(f"Failed to load item {item_data.get('id')}: {e}")
                self.failed_records.append({
                    'type': 'item',
                    'id': item_data.get('id'),
                    'error': str(e)
                })
            except Exception as e:
                self.stats['items_failed'] += 1
                self.logger.error(f"Unexpected error loading item: {e}")
                self.failed_records.append({
                    'type': 'item',
                    'id': item_data.get('id'),
                    'error': str(e)
                })
        
        self.logger.info(f"Loaded {success_count} items "
                        f"({self.stats['items_created']} created, "
                        f"{self.stats['items_updated']} updated, "
                        f"{self.stats['items_failed']} failed)")
        
        return success_count

    def load_pr_masters(self, pr_masters: List[Dict]) -> int:
        """
        Load PR master records with ID preservation
        
        Args:
            pr_masters: List of transformed PR master records
        
        Returns:
            Number of successfully loaded PR masters
        """
        from material_management.models import PRMaster
        
        success_count = 0
        
        with transaction.atomic():
            for pr_data in pr_masters:
                try:
                    pr_id = pr_data.get('id')
                    
                    obj, created = PRMaster.objects.update_or_create(
                        id=pr_id,
                        defaults=pr_data
                    )
                    
                    if created:
                        self.stats['pr_masters_created'] += 1
                        self.logger.debug(f"Created PR master: {pr_id}")
                    else:
                        self.stats['pr_masters_updated'] += 1
                        self.logger.debug(f"Updated PR master: {pr_id}")
                    
                    success_count += 1
                    
                except (IntegrityError, ValidationError) as e:
                    self.stats['pr_masters_failed'] += 1
                    self.logger.error(f"Failed to load PR master {pr_data.get('id')}: {e}")
                    self.failed_records.append({
                        'type': 'pr_master',
                        'id': pr_data.get('id'),
                        'error': str(e)
                    })
                except Exception as e:
                    self.stats['pr_masters_failed'] += 1
                    self.logger.error(f"Unexpected error loading PR master: {e}")
                    self.failed_records.append({
                        'type': 'pr_master',
                        'id': pr_data.get('id'),
                        'error': str(e)
                    })
        
        self.logger.info(f"Loaded {success_count} PR masters "
                        f"({self.stats['pr_masters_created']} created, "
                        f"{self.stats['pr_masters_updated']} updated, "
                        f"{self.stats['pr_masters_failed']} failed)")
        
        return success_count
    
    def load_pr_details(self, pr_details: List[Dict]) -> int:
        """
        Load PR detail records with FK validation
        
        Args:
            pr_details: List of transformed PR detail records
        
        Returns:
            Number of successfully loaded PR details
        """
        from material_management.models import PRDetails
        
        success_count = 0
        
        with transaction.atomic():
            for detail_data in pr_details:
                try:
                    detail_id = detail_data.get('id')
                    
                    obj, created = PRDetails.objects.update_or_create(
                        id=detail_id,
                        defaults=detail_data
                    )
                    
                    if created:
                        self.stats['pr_details_created'] += 1
                        self.logger.debug(f"Created PR detail: {detail_id}")
                    else:
                        self.stats['pr_details_updated'] += 1
                        self.logger.debug(f"Updated PR detail: {detail_id}")
                    
                    success_count += 1
                    
                except (IntegrityError, ValidationError) as e:
                    self.stats['pr_details_failed'] += 1
                    self.logger.error(f"Failed to load PR detail {detail_data.get('id')}: {e}")
                    self.failed_records.append({
                        'type': 'pr_detail',
                        'id': detail_data.get('id'),
                        'error': str(e)
                    })
                except Exception as e:
                    self.stats['pr_details_failed'] += 1
                    self.logger.error(f"Unexpected error loading PR detail: {e}")
                    self.failed_records.append({
                        'type': 'pr_detail',
                        'id': detail_data.get('id'),
                        'error': str(e)
                    })
        
        self.logger.info(f"Loaded {success_count} PR details "
                        f"({self.stats['pr_details_created']} created, "
                        f"{self.stats['pr_details_updated']} updated, "
                        f"{self.stats['pr_details_failed']} failed)")
        
        return success_count
    
    def load_spr_masters(self, spr_masters: List[Dict]) -> int:
        """
        Load SPR master records with ID preservation
        
        Args:
            spr_masters: List of transformed SPR master records
        
        Returns:
            Number of successfully loaded SPR masters
        """
        from material_management.models import SPRMaster
        
        success_count = 0
        
        with transaction.atomic():
            for spr_data in spr_masters:
                try:
                    spr_id = spr_data.get('id')
                    
                    obj, created = SPRMaster.objects.update_or_create(
                        id=spr_id,
                        defaults=spr_data
                    )
                    
                    if created:
                        self.stats['spr_masters_created'] += 1
                        self.logger.debug(f"Created SPR master: {spr_id}")
                    else:
                        self.stats['spr_masters_updated'] += 1
                        self.logger.debug(f"Updated SPR master: {spr_id}")
                    
                    success_count += 1
                    
                except (IntegrityError, ValidationError) as e:
                    self.stats['spr_masters_failed'] += 1
                    self.logger.error(f"Failed to load SPR master {spr_data.get('id')}: {e}")
                    self.failed_records.append({
                        'type': 'spr_master',
                        'id': spr_data.get('id'),
                        'error': str(e)
                    })
                except Exception as e:
                    self.stats['spr_masters_failed'] += 1
                    self.logger.error(f"Unexpected error loading SPR master: {e}")
                    self.failed_records.append({
                        'type': 'spr_master',
                        'id': spr_data.get('id'),
                        'error': str(e)
                    })
        
        self.logger.info(f"Loaded {success_count} SPR masters "
                        f"({self.stats['spr_masters_created']} created, "
                        f"{self.stats['spr_masters_updated']} updated, "
                        f"{self.stats['spr_masters_failed']} failed)")
        
        return success_count
    
    def load_spr_details(self, spr_details: List[Dict]) -> int:
        """
        Load SPR detail records with FK validation
        
        Args:
            spr_details: List of transformed SPR detail records
        
        Returns:
            Number of successfully loaded SPR details
        """
        from material_management.models import SPRDetails
        
        success_count = 0
        
        with transaction.atomic():
            for detail_data in spr_details:
                try:
                    detail_id = detail_data.get('id')
                    
                    obj, created = SPRDetails.objects.update_or_create(
                        id=detail_id,
                        defaults=detail_data
                    )
                    
                    if created:
                        self.stats['spr_details_created'] += 1
                        self.logger.debug(f"Created SPR detail: {detail_id}")
                    else:
                        self.stats['spr_details_updated'] += 1
                        self.logger.debug(f"Updated SPR detail: {detail_id}")
                    
                    success_count += 1
                    
                except (IntegrityError, ValidationError) as e:
                    self.stats['spr_details_failed'] += 1
                    self.logger.error(f"Failed to load SPR detail {detail_data.get('id')}: {e}")
                    self.failed_records.append({
                        'type': 'spr_detail',
                        'id': detail_data.get('id'),
                        'error': str(e)
                    })
                except Exception as e:
                    self.stats['spr_details_failed'] += 1
                    self.logger.error(f"Unexpected error loading SPR detail: {e}")
                    self.failed_records.append({
                        'type': 'spr_detail',
                        'id': detail_data.get('id'),
                        'error': str(e)
                    })
        
        self.logger.info(f"Loaded {success_count} SPR details "
                        f"({self.stats['spr_details_created']} created, "
                        f"{self.stats['spr_details_updated']} updated, "
                        f"{self.stats['spr_details_failed']} failed)")
        
        return success_count
    
    def get_stats(self) -> Dict:
        """
        Return loading statistics
        
        Returns:
            Dictionary with loading statistics
        """
        return self.stats.copy()
    
    def get_failed_records(self) -> List[Dict]:
        """
        Get list of failed records
        
        Returns:
            List of failed record details
        """
        return self.failed_records.copy()
    
    def get_summary(self) -> str:
        """
        Generate a summary report of loading operations
        
        Returns:
            Formatted summary string
        """
        total_created = (
            self.stats['suppliers_created'] +
            self.stats['items_created'] +
            self.stats['pr_masters_created'] +
            self.stats['pr_details_created'] +
            self.stats['spr_masters_created'] +
            self.stats['spr_details_created']
        )
        
        total_updated = (
            self.stats['suppliers_updated'] +
            self.stats['items_updated'] +
            self.stats['pr_masters_updated'] +
            self.stats['pr_details_updated'] +
            self.stats['spr_masters_updated'] +
            self.stats['spr_details_updated']
        )
        
        total_failed = (
            self.stats['suppliers_failed'] +
            self.stats['items_failed'] +
            self.stats['pr_masters_failed'] +
            self.stats['pr_details_failed'] +
            self.stats['spr_masters_failed'] +
            self.stats['spr_details_failed']
        )
        
        summary = f"""
Data Loading Summary:
=====================
Total Records Created: {total_created}
Total Records Updated: {total_updated}
Total Records Failed:  {total_failed}

Suppliers:
  - Created: {self.stats['suppliers_created']}
  - Updated: {self.stats['suppliers_updated']}
  - Failed:  {self.stats['suppliers_failed']}

Items:
  - Created: {self.stats['items_created']}
  - Updated: {self.stats['items_updated']}
  - Failed:  {self.stats['items_failed']}

PR Masters:
  - Created: {self.stats['pr_masters_created']}
  - Updated: {self.stats['pr_masters_updated']}
  - Failed:  {self.stats['pr_masters_failed']}

PR Details:
  - Created: {self.stats['pr_details_created']}
  - Updated: {self.stats['pr_details_updated']}
  - Failed:  {self.stats['pr_details_failed']}

SPR Masters:
  - Created: {self.stats['spr_masters_created']}
  - Updated: {self.stats['spr_masters_updated']}
  - Failed:  {self.stats['spr_masters_failed']}

SPR Details:
  - Created: {self.stats['spr_details_created']}
  - Updated: {self.stats['spr_details_updated']}
  - Failed:  {self.stats['spr_details_failed']}
"""
        return summary
    
    def clear_stats(self):
        """Clear all statistics"""
        for key in self.stats:
            self.stats[key] = 0
        self.failed_records = []
