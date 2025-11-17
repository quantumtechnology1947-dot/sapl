"""
Playwright-specific fixtures and configuration
NOTE: Using pytest-playwright plugin's fixtures instead of custom ones
This avoids async/sync conflicts with Django fixtures
"""
import pytest

# pytest-playwright plugin provides these fixtures automatically:
# - browser
# - page
# - context
# No need to define custom ones
