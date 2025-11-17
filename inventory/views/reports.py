"""
Inventory Reports and MCN Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse

# Import core mixins instead of inventory-specific mixins
from core.mixins import (
    BaseListViewMixin,
    BaseCreateViewMixin,
    BaseUpdateViewMixin,
    BaseDeleteViewMixin,
    BaseDetailViewMixin,
    LoginRequiredMixin,
    CompanyFinancialYearMixin,
    HTMXResponseMixin,
    QueryOptimizationMixin,
)

from ..models import (
    TblGatepass,
    TblinvMaterialrequisitionMaster, TblinvMaterialrequisitionDetails,
    TblinvMaterialissueMaster, TblinvMaterialissueDetails,
    TblinvMaterialreturnMaster, TblinvMaterialreturnDetails,
    TblinvInwardMaster, TblinvInwardDetails,
    TblinvMaterialreceivedMaster, TblinvMaterialreceivedDetails,
    TblinvMaterialservicenoteMaster, TblinvMaterialservicenoteDetails,
    TblinvSupplierChallanMaster, TblinvSupplierChallanDetails,
    TblinvCustomerChallanMaster, TblinvCustomerChallanDetails,
    TblinvWisMaster, TblinvWisDetails,
    TblvehProcessMaster,
    TblinvAutowisTimeschedule,
)
from .. import forms
from ..forms import (
    MRSMasterForm,
    MINMasterForm,
    MRNMasterForm,
    VehicleProcessMasterForm,
    VehicleMasterForm,
    AutoWISTimeScheduleForm,
    StockLedgerFilterForm,
)
from ..services import (
    MaterialRequisitionService,
    MaterialIssueService,
    MaterialReturnService,
    DashboardService,
)


class MCNListView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """MCN List View"""
    # model = Tblmcnmaster  # Model does not exist
    template_name = 'inventory/transactions/mcn_list.html'
    context_object_name = 'mcns'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('supplierid')
        
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(mcnno__icontains=search) |
                Q(supplierid__suppliername__icontains=search)
            )
        
        return queryset.order_by('-mcndate', '-mcnid')



class MCNCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """MCN Create View"""
    # model = Tblmcnmaster  # Model does not exist
    # form_class = MCNMasterForm  # Form commented out
    template_name = 'inventory/transactions/mcn_form.html'
    success_url = reverse_lazy('inventory:mcn-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.request.session.get('compid', 1)
        kwargs['finyearid'] = self.request.session.get('finyearid', 1)
        kwargs['sessionid'] = self.request.session.get('sessionid', 1)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['detail_formset'] = MCNDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['detail_formset'] = MCNDetailFormSet(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        detail_formset = context['detail_formset']
        
        if detail_formset.is_valid():
            from .services import MaterialCreditNoteService
            compid = self.request.session.get('compid', 1)
            finyearid = self.request.session.get('finyearid', 1)
            
            mcn_number = MaterialCreditNoteService.generate_mcn_number(compid, finyearid)
            form.instance.mcnno = mcn_number
            
            self.object = form.save()
            detail_formset.instance = self.object
            detail_formset.save()
            
            messages.success(self.request, f'MCN {mcn_number} created successfully!')
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)



class MCNDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """MCN Detail View"""
    # model = Tblmcnmaster  # Model does not exist
    template_name = 'inventory/transactions/mcn_detail.html'
    context_object_name = 'mcn'
    pk_url_kwarg = 'mcnid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        details = Tblmcndetail.objects.filter(mcnid=self.object).select_related('itemid')
        context['details'] = details
        return context



class MCNDeleteView(LoginRequiredMixin, CompanyFinancialYearMixin, DeleteView):
    """MCN Delete View"""
    # model = Tblmcnmaster  # Model does not exist
    template_name = 'inventory/transactions/mcn_confirm_delete.html'
    success_url = reverse_lazy('inventory:mcn-list')
    pk_url_kwarg = 'mcnid'
    
    def delete(self, request, *args, **kwargs):
        mcn = self.get_object()
        messages.success(request, f'MCN {mcn.mcnno} deleted successfully!')
        return super().delete(request, *args, **kwargs)



class MCNPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """MCN Print View"""
    # model = Tblmcnmaster  # Model does not exist
    template_name = 'inventory/transactions/mcn_print.html'
    context_object_name = 'mcn'
    pk_url_kwarg = 'mcnid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        details = Tblmcndetail.objects.filter(mcnid=self.object).select_related('itemid')
        context['details'] = details
        return context


# ============================================================================
# CLOSING STOCK VIEWS
# ============================================================================


class ClosingStockView(LoginRequiredMixin, HTMXResponseMixin, ListView):
    """
    Closing Stock View - SAP Fiori-style inline editing

    Manages period-based aggregate closing stock values (not item-level tracking).
    Shows all records in a table with inline add form in footer.

    Converted from: aspnet/Module/Inventory/Transactions/ClosingStock.aspx
    Pattern: SAP Fiori-style (like VehicleMasterListView)
    Requirements: 11.1
    """
    model = TblinvMaterialreturnMaster  # Placeholder - will use service
    template_name = 'inventory/transactions/closing_stock.html'
    partial_template_name = 'inventory/transactions/partials/closing_stock_partial.html'
    context_object_name = 'records'

    def get_queryset(self):
        """Get all closing stock records (no company/year filtering)"""
        from ..services import ClosingStockService
        return ClosingStockService.get_all_records()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from ..forms import ClosingStockForm
        context['form'] = ClosingStockForm()
        return context

    def post(self, request, *args, **kwargs):
        """Handle inline create from footer form"""
        from ..forms import ClosingStockForm
        from ..services import ClosingStockService
        from datetime import datetime

        action = request.POST.get('action')

        if action == 'delete':
            # Handle delete
            record_id = request.POST.get('record_id')
            if ClosingStockService.delete_record(record_id):
                messages.success(request, 'Closing stock record deleted successfully!')
            else:
                messages.error(request, 'Error deleting record')

            if request.headers.get('HX-Request'):
                self.object_list = self.get_queryset()
                context = self.get_context_data()
                return render(request, self.partial_template_name, context)

            return redirect('inventory:closing-stock')

        # Handle create
        form = ClosingStockForm(request.POST)
        if form.is_valid():
            # Convert dates to DD-MM-YYYY format for storage
            from_date = form.cleaned_data['from_date'].strftime('%d-%m-%Y')
            to_date = form.cleaned_data['to_date'].strftime('%d-%m-%Y')
            value = form.cleaned_data['closing_stock_value']

            ClosingStockService.create_record(from_date, to_date, value)

            messages.success(request, 'Closing stock record created successfully!')

            # HTMX partial response
            if request.headers.get('HX-Request'):
                self.object_list = self.get_queryset()
                context = self.get_context_data()
                return render(request, self.partial_template_name, context)

            return redirect('inventory:closing-stock')

        # Form errors
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['form'] = form

        if request.headers.get('HX-Request'):
            return render(request, self.partial_template_name, context)

        return render(request, self.template_name, context)



# ============================================================================
# REPORT VIEWS
# ============================================================================


class OutwardRegisterView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Outward Register Report View
    
    Consolidated view of all outward transactions (MIN, MCN, Customer Challan).
    
    Converted from: aspnet/Module/Inventory/Reports/InwardOutwardRegister.aspx
    Requirements: 5.3, 5.4, 5.5, 5.6
    """
    template_name = 'inventory/reports/outward_register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get filter parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        transaction_types = self.request.GET.getlist('transaction_types')
        
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['selected_types'] = transaction_types
        
        # Generate register if dates provided
        if start_date and end_date:
            try:
                from datetime import datetime
                from .services import ReportService
                
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Use selected types or all if none selected
                types = transaction_types if transaction_types else None
                
                register_data = ReportService.get_outward_register(
                    compid, finyearid, start_dt, end_dt, types
                )
                
                context['register_data'] = register_data
                
                # Calculate totals
                if register_data:
                    from decimal import Decimal
                    context['total_quantity'] = sum(t['quantity'] for t in register_data)
                    context['total_value'] = sum(t['value'] for t in register_data)
                
            except ValueError:
                messages.error(self.request, 'Invalid date format.')
            except Exception as e:
                messages.error(self.request, f'Error generating register: {str(e)}')
        
        return context



