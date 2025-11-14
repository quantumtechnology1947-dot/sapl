"""
Material Planning Module Utilities

Helper functions for date formatting, supplier code extraction,
PR checking, and planning number generation.
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def format_date_dmy(date_string):
    """
    Convert date from YYYY-MM-DD to DD-MM-YYYY format.
    
    Args:
        date_string: Date string in YYYY-MM-DD format or datetime object
        
    Returns:
        str: Date in DD-MM-YYYY format, or empty string if invalid
        
    Examples:
        >>> format_date_dmy("2025-10-29")
        "29-10-2025"
        >>> format_date_dmy(None)
        ""
    """
    if not date_string:
        return ""
    
    try:
        # Handle datetime object
        if isinstance(date_string, datetime):
            return date_string.strftime('%d-%m-%Y')
        
        # Handle string
        date_string = str(date_string).strip()
        
        # If already in DD-MM-YYYY format, return as-is
        if '-' in date_string and date_string.count('-') == 2:
            parts = date_string.split('-')
            if len(parts[0]) == 2:  # DD-MM-YYYY
                return date_string
            elif len(parts[0]) == 4:  # YYYY-MM-DD
                date_obj = datetime.strptime(date_string, '%Y-%m-%d')
                return date_obj.strftime('%d-%m-%Y')
        
        return date_string
    except (ValueError, AttributeError) as e:
        logger.warning(f"Error formatting date {date_string}: {e}")
        return ""


def format_date_ymd(date_string):
    """
    Convert date from DD-MM-YYYY to YYYY-MM-DD format.
    
    Args:
        date_string: Date string in DD-MM-YYYY format
        
    Returns:
        str: Date in YYYY-MM-DD format, or empty string if invalid
        
    Examples:
        >>> format_date_ymd("29-10-2025")
        "2025-10-29"
        >>> format_date_ymd(None)
        ""
    """
    if not date_string:
        return ""
    
    try:
        date_string = str(date_string).strip()
        
        # If already in YYYY-MM-DD format, return as-is
        if '-' in date_string and date_string.count('-') == 2:
            parts = date_string.split('-')
            if len(parts[0]) == 4:  # YYYY-MM-DD
                return date_string
            elif len(parts[0]) == 2:  # DD-MM-YYYY
                date_obj = datetime.strptime(date_string, '%d-%m-%Y')
                return date_obj.strftime('%Y-%m-%d')
        
        return date_string
    except (ValueError, AttributeError) as e:
        logger.warning(f"Error formatting date {date_string}: {e}")
        return ""


def extract_supplier_code(text):
    """
    Extract supplier ID from "SupplierName [SupplierID]" format.
    
    Args:
        text: Supplier text in format "Name [ID]" or just "ID"
        
    Returns:
        str: Extracted supplier ID, or original text if no brackets found
        
    Examples:
        >>> extract_supplier_code("ABC Suppliers [SUP001]")
        "SUP001"
        >>> extract_supplier_code("SUP001")
        "SUP001"
        >>> extract_supplier_code("")
        ""
    """
    if not text:
        return ""
    
    text = str(text).strip()
    
    # Extract ID from "[ID]" format
    if '[' in text and ']' in text:
        try:
            return text.split('[')[-1].split(']')[0].strip()
        except IndexError:
            return text
    
    return text


def check_item_in_pr(compid, pid, itemid, cid):
    """
    Check if an item exists in Purchase Requisition.
    
    Args:
        compid: Company ID
        pid: Process ID
        itemid: Item ID
        cid: Category ID
        
    Returns:
        bool: True if item exists in PR, False otherwise
    """
    try:
        from material_management.models import PRDetails
        
        return PRDetails.objects.filter(
            pr__comp_id=compid,
            item=itemid,
            pid=pid,
            cid=cid
        ).exists()
    except Exception as e:
        logger.error(f"Error checking item in PR: {e}")
        return False


def check_planning_in_pr(plan):
    """
    Check if any items in a planning record are in Purchase Requisition.
    
    Args:
        plan: TblmpMaterialMaster instance
        
    Returns:
        bool: True if any items are in PR, False otherwise
    """
    try:
        from .models import TblmpMaterialRawmaterial, TblmpMaterialProcess
        
        # Check raw materials
        rm_items = TblmpMaterialRawmaterial.objects.filter(
            mid=plan.id
        ).values_list('item', 'pid', 'cid')
        
        for item_id, pid, cid in rm_items:
            if item_id and check_item_in_pr(plan.compid, pid, item_id, cid):
                return True
        
        # Check process items
        pro_items = TblmpMaterialProcess.objects.filter(
            mid=plan.id
        ).values_list('item', 'pid', 'cid')
        
        for item_id, pid, cid in pro_items:
            if item_id and check_item_in_pr(plan.compid, pid, item_id, cid):
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking planning in PR: {e}")
        return False


def generate_planning_number(compid, finyearid):
    """
    Generate next planning number in format PL####.
    
    Args:
        compid: Company ID
        finyearid: Financial Year ID
        
    Returns:
        str: Next planning number (e.g., "PL0001", "PL0002")
        
    Examples:
        >>> generate_planning_number(1, 1)
        "PL0001"  # If no existing planning
        >>> generate_planning_number(1, 1)
        "PL0042"  # If last planning was PL0041
    """
    try:
        from .models import TblmpMaterialMaster
        
        # Get last planning number for this company and financial year
        last_plan = TblmpMaterialMaster.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-id').first()
        
        if last_plan and last_plan.plno:
            try:
                # Extract number from PL#### format
                last_num = int(last_plan.plno.replace('PL', '').replace('pl', ''))
                new_num = last_num + 1
            except (ValueError, AttributeError):
                # If format is unexpected, start from 1
                new_num = 1
        else:
            # First planning for this company/year
            new_num = 1
        
        # Format with leading zeros (4 digits)
        return f'PL{new_num:04d}'
    except Exception as e:
        logger.error(f"Error generating planning number: {e}")
        return 'PL0001'


def validate_date_format(date_string):
    """
    Validate date string is in DD-MM-YYYY format.
    
    Args:
        date_string: Date string to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
        
    Examples:
        >>> validate_date_format("29-10-2025")
        (True, "")
        >>> validate_date_format("2025-10-29")
        (False, "Invalid date format. Use DD-MM-YYYY")
    """
    if not date_string:
        return False, "Date is required"
    
    try:
        datetime.strptime(str(date_string).strip(), '%d-%m-%Y')
        return True, ""
    except ValueError:
        return False, "Invalid date format. Use DD-MM-YYYY"


def validate_supplier_exists(supplier_text, compid):
    """
    Validate that supplier exists in database.
    
    Args:
        supplier_text: Supplier text in format "Name [ID]" or just "ID"
        compid: Company ID
        
    Returns:
        tuple: (is_valid: bool, supplier_id: str, error_message: str)
    """
    try:
        from material_management.models import Supplier
        
        supplier_id = extract_supplier_code(supplier_text)
        
        if not supplier_id:
            return False, "", "Supplier is required"
        
        exists = Supplier.objects.filter(
            supplier_id=supplier_id,
            comp_id=compid
        ).exists()
        
        if not exists:
            return False, supplier_id, "Invalid supplier selected"
        
        return True, supplier_id, ""
    except Exception as e:
        logger.error(f"Error validating supplier: {e}")
        return False, "", "Error validating supplier"
