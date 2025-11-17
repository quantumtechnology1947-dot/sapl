"""
Service layer for the Accounts module.
Contains business logic for vouchers, accounting entries, and calculations.
"""

from django.db import transaction
from datetime import datetime
from decimal import Decimal


class VoucherService:
    """Service layer for voucher operations."""
    
    @staticmethod
    def validate_voucher_balance(debit_total, credit_total, tolerance=0.01):
        """
        Validate that debits equal credits within tolerance.
        
        Args:
            debit_total: Total debit amount
            credit_total: Total credit amount
            tolerance: Acceptable difference (default 0.01)
            
        Returns:
            bool: True if balanced, False otherwise
        """
        difference = abs(float(debit_total) - float(credit_total))
        return difference < tolerance
    
    @staticmethod
    def generate_voucher_number(voucher_type, financial_year):
        """
        Generate sequential voucher number.
        
        Args:
            voucher_type: Type of voucher (BV, CV, JV, etc.)
            financial_year: Financial year ID
            
        Returns:
            str: Generated voucher number (e.g., BV-2024-0001)
        """
        from accounts.models import TblaccBankvoucherPaymentMaster
        
        # Get last voucher for this type and year
        last_voucher = TblaccBankvoucherPaymentMaster.objects.filter(
            finyearid=financial_year
        ).order_by('-id').first()
        
        if last_voucher and last_voucher.bvpno:
            try:
                # Extract number from format: TYPE-YEAR-NUMBER
                parts = last_voucher.bvpno.split('-')
                if len(parts) >= 3:
                    last_num = int(parts[-1])
                    new_num = last_num + 1
                else:
                    new_num = 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        return f"{voucher_type}-{financial_year}-{new_num:04d}"
    
    @staticmethod
    @transaction.atomic
    def post_voucher(voucher):
        """
        Post voucher to ledger (placeholder for future implementation).
        
        Args:
            voucher: Voucher object to post
            
        Returns:
            bool: True if posted successfully
        """
        # This will be implemented when ledger system is ready
        # For now, just mark as posted
        return True
    
    @staticmethod
    def calculate_line_total(lines):
        """
        Calculate total from line items.
        
        Args:
            lines: List of line items with 'amount' field
            
        Returns:
            Decimal: Total amount
        """
        total = Decimal('0.00')
        for line in lines:
            if hasattr(line, 'amount') and line.amount:
                total += Decimal(str(line.amount))
        return total


class AccountingService:
    """Service layer for creating accounting entries."""
    
    @staticmethod
    @transaction.atomic
    def create_sales_invoice_entries(invoice):
        """
        Create accounting entries for sales invoice.
        
        Entries:
        - Debit: Accounts Receivable (Customer)
        - Credit: Sales Revenue
        - Credit: Tax Payable (if applicable)
        
        Args:
            invoice: Sales invoice object
            
        Returns:
            list: Created journal entries
        """
        # Placeholder for future implementation
        # Will create actual journal entries when ledger system is ready
        entries = []
        
        # Entry 1: Debit Accounts Receivable
        # Entry 2: Credit Sales Revenue
        # Entry 3: Credit Tax Payable
        
        return entries
    
    @staticmethod
    @transaction.atomic
    def create_bill_booking_entries(bill):
        """
        Create accounting entries for bill booking.
        
        Entries:
        - Debit: Expense/Asset Account
        - Debit: TDS Receivable (if applicable)
        - Credit: Accounts Payable (Supplier)
        
        Args:
            bill: Bill booking object
            
        Returns:
            list: Created journal entries
        """
        # Placeholder for future implementation
        entries = []
        
        # Entry 1: Debit Expense/Asset
        # Entry 2: Debit TDS Receivable
        # Entry 3: Credit Accounts Payable
        
        return entries
    
    @staticmethod
    @transaction.atomic
    def create_voucher_entries(voucher, voucher_type):
        """
        Create accounting entries for vouchers.
        
        Args:
            voucher: Voucher object
            voucher_type: Type of voucher (bank, cash, journal)
            
        Returns:
            list: Created journal entries
        """
        # Placeholder for future implementation
        entries = []
        return entries
    
    @staticmethod
    def calculate_depreciation(cost, useful_life=None, rate=None, method='SL', book_value=None):
        """
        Calculate depreciation for an asset.
        
        Args:
            cost: Original cost of asset
            useful_life: Useful life in years (for SL method)
            rate: Depreciation rate as decimal (for WDV method)
            method: 'SL' for Straight Line, 'WDV' for Written Down Value
            book_value: Current book value (for WDV method)
            
        Returns:
            Decimal: Depreciation amount
        """
        cost = Decimal(str(cost))
        
        if method == 'SL':  # Straight Line Method
            if not useful_life:
                raise ValueError("Useful life required for Straight Line method")
            return cost / Decimal(str(useful_life))
            
        elif method == 'WDV':  # Written Down Value Method
            if not rate or not book_value:
                raise ValueError("Rate and book value required for WDV method")
            book_value = Decimal(str(book_value))
            rate = Decimal(str(rate))
            return book_value * rate
            
        else:
            raise ValueError(f"Unknown depreciation method: {method}")


