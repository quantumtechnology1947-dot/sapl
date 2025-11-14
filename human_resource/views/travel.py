"""
Human Resource Travel Management Views
Handles tour intimation requests and approvals
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
from ..models import TblaccTourintimationMaster, TblhrOfficestaff
from ..forms import TourIntimationForm


class TourIntimationListView(BaseListViewMixin, ListView):
    """
    Display list of tour intimations with search and filters.
    Converted from: aspnet/Module/HR/Transactions/TourIntimation.aspx
    Shows all employee tour intimation requests with status.
    """
    model = TblaccTourintimationMaster
    template_name = 'human_resource/transactions/tour_intimation_list.html'
    context_object_name = 'tours'
    paginate_by = 20
    search_fields = ['empid', 'tourplace', 'tourpurpose']
    partial_template_name = 'human_resource/partials/tour_intimation_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search by employee ID, place, or purpose
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(empid__icontains=search_query) |
                models.Q(tourplace__icontains=search_query) |
                models.Q(tourpurpose__icontains=search_query)
            )

        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'approved':
            queryset = queryset.filter(approve=1)
        elif status_filter == 'pending':
            queryset = queryset.filter(models.Q(approve=0) | models.Q(approve__isnull=True))
        elif status_filter == 'rejected':
            queryset = queryset.filter(approve=2)

        # Filter by tour type (Local/Outstation)
        tour_type = self.request.GET.get('tour_type', '')
        if tour_type:
            queryset = queryset.filter(tourtype=tour_type)

        # Filter by date range
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        if from_date:
            queryset = queryset.filter(fromdate__gte=from_date)
        if to_date:
            queryset = queryset.filter(todate__lte=to_date)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Enhance tours with employee information
        tour_list = []
        for tour in context['tours']:
            try:
                employee = TblhrOfficestaff.objects.get(empid=tour.empid)
            except TblhrOfficestaff.DoesNotExist:
                employee = None

            # Determine status
            status = 'Pending'
            status_class = 'warning'
            if tour.approve == 1:
                status = 'Approved'
                status_class = 'success'
            elif tour.approve == 2:
                status = 'Rejected'
                status_class = 'danger'

            tour_list.append({
                'tour': tour,
                'employee': employee,
                'status': status,
                'status_class': status_class
            })

        context['tour_list'] = tour_list
        context['status_filter'] = self.request.GET.get('status', '')
        context['tour_type'] = self.request.GET.get('tour_type', '')

        return context


class TourIntimationCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new tour intimation request.
    Converted from: aspnet/Module/HR/Transactions/TourIntimation.aspx (Create Mode)
    Creates tour intimation with travel details.
    """
    model = TblaccTourintimationMaster
    form_class = TourIntimationForm
    template_name = 'human_resource/transactions/tour_intimation_form.html'
    partial_template_name = 'human_resource/partials/tour_intimation_form.html'
    success_message = 'Tour intimation created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get list of employees
        employees = TblhrOfficestaff.objects.filter(
            compid=self.get_compid()
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

        # Set approval status to pending by default
        if form.instance.approve is None:
            form.instance.approve = 0

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Tour intimation created successfully for {form.instance.empid}. Pending approval.'
        )

        return response

    def get_success_url(self):
        return reverse_lazy('human_resource:tour-intimation-detail', kwargs={'pk': self.object.pk})


class TourIntimationUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing tour intimation or approve/reject it.
    Converted from: aspnet/Module/HR/Transactions/TourIntimation.aspx (Edit/Approve Mode)
    """
    model = TblaccTourintimationMaster
    form_class = TourIntimationForm
    template_name = 'human_resource/transactions/tour_intimation_form.html'
    partial_template_name = 'human_resource/partials/tour_intimation_form.html'
    success_message = 'Tour intimation updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Approval status
        context['is_approved'] = self.object.approve == 1
        context['is_rejected'] = self.object.approve == 2
        context['is_pending'] = self.object.approve == 0 or self.object.approve is None

        return context

    def form_valid(self, form):
        # Update system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        # Handle approval/rejection
        if 'approve' in self.request.POST:
            action = self.request.POST['approve']

            if action == '1' and form.instance.approve != 1:
                # Approve
                form.instance.approve = 1
                form.instance.approveby = str(self.request.user.username)
                form.instance.approvedate = now.strftime('%d-%m-%Y')
                form.instance.approvetime = now.strftime('%H:%M:%S')
                messages.success(
                    self.request,
                    f'Tour intimation for {form.instance.empid} approved successfully.'
                )
            elif action == '2' and form.instance.approve != 2:
                # Reject
                form.instance.approve = 2
                form.instance.approveby = str(self.request.user.username)
                form.instance.approvedate = now.strftime('%d-%m-%Y')
                form.instance.approvetime = now.strftime('%H:%M:%S')
                messages.warning(
                    self.request,
                    f'Tour intimation for {form.instance.empid} rejected.'
                )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('human_resource:tour-intimation-detail', kwargs={'pk': self.object.pk})


class TourIntimationDetailView(BaseDetailViewMixin, DetailView):
    """
    Display detailed tour intimation information.
    Converted from: aspnet/Module/HR/Transactions/TourIntimation.aspx (View Mode)
    Shows complete tour details including approval status.
    """
    model = TblaccTourintimationMaster
    template_name = 'human_resource/transactions/tour_intimation_detail.html'
    context_object_name = 'tour'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Approval status
        if self.object.approve == 1:
            context['status'] = 'Approved'
            context['status_class'] = 'success'
        elif self.object.approve == 2:
            context['status'] = 'Rejected'
            context['status_class'] = 'danger'
        else:
            context['status'] = 'Pending'
            context['status_class'] = 'warning'

        context['is_approved'] = self.object.approve == 1
        context['is_rejected'] = self.object.approve == 2
        context['is_pending'] = self.object.approve == 0 or self.object.approve is None

        # Calculate tour duration
        if self.object.fromdate and self.object.todate:
            try:
                from_date = datetime.strptime(self.object.fromdate, '%d-%m-%Y')
                to_date = datetime.strptime(self.object.todate, '%d-%m-%Y')
                duration = (to_date - from_date).days + 1
                context['tour_duration'] = duration
            except:
                context['tour_duration'] = None

        return context


class TourIntimationDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete tour intimation record.
    Converted from: aspnet/Module/HR/Transactions/TourIntimation.aspx (Delete)
    Only allows deletion of pending tour intimations.
    """
    model = TblaccTourintimationMaster
    success_url = reverse_lazy('human_resource:tour-intimation-list')
    template_name = 'human_resource/transactions/tour_intimation_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check if tour intimation is approved
        if self.object.approve == 1:
            messages.error(
                request,
                f'Cannot delete approved tour intimation for {self.object.empid}. '
                'Please contact administrator.'
            )
            return redirect('human_resource:tour-intimation-detail', pk=self.object.pk)

        messages.success(
            request,
            f'Tour intimation for {self.object.empid} deleted successfully.'
        )

        return super().delete(request, *args, **kwargs)
