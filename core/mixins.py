"""
Core Mixins for Django Views

Reusable mixins to eliminate code duplication across all Django apps.
Requirements: 4.1, 4.2, 3.1, 3.2
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class CompanyFinancialYearMixin:
    """
    Mixin to add company and financial year context to views.
    
    Automatically filters querysets by company and financial year from session.
    Requirements: 4.1, 4.2
    """
    
    def get_compid(self):
        """Get company ID from session"""
        return self.request.session.get('compid', 1)
    
    def get_finyearid(self):
        """Get financial year ID from session"""
        # If not in session, get the latest financial year
        finyearid = self.request.session.get('finyearid')
        if not finyearid:
            # Try to get the latest financial year from database
            try:
                from sys_admin.models import TblfinancialMaster
                latest_fy = TblfinancialMaster.objects.filter(
                    compid=self.get_compid()
                ).order_by('-finyearid').first()
                if latest_fy:
                    finyearid = latest_fy.finyearid
                    # Set it in session for future requests
                    self.request.session['finyearid'] = finyearid
                else:
                    finyearid = 1
            except:
                finyearid = 1
        return finyearid
    
    def get_sessionid(self):
        """Get session ID"""
        return self.request.session.session_key or str(self.request.user.id)

    def get_employee_id(self):
        """Get employee ID for the logged-in user"""
        # First, try to get from session if already stored
        if hasattr(self.request, 'session') and 'employee_id' in self.request.session:
            return self.request.session['employee_id']

        # Try to get from HR table using username
        if self.request.user.is_authenticated:
            try:
                from human_resource.models import TblhrOfficestaff
                # Try looking up by username (which is typically the employee ID)
                employee = TblhrOfficestaff.objects.filter(
                    empid__iexact=self.request.user.username
                ).first()

                if employee:
                    return employee.empid

                # Fallback: try looking up by user ID in sessionid field
                employee = TblhrOfficestaff.objects.filter(
                    userid=self.request.user.id
                ).first()

                if employee:
                    return employee.empid
            except Exception as e:
                pass

        # Final fallback: use username or user ID
        return self.request.user.username if self.request.user.is_authenticated else str(self.request.user.id)

    def get_queryset(self):
        """Filter queryset by company only (financial year filter removed)"""
        queryset = super().get_queryset()
        
        # Only filter by company - show all financial years
        model = queryset.model
        if hasattr(model, 'compid'):
            queryset = queryset.filter(compid=self.get_compid())
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add company and financial year to context"""
        context = super().get_context_data(**kwargs)
        context['compid'] = self.get_compid()
        context['finyearid'] = self.get_finyearid()
        return context


class HTMXResponseMixin:
    """
    Mixin for HTMX partial template responses.
    
    Automatically returns partial templates for HTMX requests.
    Requirements: 3.1, 10.3, 12.3
    """
    
    partial_template_name = None
    
    def get_template_names(self):
        """Return partial template for HTMX requests"""
        if self.request.headers.get('HX-Request') and self.partial_template_name:
            return [self.partial_template_name]
        return super().get_template_names()
    
    def delete(self, request, *args, **kwargs):
        """Handle DELETE with HTMX support"""
        response = super().delete(request, *args, **kwargs)
        
        # Return 204 No Content for HTMX to remove element
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        
        return response


class SearchMixin:
    """
    Mixin for common search functionality.
    
    Adds search capability to list views.
    Requirements: 3.1, 3.2
    """
    
    search_fields = []  # List of fields to search
    search_param = 'search'
    
    def get_queryset(self):
        """Filter queryset by search query"""
        queryset = super().get_queryset()
        
        search_query = self.request.GET.get(self.search_param, '').strip()
        
        if search_query and self.search_fields:
            from django.db.models import Q
            
            # Build Q objects for each search field
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f'{field}__icontains': search_query})
            
            queryset = queryset.filter(q_objects)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add search query to context"""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get(self.search_param, '')
        return context


class ExportMixin:
    """
    Mixin for data export features.
    
    Adds CSV/Excel export capability to list views.
    Requirements: 4.1
    """
    
    export_fields = []  # List of fields to export
    export_filename = 'export'
    
    def export_csv(self, queryset):
        """Export queryset to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.export_filename}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        if self.export_fields:
            writer.writerow(self.export_fields)
        
        # Write data
        for obj in queryset:
            row = [getattr(obj, field, '') for field in self.export_fields]
            writer.writerow(row)
        
        return response
    
    def get(self, request, *args, **kwargs):
        """Handle export requests"""
        if request.GET.get('export') == 'csv':
            queryset = self.get_queryset()
            return self.export_csv(queryset)
        
        return super().get(request, *args, **kwargs)


class SuccessMessageMixin:
    """
    Mixin to add success messages to form views.
    
    Automatically shows success message after form submission.
    Requirements: 3.2
    """
    
    success_message = ''
    
    def get_success_message(self, cleaned_data):
        """Get success message"""
        return self.success_message % cleaned_data if self.success_message else ''
    
    def form_valid(self, form):
        """Add success message"""
        response = super().form_valid(form)
        
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        
        return response


