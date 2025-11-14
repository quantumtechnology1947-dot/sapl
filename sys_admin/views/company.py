"""
SysAdmin Company Data Views
Handles Country, State, City masters and cascading dropdowns.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
    LoginRequiredMixin,
    QueryOptimizationMixin
)

from ..models import Tblcountry, Tblstate, Tblcity, TblcompanyMaster
from ..forms import CountryForm, StateForm, CityForm


# ============================================================================
# COUNTRY MASTER
# ============================================================================

class CountryListView(BaseListViewMixin, ListView):
    """
    Display paginated list of countries with search.
    Uses BaseListViewMixin for auth, search, HTMX, and query optimization.
    """
    model = Tblcountry
    template_name = 'sys_admin/country_list.html'
    partial_template_name = 'sys_admin/partials/country_list_partial.html'
    context_object_name = 'countries'
    paginate_by = 20
    search_fields = ['countryname']

    def get_queryset(self):
        return super().get_queryset().order_by('cid')


class CountryCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new country.
    Uses BaseCreateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = Tblcountry
    form_class = CountryForm
    template_name = 'sys_admin/partials/country_form.html'
    success_url = reverse_lazy('sys_admin:country-list')
    success_message = 'Country "%(countryname)s" created successfully'

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'sys_admin/partials/country_row.html', {'country': self.object})
        return response


class CountryUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing country (inline editing).
    Uses BaseUpdateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = Tblcountry
    form_class = CountryForm
    template_name = 'sys_admin/partials/country_edit_row.html'
    success_url = reverse_lazy('sys_admin:country-list')
    success_message = 'Country "%(countryname)s" updated successfully'
    pk_url_kwarg = 'cid'

    def get(self, request, *args, **kwargs):
        """Return edit form row."""
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'country': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            # Return updated row HTML
            return render(self.request, 'sys_admin/partials/country_row.html', {'country': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'country': self.object})
        return super().form_invalid(form)


class CountryDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete country.
    Uses BaseDeleteViewMixin for auth and HTMX support (auto 204 response).
    """
    model = Tblcountry
    success_url = reverse_lazy('sys_admin:country-list')
    pk_url_kwarg = 'cid'


class CountryRowView(BaseDetailViewMixin, DetailView):
    """
    Return single country row HTML (for cancel operation).
    HTMX endpoint.
    """
    model = Tblcountry
    template_name = 'sys_admin/partials/country_row.html'
    context_object_name = 'country'
    pk_url_kwarg = 'cid'


# ============================================================================
# STATE MASTER
# ============================================================================

class StateListView(BaseListViewMixin, ListView):
    """
    Display paginated list of states with search.
    Uses BaseListViewMixin with query optimization (select_related).
    """
    model = Tblstate
    template_name = 'sys_admin/state_list.html'
    partial_template_name = 'sys_admin/partials/state_list_partial.html'
    context_object_name = 'states'
    paginate_by = 20
    search_fields = ['statename']
    select_related_fields = ['cid']

    def get_queryset(self):
        return super().get_queryset().order_by('statename')


class StateCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new state.
    Uses BaseCreateViewMixin for auth, HTMX, and success messages.
    """
    model = Tblstate
    form_class = StateForm
    template_name = 'sys_admin/partials/state_form.html'
    success_url = reverse_lazy('sys_admin:state-list')
    success_message = 'State "%(statename)s" created successfully'

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'sys_admin/partials/state_row.html', {'state': self.object})
        return response


class StateUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing state (inline editing).
    Uses BaseUpdateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = Tblstate
    form_class = StateForm
    template_name = 'sys_admin/partials/state_edit_row.html'
    success_url = reverse_lazy('sys_admin:state-list')
    success_message = 'State "%(statename)s" updated successfully'
    pk_url_kwarg = 'sid'
    select_related_fields = ['cid']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'state': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'sys_admin/partials/state_row.html', {'state': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'state': self.object})
        return super().form_invalid(form)


class StateDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete state with dependency check.
    Uses BaseDeleteViewMixin for auth and HTMX support (auto 204 response).
    """
    model = Tblstate
    success_url = reverse_lazy('sys_admin:state-list')
    pk_url_kwarg = 'sid'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check for dependent cities
        if self.object.tblcity_set.exists():
            messages.error(request, f"Cannot delete state '{self.object.statename}' because it has associated cities.")
            if request.headers.get('HX-Request'):
                return HttpResponse(status=409, reason="State has associated cities.")
            return redirect(self.success_url)

        messages.success(self.request, f"State '{self.object.statename}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


class StateRowView(BaseDetailViewMixin, DetailView):
    """
    Return single state row HTML (for cancel operation).
    HTMX endpoint with query optimization.
    """
    model = Tblstate
    template_name = 'sys_admin/partials/state_row.html'
    context_object_name = 'state'
    pk_url_kwarg = 'sid'
    select_related_fields = ['cid']


# ============================================================================
# CITY MASTER
# ============================================================================

class CityListView(BaseListViewMixin, ListView):
    """
    Display paginated list of cities with search and filtering.
    Uses BaseListViewMixin for auth, search, HTMX, and query optimization.
    """
    model = Tblcity
    template_name = 'sys_admin/city_list.html'
    partial_template_name = 'sys_admin/partials/city_list_partial.html'
    context_object_name = 'cities'
    paginate_by = 20
    search_fields = ['cityname']
    select_related_fields = ['sid', 'sid__cid']

    def get_queryset(self):
        queryset = super().get_queryset().order_by('cityname')

        # Filter by state if provided
        state_id = self.request.GET.get('state')
        if state_id:
            queryset = queryset.filter(sid_id=state_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add countries for filter dropdown
        context['countries'] = Tblcountry.objects.all().order_by('countryname')

        # Get selected country and state
        selected_country = self.request.GET.get('country')
        selected_state = self.request.GET.get('state')

        if selected_country:
            context['states'] = Tblstate.objects.filter(
                cid_id=selected_country
            ).select_related('cid').order_by('statename')
            context['selected_country'] = int(selected_country)

        if selected_state:
            context['selected_state'] = int(selected_state)

        return context


class CityCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new city.
    Uses BaseCreateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = Tblcity
    form_class = CityForm
    template_name = 'sys_admin/partials/city_form.html'
    success_url = reverse_lazy('sys_admin:city-list')
    success_message = 'City "%(cityname)s" created successfully'

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'sys_admin/partials/city_row.html', {'city': self.object})
        return response


class CityUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing city (inline editing).
    Uses BaseUpdateViewMixin for auth, HTMX, success messages, and audit fields.
    """
    model = Tblcity
    form_class = CityForm
    template_name = 'sys_admin/partials/city_edit_row.html'
    success_url = reverse_lazy('sys_admin:city-list')
    success_message = 'City "%(cityname)s" updated successfully'
    pk_url_kwarg = 'cityid'
    select_related_fields = ['sid', 'sid__cid']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return render(request, self.template_name, {'form': form, 'city': self.object})

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'sys_admin/partials/city_row.html', {'city': self.object})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form, 'city': self.object})
        return super().form_invalid(form)


class CityDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete city with dependency check.
    Uses BaseDeleteViewMixin for auth and HTMX support (auto 204 response).
    Checks if city is referenced in company master (regdcity or plantcity).
    """
    model = Tblcity
    success_url = reverse_lazy('sys_admin:city-list')
    pk_url_kwarg = 'cityid'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check for dependent companies (registered address)
        regd_companies = TblcompanyMaster.objects.filter(regdcity=self.object)
        # Check for dependent companies (plant address)
        plant_companies = TblcompanyMaster.objects.filter(plantcity=self.object)

        if regd_companies.exists() or plant_companies.exists():
            company_names = []
            if regd_companies.exists():
                company_names.extend([c.companyname for c in regd_companies[:3]])
            if plant_companies.exists():
                company_names.extend([c.companyname for c in plant_companies[:3]])

            companies_list = ', '.join(company_names[:3])
            total_count = regd_companies.count() + plant_companies.count()

            error_msg = f"Cannot delete city '{self.object.cityname}' because it is used by {total_count} company(ies): {companies_list}"
            if total_count > 3:
                error_msg += f" and {total_count - 3} more"

            messages.error(request, error_msg)
            if request.headers.get('HX-Request'):
                return HttpResponse(status=409, reason="City has associated companies.")
            return redirect(self.success_url)

        messages.success(self.request, f"City '{self.object.cityname}' deleted successfully.")
        return super().delete(request, *args, **kwargs)


class CityRowView(BaseDetailViewMixin, DetailView):
    """
    Return single city row HTML (for cancel operation).
    HTMX endpoint with query optimization.
    """
    model = Tblcity
    template_name = 'sys_admin/partials/city_row.html'
    context_object_name = 'city'
    pk_url_kwarg = 'cityid'
    select_related_fields = ['sid', 'sid__cid']


# ============================================================================
# CASCADING DROPDOWNS
# ============================================================================

class StatesByCountryView(LoginRequiredMixin, QueryOptimizationMixin, TemplateView):
    """
    HTMX endpoint: Return states dropdown for selected country.
    Used for cascading dropdowns with query optimization.
    """
    template_name = 'sys_admin/partials/state_dropdown.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Accept country_id from either URL path (cid) or query parameter (country)
        country_id = kwargs.get('cid') or self.request.GET.get('country')

        context['selected_country'] = country_id

        if country_id and country_id != '':
            context['states'] = Tblstate.objects.filter(
                cid_id=country_id
            ).select_related('cid').order_by('statename')
        else:
            context['states'] = []
        return context
