"""
Reports Module Views
ASP.NET Reference: aaspnet/Module/Report/Reports/
Spec: .kiro/specs/reports-module/requirements.md
"""

from django.views.generic import TemplateView, ListView, View  # FIXED: Added View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Count
from django.http import HttpResponse

# Import models from other apps
from design.models import TbldgItemMaster, TbldgCategoryMaster
from material_management.models import Supplier  # FIXED: Was MmSupplierMaster
from sales_distribution.models import SdCustWorkorderMaster


class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    """
    Main reports dashboard.
    
    ASP.NET Reference: aaspnet/Module/Report/Dashboard.aspx
    """
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Reports Dashboard'
        return context


class BoughtoutDesignReportView(LoginRequiredMixin, ListView):
    """
    Boughtout Design Report - Show all boughtout items by design/category.
    
    ASP.NET Reference: aaspnet/Module/Report/Reports/Dashboard.aspx?SubModId=154
    Spec: .kiro/specs/reports-module/requirements.md
    
    Filters:
    - Work Order Number
    - Customer
    - Item Category
    - Date Range
    - Status
    
    Columns:
    - Item Code, Description, Category, Unit
    - Quantity Required, Ordered, Received, Pending
    - Supplier, Rate, Amount, Status
    """
    template_name = 'reports/boughtout_design.html'
    context_object_name = 'items'
    paginate_by = 50
    
    def get_queryset(self):
        """Get boughtout items with filtering."""
        queryset = TbldgItemMaster.objects.filter(
            boughtout=1  # 1 = Boughtout
        ).select_related(
            'cid', 'unitid'
        )
        
        # Apply filters
        wo_no = self.request.GET.get('wo_no')
        if wo_no:
            # Filter by work order if BOM relationship exists
            queryset = queryset.filter(
                Q(wono__icontains=wo_no)
            )
        
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(cid=category_id)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Boughtout Design Report'
        context['categories'] = TbldgCategoryMaster.objects.all()
        
        # Get filter values
        context['filter_wo_no'] = self.request.GET.get('wo_no', '')
        context['filter_category'] = self.request.GET.get('category', '')
        
        return context


class BoughtoutVendorReportView(LoginRequiredMixin, ListView):
    """
    Boughtout Vendor Report - Show boughtout items grouped by vendor/supplier.
    
    ASP.NET Reference: aaspnet/Module/Report/Reports/Dashboard.aspx?SubModId=155
    Spec: .kiro/specs/reports-module/requirements.md
    """
    template_name = 'reports/boughtout_vendor.html'
    context_object_name = 'items'
    paginate_by = 50
    
    def get_queryset(self):
        """Get boughtout items grouped by supplier."""
        # Placeholder - needs proper PO details model
        queryset = TbldgItemMaster.objects.filter(
            boughtout=1
        ).select_related('cid', 'unitid')
        
        # Apply filters
        wo_no = self.request.GET.get('wo_no')
        if wo_no:
            queryset = queryset.filter(wono__icontains=wo_no)
        
        return queryset.order_by('itemcode')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Boughtout Vendor Report'
        context['suppliers'] = Supplier.objects.all()
        
        # Get filter values
        context['filter_supplier'] = self.request.GET.get('supplier', '')
        context['filter_wo_no'] = self.request.GET.get('wo_no', '')
        
        return context


class BoughtoutAssemblyReportView(LoginRequiredMixin, ListView):
    """
    Boughtout Assembly Report - Show boughtout items by assembly/product.
    
    ASP.NET Reference: aaspnet/Module/Report/Reports/Dashboard.aspx?SubModId=156
    Spec: .kiro/specs/reports-module/requirements.md
    """
    template_name = 'reports/boughtout_assembly.html'
    context_object_name = 'assemblies'
    paginate_by = 50
    
    def get_queryset(self):
        """Get assemblies with boughtout items."""
        # This would need BOM structure
        # Placeholder for now
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Boughtout Assembly Report'
        return context


