"""
Cash Voucher Service

Handles cash voucher payment and receipt calculations for budget tracking.
"""

from decimal import Decimal
from django.db.models import Sum
from mis.models import (
    TblaccCashVoucherPaymentDetails,
    TblaccCashVoucherReceiptMaster,
)


class CashVoucherService:
    """
    Service for calculating cash voucher amounts
    Handles both cash payments and cash receipts
    """
    
    def __init__(self, company_id, fin_year_id):
        """
        Initialize the cash voucher service
        
        Args:
            company_id: Company ID from session
            fin_year_id: Financial Year ID from session
        """
        self.company_id = company_id
        self.fin_year_id = fin_year_id
    
    def get_cash_payment_amount(self, budget_code_id, wo_no):
        """
        Calculate total cash payment amount for a budget code and work order
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Total cash payment amount
        """
        try:
            # Get cash payment details filtered by company, fin year, WO, and budget code
            total = TblaccCashVoucherPaymentDetails.objects.filter(
                m_id__comp_id=self.company_id,
                m_id__fin_year_id=self.fin_year_id,
                wo_no=wo_no,
                budget_code=budget_code_id
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            return round(total, 2)
        except Exception as e:
            print(f"Error calculating cash payment amount: {e}")
            return Decimal('0.00')
    
    def get_cash_receipt_amount(self, budget_code_id, wo_no):
        """
        Calculate total cash receipt amount for a budget code and work order
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Total cash receipt amount
        """
        try:
            # Get cash receipt amounts filtered by company, fin year, WO, and budget code
            total = TblaccCashVoucherReceiptMaster.objects.filter(
                comp_id=self.company_id,
                fin_year_id=self.fin_year_id,
                wo_no=wo_no,
                budget_code=budget_code_id
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            return round(total, 2)
        except Exception as e:
            print(f"Error calculating cash receipt amount: {e}")
            return Decimal('0.00')
    
    def get_cash_voucher_details(self, budget_code_id, wo_no):
        """
        Get detailed cash voucher transactions for a budget code and work order
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Dict with payment and receipt details
        """
        try:
            # Get payment details
            payments = TblaccCashVoucherPaymentDetails.objects.filter(
                m_id__comp_id=self.company_id,
                m_id__fin_year_id=self.fin_year_id,
                wo_no=wo_no,
                budget_code=budget_code_id
            ).select_related('m_id').order_by('id')
            
            # Get receipt details
            receipts = TblaccCashVoucherReceiptMaster.objects.filter(
                comp_id=self.company_id,
                fin_year_id=self.fin_year_id,
                wo_no=wo_no,
                budget_code=budget_code_id
            ).order_by('id')
            
            return {
                'payments': [
                    {
                        'id': p.id,
                        'master_id': p.m_id_id,
                        'amount': p.amount,
                        'wo_no': p.wo_no,
                    }
                    for p in payments
                ],
                'receipts': [
                    {
                        'id': r.id,
                        'amount': r.amount,
                        'wo_no': r.wo_no,
                    }
                    for r in receipts
                ]
            }
        except Exception as e:
            print(f"Error getting cash voucher details: {e}")
            return {'payments': [], 'receipts': []}
