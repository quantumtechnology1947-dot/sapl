"""
Customer Master views
"""

from django.views.generic import DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from io import BytesIO

from ..models import SdCustMaster
from ..forms import CustomerForm
from sys_admin.models import (
    Tblcountry, Tblstate, Tblcity,
    TblfinancialMaster as FinancialYear
)
from core.mixins import paginate_queryset

class CustomerCreateView(LoginRequiredMixin, View):
    """
    Handles customer creation as a dedicated page.
    """
    def get(self, request):
        form = CustomerForm()
        return render(request, 'sales_distribution/customer_form.html', {'form': form})

    def post(self, request):
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            now = datetime.now()
            customer.sysdate = now.strftime('%d-%m-%Y')
            customer.systime = now.strftime('%H:%M:%S')
            customer.sessionid = str(request.user.id)

            # FIXED: Get compid from session with fallback to 1
            customer.compid = request.session.get('compid', 1)

            # Get finyearid from session, or use latest active financial year
            customer.finyearid = request.session.get('finyearid')
            if not customer.finyearid:
                # Fallback: Get latest active financial year (highest finyearid with flag=1)
                current_fy = FinancialYear.objects.filter(flag=1).order_by('-finyearid').first()
                if current_fy:
                    customer.finyearid = current_fy.finyearid
                else:
                    # If no active FY, get the latest one
                    latest_fy = FinancialYear.objects.order_by('-finyearid').first()
                    customer.finyearid = latest_fy.finyearid if latest_fy else 1

            # FIXED: Generate customer ID - character-based like ASP.NET (A001, B001, etc.)
            first_char = customer.customername[0].upper() if customer.customername else 'A'

            # Find last customer ID with this starting character
            last_customer = SdCustMaster.objects.filter(
                customerid__istartswith=first_char,
                compid=customer.compid
            ).order_by('-salesid').first()

            if last_customer and last_customer.customerid:
                try:
                    # Extract numeric part (e.g., from "A012" get 12)
                    last_num = int(last_customer.customerid[1:])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1

            customer.customerid = f'{first_char}{new_num:03d}'  # Format: A001, A002, etc.

            customer.save()
            messages.success(request, f'Customer {customer.customername} created successfully.')

            # Redirect to customer list after successful creation
            return redirect('sales_distribution:customer-list')

        return render(request, 'sales_distribution/customer_form.html', {'form': form})


