"""
Policy Document Views
Converted from ASP.NET Module/Accounts/Transactions/ACC_POLICY.aspx
"""

from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from datetime import datetime

from core.mixins import (
    BaseListViewMixin, BaseCreateViewMixin,
    CompanyFinancialYearMixin, AuditMixin
)
from ...models import AccPolicy
from ...forms import PolicyForm


class PolicyListView(BaseListViewMixin, ListView):
    """
    Display list of policy documents with download links.

    Converted from: ACC_POLICY.aspx (GridView section)
    """
    model = AccPolicy
    template_name = 'accounts/transactions/policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20
    search_fields = ['cvname', 'cvfilename']
    partial_template_name = 'accounts/transactions/partials/policy_list_partial.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PolicyForm()
        return context


class PolicyUploadView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """
    Upload new policy document.

    Converted from: ACC_POLICY.aspx (Btnsubmit_Click and Save methods)
    Handles file upload with metadata storage
    """
    model = AccPolicy
    form_class = PolicyForm
    template_name = 'accounts/transactions/policy_form.html'
    success_url = reverse_lazy('accounts:policy-list')
    success_message = 'Policy document uploaded successfully'
    partial_template_name = 'accounts/transactions/partials/policy_row.html'

    def form_valid(self, form):
        """Process file upload and save to database."""
        # Get uploaded file
        uploaded_file = self.request.FILES.get('file_upload')

        if uploaded_file:
            # Create policy object
            policy = form.save(commit=False)

            # Set file metadata
            policy.cvfilename = uploaded_file.name
            policy.cvsize = str(uploaded_file.size)
            policy.cvcontenttype = uploaded_file.content_type

            # Read file data
            policy.cvdata = uploaded_file.read()

            # Set audit fields (AuditMixin will handle sysdate, systime, etc.)
            # But we need to ensure they're populated
            policy.sysdate = datetime.now().strftime('%d-%m-%Y')
            policy.systime = datetime.now().strftime('%H:%M:%S')
            policy.sessionid = str(self.request.user.id)
            policy.compid = self.request.session.get('compid', 1)
            policy.finyearid = self.request.session.get('finyearid', 1)

            policy.save()

            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(self.success_url)
        else:
            form.add_error('file_upload', 'Please select a file to upload')
            return self.form_invalid(form)


class PolicyDownloadView(LoginRequiredMixin, View):
    """
    Download policy document.

    Converted from: ACC_POLICY.aspx.cs (DownloadFile method)
    Serves the binary file data with appropriate content type
    """

    def get(self, request, pk):
        """Download the policy document by ID."""
        policy = get_object_or_404(AccPolicy, id=pk)

        # Create HTTP response with file data
        response = HttpResponse(
            policy.cvdata,
            content_type=policy.cvcontenttype or 'application/octet-stream'
        )

        # Set download headers
        response['Content-Disposition'] = f'attachment; filename="{policy.cvfilename}"'
        response['Content-Length'] = policy.cvsize

        return response
