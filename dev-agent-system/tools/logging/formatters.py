"""
JSON Logging Formatters for ADOS System
Provides structured logging capabilities as specified in system_settings.json
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    Converts log records to JSON format with standardized fields
    """
    
    def __init__(self, 
                 extra_fields: Optional[Dict[str, Any]] = None,
                 timestamp_format: str = "%Y-%m-%d %H:%M:%S.%f"):
        """
        Initialize JSON formatter
        
        Args:
            extra_fields: Additional fields to include in all log entries
            timestamp_format: Format string for timestamps
        """
        super().__init__()
        self.extra_fields = extra_fields or {}
        self.timestamp_format = timestamp_format
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string
        
        Args:
            record: LogRecord to format
            
        Returns:
            JSON formatted log entry
        """
        # Base log entry structure
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).strftime(self.timestamp_format),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
            "thread_name": record.threadName
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in log_entry and not key.startswith('_'):
                # Skip standard LogRecord attributes
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                              'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process', 'message']:
                    log_entry[key] = value
        
        # Add configured extra fields
        log_entry.update(self.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class CrewAwareJSONFormatter(JSONFormatter):
    """
    JSON formatter with crew context awareness
    Automatically adds crew and agent context to log entries
    """
    
    def __init__(self, 
                 crew_name: Optional[str] = None,
                 agent_name: Optional[str] = None,
                 **kwargs):
        """
        Initialize crew-aware JSON formatter
        
        Args:
            crew_name: Name of the crew generating logs
            agent_name: Name of the agent generating logs
            **kwargs: Additional arguments passed to JSONFormatter
        """
        extra_fields = kwargs.get('extra_fields', {})
        
        if crew_name:
            extra_fields['crew'] = crew_name
        if agent_name:
            extra_fields['agent'] = agent_name
        
        # Add system context
        extra_fields['system'] = 'ADOS'
        extra_fields['component'] = 'crew_ai'
        
        kwargs['extra_fields'] = extra_fields
        super().__init__(**kwargs)


class PerformanceAwareJSONFormatter(JSONFormatter):
    """
    JSON formatter with performance metrics integration
    Includes timing and performance data in log entries
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with performance metrics
        
        Args:
            record: LogRecord to format
            
        Returns:
            JSON formatted log entry with performance data
        """
        # Check for performance metrics in record
        if hasattr(record, 'performance_metrics'):
            metrics = record.performance_metrics
            
            # Add performance data to extra fields
            if not hasattr(self, 'extra_fields'):
                self.extra_fields = {}
            
            self.extra_fields.update({
                'performance': {
                    'duration_ms': metrics.get('duration_ms'),
                    'memory_usage_mb': metrics.get('memory_usage_mb'),
                    'cpu_usage_percent': metrics.get('cpu_usage_percent'),
                    'operation': metrics.get('operation')
                }
            })
        
        return super().format(record)


class StructuredMessageFormatter(JSONFormatter):
    """
    Formatter that handles structured messages
    Supports both string messages and dictionary/object messages
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record, handling structured message objects
        
        Args:
            record: LogRecord to format
            
        Returns:
            JSON formatted log entry
        """
        # Handle structured messages
        if hasattr(record, 'structured_data'):
            structured = record.structured_data
            
            # Update message with structured data
            if isinstance(structured, dict):
                record.msg = structured.get('message', record.msg)
                
                # Add structured fields to record
                for key, value in structured.items():
                    if key != 'message':
                        setattr(record, key, value)
        
        return super().format(record)


def create_formatter(formatter_type: str = "json", **kwargs) -> logging.Formatter:
    """
    Factory function to create appropriate formatter
    
    Args:
        formatter_type: Type of formatter to create
        **kwargs: Additional arguments for formatter
        
    Returns:
        Configured formatter instance
    """
    formatters = {
        'json': JSONFormatter,
        'crew_aware': CrewAwareJSONFormatter,
        'performance': PerformanceAwareJSONFormatter,
        'structured': StructuredMessageFormatter
    }
    
    formatter_class = formatters.get(formatter_type, JSONFormatter)
    return formatter_class(**kwargs)


def configure_json_logging(logger: logging.Logger, 
                          formatter_type: str = "json",
                          **formatter_kwargs) -> None:
    """
    Configure a logger to use JSON formatting
    
    Args:
        logger: Logger instance to configure
        formatter_type: Type of JSON formatter to use
        **formatter_kwargs: Additional arguments for formatter
    """
    formatter = create_formatter(formatter_type, **formatter_kwargs)
    
    # Apply formatter to all handlers
    for handler in logger.handlers:
        handler.setFormatter(formatter)