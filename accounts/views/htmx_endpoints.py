"""
Views for the Accounts module.
Converted from ASP.NET Module/Accounts/Masters/*.aspx
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.db import transaction, models
from django.contrib import messages
from datetime import datetime

# Import core mixins for standardized view behavior
from core.mixins import (
    BaseListViewMixin, BaseCreateViewMixin, BaseUpdateViewMixin,
    BaseDeleteViewMixin, BaseDetailViewMixin, HTMXResponseMixin,
    CompanyFinancialYearMixin, AuditMixin
)
from ..models import (
    Acchead, TblaccSalesinvoiceMaster, TblaccSalesinvoiceDetails,
    TblaccServicetaxinvoiceMaster, TblaccServicetaxinvoiceDetails,
    TblaccAdvicePaymentMaster, TblaccAdvicePaymentDetails,
    TblaccCapitalMaster, TblaccCapitalDetails,
    TblaccLoanmaster, TblaccLoandetails,
    TblaccTourvoucherMaster, TblaccTourvoucheradvanceDetails,
    TblaccTourintimationMaster, TblaccIouMaster,
    TblaccCashvoucherPaymentMaster, TblaccCashvoucherPaymentDetails,
    TblaccCashvoucherReceiptMaster,
    TblaccBankvoucherPaymentMaster, TblaccBankvoucherPaymentDetails,
    TblaccProformainvoiceMaster, TblaccProformainvoiceDetails,
    TblaccBillbookingMaster, TblaccBillbookingDetails, TblaccBillbookingAttachMaster,
    TblaccBank, TblpackingMaster, TblaccContraEntry,
    TblaccCurrencyMaster, TblaccTdscodeMaster, TblvatMaster, TblwarrentyMaster,
    TblaccAssetRegister, TblaccDebitnote,
    # Simple lookup masters
    TblaccIntresttype, TblaccInvoiceagainst, TblaccIouReasons, TblaccLoantype,
    TblaccPaidtype, TblaccPaymentmode, TblaccReceiptagainst, TblaccTourexpencesstype,
    TblexcisecommodityMaster, TblexciseserMaster, TblfreightMaster, TbloctroiMaster,
)

# Import GST views
# TODO: Implement GST views
# from .gst_views import GSTListView, GSTCreateView, GSTUpdateView, GSTDeleteView

# Import new master views
# TODO: Create these view files
# from .invoice_type_views import InvoiceTypeListView, InvoiceTypeCreateView, InvoiceTypeUpdateView, InvoiceTypeDeleteView
# from .taxable_services_views import TaxableServicesListView, TaxableServicesCreateView, TaxableServicesUpdateView, TaxableServicesDeleteView
# from .loan_master_views import LoanMasterListView, LoanMasterCreateView, LoanMasterUpdateView, LoanMasterDeleteView
from ..forms import (
    AccHeadForm, AdvicePaymentMasterForm, AdvicePaymentDetailFormSet,
    CapitalMasterForm,  # CapitalDetailFormSet removed - no FK in models
    LoanMasterForm, LoanDetailFormSet
)

# HTMX/AJAX Endpoint Views

class GetStatesView(LoginRequiredMixin, View):
    """
    HTMX endpoint to get states for a selected country.
    Converted from FBV to CBV for consistency.
    Requirements: 3.1, 10.3, 12.3
    """

    def get(self, request):
        """Return state dropdown HTML for HTMX."""
        from sys_admin.models import Tblstate

        country_id = request.GET.get('country')

        context = {
            'country_id': country_id,
            'states': Tblstate.objects.filter(cid=country_id).order_by('statename') if country_id else []
        }

        return render(request, 'accounts/partials/state_dropdown.html', context)


class GetStatesJSONView(LoginRequiredMixin, View):
    """
    JSON endpoint to get states for a selected country.
    Used by JavaScript cascading dropdowns.
    """

    def get(self, request):
        """Return states as JSON."""
        from sys_admin.models import Tblstate

        country_id = request.GET.get('country_id')

        if not country_id:
            return JsonResponse({'states': []})

        states = Tblstate.objects.filter(cid_id=country_id).order_by('statename')
        states_list = [{'id': s.sid, 'name': s.statename} for s in states]

        return JsonResponse({'states': states_list})


class GetCitiesView(LoginRequiredMixin, View):
    """
    HTMX endpoint to get cities for a selected state.
    Converted from FBV to CBV for consistency.
    Requirements: 3.1, 10.3, 12.3
    """

    def get(self, request):
        """Return city dropdown HTML for HTMX."""
        from sys_admin.models import Tblcity

        state_id = request.GET.get('state')

        context = {
            'state_id': state_id,
            'cities': Tblcity.objects.filter(sid=state_id).order_by('cityname') if state_id else []
        }

        return render(request, 'accounts/partials/city_dropdown.html', context)


class GetCitiesJSONView(LoginRequiredMixin, View):
    """
    JSON endpoint to get cities for a selected state.
    Used by JavaScript cascading dropdowns.
    """

    def get(self, request):
        """Return cities as JSON."""
        from sys_admin.models import Tblcity

        state_id = request.GET.get('state_id')

        if not state_id:
            return JsonResponse({'cities': []})

        cities = Tblcity.objects.filter(sid_id=state_id).order_by('cityname')
        cities_list = [{'id': c.cityid, 'name': c.cityname} for c in cities]

        return JsonResponse({'cities': cities_list})



# ============================================================================
# Currency Master Views
# ============================================================================

from ..models import TblaccCurrencyMaster
from ..forms import CurrencyForm

class GetAssetSubcategoriesView(LoginRequiredMixin, View):
    """
    AJAX endpoint to get subcategories for selected category.
    Used for cascading dropdown in asset register form.
    """
    
    def get(self, request, *args, **kwargs):
        """Return subcategories as HTML options."""
        category_id = request.GET.get('category')
        
        if category_id:
            subcategories = TblaccAssetSubcategory.objects.filter(
                mid=category_id
            ).order_by('subcategory')
            
            html = '<select name="subcategory" id="id_subcategory" class="w-full px-3 py-2 border border-gray-300 rounded-md">'
            html += '<option value="">Select Subcategory</option>'
            for subcat in subcategories:
                html += f'<option value="{subcat.id}">{subcat.subcategory}</option>'
            html += '</select>'
        else:
            html = '<select name="subcategory" id="id_subcategory" class="w-full px-3 py-2 border border-gray-300 rounded-md" disabled>'
            html += '<option value="">Select Category First</option>'
            html += '</select>'
        
        return HttpResponse(html)



# ============================================================================
# Financial Report Views
# ============================================================================

from ..services import ReportService

