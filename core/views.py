from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse_lazy


class CustomLoginView(auth_views.LoginView):
    """
    Custom login view with company context and enhanced authentication.
    Handles both ASP.NET and Django users through authentication backends.
    """
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Redirect to dashboard after successful login"""
        return reverse_lazy('core:dashboard')

    def form_valid(self, form):
        """Handle successful login"""
        response = super().form_valid(form)

        # Set session variables for company and financial year
        # FIXED: Set compid and finyearid in session for multi-company support
        self.request.session['compid'] = 1  # Default company ID (TODO: Get from user profile)

        # Get latest active financial year (highest finyearid with flag=1)
        from sys_admin.models import TblfinancialMaster
        active_fy = TblfinancialMaster.objects.filter(flag=1).order_by('-finyearid').first()
        if active_fy:
            self.request.session['finyearid'] = active_fy.finyearid
        else:
            # If no active FY, get the latest one
            latest_fy = TblfinancialMaster.objects.order_by('-finyearid').first()
            self.request.session['finyearid'] = latest_fy.finyearid if latest_fy else 1

        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return response

    def form_invalid(self, form):
        """Handle failed login"""
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


class CustomLogoutView(auth_views.LogoutView):
    """
    Custom logout view with audit logging and session cleanup.
    Accepts both GET and POST requests for convenience.
    """
    template_name = 'core/logged_out.html'  # Use custom template instead of admin template
    http_method_names = ['get', 'post', 'options']  # Allow GET requests

    def dispatch(self, request, *args, **kwargs):
        """Add logout message before processing"""
        if request.user.is_authenticated:
            messages.info(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard view for authenticated users.
    Shows overview statistics, recent activity, and quick actions.
    """
    template_name = 'core/dashboard.html'
    login_url = 'core:login'

    def get_context_data(self, **kwargs):
        """Add dashboard-specific context"""
        context = super().get_context_data(**kwargs)

        # Add any additional context data here
        # For example: statistics, recent activities, etc.
        context['page_title'] = 'Dashboard'

        # You can add more context here later:
        # context['total_orders'] = Order.objects.filter(company=self.request.company).count()
        # context['recent_activities'] = Activity.objects.recent()[:5]

        return context


# ============================================================================
# FINANCIAL YEAR CONTEXT SWITCHING VIEWS
# ============================================================================

from django.http import JsonResponse
from django.views import View
from core.context_manager import get_context_manager
from sys_admin.models import TblcompanyMaster, TblfinancialMaster


class CompanyListView(LoginRequiredMixin, View):
    """
    HTMX endpoint to list available companies for switching.
    Returns HTML fragment for dropdown.
    """
    
    def get(self, request):
        """Return list of active companies"""
        companies = TblcompanyMaster.objects.filter(flag=1).order_by('companyname')
        
        current_company_id = None
        if hasattr(request, 'financial_context') and request.financial_context:
            current_company_id = request.financial_context.company_id
        
        html = []
        for company in companies:
            is_active = company.compid == current_company_id
            active_class = 'bg-blue-50 text-blue-700' if is_active else 'hover:bg-gray-50'
            
            html.append(f'''
                <button
                    hx-post="{reverse_lazy('core:switch-company')}"
                    hx-vals='{{"company_id": {company.compid}}}'
                    hx-swap="none"
                    class="w-full text-left px-3 py-2 text-sm {active_class} rounded transition-colors"
                >
                    <div class="font-medium">{company.companyname}</div>
                    {f'<div class="text-xs text-blue-600">Current</div>' if is_active else ''}
                </button>
            ''')
        
        if not html:
            html.append('<div class="px-3 py-2 text-sm text-gray-500">No companies available</div>')
        
        from django.http import HttpResponse
        return HttpResponse(''.join(html))


