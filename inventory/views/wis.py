"""
WIS (Work Instruction Sheet) Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseRedirect

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
    TblinvWisMaster, TblinvWisDetails, TblinvWoreleaseWis,
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
    WISMasterForm,
)
from ..services import (
    MaterialRequisitionService,
    MaterialIssueService,
    MaterialReturnService,
    DashboardService,
)


class WISListView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    WIS List View - Shows work orders and allows releasing WIS
    Display all work orders with WIS release information

    Converted from: aspnet/Module/Inventory/Transactions/ReleaseWIS.aspx
    """
    template_name = 'inventory/transactions/wis_list.html'
    context_object_name = 'workorders'
    paginate_by = 20

    def get_queryset(self):
        from sales_distribution.models import SdCustWorkorderMaster, TblsdWoCategory

        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Get WO category filter
        category_id = self.request.GET.get('category', '')
        wono_search = self.request.GET.get('wono', '')

        # Base queryset - ONLY show OPEN work orders (CloseOpen=0)
        qs = SdCustWorkorderMaster.objects.filter(
            compid=compid,
            closeopen=0  # Only open work orders as per ASP.NET line 89
        ).select_related()

        # Apply filters
        if category_id and category_id.isdigit():
            qs = qs.filter(cid=int(category_id))

        if wono_search:
            qs = qs.filter(wono__icontains=wono_search)

        return qs.order_by('wono')  # ASC order by WONo as per ASP.NET

    def get_context_data(self, **kwargs):
        from sales_distribution.models import TblsdWoCategory
        from human_resource.models import TblhrOfficestaff

        context = super().get_context_data(**kwargs)

        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Add release information to each work order in the paginated list
        # This ensures data persists after pagination
        workorders = context.get('workorders') or context.get('object_list', [])

        for wo in workorders:
            # Count total releases for this WO
            release_count = TblinvWoreleaseWis.objects.filter(
                wono=wo.wono
            ).count()
            wo.release_count = release_count

            # Get latest release info (most recent by Id DESC)
            latest_release = TblinvWoreleaseWis.objects.filter(
                wono=wo.wono,
                compid=compid
            ).order_by('-id').first()

            if latest_release:
                wo.release_date = latest_release.releasesysdate
                wo.release_time = latest_release.releasesystime
                # Get employee name from HR table (use filter().first() to handle duplicate empid)
                staff = TblhrOfficestaff.objects.filter(empid=latest_release.releaseby).first()
                if staff:
                    wo.release_by = f"{staff.title}. {staff.employeename}" if staff.title else staff.employeename
                else:
                    wo.release_by = latest_release.releaseby
            else:
                wo.release_date = None
                wo.release_time = None
                wo.release_by = None

        # Get WO categories for dropdown
        categories = TblsdWoCategory.objects.filter(
            compid=compid,
            finyearid=finyearid
        )
        context['categories'] = categories
        context['selected_category'] = self.request.GET.get('category', '')
        context['wono_search'] = self.request.GET.get('wono', '')

        return context


class WISReleaseWOView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    Release WO for WIS - Updates WO and creates release record
    Matches ASP.NET logic (lines 171-180)
    """
    def post(self, request, *args, **kwargs):
        from datetime import datetime
        from sales_distribution.models import SdCustWorkorderMaster

        wono = request.POST.get('wono')
        wo_id = request.POST.get('wo_id')
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        username = request.user.username

        try:
            # Check if work order exists
            wo = SdCustWorkorderMaster.objects.get(
                id=wo_id,
                compid=compid
            )

            # Update ReleaseWIS field to 1 (as per ASP.NET line 176)
            wo.releasewis = 1
            wo.save(update_fields=['releasewis'])

            # Create WIS release record (as per ASP.NET line 178)
            now = datetime.now()
            TblinvWoreleaseWis.objects.create(
                compid=compid,
                finyearid=finyearid,
                wono=wono,
                releasesysdate=now.strftime('%d-%m-%Y'),
                releasesystime=now.strftime('%I:%M:%S %p'),  # 12-hour format with AM/PM
                releaseby=username
            )

            messages.success(request, f'WIS released successfully for Work Order {wono}!')
        except SdCustWorkorderMaster.DoesNotExist:
            messages.error(request, f'Work Order {wono} not found!')
        except Exception as e:
            messages.error(request, f'Error releasing WIS: {str(e)}')

        return redirect('inventory:wis-list')


class WISStopWOView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    Stop WO for WIS - Sets ReleaseWIS to 0
    Matches ASP.NET logic (lines 182-189)
    NOTE: Does NOT delete release records, only updates flag
    """
    def post(self, request, *args, **kwargs):
        from sales_distribution.models import SdCustWorkorderMaster

        wo_id = request.POST.get('wo_id')
        wono = request.POST.get('wono')
        compid = request.session.get('compid', 1)

        try:
            # Get work order and update ReleaseWIS to 0 (as per ASP.NET line 186)
            wo = SdCustWorkorderMaster.objects.get(
                id=wo_id,
                compid=compid
            )

            wo.releasewis = 0
            wo.save(update_fields=['releasewis'])

            messages.success(request, f'WIS stopped for Work Order {wono}!')
        except SdCustWorkorderMaster.DoesNotExist:
            messages.error(request, f'Work Order {wono} not found!')
        except Exception as e:
            messages.error(request, f'Error stopping WIS: {str(e)}')

        return redirect('inventory:wis-list')


