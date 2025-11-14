"""
DataValidator - Verifies data consistency between databases
"""
import logging
from typing import Dict


class DataValidator:
    """
    Validates data consistency between SQL Server and Django databases
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def verify_pr_counts(self, extractor, comp_id: int, fin_year_id: int = None) -> Dict:
        """
        Compare PR counts between databases
        
        Args:
            extractor: DataExtractor instance
            comp_id: Company ID
            fin_year_id: Financial year ID
        
        Returns:
            Dictionary with count comparison
        """
        from material_management.models import PRMaster
        
        sqlserver_count = extractor.count_authorized_prs(comp_id, fin_year_id)
        
        django_query = PRMaster.objects.filter(comp_id=comp_id, authorize=True)
        if fin_year_id:
            django_query = django_query.filter(fin_year_id__lte=fin_year_id)
        django_count = django_query.count()
        
        match = sqlserver_count == django_count
        
        result = {
            'sqlserver': sqlserver_count,
            'django': django_count,
            'match': match,
            'difference': abs(sqlserver_count - django_count)
        }
        
        if match:
            self.logger.info(f"PR counts match: {sqlserver_count}")
        else:
            self.logger.warning(f"PR count mismatch - SQL Server: {sqlserver_count}, Django: {django_count}")
        
        return result
    
    def verify_spr_counts(self, extractor, comp_id: int, fin_year_id: int = None) -> Dict:
        """
        Compare SPR counts between databases
        
        Args:
            extractor: DataExtractor instance
            comp_id: Company ID
            fin_year_id: Financial year ID
        
        Returns:
            Dictionary with count comparison
        """
        from material_management.models import SPRMaster
        
        sqlserver_count = extractor.count_authorized_sprs(comp_id, fin_year_id)
        
        django_query = SPRMaster.objects.filter(comp_id=comp_id, authorize=True)
        if fin_year_id:
            django_query = django_query.filter(fin_year_id__lte=fin_year_id)
        django_count = django_query.count()
        
        match = sqlserver_count == django_count
        
        result = {
            'sqlserver': sqlserver_count,
            'django': django_count,
            'match': match,
            'difference': abs(sqlserver_count - django_count)
        }
        
        if match:
            self.logger.info(f"SPR counts match: {sqlserver_count}")
        else:
            self.logger.warning(f"SPR count mismatch - SQL Server: {sqlserver_count}, Django: {django_count}")
        
        return result
    
    def verify_supplier_counts(self) -> Dict:
        """
        Compare supplier counts with PRs/SPRs
        
        Returns:
            Dictionary with supplier count comparison
        """
        from material_management.models import Supplier, PRDetails, SPRDetails
        
        # Count suppliers with PR items
        pr_suppliers = PRDetails.objects.values('supplier_id').distinct().count()
        
        # Count suppliers with SPR items
        spr_suppliers = SPRDetails.objects.values('supplier_id').distinct().count()
        
        # Total unique suppliers
        total_suppliers = Supplier.objects.count()
        
        result = {
            'total_suppliers': total_suppliers,
            'suppliers_with_prs': pr_suppliers,
            'suppliers_with_sprs': spr_suppliers
        }
        
        self.logger.info(f"Supplier verification - Total: {total_suppliers}, "
                        f"With PRs: {pr_suppliers}, With SPRs: {spr_suppliers}")
        
        return result
    
    def generate_comparison_report(self, pr_counts: Dict, spr_counts: Dict, 
                                   supplier_counts: Dict) -> str:
        """
        Generate detailed comparison report
        
        Args:
            pr_counts: PR count comparison
            spr_counts: SPR count comparison
            supplier_counts: Supplier count comparison
        
        Returns:
            Formatted report string
        """
        report = f"""
Data Verification Report:
=========================

PR Masters:
  SQL Server: {pr_counts['sqlserver']}
  Django:     {pr_counts['django']}
  Match:      {'✓ Yes' if pr_counts['match'] else '✗ No'}
  Difference: {pr_counts['difference']}

SPR Masters:
  SQL Server: {spr_counts['sqlserver']}
  Django:     {spr_counts['django']}
  Match:      {'✓ Yes' if spr_counts['match'] else '✗ No'}
  Difference: {spr_counts['difference']}

Suppliers:
  Total Suppliers:        {supplier_counts['total_suppliers']}
  Suppliers with PRs:     {supplier_counts['suppliers_with_prs']}
  Suppliers with SPRs:    {supplier_counts['suppliers_with_sprs']}

Overall Status: {'✓ PASS' if pr_counts['match'] and spr_counts['match'] else '✗ FAIL'}
"""
        return report
