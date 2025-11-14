#!/usr/bin/env python
"""
Setup Test Database for Accounts Module
Creates all necessary tables and inserts minimal test data
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.db import connection, transaction
from django.core.management import call_command
from datetime import datetime

def create_accounts_tables():
    """Create all tables needed by Accounts module"""

    with connection.cursor() as cursor:
        print("Creating Accounts module tables...")

        # Core Account Head table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Acc_head (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            AccHeadName TEXT,
            AccHeadCode VARCHAR(50),
            AccType VARCHAR(50),
            UnderGroup VARCHAR(100),
            OpeningBalance DECIMAL(18,2),
            DebitCredit VARCHAR(10),
            Flag INTEGER DEFAULT 1
        )
        """)

        # Bank Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Bank (
            BankId INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            BankName TEXT,
            BankCode VARCHAR(50),
            Branch TEXT,
            AccountNo VARCHAR(50),
            IFSCCode VARCHAR(50),
            Address TEXT,
            City VARCHAR(100),
            State VARCHAR(100),
            Country VARCHAR(100),
            Phone VARCHAR(50),
            Email VARCHAR(100),
            ContactPerson VARCHAR(100),
            OpeningBalance DECIMAL(18,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        # Currency Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Currency_master (
            CurrencyId INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            CurrencyName VARCHAR(100),
            CurrencyCode VARCHAR(10),
            Symbol VARCHAR(10),
            ExchangeRate DECIMAL(18,4),
            Flag INTEGER DEFAULT 1
        )
        """)

        # Bank Voucher Payment Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_BankVoucher_Payment_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            BVPNo VARCHAR(50),
            VoucherDate VARCHAR(50),
            BankId INTEGER,
            PayTo TEXT,
            PayAmt DECIMAL(18,2),
            ChequeNo VARCHAR(50),
            ChequeDate VARCHAR(50),
            Narration TEXT,
            Authorize INTEGER DEFAULT 0,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Bank Voucher Payment Details
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_BankVoucher_Payment_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            AccHeadId INTEGER,
            Amount DECIMAL(18,2),
            Narration TEXT,
            FOREIGN KEY (MasterId) REFERENCES tblAcc_BankVoucher_Payment_master(Id)
        )
        """)

        # Cash Voucher Payment Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_CashVoucher_Payment_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            CVPNo VARCHAR(50),
            VoucherDate VARCHAR(50),
            PaidTo TEXT,
            TotalAmount DECIMAL(18,2),
            Narration TEXT,
            Authorize INTEGER DEFAULT 0,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Cash Voucher Payment Details
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_CashVoucher_Payment_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            AccHeadId INTEGER,
            Amount DECIMAL(18,2),
            Narration TEXT,
            FOREIGN KEY (MasterId) REFERENCES tblAcc_CashVoucher_Payment_master(Id)
        )
        """)

        # Cash Voucher Receipt Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_CashVoucher_Receipt_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            CVRNo VARCHAR(50),
            VoucherDate VARCHAR(50),
            ReceivedFrom TEXT,
            TotalAmount DECIMAL(18,2),
            Narration TEXT,
            Authorize INTEGER DEFAULT 0,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Bill Booking Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Billbooking_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            BillNo VARCHAR(50),
            BillDate VARCHAR(50),
            VendorId INTEGER,
            VendorName TEXT,
            TotalAmount DECIMAL(18,2),
            TaxAmount DECIMAL(18,2),
            NetAmount DECIMAL(18,2),
            Narration TEXT,
            Authorize INTEGER DEFAULT 0,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Bill Booking Details
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Billbooking_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            AccHeadId INTEGER,
            Description TEXT,
            Amount DECIMAL(18,2),
            FOREIGN KEY (MasterId) REFERENCES tblAcc_Billbooking_master(Id)
        )
        """)

        # Contra Entry / Journal Entry
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Contra_Entry (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            EntryNo VARCHAR(50),
            EntryDate VARCHAR(50),
            DebitAccHead INTEGER,
            CreditAccHead INTEGER,
            Amount DECIMAL(18,2),
            Narration TEXT,
            Authorize INTEGER DEFAULT 0,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Sales Invoice Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Salesinvoice_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            InvoiceNo VARCHAR(50),
            InvoiceDate VARCHAR(50),
            CustomerId INTEGER,
            CustomerName TEXT,
            GrossAmount DECIMAL(18,2),
            TaxAmount DECIMAL(18,2),
            NetAmount DECIMAL(18,2),
            Narration TEXT,
            Authorize INTEGER DEFAULT 0,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Sales Invoice Details
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Salesinvoice_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            ItemId INTEGER,
            ItemName TEXT,
            Quantity DECIMAL(18,2),
            Rate DECIMAL(18,2),
            Amount DECIMAL(18,2),
            FOREIGN KEY (MasterId) REFERENCES tblAcc_Salesinvoice_master(Id)
        )
        """)

        # Payment Terms
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Paymentmode (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PaymentMode VARCHAR(100),
            Description TEXT,
            Flag INTEGER DEFAULT 1
        )
        """)

        # TDS Code Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_TDScode_master (
            TDSCodeId INTEGER PRIMARY KEY AUTOINCREMENT,
            TDSCode VARCHAR(50),
            TDSName VARCHAR(200),
            TDSRate DECIMAL(5,2),
            Description TEXT,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Additional lookup tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Intresttype (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            IntrestType VARCHAR(100),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Invoiceagainst (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            InvoiceAgainst VARCHAR(100),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_IOU_Reasons (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Reason VARCHAR(200),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Loantype (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            LoanType VARCHAR(100),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Paidtype (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PaidType VARCHAR(100),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Receiptagainst (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            ReceiptAgainst VARCHAR(100),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Tourexpencesstype (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            ExpenseType VARCHAR(100),
            Flag INTEGER DEFAULT 1
        )
        """)

        # Service Tax tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Servicetaxinvoice_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            InvoiceNo VARCHAR(50),
            InvoiceDate VARCHAR(50),
            PartyName TEXT,
            GrossAmount DECIMAL(18,2),
            ServiceTax DECIMAL(18,2),
            NetAmount DECIMAL(18,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Servicetaxinvoice_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            ServiceDescription TEXT,
            Amount DECIMAL(18,2),
            FOREIGN KEY (MasterId) REFERENCES tblAcc_Servicetaxinvoice_master(Id)
        )
        """)

        # Proforma Invoice
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Proformainvoice_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            PINo VARCHAR(50),
            PIDate VARCHAR(50),
            CustomerName TEXT,
            TotalAmount DECIMAL(18,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Proformainvoice_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            ItemDescription TEXT,
            Quantity DECIMAL(18,2),
            Rate DECIMAL(18,2),
            Amount DECIMAL(18,2),
            FOREIGN KEY (MasterId) REFERENCES tblAcc_Proformainvoice_master(Id)
        )
        """)

        # Capital and Loan tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Capital_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            CapitalType VARCHAR(100),
            Amount DECIMAL(18,2),
            Date VARCHAR(50),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Capital_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            Description TEXT,
            Amount DECIMAL(18,2),
            FOREIGN KEY (MasterId) REFERENCES tblAcc_Capital_master(Id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Loanmaster (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            LoanNo VARCHAR(50),
            LoanType INTEGER,
            BankId INTEGER,
            LoanAmount DECIMAL(18,2),
            InterestRate DECIMAL(5,2),
            StartDate VARCHAR(50),
            EndDate VARCHAR(50),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Loandetails (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            EMIDate VARCHAR(50),
            EMIAmount DECIMAL(18,2),
            Principal DECIMAL(18,2),
            Interest DECIMAL(18,2),
            Balance DECIMAL(18,2),
            FOREIGN KEY (MasterId) REFERENCES tblAcc_Loanmaster(Id)
        )
        """)

        # Tour voucher
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Tourvoucher_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            VoucherNo VARCHAR(50),
            VoucherDate VARCHAR(50),
            EmployeeId INTEGER,
            TotalAmount DECIMAL(18,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Tourvoucheradvance_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            ExpenseType INTEGER,
            Amount DECIMAL(18,2),
            Remarks TEXT,
            FOREIGN KEY (MasterId) REFERENCES tblAcc_Tourvoucher_master(Id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Tourintimation_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            IntimationNo VARCHAR(50),
            IntimationDate VARCHAR(50),
            EmployeeId INTEGER,
            Purpose TEXT,
            FromDate VARCHAR(50),
            ToDate VARCHAR(50),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_IOU_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            IOUNo VARCHAR(50),
            IOUDate VARCHAR(50),
            EmployeeId INTEGER,
            Amount DECIMAL(18,2),
            Reason INTEGER,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Advice Payment
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Advice_Payment_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            AdviceNo VARCHAR(50),
            AdviceDate VARCHAR(50),
            VendorName TEXT,
            TotalAmount DECIMAL(18,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Advice_Payment_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            MasterId INTEGER,
            BillNo VARCHAR(50),
            BillDate VARCHAR(50),
            Amount DECIMAL(18,2),
            FOREIGN KEY (MasterId) REFERENCES tblAcc_Advice_Payment_master(Id)
        )
        """)

        # Asset Register
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Asset_Register (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            AssetCode VARCHAR(50),
            AssetName TEXT,
            AssetType VARCHAR(100),
            PurchaseDate VARCHAR(50),
            PurchaseValue DECIMAL(18,2),
            DepreciationRate DECIMAL(5,2),
            CurrentValue DECIMAL(18,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        # Debit Note
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Debitnote (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            SysDate VARCHAR(50),
            SysTime VARCHAR(50),
            SessionId TEXT,
            CompId INTEGER,
            FinYearId INTEGER,
            DebitNoteNo VARCHAR(50),
            DebitNoteDate VARCHAR(50),
            VendorName TEXT,
            Amount DECIMAL(18,2),
            Reason TEXT,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Excise, Freight, Octori, Packing
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblExcisecommodity_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            CommodityName VARCHAR(200),
            HSNCode VARCHAR(50),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblExciseser_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            ServiceName VARCHAR(200),
            SACCode VARCHAR(50),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblFreight_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            FreightType VARCHAR(100),
            Rate DECIMAL(18,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblOctroi_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            OctroiType VARCHAR(100),
            Rate DECIMAL(5,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblPacking_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PackingType VARCHAR(100),
            Charges DECIMAL(18,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        # VAT and Warranty
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblVAT_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            VATType VARCHAR(100),
            VATRate DECIMAL(5,2),
            Flag INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblwarrenty_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            WarrantyType VARCHAR(100),
            Period INTEGER,
            Description TEXT,
            Flag INTEGER DEFAULT 1
        )
        """)

        # Bill Booking Attach
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblAcc_Billbooking_Attach_master (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            BillBookingId INTEGER,
            FileName VARCHAR(255),
            FilePath TEXT,
            UploadDate VARCHAR(50),
            FOREIGN KEY (BillBookingId) REFERENCES tblAcc_Billbooking_master(Id)
        )
        """)

        print("✅ All Accounts tables created successfully!")


def insert_test_data():
    """Insert minimal test data for testing"""

    import sqlite3
    db_path = connection.settings_dict['NAME']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\nInserting test data...")

        # Insert test currency
        cursor.execute("""
        INSERT OR IGNORE INTO tblAcc_Currency_master
        (CurrencyId, CurrencyName, CurrencyCode, Symbol, ExchangeRate, Flag, SysDate, SysTime, SessionId, CompId, FinYearId)
        VALUES (1, 'Indian Rupee', 'INR', '₹', 1.0, 1, '14-11-2025', '00:00:00', '1', 1, 1)
        """)

        # Insert test account heads
        account_heads = [
            (1, 'Cash', 'CASH001', 'Asset', 'Current Assets', 100000, 'Dr'),
            (2, 'Bank - HDFC', 'BANK001', 'Asset', 'Current Assets', 500000, 'Dr'),
            (3, 'Sundry Debtors', 'DEBT001', 'Asset', 'Current Assets', 250000, 'Dr'),
            (4, 'Sundry Creditors', 'CRED001', 'Liability', 'Current Liabilities', 150000, 'Cr'),
            (5, 'Sales', 'SALE001', 'Income', 'Direct Income', 0, 'Cr'),
            (6, 'Purchase', 'PURCH001', 'Expense', 'Direct Expense', 0, 'Dr'),
            (7, 'Salary', 'SAL001', 'Expense', 'Indirect Expense', 0, 'Dr'),
            (8, 'Rent', 'RENT001', 'Expense', 'Indirect Expense', 0, 'Dr'),
        ]

        for acc_id, name, code, acc_type, under_group, opening_bal, debit_credit in account_heads:
            cursor.execute("""
            INSERT OR IGNORE INTO Acc_head
            (Id, AccHeadName, AccHeadCode, AccType, UnderGroup, OpeningBalance, DebitCredit, Flag, SysDate, SysTime, SessionId, CompId, FinYearId)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, '14-11-2025', '00:00:00', '1', 1, 1)
            """, (acc_id, name, code, acc_type, under_group, opening_bal, debit_credit))

        # Insert test bank
        cursor.execute("""
        INSERT OR IGNORE INTO tblAcc_Bank
        (BankId, BankName, BankCode, Branch, AccountNo, IFSCCode, OpeningBalance, Flag, SysDate, SysTime, SessionId, CompId, FinYearId)
        VALUES (1, 'HDFC Bank', 'HDFC001', 'Mumbai Main Branch', '50100123456789', 'HDFC0001234', 500000, 1, '14-11-2025', '00:00:00', '1', 1, 1)
        """)

        # Insert test payment modes
        payment_modes = ['Cash', 'Cheque', 'NEFT/RTGS', 'UPI', 'Card']
        for i, mode in enumerate(payment_modes, 1):
            cursor.execute("""
            INSERT OR IGNORE INTO tblAcc_Paymentmode (Id, PaymentMode, Flag)
            VALUES (?, ?, 1)
            """, (i, mode))

        # Insert test TDS codes
        cursor.execute("""
        INSERT OR IGNORE INTO tblAcc_TDScode_master
        (TDSCodeId, TDSCode, TDSName, TDSRate, Flag)
        VALUES
        (1, '194C', 'Payment to Contractors', 2.0, 1),
        (2, '194J', 'Professional Services', 10.0, 1),
        (3, '194A', 'Interest Other Than Securities', 10.0, 1)
        """)

        # Insert lookup data
        cursor.execute("INSERT OR IGNORE INTO tblAcc_Intresttype (Id, IntrestType) VALUES (1, 'Simple Interest'), (2, 'Compound Interest')")
        cursor.execute("INSERT OR IGNORE INTO tblAcc_Invoiceagainst (Id, InvoiceAgainst) VALUES (1, 'Order'), (2, 'Performa')")
        cursor.execute("INSERT OR IGNORE INTO tblAcc_IOU_Reasons (Id, Reason) VALUES (1, 'Travel'), (2, 'Office Supplies'), (3, 'Emergency')")
        cursor.execute("INSERT OR IGNORE INTO tblAcc_Loantype (Id, LoanType) VALUES (1, 'Term Loan'), (2, 'Working Capital'), (3, 'Overdraft')")
        cursor.execute("INSERT OR IGNORE INTO tblAcc_Paidtype (Id, PaidType) VALUES (1, 'Advance'), (2, 'Against Bill')")
        cursor.execute("INSERT OR IGNORE INTO tblAcc_Receiptagainst (Id, ReceiptAgainst) VALUES (1, 'Sales'), (2, 'Advance')")
        cursor.execute("INSERT OR IGNORE INTO tblAcc_Tourexpencesstype (Id, ExpenseType) VALUES (1, 'Travel'), (2, 'Food'), (3, 'Accommodation')")

        conn.commit()
        print("✅ Test data inserted successfully!")

    finally:
        cursor.close()
        conn.close()


def main():
    print("="*60)
    print("Setting up Test Database for Accounts Module")
    print("="*60)

    try:
        create_accounts_tables()
        insert_test_data()

        print("\n" + "="*60)
        print("✅ Database setup completed successfully!")
        print("="*60)
        print("\nYou can now run the Playwright tests:")
        print("  pytest tests/playwright/test_accounts_smoke.py -v")

    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
