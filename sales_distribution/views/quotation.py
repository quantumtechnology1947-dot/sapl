"""
Quotation views and workflow
"""

from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView,
    DetailView, TemplateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, F, Value, CharField, OuterRef, Subquery
from django.db.models.functions import Coalesce, Concat
from django.db import transaction
from datetime import datetime
from io import BytesIO

from ..models import (
    SdCustMaster, SdCustEnquiryMaster, SdCustQuotationMaster,
    SdCustQuotationDetails
)
from ..forms import QuotationMasterForm, QuotationDetailForm
from .base import FinancialYearUserMixin
from sys_admin.models import (
    TblfinancialMaster as FinancialYear,
    UnitMaster, TblexciseserMaster, TblvatMaster, TblgstMaster
)
from human_resource.models import TblhrOfficestaff

class QuotationView(LoginRequiredMixin, View):
    """
    Handles CRUD operations for Quotations.
    """
    def get(self, request, id=None):
        if id:
            quotation = get_object_or_404(SdCustQuotationMaster, id=id)
            line_items = SdCustQuotationDetails.objects.filter(mid=quotation).select_related('unit')
            subtotal = sum((item.totalqty * item.rate) - ((item.totalqty * item.rate * (item.discount or 0)) / 100) for item in line_items)
            total = subtotal
            return render(request, 'sales_distribution/quotation_detail.html', {'quotation': quotation, 'line_items': line_items, 'subtotal': subtotal, 'total': total})
        else:
            from django.contrib.auth.models import User
            from core.mixins import paginate_queryset

            queryset = SdCustQuotationMaster.objects.select_related('enqid').all().order_by('-id')
            search = request.GET.get('search', '')
            if search:
                queryset = SdCustQuotationMaster.objects.select_related('enqid').filter(
                    Q(quotationno__icontains=search) |
                    Q(customerid__icontains=search) |
                    Q(enqid__customername__icontains=search)
                ).order_by('-id')

            # Paginate
            pagination = paginate_queryset(queryset, request, per_page=20)
            quotations = pagination['page_obj']

            # Enrich quotations with financial year and user info
            fy_dict = {fy.finyearid: fy.finyear for fy in FinancialYear.objects.all()}
            user_dict = {str(user.id): user.username for user in User.objects.all()}

            for quotation in quotations:
                quotation.finyear_name = fy_dict.get(quotation.finyearid, '-')
                if quotation.sessionid and quotation.sessionid.isdigit():
                    quotation.generated_by = user_dict.get(quotation.sessionid, quotation.sessionid)
                else:
                    quotation.generated_by = quotation.sessionid if quotation.sessionid else '-'

            context = {
                'quotations': quotations,
                'page_obj': pagination['page_obj'],
                'is_paginated': pagination['is_paginated'],
                'paginator': pagination['paginator'],
                'search_query': search
            }

            if request.headers.get('HX-Request'):
                return render(request, 'sales_distribution/partials/quotation_list_partial.html', context)
            return render(request, 'sales_distribution/quotation_list.html', context)

    def post(self, request):
        return redirect('sales_distribution:quotation-search')

    def delete(self, request, id):
        quotation = get_object_or_404(SdCustQuotationMaster, id=id)
        quot_no = quotation.quotationno
        if quotation.checked == 1 or quotation.approve == 1 or quotation.authorize == 1:
            messages.error(request, f'Cannot delete quotation {quot_no}. It has been checked/approved/authorized.')
            if request.headers.get('HX-Request'):
                return HttpResponse(status=403)
            return redirect('sales_distribution:quotation-list')
        if SdCustPoMaster.objects.filter(quotationno=quotation.id).exists():
            messages.error(request, f'Cannot delete quotation {quot_no}. Purchase Orders exist for this quotation.')
            if request.headers.get('HX-Request'):
                return HttpResponse(status=403)
            return redirect('sales_distribution:quotation-list')
        SdCustQuotationDetails.objects.filter(mid=quotation).delete()
        quotation.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        messages.success(request, f'Quotation {quot_no} deleted successfully.')
        return redirect('sales_distribution:quotation-list')


