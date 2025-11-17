"""
Sales Invoice Services
Business logic for Sales Invoice module using existing database models
"""
from django.db import transaction
from django.db.models import Max, Sum
from django.core.exceptions import ValidationError
from decimal import Decimal
import re
from accounts.models import (
    TblaccSalesinvoiceMaster,
    TblaccSalesinvoiceDetails,
    TblaccSalesinvoiceMasterType,
    TblexcisecommodityMaster,
    TblexciseserMaster,
    TblvatMaster,
    TblaccServiceCategory,
    TblaccTransportmode,
    TblaccRemovableNature
)
from sales_distribution.models import SdCustPoDetails, SdCustPoMaster, SdCustMaster


class SalesInvoiceService:
    """Service class for Sales Invoice operations using existing models"""
    
    @staticmethod
    def generate_invoice_number(company_id, financial_year_id):
        """
        Generate next invoice number for the company and financial year.

        EXACT ALGORITHM from ASP.NET SalesInvoice_New_Details.aspx.cs:96-111:
        - Query: SELECT InvoiceNo WHERE CompId=X AND FinYearId=Y ORDER BY InvoiceNo DESC
        - If exists: (last_number + 1).ToString("D4")
        - If none: "0001"

        Args:
            company_id: Company ID (CompId)
            financial_year_id: Financial Year ID (FinYearId)

        Returns:
            str: Zero-padded 4-digit invoice number (e.g., "0001", "0002", ...)
        """
        # Get last invoice number - ORDER BY to match ASP.NET exactly
        last_invoice = TblaccSalesinvoiceMaster.objects.filter(
            compid=company_id,
            finyearid=financial_year_id
        ).order_by('-invoiceno').first()

        if last_invoice and last_invoice.invoiceno:
            try:
                # Convert to int, add 1, format as 4-digit zero-padded
                numeric_part = int(last_invoice.invoiceno)
                next_number = numeric_part + 1
            except (ValueError, TypeError):
                # If conversion fails, start from 1
                next_number = 1
        else:
            # No previous invoices, start from 1
            next_number = 1

        # Format as 4-digit zero-padded string (matches .ToString("D4"))
        return f"{next_number:04d}"
    
    @staticmethod
    @transaction.atomic
    def create_invoice(invoice_data, items_data, user):
        """
        Create a sales invoice with items
        
        Args:
            invoice_data: dict with invoice header fields
            items_data: list of dicts with item information
            user: User object for audit trail
        
        Returns:
            TblaccSalesinvoiceMaster object
        """
        # Generate invoice number
        invoice_number = SalesInvoiceService.generate_invoice_number(
            invoice_data['compid'],
            invoice_data['finyearid']
        )
        
        invoice_data['invoiceno'] = invoice_number
        
        # Create invoice master
        invoice = TblaccSalesinvoiceMaster.objects.create(**invoice_data)
        
        # Create invoice details
        for item_data in items_data:
            item_data['mid'] = invoice
            item_data['invoiceno'] = invoice_number
            TblaccSalesinvoiceDetails.objects.create(**item_data)
        
        return invoice
    
    @staticmethod
    @transaction.atomic
    def update_invoice(invoice, invoice_data, items_data):
        """
        Update an existing sales invoice
        
        Args:
            invoice: TblaccSalesinvoiceMaster object to update
            invoice_data: dict with invoice header fields
            items_data: list of dicts with item information
        
        Returns:
            Updated TblaccSalesinvoiceMaster object
        """
        # Update invoice header
        for key, value in invoice_data.items():
            setattr(invoice, key, value)
        invoice.save()
        
        # Delete existing items and create new ones
        TblaccSalesinvoiceDetails.objects.filter(mid=invoice).delete()
        
        for item_data in items_data:
            item_data['mid'] = invoice
            item_data['invoiceno'] = invoice.invoiceno
            TblaccSalesinvoiceDetails.objects.create(**item_data)
        
        return invoice
    
    @staticmethod
    def get_invoice_items(invoice):
        """Get all items for an invoice"""
        return TblaccSalesinvoiceDetails.objects.filter(mid=invoice)
    
    @staticmethod
    def calculate_item_total(qty, rate):
        """Calculate total for an item"""
        return float(qty) * float(rate)
    
    @staticmethod
    def copy_buyer_to_consignee(invoice_data):
        """
        Copy buyer data to consignee fields
        
        Args:
            invoice_data: dict with invoice data including buyer fields
        
        Returns:
            dict with consignee fields populated from buyer
        """
        return {
            'cong_name': invoice_data.get('buyer_name'),
            'cong_add': invoice_data.get('buyer_add'),
            'cong_state': invoice_data.get('buyer_state'),
            'cong_country': invoice_data.get('buyer_country'),
            'cong_city': invoice_data.get('buyer_city'),
            'cong_cotper': invoice_data.get('buyer_cotper'),
            'cong_ph': invoice_data.get('buyer_ph'),
            'cong_mob': invoice_data.get('buyer_mob'),
            'cong_email': invoice_data.get('buyer_email'),
            'cong_tin': invoice_data.get('buyer_tin'),
            'cong_vat': invoice_data.get('buyer_vat'),
            'cong_fax': invoice_data.get('buyer_fax'),
            'cong_ecc': invoice_data.get('buyer_ecc'),
        }


