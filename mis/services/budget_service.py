"""
Budget Calculation Service

This service handles all budget-related calculations including:
- Total budget amounts with opening balances
- Budget consumption from POs, PRs, SPRs
- Cash voucher tracking
- Balance budget calculations
"""

from decimal import Decimal
from django.db.models import Sum
from mis.models import (
    TblmisBudgetcode,
    TblaccBudgetWo,
)
from .po_budget_calculator import POBudgetCalculator
from .cash_voucher_service import CashVoucherService


class BudgetCalculationService:
    """
    Core service for calculating budget balances and consumption
    """
    
    def __init__(self, company_id, fin_year_id):
        """
        Initialize the budget calculation service
        
        Args:
            company_id: Company ID from session
            fin_year_id: Financial Year ID from session
        """
        self.company_id = company_id
        self.fin_year_id = fin_year_id
        self.prev_year_id = fin_year_id - 1
        
        # Initialize sub-services
        self.po_calculator = POBudgetCalculator(company_id, fin_year_id)
        self.cash_service = CashVoucherService(company_id, fin_year_id)
    
    def get_budget_summary_for_wo(self, wo_no):
        """
        Calculate complete budget summary for a work order
        
        Args:
            wo_no: Work order number
            
        Returns:
            List of budget code summaries with all calculations
        """
        budget_codes = TblmisBudgetcode.objects.all().order_by('id')
        summary_list = []
        
        for code in budget_codes:
            # Get all budget components
            budget_amount = self._get_total_budget(code.id, wo_no)
            po_amount = self._get_po_amount(code.id, wo_no)
            tax_amount = self._get_tax_amount(code.id, wo_no)
            cash_pay = self._get_cash_payment(code.id, wo_no)
            cash_rec = self._get_cash_receipt(code.id, wo_no)
            
            # Calculate derived values
            invoice_amount = po_amount - tax_amount
            actual_amount = po_amount + tax_amount
            balance_budget = (
                budget_amount - 
                po_amount - 
                tax_amount - 
                cash_pay + 
                cash_rec
            )
            
            summary = {
                'id': code.id,
                'description': code.description or '',
                'symbol': code.symbol or '',
                'budget_code': f"{code.symbol}{wo_no}" if code.symbol else wo_no,
                'budget_amount': budget_amount,
                'po_amount': po_amount,
                'tax_amount': tax_amount,
                'cash_pay': cash_pay,
                'cash_rec': cash_rec,
                'invoice_amount': invoice_amount,
                'actual_amount': actual_amount,
                'balance_budget': balance_budget,
                'has_allocation': budget_amount > Decimal('0.00'),
            }
            
            summary_list.append(summary)
        
        return summary_list
    
    def _get_total_budget(self, budget_code_id, wo_no):
        """
        Get total budget including previous year opening balance
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Total budget amount
        """
        try:
            # Current year allocations
            current_budget = TblaccBudgetWo.objects.filter(
                budget_code_id=budget_code_id,
                wo_no=wo_no,
                fin_year_id=self.fin_year_id,
                comp_id=self.company_id
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Previous year opening balance
            opening_balance = self._get_opening_balance(budget_code_id, wo_no)
            
            total = current_budget + opening_balance
            return round(total, 2)
        except Exception as e:
            # Log error and return 0
            print(f"Error calculating total budget: {e}")
            return Decimal('0.00')
    
    def _get_opening_balance(self, budget_code_id, wo_no):
        """
        Calculate opening balance from previous year
        
        This recursively calculates the balance budget from the previous year
        which becomes the opening balance for the current year.
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Opening balance amount
        """
        try:
            if self.prev_year_id <= 0:
                return Decimal('0.00')
            
            # Get previous year's budget
            prev_budget = TblaccBudgetWo.objects.filter(
                budget_code_id=budget_code_id,
                wo_no=wo_no,
                fin_year_id=self.prev_year_id,
                comp_id=self.company_id
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            if prev_budget == Decimal('0.00'):
                return Decimal('0.00')
            
            # Calculate previous year's consumption
            prev_po_calculator = POBudgetCalculator(self.company_id, self.prev_year_id)
            prev_cash_service = CashVoucherService(self.company_id, self.prev_year_id)
            
            prev_po_amount = prev_po_calculator.get_total_po_amount(budget_code_id, wo_no)
            prev_tax_amount = prev_po_calculator.get_total_tax_amount(budget_code_id, wo_no)
            prev_cash_pay = prev_cash_service.get_cash_payment_amount(budget_code_id, wo_no)
            prev_cash_rec = prev_cash_service.get_cash_receipt_amount(budget_code_id, wo_no)
            
            # Balance from previous year
            balance = prev_budget - prev_po_amount - prev_tax_amount - prev_cash_pay + prev_cash_rec
            
            return round(balance, 2) if balance > Decimal('0.00') else Decimal('0.00')
        except Exception as e:
            print(f"Error calculating opening balance: {e}")
            return Decimal('0.00')
    
    def _get_po_amount(self, budget_code_id, wo_no):
        """
        Get PO amount (basic + discount) for budget code and work order
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: PO amount
        """
        try:
            return self.po_calculator.get_total_po_amount(budget_code_id, wo_no)
        except Exception as e:
            print(f"Error calculating PO amount: {e}")
            return Decimal('0.00')
    
    def _get_tax_amount(self, budget_code_id, wo_no):
        """
        Get tax amount for budget code and work order
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Tax amount
        """
        try:
            return self.po_calculator.get_total_tax_amount(budget_code_id, wo_no)
        except Exception as e:
            print(f"Error calculating tax amount: {e}")
            return Decimal('0.00')
    
    def _get_cash_payment(self, budget_code_id, wo_no):
        """
        Get cash payment amount for budget code and work order
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Cash payment amount
        """
        try:
            return self.cash_service.get_cash_payment_amount(budget_code_id, wo_no)
        except Exception as e:
            print(f"Error calculating cash payment: {e}")
            return Decimal('0.00')
    
    def _get_cash_receipt(self, budget_code_id, wo_no):
        """
        Get cash receipt amount for budget code and work order
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Cash receipt amount
        """
        try:
            return self.cash_service.get_cash_receipt_amount(budget_code_id, wo_no)
        except Exception as e:
            print(f"Error calculating cash receipt: {e}")
            return Decimal('0.00')
    
    def get_budget_totals(self, summary_list):
        """
        Calculate totals for all budget columns
        
        Args:
            summary_list: List of budget summaries
            
        Returns:
            Dict with totals for each column
        """
        totals = {
            'budget_amount': Decimal('0.00'),
            'po_amount': Decimal('0.00'),
            'tax_amount': Decimal('0.00'),
            'cash_pay': Decimal('0.00'),
            'cash_rec': Decimal('0.00'),
            'invoice_amount': Decimal('0.00'),
            'actual_amount': Decimal('0.00'),
            'balance_budget': Decimal('0.00'),
        }
        
        for item in summary_list:
            totals['budget_amount'] += item['budget_amount']
            totals['po_amount'] += item['po_amount']
            totals['tax_amount'] += item['tax_amount']
            totals['cash_pay'] += item['cash_pay']
            totals['cash_rec'] += item['cash_rec']
            totals['invoice_amount'] += item['invoice_amount']
            totals['actual_amount'] += item['actual_amount']
            totals['balance_budget'] += item['balance_budget']
        
        # Round all totals
        for key in totals:
            totals[key] = round(totals[key], 2)
        
        return totals
