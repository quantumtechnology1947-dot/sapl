"""
Sales Distribution Services - Business logic layer
Converted from ASP.NET Module/SalesDistribution
Requirements: 3.1, 3.2, 3.3, 3.4
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime
import io

from .models import (
    SdCustPoMaster, SdCustPoDetails, SdCustQuotationMaster,
    SdCustQuotationDetails, SdCustEnquiryMaster, SdCustWorkorderMaster,
    SdCustMaster, SdCustWorkorderProductsDetails, SdCustWorkorderRelease
)
from sys_admin.models import UnitMaster
from human_resource.models import TblhrOfficestaff
from django.db.models import Q, Sum, F


class CustomerService:
    """
    Service for Customer operations.
    Handles customer code generation and management.
    """

    @staticmethod
    def generate_customer_code():
        """
        Generate next customer code in unified sequence.
        Checks BOTH customer master and enquiry master to find highest CUST number.

        Returns:
            str: Next customer code (e.g., 'CUST009')

        Requirements: Unified customer code generation for Customer Master and Enquiries
        """
        # Get highest CUST number from Customer Master
        customer_max = 0
        last_customer = SdCustMaster.objects.filter(
            customerid__startswith='CUST'
        ).order_by('-salesid').first()

        if last_customer and last_customer.customerid:
            try:
                customer_max = int(last_customer.customerid.replace('CUST', ''))
            except:
                pass

        # Get highest CUST number from Enquiry Master
        enquiry_max = 0
        last_enquiry = SdCustEnquiryMaster.objects.filter(
            customerid__startswith='CUST'
        ).order_by('-enqid').first()

        if last_enquiry and last_enquiry.customerid:
            try:
                # Only extract if it's pure CUST format (not ENQ-CUST)
                if last_enquiry.customerid.startswith('CUST') and not last_enquiry.customerid.startswith('ENQ-CUST'):
                    enquiry_max = int(last_enquiry.customerid.replace('CUST', ''))
            except:
                pass

        # Use the highest number from both tables
        next_num = max(customer_max, enquiry_max) + 1

        # If both are 0, start from 1
        if next_num == 1 and customer_max == 0 and enquiry_max == 0:
            # Check if there are any customers at all
            if SdCustMaster.objects.exists():
                # There are customers but none with CUST prefix
                # Find the highest CUST number more carefully
                next_num = 1
            else:
                next_num = 1

        return f'CUST{next_num:03d}'

    @staticmethod
    def generate_customer_id_by_name(customer_name):
        """
        Generate customer ID based on first letter of customer name + sequential number.
        Format: {FirstLetter}{###} (e.g., T001 for TATA, A001 for ABB)

        Args:
            customer_name: Customer name string

        Returns:
            str: Generated customer ID (e.g., 'T001', 'A002')

        ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Convert.aspx
        """
        if not customer_name:
            raise ValidationError('Customer name is required to generate ID.')

        # Get first letter of customer name (uppercase)
        first_letter = customer_name.strip()[0].upper()

        # Find highest number for this letter in Customer Master
        customer_max = 0
        last_customer = SdCustMaster.objects.filter(
            customerid__startswith=first_letter,
            customerid__regex=f'^{first_letter}[0-9]+$'
        ).order_by('-salesid').first()

        if last_customer and last_customer.customerid:
            try:
                # Extract number part (e.g., "001" from "T001")
                number_part = last_customer.customerid[1:]
                customer_max = int(number_part)
            except:
                pass

        # Generate next number
        next_num = customer_max + 1

        return f'{first_letter}{next_num:03d}'

    @staticmethod
    @transaction.atomic
    def convert_enquiry_to_customer(enquiry_id, user_id, compid=1, finyearid=1):
        """
        Convert an enquiry to a customer by creating a new customer record.
        This is used when an enquiry was created for a NEW customer.

        Process:
        1. Fetch the enquiry
        2. Generate customer ID based on customer name
        3. Create customer record in SD_Cust_master with all address details
        4. Update enquiry with the new customer ID

        Args:
            enquiry_id: ID of the enquiry to convert
            user_id: Current user ID
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            dict: Dictionary with 'customer' and 'enquiry' objects

        Raises:
            ValidationError: If enquiry not found or already has a valid customer

        ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/CustEnquiry_Convert.aspx
        """
        try:
            enquiry = SdCustEnquiryMaster.objects.get(enqid=enquiry_id)
        except SdCustEnquiryMaster.DoesNotExist:
            raise ValidationError('Enquiry not found.')

        # Check if enquiry already has a valid customer ID (not ENQ-CUST)
        if enquiry.customerid and not (enquiry.customerid.startswith('ENQ-CUST') or enquiry.customerid == ''):
            # Check if customer already exists
            existing_customer = SdCustMaster.objects.filter(customerid=enquiry.customerid).first()
            if existing_customer:
                raise ValidationError(f'Enquiry already converted. Customer ID: {enquiry.customerid}')

        # Check if customer name exists
        if not enquiry.customername:
            raise ValidationError('Enquiry must have a customer name to convert.')

        # Generate customer ID based on name
        customer_id = CustomerService.generate_customer_id_by_name(enquiry.customername)

        # Helper function to get country ID by name
        def get_country_id(country_name):
            if not country_name:
                return None
            try:
                from sys_admin.models import Tblcountry
                country = Tblcountry.objects.filter(countryname=country_name).first()
                return country.cid if country else None
            except:
                return None

        # Helper function to get state ID by name
        def get_state_id(state_name):
            if not state_name:
                return None
            try:
                from sys_admin.models import Tblstate
                state = Tblstate.objects.filter(statename=state_name).first()
                return state.sid if state else None
            except:
                return None

        # Helper function to get city object by name
        def get_city_object(city_name):
            if not city_name:
                return None
            try:
                from sys_admin.models import Tblcity
                city = Tblcity.objects.filter(cityname=city_name).first()
                return city
            except:
                return None

        # Convert text fields to IDs/objects
        regdcountry_id = get_country_id(enquiry.regdcountry)
        regdstate_id = get_state_id(enquiry.regdstate)
        regdcity_obj = get_city_object(enquiry.regdcity)

        workcountry_id = get_country_id(enquiry.workcountry)
        workstate_id = get_state_id(enquiry.workstate)
        workcity_obj = get_city_object(enquiry.workcity)

        materialdelcountry_id = get_country_id(enquiry.materialdelcountry)
        materialdelstate_id = get_state_id(enquiry.materialdelstate)
        materialdelcity_obj = get_city_object(enquiry.materialdelcity)

        # Create customer record
        now = datetime.now()
        customer = SdCustMaster(
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S'),
            sessionid=str(user_id),
            compid=compid,
            finyearid=finyearid,
            customerid=customer_id,
            customername=enquiry.customername,
            # Copy address details from enquiry (with ID/object conversion)
            regdaddress=enquiry.regdaddress or '',
            regdcountry=regdcountry_id,
            regdstate=regdstate_id,
            regdcity=regdcity_obj,
            regdpinno=enquiry.regdpinno or '',
            regdcontactno=enquiry.regdcontactno or '',
            workaddress=enquiry.workaddress or '',
            workcountry=workcountry_id,
            workstate=workstate_id,
            workcity=workcity_obj,
            workpinno=enquiry.workpinno or '',
            workcontactno=enquiry.workcontactno or '',
            materialdeladdress=enquiry.materialdeladdress or '',
            materialdelcountry=materialdelcountry_id,
            materialdelstate=materialdelstate_id,
            materialdelcity=materialdelcity_obj,
            materialdelpinno=enquiry.materialdelpinno or '',
            materialdelcontactno=enquiry.materialdelcontactno or '',
            # Copy contact details
            contactperson=enquiry.contactperson or '',
            email=enquiry.email or '',
            contactno=enquiry.contactno or '',
            tincstno=enquiry.tincstno or '',
        )
        customer.save()

        # Update enquiry with new customer ID and mark as converted
        enquiry.customerid = customer_id
        enquiry.flag = 1  # Mark as converted
        enquiry.save()

        return {
            'customer': customer,
            'enquiry': enquiry,
            'message': f'Enquiry #{enquiry_id} converted successfully. Customer ID: {customer_id}'
        }


class POService:
    """
    Service for Customer Purchase Order operations.
    Handles complex business logic for PO management.
    """
    
    @staticmethod
    @transaction.atomic
    def create_po_from_quotation(quotation_id, user_id, compid=1, finyearid=1):
        """
        Create a new PO by auto-populating data from an approved quotation.
        
        Args:
            quotation_id: ID of the approved quotation
            user_id: Current user ID
            compid: Company ID (default: 1)
            finyearid: Financial year ID (default: 1)
        
        Returns:
            dict: Dictionary with 'po_master' and 'po_details' keys
        
        Raises:
            ValidationError: If quotation is not found or not authorized
        
        Requirements: 3.1, 1.2
        """
        try:
            quotation = SdCustQuotationMaster.objects.select_related('enqid').get(
                id=quotation_id
            )
        except SdCustQuotationMaster.DoesNotExist:
            raise ValidationError('Quotation not found.')
        
        # Check if quotation is authorized
        if quotation.authorize != 1:
            raise ValidationError('Only authorized quotations can be converted to PO.')
        
        # Get quotation details (line items)
        quotation_details = SdCustQuotationDetails.objects.filter(
            mid=quotation
        ).select_related('unit')
        
        if not quotation_details.exists():
            raise ValidationError('Quotation has no line items.')
        
        # Create PO master with data from quotation
        now = datetime.now()
        po_master = SdCustPoMaster(
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S'),
            sessionid=str(user_id),
            compid=compid,
            finyearid=finyearid,
            customerid=quotation.customerid,
            quotationno=quotation.id,
            enqid=quotation.enqid,
            paymentterms=quotation.paymentterms or '',
            warrenty=quotation.warrenty or '',
            validity=quotation.validity or '',
            remarks=quotation.remarks or ''
        )
        # Note: PO number and dates should be set by the form/view
        
        # Prepare PO details from quotation details
        po_details_data = []
        for qd in quotation_details:
            po_details_data.append({
                'itemdesc': qd.itemdesc,
                'totalqty': qd.totalqty,
                'rate': qd.rate,
                'discount': qd.discount or 0,
                'unit': qd.unit
            })
        
        return {
            'po_master': po_master,
            'po_details': po_details_data,
            'enquiry': quotation.enqid
        }
    
    @staticmethod
    def handle_file_upload(po, file):
        """
        Handle PO document attachment upload.
        
        Args:
            po: SdCustPoMaster instance
            file: Uploaded file object
        
        Returns:
            SdCustPoMaster: Updated PO object
        
        Requirements: 3.2, 1.5
        """
        if file:
            po.filename = file.name
            po.filesize = file.size
            po.contenttype = file.content_type
            po.filedata = file.read()
            po.save()
        
        return po
    
    @staticmethod
    def handle_file_download(po):
        """
        Prepare PO document for download.
        
        Args:
            po: SdCustPoMaster instance
        
        Returns:
            tuple: (file_data, filename, content_type, file_size)
        
        Raises:
            ValidationError: If no file is attached
        
        Requirements: 3.3, 2.5
        """
        if not po.filedata:
            raise ValidationError('No file attached to this PO.')
        
        file_data = io.BytesIO(po.filedata)
        
        return (
            file_data,
            po.filename,
            po.contenttype,
            po.filesize
        )
    
    @staticmethod
    def validate_po_references(po):
        """
        Check if PO has dependent work orders before deletion.
        
        Args:
            po: SdCustPoMaster instance
        
        Returns:
            dict: Dictionary with 'can_delete' (bool) and 'message' (str) keys
        
        Requirements: 3.4, 2.4
        """
        # Check for work orders
        work_orders = SdCustWorkorderMaster.objects.filter(poid=po)
        
        if work_orders.exists():
            return {
                'can_delete': False,
                'message': f'Cannot delete PO. {work_orders.count()} work order(s) exist for this PO.'
            }
        
        return {
            'can_delete': True,
            'message': 'PO can be deleted.'
        }
    
    @staticmethod
    def get_po_summary(po):
        """
        Get PO summary with calculated totals.
        
        Args:
            po: SdCustPoMaster instance
        
        Returns:
            dict: Dictionary with summary information
        """
        line_items = SdCustPoDetails.objects.filter(poid=po).select_related('unit')
        
        subtotal = 0
        for item in line_items:
            item_total = item.totalqty * item.rate
            discount_amount = item_total * (item.discount / 100) if item.discount else 0
            subtotal += (item_total - discount_amount)
        
        return {
            'po': po,
            'line_items': line_items,
            'line_item_count': line_items.count(),
            'subtotal': subtotal,
            'has_attachment': bool(po.filedata)
        }
    
    @staticmethod
    def get_pos_by_customer(customer_id):
        """
        Get all POs for a specific customer.
        
        Args:
            customer_id: Customer ID
        
        Returns:
            QuerySet: POs for the customer
        """
        return SdCustPoMaster.objects.filter(
            customerid=customer_id
        ).order_by('-podate')
    
    @staticmethod
    def get_pos_by_enquiry(enquiry_id):
        """
        Get all POs for a specific enquiry.

        Args:
            enquiry_id: Enquiry ID

        Returns:
            QuerySet: POs for the enquiry
        """
        return SdCustPoMaster.objects.filter(
            enqid_id=enquiry_id
        ).order_by('-podate')

    @staticmethod
    def calculate_total(po):
        """
        Calculate PO total with all taxes (matching Quotation calculation).

        CRITICAL: Uses same formula as QuotationService.calculate_total()

        Args:
            po: SdCustPoMaster instance

        Returns:
            dict: Dictionary with detailed calculation breakdown
        """
        # Get line items
        line_items = SdCustPoDetails.objects.filter(poid=po)

        # Step 1: Calculate base amount
        base_amount = 0
        for item in line_items:
            item_total = item.totalqty * item.rate
            discount_amount = item_total * (item.discount / 100) if item.discount else 0
            base_amount += (item_total - discount_amount)

        # Step 2: P&F (Packing & Forwarding)
        pf_amount = 0
        if po.pf:
            try:
                pf_value = float(po.pf)
                pf_amount = pf_value  # PO stores as text, assume fixed for now
            except:
                pass

        # Step 3: VAT/CST
        vat_amount = 0
        if po.vat:
            try:
                vat_amount = float(po.vat)
            except:
                pass

        # Step 4: Excise
        excise_amount = 0
        if po.excise:
            try:
                excise_amount = float(po.excise)
            except:
                pass

        # Step 5: Octroi
        octroi_amount = 0
        if po.octroi:
            try:
                octroi_amount = float(po.octroi)
            except:
                pass

        # Step 6: Freight
        freight_amount = 0
        if po.freight:
            try:
                freight_amount = float(po.freight)
            except:
                pass

        # Step 7: Other Charges
        other_charges_amount = 0
        if po.othercharges:
            try:
                other_charges_amount = float(po.othercharges)
            except:
                pass

        # Step 8: Insurance
        insurance_amount = 0
        if po.insurance:
            try:
                insurance_amount = float(po.insurance)
            except:
                pass

        # Grand Total
        grand_total = (base_amount + pf_amount + vat_amount + excise_amount +
                      octroi_amount + freight_amount + other_charges_amount +
                      insurance_amount)

        return {
            'base_amount': round(base_amount, 2),
            'pf_amount': round(pf_amount, 2),
            'vat_amount': round(vat_amount, 2),
            'excise_amount': round(excise_amount, 2),
            'octroi_amount': round(octroi_amount, 2),
            'freight_amount': round(freight_amount, 2),
            'other_charges_amount': round(other_charges_amount, 2),
            'insurance_amount': round(insurance_amount, 2),
            'grand_total': round(grand_total, 2)
        }



class ApprovalService:
    """
    Reusable service for three-level approval workflow (Check → Approve → Authorize).
    Used across Quotation, PO, and Work Order modules.

    Requirements: Approval workflow matching ASP.NET system
    """

    @staticmethod
    @transaction.atomic
    def check(model_class, record_id, user):
        """
        Mark record as checked (first level of approval).

        Args:
            model_class: Django model class (e.g., SdCustQuotationMaster)
            record_id: Primary key of the record
            user: Django User object

        Returns:
            Updated record instance

        Raises:
            ValidationError: If record already checked or not found
        """
        try:
            record = model_class.objects.get(pk=record_id)
        except model_class.DoesNotExist:
            raise ValidationError(f'{model_class.__name__} not found.')

        # Check if already checked
        if hasattr(record, 'checked') and record.checked == 1:
            raise ValidationError('Record is already checked.')

        # Update check fields
        now = datetime.now()
        record.checked = 1
        record.checkedby = user.username
        record.checkeddate = now.strftime('%d-%m-%Y')  # DD-MM-YYYY format
        record.checkedtime = now.strftime('%H:%M:%S')   # HH:MM:SS format
        record.save()

        return record

    @staticmethod
    @transaction.atomic
    def approve(model_class, record_id, user):
        """
        Mark record as approved (second level of approval).

        Args:
            model_class: Django model class
            record_id: Primary key of the record
            user: Django User object

        Returns:
            Updated record instance

        Raises:
            ValidationError: If record not checked, already approved, or not found
        """
        try:
            record = model_class.objects.get(pk=record_id)
        except model_class.DoesNotExist:
            raise ValidationError(f'{model_class.__name__} not found.')

        # Validate: Must be checked first
        if not hasattr(record, 'checked') or record.checked != 1:
            raise ValidationError('Record must be checked before approval.')

        # Check if already approved
        if hasattr(record, 'approve') and record.approve == 1:
            raise ValidationError('Record is already approved.')

        # Update approve fields
        now = datetime.now()
        record.approve = 1
        record.approvedby = user.username
        record.approvedate = now.strftime('%d-%m-%Y')  # DD-MM-YYYY format
        record.approvetime = now.strftime('%H:%M:%S')   # HH:MM:SS format
        record.save()

        return record

    @staticmethod
    @transaction.atomic
    def authorize(model_class, record_id, user):
        """
        Mark record as authorized (third level of approval).

        Args:
            model_class: Django model class
            record_id: Primary key of the record
            user: Django User object

        Returns:
            Updated record instance

        Raises:
            ValidationError: If record not approved, already authorized, or not found
        """
        try:
            record = model_class.objects.get(pk=record_id)
        except model_class.DoesNotExist:
            raise ValidationError(f'{model_class.__name__} not found.')

        # Validate: Must be approved first
        if not hasattr(record, 'approve') or record.approve != 1:
            raise ValidationError('Record must be approved before authorization.')

        # Check if already authorized
        if hasattr(record, 'authorize') and record.authorize == 1:
            raise ValidationError('Record is already authorized.')

        # Update authorize fields
        now = datetime.now()
        record.authorize = 1
        record.authorizedby = user.username
        record.authorizedate = now.strftime('%d-%m-%Y')  # DD-MM-YYYY format
        record.authorizetime = now.strftime('%H:%M:%S')   # HH:MM:SS format
        record.save()

        return record

    @staticmethod
    def can_edit(record):
        """
        Check if record can be edited (not approved).

        Args:
            record: Model instance

        Returns:
            bool: True if can edit, False otherwise
        """
        if hasattr(record, 'approve') and record.approve == 1:
            return False
        return True

    @staticmethod
    def can_delete(record):
        """
        Check if record can be deleted (not authorized).

        Args:
            record: Model instance

        Returns:
            bool: True if can delete, False otherwise
        """
        if hasattr(record, 'authorize') and record.authorize == 1:
            return False
        return True


class QuotationService:
    """
    Service for Quotation operations.
    Handles calculation, creation from enquiry, and auto-numbering.

    Requirements: Tax calculation matching ASP.NET exactly
    """

    @staticmethod
    def calculate_total(quotation):
        """
        Calculate quotation total with all taxes (P&F, VAT/CST, Excise, Octroi, Freight, Other Charges, Insurance).

        CRITICAL: Formula must match ASP.NET calculation order exactly!

        ASP.NET Calculation Order:
        1. Base Amount = Sum(Qty * Rate * (1 - Discount/100))
        2. Add P&F (percentage or fixed based on PFType)
        3. Add VAT/CST on (Base + P&F)
        4. Add Excise
        5. Add Octroi (percentage or fixed based on OctroiType)
        6. Add Freight (percentage or fixed based on FreightType)
        7. Add Other Charges (percentage or fixed based on OtherChargesType)
        8. Add Insurance (fixed amount)
        = Grand Total

        Args:
            quotation: SdCustQuotationMaster instance

        Returns:
            dict: Dictionary with detailed calculation breakdown
        """
        # Get line items
        line_items = SdCustQuotationDetails.objects.filter(mid=quotation)

        # Step 1: Calculate base amount
        base_amount = 0
        for item in line_items:
            item_total = item.totalqty * item.rate
            discount_amount = item_total * (item.discount / 100) if item.discount else 0
            base_amount += (item_total - discount_amount)

        # Step 2: P&F (Packing & Forwarding)
        pf_amount = 0
        if quotation.pf:
            if quotation.pftype == 0:  # Percentage
                pf_amount = base_amount * quotation.pf / 100
            else:  # Fixed amount
                pf_amount = quotation.pf

        # Step 3: VAT/CST (applied on base + P&F)
        taxable_amount = base_amount + pf_amount
        vat_amount = 0
        # Note: VAT/CST rate would come from master table - placeholder for now
        # if quotation.vatcst == 0:  # VAT
        #     vat_amount = taxable_amount * vat_rate / 100
        # else:  # CST
        #     vat_amount = taxable_amount * cst_rate / 100

        # Step 4: Excise
        excise_amount = 0
        # Note: Excise rate would come from master table
        # excise_amount = taxable_amount * excise_rate / 100

        # Step 5: Octroi
        octroi_amount = 0
        if quotation.octroi:
            if quotation.octroitype == 0:  # Percentage
                octroi_amount = taxable_amount * quotation.octroi / 100
            else:  # Fixed amount
                octroi_amount = quotation.octroi

        # Step 6: Freight
        freight_amount = 0
        if quotation.freight:
            if quotation.freighttype == 0:  # Percentage
                freight_amount = taxable_amount * quotation.freight / 100
            else:  # Fixed amount
                freight_amount = quotation.freight

        # Step 7: Other Charges
        other_charges_amount = 0
        if quotation.othercharges:
            if quotation.otherchargestype == 0:  # Percentage
                other_charges_amount = taxable_amount * quotation.othercharges / 100
            else:  # Fixed amount
                other_charges_amount = quotation.othercharges

        # Step 8: Insurance (always fixed)
        insurance_amount = quotation.insurance if quotation.insurance else 0

        # Grand Total
        grand_total = (taxable_amount + vat_amount + excise_amount +
                      octroi_amount + freight_amount + other_charges_amount +
                      insurance_amount)

        return {
            'base_amount': round(base_amount, 2),
            'pf_amount': round(pf_amount, 2),
            'taxable_amount': round(taxable_amount, 2),
            'vat_amount': round(vat_amount, 2),
            'excise_amount': round(excise_amount, 2),
            'octroi_amount': round(octroi_amount, 2),
            'freight_amount': round(freight_amount, 2),
            'other_charges_amount': round(other_charges_amount, 2),
            'insurance_amount': round(insurance_amount, 2),
            'grand_total': round(grand_total, 2)
        }

    @staticmethod
    @transaction.atomic
    def create_from_enquiry(enquiry_id, user_id, compid=1, finyearid=1):
        """
        Create quotation by auto-populating data from enquiry.

        Args:
            enquiry_id: ID of the enquiry
            user_id: Current user ID
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            dict: Dictionary with quotation_master and enquiry data

        Raises:
            ValidationError: If enquiry not found
        """
        try:
            enquiry = SdCustEnquiryMaster.objects.get(enqid=enquiry_id)
        except SdCustEnquiryMaster.DoesNotExist:
            raise ValidationError('Enquiry not found.')

        # Generate quotation number
        quotation_no = QuotationService.generate_quotation_no(compid, finyearid)

        # Create quotation master
        now = datetime.now()
        quotation = SdCustQuotationMaster(
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S'),
            sessionid=str(user_id),
            compid=compid,
            finyearid=finyearid,
            customerid=enquiry.customerid or '',
            quotationno=quotation_no,
            quotationdate=now.strftime('%d-%m-%Y'),
            enqid=enquiry,
            # Initialize approval fields
            checked=0,
            approve=0,
            authorize=0
        )

        return {
            'quotation_master': quotation,
            'enquiry': enquiry
        }

    @staticmethod
    def generate_quotation_no(compid=1, finyearid=1):
        """
        Generate next quotation number in format: QT-YYYY-NNNN.

        Args:
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            str: Next quotation number (e.g., 'QT-2024-0001')
        """
        from datetime import datetime

        # Get current year
        current_year = datetime.now().year

        # Get highest quotation number for this year, company, and FY
        last_quotation = SdCustQuotationMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            quotationno__startswith=f'QT-{current_year}-'
        ).order_by('-id').first()

        if last_quotation and last_quotation.quotationno:
            try:
                # Extract number from QT-YYYY-NNNN
                parts = last_quotation.quotationno.split('-')
                if len(parts) == 3:
                    last_num = int(parts[2])
                    next_num = last_num + 1
                else:
                    next_num = 1
            except:
                next_num = 1
        else:
            next_num = 1

        return f'QT-{current_year}-{next_num:04d}'


class WorkOrderService:
    """
    Service for Work Order operations.
    Requirements: 13.1, 13.2, 13.3
    """

    @staticmethod
    @transaction.atomic
    def create_from_po(po_id, user_id, compid=1, finyearid=1):
        """
        Create Work Order from PO by auto-populating data.

        Args:
            po_id: ID of the PO
            user_id: Current user ID
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            dict: Dictionary with wo_master and po data

        Raises:
            ValidationError: If PO not found
        """
        try:
            po = SdCustPoMaster.objects.select_related('enqid').get(poid=po_id)
        except SdCustPoMaster.DoesNotExist:
            raise ValidationError('PO not found.')

        # Generate work order number
        wo_no = WorkOrderService.generate_wo_no(compid, finyearid)

        # Create work order master
        now = datetime.now()
        wo = SdCustWorkorderMaster(
            sysdate=now.strftime('%d-%m-%Y'),
            systime=now.strftime('%H:%M:%S'),
            sessionid=str(user_id),
            compid=compid,
            finyearid=finyearid,
            customerid=po.customerid or '',
            pono=po.pono or '',
            wono=wo_no,
            enqid=po.enqid.enqid if po.enqid else None,
            poid=po,
            closeopen=0,  # 0 = Open
            # Other fields to be filled in form
        )

        return {
            'wo_master': wo,
            'po': po
        }

    @staticmethod
    def generate_wo_no(compid=1, finyearid=1):
        """
        Generate next work order number in format: WO-YYYY-NNNN.

        Args:
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            str: Next work order number (e.g., 'WO-2024-0001')
        """
        from datetime import datetime

        current_year = datetime.now().year

        last_wo = SdCustWorkorderMaster.objects.filter(
            compid=compid,
            finyearid=finyearid,
            wono__startswith=f'WO-{current_year}-'
        ).order_by('-id').first()

        if last_wo and last_wo.wono:
            try:
                parts = last_wo.wono.split('-')
                if len(parts) == 3:
                    last_num = int(parts[2])
                    next_num = last_num + 1
                else:
                    next_num = 1
            except:
                next_num = 1
        else:
            next_num = 1

        return f'WO-{current_year}-{next_num:04d}'

    @staticmethod
    def close_work_order(wo_id):
        """
        Close work order.
        
        ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_close.aspx
        """
        try:
            wo = SdCustWorkorderMaster.objects.get(id=wo_id)
            wo.closeopen = 1  # 1 = Closed
            wo.save()
            return {'success': True, 'message': 'Work order closed successfully.'}
        except SdCustWorkorderMaster.DoesNotExist:
            raise ValidationError('Work order not found.')
    
    @staticmethod
    def open_work_order(wo_id):
        """
        Open (reopen) a closed work order.
        
        ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_close.aspx
        """
        try:
            wo = SdCustWorkorderMaster.objects.get(id=wo_id)
            if wo.closeopen != 1:
                raise ValidationError('Work order is already open.')
            wo.closeopen = 0  # 0 = Open
            wo.save()
            return {'success': True, 'message': 'Work order opened successfully.'}
        except SdCustWorkorderMaster.DoesNotExist:
            raise ValidationError('Work order not found.')

    @staticmethod
    def validate_work_order_status(wo_id):
        """Check if work order can be edited."""
        try:
            wo = SdCustWorkorderMaster.objects.get(id=wo_id)
            if wo.closeopen == 1:
                return {'can_edit': False, 'message': 'Work order is closed.'}
            return {'can_edit': True, 'message': 'Work order is open.'}
        except SdCustWorkorderMaster.DoesNotExist:
            raise ValidationError('Work order not found.')


class WorkOrderReleaseService:
    """
    Service for Work Order Release operations.
    Handles release transactions, remaining quantity calculations, and email notifications.

    ASP.NET Reference: aaspnet/Module/SalesDistribution/Transactions/WorkOrder_ReleaseRPT.aspx
    Requirements: Work Order Release functionality
    """

    @staticmethod
    def get_releaseable_work_orders(compid=None, finyearid=None, search_term=None, search_field='CustomerName'):
        """
        Get list of work orders available for release with search capability.

        Args:
            compid: Company ID (None = all companies)
            finyearid: Financial year ID (None = all financial years)
            search_term: Search text
            search_field: Field to search in (CustomerName, EnquiryNo, PONo, WONo)

        Returns:
            QuerySet: Work orders with related data (only OPEN work orders)
        """
        queryset = SdCustWorkorderMaster.objects.all().select_related('poid')

        # Filter only OPEN work orders (closeopen = 0 or NULL, not 1)
        # closeopen = 1 means CLOSED, 0 means OPEN
        queryset = queryset.filter(Q(closeopen=0) | Q(closeopen__isnull=True))

        # Apply company and financial year filters only if provided
        if compid is not None:
            queryset = queryset.filter(compid=compid)
        if finyearid is not None:
            queryset = queryset.filter(finyearid=finyearid)

        # Apply search filter
        if search_term:
            if search_field == 'CustomerName':
                # Search in customer ID field (no customername field exists)
                queryset = queryset.filter(
                    Q(poid__customerid__icontains=search_term) |
                    Q(customerid__icontains=search_term)
                )
            elif search_field == 'EnquiryNo':
                queryset = queryset.filter(enqid__icontains=search_term)
            elif search_field == 'PONo':
                queryset = queryset.filter(pono__icontains=search_term)
            elif search_field == 'WONo':
                queryset = queryset.filter(wono__icontains=search_term)

        return queryset.order_by('-id')

    @staticmethod
    def get_work_order_release_detail(wo_id):
        """
        Get work order with products and calculate remaining quantities.

        Args:
            wo_id: Work order ID

        Returns:
            dict: Work order data with products and remaining quantities

        Raises:
            ValidationError: If work order not found
        """
        try:
            wo = SdCustWorkorderMaster.objects.select_related('poid').get(id=wo_id)
        except SdCustWorkorderMaster.DoesNotExist:
            raise ValidationError('Work order not found.')

        # Get work order products
        products = SdCustWorkorderProductsDetails.objects.filter(mid=wo_id)

        # Calculate remaining quantities for each product
        products_with_remaining = []
        for product in products:
            # IMPORTANT: Use product.id (not itemcode) for release tracking
            # This matches ASP.NET logic: ItemId in release table = product detail Id
            remaining_data = WorkOrderReleaseService.calculate_remaining_quantity_by_id(
                wo_id, product.id
            )
            products_with_remaining.append({
                'id': product.id,
                'itemcode': product.itemcode or '',
                'description': product.description or '',
                'qty': product.qty or 0,
                'released_qty': remaining_data['released_qty'],
                'remain_qty': remaining_data['remain_qty'],
                'show_controls': remaining_data['remain_qty'] > 0  # Hide checkbox/input if fully released
            })

        # Get customer name from SdCustMaster
        customer_name = wo.customerid or ''
        if wo.customerid:
            try:
                customer = SdCustMaster.objects.get(customerid=wo.customerid)
                customer_name = customer.customername or wo.customerid
            except SdCustMaster.DoesNotExist:
                pass  # Fall back to customerid if not found

        return {
            'work_order': wo,
            'products': products_with_remaining,
            'customer_name': customer_name,
            'enquiry_no': wo.enqid or '',
            'po_no': wo.pono or '',
            'wo_no': wo.wono or ''
        }

    @staticmethod
    def calculate_remaining_quantity(wo_id, item_code):
        """
        Calculate remaining quantity for a specific item in work order.
        DEPRECATED: Use calculate_remaining_quantity_by_id instead.

        Formula: Remain Qty = Total Qty - SUM(Released Qty)

        Args:
            wo_id: Work order ID
            item_code: Item code

        Returns:
            dict: Dictionary with total_qty, released_qty, remain_qty
        """
        # Get total quantity from work order products
        try:
            product = SdCustWorkorderProductsDetails.objects.get(
                mid=wo_id,
                itemcode=item_code
            )
            total_qty = product.qty or 0
        except SdCustWorkorderProductsDetails.DoesNotExist:
            return {
                'total_qty': 0,
                'released_qty': 0,
                'remain_qty': 0
            }

        # Get work order number
        try:
            wo = SdCustWorkorderMaster.objects.get(id=wo_id)
            wo_no = wo.wono
        except SdCustWorkorderMaster.DoesNotExist:
            return {
                'total_qty': total_qty,
                'released_qty': 0,
                'remain_qty': total_qty
            }

        # Calculate total released quantity for this item
        released_qty = SdCustWorkorderRelease.objects.filter(
            wono=wo_no,
            itemid=item_code
        ).aggregate(
            total=Sum('issuedqty')
        )['total'] or 0

        # Calculate remaining quantity
        remain_qty = total_qty - released_qty

        return {
            'total_qty': total_qty,
            'released_qty': released_qty,
            'remain_qty': remain_qty
        }

    @staticmethod
    def calculate_remaining_quantity_by_id(wo_id, product_detail_id):
        """
        Calculate remaining quantity using product detail ID (matches ASP.NET logic).

        IMPORTANT: ASP.NET stores ItemId in release table as the product detail Id, not itemcode!
        This is confirmed in line 98 of WorkOrder_ReleaseRPT.cs

        Formula: Remain Qty = Total Qty - SUM(Released Qty)

        Args:
            wo_id: Work order ID
            product_detail_id: Product detail ID (SD_Cust_WorkOrder_Products_Details.Id)

        Returns:
            dict: Dictionary with total_qty, released_qty, remain_qty
        """
        # Get total quantity from work order products
        try:
            product = SdCustWorkorderProductsDetails.objects.get(id=product_detail_id, mid=wo_id)
            total_qty = product.qty or 0
        except SdCustWorkorderProductsDetails.DoesNotExist:
            return {
                'total_qty': 0,
                'released_qty': 0,
                'remain_qty': 0
            }

        # Get work order number
        try:
            wo = SdCustWorkorderMaster.objects.get(id=wo_id)
            wo_no = wo.wono
        except SdCustWorkorderMaster.DoesNotExist:
            return {
                'total_qty': total_qty,
                'released_qty': 0,
                'remain_qty': total_qty
            }

        # Calculate total released quantity for this product detail id
        # CRITICAL: ItemId in release table is the product detail Id (not itemcode)
        released_qty = SdCustWorkorderRelease.objects.filter(
            wono=wo_no,
            itemid=str(product_detail_id)  # ItemId is stored as text
        ).aggregate(
            total=Sum('issuedqty')
        )['total'] or 0

        # Calculate remaining quantity
        remain_qty = total_qty - released_qty

        return {
            'total_qty': total_qty,
            'released_qty': released_qty,
            'remain_qty': remain_qty
        }

    @staticmethod
    def generate_release_number(compid=1, finyearid=1):
        """
        Generate next release number in format: 0001, 0002, etc.

        Args:
            compid: Company ID
            finyearid: Financial year ID

        Returns:
            str: Next release number (e.g., '0001', '0002')
        """
        # Get highest release number for this company and financial year
        last_release = SdCustWorkorderRelease.objects.filter(
            compid=compid,
            finyearid=finyearid
        ).order_by('-wrno').first()

        if last_release and last_release.wrno:
            try:
                # Extract number and increment
                last_num = int(last_release.wrno)
                next_num = last_num + 1
            except:
                next_num = 1
        else:
            next_num = 1

        return f'{next_num:04d}'

    @staticmethod
    @transaction.atomic
    def process_release(wo_id, release_items, user_id, compid=1, finyearid=1, email_recipients=None):
        """
        Process work order release transaction.

        Args:
            wo_id: Work order ID
            release_items: List of dicts with 'item_code' and 'to_release_qty'
            user_id: Current user ID
            compid: Company ID
            finyearid: Financial year ID
            email_recipients: List of employee IDs to send notification emails

        Returns:
            dict: Release result with wrno and created records

        Raises:
            ValidationError: If validation fails
        """
        # Get work order
        try:
            wo = SdCustWorkorderMaster.objects.get(id=wo_id)
        except SdCustWorkorderMaster.DoesNotExist:
            raise ValidationError('Work order not found.')

        # Validate work order is not closed
        if wo.closeopen == 1:
            raise ValidationError('Cannot release from a closed work order.')

        # Generate release number
        wrno = WorkOrderReleaseService.generate_release_number(compid, finyearid)

        # Prepare audit fields
        now = datetime.now()
        sysdate = now.strftime('%d-%m-%Y')
        systime = now.strftime('%H:%M:%S')
        sessionid = str(user_id)

        # Process each release item
        created_releases = []
        for item in release_items:
            product_detail_id = item['product_detail_id']  # Use product detail id (not itemcode)
            to_release_qty = float(item['to_release_qty'])

            # Skip if quantity is 0
            if to_release_qty <= 0:
                continue

            # Validate remaining quantity
            remaining_data = WorkOrderReleaseService.calculate_remaining_quantity_by_id(
                wo_id, product_detail_id
            )

            if to_release_qty > remaining_data['remain_qty']:
                raise ValidationError(
                    f"Cannot release {to_release_qty} for product detail ID {product_detail_id}. "
                    f"Only {remaining_data['remain_qty']} remaining."
                )

            # Create release record
            # IMPORTANT: ItemId in release table is the product detail Id (not itemcode)
            release = SdCustWorkorderRelease(
                wrno=wrno,
                wono=wo.wono,
                itemid=str(product_detail_id),  # Store product detail id as text
                issuedqty=to_release_qty,
                sysdate=sysdate,
                systime=systime,
                sessionid=sessionid,
                compid=compid,
                finyearid=finyearid
            )
            release.save()
            created_releases.append(release)

        if not created_releases:
            raise ValidationError('No items selected for release or all quantities are zero.')

        # Send email notifications if recipients provided
        if email_recipients:
            WorkOrderReleaseService.send_release_notifications(
                wo, wrno, created_releases, email_recipients
            )

        return {
            'success': True,
            'wrno': wrno,
            'message': f'Work order released successfully. Release No: {wrno}',
            'releases': created_releases
        }

    @staticmethod
    def get_eligible_employees(compid=1):
        """
        Get list of employees eligible to receive work order release notifications.

        Criteria:
        - WR (Work Release) permission = '1' (stored as text)
        - ResignationDate is empty (still employed)
        - CompId matches
        - UserID != 1

        Args:
            compid: Company ID

        Returns:
            QuerySet: Eligible employees with email addresses
        """
        return TblhrOfficestaff.objects.filter(
            wr='1',  # WR is stored as text field
            compid=compid
        ).exclude(
            userid=1
        ).filter(
            Q(resignationdate__isnull=True) | Q(resignationdate='')
        ).values('empid', 'employeename', 'emailid1').order_by('employeename')

    @staticmethod
    def send_release_notifications(work_order, wrno, releases, recipient_emp_ids):
        """
        Send email notifications to selected employees about work order release.

        Args:
            work_order: SdCustWorkorderMaster instance
            wrno: Release number
            releases: List of SdCustWorkorderRelease instances
            recipient_emp_ids: List of employee IDs to send emails to

        Returns:
            dict: Email send status

        Note: Email implementation depends on Django email configuration
        """
        from django.core.mail import send_mail
        from django.conf import settings

        # Get recipient email addresses
        recipients = TblhrOfficestaff.objects.filter(
            empid__in=recipient_emp_ids,
            emailid1__isnull=False
        ).exclude(emailid1='')

        if not recipients:
            return {
                'success': False,
                'message': 'No valid email addresses found for selected recipients.'
            }

        # Build email content
        subject = f'Work Order Release Notification - {wrno}'

        # Get customer name from customerid
        customer_name = work_order.customerid or ''
        if work_order.customerid:
            try:
                customer = SdCustMaster.objects.get(customerid=work_order.customerid)
                customer_name = customer.customername or work_order.customerid
            except SdCustMaster.DoesNotExist:
                pass

        message_lines = [
            f'Work Order Release Notification',
            f'',
            f'Release No: {wrno}',
            f'Work Order No: {work_order.wono}',
            f'Customer: {customer_name}',
            f'PO No: {work_order.pono or ""}',
            f'Enquiry No: {work_order.enqid or ""}',
            f'',
            f'Released Items:',
        ]

        for release in releases:
            message_lines.append(
                f'  - Item: {release.itemid}, Quantity: {release.issuedqty}'
            )

        message_lines.extend([
            f'',
            f'Released by: User ID {work_order.sessionid}',
            f'Date: {releases[0].sysdate} {releases[0].systime}',
            f'',
            f'This is an automated notification from SAPL/Cortex ERP.',
        ])

        message = '\n'.join(message_lines)

        # Extract email addresses
        email_list = [r.emailid1 for r in recipients if r.emailid1]

        # Send email (will only work if email is configured in settings)
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@sapl.com'),
                recipient_list=email_list,
                fail_silently=False
            )
            return {
                'success': True,
                'message': f'Email sent to {len(email_list)} recipient(s).'
            }
        except Exception as e:
            # Log error but don't fail the release
            return {
                'success': False,
                'message': f'Email failed: {str(e)}'
            }

    @staticmethod
    def get_release_history(wo_id=None, wo_no=None):
        """
        Get release history for a work order.

        Args:
            wo_id: Work order ID (optional)
            wo_no: Work order number (optional)

        Returns:
            QuerySet: Release records
        """
        if wo_id:
            try:
                wo = SdCustWorkorderMaster.objects.get(id=wo_id)
                wo_no = wo.wono
            except SdCustWorkorderMaster.DoesNotExist:
                return SdCustWorkorderRelease.objects.none()

        if wo_no:
            return SdCustWorkorderRelease.objects.filter(
                wono=wo_no
            ).order_by('wrno', 'itemid')

        return SdCustWorkorderRelease.objects.none()
