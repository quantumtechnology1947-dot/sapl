"""
Project Analysis Module

Scans Django project and detects patterns that need modernization.
Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field

from .utils import (
    ProjectInventory,
    FileInfo,
    is_protected_file,
    scan_django_project,
    count_lines_of_code
)
from .context7_validator import Context7Validator, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Detected pattern that needs modernization"""
    pattern_type: str  # 'fbv', 'custom_css', 'javascript', 'manual_pagination', etc.
    file_path: Path
    line_number: int
    code_snippet: str
    severity: str = 'info'  # 'info', 'warning', 'error'
    recommendation: str = ''
    
    def __str__(self):
        return f"{self.pattern_type} at {self.file_path}:{self.line_number}"


@dataclass
class AnalysisResult:
    """Result of project analysis"""
    inventory: ProjectInventory
    patterns: List[Pattern] = field(default_factory=list)
    validation_results: List[ValidationResult] = field(default_factory=list)
    
    @property
    def fbv_count(self) -> int:
        """Count of function-based views"""
        return len([p for p in self.patterns if p.pattern_type == 'fbv'])
    
    @property
    def custom_css_count(self) -> int:
        """Count of custom CSS occurrences"""
        return len([p for p in self.patterns if p.pattern_type == 'custom_css'])
    
    @property
    def javascript_count(self) -> int:
        """Count of JavaScript occurrences"""
        return len([p for p in self.patterns if p.pattern_type == 'javascript'])
    
    @property
    def total_patterns(self) -> int:
        """Total patterns detected"""
        return len(self.patterns)


