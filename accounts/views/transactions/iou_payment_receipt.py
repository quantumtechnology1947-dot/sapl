"""
IOU Payment/Receipt Views
Converted from ASP.NET Module/Accounts/Transactions/IOU_PaymentReceipt.aspx
"""

from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from datetime import datetime

from core.mixins import CompanyFinancialYearMixin
from ...models import TblaccIouMaster, TblaccIouReasons
from human_resource.models import TblhrOfficestaff


def get_employee_lookup():
    """Helper function to get employee name lookup dictionary"""
    employees_dict = {}
    try:
        employees = TblhrOfficestaff.objects.all()
        employees_dict = {emp.empid: f"{emp.title or ''} {emp.employeename or ''}".strip() for emp in employees if emp.empid}
    except:
        pass
    return employees_dict


def get_reason_lookup():
    """Helper function to get reason lookup dictionary"""
    reasons_dict = {}
    try:
        reasons = TblaccIouReasons.objects.all()
        reasons_dict = {reason.id: reason.terms for reason in reasons}
    except:
        pass
    return reasons_dict


@method_decorator(login_required, name='dispatch')
class IOUPaymentReceiptView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Main IOU Payment/Receipt page with tabs for Payment and Receipt.
    Maps to: IOU_PaymentReceipt.aspx
    
    URL: /accounts/transactions/iou-payment-receipt/
    """
    template_name = 'accounts/transactions/iou_payment_receipt.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        company_id = self.request.session.get('compid', 1)
        financial_year_id = self.request.session.get('finyearid', 1)
        
        # Determine active tab from query params
        active_tab = self.request.GET.get('tab', 'payment')
        
        # Get lookup dictionaries
        reasons_dict = get_reason_lookup()
        employees_dict = get_employee_lookup()
        
        # Get Payment data (IOU payments made)
        payments = TblaccIouMaster.objects.filter(
            compid=company_id,
            finyearid__lte=financial_year_id
        ).order_by('-id')
        
        # Enrich with reason names and employee names
        payment_list = []
        for payment in payments:
            reason_name = reasons_dict.get(payment.reason, '') if payment.reason else ''
            emp_name = employees_dict.get(payment.empid, payment.empid or '')
            payment_dict = {
                'id': payment.id,
                'paymentdate': payment.paymentdate,
                'empid': payment.empid,
                'empname': emp_name,
                'amount': payment.amount,
                'narration': payment.narration,
                'authorize': payment.authorize,
                'reason_name': reason_name
            }
            payment_list.append(payment_dict)
        
        # Get Receipt data (same as payments, for receipt tracking)
        receipts = TblaccIouMaster.objects.filter(
            compid=company_id,
            finyearid__lte=financial_year_id
        ).order_by('-id')
        
        # Enrich with reason names and employee names
        receipt_list = []
        for receipt in receipts:
            reason_name = reasons_dict.get(receipt.reason, '') if receipt.reason else ''
            emp_name = employees_dict.get(receipt.empid, receipt.empid or '')
            receipt_dict = {
                'id': receipt.id,
                'paymentdate': receipt.paymentdate,
                'empid': receipt.empid,
                'empname': emp_name,
                'amount': receipt.amount,
                'narration': receipt.narration,
                'recivedamt': receipt.recieved,  # Using recieved field
                'receiptdate': receipt.paymentdate,  # Using paymentdate as receiptdate
                'reason_name': reason_name
            }
            receipt_list.append(receipt_dict)
        
        context.update({
            'active_tab': active_tab,
            'payments': payment_list,
            'receipts': receipt_list,
            'mod_id': 11,
            'sub_mod_id': 120,
        })
        
        return context


@method_decorator(login_required, name='dispatch')
class IOUPaymentDeleteView(View):
    """Delete IOU payment."""
    
    def post(self, request, payment_id):
        try:
            payment = TblaccIouMaster.objects.get(id=payment_id)
            
            # Check if authorized
            if payment.authorize:
                return JsonResponse({'error': 'Cannot delete authorized payment'}, status=400)
            
            payment.delete()
            
            # Return updated grid
            company_id = request.session.get('compid', 1)
            financial_year_id = request.session.get('finyearid', 1)
            
            # Get lookup dictionaries
            reasons_dict = get_reason_lookup()
            employees_dict = get_employee_lookup()
            
            payments = TblaccIouMaster.objects.filter(
                compid=company_id,
                finyearid__lte=financial_year_id
            ).order_by('-id')
            
            payment_list = []
            for payment in payments:
                reason_name = reasons_dict.get(payment.reason, '') if payment.reason else ''
                emp_name = employees_dict.get(payment.empid, payment.empid or '')
                payment_dict = {
                    'id': payment.id,
                    'paymentdate': payment.paymentdate,
                    'empid': payment.empid,
                    'empname': emp_name,
                    'amount': payment.amount,
                    'narration': payment.narration,
                    'authorize': payment.authorize,
                    'reason_name': reason_name
                }
                payment_list.append(payment_dict)
            
            return render(request, 'accounts/transactions/partials/iou_payment_grid.html', {
                'payments': payment_list
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(login_required, name='dispatch')
class IOUPaymentAuthorizeView(View):
    """Authorize IOU payment."""
    
    def post(self, request, payment_id):
        try:
            payment = TblaccIouMaster.objects.get(id=payment_id)
            payment.authorize = 1
            payment.authorizedby = request.user.username
            payment.authorizeddate = datetime.now().strftime('%d-%m-%Y')
            payment.authorizedtime = datetime.now().strftime('%H:%M:%S')
            payment.save()
            
            # Return updated grid
            company_id = request.session.get('compid', 1)
            financial_year_id = request.session.get('finyearid', 1)
            
            # Get lookup dictionaries
            reasons_dict = get_reason_lookup()
            employees_dict = get_employee_lookup()
            
            payments = TblaccIouMaster.objects.filter(
                compid=company_id,
                finyearid__lte=financial_year_id
            ).order_by('-id')
            
            payment_list = []
            for payment in payments:
                reason_name = reasons_dict.get(payment.reason, '') if payment.reason else ''
                emp_name = employees_dict.get(payment.empid, payment.empid or '')
                payment_dict = {
                    'id': payment.id,
                    'paymentdate': payment.paymentdate,
                    'empid': payment.empid,
                    'empname': emp_name,
                    'amount': payment.amount,
                    'narration': payment.narration,
                    'authorize': payment.authorize,
                    'reason_name': reason_name
                }
                payment_list.append(payment_dict)
            
            return render(request, 'accounts/transactions/partials/iou_payment_grid.html', {
                'payments': payment_list
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(login_required, name='dispatch')
class IOUReceiptDeleteView(View):
    """Delete IOU receipt."""
    
    def post(self, request, receipt_id):
        try:
            receipt = TblaccIouMaster.objects.get(id=receipt_id)
            receipt.delete()
            
            # Return updated grid
            company_id = request.session.get('compid', 1)
            financial_year_id = request.session.get('finyearid', 1)
            
            # Get lookup dictionaries
            reasons_dict = get_reason_lookup()
            employees_dict = get_employee_lookup()
            
            receipts = TblaccIouMaster.objects.filter(
                compid=company_id,
                finyearid__lte=financial_year_id
            ).order_by('-id')
            
            receipt_list = []
            for receipt in receipts:
                reason_name = reasons_dict.get(receipt.reason, '') if receipt.reason else ''
                emp_name = employees_dict.get(receipt.empid, receipt.empid or '')
                receipt_dict = {
                    'id': receipt.id,
                    'paymentdate': receipt.paymentdate,
                    'empid': receipt.empid,
                    'empname': emp_name,
                    'amount': receipt.amount,
                    'narration': receipt.narration,
                    'recivedamt': receipt.recieved,
                    'receiptdate': receipt.paymentdate,
                    'reason_name': reason_name
                }
                receipt_list.append(receipt_dict)
            
            return render(request, 'accounts/transactions/partials/iou_receipt_grid.html', {
                'receipts': receipt_list
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(login_required, name='dispatch')
class IOUReceiptAddView(View):
    """Add receipt amount to IOU."""
    
    def post(self, request, receipt_id):
        try:
            receipt = TblaccIouMaster.objects.get(id=receipt_id)
            
            # Get receipt amount from POST
            recivedamt = request.POST.get('recivedamt')
            
            if recivedamt:
                receipt.recieved = float(recivedamt)
            
            receipt.save()
            
            # Return updated grid
            company_id = request.session.get('compid', 1)
            financial_year_id = request.session.get('finyearid', 1)
            
            # Get lookup dictionaries
            reasons_dict = get_reason_lookup()
            employees_dict = get_employee_lookup()
            
            receipts = TblaccIouMaster.objects.filter(
                compid=company_id,
                finyearid__lte=financial_year_id
            ).order_by('-id')
            
            receipt_list = []
            for receipt in receipts:
                reason_name = reasons_dict.get(receipt.reason, '') if receipt.reason else ''
                emp_name = employees_dict.get(receipt.empid, receipt.empid or '')
                receipt_dict = {
                    'id': receipt.id,
                    'paymentdate': receipt.paymentdate,
                    'empid': receipt.empid,
                    'empname': emp_name,
                    'amount': receipt.amount,
                    'narration': receipt.narration,
                    'recivedamt': receipt.recieved,
                    'receiptdate': receipt.paymentdate,
                    'reason_name': reason_name
                }
                receipt_list.append(receipt_dict)
            
            return render(request, 'accounts/transactions/partials/iou_receipt_grid.html', {
                'receipts': receipt_list
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
