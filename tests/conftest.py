"""
Pytest configuration for Sales Invoice Module Tests
"""
import pytest
import os
import sys
from playwright.sync_api import Page, expect

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup():
    """Setup test database"""
    pass


@pytest.fixture
def admin_user(db):
    """Create admin user for testing"""
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        user.set_password('admin')
        user.save()
    return user


@pytest.fixture
def logged_in_page(page: Page, admin_user, live_server):
    """
    Fixture providing a logged-in Playwright page
    """
    # Navigate to login page
    page.goto(f"{live_server.url}/login/")

    # Fill login form
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'admin')

    # Submit login
    page.click('button[type="submit"]')

    # Wait for navigation to complete
    page.wait_for_load_state('networkidle')

    return page


@pytest.fixture(scope="session")
def live_server():
    """Django live server for Playwright tests"""
    from django.test.utils import setup_test_environment, teardown_test_environment
    from django.core.management import call_command

    class LiveServer:
        url = "http://localhost:8000"

    setup_test_environment()
    yield LiveServer()
    teardown_test_environment()


@pytest.fixture
def test_customer(db):
    """Create a test customer for invoice tests"""
    from sales_distribution.models import SdCustMaster

    customer, created = SdCustMaster.objects.get_or_create(
        customercode='TEST001',
        defaults={
            'customername': 'Test Customer',
            'materialdeladdress': '123 Test Street',
            'materialdelcountry_id': 1,  # India
            'materialdelstate_id': 1,     # Maharashtra
            'materialdelcity_id': 1,      # Mumbai
            'contactperson': 'John Doe',
            'contactno': '1234567890',
            'email': 'test@example.com',
        }
    )
    return customer


@pytest.fixture
def test_po(db, test_customer):
    """Create a test Purchase Order"""
    from sales_distribution.models import SdCustPoMaster, SdCustPoDetails
    from design.models import TbldgItemMaster
    from datetime import datetime

    # Create PO Master
    po_master, created = SdCustPoMaster.objects.get_or_create(
        pono='PO-TEST-001',
        defaults={
            'customerid': test_customer,
            'sysdate': datetime.now().strftime('%d-%m-%Y'),
            'compid_id': 1,
            'finyearid_id': 1,
        }
    )

    # Get or create test item
    item, _ = TbldgItemMaster.objects.get_or_create(
        itemid=1,
        defaults={
            'itemname': 'Test Item',
            'itemcode': 'ITEM001',
        }
    )

    # Create PO Details
    po_detail, _ = SdCustPoDetails.objects.get_or_create(
        poid=po_master,
        defaults={
            'itemid': item,
            'totalqty': 100,
            'rate': 100.00,
        }
    )

    return po_master, po_detail
