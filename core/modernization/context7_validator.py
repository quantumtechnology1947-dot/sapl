"""
Context7 MCP Integration for Django Pattern Validation

Uses Context7 MCP server to validate Django code against latest documentation.
Requirements: 1.1, 1.2, 1.3, 1.4
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import MCP client (optional dependency)
try:
    from mcp import Client as MCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPClient = None  # type: ignore
    logger.warning("MCP client not available. Context7 integration will use offline validation only.")


@dataclass
class ValidationResult:
    """Result of pattern validation"""
    is_valid: bool
    pattern_name: str
    current_pattern: str
    recommended_pattern: Optional[str] = None
    documentation_url: Optional[str] = None
    severity: str = 'info'  # 'info', 'warning', 'error'
    message: str = ''


class Context7Validator:
    """
    Validates Django code patterns against Context7 MCP server documentation
    
    Requirements: 1.1, 1.2, 1.3
    """
    
    def __init__(self, library_id: str = "/django/django/5_2_6", use_mcp: bool = True):
        """
        Initialize validator with Django library ID
        
        Args:
            library_id: Context7 library identifier for Django version
            use_mcp: Whether to use MCP client for live documentation queries
        """
        self.library_id = library_id
        self.django_version = "5.2.6"
        self.use_mcp = use_mcp and MCP_AVAILABLE
        
        # Cache for documentation queries
        self._doc_cache: Dict[str, str] = {}
        
        # MCP client (initialized on first use)
        self._mcp_client = None
        
        if self.use_mcp:
            logger.info(f"Initialized Context7Validator with MCP integration for {library_id}")
        else:
            logger.info(f"Initialized Context7Validator in offline mode for {library_id}")
    
    def validate_cbv_pattern(self, view_code: str, view_name: str) -> ValidationResult:
        """
        Validate if a class-based view follows Django 5.2.6 patterns
        
        Requirements: 1.2, 3.1, 3.2
        
        Args:
            view_code: Source code of the view
            view_name: Name of the view class
            
        Returns:
            ValidationResult with validation details
        """
        # Check if it's a proper CBV
        if not self._is_class_based_view(view_code):
            return ValidationResult(
                is_valid=False,
                pattern_name='class_based_view',
                current_pattern='function_based_view',
                recommended_pattern='Use Django generic views (ListView, DetailView, etc.)',
                severity='warning',
                message=f'{view_name} should be converted to a class-based view'
            )
        
        # Check for proper generic view usage
        generic_views = ['ListView', 'DetailView', 'CreateView', 'UpdateView', 'DeleteView', 'FormView', 'TemplateView']
        uses_generic = any(gv in view_code for gv in generic_views)
        
        if not uses_generic:
            return ValidationResult(
                is_valid=False,
                pattern_name='generic_view',
                current_pattern='custom_cbv',
                recommended_pattern='Inherit from Django generic views',
                severity='info',
                message=f'{view_name} should inherit from a Django generic view'
            )
        
        # Check for proper mixin usage
        validation_issues = []
        
        # Check for LoginRequiredMixin
        if 'LoginRequiredMixin' not in view_code and '@login_required' in view_code:
            validation_issues.append('Use LoginRequiredMixin instead of @login_required decorator')
        
        # Check for proper queryset optimization
        if 'get_queryset' in view_code:
            if 'select_related' not in view_code and 'prefetch_related' not in view_code:
                validation_issues.append('Consider using select_related() or prefetch_related() for query optimization')
        
        if validation_issues:
            return ValidationResult(
                is_valid=False,
                pattern_name='cbv_best_practices',
                current_pattern=view_name,
                recommended_pattern='; '.join(validation_issues),
                severity='info',
                message=f'{view_name} can be improved'
            )
        
        return ValidationResult(
            is_valid=True,
            pattern_name='class_based_view',
            current_pattern=view_name,
            message=f'{view_name} follows Django 5.2.6 CBV patterns'
        )
    
    def get_recommended_mixins(self, view_type: str) -> List[str]:
        """
        Get recommended mixins for a view type
        
        Requirements: 1.2, 3.3
        
        Args:
            view_type: Type of view (ListView, DetailView, etc.)
            
        Returns:
            List of recommended mixin names
        """
        mixin_recommendations = {
            'ListView': ['LoginRequiredMixin', 'PermissionRequiredMixin'],
            'DetailView': ['LoginRequiredMixin', 'PermissionRequiredMixin'],
            'CreateView': ['LoginRequiredMixin', 'PermissionRequiredMixin', 'SuccessMessageMixin'],
            'UpdateView': ['LoginRequiredMixin', 'PermissionRequiredMixin', 'SuccessMessageMixin'],
            'DeleteView': ['LoginRequiredMixin', 'PermissionRequiredMixin', 'SuccessMessageMixin'],
            'FormView': ['LoginRequiredMixin', 'FormValidMessageMixin'],
            'TemplateView': ['LoginRequiredMixin'],
        }
        
        return mixin_recommendations.get(view_type, ['LoginRequiredMixin'])
    
    def validate_form_pattern(self, form_code: str, form_name: str) -> ValidationResult:
        """
        Validate if a form follows Django 5.2.6 patterns
        
        Requirements: 1.2, 3.2
        
        Args:
            form_code: Source code of the form
            form_name: Name of the form class
            
        Returns:
            ValidationResult with validation details
        """
        issues = []
        
        # Check if it's a ModelForm
        if 'ModelForm' in form_code:
            # Check for Meta class
            if 'class Meta:' not in form_code:
                issues.append('ModelForm should have a Meta class')
            
            # Check for proper field definition
            if 'fields = ' not in form_code and 'exclude = ' not in form_code:
                issues.append('ModelForm Meta should define fields or exclude')
        
        # Check for manual validation that could use validators
        if 'def clean_' in form_code:
            # This is fine, but check if it could use built-in validators
            if 'MinValueValidator' not in form_code and 'MaxValueValidator' not in form_code:
                issues.append('Consider using Django validators instead of custom clean methods')
        
        # Check for widget customization
        if 'widgets = {' in form_code:
            # Good practice
            pass
        elif 'widget=' in form_code:
            # Also good
            pass
        else:
            issues.append('Consider customizing widgets for better UX')
        
        if issues:
            return ValidationResult(
                is_valid=False,
                pattern_name='form_best_practices',
                current_pattern=form_name,
                recommended_pattern='; '.join(issues),
                severity='info',
                message=f'{form_name} can be improved'
            )
        
        return ValidationResult(
            is_valid=True,
            pattern_name='form_pattern',
            current_pattern=form_name,
            message=f'{form_name} follows Django form patterns'
        )
    
    def validate_url_pattern(self, url_code: str) -> ValidationResult:
        """
        Validate URL patterns use latest Django syntax
        
        Requirements: 1.2, 9.1
        
        Args:
            url_code: Source code of urls.py
            
        Returns:
            ValidationResult with validation details
        """
        # Check for old url() function
        if re.search(r'\burl\s*\(', url_code):
            return ValidationResult(
                is_valid=False,
                pattern_name='url_pattern',
                current_pattern='url()',
                recommended_pattern='Use path() or re_path() instead of url()',
                severity='warning',
                message='Old url() function detected, should use path() or re_path()'
            )
        
        # Check for proper include() usage
        if 'urlpatterns' in url_code and 'include(' not in url_code:
            # Check if this is a project-level urls.py
            if 'admin.site.urls' in url_code:
                return ValidationResult(
                    is_valid=False,
                    pattern_name='url_organization',
                    current_pattern='flat_urls',
                    recommended_pattern='Use include() for app-level URL namespacing',
                    severity='info',
                    message='Consider using include() for better URL organization'
                )
        
        return ValidationResult(
            is_valid=True,
            pattern_name='url_pattern',
            current_pattern='modern_urls',
            message='URL patterns follow Django 5.2.6 syntax'
        )
    
    def get_django_shortcuts(self) -> Dict[str, str]:
        """
        Get recommended Django shortcuts
        
        Requirements: 1.2, 5.4
        
        Returns:
            Dictionary mapping patterns to shortcuts
        """
        return {
            'try_get_except_404': 'get_object_or_404(Model, pk=pk)',
            'manual_redirect': 'redirect("view_name")',
            'manual_render': 'render(request, "template.html", context)',
            'manual_reverse': 'reverse("view_name")',
            'manual_reverse_lazy': 'reverse_lazy("view_name")',
        }
    
    def validate_query_optimization(self, view_code: str) -> List[str]:
        """
        Check for query optimization opportunities
        
        Requirements: 1.2, 5.5
        
        Args:
            view_code: Source code of the view
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Check for N+1 query patterns
        if '.all()' in view_code or '.filter(' in view_code:
            if 'select_related' not in view_code:
                recommendations.append('Consider using select_related() for foreign key relationships')
            
            if 'prefetch_related' not in view_code:
                recommendations.append('Consider using prefetch_related() for many-to-many relationships')
        
        # Check for only() and defer()
        if '.all()' in view_code and 'only(' not in view_code and 'defer(' not in view_code:
            recommendations.append('Consider using only() or defer() to limit fields fetched')
        
        # Check for count() vs len()
        if 'len(' in view_code and '.all()' in view_code:
            recommendations.append('Use .count() instead of len() for querysets')
        
        # Check for exists()
        if 'if ' in view_code and '.filter(' in view_code and '.exists()' not in view_code:
            recommendations.append('Use .exists() instead of checking queryset length')
        
        return recommendations
    
    def _get_mcp_client(self):
        """
        Get or initialize MCP client
        
        Returns:
            MCP client instance or None if not available
        """
        if not self.use_mcp:
            return None
        
        if self._mcp_client is None:
            try:
                self._mcp_client = MCPClient()
                logger.info("MCP client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MCP client: {e}")
                self.use_mcp = False
                return None
        
        return self._mcp_client
    
    def query_context7_docs(self, topic: str, max_tokens: int = 2000) -> Optional[str]:
        """
        Query Context7 MCP server for Django documentation
        
        Requirements: 1.2
        
        Args:
            topic: Topic to query (e.g., 'class-based views', 'forms', 'querysets')
            max_tokens: Maximum tokens to retrieve
            
        Returns:
            Documentation text or None if not available
        """
        # Check cache first
        cache_key = f"{topic}:{max_tokens}"
        if cache_key in self._doc_cache:
            logger.debug(f"Returning cached documentation for: {topic}")
            return self._doc_cache[cache_key]
        
        # Try MCP query
        client = self._get_mcp_client()
        if client:
            try:
                # Query Context7 for Django documentation
                docs = client.get_library_docs(
                    context7CompatibleLibraryID=self.library_id,
                    topic=topic,
                    tokens=max_tokens
                )
                
                if docs:
                    self._doc_cache[cache_key] = docs
                    logger.info(f"Retrieved documentation from Context7 for: {topic}")
                    return docs
            except Exception as e:
                logger.warning(f"Failed to query Context7 for {topic}: {e}")
        
        # Fallback to offline validation
        logger.debug(f"Using offline validation for: {topic}")
        return None
    
    def validate_against_docs(self, pattern: str, code: str) -> Optional[ValidationResult]:
        """
        Validate code pattern against Context7 documentation
        
        Requirements: 1.2, 1.3
        
        Args:
            pattern: Pattern type (e.g., 'cbv', 'form', 'queryset')
            code: Code to validate
            
        Returns:
            ValidationResult if documentation is available, None otherwise
        """
        docs = self.query_context7_docs(pattern)
        
        if not docs:
            return None
        
        # Analyze documentation for best practices
        # This is a simplified implementation - in production, you'd use
        # more sophisticated NLP or pattern matching
        
        recommendations = []
        
        # Check if code follows patterns mentioned in docs
        if 'select_related' in docs and 'select_related' not in code:
            recommendations.append('Documentation recommends using select_related()')
        
        if 'prefetch_related' in docs and 'prefetch_related' not in code:
            recommendations.append('Documentation recommends using prefetch_related()')
        
        if recommendations:
            return ValidationResult(
                is_valid=False,
                pattern_name=pattern,
                current_pattern='custom_implementation',
                recommended_pattern='; '.join(recommendations),
                severity='info',
                message=f'Code can be improved based on Django {self.django_version} documentation'
            )
        
        return ValidationResult(
            is_valid=True,
            pattern_name=pattern,
            current_pattern='follows_docs',
            message=f'Code follows Django {self.django_version} documentation'
        )
    
    def _is_class_based_view(self, code: str) -> bool:
        """Check if code contains a class-based view"""
        # Look for class definition with View inheritance
        view_patterns = [
            r'class\s+\w+\([^)]*View[^)]*\):',
            r'class\s+\w+\([^)]*ListView[^)]*\):',
            r'class\s+\w+\([^)]*DetailView[^)]*\):',
            r'class\s+\w+\([^)]*CreateView[^)]*\):',
            r'class\s+\w+\([^)]*UpdateView[^)]*\):',
            r'class\s+\w+\([^)]*DeleteView[^)]*\):',
        ]
        
        return any(re.search(pattern, code) for pattern in view_patterns)
    
    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """
        Generate a formatted validation report
        
        Requirements: 1.4
        
        Args:
            results: List of validation results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("DJANGO PATTERN VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Django Version: {self.django_version}")
        report.append(f"Library ID: {self.library_id}")
        report.append("")
        
        # Count by severity
        errors = [r for r in results if r.severity == 'error']
        warnings = [r for r in results if r.severity == 'warning']
        info = [r for r in results if r.severity == 'info']
        valid = [r for r in results if r.is_valid]
        
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Patterns Checked: {len(results)}")
        report.append(f"Valid Patterns: {len(valid)}")
        report.append(f"Errors: {len(errors)}")
        report.append(f"Warnings: {len(warnings)}")
        report.append(f"Info: {len(info)}")
        report.append("")
        
        # Report issues by severity
        if errors:
            report.append("ERRORS")
            report.append("-" * 80)
            for result in errors:
                report.append(f"✗ {result.pattern_name}: {result.message}")
                if result.recommended_pattern:
                    report.append(f"  Recommendation: {result.recommended_pattern}")
                report.append("")
        
        if warnings:
            report.append("WARNINGS")
            report.append("-" * 80)
            for result in warnings:
                report.append(f"⚠ {result.pattern_name}: {result.message}")
                if result.recommended_pattern:
                    report.append(f"  Recommendation: {result.recommended_pattern}")
                report.append("")
        
        if info:
            report.append("INFORMATION")
            report.append("-" * 80)
            for result in info:
                report.append(f"ℹ {result.pattern_name}: {result.message}")
                if result.recommended_pattern:
                    report.append(f"  Recommendation: {result.recommended_pattern}")
                report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


# Django 5.2.6 Best Practices Reference
DJANGO_BEST_PRACTICES = {
    'views': {
        'use_cbv': 'Always use class-based views instead of function-based views',
        'use_generic_views': 'Inherit from Django generic views (ListView, DetailView, etc.)',
        'use_mixins': 'Use mixins for cross-cutting concerns (LoginRequiredMixin, etc.)',
        'optimize_queries': 'Use select_related() and prefetch_related() to avoid N+1 queries',
        'use_pagination': 'Use paginate_by attribute instead of manual Paginator',
    },
    'forms': {
        'use_modelform': 'Use ModelForm for model-based forms',
        'define_fields': 'Always define fields or exclude in Meta class',
        'use_validators': 'Use Django validators instead of custom clean methods when possible',
        'customize_widgets': 'Customize widgets for better UX',
    },
    'urls': {
        'use_path': 'Use path() instead of url()',
        'use_include': 'Use include() for app-level URL namespacing',
        'name_urls': 'Always name your URL patterns for reverse resolution',
    },
    'queries': {
        'select_related': 'Use for foreign key and one-to-one relationships',
        'prefetch_related': 'Use for many-to-many and reverse foreign key relationships',
        'only_defer': 'Use only() or defer() to limit fields fetched',
        'use_count': 'Use .count() instead of len() for querysets',
        'use_exists': 'Use .exists() instead of checking queryset length',
    },
}
