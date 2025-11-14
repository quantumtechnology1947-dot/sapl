"""
Enhanced AI-Powered PR Intelligence Service - Using Django ORM
This service uses Django ORM instead of raw SQL queries for better maintainability
"""

import os
from collections import defaultdict
from datetime import datetime
from django.db.models import Count, Avg, Max, Q, F
from django.db.models.functions import Coalesce

# Import models
from material_management.models import PRMaster, PRDetails, Supplier, RateRegister
from design.models import TbldgBomMaster, TbldgItemMaster
from sys_admin.models import UnitMaster

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class EnhancedPRIntelligenceServiceORM:
    """
    AI-Powered Purchase Requisition Intelligence System using Django ORM

    This service analyzes historical PR data to intelligently suggest:
    - Best suppliers for each item based on historical patterns
    - Recommended rates and discounts
    - Confidence scores based on usage frequency
    - Alternative supplier options
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

    def analyze_work_order_for_pr(self, wo_no, comp_id):
        """
        Main entry point: Analyze Work Order and return intelligent PR suggestions

        Args:
            wo_no (str): Work Order Number
            comp_id (int): Company ID

        Returns:
            list: List of enriched item suggestions with supplier recommendations
        """
        # Step 1: Get BOM items for the Work Order
        bom_items = self._get_bom_items_orm(wo_no, comp_id)
        if not bom_items:
            print(f"No BOM items found for WO {wo_no}")
            return []

        print(f"[OK] Found {len(bom_items)} BOM items")

        # Step 2: Build comprehensive supplier-item intelligence using ORM
        supplier_intelligence = self._build_supplier_intelligence_orm(comp_id)
        print(f"[OK] Analyzed {len(supplier_intelligence)} item-supplier relationships")

        # Step 3: For each BOM item, find best supplier based on historical data
        enriched_items = []
        for item in bom_items:
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
                rate_data = self._get_rate_register_data_orm(item_id, comp_id)
                confidence = 30
                reasoning = "New item - no historical supplier data. Rate from Rate Register."
            else:
                rate_data = {
                    'rate': best_supplier['avg_rate'],
                    'discount': best_supplier['avg_discount']
                }
                confidence = self._calculate_confidence(best_supplier['usage_count'])
                reasoning = f"Used {best_supplier['usage_count']} times historically with avg rate Rs.{best_supplier['avg_rate']:.2f}"

            # Build enriched item
            enriched_item = {
                'item_id': item_id,
                'item_code': item['item_code'],
                'item_desc': item['item_desc'],
                'uom': item['uom'],
                'qty': item['qty'],
                'suggested_supplier_id': best_supplier['supplier_id'] if best_supplier else None,
                'suggested_supplier_name': best_supplier['name'] if best_supplier else 'NO HISTORY - Manual Selection Required',
                'suggested_rate': rate_data.get('rate', 0),
                'suggested_discount': rate_data.get('discount', 0),
                'confidence': confidence,
                'reasoning': reasoning,
                'alternative_suppliers': alternatives
            }

            enriched_items.append(enriched_item)

        # Step 4: Optionally enhance with AI insights
        if enriched_items and self.ai_model:
            try:
                self._get_ai_insights(wo_no, enriched_items, comp_id)
                print(f"[OK] AI provided additional insights")
            except Exception as e:
                print(f"AI insights skipped: {e}")

        print(f"\n[OK] Analysis complete: {len(enriched_items)} items with supplier suggestions\n")
        return enriched_items

    def _get_bom_items_orm(self, wo_no, comp_id):
        """
        Get BOM items for Work Order using Django ORM

        Returns:
            list: List of items with item_id, item_code, description, uom, qty
        """
        from django.db.models import Sum

        bom_queryset = (
            TbldgBomMaster.objects
            .filter(wono=wo_no, compid=comp_id, ecnflag=0)
            .select_related('itemid')  # Join with Item Master
            .values(
                'itemid__id',
                'itemid__itemcode',
                'itemid__manfdesc',
                'itemid__uombasic'
            )
            .annotate(
                total_qty=Sum('qty')
            )
        )

        items = []
        for bom in bom_queryset:
            # Get UOM symbol
            uom_id = bom['itemid__uombasic']
            uom_symbol = 'PCS'
            if uom_id:
                try:
                    unit = UnitMaster.objects.get(id=uom_id)
                    uom_symbol = unit.symbol or 'PCS'
                except UnitMaster.DoesNotExist:
                    pass

            items.append({
                'item_id': bom['itemid__id'],
                'item_code': bom['itemid__itemcode'] or '',
                'item_desc': bom['itemid__manfdesc'] or 'No description',
                'uom': uom_symbol,
                'qty': float(bom['total_qty']) if bom['total_qty'] else 0
            })

        return items

    def _build_supplier_intelligence_orm(self, comp_id):
        """
        Build comprehensive supplier-item intelligence map using Django ORM

        Analyzes all historical PRs to find which suppliers are used for which items

        Returns:
            dict: {
                item_id: {
                    'item_code': 'H024-008-000',
                    'suppliers': {
                        'SUPP001': {
                            'name': 'Supplier Name',
                            'usage_count': 9,
                            'avg_rate': 150.50,
                            'avg_discount': 5.0,
                            'last_used': '2025-01-15'
                        }
                    }
                }
            }
        """
        # Get list of PR Master IDs for this company
        pr_master_ids = list(PRMaster.objects.filter(comp_id=comp_id).values_list('pr_id', flat=True))

        # Query historical PR data with aggregations
        pr_analysis = (
            PRDetails.objects
            .filter(
                m_id__in=pr_master_ids,
                item_id__isnull=False,
                supplier_id__isnull=False
            )
            .values('item_id', 'supplier_id')
            .annotate(
                usage_count=Count('id'),
                avg_rate=Avg('rate'),
                avg_discount=Avg('discount')
            )
            .order_by('item_id', '-usage_count')
        )

        # Build intelligence map
        intelligence_map = defaultdict(lambda: {'item_code': None, 'suppliers': {}})

        for record in pr_analysis:
            item_id = record['item_id']
            supplier_id = record['supplier_id']

            # Get item code
            try:
                item = TbldgItemMaster.objects.get(id=item_id)
                intelligence_map[item_id]['item_code'] = item.itemcode
            except TbldgItemMaster.DoesNotExist:
                intelligence_map[item_id]['item_code'] = f'Item-{item_id}'

            # Get supplier name
            try:
                supplier = Supplier.objects.get(supplier_id=supplier_id)
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

    def _select_best_supplier(self, suppliers):
        """
        Select best supplier based on usage frequency

        Args:
            suppliers (dict): Dictionary of supplier_id -> supplier_info

        Returns:
            dict: Best supplier info or None
        """
        if not suppliers:
            return None

        # Sort by usage count (descending)
        sorted_suppliers = sorted(
            suppliers.values(),
            key=lambda x: x['usage_count'],
            reverse=True
        )

        return sorted_suppliers[0] if sorted_suppliers else None

    def _get_alternative_suppliers(self, suppliers, best_supplier, limit=3):
        """
        Get alternative supplier options

        Args:
            suppliers (dict): Dictionary of supplier_id -> supplier_info
            best_supplier (dict): The primary suggested supplier
            limit (int): Maximum number of alternatives

        Returns:
            list: List of alternative supplier info
        """
        if not suppliers or not best_supplier:
            return []

        # Get all suppliers except the best one
        alternatives = [
            s for s in suppliers.values()
            if s['supplier_id'] != best_supplier['supplier_id']
        ]

        # Sort by usage count
        alternatives.sort(key=lambda x: x['usage_count'], reverse=True)

        return alternatives[:limit]

    def _calculate_confidence(self, usage_count):
        """
        Calculate confidence score based on usage frequency

        Args:
            usage_count (int): Number of times this Item-Supplier pair was used

        Returns:
            int: Confidence score (0-100)
        """
        if usage_count >= 5:
            return 90  # Very High Confidence
        elif usage_count >= 3:
            return 75  # High Confidence
        elif usage_count >= 2:
            return 60  # Medium Confidence
        elif usage_count == 1:
            return 45  # Low Confidence
        else:
            return 30  # Very Low (new item)

    def _get_rate_register_data_orm(self, item_id, comp_id):
        """
        Get rate from Rate Register using Django ORM (prioritize flagged rates)

        Args:
            item_id (int): Item ID
            comp_id (int): Company ID

        Returns:
            dict: {'rate': float, 'discount': float, 'is_locked': bool} or empty dict
        """
        try:
            rate_record = (
                RateRegister.objects
                .filter(item_id=item_id, comp_id=comp_id)
                .order_by('-flag', '-id')  # Prioritize flagged rates, then latest
                .first()
            )

            if rate_record:
                return {
                    'rate': float(rate_record.rate) if rate_record.rate else 0,
                    'discount': float(rate_record.discount) if rate_record.discount else 0,
                    'is_locked': rate_record.flag == 1
                }
        except Exception as e:
            print(f"Rate Register lookup error for item {item_id}: {e}")

        return {}

    def _get_supplier_name_orm(self, supplier_id, comp_id):
        """
        Get supplier name using Django ORM

        Args:
            supplier_id (str): Supplier ID
            comp_id (int): Company ID

        Returns:
            str: Supplier name or None
        """
        if not supplier_id:
            return None

        try:
            supplier = Supplier.objects.get(supplier_id=supplier_id, comp_id=comp_id)
            return supplier.supplier_name
        except Supplier.DoesNotExist:
            return None

    def _get_ai_insights(self, wo_no, enriched_items, comp_id):
        """
        Optional: Use Gemini AI for additional insights and validation

        Args:
            wo_no (str): Work Order Number
            enriched_items (list): Items with supplier suggestions
            comp_id (int): Company ID
        """
        if not self.ai_model:
            return

        # Prepare summary for AI
        summary = f"Work Order: {wo_no}\n"
        summary += f"Total Items: {len(enriched_items)}\n\n"
        summary += "Sample Items:\n"

        for item in enriched_items[:5]:
            summary += f"- {item['item_code']}: {item['item_desc'][:50]}\n"
            summary += f"  Qty: {item['qty']} {item['uom']}\n"
            summary += f"  Suggested: {item['suggested_supplier_name']} @ Rs.{item['suggested_rate']}\n"
            summary += f"  Confidence: {item['confidence']}%\n\n"

        prompt = f"""
You are an ERP procurement assistant. Analyze this Purchase Requisition:

{summary}

Provide:
1. Overall procurement risk assessment
2. Any items that need special attention
3. Budget optimization suggestions

Keep response concise (2-3 sentences).
"""

        try:
            response = self.ai_model.generate_content(prompt)
            # Store AI insights (could be added to session or returned)
            print(f"AI Insights: {response.text}")
        except Exception as e:
            print(f"AI insights error: {e}")