class WISCreateView(LoginRequiredMixin, CompanyFinancialYearMixin, CreateView):
    """
    WIS Create View

    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Material.aspx (create section)
    """
    model = TblinvWisMaster
    form_class = WISMasterForm
    template_name = 'inventory/transactions/wis_form.html'
    success_url = reverse_lazy('inventory:wis-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compid'] = self.request.session.get('compid', 1)
        kwargs['finyearid'] = self.request.session.get('finyearid', 1)
        kwargs['sessionid'] = self.request.session.get('sessionid', 1)
        return kwargs

    def form_valid(self, form):
        """Save WIS with audit fields"""
        from datetime import datetime

        # Set audit fields
        now = datetime.now()
        form.instance.sysdate = now.strftime('%d-%m-%Y')
        form.instance.systime = now.strftime('%H:%M:%S')
        form.instance.compid = self.request.session.get('compid', 1)
        form.instance.finyearid = self.request.session.get('finyearid', 1)
        form.instance.sessionid = str(self.request.user.id)

        # Generate WIS number if not provided
        if not form.instance.wisno:
            from ..services import generate_transaction_number
            form.instance.wisno = generate_transaction_number('WIS', form.instance.compid, form.instance.finyearid)

        self.object = form.save()

        messages.success(
            self.request,
            f'WIS {self.object.wisno} created successfully!'
        )

        return HttpResponseRedirect(self.get_success_url())



class WISDetailView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    WIS Detail View with material details

    Converted from: aspnet/Module/Inventory/Transactions/WIS_View_TransWise.aspx
    """
    model = TblinvWisMaster
    template_name = 'inventory/transactions/wis_detail.html'
    context_object_name = 'wis'
    pk_url_kwarg = 'pk'  # Fixed: use 'pk' not 'wisid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get WIS details - fixed model name and filter field
        details = TblinvWisDetails.objects.filter(
            mid=self.object
        )

        context['details'] = details

        # Get item information for each detail
        from design.models import TbldgItemMaster
        details_with_items = []
        for detail in details:
            item = None
            if detail.itemid:
                try:
                    item = TbldgItemMaster.objects.get(id=detail.itemid)
                except TbldgItemMaster.DoesNotExist:
                    pass
            details_with_items.append({
                'detail': detail,
                'item': item
            })

        context['details_with_items'] = details_with_items

        return context



class WISReleaseView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    WIS Release View - Mark WIS as released

    Converted from: aspnet/Module/Inventory/Transactions/ReleaseWIS.aspx
    """

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        try:
            wis = TblinvWisMaster.objects.get(pk=pk)

            # Record in release table
            from ..models import TblinvWoreleaseWis
            from datetime import datetime

            release_record, created = TblinvWoreleaseWis.objects.get_or_create(
                compid=wis.compid,
                finyearid=wis.finyearid,
                wono=wis.wono,
                defaults={
                    'releasesysdate': datetime.now().strftime('%d-%m-%Y')
                }
            )

            messages.success(request, f'WIS {wis.wisno} released successfully!')
        except TblinvWisMaster.DoesNotExist:
            messages.error(request, 'WIS not found!')
        except Exception as e:
            messages.error(request, f'Error releasing WIS: {str(e)}')

        return HttpResponseRedirect(
            reverse_lazy('inventory:wis-detail', kwargs={'pk': pk})
        )



