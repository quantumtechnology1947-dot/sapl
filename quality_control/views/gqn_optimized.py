"""
Optimized GQN List View using raw SQL for performance
"""
from django.views.generic import ListView
from quality_control.models import TblqcMaterialqualityMaster
from quality_control.utils import QueryBuilder, DatabaseQueryOptimizer, paginate_results
from .base import QualityControlBaseMixin


class GoodsQualityNoteListViewOptimized(QualityControlBaseMixin, ListView):
    """
    Optimized GQN List using raw SQL for performance on large datasets
    Uses reusable query builder and database optimizer utilities
    """
    model = TblqcMaterialqualityMaster
    template_name = 'quality_control/gqn/list.html'
    context_object_name = 'gqns'
    paginate_by = 20

    def get_queryset(self):
        """
        Use raw SQL with proper joins for performance.
        Returns a list of dicts instead of model instances for speed.
        """
        # Build search filters
        search_filters = {
            'search_by': self.request.GET.get('search_by', '0'),
            'search_value': self.request.GET.get('search_value', '').strip()
        }
        
        # Build optimized query using reusable query builder
        sql, params = QueryBuilder.build_gqn_list_query(
            self.get_compid(),
            search_filters if search_filters['search_value'] else None
        )
        
        # Execute query using optimized database utility
        return DatabaseQueryOptimizer.execute_raw_sql(sql, params)

    def get_context_data(self, **kwargs):
        """Override to handle list of dicts instead of queryset"""
        # Don't call super() because it expects a queryset
        context = {}
        
        # Get all results
        all_results = self.get_queryset()
        
        # Manual pagination using utility function
        page_number = self.request.GET.get('page', 1)
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1
        
        pagination_data = paginate_results(all_results, page_number, self.paginate_by)
        
        # Add paginated data to context
        context['gqns'] = pagination_data['results']
        context['is_paginated'] = pagination_data['total_count'] > self.paginate_by
        context['page_obj'] = type('obj', (object,), {
            'number': pagination_data['page'],
            'paginator': type('obj', (object,), {
                'num_pages': pagination_data['num_pages'],
                'count': pagination_data['total_count']
            })()
        })()
        
        # Table headers
        context['table_headers'] = [
            {'text': 'SN', 'align': 'right', 'width': 'w-12'},
            {'text': 'Select', 'align': 'center', 'width': 'w-16'},
            {'text': 'Fin Year', 'align': 'center', 'width': 'w-24'},
            {'text': 'GQN No', 'align': 'center', 'width': 'w-28'},
            {'text': 'Date', 'align': 'center', 'width': 'w-24'},
            {'text': 'GRR No', 'align': 'center', 'width': 'w-28'},
            {'text': 'GIN No', 'align': 'center', 'width': 'w-28'},
            {'text': 'PO No', 'align': 'center', 'width': 'w-28'},
            {'text': 'Name of Supplier', 'align': 'left', 'width': 'w-64'},
            {'text': 'Challan No', 'align': 'center', 'width': 'w-28'},
            {'text': 'Challan Date', 'align': 'center', 'width': 'w-28'},
        ]
        
        # Format rows
        start_idx = (pagination_data['page'] - 1) * self.paginate_by
        rows = []
        for idx, gqn in enumerate(pagination_data['results'], start=start_idx + 1):
            rows.append({
                'cells': [
                    idx,
                    'NA',
                    gqn.get('finyearname') or '-',
                    gqn.get('gqnno') or '-',
                    gqn.get('sysdate') or '-',
                    gqn.get('grrno') or '-',
                    gqn.get('ginno') or '-',
                    gqn.get('pono_from_gin') or '-',
                    gqn.get('suppliername') or '-',
                    gqn.get('challanno') or '-',
                    gqn.get('challandate') or '-',
                ]
            })
        
        context['rows'] = rows
        context['search_options'] = [
            {'value': '0', 'label': 'Supplier Name'},
            {'value': '1', 'label': 'GQN No'},
            {'value': '2', 'label': 'GRR No'},
            {'value': '3', 'label': 'PO No'},
        ]
        context['gqn_list_url'] = '/quality/gqn/'
        context['view'] = self
        
        return context
