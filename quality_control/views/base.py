"""
Base Mixin for Quality Control Views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime


class QualityControlBaseMixin(LoginRequiredMixin):
    """Base mixin for all Quality Control views"""
    login_url = '/login/'

    def get_compid(self):
        """Get company ID from session or default to 1"""
        return self.request.session.get('compid', 1)

    def get_finyearid(self):
        """Get financial year ID from session or default to 10 (latest in system)"""
        return self.request.session.get('finyearid', 10)

    def get_session_metadata(self):
        """Get common session metadata for new records"""
        now = datetime.now()
        return {
            'sysdate': now.strftime('%Y-%m-%d'),
            'systime': now.strftime('%H:%M:%S'),
            'compid': self.get_compid(),
            'finyearid': self.get_finyearid(),
            'sessionid': self.request.session.session_key or '',
        }
