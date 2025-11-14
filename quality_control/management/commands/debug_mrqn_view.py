"""
Debug command to check MRQN view data loading
"""

from django.core.management.base import BaseCommand
from inventory.models import TblinvMaterialreturnMaster


class Command(BaseCommand):
    help = 'Debug MRQN view data loading'

    def handle(self, *args, **options):
        self.stdout.write("Debugging MRQN view data loading...")
        
        # Check MRN records by company
        companies = TblinvMaterialreturnMaster.objects.values_list('compid', flat=True).distinct()
        self.stdout.write(f"Companies with MRN records: {list(companies)}")
        
        for compid in companies:
            count = TblinvMaterialreturnMaster.objects.filter(compid=compid).count()
            self.stdout.write(f"Company {compid}: {count} MRN records")
            
            if count > 0:
                # Show first record for this company
                first_record = TblinvMaterialreturnMaster.objects.filter(compid=compid).first()
                self.stdout.write(f"  First record: ID={first_record.id}, MRN={first_record.mrnno}, Date={first_record.sysdate}")
        
        # Test the exact query from the view
        self.stdout.write("\nTesting view query with compid=1:")
        test_records = TblinvMaterialreturnMaster.objects.filter(compid=1).order_by('-id')[:5]
        
        if test_records:
            for record in test_records:
                self.stdout.write(f"  ID: {record.id}, MRN: {record.mrnno}, Date: {record.sysdate}")
        else:
            self.stdout.write("  No records found for compid=1")
            
        self.stdout.write(self.style.SUCCESS("Debug completed!"))