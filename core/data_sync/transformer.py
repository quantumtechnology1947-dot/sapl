"""
DataTransformer - Validates and transforms data from SQL Server to Django models
"""
import logging
from datetime import datetime, date, time
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Any


class DataTransformer:
    """
    Validates and transforms extracted data for Django models
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_errors = []
    
    def transform_pr_master(self, record: Dict) -> Optional[Dict]:
        """
        Transform PR master record from SQL Server to Django format
        
        Args:
            record: Raw PR master record from SQL Server
        
        Returns:
            Transformed record dict or None if validation fails
        """
        try:
            transformed = {
                'id': self._get_int(record, 'Id'),
                'pr_no': self._get_string(record, 'PRNo', max_length=50),
                'comp_id': self._get_int(record, 'CompId'),
                'fin_year_id': self._get_int(record, 'FinYearId'),
                'sys_date': self._parse_date(record.get('SysDate')),
                'sys_time': self._parse_time(record.get('SysTime')),
                'session_id': self._get_string(record, 'SessionId', max_length=100),
                'authorize': self._get_bool(record, 'Authorize'),
                'pr_date': self._parse_date(record.get('PRDate')),
                'dept_id': self._get_int_nullable(record, 'DeptId'),
                'remarks': self._get_string(record, 'Remarks', max_length=500, nullable=True),
                'user_id': self._get_int_nullable(record, 'UserId'),
                'modify_date': self._parse_date_nullable(record.get('ModifyDate')),
                'modify_time': self._parse_time_nullable(record.get('ModifyTime')),
                'modify_user_id': self._get_int_nullable(record, 'ModifyUserId'),
                'cancel': self._get_bool(record, 'Cancel'),
                'cancel_date': self._parse_date_nullable(record.get('CancelDate')),
                'cancel_time': self._parse_time_nullable(record.get('CancelTime')),
                'cancel_user_id': self._get_int_nullable(record, 'CancelUserId'),
                'cancel_remarks': self._get_string(record, 'CancelRemarks', max_length=500, nullable=True),
            }
            
            # Validate required fields
            if not self._validate_required_fields(transformed, ['id', 'pr_no', 'comp_id', 'fin_year_id']):
                return None
            
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming PR master {record.get('Id')}: {e}")
            self.validation_errors.append({
                'type': 'pr_master',
                'id': record.get('Id'),
                'error': str(e)
            })
            return None
    
    def transform_pr_detail(self, record: Dict) -> Optional[Dict]:
        """
        Transform PR detail record from SQL Server to Django format
        
        Args:
            record: Raw PR detail record from SQL Server
        
        Returns:
            Transformed record dict or None if validation fails
        """
        try:
            transformed = {
                'id': self._get_int(record, 'Id'),
                'm_id': self._get_int(record, 'MId'),
                'pr_no': self._get_string(record, 'PRNo', max_length=50),
                'item_id': self._get_int_nullable(record, 'ItemId'),
                'supplier_id': self._get_string(record, 'SupplierId', max_length=50, nullable=True),
                'qty': self._get_decimal(record, 'Qty', max_digits=18, decimal_places=3),
                'rate': self._get_decimal(record, 'Rate', max_digits=18, decimal_places=2),
                'amount': self._get_decimal(record, 'Amount', max_digits=18, decimal_places=2),
                'required_date': self._parse_date_nullable(record.get('RequiredDate')),
                'specification': self._get_string(record, 'Specification', max_length=1000, nullable=True),
                'remarks': self._get_string(record, 'Remarks', max_length=500, nullable=True),
                'user_id': self._get_int_nullable(record, 'UserId'),
                'sys_date': self._parse_date(record.get('SysDate')),
                'sys_time': self._parse_time(record.get('SysTime')),
                'session_id': self._get_string(record, 'SessionId', max_length=100),
                'modify_date': self._parse_date_nullable(record.get('ModifyDate')),
                'modify_time': self._parse_time_nullable(record.get('ModifyTime')),
                'modify_user_id': self._get_int_nullable(record, 'ModifyUserId'),
                'cancel': self._get_bool(record, 'Cancel'),
                'cancel_date': self._parse_date_nullable(record.get('CancelDate')),
                'cancel_time': self._parse_time_nullable(record.get('CancelTime')),
                'cancel_user_id': self._get_int_nullable(record, 'CancelUserId'),
                'cancel_remarks': self._get_string(record, 'CancelRemarks', max_length=500, nullable=True),
                'po_qty': self._get_decimal(record, 'POQty', max_digits=18, decimal_places=3, default=Decimal('0')),
                'balance_qty': self._get_decimal(record, 'BalanceQty', max_digits=18, decimal_places=3, default=Decimal('0')),
                'unit_id': self._get_int_nullable(record, 'UnitId'),
                'acc_head_id': self._get_int_nullable(record, 'AccHeadId'),
            }
            
            # Validate required fields
            if not self._validate_required_fields(transformed, ['id', 'm_id', 'pr_no']):
                return None
            
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming PR detail {record.get('Id')}: {e}")
            self.validation_errors.append({
                'type': 'pr_detail',
                'id': record.get('Id'),
                'error': str(e)
            })
            return None

    def transform_spr_master(self, record: Dict) -> Optional[Dict]:
        """
        Transform SPR master record from SQL Server to Django format
        
        Args:
            record: Raw SPR master record from SQL Server
        
        Returns:
            Transformed record dict or None if validation fails
        """
        try:
            transformed = {
                'id': self._get_int(record, 'Id'),
                'spr_no': self._get_string(record, 'SPRNo', max_length=50),
                'comp_id': self._get_int(record, 'CompId'),
                'fin_year_id': self._get_int(record, 'FinYearId'),
                'sys_date': self._parse_date(record.get('SysDate')),
                'sys_time': self._parse_time(record.get('SysTime')),
                'session_id': self._get_string(record, 'SessionId', max_length=100),
                'authorize': self._get_bool(record, 'Authorize'),
                'spr_date': self._parse_date(record.get('SPRDate')),
                'dept_id': self._get_int_nullable(record, 'DeptId'),
                'remarks': self._get_string(record, 'Remarks', max_length=500, nullable=True),
                'user_id': self._get_int_nullable(record, 'UserId'),
                'modify_date': self._parse_date_nullable(record.get('ModifyDate')),
                'modify_time': self._parse_time_nullable(record.get('ModifyTime')),
                'modify_user_id': self._get_int_nullable(record, 'ModifyUserId'),
                'cancel': self._get_bool(record, 'Cancel'),
                'cancel_date': self._parse_date_nullable(record.get('CancelDate')),
                'cancel_time': self._parse_time_nullable(record.get('CancelTime')),
                'cancel_user_id': self._get_int_nullable(record, 'CancelUserId'),
                'cancel_remarks': self._get_string(record, 'CancelRemarks', max_length=500, nullable=True),
            }
            
            # Validate required fields
            if not self._validate_required_fields(transformed, ['id', 'spr_no', 'comp_id', 'fin_year_id']):
                return None
            
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming SPR master {record.get('Id')}: {e}")
            self.validation_errors.append({
                'type': 'spr_master',
                'id': record.get('Id'),
                'error': str(e)
            })
            return None
    
    def transform_spr_detail(self, record: Dict) -> Optional[Dict]:
        """
        Transform SPR detail record from SQL Server to Django format
        
        Args:
            record: Raw SPR detail record from SQL Server
        
        Returns:
            Transformed record dict or None if validation fails
        """
        try:
            transformed = {
                'id': self._get_int(record, 'Id'),
                'm_id': self._get_int(record, 'MId'),
                'spr_no': self._get_string(record, 'SPRNo', max_length=50),
                'item_id': self._get_int_nullable(record, 'ItemId'),
                'supplier_id': self._get_string(record, 'SupplierId', max_length=50, nullable=True),
                'qty': self._get_decimal(record, 'Qty', max_digits=18, decimal_places=3),
                'rate': self._get_decimal(record, 'Rate', max_digits=18, decimal_places=2),
                'amount': self._get_decimal(record, 'Amount', max_digits=18, decimal_places=2),
                'required_date': self._parse_date_nullable(record.get('RequiredDate')),
                'specification': self._get_string(record, 'Specification', max_length=1000, nullable=True),
                'remarks': self._get_string(record, 'Remarks', max_length=500, nullable=True),
                'user_id': self._get_int_nullable(record, 'UserId'),
                'sys_date': self._parse_date(record.get('SysDate')),
                'sys_time': self._parse_time(record.get('SysTime')),
                'session_id': self._get_string(record, 'SessionId', max_length=100),
                'modify_date': self._parse_date_nullable(record.get('ModifyDate')),
                'modify_time': self._parse_time_nullable(record.get('ModifyTime')),
                'modify_user_id': self._get_int_nullable(record, 'ModifyUserId'),
                'cancel': self._get_bool(record, 'Cancel'),
                'cancel_date': self._parse_date_nullable(record.get('CancelDate')),
                'cancel_time': self._parse_time_nullable(record.get('CancelTime')),
                'cancel_user_id': self._get_int_nullable(record, 'CancelUserId'),
                'cancel_remarks': self._get_string(record, 'CancelRemarks', max_length=500, nullable=True),
                'po_qty': self._get_decimal(record, 'POQty', max_digits=18, decimal_places=3, default=Decimal('0')),
                'balance_qty': self._get_decimal(record, 'BalanceQty', max_digits=18, decimal_places=3, default=Decimal('0')),
                'unit_id': self._get_int_nullable(record, 'UnitId'),
                'acc_head_id': self._get_int_nullable(record, 'AccHeadId'),
            }
            
            # Validate required fields
            if not self._validate_required_fields(transformed, ['id', 'm_id', 'spr_no']):
                return None
            
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming SPR detail {record.get('Id')}: {e}")
            self.validation_errors.append({
                'type': 'spr_detail',
                'id': record.get('Id'),
                'error': str(e)
            })
            return None
    
    def transform_supplier(self, record: Dict) -> Optional[Dict]:
        """
        Transform supplier record from SQL Server to Django format
        
        Args:
            record: Raw supplier record from SQL Server
        
        Returns:
            Transformed record dict or None if validation fails
        """
        try:
            transformed = {
                'supplier_id': self._get_string(record, 'SupplierId', max_length=50),
                'supplier_name': self._get_string(record, 'SupplierName', max_length=200),
                'address': self._get_string(record, 'Address', max_length=500, nullable=True),
                'city': self._get_string(record, 'City', max_length=100, nullable=True),
                'state': self._get_string(record, 'State', max_length=100, nullable=True),
                'country': self._get_string(record, 'Country', max_length=100, nullable=True),
                'pin_code': self._get_string(record, 'PinCode', max_length=20, nullable=True),
                'phone': self._get_string(record, 'Phone', max_length=50, nullable=True),
                'fax': self._get_string(record, 'Fax', max_length=50, nullable=True),
                'email': self._get_string(record, 'Email', max_length=100, nullable=True),
                'contact_person': self._get_string(record, 'ContactPerson', max_length=100, nullable=True),
                'pan_no': self._get_string(record, 'PANNo', max_length=50, nullable=True),
                'tin_no': self._get_string(record, 'TINNo', max_length=50, nullable=True),
                'cst_no': self._get_string(record, 'CSTNo', max_length=50, nullable=True),
                'service_tax_no': self._get_string(record, 'ServiceTaxNo', max_length=50, nullable=True),
                'excise_no': self._get_string(record, 'ExciseNo', max_length=50, nullable=True),
                'comp_id': self._get_int(record, 'CompId'),
                'user_id': self._get_int_nullable(record, 'UserId'),
                'sys_date': self._parse_date_nullable(record.get('SysDate')),
                'sys_time': self._parse_time_nullable(record.get('SysTime')),
                'session_id': self._get_string(record, 'SessionId', max_length=100, nullable=True),
                'modify_date': self._parse_date_nullable(record.get('ModifyDate')),
                'modify_time': self._parse_time_nullable(record.get('ModifyTime')),
                'modify_user_id': self._get_int_nullable(record, 'ModifyUserId'),
                'cancel': self._get_bool(record, 'Cancel'),
                'cancel_date': self._parse_date_nullable(record.get('CancelDate')),
                'cancel_time': self._parse_time_nullable(record.get('CancelTime')),
                'cancel_user_id': self._get_int_nullable(record, 'CancelUserId'),
                'cancel_remarks': self._get_string(record, 'CancelRemarks', max_length=500, nullable=True),
            }
            
            # Validate required fields
            if not self._validate_required_fields(transformed, ['supplier_id', 'supplier_name']):
                return None
            
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming supplier {record.get('SupplierId')}: {e}")
            self.validation_errors.append({
                'type': 'supplier',
                'id': record.get('SupplierId'),
                'error': str(e)
            })
            return None
    
    def transform_item(self, record: Dict) -> Optional[Dict]:
        """
        Transform item master record from SQL Server to Django format
        
        Args:
            record: Raw item record from SQL Server
        
        Returns:
            Transformed record dict or None if validation fails
        """
        try:
            transformed = {
                'id': self._get_int(record, 'Id'),
                'item_code': self._get_string(record, 'ItemCode', max_length=50),
                'item_name': self._get_string(record, 'ItemName', max_length=200),
                'item_description': self._get_string(record, 'ItemDescription', max_length=1000, nullable=True),
                'unit_id': self._get_int_nullable(record, 'UnitId'),
                'category_id': self._get_int_nullable(record, 'CategoryId'),
                'sub_category_id': self._get_int_nullable(record, 'SubCategoryId'),
                'hsn_code': self._get_string(record, 'HSNCode', max_length=50, nullable=True),
                'rate': self._get_decimal(record, 'Rate', max_digits=18, decimal_places=2, default=Decimal('0')),
                'comp_id': self._get_int(record, 'CompId'),
                'user_id': self._get_int_nullable(record, 'UserId'),
                'sys_date': self._parse_date_nullable(record.get('SysDate')),
                'sys_time': self._parse_time_nullable(record.get('SysTime')),
                'session_id': self._get_string(record, 'SessionId', max_length=100, nullable=True),
                'modify_date': self._parse_date_nullable(record.get('ModifyDate')),
                'modify_time': self._parse_time_nullable(record.get('ModifyTime')),
                'modify_user_id': self._get_int_nullable(record, 'ModifyUserId'),
                'cancel': self._get_bool(record, 'Cancel'),
                'cancel_date': self._parse_date_nullable(record.get('CancelDate')),
                'cancel_time': self._parse_time_nullable(record.get('CancelTime')),
                'cancel_user_id': self._get_int_nullable(record, 'CancelUserId'),
                'cancel_remarks': self._get_string(record, 'CancelRemarks', max_length=500, nullable=True),
                'min_stock': self._get_decimal(record, 'MinStock', max_digits=18, decimal_places=3, default=Decimal('0')),
                'max_stock': self._get_decimal(record, 'MaxStock', max_digits=18, decimal_places=3, default=Decimal('0')),
                'reorder_level': self._get_decimal(record, 'ReorderLevel', max_digits=18, decimal_places=3, default=Decimal('0')),
            }
            
            # Validate required fields
            if not self._validate_required_fields(transformed, ['id', 'item_code', 'item_name']):
                return None
            
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming item {record.get('Id')}: {e}")
            self.validation_errors.append({
                'type': 'item',
                'id': record.get('Id'),
                'error': str(e)
            })
            return None
    
    # Helper methods for data type conversion and validation
    
    def _get_int(self, record: Dict, field: str) -> int:
        """Get integer value from record"""
        value = record.get(field)
        if value is None:
            raise ValueError(f"Required field '{field}' is None")
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid integer value for field '{field}': {value}")
    
    def _get_int_nullable(self, record: Dict, field: str) -> Optional[int]:
        """Get nullable integer value from record"""
        value = record.get(field)
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid integer value for field '{field}': {value}, using None")
            return None
    
    def _get_string(self, record: Dict, field: str, max_length: int = None, nullable: bool = False) -> Optional[str]:
        """Get string value from record"""
        value = record.get(field)
        
        if value is None or value == '':
            if nullable:
                return None
            raise ValueError(f"Required field '{field}' is None or empty")
        
        str_value = str(value).strip()
        
        if max_length and len(str_value) > max_length:
            self.logger.warning(f"Field '{field}' exceeds max length {max_length}, truncating")
            str_value = str_value[:max_length]
        
        return str_value if str_value else (None if nullable else '')
    
    def _get_bool(self, record: Dict, field: str, default: bool = False) -> bool:
        """Get boolean value from record"""
        value = record.get(field)
        if value is None:
            return default
        
        # Handle various boolean representations
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 't', 'y')
        
        return default
    
    def _get_decimal(self, record: Dict, field: str, max_digits: int = 18, 
                     decimal_places: int = 2, default: Decimal = None) -> Optional[Decimal]:
        """Get decimal value from record"""
        value = record.get(field)
        
        if value is None or value == '':
            return default
        
        try:
            decimal_value = Decimal(str(value))
            
            # Validate precision
            sign, digits, exponent = decimal_value.as_tuple()
            total_digits = len(digits)
            
            if total_digits > max_digits:
                self.logger.warning(f"Field '{field}' exceeds max digits {max_digits}")
            
            return decimal_value
            
        except (InvalidOperation, ValueError, TypeError) as e:
            self.logger.warning(f"Invalid decimal value for field '{field}': {value}, using default")
            return default
    
    def _parse_date(self, value: Any) -> Optional[date]:
        """Parse date from various formats"""
        if value is None:
            return None
        
        if isinstance(value, date):
            return value
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, str):
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        
        self.logger.warning(f"Could not parse date: {value}")
        return None
    
    def _parse_date_nullable(self, value: Any) -> Optional[date]:
        """Parse nullable date"""
        return self._parse_date(value)
    
    def _parse_time(self, value: Any) -> Optional[time]:
        """Parse time from various formats"""
        if value is None:
            return None
        
        if isinstance(value, time):
            return value
        
        if isinstance(value, datetime):
            return value.time()
        
        if isinstance(value, str):
            # Try common time formats
            for fmt in ['%H:%M:%S', '%H:%M', '%I:%M:%S %p', '%I:%M %p']:
                try:
                    return datetime.strptime(value, fmt).time()
                except ValueError:
                    continue
        
        self.logger.warning(f"Could not parse time: {value}")
        return None
    
    def _parse_time_nullable(self, value: Any) -> Optional[time]:
        """Parse nullable time"""
        return self._parse_time(value)
    
    def _validate_required_fields(self, record: Dict, required_fields: List[str]) -> bool:
        """Validate that required fields are present and not None"""
        for field in required_fields:
            if field not in record or record[field] is None:
                self.logger.error(f"Required field '{field}' is missing or None")
                return False
        return True
    
    def get_validation_errors(self) -> List[Dict]:
        """Get list of validation errors"""
        return self.validation_errors
    
    def clear_validation_errors(self):
        """Clear validation errors"""
        self.validation_errors = []
    
    def get_error_summary(self) -> Dict:
        """Get summary of validation errors by type"""
        summary = {}
        for error in self.validation_errors:
            error_type = error['type']
            if error_type not in summary:
                summary[error_type] = 0
            summary[error_type] += 1
        return summary
