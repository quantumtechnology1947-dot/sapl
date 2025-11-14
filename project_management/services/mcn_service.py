"""
Material Credit Note (MCN) Service

Business logic for MCN processing, BOM validation, and material tracking.
Extracted from views.py for better separation of concerns.
"""

from datetime import datetime
from django.db.models import Sum
from django.db import models
from ..models import (
    TblpmMaterialcreditnoteMaster,
    TblpmMaterialcreditnoteDetails,
)


class MCNService:
    """Service class for Material Credit Note operations"""

    @staticmethod
    def enrich_work_orders_with_mcn_info(work_orders, compid):
        """
        Enrich work orders with customer and MCN information.

        Args:
            work_orders: QuerySet of SdCustWorkorderMaster objects
            compid: Company ID

        Returns:
            list: Enriched work order dictionaries with customer names and MCN status
        """
        from sales_distribution.models import SdCustMaster

        enriched_wos = []
        for wo in work_orders:
            # Get customer name
            customer = SdCustMaster.objects.filter(
                compid=compid,
                customerid=wo.customerid
            ).first()

            # Check if this WO has MCN
            mcn = TblpmMaterialcreditnoteMaster.objects.filter(
                compid=compid,
                wono=wo.wono
            ).first()

            enriched_wos.append({
                'id': wo.id,
                'wono': wo.wono,
                'date': wo.sysdate,
                'project_title': wo.taskprojecttitle or '-',
                'customer_name': customer.customername if customer else '-',
                'customer_code': wo.customerid,
                'has_mcn': mcn is not None,
                'mcn_id': mcn.id if mcn else None,
                'mcn_no': mcn.mcnno if mcn else None
            })

        return enriched_wos

    @staticmethod
    def get_bom_items_with_mcn_history(compid, wono):
        """
        Get BOM items for a work order with MCN history.

        Args:
            compid: Company ID
            wono: Work Order Number

        Returns:
            list: Enriched BOM items with MCN quantities
        """
        from design.models import TbldgBomMaster
        from sys_admin.models import UnitMaster

        # Get BOM items for this WO
        bom_items = TbldgBomMaster.objects.filter(
            compid=compid,
            wono=wono,
            pid=0  # Parent items only
        ).order_by('id')

        enriched_items = []
        for bom in bom_items:
            item = bom.itemid
            item_id_value = bom.itemid_id if bom.itemid else None

            # Get UOM symbol
            uom_symbol = '-'
            if item and item.uombasic:
                unit = UnitMaster.objects.filter(id=item.uombasic).first()
                if unit:
                    uom_symbol = unit.symbol or '-'

            # Get item code (ItemCode if CId is set, otherwise PartNo)
            item_code = '-'
            if item:
                if item.cid:
                    item_code = item.itemcode or '-'
                else:
                    item_code = item.partno or '-'

            # Calculate total MCN qty for this BOM item
            total_mcn_qty = MCNService.get_total_mcn_qty_for_bom(compid, wono, bom.id)

            enriched_items.append({
                'id': bom.id,
                'item_id': item_id_value or 0,
                'item_code': item_code,
                'description': item.manfdesc if item else '-',
                'uom': uom_symbol,
                'bom_qty': bom.qty or 0,
                'total_mcn_qty': total_mcn_qty,
                'mcn_qty': 0,  # To be filled by user
            })

        return enriched_items

    @staticmethod
    def get_total_mcn_qty_for_bom(compid, wono, bom_id):
        """
        Calculate total MCN quantity for a specific BOM item.

        Args:
            compid: Company ID
            wono: Work Order Number
            bom_id: BOM item ID

        Returns:
            float: Total MCN quantity across all MCNs for this BOM item
        """
        # Find all MCN Masters for this WO
        mcn_masters = TblpmMaterialcreditnoteMaster.objects.filter(
            compid=compid,
            wono=wono
        ).values_list('id', flat=True)

        # Sum up mcnqty for this BOM id from all MCN details
        total_mcn_qty = TblpmMaterialcreditnoteDetails.objects.filter(
            mid_id__in=mcn_masters,
            pid=bom_id
        ).aggregate(total=models.Sum('mcnqty'))['total'] or 0

        return float(total_mcn_qty)

    @staticmethod
    def validate_mcn_quantities(request_post, compid, wono):
        """
        Validate MCN quantities against BOM quantities.
        Based on ASP.NET MaterialCreditNote_MCN_New_Details.aspx validation logic.

        Args:
            request_post: POST data containing mcn_qty_* fields
            compid: Company ID
            wono: Work Order Number

        Returns:
            tuple: (is_valid, bom_data, count, k)
                - is_valid: Boolean indicating if all items pass validation
                - bom_data: Dict mapping item_id to BOM info
                - count: Total items with valid quantity
                - k: Items that pass validation
        """
        from design.models import TbldgBomMaster

        # Get BOM items for validation
        bom_items = TbldgBomMaster.objects.filter(
            compid=compid,
            wono=wono,
            pid=0
        )

        # Create mappings for validation
        bom_data = {}
        for bom in bom_items:
            if bom.itemid_id:
                item_id_str = str(bom.itemid_id)
                total_mcn_qty = MCNService.get_total_mcn_qty_for_bom(compid, wono, bom.id)

                bom_data[item_id_str] = {
                    'bom_id': bom.id,
                    'bom_qty': float(bom.qty or 0),
                    'total_mcn_qty': float(total_mcn_qty)
                }

        # Validation phase
        count = 0  # Total items with valid quantity
        k = 0      # Items that pass validation

        for key, value in request_post.items():
            if key.startswith('mcn_qty_'):
                item_id = key.replace('mcn_qty_', '')
                qty_str = value.strip()

                if qty_str:
                    try:
                        mcn_qty = float(qty_str)
                        if mcn_qty > 0:
                            count += 1

                            if item_id in bom_data:
                                bom_qty = bom_data[item_id]['bom_qty']
                                # Validation: MCN qty should not exceed BOM qty
                                if (bom_qty - mcn_qty) >= 0:
                                    k += 1
                    except ValueError:
                        pass

        is_valid = (count - k) == 0 and count > 0
        return is_valid, bom_data, count, k

    @staticmethod
    def generate_next_mcn_number(compid, finyearid):
        """
        Auto-generate next MCN number.

        Args:
            compid: Company ID
            finyearid: Financial Year ID

        Returns:
            str: Next MCN number (zero-padded to 4 digits)
        """
        last_mcn = TblpmMaterialcreditnoteMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-id').first()

        if last_mcn and last_mcn.mcnno:
            try:
                next_num = int(last_mcn.mcnno) + 1
                return str(next_num).zfill(4)
            except Exception:
                return '0001'
        else:
            return '0001'

    @staticmethod
    def create_mcn_with_details(compid, finyearid, sessionid, wono, bom_data, request_post):
        """
        Create MCN master and detail records.

        Args:
            compid: Company ID
            finyearid: Financial Year ID
            sessionid: Session ID
            wono: Work Order Number
            bom_data: Dict mapping item_id to BOM info
            request_post: POST data containing mcn_qty_* fields

        Returns:
            tuple: (mcn_master, saved_count)
        """
        # Generate MCN number
        mcnno = MCNService.generate_next_mcn_number(compid, finyearid)

        # Create MCN Master record
        mcn_master = TblpmMaterialcreditnoteMaster()
        mcn_master.compid = compid
        mcn_master.finyearid = finyearid
        mcn_master.sessionid = sessionid
        mcn_master.sysdate = datetime.now().strftime('%Y-%m-%d')
        mcn_master.systime = datetime.now().strftime('%H:%M:%S')
        mcn_master.mcnno = mcnno
        mcn_master.wono = wono
        mcn_master.save()

        # Save MCN detail lines
        saved_count = 0
        for key, value in request_post.items():
            if key.startswith('mcn_qty_'):
                item_id = key.replace('mcn_qty_', '')
                qty_str = value.strip()

                if qty_str:
                    try:
                        mcn_qty = float(qty_str)

                        if mcn_qty > 0 and item_id in bom_data:
                            bom_qty = bom_data[item_id]['bom_qty']

                            if (bom_qty - mcn_qty) >= 0:
                                detail = TblpmMaterialcreditnoteDetails()
                                detail.mid_id = mcn_master.id
                                detail.pid = bom_data[item_id]['bom_id']
                                detail.cid = 0  # Parent items have CId = 0
                                detail.mcnqty = mcn_qty
                                detail.save()
                                saved_count += 1
                    except ValueError:
                        pass

        return mcn_master, saved_count

    @staticmethod
    def get_mcn_details(mcn):
        """
        Get all detail records for an MCN.

        Args:
            mcn: TblpmMaterialcreditnoteMaster instance

        Returns:
            QuerySet: TblpmMaterialcreditnoteDetails for this MCN
        """
        return TblpmMaterialcreditnoteDetails.objects.filter(mid=mcn)
