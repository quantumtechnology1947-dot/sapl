"""
Data Sync Management Command
Syncs PR/SPR data from ASP.NET SQL Server to Django SQLite
"""
import os
import sys
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sync PR/SPR data from ASP.NET SQL Server to Django SQLite'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview changes without committing')
        parser.add_argument('--clean', action='store_true', help='Delete existing PR/SPR data before sync')
        parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')
        parser.add_argument('--company-id', type=int, default=1, help='Filter by company ID')
        parser.add_argument('--financial-year', type=int, default=None, help='Filter by financial year ID')
    
    def handle(self, *args, **options):
        from core.data_sync.extractor import DataExtractor
        from core.data_sync.transformer import DataTransformer
        from core.data_sync.loader import DataLoader
        from core.data_sync.validator import DataValidator
        from core.data_sync.sync_logger import SyncLogger
        
        # Initialize logger
        sync_logger = SyncLogger()
        sync_logger.log_progress('Starting PR/SPR data sync...')
        
        # Check environment variables
        conn_str = os.getenv('ASPNET_DB_CONNECTION')
        if not conn_str:
            self.stdout.write(self.style.ERROR(
                'Error: ASPNET_DB_CONNECTION not set. Add to .env:\n'
                'ASPNET_DB_CONNECTION="Server=localhost;Database=NewERP;User Id=sa;Password=xxx;TrustServerCertificate=True"'
            ))
            sys.exit(1)
        
        # Extract options
        dry_run = options['dry_run']
        clean = options['clean']
        force = options['force']
        company_id = options['company_id']
        fin_year_id = options['financial_year']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY-RUN mode - no changes will be made'))
        
        self.stdout.write(f'Company ID: {company_id}')
        if fin_year_id:
            self.stdout.write(f'Financial Year ID: {fin_year_id}')
        
        try:
            # Initialize components
            extractor = DataExtractor(conn_str)
            transformer = DataTransformer()
            loader = DataLoader()
            validator = DataValidator()
            
            # Connect to SQL Server
            self.stdout.write('Connecting to SQL Server...')
            if not extractor.connect():
                self.stdout.write(self.style.ERROR('Failed to connect to SQL Server'))
                sys.exit(1)
            
            sync_logger.log_progress('Connected to SQL Server')
            
            # Clean data if requested
            if clean and not dry_run:
                if not force:
                    confirm = input('This will delete all PR/SPR data. Continue? (yes/no): ')
                    if confirm.lower() != 'yes':
                        self.stdout.write('Sync cancelled')
                        return
                
                self.stdout.write('Cleaning existing PR/SPR data...')
                self._clean_data()
                sync_logger.log_progress('Cleaned existing data')
            
            # EXTRACT
            self.stdout.write(self.style.SUCCESS('\n=== EXTRACTION PHASE ==='))
            sync_logger.log_progress('Starting extraction phase')
            
            pr_data = extractor.extract_pr_data(company_id, fin_year_id)
            self.stdout.write(f'Extracted {len(pr_data["masters"])} PR masters, {len(pr_data["details"])} PR details')
            
            spr_data = extractor.extract_spr_data(company_id, fin_year_id)
            self.stdout.write(f'Extracted {len(spr_data["masters"])} SPR masters, {len(spr_data["details"])} SPR details')
            
            # Extract supplier and item IDs
            supplier_ids = set()
            item_ids = set()
            for detail in pr_data['details'] + spr_data['details']:
                if detail.get('SupplierId'):
                    supplier_ids.add(detail['SupplierId'])
                if detail.get('ItemId'):
                    item_ids.add(detail['ItemId'])
            
            suppliers = extractor.extract_suppliers(list(supplier_ids)) if supplier_ids else []
            self.stdout.write(f'Extracted {len(suppliers)} suppliers')
            
            items = extractor.extract_items(list(item_ids)) if item_ids else []
            self.stdout.write(f'Extracted {len(items)} items')
            
            # TRANSFORM
            self.stdout.write(self.style.SUCCESS('\n=== TRANSFORMATION PHASE ==='))
            sync_logger.log_progress('Starting transformation phase')
            
            transformed_suppliers = [transformer.transform_supplier(s) for s in suppliers]
            transformed_suppliers = [s for s in transformed_suppliers if s]
            self.stdout.write(f'Transformed {len(transformed_suppliers)} suppliers')
            
            transformed_items = [transformer.transform_item(i) for i in items]
            transformed_items = [i for i in transformed_items if i]
            self.stdout.write(f'Transformed {len(transformed_items)} items')
            
            transformed_pr_masters = [transformer.transform_pr_master(m) for m in pr_data['masters']]
            transformed_pr_masters = [m for m in transformed_pr_masters if m]
            self.stdout.write(f'Transformed {len(transformed_pr_masters)} PR masters')
            
            transformed_pr_details = [transformer.transform_pr_detail(d) for d in pr_data['details']]
            transformed_pr_details = [d for d in transformed_pr_details if d]
            self.stdout.write(f'Transformed {len(transformed_pr_details)} PR details')
            
            transformed_spr_masters = [transformer.transform_spr_master(m) for m in spr_data['masters']]
            transformed_spr_masters = [m for m in transformed_spr_masters if m]
            self.stdout.write(f'Transformed {len(transformed_spr_masters)} SPR masters')
            
            transformed_spr_details = [transformer.transform_spr_detail(d) for d in spr_data['details']]
            transformed_spr_details = [d for d in transformed_spr_details if d]
            self.stdout.write(f'Transformed {len(transformed_spr_details)} SPR details')
            
            # Show validation errors
            errors = transformer.get_validation_errors()
            if errors:
                self.stdout.write(self.style.WARNING(f'\nValidation errors: {len(errors)}'))
                error_summary = transformer.get_error_summary()
                for error_type, count in error_summary.items():
                    self.stdout.write(f'  {error_type}: {count} errors')
            
            # LOAD
            if not dry_run:
                self.stdout.write(self.style.SUCCESS('\n=== LOADING PHASE ==='))
                sync_logger.log_progress('Starting loading phase')
                
                loader.load_suppliers(transformed_suppliers)
                loader.load_items(transformed_items)
                loader.load_pr_masters(transformed_pr_masters)
                loader.load_pr_details(transformed_pr_details)
                loader.load_spr_masters(transformed_spr_masters)
                loader.load_spr_details(transformed_spr_details)
                
                # Show loading summary
                self.stdout.write(loader.get_summary())
                
                # VERIFY
                self.stdout.write(self.style.SUCCESS('\n=== VERIFICATION PHASE ==='))
                sync_logger.log_progress('Starting verification phase')
                
                pr_counts = validator.verify_pr_counts(extractor, company_id, fin_year_id)
                spr_counts = validator.verify_spr_counts(extractor, company_id, fin_year_id)
                supplier_counts = validator.verify_supplier_counts()
                
                report = validator.generate_comparison_report(pr_counts, spr_counts, supplier_counts)
                self.stdout.write(report)
                
                sync_logger.log_progress('Sync completed successfully')
                self.stdout.write(self.style.SUCCESS('\n✓ Sync completed successfully!'))
            else:
                self.stdout.write(self.style.WARNING('\nDRY-RUN complete - no data was loaded'))
            
            # Close extractor
            extractor.close()
            
            self.stdout.write(f'\nLog file: {sync_logger.get_log_file_path()}')
            
        except Exception as e:
            sync_logger.log_error(f'Sync failed: {e}')
            self.stdout.write(self.style.ERROR(f'\n✗ Sync failed: {e}'))
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def _clean_data(self):
        """Clean existing PR/SPR data"""
        from material_management.models import PRMaster, PRDetails, SPRMaster, SPRDetails
        
        pr_details_count = PRDetails.objects.count()
        pr_masters_count = PRMaster.objects.count()
        spr_details_count = SPRDetails.objects.count()
        spr_masters_count = SPRMaster.objects.count()
        
        PRDetails.objects.all().delete()
        PRMaster.objects.all().delete()
        SPRDetails.objects.all().delete()
        SPRMaster.objects.all().delete()
        
        self.stdout.write(f'Deleted {pr_details_count} PR details, {pr_masters_count} PR masters')
        self.stdout.write(f'Deleted {spr_details_count} SPR details, {spr_masters_count} SPR masters')
