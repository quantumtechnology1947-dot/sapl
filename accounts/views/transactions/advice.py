"""
Advice Payment/Receipt Views
Converted from ASP.NET Module/Accounts/Transactions/Advice.aspx
"""

from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.db import transaction
from datetime import datetime

from core.mixins import CompanyFinancialYearMixin, HTMXResponseMixin, AuditMixin
from ...models import (
    TblaccAdvicePaymentMaster,
    TblaccAdvicePaymentDetails,
    TblaccAdvicePaymentTemp,
    TblaccBank,
)
from ...services import AdviceService
from material_management.models import TblmmSupplierMaster
from sales_distribution.models import SdCustMaster
from human_resource.models import TblhrOfficestaff


class AdviceView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Main Advice page with tabs for Payment and Receipt.

    Payment tab has 4 sub-tabs:
    - Advance: Payments against Proforma Invoices
    - Creditors: Payments against Bill Bookings
    - Salary: Employee salary payments
    - Others: Miscellaneous payments

    Receipt tab: Record money received (ADR - Advice Debit Receipt)
    """
    template_name = 'accounts/transactions/advice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get company and financial year from session
        company_id = self.request.session.get('compid', 1)
        financial_year_id = self.request.session.get('finyearid', 1)
        session_id = str(self.request.user.id)

        # Determine active tab from query parameter (default to payment)
        active_tab = self.request.GET.get('tab', 'payment')

        # Determine active sub-tab (default to advance)
        active_subtab = self.request.GET.get('subtab', 'advance')

        # Get banks for dropdown
        banks = TblaccBank.objects.all()

        # Get temp data for current session
        temp_advance = TblaccAdvicePaymentTemp.objects.filter(
            compid=company_id,
            sessionid=session_id,
            types=1  # Advance type
        )

        temp_creditors_raw = TblaccAdvicePaymentTemp.objects.filter(
            compid=company_id,
            sessionid=session_id,
            types=2  # Creditors type
        )
        # Enrich creditors with bill amounts
        from accounts.models import TblaccBillbookingMaster, TblaccBillbookingDetails, TblaccAdvicePaymentDetails
        from django.db.models import Sum
        temp_creditors = []
        for item in temp_creditors_raw:
            if item.pvevno:
                try:
                    bill = TblaccBillbookingMaster.objects.get(id=item.pvevno)
                    bill_details = TblaccBillbookingDetails.objects.filter(mid=bill.id)
                    actual_amt = sum([(d.valuewithduty or 0) for d in bill_details]) + (bill.othercharges or 0) + (bill.debitamt or 0)
                    paid_amt = TblaccAdvicePaymentDetails.objects.filter(pvevno=bill.id).aggregate(total=Sum('amount'))['total'] or 0
                    bal_amt = actual_amt - paid_amt
                    temp_creditors.append({
                        'item': item,
                        'actual_amt': actual_amt,
                        'paid_amt': paid_amt,
                        'bal_amt': bal_amt
                    })
                except:
                    pass

        temp_salary = TblaccAdvicePaymentTemp.objects.filter(
            compid=company_id,
            sessionid=session_id,
            types=3  # Salary type
        )

        temp_others = TblaccAdvicePaymentTemp.objects.filter(
            compid=company_id,
            sessionid=session_id,
            types=4  # Others type
        )

        context.update({
            'active_tab': active_tab,
            'active_subtab': active_subtab,
            'banks': banks,
            'temp_advance': temp_advance,
            'temp_creditors': temp_creditors,
            'temp_salary': temp_salary,
            'temp_others': temp_others,
        })

        return context

from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ...services import AdviceService


@method_decorator(login_required, name='dispatch')
class AdviceAutocompleteView(View):
    """Autocomplete for Employee/Customer/Supplier selection."""
    
    def get(self, request):
        search_term = request.GET.get('q', '')
        option_type = request.GET.get('type', '1')
        company_id = request.session.get('compid', 1)
        format_type = request.GET.get('format', 'json')  # json or html
        
        results = AdviceService.get_autocomplete_options(
            search_term, option_type, company_id
        )
        
        # Return HTML options for datalist if requested
        if format_type == 'html':
            html = ''.join([f'<option value="{r["text"]}">' for r in results])
            return HttpResponse(html)
        
        return JsonResponse({'results': results})


@method_decorator(login_required, name='dispatch')
class AdviceInsertTempView(View):
    """Insert item into temp table."""
    
    def post(self, request):
        company_id = request.session.get('compid', 1)
        session_id = str(request.user.id)
        
        data = {
            'proforma_inv_no': request.POST.get('proforma_inv_no'),
            'date': request.POST.get('date'),
            'po_no': request.POST.get('po_no'),
            'amount': request.POST.get('amount'),
            'particulars': request.POST.get('particulars', '')
        }
        
        success = AdviceService.insert_advance_temp(data, session_id, company_id)
        
        if success:
            # Return updated grid HTML
            temp_items = AdviceService.get_advance_temp_items(session_id, company_id)
            return render(request, 'accounts/transactions/partials/advice_advance_grid.html', {
                'temp_advance': temp_items
            })
        else:
            return JsonResponse({'error': 'Failed to insert item'}, status=400)


@method_decorator(login_required, name='dispatch')
class AdviceDeleteTempView(View):
    """Delete item from temp table."""
    
    def post(self, request, temp_id):
        company_id = request.session.get('compid', 1)
        session_id = str(request.user.id)
        
        success = AdviceService.delete_advance_temp(temp_id)
        
        if success:
            # Return updated grid HTML
            temp_items = AdviceService.get_advance_temp_items(session_id, company_id)
            return render(request, 'accounts/transactions/partials/advice_advance_grid.html', {
                'temp_advance': temp_items
            })
        else:
            return JsonResponse({'error': 'Failed to delete item'}, status=400)


@method_decorator(login_required, name='dispatch')
class AdviceProceedView(View):
    """Save Advance payment to master and details tables."""
    
    def post(self, request):
        company_id = request.session.get('compid', 1)
        financial_year_id = request.session.get('finyearid', 1)
        session_id = str(request.user.id)
        
        # Validate form data
        form_data = {
            'pay_to_type': request.POST.get('pay_to_type'),
            'pay_to_name': request.POST.get('pay_to_name'),
            'cheque_no': request.POST.get('cheque_no'),
            'cheque_date': request.POST.get('cheque_date'),
            'bank_id': request.POST.get('bank_id'),
            'payable_at': request.POST.get('payable_at')
        }
        
        # Get temp items
        temp_items = AdviceService.get_advance_temp_items(session_id, company_id)
        
        if not temp_items.exists():
            return JsonResponse({'error': 'No items to save. Please add at least one item.'}, status=400)
        
        # Save to database
        success, result = AdviceService.save_advance_payment(
            form_data, temp_items, request.user, company_id, financial_year_id
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Advice {result} saved successfully!',
                'advice_number': result
            })
        else:
            return JsonResponse({'error': f'Failed to save: {result}'}, status=400)


# ===== CREDITORS SUB-TAB VIEWS =====

@method_decorator(login_required, name='dispatch')
class AdviceSearchBillsView(View):
    """Search bill bookings for supplier (Creditors sub-tab)."""

    def get(self, request):
        # Handle GET request for testing
        return JsonResponse({'message': 'Use POST to search bills'})

    def post(self, request):
        company_id = request.session.get('compid', 1)
        financial_year_id = request.session.get('finyearid', 1)

        supplier_name = request.POST.get('supplier_name', '').strip()

        if not supplier_name:
            # Return empty results HTML
            return render(request, 'accounts/transactions/partials/advice_creditors_search_results.html', {
                'bills': [],
                'supplier_name': '',
                'message': 'Please enter a supplier name'
            })

        # Search for supplier - try to extract code from name if in format "Name [CODE]"
        supplier_code = None
        if '[' in supplier_name and ']' in supplier_name:
            # Extract code from "Supplier Name [CODE]" format
            supplier_code = supplier_name.split('[')[1].split(']')[0].strip()
        
        # Search bill bookings using supplier name or code
        bills = AdviceService.search_bill_bookings(
            supplier_name, company_id, financial_year_id
        )

        # Return search results partial
        return render(request, 'accounts/transactions/partials/advice_creditors_search_results.html', {
            'bills': bills,
            'supplier_name': supplier_name,
            'message': f'Found {len(bills)} pending bills' if bills else 'No pending bills found for this supplier'
        })


@method_decorator(login_required, name='dispatch')
class AdviceAddBillToTempView(View):
    """Add selected bills to creditor temp table."""

    def post(self, request):
        company_id = request.session.get('compid', 1)
        session_id = str(request.user.id)

        # Get selected bills (multiple checkboxes)
        selected_bills = []
        for key, value in request.POST.items():
            if key.startswith('bill_'):
                bill_id = int(key.split('_')[1])
                amount = float(request.POST.get(f'amount_{bill_id}', 0))
                narration = request.POST.get(f'narration_{bill_id}', '')
                selected_bills.append({
                    'bill_id': bill_id,
                    'amount': amount,
                    'narration': narration
                })

        if not selected_bills:
            return JsonResponse({'error': 'No bills selected'}, status=400)

        # Add to temp
        success = AdviceService.add_creditor_to_temp(
            selected_bills, session_id, company_id
        )

        if success:
            # Return updated temp grid with enriched data
            temp_items = AdviceService.get_creditor_temp_items(session_id, company_id)
            # Enrich with bill amounts
            from accounts.models import TblaccBillbookingMaster, TblaccBillbookingDetails, TblaccAdvicePaymentDetails
            from django.db.models import Sum
            enriched_items = []
            for item in temp_items:
                bill_id = item.pvevno
                bill = TblaccBillbookingMaster.objects.get(id=bill_id)
                bill_details = TblaccBillbookingDetails.objects.filter(mid=bill.id)
                actual_amt = sum([(d.valuewithduty or 0) for d in bill_details]) + (bill.othercharges or 0) + (bill.debitamt or 0)
                paid_amt = TblaccAdvicePaymentDetails.objects.filter(pvevno=bill.id).aggregate(total=Sum('amount'))['total'] or 0
                bal_amt = actual_amt - paid_amt
                enriched_items.append({
                    'item': item,
                    'actual_amt': actual_amt,
                    'paid_amt': paid_amt,
                    'bal_amt': bal_amt
                })
            return render(request, 'accounts/transactions/partials/advice_creditors_temp_grid.html', {
                'temp_creditors': enriched_items
            })
        else:
            return JsonResponse({'error': 'Failed to add bills'}, status=400)


@method_decorator(login_required, name='dispatch')
class AdviceDeleteCreditorTempView(View):
    """Delete item from creditor temp table."""

    def post(self, request, temp_id):
        company_id = request.session.get('compid', 1)
        session_id = str(request.user.id)

        success = AdviceService.delete_creditor_temp(temp_id)

        if success:
            # Return updated grid with enriched data
            temp_items = AdviceService.get_creditor_temp_items(session_id, company_id)
            # Enrich with bill amounts
            from accounts.models import TblaccBillbookingMaster, TblaccBillbookingDetails, TblaccAdvicePaymentDetails
            from django.db.models import Sum
            enriched_items = []
            for item in temp_items:
                bill_id = item.pvevno
                bill = TblaccBillbookingMaster.objects.get(id=bill_id)
                bill_details = TblaccBillbookingDetails.objects.filter(mid=bill.id)
                actual_amt = sum([(d.valuewithduty or 0) for d in bill_details]) + (bill.othercharges or 0) + (bill.debitamt or 0)
                paid_amt = TblaccAdvicePaymentDetails.objects.filter(pvevno=bill.id).aggregate(total=Sum('amount'))['total'] or 0
                bal_amt = actual_amt - paid_amt
                enriched_items.append({
                    'item': item,
                    'actual_amt': actual_amt,
                    'paid_amt': paid_amt,
                    'bal_amt': bal_amt
                })
            return render(request, 'accounts/transactions/partials/advice_creditors_temp_grid.html', {
                'temp_creditors': enriched_items
            })
        else:
            return JsonResponse({'error': 'Failed to delete item'}, status=400)


@method_decorator(login_required, name='dispatch')
class AdviceProceedCreditorView(View):
    """Save creditor payment to master and details tables."""

    def post(self, request):
        company_id = request.session.get('compid', 1)
        financial_year_id = request.session.get('finyearid', 1)
        session_id = str(request.user.id)

        # Validate form data
        form_data = {
            'pay_to_name': request.POST.get('supplier_name'),
            'cheque_no': request.POST.get('cheque_no'),
            'cheque_date': request.POST.get('cheque_date'),
            'bank_id': request.POST.get('bank_id'),
            'payable_at': request.POST.get('payable_at')
        }

        # Get temp items
        temp_items = AdviceService.get_creditor_temp_items(session_id, company_id)

        if not temp_items.exists():
            return JsonResponse({'error': 'No items to save. Please add bills first.'}, status=400)

        # Save to database
        success, result = AdviceService.save_creditor_payment(
            form_data, temp_items, request.user, company_id, financial_year_id
        )

        if success:
            return JsonResponse({
                'success': True,
                'message': f'Creditor payment {result} saved successfully!',
                'advice_number': result
            })
        else:
            return JsonResponse({'error': f'Failed to save: {result}'}, status=400)


# ============================================================================
# SALARY SUB-TAB VIEWS
# ============================================================================

@method_decorator(login_required, name='dispatch')
class AdviceSalaryInsertTempView(View):
    """Insert salary item into temp table."""

    def post(self, request):
        try:
            company_id = request.session.get('compid', 1)
            session_id = str(request.user.id)

            # Get form data
            employee_name = request.POST.get('employee_salary', '').strip()
            amount = request.POST.get('amount_salary', '0')
            particulars = request.POST.get('particulars_salary', '').strip()

            # Validate
            if not employee_name or not amount or float(amount) <= 0:
                return render(request, 'accounts/transactions/partials/advice_salary_grid.html', {
                    'temp_salary': [],
                    'message': 'Please fill all required fields'
                })

            # Insert into temp
            data = {
                'empname': employee_name,
                'amt': float(amount),
                'particulars': particulars
            }
            
            success = AdviceService.insert_salary_temp(data, session_id, company_id)

            # Return updated grid
            temp_items = AdviceService.get_salary_temp_items(session_id, company_id)
            return render(request, 'accounts/transactions/partials/advice_salary_grid.html', {
                'temp_salary': temp_items
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return render(request, 'accounts/transactions/partials/advice_salary_grid.html', {
                'temp_salary': [],
                'message': f'Error: {str(e)}'
            })


@method_decorator(login_required, name='dispatch')
class AdviceSalaryDeleteTempView(View):
    """Delete salary item from temp table."""

    def post(self, request, temp_id):
        company_id = request.session.get('compid', 1)
        session_id = str(request.user.id)

        success = AdviceService.delete_salary_temp(temp_id)

        # Return updated grid
        temp_items = AdviceService.get_salary_temp_items(session_id, company_id)
        return render(request, 'accounts/transactions/partials/advice_salary_grid.html', {
            'temp_salary': temp_items
        })


@method_decorator(login_required, name='dispatch')
class AdviceSalaryProceedView(View):
    """Save salary payment to master and details tables."""

    def post(self, request):
        company_id = request.session.get('compid', 1)
        financial_year_id = request.session.get('finyearid', 1)
        session_id = str(request.user.id)

        # Get form data
        form_data = {
            'pay_to_name': request.POST.get('pay_to_salary'),
            'cheque_no': request.POST.get('cheque_no_salary'),
            'cheque_date': request.POST.get('cheque_date_salary'),
            'bank_id': request.POST.get('bank_id_salary'),
            'payable_at': request.POST.get('payable_at_salary')
        }

        # Get temp items
        temp_items = AdviceService.get_salary_temp_items(session_id, company_id)

        if not temp_items.exists():
            return JsonResponse({'error': 'No items to save. Please add salary entries first.'}, status=400)

        # Save to database
        success, result = AdviceService.save_salary_payment(
            form_data, temp_items, request.user, company_id, financial_year_id
        )

        if success:
            return JsonResponse({
                'success': True,
                'message': f'Salary payment {result} saved successfully!',
                'advice_number': result
            })
        else:
            return JsonResponse({'error': f'Failed to save: {result}'}, status=400)


# ============================================================================
# OTHERS SUB-TAB VIEWS
# ============================================================================

@method_decorator(login_required, name='dispatch')
class AdviceOthersInsertTempView(View):
    """Insert others item into temp table."""

    def post(self, request):
        company_id = request.session.get('compid', 1)
        session_id = str(request.user.id)

        # Get form data
        particulars = request.POST.get('particulars_others', '').strip()
        amount = request.POST.get('amount_others', '0')

        # Validate
        if not particulars or not amount or float(amount) <= 0:
            return render(request, 'accounts/transactions/partials/advice_others_grid.html', {
                'temp_others': [],
                'message': 'Please fill all required fields'
            })

        # Insert into temp
        data = {
            'particulars': particulars,
            'amt': float(amount)
        }
        
        success = AdviceService.insert_others_temp(data, session_id, company_id)

        # Return updated grid
        temp_items = AdviceService.get_others_temp_items(session_id, company_id)
        return render(request, 'accounts/transactions/partials/advice_others_grid.html', {
            'temp_others': temp_items
        })


@method_decorator(login_required, name='dispatch')
class AdviceOthersDeleteTempView(View):
    """Delete others item from temp table."""

    def post(self, request, temp_id):
        company_id = request.session.get('compid', 1)
        session_id = str(request.user.id)

        success = AdviceService.delete_others_temp(temp_id)

        # Return updated grid
        temp_items = AdviceService.get_others_temp_items(session_id, company_id)
        return render(request, 'accounts/transactions/partials/advice_others_grid.html', {
            'temp_others': temp_items
        })


@method_decorator(login_required, name='dispatch')
class AdviceOthersProceedView(View):
    """Save others payment to master and details tables."""

    def post(self, request):
        company_id = request.session.get('compid', 1)
        financial_year_id = request.session.get('finyearid', 1)
        session_id = str(request.user.id)

        # Get form data
        form_data = {
            'work_order': request.POST.get('work_order_others'),
            'business_group': request.POST.get('business_group_others'),
            'pay_to_name': request.POST.get('pay_to_others'),
            'cheque_no': request.POST.get('cheque_no_others'),
            'cheque_date': request.POST.get('cheque_date_others'),
            'bank_id': request.POST.get('bank_id_others'),
            'payable_at': request.POST.get('payable_at_others')
        }

        # Get temp items
        temp_items = AdviceService.get_others_temp_items(session_id, company_id)

        if not temp_items.exists():
            return JsonResponse({'error': 'No items to save. Please add payment details first.'}, status=400)

        # Save to database
        success, result = AdviceService.save_others_payment(
            form_data, temp_items, request.user, company_id, financial_year_id
        )

        if success:
            return JsonResponse({
                'success': True,
                'message': f'Others payment {result} saved successfully!',
                'advice_number': result
            })
        else:
            return JsonResponse({'error': f'Failed to save: {result}'}, status=400)
