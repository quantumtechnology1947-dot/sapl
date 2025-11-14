"""
Product Master views
"""

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from ..models import SdCustWorkorderProductsDetails
from sys_admin.models import TblfinancialMaster as FinancialYear



# ============================================================================
# WO DISPATCH
# ============================================================================




# ============================================================================
# PRODUCT MASTER
# ============================================================================

class ProductView(LoginRequiredMixin, View):
    """
    Handles CRUD operations for Products.
    """
    def get(self, request, itemcode=None):
        if itemcode:
            product = SdCustWorkorderProductsDetails.objects.filter(itemcode=itemcode).values('itemcode', 'description').first()
            if product:
                form = ProductForm(initial=product)
                return render(request, 'sales_distribution/partials/product_edit_row.html', {'form': form, 'product': product})
            return HttpResponse(status=404)
        else:
            products = SdCustWorkorderProductsDetails.objects.filter(itemcode__isnull=False).exclude(itemcode='').values('itemcode', 'description').distinct().order_by('itemcode')
            search = request.GET.get('search', '')
            if search:
                products = products.filter(Q(itemcode__icontains=search) | Q(description__icontains=search))
            return render(request, 'sales_distribution/product_list.html', {'products': products, 'search_query': search})

    def post(self, request):
        form = ProductForm(request.POST)
        if form.is_valid():
            product = {
                'itemcode': form.cleaned_data['itemcode'],
                'description': form.cleaned_data['description']
            }
            messages.success(request, f'Product {product["itemcode"]} created successfully.')
            if request.headers.get('HX-Request'):
                return render(request, 'sales_distribution/partials/product_row.html', {'product': product})
            return redirect('sales_distribution:product-list')
        return render(request, 'sales_distribution/product_list.html', {'form': form})

    def put(self, request, itemcode):
        form = ProductForm(request.POST)
        if form.is_valid():
            SdCustWorkorderProductsDetails.objects.filter(itemcode=itemcode).update(description=form.cleaned_data['description'])
            product = {
                'itemcode': itemcode,
                'description': form.cleaned_data['description']
            }
            messages.success(request, f'Product {itemcode} updated successfully.')
            if request.headers.get('HX-Request'):
                return render(request, 'sales_distribution/partials/product_row.html', {'product': product})
            return redirect('sales_distribution:product-list')
        return render(request, 'sales_distribution/partials/product_edit_row.html', {'form': form})

    def delete(self, request, itemcode):
        usage_count = SdCustWorkorderProductsDetails.objects.filter(itemcode=itemcode).count()
        if usage_count > 0:
            messages.error(request, f'Cannot delete product. It is used in {usage_count} work order(s).')
            return HttpResponse(status=400)
        messages.success(request, f'Product {itemcode} deleted successfully.')
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return redirect('sales_distribution:product-list')




