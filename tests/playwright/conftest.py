"""
Playwright-specific test fixtures for SAPL ERP
"""
import pytest
from playwright.sync_api import Page, expect
import os


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application"""
    return os.environ.get('DJANGO_TEST_URL', 'http://localhost:8000')


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Browser context configuration"""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
    }


@pytest.fixture
def authenticated_page(page: Page, base_url: str):
    """
    Playwright page with authenticated session
    Logs in as admin user with company and financial year context
    """
    # Navigate to login page
    page.goto(f"{base_url}/login/")

    # Fill login form
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'admin')

    # Submit login
    page.click('button[type="submit"]')

    # Wait for navigation after login
    page.wait_for_url(f"{base_url}/dashboard/", timeout=5000)

    # Verify we're logged in by checking for logout link or user menu
    expect(page.locator('text=Logout')).to_be_visible()

    return page


@pytest.fixture
def inventory_page(authenticated_page: Page, base_url: str):
    """
    Authenticated page navigated to inventory module
    """
    authenticated_page.goto(f"{base_url}/inventory/")
    authenticated_page.wait_for_load_state('networkidle')
    return authenticated_page
