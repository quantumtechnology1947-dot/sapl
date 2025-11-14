"""
Quality Control Utility Functions
Reusable helper functions for performance optimization
"""
from django.db import connection
from functools import lru_cache
from typing import List, Dict, Any, Optional


class DatabaseQueryOptimizer:
    """Optimized database query utilities"""
    
    @staticmethod
    def execute_raw_sql(sql: str, params: tuple) -> List[Dict[str, Any]]:
        """
        Execute raw SQL and return results as list of dicts
        Optimized for performance with proper connection handling
        """
        from django.conf import settings
        from django.db import reset_queries
        
        # Temporarily disable query logging to avoid SQL formatting issues in debug mode
        original_debug = settings.DEBUG
        try:
            if original_debug:
                settings.DEBUG = False
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return result
        finally:
            if original_debug:
                settings.DEBUG = True
                reset_queries()
    
    @staticmethod
    def execute_raw_sql_single(sql: str, params: tuple) -> Optional[Dict[str, Any]]:
        """Execute raw SQL and return single result"""
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
        return None


class CacheHelper:
    """Cache helper for frequently accessed data"""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_financial_year(finyear_id: int) -> Optional[str]:
        """Get financial year name with caching"""
        from sys_admin.models import TblfinancialMaster
        try:
            fy = TblfinancialMaster.objects.only('finyear').get(finyearid=finyear_id)
            return fy.finyear
        except TblfinancialMaster.DoesNotExist:
            return None
    
    @staticmethod
    @lru_cache(maxsize=256)
    def get_supplier_name(supplier_id: int) -> Optional[str]:
        """Get supplier name with caching"""
        from material_management.models import Supplier
        try:
            supplier = Supplier.objects.only('supplier_name').get(supplier_id=supplier_id)
            return supplier.supplier_name
        except Supplier.DoesNotExist:
            return None
    
    @staticmethod
    def clear_cache():
        """Clear all caches"""
        CacheHelper.get_financial_year.cache_clear()
        CacheHelper.get_supplier_name.cache_clear()


class QueryBuilder:
    """SQL Query builder for common patterns"""
    
    @staticmethod
    def build_gqn_list_query(comp_id: int, search_filters: Optional[Dict] = None) -> tuple:
        """
        Build optimized GQN list query with optional filters
        Returns: (sql, params)
        """
        sql = """
            SELECT 
                gqn.Id as id,
                gqn.GQNNo as gqnno,
                gqn.SysDate as sysdate,
                gqn.GRRNo as grrno,
                fy.FinYear as finyearname,
                grr.GINNo as ginno,
                gin.PONo as pono_from_gin,
                gin.ChallanNo as challanno,
                gin.ChallanDate as challandate,
                sup.SupplierName as suppliername
            FROM tblQc_MaterialQuality_Master gqn
            LEFT JOIN tblFinancial_Master fy ON gqn.FinYearId = fy.FinYearId
            LEFT JOIN tblInv_MaterialReceived_Master grr ON gqn.GRRId = grr.Id
            LEFT JOIN tblInv_Inward_Master gin ON grr.GINId = gin.Id
            LEFT JOIN tblMM_PO_Master po ON gin.PONo = po.PONo AND po.CompId = ?
            LEFT JOIN tblMM_Supplier_Master sup ON po.SupplierId = sup.SupplierId
            WHERE gqn.CompId = ?
        """
        
        params = [comp_id, comp_id]
        
        # Add search filters
        if search_filters:
            search_by = search_filters.get('search_by')
            search_value = search_filters.get('search_value', '').strip()
            
            if search_value:
                if search_by == '0':  # Supplier Name
                    sql += " AND sup.SupplierName LIKE ?"
                    params.append(f'%{search_value}%')
                elif search_by == '1':  # GQN No
                    sql += " AND gqn.GQNNo LIKE ?"
                    params.append(f'%{search_value}%')
                elif search_by == '2':  # GRR No
                    sql += " AND gqn.GRRNo LIKE ?"
                    params.append(f'%{search_value}%')
                elif search_by == '3':  # PO No
                    sql += " AND gin.PONo LIKE ?"
                    params.append(f'%{search_value}%')
        
        sql += " ORDER BY gqn.Id DESC"
        
        return sql, tuple(params)
    
    @staticmethod
    def build_pending_grr_query(comp_id: int, fin_year_id: int) -> tuple:
        """
        Build query for pending GRR records
        Returns: (sql, params)
        """
        sql = """
            SELECT 
                grr.Id,
                grr.GRRNo,
                grr.SysDate,
                grr.GINNo,
                grr.GINId,
                grr.FinYearId,
                fy.FinYear,
                SUM(grd.ReceivedQty) as ReceivedQty,
                COALESCE(SUM(gqd.AcceptedQty), 0) + COALESCE(SUM(gqd.RejectedQty), 0) as InspectedQty
            FROM tblInv_MaterialReceived_Master grr
            LEFT JOIN tblFinancial_Master fy ON grr.FinYearId = fy.FinYearId
            LEFT JOIN tblInv_MaterialReceived_Details grd ON grr.Id = grd.MId
            LEFT JOIN tblQc_MaterialQuality_Details gqd ON gqd.MId IN (
                SELECT Id FROM tblQc_MaterialQuality_Master WHERE GRRId = grr.Id
            )
            WHERE grr.CompId = ? AND grr.FinYearId <= ?
            GROUP BY grr.Id, grr.GRRNo, grr.SysDate, grr.GINNo, grr.GINId, grr.FinYearId, fy.FinYear
            HAVING SUM(grd.ReceivedQty) > (COALESCE(SUM(gqd.AcceptedQty), 0) + COALESCE(SUM(gqd.RejectedQty), 0))
            ORDER BY grr.Id DESC
        """
        
        return sql, (comp_id, fin_year_id)


def paginate_results(results: List[Dict], page: int = 1, per_page: int = 20) -> Dict:
    """
    Paginate results manually for raw SQL queries
    Returns: dict with paginated data and pagination info
    """
    total_count = len(results)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        'results': results[start_idx:end_idx],
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'num_pages': (total_count + per_page - 1) // per_page,
        'has_previous': page > 1,
        'has_next': end_idx < total_count,
    }