class CustomerView(LoginRequiredMixin, View):
    """
    Handles CRUD operations for Customers.
    """
    def get(self, request, salesid=None):
        if salesid:
            customer = get_object_or_404(SdCustMaster, salesid=salesid)
            form = CustomerForm(instance=customer)
            return render(request, 'sales_distribution/customer_form.html', {'form': form, 'customer': customer})
        else:
            from django.contrib.auth.models import User
            from core.mixins import paginate_queryset

            queryset = SdCustMaster.objects.all().order_by('-salesid')
            search = request.GET.get('search', '')
            if search:
                queryset = SdCustMaster.objects.filter(
                    Q(customername__icontains=search) |
                    Q(contactperson__icontains=search) |
                    Q(email__icontains=search)
                ).order_by('-salesid')

            # Paginate
            pagination = paginate_queryset(queryset, request, per_page=20)
            customers = pagination['page_obj']

            # Enrich customers with financial year and user info
            fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}
            user_dict = {str(user.id): user.username for user in User.objects.all()}

            for customer in customers:
                customer.finyear_name = fy_dict.get(customer.finyearid, '-')
                if customer.sessionid and customer.sessionid.isdigit():
                    customer.generated_by = user_dict.get(customer.sessionid, customer.sessionid)
                else:
                    customer.generated_by = customer.sessionid if customer.sessionid else '-'

            context = {
                'customers': customers,
                'page_obj': pagination['page_obj'],
                'is_paginated': pagination['is_paginated'],
                'paginator': pagination['paginator'],
                'search_query': search,
                'form': CustomerForm()
            }

            if request.headers.get('HX-Request'):
                return render(request, 'sales_distribution/partials/customer_list_partial.html', context)

            return render(request, 'sales_distribution/customer_list.html', context)

    def post(self, request, salesid=None):
        if salesid:
            # Update existing customer
            customer = get_object_or_404(SdCustMaster, salesid=salesid)
            form = CustomerForm(request.POST, instance=customer)
            if form.is_valid():
                customer = form.save(commit=False)
                # Update audit fields
                now = datetime.now()
                customer.sysdate = now.strftime('%d-%m-%Y')
                customer.systime = now.strftime('%H:%M:%S')
                customer.sessionid = str(request.user.id)
                customer.compid = request.session.get('compid', 1)

                # Get finyearid from session, or use latest active financial year
                customer.finyearid = request.session.get('finyearid')
                if not customer.finyearid:
                    # Fallback: Get latest active financial year (highest finyearid with flag=1)
                    current_fy = FinancialYear.objects.filter(flag=1).order_by('-finyearid').first()
                    if current_fy:
                        customer.finyearid = current_fy.finyearid
                    else:
                        # If no active FY, get the latest one
                        latest_fy = FinancialYear.objects.order_by('-finyearid').first()
                        customer.finyearid = latest_fy.finyearid if latest_fy else 1

                customer.save()
                messages.success(request, f'Customer {customer.customername} updated successfully.')
                return redirect('sales_distribution:customer-list')
            return render(request, 'sales_distribution/customer_form.html', {'form': form, 'customer': customer})
        else:
            # Create new customer - redirect to CustomerCreateView
            return redirect('sales_distribution:customer-create')

    def put(self, request, salesid):
        customer = get_object_or_404(SdCustMaster, salesid=salesid)
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            # Update audit fields
            now = datetime.now()
            customer.sysdate = now.strftime('%d-%m-%Y')
            customer.systime = now.strftime('%H:%M:%S')
            customer.sessionid = str(request.user.id)
            customer.compid = request.session.get('compid', 1)

            # Get finyearid from session, or use latest active financial year
            customer.finyearid = request.session.get('finyearid')
            if not customer.finyearid:
                # Fallback: Get latest active financial year (highest finyearid with flag=1)
                current_fy = FinancialYear.objects.filter(flag=1).order_by('-finyearid').first()
                if current_fy:
                    customer.finyearid = current_fy.finyearid
                else:
                    # If no active FY, get the latest one
                    latest_fy = FinancialYear.objects.order_by('-finyearid').first()
                    customer.finyearid = latest_fy.finyearid if latest_fy else 1

            customer.save()
            messages.success(request, f'Customer {customer.customername} updated successfully.')
            return redirect('sales_distribution:customer-list')
        return render(request, 'sales_distribution/customer_form.html', {'form': form, 'customer': customer})

    def delete(self, request, salesid):
        customer = get_object_or_404(SdCustMaster, salesid=salesid)
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return HttpResponse(status=204)