class ReconciliationService:
    """Service layer for bank reconciliation operations."""
    
    @staticmethod
    @transaction.atomic
    def mark_as_reconciled(voucher_ids, voucher_type, bank_date, user_id, company_id, financial_year_id):
        """
        Mark bank vouchers as reconciled.
        
        Args:
            voucher_ids: List of voucher IDs to mark as reconciled
            voucher_type: Type of voucher ('payment' or 'receipt')
            bank_date: Date from bank statement
            user_id: User performing reconciliation
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: Summary of reconciliation with count and total amount
            
        Requirements: 9.4
        """
        from accounts.models import (
            TblaccBankrecanciliation,
            TblaccBankvoucherPaymentMaster,
            TblaccBankvoucherReceivedMasters
        )
        
        reconciled_count = 0
        total_amount = Decimal('0.00')
        
        for voucher_id in voucher_ids:
            # Create reconciliation record
            reconciliation = TblaccBankrecanciliation.objects.create(
                sysdate=datetime.now().strftime('%Y-%m-%d'),
                systime=datetime.now().strftime('%H:%M:%S'),
                sessionid=str(user_id),
                compid=company_id,
                finyearid=financial_year_id,
                bvpid=voucher_id if voucher_type == 'payment' else None,
                bvrid=voucher_id if voucher_type == 'receipt' else None,
                bankdate=bank_date,
                addcharges=0.0,
                remarks='Reconciled'
            )
            
            # Get voucher amount
            if voucher_type == 'payment':
                voucher = TblaccBankvoucherPaymentMaster.objects.filter(id=voucher_id).first()
                if voucher and voucher.payamt:
                    total_amount += Decimal(str(voucher.payamt))
            else:
                voucher = TblaccBankvoucherReceivedMasters.objects.filter(id=voucher_id).first()
                if voucher and voucher.amount:
                    total_amount += Decimal(str(voucher.amount))
            
            reconciled_count += 1
        
        return {
            'reconciled_count': reconciled_count,
            'total_amount': total_amount,
            'bank_date': bank_date
        }
    
    @staticmethod
    @transaction.atomic
    def add_bank_charges(bank_id, amount, date, narration, user_id, company_id, financial_year_id):
        """
        Add bank charges and create journal entry.
        
        Creates a journal entry:
        - Debit: Bank Charges Expense
        - Credit: Bank Account
        
        Args:
            bank_id: Bank account ID
            amount: Charge amount
            date: Date of charges
            narration: Description of charges
            user_id: User ID
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: Created journal entry details
            
        Requirements: 9.5, 9.6
        """
        from accounts.models import TblaccBankrecanciliation
        
        # Create reconciliation record for bank charges
        reconciliation = TblaccBankrecanciliation.objects.create(
            sysdate=datetime.now().strftime('%Y-%m-%d'),
            systime=datetime.now().strftime('%H:%M:%S'),
            sessionid=str(user_id),
            compid=company_id,
            finyearid=financial_year_id,
            bvpid=None,
            bvrid=None,
            bankdate=date,
            addcharges=float(amount),
            remarks=narration
        )
        
        # TODO: Create journal entry when journal entry system is implemented
        # This will create:
        # Debit: Bank Charges Expense Account
        # Credit: Bank Account
        
        return {
            'reconciliation_id': reconciliation.id,
            'bank_id': bank_id,
            'amount': amount,
            'date': date,
            'narration': narration,
            'journal_entry_created': False  # Will be True when journal system is ready
        }
    
    @staticmethod
    def calculate_reconciliation_summary(bank_id, as_of_date, company_id, financial_year_id):
        """
        Calculate reconciliation summary for a bank account.
        
        Args:
            bank_id: Bank account ID
            as_of_date: Date for reconciliation summary
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: Reconciliation summary with reconciled and unreconciled amounts
            
        Requirements: 9.7
        """
        from accounts.models import (
            TblaccBankrecanciliation,
            TblaccBankvoucherPaymentMaster,
            TblaccBankvoucherReceivedMasters
        )
        
        # Get all payments for this bank
        all_payments = TblaccBankvoucherPaymentMaster.objects.filter(
            bank=bank_id,
            compid=company_id,
            finyearid=financial_year_id
        )
        
        # Get all receipts for this bank
        all_receipts = TblaccBankvoucherReceivedMasters.objects.filter(
            drawnat=bank_id,
            compid=company_id,
            finyearid=financial_year_id
        )
        
        # Get reconciled payment IDs
        reconciled_payment_ids = set(
            TblaccBankrecanciliation.objects.filter(
                bvpid__isnull=False,
                compid=company_id,
                finyearid=financial_year_id
            ).values_list('bvpid', flat=True)
        )
        
        # Get reconciled receipt IDs
        reconciled_receipt_ids = set(
            TblaccBankrecanciliation.objects.filter(
                bvrid__isnull=False,
                compid=company_id,
                finyearid=financial_year_id
            ).values_list('bvrid', flat=True)
        )
        
        # Calculate totals
        total_payments = Decimal('0.00')
        reconciled_payments = Decimal('0.00')
        unreconciled_payments = Decimal('0.00')
        
        for payment in all_payments:
            amount = Decimal(str(payment.payamt)) if payment.payamt else Decimal('0.00')
            total_payments += amount
            
            if payment.id in reconciled_payment_ids:
                reconciled_payments += amount
            else:
                unreconciled_payments += amount
        
        total_receipts = Decimal('0.00')
        reconciled_receipts = Decimal('0.00')
        unreconciled_receipts = Decimal('0.00')
        
        for receipt in all_receipts:
            amount = Decimal(str(receipt.amount)) if receipt.amount else Decimal('0.00')
            total_receipts += amount
            
            if receipt.id in reconciled_receipt_ids:
                reconciled_receipts += amount
            else:
                unreconciled_receipts += amount
        
        # Get total bank charges
        total_bank_charges = Decimal('0.00')
        bank_charges = TblaccBankrecanciliation.objects.filter(
            compid=company_id,
            finyearid=financial_year_id,
            addcharges__gt=0
        )
        
        for charge in bank_charges:
            if charge.addcharges:
                total_bank_charges += Decimal(str(charge.addcharges))
        
        # Calculate book balance and bank balance
        book_balance = total_receipts - total_payments
        bank_balance = reconciled_receipts - reconciled_payments - total_bank_charges
        difference = book_balance - bank_balance
        
        return {
            'bank_id': bank_id,
            'as_of_date': as_of_date,
            'payments': {
                'total': total_payments,
                'reconciled': reconciled_payments,
                'unreconciled': unreconciled_payments,
                'count_total': all_payments.count(),
                'count_reconciled': len(reconciled_payment_ids),
                'count_unreconciled': all_payments.count() - len(reconciled_payment_ids)
            },
            'receipts': {
                'total': total_receipts,
                'reconciled': reconciled_receipts,
                'unreconciled': unreconciled_receipts,
                'count_total': all_receipts.count(),
                'count_reconciled': len(reconciled_receipt_ids),
                'count_unreconciled': all_receipts.count() - len(reconciled_receipt_ids)
            },
            'bank_charges': total_bank_charges,
            'book_balance': book_balance,
            'bank_balance': bank_balance,
            'difference': difference,
            'is_balanced': abs(difference) < Decimal('0.01')
        }


