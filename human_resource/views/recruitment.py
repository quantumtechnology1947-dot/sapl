"""
Human Resource Recruitment Views
Handles offer letter generation and management
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models
from datetime import datetime

from core.mixins import (
    BaseListViewMixin, BaseCreateViewMixin, BaseUpdateViewMixin,
    BaseDeleteViewMixin, BaseDetailViewMixin
)
from ..models import TblhrOfferMaster, TblhrOfferAccessories, TblhrOfficestaff
from ..forms import OfferLetterForm


class OfferLetterListView(BaseListViewMixin, ListView):
    """
    Display list of offer letters with search and filters.
    Converted from: aspnet/Module/HR/Transactions/OfferMaster.aspx
    Shows all offer letters with employee information.
    """
    model = TblhrOfferMaster
    template_name = 'human_resource/transactions/offer_letter_list.html'
    context_object_name = 'offers'
    paginate_by = 20
    search_fields = ['empid', 'empname', 'designation']
    partial_template_name = 'human_resource/partials/offer_letter_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search by employee name, ID, or designation
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(empname__icontains=search_query) |
                models.Q(empid__icontains=search_query) |
                models.Q(designation__icontains=search_query)
            )

        # Filter by status (active/inactive)
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(active=1)
        elif status_filter == 'inactive':
            queryset = queryset.filter(models.Q(active=0) | models.Q(active__isnull=True))

        return queryset.order_by('-offerid')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Enhance offers with salary calculations
        offer_list = []
        for offer in context['offers']:
            # Calculate salary components from accessories
            accessories = TblhrOfferAccessories.objects.filter(mid=offer.offerid)

            gross_total = sum(
                (acc.qty or 0) * (acc.amount or 0)
                for acc in accessories if acc.includesin == 1
            )
            ctc_total = sum(
                (acc.qty or 0) * (acc.amount or 0)
                for acc in accessories if acc.includesin == 2
            )
            net_total = sum(
                (acc.qty or 0) * (acc.amount or 0)
                for acc in accessories if acc.includesin == 3
            )

            offer_list.append({
                'offer': offer,
                'gross_total': gross_total,
                'ctc_total': ctc_total,
                'net_total': net_total
            })

        context['offer_list'] = offer_list
        context['status_filter'] = self.request.GET.get('status', '')

        return context


class OfferLetterCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new offer letter.
    Converted from: aspnet/Module/HR/Transactions/OfferMaster.aspx (Create Mode)
    Creates offer letter with salary components and accessories.
    """
    model = TblhrOfferMaster
    form_class = OfferLetterForm
    template_name = 'human_resource/transactions/offer_letter_form.html'
    partial_template_name = 'human_resource/partials/offer_letter_form.html'
    success_message = 'Offer letter created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get list of employees without offer letters
        employees_with_offers = TblhrOfferMaster.objects.filter(
            compid=self.get_compid()
        ).values_list('empid', flat=True)

        employees = TblhrOfficestaff.objects.filter(
            compid=self.get_compid()
        ).exclude(
            empid__in=employees_with_offers
        ).order_by('employeename')

        context['employees'] = employees

        return context

    def form_valid(self, form):
        # Set company and financial year from session
        form.instance.compid = self.get_compid()
        form.instance.finyearid = self.get_finyearid()
        form.instance.sessionid = str(self.request.user.id)

        # Set system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        # Set active flag to 1 by default
        if form.instance.active is None:
            form.instance.active = 1

        response = super().form_valid(form)

        # Update employee record with offer ID
        try:
            employee = TblhrOfficestaff.objects.get(empid=form.instance.empid)
            employee.offerid = self.object.offerid
            employee.save()
        except TblhrOfficestaff.DoesNotExist:
            pass

        messages.success(
            self.request,
            f'Offer letter created successfully for {form.instance.empname}. '
            'You can now add salary components and accessories.'
        )

        return response

    def get_success_url(self):
        return reverse_lazy('human_resource:offer-letter-detail', kwargs={'pk': self.object.pk})


class OfferLetterUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing offer letter.
    Converted from: aspnet/Module/HR/Transactions/OfferMaster.aspx (Edit Mode)
    """
    model = TblhrOfferMaster
    form_class = OfferLetterForm
    template_name = 'human_resource/transactions/offer_letter_form.html'
    partial_template_name = 'human_resource/partials/offer_letter_form.html'
    success_message = 'Offer letter updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Get offer accessories
        accessories = TblhrOfferAccessories.objects.filter(mid=self.object.offerid)
        context['accessories'] = accessories

        # Calculate salary components
        gross_total = sum(
            (acc.qty or 0) * (acc.amount or 0)
            for acc in accessories if acc.includesin == 1
        )
        ctc_total = sum(
            (acc.qty or 0) * (acc.amount or 0)
            for acc in accessories if acc.includesin == 2
        )
        net_total = sum(
            (acc.qty or 0) * (acc.amount or 0)
            for acc in accessories if acc.includesin == 3
        )

        context['gross_total'] = gross_total
        context['ctc_total'] = ctc_total
        context['net_total'] = net_total

        return context

    def form_valid(self, form):
        # Update system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('human_resource:offer-letter-detail', kwargs={'pk': self.object.pk})


class OfferLetterDetailView(BaseDetailViewMixin, DetailView):
    """
    Display detailed offer letter information.
    Converted from: aspnet/Module/HR/Transactions/OfferMaster.aspx (View Mode)
    Shows complete offer details including salary breakdown and accessories.
    """
    model = TblhrOfferMaster
    template_name = 'human_resource/transactions/offer_letter_detail.html'
    context_object_name = 'offer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Get offer accessories
        accessories = TblhrOfferAccessories.objects.filter(mid=self.object.offerid)

        # Group accessories by type
        gross_accessories = []
        ctc_accessories = []
        net_accessories = []

        gross_total = 0
        ctc_total = 0
        net_total = 0

        for acc in accessories:
            total = (acc.qty or 0) * (acc.amount or 0)

            if acc.includesin == 1:  # Gross
                gross_accessories.append({'accessory': acc, 'total': total})
                gross_total += total
            elif acc.includesin == 2:  # CTC
                ctc_accessories.append({'accessory': acc, 'total': total})
                ctc_total += total
            elif acc.includesin == 3:  # Net
                net_accessories.append({'accessory': acc, 'total': total})
                net_total += total

        context['gross_accessories'] = gross_accessories
        context['ctc_accessories'] = ctc_accessories
        context['net_accessories'] = net_accessories
        context['gross_total'] = gross_total
        context['ctc_total'] = ctc_total
        context['net_total'] = net_total

        return context


class OfferLetterDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete offer letter record.
    Converted from: aspnet/Module/HR/Transactions/OfferMaster.aspx (Delete)
    Also removes offer ID from employee record.
    """
    model = TblhrOfferMaster
    success_url = reverse_lazy('human_resource:offer-letter-list')
    template_name = 'human_resource/transactions/offer_letter_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Remove offer ID from employee record
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            employee.offerid = None
            employee.save()
        except TblhrOfficestaff.DoesNotExist:
            pass

        # Delete related accessories
        TblhrOfferAccessories.objects.filter(mid=self.object.offerid).delete()

        messages.success(
            request,
            f'Offer letter for {self.object.empname} deleted successfully.'
        )

        return super().delete(request, *args, **kwargs)