class SalesInvoiceSearchService:
    """Service class for searching and filtering sales invoices"""
    
    @staticmethod
    def search_invoices(company_id, financial_year_id, search_query=None, search_type='customer_name'):
        """
        Search invoices by various criteria
        
        Args:
            company_id: Company ID
            financial_year_id: Financial Year ID
            search_query: Search string
            search_type: Type of search (customer_name, po_number, invoice_number)
        
        Returns:
            QuerySet of TblaccSalesinvoiceMaster objects
        """
        queryset = TblaccSalesinvoiceMaster.objects.filter(
            compid=company_id,
            finyearid=financial_year_id
        )
        
        if search_query:
            if search_type == 'customer_name':
                queryset = queryset.filter(buyer_name__icontains=search_query)
            elif search_type == 'po_number':
                queryset = queryset.filter(pono__icontains=search_query)
            elif search_type == 'invoice_number':
                queryset = queryset.filter(invoiceno__icontains=search_query)
        
        return queryset.order_by('-id')
    
    @staticmethod
    def get_invoice_list(company_id, financial_year_id, page=1, per_page=20):
        """
        Get paginated list of invoices
        
        Args:
            company_id: Company ID
            financial_year_id: Financial Year ID
            page: Page number
            per_page: Items per page
        
        Returns:
            QuerySet of TblaccSalesinvoiceMaster objects
        """
        queryset = TblaccSalesinvoiceMaster.objects.filter(
            compid=company_id,
            finyearid=financial_year_id
        ).order_by('-id')
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return queryset[start:end]


