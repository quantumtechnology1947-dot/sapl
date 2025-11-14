"""
Pytest configuration and fixtures for SAPL ERP tests
"""
import pytest
import django
import os
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup():
    """Setup test database"""
    pass


@pytest.fixture
def client():
    """Django test client"""
    return Client()


@pytest.fixture
def authenticated_client(db):
    """Authenticated Django test client with session setup"""
    client = Client()

    # Get or create admin user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True
        }
    )

    if created:
        user.set_password('admin')
        user.save()

    # Login
    client.login(username='admin', password='admin')

    # Setup session with company and financial year
    session = client.session
    session['compid'] = 1
    session['finyearid'] = 1
    session.save()

    return client


@pytest.fixture
def test_user(db):
    """Create a test user"""
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        is_staff=True
    )
    return user
