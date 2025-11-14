"""
Simple Django tests for Inventory module (no browser required)
Tests URL accessibility and view responses
"""
import pytest
from django.urls import reverse
from django.test import Client


@pytest.mark.django_db
class TestInventoryURLs:
    """Test that inventory URLs are accessible"""

    def test_inventory_dashboard_url(self, client):
        """Test inventory dashboard URL exists"""
        response = client.get('/inventory/')
        # Should redirect to login (302) or show page (200)
        assert response.status_code in [200, 302]

    def test_mrs_list_url(self, client):
        """Test MRS list URL exists"""
        response = client.get('/inventory/mrs/')
        assert response.status_code in [200, 302]

    def test_min_list_url(self, client):
        """Test MIN list URL exists"""
        response = client.get('/inventory/min/')
        assert response.status_code in [200, 302]

    def test_gin_list_url(self, client):
        """Test GIN list URL exists"""
        response = client.get('/inventory/gin/')
        assert response.status_code in [200, 302]

    def test_grr_list_url(self, client):
        """Test GRR list URL exists"""
        response = client.get('/inventory/grr/')
        assert response.status_code in [200, 302]

    def test_closing_stock_url(self, client):
        """Test Closing Stock URL exists"""
        response = client.get('/inventory/closing-stock/')
        assert response.status_code in [200, 302]

    def test_closing_stock_report_url(self, client):
        """Test Closing Stock Report URL exists"""
        response = client.get('/inventory/closing-stock/report/')
        assert response.status_code in [200, 302]

    def test_stock_ledger_report_url(self, client):
        """Test Stock Ledger report URL exists"""
        response = client.get('/inventory/reports/stock-ledger/')
        assert response.status_code in [200, 302]

    def test_stock_statement_report_url(self, client):
        """Test Stock Statement report URL exists"""
        response = client.get('/inventory/reports/stock-statement/')
        assert response.status_code in [200, 302]

    def test_abc_analysis_report_url(self, client):
        """Test ABC Analysis report URL exists"""
        response = client.get('/inventory/reports/abc-analysis/')
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestInventoryResponseCodes:
    """Test inventory pages return valid HTTP codes"""

    def test_all_inventory_urls_respond(self, client):
        """Test that all major inventory URLs respond (200 or 302 redirect)"""
        urls = [
            '/inventory/',
            '/inventory/mrs/',
            '/inventory/mrs/create/',
            '/inventory/min/',
            '/inventory/mrn/',
            '/inventory/gin/',
            '/inventory/grr/',
            '/inventory/gsn/',
            '/inventory/mcn/',
            '/inventory/supplier-challan/',
            '/inventory/customer-challan/',
            '/inventory/challan/',
            '/inventory/gate-pass/',
            '/inventory/wis/',
            '/inventory/vehicle/',
            '/inventory/vehicle-master/',
            '/inventory/item-location/',
            '/inventory/closing-stock/',
            '/inventory/closing-stock/report/',
            '/inventory/reports/stock-ledger/',
            '/inventory/reports/stock-statement/',
            '/inventory/reports/moving-items/',
            '/inventory/reports/abc-analysis/',
            '/inventory/reports/work-order-shortage/',
            '/inventory/reports/work-order-issue/',
            '/inventory/reports/inward-register/',
            '/inventory/reports/outward-register/',
            '/inventory/search/',
            '/inventory/autowis-schedule/',
        ]

        failed_urls = []
        for url in urls:
            response = client.get(url)
            if response.status_code not in [200, 302]:
                failed_urls.append((url, response.status_code))

        assert len(failed_urls) == 0, f"Failed URLs: {failed_urls}"