class SalesInvoiceLookupService:
    """Service for looking up master data IDs and names"""
    
    # Mode of Transport mapping
    TRANSPORT_MODES = {
        1: 'By Road',
        2: 'By Air',
        3: 'By Ship',
        4: 'By Post',
        5: 'By Currier',
    }
    
    # Customer Category mapping
    CUSTOMER_CATEGORIES = {
        1: 'Industrial Consumer',
        2: 'WholeSale Dealer',
        3: 'Government Department',
        4: 'Other',
    }
    
    # Invoice Mode mapping
    INVOICE_MODES = {
        'Within Maharashtra': 'Within Maharashtra',
        'Out Of Maharashtra': 'Out Of Maharashtra',
    }
    
    @staticmethod
    def get_transport_mode_name(mode_id):
        """Get transport mode name from ID"""
        return SalesInvoiceLookupService.TRANSPORT_MODES.get(mode_id, 'Unknown')
    
    @staticmethod
    def get_transport_mode_id(mode_name):
        """Get transport mode ID from name"""
        for id, name in SalesInvoiceLookupService.TRANSPORT_MODES.items():
            if name == mode_name:
                return id
        return 1  # Default to By Road
    
    @staticmethod
    def get_customer_category_name(category_id):
        """Get customer category name from ID"""
        return SalesInvoiceLookupService.CUSTOMER_CATEGORIES.get(category_id, 'Unknown')
    
    @staticmethod
    def get_customer_category_id(category_name):
        """Get customer category ID from name"""
        for id, name in SalesInvoiceLookupService.CUSTOMER_CATEGORIES.items():
            if name == category_name:
                return id
        return 1  # Default to Industrial Consumer
    
    @staticmethod
    def get_transport_mode_choices():
        """Get choices for transport mode dropdown"""
        return [(id, name) for id, name in SalesInvoiceLookupService.TRANSPORT_MODES.items()]
    
    @staticmethod
    def get_customer_category_choices():
        """Get choices for customer category dropdown"""
        return [(id, name) for id, name in SalesInvoiceLookupService.CUSTOMER_CATEGORIES.items()]
    
    @staticmethod
    def get_invoice_mode_choices():
        """Get choices for invoice mode dropdown"""
        return [(mode, mode) for mode in SalesInvoiceLookupService.INVOICE_MODES.keys()]

    @staticmethod
    def get_commodity_choices():
        """Get choices for excisable commodity dropdown from database"""
        commodities = TblexcisecommodityMaster.objects.all().order_by('terms')
        return [(c.id, c.terms) for c in commodities]

    @staticmethod
    def get_tariff_for_commodity(commodity_id):
        """Get tariff heading for a commodity"""
        try:
            commodity = TblexcisecommodityMaster.objects.get(id=commodity_id)
            return commodity.chaphead if commodity.chaphead else ''
        except TblexcisecommodityMaster.DoesNotExist:
            return ''

    @staticmethod
    def get_tax_rate_choices(tax_type='cenvat'):
        """Get tax rate choices from database

        Args:
            tax_type: 'cenvat' for CGST/IGST, 'vat' for VAT/SGST
        """
        if tax_type == 'cenvat':
            rates = TblexciseserMaster.objects.filter(live=1).order_by('terms')
        else:  # vat
            rates = TblvatMaster.objects.all().order_by('terms')
        return [(r.id, r.terms) for r in rates]

    @staticmethod
    def extract_rate_from_text(rate_text):
        """Extract numeric rate from text like 'IGST@18%' -> 18.0

        Args:
            rate_text: String like 'IGST@18%', 'SGST@ 9%'

        Returns:
            Decimal rate value
        """
        if not rate_text:
            return Decimal('0.00')

        # Extract number from text using regex
        match = re.search(r'(\d+\.?\d*)', str(rate_text))
        if match:
            return Decimal(match.group(1))
        return Decimal('0.00')

    @staticmethod
    def get_service_category_choices():
        """Get service category choices from database"""
        categories = TblaccServiceCategory.objects.all().order_by('description')
        return [(c.id, c.description) for c in categories]

    @staticmethod
    def get_transport_mode_choices_from_db():
        """Get transport mode choices from database"""
        modes = TblaccTransportmode.objects.all().order_by('description')
        return [(m.id, m.description) for m in modes]

    @staticmethod
    def get_nature_of_removal_choices():
        """Get nature of removal choices from database"""
        natures = TblaccRemovableNature.objects.all().order_by('description')
        return [(n.id, n.description) for n in natures]


