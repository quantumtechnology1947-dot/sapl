"""
Material Return Quality Note (MRQN) Views

Workflow for MRQN creation and management:
1. Search MRN records
2. Create MRQN based on selected MRN
3. Manage existing MRQNs (CRUD)
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from datetime import datetime

from .base import QualityControlBaseMixin
from quality_control.models import TblqcMaterialreturnqualityMaster
from quality_control.forms import MaterialReturnQualityNoteForm, MaterialReturnQualityNoteDetailFormSet
from quality_control.services import MRQNSearchService


class MaterialReturnQualityNoteListView(QualityControlBaseMixin, ListView):
    """List all Material Return Quality Notes"""
    model = TblqcMaterialreturnqualityMaster
    template_name = 'quality_control/mrqn/list_new.html'
    context_object_name = 'mrqns'
    paginate_by = 20

    def get_queryset(self):
        from sys_admin.models import TblfinancialMaster
        
        queryset = TblqcMaterialreturnqualityMaster.objects.filter(
            compid=self.get_compid()
        ).order_by('-id')

        # Add search filters
        search_by = self.request.GET.get('search_by', '0')
        search_value = self.request.GET.get('search_value', '').strip()

        if search_value:
            if search_by == '0':  # MRN No
                queryset = queryset.filter(mrnno__icontains=search_value)
            elif search_by == '1':  # MRQN No
                queryset = queryset.filter(mrqnno__icontains=search_value)

        # Enrich with financial year names
        mrqns = list(queryset)
        for mrqn in mrqns:
            try:
                finyear = TblfinancialMaster.objects.get(finyearid=mrqn.finyearid)
                mrqn.finyear_name = finyear.finyear
            except:
                mrqn.finyear_name = str(mrqn.finyearid)

        return mrqns

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search_value', '')
        return context


class MaterialReturnQualityNoteCreateView(QualityControlBaseMixin, TemplateView):
    """Search and select MRN for MRQN creation"""
    template_name = 'quality_control/mrqn/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get search parameters
        search_by = self.request.GET.get('search_by', '0')
        search_value = self.request.GET.get('search_value', '')

        context['search_by'] = search_by
        context['search_value'] = search_value

        # Search MRN records using service
        if search_value or not search_value:  # Always load records
            mrn_records = MRQNSearchService.search_mrn_records(
                self.get_compid(),
                search_by,
                search_value
            )[:20]  # Limit results

            # Add computed fields for template
            for mrn in mrn_records:
                mrn.finyear_name = f"FY-{mrn.finyearid}"
                mrn.generated_by = "System User"

            context['mrn_records'] = mrn_records

        return context


class MaterialReturnQualityNoteCreateDetailsView(QualityControlBaseMixin, CreateView):
    """Create MRQN details based on selected MRN"""
    model = TblqcMaterialreturnqualityMaster
    form_class = MaterialReturnQualityNoteForm
    template_name = 'quality_control/mrqn/details_form.html'
    success_url = reverse_lazy('quality_control:mrqn-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get MRN details from URL parameters
        mrn_id = self.request.GET.get('mrn_id')
        mrn_no = self.request.GET.get('mrn_no')
        fy_id = self.request.GET.get('fy_id')

        context['mrn_id'] = mrn_id
        context['mrn_no'] = mrn_no
        context['fy_id'] = fy_id

        if self.request.POST:
            context['details'] = MaterialReturnQualityNoteDetailFormSet(self.request.POST)
        else:
            context['details'] = MaterialReturnQualityNoteDetailFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        details = context['details']

        # Set session metadata
        for field, value in self.get_session_metadata().items():
            setattr(form.instance, field, value)

        # Set MRN details from URL parameters
        form.instance.mrnid = self.request.GET.get('mrn_id')
        form.instance.mrnno = self.request.GET.get('mrn_no')

        if details.is_valid():
            self.object = form.save()
            details.instance = self.object
            details.save()
            messages.success(self.request, f'MRQN {self.object.mrqnno} created successfully')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class MaterialReturnQualityNoteUpdateView(QualityControlBaseMixin, UpdateView):
    """Update existing Material Return Quality Note"""
    model = TblqcMaterialreturnqualityMaster
    form_class = MaterialReturnQualityNoteForm
    template_name = 'quality_control/mrqn/form.html'
    success_url = reverse_lazy('quality_control:mrqn-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['details'] = MaterialReturnQualityNoteDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['details'] = MaterialReturnQualityNoteDetailFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        details = context['details']

        if details.is_valid():
            self.object = form.save()
            details.instance = self.object
            details.save()
            messages.success(self.request, f'MRQN {self.object.mrqnno} updated successfully')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class MaterialReturnQualityNoteDetailView(QualityControlBaseMixin, DetailView):
    """View Material Return Quality Note details"""
    model = TblqcMaterialreturnqualityMaster
    template_name = 'quality_control/mrqn/detail.html'
    context_object_name = 'mrqn'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.all()
        return context


class MaterialReturnQualityNoteDeleteView(QualityControlBaseMixin, DeleteView):
    """Delete Material Return Quality Note"""
    model = TblqcMaterialreturnqualityMaster
    template_name = 'quality_control/mrqn/delete.html'
    success_url = reverse_lazy('quality_control:mrqn-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'MRQN deleted successfully')
        return super().delete(request, *args, **kwargs)


class MaterialReturnQualityNotePrintView(QualityControlBaseMixin, DetailView):
    """Print Material Return Quality Note"""
    model = TblqcMaterialreturnqualityMaster
    template_name = 'quality_control/mrqn/print.html'
    context_object_name = 'mrqn'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.all()
        context['print_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return context