class QueryOptimizationMixin:
    """
    Mixin for automatic query optimization.
    
    Adds select_related and prefetch_related to querysets.
    Requirements: 3.4, 5.5
    """
    
    select_related_fields = []  # Foreign key fields
    prefetch_related_fields = []  # Many-to-many fields
    
    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related"""
        queryset = super().get_queryset()
        
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        
        return queryset


class AuditMixin:
    """
    Mixin to automatically set audit fields.
    
    Sets sessionid, sysdate, systime on form save.
    Requirements: 4.1
    """
    
    def form_valid(self, form):
        """Set audit fields before saving"""
        from datetime import datetime
        
        # Set audit fields if they exist
        if hasattr(form.instance, 'sessionid'):
            form.instance.sessionid = self.request.session.session_key or str(self.request.user.id)
        
        if hasattr(form.instance, 'sysdate'):
            form.instance.sysdate = datetime.now().strftime('%Y-%m-%d')
        
        if hasattr(form.instance, 'systime'):
            form.instance.systime = datetime.now().strftime('%H:%M:%S')
        
        return super().form_valid(form)


# Commonly used mixin combinations
class BaseListViewMixin(LoginRequiredMixin, CompanyFinancialYearMixin, 
                       HTMXResponseMixin, SearchMixin, QueryOptimizationMixin):
    """
    Base mixin for list views.
    
    Combines authentication, company/year filtering, HTMX support, 
    search, and query optimization.
    """
    pass


class BaseCreateViewMixin(LoginRequiredMixin, CompanyFinancialYearMixin,
                         HTMXResponseMixin, SuccessMessageMixin, AuditMixin):
    """
    Base mixin for create views.
    
    Combines authentication, company/year context, HTMX support,
    success messages, and audit fields.
    """
    pass


class BaseUpdateViewMixin(LoginRequiredMixin, CompanyFinancialYearMixin,
                         HTMXResponseMixin, SuccessMessageMixin, AuditMixin):
    """
    Base mixin for update views.
    
    Combines authentication, company/year filtering, HTMX support,
    success messages, and audit fields.
    """
    pass


class BaseDeleteViewMixin(LoginRequiredMixin, CompanyFinancialYearMixin,
                         HTMXResponseMixin):
    """
    Base mixin for delete views.
    
    Combines authentication, company/year filtering, and HTMX support.
    """
    pass


class BaseDetailViewMixin(LoginRequiredMixin, CompanyFinancialYearMixin,
                         QueryOptimizationMixin):
    """
    Base mixin for detail views.
    
    Combines authentication, company/year filtering, and query optimization.
    """
    pass


# ============================================================================
# UNIFIED CRUD VIEW
# ============================================================================

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy


class BaseCRUDView(LoginRequiredMixin, CompanyFinancialYearMixin, 
                   HTMXResponseMixin, SearchMixin, QueryOptimizationMixin,
                   SuccessMessageMixin, AuditMixin, View):
    """
    Unified CRUD view that handles List, Create, Update, Delete in one class.
    
    This eliminates the need for separate ListView, CreateView, UpdateView, DeleteView.
    
    Usage:
        class CountryCRUDView(BaseCRUDView):
            model = Tblcountry
            form_class = CountryForm
            template_name = 'sys_admin/country_list.html'
            success_url = reverse_lazy('sys_admin:country-list')
    
    URLs:
        path('countries/', CountryCRUDView.as_view(), name='country-list'),  # GET: list
        path('countries/create/', CountryCRUDView.as_view(), name='country-create'),  # GET/POST: create
        path('countries/<int:pk>/', CountryCRUDView.as_view(), name='country-detail'),  # GET: detail
        path('countries/<int:pk>/edit/', CountryCRUDView.as_view(), name='country-edit'),  # GET/POST: update
        path('countries/<int:pk>/delete/', CountryCRUDView.as_view(), name='country-delete'),  # POST/DELETE: delete
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 5.1, 5.2
    """
    
    # Model and form configuration
    model = None
    form_class = None
    
    # Template names
    template_name = None  # List template
    partial_template_name = None  # HTMX partial for list
    form_template_name = None  # Form template (create/edit)
    detail_template_name = None  # Detail template
    row_template_name = None  # Single row template for HTMX
    
    # URL configuration
    success_url = None
    
    # List view configuration
    paginate_by = 20
    context_object_name = 'objects'
    ordering = None
    
    # Success messages
    create_success_message = 'Created successfully'
    update_success_message = 'Updated successfully'
    delete_success_message = 'Deleted successfully'
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests - List, Detail, or Edit form"""
        pk = kwargs.get('pk')
        action = kwargs.get('action')
        
        if pk and action == 'edit':
            # Show edit form
            return self.edit(request, pk)
        elif pk:
            # Show detail or return row HTML
            return self.detail(request, pk)
        else:
            # Show list
            return self.list(request)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests - Create, Update, or Delete"""
        pk = kwargs.get('pk')
        action = kwargs.get('action')
        
        if pk and action == 'delete':
            # Delete object
            return self.delete_object(request, pk)
        elif pk:
            # Update object
            return self.update(request, pk)
        else:
            # Create object
            return self.create(request)
    
    def delete(self, request, *args, **kwargs):
        """Handle DELETE requests"""
        pk = kwargs.get('pk')
        return self.delete_object(request, pk)
    
    # ========================================================================
    # LIST VIEW
    # ========================================================================
    
    def list(self, request):
        """Display paginated list of objects"""
        from django.core.paginator import Paginator
        
        queryset = self.get_queryset()
        
        if self.ordering:
            queryset = queryset.order_by(self.ordering)
        
        # Pagination
        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context = {
            self.context_object_name: page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        }
        context.update(self.get_context_data())
        
        # Return partial template for HTMX
        template = self.partial_template_name if request.headers.get('HX-Request') and self.partial_template_name else self.template_name
        
        return render(request, template, context)
    
    # ========================================================================
    # CREATE VIEW
    # ========================================================================
    
    def create(self, request):
        """Handle object creation"""
        form = self.form_class(request.POST or None)
        
        if request.method == 'POST' and form.is_valid():
            obj = form.save(commit=False)
            
            # Set audit fields
            self._set_audit_fields(obj)
            
            obj.save()
            
            messages.success(request, self.create_success_message)
            
            # Return row HTML for HTMX
            if request.headers.get('HX-Request') and self.row_template_name:
                return render(request, self.row_template_name, {self.model.__name__.lower(): obj})
            
            return redirect(self.success_url)
        
        # Show form
        template = self.form_template_name or self.template_name
        context = {'form': form, 'action': 'create'}
        context.update(self.get_context_data())
        
        return render(request, template, context)
    
    # ========================================================================
    # UPDATE VIEW
    # ========================================================================
    
    def edit(self, request, pk):
        """Show edit form"""
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        form = self.form_class(instance=obj)
        
        template = self.form_template_name or self.template_name
        context = {
            'form': form,
            'object': obj,
            self.model.__name__.lower(): obj,
            'action': 'edit'
        }
        context.update(self.get_context_data())
        
        return render(request, template, context)
    
    def update(self, request, pk):
        """Handle object update"""
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        form = self.form_class(request.POST, instance=obj)
        
        if form.is_valid():
            obj = form.save(commit=False)
            
            # Set audit fields
            self._set_audit_fields(obj)
            
            obj.save()
            
            messages.success(request, self.update_success_message)
            
            # Return row HTML for HTMX
            if request.headers.get('HX-Request') and self.row_template_name:
                return render(request, self.row_template_name, {self.model.__name__.lower(): obj})
            
            return redirect(self.success_url)
        
        # Show form with errors
        template = self.form_template_name or self.template_name
        context = {
            'form': form,
            'object': obj,
            self.model.__name__.lower(): obj,
            'action': 'edit'
        }
        context.update(self.get_context_data())
        
        return render(request, template, context)
    
    # ========================================================================
    # DELETE VIEW
    # ========================================================================
    
    def delete_object(self, request, pk):
        """Handle object deletion"""
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        obj.delete()
        
        messages.success(request, self.delete_success_message)
        
        # Return 204 for HTMX to remove element
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        
        return redirect(self.success_url)
    
    # ========================================================================
    # DETAIL VIEW
    # ========================================================================
    
    def detail(self, request, pk):
        """Display object detail or return row HTML"""
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Return row HTML for HTMX (cancel edit)
        if request.headers.get('HX-Request') and self.row_template_name:
            return render(request, self.row_template_name, {self.model.__name__.lower(): obj})
        
        # Show detail page
        template = self.detail_template_name or self.template_name
        context = {
            'object': obj,
            self.model.__name__.lower(): obj,
        }
        context.update(self.get_context_data())
        
        return render(request, template, context)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _set_audit_fields(self, obj):
        """Set audit fields on object"""
        from datetime import datetime
        
        if hasattr(obj, 'sessionid'):
            obj.sessionid = self.request.session.session_key or str(self.request.user.id)
        
        if hasattr(obj, 'sysdate'):
            obj.sysdate = datetime.now().strftime('%Y-%m-%d')
        
        if hasattr(obj, 'systime'):
            obj.systime = datetime.now().strftime('%H:%M:%S')
    
    def get_context_data(self, **kwargs):
        """Get additional context data"""
        context = {}
        
        # Add company and financial year
        if hasattr(self, 'get_compid'):
            context['compid'] = self.get_compid()
        
        if hasattr(self, 'get_finyearid'):
            context['finyearid'] = self.get_finyearid()
        
        # Add search query
        if hasattr(self, 'search_param'):
            context['search_query'] = self.request.GET.get(self.search_param, '')
        
        return context



# ============================================================================
# PAGINATION HELPER FUNCTION
# ============================================================================

def paginate_queryset(queryset, request, per_page=20):
    """
    Quick pagination helper for any queryset.
    Returns dict with page_obj, is_paginated, paginator for context.
    
    Usage in views:
        customers = SdCustMaster.objects.all()
        context = paginate_queryset(customers, request, per_page=20)
        return render(request, "template.html", context)
    """
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page", 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return {
        "page_obj": page_obj,
        "is_paginated": paginator.num_pages > 1,
        "paginator": paginator,
    }

