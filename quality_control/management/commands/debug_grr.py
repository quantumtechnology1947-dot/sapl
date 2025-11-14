"""
Management command to debug GRR records for Quality Control
"""
from django.core.management.base import BaseCommand
from inventory.models import TblinvMaterialreceivedMaster, TblinvMaterialreceivedDetails


class Command(BaseCommand):
    help = 'Debug GRR records for Quality Control'

    def handle(self, *args, **options):
        self.stdout.write("=== GRR Debug Information ===")
        
        # Check if tables exist and have data
        try:
            total_grr_master = TblinvMaterialreceivedMaster.objects.count()
            self.stdout.write(f"Total GRR Master records: {total_grr_master}")
            
            if total_grr_master > 0:
                # Show first few records
                first_grrs = TblinvMaterialreceivedMaster.objects.all()[:5]
                for grr in first_grrs:
                    self.stdout.write(f"GRR ID: {grr.id}, CompID: {grr.compid}, FinYearID: {grr.finyearid}, GRRNo: {grr.grrno}")
                
                # Show unique company IDs
                compids = TblinvMaterialreceivedMaster.objects.values_list('compid', flat=True).distinct()
                self.stdout.write(f"Unique Company IDs: {list(compids)}")
                
                # Show unique financial year IDs
                finyearids = TblinvMaterialreceivedMaster.objects.values_list('finyearid', flat=True).distinct()
                self.stdout.write(f"Unique Financial Year IDs: {list(finyearids)}")
            
            # Check GRR Details
            total_grr_details = TblinvMaterialreceivedDetails.objects.count()
            self.stdout.write(f"Total GRR Detail records: {total_grr_details}")
            
            if total_grr_details > 0:
                # Show first few detail records
                first_details = TblinvMaterialreceivedDetails.objects.all()[:5]
                for detail in first_details:
                    self.stdout.write(f"Detail ID: {detail.id}, MID: {detail.mid}, ReceivedQty: {detail.receivedqty}")
            
        except Exception as e:
            self.stdout.write(f"Error accessing GRR tables: {e}")
            
        self.stdout.write("=== End Debug ===")