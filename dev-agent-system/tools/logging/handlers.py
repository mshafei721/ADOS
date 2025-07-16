"""
Custom Log Handlers for ADOS System
Provides advanced log rotation and file management capabilities
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
import gzip
import shutil
from datetime import datetime


class ADOSRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Enhanced rotating file handler with additional features
    - Better file permission handling
    - Compression of old log files
    - Enhanced error handling
    """
    
    def __init__(self, 
                 filename: str,
                 mode: str = 'a',
                 maxBytes: int = 0,
                 backupCount: int = 0,
                 encoding: Optional[str] = None,
                 delay: bool = False,
                 compress_old_logs: bool = True,
                 file_permissions: int = 0o644):
        """
        Initialize enhanced rotating file handler
        
        Args:
            filename: Path to log file
            mode: File open mode
            maxBytes: Maximum bytes per file
            backupCount: Number of backup files to keep
            encoding: File encoding
            delay: Delay file opening
            compress_old_logs: Whether to compress rotated logs
            file_permissions: File permissions for created files
        """
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.compress_old_logs = compress_old_logs
        self.file_permissions = file_permissions
        
        # Ensure directory exists
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _open(self):
        """Open file with proper permissions"""
        stream = super()._open()
        
        # Set file permissions
        try:
            os.chmod(self.baseFilename, self.file_permissions)
        except OSError:
            # Ignore permission errors on some systems
            pass
        
        return stream
    
    def doRollover(self):
        """
        Perform rollover with compression if enabled
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Rotate files
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = f"{self.baseFilename}.{i}"
                dfn = f"{self.baseFilename}.{i + 1}"
                
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            
            # Move current file to .1
            dfn = f"{self.baseFilename}.1"
            if os.path.exists(dfn):
                os.remove(dfn)
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
                
                # Compress the rotated file if enabled
                if self.compress_old_logs:
                    self._compress_file(dfn)
        
        # Create new file
        if not self.delay:
            self.stream = self._open()
    
    def _compress_file(self, filename: str):
        """
        Compress a log file using gzip
        
        Args:
            filename: Path to file to compress
        """
        try:
            compressed_filename = f"{filename}.gz"
            
            with open(filename, 'rb') as f_in:
                with gzip.open(compressed_filename, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file
            os.remove(filename)
            
            # Set permissions on compressed file
            os.chmod(compressed_filename, self.file_permissions)
            
        except Exception as e:
            # Log compression failure but don't interrupt logging
            print(f"Failed to compress log file {filename}: {e}")


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Enhanced timed rotating file handler with compression
    """
    
    def __init__(self, 
                 filename: str,
                 when: str = 'h',
                 interval: int = 1,
                 backupCount: int = 0,
                 encoding: Optional[str] = None,
                 delay: bool = False,
                 utc: bool = False,
                 atTime: Optional[datetime] = None,
                 compress_old_logs: bool = True,
                 file_permissions: int = 0o644):
        """
        Initialize enhanced timed rotating file handler
        """
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        self.compress_old_logs = compress_old_logs
        self.file_permissions = file_permissions
        
        # Ensure directory exists
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _open(self):
        """Open file with proper permissions"""
        stream = super()._open()
        
        # Set file permissions
        try:
            os.chmod(self.baseFilename, self.file_permissions)
        except OSError:
            pass
        
        return stream
    
    def doRollover(self):
        """Perform rollover with compression"""
        super().doRollover()
        
        # Compress the rotated file if enabled
        if self.compress_old_logs and self.backupCount > 0:
            # Find the most recent backup file
            backup_files = []
            dir_name = os.path.dirname(self.baseFilename)
            base_name = os.path.basename(self.baseFilename)
            
            for file_name in os.listdir(dir_name):
                if file_name.startswith(base_name) and file_name != base_name:
                    if not file_name.endswith('.gz'):
                        backup_files.append(os.path.join(dir_name, file_name))
            
            # Compress the most recent backup
            if backup_files:
                backup_files.sort(key=os.path.getmtime, reverse=True)
                self._compress_file(backup_files[0])
    
    def _compress_file(self, filename: str):
        """Compress a log file using gzip"""
        try:
            compressed_filename = f"{filename}.gz"
            
            with open(filename, 'rb') as f_in:
                with gzip.open(compressed_filename, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            os.remove(filename)
            os.chmod(compressed_filename, self.file_permissions)
            
        except Exception as e:
            print(f"Failed to compress log file {filename}: {e}")


class StructuredFileHandler(logging.Handler):
    """
    File handler that writes structured logs to separate files
    Useful for creating separate files for different log types
    """
    
    def __init__(self, 
                 base_directory: str,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 compress_old_logs: bool = True):
        """
        Initialize structured file handler
        
        Args:
            base_directory: Base directory for log files
            max_file_size: Maximum file size in bytes
            backup_count: Number of backup files to keep
            compress_old_logs: Whether to compress old logs
        """
        super().__init__()
        self.base_directory = Path(base_directory)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.compress_old_logs = compress_old_logs
        
        # Ensure directory exists
        self.base_directory.mkdir(parents=True, exist_ok=True)
        
        # Track file handlers for different log types
        self.handlers: Dict[str, ADOSRotatingFileHandler] = {}
    
    def emit(self, record: logging.LogRecord):
        """
        Emit log record to appropriate file based on log type
        
        Args:
            record: LogRecord to emit
        """
        try:
            # Determine log type from record
            log_type = getattr(record, 'log_type', 'general')
            
            # Get or create handler for this log type
            handler = self._get_handler(log_type)
            
            # Emit record
            handler.emit(record)
            
        except Exception:
            self.handleError(record)
    
    def _get_handler(self, log_type: str) -> ADOSRotatingFileHandler:
        """
        Get or create handler for specific log type
        
        Args:
            log_type: Type of log (e.g., 'error', 'performance', 'audit')
            
        Returns:
            Handler for the log type
        """
        if log_type not in self.handlers:
            # Create new handler
            filename = self.base_directory / f"{log_type}.log"
            
            handler = ADOSRotatingFileHandler(
                filename=str(filename),
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                compress_old_logs=self.compress_old_logs
            )
            
            # Set same formatter as parent
            if self.formatter:
                handler.setFormatter(self.formatter)
            
            self.handlers[log_type] = handler
        
        return self.handlers[log_type]
    
    def close(self):
        """Close all file handlers"""
        for handler in self.handlers.values():
            handler.close()
        self.handlers.clear()
        super().close()


class PerformanceLogHandler(logging.Handler):
    """
    Specialized handler for performance logs
    Separates performance metrics from regular logs
    """
    
    def __init__(self, 
                 performance_log_file: str,
                 max_file_size: int = 10 * 1024 * 1024,
                 backup_count: int = 5):
        """
        Initialize performance log handler
        
        Args:
            performance_log_file: Path to performance log file
            max_file_size: Maximum file size in bytes
            backup_count: Number of backup files to keep
        """
        super().__init__()
        
        self.file_handler = ADOSRotatingFileHandler(
            filename=performance_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            compress_old_logs=True
        )
    
    def emit(self, record: logging.LogRecord):
        """
        Emit performance log record
        
        Args:
            record: LogRecord to emit
        """
        # Only emit if record has performance metrics
        if hasattr(record, 'performance_metrics'):
            try:
                self.file_handler.emit(record)
            except Exception:
                self.handleError(record)
    
    def setFormatter(self, formatter: logging.Formatter):
        """Set formatter for the file handler"""
        super().setFormatter(formatter)
        self.file_handler.setFormatter(formatter)
    
    def close(self):
        """Close the file handler"""
        self.file_handler.close()
        super().close()


def create_handler(handler_type: str, **kwargs) -> logging.Handler:
    """
    Factory function to create appropriate handler
    
    Args:
        handler_type: Type of handler to create
        **kwargs: Additional arguments for handler
        
    Returns:
        Configured handler instance
    """
    handlers = {
        'rotating_file': ADOSRotatingFileHandler,
        'timed_rotating': TimedRotatingFileHandler,
        'structured_file': StructuredFileHandler,
        'performance': PerformanceLogHandler
    }
    
    handler_class = handlers.get(handler_type)
    if not handler_class:
        raise ValueError(f"Unknown handler type: {handler_type}")
    
    return handler_class(**kwargs)


def setup_log_rotation(log_directory: str, 
                      max_size_mb: int = 10,
                      max_files: int = 5,
                      compress_old_logs: bool = True) -> Dict[str, Any]:
    """
    Setup log rotation configuration
    
    Args:
        log_directory: Directory for log files
        max_size_mb: Maximum size per log file in MB
        max_files: Maximum number of log files to keep
        compress_old_logs: Whether to compress old logs
        
    Returns:
        Configuration dictionary
    """
    return {
        'log_directory': Path(log_directory),
        'max_bytes': max_size_mb * 1024 * 1024,
        'backup_count': max_files - 1,
        'compress_old_logs': compress_old_logs
    }