class FinYearListView(LoginRequiredMixin, View):
    """
    HTMX endpoint to list available financial years for switching.
    Returns HTML fragment for dropdown.
    """
    
    def get(self, request):
        """Return list of financial years for current company"""
        company_id = request.GET.get('company_id')
        
        if not company_id:
            if hasattr(request, 'financial_context') and request.financial_context:
                company_id = request.financial_context.company_id
        
        if company_id:
            finyears = TblfinancialMaster.objects.filter(
                compid=company_id,
                flag=1
            ).order_by('-finyearfrom')
        else:
            finyears = TblfinancialMaster.objects.filter(flag=1).order_by('-finyearfrom')
        
        current_finyear_id = None
        if hasattr(request, 'financial_context') and request.financial_context:
            current_finyear_id = request.financial_context.finyear_id
        
        html = []
        for finyear in finyears:
            is_active = finyear.finyearid == current_finyear_id
            active_class = 'bg-blue-50 text-blue-700' if is_active else 'hover:bg-gray-50'
            
            html.append(f'''
                <button
                    hx-post="{reverse_lazy('core:switch-finyear')}"
                    hx-vals='{{"finyear_id": {finyear.finyearid}}}'
                    hx-swap="none"
                    class="w-full text-left px-3 py-2 text-sm {active_class} rounded transition-colors"
                >
                    <div class="font-medium">{finyear.finyear}</div>
                    <div class="text-xs text-gray-500">{finyear.finyearfrom} to {finyear.finyearto}</div>
                    {f'<div class="text-xs text-blue-600 mt-1">Current</div>' if is_active else ''}
                </button>
            ''')
        
        if not html:
            html.append('<div class="px-3 py-2 text-sm text-gray-500">No financial years available</div>')
        
        from django.http import HttpResponse
        return HttpResponse(''.join(html))


class SwitchCompanyView(LoginRequiredMixin, View):
    """
    Switch active company context.
    Auto-detects appropriate financial year for new company.
    """
    
    def post(self, request):
        """Handle company switch"""
        company_id = request.POST.get('company_id')
        
        if not company_id:
            return JsonResponse({
                'success': False,
                'error': 'Company ID required'
            }, status=400)
        
        try:
            company_id = int(company_id)
            
            # Validate company exists
            company = TblcompanyMaster.objects.filter(compid=company_id).first()
            if not company:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid company'
                }, status=400)
            
            # Get context manager
            context_manager = get_context_manager(request)
            
            # Auto-detect financial year for this company
            finyear = context_manager.get_current_financial_year(company_id)
            
            if not finyear:
                # No active FY, get most recent
                finyear = TblfinancialMaster.objects.filter(
                    compid=company_id
                ).order_by('-finyearid').first()
            
            if finyear:
                # Set new context
                context_manager.set_context(company_id, finyear.finyearid)
                
                messages.success(
                    request,
                    f'Switched to {company.companyname} - FY {finyear.finyear}'
                )
                
                # Return success with page reload
                from django.http import HttpResponse
                response = HttpResponse()
                response['HX-Refresh'] = 'true'  # Tell HTMX to reload page
                return response
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No financial year available for this company'
                }, status=400)
        
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid company ID format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class SwitchFinYearView(LoginRequiredMixin, View):
    """
    Switch active financial year context.
    Keeps current company.
    """
    
    def post(self, request):
        """Handle financial year switch"""
        finyear_id = request.POST.get('finyear_id')
        
        if not finyear_id:
            return JsonResponse({
                'success': False,
                'error': 'Financial Year ID required'
            }, status=400)
        
        try:
            finyear_id = int(finyear_id)
            
            # Get current company
            context_manager = get_context_manager(request)
            company_id = context_manager.company_id
            
            if not company_id:
                return JsonResponse({
                    'success': False,
                    'error': 'No company context set'
                }, status=400)
            
            # Validate financial year exists
            finyear = TblfinancialMaster.objects.filter(finyearid=finyear_id).first()
            if not finyear:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid financial year'
                }, status=400)
            
            # Set new context
            context_manager.set_context(company_id, finyear_id)
            
            messages.success(
                request,
                f'Switched to Financial Year {finyear.finyear}'
            )
            
            # Return success with page reload
            from django.http import HttpResponse
            response = HttpResponse()
            response['HX-Refresh'] = 'true'  # Tell HTMX to reload page
            return response
        
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid financial year ID format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class EmptyView(TemplateView):
    """
    Returns empty response for HTMX cancel operations.
    Used when users cancel form actions and want to clear the form area.
    """
    template_name = 'core/empty.html'