class WISActualRunView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    WIS Actual Run View - Display materials for actual run

    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Material.aspx
    Note: Complex BOM calculation logic from ASP.NET deferred to Phase 2
    """
    template_name = 'inventory/transactions/wis_actual_run.html'

    def get_wis(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(TblinvWisMaster, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wis = self.get_wis()

        # Get WIS details
        details = TblinvWisDetails.objects.filter(mid=wis)

        # Get item information
        from design.models import TbldgItemMaster
        details_with_items = []
        for detail in details:
            item = None
            if detail.itemid:
                try:
                    item = TbldgItemMaster.objects.get(id=detail.itemid)
                except TbldgItemMaster.DoesNotExist:
                    pass
            details_with_items.append({
                'detail': detail,
                'item': item
            })

        context['wis'] = wis
        context['details_with_items'] = details_with_items

        return context



class WISPrintView(LoginRequiredMixin, CompanyFinancialYearMixin, DetailView):
    """
    WIS Print View

    Converted from: aspnet/Module/Inventory/Transactions/WIS_ActualRun_Print.aspx
    """
    model = TblinvWisMaster
    template_name = 'inventory/transactions/wis_print.html'
    context_object_name = 'wis'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get WIS details
        details = TblinvWisDetails.objects.filter(mid=self.object)

        # Get item information
        from design.models import TbldgItemMaster
        details_with_items = []
        for detail in details:
            item = None
            if detail.itemid:
                try:
                    item = TbldgItemMaster.objects.get(id=detail.itemid)
                except TbldgItemMaster.DoesNotExist:
                    pass
            details_with_items.append({
                'detail': detail,
                'item': item
            })

        context['details_with_items'] = details_with_items

        return context



# ============================================================================
# AUTO WIS TIME SCHEDULE VIEWS
# ============================================================================


class AutoWISTimeScheduleListView(BaseListViewMixin, ListView):
    """
    Auto WIS Time Schedule List View
    Converted from: aspnet/Module/Inventory/Masters/AutoWIS_Time_Set.aspx
    """
    model = TblinvAutowisTimeschedule
    template_name = 'inventory/masters/autowis_timeschedule_list.html'
    context_object_name = 'schedules'
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AutoWISTimeScheduleForm()
        return context


class AutoWISTimeScheduleCreateView(BaseCreateViewMixin, CreateView):
    """
    Auto WIS Time Schedule Create View
    """
    model = TblinvAutowisTimeschedule
    form_class = AutoWISTimeScheduleForm
    success_url = reverse_lazy('inventory:autowis-timeschedule-list')
    success_message = 'Scheduled time added successfully!'
    error_message = 'Error adding scheduled time.'


class AutoWISTimeScheduleUpdateView(BaseUpdateViewMixin, UpdateView):
    """
    Auto WIS Time Schedule Update View
    """
    model = TblinvAutowisTimeschedule
    form_class = AutoWISTimeScheduleForm
    success_url = reverse_lazy('inventory:autowis-timeschedule-list')
    template_name = 'inventory/masters/partials/autowis_timeschedule_edit.html'
    success_message = 'Scheduled time updated successfully!'


class AutoWISTimeScheduleDeleteView(BaseDeleteViewMixin, DeleteView):
    """
    Auto WIS Time Schedule Delete View
    """
    model = TblinvAutowisTimeschedule
    success_url = reverse_lazy('inventory:autowis-timeschedule-list')
    success_message = 'Scheduled time deleted successfully!'


class AutoWISTimeScheduleRowView(LoginRequiredMixin, DetailView):
    """
    Renders a single row for the Auto WIS Time Schedule list.
    Used for HTMX cancel actions.
    """
    model = TblinvAutowisTimeschedule
    template_name = 'inventory/masters/partials/autowis_timeschedule_row.html'
    context_object_name = 'schedule'


# ============================================================================
# WIS DRY RUN VIEWS
# ============================================================================


class WISDryRunEntryView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    Dry Run Entry Point - Lists Work Orders with "Dry Run" button

    Converted from: WIS_Dry_Actual_Run.aspx
    """
    template_name = 'inventory/transactions/wis_dryrun_entry.html'
    context_object_name = 'workorders'
    paginate_by = 20

    def get_queryset(self):
        from sales_distribution.models import SdCustWorkorderMaster

        compid = self.request.session.get('compid', 1)

        # Get filter parameters
        wo_type = self.request.GET.get('wo_type', '')
        wono_search = self.request.GET.get('wono', '')

        # Base queryset - ONLY show OPEN work orders with ReleaseWIS=1
        qs = SdCustWorkorderMaster.objects.filter(
            compid=compid,
            closeopen=0,  # Open work orders only
            releasewis=1  # Must be released for WIS
        ).select_related()

        # Apply filters
        if wo_type and wo_type.isdigit():
            qs = qs.filter(cid=int(wo_type))

        if wono_search:
            qs = qs.filter(wono__icontains=wono_search)

        return qs.order_by('wono')

    def get_context_data(self, **kwargs):
        from sales_distribution.models import TblsdWoCategory

        context = super().get_context_data(**kwargs)

        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Get WO types/categories for dropdown
        wo_categories = TblsdWoCategory.objects.filter(
            compid=compid,
            finyearid=finyearid
        )
        context['wo_categories'] = wo_categories
        context['selected_wo_type'] = self.request.GET.get('wo_type', '')
        context['wono_search'] = self.request.GET.get('wono', '')

        return context


