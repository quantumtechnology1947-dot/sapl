"""
Authorized MCN Views

Handles Authorized MCN CRUD operations - showing Work Orders with MCN records.
"""
from django.views.generic import ListView, CreateView, DetailView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection

from .base import QualityControlBaseMixin
from quality_control.models import TblqcAuthorizedmcn
from quality_control.forms import AuthorizedMCNForm


class AuthorizedMCNListView(QualityControlBaseMixin, TemplateView):
    """List Work Orders that have MCN records"""
    template_name = 'quality_control/authorized_mcn/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get search parameter
        search_query = self.request.GET.get('search', '').strip()
        
        # Get Work Orders that have MCN records
        with connection.cursor() as cursor:
            sql = """
                SELECT DISTINCT
                    wo.WONo,
                    wo.TaskWorkOrderDate,
                    wo.TaskProjectTitle,
                    wo.CustomerId,
                    wo.SCId
                FROM SD_Cust_WorkOrder_Master wo
                INNER JOIN tblPM_MaterialCreditNote_Master mcn ON wo.WONo = mcn.WONo
                WHERE wo.CompId = ?
            """
            
            params = [self.get_compid()]
            
            if search_query:
                sql += " AND wo.WONo LIKE ?"
                search_param = f'%{search_query}%'
                params.append(search_param)
            
            sql += " ORDER BY wo.TaskWorkOrderDate DESC, wo.WONo"
            
            cursor.execute(sql, params)
            
            work_orders = []
            for row in cursor.fetchall():
                work_orders.append({
                    'wo_no': row[0] or '',
                    'wo_date': row[1] or '',
                    'project_title': row[2] or '',
                    'customer_name': row[3] or '',
                    'code': row[4] or ''
                })
        
        context['work_orders'] = work_orders
        context['search_query'] = search_query
        
        return context


class AuthorizedMCNCreateView(QualityControlBaseMixin, CreateView):
    """Create new Authorized MCN"""
    model = TblqcAuthorizedmcn
    form_class = AuthorizedMCNForm
    template_name = 'quality_control/authorized_mcn/form.html'
    success_url = reverse_lazy('quality_control:authorized-mcn-list')

    def form_valid(self, form):
        # Set session metadata
        for field, value in self.get_session_metadata().items():
            setattr(form.instance, field, value)
        messages.success(self.request, 'Authorized MCN created successfully')
        return super().form_valid(form)


class AuthorizedMCNDetailView(QualityControlBaseMixin, DetailView):
    """View Authorized MCN details"""
    model = TblqcAuthorizedmcn
    template_name = 'quality_control/authorized_mcn/detail.html'
    context_object_name = 'authorized_mcn'


class AuthorizedMCNDeleteView(QualityControlBaseMixin, DeleteView):
    """Delete Authorized MCN"""
    model = TblqcAuthorizedmcn
    template_name = 'quality_control/authorized_mcn/delete.html'
    success_url = reverse_lazy('quality_control:authorized-mcn-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Authorized MCN deleted successfully')
        return super().delete(request, *args, **kwargs)
