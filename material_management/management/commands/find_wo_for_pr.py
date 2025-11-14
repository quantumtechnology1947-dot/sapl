"""
Find a work order suitable for PR creation testing
This command finds work orders that have bought-out items with shortages
"""
from django.core.management.base import BaseCommand
from django.db import connection
from design.models import TbldgBomMaster, TbldgItemMaster
from sales_distribution.models import SdCustWorkorderMaster


class Command(BaseCommand):
    help = 'Find work orders with bought-out items suitable for PR creation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Searching for work orders with bought-out items...'))
        
        # Get all work orders with BOM
        work_orders = TbldgBomMaster.objects.filter(
            compid=1,
            finyearid__lte=4
        ).values_list('wono', flat=True).distinct()[:50]
        
        self.stdout.write(f"Found {len(work_orders)} work orders with BOM")
        
        suitable_wos = []
        
        for wo_no in work_orders:
            # Check if this WO has bought-out items (items with CId)
            bom_items = TbldgBomMaster.objects.filter(
                wono=wo_no,
                compid=1,
                ecnflag=0
            ).select_related('itemid')
            
            bought_out_count = 0
            for bom_item in bom_items:
                if bom_item.itemid and bom_item.itemid.cid:
                    bought_out_count += 1
            
            if bought_out_count > 0:
                suitable_wos.append({
                    'wo_no': wo_no,
                    'bought_out_items': bought_out_count
                })
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ {wo_no}: {bought_out_count} bought-out items"
                    )
                )
        
        if suitable_wos:
            self.stdout.write(self.style.SUCCESS(f"\n✓ Found {len(suitable_wos)} suitable work orders!"))
            self.stdout.write(self.style.SUCCESS(f"\nBest candidate: {suitable_wos[0]['wo_no']}"))
            self.stdout.write(self.style.SUCCESS(f"URL: http://localhost:8000/material-management/pr/new/{suitable_wos[0]['wo_no']}/"))
        else:
            self.stdout.write(self.style.WARNING("\n⚠ No work orders found with bought-out items"))
            self.stdout.write(self.style.WARNING("Creating test data..."))
            self.create_test_data()
    
    def create_test_data(self):
        """Create test work order with bought-out items"""
        self.stdout.write("Creating test work order with bought-out items...")
        
        # Find or create a test work order
        wo, created = SdCustWorkorderMaster.objects.get_or_create(
            wono='TEST001',
            compid=1,
            finyearid=4,
            defaults={
                'custcode': 'C001',
                'projecttitle': 'Test Project for PR',
                'wocategory': 'T',
                'releaseflag': 1,
                'wisflag': 1
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Created work order: TEST001"))
        
        # Find bought-out items (items with category)
        bought_out_items = TbldgItemMaster.objects.filter(
            compid=1,
            cid__isnull=False
        )[:5]
        
        if not bought_out_items:
            self.stdout.write(self.style.ERROR("✗ No bought-out items found in item master"))
            return
        
        # Create BOM entries for these items
        for idx, item in enumerate(bought_out_items, 1):
            bom, created = TbldgBomMaster.objects.get_or_create(
                wono='TEST001',
                itemid=item,
                compid=1,
                finyearid=4,
                defaults={
                    'qty': 10.0 * idx,
                    'pid': 0,
                    'cid': 0,
                    'ecnflag': 0,
                    'level': 1
                }
            )
            if created:
                self.stdout.write(f"  ✓ Added {item.itemcode} - {item.manfdesc}")
        
        self.stdout.write(self.style.SUCCESS(f"\n✓ Test data created!"))
        self.stdout.write(self.style.SUCCESS(f"URL: http://localhost:8000/material-management/pr/new/TEST001/"))
