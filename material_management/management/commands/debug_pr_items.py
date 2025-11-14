"""
Debug command to check why PR items are not showing
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Debug PR items query for a work order'

    def add_arguments(self, parser):
        parser.add_argument('wo_no', type=str, help='Work Order Number')
        parser.add_argument('--compid', type=int, default=1, help='Company ID')
        parser.add_argument('--finyearid', type=int, default=15, help='Financial Year ID')

    def handle(self, *args, **options):
        wo_no = options['wo_no']
        compid = options['compid']
        finyearid = options['finyearid']

        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(f"Debugging PR Items for WO: {wo_no}")
        self.stdout.write(f"CompId: {compid}, FinYearId: {finyearid}")
        self.stdout.write(f"{'='*80}\n")

        cursor = connection.cursor()

        # Step 1: Check if work order exists
        self.stdout.write("\n1. Checking Work Order...")
        cursor.execute("""
            SELECT WONo, WODate, ProductId, Qty 
            FROM tblSD_WO_Master 
            WHERE WONo = %s AND CompId = %s
        """, [wo_no, compid])
        wo_result = cursor.fetchone()
        if wo_result:
            self.stdout.write(self.style.SUCCESS(f"   ✓ Work Order found: {wo_result}"))
        else:
            self.stdout.write(self.style.ERROR(f"   ✗ Work Order NOT found!"))
            return

        # Step 2: Check BOM entries for this WO
        self.stdout.write("\n2. Checking BOM entries...")
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN ECNFlag = 0 THEN 1 ELSE 0 END) as active
            FROM tblDG_BOM_Master 
            WHERE WONo = %s AND CompId = %s
        """, [wo_no, compid])
        bom_count = cursor.fetchone()
        self.stdout.write(f"   Total BOM entries: {bom_count[0]}, Active (ECNFlag=0): {bom_count[1]}")

        # Step 3: Check items with CId (bought-out items)
        self.stdout.write("\n3. Checking bought-out items (CId IS NOT NULL)...")
        cursor.execute("""
            SELECT 
                bom.Id,
                bom.ItemId,
                item.ItemCode,
                item.ManfDesc,
                item.CId,
                bom.Qty,
                bom.ECNFlag
            FROM tblDG_BOM_Master bom
            INNER JOIN tblDG_Item_Master item ON item.Id = bom.ItemId
            WHERE bom.WONo = %s 
            AND bom.CompId = %s
            AND bom.ECNFlag = 0
            AND item.CId IS NOT NULL
            ORDER BY item.ItemCode
            LIMIT 20
        """, [wo_no, compid])
        
        bought_out_items = cursor.fetchall()
        if bought_out_items:
            self.stdout.write(self.style.SUCCESS(f"   ✓ Found {len(bought_out_items)} bought-out items:"))
            for item in bought_out_items:
                self.stdout.write(f"      - {item[2]} | {item[3][:50]} | Qty: {item[5]} | CId: {item[4]}")
        else:
            self.stdout.write(self.style.WARNING("   ⚠ No bought-out items found!"))

        # Step 4: Check all items (including assemblies)
        self.stdout.write("\n4. Checking ALL items in BOM...")
        cursor.execute("""
            SELECT 
                item.ItemCode,
                item.ManfDesc,
                item.CId,
                bom.Qty,
                CASE WHEN item.CId IS NULL THEN 'Assembly' ELSE 'Bought-Out' END as Type
            FROM tblDG_BOM_Master bom
            INNER JOIN tblDG_Item_Master item ON item.Id = bom.ItemId
            WHERE bom.WONo = %s 
            AND bom.CompId = %s
            AND bom.ECNFlag = 0
            ORDER BY Type, item.ItemCode
            LIMIT 20
        """, [wo_no, compid])
        
        all_items = cursor.fetchall()
        if all_items:
            self.stdout.write(f"   Found {len(all_items)} total items:")
            for item in all_items:
                self.stdout.write(f"      - {item[0]} | {item[1][:40]} | Type: {item[4]} | Qty: {item[3]}")
        else:
            self.stdout.write(self.style.ERROR("   ✗ No items found in BOM!"))

        # Step 5: Run the actual PR query
        self.stdout.write("\n5. Running actual PR query...")
        sql = f"""
            SELECT DISTINCT
                tblDG_Item_Master.Id as ItemId,
                tblDG_Item_Master.ItemCode,
                tblDG_Item_Master.ManfDesc,
                Unit_Master.Symbol As UOMBasic,
                COALESCE((SELECT SUM(Qty) FROM tblDG_BOM_Master bom2
                          WHERE bom2.ItemId = tblDG_Item_Master.Id
                          AND bom2.WONo = '{wo_no}'
                          AND bom2.CompId = {compid}), 0) as BOMQty
            FROM tblDG_BOM_Master
            INNER JOIN tblDG_Item_Master ON tblDG_Item_Master.Id = tblDG_BOM_Master.ItemId
            INNER JOIN Unit_Master ON Unit_Master.Id = tblDG_Item_Master.UOMBasic
            WHERE tblDG_BOM_Master.WONo = '{wo_no}'
            AND tblDG_BOM_Master.CompId = {compid}
            AND tblDG_BOM_Master.ECNFlag = 0
            AND tblDG_Item_Master.CId IS NOT NULL
            ORDER BY tblDG_Item_Master.ItemCode
            LIMIT 10
        """
        
        cursor.execute(sql)
        pr_items = cursor.fetchall()
        
        if pr_items:
            self.stdout.write(self.style.SUCCESS(f"   ✓ PR Query returned {len(pr_items)} items:"))
            for item in pr_items:
                self.stdout.write(f"      - {item[1]} | {item[2][:50]} | BOM Qty: {item[4]}")
        else:
            self.stdout.write(self.style.ERROR("   ✗ PR Query returned NO items!"))

        # Step 6: Check if CId constraint is the issue
        self.stdout.write("\n6. Testing without CId constraint...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM tblDG_BOM_Master bom
            INNER JOIN tblDG_Item_Master item ON item.Id = bom.ItemId
            WHERE bom.WONo = %s 
            AND bom.CompId = %s
            AND bom.ECNFlag = 0
        """, [wo_no, compid])
        total_without_cid = cursor.fetchone()[0]
        self.stdout.write(f"   Items without CId filter: {total_without_cid}")

        self.stdout.write(f"\n{'='*80}")
        self.stdout.write("Debug complete!")
        self.stdout.write(f"{'='*80}\n")