class SalesInvoiceValidationService:
    """Service class for validating sales invoice data"""

    @staticmethod
    def get_remaining_quantity(po_detail_id, company_id, exclude_invoice_id=None):
        """Calculate remaining quantity for a PO detail item

        Args:
            po_detail_id: ID of SD_Cust_PO_Details record
            company_id: Company ID to filter invoices
            exclude_invoice_id: Invoice ID to exclude (for editing)

        Returns:
            dict with totalqty, invoiced_qty, and remaining_qty
        """
        try:
            po_detail = SdCustPoDetails.objects.get(id=po_detail_id)
            total_qty = Decimal(str(po_detail.totalqty or 0))
        except SdCustPoDetails.DoesNotExist:
            return {
                'totalqty': Decimal('0.00'),
                'invoiced_qty': Decimal('0.00'),
                'remaining_qty': Decimal('0.00')
            }

        # Sum all invoiced quantities for this PO detail item
        invoices_query = TblaccSalesinvoiceDetails.objects.filter(
            itemid=po_detail_id,
            mid__compid=company_id
        )

        # Exclude current invoice if editing
        if exclude_invoice_id:
            invoices_query = invoices_query.exclude(mid_id=exclude_invoice_id)

        invoiced_qty = invoices_query.aggregate(
            total=Sum('reqqty')
        )['total'] or Decimal('0.00')

        remaining_qty = total_qty - Decimal(str(invoiced_qty))

        return {
            'totalqty': total_qty,
            'invoiced_qty': Decimal(str(invoiced_qty)),
            'remaining_qty': remaining_qty
        }

    @staticmethod
    def validate_item_quantity(po_detail_id, requested_qty, company_id, exclude_invoice_id=None):
        """Validate that requested quantity doesn't exceed remaining quantity

        Args:
            po_detail_id: ID of PO detail item
            requested_qty: Quantity being requested in this invoice
            company_id: Company ID
            exclude_invoice_id: Invoice ID to exclude (for editing)

        Raises:
            ValidationError if quantity exceeds remaining

        Returns:
            bool True if valid
        """
        remaining = SalesInvoiceValidationService.get_remaining_quantity(
            po_detail_id, company_id, exclude_invoice_id
        )

        requested_qty = Decimal(str(requested_qty))

        if requested_qty > remaining['remaining_qty']:
            raise ValidationError(
                f"Requested quantity {requested_qty} exceeds remaining quantity "
                f"{remaining['remaining_qty']} for this item."
            )

        return True

    @staticmethod
    def get_amount_percentage_status(po_detail_id, company_id, exclude_invoice_id=None):
        """Get total amount percentage used for a PO detail item

        Args:
            po_detail_id: ID of PO detail item
            company_id: Company ID
            exclude_invoice_id: Invoice ID to exclude (for editing)

        Returns:
            dict with used_percentage and remaining_percentage
        """
        invoices_query = TblaccSalesinvoiceDetails.objects.filter(
            itemid=po_detail_id,
            mid__compid=company_id
        )

        if exclude_invoice_id:
            invoices_query = invoices_query.exclude(mid_id=exclude_invoice_id)

        used_percentage = invoices_query.aggregate(
            total=Sum('amtinper')
        )['total'] or Decimal('0.00')

        used_percentage = Decimal(str(used_percentage))
        remaining_percentage = Decimal('100.00') - used_percentage

        return {
            'used_percentage': used_percentage,
            'remaining_percentage': remaining_percentage
        }

    @staticmethod
    def validate_amount_percentage(po_detail_id, requested_percentage, company_id, exclude_invoice_id=None):
        """Validate that amount percentage doesn't exceed 100%

        Args:
            po_detail_id: ID of PO detail item
            requested_percentage: Percentage being requested
            company_id: Company ID
            exclude_invoice_id: Invoice ID to exclude (for editing)

        Raises:
            ValidationError if percentage would exceed 100%

        Returns:
            bool True if valid
        """
        status = SalesInvoiceValidationService.get_amount_percentage_status(
            po_detail_id, company_id, exclude_invoice_id
        )

        requested_percentage = Decimal(str(requested_percentage))

        if requested_percentage > status['remaining_percentage']:
            raise ValidationError(
                f"Requested percentage {requested_percentage}% would exceed 100%. "
                f"Only {status['remaining_percentage']}% remaining for this item."
            )

        return True

    @staticmethod
    def get_po_items_with_remaining_qty(po_id, company_id):
        """Get all PO detail items with remaining quantities

        Args:
            po_id: Purchase Order ID
            company_id: Company ID

        Returns:
            List of dicts with item details and remaining quantities
        """
        po_details = SdCustPoDetails.objects.filter(poid=po_id)
        items = []

        for detail in po_details:
            remaining_info = SalesInvoiceValidationService.get_remaining_quantity(
                detail.id, company_id
            )

            # Only include items with remaining quantity > 0
            if remaining_info['remaining_qty'] > 0:
                percentage_info = SalesInvoiceValidationService.get_amount_percentage_status(
                    detail.id, company_id
                )

                items.append({
                    'id': detail.id,
                    'itemdesc': detail.itemdesc,
                    'totalqty': remaining_info['totalqty'],
                    'invoiced_qty': remaining_info['invoiced_qty'],
                    'remaining_qty': remaining_info['remaining_qty'],
                    'unit': detail.unit,
                    'rate': detail.rate,
                    'used_percentage': percentage_info['used_percentage'],
                    'remaining_percentage': percentage_info['remaining_percentage']
                })

        return items


