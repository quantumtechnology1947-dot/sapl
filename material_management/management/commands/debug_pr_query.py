"""
Debug PR query to see what's being filtered out
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Debug PR query for PRTEST01'

    def handle(self, *args, **options):
        wo_no = 'PRTEST01'
        compid = 1
        finyearid = 4
        
        self.stdout.write(self.style.SUCCESS(f'Debugging PR query for {wo_no}...'))
        
        # Check BOM entries
        cursor = connection.cursor()
        cursor.execute(f"""
            SELECT 
                tblDG_BOM_Master.Id,
                tblDG_BOM_Master.WONo,
                tblDG_BOM_Master.ItemId,
                tblDG_BOM_Master.CId,
                tblDG_BOM_Master.PId,
                tblDG_BOM_Master.Qty,
                tblDG_BOM_Master.ECNFlag,
                tblDG_Item_Master.ItemCode,
                tblDG_Item_Master.CId as ItemCId
            FROM tblDG_BOM_Master
            LEFT JOIN tblDG_Item_Master ON tblDG_Item_Master.Id = tblDG_BOM_Master.ItemId
            WHERE tblDG_BOM_Master.WONo = '{wo_no}'
            AND tblDG_BOM_Master.CompId = {compid}
        """)
        
        rows = cursor.fetchall()
        self.stdout.write(f'\nFound {len(rows)} BOM entries:')
        for row in rows:
            self.stdout.write(f'  BOM ID: {row[0]}, Item: {row[7]}, BOM.CId: {row[3]}, BOM.PId: {row[4]}, Item.CId: {row[8]}, Qty: {row[5]}, ECNFlag: {row[6]}')
        
        # Check which CIds are used as PIds (these get excluded)
        cursor.execute(f"""
            SELECT DISTINCT PId 
            FROM tblDG_BOM_Master 
            WHERE WONo = '{wo_no}' 
            AND CompId = {compid}
            AND FinYearId <= {finyearid}
        """)
        
        pids = [row[0] for row in cursor.fetchall()]
        self.stdout.write(f'\nPIds that will exclude items: {pids}')
        
        # Now run the actual PR query
        cursor.execute(f"""
            SELECT DISTINCT
                tblDG_Item_Master.Id as ItemId,
                tblDG_Item_Master.ItemCode,
                tblDG_Item_Master.ManfDesc,
                tblDG_Item_Master.CId as ItemCategoryId
            FROM tblDG_BOM_Master
            INNER JOIN tblDG_Item_Master ON tblDG_Item_Master.Id = tblDG_BOM_Master.ItemId
            WHERE tblDG_BOM_Master.WONo = '{wo_no}'
            AND tblDG_BOM_Master.CompId = {compid}
            AND tblDG_BOM_Master.ECNFlag = 0
            AND tblDG_Item_Master.CId IS NOT NULL
            AND tblDG_BOM_Master.CId NOT IN ({','.join(map(str, pids)) if pids else '0'})
            LIMIT 10
        """)
        
        items = cursor.fetchall()
        self.stdout.write(f'\n✓ Items that pass all filters: {len(items)}')
        for item in items:
            self.stdout.write(f'  Item: {item[1]} - {item[2][:50]}')
        
        if not items:
            self.stdout.write(self.style.WARNING('\n⚠ No items found! Checking each filter:'))
            
            # Check without CId NOT IN filter
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM tblDG_BOM_Master
                INNER JOIN tblDG_Item_Master ON tblDG_Item_Master.Id = tblDG_BOM_Master.ItemId
                WHERE tblDG_BOM_Master.WONo = '{wo_no}'
                AND tblDG_BOM_Master.CompId = {compid}
                AND tblDG_BOM_Master.ECNFlag = 0
                AND tblDG_Item_Master.CId IS NOT NULL
            """)
            count = cursor.fetchone()[0]
            self.stdout.write(f'  Without CId NOT IN filter: {count} items')
            
            # Check which items are being excluded by CId NOT IN
            cursor.execute(f"""
                SELECT 
                    tblDG_Item_Master.ItemCode,
                    tblDG_BOM_Master.CId
                FROM tblDG_BOM_Master
                INNER JOIN tblDG_Item_Master ON tblDG_Item_Master.Id = tblDG_BOM_Master.ItemId
                WHERE tblDG_BOM_Master.WONo = '{wo_no}'
                AND tblDG_BOM_Master.CompId = {compid}
                AND tblDG_BOM_Master.ECNFlag = 0
                AND tblDG_Item_Master.CId IS NOT NULL
                AND tblDG_BOM_Master.CId IN ({','.join(map(str, pids)) if pids else '0'})
            """)
            excluded = cursor.fetchall()
            if excluded:
                self.stdout.write(f'  Items excluded by CId NOT IN filter:')
                for item in excluded:
                    self.stdout.write(f'    {item[0]} (BOM.CId={item[1]} is in PId list)')
