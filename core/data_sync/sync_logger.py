"""
SyncLogger - Logging infrastructure for data sync operations
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class SyncLogger:
    """
    Manages logging for data sync operations
    """
    
    def __init__(self, log_dir: str = 'logs/data_sync'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f'sync_{timestamp}.log'
        self.error_file = self.log_dir / f'errors_{timestamp}.log'
        
        # Configure logging
        self.logger = logging.getLogger('data_sync')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler for all logs
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # File handler for errors only
        error_handler = logging.FileHandler(self.error_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logging initialized - Log file: {self.log_file}")
    
    def log_progress(self, message: str):
        """Log progress update"""
        self.logger.info(message)
    
    def log_error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def log_debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def get_log_file_path(self) -> str:
        """Get path to log file"""
        return str(self.log_file)
    
    def get_error_file_path(self) -> str:
        """Get path to error log file"""
        return str(self.error_file)
