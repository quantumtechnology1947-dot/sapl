"""
Modernization Utilities
File scanning, validation, and helper functions for Django code modernization.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
import ast


logger = logging.getLogger(__name__)


# ============================================================================
# PROTECTED FILES CONFIGURATION
# ============================================================================

PROTECTED_FILES = {
    'models.py',  # Never modify models.py files
}

PROTECTED_PATTERNS = {
    'migrations',  # Never modify migration files
    '__pycache__',  # Skip cache directories
    '.pyc',  # Skip compiled Python files
    'venv',  # Skip virtual environment
    'env',  # Skip virtual environment
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class FileInfo:
    """Information about a Python file."""
    path: Path
    relative_path: str
    app_name: str
    file_type: str  # 'views', 'forms', 'urls', 'admin', 'services', 'models'
    lines_of_code: int = 0
    is_protected: bool = False
    
    def __str__(self):
        return f"{self.relative_path} ({self.lines_of_code} lines)"


@dataclass
class ProjectInventory:
    """Complete inventory of Django project files."""
    project_root: Path
    apps: List[str] = field(default_factory=list)
    files: List[FileInfo] = field(default_factory=list)
    protected_files: List[FileInfo] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    
    def get_files_by_type(self, file_type: str) -> List[FileInfo]:
        """Get all files of a specific type."""
        return [f for f in self.files if f.file_type == file_type]
    
    def get_files_by_app(self, app_name: str) -> List[FileInfo]:
        """Get all files for a specific app."""
        return [f for f in self.files if f.app_name == app_name]


# ============================================================================
# FILE VALIDATION
# ============================================================================

def is_protected_file(file_path: Path) -> bool:
    """
    Check if a file is protected and should not be modified.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is protected, False otherwise
        
    Requirements: 6.1, 6.2
    """
    # Check if filename is in protected list
    if file_path.name in PROTECTED_FILES:
        logger.info(f"Protected file detected: {file_path}")
        return True
    
    # Check if path contains protected patterns
    path_str = str(file_path).replace('\\', '/')  # Normalize path separators
    for pattern in PROTECTED_PATTERNS:
        if f'/{pattern}/' in path_str or path_str.startswith(f'{pattern}/'):
            logger.debug(f"Protected pattern '{pattern}' found in: {file_path}")
            return True
    
    return False


def validate_file_not_protected(file_path: Path) -> None:
    """
    Validate that a file is not protected before modification.
    
    Args:
        file_path: Path to the file
        
    Raises:
        ProtectedFileError: If file is protected
        
    Requirements: 6.1, 6.2, 6.3
    """
    if is_protected_file(file_path):
        raise ProtectedFileError(
            f"Cannot modify protected file: {file_path}\n"
            f"Protected files: {', '.join(PROTECTED_FILES)}"
        )


class ProtectedFileError(Exception):
    """Raised when attempting to modify a protected file."""
    pass


# ============================================================================
# FILE SCANNING
# ============================================================================

def scan_django_project(project_root: str) -> ProjectInventory:
    """
    Scan Django project and create inventory of all files.
    
    Args:
        project_root: Path to Django project root
        
    Returns:
        ProjectInventory with all discovered files
        
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    project_path = Path(project_root).resolve()
    
    if not project_path.exists():
        raise ValueError(f"Project root does not exist: {project_root}")
    
    logger.info(f"Scanning Django project: {project_path}")
    
    inventory = ProjectInventory(project_root=project_path)
    
    # Find all Django apps
    apps = find_django_apps(project_path)
    inventory.apps = apps
    
    logger.info(f"Found {len(apps)} Django apps: {', '.join(apps)}")
    
    # Scan each app
    for app_name in apps:
        app_path = project_path / app_name
        app_files = scan_django_app(app_path, app_name)
        
        for file_info in app_files:
            if file_info.is_protected:
                inventory.protected_files.append(file_info)
            else:
                inventory.files.append(file_info)
            
            inventory.total_files += 1
            inventory.total_lines += file_info.lines_of_code
    
    logger.info(
        f"Scan complete: {inventory.total_files} files, "
        f"{inventory.total_lines} lines, "
        f"{len(inventory.protected_files)} protected"
    )
    
    return inventory


def find_django_apps(project_root: Path) -> List[str]:
    """
    Find all Django apps in the project.
    
    Args:
        project_root: Path to project root
        
    Returns:
        List of app names
    """
    apps = []
    
    # Look for directories with apps.py or models.py
    for item in project_root.iterdir():
        if not item.is_dir():
            continue
        
        # Skip common non-app directories
        if item.name.startswith('.') or item.name.startswith('_'):
            continue
        
        if item.name in ['venv', 'env', 'static', 'media', 'templates', 'staticfiles']:
            continue
        
        # Check if it's a Django app
        if (item / 'apps.py').exists() or (item / 'models.py').exists():
            apps.append(item.name)
    
    return sorted(apps)