class ManufacturingDesignReportView(LoginRequiredMixin, ListView):
    """
    Manufacturing Design Report - Show manufactured items by design.
    
    ASP.NET Reference: aaspnet/Module/Report/Reports/Dashboard.aspx?SubModId=158
    Spec: .kiro/specs/reports-module/requirements.md
    """
    template_name = 'reports/manufacturing_design.html'
    context_object_name = 'items'
    paginate_by = 50
    
    def get_queryset(self):
        """Get manufactured items."""
        queryset = DesignItemMaster.objects.filter(
            is_boughtout=False
        ).select_related(
            'category', 'unit'
        )
        
        # Apply filters
        wo_no = self.request.GET.get('wo_no')
        if wo_no:
            queryset = queryset.filter(
                Q(bom_items__work_order__wono__icontains=wo_no)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Manufacturing Design Report'
        context['filter_wo_no'] = self.request.GET.get('wo_no', '')
        return context


class ManufacturingVendorReportView(LoginRequiredMixin, ListView):
    """
    Manufacturing Vendor Report - Show manufactured items by vendor/subcontractor.
    
    ASP.NET Reference: aaspnet/Module/Report/Reports/Manufacturing_Report_Info.aspx?SubModId=159
    Spec: .kiro/specs/reports-module/requirements.md
    """
    template_name = 'reports/manufacturing_vendor.html'
    context_object_name = 'items'
    paginate_by = 50
    
    def get_queryset(self):
        """Get manufacturing items by vendor."""
        # Placeholder - needs subcontracting data
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Manufacturing Vendor Report'
        return context


class ManufacturingAssemblyReportView(LoginRequiredMixin, ListView):
    """
    Manufacturing Assembly Report - Show manufactured items by assembly.
    
    ASP.NET Reference: aaspnet/Module/Report/Reports/Manufacturing_Assemly_New_Report_Info.aspx?SubModId=160
    Spec: .kiro/specs/reports-module/requirements.md
    """
    template_name = 'reports/manufacturing_assembly.html'
    context_object_name = 'assemblies'
    paginate_by = 50
    
    def get_queryset(self):
        """Get assemblies with manufactured items."""
        # Placeholder - needs BOM structure
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Manufacturing Assembly Report'
        return context


# ============================================================================
# EXPORT VIEWS
# ============================================================================

class ReportExportPDFView(LoginRequiredMixin, View):
    """
    Export report to PDF.
    
    Requires: pip install reportlab
    """
    def get(self, request, report_type):
        from .exporters import PDFExporter, create_pdf_response
        from datetime import datetime
        
        # Get report data based on type
        if report_type == 'boughtout-design':
            queryset = DesignItemMaster.objects.filter(is_boughtout=True)
            title = "Boughtout Design Report"
            headers = ['SN', 'Item Code', 'Description', 'Category', 'Unit', 'Status']
            data = [[str(i+1), item.itemcode, item.itemdescription[:30], 
                    item.category.name if item.category else '-',
                    item.unit.name if item.unit else '-', 'Pending'] 
                   for i, item in enumerate(queryset[:100])]
        else:
            return HttpResponse("Report type not supported", status=400)
        
        # Generate PDF
        output = PDFExporter.export_report(title, headers, data)
        
        if output is None:
            return HttpResponse(
                "PDF export requires 'reportlab' package. Install with: pip install reportlab",
                content_type="text/plain",
                status=501
            )
        
        filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return create_pdf_response(output, filename)


class ReportExportExcelView(LoginRequiredMixin, View):
    """
    Export report to Excel.
    
    Requires: pip install openpyxl
    """
    def get(self, request, report_type):
        from .exporters import ExcelExporter, create_excel_response
        from datetime import datetime
        
        # Get filters
        filters = {
            'Work Order': request.GET.get('wo_no', ''),
            'Category': request.GET.get('category', ''),
            'Supplier': request.GET.get('supplier', ''),
        }
        
        # Get report data based on type
        if report_type == 'boughtout-design':
            queryset = DesignItemMaster.objects.filter(is_boughtout=True).select_related('category', 'unit')
            output = ExcelExporter.export_boughtout_design(queryset, filters)
        elif report_type == 'boughtout-vendor':
            queryset = PurchaseOrderDetails.objects.filter(
                po__po_type='BOUGHTOUT'
            ).select_related('po', 'po__supplier', 'item')
            output = ExcelExporter.export_boughtout_vendor(queryset, filters)
        else:
            return HttpResponse("Report type not supported", status=400)
        
        if output is None:
            return HttpResponse(
                "Excel export requires 'openpyxl' package. Install with: pip install openpyxl",
                content_type="text/plain",
                status=501
            )
        
        filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return create_excel_response(output, filename)
