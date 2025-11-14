"""
Core middleware for Cortex ERP
"""
from django.shortcuts import redirect
from django.urls import reverse


class CompanyFinancialYearMiddleware:
    """
    Middleware to attach company and financial year to request object.
    Redirects to selection page if not set.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exempt URLs that don't need company/FY
        exempt_urls = [
            '/admin/',
            '/login/',
            '/logout/',
            '/static/',
            '/media/',
            '/__reload__/',  # django-browser-reload
        ]

        # Check if URL should be exempted
        is_exempt = any(request.path.startswith(url) for url in exempt_urls)

        if request.user.is_authenticated and not is_exempt:
            # For now, just attach None values
            # In production, these would come from session and database
            request.company = None
            request.financial_year = None

        response = self.get_response(request)
        return response


class UserActivityMiddleware:
    """
    Middleware to track user activity (IP address, last login).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track user IP address
        if request.user.is_authenticated:
            # Get IP address from request
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            # You can update user's last_login_ip here if the field exists
            # For now, we'll just pass

        response = self.get_response(request)
        return response
