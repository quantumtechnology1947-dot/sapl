"""
Inventory Module Mixins
Reusable view mixins for common functionality
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages


class CompanyFinYearMixin:
    """Mixin to add company and financial year context"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compid'] = self.request.session.get('compid')
        context['finyearid'] = self.request.session.get('finyear')
        context['sessionid'] = self.request.session.get('username')
        return context
    
    def get_compid(self):
        """Get company ID from session"""
        return self.request.session.get('compid')
    
    def get_finyearid(self):
        """Get financial year ID from session"""
        return self.request.session.get('finyear')
    
    def get_sessionid(self):
        """Get session ID (username) from session"""
        return self.request.session.get('username')


class SessionTrackingMixin:
    """Mixin to track user session in transactions"""
    
    def form_valid(self, form):
        """Add session tracking to form save"""
        if hasattr(form, 'compid'):
            form.compid = self.request.session.get('compid')
        if hasattr(form, 'finyearid'):
            form.finyearid = self.request.session.get('finyear')
        if hasattr(form, 'sessionid'):
            form.sessionid = self.request.session.get('username')
        
        return super().form_valid(form)


class MasterDetailFormSetMixin:
    """Mixin for handling master-detail formsets"""
    
    formset_class = None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = self.formset_class(
                self.request.POST,
                instance=self.object
            )
        else:
            context['formset'] = self.formset_class(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class HTMXResponseMixin:
    """Mixin for handling HTMX requests"""
    
    htmx_template_name = None
    
    def get_template_names(self):
        """Return HTMX template for HTMX requests"""
        if self.request.headers.get('HX-Request') and self.htmx_template_name:
            return [self.htmx_template_name]
        return super().get_template_names()


class InventoryBaseMixin(LoginRequiredMixin, CompanyFinYearMixin, SessionTrackingMixin):
    """Base mixin combining common inventory functionality"""
    pass
