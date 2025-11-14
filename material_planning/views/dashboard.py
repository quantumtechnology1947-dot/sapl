"""
Material Planning Dashboard View

Provides overview statistics and recent plans.
"""

from django.views.generic import TemplateView
from .base import MaterialPlanningBaseMixin
from material_planning.models import TblmpMaterialMaster, TblmpMaterialDetail


class MaterialPlanningDashboardView(MaterialPlanningBaseMixin, TemplateView):
    """Material Planning Dashboard"""
    template_name = 'material_planning/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compid = self.get_compid()
        finyearid = self.get_finyearid()

        plans = TblmpMaterialMaster.objects.filter(compid=compid, finyearid=finyearid)
        context['total_plans'] = plans.count()
        context['recent_plans'] = plans.order_by('-id')[:5]

        all_details = TblmpMaterialDetail.objects.filter(master__compid=compid, master__finyearid=finyearid)
        context['rm_count'] = all_details.filter(rm=1).count()
        context['pro_count'] = all_details.filter(pro=1).count()
        context['fin_count'] = all_details.filter(fin=1).count()

        return context