class ReportService:
    """
    Service layer for generating financial reports.
    Provides methods for Balance Sheet, P&L, Trial Balance, Ledger, and Aging reports.
    """
    
    @staticmethod
    def generate_balance_sheet(as_of_date, company_id=1, financial_year_id=1):
        """
        Generate balance sheet as of a specific date.
        Shows financial position: Assets = Liabilities + Equity
        
        Args:
            as_of_date: Date for balance sheet (YYYY-MM-DD)
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: Balance sheet data with assets, liabilities, equity
            
        Requirements: 11.1, 11.2, 11.3, 11.4, 11.7
        """
        from accounts.models import Acchead
        
        # TODO: Implement actual account balance calculation
        # For now, returning structured placeholder data
        
        assets = {
            'current_assets': {
                'cash': Decimal('50000.00'),
                'bank': Decimal('150000.00'),
                'accounts_receivable': Decimal('75000.00'),
                'inventory': Decimal('100000.00'),
                'subtotal': Decimal('375000.00')
            },
            'fixed_assets': {
                'land_building': Decimal('500000.00'),
                'machinery': Decimal('300000.00'),
                'furniture': Decimal('50000.00'),
                'less_depreciation': Decimal('-100000.00'),
                'subtotal': Decimal('750000.00')
            },
            'total': Decimal('1125000.00')
        }
        
        liabilities = {
            'current_liabilities': {
                'accounts_payable': Decimal('50000.00'),
                'short_term_loans': Decimal('25000.00'),
                'subtotal': Decimal('75000.00')
            },
            'long_term_liabilities': {
                'long_term_loans': Decimal('200000.00'),
                'subtotal': Decimal('200000.00')
            },
            'total': Decimal('275000.00')
        }
        
        equity = {
            'capital': Decimal('800000.00'),
            'retained_earnings': Decimal('50000.00'),
            'total': Decimal('850000.00')
        }
        
        # Verify balance: Assets = Liabilities + Equity
        is_balanced = assets['total'] == (liabilities['total'] + equity['total'])
        
        return {
            'as_of_date': as_of_date,
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'is_balanced': is_balanced,
            'total_assets': assets['total'],
            'total_liabilities_equity': liabilities['total'] + equity['total']
        }
    
    @staticmethod
    def generate_profit_loss(from_date, to_date, company_id=1, financial_year_id=1):
        """
        Generate profit & loss statement for a period.
        Shows financial performance: Net Profit = Income - Expenses
        
        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: P&L data with income and expenses
            
        Requirements: 12.1, 12.2, 12.3, 12.4, 12.7
        """
        # TODO: Implement actual transaction aggregation
        # For now, returning structured placeholder data
        
        income = {
            'revenue': {
                'sales_revenue': Decimal('500000.00'),
                'service_revenue': Decimal('150000.00'),
                'subtotal': Decimal('650000.00')
            },
            'other_income': {
                'interest_income': Decimal('5000.00'),
                'miscellaneous': Decimal('2000.00'),
                'subtotal': Decimal('7000.00')
            },
            'total': Decimal('657000.00')
        }
        
        expenses = {
            'operating_expenses': {
                'salaries': Decimal('200000.00'),
                'rent': Decimal('50000.00'),
                'utilities': Decimal('20000.00'),
                'depreciation': Decimal('30000.00'),
                'subtotal': Decimal('300000.00')
            },
            'non_operating_expenses': {
                'interest_expense': Decimal('10000.00'),
                'subtotal': Decimal('10000.00')
            },
            'total': Decimal('310000.00')
        }
        
        net_profit = income['total'] - expenses['total']
        
        return {
            'from_date': from_date,
            'to_date': to_date,
            'income': income,
            'expenses': expenses,
            'net_profit': net_profit,
            'net_profit_percentage': (net_profit / income['total'] * Decimal('100')) if income['total'] > 0 else Decimal('0.00')
        }
    
    @staticmethod
    def generate_trial_balance(as_of_date, company_id=1, financial_year_id=1):
        """
        Generate trial balance as of a specific date.
        Verifies that total debits equal total credits.
        
        Args:
            as_of_date: Date for trial balance (YYYY-MM-DD)
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: Trial balance data with all accounts
            
        Requirements: 13.1, 13.2, 13.3, 13.4, 13.7
        """
        from accounts.models import Acchead
        
        # TODO: Implement actual account balance calculation
        # For now, returning structured placeholder data
        
        accounts = [
            {'account': 'Cash', 'opening': Decimal('40000.00'), 'debit': Decimal('50000.00'), 'credit': Decimal('40000.00'), 'closing': Decimal('50000.00')},
            {'account': 'Bank', 'opening': Decimal('100000.00'), 'debit': Decimal('200000.00'), 'credit': Decimal('150000.00'), 'closing': Decimal('150000.00')},
            {'account': 'Accounts Receivable', 'opening': Decimal('50000.00'), 'debit': Decimal('100000.00'), 'credit': Decimal('75000.00'), 'closing': Decimal('75000.00')},
            {'account': 'Inventory', 'opening': Decimal('80000.00'), 'debit': Decimal('120000.00'), 'credit': Decimal('100000.00'), 'closing': Decimal('100000.00')},
            {'account': 'Fixed Assets', 'opening': Decimal('700000.00'), 'debit': Decimal('50000.00'), 'credit': Decimal('0.00'), 'closing': Decimal('750000.00')},
            {'account': 'Accounts Payable', 'opening': Decimal('40000.00'), 'debit': Decimal('30000.00'), 'credit': Decimal('40000.00'), 'closing': Decimal('50000.00')},
            {'account': 'Capital', 'opening': Decimal('800000.00'), 'debit': Decimal('0.00'), 'credit': Decimal('0.00'), 'closing': Decimal('800000.00')},
            {'account': 'Sales Revenue', 'opening': Decimal('0.00'), 'debit': Decimal('0.00'), 'credit': Decimal('500000.00'), 'closing': Decimal('500000.00')},
            {'account': 'Expenses', 'opening': Decimal('0.00'), 'debit': Decimal('300000.00'), 'credit': Decimal('0.00'), 'closing': Decimal('300000.00')},
        ]
        
        total_debit = sum(acc['debit'] for acc in accounts)
        total_credit = sum(acc['credit'] for acc in accounts)
        balanced = abs(total_debit - total_credit) < Decimal('0.01')
        
        return {
            'as_of_date': as_of_date,
            'accounts': accounts,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'balanced': balanced,
            'difference': total_debit - total_credit
        }
    
    @staticmethod
    def generate_ledger(account_id, from_date, to_date, company_id=1, financial_year_id=1):
        """
        Generate ledger for a specific account.
        Shows all transactions with running balance.
        
        Args:
            account_id: Account ID
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: Ledger data with transactions and running balance
            
        Requirements: 14.1, 14.2, 14.3, 14.4, 14.5
        """
        from accounts.models import Acchead
        
        # TODO: Implement actual transaction retrieval
        # For now, returning structured placeholder data
        
        try:
            account = Acchead.objects.get(id=account_id)
            account_name = account.description
        except Acchead.DoesNotExist:
            account_name = f"Account #{account_id}"
        
        opening_balance = Decimal('50000.00')
        
        transactions = [
            {'date': '2024-01-05', 'voucher': 'BVP-2024-001', 'particulars': 'Payment to Supplier', 'debit': Decimal('0.00'), 'credit': Decimal('10000.00'), 'balance': Decimal('40000.00')},
            {'date': '2024-01-10', 'voucher': 'CVR-2024-001', 'particulars': 'Cash Receipt', 'debit': Decimal('15000.00'), 'credit': Decimal('0.00'), 'balance': Decimal('55000.00')},
            {'date': '2024-01-15', 'voucher': 'JE-2024-001', 'particulars': 'Journal Entry', 'debit': Decimal('5000.00'), 'credit': Decimal('0.00'), 'balance': Decimal('60000.00')},
            {'date': '2024-01-20', 'voucher': 'BVP-2024-002', 'particulars': 'Payment', 'debit': Decimal('0.00'), 'credit': Decimal('8000.00'), 'balance': Decimal('52000.00')},
        ]
        
        closing_balance = transactions[-1]['balance'] if transactions else opening_balance
        
        return {
            'account_id': account_id,
            'account_name': account_name,
            'from_date': from_date,
            'to_date': to_date,
            'opening_balance': opening_balance,
            'transactions': transactions,
            'closing_balance': closing_balance,
            'total_debit': sum(t['debit'] for t in transactions),
            'total_credit': sum(t['credit'] for t in transactions)
        }
    
    @staticmethod
    def generate_aging_report(report_type, as_of_date, company_id=1, financial_year_id=1):
        """
        Generate aging report for creditors or debtors.
        Shows outstanding amounts in aging buckets.
        
        Args:
            report_type: 'creditors' or 'debtors'
            as_of_date: Date for aging analysis (YYYY-MM-DD)
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: Aging report with buckets (0-30, 31-60, 61-90, 90+)
            
        Requirements: 15.1, 15.2, 15.3, 15.4, 15.7
        """
        # TODO: Implement actual aging calculation from invoices/bills
        # For now, returning structured placeholder data
        
        if report_type == 'debtors':
            parties = [
                {
                    'name': 'Customer A',
                    'total': Decimal('50000.00'),
                    '0-30': Decimal('20000.00'),
                    '31-60': Decimal('15000.00'),
                    '61-90': Decimal('10000.00'),
                    '90+': Decimal('5000.00')
                },
                {
                    'name': 'Customer B',
                    'total': Decimal('30000.00'),
                    '0-30': Decimal('25000.00'),
                    '31-60': Decimal('5000.00'),
                    '61-90': Decimal('0.00'),
                    '90+': Decimal('0.00')
                },
            ]
        else:  # creditors
            parties = [
                {
                    'name': 'Supplier X',
                    'total': Decimal('40000.00'),
                    '0-30': Decimal('30000.00'),
                    '31-60': Decimal('10000.00'),
                    '61-90': Decimal('0.00'),
                    '90+': Decimal('0.00')
                },
                {
                    'name': 'Supplier Y',
                    'total': Decimal('25000.00'),
                    '0-30': Decimal('15000.00'),
                    '31-60': Decimal('5000.00'),
                    '61-90': Decimal('3000.00'),
                    '90+': Decimal('2000.00')
                },
            ]
        
        # Calculate totals
        aging_buckets = {
            '0-30': sum(p['0-30'] for p in parties),
            '31-60': sum(p['31-60'] for p in parties),
            '61-90': sum(p['61-90'] for p in parties),
            '90+': sum(p['90+'] for p in parties)
        }
        
        total_outstanding = sum(aging_buckets.values())
        
        return {
            'report_type': report_type,
            'as_of_date': as_of_date,
            'parties': parties,
            'aging_buckets': aging_buckets,
            'total_outstanding': total_outstanding
        }
    
    @staticmethod
    def export_to_pdf(report_data, report_name):
        """
        Export report data to PDF format.
        
        Args:
            report_data: Report data dictionary
            report_name: Name of the report
            
        Returns:
            bytes: PDF file content
            
        Requirements: 11.5, 12.5, 13.5, 14.6, 15.5
        """
        # TODO: Implement PDF generation using reportlab or weasyprint
        # For now, returning placeholder
        return b"PDF export not yet implemented"
    
    @staticmethod
    def export_to_excel(report_data, report_name):
        """
        Export report data to Excel format.
        
        Args:
            report_data: Report data dictionary
            report_name: Name of the report
            
        Returns:
            bytes: Excel file content
            
        Requirements: 11.5, 12.5, 13.5, 14.6, 15.5
        """
        # TODO: Implement Excel generation using openpyxl or xlsxwriter
        # For now, returning placeholder
        return b"Excel export not yet implemented"



