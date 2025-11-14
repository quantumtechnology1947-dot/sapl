"""
Business Group Budget Service
Calculates budget allocations and usage for business groups
"""

from decimal import Decimal
from django.db.models import Sum, Q
from human_resource.models import Businessgroup
from mis.models import (
    TblaccBudgetWo,
    TblmmSprDetails,
    TblPackingMaster,
    TblExciseserMaster,
    TblVatMaster
)
from material_management.models import POMaster, PODetails
from accounts.models import (
    TblaccCashvoucherPaymentMaster,
    TblaccCashvoucherPaymentDetails,
    TblaccCashvoucherReceiptMaster,
    TblaccBudgetDept
)


class BusinessGroupBudgetService:
    """Service for calculating business group budget data"""
    
    def __init__(self, company_id, fin_year_id):
        self.company_id = company_id
        self.fin_year_id = fin_year_id
    
    def get_all_business_groups_with_budget(self):
        """
        Get all business groups with their budget calculations
        Returns list of dicts with budget data
        """
        business_groups = Businessgroup.objects.all().order_by('name')
        
        result = []
        for bg in business_groups:
            budget_data = self._calculate_budget_for_group(bg.id)
            result.append({
                'id': bg.id,
                'name': bg.name,
                'symbol': bg.symbol,
                'incharge': bg.incharge,
                **budget_data
            })
        
        return result
    
    def _calculate_budget_for_group(self, bg_id):
        """Calculate budget totals for a business group"""

        # Get total budget allocated for this business group (CUMULATIVE from all years)
        # In ASP.NET: "select Sum(Amount) As Budget from tblACC_Budget_Dept where BGId='" + BGId + "' And CompId=" + CompId + " And FinYearId<=" + FinYearId
        # NOTE: Using FinYearId <= (not =) to get cumulative budget from all previous years
        budget_allocated = TblaccBudgetDept.objects.filter(
            compid=self.company_id,
            finyearid__lte=self.fin_year_id,  # Changed from = to <=
            bgid=bg_id
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # TODO: Add opening balance from previous year
        # openingBalOfPrevYear = calbalbud.TotBalBudget_BG(BGId, CompId, prevYear, 0);
        # budget = budget_allocated + openingBalOfPrevYear
        
        # Get PO total (Basic + Discount amount)
        po_total = self._get_po_total_for_group(bg_id)
        
        # Get Tax total
        tax_total = self._get_tax_total_for_group(bg_id)
        
        # Get Cash Payment total
        cash_pay_total = self._get_cash_payment_total(bg_id)
        
        # Get Cash Receipt total
        cash_rec_total = self._get_cash_receipt_total(bg_id)
        
        # Calculate balance
        # ASP.NET: TotBalBudget = Math.Round(budget - (POSPRBasicDiscAmt + POSPRTaxAmt + totalCash), 2) + totalCashRec;
        # Convert all to Decimal for consistent calculation
        budget_allocated = Decimal(str(budget_allocated)) if budget_allocated else Decimal('0')
        po_total = Decimal(str(po_total)) if po_total else Decimal('0')
        tax_total = Decimal(str(tax_total)) if tax_total else Decimal('0')
        cash_pay_total = Decimal(str(cash_pay_total)) if cash_pay_total else Decimal('0')
        cash_rec_total = Decimal(str(cash_rec_total)) if cash_rec_total else Decimal('0')
        
        balance = budget_allocated - (po_total + tax_total + cash_pay_total) + cash_rec_total
        
        return {
            'budget_amount': float(budget_allocated),
            'po_total': float(po_total),
            'cash_pay': float(cash_pay_total),
            'cash_rec': float(cash_rec_total),
            'tax': float(tax_total),
            'balance': float(balance),
        }
    
    def _get_po_total_for_group(self, bg_id):
        """
        Get total PO amount for business group - OPTIMIZED with raw SQL (CUMULATIVE)
        ASP.NET: PBM.getTotal_PO_Budget_Amt(CompId, BGId, 1, 1, "0", BGId, 1, FinYearId)
        NOTE: Uses FinYearId <= (cumulative) to match ASP.NET CalBalBudgetAmt.cs logic

        Calculates: Qty × Rate × (1 - Discount/100) for SPR-based POs where DeptId=BGId
        NOTE: Does NOT filter by Authorize status (matches ASP.NET behavior)
        """
        try:
            from django.db import connection

            # Use raw SQL for performance - matches ASP.NET query exactly
            query = """
                SELECT SUM(pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) AS total
                FROM tblMM_PO_Details pod
                INNER JOIN tblMM_PO_Master pom ON pod.PONo = pom.PONo
                INNER JOIN tblMM_SPR_Details sprd ON pod.SPRId = sprd.Id
                WHERE pom.CompId = %s
                  AND pom.FinYearId <= %s
                  AND pom.PRSPRFlag = 1
                  AND pod.BudgetCode = '0'
                  AND pod.SPRNo IS NOT NULL
                  AND pod.SPRNo != ''
                  AND sprd.DeptId = %s
            """

            with connection.cursor() as cursor:
                cursor.execute(query, [self.company_id, self.fin_year_id, bg_id])
                result = cursor.fetchone()
                return Decimal(str(result[0])) if result[0] else Decimal('0')

        except Exception as e:
            print(f"Error calculating PO total for BG {bg_id}: {e}")
            return Decimal('0')
    
    def _get_tax_total_for_group(self, bg_id):
        """
        Get total tax amount for business group - OPTIMIZED with raw SQL (CUMULATIVE)
        ASP.NET: PBM.getTotal_PO_Budget_Amt(CompId, BGId, 1, 1, "0", BGId, 2, FinYearId)
        NOTE: Uses FinYearId <= (cumulative) to match ASP.NET CalBalBudgetAmt.cs logic

        Calculates tax (PF + ExST + VAT) from PO details
        NOTE: Does NOT filter by Authorize status (matches ASP.NET behavior)
        """
        try:
            from django.db import connection

            # Use raw SQL for performance - calculates cascading tax
            # Tax calculation: PF + ExST + VAT (cascading)
            query = """
                SELECT SUM(
                    -- Basic discounted amount
                    (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0) +
                    -- ExST on (Basic + PF)
                    ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                     (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0)) * (COALESCE(exst.Value, 0) / 100.0) +
                    -- VAT on (Basic + PF + ExST)
                    ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                     (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0) +
                     ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                      (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0)) * (COALESCE(exst.Value, 0) / 100.0)) * (COALESCE(vat.Value, 0) / 100.0)
                ) AS total_tax
                FROM tblMM_PO_Details pod
                INNER JOIN tblMM_PO_Master pom ON pod.PONo = pom.PONo
                INNER JOIN tblMM_SPR_Details sprd ON pod.SPRId = sprd.Id
                LEFT JOIN tblPacking_Master pf ON pod.PF = pf.Id
                LEFT JOIN tblExciseser_Master exst ON pod.ExST = exst.Id
                LEFT JOIN tblVAT_Master vat ON pod.VAT = vat.Id
                WHERE pom.CompId = %s
                  AND pom.FinYearId <= %s
                  AND pom.PRSPRFlag = 1
                  AND pod.BudgetCode = '0'
                  AND pod.SPRNo IS NOT NULL
                  AND pod.SPRNo != ''
                  AND sprd.DeptId = %s
            """

            with connection.cursor() as cursor:
                cursor.execute(query, [self.company_id, self.fin_year_id, bg_id])
                result = cursor.fetchone()
                return Decimal(str(result[0])) if result[0] else Decimal('0')

        except Exception as e:
            print(f"Error calculating tax total for BG {bg_id}: {e}")
            return Decimal('0')
    
    def _get_tax_value(self, tax_id, model_class):
        """Get tax percentage from master table"""
        try:
            if not tax_id:
                return Decimal('0')
            tax_record = model_class.objects.filter(id=tax_id).first()
            if tax_record and hasattr(tax_record, 'value') and tax_record.value:
                return Decimal(str(tax_record.value))
            return Decimal('0')
        except:
            return Decimal('0')
    
    def _get_cash_payment_total(self, bg_id):
        """
        Get total cash payments for business group (CUMULATIVE from all years)
        Note: Amount is in Details table, not Master table
        ASP.NET: FinYearId <= current year (line 50 of CalBalBudgetAmt.cs)
        """
        try:
            # Sum from Details table, filtering by Master's company/year and Detail's bggroup
            total = TblaccCashvoucherPaymentDetails.objects.filter(
                mid__compid=self.company_id,
                mid__finyearid__lte=self.fin_year_id,  # Changed from = to <=
                bggroup=bg_id
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            return total
        except Exception as e:
            print(f"Error calculating cash payment total for BG {bg_id}: {e}")
            return Decimal('0')
    
    def _get_cash_receipt_total(self, bg_id):
        """
        Get total cash receipts for business group (CUMULATIVE from all years)
        Note: Receipt Master has amount field directly
        ASP.NET: FinYearId <= current year (line 58 of CalBalBudgetAmt.cs)
        """
        try:
            total = TblaccCashvoucherReceiptMaster.objects.filter(
                compid=self.company_id,
                finyearid__lte=self.fin_year_id,  # Changed from = to <=
                bggroup=bg_id
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            return total
        except Exception as e:
            print(f"Error calculating cash receipt total for BG {bg_id}: {e}")
            return Decimal('0')
