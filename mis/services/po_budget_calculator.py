"""
PO Budget Calculator Service

Calculates PO-related budget consumption from PR and SPR based purchase orders.
Handles different calculation modes: basic, discount, tax, and total amounts.
"""

from decimal import Decimal
from django.db.models import Q
from mis.models import (
    TblmmPoMaster,
    TblmmPoDetails,
    TblmmPrMaster,
    TblmmSprMaster,
    TblPackingMaster,
    TblExciseserMaster,
    TblVatMaster,
)


class POBudgetCalculator:
    """
    Calculates PO-related budget consumption
    Handles both PR and SPR based POs with authorization filtering
    """
    
    # Calculation modes
    CALC_MODE_BASIC = 0
    CALC_MODE_BASIC_DISC = 1
    CALC_MODE_TAX_ONLY = 2
    CALC_MODE_TOTAL = 3
    
    def __init__(self, company_id, fin_year_id):
        """
        Initialize the PO budget calculator
        
        Args:
            company_id: Company ID from session
            fin_year_id: Financial Year ID from session
        """
        self.company_id = company_id
        self.fin_year_id = fin_year_id
    
    def get_total_po_amount(self, budget_code_id, wo_no):
        """
        Get total PO amount (basic + discount) for both PR and SPR
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Total PO amount
        """
        pr_amount = self._calculate_pr_po_amount(
            budget_code_id, wo_no, authorize_flag=1, calc_mode=self.CALC_MODE_BASIC_DISC
        )
        spr_amount = self._calculate_spr_po_amount(
            budget_code_id, wo_no, authorize_flag=1, calc_mode=self.CALC_MODE_BASIC_DISC
        )
        
        total = pr_amount + spr_amount
        return round(total, 2)
    
    def get_total_tax_amount(self, budget_code_id, wo_no):
        """
        Get total tax amount for both PR and SPR
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            
        Returns:
            Decimal: Total tax amount
        """
        pr_tax = self._calculate_pr_po_amount(
            budget_code_id, wo_no, authorize_flag=1, calc_mode=self.CALC_MODE_TAX_ONLY
        )
        spr_tax = self._calculate_spr_po_amount(
            budget_code_id, wo_no, authorize_flag=1, calc_mode=self.CALC_MODE_TAX_ONLY
        )
        
        total = pr_tax + spr_tax
        return round(total, 2)
    
    def _calculate_pr_po_amount(self, budget_code_id, wo_no, authorize_flag, calc_mode):
        """
        Calculate PO amount for PR-based POs
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            authorize_flag: 0 for non-authorized, 1 for authorized
            calc_mode: Calculation mode
            
        Returns:
            Decimal: Calculated amount
        """
        try:
            # Get authorized PO numbers for PR
            po_numbers = TblmmPoMaster.objects.filter(
                comp_id=self.company_id,
                pr_spr_flag=0,  # PR
                authorize=authorize_flag
            ).values_list('po_no', flat=True)
            
            # Get PO details for this budget code
            po_details = TblmmPoDetails.objects.filter(
                po_no__in=po_numbers,
                budget_code=budget_code_id
            ).exclude(
                Q(pr_no__isnull=True) | Q(pr_no='')
            )
            
            total_amount = Decimal('0.00')
            
            for detail in po_details:
                # Verify PR belongs to this work order
                pr_exists = TblmmPrMaster.objects.filter(
                    pr_no=detail.pr_no,
                    wo_no=wo_no,
                    comp_id=self.company_id
                ).exists()
                
                if pr_exists:
                    amount = self._calculate_line_amount(detail, calc_mode)
                    total_amount += amount
            
            return round(total_amount, 2)
        except Exception as e:
            print(f"Error calculating PR PO amount: {e}")
            return Decimal('0.00')
    
    def _calculate_spr_po_amount(self, budget_code_id, wo_no, authorize_flag, calc_mode):
        """
        Calculate PO amount for SPR-based POs
        
        Args:
            budget_code_id: Budget code ID
            wo_no: Work order number
            authorize_flag: 0 for non-authorized, 1 for authorized
            calc_mode: Calculation mode
            
        Returns:
            Decimal: Calculated amount
        """
        try:
            # Get authorized PO numbers for SPR
            po_numbers = TblmmPoMaster.objects.filter(
                comp_id=self.company_id,
                pr_spr_flag=1,  # SPR
                authorize=authorize_flag
            ).values_list('po_no', flat=True)
            
            # Get PO details for this budget code
            po_details = TblmmPoDetails.objects.filter(
                po_no__in=po_numbers,
                budget_code=budget_code_id
            ).exclude(
                Q(spr_no__isnull=True) | Q(spr_no='')
            )
            
            total_amount = Decimal('0.00')
            
            for detail in po_details:
                # Verify SPR belongs to this work order
                from mis.models import TblmmSprDetails
                spr_exists = TblmmSprDetails.objects.filter(
                    spr_no=detail.spr_no,
                    wo_no=wo_no
                ).exists()
                
                if spr_exists:
                    amount = self._calculate_line_amount(detail, calc_mode)
                    total_amount += amount
            
            return round(total_amount, 2)
        except Exception as e:
            print(f"Error calculating SPR PO amount: {e}")
            return Decimal('0.00')
    
    def _calculate_line_amount(self, detail, calc_mode):
        """
        Calculate amount for a single PO line based on mode
        
        Args:
            detail: TblmmPoDetails instance
            calc_mode: Calculation mode (0=basic, 1=basic-disc, 2=tax, 3=total)
            
        Returns:
            Decimal: Calculated amount
        """
        try:
            qty = Decimal(str(detail.qty))
            rate = Decimal(str(detail.rate))
            discount = Decimal(str(detail.discount)) if detail.discount else Decimal('0.00')
            
            if calc_mode == self.CALC_MODE_BASIC:
                # Basic amount = Qty * Rate
                return qty * rate
            
            elif calc_mode == self.CALC_MODE_BASIC_DISC:
                # Basic with discount = (Qty * Rate) - Discount Amount
                basic = qty * rate
                disc_amount = basic * (discount / Decimal('100'))
                return basic - disc_amount
            
            elif calc_mode == self.CALC_MODE_TAX_ONLY:
                # Calculate only tax components
                basic_disc = self._calculate_line_amount(detail, self.CALC_MODE_BASIC_DISC)
                
                # Get tax percentages
                pf_pct = self._get_tax_value(detail.pf, TblPackingMaster)
                exst_pct = self._get_tax_value(detail.ex_st, TblExciseserMaster)
                vat_pct = self._get_tax_value(detail.vat, TblVatMaster)
                
                # Calculate cascading tax
                pf_amt = basic_disc * (pf_pct / Decimal('100'))
                exst_base = basic_disc + pf_amt
                exst_amt = exst_base * (exst_pct / Decimal('100'))
                vat_base = exst_base + exst_amt
                vat_amt = vat_base * (vat_pct / Decimal('100'))
                
                return pf_amt + exst_amt + vat_amt
            
            elif calc_mode == self.CALC_MODE_TOTAL:
                # Total = Basic with discount + Tax
                basic_disc = self._calculate_line_amount(detail, self.CALC_MODE_BASIC_DISC)
                tax = self._calculate_line_amount(detail, self.CALC_MODE_TAX_ONLY)
                return basic_disc + tax
            
            return Decimal('0.00')
        except Exception as e:
            print(f"Error calculating line amount: {e}")
            return Decimal('0.00')
    
    def _get_tax_value(self, tax_id, model_class):
        """
        Get tax percentage from master table
        
        Args:
            tax_id: Tax master ID
            model_class: Model class (TblPackingMaster, TblExciseserMaster, TblVatMaster)
            
        Returns:
            Decimal: Tax percentage value
        """
        try:
            if not tax_id:
                return Decimal('0.00')
            
            tax_record = model_class.objects.filter(id=tax_id).first()
            if tax_record and tax_record.value:
                return Decimal(str(tax_record.value))
            
            return Decimal('0.00')
        except Exception as e:
            print(f"Error getting tax value: {e}")
            return Decimal('0.00')