class SalesInvoiceCalculationService:
    """Service class for calculating invoice totals and taxes"""

    @staticmethod
    def calculate_item_subtotal(items_data):
        """Calculate subtotal from items

        Args:
            items_data: List of dicts with 'reqqty' and 'rate'

        Returns:
            Decimal subtotal amount
        """
        subtotal = Decimal('0.00')

        for item in items_data:
            qty = Decimal(str(item.get('reqqty', 0)))
            rate = Decimal(str(item.get('rate', 0)))
            subtotal += qty * rate

        return subtotal

    @staticmethod
    def calculate_tax_amount(subtotal, tax_rate_text):
        """Calculate tax amount from subtotal and tax rate

        Args:
            subtotal: Subtotal amount
            tax_rate_text: Tax rate text like 'IGST@18%'

        Returns:
            Decimal tax amount
        """
        rate = SalesInvoiceLookupService.extract_rate_from_text(tax_rate_text)
        subtotal = Decimal(str(subtotal))

        return (subtotal * rate) / Decimal('100.00')

    @staticmethod
    def calculate_invoice_totals(invoice_data, items_data):
        """Calculate all totals for an invoice

        Args:
            invoice_data: Dict with invoice header data (tax selections, etc.)
            items_data: List of dicts with item data

        Returns:
            dict with calculated amounts
        """
        subtotal = SalesInvoiceCalculationService.calculate_item_subtotal(items_data)

        # Get tax rate texts from invoice data
        cenvat_text = invoice_data.get('cenvat', '')
        vat_text = invoice_data.get('vat', '')

        # Calculate tax amounts
        cenvat_amount = SalesInvoiceCalculationService.calculate_tax_amount(
            subtotal, cenvat_text
        )
        vat_amount = SalesInvoiceCalculationService.calculate_tax_amount(
            subtotal, vat_text
        )

        # Get other amounts
        other_amt = Decimal(str(invoice_data.get('otheramt', 0)))
        add_amt = Decimal(str(invoice_data.get('addamt', 0)))
        deduction = Decimal(str(invoice_data.get('deduction', 0)))
        pf = Decimal(str(invoice_data.get('pf', 0)))
        sed = Decimal(str(invoice_data.get('sed', 0)))
        aed = Decimal(str(invoice_data.get('aed', 0)))
        freight = Decimal(str(invoice_data.get('freight', 0)))
        insurance = Decimal(str(invoice_data.get('insurance', 0)))

        # Calculate grand total
        grand_total = (
            subtotal +
            cenvat_amount +
            vat_amount +
            other_amt +
            add_amt +
            pf +
            sed +
            aed +
            freight +
            insurance -
            deduction
        )

        return {
            'subtotal': subtotal,
            'cenvat_amount': cenvat_amount,
            'vat_amount': vat_amount,
            'other_amt': other_amt,
            'add_amt': add_amt,
            'deduction': deduction,
            'pf': pf,
            'sed': sed,
            'aed': aed,
            'freight': freight,
            'insurance': insurance,
            'grand_total': grand_total
        }