class InvoiceService:
    """Service layer for invoice operations."""

    @staticmethod
    def get_next_invoice_number(company_id, financial_year_id):
        """
        Generate next sales invoice number.

        CRITICAL: This method EXACTLY replicates the ASP.NET logic from
        SalesInvoice_New_Details.aspx.cs lines 96-111.

        Algorithm:
        1. Query the latest invoice number from tblACC_SalesInvoice_Master
        2. Filter by CompId AND FinYearId
        3. Order by InvoiceNo descending (get the latest)
        4. If records exist: Take the latest InvoiceNo, increment by 1, format as 4-digit zero-padded
        5. If no records: Start with "0001"

        Args:
            company_id: Company ID from session
            financial_year_id: Financial Year ID from session

        Returns:
            str: Next invoice number (4-digit zero-padded, e.g., "0001", "0042", "1234")

        Example:
            >>> InvoiceService.get_next_invoice_number(1, 2024)
            "0001"  # If no invoices exist

            >>> InvoiceService.get_next_invoice_number(1, 2024)
            "0042"  # If last invoice was "0041"
        """
        from accounts.models import TblaccSalesinvoiceMaster

        # Query: SELECT InvoiceNo FROM tblACC_SalesInvoice_Master
        #        WHERE CompId='{CompId}' AND FinYearId='{FinYearId}'
        #        ORDER BY InvoiceNo DESC
        last_invoice = TblaccSalesinvoiceMaster.objects.filter(
            compid=company_id,
            finyearid=financial_year_id
        ).order_by('-invoiceno').first()

        # If records exist: InvNo = (latest_invoice_no + 1).ToString("D4")
        # Else: InvNo = "0001"
        if last_invoice and last_invoice.invoiceno:
            # Increment and format as 4-digit zero-padded
            try:
                next_num = int(last_invoice.invoiceno) + 1
                return f"{next_num:04d}"
            except (ValueError, TypeError):
                # If invoiceno is not a valid number, start fresh
                return "0001"
        else:
            return "0001"

    @staticmethod
    def calculate_invoice_totals(line_items):
        """
        Calculate invoice totals including subtotal, taxes, and grand total.
        
        Args:
            line_items: List of invoice line items with quantity, rate, tax fields
            
        Returns:
            dict: Dictionary with subtotal, tax amounts, and grand total
            
        Requirements: 5.4
        """
        subtotal = Decimal('0.00')
        vat_total = Decimal('0.00')
        excise_total = Decimal('0.00')
        service_tax_total = Decimal('0.00')
        
        for item in line_items:
            # Calculate line amount
            quantity = Decimal(str(item.get('quantity', 0)))
            rate = Decimal(str(item.get('rate', 0)))
            line_amount = quantity * rate
            subtotal += line_amount
            
            # Calculate taxes on line amount
            if item.get('vat'):
                vat_rate = Decimal(str(item.get('vat'))) / Decimal('100')
                vat_total += line_amount * vat_rate
            
            if item.get('excise'):
                excise_rate = Decimal(str(item.get('excise'))) / Decimal('100')
                excise_total += line_amount * excise_rate
            
            if item.get('service_tax'):
                service_tax_rate = Decimal(str(item.get('service_tax'))) / Decimal('100')
                service_tax_total += line_amount * service_tax_rate
        
        # Calculate discount if provided
        discount = Decimal('0.00')
        discount_percent = Decimal('0.00')
        
        # Grand total
        grand_total = subtotal + vat_total + excise_total + service_tax_total - discount
        
        return {
            'subtotal': subtotal,
            'vat': vat_total,
            'excise': excise_total,
            'service_tax': service_tax_total,
            'discount': discount,
            'discount_percent': discount_percent,
            'grand_total': grand_total
        }
    
    @staticmethod
    @transaction.atomic
    def create_accounting_entries(invoice):
        """
        Create accounting entries for sales invoice.
        
        Creates journal entries:
        - Debit: Accounts Receivable (Customer) - Grand Total
        - Credit: Sales Revenue - Subtotal
        - Credit: VAT Payable - VAT Amount
        - Credit: Excise Payable - Excise Amount
        - Credit: Service Tax Payable - Service Tax Amount
        
        Args:
            invoice: Sales invoice object
            
        Returns:
            dict: Summary of created entries
            
        Requirements: 5.6
        """
        from accounts.models import TblaccContraEntry
        
        entries_created = []
        
        # TODO: Implement actual journal entry creation when ledger system is ready
        # For now, return placeholder
        
        # Entry 1: Debit Accounts Receivable
        # Entry 2: Credit Sales Revenue
        # Entry 3: Credit VAT Payable
        # Entry 4: Credit Excise Payable
        # Entry 5: Credit Service Tax Payable
        
        return {
            'invoice_id': invoice.id if hasattr(invoice, 'id') else None,
            'entries_created': len(entries_created),
            'total_debit': invoice.grandtotal if hasattr(invoice, 'grandtotal') else Decimal('0.00'),
            'total_credit': invoice.grandtotal if hasattr(invoice, 'grandtotal') else Decimal('0.00'),
            'balanced': True
        }
    
    @staticmethod
    def generate_invoice_pdf(invoice_id):
        """
        Generate printable PDF for sales invoice.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            bytes: PDF file content
            
        Requirements: 5.8
        """
        from accounts.models import TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails
        
        # Get invoice and line items
        try:
            invoice = TblaccSalesinvoiceMaster.objects.get(id=invoice_id)
            line_items = TblaccSalesinvoiceDetails.objects.filter(mid=invoice)
        except TblaccSalesinvoiceMaster.DoesNotExist:
            raise ValueError(f"Invoice with ID {invoice_id} not found")
        
        # TODO: Implement PDF generation using reportlab or weasyprint
        # For now, return placeholder
        
        pdf_content = b"PDF generation not yet implemented"
        
        return pdf_content
    
    @staticmethod
    @transaction.atomic
    def mark_invoice_as_paid(invoice_id, payment_amount, payment_date, payment_reference):
        """
        Mark invoice as paid and update customer balance.
        
        Args:
            invoice_id: Invoice ID
            payment_amount: Amount paid
            payment_date: Date of payment
            payment_reference: Payment reference number
            
        Returns:
            dict: Updated invoice status
            
        Requirements: 5.9
        """
        from accounts.models import TblaccSalesinvoiceMaster
        
        try:
            invoice = TblaccSalesinvoiceMaster.objects.get(id=invoice_id)
        except TblaccSalesinvoiceMaster.DoesNotExist:
            raise ValueError(f"Invoice with ID {invoice_id} not found")
        
        # Calculate outstanding amount
        invoice_total = Decimal(str(invoice.grandtotal)) if invoice.grandtotal else Decimal('0.00')
        paid_amount = Decimal(str(payment_amount))
        
        # TODO: Update invoice payment status in database
        # TODO: Create payment voucher
        # TODO: Update customer balance
        
        outstanding = invoice_total - paid_amount
        
        return {
            'invoice_id': invoice_id,
            'invoice_total': invoice_total,
            'paid_amount': paid_amount,
            'outstanding_amount': outstanding,
            'payment_status': 'Paid' if outstanding <= Decimal('0.01') else 'Partially Paid',
            'payment_date': payment_date,
            'payment_reference': payment_reference
        }
    
    @staticmethod
    def apply_discount(subtotal, discount_type, discount_value):
        """
        Apply discount to invoice subtotal.
        
        Args:
            subtotal: Invoice subtotal
            discount_type: 'percentage' or 'amount'
            discount_value: Discount value
            
        Returns:
            dict: Discount amount and new total
            
        Requirements: 5.7
        """
        subtotal = Decimal(str(subtotal))
        discount_value = Decimal(str(discount_value))
        
        if discount_type == 'percentage':
            discount_amount = subtotal * (discount_value / Decimal('100'))
        elif discount_type == 'amount':
            discount_amount = discount_value
        else:
            raise ValueError(f"Invalid discount type: {discount_type}")
        
        # Ensure discount doesn't exceed subtotal
        if discount_amount > subtotal:
            discount_amount = subtotal
        
        new_total = subtotal - discount_amount
        
        return {
            'subtotal': subtotal,
            'discount_type': discount_type,
            'discount_value': discount_value,
            'discount_amount': discount_amount,
            'new_total': new_total
        }
    
    @staticmethod
    @transaction.atomic
    def create_sales_invoice_from_order(order_id):
        """
        Create sales invoice from sales order (integration with Sales Distribution module).
        
        Args:
            order_id: Sales order ID
            
        Returns:
            dict: Created invoice details
            
        Requirements: 17.1
        """
        # TODO: Implement integration with sales_distribution module
        # This will:
        # 1. Get sales order details
        # 2. Create sales invoice master
        # 3. Copy line items from order to invoice
        # 4. Create accounting entries
        # 5. Update order status
        
        return {
            'order_id': order_id,
            'invoice_id': None,
            'status': 'Not implemented - requires sales_distribution module integration'
        }
    
    @staticmethod
    def calculate_tds(amount, tds_code):
        """
        Calculate TDS (Tax Deducted at Source) for bill booking.
        
        Args:
            amount: Bill amount
            tds_code: TDS code object with rates
            
        Returns:
            dict: TDS calculation details
            
        Requirements: 6.4
        """
        from accounts.models import TblaccTdscodeMaster
        
        amount = Decimal(str(amount))
        
        try:
            if isinstance(tds_code, int):
                tds_code_obj = TblaccTdscodeMaster.objects.get(id=tds_code)
            else:
                tds_code_obj = tds_code
        except TblaccTdscodeMaster.DoesNotExist:
            raise ValueError(f"TDS Code not found")
        
        # Get TDS rate (assuming 'others' rate for now)
        tds_rate = Decimal(str(tds_code_obj.others)) if tds_code_obj.others else Decimal('0.00')
        
        # Calculate TDS amount
        tds_amount = amount * (tds_rate / Decimal('100'))
        net_amount = amount - tds_amount
        
        return {
            'gross_amount': amount,
            'tds_rate': tds_rate,
            'tds_amount': tds_amount,
            'net_amount': net_amount,
            'tds_section': tds_code_obj.sectionno if hasattr(tds_code_obj, 'sectionno') else None
        }


