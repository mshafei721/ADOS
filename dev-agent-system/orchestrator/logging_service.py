"""
Central Logging Service for ADOS System
Manages logging configuration and provides centralized logging capabilities
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from config.config_loader import ConfigLoader
from tools.logging.formatters import create_formatter


class LoggingService:
    """
    Central logging service for ADOS system
    Manages configuration, handlers, and formatters based on system_settings.json
    """
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """
        Initialize logging service
        
        Args:
            config_loader: Configuration loader instance
        """
        self.config_loader = config_loader or ConfigLoader()
        self.initialized = False
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self._system_settings = None
    
    def initialize(self) -> bool:
        """
        Initialize the logging service based on system settings
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load system settings
            self._system_settings = self.config_loader.load_system_settings()
            
            # Setup logging configuration
            self._setup_logging_config()
            
            # Create output directories
            self._create_output_directories()
            
            # Configure root logger
            self._configure_root_logger()
            
            # Create system loggers
            self._create_system_loggers()
            
            self.initialized = True
            self.get_logger("logging_service").info("Logging service initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize logging service: {e}")
            return False
    
    def _setup_logging_config(self):
        """Setup basic logging configuration"""
        logging_config = self._system_settings.get("logging", {})
        
        # Set global logging level
        log_level = getattr(logging, logging_config.get("level", "INFO").upper())
        logging.getLogger().setLevel(log_level)
        
        # Configure basic format for fallback
        self.log_format = logging_config.get("format", "json")
        self.rotate_size_mb = logging_config.get("rotate_size_mb", 10)
        self.max_files = logging_config.get("max_files", 5)
    
    def _create_output_directories(self):
        """Create necessary output directories"""
        output_config = self._system_settings.get("output", {})
        base_dir = Path(output_config.get("base_directory", "./output"))
        logs_dir = base_dir / output_config.get("structure", {}).get("logs", "logs")
        
        # Create logs directory
        logs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = logs_dir
    
    def _configure_root_logger(self):
        """Configure the root logger with appropriate handlers"""
        root_logger = logging.getLogger()
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create console handler
        console_handler = self._create_console_handler()
        root_logger.addHandler(console_handler)
        
        # Create file handler
        file_handler = self._create_file_handler("ados_system.log")
        root_logger.addHandler(file_handler)
        
        # Store handlers
        self.handlers["console"] = console_handler
        self.handlers["system_file"] = file_handler
    
    def _create_console_handler(self) -> logging.Handler:
        """Create console handler with appropriate formatting"""
        handler = logging.StreamHandler()
        
        if self.log_format == "json":
            formatter = create_formatter("json", extra_fields={"output": "console"})
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        return handler
    
    def _create_file_handler(self, filename: str) -> logging.Handler:
        """Create rotating file handler"""
        file_path = self.logs_dir / filename
        
        # Create rotating file handler
        handler = logging.handlers.RotatingFileHandler(
            filename=str(file_path),
            maxBytes=self.rotate_size_mb * 1024 * 1024,  # Convert MB to bytes
            backupCount=self.max_files - 1  # backupCount doesn't include current file
        )
        
        # Set formatter
        if self.log_format == "json":
            formatter = create_formatter("json", extra_fields={"output": "file"})
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        return handler
    
    def _create_system_loggers(self):
        """Create system-specific loggers"""
        system_loggers = [
            "ados_orchestrator",
            "ados_agent_factory",
            "ados_crew_factory",
            "ados_task_decomposer",
            "ados_memory_coordinator",
            "ados_performance_monitor",
            "logging_service"
        ]
        
        for logger_name in system_loggers:
            logger = self.get_logger(logger_name)
            # Logger inherits from root logger configuration
            # Additional configuration can be added here per logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get or create a logger with the specified name
        
        Args:
            name: Logger name
            
        Returns:
            Configured logger instance
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            
            # Configure logger if logging service is initialized
            if self.initialized:
                self._configure_logger(logger, name)
            
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def _configure_logger(self, logger: logging.Logger, name: str):
        """Configure a specific logger"""
        # Logger inherits from root logger by default
        # Additional per-logger configuration can be added here
        pass
    
    def create_crew_logger(self, crew_name: str, agent_name: Optional[str] = None) -> logging.Logger:
        """
        Create a crew-specific logger
        
        Args:
            crew_name: Name of the crew
            agent_name: Optional agent name
            
        Returns:
            Configured crew logger
        """
        if agent_name:
            logger_name = f"crew.{crew_name}.{agent_name}"
        else:
            logger_name = f"crew.{crew_name}"
        
        logger = self.get_logger(logger_name)
        
        # Add crew-specific file handler if not exists
        crew_handler_name = f"crew_{crew_name}"
        if crew_handler_name not in self.handlers:
            crew_file_handler = self._create_crew_file_handler(crew_name)
            logger.addHandler(crew_file_handler)
            self.handlers[crew_handler_name] = crew_file_handler
        
        return logger
    
    def _create_crew_file_handler(self, crew_name: str) -> logging.Handler:
        """Create crew-specific file handler"""
        filename = f"crew_{crew_name}.log"
        if not hasattr(self, 'logs_dir'):
            self._create_output_directories()
        file_path = self.logs_dir / filename
        
        handler = logging.handlers.RotatingFileHandler(
            filename=str(file_path),
            maxBytes=self.rotate_size_mb * 1024 * 1024,
            backupCount=self.max_files - 1
        )
        
        # Use crew-aware formatter
        formatter = create_formatter(
            "crew_aware",
            crew_name=crew_name,
            extra_fields={"output": "crew_file"}
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def create_performance_logger(self) -> logging.Logger:
        """
        Create performance-specific logger
        
        Returns:
            Configured performance logger
        """
        logger = self.get_logger("performance")
        
        # Add performance-specific file handler
        if "performance_file" not in self.handlers:
            perf_handler = self._create_performance_file_handler()
            logger.addHandler(perf_handler)
            self.handlers["performance_file"] = perf_handler
        
        return logger
    
    def _create_performance_file_handler(self) -> logging.Handler:
        """Create performance-specific file handler"""
        filename = "performance.log"
        if not hasattr(self, 'logs_dir'):
            self._create_output_directories()
        file_path = self.logs_dir / filename
        
        handler = logging.handlers.RotatingFileHandler(
            filename=str(file_path),
            maxBytes=self.rotate_size_mb * 1024 * 1024,
            backupCount=self.max_files - 1
        )
        
        # Use performance-aware formatter
        formatter = create_formatter(
            "performance",
            extra_fields={"output": "performance_file", "component": "performance"}
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def log_structured(self, logger_name: str, level: str, message: str, **kwargs):
        """
        Log a structured message
        
        Args:
            logger_name: Name of the logger
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            **kwargs: Additional structured data
        """
        logger = self.get_logger(logger_name)
        log_level = getattr(logging, level.upper())
        
        # Create structured data
        structured_data = {"message": message, **kwargs}
        
        # Log with structured data
        logger.log(log_level, message, extra={"structured_data": structured_data})
    
    def get_logging_status(self) -> Dict[str, Any]:
        """
        Get current logging status
        
        Returns:
            Dictionary with logging system status
        """
        return {
            "initialized": self.initialized,
            "log_format": self.log_format,
            "rotate_size_mb": self.rotate_size_mb,
            "max_files": self.max_files,
            "logs_directory": str(self.logs_dir) if hasattr(self, 'logs_dir') else None,
            "active_loggers": list(self.loggers.keys()),
            "active_handlers": list(self.handlers.keys()),
            "root_logger_level": logging.getLogger().level,
            "root_logger_handlers": len(logging.getLogger().handlers)
        }
    
    def shutdown(self):
        """Shutdown logging service and cleanup resources"""
        if not self.initialized:
            return
        
        # Close all handlers
        for handler in self.handlers.values():
            handler.close()
        
        # Clear handlers and loggers
        self.handlers.clear()
        self.loggers.clear()
        
        self.initialized = False
    
    def reload_configuration(self) -> bool:
        """
        Reload logging configuration
        
        Returns:
            True if reload successful, False otherwise
        """
        self.shutdown()
        return self.initialize()


# Global logging service instance
_logging_service: Optional[LoggingService] = None


def get_logging_service() -> LoggingService:
    """
    Get the global logging service instance
    
    Returns:
        LoggingService instance
    """
    global _logging_service
    if _logging_service is None:
        _logging_service = LoggingService()
    return _logging_service


def initialize_logging(config_loader: Optional[ConfigLoader] = None) -> bool:
    """
    Initialize the global logging service
    
    Args:
        config_loader: Configuration loader instance
        
    Returns:
        True if initialization successful, False otherwise
    """
    global _logging_service
    _logging_service = LoggingService(config_loader)
    return _logging_service.initialize()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger from the global logging service
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return get_logging_service().get_logger(name)