# ============================================================================
# SEARCH VIEWS
# ============================================================================


class StockStatementView(LoginRequiredMixin, CompanyFinancialYearMixin, HTMXResponseMixin, TemplateView):
    """
    Stock Statement Report View
    
    Converted from: aspnet/Module/Inventory/Reports/SSStock_Statement.aspx
    """
    template_name = 'inventory/reports/stock_statement.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from sys_admin.models import Tblitemcategorymaster
        
        context['categories'] = Tblitemcategorymaster.objects.filter(compid=self.get_compid())
        
        filters = {
            'category_id': self.request.GET.get('category_id'),
            'stock_status': self.request.GET.get('stock_status'),
            'search': self.request.GET.get('search'),
        }
        context['filters'] = filters
        
        # Only fetch data if there are filters applied
        if any(filters.values()):
            from .services import ReportService
            context['stock_data'] = ReportService.get_stock_statement(
                compid=self.get_compid(),
                finyearid=self.get_finyearid(),
                filters=filters
            )
        
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.htmx:
            self.template_name = 'inventory/reports/partials/stock_statement_results.html'
            return self.render_to_response(context)
        return super().get(request, *args, **kwargs)



class ABCAnalysisView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    ABC Analysis Report View
    
    Performs ABC analysis on inventory items based on value/quantity/frequency.
    
    Converted from: aspnet/Module/Inventory/Reports/ABCAnalysis.aspx
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
    """
    template_name = 'inventory/reports/abc_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get filter parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        criteria = self.request.GET.get('criteria', 'value')
        category_filter = self.request.GET.get('category_filter', 'all')
        
        context['criteria'] = criteria
        context['category_filter'] = category_filter
        
        # Generate analysis if dates provided
        if start_date and end_date:
            try:
                from datetime import datetime
                from .services import ReportService
                
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                analysis_data = ReportService.get_abc_analysis(
                    compid, finyearid, start_dt, end_dt, criteria
                )
                
                # Filter by category if selected
                if category_filter != 'all':
                    analysis_data = [item for item in analysis_data 
                                   if item['abc_category'] == category_filter]
                
                context['analysis_data'] = analysis_data
                context['start_date'] = start_date
                context['end_date'] = end_date
                
                # Calculate summary statistics
                if analysis_data:
                    context['summary'] = {
                        'total_items': len(analysis_data),
                        'a_items': len([i for i in analysis_data if i['abc_category'] == 'A']),
                        'b_items': len([i for i in analysis_data if i['abc_category'] == 'B']),
                        'c_items': len([i for i in analysis_data if i['abc_category'] == 'C']),
                    }
                
            except ValueError:
                messages.error(self.request, 'Invalid date format.')
            except Exception as e:
                messages.error(self.request, f'Error generating ABC analysis: {str(e)}')
        
        return context



class MovingNonMovingItemsView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Moving and Non-Moving Items Report View
    
    Identifies items based on transaction activity threshold.
    
    Converted from: aspnet/Module/Inventory/Reports/Moving_NonMoving_Items.aspx
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
    """
    template_name = 'inventory/reports/moving_items.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get threshold parameter (default 90 days)
        threshold_days = int(self.request.GET.get('threshold_days', 90))
        movement_filter = self.request.GET.get('movement_filter', 'all')
        
        context['threshold_days'] = threshold_days
        context['movement_filter'] = movement_filter
        
        try:
            from .services import ReportService
            
            items_data = ReportService.get_moving_nonmoving_items(
                compid, finyearid, threshold_days
            )
            
            # Filter by movement status if selected
            if movement_filter != 'all':
                items_data = [item for item in items_data 
                            if item['movement_status'] == movement_filter]
            
            context['items_data'] = items_data
            
            # Calculate summary
            if items_data:
                context['summary'] = {
                    'total_items': len(items_data),
                    'moving_items': len([i for i in items_data if i['movement_status'] == 'Moving']),
                    'non_moving_items': len([i for i in items_data if i['movement_status'] == 'Non-Moving']),
                    'never_moved_items': len([i for i in items_data if i['movement_status'] == 'Never Moved']),
                    'critical_items': len([i for i in items_data if i['is_critical']]),
                }
            
        except Exception as e:
            messages.error(self.request, f'Error generating report: {str(e)}')
            context['items_data'] = []
        
        return context