class CustomerSearchView(LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint: Search customers by name.
    Returns dropdown of matching customers.
    """
    template_name = 'sales_distribution/partials/customer_search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get search query
        query = self.request.GET.get('existing_customer_search', '').strip()

        if query and len(query) >= 1:  # Search after 1 character
            # Search customers by name
            customers = SdCustMaster.objects.filter(
                customername__icontains=query
            ).order_by('customername')[:10]  # Limit to 10 results

            context['customers'] = customers
        else:
            context['customers'] = []

        return context


class CustomerJSONView(LoginRequiredMixin, View):
    """
    Return customer data as JSON for populating enquiry form.
    Used by Search button in enquiry form.
    """

    def get(self, request, salesid):
        """Return customer data as JSON."""
        from django.http import JsonResponse

        try:
            customer = SdCustMaster.objects.get(salesid=salesid)

            # Get country/state names from IDs (SdCustMaster uses IntegerField for country/state)
            # Registered office
            regdcountry_name = ''
            regdstate_name = ''
            if customer.regdcountry:
                regdcountry_obj = Tblcountry.objects.filter(cid=customer.regdcountry).first()
                regdcountry_name = regdcountry_obj.countryname if regdcountry_obj else ''
            if customer.regdstate:
                regdstate_obj = Tblstate.objects.filter(sid=customer.regdstate).first()
                regdstate_name = regdstate_obj.statename if regdstate_obj else ''

            # Works/Factory
            workcountry_name = ''
            workstate_name = ''
            if customer.workcountry:
                workcountry_obj = Tblcountry.objects.filter(cid=customer.workcountry).first()
                workcountry_name = workcountry_obj.countryname if workcountry_obj else ''
            if customer.workstate:
                workstate_obj = Tblstate.objects.filter(sid=customer.workstate).first()
                workstate_name = workstate_obj.statename if workstate_obj else ''

            # Material delivery
            materialdelcountry_name = ''
            materialdelstate_name = ''
            if customer.materialdelcountry:
                materialdelcountry_obj = Tblcountry.objects.filter(cid=customer.materialdelcountry).first()
                materialdelcountry_name = materialdelcountry_obj.countryname if materialdelcountry_obj else ''
            if customer.materialdelstate:
                materialdelstate_obj = Tblstate.objects.filter(sid=customer.materialdelstate).first()
                materialdelstate_name = materialdelstate_obj.statename if materialdelstate_obj else ''

            # Build customer data dictionary
            data = {
                'salesid': customer.salesid,
                'customerid': customer.customerid,
                'customername': customer.customername,

                # Registered office address
                'regdaddress': customer.regdaddress or '',
                'regdcountry': regdcountry_name,
                'regdstate': regdstate_name,
                'regdcity': customer.regdcity.cityname if customer.regdcity else '',
                'regdpinno': customer.regdpinno or '',
                'regdcontactno': customer.contactno or '',

                # Works/Factory address
                'workaddress': customer.workaddress or '',
                'workcountry': workcountry_name,
                'workstate': workstate_name,
                'workcity': customer.workcity.cityname if customer.workcity else '',
                'workpinno': customer.workpinno or '',
                'workcontactno': customer.contactno or '',

                # Material delivery address
                'materialdeladdress': customer.materialdeladdress or '',
                'materialdelcountry': materialdelcountry_name,
                'materialdelstate': materialdelstate_name,
                'materialdelcity': customer.materialdelcity.cityname if customer.materialdelcity else '',
                'materialdelpinno': customer.materialdelpinno or '',
                'materialdelcontactno': customer.contactno or '',

                # Contact info
                'contactperson': customer.contactperson or '',
                'email': customer.email or '',
                'contactno': customer.contactno or '',

                # Tax info
                'tincstno': customer.tincstno or '',
            }

            return JsonResponse(data)

        except SdCustMaster.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)


class StatesByCountryView(LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint: Return states dropdown for selected country.
    Handles both country ID (integer) and country name (string).
    Requirements: 12.1, 12.2
    """
    template_name = 'sales_distribution/partials/state_dropdown.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get country from any of the three address sections
        country_value = (
            self.request.GET.get('regdcountry') or
            self.request.GET.get('workcountry') or
            self.request.GET.get('materialdelcountry')
        )

        # Determine which address section this is for
        if self.request.GET.get('regdcountry'):
            field_prefix = 'regd'
        elif self.request.GET.get('workcountry'):
            field_prefix = 'work'
        else:
            field_prefix = 'materialdel'

        # Check if this is for enquiry form (use_names=true) or customer form (use IDs)
        use_names = self.request.GET.get('use_names', '').lower() == 'true'
        context['use_names'] = use_names

        if country_value:
            # Check if value is an integer ID or a country name
            try:
                country_id = int(country_value)
                # It's an integer ID - use it directly
                context['states'] = Tblstate.objects.filter(cid_id=country_id).order_by('statename')
            except ValueError:
                # It's a country name - look up the country ID first
                country = Tblcountry.objects.filter(countryname=country_value).first()
                if country:
                    context['states'] = Tblstate.objects.filter(cid_id=country.cid).order_by('statename')
                else:
                    context['states'] = Tblstate.objects.none()
        else:
            context['states'] = Tblstate.objects.none()

        context['field_prefix'] = field_prefix
        return context


class CitiesByStateView(LoginRequiredMixin, TemplateView):
    """
    HTMX endpoint: Return cities dropdown for selected state.
    Handles both state ID (integer) and state name (string).
    Requirements: 12.3
    """
    template_name = 'sales_distribution/partials/city_dropdown.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get state from any of the three address sections
        state_value = (
            self.request.GET.get('regdstate') or
            self.request.GET.get('workstate') or
            self.request.GET.get('materialdelstate')
        )

        # Determine which address section this is for
        if self.request.GET.get('regdstate'):
            field_prefix = 'regd'
        elif self.request.GET.get('workstate'):
            field_prefix = 'work'
        else:
            field_prefix = 'materialdel'

        # Check if this is for enquiry form (use_names=true) or customer form (use IDs)
        use_names = self.request.GET.get('use_names', '').lower() == 'true'
        context['use_names'] = use_names

        if state_value:
            # Check if value is an integer ID or a state name
            try:
                state_id = int(state_value)
                # It's an integer ID - use it directly
                context['cities'] = Tblcity.objects.filter(sid_id=state_id).order_by('cityname')
            except ValueError:
                # It's a state name - look up the state ID first
                state = Tblstate.objects.filter(statename=state_value).first()
                if state:
                    context['cities'] = Tblcity.objects.filter(sid_id=state.sid).order_by('cityname')
                else:
                    context['cities'] = Tblcity.objects.none()
        else:
            context['cities'] = Tblcity.objects.none()

        context['field_prefix'] = field_prefix
        return context


class CustomerMasterPrintView(LoginRequiredMixin, DetailView):
    """
    Generate professional PDF for Customer Master data.
    Converted from: D:/inetpub/NewERP/Module/SalesDistribution/Masters/CustomerMaster_Print_Details.aspx

    Note: Uses xhtml2pdf instead of Crystal Reports for Windows compatibility
    """
    model = SdCustMaster
    pk_url_kwarg = 'salesid'
    template_name = 'sales_distribution/customer_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()

        # Get related city/state/country data for registered address
        # Note: regdcity, workcity, materialdelcity are ForeignKey fields (already objects)
        # regdstate, regdcountry, etc. are IntegerField (need to fetch)
        regdcity_name = customer.regdcity.cityname if customer.regdcity else None
        regdstate_name = None
        regdcountry_name = None

        if customer.regdstate:
            try:
                state = Tblstate.objects.get(pk=customer.regdstate)
                regdstate_name = state.statename
            except Tblstate.DoesNotExist:
                pass

        if customer.regdcountry:
            try:
                country = Tblcountry.objects.get(pk=customer.regdcountry)
                regdcountry_name = country.countryname
            except Tblcountry.DoesNotExist:
                pass

        # Get related city/state/country data for work address
        workcity_name = customer.workcity.cityname if customer.workcity else None
        workstate_name = None
        workcountry_name = None

        if customer.workstate:
            try:
                state = Tblstate.objects.get(pk=customer.workstate)
                workstate_name = state.statename
            except Tblstate.DoesNotExist:
                pass

        if customer.workcountry:
            try:
                country = Tblcountry.objects.get(pk=customer.workcountry)
                workcountry_name = country.countryname
            except Tblcountry.DoesNotExist:
                pass

        # Get related city/state/country data for material delivery address
        materialdelcity_name = customer.materialdelcity.cityname if customer.materialdelcity else None
        materialdelstate_name = None
        materialdelcountry_name = None

        if customer.materialdelstate:
            try:
                state = Tblstate.objects.get(pk=customer.materialdelstate)
                materialdelstate_name = state.statename
            except Tblstate.DoesNotExist:
                pass

        if customer.materialdelcountry:
            try:
                country = Tblcountry.objects.get(pk=customer.materialdelcountry)
                materialdelcountry_name = country.countryname
            except Tblcountry.DoesNotExist:
                pass

        # Get financial year name if available
        finyear_name = None
        if hasattr(customer, 'finyearid') and customer.finyearid:
            try:
                finyear = FinancialYear.objects.get(pk=customer.finyearid)
                finyear_name = finyear.finyear
            except FinancialYear.DoesNotExist:
                finyear_name = str(customer.finyearid)

        # Get employee/user name if available
        employee_name = None
        if hasattr(customer, 'sessionid') and customer.sessionid:
            try:
                user = User.objects.get(pk=int(customer.sessionid))
                employee_name = user.username
            except (User.DoesNotExist, ValueError):
                employee_name = customer.sessionid

        # Company info from settings
        context.update({
            'customer': customer,
            'regdcity_name': regdcity_name,
            'regdstate_name': regdstate_name,
            'regdcountry_name': regdcountry_name,
            'workcity_name': workcity_name,
            'workstate_name': workstate_name,
            'workcountry_name': workcountry_name,
            'materialdelcity_name': materialdelcity_name,
            'materialdelstate_name': materialdelstate_name,
            'materialdelcountry_name': materialdelcountry_name,
            'finyear_name': finyear_name,
            'employee_name': employee_name,
            'company_name': 'Synergytech Automation Pvt. Ltd.',
            'company_address': 'Pune, Maharashtra, India',
            'company_phone': '+91-XXX-XXXXXXX',
            'company_email': 'sales@synergytechs.com',
            'company_website': 'www.synergytechs.com',
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        """Generate PDF from template"""
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa
        from io import BytesIO

        # Render HTML template
        html_string = render_to_string(self.template_name, context)

        # Generate PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

        if pdf.err:
            return HttpResponse(f'Error generating PDF: {pdf.err}', content_type='text/html')

        # Return as PDF response
        customer_id = context['customer'].customerid if context['customer'].customerid else f'CUST_{context["customer"].salesid}'
        filename = f'Customer_{customer_id}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response



