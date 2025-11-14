"""
Financial Year Middleware

Automatically initializes and injects financial year context into requests.
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from core.context_manager import FinancialYearContextManager

logger = logging.getLogger(__name__)


class FinancialYearMiddleware(MiddlewareMixin):
    """
    Middleware to automatically manage financial year context.
    
    Features:
    - Auto-detects FY on first request
    - Injects context into request object
    - Handles unauthenticated users gracefully
    - Logs context switches
    """
    
    def process_request(self, request):
        """
        Process incoming request and inject context.
        
        Args:
            request: Django request object
        """
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            request.financial_context = None
            return None
        
        # Create context manager
        context_manager = FinancialYearContextManager(request)
        
        # Initialize context if not already set
        if not context_manager.has_context():
            try:
                company_id, finyear_id = context_manager.initialize_context(request.user)
                
                if company_id and finyear_id:
                    logger.info(
                        f"Initialized context for user {request.user.username}: "
                        f"Company={company_id}, FinYear={finyear_id}"
                    )
                else:
                    logger.warning(
                        f"Could not initialize context for user {request.user.username}"
                    )
            except Exception as e:
                logger.error(f"Error initializing context: {e}")
                request.financial_context = None
                return None
        
        # Inject context manager into request
        request.financial_context = context_manager
        
        # Also inject context dict for easy template access
        request.context_data = context_manager.get_context()
        
        return None
    
    def process_template_response(self, request, response):
        """
        Inject context into template context.
        
        Args:
            request: Django request object
            response: Template response object
            
        Returns:
            Modified response
        """
        if hasattr(request, 'context_data') and hasattr(response, 'context_data'):
            response.context_data['financial_context'] = request.context_data
        
        return response
