"""
AI-Powered Purchase Requisition Intelligence Service
Uses Google Gemini 2.5 Pro to analyze Work Orders and suggest items with suppliers
"""

import os
import google.generativeai as genai
from django.db import connection
import json


class PRIntelligenceService:
    """
    AI-powered service for intelligent PR creation
    Analyzes Work Orders, historical data, and suggests optimal items/suppliers
    """

    def __init__(self):
        """Initialize Gemini AI with API key"""
        # Read API key from file
        api_key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api_key.txt')
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def analyze_work_order_for_pr(self, wo_no, comp_id):
        """
        Analyze Work Order using AI and suggest items with suppliers

        Returns:
            List of suggested items with supplier, rate, discount, quantity
        """
        # Step 1: Get Work Order details
        wo_data = self._get_work_order_details(wo_no, comp_id)

        if not wo_data:
            print(f"Work Order {wo_no} not found")
            return []

        # Step 2: Get BOM items for this Work Order
        bom_items = self._get_bom_items(wo_no, comp_id)

        if not bom_items:
            print(f"No BOM items found for WO {wo_no}")
            return []

        # Step 3: Get historical PR data
        historical_data = self._get_historical_pr_data(comp_id)

        # Step 4: Get supplier and rate data
        supplier_rate_data = self._get_supplier_rate_data(comp_id)

        # Step 5: Build AI prompt with all data
        prompt = self._build_ai_prompt(wo_data, historical_data, bom_items, supplier_rate_data)

        # Step 6: Get AI suggestions
        try:
            print(f"Sending {len(bom_items)} items to AI for analysis...")
            response = self.model.generate_content(prompt)
            suggestions = self._parse_ai_response(response.text)
            print(f"AI returned {len(suggestions)} suggestions")
            return suggestions
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            # Fallback to traditional method
            return self._fallback_suggestions(bom_items, supplier_rate_data)

    def _get_work_order_details(self, wo_no, comp_id):
        """Get Work Order details from database"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT
                        WONo,
                        TaskProjectTitle,
                        CustomerId,
                        CustomerName,
                        BoughtOutMaterialDate,
                        Quantity,
                        DeliveryDate
                    FROM SD_Cust_Workorder_Master
                    WHERE WONo = ? AND CompId = ?
                """, [wo_no, comp_id])

                row = cursor.fetchone()
                if row:
                    return {
                        'wo_no': row[0],
                        'project_title': row[1] if row[1] else 'Unknown Project',
                        'customer_id': row[2],
                        'customer_name': row[3] if row[3] else 'Unknown Customer',
                        'material_date': row[4] if row[4] else 'Not specified',
                        'quantity': row[5] if row[5] else 1,
                        'delivery_date': row[6] if row[6] else 'Not specified'
                    }
            except Exception as e:
                print(f"Error fetching WO details: {e}")
        return {}

    def _get_historical_pr_data(self, comp_id):
        """Get historical PR data for analysis"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT
                        pr.WONo,
                        pr.PRNo,
                        prd.ItemId,
                        im.ItemCode,
                        im.ManfDesc,
                        prd.SupplierId,
                        prd.Qty,
                        prd.Rate,
                        prd.Discount
                    FROM tblMM_PR_Master pr
                    INNER JOIN tblMM_PR_Details prd ON pr.Id = prd.MId
                    INNER JOIN tblDG_Item_Master im ON prd.ItemId = im.Id
                    WHERE pr.CompId = ?
                    ORDER BY pr.Id DESC
                    LIMIT 50
                """, [comp_id])

                results = []
                for row in cursor.fetchall():
                    results.append({
                        'wo_no': row[0],
                        'pr_no': row[1],
                        'item_id': row[2],
                        'item_code': row[3],
                        'item_desc': row[4] if row[4] else '',
                        'supplier_id': row[5],
                        'qty': float(row[6]) if row[6] else 0,
                        'rate': float(row[7]) if row[7] else 0,
                        'discount': float(row[8]) if row[8] else 0
                    })
                return results
            except Exception as e:
                print(f"Error fetching historical PR data: {e}")
                return []

    def _get_bom_items(self, wo_no, comp_id):
        """Get BOM items for this Work Order"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT DISTINCT
                        bom.ItemId,
                        im.ItemCode,
                        im.ManfDesc,
                        um.Symbol as UOM,
                        SUM(bom.Qty) as BOMQty
                    FROM tblDG_BOM_Master bom
                    INNER JOIN tblDG_Item_Master im ON im.Id = bom.ItemId
                    INNER JOIN Unit_Master um ON um.Id = im.UOMBasic
                    WHERE bom.WONo = ?
                    AND bom.CompId = ?
                    AND bom.ECNFlag = 0
                    GROUP BY bom.ItemId, im.ItemCode, im.ManfDesc, um.Symbol
                """, [wo_no, comp_id])

                results = []
                for row in cursor.fetchall():
                    results.append({
                        'item_id': row[0],
                        'item_code': row[1],
                        'item_desc': row[2] if row[2] else 'No description',
                        'uom': row[3] if row[3] else 'PCS',
                        'bom_qty': float(row[4]) if row[4] else 0
                    })
                return results
            except Exception as e:
                print(f"Error fetching BOM items: {e}")
                return []

    def _get_supplier_rate_data(self, comp_id):
        """Get supplier and rate information"""
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT
                        ItemId,
                        Rate,
                        Discount,
                        Flag
                    FROM tblMM_Rate_Register
                    WHERE CompId = ?
                    LIMIT 200
                """, [comp_id])

                results = []
                for row in cursor.fetchall():
                    results.append({
                        'item_id': row[0],
                        'rate': float(row[1]) if row[1] else 0,
                        'discount': float(row[2]) if row[2] else 0,
                        'is_flagged': row[3] == 1 if row[3] else False
                    })
                return results
            except Exception as e:
                print(f"Error fetching supplier rate data: {e}")
                return []

    def _build_ai_prompt(self, wo_data, historical_data, bom_items, supplier_rate_data):
        """Build comprehensive AI prompt for Gemini"""

        # Limit data to avoid token limits
        historical_summary = historical_data[:15] if len(historical_data) > 15 else historical_data
        rate_summary = supplier_rate_data[:30] if len(supplier_rate_data) > 30 else supplier_rate_data

        prompt = f"""You are an AI procurement assistant for an ERP system. Analyze the data and suggest Purchase Requisition items.