class QuotationSearchView(LoginRequiredMixin, FinancialYearUserMixin, TemplateView):
    """
    Full page view for searching enquiries to create quotations.
    Shows all pending enquiries by default.
    """
    template_name = 'sales_distribution/quotation_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth.models import User
        
        # Show all pending enquiries by default (postatus=0 means no PO created yet)
        enquiries = list(SdCustEnquiryMaster.objects.filter(postatus=0).order_by('-enqid')[:50])
        
        # Enrich with metadata including quotation count
        self.enrich_with_metadata(enquiries, include_quotation_count=True)
        
        context['enquiries'] = enquiries
        return context


class QuotationSearchResultsView(LoginRequiredMixin, FinancialYearUserMixin, TemplateView):
    """
    HTMX endpoint: Return search results for enquiries with universal search.
    Searches across enquiry ID, customer name, and customer code.
    """
    template_name = 'sales_distribution/partials/quotation_enquiry_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_value = self.request.GET.get('search_value', '').strip()

        if not search_value:
            context['enquiries'] = []
            return context

        # Universal search across multiple fields using Q objects
        queryset = SdCustEnquiryMaster.objects.filter(postatus=0).filter(
            Q(enqid__icontains=search_value) |
            Q(customername__icontains=search_value) |
            Q(customerid__icontains=search_value)
        )

        enquiries = list(queryset.order_by('-enqid')[:20])  # Limit to 20 results

        # Add metadata using mixin (includes quotation count)
        self.enrich_with_metadata(enquiries, include_quotation_count=True)

        context['enquiries'] = enquiries
        return context


