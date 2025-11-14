"""
PR Service - Business Logic for Purchase Requisition Operations

Extracted from material_planning/views.py
Handles PR generation from plans, item aggregation by supplier, and PR validation.
"""

from material_management.models import PRMaster, PRDetails
from material_planning.models import (
    TblmpMaterialMaster,
    TblmpMaterialDetail,
    TblmpMaterialRawmaterial,
    TblmpMaterialProcess,
    TblmpMaterialFinish,
)


class PRService:
    """
    Service for Purchase Requisition (PR) operations.

    Provides methods for:
    - Checking if plan items exist in PR
    - PR generation from material plans (future implementation)
    - Item aggregation by supplier
    - PR validation and status checks
    """

    @staticmethod
    def check_plan_items_in_pr(plan_id, compid):
        """
        Check if any items from a material plan exist in Purchase Requisitions.
        Used to determine if plan has been converted to PR.

        Args:
            plan_id: Material plan ID
            compid: Company ID

        Returns:
            bool: True if any items are in PR, False otherwise
        """
        try:
            # Get plan details
            plan = TblmpMaterialMaster.objects.get(id=plan_id, compid=compid)
            details = TblmpMaterialDetail.objects.filter(master=plan)

            # Get all item IDs from raw material, process, and finish
            item_ids = set()

            for detail in details:
                # Raw materials
                if detail.rm:
                    raw_materials = TblmpMaterialRawmaterial.objects.filter(detail=detail)
                    item_ids.update(rm.item for rm in raw_materials if rm.item)

                # Processes
                if detail.pro:
                    processes = TblmpMaterialProcess.objects.filter(detail=detail)
                    item_ids.update(proc.item for proc in processes if proc.item)

                # Finishes
                if detail.fin:
                    finishes = TblmpMaterialFinish.objects.filter(detail=detail)
                    item_ids.update(fin.item for fin in finishes if fin.item)

            # Check if any of these items appear in PRDetails
            if item_ids:
                pr_exists = PRDetails.objects.filter(item_id__in=item_ids).exists()
                return pr_exists

            return False

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking plan items in PR: {e}", exc_info=True)
            return False

    @staticmethod
    def get_plan_items_by_supplier(plan_id, compid):
        """
        Get plan items grouped by supplier for PR generation.
        Aggregates quantities by supplier to create efficient PRs.

        Args:
            plan_id: Material plan ID
            compid: Company ID

        Returns:
            dict: Supplier ID -> list of items with quantities
        """
        try:
            # Get plan details
            plan = TblmpMaterialMaster.objects.get(id=plan_id, compid=compid)
            details = TblmpMaterialDetail.objects.filter(master=plan)

            supplier_items = {}

            for detail in details:
                # Raw materials
                if detail.rm:
                    raw_materials = TblmpMaterialRawmaterial.objects.filter(detail=detail)
                    for rm in raw_materials:
                        supplier_id = rm.supplierid
                        if supplier_id not in supplier_items:
                            supplier_items[supplier_id] = []

                        supplier_items[supplier_id].append({
                            'item_id': rm.item,
                            'qty': rm.qty,
                            'rate': rm.rate,
                            'discount': rm.discount,
                            'delivery_date': rm.deldate,
                            'type': 'raw_material'
                        })

                # Processes
                if detail.pro:
                    processes = TblmpMaterialProcess.objects.filter(detail=detail)
                    for proc in processes:
                        supplier_id = proc.supplierid
                        if supplier_id not in supplier_items:
                            supplier_items[supplier_id] = []

                        supplier_items[supplier_id].append({
                            'item_id': proc.item,
                            'qty': proc.qty,
                            'rate': proc.rate,
                            'discount': proc.discount,
                            'delivery_date': proc.deldate,
                            'type': 'process'
                        })

                # Finishes
                if detail.fin:
                    finishes = TblmpMaterialFinish.objects.filter(detail=detail)
                    for fin in finishes:
                        supplier_id = fin.supplierid
                        if supplier_id not in supplier_items:
                            supplier_items[supplier_id] = []

                        supplier_items[supplier_id].append({
                            'item_id': fin.item,
                            'qty': fin.qty,
                            'rate': fin.rate,
                            'discount': fin.discount,
                            'delivery_date': fin.deldate,
                            'type': 'finish'
                        })

            return supplier_items

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error grouping plan items by supplier: {e}", exc_info=True)
            return {}

    @staticmethod
    def aggregate_items_by_supplier(items_list):
        """
        Aggregate multiple items with same supplier and item_id.
        Sums quantities for efficient PR generation.

        Args:
            items_list: List of dicts with keys: supplier_id, item_id, qty, rate, discount, delivery_date

        Returns:
            dict: (supplier_id, item_id) -> aggregated dict
        """
        aggregated = {}

        for item in items_list:
            key = (item['supplier_id'], item['item_id'])

            if key in aggregated:
                # Aggregate quantities
                aggregated[key]['qty'] += item['qty']
                # Use earliest delivery date
                if item.get('delivery_date'):
                    existing_date = aggregated[key].get('delivery_date')
                    if not existing_date or item['delivery_date'] < existing_date:
                        aggregated[key]['delivery_date'] = item['delivery_date']
            else:
                aggregated[key] = item.copy()

        return list(aggregated.values())

    @staticmethod
    def generate_pr_from_plan(plan_id, compid, finyearid, user_id):
        """
        Generate Purchase Requisitions from a material plan.
        Creates one PR per supplier with aggregated items.

        NOTE: This is a placeholder for future implementation.
        The actual PR generation logic needs to be implemented based on:
        - Material Management module PRMaster/PRDetails structure
        - PR number generation logic
        - PR approval workflow

        Args:
            plan_id: Material plan ID
            compid: Company ID
            finyearid: Financial year ID
            user_id: User session ID

        Returns:
            dict with status, message, pr_ids
        """
        try:
            # Future implementation:
            # 1. Get plan items grouped by supplier
            # 2. Generate PR number for each supplier
            # 3. Create PRMaster record
            # 4. Create PRDetails records for each item
            # 5. Set audit fields
            # 6. Return list of generated PR numbers

            return {
                'status': 'error',
                'message': 'PR generation not yet implemented. Please use Material Management module to create PRs manually.'
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating PR from plan: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }

    @staticmethod
    def validate_plan_for_pr_generation(plan_id, compid):
        """
        Validate if a material plan is ready for PR generation.
        Checks for required data and business rules.

        Args:
            plan_id: Material plan ID
            compid: Company ID

        Returns:
            dict with status, message, errors (list)
        """
        errors = []

        try:
            # Get plan
            plan = TblmpMaterialMaster.objects.get(id=plan_id, compid=compid)
            details = TblmpMaterialDetail.objects.filter(master=plan)

            if not details.exists():
                errors.append("Plan has no items")

            # Check each detail has at least one procurement type
            for detail in details:
                if not (detail.rm or detail.pro or detail.fin):
                    errors.append(f"Item {detail.item} has no procurement type selected")

                # Check raw materials have suppliers
                if detail.rm:
                    raw_materials = TblmpMaterialRawmaterial.objects.filter(detail=detail)
                    if not raw_materials.exists():
                        errors.append(f"Item {detail.item} marked as Raw Material but has no suppliers")
                    else:
                        for rm in raw_materials:
                            if not rm.supplierid:
                                errors.append(f"Item {detail.item} has missing supplier")
                            if not rm.qty or rm.qty <= 0:
                                errors.append(f"Item {detail.item} has invalid quantity")

                # Check processes have suppliers
                if detail.pro:
                    processes = TblmpMaterialProcess.objects.filter(detail=detail)
                    if not processes.exists():
                        errors.append(f"Item {detail.item} marked as Process but has no suppliers")
                    else:
                        for proc in processes:
                            if not proc.supplierid:
                                errors.append(f"Item {detail.item} has missing supplier")
                            if not proc.qty or proc.qty <= 0:
                                errors.append(f"Item {detail.item} has invalid quantity")

                # Check finishes have suppliers
                if detail.fin:
                    finishes = TblmpMaterialFinish.objects.filter(detail=detail)
                    if not finishes.exists():
                        errors.append(f"Item {detail.item} marked as Finish but has no suppliers")
                    else:
                        for fin in finishes:
                            if not fin.supplierid:
                                errors.append(f"Item {detail.item} has missing supplier")
                            if not fin.qty or fin.qty <= 0:
                                errors.append(f"Item {detail.item} has invalid quantity")

            if errors:
                return {
                    'status': 'error',
                    'message': 'Plan validation failed',
                    'errors': errors
                }

            return {
                'status': 'success',
                'message': 'Plan is valid for PR generation',
                'errors': []
            }

        except TblmpMaterialMaster.DoesNotExist:
            return {
                'status': 'error',
                'message': 'Plan not found',
                'errors': ['Plan does not exist']
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error validating plan for PR: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'errors': [str(e)]
            }
