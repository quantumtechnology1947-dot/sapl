"""
Human Resource Gate Pass Management Views
Handles employee gate pass requests and approvals
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
from ..models import TblgatePass, TblgatepassDetails, TblgatepassReason, TblhrOfficestaff
from ..forms import GatePassForm


class GatePassListView(BaseListViewMixin, ListView):
    """
    Display list of gate passes with search and filters.
    Converted from: aspnet/Module/HR/Transactions/GatePass.aspx
    Shows all employee gate pass requests with status.
    """
    model = TblgatePass
    template_name = 'human_resource/transactions/gatepass_list.html'
    context_object_name = 'gatepasses'
    paginate_by = 20
    search_fields = ['empid', 'gpno']
    partial_template_name = 'human_resource/partials/gatepass_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search by employee ID or gate pass number
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(empid__icontains=search_query) |
                models.Q(gpno__icontains=search_query)
            )

        # Filter by authorization status
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'authorized':
            queryset = queryset.filter(authorize=1)
        elif status_filter == 'pending':
            queryset = queryset.filter(models.Q(authorize=0) | models.Q(authorize__isnull=True))

        # Filter by date range
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        if from_date:
            queryset = queryset.filter(sysdate__gte=from_date)
        if to_date:
            queryset = queryset.filter(sysdate__lte=to_date)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Enhance gate passes with employee and details information
        gatepass_list = []
        for gatepass in context['gatepasses']:
            try:
                employee = TblhrOfficestaff.objects.get(empid=gatepass.empid)
            except TblhrOfficestaff.DoesNotExist:
                employee = None

            # Get gate pass details
            details = TblgatepassDetails.objects.filter(mid=gatepass.id).first()

            gatepass_list.append({
                'gatepass': gatepass,
                'employee': employee,
                'details': details,
                'is_authorized': gatepass.authorize == 1
            })

        context['gatepass_list'] = gatepass_list
        context['status_filter'] = self.request.GET.get('status', '')

        return context


class GatePassCreateView(BaseCreateViewMixin, CreateView):
    """
    Create new gate pass request.
    Converted from: aspnet/Module/HR/Transactions/GatePass.aspx (Create Mode)
    Creates gate pass with details and reason.
    """
    model = TblgatePass
    form_class = GatePassForm
    template_name = 'human_resource/transactions/gatepass_form.html'
    partial_template_name = 'human_resource/partials/gatepass_form.html'
    success_message = 'Gate pass created successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get list of employees
        employees = TblhrOfficestaff.objects.filter(
            compid=self.get_compid()
        ).order_by('employeename')
        context['employees'] = employees

        # Get gate pass reasons
        reasons = TblgatepassReason.objects.all()
        context['reasons'] = reasons

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

        # Generate gate pass number if not provided
        if not form.instance.gpno:
            # Get the last gate pass number
            last_gatepass = TblgatePass.objects.filter(
                compid=self.get_compid(),
                finyearid=self.get_finyearid()
            ).order_by('-id').first()

            if last_gatepass and last_gatepass.gpno:
                try:
                    last_num = int(last_gatepass.gpno.replace('GP', ''))
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1

            form.instance.gpno = f'GP{new_num:05d}'

        # Set authorization to pending by default
        if form.instance.authorize is None:
            form.instance.authorize = 0

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Gate pass {form.instance.gpno} created successfully. Pending authorization.'
        )

        return response

    def get_success_url(self):
        return reverse_lazy('human_resource:gatepass-detail', kwargs={'pk': self.object.pk})


class GatePassUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Update existing gate pass or authorize it.
    Converted from: aspnet/Module/HR/Transactions/GatePass.aspx (Edit/Authorize Mode)
    """
    model = TblgatePass
    form_class = GatePassForm
    template_name = 'human_resource/transactions/gatepass_form.html'
    partial_template_name = 'human_resource/partials/gatepass_form.html'
    success_message = 'Gate pass updated successfully'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Get gate pass details
        details = TblgatepassDetails.objects.filter(mid=self.object.id).first()
        context['details'] = details

        # Get gate pass reasons
        reasons = TblgatepassReason.objects.all()
        context['reasons'] = reasons

        # Authorization status
        context['is_authorized'] = self.object.authorize == 1

        return context

    def form_valid(self, form):
        # Update system date and time
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')

        # If authorizing, set authorization details
        if 'authorize' in self.request.POST and self.request.POST['authorize'] == '1':
            if form.instance.authorize != 1:
                form.instance.authorize = 1
                form.instance.authorizedby = str(self.request.user.username)
                form.instance.authorizedate = now.strftime('%d-%m-%Y')
                form.instance.authorizetime = now.strftime('%H:%M:%S')
                messages.success(self.request, f'Gate pass {form.instance.gpno} authorized successfully.')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('human_resource:gatepass-detail', kwargs={'pk': self.object.pk})


class GatePassDetailView(BaseDetailViewMixin, DetailView):
    """
    Display detailed gate pass information.
    Converted from: aspnet/Module/HR/Transactions/GatePass.aspx (View Mode)
    Shows complete gate pass details including authorization status.
    """
    model = TblgatePass
    template_name = 'human_resource/transactions/gatepass_detail.html'
    context_object_name = 'gatepass'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get employee information
        try:
            employee = TblhrOfficestaff.objects.get(empid=self.object.empid)
            context['employee'] = employee
        except TblhrOfficestaff.DoesNotExist:
            context['employee'] = None

        # Get gate pass details
        details = TblgatepassDetails.objects.filter(mid=self.object.id).first()
        context['details'] = details

        # Get reason name if details exist
        if details and details.reason:
            try:
                reason = TblgatepassReason.objects.get(id=details.reason)
                context['reason_name'] = reason.reason
            except TblgatepassReason.DoesNotExist:
                context['reason_name'] = details.reason

        # Authorization status
        context['is_authorized'] = self.object.authorize == 1
        context['is_pending'] = self.object.authorize != 1

        return context


class GatePassDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Delete gate pass record.
    Converted from: aspnet/Module/HR/Transactions/GatePass.aspx (Delete)
    Also deletes related gate pass details.
    """
    model = TblgatePass
    success_url = reverse_lazy('human_resource:gatepass-list')
    template_name = 'human_resource/transactions/gatepass_confirm_delete.html'

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

        # Check if gate pass is authorized
        if self.object.authorize == 1:
            messages.error(
                request,
                f'Cannot delete authorized gate pass {self.object.gpno}. '
                'Please contact administrator.'
            )
            return redirect('human_resource:gatepass-detail', pk=self.object.pk)

        # Delete related gate pass details
        TblgatepassDetails.objects.filter(mid=self.object.id).delete()

        messages.success(request, f'Gate pass {self.object.gpno} deleted successfully.')

        return super().delete(request, *args, **kwargs)
