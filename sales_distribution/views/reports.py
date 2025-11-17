"""
Sales Distribution Reports
Implements all reporting functionality for the Sales Distribution module
"""
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Sum, Avg
from datetime import datetime, timedelta

from core.mixins import CompanyFinancialYearMixin
from ..models import (
    SdCustMaster,
    SdCustPoMaster, SdCustPoDetails,
    SdCustQuotationMaster, SdCustQuotationDetails,
    SdCustEnquiryMaster,
    SdCustWorkorderMaster,
)


class ReportsDashboardView(LoginRequiredMixin, CompanyFinancialYearMixin, TemplateView):
    """
    Sales Distribution Reports Dashboard
    Shows summary statistics and quick links to all reports
    """
    template_name = 'sales_distribution/reports/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        # Get counts
        context['total_customers'] = SdCustMaster.objects.filter(compid=compid).count()
        context['total_enquiries'] = SdCustEnquiryMaster.objects.filter(compid=compid, finyearid=finyearid).count()
        context['total_quotations'] = SdCustQuotationMaster.objects.filter(compid=compid, finyearid=finyearid).count()
        context['total_pos'] = SdCustPoMaster.objects.filter(compid=compid, finyearid=finyearid).count()
        context['total_workorders'] = SdCustWorkorderMaster.objects.filter(compid=compid, finyearid=finyearid).count()

        # Recent activity (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%d-%m-%Y')
        context['recent_enquiries'] = SdCustEnquiryMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-enquiryid')[:5]

        context['recent_pos'] = SdCustPoMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-poid')[:5]

        return context


class CustomerMasterReportView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    Customer Master Report
    Lists all customers with filtering and search
    """
    template_name = 'sales_distribution/reports/customer_master.html'
    context_object_name = 'customers'
    paginate_by = 50

    def get_queryset(self):
        compid = self.get_compid()

        qs = SdCustMaster.objects.filter(compid=compid)

        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(customername__icontains=search) |
                Q(customerid__icontains=search) |
                Q(add__icontains=search)
            )

        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            qs = qs.filter(categoryid=category)

        return qs.order_by('customername')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['category'] = self.request.GET.get('category', '')
        return context


class CustomerPOReportView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    Customer PO Report
    Lists all customer purchase orders with details
    """
    template_name = 'sales_distribution/reports/customer_po.html'
    context_object_name = 'pos'
    paginate_by = 50

    def get_queryset(self):
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        qs = SdCustPoMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).select_related()

        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(pono__icontains=search) |
                Q(customerid__icontains=search)
            )

        # Date range filter
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')

        if from_date:
            qs = qs.filter(podate__gte=from_date)
        if to_date:
            qs = qs.filter(podate__lte=to_date)

        # Customer filter
        customer = self.request.GET.get('customer', '')
        if customer:
            qs = qs.filter(customerid=customer)

        return qs.order_by('-poid')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['from_date'] = self.request.GET.get('from_date', '')
        context['to_date'] = self.request.GET.get('to_date', '')
        context['customer'] = self.request.GET.get('customer', '')

        # Get customers for dropdown
        compid = self.get_compid()
        context['customers'] = SdCustMaster.objects.filter(compid=compid).order_by('customername')

        return context


class CustomerQuotationReportView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    Customer Quotation Report
    Lists all quotations with filtering
    """
    template_name = 'sales_distribution/reports/customer_quotation.html'
    context_object_name = 'quotations'
    paginate_by = 50

    def get_queryset(self):
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        qs = SdCustQuotationMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).select_related()

        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(quotationno__icontains=search) |
                Q(customerid__icontains=search)
            )

        # Status filter
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        # Customer filter
        customer = self.request.GET.get('customer', '')
        if customer:
            qs = qs.filter(customerid=customer)

        return qs.order_by('-quotationid')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['customer'] = self.request.GET.get('customer', '')

        # Get customers for dropdown
        compid = self.get_compid()
        context['customers'] = SdCustMaster.objects.filter(compid=compid).order_by('customername')

        return context


class CustomerEnquiryReportView(LoginRequiredMixin, CompanyFinancialYearMixin, ListView):
    """
    Customer Enquiry Report
    Lists all customer enquiries with filtering
    """
    template_name = 'sales_distribution/reports/customer_enquiry.html'
    context_object_name = 'enquiries'
    paginate_by = 50

    def get_queryset(self):
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        qs = SdCustEnquiryMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).select_related()

        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(enquiryno__icontains=search) |
                Q(customerid__icontains=search)
            )

        # Date range filter
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')

        if from_date:
            qs = qs.filter(enquirydate__gte=from_date)
        if to_date:
            qs = qs.filter(enquirydate__lte=to_date)

        # Customer filter
        customer = self.request.GET.get('customer', '')
        if customer:
            qs = qs.filter(customerid=customer)

        return qs.order_by('-enquiryid')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['from_date'] = self.request.GET.get('from_date', '')
        context['to_date'] = self.request.GET.get('to_date', '')
        context['customer'] = self.request.GET.get('customer', '')

        # Get customers for dropdown
        compid = self.get_compid()
        context['customers'] = SdCustMaster.objects.filter(compid=compid).order_by('customername')

        return context