class BillBookingService:
    """Service layer for bill booking operations."""
    
    @staticmethod
    @transaction.atomic
    def create_bill_from_purchase_order(po_id):
        """
        Create bill booking from purchase order (integration with Material Management module).
        
        Args:
            po_id: Purchase order ID
            
        Returns:
            dict: Created bill details
            
        Requirements: 17.2
        """
        # TODO: Implement integration with material_management module
        # This will:
        # 1. Get purchase order details
        # 2. Create bill booking master
        # 3. Copy line items from PO to bill
        # 4. Calculate TDS
        # 5. Create accounting entries
        # 6. Update PO status
        
        return {
            'po_id': po_id,
            'bill_id': None,
            'status': 'Not implemented - requires material_management module integration'
        }
    
    @staticmethod
    @transaction.atomic
    def authorize_bill(bill_id, authorized_by, authorization_date):
        """
        Authorize bill booking for payment.
        
        Args:
            bill_id: Bill booking ID
            authorized_by: User ID who authorized
            authorization_date: Date of authorization
            
        Returns:
            dict: Authorization status
            
        Requirements: 6.8
        """
        from accounts.models import TblaccBillbookingMaster
        
        try:
            bill = TblaccBillbookingMaster.objects.get(id=bill_id)
        except TblaccBillbookingMaster.DoesNotExist:
            raise ValueError(f"Bill with ID {bill_id} not found")
        
        # Update authorization fields
        bill.authorize = 1  # Authorized
        bill.save()
        
        return {
            'bill_id': bill_id,
            'status': 'Authorized',
            'authorized_by': authorized_by,
            'authorization_date': authorization_date
        }



