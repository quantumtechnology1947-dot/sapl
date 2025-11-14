"""
AI-Powered SPR Intelligence Service - Using Django ORM

SPR (Special Purpose Requisition) differs from PR:
- PR: Work Order based (production materials from BOM)
- SPR: Department/Business Group based (services, labor, expenses)

This service analyzes historical SPR data to intelligently suggest:
- Common services/items used by each department
- Best suppliers for account head categories (Labour, With Material, Expenses, Service Provider)
- Recommended rates and discounts
- Confidence scores based on usage frequency
"""

import os
from collections import defaultdict
from datetime import datetime
from django.db.models import Count, Avg, Max, Q, F
from django.db.models.functions import Coalesce

# Import models
from material_management.models import SPRMaster, SPRDetails, Supplier, RateRegister
from design.models import TbldgItemMaster
from sys_admin.models import UnitMaster
from human_resource.models import Businessgroup
from accounts.models import Acchead

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class EnhancedSPRIntelligenceService:
    """
    AI-Powered Special Purpose Requisition Intelligence System

    Analyzes historical SPR data to suggest:
    - Common items/services for each department
    - Best suppliers for each account head category
    - Recommended rates based on historical patterns
    """

    def __init__(self):
        """Initialize the service and configure Gemini AI"""
        self.ai_model = None
        if genai:
            try:
                # Read API key from api_key.txt
                api_key_file = os.path.join(os.path.dirname(__file__), '..', 'api_key.txt')
                if os.path.exists(api_key_file):
                    with open(api_key_file, 'r') as f:
                        api_key = f.read().strip()
                    genai.configure(api_key=api_key)
                    self.ai_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception as e:
                print(f"AI initialization warning: {e}")

    def analyze_department_for_spr(self, dept_id, ah_category, comp_id):
        """
        Main entry point: Analyze Department/Business Group and suggest SPR items

        Args:
            dept_id (int): Business Group ID (or None for WO-based)
            ah_category (str): Account Head category ('Labour', 'With Material', 'Expenses', 'Ser. Provider')
            comp_id (int): Company ID

        Returns:
            list: List of enriched item suggestions with supplier recommendations
        """
        # Step 1: Build comprehensive supplier-item intelligence for this department and AH category
        supplier_intelligence = self._build_department_supplier_intelligence(dept_id, ah_category, comp_id)
        print(f"[SPR AI] Analyzed {len(supplier_intelligence)} item-supplier relationships for dept {dept_id}, AH category: {ah_category}")

        # Step 2: Get most commonly used items for this department
        common_items = self._get_common_items_for_department(dept_id, ah_category, comp_id, limit=20)
        print(f"[SPR AI] Found {len(common_items)} common items for this department/category")

        # Step 3: For each common item, find best supplier
        enriched_items = []
        for item in common_items:
            item_id = item['item_id']

            # Get supplier intelligence for this item
            item_intel = supplier_intelligence.get(item_id, {})
            suppliers = item_intel.get('suppliers', {})

            # Find best supplier (most frequently used)
            best_supplier = self._select_best_supplier(suppliers)

            # Get alternative suppliers
            alternatives = self._get_alternative_suppliers(suppliers, best_supplier)

            # If no historical data, check Rate Register
            if not best_supplier:
                rate_data = self._get_rate_register_data(item_id, comp_id)
                confidence = 30
                reasoning = "New item for this department - no historical supplier data. Rate from Rate Register."
            else:
                rate_data = {
                    'rate': best_supplier['avg_rate'],
                    'discount': best_supplier['avg_discount']
                }
                confidence = self._calculate_confidence(best_supplier['usage_count'])
                reasoning = f"Used {best_supplier['usage_count']} times by this department with avg rate Rs.{best_supplier['avg_rate']:.2f}"

            # Build enriched item
            enriched_item = {
                'item_id': item_id,
                'item_code': item.get('item_code', 'NO-CODE'),
                'item_desc': item['item_desc'],
                'uom': item.get('uom', 'PCS'),
                'suggested_qty': item.get('avg_qty', 1),
                'suggested_supplier_id': best_supplier['supplier_id'] if best_supplier else None,
                'suggested_supplier_name': best_supplier['name'] if best_supplier else 'NO HISTORY - Manual Selection Required',
                'suggested_rate': rate_data.get('rate', 0),
                'suggested_discount': rate_data.get('discount', 0),
                'confidence': confidence,
                'reasoning': reasoning,
                'alternative_suppliers': alternatives,
                'usage_count': item.get('usage_count', 0)
            }

            enriched_items.append(enriched_item)

        # Step 4: Optionally enhance with AI insights
        if enriched_items and self.ai_model:
            try:
                self._get_ai_insights_spr(dept_id, ah_category, enriched_items, comp_id)
                print(f"[SPR AI] AI provided additional insights")
            except Exception as e:
                print(f"[SPR AI] AI insights skipped: {e}")

        print(f"\n[SPR AI] Analysis complete: {len(enriched_items)} items with supplier suggestions\n")
        return enriched_items

    def _build_department_supplier_intelligence(self, dept_id, ah_category, comp_id):
        """
        Build supplier-item intelligence map for specific department and AH category

        Returns:
            dict: {
                item_id: {
                    'suppliers': {
                        'SUPP001': {
                            'name': 'Supplier Name',
                            'usage_count': 5,
                            'avg_rate': 200.00,
                            'avg_discount': 3.0
                        }
                    }
                }
            }
        """
        # Get AH IDs for this category
        ah_ids = list(Acchead.objects.filter(category=ah_category).values_list('id', flat=True))

        # Get SPR Master IDs for this company
        spr_master_ids = list(SPRMaster.objects.filter(comp_id=comp_id).values_list('spr_id', flat=True))

        # Build filter for SPR Details
        filters = Q(m_id__in=spr_master_ids, item_id__isnull=False, supplier_id__isnull=False)

        # Add department filter if provided
        if dept_id:
            filters &= Q(dept_id=dept_id)

        # Add account head filter
        if ah_ids:
            filters &= Q(ah_id__in=ah_ids)

        # Query historical SPR data with aggregations
        spr_analysis = (
            SPRDetails.objects
            .filter(filters)
            .values('item_id', 'supplier_id')
            .annotate(
                usage_count=Count('id'),
                avg_rate=Avg('rate'),
                avg_discount=Avg('discount')
            )
            .order_by('item_id', '-usage_count')
        )

        # Build intelligence map
        intelligence_map = defaultdict(lambda: {'suppliers': {}})

        for record in spr_analysis:
            item_id = record['item_id']
            supplier_id = record['supplier_id']

            # Get supplier name
            try:
                supplier = Supplier.objects.get(supplier_id=supplier_id, comp_id=comp_id)
                supplier_name = supplier.supplier_name
            except Supplier.DoesNotExist:
                supplier_name = f'Supplier-{supplier_id}'

            # Store supplier intelligence
            intelligence_map[item_id]['suppliers'][supplier_id] = {
                'supplier_id': supplier_id,
                'name': supplier_name,
                'usage_count': record['usage_count'],
                'avg_rate': float(record['avg_rate']) if record['avg_rate'] else 0,
                'avg_discount': float(record['avg_discount']) if record['avg_discount'] else 0
            }

        return intelligence_map

    def _get_common_items_for_department(self, dept_id, ah_category, comp_id, limit=20):
        """
        Get most commonly used items for this department and account head category

        Returns:
            list: List of items with usage statistics
        """
        # Get AH IDs for this category
        ah_ids = list(Acchead.objects.filter(category=ah_category).values_list('id', flat=True))

        # Get SPR Master IDs for this company
        spr_master_ids = list(SPRMaster.objects.filter(comp_id=comp_id).values_list('spr_id', flat=True))

        # Build filter
        filters = Q(m_id__in=spr_master_ids, item_id__isnull=False)

        # Add department filter if provided
        if dept_id:
            filters &= Q(dept_id=dept_id)

        # Add account head filter
        if ah_ids:
            filters &= Q(ah_id__in=ah_ids)

        # Get common items
        common_items_query = (
            SPRDetails.objects
            .filter(filters)
            .values('item_id')
            .annotate(
                usage_count=Count('id'),
                avg_qty=Avg('qty'),
                avg_rate=Avg('rate')
            )
            .order_by('-usage_count')[:limit]
        )

        items = []
        for record in common_items_query:
            item_id = record['item_id']

            # Get item details
            try:
                item = TbldgItemMaster.objects.get(id=item_id)
                item_code = item.itemcode or 'NO-CODE'
                item_desc = item.manfdesc or 'No description'

                # Get UOM
                uom_symbol = 'PCS'
                if item.uombasic:
                    try:
                        unit = UnitMaster.objects.get(id=item.uombasic)
                        uom_symbol = unit.symbol or 'PCS'
                    except UnitMaster.DoesNotExist:
                        pass
            except TbldgItemMaster.DoesNotExist:
                item_code = 'NO-CODE'
                item_desc = f'Item-{item_id} (No longer in system)'
                uom_symbol = 'PCS'

            items.append({
                'item_id': item_id,
                'item_code': item_code,
                'item_desc': item_desc,
                'uom': uom_symbol,
                'usage_count': record['usage_count'],
                'avg_qty': float(record['avg_qty']) if record['avg_qty'] else 1,
                'avg_rate': float(record['avg_rate']) if record['avg_rate'] else 0
            })

        return items

    def _select_best_supplier(self, suppliers):
        """Select best supplier based on usage frequency"""
        if not suppliers:
            return None

        sorted_suppliers = sorted(
            suppliers.values(),
            key=lambda x: x['usage_count'],
            reverse=True
        )

        return sorted_suppliers[0] if sorted_suppliers else None

    def _get_alternative_suppliers(self, suppliers, best_supplier, limit=3):
        """Get alternative supplier options"""
        if not suppliers or not best_supplier:
            return []

        alternatives = [
            s for s in suppliers.values()
            if s['supplier_id'] != best_supplier['supplier_id']
        ]

        alternatives.sort(key=lambda x: x['usage_count'], reverse=True)
        return alternatives[:limit]

    def _calculate_confidence(self, usage_count):
        """Calculate confidence score based on usage frequency"""
        if usage_count >= 10:
            return 95
        elif usage_count >= 5:
            return 80
        elif usage_count >= 3:
            return 65
        elif usage_count >= 1:
            return 50
        else:
            return 30

    def _get_rate_register_data(self, item_id, comp_id):
        """Get rate from Rate Register as fallback"""
        # First check for flagged (locked) rate
        flagged_rate = RateRegister.objects.filter(
            item_id=item_id,
            comp_id=comp_id,
            flag=1
        ).first()

        if flagged_rate:
            return {
                'rate': float(flagged_rate.rate) if flagged_rate.rate else 0.00,
                'discount': float(flagged_rate.discount) if flagged_rate.discount else 0.00
            }

        # Otherwise get minimum discounted rate
        rates = RateRegister.objects.filter(
            item_id=item_id,
            comp_id=comp_id
        ).exclude(rate__isnull=True)

        if rates.exists():
            min_rate = min(rates, key=lambda r: r.amount, default=None)
            if min_rate:
                return {
                    'rate': float(min_rate.rate) if min_rate.rate else 0.00,
                    'discount': float(min_rate.discount) if min_rate.discount else 0.00
                }

        return {'rate': 0.00, 'discount': 0.00}

    def _get_ai_insights_spr(self, dept_id, ah_category, enriched_items, comp_id):
        """
        Use Gemini AI to provide additional insights for SPR

        Analyzes department spending patterns and provides procurement recommendations
        """
        if not self.ai_model:
            return

        # Get department name
        dept_name = "General"
        if dept_id:
            try:
                dept = Businessgroup.objects.get(id=dept_id)
                dept_name = dept.name or f"Dept-{dept_id}"
            except Businessgroup.DoesNotExist:
                pass

        # Prepare data for AI
        items_summary = []
        for item in enriched_items[:10]:  # Top 10 items
            items_summary.append({
                'description': item['item_desc'],
                'suggested_supplier': item['suggested_supplier_name'],
                'suggested_rate': item['suggested_rate'],
                'confidence': item['confidence'],
                'usage_count': item.get('usage_count', 0)
            })

        prompt = f"""
You are a procurement analyst for an ERP system. Analyze this Special Purpose Requisition (SPR) data:

Department: {dept_name}
Account Head Category: {ah_category}
Items Being Requisitioned: {len(enriched_items)}

Top Items:
{items_summary}

Provide a concise analysis (3-4 bullet points):
1. **Procurement Risk Assessment**: Evaluate the risk level based on supplier confidence and item history.
2. **Items Needing Special Attention**: Identify items that require manual review or have low confidence.
3. **Budget Optimization Suggestions**: Recommend ways to optimize spending for this department.

Keep each point to 1-2 sentences maximum.
"""

        try:
            response = self.ai_model.generate_content(prompt)
            ai_insights = response.text.strip()
            print(f"\nAI Insights: {ai_insights}\n")

            # Store AI insights in first item for template access
            if enriched_items:
                enriched_items[0]['ai_insights'] = ai_insights
        except Exception as e:
            print(f"AI insights generation failed: {e}")
