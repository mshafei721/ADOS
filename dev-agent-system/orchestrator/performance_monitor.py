"""
Performance Monitor for ADOS System
Provides performance tracking and metrics collection capabilities
"""

import time
import psutil
import logging
import functools
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading


@dataclass
class PerformanceMetrics:
    """Data class for performance metrics"""
    operation: str
    start_time: float
    end_time: float
    duration_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    thread_id: int
    process_id: int
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return asdict(self)


class PerformanceMonitor:
    """
    Performance monitoring system for ADOS operations
    Tracks timing, memory usage, and CPU utilization
    """
    
    def __init__(self, enable_logging: bool = True):
        """
        Initialize performance monitor
        
        Args:
            enable_logging: Whether to enable performance logging
        """
        self.enable_logging = enable_logging
        self.metrics_history: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, float] = {}
        self.lock = threading.Lock()
        
        # Performance logger
        self.logger = logging.getLogger("performance") if enable_logging else None
    
    def start_operation(self, operation_name: str) -> str:
        """
        Start tracking an operation
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        with self.lock:
            self.active_operations[operation_id] = time.time()
        
        return operation_id
    
    def end_operation(self, operation_id: str) -> Optional[PerformanceMetrics]:
        """
        End tracking an operation and collect metrics
        
        Args:
            operation_id: Operation ID from start_operation
            
        Returns:
            Performance metrics if operation was tracked
        """
        with self.lock:
            if operation_id not in self.active_operations:
                return None
            
            start_time = self.active_operations.pop(operation_id)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Get system metrics
        process = psutil.Process()
        memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        cpu_usage_percent = process.cpu_percent()
        
        # Create metrics object
        metrics = PerformanceMetrics(
            operation=operation_id.split('_')[0],
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            thread_id=threading.get_ident(),
            process_id=process.pid,
            timestamp=datetime.now().isoformat()
        )
        
        # Store metrics
        self.metrics_history.append(metrics)
        
        # Log metrics
        if self.logger:
            self.logger.info(
                f"Operation completed: {metrics.operation}",
                extra={
                    'performance_metrics': metrics.to_dict(),
                    'log_type': 'performance'
                }
            )
        
        return metrics
    
    @contextmanager
    def track_operation(self, operation_name: str):
        """
        Context manager for tracking operations
        
        Args:
            operation_name: Name of the operation
            
        Yields:
            Performance metrics object (populated after operation)
        """
        operation_id = self.start_operation(operation_name)
        metrics = None
        
        try:
            yield metrics
        finally:
            metrics = self.end_operation(operation_id)
    
    def timing_decorator(self, operation_name: Optional[str] = None):
        """
        Decorator for timing function calls
        
        Args:
            operation_name: Optional operation name, defaults to function name
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name or func.__name__
                
                with self.track_operation(op_name):
                    return func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def get_metrics_summary(self, operation_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary of performance metrics
        
        Args:
            operation_filter: Optional filter for specific operations
            
        Returns:
            Summary statistics
        """
        with self.lock:
            metrics = self.metrics_history.copy()
        
        if operation_filter:
            metrics = [m for m in metrics if m.operation == operation_filter]
        
        if not metrics:
            return {
                "total_operations": 0,
                "summary": "No metrics available"
            }
        
        # Calculate statistics
        durations = [m.duration_ms for m in metrics]
        memory_usage = [m.memory_usage_mb for m in metrics]
        cpu_usage = [m.cpu_usage_percent for m in metrics]
        
        summary = {
            "total_operations": len(metrics),
            "time_range": {
                "start": min(m.timestamp for m in metrics),
                "end": max(m.timestamp for m in metrics)
            },
            "duration_ms": {
                "min": min(durations),
                "max": max(durations),
                "avg": sum(durations) / len(durations),
                "total": sum(durations)
            },
            "memory_usage_mb": {
                "min": min(memory_usage),
                "max": max(memory_usage),
                "avg": sum(memory_usage) / len(memory_usage)
            },
            "cpu_usage_percent": {
                "min": min(cpu_usage),
                "max": max(cpu_usage),
                "avg": sum(cpu_usage) / len(cpu_usage)
            },
            "operations_by_type": {}
        }
        
        # Group by operation type
        for metric in metrics:
            op_type = metric.operation
            if op_type not in summary["operations_by_type"]:
                summary["operations_by_type"][op_type] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0
                }
            
            summary["operations_by_type"][op_type]["count"] += 1
            summary["operations_by_type"][op_type]["total_duration_ms"] += metric.duration_ms
        
        # Calculate averages
        for op_type in summary["operations_by_type"]:
            op_data = summary["operations_by_type"][op_type]
            op_data["avg_duration_ms"] = op_data["total_duration_ms"] / op_data["count"]
        
        return summary
    
    def get_recent_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent performance metrics
        
        Args:
            limit: Number of recent metrics to return
            
        Returns:
            List of recent metrics
        """
        with self.lock:
            recent_metrics = self.metrics_history[-limit:]
        
        return [m.to_dict() for m in recent_metrics]
    
    def get_slow_operations(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        """
        Get operations that exceeded the duration threshold
        
        Args:
            threshold_ms: Threshold in milliseconds
            
        Returns:
            List of slow operations
        """
        with self.lock:
            slow_operations = [
                m for m in self.metrics_history 
                if m.duration_ms > threshold_ms
            ]
        
        return [m.to_dict() for m in slow_operations]
    
    def clear_metrics(self):
        """Clear all stored metrics"""
        with self.lock:
            self.metrics_history.clear()
            self.active_operations.clear()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system performance metrics
        
        Returns:
            Current system metrics
        """
        process = psutil.Process()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "memory": {
                "rss_mb": process.memory_info().rss / (1024 * 1024),
                "vms_mb": process.memory_info().vms / (1024 * 1024),
                "percent": process.memory_percent()
            },
            "cpu": {
                "percent": process.cpu_percent(),
                "num_threads": process.num_threads()
            },
            "system": {
                "cpu_count": psutil.cpu_count(),
                "available_memory_mb": psutil.virtual_memory().available / (1024 * 1024),
                "total_memory_mb": psutil.virtual_memory().total / (1024 * 1024)
            }
        }
    
    def log_system_metrics(self):
        """Log current system metrics"""
        if self.logger:
            metrics = self.get_system_metrics()
            self.logger.info(
                "System metrics snapshot",
                extra={
                    'system_metrics': metrics,
                    'log_type': 'system_performance'
                }
            )


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance
    
    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def initialize_performance_monitoring(enable_logging: bool = True) -> PerformanceMonitor:
    """
    Initialize the global performance monitor
    
    Args:
        enable_logging: Whether to enable performance logging
        
    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    _performance_monitor = PerformanceMonitor(enable_logging)
    return _performance_monitor


# Convenience functions for global monitor
def track_operation(operation_name: str):
    """Context manager for tracking operations using global monitor"""
    return get_performance_monitor().track_operation(operation_name)


def timing_decorator(operation_name: Optional[str] = None):
    """Decorator for timing function calls using global monitor"""
    return get_performance_monitor().timing_decorator(operation_name)


def get_metrics_summary(operation_filter: Optional[str] = None) -> Dict[str, Any]:
    """Get metrics summary from global monitor"""
    return get_performance_monitor().get_metrics_summary(operation_filter)


def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics from global monitor"""
    return get_performance_monitor().get_system_metrics()


def log_system_metrics():
    """Log system metrics using global monitor"""
    get_performance_monitor().log_system_metrics()