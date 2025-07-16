"""
Crew Logger Utilities for ADOS System
Provides crew-specific logging capabilities with context awareness
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from orchestrator.logging_service import get_logging_service
from orchestrator.performance_monitor import get_performance_monitor, track_operation
from tools.logging.formatters import CrewAwareJSONFormatter


class CrewLogger:
    """
    Crew-specific logger that provides context-aware logging
    Integrates with performance monitoring and structured logging
    """
    
    def __init__(self, 
                 crew_name: str,
                 agent_name: Optional[str] = None,
                 task_context: Optional[Dict[str, Any]] = None):
        """
        Initialize crew logger
        
        Args:
            crew_name: Name of the crew
            agent_name: Optional agent name
            task_context: Optional task context information
        """
        self.crew_name = crew_name
        self.agent_name = agent_name
        self.task_context = task_context or {}
        
        # Get logging service
        self.logging_service = get_logging_service()
        
        # Get crew-specific logger
        self.logger = self.logging_service.create_crew_logger(crew_name, agent_name)
        
        # Get performance monitor
        self.performance_monitor = get_performance_monitor()
        
        # Track active operations
        self.active_operations: Dict[str, str] = {}
    
    def _get_log_context(self, extra_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get logging context with crew, agent, and task information
        
        Args:
            extra_context: Additional context to include
            
        Returns:
            Complete logging context
        """
        context = {
            'crew': self.crew_name,
            'timestamp': datetime.now().isoformat(),
            'system': 'ADOS',
            'component': 'crew_ai'
        }
        
        if self.agent_name:
            context['agent'] = self.agent_name
        
        if self.task_context:
            context['task'] = self.task_context
        
        if extra_context:
            context.update(extra_context)
        
        return context
    
    def debug(self, message: str, **kwargs):
        """Log debug message with crew context"""
        context = self._get_log_context(kwargs)
        self.logger.debug(message, extra=context)
    
    def info(self, message: str, **kwargs):
        """Log info message with crew context"""
        context = self._get_log_context(kwargs)
        self.logger.info(message, extra=context)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with crew context"""
        context = self._get_log_context(kwargs)
        self.logger.warning(message, extra=context)
    
    def error(self, message: str, **kwargs):
        """Log error message with crew context"""
        context = self._get_log_context(kwargs)
        self.logger.error(message, extra=context)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with crew context"""
        context = self._get_log_context(kwargs)
        self.logger.critical(message, extra=context)
    
    def log_task_start(self, task_description: str, task_id: Optional[str] = None):
        """
        Log task start with performance tracking
        
        Args:
            task_description: Description of the task
            task_id: Optional task identifier
        """
        # Start performance tracking
        operation_id = self.performance_monitor.start_operation(f"task_{self.crew_name}")
        
        # Store operation ID
        task_key = task_id or task_description
        self.active_operations[task_key] = operation_id
        
        # Log task start
        self.info(
            f"Task started: {task_description}",
            task_id=task_id,
            task_description=task_description,
            operation_id=operation_id,
            log_type='task_lifecycle'
        )
    
    def log_task_end(self, task_description: str, 
                     task_id: Optional[str] = None,
                     result: Optional[Any] = None,
                     status: str = "completed"):
        """
        Log task completion with performance metrics
        
        Args:
            task_description: Description of the task
            task_id: Optional task identifier
            result: Optional task result
            status: Task completion status
        """
        # Get operation ID
        task_key = task_id or task_description
        operation_id = self.active_operations.pop(task_key, None)
        
        # End performance tracking
        metrics = None
        if operation_id:
            metrics = self.performance_monitor.end_operation(operation_id)
        
        # Log task completion
        log_data = {
            'task_id': task_id,
            'task_description': task_description,
            'status': status,
            'log_type': 'task_lifecycle'
        }
        
        if result is not None:
            log_data['result'] = str(result)
        
        if metrics:
            log_data['performance'] = metrics.to_dict()
        
        self.info(f"Task {status}: {task_description}", **log_data)
    
    def log_agent_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """
        Log agent action with context
        
        Args:
            action: Action performed by agent
            details: Optional action details
        """
        log_data = {
            'action': action,
            'log_type': 'agent_action'
        }
        
        if details:
            log_data.update(details)
        
        self.info(f"Agent action: {action}", **log_data)
    
    def log_crew_communication(self, message: str, 
                              target_crew: Optional[str] = None,
                              message_type: str = "info"):
        """
        Log crew-to-crew communication
        
        Args:
            message: Communication message
            target_crew: Target crew name
            message_type: Type of message
        """
        log_data = {
            'message': message,
            'target_crew': target_crew,
            'message_type': message_type,
            'log_type': 'crew_communication'
        }
        
        self.info(f"Crew communication: {message}", **log_data)
    
    def log_structured_data(self, event_type: str, data: Dict[str, Any]):
        """
        Log structured data with event type
        
        Args:
            event_type: Type of event
            data: Structured data to log
        """
        log_data = {
            'event_type': event_type,
            'log_type': 'structured_event',
            **data
        }
        
        self.info(f"Structured event: {event_type}", **log_data)
    
    def log_performance_metrics(self, operation: str, metrics: Dict[str, Any]):
        """
        Log performance metrics for specific operation
        
        Args:
            operation: Operation name
            metrics: Performance metrics
        """
        log_data = {
            'operation': operation,
            'performance_metrics': metrics,
            'log_type': 'performance'
        }
        
        self.info(f"Performance metrics for {operation}", **log_data)
    
    def log_error_with_context(self, error: Exception, 
                              context: str,
                              additional_info: Optional[Dict[str, Any]] = None):
        """
        Log error with full context information
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            additional_info: Additional error information
        """
        log_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'log_type': 'error'
        }
        
        if additional_info:
            log_data.update(additional_info)
        
        self.error(f"Error in {context}: {error}", **log_data)
    
    def create_child_logger(self, child_name: str) -> 'CrewLogger':
        """
        Create a child logger for sub-operations
        
        Args:
            child_name: Name for the child logger
            
        Returns:
            Child CrewLogger instance
        """
        child_agent_name = f"{self.agent_name}.{child_name}" if self.agent_name else child_name
        
        return CrewLogger(
            crew_name=self.crew_name,
            agent_name=child_agent_name,
            task_context=self.task_context
        )
    
    def update_task_context(self, context: Dict[str, Any]):
        """
        Update task context for subsequent logs
        
        Args:
            context: New task context
        """
        self.task_context.update(context)
    
    def get_logging_status(self) -> Dict[str, Any]:
        """
        Get current logging status
        
        Returns:
            Logging status information
        """
        return {
            'crew_name': self.crew_name,
            'agent_name': self.agent_name,
            'task_context': self.task_context,
            'active_operations': len(self.active_operations),
            'logger_name': self.logger.name,
            'logger_level': self.logger.level,
            'handler_count': len(self.logger.handlers)
        }


