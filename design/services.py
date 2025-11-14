"""
Design Services - Business logic for Design module
Handles complex operations like BOM tree management, copying, and ECN processing.
"""

from django.db import transaction
from django.db.models import Max
from .models import TbldgBomMaster, TbldgItemMaster, TbldgEcnMaster, TbldgBomitemTemp, TbldgBomAmd
from datetime import datetime
import re


class BomService:
    """
    Service class for BOM operations.
    Handles hierarchical tree operations, copying, and ECN management.
    """
    
    @staticmethod
    def get_bom_tree(wono):
        """
        Get hierarchical BOM structure for a work order.
        
        Args:
            wono: Work order number
            
        Returns:
            dict: Hierarchical tree structure with nested children
        """
        # Get all BOM items for this work order
        all_items = TbldgBomMaster.objects.filter(wono=wono).select_related('itemid')
        
        # Build tree starting from root items (pid is null or 0)
        root_items = all_items.filter(pid__isnull=True) | all_items.filter(pid=0)
        
        tree = []
        for root in root_items:
            node = BomService._build_node(root, all_items)
            tree.append(node)
        
        return tree
    
    @staticmethod
    def _build_node(item, all_items):
        """
        Recursively build tree node with children.
        
        Args:
            item: Current BOM item
            all_items: QuerySet of all BOM items
            
        Returns:
            dict: Node with item data and children
        """
        # Get children of this item
        children = all_items.filter(pid=item.id)
        
        node = {
            'id': item.id,
            'item': item,
            'itemcode': item.itemid.itemcode if item.itemid else '',
            'description': item.itemid.manfdesc if item.itemid else '',
            'qty': item.qty,
            'children': []
        }
        
        # Recursively build children
        for child in children:
            child_node = BomService._build_node(child, all_items)
            node['children'].append(child_node)
        
        return node
    
    @staticmethod
    @transaction.atomic
    def copy_bom(source_wono, target_wono, user_id):
        """
        Copy entire BOM structure from source to target work order.
        
        Args:
            source_wono: Source work order number
            target_wono: Target work order number
            user_id: User performing the copy
            
        Returns:
            int: Number of items copied
        """
        # Get all source BOM items
        source_items = TbldgBomMaster.objects.filter(wono=source_wono)
        
        if not source_items.exists():
            return 0
        
        # Create mapping of old IDs to new IDs
        id_mapping = {}
        
        # First pass: Copy all items
        for source_item in source_items:
            new_item = TbldgBomMaster()
            
            # Copy all fields
            new_item.wono = target_wono
            new_item.equipmentno = source_item.equipmentno
            new_item.unitno = source_item.unitno
            new_item.partno = source_item.partno
            new_item.itemid = source_item.itemid
            new_item.qty = source_item.qty
            new_item.revision = source_item.revision
            new_item.remark = source_item.remark
            new_item.material = source_item.material
            new_item.amdno = 0  # Reset amendment number
            new_item.ecn = 0  # Reset ECN
            new_item.ecnflag = 0
            
            # System fields
            now = datetime.now()
            new_item.sysdate = now.strftime('%d-%m-%Y')
            new_item.systime = now.strftime('%H:%M:%S')
            new_item.sessionid = str(user_id)
            new_item.compid = source_item.compid
            new_item.finyearid = source_item.finyearid
            
            # Don't set pid yet - will do in second pass
            new_item.pid = None
            new_item.cid = source_item.cid
            
            new_item.save()
            
            # Store mapping
            id_mapping[source_item.id] = new_item.id
        
        # Second pass: Update parent relationships
        for source_item in source_items:
            if source_item.pid and source_item.pid in id_mapping:
                new_item = TbldgBomMaster.objects.get(id=id_mapping[source_item.id])
                new_item.pid = id_mapping[source_item.pid]
                new_item.save()
        
        return len(id_mapping)
    
    @staticmethod
    @transaction.atomic
    def apply_ecn(ecn_id):
        """
        Apply ECN changes to BOM.
        Increments amendment number and updates revision.
        
        Args:
            ecn_id: ECN master ID
            
        Returns:
            bool: Success status
        """
        try:
            ecn = TbldgEcnMaster.objects.get(id=ecn_id)
            
            # Get all BOM items for this work order
            bom_items = TbldgBomMaster.objects.filter(wono=ecn.wono)
            
            # Increment amendment number for all items
            for item in bom_items:
                item.amdno += 1
                item.ecn = ecn_id
                item.ecnflag = 1
                item.save()
            
            # Mark ECN as applied
            ecn.flag = 1
            ecn.save()
            
            return True
        except TbldgEcnMaster.DoesNotExist:
            return False
    
    @staticmethod
    def get_bom_statistics(wono):
        """
        Get statistics for a BOM.
        
        Args:
            wono: Work order number
            
        Returns:
            dict: Statistics including total items, levels, etc.
        """
        all_items = TbldgBomMaster.objects.filter(wono=wono)
        
        if not all_items.exists():
            return {
                'total_items': 0,
                'root_items': 0,
                'max_depth': 0
            }
        
        root_items = all_items.filter(pid__isnull=True) | all_items.filter(pid=0)
        
        # Calculate max depth
        max_depth = BomService._calculate_max_depth(all_items)
        
        return {
            'total_items': all_items.count(),
            'root_items': root_items.count(),
            'max_depth': max_depth
        }
    
    @staticmethod
    def _calculate_max_depth(all_items):
        """Calculate maximum depth of BOM tree."""
        root_items = all_items.filter(pid__isnull=True) | all_items.filter(pid=0)
        
        max_depth = 0
        for root in root_items:
            depth = BomService._get_depth(root, all_items, 1)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    @staticmethod
    def _get_depth(item, all_items, current_depth):
        """Recursively calculate depth of a node."""
        children = all_items.filter(pid=item.id)

        if not children.exists():
            return current_depth

        max_child_depth = current_depth
        for child in children:
            child_depth = BomService._get_depth(child, all_items, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    @staticmethod
    def generate_equipment_no(wono, compid):
        """
        Generate next equipment number for a work order.
        Format: 00001, 00002, 00003, etc. (5-digit zero-padded)

        Converted from: BOM_Design_Assembly_New.aspx.cs Page_Load() method

        Args:
            wono: Work order number
            compid: Company ID

        Returns:
            str: Next equipment number (e.g., "00001")
        """
        # Get max equipment number from BOM_Master only (not temp - ASP.NET doesn't check temp for this)
        max_bom = TbldgBomMaster.objects.filter(
            compid=compid,
            equipmentno__isnull=False
        ).exclude(
            equipmentno=''
        ).exclude(
            equipmentno='99999'  # Exclude special placeholder value
        ).aggregate(Max('equipmentno'))['equipmentno__max']

        if max_bom:
            # Parse numeric part
            try:
                max_num = int(max_bom)
                next_num = max_num + 1
            except ValueError:
                # If parsing fails, start at 1
                next_num = 1
        else:
            next_num = 1

        # Format as 5-digit zero-padded string
        return f'{next_num:05d}'

    @staticmethod
    def generate_next_cid(wono, compid):
        """
        Generate next child sequential ID (CId) for a work order.

        Args:
            wono: Work order number
            compid: Company ID

        Returns:
            int: Next CId value
        """
        # Get max CId from BOM_Master
        max_cid = TbldgBomMaster.objects.filter(
            wono=wono,
            compid=compid
        ).aggregate(Max('cid'))['cid__max']

        return (max_cid or 0) + 1

    @staticmethod
    def check_duplicate_item(wono, parent_id, item_id, sessionid, compid):
        """
        Check if an item already exists under a parent in BOM or temp table.
        Prevents duplicate items in the same assembly.

        Args:
            wono: Work order number
            parent_id: Parent BOM item ID (PId)
            item_id: Item master ID to check
            sessionid: Session ID
            compid: Company ID

        Returns:
            dict: {'is_duplicate': bool, 'message': str}
        """
        # Check in permanent BOM table
        exists_in_bom = TbldgBomMaster.objects.filter(
            wono=wono,
            pid=parent_id,
            itemid=item_id,
            compid=compid
        ).exists()

        if exists_in_bom:
            return {
                'is_duplicate': True,
                'message': 'This item already exists in the BOM under this parent assembly'
            }

        # Check in temp table for current session
        exists_in_temp = TbldgBomitemTemp.objects.filter(
            wono=wono,
            childid=parent_id,
            itemid=item_id,
            sessionid=sessionid,
            compid=compid
        ).exists()

        if exists_in_temp:
            return {
                'is_duplicate': True,
                'message': 'This item is already added to the pending list for this assembly'
            }

        return {
            'is_duplicate': False,
            'message': 'Item can be added'
        }

    @staticmethod
    def split_assembly_number(assembly_no):
        """
        Split assembly number into equipment, unit, and part components.
        Format: "E001-01-01" → {'equipment': 'E001', 'unit': '01', 'part': '01'}

        Args:
            assembly_no: Full assembly number (e.g., "E001-01-01")

        Returns:
            dict: Components or None if invalid format
        """
        if not assembly_no:
            return None

        # Match format: E###-##-##
        match = re.match(r'(E\d+)-(\d+)-(\d+)', assembly_no)
        if match:
            return {
                'equipment': match.group(1),
                'unit': match.group(2),
                'part': match.group(3)
            }

        # Match partial format: E###-##
        match = re.match(r'(E\d+)-(\d+)', assembly_no)
        if match:
            return {
                'equipment': match.group(1),
                'unit': match.group(2),
                'part': None
            }

        # Match equipment only: E###
        match = re.match(r'(E\d+)', assembly_no)
        if match:
            return {
                'equipment': match.group(1),
                'unit': None,
                'part': None
            }

        return None

    @staticmethod
    def generate_part_number(parent_assembly_no, wono, compid):
        """
        Generate next part number for an assembly.
        If parent is "E001-01", generates "E001-01-01", "E001-01-02", etc.

        Converted from: BOM_WoItems.aspx.cs CreateNextUnitPartNo() method (lines 33-98)

        Args:
            parent_assembly_no: Parent assembly number (e.g., "E001-01")
            wono: Work order number
            compid: Company ID

        Returns:
            str: Next part number
        """
        if not parent_assembly_no:
            return None

        # Split parent assembly number
        components = BomService.split_assembly_number(parent_assembly_no)
        if not components:
            return None

        equipment = components['equipment']
        unit = components['unit']

        # Find max part number under this parent
        # Check both BOM_Master and BOMItem_Temp

        # Pattern to match: E###-##-##
        if unit:
            pattern = f'{equipment}-{unit}-'
        else:
            pattern = f'{equipment}-'

        # Get max from BOM_Master
        max_bom = TbldgBomMaster.objects.filter(
            wono=wono,
            compid=compid,
            partno__istartswith=pattern
        ).aggregate(Max('partno'))['partno__max']

        # Get max from BOMItem_Temp
        max_temp = TbldgBomitemTemp.objects.filter(
            wono=wono,
            compid=compid,
            partno__istartswith=pattern
        ).aggregate(Max('partno'))['partno__max']

        # Extract numeric part and find maximum
        max_num = 0

        if max_bom:
            parts = max_bom.split('-')
            if len(parts) >= 3:
                try:
                    max_num = max(max_num, int(parts[2]))
                except ValueError:
                    pass

        if max_temp:
            parts = max_temp.split('-')
            if len(parts) >= 3:
                try:
                    max_num = max(max_num, int(parts[2]))
                except ValueError:
                    pass

        # Increment and format
        next_num = max_num + 1

        if unit:
            return f'{equipment}-{unit}-{next_num:02d}'
        else:
            return f'{equipment}-{next_num:02d}'


class BomTempService:
    """
    Service class for BOM temporary storage operations.
    Handles session-based temporary storage before committing items to permanent BOM.

    This implements the ASP.NET pattern where items are added to tblDG_BOMItem_Temp
    first, allowing users to review selections before final commit.

    Converted from: BOM_WoItems.aspx.cs (lines 880-1049)
    """

    @staticmethod
    def add_to_temp(wono, parent_cid, item_id, qty, sessionid, compid, part_no=None, manf_desc=None, uom_basic=None):
        """
        Add an item to temporary storage for a BOM session.

        Args:
            wono: Work order number
            parent_cid: Parent item's CId (childid in temp table)
            item_id: Item master ID
            qty: Quantity
            sessionid: Session ID (user ID as string)
            compid: Company ID
            part_no: Optional part number (for new items)
            manf_desc: Optional manufacturer description (for new items)
            uom_basic: Optional UOM ID (for new items)

        Returns:
            TbldgBomitemTemp: Created temp item or None if duplicate
        """
        # Check for duplicates
        duplicate_check = BomService.check_duplicate_item(
            wono, parent_cid, item_id, sessionid, compid
        )

        if duplicate_check['is_duplicate']:
            return None

        # Create temp item
        temp_item = TbldgBomitemTemp()
        temp_item.compid = compid
        temp_item.sessionid = sessionid
        temp_item.wono = wono
        temp_item.itemid_id = item_id  # ForeignKey uses _id suffix
        temp_item.qty = qty
        temp_item.childid = parent_cid
        temp_item.partno = part_no
        temp_item.manfdesc = manf_desc
        temp_item.uombasic = uom_basic

        temp_item.save()
        return temp_item

    @staticmethod
    def get_temp_items(wono, parent_cid, sessionid, compid):
        """
        Retrieve temporary items for a specific parent and session.

        Args:
            wono: Work order number
            parent_cid: Parent item's CId
            sessionid: Session ID
            compid: Company ID

        Returns:
            QuerySet: TbldgBomitemTemp items
        """
        return TbldgBomitemTemp.objects.filter(
            wono=wono,
            childid=parent_cid,
            sessionid=sessionid,
            compid=compid
        ).select_related('itemid')

    @staticmethod
    @transaction.atomic
    def commit_temp_to_bom(wono, parent_cid, sessionid, compid, finyearid, user_id, revision='0', material=''):
        """
        Commit all temporary items for a parent to permanent BOM table.
        This replicates the ASP.NET AddToTPLBOM() method (BOM_WoItems.aspx.cs lines 896-1049).

        Args:
            wono: Work order number
            parent_cid: Parent item's CId (or None for root level)
            sessionid: Session ID
            compid: Company ID
            finyearid: Financial year ID
            user_id: User performing the commit
            revision: Revision number (default '0')
            material: Material specification

        Returns:
            dict: {'success': bool, 'count': int, 'message': str}
        """
        # Get all temp items for this parent
        temp_items = BomTempService.get_temp_items(wono, parent_cid, sessionid, compid)

        if not temp_items.exists():
            return {
                'success': False,
                'count': 0,
                'message': 'No items found in temporary storage'
            }

        # Get parent item to determine assembly number
        parent_item = None
        parent_assembly_no = None
        if parent_cid:
            try:
                parent_item = TbldgBomMaster.objects.get(id=parent_cid, wono=wono, compid=compid)
                parent_assembly_no = parent_item.partno
            except TbldgBomMaster.DoesNotExist:
                return {
                    'success': False,
                    'count': 0,
                    'message': f'Parent item with CId={parent_cid} not found'
                }

        # Prepare common fields
        now = datetime.now()
        sysdate = now.strftime('%d-%m-%Y')
        systime = now.strftime('%H:%M:%S')

        committed_count = 0

        for temp_item in temp_items:
            # Generate next CId
            next_cid = BomService.generate_next_cid(wono, compid)

            # Generate part number
            if parent_assembly_no:
                part_no = BomService.generate_part_number(parent_assembly_no, wono, compid)
            else:
                # Root level - use equipment number
                part_no = BomService.generate_equipment_no(wono, compid)

            # Create BOM item
            bom_item = TbldgBomMaster()
            bom_item.sysdate = sysdate
            bom_item.systime = systime
            bom_item.compid = compid
            bom_item.finyearid = finyearid
            bom_item.sessionid = sessionid
            bom_item.wono = wono

            # Assembly numbering
            if parent_item:
                bom_item.equipmentno = parent_item.equipmentno
                bom_item.unitno = parent_item.unitno if parent_item.unitno else '01'
            else:
                # Root level
                bom_item.equipmentno = part_no  # E001
                bom_item.unitno = None

            bom_item.partno = part_no
            bom_item.pid = parent_cid  # Parent ID
            bom_item.cid = next_cid

            # Item details
            bom_item.itemid = temp_item.itemid
            bom_item.qty = temp_item.qty
            bom_item.revision = revision
            bom_item.remark = ''
            bom_item.material = material

            # ECN and amendment
            bom_item.amdno = 0
            bom_item.ecn = 0
            bom_item.ecnflag = 0

            bom_item.save()
            committed_count += 1

        # Clear temp items after successful commit
        temp_items.delete()

        return {
            'success': True,
            'count': committed_count,
            'message': f'Successfully committed {committed_count} item(s) to BOM'
        }

    @staticmethod
    def clear_temp(wono, parent_cid, sessionid, compid):
        """
        Clear temporary items for a specific parent and session without committing.

        Args:
            wono: Work order number
            parent_cid: Parent item's CId (or None for all)
            sessionid: Session ID
            compid: Company ID

        Returns:
            int: Number of items deleted
        """
        query = TbldgBomitemTemp.objects.filter(
            wono=wono,
            sessionid=sessionid,
            compid=compid
        )

        if parent_cid is not None:
            query = query.filter(childid=parent_cid)

        count = query.count()
        query.delete()

        return count

    @staticmethod
    def get_temp_summary(wono, sessionid, compid):
        """
        Get summary of all temporary items for a work order session.

        Args:
            wono: Work order number
            sessionid: Session ID
            compid: Company ID

        Returns:
            dict: Summary with counts and groupings
        """
        all_temp = TbldgBomitemTemp.objects.filter(
            wono=wono,
            sessionid=sessionid,
            compid=compid
        )

        # Group by parent
        parent_groups = {}
        for item in all_temp.select_related('itemid'):
            parent_id = item.childid
            if parent_id not in parent_groups:
                parent_groups[parent_id] = []
            parent_groups[parent_id].append({
                'id': item.id,
                'itemcode': item.itemid.itemcode if item.itemid else '',
                'description': item.itemid.manfdesc if item.itemid else item.manfdesc,
                'qty': item.qty,
                'partno': item.partno
            })

        return {
            'total_count': all_temp.count(),
            'parent_groups': parent_groups,
            'has_items': all_temp.exists()
        }


class ItemService:
    """
    Service class for Item Master operations.
    """

    @staticmethod
    def validate_item_references(item_id):
        """
        Check if item is used in BOMs.

        Args:
            item_id: Item ID

        Returns:
            dict: Validation result with can_delete flag and reference count
        """
        bom_count = TbldgBomMaster.objects.filter(itemid=item_id).count()

        return {
            'can_delete': bom_count == 0,
            'bom_count': bom_count,
            'message': f'Item is used in {bom_count} BOM(s)' if bom_count > 0 else 'Item can be deleted'
        }

    @staticmethod
    def get_item_usage_summary(item_id):
        """
        Get summary of where an item is used.

        Args:
            item_id: Item ID

        Returns:
            dict: Usage summary
        """
        boms = TbldgBomMaster.objects.filter(itemid=item_id).select_related('itemid')

        work_orders = boms.values('wono').distinct()

        return {
            'total_boms': boms.count(),
            'work_orders': list(work_orders),
            'bom_details': [
                {
                    'wono': bom.wono,
                    'qty': bom.qty,
                    'equipmentno': bom.equipmentno
                }
                for bom in boms
            ]
        }


class BomHistoryService:
    """
    Service class for BOM History and Item Usage tracking.
    Handles recursive quantity calculations for item history reports.

    Converted from: aaspnet/Module/Design/Reports/ItemHistory_BOM_View.aspx
    """

    @staticmethod
    def get_recursive_bom_qty(wono, pid, cid, base_qty, compid):
        """
        Calculate recursive BOM quantity traversing up the BOM hierarchy.
        This replicates the ASP.NET fun.BOMRecurQty() function.

        The function multiplies quantities up the BOM tree to calculate
        the total quantity of a component needed in the final assembly.

        Example: If Assembly A needs 2x of Sub-assembly B, and B needs 3x of Part C,
        then the recursive quantity for C in the context of A is 2 * 3 = 6.

        Args:
            wono: Work order number
            pid: Parent ID in BOM (current level parent)
            cid: Child ID in BOM (the component we're calculating for)
            base_qty: Base quantity from current BOM level
            compid: Company ID for filtering

        Returns:
            float: Total recursive quantity needed
        """
        # If we've reached the root (pid is 0 or None), return the base quantity
        if not pid or pid == 0:
            return base_qty

        # Find the parent BOM record
        try:
            parent_bom = TbldgBomMaster.objects.get(
                id=pid,
                wono=wono,
                compid=compid
            )

            # If parent has its own parent, recursively calculate
            if parent_bom.pid and parent_bom.pid != 0:
                # Multiply current quantity by parent's quantity and recurse up
                parent_qty = parent_bom.qty if parent_bom.qty else 1.0
                return BomHistoryService.get_recursive_bom_qty(
                    wono,
                    parent_bom.pid,
                    pid,
                    base_qty * parent_qty,
                    compid
                )
            else:
                # Parent is root level, multiply and return
                parent_qty = parent_bom.qty if parent_bom.qty else 1.0
                return base_qty * parent_qty

        except TbldgBomMaster.DoesNotExist:
            # If parent not found, return base quantity
            return base_qty

    @staticmethod
    def get_item_bom_usage(item_id, compid, finyearid):
        """
        Get all BOM usage records for an item where it appears as a child component.
        Returns detailed information about where the item is used in assemblies.

        Args:
            item_id: Item ID to search for
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            list: List of dicts with BOM usage details including recursive quantities
        """
        # Query all BOM records where this item is the itemid (the item being used)
        # and PId is not 0 (meaning it's a child component, not a root assembly)
        bom_records = TbldgBomMaster.objects.filter(
            itemid=item_id,
            compid=compid,
            pid__isnull=False
        ).exclude(
            pid=0
        ).select_related('itemid').order_by('-sysdate', '-systime')

        usage_list = []
        for bom in bom_records:
            # Get parent assembly information
            parent_item = None
            parent_uom = None
            if bom.pid:
                try:
                    parent_bom = TbldgBomMaster.objects.get(id=bom.pid)
                    if parent_bom.itemid:
                        parent_item = parent_bom.itemid
                        # Get UOM from sys_admin.UnitMaster
                        if parent_item.uombasic:
                            from sys_admin.models import UnitMaster
                            try:
                                parent_uom = UnitMaster.objects.get(id=parent_item.uombasic)
                            except UnitMaster.DoesNotExist:
                                pass
                except TbldgBomMaster.DoesNotExist:
                    pass

            # Calculate recursive quantity
            base_qty = bom.qty if bom.qty else 0.0
            recursive_qty = BomHistoryService.get_recursive_bom_qty(
                bom.wono,
                bom.pid,
                bom.id,
                base_qty,
                compid
            )

            usage_list.append({
                'bom_id': bom.id,
                'wono': bom.wono,
                'sysdate': bom.sysdate,
                'systime': bom.systime,
                'parent_itemcode': parent_item.itemcode if parent_item else '-',
                'parent_desc': parent_item.manfdesc if parent_item else '-',
                'parent_uom': parent_uom.symbol if parent_uom else '-',
                'base_qty': base_qty,
                'recursive_qty': recursive_qty,
                'pid': bom.pid,
                'cid': bom.id
            })

        return usage_list

    @staticmethod
    def get_next_part_no(parent_part_no, wono, compid):
        """
        Generate next part number for a parent assembly.
        Example: If parent is "00001-01-01", generates "00001-01-02"

        Converted from: BOM_WoItems.aspx.cs CreateNextUnitPartNo() method

        Args:
            parent_part_no: Parent assembly part number (e.g., "00001-01-01")
            wono: Work order number
            compid: Company ID

        Returns:
            str: Next part number (e.g., "02")
        """
        # Parse parent part number: "00001-01-01" → equip=00001, unit=01
        parts = parent_part_no.split('-')
        if len(parts) < 2:
            return "01"

        equip_no = parts[0]
        unit_no = parts[1]

        # Find max part no with this prefix
        prefix = f'{equip_no}-{unit_no}-'

        # Check both BOM_Master and BOMItem_Temp
        max_bom = TbldgBomMaster.objects.filter(
            wono=wono,
            compid=compid,
            partno__startswith=prefix
        ).aggregate(max_part=Max('partno'))['max_part']

        max_temp = TbldgBomitemTemp.objects.filter(
            wono=wono,
            compid=compid,
            partno__startswith=prefix
        ).aggregate(max_part=Max('partno'))['max_part']

        # Get max from both
        max_part = max_bom or max_temp

        if max_part:
            # Extract last part: "00001-01-03" → "03"
            last_part = max_part.split('-')[2]
            # Handle case where it might have trailing 0: "030" → "03"
            last_part_num = int(last_part.rstrip('0') or '0')
            next_part = last_part_num + 1
        else:
            next_part = 1

        return f'{next_part:02d}'  # Zero-padded 2 digits

    @staticmethod
    def generate_item_code(equip_no, unit_no, part_no, process='0'):
        """
        Generate item code in format: EquipNo-UnitNo-PartNo-Process
        Example: "00001-01-01-0" → "00001-01-010"

        Converted from: BOM_Design_Assembly_New.aspx.cs and BOM_WoItems.aspx.cs

        Args:
            equip_no: Equipment number (e.g., "00001")
            unit_no: Unit number (e.g., "01")
            part_no: Part number (e.g., "01")
            process: Process code (default "0")

        Returns:
            str: Item code (e.g., "00001-01-010")
        """
        return f'{equip_no}-{unit_no}-{part_no}{process}'

    @staticmethod
    def calculate_bom_qty(wono, cid, compid, finyearid):
        """
        Calculate recursive BOM quantity by traversing parent chain.
        Multiplies quantities up the tree to get final BOM quantity.

        Converted from: fun.BOMTreeQty() in ASP.NET

        Args:
            wono: Work order number
            cid: Current item's CId
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            float: Calculated BOM quantity (recursive multiplication)
        """
        quantities = []
        current_cid = cid

        # Traverse up the tree
        max_iterations = 100  # Prevent infinite loops
        iterations = 0

        while iterations < max_iterations:
            try:
                bom_item = TbldgBomMaster.objects.get(
                    wono=wono,
                    cid=current_cid,
                    compid=compid
                )
                quantities.append(float(bom_item.qty or 0))

                # Move to parent
                if not bom_item.pid or bom_item.pid == 0:
                    break  # Reached root
                current_cid = bom_item.pid

            except TbldgBomMaster.DoesNotExist:
                break

            iterations += 1

        # Multiply all quantities
        result = 1.0
        for qty in quantities:
            result *= qty

        return round(result, 3)

    @staticmethod
    def get_next_cid(wono, compid, finyearid):
        """
        Generate next CId (Child ID) for this work order.
        CId is auto-incremented per work order.

        Converted from: fun.getBOMCId() in ASP.NET

        Args:
            wono: Work order number
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            int: Next available CId
        """
        max_cid = TbldgBomMaster.objects.filter(
            wono=wono,
            compid=compid
        ).aggregate(max_cid=Max('cid'))['max_cid']

        if max_cid:
            return max_cid + 1
        else:
            return 1


class BOMSessionService:
    """
    Service for session-based temporary BOM item storage.
    Implements the 4-tab wizard pattern from ASP.NET (tblDG_BOMItem_Temp equivalent).

    Converted from: BOM_WoItems.aspx - Tabs 1-4 workflow
    """

    SESSION_KEY = 'bom_temp_items'

    @staticmethod
    def add_existing_item(request, item_id, qty, parent_cid, remark=''):
        """
        Add existing item from Item Master to session temp storage.
        This is Tab 1 functionality in ASP.NET.

        Args:
            request: HTTP request with session
            item_id: ID of existing item from tblDG_Item_Master
            qty: Required quantity
            parent_cid: Parent's CId (where this item will be added)
            remark: Optional remarks
        """
        temp_items = request.session.get(BOMSessionService.SESSION_KEY, [])

        temp_items.append({
            'item_id': item_id,
            'qty': float(qty),
            'parent_cid': parent_cid,
            'remark': remark,
            'is_new': False,
            'timestamp': datetime.now().isoformat()
        })

        request.session[BOMSessionService.SESSION_KEY] = temp_items
        request.session.modified = True

    @staticmethod
    def add_new_item(request, item_data, qty, parent_cid, remark=''):
        """
        Add new item (to be created) to session temp storage.
        This is Tab 2 functionality in ASP.NET.

        Args:
            request: HTTP request with session
            item_data: Dict with new item details (partno, itemcode, manfdesc, uombasic, etc.)
            qty: Required quantity
            parent_cid: Parent's CId
            remark: Optional remarks
        """
        temp_items = request.session.get(BOMSessionService.SESSION_KEY, [])

        temp_items.append({
            'item_data': item_data,
            'qty': float(qty),
            'parent_cid': parent_cid,
            'remark': remark,
            'is_new': True,
            'timestamp': datetime.now().isoformat()
        })

        request.session[BOMSessionService.SESSION_KEY] = temp_items
        request.session.modified = True

    @staticmethod
    def get_temp_items(request):
        """
        Get all items in session temp storage.
        This is Tab 4 display functionality.

        Returns:
            list: List of temp items
        """
        return request.session.get(BOMSessionService.SESSION_KEY, [])

    @staticmethod
    def get_temp_items_with_details(request):
        """
        Get temp items with full item details populated.

        Returns:
            list: List of dicts with item details
        """
        temp_items = BOMSessionService.get_temp_items(request)
        detailed_items = []

        for idx, temp_item in enumerate(temp_items):
            if temp_item['is_new']:
                # New item - use item_data
                item_data = temp_item['item_data']
                detailed_items.append({
                    'index': idx,
                    'itemcode': item_data.get('itemcode', ''),
                    'partno': item_data.get('partno', ''),
                    'manfdesc': item_data.get('manfdesc', ''),
                    'uom': item_data.get('uom_symbol', ''),
                    'qty': temp_item['qty'],
                    'remark': temp_item.get('remark', ''),
                    'is_new': True
                })
            else:
                # Existing item - fetch from database
                try:
                    from sys_admin.models import UnitMaster
                    item = TbldgItemMaster.objects.get(id=temp_item['item_id'])
                    uom = UnitMaster.objects.get(id=item.uombasic_id) if item.uombasic_id else None

                    detailed_items.append({
                        'index': idx,
                        'item_id': item.id,
                        'itemcode': item.itemcode or '',
                        'partno': item.partno or '',
                        'manfdesc': item.manfdesc or '',
                        'uom': uom.symbol if uom else '',
                        'qty': temp_item['qty'],
                        'remark': temp_item.get('remark', ''),
                        'is_new': False
                    })
                except TbldgItemMaster.DoesNotExist:
                    pass

        return detailed_items

    @staticmethod
    def clear_temp_items(request):
        """
        Clear all items from session temp storage.
        Called after commit or cancel.
        """
        request.session[BOMSessionService.SESSION_KEY] = []
        request.session.modified = True

    @staticmethod
    def remove_item(request, index):
        """
        Remove item by index from session temp storage.
        This is the Delete functionality in Tab 4.

        Args:
            request: HTTP request with session
            index: Index of item to remove
        """
        temp_items = request.session.get(BOMSessionService.SESSION_KEY, [])
        if 0 <= index < len(temp_items):
            temp_items.pop(index)
            request.session[BOMSessionService.SESSION_KEY] = temp_items
            request.session.modified = True

    @staticmethod
    @transaction.atomic
    def commit_to_bom(request, wono, parent_cid, compid, finyearid, sessionid):
        """
        Commit all session temp items to permanent BOM tables.
        This is the "Add to BOM" button functionality in Tab 4.

        Converted from: AddToTPLBOM() method in BOM_WoItems.aspx.cs

        Args:
            request: HTTP request with session
            wono: Work order number
            parent_cid: Parent's CId (where items are being added)
            compid: Company ID
            finyearid: Financial year ID
            sessionid: Session ID (user ID as string)

        Returns:
            int: Number of items committed
        """
        temp_items = BOMSessionService.get_temp_items(request)
        committed_count = 0

        for temp_item in temp_items:
            # Get next CId for each item
            next_cid = BomService.get_next_cid(wono, compid, finyearid)

            if temp_item['is_new']:
                # Create new item in Item_Master first
                item_data = temp_item['item_data']

                from sys_admin.models import UnitMaster

                item = TbldgItemMaster.objects.create(
                    sysdate=datetime.now().strftime('%d-%m-%Y'),
                    systime=datetime.now().strftime('%H:%M:%S'),
                    sessionid=sessionid,
                    compid=compid,
                    finyearid=finyearid,
                    partno=item_data['partno'],
                    itemcode=item_data['itemcode'],
                    process=item_data.get('process', '0'),
                    manfdesc=item_data['manfdesc'],
                    uombasic_id=item_data['uombasic'],
                    material=item_data.get('material', ''),
                    # File data
                    filename=item_data.get('filename', ''),
                    filesize=item_data.get('filesize', 0),
                    contenttype=item_data.get('contenttype', ''),
                    filedata=item_data.get('filedata', b''),
                    attname=item_data.get('attname', ''),
                    attsize=item_data.get('attsize', 0),
                    attcontenttype=item_data.get('attcontenttype', ''),
                    attdata=item_data.get('attdata', b''),
                    # Opening balance
                    openingbaldate=datetime.now().strftime('%d-%m-%Y'),
                    openingbalqty=0
                )
                item_id = item.id

                # Insert into BOM_Master with part number info
                TbldgBomMaster.objects.create(
                    sysdate=datetime.now().strftime('%d-%m-%Y'),
                    systime=datetime.now().strftime('%H:%M:%S'),
                    sessionid=sessionid,
                    compid=compid,
                    finyearid=finyearid,
                    wono=wono,
                    pid=parent_cid,  # Parent is the node user clicked
                    cid=next_cid,
                    itemid_id=item_id,
                    qty=temp_item['qty'],
                    partno=item_data['partno'],
                    equipmentno=item_data.get('equipmentno', ''),
                    unitno=item_data.get('unitno', ''),
                    remark=temp_item.get('remark', ''),
                    material=item_data.get('material', ''),
                    ecnflag=item_data.get('ecnflag', 0),
                    ecn=0,
                    amdno=0,
                    revision=item_data.get('revision', '')
                )

            else:
                # Existing item - just insert into BOM_Master
                TbldgBomMaster.objects.create(
                    sysdate=datetime.now().strftime('%d-%m-%Y'),
                    systime=datetime.now().strftime('%H:%M:%S'),
                    sessionid=sessionid,
                    compid=compid,
                    finyearid=finyearid,
                    wono=wono,
                    pid=parent_cid,
                    cid=next_cid,
                    itemid_id=temp_item['item_id'],
                    qty=temp_item['qty'],
                    remark=temp_item.get('remark', ''),
                    ecn=0,
                    ecnflag=0,
                    amdno=0,
                    revision=''
                )

            committed_count += 1

        # Update work order flag
        from sales_distribution.models import SdCustWorkorderMaster
        SdCustWorkorderMaster.objects.filter(
            wono=wono, compid=compid
        ).update(updatewo='1')

        # Clear session
        BOMSessionService.clear_temp_items(request)

        return committed_count