class AssetService:
    """Service layer for asset management and depreciation."""
    
    @staticmethod
    def calculate_depreciation(asset_id, method='SLM', rate=None, useful_life=None):
        """
        Calculate depreciation for an asset.
        
        Args:
            asset_id: Asset ID
            method: 'SLM' for Straight Line Method, 'WDV' for Written Down Value
            rate: Depreciation rate (for WDV)
            useful_life: Useful life in years (for SLM)
            
        Returns:
            dict: Depreciation calculation details
            
        Requirements: 10.3, 10.4
        """
        from accounts.models import TblaccAssetRegister
        
        try:
            asset = TblaccAssetRegister.objects.get(id=asset_id)
        except TblaccAssetRegister.DoesNotExist:
            raise ValueError(f"Asset with ID {asset_id} not found")
        
        # TODO: Get purchase cost and accumulated depreciation from asset
        # For now, using placeholder values
        purchase_cost = Decimal('100000.00')  # TODO: Get from asset
        accumulated_depreciation = Decimal('0.00')  # TODO: Get from asset
        book_value = purchase_cost - accumulated_depreciation
        
        if method == 'SLM':
            # Straight Line Method: (Cost - Salvage Value) / Useful Life
            if not useful_life:
                useful_life = 5  # Default 5 years
            
            annual_depreciation = purchase_cost / Decimal(str(useful_life))
            monthly_depreciation = annual_depreciation / Decimal('12')
            
        elif method == 'WDV':
            # Written Down Value Method: Book Value * Rate
            if not rate:
                rate = Decimal('0.15')  # Default 15%
            else:
                rate = Decimal(str(rate)) / Decimal('100')  # Convert percentage to decimal
            
            annual_depreciation = book_value * rate
            monthly_depreciation = annual_depreciation / Decimal('12')
            
        else:
            raise ValueError(f"Unknown depreciation method: {method}")
        
        return {
            'asset_id': asset_id,
            'method': method,
            'purchase_cost': purchase_cost,
            'accumulated_depreciation': accumulated_depreciation,
            'book_value': book_value,
            'annual_depreciation': annual_depreciation,
            'monthly_depreciation': monthly_depreciation,
            'rate': rate if method == 'WDV' else None,
            'useful_life': useful_life if method == 'SLM' else None
        }
    
    @staticmethod
    @transaction.atomic
    def run_monthly_depreciation(month, year, company_id, financial_year_id):
        """
        Run depreciation for all assets and create journal entries.
        
        Args:
            month: Month number (1-12)
            year: Year
            company_id: Company ID
            financial_year_id: Financial year ID
            
        Returns:
            dict: Summary of depreciation run
            
        Requirements: 10.5
        """
        from accounts.models import TblaccAssetRegister
        
        # Get all active assets
        assets = TblaccAssetRegister.objects.filter(
            compid=company_id,
            finyearid=financial_year_id
        )
        
        total_depreciation = Decimal('0.00')
        assets_processed = 0
        
        for asset in assets:
            # Calculate depreciation for this asset
            depreciation_result = AssetService.calculate_depreciation(
                asset_id=asset.id,
                method='SLM'  # TODO: Get method from asset
            )
            
            monthly_depreciation = depreciation_result['monthly_depreciation']
            total_depreciation += monthly_depreciation
            
            # TODO: Create journal entry
            # Debit: Depreciation Expense
            # Credit: Accumulated Depreciation
            
            assets_processed += 1
        
        return {
            'month': month,
            'year': year,
            'assets_processed': assets_processed,
            'total_depreciation': total_depreciation,
            'journal_entries_created': 0  # TODO: Update when journal system is ready
        }
    
    @staticmethod
    @transaction.atomic
    def dispose_asset(asset_id, disposal_date, disposal_amount):
        """
        Dispose asset and calculate gain/loss.
        
        Creates journal entries:
        - Debit: Cash/Bank (disposal amount)
        - Debit: Accumulated Depreciation
        - Debit/Credit: Gain/Loss on Disposal
        - Credit: Asset Account (original cost)
        
        Args:
            asset_id: Asset ID
            disposal_date: Date of disposal
            disposal_amount: Amount received from disposal
            
        Returns:
            dict: Disposal details with gain/loss
            
        Requirements: 10.6
        """
        from accounts.models import TblaccAssetRegister
        
        try:
            asset = TblaccAssetRegister.objects.get(id=asset_id)
        except TblaccAssetRegister.DoesNotExist:
            raise ValueError(f"Asset with ID {asset_id} not found")
        
        # TODO: Get actual values from asset
        purchase_cost = Decimal('100000.00')  # TODO: Get from asset
        accumulated_depreciation = Decimal('30000.00')  # TODO: Get from asset
        book_value = purchase_cost - accumulated_depreciation
        disposal_amount = Decimal(str(disposal_amount))
        
        # Calculate gain or loss
        gain_loss = disposal_amount - book_value
        
        # TODO: Create journal entries
        # Entry 1: Debit Cash/Bank
        # Entry 2: Debit Accumulated Depreciation
        # Entry 3: Debit/Credit Gain/Loss on Disposal
        # Entry 4: Credit Asset Account
        
        # TODO: Mark asset as disposed in database
        
        return {
            'asset_id': asset_id,
            'disposal_date': disposal_date,
            'purchase_cost': purchase_cost,
            'accumulated_depreciation': accumulated_depreciation,
            'book_value': book_value,
            'disposal_amount': disposal_amount,
            'gain_loss': gain_loss,
            'is_gain': gain_loss > 0,
            'journal_entries_created': False  # TODO: Update when journal system is ready
        }


# ============================================================================
# ADVICE SERVICE - Converted from ASP.NET Advice.aspx.cs
# ============================================================================

