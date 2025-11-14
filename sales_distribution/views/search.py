"""
Universal Search views
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime

from ..models import (
    SdCustMaster, SdCustEnquiryMaster, SdCustQuotationMaster,
    SdCustPoMaster, SdCustWorkorderMaster, SdCustWorkorderDispatch,
    SdCustWorkorderProductsDetails
)
from sys_admin.models import TblfinancialMaster as FinancialYear

class UniversalSearchView(LoginRequiredMixin, TemplateView):
    """
    Universal search across all Sales & Distribution entities.
    Searches: Customers, Enquiries, Quotations, POs, Work Orders, Releases, Dispatches,
              WO Categories, WO Sub-categories, Products
    Requirements: 10.1, 10.2, 10.3
    """
    template_name = 'sales_distribution/universal_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '').strip()
        context['search_query'] = search_query

        if not search_query or len(search_query) < 2:
            context['results'] = {}
            context['total_results'] = 0
            return context

        results = {}

        # Search Customers
        customers = SdCustMaster.objects.filter(
            Q(customername__icontains=search_query) |
            Q(customercode__icontains=search_query) |
            Q(contactperson__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(regdcontactno__icontains=search_query)
        )[:10]
        if customers:
            results['customers'] = customers

        # Search Enquiries
        enquiries = SdCustEnquiryMaster.objects.filter(
            Q(customername__icontains=search_query) |
            Q(enquiryfor__icontains=search_query) |
            Q(regdcontactno__icontains=search_query)
        )[:10]
        if enquiries:
            results['enquiries'] = enquiries

        # Search Quotations
        quotations = SdCustQuotationMaster.objects.select_related('enqid').filter(
            Q(quotationno__icontains=search_query) |
            Q(customerid__icontains=search_query) |
            Q(enqid__customername__icontains=search_query)
        )[:10]
        if quotations:
            results['quotations'] = quotations

        # Search Purchase Orders
        pos = SdCustPoMaster.objects.select_related('enqid').filter(
            Q(pono__icontains=search_query) |
            Q(customerid__icontains=search_query) |
            Q(enqid__customername__icontains=search_query)
        )[:10]
        if pos:
            results['pos'] = pos

        # Search Work Orders
        workorders = SdCustWorkorderMaster.objects.filter(
            Q(wono__icontains=search_query) |
            Q(pono__icontains=search_query) |
            Q(customerid__icontains=search_query)
        )[:10]
        if workorders:
            results['workorders'] = workorders

        # Search Releases
        releases = SdCustWorkorderRelease.objects.filter(
            Q(wrno__icontains=search_query) |
            Q(wono__icontains=search_query) |
            Q(itemid__icontains=search_query)
        )[:10]
        if releases:
            results['releases'] = releases

        # Search Dispatches
        dispatches = SdCustWorkorderDispatch.objects.filter(
            Q(dano__icontains=search_query) |
            Q(wrno__icontains=search_query) |
            Q(itemid__icontains=search_query)
        )[:10]
        if dispatches:
            results['dispatches'] = dispatches

        # Search WO Categories
        categories = TblsdWoCategory.objects.filter(
            Q(cname__icontains=search_query) |
            Q(symbol__icontains=search_query)
        )[:10]
        if categories:
            results['categories'] = categories

        # Search WO Sub-Categories
        subcategories = TblsdWoSubcategory.objects.filter(
            Q(scname__icontains=search_query) |
            Q(symbol__icontains=search_query)
        )[:10]
        if subcategories:
            results['subcategories'] = subcategories

        # Count total results
        total_results = sum(len(result_list) for result_list in results.values())

        context['results'] = results
        context['total_results'] = total_results

        return context




