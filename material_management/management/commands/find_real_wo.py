"""
Find real work orders that have BOM data
"""
from django.core.management.base import BaseCommand
from sales_distribution.models import SdCustWorkorderMaster
from design.models import TbldgBomMaster
from django.db.models import Count


class Command(BaseCommand):
    help = 'Find work orders with BOM data for PR testing'

    def handle(self, *args, **options):
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write("Finding Work Orders with BOM Data")
        self.stdout.write(f"{'='*80}\n")

        # Find work orders with BOM entries
        work_orders = SdCustWorkorderMaster.objects.filter(
            compid=1
        ).order_by('-taskworkorderdate')[:20]

        self.stdout.write(f"Found {work_orders.count()} recent work orders\n")

        for wo in work_orders:
            # Count BOM entries for this WO
            bom_count = TbldgBomMaster.objects.filter(
                wono=wo.wono,
                compid=wo.compid,
                ecnflag=0
            ).count()

            # Count bought-out items (items with CId)
            bought_out_count = TbldgBomMaster.objects.filter(
                wono=wo.wono,
                compid=wo.compid,
                ecnflag=0,
                itemid__cid__isnull=False
            ).count()

            if bom_count > 0:
                status = "✓" if bought_out_count > 0 else "⚠"
                self.stdout.write(
                    f"{status} WO: {wo.wono} | Date: {wo.taskworkorderdate} | "
                    f"BOM: {bom_count} items | Bought-Out: {bought_out_count} items"
                )

                if bought_out_count > 0:
                    # Show sample items
                    sample_items = TbldgBomMaster.objects.filter(
                        wono=wo.wono,
                        compid=wo.compid,
                        ecnflag=0,
                        itemid__cid__isnull=False
                    ).select_related('itemid')[:3]

                    for bom in sample_items:
                        self.stdout.write(
                            f"    - {bom.itemid.itemcode} | {bom.itemid.manfdesc[:50]} | Qty: {bom.qty}"
                        )

        self.stdout.write(f"\n{'='*80}")
        self.stdout.write("Search complete!")
        self.stdout.write(f"{'='*80}\n")
