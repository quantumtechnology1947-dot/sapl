"""
BOM Services - Business logic for BOM operations
Handles tree building, quantity calculations, and BOM operations
"""

from django.db.models import Q
from .models import TbldgBomMaster, TbldgItemMaster, TbldgBomAmd, TbldgEcnMaster, TbldgEcnDetails
from sales_distribution.models import SdCustWorkorderMaster
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BomService:
    """Service class for BOM operations"""
    
    @staticmethod
    def build_bom_tree(wo_no, company_id, fin_year_id, filter_type='all'):
        """
        Build hierarchical BOM tree structure
        
        Args:
            wo_no: Work order number
            company_id: Company ID
            fin_year_id: Financial year ID
            filter_type: 'all', 'boughtout', or 'manufacturing'
            
        Returns:
            List of root nodes with nested children
        """
        # Get all BOM items for this work order
        all_items = TbldgBomMaster.objects.filter(
            wono=wo_no,
            compid=company_id,
            finyearid__lte=fin_year_id
        ).select_related('itemid').order_by('cid')
        
        # Apply filter if needed
        if filter_type == 'boughtout':
            # Get bought-out items (items with class = bought-out)
            boughtout_item_ids = TbldgItemMaster.objects.filter(
                class_field=1  # Assuming 1 = Bought Out
            ).values_list('id', flat=True)
            all_items = all_items.filter(itemid__in=boughtout_item_ids)
        elif filter_type == 'manufacturing':
            # Get manufacturing items (items with class = manufacturing)
            manufacturing_item_ids = TbldgItemMaster.objects.filter(
                class_field=2  # Assuming 2 = Manufacturing
            ).values_list('id', flat=True)
            all_items = all_items.filter(itemid__in=manufacturing_item_ids)
        
        # Build tree recursively
        return BomService._build_tree_recursive(all_items, 0)
    
    @staticmethod
    def _build_tree_recursive(all_items, parent_cid):
        """
        Recursively build tree structure
        
        Args:
            all_items: QuerySet of all BOM items
            parent_cid: Parent CId to find children for
            
        Returns:
            List of nodes with children
        """
        tree = []
        
        # Find children of this parent
        children = [item for item in all_items if item.pid == parent_cid]
        
        for child in children:
            node = {
                'item': child,
                'children': BomService._build_tree_recursive(all_items, child.cid),
                'bom_qty': BomService.calculate_bom_qty(all_items, child.cid)
            }
            tree.append(node)
        
        return tree
    
    @staticmethod
    def calculate_bom_qty(all_items, cid):
        """
        Calculate BOM quantity by multiplying quantities up the tree
        
        Args:
            all_items: QuerySet of all BOM items
            cid: Child ID to calculate quantity for
            
        Returns:
            Total BOM quantity
        """
        # Find the item
        try:
            item = next(i for i in all_items if i.cid == cid)
        except StopIteration:
            return 0
        
        # Start with this item's quantity
        total_qty = item.qty if item.qty else 1
        
        # Multiply by parent quantities up the tree
        current_pid = item.pid
        while current_pid and current_pid != 0:
            try:
                parent = next(i for i in all_items if i.cid == current_pid)
                total_qty *= (parent.qty if parent.qty else 1)
                current_pid = parent.pid
            except StopIteration:
                break
        
        return total_qty
    
    @staticmethod
    def generate_part_number(wo_no, parent_cid, company_id, fin_year_id):
        """
        Auto-generate next part number in format: Equipment-Unit-Part
        
        Args:
            wo_no: Work order number
            parent_cid: Parent CId
            company_id: Company ID
            fin_year_id: Financial year ID
            
        Returns:
            Generated part number string
        """
        # Get parent item to determine equipment and unit numbers
        if parent_cid and parent_cid != 0:
            try:
                parent = TbldgBomMaster.objects.get(
                    wono=wo_no,
                    cid=parent_cid,
                    compid=company_id
                )
                equipment_no = parent.equipmentno or 'E001'
                unit_no = parent.unitno or '01'
            except TbldgBomMaster.DoesNotExist:
                equipment_no = 'E001'
                unit_no = '01'
        else:
            equipment_no = 'E001'
            unit_no = '01'
        
        # Find next part number
        existing_parts = TbldgBomMaster.objects.filter(
            wono=wo_no,
            equipmentno=equipment_no,
            unitno=unit_no,
            compid=company_id
        ).values_list('partno', flat=True)
        
        # Extract numeric part and find max
        max_part = 0
        for part in existing_parts:
            if part:
                try:
                    # Extract last segment after last dash
                    part_num = int(part.split('-')[-1])
                    max_part = max(max_part, part_num)
                except (ValueError, IndexError):
                    pass
        
        # Generate new part number
        next_part = str(max_part + 1).zfill(2)
        return f"{equipment_no}-{unit_no}-{next_part}"
    
    @staticmethod
    def check_design_date(wo_no, company_id):
        """
        Check if design finalization date has passed
        
        Args:
            wo_no: Work order number
            company_id: Company ID
            
        Returns:
            Tuple (has_passed, design_date)
        """
        try:
            wo = SdCustWorkorderMaster.objects.get(
                wono=wo_no,
                compid=company_id
            )
            
            # Check if design finalization date exists and has passed
            if wo.taskdesignfinalization_fdate:
                # Try multiple date formats (database may store in different formats)
                date_str = wo.taskdesignfinalization_fdate
                design_date = None

                # Try YYYY-MM-DD format first (ISO format)
                try:
                    design_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    # Try dd-MM-yyyy format (ASP.NET format)
                    try:
                        design_date = datetime.strptime(date_str, '%d-%m-%Y')
                    except ValueError:
                        # If both fail, return False
                        return (False, date_str)

                if design_date:
                    current_date = datetime.now()
                    return (current_date > design_date, date_str)
            
            return (False, None)
        except SdCustWorkorderMaster.DoesNotExist:
            return (False, None)
    
    @staticmethod
    def create_amendment(bom_item):
        """
        Create amendment record before updating BOM item
        
        Args:
            bom_item: TbldgBomMaster instance
            
        Returns:
            Created TbldgBomAmd instance
        """
        now = datetime.now()
        
        amendment = TbldgBomAmd.objects.create(
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S'),
            compid=bom_item.compid,
            finyearid=bom_item.finyearid,
            sessionid=bom_item.sessionid,
            wono=bom_item.wono,
            bomid=bom_item.id,
            pid=bom_item.pid,
            cid=bom_item.cid,
            itemid=bom_item.itemid.id if bom_item.itemid else None,
            qty=bom_item.qty,
            description=bom_item.itemid.manfdesc if bom_item.itemid else None,
            uom=bom_item.itemid.uombasic if bom_item.itemid else None,
            amdno=bom_item.amdno
        )
        
        return amendment
    
    @staticmethod
    def create_ecn_record(wo_no, item_id, pid, cid, reasons, remarks, company_id, fin_year_id, session_id):
        """
        Create ECN master and details records
        
        Args:
            wo_no: Work order number
            item_id: Item ID
            pid: Parent CId
            cid: Child CId
            reasons: List of ECN reason IDs
            remarks: Remarks text
            company_id: Company ID
            fin_year_id: Financial year ID
            session_id: Session ID
            
        Returns:
            Created TbldgEcnMaster instance
        """
        now = datetime.now()
        
        # Create ECN master
        ecn_master = TbldgEcnMaster.objects.create(
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S'),
            compid=company_id,
            finyearid=fin_year_id,
            sessionid=session_id,
            itemid=item_id,
            wono=wo_no,
            pid=pid,
            cid=cid,
            flag=0  # 0 = Open, 1 = Closed
        )
        
        # Create ECN details for each reason
        for reason_id in reasons:
            TbldgEcnDetails.objects.create(
                mid=ecn_master,
                ecnreason=reason_id,
                remarks=remarks
            )
        
        return ecn_master
    
    @staticmethod
    def copy_bom(source_wo_no, target_wo_no, company_id, fin_year_id, session_id):
        """
        Copy entire BOM structure from one work order to another
        
        Args:
            source_wo_no: Source work order number
            target_wo_no: Target work order number
            company_id: Company ID
            fin_year_id: Financial year ID
            session_id: Session ID
            
        Returns:
            Number of items copied
        """
        # Get all source BOM items
        source_items = TbldgBomMaster.objects.filter(
            wono=source_wo_no,
            compid=company_id
        ).order_by('cid')
        
        if not source_items.exists():
            return 0
        
        # Create mapping of old CId to new CId
        cid_mapping = {}
        now = datetime.now()
        
        # Copy items maintaining hierarchy
        for source_item in source_items:
            # Map parent CId
            new_pid = cid_mapping.get(source_item.pid, source_item.pid)
            
            # Create new item
            new_item = TbldgBomMaster.objects.create(
                sysdate=now.strftime('%d-%m-%Y'),
                systime=now.strftime('%H:%M:%S'),
                compid=company_id,
                finyearid=fin_year_id,
                sessionid=session_id,
                wono=target_wo_no,
                equipmentno=source_item.equipmentno,
                unitno=source_item.unitno,
                partno=source_item.partno,
                pid=new_pid,
                cid=source_item.cid,  # Keep same CId structure
                qty=source_item.qty,
                ecn=0,
                ecnflag=0,
                amdno=0,
                revision=source_item.revision,
                remark=source_item.remark,
                material=source_item.material,
                itemid=source_item.itemid
            )
            
            # Store mapping
            cid_mapping[source_item.cid] = new_item.cid
        
        return len(source_items)
    
    @staticmethod
    def get_bom_statistics(wo_no, company_id, fin_year_id):
        """
        Get statistics for a BOM

        Args:
            wo_no: Work order number
            company_id: Company ID
            fin_year_id: Financial year ID

        Returns:
            Dictionary with statistics
        """
        items = TbldgBomMaster.objects.filter(
            wono=wo_no,
            compid=company_id,
            finyearid__lte=fin_year_id
        )

        total_items = items.count()

        # Count by class
        boughtout_count = 0
        manufacturing_count = 0

        for item in items:
            if item.itemid and item.itemid.class_field == 1:
                boughtout_count += 1
            elif item.itemid and item.itemid.class_field == 2:
                manufacturing_count += 1

        return {
            'total_items': total_items,
            'boughtout_count': boughtout_count,
            'manufacturing_count': manufacturing_count,
            'has_ecn': items.filter(ecnflag=1).exists()
        }

    @staticmethod
    def generate_next_cid(wo_no, company_id):
        """
        Generate next sequential CId for a work order.
        Centralized method to ensure consistent CId generation.

        Args:
            wo_no: Work order number
            company_id: Company ID

        Returns:
            Next CId (integer)
        """
        from django.db.models import Max

        max_cid = TbldgBomMaster.objects.filter(
            wono=wo_no,
            compid=company_id
        ).aggregate(Max('cid'))['cid__max'] or 0

        return max_cid + 1

    @staticmethod
    def create_child_item(parent, item, quantity, remarks, request):
        """
        Unified method to create a child item with proper CId/PId handling.
        This ensures consistent tree structure across the application.

        Args:
            parent: Parent TbldgBomMaster instance
            item: TbldgItemMaster instance to add as child
            quantity: Quantity of the child item
            remarks: Remarks for the BOM entry
            request: Django request object (for session data)

        Returns:
            Created TbldgBomMaster instance
        """
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        sessionid = str(request.user.id)
        now = datetime.now()

        # Generate next CId using centralized method
        next_cid = BomService.generate_next_cid(parent.wono, compid)

        # Create BOM entry with correct PId (parent's CId, not database ID)
        bom_entry = TbldgBomMaster.objects.create(
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S'),
            compid=compid,
            finyearid=finyearid,
            sessionid=sessionid,
            wono=parent.wono,
            equipmentno=parent.equipmentno,
            unitno=parent.unitno,
            partno=item.partno if item.partno else item.itemcode,
            pid=parent.cid,  # ✅ Parent's CId, NOT database ID
            cid=next_cid,    # ✅ Next sequential CId
            qty=quantity,
            ecn=0,
            ecnflag=0,
            amdno=parent.amdno or 0,
            revision=parent.revision or 'A',
            remark=remarks,
            material='',
            itemid=item
        )

        logger.info(
            f"Created BOM child: CId={next_cid}, PId={parent.cid}, "
            f"Item={item.partno or item.itemcode}, WO={parent.wono}"
        )

        return bom_entry

    @staticmethod
    def validate_tree_structure(wo_no, company_id):
        """
        Validate BOM tree structure integrity.
        Checks for orphaned nodes, circular references, and invalid PId/CId relationships.

        Args:
            wo_no: Work order number
            company_id: Company ID

        Returns:
            Tuple (is_valid, error_messages)
        """
        items = TbldgBomMaster.objects.filter(
            wono=wo_no,
            compid=company_id
        )

        errors = []

        # Check for duplicate CIds
        cid_list = [item.cid for item in items]
        if len(cid_list) != len(set(cid_list)):
            errors.append("Duplicate CIds found in BOM structure")

        # Check for orphaned nodes (PId points to non-existent CId)
        cid_set = set(cid_list)
        for item in items:
            if item.pid != 0 and item.pid not in cid_set:
                errors.append(
                    f"Orphaned node: CId={item.cid}, PId={item.pid} (parent does not exist)"
                )

        # Check for circular references
        def has_circular_reference(item, visited=None):
            if visited is None:
                visited = set()

            if item.cid in visited:
                return True

            visited.add(item.cid)

            # Find parent
            if item.pid != 0:
                try:
                    parent = next(i for i in items if i.cid == item.pid)
                    return has_circular_reference(parent, visited)
                except StopIteration:
                    pass

            return False

        for item in items:
            if has_circular_reference(item):
                errors.append(
                    f"Circular reference detected for CId={item.cid}"
                )

        return (len(errors) == 0, errors)

    @staticmethod
    def build_bom_tree_with_levels(wo_no, company_id, fin_year_id, filter_type='all'):
        """
        Build hierarchical BOM tree with level calculation.
        Enhanced version that includes level metadata for each node.
        
        Args:
            wo_no: Work order number
            company_id: Company ID
            fin_year_id: Financial year ID
            filter_type: 'all', 'boughtout', or 'manufacturing'
            
        Returns:
            List of root nodes with nested children and level metadata:
            {
                'item': TbldgBomMaster,
                'level': 0|1|2,
                'children': [...],
                'bom_qty': float,
                'can_add_children': boolean
            }
        """
        # Get all BOM items for this work order
        all_items = TbldgBomMaster.objects.filter(
            wono=wo_no,
            compid=company_id,
            finyearid__lte=fin_year_id
        ).select_related('itemid').order_by('cid')
        
        # Apply filter if needed
        if filter_type == 'boughtout':
            boughtout_item_ids = TbldgItemMaster.objects.filter(
                class_field=1
            ).values_list('id', flat=True)
            all_items = all_items.filter(itemid__in=boughtout_item_ids)
        elif filter_type == 'manufacturing':
            manufacturing_item_ids = TbldgItemMaster.objects.filter(
                class_field=2
            ).values_list('id', flat=True)
            all_items = all_items.filter(itemid__in=manufacturing_item_ids)
        
        # Build tree with level tracking
        return BomService._build_tree_with_levels(all_items, 0, 0)
    
    @staticmethod
    def _build_tree_with_levels(all_items, parent_cid, current_level):
        """
        Recursively build tree structure with level tracking.
        
        Args:
            all_items: QuerySet of all BOM items
            parent_cid: Parent CId to find children for
            current_level: Current level in hierarchy (0, 1, or 2)
            
        Returns:
            List of nodes with children and level metadata
        """
        tree = []
        
        # Find children of this parent
        children = [item for item in all_items if item.pid == parent_cid]
        
        for child in children:
            node = {
                'item': child,
                'level': current_level,
                'children': BomService._build_tree_with_levels(
                    all_items, child.cid, current_level + 1
                ),
                'bom_qty': BomService.calculate_bom_qty(all_items, child.cid),
                'can_add_children': current_level < 2  # Max 3 levels (0, 1, 2)
            }
            tree.append(node)
        
        return tree
    
    @staticmethod
    def validate_level_constraints(parent_cid, wo_no, company_id):
        """
        Validate that adding a child won't exceed 3-level limit.
        
        Args:
            parent_cid: Parent CId (0 for root)
            wo_no: Work order number
            company_id: Company ID
            
        Returns:
            Tuple (is_valid, current_level, error_message)
        """
        if parent_cid == 0:
            # Adding root level assembly
            return (True, 0, None)
        
        try:
            # Find parent and calculate its level
            parent = TbldgBomMaster.objects.get(
                cid=parent_cid,
                wono=wo_no,
                compid=company_id
            )
            
            level = BomService._calculate_node_level(parent, wo_no, company_id)
            
            if level >= 2:
                return (
                    False,
                    level,
                    f"Cannot add items beyond Level 2 (Parts). Maximum 3 levels allowed. "
                    f"Current node is at Level {level}."
                )
            
            return (True, level, None)
            
        except TbldgBomMaster.DoesNotExist:
            return (False, -1, f"Parent node with CId={parent_cid} not found")
    
    @staticmethod
    def _calculate_node_level(node, wo_no, company_id):
        """
        Calculate level of a node by traversing up to root.
        
        Args:
            node: TbldgBomMaster instance
            wo_no: Work order number
            company_id: Company ID
            
        Returns:
            Level (0 for Assembly, 1 for Sub-Assembly, 2 for Part)
        """
        level = 0
        current_pid = node.pid
        
        # Traverse up the tree until we reach root (pid=0)
        while current_pid != 0:
            level += 1
            parent = TbldgBomMaster.objects.filter(
                cid=current_pid,
                wono=wo_no,
                compid=company_id
            ).first()
            
            if not parent:
                # Orphaned node - return current level
                logger.warning(
                    f"Orphaned node detected: WO={wo_no}, CId={node.cid}, PId={current_pid}"
                )
                break
            
            current_pid = parent.pid
        
        return level
    
    @staticmethod
    def get_level_name(level):
        """
        Get human-readable level name.
        
        Args:
            level: Level number (0, 1, or 2)
            
        Returns:
            Level name string
        """
        level_names = {
            0: "Assembly",
            1: "Sub-Assembly",
            2: "Part/Component"
        }
        return level_names.get(level, "Unknown")
    
    @staticmethod
    def get_allowed_child_type(parent_level):
        """
        Get allowed child type for a parent level.
        
        Args:
            parent_level: Parent level (0, 1, or 2)
            
        Returns:
            Allowed child type string or None if no children allowed
        """
        if parent_level == 0:
            return "Sub-Assembly"
        elif parent_level == 1:
            return "Part/Component"
        else:
            return None