def scan_django_app(app_path: Path, app_name: str) -> List[FileInfo]:
    """
    Scan a Django app directory for Python files.
    
    Args:
        app_path: Path to app directory
        app_name: Name of the app
        
    Returns:
        List of FileInfo objects
        
    Requirements: 2.1, 2.2, 2.3
    """
    files = []
    
    # Target files to scan
    target_files = {
        'views.py': 'views',
        'forms.py': 'forms',
        'urls.py': 'urls',
        'admin.py': 'admin',
        'services.py': 'services',
        'models.py': 'models',
    }
    
    for filename, file_type in target_files.items():
        file_path = app_path / filename
        
        if not file_path.exists():
            continue
        
        # Check if protected
        is_protected = is_protected_file(file_path)
        
        # Count lines of code
        lines = count_lines_of_code(file_path)
        
        file_info = FileInfo(
            path=file_path,
            relative_path=f"{app_name}/{filename}",
            app_name=app_name,
            file_type=file_type,
            lines_of_code=lines,
            is_protected=is_protected
        )
        
        files.append(file_info)
        
        if is_protected:
            logger.info(f"Protected: {file_info.relative_path}")
        else:
            logger.debug(f"Scanned: {file_info.relative_path} ({lines} lines)")
    
    return files


def count_lines_of_code(file_path: Path) -> int:
    """
    Count lines of code in a Python file (excluding blank lines and comments).
    
    Args:
        file_path: Path to Python file
        
    Returns:
        Number of lines of code
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Count non-blank, non-comment lines
        code_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                code_lines += 1
        
        return code_lines
    
    except Exception as e:
        logger.warning(f"Error counting lines in {file_path}: {e}")
        return 0


# ============================================================================
# SYNTAX VALIDATION
# ============================================================================

def validate_python_syntax(code: str, file_path: Optional[Path] = None) -> bool:
    """
    Validate Python syntax.
    
    Args:
        code: Python code as string
        file_path: Optional file path for error messages
        
    Returns:
        True if syntax is valid, False otherwise
        
    Requirements: 7.1, 7.2
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        file_str = f" in {file_path}" if file_path else ""
        logger.error(f"Syntax error{file_str}: {e}")
        return False


def validate_file_syntax(file_path: Path) -> bool:
    """
    Validate syntax of a Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        True if syntax is valid, False otherwise
        
    Requirements: 7.1, 7.2
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        return validate_python_syntax(code, file_path)
    
    except Exception as e:
        logger.error(f"Error validating {file_path}: {e}")
        return False


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def read_file(file_path: Path) -> str:
    """
    Read file contents safely.
    
    Args:
        file_path: Path to file
        
    Returns:
        File contents as string
        
    Raises:
        ProtectedFileError: If attempting to read protected file for modification
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        raise


def write_file(file_path: Path, content: str, validate: bool = True) -> None:
    """
    Write content to file with protection checks.
    
    Args:
        file_path: Path to file
        content: Content to write
        validate: Whether to validate syntax before writing
        
    Raises:
        ProtectedFileError: If file is protected
        SyntaxError: If validation fails
        
    Requirements: 6.1, 6.2, 6.3, 7.1, 7.2
    """
    # Check if file is protected
    validate_file_not_protected(file_path)
    
    # Validate syntax if requested
    if validate and file_path.suffix == '.py':
        if not validate_python_syntax(content, file_path):
            raise SyntaxError(f"Invalid Python syntax in {file_path}")
    
    # Write file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Written: {file_path}")
    
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")
        raise


def backup_file(file_path: Path) -> Path:
    """
    Create a backup of a file before modification.
    
    Args:
        file_path: Path to file
        
    Returns:
        Path to backup file
    """
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.with_suffix(f'.{timestamp}.bak')
    
    shutil.copy2(file_path, backup_path)
    logger.info(f"Backup created: {backup_path}")
    
    return backup_path


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO) -> None:
    """
    Set up logging for modernization process.
    
    Args:
        log_file: Optional log file path
        level: Logging level
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")


def log_operation(operation: str, file_path: Path, success: bool = True) -> None:
    """
    Log a modernization operation.
    
    Args:
        operation: Operation name (e.g., 'convert_view', 'update_template')
        file_path: Path to file being operated on
        success: Whether operation succeeded
    """
    status = "✓" if success else "✗"
    level = logging.INFO if success else logging.ERROR
    logger.log(level, f"{status} {operation}: {file_path}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_django_apps_from_settings(project_root: Path) -> List[str]:
    """
    Extract Django apps from settings.py INSTALLED_APPS.
    
    Args:
        project_root: Path to project root
        
    Returns:
        List of app names
    """
    # Try to find settings.py
    settings_paths = list(project_root.glob('*/settings.py'))
    
    if not settings_paths:
        logger.warning("Could not find settings.py")
        return []
    
    settings_path = settings_paths[0]
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse INSTALLED_APPS
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'INSTALLED_APPS':
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            apps = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    app_name = elt.value
                                    # Extract local apps (not django.* or third-party)
                                    if not app_name.startswith('django.') and '.' not in app_name:
                                        apps.append(app_name)
                            return apps
        
        return []
    
    except Exception as e:
        logger.warning(f"Error parsing settings.py: {e}")
        return []


def calculate_code_reduction(before_lines: int, after_lines: int) -> float:
    """
    Calculate code reduction percentage.
    
    Args:
        before_lines: Lines of code before modernization
        after_lines: Lines of code after modernization
        
    Returns:
        Reduction percentage
    """
    if before_lines == 0:
        return 0.0
    
    reduction = ((before_lines - after_lines) / before_lines) * 100
    return round(reduction, 2)