class QuotationCreateDetailView(LoginRequiredMixin, CreateView):
    """
    Create new quotation with line items from selected enquiry.
    Converted from: aspnet/Module/SalesDistribution/Transactions/Quotation_New_Details.aspx
    """
    model = SdCustQuotationMaster
    form_class = QuotationMasterForm
    template_name = 'sales_distribution/quotation_create_detail.html'
    success_url = reverse_lazy('sales_distribution:quotation-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get enquiry
        enqid = self.kwargs.get('enqid')
        try:
            enquiry = SdCustEnquiryMaster.objects.get(enqid=enqid)
            context['enquiry'] = enquiry
        except SdCustEnquiryMaster.DoesNotExist:
            messages.error(self.request, 'Enquiry not found.')
            context['enquiry'] = None

        # Get units for line items
        context['units'] = UnitMaster.objects.all().order_by('symbol')

        # Get GST 2.0 rates (replaces separate CGST/SGST dropdowns)
        context['gst_rates'] = TblgstMaster.objects.filter(live=1).order_by('ratevalue')

        return context

    def form_valid(self, form):
        """Save quotation master and line items."""
        import json
        from django.core.exceptions import ValidationError

        try:
            # Get enquiry
            enqid = self.request.POST.get('enqid')
            enquiry = SdCustEnquiryMaster.objects.get(enqid=enqid)

            # Add system fields
            now = datetime.now()
            form.instance.sysdate = now.strftime('%d-%m-%Y')
            form.instance.systime = now.strftime('%H:%M:%S')
            form.instance.sessionid = str(self.request.user.id)

            # FIXED: Get compid from session, with fallback to default company ID
            form.instance.compid = self.request.session.get('compid', 1)  # Default to company ID 1

            # If still not set, force it to 1 and update session for future requests
            if not form.instance.compid:
                form.instance.compid = 1
                self.request.session['compid'] = 1
                self.request.session.modified = True

            # Get finyearid from session, or use latest active financial year
            form.instance.finyearid = self.request.session.get('finyearid')
            if not form.instance.finyearid:
                # Fallback: Get latest active financial year (highest finyearid with flag=1)
                current_fy = FinancialYear.objects.filter(flag=1).order_by('-finyearid').first()
                if current_fy:
                    form.instance.finyearid = current_fy.finyearid
                else:
                    # If no active FY, get the latest one
                    latest_fy = FinancialYear.objects.order_by('-finyearid').first()
                    form.instance.finyearid = latest_fy.finyearid if latest_fy else 1

            # FIXED: Generate Quotation Number - numeric only like ASP.NET (0001, 0002, etc.)
            last_quot = SdCustQuotationMaster.objects.filter(
                compid=form.instance.compid,
                finyearid=form.instance.finyearid
            ).order_by('-id').first()

            if last_quot and last_quot.quotationno:
                try:
                    # Handle both old format "QUOT0001" and new format "0001"
                    quotno_clean = last_quot.quotationno.replace('QUOT', '')
                    last_num = int(quotno_clean)
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1

            form.instance.quotationno = f'{new_num:04d}'  # Format: 0001, 0002, etc.

            # Set enquiry and customer
            form.instance.enqid = enquiry
            form.instance.customerid = enquiry.customerid

            # Set workflow status
            form.instance.checked = 0
            form.instance.authorize = 0
            form.instance.approve = 0

            # Save master
            quotation = form.save()

            # Parse and save line items
            line_items_json = self.request.POST.get('line_items', '[]')
            line_items = json.loads(line_items_json)

            if not line_items:
                raise ValidationError('At least one line item is required.')

            for item in line_items:
                SdCustQuotationDetails.objects.create(
                    mid=quotation,
                    sessionid=str(self.request.user.id),
                    compid=quotation.compid,
                    finyearid=quotation.finyearid,
                    itemdesc=item['itemdesc'],
                    totalqty=item['totalqty'],
                    rate=item['rate'],
                    discount=item.get('discount', 0),
                    unit_id=item['unit']
                )

            messages.success(self.request, f'Quotation {quotation.quotationno} created successfully with {len(line_items)} line items.')
            return redirect(self.success_url)

        except SdCustEnquiryMaster.DoesNotExist:
            messages.error(self.request, 'Enquiry not found.')
            return self.form_invalid(form)
        except json.JSONDecodeError:
            messages.error(self.request, 'Invalid line items data.')
            return self.form_invalid(form)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error creating quotation: {str(e)}')
            return self.form_invalid(form)


class QuotationEditView(LoginRequiredMixin, UpdateView):
    """
    Edit existing quotation with line items.
    """
    model = SdCustQuotationMaster
    form_class = QuotationMasterForm
    template_name = 'sales_distribution/quotation_create_detail.html'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy('sales_distribution:quotation-detail', kwargs={'id': self.object.id})

    def get_context_data(self, **kwargs):
        import json
        from decimal import Decimal

        context = super().get_context_data(**kwargs)

        # Get the quotation being edited
        quotation = self.object

        # Get enquiry from quotation
        context['enquiry'] = quotation.enqid

        # Get existing line items
        line_items = SdCustQuotationDetails.objects.filter(mid=quotation).select_related('unit')
        items_data = list(line_items.values(
            'itemdesc', 'totalqty', 'unit__id', 'unit__unitname',
            'rate', 'discount'
        ))

        # Convert Decimal to float for JSON serialization
        for item in items_data:
            if isinstance(item.get('totalqty'), Decimal):
                item['totalqty'] = float(item['totalqty'])
            if isinstance(item.get('rate'), Decimal):
                item['rate'] = float(item['rate'])
            if isinstance(item.get('discount'), Decimal):
                item['discount'] = float(item['discount'])

        # Convert to JSON string for template
        context['existing_line_items_json'] = json.dumps(items_data)

        # Get units for line items
        context['units'] = UnitMaster.objects.all().order_by('symbol')

        # Get GST rates
        context['gst_rates'] = TblgstMaster.objects.filter(live=1).order_by('ratevalue')

        # Set edit mode flag
        context['is_edit'] = True

        return context

    def form_valid(self, form):
        """Update quotation master and line items."""
        import json
        from django.core.exceptions import ValidationError

        try:
            quotation = self.object

            # Update system fields
            now = datetime.now()
            form.instance.systime = now.strftime('%H:%M:%S')

            # Save master
            quotation = form.save()

            # Delete existing line items
            SdCustQuotationDetails.objects.filter(mid=quotation).delete()

            # Parse and save line items
            line_items_json = self.request.POST.get('line_items', '[]')
            line_items = json.loads(line_items_json)

            if not line_items:
                raise ValidationError('At least one line item is required.')

            for item_data in line_items:
                if not item_data.get('itemdesc') or not item_data.get('totalqty'):
                    continue

                SdCustQuotationDetails.objects.create(
                    mid=quotation,
                    sessionid=str(self.request.user.id),
                    compid=quotation.compid,
                    finyearid=quotation.finyearid,
                    itemdesc=item_data['itemdesc'],
                    totalqty=float(item_data['totalqty']),
                    unit_id=int(item_data['unit']),
                    rate=float(item_data.get('rate', 0)),
                    discount=float(item_data.get('discount', 0))
                )

            messages.success(self.request, f'Quotation {quotation.quotationno} updated successfully.')
            return redirect(self.get_success_url())

        except json.JSONDecodeError:
            messages.error(self.request, 'Invalid line items data.')
            return self.form_invalid(form)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error updating quotation: {str(e)}')
            return self.form_invalid(form)


class QuotationWorkflowBaseView(LoginRequiredMixin, FinancialYearUserMixin, ListView):
    """
    Base view for Check/Approve/Authorize workflow.
    Eliminates duplicate code across three workflow views.
    """
    model = SdCustQuotationMaster
    context_object_name = 'quotations'
    paginate_by = 20
    
    # Override these in subclasses
    workflow_filter = {}
    workflow_fields = {}
    success_message = ''
    post_action = None
    
    def get_context_data(self, **kwargs):
        """Add metadata to quotations using mixin."""
        context = super().get_context_data(**kwargs)
        quotations = list(context['quotations'])
        self.enrich_with_metadata(quotations)
        context['quotations'] = quotations
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle workflow action."""
        quotation_id = request.POST.get('quotation_id')
        quotation = get_object_or_404(SdCustQuotationMaster, id=quotation_id)
        
        # Update workflow fields
        now = datetime.now()
        for field, value_type in self.workflow_fields.items():
            if value_type == 'username':
                setattr(quotation, field, request.user.username)
            elif value_type == 'date':
                setattr(quotation, field, now.strftime('%d-%m-%Y'))
            elif value_type == 'time':
                setattr(quotation, field, now.strftime('%H:%M:%S'))
            else:
                setattr(quotation, field, value_type)
        
        quotation.save()
        
        # Execute post-action if defined
        if self.post_action == 'update_enquiry_status' and quotation.enqid:
            quotation.enqid.postatus = 1
            quotation.enqid.save()
        
        messages.success(request, f'Quotation {quotation.quotationno} {self.success_message} successfully!')
        return HttpResponse(status=200)


class QuotationCheckView(QuotationWorkflowBaseView):
    """Quotation Check Dashboard - List Pending Quotations for checking."""
    template_name = 'sales_distribution/quotation_check.html'
    workflow_filter = {'checked': 0}
    workflow_fields = {
        'checked': 1,
        'checkedby': 'username',
        'checkeddate': 'date',
        'checkedtime': 'time'
    }
    success_message = 'checked'
    
    def get_queryset(self):
        return SdCustQuotationMaster.objects.select_related('enqid').filter(
            **self.workflow_filter
        ).order_by('-id')


class QuotationApproveView(QuotationWorkflowBaseView):
    """Quotation Approve Dashboard - List Checked Quotations for approval."""
    template_name = 'sales_distribution/quotation_approve.html'
    workflow_filter = {'checked': 1, 'approve': 0}
    workflow_fields = {
        'approve': 1,
        'approvedby': 'username',
        'approvedate': 'date',
        'approvetime': 'time'
    }
    success_message = 'approved'
    
    def get_queryset(self):
        return SdCustQuotationMaster.objects.select_related('enqid').filter(
            **self.workflow_filter
        ).order_by('-id')


class QuotationAuthorizeView(QuotationWorkflowBaseView):
    """Quotation Authorize Dashboard - List Approved Quotations for authorization."""
    template_name = 'sales_distribution/quotation_authorize.html'
    workflow_filter = {'approve': 1, 'authorize': 0}
    workflow_fields = {
        'authorize': 1,
        'authorizedby': 'username',
        'authorizedate': 'date',
        'authorizetime': 'time'
    }
    success_message = 'authorized'
    post_action = 'update_enquiry_status'

    def get_queryset(self):
        return SdCustQuotationMaster.objects.select_related('enqid').filter(
            **self.workflow_filter
        ).order_by('-id')


class QuotationDeleteView(LoginRequiredMixin, FinancialYearUserMixin, DeleteView):
    """
    Delete quotation with confirmation.
    Converted from: D:/inetpub/NewERP/Module/SalesDistribution/Transactions/Quotation_Delete.aspx
    """
    model = SdCustQuotationMaster
    pk_url_kwarg = 'quotation_id'
    template_name = 'sales_distribution/quotation_delete.html'
    success_url = reverse_lazy('sales_distribution:quotation-check')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get quotation details
        quotation = self.get_object()
        details = SdCustQuotationDetails.objects.filter(mid=quotation).select_related('unit')

        context['quotation'] = quotation
        context['details'] = details
        context['detail_count'] = details.count()

        # Enrich with metadata
        self.enrich_with_metadata([quotation])

        return context

    def delete(self, request, *args, **kwargs):
        """Handle quotation deletion with cascade delete of details."""
        quotation = self.get_object()
        quotation_no = quotation.quotationno

        try:
            # Delete details first (cascade)
            SdCustQuotationDetails.objects.filter(mid=quotation).delete()

            # Delete master
            quotation.delete()

            messages.success(request, f'Quotation {quotation_no} deleted successfully!')
            return HttpResponseRedirect(self.success_url)

        except Exception as e:
            messages.error(request, f'Error deleting quotation: {str(e)}')
            return HttpResponseRedirect(reverse('sales_distribution:quotation-check'))


class QuotationPrintView(LoginRequiredMixin, DetailView):
    """
    Generate professional PDF quotation for customer.
    Converted from: D:/inetpub/NewERP/Module/SalesDistribution/Transactions/Quotation_Print.aspx

    Note: Uses xhtml2pdf instead of WeasyPrint for Windows compatibility (no GTK dependencies required)
    """
    model = SdCustQuotationMaster
    pk_url_kwarg = 'quotation_id'
    template_name = 'sales_distribution/quotation_print_pdf.html'

    def get_context_data(self, **kwargs):
        from django.conf import settings

        context = super().get_context_data(**kwargs)
        quotation = self.get_object()

        # Get quotation details with unit info
        details = SdCustQuotationDetails.objects.filter(mid=quotation).select_related('unit')

        # Get customer info
        try:
            customer = SdCustMaster.objects.get(customerid=quotation.customerid)
        except SdCustMaster.DoesNotExist:
            customer = None

        # Calculate totals
        subtotal = 0
        for detail in details:
            line_total = detail.totalqty * detail.rate
            if detail.discount:
                line_total -= (line_total * detail.discount / 100)
            subtotal += line_total
            detail.line_total = line_total

        # Apply charges
        pf_amount = 0
        if quotation.pf and quotation.pftype:
            if quotation.pftype == 1:  # Percentage
                pf_amount = subtotal * quotation.pf / 100
            else:  # Fixed amount
                pf_amount = quotation.pf

        freight_amount = 0
        if quotation.freight and quotation.freighttype:
            if quotation.freighttype == 1:  # Percentage
                freight_amount = subtotal * quotation.freight / 100
            else:
                freight_amount = quotation.freight

        other_charges = quotation.othercharges or 0
        insurance = quotation.insurance or 0
        octroi_amount = 0
        if quotation.octroi and quotation.octroitype:
            if quotation.octroitype == 1:
                octroi_amount = subtotal * quotation.octroi / 100
            else:
                octroi_amount = quotation.octroi

        grand_total = subtotal + pf_amount + freight_amount + other_charges + insurance + octroi_amount

        context.update({
            'quotation': quotation,
            'details': details,
            'customer': customer,
            'subtotal': subtotal,
            'pf_amount': pf_amount,
            'freight_amount': freight_amount,
            'other_charges': other_charges,
            'insurance': insurance,
            'octroi_amount': octroi_amount,
            'grand_total': grand_total,
            'company_name': 'Synergytech Automation Pvt. Ltd.',
            'company_address': 'Pune, Maharashtra, India',
            'company_phone': '+91-XXX-XXXXXXX',
            'company_email': 'sales@synergytechs.com',
            'company_website': 'www.synergytechs.com',
        })

        return context

    def render_to_response(self, context, **response_kwargs):
        """Render as PDF using xhtml2pdf"""
        from xhtml2pdf import pisa
        from django.template.loader import render_to_string
        from io import BytesIO

        # Render HTML template
        html_string = render_to_string(self.template_name, context)

        # Generate PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

        if pdf.err:
            return HttpResponse(f'Error generating PDF: {pdf.err}', content_type='text/html')

        # Return as PDF response
        quotation_no = context['quotation'].quotationno.replace('/', '_')
        filename = f'Quotation_{quotation_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response




class QuotationPrintView(LoginRequiredMixin, DetailView):
    """
    Generate professional PDF for Customer Quotation.
    Converted from: D:/inetpub/NewERP/Module/SalesDistribution/Transactions/Quotation_Print_Details.aspx

    Note: Uses xhtml2pdf instead of Crystal Reports for Windows compatibility
    """
    model = SdCustQuotationMaster
    pk_url_kwarg = 'quotation_id'
    template_name = 'sales_distribution/quotation_print_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quotation = self.get_object()

        # Get quotation line items with unit info
        line_items = SdCustQuotationDetails.objects.filter(mid=quotation).select_related('unit')

        # Get customer info
        try:
            customer = SdCustMaster.objects.get(customerid=quotation.customerid)
        except SdCustMaster.DoesNotExist:
            customer = None

        # Get enquiry info if linked
        enquiry = None
        try:
            # Find enquiry by matching customer and approximate date/ID
            enquiry = SdCustEnquiryMaster.objects.filter(customerid=quotation.customerid).first()
        except SdCustEnquiryMaster.DoesNotExist:
            pass

        # Get financial year name
        finyear_name = None
        try:
            finyear = FinancialYear.objects.get(pk=quotation.finyearid)
            finyear_name = finyear.finyear
        except FinancialYear.DoesNotExist:
            finyear_name = str(quotation.finyearid)

        # Get employee/user name
        employee_name = None
        try:
            user = User.objects.get(pk=int(quotation.sessionid))
            employee_name = user.username
        except (User.DoesNotExist, ValueError):
            employee_name = quotation.sessionid

        # Calculate line item totals
        subtotal = 0
        for item in line_items:
            line_total = item.totalqty * item.rate
            if item.discount:
                line_total -= (line_total * item.discount / 100)
            subtotal += line_total
            item.line_total = line_total

        # Handle charges - quotation has type fields (1=percentage, 0=fixed)
        pf_amount = 0
        if quotation.pf:
            if quotation.pftype == 1:  # Percentage
                pf_amount = subtotal * quotation.pf / 100
            else:  # Fixed amount
                pf_amount = quotation.pf

        freight_amount = 0
        if quotation.freight:
            if quotation.freighttype == 1:  # Percentage
                freight_amount = subtotal * quotation.freight / 100
            else:  # Fixed amount
                freight_amount = quotation.freight

        octroi_amount = 0
        if quotation.octroi:
            if quotation.octroitype == 1:  # Percentage
                octroi_amount = subtotal * quotation.octroi / 100
            else:  # Fixed amount
                octroi_amount = quotation.octroi

        other_charges = 0
        if quotation.othercharges:
            if quotation.otherchargestype == 1:  # Percentage
                other_charges = subtotal * quotation.othercharges / 100
            else:  # Fixed amount
                other_charges = quotation.othercharges

        insurance = quotation.insurance if quotation.insurance else 0

        # Calculate tax amounts
        vat_cst_amount = 0
        if quotation.vatcst:
            vat_cst_amount = subtotal * quotation.vatcst / 100

        excise_amount = 0
        if quotation.excise:
            excise_amount = subtotal * quotation.excise / 100

        grand_total = subtotal + pf_amount + freight_amount + other_charges + insurance + octroi_amount + vat_cst_amount + excise_amount

        # Company info from settings
        context.update({
            'quotation': quotation,
            'line_items': line_items,
            'customer': customer,
            'enquiry': enquiry,
            'finyear_name': finyear_name,
            'employee_name': employee_name,
            'subtotal': subtotal,
            'pf_amount': pf_amount,
            'freight_amount': freight_amount,
            'octroi_amount': octroi_amount,
            'other_charges': other_charges,
            'insurance': insurance,
            'vat_cst_amount': vat_cst_amount,
            'excise_amount': excise_amount,
            'grand_total': grand_total,
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
        quotation_no = context['quotation'].quotationno if context['quotation'].quotationno else f'QUOT_{context["quotation"].id}'
        filename = f'Quotation_{quotation_no}.pdf'

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response



