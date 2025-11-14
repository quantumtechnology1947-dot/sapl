"""
SysAdmin Financial Year Management Views
Handles Financial Year CRUD operations and year-end closing.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from datetime import datetime

from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
    LoginRequiredMixin
)

from ..models import TblfinancialMaster, TblcompanyMaster
from ..forms import FinancialYearForm, FinancialYearUpdateForm


# ============================================================================
# FINANCIAL YEAR MASTER
# ============================================================================

class FinancialYearListView(BaseListViewMixin, ListView):
    """
    Display paginated list of financial years with search.
    Uses BaseListViewMixin for auth, search, HTMX, and query optimization.
    """
    model = TblfinancialMaster
    template_name = 'sys_admin/financial_year_list.html'
    partial_template_name = 'sys_admin/partials/financial_year_list_partial.html'
    context_object_name = 'financial_years'
    paginate_by = 20

    def get_queryset(self):
        """Filter active financial years and apply search."""
        # Show all financial years (including inactive for debugging)
        # Change to filter(flag=1) to show only active ones
        queryset = TblfinancialMaster.objects.all()

        # Search by company name
        search = self.request.GET.get('search', '')
        if search:
            # Optimize: Use subquery instead of values_list for better performance
            company_ids = TblcompanyMaster.objects.filter(
                companyname__icontains=search
            ).values_list('compid', flat=True)
            queryset = queryset.filter(compid__in=company_ids)

        # Filter by company if specified
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(compid=company_id)

        # Filter by status (open/closed)
        status = self.request.GET.get('status')
        if status == 'open':
            queryset = queryset.filter(flag=1)
        elif status == 'closed':
            queryset = queryset.filter(flag=0)

        # Order by ID (most recent first) since finyearfrom might be string
        return queryset.order_by('-finyearid')

    def get_context_data(self, **kwargs):
        """Add company names and search query to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')

        # Optimize: Fetch companies only once and create map
        company_map = {
            c.compid: c.companyname
            for c in TblcompanyMaster.objects.filter(flag=1).only('compid', 'companyname')
        }

        # Attach company names to each financial year
        for fy in context['financial_years']:
            fy.company_name = company_map.get(fy.compid, 'Unknown Company')

        # Add companies for filter dropdown
        context['companies'] = TblcompanyMaster.objects.filter(flag=1).order_by('companyname')
        context['selected_company'] = self.request.GET.get('company')
        context['selected_status'] = self.request.GET.get('status')

        # Add total count for debugging
        context['total_count'] = TblfinancialMaster.objects.count()
        context['active_count'] = TblfinancialMaster.objects.filter(flag=1).count()

        return context


class FinancialYearCreateView(LoginRequiredMixin, CreateView):
    """
    Create new financial year (redirects to confirmation page).
    Converted from: aspnet/Module/SysAdmin/FinancialYear/FinYrs_New.aspx
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
    """
    model = TblfinancialMaster
    form_class = FinancialYearForm
    template_name = 'sys_admin/financial_year_form.html'

    def form_valid(self, form):
        """Store form data in session and redirect to confirmation page."""
        company = form.cleaned_data['company']

        # Store pending financial year data in session
        self.request.session['pending_financial_year'] = {
            'compid': company.compid,
            'company_name': company.companyname,
            'finyear': form.cleaned_data['finyear'],
            'finyearfrom': form.cleaned_data['finyearfrom'].strftime('%d-%m-%Y'),
            'finyearto': form.cleaned_data['finyearto'].strftime('%d-%m-%Y'),
        }

        # Redirect to confirmation page instead of saving
        return redirect('sys_admin:financial-year-confirm')

    def form_invalid(self, form):
        """Handle form validation errors."""
        return self.render_to_response(self.get_context_data(form=form))


class FinancialYearConfirmView(LoginRequiredMixin, TemplateView):
    """
    Confirmation page before creating financial year.
    Converted from: aspnet/Module/SysAdmin/FinancialYear/FinYear_New_Details.aspx
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 2.9
    """
    template_name = 'sys_admin/financial_year_confirm.html'

    def get_context_data(self, **kwargs):
        """Get pending financial year data from session."""
        context = super().get_context_data(**kwargs)
        context['pending_fy'] = self.request.session.get('pending_financial_year')

        if not context['pending_fy']:
            messages.error(self.request, 'No pending financial year found.')

        return context

    def post(self, request, *args, **kwargs):
        """Handle confirmation submission."""
        pending_fy_data = request.session.get('pending_financial_year')

        if not pending_fy_data:
            messages.error(request, 'No pending financial year found in session.')
            return redirect('sys_admin:financial-year-create')

        from ..services import YearEndClosingService

        try:
            with transaction.atomic():
                # Find the previous financial year to close it
                old_fy = TblfinancialMaster.objects.filter(
                    compid=pending_fy_data['compid'],
                    flag=1
                ).order_by('-finyearto').first()

                # Create the new financial year
                new_fy = TblfinancialMaster.objects.create(
                    compid=pending_fy_data['compid'],
                    finyear=pending_fy_data['finyear'],
                    finyearfrom=datetime.strptime(pending_fy_data['finyearfrom'], '%d-%m-%Y').strftime('%Y-%m-%d'),
                    finyearto=datetime.strptime(pending_fy_data['finyearto'], '%d-%m-%Y').strftime('%Y-%m-%d'),
                    sessionid=request.session.session_key or str(request.user.id),
                    sysdate=datetime.now().strftime('%Y-%m-%d'),
                    systime=datetime.now().strftime('%H:%M:%S'),
                    flag=1
                )

                if old_fy:
                    # Execute the year-end closing service
                    service = YearEndClosingService()
                    service.execute_year_end_closing(
                        old_year=old_fy,
                        new_year=new_fy,
                        session_id=request.session.session_key or str(request.user.id)
                    )

                # Clear session data
                del request.session['pending_financial_year']

                messages.success(request, f'Financial year {new_fy.finyear} created and year-end process completed successfully.')
                return redirect('sys_admin:financial-year-list')

        except Exception as e:
            messages.error(request, f'An error occurred during the year-end process: {str(e)}')
            return redirect('sys_admin:financial-year-create')


class FinancialYearUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update financial year dates (inline editing).
    Uses BaseUpdateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = TblfinancialMaster
    form_class = FinancialYearUpdateForm
    template_name = 'sys_admin/partials/financial_year_edit_row.html'
    success_url = reverse_lazy('sys_admin:financial-year-list')
    success_message = 'Financial year updated successfully'
    pk_url_kwarg = 'finyearid'

    def get(self, request, *args, **kwargs):
        """Return edit form row for HTMX."""
        self.object = self.get_object()
        form = self.get_form()

        # Get company name
        company = TblcompanyMaster.objects.filter(compid=self.object.compid).first()
        company_name = company.companyname if company else 'Unknown'

        return render(request, self.template_name, {
            'form': form,
            'financial_year': self.object,
            'company_name': company_name
        })

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)

        if self.request.headers.get('HX-Request'):
            # Return updated row for inline editing
            company = TblcompanyMaster.objects.filter(compid=self.object.compid).first()
            self.object.company_name = company.companyname if company else 'Unknown'

            return render(self.request, 'sys_admin/partials/financial_year_row.html', {
                'financial_year': self.object
            })

        messages.success(self.request, 'Financial year updated successfully.')
        return response

    def form_invalid(self, form):
        """Handle form validation errors."""
        if self.request.headers.get('HX-Request'):
            company = TblcompanyMaster.objects.filter(compid=self.object.compid).first()
            company_name = company.companyname if company else 'Unknown'

            return render(self.request, self.template_name, {
                'form': form,
                'financial_year': self.object,
                'company_name': company_name
            })
        return super().form_invalid(form)


class FinancialYearDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Soft delete financial year (set flag=0).
    Uses BaseDeleteViewMixin for auth and HTMX support.
    """
    model = TblfinancialMaster
    success_url = reverse_lazy('sys_admin:financial-year-list')
    pk_url_kwarg = 'finyearid'

    def delete(self, request, *args, **kwargs):
        """Perform soft delete by setting flag=0."""
        self.object = self.get_object()

        # Soft delete: set flag=0
        self.object.flag = 0
        self.object.save()

        messages.success(request, 'Financial year deleted successfully.')

        # BaseDeleteViewMixin handles HTMX 204 response
        return super().delete(request, *args, **kwargs)


class FinancialYearRowView(BaseDetailViewMixin, DetailView):
    """
    Return single financial year row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = TblfinancialMaster
    template_name = 'sys_admin/partials/financial_year_row.html'
    context_object_name = 'financial_year'
    pk_url_kwarg = 'finyearid'

    def get_context_data(self, **kwargs):
        """Add company name to context."""
        context = super().get_context_data(**kwargs)
        company = TblcompanyMaster.objects.filter(compid=self.object.compid).first()
        self.object.company_name = company.companyname if company else 'Unknown'
        return context


# ============================================================================
# FINANCIAL YEAR DETAILS AND MANAGEMENT (Legacy - kept for compatibility)
# ============================================================================

class FinancialYearDetailsView(LoginRequiredMixin, DetailView):
    """
    Display financial year details and execute year-end closing.
    Converted from: aspnet/Module/SysAdmin/FinancialYear/FinYear_New_Details.aspx
    Requirements: 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
    """
    model = TblfinancialMaster
    template_name = 'sys_admin/financial_year_details.html'
    context_object_name = 'financial_year'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Financial Year Details'

        # Get company details
        company = TblcompanyMaster.objects.filter(compid=self.object.compid).first()
        context['company'] = company

        # Get previous financial year
        previous_year = TblfinancialMaster.objects.filter(
            compid=self.object.compid,
            finyearfrom__lt=self.object.finyearfrom
        ).order_by('-finyearfrom').first()
        context['previous_year'] = previous_year

        return context

    def post(self, request, *args, **kwargs):
        """Execute year-end closing process."""
        self.object = self.get_object()

        try:
            # Get previous financial year
            previous_year = TblfinancialMaster.objects.filter(
                compid=self.object.compid,
                finyearfrom__lt=self.object.finyearfrom
            ).order_by('-finyearfrom').first()

            if previous_year:
                # Execute year-end closing
                from ..services import YearEndClosingService
                service = YearEndClosingService()
                result = service.execute_year_end_closing(
                    old_year=previous_year,
                    new_year=self.object
                )

                messages.success(
                    request,
                    f"Financial year {self.object.finyear} created successfully! "
                    f"Year-end closing completed: {result['cloned_items']} items cloned, "
                    f"{result['updated_balances']} balances updated, "
                    f"{result['access_records']} access records carried forward."
                )
            else:
                messages.success(
                    request,
                    f"Financial year {self.object.finyear} created successfully! "
                    f"(No previous year found for year-end closing)"
                )

            return redirect('sys_admin:financial_year_list')

        except Exception as e:
            messages.error(request, f"Error during year-end closing: {str(e)}")
            return self.render_to_response(self.get_context_data())
