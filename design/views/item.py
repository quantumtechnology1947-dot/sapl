"""
Design Item Master Views
Converted from: aspnet/Module/Design/Masters/ItemMaster_Edit.aspx, ItemMasterNew.aspx
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
from django.db.models import Q

from ..models import TbldgItemMaster, TbldgCategoryMaster
from ..forms import ItemMasterForm
from sys_admin.models import UnitMaster


class ItemMasterListView(LoginRequiredMixin, ListView):
    """
    Display paginated list of items with search functionality.
    Converted from: aspnet/Module/Design/Masters/ItemMaster_Edit.aspx
    """
    model = TbldgItemMaster
    template_name = 'design/item_list.html'
    context_object_name = 'items'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter items based on search criteria."""
        queryset = TbldgItemMaster.objects.all().order_by('-id')
        
        # Search by item code
        search_itemcode = self.request.GET.get('search_itemcode', '').strip()
        if search_itemcode:
            queryset = queryset.filter(itemcode__icontains=search_itemcode)
        
        # Search by description
        search_desc = self.request.GET.get('search_desc', '').strip()
        if search_desc:
            queryset = queryset.filter(manfdesc__icontains=search_desc)
        
        # Filter by category
        category_id = self.request.GET.get('category', '').strip()
        if category_id:
            try:
                queryset = queryset.filter(cid=int(category_id))
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add categories and search parameters to context."""
        context = super().get_context_data(**kwargs)
        
        # Create efficient category lookup dictionary
        categories = TbldgCategoryMaster.objects.all().order_by('cname')
        context['categories'] = categories
        context['categories_dict'] = {cat.cid: cat.cname for cat in categories}
        
        context['search_itemcode'] = self.request.GET.get('search_itemcode', '')
        context['search_desc'] = self.request.GET.get('search_desc', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context
    
    def get_template_names(self):
        """Return partial template for HTMX requests."""
        if self.request.headers.get('HX-Request'):
            return ['design/partials/item_list_partial.html']
        return ['design/item_list.html']


class ItemMasterDetailView(LoginRequiredMixin, DetailView):
    """
    Display item details and revision history.
    Converted from: aspnet/Module/Design/Masters/ItemMaster_Edit_Details.aspx
    """
    model = TbldgItemMaster
    template_name = 'design/item_detail.html'
    context_object_name = 'item'
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        """Add related data to context."""
        context = super().get_context_data(**kwargs)
        
        # Get category name
        if self.object.cid:
            try:
                context['category'] = TbldgCategoryMaster.objects.get(cid=self.object.cid)
            except TbldgCategoryMaster.DoesNotExist:
                context['category'] = None
        
        # Get sub-category name
        if self.object.cid:
            try:
                context['subcategory'] = TbldgSubcategoryMaster.objects.get(scid=self.object.cid)
            except TbldgSubcategoryMaster.DoesNotExist:
                context['subcategory'] = None
        
        # Get unit name
        if self.object.uombasic:
            try:
                context['unit'] = UnitMaster.objects.get(id=self.object.uombasic)
            except UnitMaster.DoesNotExist:
                context['unit'] = None
        
        # Check if item is used in BOMs
        context['bom_count'] = TbldgBomMaster.objects.filter(itemid=self.object.id).count()
        
        return context


class ItemMasterCreateView(LoginRequiredMixin, CreateView):
    """
    Create new item.
    Converted from: aspnet/Module/Design/Masters/ItemMaster_New.aspx
    """
    model = TbldgItemMaster
    form_class = ItemMasterForm
    template_name = 'design/item_form.html'
    success_url = reverse_lazy('design:item-list')
    
    def form_valid(self, form):
        """Add system fields before saving."""
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.sessionid = str(self.request.user.id)
        form.instance.compid = 1
        form.instance.finyearid = 1

        # Set default values for required fields
        if not form.instance.stockqty:
            form.instance.stockqty = 0
        if not form.instance.openingbaldate:
            form.instance.openingbaldate = now.strftime('%d-%m-%Y')
        if not form.instance.openingbalqty:
            form.instance.openingbalqty = 0
        if not form.instance.excise:
            form.instance.excise = 0
        if not form.instance.importlocal:
            form.instance.importlocal = 0

        # Handle file upload
        file_upload = form.cleaned_data.get('file_upload')
        if file_upload:
            form.instance.filename = file_upload.name
            form.instance.filesize = file_upload.size
            form.instance.contenttype = file_upload.content_type
            form.instance.filedata = file_upload.read()

        # Handle attachment upload
        attachment_upload = form.cleaned_data.get('attachment_upload')
        if attachment_upload:
            form.instance.attname = attachment_upload.name
            form.instance.attsize = attachment_upload.size
            form.instance.attcontenttype = attachment_upload.content_type
            form.instance.attdata = attachment_upload.read()

        messages.success(self.request, f'Item {form.instance.itemcode} created successfully.')
        return super().form_valid(form)


class ItemMasterUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing item.
    Converted from: aspnet/Module/Design/Masters/ItemMaster_Edit_Details.aspx
    """
    model = TbldgItemMaster
    form_class = ItemMasterForm
    template_name = 'design/item_form.html'
    success_url = reverse_lazy('design:item-list')
    pk_url_kwarg = 'id'
    
    def get_form(self, form_class=None):
        """Make item code readonly when editing."""
        form = super().get_form(form_class)
        form.fields['itemcode'].widget.attrs['readonly'] = True
        form.fields['itemcode'].widget.attrs['class'] += ' bg-gray-100'
        return form
    
    def form_valid(self, form):
        """Update item."""
        # Handle file upload
        file_upload = form.cleaned_data.get('file_upload')
        if file_upload:
            form.instance.filename = file_upload.name
            form.instance.filesize = file_upload.size
            form.instance.contenttype = file_upload.content_type
            form.instance.filedata = file_upload.read()

        # Handle attachment upload
        attachment_upload = form.cleaned_data.get('attachment_upload')
        if attachment_upload:
            form.instance.attname = attachment_upload.name
            form.instance.attsize = attachment_upload.size
            form.instance.attcontenttype = attachment_upload.content_type
            form.instance.attdata = attachment_upload.read()

        messages.success(self.request, f'Item {form.instance.itemcode} updated successfully.')
        return super().form_valid(form)


class ItemMasterDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete item with BOM reference checking.
    Converted from: aspnet/Module/Design/Masters/ItemMaster_Delete.aspx
    """
    model = TbldgItemMaster
    success_url = reverse_lazy('design:item-list')
    pk_url_kwarg = 'id'
    
    def delete(self, request, *args, **kwargs):
        """Check for BOM references before deleting."""
        self.object = self.get_object()
        item_code = self.object.itemcode
        
        # Check if item is used in BOMs
        bom_count = TbldgBomMaster.objects.filter(itemid=self.object.id).count()
        if bom_count > 0:
            messages.error(
                request,
                f'Cannot delete item {item_code}. It is used in {bom_count} BOM(s).'
            )
            return redirect(self.success_url)
        
        self.object.delete()
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        
        messages.success(request, f'Item {item_code} deleted successfully.')
        return redirect(self.success_url)

class ItemFileDownloadView(LoginRequiredMixin, View):
    """
    Download item drawing/document file.
    """
    def get(self, request, id):
        """Download file."""
        try:
            item = TbldgItemMaster.objects.get(id=id)

            if not item.filedata:
                messages.error(request, 'No file attached to this item.')
                return redirect('design:item-detail', id=id)

            # Create HTTP response with file
            response = HttpResponse(bytes(item.filedata), content_type=item.contenttype or 'application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{item.filename}"'
            response['Content-Length'] = item.filesize or len(item.filedata)

            return response

        except TbldgItemMaster.DoesNotExist:
            messages.error(request, 'Item not found.')
            return redirect('design:item-list')


class ItemAttachmentDownloadView(LoginRequiredMixin, View):
    """
    Download item attachment file.
    """
    def get(self, request, id):
        """Download attachment."""
        try:
            item = TbldgItemMaster.objects.get(id=id)

            if not item.attdata:
                messages.error(request, 'No attachment found for this item.')
                return redirect('design:item-detail', id=id)

            # Create HTTP response with file
            response = HttpResponse(bytes(item.attdata), content_type=item.attcontenttype or 'application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{item.attname}"'
            response['Content-Length'] = item.attsize or len(item.attdata)

            return response

        except TbldgItemMaster.DoesNotExist:
            messages.error(request, 'Item not found.')
            return redirect('design:item-list')
