"""
BOM Service - Business Logic for Bill of Materials Operations

Extracted from material_planning/views.py
Handles BOM explosion, recursive quantity calculations, and inventory checks.
"""

from django.db import connection
from django.conf import settings
from design.models import TbldgItemMaster
from sys_admin.models import UnitMaster


class BOMService:
    """
    Service for BOM (Bill of Materials) operations.

    Provides methods for:
    - BOM explosion and tree traversal
    - Recursive quantity calculations
    - Inventory availability checks
    - Already-planned quantity calculations
    """

    @staticmethod
    def get_bom_items(wono, comp_id, fin_year_id):
        """
        Get distinct BOM items for the work order - following pdt.aspx MP_GRID logic
        Line 164-228 in pdt.aspx.cs

        Returns list of dicts with item details and calculated quantities:
        - item_id, item_code, description, uom
        - bom_qty: Total BOM quantity (recursive calculation)
        - pr_qty: Purchase requisition quantity
        - wis_qty: Work-in-shop issued quantity
        - gqn_qty: Goods received note quantity
        - raw_planned, pro_planned, fin_planned: Already planned quantities
        - available: Available quantity to plan (BOM - PR - WIS + GQN - planned)
        """
        items = []

        try:
            # Get distinct item IDs from BOM where CId not in (Select PId from BOM)
            # This gets leaf items only (line 164 in pdt.aspx.cs)
            # CRITICAL FIX: Removed FinYearId filter - BOM data should show regardless of financial year
            # CRITICAL FIX: Added "AND PId > 0" to exclude PId=0 which causes NULL handling issues

            # Workaround: Disable connection debug to avoid parameterized query formatting issues
            original_debug = settings.DEBUG
            settings.DEBUG = False

            try:
                with connection.cursor() as cursor:
                    query = """
                        SELECT DISTINCT ItemId
                        FROM tblDG_BOM_Master
                        WHERE WONo = ?
                        AND CompId = ?
                        AND ECNFlag = 0
                        AND CId NOT IN (
                            SELECT PId
                            FROM tblDG_BOM_Master
                            WHERE WONo = ?
                            AND CompId = ?
                            AND PId > 0
                        )
                    """
                    cursor.execute(query, [wono, comp_id, wono, comp_id])
                    item_ids = [row[0] for row in cursor.fetchall()]
            finally:
                settings.DEBUG = original_debug

            # Get item details for each item
            for item_id in item_ids:
                try:
                    # Get item master (line 170 in pdt.aspx.cs)
                    # FIXED: Removed cid__isnull=True filter - cid is category ID, not BOM CId
                    item = TbldgItemMaster.objects.get(id=item_id)

                    # Get unit symbol
                    unit_symbol = ''
                    if item.uombasic:
                        try:
                            unit = UnitMaster.objects.get(id=item.uombasic)
                            unit_symbol = unit.symbol
                        except:
                            pass

                    # Calculate BOM qty using AllComponentBOMQty equivalent
                    # This recursively walks the BOM tree (PId->CId relationships)
                    bom_qty = BOMService.all_component_bom_qty(comp_id, wono, item_id, fin_year_id)

                    # Calculate actual quantities (replaces placeholders)
                    pr_qty = BOMService.calc_pr_qty(comp_id, wono, item_id)      # fun.CalPRQty - line 202
                    wis_qty = BOMService.calc_wis_qty(comp_id, wono, item_id)    # fun.CalWISQty - line 205
                    gqn_qty = BOMService.calc_gqn_qty(comp_id, wono, item_id)    # fun.GQNQTY - line 208

                    # Calculate already planned quantities (pdt.aspx.cs lines 210-220)
                    # This prevents duplicate planning for the same item
                    raw_planned = BOMService.calc_planned_qty(wono, item_id, 'raw')
                    pro_planned = BOMService.calc_planned_qty(wono, item_id, 'process')
                    fin_planned = BOMService.calc_planned_qty(wono, item_id, 'finish')

                    # Calculate Available quantity (pdt.aspx.cs line 225-240)
                    # Formula: Available = BOMQty - PRQty - WISQty + GQNQty - RawPlanned - ProPlanned - FinPlanned
                    available = bom_qty - pr_qty - wis_qty + gqn_qty - raw_planned - pro_planned - fin_planned

                    # DEBUG: Print quantities for troubleshooting
                    print(f"DEBUG Item {item_id}: BOM={bom_qty}, PR={pr_qty}, WIS={wis_qty}, GQN={gqn_qty}, RawP={raw_planned}, ProP={pro_planned}, FinP={fin_planned}, Avail={available}")

                    # CRITICAL: Only show items with Available > 0 (pdt.aspx.cs line 240)
                    # This matches ASP.NET behavior where items fully planned are hidden
                    if available > 0:
                        items.append({
                            'item_id': item.id,
                            'item_code': item.itemcode or item.partno or '',
                            'description': item.manfdesc or '',
                            'uom': unit_symbol,
                            'bom_qty': bom_qty,
                            'pr_qty': pr_qty,
                            'wis_qty': wis_qty,
                            'gqn_qty': gqn_qty,
                            'raw_planned': raw_planned,
                            'pro_planned': pro_planned,
                            'fin_planned': fin_planned,
                            'available': available,
                        })
                except TbldgItemMaster.DoesNotExist:
                    # Item not found or CId is not null - skip it
                    continue
                except Exception as e:
                    # Error processing item - log and skip it
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing item {item_id} for WO {wono}: {e}", exc_info=True)
                    continue
        except Exception as e:
            # Log error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting BOM items for WO {wono}: {e}", exc_info=True)

        return items

    @staticmethod
    def all_component_bom_qty(comp_id, wono, item_id, fin_year_id):
        """
        Calculate total BOM quantity for an item by recursively walking the BOM tree.
        Replicates: clsFunctions.AllComponentBOMQty() from lines 2050-2071
        """
        # CRITICAL FIX: Disable DEBUG to avoid SQLite parameter formatting issues
        original_debug = settings.DEBUG
        settings.DEBUG = False

        total_qty = 0.0
        try:
            # Get all PId, CId pairs for this item
            with connection.cursor() as cursor:
                query = """
                    SELECT PId, CId
                    FROM tblDG_BOM_Master
                    WHERE WONo = ?
                    AND ItemId = ?
                    AND CompId = ?
                """
                cursor.execute(query, [wono, item_id, comp_id])
                rows = cursor.fetchall()

                print(f"DEBUG all_component_bom_qty: Item {item_id}, found {len(rows)} BOM records")

                # Recursively calculate quantity for each parent-child pair
                for row in rows:
                    pid, cid = row[0], row[1]
                    recur_qty = BOMService.bom_recur_qty(wono, pid, cid, 1.0, comp_id, fin_year_id)
                    print(f"DEBUG: PId={pid}, CId={cid} -> recur_qty={recur_qty}")
                    total_qty += recur_qty

            print(f"DEBUG all_component_bom_qty: Total={total_qty}")
            return round(total_qty, 5)
        except Exception as e:
            print(f"DEBUG all_component_bom_qty EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
        finally:
            settings.DEBUG = original_debug

    @staticmethod
    def bom_recur_qty(wono, pid, cid, parent_qty, comp_id, fin_year_id):
        """
        Recursively calculate BOM quantity by walking the parent-child tree.
        Replicates: clsFunctions.BOMRecurQty() from lines 2096-2125
        """
        # CRITICAL FIX: Disable DEBUG to avoid SQLite parameter formatting issues
        original_debug = settings.DEBUG
        settings.DEBUG = False

        try:
            # Get quantity for this PId->CId relationship
            with connection.cursor() as cursor:
                query = """
                    SELECT Qty
                    FROM tblDG_BOM_Master
                    WHERE WONo = ?
                    AND PId = ?
                    AND CId = ?
                    AND CompId = ?
                """
                cursor.execute(query, [wono, pid, cid, comp_id])
                result = cursor.fetchone()

                if not result:
                    return 0.0

                current_qty = float(result[0] or 0.0)
                total_qty = parent_qty * current_qty

                # Recursively get quantities for all children of this node
                query2 = """
                    SELECT PId, CId, Qty
                    FROM tblDG_BOM_Master
                    WHERE WONo = ?
                    AND PId = ?
                    AND CompId = ?
                """
                cursor.execute(query2, [wono, cid, comp_id])
                children = cursor.fetchall()

                for child in children:
                    child_pid, child_cid, child_qty = child[0], child[1], float(child[2] or 0.0)
                    total_qty += BOMService.bom_recur_qty(wono, child_pid, child_cid, parent_qty * current_qty, comp_id, fin_year_id)

                return total_qty
        except Exception as e:
            return 0.0
        finally:
            settings.DEBUG = original_debug

    @staticmethod
    def calc_pr_qty(comp_id, wono, item_id):
        """
        Calculate Purchase Requisition quantity for an item.
        Replicates: clsFunctions.CalPRQty() - referenced in pdt.aspx.cs line 202
        """
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT SUM(tblMM_PR_Details.Qty) AS PRQty
                    FROM tblMM_PR_Master
                    INNER JOIN tblMM_PR_Details ON tblMM_PR_Master.Id = tblMM_PR_Details.MId
                    WHERE tblMM_PR_Details.ItemId = ?
                    AND tblMM_PR_Master.WONo = ?
                    AND tblMM_PR_Master.CompId = ?
                """
                cursor.execute(query, [item_id, wono, comp_id])
                result = cursor.fetchone()
                return round(float(result[0] or 0.0), 5)
        except Exception as e:
            return 0.0

    @staticmethod
    def calc_wis_qty(comp_id, wono, item_id):
        """
        Calculate Work In Shop issued quantity for an item.
        Replicates: clsFunctions.CalWISQty() - referenced in pdt.aspx.cs line 205
        """
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT ISNULL(SUM(tblMM_WIS_Details.Qty), 0) AS WISQty
                    FROM tblMM_WIS_Master
                    INNER JOIN tblMM_WIS_Details ON tblMM_WIS_Master.Id = tblMM_WIS_Details.MId
                    WHERE tblMM_WIS_Details.ItemId = ?
                    AND tblMM_WIS_Master.WONo = ?
                    AND tblMM_WIS_Master.CompId = ?
                """
                cursor.execute(query, [item_id, wono, comp_id])
                result = cursor.fetchone()
                return round(float(result[0] or 0.0), 5)
        except Exception as e:
            return 0.0

    @staticmethod
    def calc_gqn_qty(comp_id, wono, item_id):
        """
        Calculate Goods Received Note quantity for an item.
        Replicates: clsFunctions.GQNQTY() - referenced in pdt.aspx.cs line 208

        Note: GQN/GRN is goods received back from shop floor or external processing.
        This reduces the requirement as material is already available.
        """
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT ISNULL(SUM(tblMM_GQN_Details.Qty), 0) AS GQNQty
                    FROM tblMM_GQN_Master
                    INNER JOIN tblMM_GQN_Details ON tblMM_GQN_Master.Id = tblMM_GQN_Details.MId
                    WHERE tblMM_GQN_Details.ItemId = ?
                    AND tblMM_GQN_Master.WONo = ?
                    AND tblMM_GQN_Master.CompId = ?
                """
                cursor.execute(query, [item_id, wono, comp_id])
                result = cursor.fetchone()
                return round(float(result[0] or 0.0), 5)
        except Exception as e:
            return 0.0

    @staticmethod
    def calc_planned_qty(wono, item_id, planning_type):
        """
        Calculate already planned quantity for an item to prevent duplicate planning.
        Replicates: pdt.aspx.cs lines 210-220

        Args:
            wono: Work order number
            item_id: Item ID
            planning_type: 'raw', 'process', or 'finish'

        Returns:
            Total quantity already planned for this item in this category
        """
        from material_planning.models import (
            TblmpMaterialDetail,
            TblmpMaterialRawmaterial,
            TblmpMaterialProcess,
            TblmpMaterialFinish,
        )

        try:
            # Get all plan details for this WO and item
            details = TblmpMaterialDetail.objects.filter(
                master__wono=wono,
                item=item_id
            )

            total_qty = 0.0

            if planning_type == 'raw':
                # Sum quantities from raw material records
                for detail in details.filter(rm=1):
                    raw_materials = TblmpMaterialRawmaterial.objects.filter(detail=detail)
                    total_qty += sum(rm.qty or 0.0 for rm in raw_materials)

            elif planning_type == 'process':
                # Sum quantities from process records
                for detail in details.filter(pro=1):
                    processes = TblmpMaterialProcess.objects.filter(detail=detail)
                    total_qty += sum(proc.qty or 0.0 for proc in processes)

            elif planning_type == 'finish':
                # Sum quantities from finish records
                for detail in details.filter(fin=1):
                    finishes = TblmpMaterialFinish.objects.filter(detail=detail)
                    total_qty += sum(fin.qty or 0.0 for fin in finishes)

            return round(total_qty, 5)
        except Exception as e:
            return 0.0

    @staticmethod
    def categorize_materials(bom_details):
        """
        Categorize BOM items into Raw Material, Process, or Finish based on procurement strategy.
        Replicates: pdt.aspx.cs lines 246-320

        Args:
            bom_details: List of BOM item dictionaries

        Returns:
            dict with keys 'raw_materials', 'processes', 'finishes' containing categorized items
        """
        raw_materials = []
        processes = []
        finishes = []

        for item in bom_details:
            item_id = item.get('item_id')

            try:
                item_obj = TbldgItemMaster.objects.get(id=item_id)

                # Check procurement strategy
                # A = Raw Material (Buy as-is)
                # O = Process (Outsource machining/processing)
                # F = Finish (Outsource finishing like coating)

                if item_obj.strategytype == 'A':
                    raw_materials.append(item)
                elif item_obj.strategytype == 'O':
                    processes.append(item)
                elif item_obj.strategytype == 'F':
                    finishes.append(item)
                else:
                    # Default to raw material if strategy not defined
                    raw_materials.append(item)

            except TbldgItemMaster.DoesNotExist:
                # Default to raw material if item not found
                raw_materials.append(item)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error categorizing item {item_id}: {e}")
                raw_materials.append(item)

        return {
            'raw_materials': raw_materials,
            'processes': processes,
            'finishes': finishes,
        }