class ProjectAnalyzer:
    """
    Analyzes Django project for modernization opportunities
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize analyzer
        
        Args:
            project_path: Path to Django project root
        """
        self.project_path = project_path
        self.validator = Context7Validator()
        logger.info(f"Initialized ProjectAnalyzer for {project_path}")
    
    def analyze(self, app_names: Optional[List[str]] = None) -> AnalysisResult:
        """
        Analyze entire project
        
        Requirements: 2.1, 2.5
        
        Args:
            app_names: Optional list of app names to analyze
            
        Returns:
            AnalysisResult with all findings
        """
        logger.info("Starting project analysis...")
        
        # Scan project structure
        inventory = scan_django_project(str(self.project_path))
        
        # Create result
        result = AnalysisResult(inventory=inventory)
        
        # Analyze Python files by type
        for file_info in inventory.files:
            if file_info.file_type == 'views':
                result.patterns.extend(self._analyze_views(file_info))
                result.validation_results.extend(self._validate_views(file_info))
            elif file_info.file_type == 'forms':
                result.patterns.extend(self._analyze_forms(file_info))
                result.validation_results.extend(self._validate_forms(file_info))
            elif file_info.file_type == 'urls':
                result.patterns.extend(self._analyze_urls(file_info))
                result.validation_results.extend(self._validate_urls(file_info))
        
        # Analyze templates
        logger.info("Scanning templates...")
        template_patterns = self._scan_templates()
        result.patterns.extend(template_patterns)
        logger.info(f"Found {len(template_patterns)} template patterns")
        
        # Analyze static files (CSS/JS)
        logger.info("Scanning static files...")
        static_patterns = self._scan_static_files()
        result.patterns.extend(static_patterns)
        logger.info(f"Found {len(static_patterns)} static file patterns")
        
        logger.info(f"Analysis complete: {result.total_patterns} patterns found")
        
        return result
    
    def _analyze_views(self, file_info: FileInfo) -> List[Pattern]:
        """
        Analyze views.py for patterns
        
        Requirements: 2.3, 3.1
        
        Args:
            file_info: FileInfo for views.py
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        try:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_info.path))
            
            # Detect function-based views
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if it's a view (has request parameter)
                    if node.args.args and node.args.args[0].arg == 'request':
                        # Check if it has @login_required or returns HttpResponse
                        is_view = False
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Name) and 'login_required' in decorator.id:
                                is_view = True
                        
                        # Check for render/HttpResponse in body
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                if isinstance(child.func, ast.Name):
                                    if child.func.id in ['render', 'HttpResponse', 'redirect']:
                                        is_view = True
                        
                        if is_view:
                            patterns.append(Pattern(
                                pattern_type='fbv',
                                file_path=file_info.path,
                                line_number=node.lineno,
                                code_snippet=f"def {node.name}(request):",
                                severity='warning',
                                recommendation='Convert to class-based view (ListView, DetailView, etc.)'
                            ))
            
            # Detect manual pagination
            if 'Paginator(' in content:
                for i, line in enumerate(lines, 1):
                    if 'Paginator(' in line:
                        patterns.append(Pattern(
                            pattern_type='manual_pagination',
                            file_path=file_info.path,
                            line_number=i,
                            code_snippet=line.strip(),
                            severity='info',
                            recommendation='Use paginate_by attribute in ListView'
                        ))
            
            # Detect manual form handling
            if 'if request.method == ' in content:
                for i, line in enumerate(lines, 1):
                    if 'if request.method ==' in line:
                        patterns.append(Pattern(
                            pattern_type='manual_form_handling',
                            file_path=file_info.path,
                            line_number=i,
                            code_snippet=line.strip(),
                            severity='info',
                            recommendation='Use CreateView or UpdateView for form handling'
                        ))
            
            # Detect missing query optimization
            if '.all()' in content or '.filter(' in content:
                if 'select_related' not in content and 'prefetch_related' not in content:
                    patterns.append(Pattern(
                        pattern_type='missing_query_optimization',
                        file_path=file_info.path,
                        line_number=1,
                        code_snippet='Queries without optimization',
                        severity='info',
                        recommendation='Add select_related() or prefetch_related() to optimize queries'
                    ))
        
        except Exception as e:
            logger.error(f"Error analyzing views {file_info.path}: {e}")
        
        return patterns
    
    def _analyze_forms(self, file_info: FileInfo) -> List[Pattern]:
        """
        Analyze forms.py for patterns
        
        Requirements: 2.3
        
        Args:
            file_info: FileInfo for forms.py
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        try:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detect forms without Meta class
            if 'ModelForm' in content and 'class Meta:' not in content:
                patterns.append(Pattern(
                    pattern_type='form_without_meta',
                    file_path=file_info.path,
                    line_number=1,
                    code_snippet='ModelForm without Meta',
                    severity='warning',
                    recommendation='Add Meta class with model and fields'
                ))
            
            # Detect manual validation that could use validators
            if 'def clean_' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'def clean_' in line:
                        patterns.append(Pattern(
                            pattern_type='manual_validation',
                            file_path=file_info.path,
                            line_number=i,
                            code_snippet=line.strip(),
                            severity='info',
                            recommendation='Consider using Django validators'
                        ))
        
        except Exception as e:
            logger.error(f"Error analyzing forms {file_info.path}: {e}")
        
        return patterns
    
    def _analyze_urls(self, file_info: FileInfo) -> List[Pattern]:
        """
        Analyze urls.py for patterns
        
        Requirements: 2.3, 9.1
        
        Args:
            file_info: FileInfo for urls.py
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        try:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Detect old url() patterns
            for i, line in enumerate(lines, 1):
                if re.search(r'\burl\s*\(', line):
                    patterns.append(Pattern(
                        pattern_type='old_url_pattern',
                        file_path=file_info.path,
                        line_number=i,
                        code_snippet=line.strip(),
                        severity='warning',
                        recommendation='Use path() or re_path() instead of url()'
                    ))
        
        except Exception as e:
            logger.error(f"Error analyzing urls {file_info.path}: {e}")
        
        return patterns
    
    def _analyze_template(self, file_info: FileInfo) -> List[Pattern]:
        """
        Analyze template for custom CSS and JavaScript
        
        Requirements: 2.4, 10.1, 10.2, 12.1, 12.2
        
        Args:
            file_info: FileInfo for template
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        try:
            # Try UTF-8 first, then fall back to other encodings
            try:
                with open(file_info.path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with latin-1 as fallback
                with open(file_info.path, 'r', encoding='latin-1') as f:
                    content = f.read()
                logger.warning(f"Used latin-1 encoding for {file_info.path}")
            
            lines = content.split('\n')
            
            # Detect inline styles
            for i, line in enumerate(lines, 1):
                if 'style=' in line:
                    patterns.append(Pattern(
                        pattern_type='inline_style',
                        file_path=file_info.path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        severity='info',
                        recommendation='Replace with Tailwind CSS utility classes'
                    ))
            
            # Detect <style> tags
            if '<style' in content:
                for i, line in enumerate(lines, 1):
                    if '<style' in line:
                        patterns.append(Pattern(
                            pattern_type='style_tag',
                            file_path=file_info.path,
                            line_number=i,
                            code_snippet='<style> tag found',
                            severity='warning',
                            recommendation='Remove <style> tags and use Tailwind CSS'
                        ))
            
            # Detect <script> tags (excluding CDN)
            for i, line in enumerate(lines, 1):
                if '<script' in line and 'src=' in line:
                    # Check if it's not a CDN (Tailwind, HTMX, etc.)
                    if not any(cdn in line for cdn in ['cdn.tailwindcss.com', 'unpkg.com/htmx', 'cdn.jsdelivr.net']):
                        patterns.append(Pattern(
                            pattern_type='custom_script',
                            file_path=file_info.path,
                            line_number=i,
                            code_snippet=line.strip()[:80],
                            severity='warning',
                            recommendation='Remove custom JavaScript and use HTMX'
                        ))
                elif '<script>' in line or '<script ' in line:
                    patterns.append(Pattern(
                        pattern_type='inline_script',
                        file_path=file_info.path,
                        line_number=i,
                        code_snippet='Inline JavaScript found',
                        severity='warning',
                        recommendation='Replace with HTMX attributes'
                    ))
            
            # Detect JavaScript event handlers
            js_events = ['onclick=', 'onchange=', 'onsubmit=', 'onload=', 'oninput=']
            for i, line in enumerate(lines, 1):
                for event in js_events:
                    if event in line:
                        patterns.append(Pattern(
                            pattern_type='js_event_handler',
                            file_path=file_info.path,
                            line_number=i,
                            code_snippet=line.strip()[:80],
                            severity='info',
                            recommendation=f'Replace {event} with HTMX attributes (hx-get, hx-post, etc.)'
                        ))
                        break
            
            # Check for Tailwind CDN
            if 'cdn.tailwindcss.com' not in content and 'tailwind' not in content.lower():
                patterns.append(Pattern(
                    pattern_type='missing_tailwind',
                    file_path=file_info.path,
                    line_number=1,
                    code_snippet='Tailwind CSS not detected',
                    severity='info',
                    recommendation='Add Tailwind CSS CDN to base template'
                ))
            
            # Check for HTMX
            if 'unpkg.com/htmx' not in content and 'hx-' not in content:
                patterns.append(Pattern(
                    pattern_type='missing_htmx',
                    file_path=file_info.path,
                    line_number=1,
                    code_snippet='HTMX not detected',
                    severity='info',
                    recommendation='Add HTMX CDN to base template'
                ))
        
        except Exception as e:
            logger.error(f"Error analyzing template {file_info.path}: {e}")
        
        return patterns
    
    def _analyze_css(self, file_info: FileInfo) -> List[Pattern]:
        """
        Analyze CSS file
        
        Requirements: 11.1, 11.2
        
        Args:
            file_info: FileInfo for CSS file
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        patterns.append(Pattern(
            pattern_type='custom_css_file',
            file_path=file_info.path,
            line_number=1,
            code_snippet=f'Custom CSS file: {file_info.path.name}',
            severity='warning',
            recommendation='Convert CSS rules to Tailwind utility classes and remove file'
        ))
        
        return patterns
    
    def _analyze_javascript(self, file_info: FileInfo) -> List[Pattern]:
        """
        Analyze JavaScript file
        
        Requirements: 12.1, 12.2
        
        Args:
            file_info: FileInfo for JavaScript file
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        patterns.append(Pattern(
            pattern_type='custom_js_file',
            file_path=file_info.path,
            line_number=1,
            code_snippet=f'Custom JavaScript file: {file_info.path.name}',
            severity='warning',
            recommendation='Convert JavaScript to HTMX attributes and remove file'
        ))
        
        return patterns
    
    def _validate_views(self, file_info: FileInfo) -> List[ValidationResult]:
        """Validate views using Context7"""
        results = []
        
        try:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to find view classes
            tree = ast.parse(content, filename=str(file_info.path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a view class
                    if any('View' in base.id if isinstance(base, ast.Name) else False 
                          for base in node.bases):
                        # Get class source
                        class_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                        class_source = '\n'.join(class_lines)
                        
                        result = self.validator.validate_cbv_pattern(class_source, node.name)
                        results.append(result)
        
        except Exception as e:
            logger.error(f"Error validating views {file_info.path}: {e}")
        
        return results
    
    def _validate_forms(self, file_info: FileInfo) -> List[ValidationResult]:
        """Validate forms using Context7"""
        results = []
        
        try:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to find form classes
            tree = ast.parse(content, filename=str(file_info.path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a form class
                    if any('Form' in base.id if isinstance(base, ast.Name) else False 
                          for base in node.bases):
                        # Get class source
                        class_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                        class_source = '\n'.join(class_lines)
                        
                        result = self.validator.validate_form_pattern(class_source, node.name)
                        results.append(result)
        
        except Exception as e:
            logger.error(f"Error validating forms {file_info.path}: {e}")
        
        return results
    
    def _validate_urls(self, file_info: FileInfo) -> List[ValidationResult]:
        """Validate URLs using Context7"""
        results = []
        
        try:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = self.validator.validate_url_pattern(content)
            results.append(result)
        
        except Exception as e:
            logger.error(f"Error validating URLs {file_info.path}: {e}")
        
        return results
    
    def _scan_templates(self) -> List[Pattern]:
        """
        Scan all template files in the project.
        
        Returns:
            List of patterns found in templates
        """
        patterns = []
        
        # Find all template directories
        template_dirs = []
        for app_dir in self.project_path.iterdir():
            if app_dir.is_dir() and not app_dir.name.startswith('.'):
                templates_dir = app_dir / 'templates'
                if templates_dir.exists():
                    template_dirs.append(templates_dir)
        
        # Also check for project-level templates
        project_templates = self.project_path / 'templates'
        if project_templates.exists():
            template_dirs.append(project_templates)
        
        # Scan each template directory
        for template_dir in template_dirs:
            for template_file in template_dir.rglob('*.html'):
                if not is_protected_file(template_file):
                    file_info = FileInfo(
                        path=template_file,
                        relative_path=str(template_file.relative_to(self.project_path)),
                        app_name=template_file.parts[-3] if len(template_file.parts) >= 3 else 'unknown',
                        file_type='template',
                        lines_of_code=count_lines_of_code(template_file)
                    )
                    patterns.extend(self._analyze_template(file_info))
        
        return patterns
    
    def _scan_static_files(self) -> List[Pattern]:
        """
        Scan all static CSS and JavaScript files.
        
        Returns:
            List of patterns found in static files
        """
        patterns = []
        
        # Find all static directories
        static_dirs = []
        for app_dir in self.project_path.iterdir():
            if app_dir.is_dir() and not app_dir.name.startswith('.'):
                static_dir = app_dir / 'static'
                if static_dir.exists():
                    static_dirs.append(static_dir)
        
        # Also check for project-level static
        project_static = self.project_path / 'static'
        if project_static.exists():
            static_dirs.append(project_static)
        
        # Scan each static directory
        for static_dir in static_dirs:
            # Scan CSS files
            for css_file in static_dir.rglob('*.css'):
                if not is_protected_file(css_file):
                    file_info = FileInfo(
                        path=css_file,
                        relative_path=str(css_file.relative_to(self.project_path)),
                        app_name=css_file.parts[-3] if len(css_file.parts) >= 3 else 'unknown',
                        file_type='css',
                        lines_of_code=count_lines_of_code(css_file)
                    )
                    patterns.extend(self._analyze_css(file_info))
            
            # Scan JavaScript files
            for js_file in static_dir.rglob('*.js'):
                if not is_protected_file(js_file):
                    file_info = FileInfo(
                        path=js_file,
                        relative_path=str(js_file.relative_to(self.project_path)),
                        app_name=js_file.parts[-3] if len(js_file.parts) >= 3 else 'unknown',
                        file_type='javascript',
                        lines_of_code=count_lines_of_code(js_file)
                    )
                    patterns.extend(self._analyze_javascript(file_info))
        
        return patterns
    
    def generate_analysis_report(self, result: AnalysisResult) -> str:
        """
        Generate comprehensive analysis report
        
        Requirements: 2.5
        
        Args:
            result: AnalysisResult from analysis
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("DJANGO PROJECT MODERNIZATION ANALYSIS")
        report.append("=" * 80)
        report.append(f"Project: {self.project_path}")
        report.append(f"Apps Analyzed: {len(result.inventory.apps)}")
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Files: {result.inventory.total_files}")
        report.append(f"Total Lines of Code: {result.inventory.total_lines:,}")
        report.append(f"Protected Files: {len(result.inventory.protected_files)}")
        report.append(f"Patterns Detected: {result.total_patterns}")
        report.append(f"  - Function-Based Views: {result.fbv_count}")
        report.append(f"  - Custom CSS: {result.custom_css_count}")
        report.append(f"  - JavaScript: {result.javascript_count}")
        report.append("")
        
        # Patterns by type
        pattern_types: Dict[str, List[Pattern]] = {}
        for pattern in result.patterns:
            if pattern.pattern_type not in pattern_types:
                pattern_types[pattern.pattern_type] = []
            pattern_types[pattern.pattern_type].append(pattern)
        
        report.append("PATTERNS BY TYPE")
        report.append("-" * 80)
        for pattern_type, patterns in sorted(pattern_types.items()):
            report.append(f"\n{pattern_type.upper().replace('_', ' ')} ({len(patterns)})")
            for pattern in patterns[:5]:  # Show first 5
                report.append(f"  {pattern.file_path.name}:{pattern.line_number} - {pattern.recommendation}")
            if len(patterns) > 5:
                report.append(f"  ... and {len(patterns) - 5} more")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
