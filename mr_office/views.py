"""
MR Office Module Views
Converted from: aaspnet/Module/MROffice/Transactions/MROffice.aspx

Document/File Management System for ERP modules
Handles file upload, download, viewing, and deletion (ISO document management)
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from datetime import datetime
import os

from core.mixins import CompanyFinancialYearMixin, HTMXResponseMixin, SearchMixin
from .models import Tblmroffice
from .forms import MROfficeDocumentForm


# ============================================================
# Dashboard
# ============================================================

class MROfficeDashboardView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """MR Office Dashboard with statistics"""
    template_name = 'mr_office/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()

        # Total documents - filter only by company (not financial year)
        all_docs = Tblmroffice.objects.filter(compid=compid)
        context['total_documents'] = all_docs.count()

        # Documents by module
        module_stats = []
        for module_id, module_name in Tblmroffice.MODULE_CHOICES:
            count = all_docs.filter(formodule=module_id).count()
            if count > 0:
                module_stats.append({
                    'id': module_id,
                    'name': module_name,
                    'count': count
                })
        context['module_stats'] = module_stats

        # Recent documents
        context['recent_documents'] = all_docs.order_by('-id')[:10]

        # Total storage used (approximate)
        total_size = 0
        for doc in all_docs:
            if doc.size:
                try:
                    total_size += int(doc.size)
                except (ValueError, TypeError):
                    pass

        # Convert to MB
        context['total_storage_mb'] = round(total_size / (1024 * 1024), 2)

        return context


# ============================================================
# Document List
# ============================================================

class DocumentListView(LoginRequiredMixin, CompanyFinancialYearMixin, HTMXResponseMixin, SearchMixin, ListView):
    """
    List all documents (MR Office - ISO)
    Converted from: aaspnet/Module/MROffice/Transactions/MROffice.aspx (GridView)
    """
    model = Tblmroffice
    template_name = 'mr_office/document_list.html'
    partial_template_name = 'mr_office/partials/document_table.html'
    context_object_name = 'documents'
    paginate_by = 20
    search_fields = ['filename', 'format']

    def get_queryset(self):
        # Get base queryset filtered by company (super() handles CompanyFinancialYearMixin)
        queryset = super().get_queryset().order_by('formodule', '-id')

        # Module filter
        module = self.request.GET.get('module')
        if module:
            try:
                queryset = queryset.filter(formodule=int(module))
            except (ValueError, TypeError):
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = Tblmroffice.MODULE_CHOICES
        context['selected_module'] = self.request.GET.get('module', '')
        return context


# ============================================================
# Document Create (Add) - Inline in List View
# ============================================================

class DocumentCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    Create new document (HTMX endpoint)
    Converted from: aaspnet/Module/MROffice/Transactions/MROffice.aspx (GridView Add command)
    """

    def post(self, request):
        form = MROfficeDocumentForm(request.POST, request.FILES)

        if form.is_valid():
            # Save with audit fields
            document = form.save(commit=False, request=request)
            document.save()

            messages.success(request, f'Document "{document.filename}" uploaded successfully')

            # Return redirect to list page (HTMX will handle)
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse_lazy('mr_office:document-list')
                return response
            else:
                from django.shortcuts import redirect
                return redirect('mr_office:document-list')
        else:
            messages.error(request, 'Please correct the errors below')
            # Re-render form with errors
            from django.shortcuts import render
            return render(request, 'mr_office/document_list.html', {
                'form': form,
                'documents': Tblmroffice.objects.filter(compid=self.get_compid()).order_by('-id')[:20],
                'modules': Tblmroffice.MODULE_CHOICES
            })


# ============================================================
# Document Detail
# ============================================================

class DocumentDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """View document details"""
    model = Tblmroffice
    template_name = 'mr_office/document_detail.html'
    context_object_name = 'document'


# ============================================================
# Document Download
# ============================================================

class DocumentDownloadView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    Download document file
    Converted from: aaspnet/Controls/DownloadFile.aspx
    """
    model = Tblmroffice

    def render_to_response(self, context, **response_kwargs):
        document = self.object

        if not document.data:
            messages.error(self.request, 'Document file data not found')
            return HttpResponse("File data not found", status=404)

        # Create HTTP response with file data
        response = HttpResponse(
            bytes(document.data),
            content_type=document.contenttype or 'application/octet-stream'
        )

        # Set filename in Content-Disposition header
        filename = document.filename or f"document_{document.id}"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response


# ============================================================
# Document Delete
# ============================================================

class DocumentDeleteView(LoginRequiredMixin, CompanyFinancialYearMixin, HTMXResponseMixin, DeleteView):
    """
    Delete document
    Converted from: aaspnet/Module/MROffice/Transactions/MROffice.aspx (Delete command)
    """
    model = Tblmroffice
    success_url = reverse_lazy('mr_office:document-list')

    def delete(self, request, *args, **kwargs):
        document = self.get_object()
        filename = document.filename
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Document "{filename}" deleted successfully')
        return result


# ============================================================
# Reports
# ============================================================

class DocumentStorageReportView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """Document Storage Report by Module"""
    template_name = 'mr_office/reports/storage_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()

        # Get all documents (filter only by company)
        all_docs = Tblmroffice.objects.filter(compid=compid)

        # Calculate storage by module
        module_storage = []
        for module_id, module_name in Tblmroffice.MODULE_CHOICES:
            docs = all_docs.filter(formodule=module_id)
            doc_count = docs.count()

            total_size = 0
            for doc in docs:
                if doc.size:
                    try:
                        total_size += int(doc.size)
                    except (ValueError, TypeError):
                        pass

            if doc_count > 0:
                module_storage.append({
                    'module': module_name,
                    'count': doc_count,
                    'size_bytes': total_size,
                    'size_mb': round(total_size / (1024 * 1024), 2)
                })

        context['module_storage'] = sorted(module_storage, key=lambda x: x['size_bytes'], reverse=True)

        # Grand totals
        context['total_documents'] = sum(m['count'] for m in module_storage)
        context['total_size_mb'] = round(sum(m['size_bytes'] for m in module_storage) / (1024 * 1024), 2)

        return context


class DocumentListByModuleView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """List documents grouped by module"""
    template_name = 'mr_office/reports/by_module.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()

        # Get all documents (filter only by company)
        all_docs = Tblmroffice.objects.filter(compid=compid)

        # Group by module
        module_data = []
        for module_id, module_name in Tblmroffice.MODULE_CHOICES:
            docs = all_docs.filter(formodule=module_id).order_by('-id')
            if docs.exists():
                module_data.append({
                    'module': module_name,
                    'documents': docs
                })

        context['module_data'] = module_data

        return context
