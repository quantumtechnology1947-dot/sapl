"""
Planning Service - Business Logic for Material Planning Operations

Extracted from material_planning/views.py
Handles temp table management, plan generation, PLN number generation, and session-based workflow.
"""

from datetime import datetime
from django.db import transaction
from sys_admin.models import TblfinancialMaster
from material_planning.models import (
    TblmpMaterialMaster,
    TblmpMaterialDetail,
    TblmpMaterialRawmaterial,
    TblmpMaterialProcess,
    TblmpMaterialFinish,
    TblmpMaterialDetailTemp,
    TblmpMaterialRawmaterialTemp,
    TblmpMaterialProcessTemp,
    TblmpMaterialFinishTemp,
)


class PlanningService:
    """
    Service for Material Planning operations.

    Provides methods for:
    - Temporary table management (session-based multi-user isolation)
    - Plan generation and PLN number generation
    - Temp to permanent migration workflow
    """

    @staticmethod
    def cleanup_temp_tables(user_id):
        """
        Clear temporary planning tables for a specific user session.
        Replicates: pdt.aspx.cs Page_Load lines 95-122

        Called at page load to prevent stale data from previous sessions.
        Multi-user safe through sessionid isolation.
        """
        try:
            # Delete in reverse order (quotes first, then details)
            TblmpMaterialRawmaterialTemp.objects.filter(sessionid=user_id).delete()
            TblmpMaterialProcessTemp.objects.filter(sessionid=user_id).delete()
            TblmpMaterialFinishTemp.objects.filter(sessionid=user_id).delete()
            TblmpMaterialDetailTemp.objects.filter(sessionid=user_id).delete()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error cleaning up temp tables for user {user_id}: {e}", exc_info=True)

    @staticmethod
    def add_to_temp(wono, item_id, bom_qty, available, rm_data, pro_data, fin_data, user_id, compid, finyearid):
        """
        Save procurement data to temporary tables (Add to Temp button).
        Replicates: pdt.aspx.cs btnAddToTemp_Click (lines 402-500)

        Workflow:
        1. User selects an item from BOM grid
        2. User selects procurement strategy (RM/Process/Finish)
        3. User enters supplier quotes in grid
        4. Click "Add to Temp" → Save to temp tables
        5. Repeat for other items
        6. Click "Generate PLN" → Migrate temp → permanent

        Args:
            wono: Work order number
            item_id: Item ID
            bom_qty: BOM quantity
            available: Available quantity
            rm_data: List of dicts with keys: supplier, qty, rate, discount, deldate
            pro_data: List of dicts with keys: supplier, qty, rate, discount, deldate
            fin_data: List of dicts with keys: supplier, qty, rate, discount, deldate
            user_id: Session ID for multi-user isolation
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            dict with status, message, detail_temp_ids, saved_count
        """
        now = datetime.now()
        sysdate = now.strftime('%d-%m-%Y')
        systime = now.strftime('%H:%M:%S')

        saved_count = 0
        detail_temp_ids = []

        try:
            # Step 1: Process Raw Material [A] if provided
            if rm_data:
                # Create detail temp with RM flag
                detail_temp = TblmpMaterialDetailTemp.objects.create(
                    wono=wono,
                    item=int(item_id),
                    bomqty=float(bom_qty) if bom_qty else 0,
                    available=float(available) if available else 0,
                    sessionid=user_id,
                    compid=compid,
                    finyearid=finyearid,
                    sysdate=sysdate,
                    systime=systime
                )
                detail_temp_ids.append(detail_temp.id)

                # Save supplier quotes
                for quote in rm_data:
                    if quote.get('supplier') and quote['supplier'].strip():
                        qty = float(quote.get('qty', 0))
                        rate = float(quote.get('rate', 0))
                        discount = float(quote.get('discount', 0))
                        total = (qty * rate) - discount

                        TblmpMaterialRawmaterialTemp.objects.create(
                            dmid=detail_temp.id,
                            supplier=quote['supplier'],
                            qty=qty,
                            rate=rate,
                            discount=discount,
                            deliverydate=quote.get('deldate', ''),
                            total=total,
                            sessionid=user_id
                        )
                        saved_count += 1

            # Step 2: Process Process [O] if provided
            if pro_data:
                # Create detail temp with PRO flag
                detail_temp = TblmpMaterialDetailTemp.objects.create(
                    wono=wono,
                    item=int(item_id),
                    bomqty=float(bom_qty) if bom_qty else 0,
                    available=float(available) if available else 0,
                    sessionid=user_id,
                    compid=compid,
                    finyearid=finyearid,
                    sysdate=sysdate,
                    systime=systime
                )
                detail_temp_ids.append(detail_temp.id)

                # Save supplier quotes
                for quote in pro_data:
                    if quote.get('supplier') and quote['supplier'].strip():
                        qty = float(quote.get('qty', 0))
                        rate = float(quote.get('rate', 0))
                        discount = float(quote.get('discount', 0))
                        total = (qty * rate) - discount

                        TblmpMaterialProcessTemp.objects.create(
                            dmid=detail_temp.id,
                            supplier=quote['supplier'],
                            qty=qty,
                            rate=rate,
                            discount=discount,
                            deliverydate=quote.get('deldate', ''),
                            total=total,
                            sessionid=user_id
                        )
                        saved_count += 1

            # Step 3: Process Finish [F] if provided
            if fin_data:
                # Create detail temp with FIN flag
                detail_temp = TblmpMaterialDetailTemp.objects.create(
                    wono=wono,
                    item=int(item_id),
                    bomqty=float(bom_qty) if bom_qty else 0,
                    available=float(available) if available else 0,
                    sessionid=user_id,
                    compid=compid,
                    finyearid=finyearid,
                    sysdate=sysdate,
                    systime=systime
                )
                detail_temp_ids.append(detail_temp.id)

                # Save supplier quotes
                for quote in fin_data:
                    if quote.get('supplier') and quote['supplier'].strip():
                        qty = float(quote.get('qty', 0))
                        rate = float(quote.get('rate', 0))
                        discount = float(quote.get('discount', 0))
                        total = (qty * rate) - discount

                        TblmpMaterialFinishTemp.objects.create(
                            dmid=detail_temp.id,
                            supplier=quote['supplier'],
                            qty=qty,
                            rate=rate,
                            discount=discount,
                            deliverydate=quote.get('deldate', ''),
                            total=total,
                            sessionid=user_id
                        )
                        saved_count += 1

            return {
                'status': 'success',
                'message': f'Added to temporary planning ({saved_count} supplier quotes saved)',
                'detail_temp_ids': detail_temp_ids,
                'saved_count': saved_count
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in add_to_temp: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }

    @staticmethod
    def generate_pln_from_temp(wono, user_id, compid, finyearid):
        """
        Generate PLN from temporary tables (Generate PLN button).
        Replicates: pdt.aspx.cs btnGenerate_Click (lines 502-650)

        Workflow:
        1. Generate PLN number in format PLN/YYYY-YY/XXXX
        2. Get all temp detail records for current user
        3. For each temp detail:
           - Create permanent detail record
           - Check which temp table has quotes (RM/Process/Finish)
           - Copy quotes to permanent table
           - Set RM='A' or PRO='O' or FIN='F' flag
        4. Create master record with PLN number
        5. Delete all temp records for user

        Args:
            wono: Work order number
            user_id: Session ID for multi-user isolation
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            dict with status, message, pln_no, plan_id, redirect_url
        """
        try:
            now = datetime.now()
            sysdate = now.strftime('%d-%m-%Y')
            systime = now.strftime('%H:%M:%S')

            # Step 1: Generate PLN number
            pln_no = PlanningService.generate_pln_number(compid, finyearid)

            # Step 2: Atomic transaction
            with transaction.atomic():
                # Get all temp detail records for this user and WO
                temp_details = TblmpMaterialDetailTemp.objects.filter(
                    sessionid=user_id,
                    wono=wono
                )

                if not temp_details.exists():
                    return {
                        'status': 'error',
                        'message': 'No temporary data found. Please add items to temp first.'
                    }

                # Step 3: Create master record first
                master = TblmpMaterialMaster.objects.create(
                    plno=pln_no,
                    wono=wono,
                    sysdate=sysdate,
                    systime=systime,
                    sessionid=user_id,
                    compid=compid,
                    finyearid=finyearid
                )

                # Step 4: Process each temp detail record
                for temp_detail in temp_details:
                    # Create permanent detail record
                    # Note: TblmpMaterialDetail only has: id, item, rm, pro, fin, master
                    perm_detail = TblmpMaterialDetail.objects.create(
                        master=master,  # Link to master record
                        item=temp_detail.item,
                        # RM/PRO/FIN flags will be set below based on which temp tables have data
                        rm=None,
                        pro=None,
                        fin=None
                    )

                    # Check which temp table has quotes and copy them

                    # Raw Material?
                    raw_temps = TblmpMaterialRawmaterialTemp.objects.filter(
                        dmid=temp_detail.id,
                        sessionid=user_id
                    )
                    if raw_temps.exists():
                        # Set RM flag (IntegerField: 1 = true, NULL = false)
                        perm_detail.rm = 1
                        perm_detail.save()

                        # Copy all raw material rows
                        for raw_temp in raw_temps:
                            TblmpMaterialRawmaterial.objects.create(
                                detail=perm_detail,  # Foreign key to TblmpMaterialDetail
                                item=temp_detail.item,
                                supplierid=raw_temp.supplier,
                                qty=raw_temp.qty,
                                rate=raw_temp.rate,
                                discount=raw_temp.discount,
                                deldate=raw_temp.deliverydate
                            )

                    # Process?
                    pro_temps = TblmpMaterialProcessTemp.objects.filter(
                        dmid=temp_detail.id,
                        sessionid=user_id
                    )
                    if pro_temps.exists():
                        # Set PRO flag (IntegerField: 1 = true, NULL = false)
                        perm_detail.pro = 1
                        perm_detail.save()

                        # Copy all process rows
                        for pro_temp in pro_temps:
                            TblmpMaterialProcess.objects.create(
                                detail=perm_detail,  # Foreign key to TblmpMaterialDetail
                                item=temp_detail.item,
                                supplierid=pro_temp.supplier,
                                qty=pro_temp.qty,
                                rate=pro_temp.rate,
                                discount=pro_temp.discount,
                                deldate=pro_temp.deliverydate
                            )

                    # Finish?
                    fin_temps = TblmpMaterialFinishTemp.objects.filter(
                        dmid=temp_detail.id,
                        sessionid=user_id
                    )
                    if fin_temps.exists():
                        # Set FIN flag (IntegerField: 1 = true, NULL = false)
                        perm_detail.fin = 1
                        perm_detail.save()

                        # Copy all finish rows
                        for fin_temp in fin_temps:
                            TblmpMaterialFinish.objects.create(
                                detail=perm_detail,  # Foreign key to TblmpMaterialDetail
                                item=temp_detail.item,
                                supplierid=fin_temp.supplier,
                                qty=fin_temp.qty,
                                rate=fin_temp.rate,
                                discount=fin_temp.discount,
                                deldate=fin_temp.deliverydate
                            )

                # Step 5: Delete all temp records for this user
                # Delete in reverse order (quotes first, then details)
                TblmpMaterialRawmaterialTemp.objects.filter(sessionid=user_id).delete()
                TblmpMaterialProcessTemp.objects.filter(sessionid=user_id).delete()
                TblmpMaterialFinishTemp.objects.filter(sessionid=user_id).delete()
                TblmpMaterialDetailTemp.objects.filter(sessionid=user_id).delete()

            # Redirect to plan list instead of detail page to avoid URL encoding issues
            # Plan numbers contain slashes (PLN/2013-14/0001) which cause routing problems
            return {
                'status': 'success',
                'message': f'PLN {pln_no} generated successfully',
                'pln_no': pln_no,
                'plan_id': master.id,
                'redirect_url': '/material-planning/plans/'  # Redirect to plan list page
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in generate_pln_from_temp: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }

    @staticmethod
    def generate_pln_number(compid, finyearid):
        """
        Generate PLN number in format: PLN/YYYY-YY/XXXX
        Converted from: pdt.aspx.cs GeneratePLNNumber (lines 652-680)

        Example: PLN/2024-25/0016

        Args:
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            str: Generated PLN number
        """
        # Get financial year
        finyear = TblfinancialMaster.objects.get(finyearid=finyearid)
        start_year = finyear.startyear if hasattr(finyear, 'startyear') else finyear.finyear.split('-')[0]
        end_year = finyear.endyear if hasattr(finyear, 'endyear') else finyear.finyear.split('-')[1]

        # Get last 2 digits of end year
        if isinstance(end_year, int):
            end_year_short = str(end_year)[-2:]
        else:
            end_year_short = str(end_year)[-2:]

        # Get last PLN number for this company and fin year
        last_pln = TblmpMaterialMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-id').first()

        if last_pln and last_pln.plno:
            # Extract sequence from "PLN/2024-25/0015"
            try:
                parts = last_pln.plno.split('/')
                last_seq = int(parts[2]) if len(parts) == 3 else 0
                next_seq = last_seq + 1
            except (IndexError, ValueError):
                next_seq = 1
        else:
            next_seq = 1

        # Format: PLN/YYYY-YY/XXXX
        pln_no = f"PLN/{start_year}-{end_year_short}/{next_seq:04d}"
        return pln_no

    @staticmethod
    def get_temp_items_summary(user_id, wono):
        """
        Get summary of items currently in temp tables for display.
        Used to show user what's pending before generating PLN.

        Args:
            user_id: Session ID for multi-user isolation
            wono: Work order number (optional filter)

        Returns:
            List of dicts with item details and procurement types
        """
        from design.models import TbldgItemMaster

        temp_details = TblmpMaterialDetailTemp.objects.filter(sessionid=user_id)
        if wono:
            temp_details = temp_details.filter(wono=wono)

        items = []
        for temp_detail in temp_details:
            # Get item details
            try:
                item = TbldgItemMaster.objects.get(id=temp_detail.item)
                item_code = item.itemcode or item.partno or ''
                description = item.manfdesc or ''
            except:
                item_code = f'Item {temp_detail.item}'
                description = 'N/A'

            # Check which procurement types have quotes
            has_rm = TblmpMaterialRawmaterialTemp.objects.filter(
                dmid=temp_detail.id, sessionid=user_id
            ).exists()
            has_pro = TblmpMaterialProcessTemp.objects.filter(
                dmid=temp_detail.id, sessionid=user_id
            ).exists()
            has_fin = TblmpMaterialFinishTemp.objects.filter(
                dmid=temp_detail.id, sessionid=user_id
            ).exists()

            procurement_types = []
            if has_rm:
                procurement_types.append('Raw Material')
            if has_pro:
                procurement_types.append('Process')
            if has_fin:
                procurement_types.append('Finish')

            items.append({
                'item_id': temp_detail.item,
                'item_code': item_code,
                'description': description,
                'bom_qty': temp_detail.bomqty,
                'available': temp_detail.available,
                'procurement_types': ', '.join(procurement_types),
                'temp_detail_id': temp_detail.id
            })

        return items
