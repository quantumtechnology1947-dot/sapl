"""
Work Order Category & Subcategory views
"""

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime

from ..models import TblsdWoCategory, TblsdWoSubcategory
from ..forms import WoCategoryForm, WoSubCategoryForm
from sys_admin.models import TblfinancialMaster as FinancialYear

class WoCategoryView(LoginRequiredMixin, View):
    """
    Handles CRUD operations for Work Order Categories.
    """
    def get(self, request, cid=None):
        if cid:
            category = get_object_or_404(TblsdWoCategory, cid=cid)
            form = WoCategoryForm(instance=category)
            return render(request, 'sales_distribution/wo_category_form.html', {'form': form, 'category': category})
        else:
            categories = TblsdWoCategory.objects.all().order_by('cname')
            if request.headers.get('HX-Request'):
                return render(request, 'sales_distribution/partials/wo_category_list_partial.html', {'categories': categories})
            return render(request, 'sales_distribution/wo_category_list.html', {'categories': categories, 'form': WoCategoryForm()})

    def post(self, request, cid=None):
        form = WoCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            now = datetime.now()
            category.sysdate = now.strftime('%d-%m-%Y')
            category.systime = now.strftime('%H:%M:%S')
            category.sessionid = str(request.user.id)
            category.compid = 1
            category.finyearid = 1
            category.save()
            messages.success(request, f'Category {category.cname} created successfully.')
            return redirect('sales_distribution:wo-category-list')
        return render(request, 'sales_distribution/wo_category_form.html', {'form': form})

    def put(self, request, cid):
        category = get_object_or_404(TblsdWoCategory, cid=cid)
        form = WoCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category {category.cname} updated successfully.')
            return redirect('sales_distribution:wo-category-list')
        return render(request, 'sales_distribution/wo_category_form.html', {'form': form, 'category': category})

    def delete(self, request, cid):
        category = get_object_or_404(TblsdWoCategory, cid=cid)
        category_name = category.cname

        # FIXED: Check for dependent Work Orders before deleting
        dependent_wo = SdCustWorkorderMaster.objects.filter(cid=cid).exists()
        if dependent_wo:
            messages.error(request, f'Cannot delete category "{category_name}" - Work Orders exist using this category.')
            if request.headers.get('HX-Request'):
                return HttpResponse(status=400)
            return redirect('sales_distribution:wo-category-list')

        category.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        messages.success(request, f'Category {category_name} deleted successfully.')
        return redirect('sales_distribution:wo-category-list')


class WoCategoryCreateView(LoginRequiredMixin, View):
    """
    Handles WO Category creation.
    """
    def get(self, request):
        form = WoCategoryForm()
        return render(request, 'sales_distribution/wo_category_form.html', {'form': form})

    def post(self, request):
        form = WoCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            now = datetime.now()
            category.sysdate = now.strftime('%d-%m-%Y')
            category.systime = now.strftime('%H:%M:%S')
            category.sessionid = str(request.user.id)
            category.compid = 1
            category.finyearid = 1
            category.save()
            messages.success(request, f'Category {category.cname} created successfully.')
            return redirect('sales_distribution:wo-category-list')
        return render(request, 'sales_distribution/wo_category_form.html', {'form': form})


# ============================================================================
# WO SUB-CATEGORY MASTER
# ============================================================================

class WoSubCategoryView(LoginRequiredMixin, View):
    """
    Handles CRUD operations for Work Order Sub-Categories.
    """
    def get(self, request, scid=None):
        if scid:
            subcategory = get_object_or_404(TblsdWoSubcategory, scid=scid)
            form = WoSubCategoryForm(instance=subcategory)
            return render(request, 'sales_distribution/wo_subcategory_form.html', {'form': form, 'subcategory': subcategory})
        else:
            subcategories = TblsdWoSubcategory.objects.select_related().all().order_by('scname')
            categories = TblsdWoCategory.objects.all().order_by('cname')
            if request.headers.get('HX-Request'):
                return render(request, 'sales_distribution/partials/wo_subcategory_list_partial.html', {'subcategories': subcategories})
            return render(request, 'sales_distribution/wo_subcategory_list.html', {'subcategories': subcategories, 'categories': categories, 'form': WoSubCategoryForm()})

    def post(self, request, scid=None):
        form = WoSubCategoryForm(request.POST)
        if form.is_valid():
            subcategory = form.save(commit=False)
            now = datetime.now()
            subcategory.sysdate = now.strftime('%d-%m-%Y')
            subcategory.systime = now.strftime('%H:%M:%S')
            subcategory.sessionid = str(request.user.id)
            subcategory.compid = 1
            subcategory.finyearid = 1
            if form.cleaned_data.get('cid'):
                subcategory.cid = form.cleaned_data['cid'].cid
            subcategory.save()
            messages.success(request, f'Sub-category {subcategory.scname} created successfully.')
            return redirect('sales_distribution:wo-subcategory-list')
        return render(request, 'sales_distribution/wo_subcategory_form.html', {'form': form})

    def put(self, request, scid):
        subcategory = get_object_or_404(TblsdWoSubcategory, scid=scid)
        form = WoSubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            if form.cleaned_data.get('cid'):
                subcategory.cid = form.cleaned_data['cid'].cid
            form.save()
            messages.success(request, f'Sub-category {subcategory.scname} updated successfully.')
            return redirect('sales_distribution:wo-subcategory-list')
        return render(request, 'sales_distribution/wo_subcategory_form.html', {'form': form, 'subcategory': subcategory})

    def delete(self, request, scid):
        subcategory = get_object_or_404(TblsdWoSubcategory, scid=scid)
        subcategory_name = subcategory.scname
        subcategory.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        messages.success(request, f'Sub-category {subcategory_name} deleted successfully.')
        return redirect('sales_distribution:wo-subcategory-list')


class WoSubCategoryCreateView(LoginRequiredMixin, View):
    """
    Handles WO Sub-Category creation.
    """
    def get(self, request):
        form = WoSubCategoryForm()
        categories = TblsdWoCategory.objects.all().order_by('cname')
        return render(request, 'sales_distribution/wo_subcategory_form.html', {'form': form, 'categories': categories})

    def post(self, request):
        form = WoSubCategoryForm(request.POST)
        if form.is_valid():
            subcategory = form.save(commit=False)
            now = datetime.now()
            subcategory.sysdate = now.strftime('%d-%m-%Y')
            subcategory.systime = now.strftime('%H:%M:%S')
            subcategory.sessionid = str(request.user.id)
            subcategory.compid = 1
            subcategory.finyearid = 1
            if form.cleaned_data.get('cid'):
                subcategory.cid = form.cleaned_data['cid'].cid
            subcategory.save()
            messages.success(request, f'Sub-category {subcategory.scname} created successfully.')
            return redirect('sales_distribution:wo-subcategory-list')
        categories = TblsdWoCategory.objects.all().order_by('cname')
        return render(request, 'sales_distribution/wo_subcategory_form.html', {'form': form, 'categories': categories})




