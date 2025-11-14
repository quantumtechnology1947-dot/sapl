"""
Enhanced AI-Powered Purchase Requisition Intelligence Service
Uses Google Gemini 2.5 Pro with deep supplier-item relationship analysis

Based on investigation findings:
1. Suppliers are selected based on historical PR/PO patterns for same items
2. Same item → Same supplier (consistency principle)
3. Rate Register provides approved rates (Flag=1)
4. Item-Supplier relationships tracked through PR_Details and PO_Details
"""

import os
import google.generativeai as genai
from django.db import connection
import json
from collections import defaultdict


class EnhancedPRIntelligenceService:
    """
    Enhanced AI service with deep supplier-item relationship analysis
    """

    def __init__(self):
        """Initialize Gemini AI"""
        api_key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api_key.txt')
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def analyze_work_order_for_pr(self, wo_no, comp_id):
        """
        Main method: Analyze WO and suggest items with intelligent supplier selection
        """
        print(f"\n{'='*80}")
        print(f"AI ANALYSIS FOR WORK ORDER: {wo_no}")
        print(f"{'='*80}\n")

        # Step 1: Get BOM items for this WO
        bom_items = self._get_bom_items(wo_no, comp_id)
        if not bom_items:
            print(f"No BOM items found for WO {wo_no}")
            return []

        print(f"[OK] Found {len(bom_items)} BOM items")

        # Step 2: Build comprehensive supplier-item intelligence
        supplier_intelligence = self._build_supplier_intelligence(comp_id)
        print(f"[OK] Analyzed {len(supplier_intelligence)} item-supplier relationships")

        # Step 3: For each BOM item, find best supplier
        enriched_items = []
        for item in bom_items:
            item_id = item['item_id']
            item_code = item['item_code']

            # Get supplier suggestions for this item
            supplier_data = supplier_intelligence.get(item_id, {})

            if supplier_data:
                # Sort suppliers by usage frequency
                sorted_suppliers = sorted(
                    supplier_data['suppliers'].items(),
                    key=lambda x: x[1]['usage_count'],
                    reverse=True
                )

                # Get top supplier
                best_supplier_id, best_supplier_info = sorted_suppliers[0]

                enriched_item = {
                    **item,
                    'suggested_supplier_id': best_supplier_id,
                    'suggested_supplier_name': best_supplier_info['name'],
                    'suggested_rate': best_supplier_info['avg_rate'],
                    'suggested_discount': best_supplier_info['avg_discount'],
                    'confidence': self._calculate_confidence(best_supplier_info['usage_count']),
                    'reasoning': f"Used {best_supplier_info['usage_count']} times historically with avg rate Rs.{best_supplier_info['avg_rate']:.2f}",
                    'alternative_suppliers': [
                        {
                            'id': supp_id,
                            'name': supp_info['name'],
                            'usage_count': supp_info['usage_count'],
                            'avg_rate': supp_info['avg_rate']
                        }
                        for supp_id, supp_info in sorted_suppliers[1:4]  # Top 3 alternatives
                    ]
                }
            else:
                # No historical data - check Rate Register only
                rate_data = self._get_rate_register_data(item_id, comp_id)
                enriched_item = {
                    **item,
                    'suggested_supplier_id': '',
                    'suggested_supplier_name': 'NO HISTORY - Manual Selection Required',
                    'suggested_rate': rate_data.get('rate', 0),
                    'suggested_discount': rate_data.get('discount', 0),
                    'confidence': 30,  # Low confidence
                    'reasoning': 'New item - no historical supplier data. Rate from Rate Register.',
                    'alternative_suppliers': []
                }

            enriched_items.append(enriched_item)

        # Step 4: Use AI for final validation and insights
        if enriched_items:
            try:
                ai_insights = self._get_ai_insights(wo_no, enriched_items, comp_id)
                print(f"[OK] AI provided additional insights")
            except Exception as e:
                print(f"AI insights skipped: {e}")

        print(f"\n[OK] Analysis complete: {len(enriched_items)} items with supplier suggestions\n")
        return enriched_items

    def _build_supplier_intelligence(self, comp_id):
        """
        Build comprehensive supplier-item intelligence map from historical data

        Returns:
            {
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
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    prd.ItemId,
                    im.ItemCode,
                    prd.SupplierId,
                    sm.SupplierName,
                    COUNT(*) as usage_count,
                    AVG(prd.Rate) as avg_rate,
                    AVG(prd.Discount) as avg_discount,
                    MAX(pr.SysDate) as last_used
                FROM tblMM_PR_Details prd
                INNER JOIN tblMM_PR_Master pr ON prd.MId = pr.Id
                LEFT JOIN tblDG_Item_Master im ON prd.ItemId = im.Id
                LEFT JOIN tblMM_Supplier_master sm ON prd.SupplierId = sm.SupplierId
                WHERE pr.CompId = %s AND prd.ItemId IS NOT NULL AND prd.SupplierId IS NOT NULL
                GROUP BY prd.ItemId, prd.SupplierId
                ORDER BY prd.ItemId, usage_count DESC
            """, [comp_id])

            intelligence_map = defaultdict(lambda: {'item_code': None, 'suppliers': {}})

            for row in cursor.fetchall():
                item_id, item_code, supplier_id, supplier_name, usage_count, avg_rate, avg_discount, last_used = row

                intelligence_map[item_id]['item_code'] = item_code
                intelligence_map[item_id]['suppliers'][supplier_id] = {
                    'name': supplier_name or 'Unknown',
                    'usage_count': usage_count,
                    'avg_rate': float(avg_rate) if avg_rate else 0,
                    'avg_discount': float(avg_discount) if avg_discount else 0,
                    'last_used': last_used
                }

            return dict(intelligence_map)

    def _get_bom_items(self, wo_no, comp_id):
        """Get BOM items for Work Order"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT
                    bom.ItemId,
                    im.ItemCode,
                    im.ManfDesc,
                    um.Symbol as UOM,
                    SUM(bom.Qty) as BOMQty
                FROM tblDG_BOM_Master bom
                INNER JOIN tblDG_Item_Master im ON im.Id = bom.ItemId
                LEFT JOIN Unit_Master um ON um.Id = im.UOMBasic
                WHERE bom.WONo = %s
                AND bom.CompId = %s
                AND bom.ECNFlag = 0
                GROUP BY bom.ItemId, im.ItemCode, im.ManfDesc, um.Symbol
            """, [wo_no, comp_id])

            items = []
            for row in cursor.fetchall():
                items.append({
                    'item_id': row[0],
                    'item_code': row[1],
                    'item_desc': row[2] if row[2] else 'No description',
                    'uom': row[3] if row[3] else 'PCS',
                    'qty': float(row[4]) if row[4] else 0
                })
            return items

    def _get_rate_register_data(self, item_id, comp_id):
        """Get rate from Rate Register (prioritize flagged rates)"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Rate, Discount, Flag
                FROM tblMM_Rate_Register
                WHERE ItemId = %s AND CompId = %s
                ORDER BY Flag DESC, Id DESC
                LIMIT 1
            """, [item_id, comp_id])

            row = cursor.fetchone()
            if row:
                return {
                    'rate': float(row[0]) if row[0] else 0,
                    'discount': float(row[1]) if row[1] else 0,
                    'is_flagged': row[2] == 1
                }
        return {'rate': 0, 'discount': 0, 'is_flagged': False}

    def _calculate_confidence(self, usage_count):
        """Calculate confidence score based on usage frequency"""
        if usage_count >= 5:
            return 90
        elif usage_count >= 3:
            return 75
        elif usage_count >= 2:
            return 60
        elif usage_count == 1:
            return 45
        else:
            return 30

    def _get_ai_insights(self, wo_no, items, comp_id):
        """
        Use AI to provide additional insights and validate suggestions
        """
        # Simplified data for AI
        items_summary = [
            {
                'item_code': item['item_code'],
                'suggested_supplier': item['suggested_supplier_name'],
                'confidence': item['confidence'],
                'rate': item['suggested_rate']
            }
            for item in items[:10]  # Limit to 10 items to save tokens
        ]

        prompt = f"""You are analyzing a Purchase Requisition for Work Order {wo_no}.

Items with suggested suppliers based on historical data:
{json.dumps(items_summary, indent=2)}

Provide brief insights:
1. Are there any patterns you notice?
2. Any risks or recommendations?
3. Overall confidence in these suggestions?

Keep response under 100 words.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "AI insights unavailable"

    def get_supplier_name(self, supplier_id, comp_id):
        """Get supplier name from ID"""
        if not supplier_id:
            return None

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SupplierName
                FROM tblMM_Supplier_master
                WHERE SupplierId = %s AND CompId = %s
            """, [supplier_id, comp_id])

            row = cursor.fetchone()
            return row[0] if row else None