class CrewLoggerFactory:
    """
    Factory for creating crew loggers with consistent configuration
    """
    
    def __init__(self):
        """Initialize crew logger factory"""
        self.loggers: Dict[str, CrewLogger] = {}
    
    def get_logger(self, crew_name: str, 
                   agent_name: Optional[str] = None,
                   task_context: Optional[Dict[str, Any]] = None) -> CrewLogger:
        """
        Get or create a crew logger
        
        Args:
            crew_name: Name of the crew
            agent_name: Optional agent name
            task_context: Optional task context
            
        Returns:
            CrewLogger instance
        """
        # Create logger key
        logger_key = f"{crew_name}_{agent_name or 'default'}"
        
        # Get or create logger
        if logger_key not in self.loggers:
            self.loggers[logger_key] = CrewLogger(
                crew_name=crew_name,
                agent_name=agent_name,
                task_context=task_context
            )
        else:
            # Update task context if provided
            if task_context:
                self.loggers[logger_key].update_task_context(task_context)
        
        return self.loggers[logger_key]
    
    def get_all_loggers(self) -> Dict[str, CrewLogger]:
        """
        Get all active crew loggers
        
        Returns:
            Dictionary of all active loggers
        """
        return self.loggers.copy()
    
    def clear_loggers(self):
        """Clear all cached loggers"""
        self.loggers.clear()


# Global crew logger factory
_crew_logger_factory: Optional[CrewLoggerFactory] = None


def get_crew_logger_factory() -> CrewLoggerFactory:
    """
    Get the global crew logger factory
    
    Returns:
        CrewLoggerFactory instance
    """
    global _crew_logger_factory
    if _crew_logger_factory is None:
        _crew_logger_factory = CrewLoggerFactory()
    return _crew_logger_factory


def get_crew_logger(crew_name: str, 
                    agent_name: Optional[str] = None,
                    task_context: Optional[Dict[str, Any]] = None) -> CrewLogger:
    """
    Get a crew logger using the global factory
    
    Args:
        crew_name: Name of the crew
        agent_name: Optional agent name
        task_context: Optional task context
        
    Returns:
        CrewLogger instance
    """
    return get_crew_logger_factory().get_logger(crew_name, agent_name, task_context)


def log_crew_startup(crew_name: str, agents: List[str]):
    """
    Log crew startup with agent information
    
    Args:
        crew_name: Name of the crew
        agents: List of agent names
    """
    logger = get_crew_logger(crew_name)
    logger.info(
        f"Crew {crew_name} starting up",
        agents=agents,
        agent_count=len(agents),
        log_type='crew_lifecycle'
    )


def log_crew_shutdown(crew_name: str):
    """
    Log crew shutdown
    
    Args:
        crew_name: Name of the crew
    """
    logger = get_crew_logger(crew_name)
    logger.info(
        f"Crew {crew_name} shutting down",
        log_type='crew_lifecycle'
    )


def log_system_event(event_type: str, details: Dict[str, Any]):
    """
    Log system-wide events
    
    Args:
        event_type: Type of system event
        details: Event details
    """
    logger = get_crew_logger('system')
    logger.log_structured_data(event_type, details)