"""
Number Sequence Service - Manages auto-numbering across all modules

Provides centralized utilities for generating sequential numbers for:
- Customer IDs
- Purchase Order numbers
- Invoice numbers
- Item codes
- And other auto-numbered fields
"""
from typing import Optional, Callable
from django.db import models, transaction
from django.db.models import Max


class NumberSequenceService:
    """
    Service class for managing auto-number generation
    """

    @staticmethod
    def get_next_number(
        model: models.Model,
        field_name: str,
        prefix: str = '',
        suffix: str = '',
        padding: int = 4,
        filter_kwargs: Optional[dict] = None
    ) -> str:
        """
        Generate next sequential number for a model field

        Args:
            model: Django model class
            field_name: Field name to get max value from
            prefix: Prefix to add before number (e.g., 'CUST')
            suffix: Suffix to add after number (e.g., '-2025')
            padding: Zero-padding width (default 4 = '0001')
            filter_kwargs: Optional filters for queryset (e.g., {'compid': 1})

        Returns:
            Next sequential number string

        Example:
            # Generate 'CUST0001'
            NumberSequenceService.get_next_number(
                SdCustMaster,
                'salesid',
                prefix='CUST',
                padding=4
            )

            # Generate 'PO-2025-0001'
            NumberSequenceService.get_next_number(
                SdPo,
                'poid',
                prefix='PO-2025-',
                padding=4
            )
        """
        queryset = model.objects.all()

        # Apply filters if provided
        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)

        # Get max value
        max_value = queryset.aggregate(Max(field_name))[f'{field_name}__max']

        # Calculate next number
        if max_value is None:
            next_num = 1
        else:
            # If max_value is string with prefix/suffix, extract number
            if isinstance(max_value, str):
                # Remove prefix and suffix to get numeric part
                numeric_part = max_value
                if prefix:
                    numeric_part = numeric_part.replace(prefix, '')
                if suffix:
                    numeric_part = numeric_part.replace(suffix, '')
                try:
                    next_num = int(numeric_part) + 1
                except ValueError:
                    next_num = 1
            else:
                next_num = int(max_value) + 1

        # Format with padding
        padded_num = str(next_num).zfill(padding)

        # Return with prefix and suffix
        return f"{prefix}{padded_num}{suffix}"

    @staticmethod
    def get_next_number_by_year(
        model: models.Model,
        field_name: str,
        year: int,
        prefix: str = '',
        padding: int = 4,
        filter_kwargs: Optional[dict] = None
    ) -> str:
        """
        Generate next sequential number for a specific year

        Args:
            model: Django model class
            field_name: Field name to get max value from
            year: Financial year (e.g., 2025)
            prefix: Prefix before year (e.g., 'PO')
            padding: Zero-padding width
            filter_kwargs: Optional filters

        Returns:
            Next number string (e.g., 'PO-2025-0001')

        Example:
            NumberSequenceService.get_next_number_by_year(
                SdPo,
                'poid',
                year=2025,
                prefix='PO',
                padding=4
            )
        """
        year_prefix = f"{prefix}-{year}-" if prefix else f"{year}-"
        return NumberSequenceService.get_next_number(
            model=model,
            field_name=field_name,
            prefix=year_prefix,
            padding=padding,
            filter_kwargs=filter_kwargs
        )

    @staticmethod
    def get_next_number_by_company(
        model: models.Model,
        field_name: str,
        company_id: int,
        prefix: str = '',
        padding: int = 4
    ) -> str:
        """
        Generate next sequential number for a specific company

        Args:
            model: Django model class
            field_name: Field name to get max value from
            company_id: Company ID
            prefix: Number prefix
            padding: Zero-padding width

        Returns:
            Next number string

        Example:
            NumberSequenceService.get_next_number_by_company(
                SdCustMaster,
                'salesid',
                company_id=1,
                prefix='CUST',
                padding=4
            )
        """
        return NumberSequenceService.get_next_number(
            model=model,
            field_name=field_name,
            prefix=prefix,
            padding=padding,
            filter_kwargs={'compid': company_id}
        )

    @staticmethod
    @transaction.atomic
    def generate_unique_code(
        model: models.Model,
        field_name: str,
        generator_func: Callable[[], str],
        max_attempts: int = 100
    ) -> str:
        """
        Generate unique code with custom generator function

        Ensures uniqueness by checking database and retrying if needed

        Args:
            model: Django model class
            field_name: Field name to check for uniqueness
            generator_func: Function that generates code
            max_attempts: Maximum retry attempts

        Returns:
            Unique code string

        Raises:
            ValueError: If unable to generate unique code after max_attempts

        Example:
            def custom_generator():
                import random
                return f"CUST{random.randint(1000, 9999)}"

            code = NumberSequenceService.generate_unique_code(
                SdCustMaster,
                'customerid',
                custom_generator
            )
        """
        for _ in range(max_attempts):
            code = generator_func()
            if not model.objects.filter(**{field_name: code}).exists():
                return code

        raise ValueError(
            f"Unable to generate unique {field_name} after {max_attempts} attempts"
        )

    @staticmethod
    def format_code(
        number: int,
        prefix: str = '',
        suffix: str = '',
        padding: int = 4,
        separator: str = ''
    ) -> str:
        """
        Format a number with prefix, suffix, and padding

        Args:
            number: Numeric value
            prefix: Prefix string
            suffix: Suffix string
            padding: Zero-padding width
            separator: Separator between parts

        Returns:
            Formatted code string

        Example:
            NumberSequenceService.format_code(
                123,
                prefix='ITEM',
                padding=6
            ) # Returns: 'ITEM000123'

            NumberSequenceService.format_code(
                45,
                prefix='PO',
                suffix='2025',
                padding=4,
                separator='-'
            ) # Returns: 'PO-0045-2025'
        """
        padded = str(number).zfill(padding)

        if separator:
            parts = [p for p in [prefix, padded, suffix] if p]
            return separator.join(parts)
        else:
            return f"{prefix}{padded}{suffix}"


# Convenience functions for common use cases

def get_next_customer_code(company_id: int = 1) -> str:
    """Generate next customer code (e.g., 'CUST0001')"""
    from sales_distribution.models import SdCustMaster
    return NumberSequenceService.get_next_number_by_company(
        SdCustMaster,
        'salesid',
        company_id=company_id,
        prefix='CUST',
        padding=4
    )


def get_next_po_number(year: int, company_id: int = 1) -> str:
    """Generate next PO number (e.g., 'PO-2025-0001')"""
    from sales_distribution.models import SdPo
    return NumberSequenceService.get_next_number(
        SdPo,
        'poid',
        prefix=f'PO-{year}-',
        padding=4,
        filter_kwargs={'compid': company_id}
    )


def get_next_item_code(company_id: int = 1) -> str:
    """Generate next item code (e.g., 'ITEM000001')"""
    from inventory.models import ItemMaster
    return NumberSequenceService.get_next_number_by_company(
        ItemMaster,
        'id',
        company_id=company_id,
        prefix='ITEM',
        padding=6
    )