**WORK ORDER:**
- WO No: {wo_data.get('wo_no')}
- Project: {wo_data.get('project_title')}
- Customer: {wo_data.get('customer_name')}
- Required Date: {wo_data.get('material_date')}

**REQUIRED ITEMS (from BOM):**
{json.dumps(bom_items, indent=2)}

**HISTORICAL DATA (Last 15 PRs):**
{json.dumps(historical_summary, indent=2)}

**RATE REGISTER (Approved Rates):**
{json.dumps(rate_summary, indent=2)}

**TASK:**
For each BOM item, suggest:
1. Best supplier based on historical patterns
2. Optimal rate from Rate Register (prioritize flagged rates)
3. Appropriate discount
4. Confidence score (0-100)

**OUTPUT FORMAT (JSON only, no markdown):**
```json
[
  {{
    "item_id": <id>,
    "item_code": "<code>",
    "item_desc": "<desc>",
    "qty": <quantity>,
    "suggested_supplier": "<supplier_id from history or leave empty>",
    "suggested_rate": <rate>,
    "suggested_discount": <discount>,
    "confidence": <0-100>,
    "reasoning": "<brief explanation>"
  }}
]
```

Return ONLY the JSON array, nothing else.
"""
        return prompt

    def _parse_ai_response(self, response_text):
        """Parse AI response and extract suggestions"""
        try:
            # Extract JSON from response
            json_text = response_text.strip()

            # Remove markdown code blocks if present
            if '```json' in json_text:
                json_text = json_text.split('```json')[1].split('```')[0].strip()
            elif '```' in json_text:
                json_text = json_text.split('```')[1].split('```')[0].strip()

            # Remove any leading/trailing text
            json_start = json_text.find('[')
            json_end = json_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = json_text[json_start:json_end]

            suggestions = json.loads(json_text)
            return suggestions
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            print(f"Response text: {response_text[:500]}...")
            return []

    def _fallback_suggestions(self, bom_items, supplier_rate_data):
        """Fallback method if AI fails"""
        suggestions = []

        # Create lookup for rate data
        rate_lookup = {}
        for rate_data in supplier_rate_data:
            item_id = rate_data['item_id']
            if item_id not in rate_lookup or rate_data.get('is_flagged'):
                rate_lookup[item_id] = rate_data

        # Process each BOM item
        for item in bom_items:
            item_id = item['item_id']

            # Find rate
            rate_data = rate_lookup.get(item_id, {})

            suggestions.append({
                'item_id': item_id,
                'item_code': item['item_code'],
                'item_desc': item['item_desc'],
                'qty': item['bom_qty'],
                'uom': item['uom'],
                'suggested_supplier': '',
                'suggested_rate': rate_data.get('rate', 0),
                'suggested_discount': rate_data.get('discount', 0),
                'confidence': 50,
                'reasoning': 'Fallback: Used Rate Register data'
            })

        return suggestions

    def get_supplier_name(self, supplier_id, comp_id):
        """Get supplier name from ID"""
        if not supplier_id:
            return None

        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT SupplierName
                    FROM tblMM_Supplier
                    WHERE SupplierId = ? AND CompId = ?
                """, [supplier_id, comp_id])

                row = cursor.fetchone()
                return row[0] if row else None
            except Exception as e:
                print(f"Error fetching supplier name: {e}")
                return None