class WorkOrderIssueView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Work Order Issue Report View
    
    Shows material issues for a specific work order.
    
    Converted from: aspnet/Module/Inventory/Reports/WorkOrder_Issue.aspx
    Requirements: 4.1, 4.2, 4.3, 4.6, 4.7
    """
    template_name = 'inventory/reports/work_order_issue.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get work order parameter
        work_order_id = self.request.GET.get('work_order_id')
        
        # Get all work orders for dropdown
        from production.models import TblworkorderMaster
        context['work_orders'] = TblworkorderMaster.objects.filter(
            compid=compid
        ).order_by('-woid')[:100]  # Last 100 work orders
        
        # Generate report if work order selected
        if work_order_id:
            try:
                from .services import ReportService
                
                issues_data = ReportService.get_work_order_issues(
                    work_order_id, compid, finyearid
                )
                
                context['issues_data'] = issues_data
                context['selected_work_order_id'] = int(work_order_id)
                
                # Get work order details
                try:
                    work_order = TblworkorderMaster.objects.get(woid=work_order_id)
                    context['work_order'] = work_order
                except:
                    pass
                
            except Exception as e:
                messages.error(self.request, f'Error generating report: {str(e)}')
        
        return context



class WorkOrderShortageView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Work Order Shortage Report View
    
    Shows material shortages for a specific work order.
    
    Converted from: aspnet/Module/Inventory/Reports/WorkOrder_Shortage.aspx
    Requirements: 4.4, 4.5, 4.7
    """
    template_name = 'inventory/reports/work_order_shortage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get work order parameter
        work_order_id = self.request.GET.get('work_order_id')
        
        # Get all work orders for dropdown
        from production.models import TblworkorderMaster
        context['work_orders'] = TblworkorderMaster.objects.filter(
            compid=compid
        ).order_by('-woid')[:100]
        
        # Generate report if work order selected
        if work_order_id:
            try:
                from .services import ReportService
                
                shortages_data = ReportService.get_work_order_shortages(
                    work_order_id, compid, finyearid
                )
                
                context['shortages_data'] = shortages_data
                context['selected_work_order_id'] = int(work_order_id)
                
                # Get work order details
                try:
                    work_order = TblworkorderMaster.objects.get(woid=work_order_id)
                    context['work_order'] = work_order
                except:
                    pass
                
                # Check if all materials issued
                if not shortages_data:
                    messages.success(self.request, 'All materials issued completely for this work order.')
                
            except Exception as e:
                messages.error(self.request, f'Error generating report: {str(e)}')
        
        return context



