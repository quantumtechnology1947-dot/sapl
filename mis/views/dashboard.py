"""
MIS Dashboard and Menu Views

Handles main menu and autocomplete functionality.
"""

from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from sales_distribution.models import SdCustWorkorderMaster, SdCustMaster


class MISTransactionMenuView(TemplateView):
    """MIS Transaction Menu Page"""
    template_name = 'mis/transactions/menu.html'


class AutocompleteView(View):
    """
    AJAX endpoint for autocomplete suggestions
    Supports customer name and WO number autocomplete
    """

    def get(self, request):
        """Return autocomplete suggestions"""
        search_type = request.GET.get('type', '')
        query = request.GET.get('q', '')
        company_id = request.session.get('compid')

        if not query or len(query) < 2:
            return JsonResponse({'results': []})

        results = []

        if search_type == 'customer':
            # Autocomplete customer names
            customers = SdCustMaster.objects.filter(
                compid=company_id,
                customername__icontains=query
            ).values_list('customername', flat=True).distinct()[:10]
            results = [{'value': name, 'label': name} for name in customers if name]

        elif search_type == 'wo':
            # Autocomplete WO numbers
            work_orders = SdCustWorkorderMaster.objects.filter(
                compid=company_id,
                wono__icontains=query
            ).values('wono', 'taskprojecttitle')[:10]
            results = [
                {
                    'value': wo['wono'],
                    'label': f"{wo['wono']} - {wo['taskprojecttitle'][:40] if wo['taskprojecttitle'] else ''}"
                }
                for wo in work_orders if wo['wono']
            ]

        return JsonResponse({'results': results})