class WISDryRunAssemblyView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Dry Run for Assemblies - Displays hierarchical tree of assemblies

    Converted from: WIS_ActualRun_Assembly.aspx
    """
    template_name = 'inventory/transactions/wis_dryrun_assembly.html'

    def get_context_data(self, **kwargs):
        from sales_distribution.models import SdCustWorkorderMaster
        from design.models import TbldgBomMaster, TbldgItemMaster
        from ..services import WISDryRunService

        context = super().get_context_data(**kwargs)

        wono = self.kwargs.get('wono')
        compid = self.request.session.get('compid', 1)

        # Get Work Order details (use filter + first to handle duplicates)
        wo = SdCustWorkorderMaster.objects.filter(
            wono=wono, compid=compid
        ).order_by('-id').first()

        if not wo:
            context['error'] = f'Work Order {wono} not found'
            return context

        context['wo'] = wo

        # Get BOM assembly items (items that are assemblies/sub-assemblies)
        # Filter for items that have children (are parents in hierarchy)
        assembly_pids = TbldgBomMaster.objects.filter(
            wono=wono,
            compid=compid,
            pid__gt=0  # Has parent, so is a sub-assembly
        ).values_list('cid', flat=True).distinct()

        assembly_items = []
        for pid in assembly_pids:
            bom = TbldgBomMaster.objects.filter(
                wono=wono,
                cid=pid,
                compid=compid
            ).first()

            if bom and bom.itemid:
                try:
                    item = TbldgItemMaster.objects.get(id=bom.itemid, compid=compid)

                    # Calculate BOM quantity
                    bom_qty = WISDryRunService.calculate_bom_tree_qty(
                        wono, bom.pid, bom.cid, 0, compid
                    )

                    assembly_items.append({
                        'pid': bom.pid,
                        'cid': bom.cid,
                        'item_code': item.partno or item.itemcode or '-',
                        'description': item.manfdesc or item.itemname or '-',
                        'uom': item.uombasic or '-',
                        'unit_qty': float(bom.qty) if bom.qty else 0,
                        'bom_qty': bom_qty,
                    })
                except TbldgItemMaster.DoesNotExist:
                    pass

        context['assembly_items'] = assembly_items

        return context


class WISDryRunMaterialView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Dry Run for Materials - Displays hierarchical tree with all quantities

    Enhanced version of WISActualRunView with complete BOM calculations.
    Converted from: WIS_ActualRun_Material.aspx
    """
    template_name = 'inventory/transactions/wis_dryrun_material.html'

    def get_context_data(self, **kwargs):
        from sales_distribution.models import SdCustWorkorderMaster
        from ..services import WISDryRunService

        context = super().get_context_data(**kwargs)

        wono = self.kwargs.get('wono')
        compid = self.request.session.get('compid', 1)
        finyearid = self.request.session.get('finyearid', 1)

        # Get Work Order details (use filter + first to handle duplicates)
        wo = SdCustWorkorderMaster.objects.filter(
            wono=wono, compid=compid
        ).order_by('-id').first()

        if not wo:
            context['error'] = f'Work Order {wono} not found'
            return context

        context['wo'] = wo

        # Get dry run data (all calculations)
        try:
            materials = WISDryRunService.get_dry_run_data(wono, compid, finyearid)
            context['materials'] = materials

            # Calculate totals
            context['total_items'] = len(materials)
            context['items_to_issue'] = len([m for m in materials if m['dry_run_qty'] > 0])
            context['items_with_shortage'] = len([m for m in materials if m['has_shortage']])

        except Exception as e:
            context['error'] = f'Error calculating dry run: {str(e)}'
            context['materials'] = []

        return context


class WISExecuteActualRunView(LoginRequiredMixin, CompanyFinancialYearMixin, View):
    """
    Execute Actual Run - POST only view to execute real material issuance

    Calls WISDryRunService.execute_actual_run() which:
    - Creates WIS Master and Details records
    - Updates stock quantities
    - Marks Work Order as DryActualRun=1
    """

    def post(self, request, *args, **kwargs):
        from ..services import WISDryRunService

        wono = kwargs.get('wono')
        compid = request.session.get('compid', 1)
        finyearid = request.session.get('finyearid', 1)
        username = request.user.username

        # Execute actual run
        result = WISDryRunService.execute_actual_run(wono, compid, finyearid, username)

        if result['success']:
            messages.success(request, result['message'])
            messages.info(request, f"{result['items_issued']} items issued successfully.")

            # Redirect to WIS detail page
            from ..models import TblinvWisMaster
            wis = TblinvWisMaster.objects.filter(
                wisno=result['wis_no'],
                compid=compid
            ).first()

            if wis:
                return redirect('inventory:wis-detail', pk=wis.pk)
            else:
                return redirect('inventory:wis-dryrun-entry')
        else:
            messages.error(request, result['message'])
            return redirect('inventory:wis-dryrun-material', wono=wono)
