"""
Salary Service
Business logic for salary calculations and bank statement generation
"""

from datetime import datetime
from ..models import (
    TblhrOfficestaff, TblhrOfferMaster, TblhrOfferAccessories,
    TblhrWorkingdays, TblhrBankloan, TblhrMobilebill,
    TblhrCoporatemobileno, TblhrSalaryDetails
)


class SalaryService:
    """
    Service class for salary-related business logic
    """

    @staticmethod
    def calculate_salary_components(employee):
        """
        Calculate salary components (Gross, CTC, Net) from offer accessories
        Returns: dict with gross_total, ctc_total, net_total
        """
        if not employee.offerid:
            return {'gross_total': 0, 'ctc_total': 0, 'net_total': 0}

        salary_components = TblhrOfferAccessories.objects.filter(mid=employee.offerid)

        gross_total = 0
        ctc_total = 0
        net_total = 0

        for component in salary_components:
            total = (component.qty or 0) * (component.amount or 0)
            if component.includesin == 1:  # Gross
                gross_total += total
            elif component.includesin == 2:  # CTC
                ctc_total += total
            elif component.includesin == 3:  # Net
                net_total += total

        return {
            'gross_total': gross_total,
            'ctc_total': ctc_total,
            'net_total': net_total,
            'components': salary_components
        }

    @staticmethod
    def get_bank_installment(empid, company_id, fy_id):
        """
        Get bank loan installment amount for employee
        """
        bank_loans = TblhrBankloan.objects.filter(
            empid=empid,
            compid=company_id,
            finyearid=fy_id
        )
        if bank_loans.exists():
            loan = bank_loans.first()
            return loan.installment or 0
        return 0

    @staticmethod
    def get_mobile_excess(empid, mobile_no, month, company_id, fy_id):
        """
        Calculate mobile bill excess amount
        """
        mobile_bills = TblhrMobilebill.objects.filter(
            empid=empid,
            compid=company_id,
            finyearid=fy_id,
            billmonth=month
        ).first()

        if not mobile_bills:
            return 0

        mobile_limit = TblhrCoporatemobileno.objects.filter(mobileno=mobile_no).first()
        if not mobile_limit:
            return 0

        excess = (mobile_bills.billamt or 0) - (mobile_limit.limitamt or 0)
        return max(excess, 0)

    @staticmethod
    def get_working_days(company_id, fy_id, month):
        """
        Get working days for a specific month
        """
        working_days = TblhrWorkingdays.objects.filter(
            compid=company_id,
            finyearid=fy_id,
            monthid=month
        ).first()
        return working_days.days if working_days else 0

    @staticmethod
    def calculate_net_salary(net_total, salary_detail):
        """
        Calculate final net salary after overtime, additions, and deductions
        """
        overtime_amount = (salary_detail.overtimehrs or 0) * (salary_detail.overtimerate or 0)
        total_deductions = (
            (salary_detail.installment or 0) +
            (salary_detail.mobileexeamt or 0) +
            (salary_detail.deduction or 0)
        )
        net_salary = net_total + overtime_amount + (salary_detail.addition or 0) - total_deductions

        return {
            'overtime_amount': overtime_amount,
            'total_deductions': total_deductions,
            'net_salary': net_salary
        }

    @staticmethod
    def generate_bank_statement_data(month, company_id, fy_id):
        """
        Generate bank statement data for salary transfers
        Returns list of employee salary transfer records
        """
        from ..models import TblhrSalaryMaster

        salaries = TblhrSalaryMaster.objects.filter(
            fmonth=month,
            compid=company_id,
            finyearid=fy_id
        )

        employee_list = []
        for salary in salaries:
            try:
                employee = TblhrOfficestaff.objects.get(empid=salary.empid)
                salary_detail = TblhrSalaryDetails.objects.get(mid=salary)

                # Calculate net pay
                components = SalaryService.calculate_salary_components(employee)
                net_calc = SalaryService.calculate_net_salary(
                    components['net_total'],
                    salary_detail
                )

                employee_list.append({
                    'employee': employee,
                    'net_pay': net_calc['net_salary'],
                    'salary_id': salary.id
                })
            except (TblhrOfficestaff.DoesNotExist, TblhrSalaryDetails.DoesNotExist):
                pass

        return employee_list

    @staticmethod
    def get_month_name(month_num):
        """
        Convert month number to name
        """
        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        return months.get(month_num, '')