class InwardRegisterView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Inward Register Report View
    
    Consolidated view of all inward transactions (GIN, GRR, MRN).
    
    Converted from: aspnet/Module/Inventory/Reports/InwardOutwardRegister.aspx
    Requirements: 5.1, 5.2, 5.5, 5.6
    """
    template_name = 'inventory/reports/inward_register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        compid = self.get_compid()
        finyearid = self.get_finyearid()
        
        # Get filter parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        transaction_types = self.request.GET.getlist('transaction_types')
        
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['selected_types'] = transaction_types
        
        # Generate register if dates provided
        if start_date and end_date:
            try:
                from datetime import datetime
                from .services import ReportService
                
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Use selected types or all if none selected
                types = transaction_types if transaction_types else None
                
                register_data = ReportService.get_inward_register(
                    compid, finyearid, start_dt, end_dt, types
                )
                
                context['register_data'] = register_data
                
                # Calculate totals
                if register_data:
                    from decimal import Decimal
                    context['total_quantity'] = sum(t['quantity'] for t in register_data)
                    context['total_value'] = sum(t['value'] for t in register_data)
                
            except ValueError:
                messages.error(self.request, 'Invalid date format.')
            except Exception as e:
                messages.error(self.request, f'Error generating register: {str(e)}')
        
        return context



class StockLedgerSelectionView(LoginRequiredMixin, TemplateView):
    """
    Stock Ledger Selection View
    Converted from: aspnet/Module/Inventory/Reports/StockLedger.aspx
    """
    template_name = 'inventory/reports/stock_ledger_selection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from sys_admin.models import Tblitemcategorymaster

        categories = Tblitemcategorymaster.objects.filter(compid=self.request.session.get('compid', 1)).values_list('cid', 'cname')
        
        form = StockLedgerFilterForm(self.request.GET or None, categories=categories)
        context['form'] = form

        if form.is_valid():
            # This is a placeholder. The actual filtering logic will be complex.
            # For now, we'll just indicate that the form was submitted.
            context['items'] = [] # Placeholder for filtered items
            messages.info(self.request, "Search functionality to be implemented.")

        return context


# ============================================================================
# VEHICLE MASTER VIEWS - SAP Fiori Style with HTMX
# ============================================================================