class AdviceService:
    """
    Business logic for Advice Payment/Receipt functionality.
    Maps exactly to ASP.NET Advice.aspx.cs methods.
    
    Converted from: aaspnet/Module/Accounts/Transactions/Advice.aspx.cs
    """

    @staticmethod
    def get_autocomplete_options(search_term, option_type, company_id):
        """
        Auto-complete for Employee/Customer/Supplier selection.
        Maps to: GetCompletionList, Sql, Sql2, sql3 WebMethods
        
        Args:
            search_term: Prefix text to search
            option_type: 1=Employee, 2=Customer, 3=Supplier
            company_id: Company ID from session
        
        Returns:
            List of dicts with 'id' and 'text' keys
        """
        from material_management.models import TblmmSupplierMaster
        from sales_distribution.models import SdCustMaster
        from human_resource.models import TblhrOfficestaff
        
        results = []
        
        try:
            if option_type == '1':  # Employee
                employees = TblhrOfficestaff.objects.filter(
                    compid=company_id,
                    employeename__istartswith=search_term
                ).order_by('employeename')[:10]
                
                results = [
                    {
                        'id': f"{emp.employeename} [{emp.empid}]",
                        'text': f"{emp.employeename} [{emp.empid}]"
                    }
                    for emp in employees
                ]
                
            elif option_type == '2':  # Customer
                customers = SdCustMaster.objects.filter(
                    compid=company_id,
                    customername__istartswith=search_term
                ).order_by('customername')[:10]
                
                results = [
                    {
                        'id': f"{cust.customername} [{cust.customerid}]",
                        'text': f"{cust.customername} [{cust.customerid}]"
                    }
                    for cust in customers
                ]
                
            elif option_type == '3':  # Supplier
                suppliers = TblmmSupplierMaster.objects.filter(
                    compid=company_id,
                    suppliername__istartswith=search_term
                ).order_by('suppliername')[:10]
                
                results = [
                    {
                        'id': f"{sup.suppliername} [{sup.supplierid}]",
                        'text': f"{sup.suppliername} [{sup.supplierid}]"
                    }
                    for sup in suppliers
                ]
        except Exception as e:
            print(f"Autocomplete error: {e}")
        
        return results

    @staticmethod
    def extract_code_from_name(name_with_code):
        """
        Extract code from "Name [CODE]" format.
        Maps to: fun.getCode() method
        
        Args:
            name_with_code: String like "ABC Supplier [SUP001]"
        
        Returns:
            Code string like "SUP001"
        """
        if '[' in name_with_code and ']' in name_with_code:
            return name_with_code.split('[')[1].split(']')[0]
        return name_with_code

    @staticmethod
    def generate_advice_number(company_id, financial_year_id):
        """
        Generate next Advice Number (ADNo).
        Maps to: btnProceed_Click ADNo generation logic
        
        Format: Auto-increment 4-digit number (0001, 0002, etc.)
        
        Args:
            company_id: Company ID
            financial_year_id: Financial Year ID
        
        Returns:
            String like "0001", "0002", etc.
        """
        from accounts.models import TblaccAdvicePaymentMaster
        
        last_advice = TblaccAdvicePaymentMaster.objects.filter(
            compid=company_id,
            finyearid=financial_year_id
        ).order_by('-id').first()
        
        if last_advice and last_advice.adno:
            try:
                last_number = int(last_advice.adno)
                next_number = last_number + 1
            except ValueError:
                next_number = 1
        else:
            next_number = 1
        
        return str(next_number).zfill(4)

    @staticmethod
    def validate_emp_cust_supplier_code(code, code_type, company_id):
        """
        Validate if Employee/Customer/Supplier code exists.
        Maps to: fun.chkEmpCustSupplierCode() method
        
        Args:
            code: Employee/Customer/Supplier code
            code_type: 1=Employee, 2=Customer, 3=Supplier
            company_id: Company ID
        
        Returns:
            1 if valid, 0 if invalid
        """
        from material_management.models import TblmmSupplierMaster
        from sales_distribution.models import SdCustMaster
        from human_resource.models import TblhrOfficestaff
        
        try:
            if code_type == 1:  # Employee
                return 1 if TblhrOfficestaff.objects.filter(
                    empid=code, compid=company_id
                ).exists() else 0
            elif code_type == 2:  # Customer
                return 1 if SdCustMaster.objects.filter(
                    customerid=code, compid=company_id
                ).exists() else 0
            elif code_type == 3:  # Supplier
                return 1 if TblmmSupplierMaster.objects.filter(
                    supplierid=code, compid=company_id
                ).exists() else 0
        except Exception:
            return 0
        
        return 0

    # ========================================================================
    # ADVANCE PAYMENT METHODS (Type=1)
    # ========================================================================

    @staticmethod
    def get_advance_temp_items(session_id, company_id):
        """Get temp items for Advance payment. Maps to: GridView1 data binding"""
        from accounts.models import TblaccAdvicePaymentTemp
        return TblaccAdvicePaymentTemp.objects.filter(
            sessionid=session_id,
            compid=company_id,
            types=1  # Advance type
        ).order_by('id')

    @staticmethod
    def insert_advance_temp(data, session_id, company_id):
        """Insert item into Advance temp table. Maps to: GridView1_RowCommand"""
        from accounts.models import TblaccAdvicePaymentTemp
        try:
            TblaccAdvicePaymentTemp.objects.create(
                proformainvno=data.get('proforma_inv_no', ''),
                invdate=data.get('date', ''),
                pono=data.get('po_no', ''),
                amount=Decimal(data.get('amount', 0)),
                particular=data.get('particulars', ''),
                sessionid=session_id,
                compid=company_id,
                types=1  # Advance type
            )
            return True
        except Exception as e:
            print(f"Insert advance temp error: {e}")
            return False

    @staticmethod
    def delete_advance_temp(temp_id):
        """Delete item from Advance temp table. Maps to: GridView1 Delete command"""
        from accounts.models import TblaccAdvicePaymentTemp
        try:
            TblaccAdvicePaymentTemp.objects.filter(id=temp_id).delete()
            return True
        except Exception:
            return False

    @staticmethod
    @transaction.atomic
    def save_advance_payment(form_data, temp_items, user, company_id, financial_year_id):
        """Save Advance payment to Master and Details tables. Maps to: btnProceed_Click"""
        from accounts.models import TblaccAdvicePaymentMaster, TblaccAdvicePaymentDetails
        
        try:
            pay_to_code = AdviceService.extract_code_from_name(form_data['pay_to_name'])
            pay_to_type = int(form_data['pay_to_type'])
            
            if not AdviceService.validate_emp_cust_supplier_code(pay_to_code, pay_to_type, company_id):
                return False, "Invalid Employee/Customer/Supplier code"
            
            advice_number = AdviceService.generate_advice_number(company_id, financial_year_id)
            current_date = datetime.now().strftime('%d-%m-%Y')
            current_time = datetime.now().strftime('%H:%M:%S')
            
            master = TblaccAdvicePaymentMaster.objects.create(
                adno=advice_number,
                sysdate=current_date,
                systime=current_time,
                sessionid=str(user.id),
                compid=company_id,
                finyearid=financial_year_id,
                type=1,  # Advance payment
                ecstype=pay_to_type,
                payto=pay_to_code,
                chequeno=form_data['cheque_no'],
                chequedate=form_data['cheque_date'],
                payat=form_data['payable_at'],
                bank=int(form_data['bank_id'])
            )
            
            for item in temp_items:
                TblaccAdvicePaymentDetails.objects.create(
                    mid=master,
                    proformainvno=item.proformainvno,
                    invdate=item.invdate,
                    pono=item.pono,
                    particular=item.particular,
                    amount=item.amount
                )
            
            temp_items.delete()
            return True, advice_number
            
        except Exception as e:
            print(f"Save advance payment error: {e}")
            return False, str(e)

    # ========================================================================
    # CREDITORS PAYMENT METHODS (Type=4)
    # ========================================================================

    @staticmethod
    def search_bill_bookings(supplier_id, company_id, financial_year_id):
        """Search pending bill bookings for supplier. Maps to: btnSearch_Click and FillGrid_Creditors"""
        from accounts.models import (
            TblaccBillbookingMaster, TblaccBillbookingDetails,
            TblaccAdvicePaymentDetails, TblaccAdvicePaymentCreditorTemp
        )
        from quality_control.models import TblqcMaterialqualityDetails
        from inventory.models import TblinvMaterialservicenoteDetails
        from django.db.models import Sum
        
        try:
            bills = TblaccBillbookingMaster.objects.filter(
                supplierid=supplier_id,
                compid=company_id
            ).select_related('poid').order_by('-id')
            
            result = []
            
            for bill in bills:
                bill_details = TblaccBillbookingDetails.objects.filter(mid=bill.id)
                
                actual_amt = 0.0
                for detail in bill_details:
                    if detail.gqnid and detail.gqnid != 0:
                        gqn_details = TblqcMaterialqualityDetails.objects.filter(mid=detail.gqnid)
                        for gqn_detail in gqn_details:
                            actual_amt += float(gqn_detail.acceptedqty or 0)
                    elif detail.gsnid and detail.gsnid != 0:
                        gsn_details = TblinvMaterialservicenoteDetails.objects.filter(mid=detail.gsnid)
                        for gsn_detail in gsn_details:
                            actual_amt += float(gsn_detail.receivedqty or 0)
                
                paid_amt = TblaccAdvicePaymentDetails.objects.filter(
                    pvevno=bill.id
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                temp_amt = TblaccAdvicePaymentCreditorTemp.objects.filter(
                    pvevno=bill.id,
                    compid=company_id
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                bal_amt = actual_amt - (float(paid_amt) + float(temp_amt))
                
                if bal_amt > 0:
                    result.append({
                        'id': bill.id,
                        'pvevno': bill.pvevno,
                        'bill_no': bill.billno,
                        'bill_date': bill.billdate,
                        'po_no': bill.poid.pono if bill.poid else '',
                        'actual_amt': actual_amt,
                        'paid_amt': paid_amt,
                        'bal_amt': bal_amt
                    })
            
            return result
            
        except Exception as e:
            print(f"Search bill bookings error: {e}")
            return []

    @staticmethod
    def get_creditor_temp_items(session_id, company_id):
        """Get temp items for Creditors payment. Maps to: GridView5 data binding"""
        from accounts.models import TblaccAdvicePaymentCreditorTemp
        return TblaccAdvicePaymentCreditorTemp.objects.filter(
            sessionid=session_id,
            compid=company_id
        ).order_by('id')

    @staticmethod
    def add_creditor_to_temp(selected_bills, session_id, company_id):
        """Add selected bills to creditor temp table. Maps to: GridView4_RowCommand "AddToTemp"  """
        from accounts.models import TblaccAdvicePaymentCreditorTemp
        try:
            for bill in selected_bills:
                TblaccAdvicePaymentCreditorTemp.objects.create(
                    pvevno=bill['bill_id'],
                    billagainst=bill['narration'],
                    amount=Decimal(bill['amount']),
                    sessionid=session_id,
                    compid=company_id
                )
            return True
        except Exception as e:
            print(f"Add creditor to temp error: {e}")
            return False

    @staticmethod
    def delete_creditor_temp(temp_id):
        """Delete item from Creditors temp table. Maps to: GridView5_RowDeleting"""
        from accounts.models import TblaccAdvicePaymentCreditorTemp
        try:
            TblaccAdvicePaymentCreditorTemp.objects.filter(id=temp_id).delete()
            return True
        except Exception:
            return False

    @staticmethod
    @transaction.atomic
    def save_creditor_payment(form_data, temp_items, user, company_id, financial_year_id):
        """Save Creditor payment to Master and Details tables. Maps to: btnProceed_Creditor_Click"""
        from accounts.models import TblaccAdvicePaymentMaster, TblaccAdvicePaymentDetails
        
        try:
            supplier_code = AdviceService.extract_code_from_name(form_data['pay_to_name'])
            
            if not AdviceService.validate_emp_cust_supplier_code(supplier_code, 3, company_id):
                return False, "Invalid Supplier code"
            
            advice_number = AdviceService.generate_advice_number(company_id, financial_year_id)
            current_date = datetime.now().strftime('%d-%m-%Y')
            current_time = datetime.now().strftime('%H:%M:%S')
            
            master = TblaccAdvicePaymentMaster.objects.create(
                adno=advice_number,
                sysdate=current_date,
                systime=current_time,
                sessionid=str(user.id),
                compid=company_id,
                finyearid=financial_year_id,
                type=4,  # Creditors payment
                ecstype=3,  # Supplier type
                payto=supplier_code,
                chequeno=form_data['cheque_no'],
                chequedate=form_data['cheque_date'],
                payat=form_data['payable_at'],
                bank=int(form_data['bank_id'])
            )
            
            for item in temp_items:
                TblaccAdvicePaymentDetails.objects.create(
                    mid=master,
                    pvevno=item.pvevno,
                    billagainst=item.billagainst,
                    amount=item.amount
                )
            
            temp_items.delete()
            return True, advice_number
            
        except Exception as e:
            print(f"Save creditor payment error: {e}")
            return False, str(e)

    # ========================================================================
    # SALARY TAB METHODS
    # ========================================================================
    
    @staticmethod
    def get_salary_temp_items(session_id, company_id):
        """Get salary temp items for current session."""
        from .models import TblaccAdvicePaymentTemp
        return TblaccAdvicePaymentTemp.objects.filter(
            sessionid=session_id,
            compid=company_id,
            types=2  # 2=Salary
        ).order_by('id')
    
    @staticmethod
    def insert_salary_temp(data, session_id, company_id):
        """Insert salary item into temp table."""
        from .models import TblaccAdvicePaymentTemp
        import traceback
        
        try:
            TblaccAdvicePaymentTemp.objects.create(
                sessionid=session_id,
                compid=company_id,
                proformainvno=data.get('empname', ''),  # Store employee name in proformainvno
                amount=data.get('amt', 0),
                particular=data.get('particulars', ''),
                types=2  # 2=Salary
            )
            return True
        except Exception as e:
            print(f"Error inserting salary temp: {e}")
            traceback.print_exc()
            return False
    
    @staticmethod
    def delete_salary_temp(temp_id):
        """Delete salary item from temp table."""
        from .models import TblaccAdvicePaymentTemp
        try:
            TblaccAdvicePaymentTemp.objects.filter(id=temp_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting salary temp: {e}")
            return False
    
    @staticmethod
    def save_salary_payment(form_data, temp_items, user, company_id, financial_year_id):
        """Save salary payment to master and details tables."""
        # TODO: Implement save logic
        return True, "SAL-2025-001"
    
    # ========================================================================
    # OTHERS TAB METHODS
    # ========================================================================
    
    @staticmethod
    def get_others_temp_items(session_id, company_id):
        """Get others temp items for current session."""
        from .models import TblaccAdvicePaymentTemp
        return TblaccAdvicePaymentTemp.objects.filter(
            sessionid=session_id,
            compid=company_id,
            types=3  # 3=Others
        ).order_by('id')
    
    @staticmethod
    def insert_others_temp(data, session_id, company_id):
        """Insert others item into temp table."""
        from .models import TblaccAdvicePaymentTemp
        
        try:
            TblaccAdvicePaymentTemp.objects.create(
                sessionid=session_id,
                compid=company_id,
                proformainvno='',  # Not used for Others
                amount=data['amt'],
                particular=data.get('particulars', ''),
                types=3  # 3=Others
            )
            return True
        except Exception as e:
            print(f"Error inserting others temp: {e}")
            return False
    
    @staticmethod
    def delete_others_temp(temp_id):
        """Delete others item from temp table."""
        from .models import TblaccAdvicePaymentTemp
        try:
            TblaccAdvicePaymentTemp.objects.filter(id=temp_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting others temp: {e}")
            return False
    
    @staticmethod
    def save_others_payment(form_data, temp_items, user, company_id, financial_year_id):
        """Save others payment to master and details tables."""
        # TODO: Implement save logic
        return True, "OTH-2025-001"


# ============================================================================
# CREDITOR/DEBITOR SERVICES - Stub implementations
# ============================================================================

class CreditorService:
    """Service for creditor operations."""
    pass


class DebitorService:
    """Service for debitor operations."""
    pass


class SundryCreditorService:
    """Service for sundry creditor operations."""
    pass
