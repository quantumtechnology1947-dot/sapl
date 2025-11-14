"""
Loan Service
Business logic for bank loans and mobile bill calculations
"""

from datetime import datetime
from ..models import TblhrBankloan, TblhrMobilebill, TblhrCoporatemobileno


class LoanService:
    """
    Service class for loan and mobile bill business logic
    """

    @staticmethod
    def calculate_loan_installment(loan_amount, tenure_months):
        """
        Calculate monthly installment for a loan
        Simple equal installment calculation (can be enhanced with interest)
        """
        if tenure_months == 0:
            return 0
        return loan_amount / tenure_months

    @staticmethod
    def get_remaining_installments(loan):
        """
        Calculate remaining installments for a loan
        """
        if not loan.noofinstallment or not loan.installment:
            return 0

        # This is simplified - actual logic would track paid installments
        total_installments = loan.noofinstallment or 0
        # In production, query TblhrSalaryDetails to count paid installments
        paid_installments = 0  # TODO: Calculate from salary details

        return total_installments - paid_installments

    @staticmethod
    def calculate_mobile_excess(bill_amount, limit_amount):
        """
        Calculate excess mobile bill amount
        """
        excess = bill_amount - limit_amount
        return max(excess, 0)

    @staticmethod
    def get_employee_mobile_limit(mobile_no):
        """
        Get mobile number limit from corporate mobile master
        """
        mobile = TblhrCoporatemobileno.objects.filter(mobileno=mobile_no).first()
        return mobile.limitamt if mobile else 0

    @staticmethod
    def get_total_loan_amount(empid, company_id, fy_id):
        """
        Get total outstanding loan amount for an employee
        """
        loans = TblhrBankloan.objects.filter(
            empid=empid,
            compid=company_id,
            finyearid=fy_id
        )
        return sum(loan.loanamt or 0 for loan in loans)

    @staticmethod
    def get_monthly_deductions(empid, month, company_id, fy_id):
        """
        Calculate total monthly deductions for loans and mobile bills
        """
        # Bank loan installment
        loan_installment = 0
        loans = TblhrBankloan.objects.filter(
            empid=empid,
            compid=company_id,
            finyearid=fy_id
        )
        if loans.exists():
            loan_installment = loans.first().installment or 0

        # Mobile bill excess
        mobile_excess = 0
        mobile_bills = TblhrMobilebill.objects.filter(
            empid=empid,
            compid=company_id,
            finyearid=fy_id,
            billmonth=month
        )
        if mobile_bills.exists():
            bill = mobile_bills.first()
            from ..models import TblhrOfficestaff
            employee = TblhrOfficestaff.objects.filter(empid=empid).first()
            if employee and employee.mobileno:
                limit = LoanService.get_employee_mobile_limit(employee.mobileno)
                mobile_excess = LoanService.calculate_mobile_excess(
                    bill.billamt or 0,
                    limit
                )

        return {
            'loan_installment': loan_installment,
            'mobile_excess': mobile_excess,
            'total': loan_installment + mobile_excess
        }

    @staticmethod
    def validate_loan_application(empid, loan_amount, company_id, fy_id, max_loan_limit=None):
        """
        Validate loan application against business rules
        """
        # Check existing loans
        existing_total = LoanService.get_total_loan_amount(empid, company_id, fy_id)

        # Apply max loan limit if specified
        if max_loan_limit and (existing_total + loan_amount) > max_loan_limit:
            return False, f"Total loan amount exceeds limit of {max_loan_limit}"

        return True, "Loan application valid"
