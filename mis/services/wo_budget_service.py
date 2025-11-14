"""
Work Order Budget Service
Calculates budget allocations and usage for work orders
Converted from: aaspnet/Module/MIS/Transactions/Budget_WONo.aspx.cs
"""

from decimal import Decimal
from django.db.models import Sum, Q
from mis.models import TblmisBudgetcode, TblaccBudgetWo
from material_management.models import POMaster, PODetails
from accounts.models import TblaccCashvoucherPaymentMaster, TblaccCashvoucherPaymentDetails, TblaccCashvoucherReceiptMaster


class WOBudgetService:
    """Service for calculating work order budget data"""

    def __init__(self, company_id, fin_year_id, wo_no):
        self.company_id = company_id
        self.fin_year_id = fin_year_id
        self.wo_no = wo_no

    def get_all_budget_codes_with_data(self):
        """
        Get all budget codes with their budget calculations for the work order
        Returns list of dicts with budget data
        """
        budget_codes = TblmisBudgetcode.objects.all().order_by('description')

        result = []
        for code in budget_codes:
            budget_data = self._calculate_budget_for_code(code.id)
            result.append({
                'id': code.id,
                'description': code.description,
                'symbol': code.symbol,
                'budget_code': f"{code.symbol}{self.wo_no}",
                **budget_data
            })

        return result

    def _calculate_budget_for_code(self, code_id):
        """Calculate budget totals for a budget code"""

        # Get total budget allocated for this WO and budget code
        budget_allocated = TblaccBudgetWo.objects.filter(
            comp_id=self.company_id,
            fin_year_id=self.fin_year_id,
            wo_no=self.wo_no,
            budget_code_id=code_id
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Get PO total (Purchase Orders)
        po_total = self._get_po_total_for_code(code_id)

        # Get Cash Payment total
        cash_pay_total = self._get_cash_payment_total(code_id)

        # Get Cash Receipt total
        cash_rec_total = self._get_cash_receipt_total(code_id)

        # Get Tax total
        tax_total = self._get_tax_total(code_id)

        # Calculate invoice amount (PO - Tax)
        invoice_amount = po_total - tax_total

        # Calculate actual amount (PO + Tax)
        actual_amount = po_total + tax_total

        # Calculate balance
        balance = budget_allocated - po_total - cash_pay_total + cash_rec_total - tax_total

        return {
            'budget_amount': float(budget_allocated),
            'po_total': float(po_total),
            'cash_pay': float(cash_pay_total),
            'cash_rec': float(cash_rec_total),
            'tax': float(tax_total),
            'balance': float(balance),
            'invoice': float(invoice_amount),
            'actual_amount': float(actual_amount),
        }

    def _get_po_total_for_code(self, code_id):
        """
        Get total PO amount for budget code and work order
        Matches ASP.NET PO_Budget_Amt.getTotal_PO_Budget_Amt logic
        Joins through PR/SPR to filter by WO number
        """
        try:
            from django.db import connection

            # Query for PR-based POs (PRSPRFlag=0)
            # Joins: PO_Details -> PO_Master -> PR_Details -> PR_Master
            # Filters by: CompId, FinYearId, BudgetCode, WONo (in PR_Master)
            pr_query = """
                SELECT SUM(pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) AS total
                FROM tblMM_PO_Details pod
                INNER JOIN tblMM_PO_Master pom ON pod.MId = pom.Id
                INNER JOIN tblMM_PR_Details prd ON pod.PRId = prd.Id
                INNER JOIN tblMM_PR_Master prm ON prd.MId = prm.Id
                WHERE pom.CompId = %s
                  AND pom.FinYearId = %s
                  AND pom.PRSPRFlag = 0
                  AND pod.BudgetCode = %s
                  AND prm.WONo = %s
            """

            # Query for SPR-based POs (PRSPRFlag=1)
            # Joins: PO_Details -> PO_Master -> SPR_Details -> SPR_Master
            # Filters by: CompId, FinYearId, BudgetCode, WONo (in SPR_Details)
            spr_query = """
                SELECT SUM(pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) AS total
                FROM tblMM_PO_Details pod
                INNER JOIN tblMM_PO_Master pom ON pod.MId = pom.Id
                INNER JOIN tblMM_SPR_Details sprd ON pod.SPRId = sprd.Id
                INNER JOIN tblMM_SPR_Master sprm ON sprd.MId = sprm.Id
                WHERE pom.CompId = %s
                  AND pom.FinYearId = %s
                  AND pom.PRSPRFlag = 1
                  AND pod.BudgetCode = %s
                  AND sprd.WONo = %s
            """

            pr_total = Decimal('0')
            spr_total = Decimal('0')

            with connection.cursor() as cursor:
                # Get PR total
                cursor.execute(pr_query, [self.company_id, self.fin_year_id, code_id, self.wo_no])
                result = cursor.fetchone()
                if result[0]:
                    pr_total = Decimal(str(result[0]))

                # Get SPR total
                cursor.execute(spr_query, [self.company_id, self.fin_year_id, code_id, self.wo_no])
                result = cursor.fetchone()
                if result[0]:
                    spr_total = Decimal(str(result[0]))

            return pr_total + spr_total

        except Exception as e:
            print(f"Error calculating PO total for code {code_id}, WO {self.wo_no}: {e}")
            import traceback
            traceback.print_exc()
            return Decimal('0')

    def _get_tax_total(self, code_id):
        """
        Get total tax amount for budget code and work order
        Matches ASP.NET PO_Budget_Amt.getTotal_PO_Budget_Amt logic with BasicTax=2
        Joins through PR/SPR to filter by WO number
        """
        try:
            from django.db import connection

            # Query for PR-based POs (PRSPRFlag=0)
            # Calculates cascading tax: PF + ExST + VAT
            pr_query = """
                SELECT SUM(
                    (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0) +
                    ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                     (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0)) * (COALESCE(exst.Value, 0) / 100.0) +
                    ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                     (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0) +
                     ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                      (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0)) * (COALESCE(exst.Value, 0) / 100.0)) * (COALESCE(vat.Value, 0) / 100.0)
                ) AS total_tax
                FROM tblMM_PO_Details pod
                INNER JOIN tblMM_PO_Master pom ON pod.MId = pom.Id
                INNER JOIN tblMM_PR_Details prd ON pod.PRId = prd.Id
                INNER JOIN tblMM_PR_Master prm ON prd.MId = prm.Id
                LEFT JOIN tblPacking_Master pf ON pod.PF = pf.Id
                LEFT JOIN tblExciseser_Master exst ON pod.ExST = exst.Id
                LEFT JOIN tblVAT_Master vat ON pod.VAT = vat.Id
                WHERE pom.CompId = %s
                  AND pom.FinYearId = %s
                  AND pom.PRSPRFlag = 0
                  AND pod.BudgetCode = %s
                  AND prm.WONo = %s
            """

            # Query for SPR-based POs (PRSPRFlag=1)
            spr_query = """
                SELECT SUM(
                    (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0) +
                    ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                     (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0)) * (COALESCE(exst.Value, 0) / 100.0) +
                    ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                     (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0) +
                     ((pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) +
                      (pod.Qty * pod.Rate * (1 - pod.Discount / 100.0)) * (COALESCE(pf.Value, 0) / 100.0)) * (COALESCE(exst.Value, 0) / 100.0)) * (COALESCE(vat.Value, 0) / 100.0)
                ) AS total_tax
                FROM tblMM_PO_Details pod
                INNER JOIN tblMM_PO_Master pom ON pod.MId = pom.Id
                INNER JOIN tblMM_SPR_Details sprd ON pod.SPRId = sprd.Id
                INNER JOIN tblMM_SPR_Master sprm ON sprd.MId = sprm.Id
                LEFT JOIN tblPacking_Master pf ON pod.PF = pf.Id
                LEFT JOIN tblExciseser_Master exst ON pod.ExST = exst.Id
                LEFT JOIN tblVAT_Master vat ON pod.VAT = vat.Id
                WHERE pom.CompId = %s
                  AND pom.FinYearId = %s
                  AND pom.PRSPRFlag = 1
                  AND pod.BudgetCode = %s
                  AND sprd.WONo = %s
            """

            pr_tax = Decimal('0')
            spr_tax = Decimal('0')

            with connection.cursor() as cursor:
                # Get PR tax total
                cursor.execute(pr_query, [self.company_id, self.fin_year_id, code_id, self.wo_no])
                result = cursor.fetchone()
                if result[0]:
                    pr_tax = Decimal(str(result[0]))

                # Get SPR tax total
                cursor.execute(spr_query, [self.company_id, self.fin_year_id, code_id, self.wo_no])
                result = cursor.fetchone()
                if result[0]:
                    spr_tax = Decimal(str(result[0]))

            return pr_tax + spr_tax

        except Exception as e:
            print(f"Error calculating tax total for code {code_id}, WO {self.wo_no}: {e}")
            import traceback
            traceback.print_exc()
            return Decimal('0')

    def _get_cash_payment_total(self, code_id):
        """
        Get total cash payments for budget code and work order
        ASP.NET query (line 122 Budget_WONo.aspx.cs):
        Filters by: WONo, FinYearId, BudgetCode
        """
        try:
            total = TblaccCashvoucherPaymentDetails.objects.filter(
                mid__compid=self.company_id,
                mid__finyearid=self.fin_year_id,
                wono=self.wo_no,
                budgetcode=code_id
            ).aggregate(total=Sum('amount'))['total']
            return Decimal(str(total)) if total is not None else Decimal('0')
        except Exception as e:
            print(f"Error calculating cash payment for code {code_id}, WO {self.wo_no}: {e}")
            return Decimal('0')

    def _get_cash_receipt_total(self, code_id):
        """
        Get total cash receipts for budget code and work order
        ASP.NET query (line 135 Budget_WONo.aspx.cs):
        Filters by: WONo, BudgetCode, FinYearId
        """
        try:
            total = TblaccCashvoucherReceiptMaster.objects.filter(
                compid=self.company_id,
                finyearid=self.fin_year_id,
                wono=self.wo_no,
                budgetcode=code_id
            ).aggregate(total=Sum('amount'))['total']
            return Decimal(str(total)) if total is not None else Decimal('0')
        except Exception as e:
            print(f"Error calculating cash receipt for code {code_id}, WO {self.wo_no}: {e}")
            return Decimal('0')
