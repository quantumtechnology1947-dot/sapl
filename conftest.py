"""
pytest configuration for Playwright tests
"""
import pytest
from playwright.sync_api import Browser


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for containerized environment"""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch args for containerized environment"""
    return {
        **browser_type_launch_args,
        "headless": True,
        "args": [
            "--disable-dev-shm-usage",  # Overcome limited resource problems
            "--no-sandbox",  # Required for running in Docker
            "--disable-setuid-sandbox",  # Required for running in Docker
            "--disable-gpu",  # Disable GPU hardware acceleration
            "--disable-software-rasterizer",  # Disable software rasterizer
            "--single-process",  # Run in single process mode
        ],
    }
