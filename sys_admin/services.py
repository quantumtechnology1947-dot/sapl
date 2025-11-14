"""
SysAdmin Services - Business Logic Layer
Handles complex operations like year-end closing.
"""

import logging
from datetime import datetime
from django.db import transaction, connection
from django.core.exceptions import ValidationError
from .models import TblfinancialMaster, TblcompanyMaster
from design.models import TbldgItemMaster
from .access_models import TblaccessMaster
# This clone model is not yet in the project, so we define it here for now.
# In a real project, this should be in a models.py file.
from django.db import models

class TbldgItemMasterClone(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50)
    systime = models.CharField(db_column='SysTime', max_length=50)
    sessionid = models.CharField(db_column='SessionId', max_length=50)
    compid = models.IntegerField(db_column='CompId')
    finyearid = models.IntegerField(db_column='FinYearId')
    itemid = models.IntegerField(db_column='ItemId')
    stockqty = models.FloatField(db_column='StockQty', default=0.0)
    openingqty = models.FloatField(db_column='OpeningQty', default=0.0)
    openingdate = models.CharField(db_column='OpeningDate', max_length=50)

    class Meta:
        managed = False
        db_table = 'tblDG_Item_Master_Clone'


logger = logging.getLogger(__name__)


class YearEndClosingService:
    """
    Service class for handling year-end closing operations.
    
    Converted from: aspnet/Module/SysAdmin/FinancialYear/FinYear_New_Details.aspx
    
    Year-end closing process:
    1. Clone item master data to historical table
    2. Update opening balances from closing balances
    3. Carry forward user access permissions
    4. Close previous financial year
    5. Reset transaction numbers
    6. Carry forward partial transactions
    """
    
    @transaction.atomic
    def execute_year_end_closing(self, old_year, new_year):
        """
        Execute complete year-end closing process.
        
        Args:
            old_year: TblfinancialMaster instance (previous year)
            new_year: TblfinancialMaster instance (new year)
        
        Raises:
            ValidationError: If validation fails
            Exception: If any step fails (transaction will rollback)
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 6.4
        """
        try:
            logger.info(
                f"Starting year-end closing: {old_year.finyear} → {new_year.finyear} "
                f"for company {old_year.compid}"
            )
            
            # Validate years belong to same company
            if old_year.compid != new_year.compid:
                raise ValidationError("Financial years must belong to the same company")
            
            # Validate old year is not already closed
            if old_year.is_closed():
                raise ValidationError(f"Financial year {old_year.finyear} is already closed")
            
            # Validate new year is not already closed
            if new_year.is_closed():
                raise ValidationError(f"Financial year {new_year.finyear} is already closed")
            
            # Step 1: Clone item master data
            logger.info("Step 1: Cloning item master data...")
            cloned_count = self.clone_item_master(old_year, new_year)
            logger.info(f"Cloned {cloned_count} item master records")
            
            # Step 2: Update opening balances
            logger.info("Step 2: Updating opening balances...")
            updated_count = self.update_opening_balances(old_year, new_year)
            logger.info(f"Updated {updated_count} opening balances")
            
            # Step 3: Carry forward user access
            logger.info("Step 3: Carrying forward user access...")
            access_count = self.carry_forward_access(old_year, new_year)
            logger.info(f"Carried forward access for {access_count} users")
            
            # Step 4: Close previous year
            logger.info("Step 4: Closing previous financial year...")
            self.close_previous_year(old_year)
            logger.info(f"Closed financial year: {old_year.finyear}")
            
            # Step 5: Reset transaction numbers
            logger.info("Step 5: Resetting transaction numbers...")
            reset_count = self.reset_transaction_numbers(new_year)
            logger.info(f"Reset {reset_count} transaction sequences")
            
            # Step 6: Carry forward partial transactions
            logger.info("Step 6: Carrying forward partial transactions...")
            transaction_count = self.carry_forward_transactions(old_year, new_year)
            logger.info(f"Carried forward {transaction_count} partial transactions")
            
            logger.info(
                f"Year-end closing completed successfully: {old_year.finyear} → {new_year.finyear}"
            )
            
            return {
                'success': True,
                'cloned_items': cloned_count,
                'updated_balances': updated_count,
                'access_records': access_count,
                'reset_sequences': reset_count,
                'carried_transactions': transaction_count
            }
            
        except Exception as e:
            logger.error(f"Year-end closing failed: {str(e)}", exc_info=True)
            raise
    
    def clone_item_master(self, old_year, session_id):
        """
        Clone all item master records to clone table for historical reference.
        """
        now = datetime.now()
        cdate = now.strftime('%Y-%m-%d')
        ctime = now.strftime('%H:%M:%S')
        
        items_to_clone = TbldgItemMaster.objects.filter(compid=old_year.compid)
        
        clones = [
            TbldgItemMasterClone(
                sysdate=cdate,
                systime=ctime,
                sessionid=session_id,
                compid=old_year.compid,
                finyearid=old_year.finyearid,
                itemid=item.id,
                stockqty=item.stockqty,
                openingqty=item.openingbalqty,
                openingdate=item.openingbaldate
            )
            for item in items_to_clone
        ]
        
        if clones:
            TbldgItemMasterClone.objects.bulk_create(clones)
            
        return len(clones)
        
        # Implementation will be:
        # items = TbldgItemMaster.objects.filter(fin_year=old_year)
        # clones = [
        #     TbldgItemMasterClone(
        #         item_id=item.item_id,
        #         fin_year=old_year,
        #         item_name=item.item_name,
        #         closing_qty=item.closing_qty,
        #         # ... other fields
        #     )
        #     for item in items
        # ]
        # TbldgItemMasterClone.objects.bulk_create(clones)
        # return len(clones)
    
    def update_opening_balances(self, old_year):
        """
        Update opening balances from closing balances of previous year.
        """
        now = datetime.now()
        cdate = now.strftime('%Y-%m-%d')
        
        updated_count = TbldgItemMaster.objects.filter(compid=old_year.compid).update(
            openingbalqty=models.F('stockqty'),
            openingbaldate=cdate
        )
        return updated_count
        
        # Implementation will be:
        # old_items = TbldgItemMaster.objects.filter(fin_year=old_year)
        # new_items = [
        #     TbldgItemMaster(
        #         fin_year=new_year,
        #         item_name=item.item_name,
        #         opening_qty=item.closing_qty,
        #         closing_qty=0,
        #         opening_date=new_year.get_from_date()
        #     )
        #     for item in old_items
        # ]
        # TbldgItemMaster.objects.bulk_create(new_items)
        # return len(new_items)
    
    def carry_forward_access(self, old_year, new_year, session_id):
        """
        Carry forward user access permissions to new financial year.
        """
        now = datetime.now()
        cdate = now.strftime('%Y-%m-%d')
        ctime = now.strftime('%H:%M:%S')

        old_access_records = TblaccessMaster.objects.filter(
            compid=old_year.compid, 
            finyearid=old_year.finyearid
        )

        new_access_records = [
            TblaccessMaster(
                sysdate=cdate,
                systime=ctime,
                sessionid=session_id,
                compid=new_year.compid,
                finyearid=new_year.finyearid,
                empid=rec.empid,
                modid=rec.modid,
                submodid=rec.submodid,
                accesstype=rec.accesstype,
                access=rec.access
            )
            for rec in old_access_records
        ]

        if new_access_records:
            TblaccessMaster.objects.bulk_create(new_access_records)

        # This corresponds to the logic: "update New,Edit,Delete,Print in tblAccess Master"
        TblaccessMaster.objects.filter(
            compid=old_year.compid, 
            finyearid=old_year.finyearid
        ).exclude(access=4).update(access=0)

        return len(new_access_records)
        
        # Implementation will be:
        # old_access = TblaccessMaster.objects.filter(fin_year=old_year)
        # new_access = [
        #     TblaccessMaster(
        #         user=access.user,
        #         fin_year=new_year,
        #         module_access=access.module_access
        #     )
        #     for access in old_access
        # ]
        # TblaccessMaster.objects.bulk_create(new_access)
        # return len(new_access)
    
    def close_previous_year(self, old_year):
        """
        Mark previous financial year as closed.
        
        Args:
            old_year: TblfinancialMaster instance (previous year)
        
        Requirements: 2.4
        """
        # Set flag=0 to indicate closed status
        old_year.flag = 0
        old_year.save(update_fields=['flag'])
        
        logger.info(f"Closed financial year: {old_year.finyear} (ID: {old_year.finyearid})")
    
    def reset_transaction_numbers(self, new_year):
        """
        Reset transaction number sequences for new financial year.
        
        Args:
            new_year: TblfinancialMaster instance (new year)
        
        Returns:
            int: Number of sequences reset
        
        Requirements: 2.5, 9.1, 9.2, 9.3
        """
        # TODO: Implement when transaction number tables are available
        # For now, return 0 as placeholder
        logger.warning("reset_transaction_numbers: Not implemented - transaction tables not available")
        return 0
        
        # Implementation will be:
        # Transaction types to reset:
        # - Purchase Orders (PO)
        # - Sales Orders (SO)
        # - Invoices (INV)
        # - Receipts (RCP)
        # - Payments (PAY)
        # - etc.
        #
        # For each transaction type:
        # TransactionNumber.objects.create(
        #     fin_year=new_year,
        #     transaction_type='PO',
        #     current_number=1,
        #     prefix='PO',
        #     suffix=''
        # )
    
    def carry_forward_transactions(self, old_year, new_year):
        """
        Carry forward partial/pending transactions to new financial year.
        
        Args:
            old_year: TblfinancialMaster instance (previous year)
            new_year: TblfinancialMaster instance (new year)
        
        Returns:
            int: Number of transactions carried forward
        
        Requirements: 2.6
        """
        # TODO: Implement when transaction tables are available
        # For now, return 0 as placeholder
        logger.warning("carry_forward_transactions: Not implemented - transaction tables not available")
        return 0
        
        # Implementation will be:
        # Identify partial transactions:
        # - Purchase orders not fully received
        # - Sales orders not fully delivered
        # - Pending invoices
        # - etc.
        #
        # For each partial transaction:
        # - Copy to new financial year
        # - Update dates to new year start date
        # - Maintain references to original transaction
        # - Update status to indicate carried forward
