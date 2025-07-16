"""
Basic Integration Test for ADOS Logging Infrastructure
Simple test to verify that all components work together
"""

import tempfile
import json
import os
from unittest.mock import Mock, patch
from pathlib import Path

from orchestrator.logging_service import LoggingService
from orchestrator.performance_monitor import PerformanceMonitor
from tools.logging.crew_logger import CrewLogger


def test_logging_integration():
    """Test basic logging integration"""
    
    # Create temporary directory for logs
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock system settings
        system_settings = {
            "logging": {
                "level": "INFO",
                "format": "json",
                "rotate_size_mb": 10,
                "max_files": 5
            },
            "output": {
                "base_directory": temp_dir,
                "structure": {
                    "logs": "logs"
                }
            }
        }
        
        # Mock config loader
        mock_config_loader = Mock()
        mock_config_loader.load_system_settings.return_value = system_settings
        
        # Test logging service
        logging_service = LoggingService(mock_config_loader)
        assert logging_service.initialize() == True
        
        # Test logger creation
        logger = logging_service.get_logger('test_logger')
        assert logger is not None
        
        # Test crew logger
        crew_logger = logging_service.create_crew_logger('test_crew', 'test_agent')
        assert crew_logger is not None
        
        # Test performance monitor
        perf_monitor = PerformanceMonitor(enable_logging=False)
        op_id = perf_monitor.start_operation('test_op')
        assert op_id is not None
        
        metrics = perf_monitor.end_operation(op_id)
        assert metrics is not None
        assert metrics.operation == 'test_op'
        
        # Test log file creation
        logs_dir = Path(temp_dir) / 'logs'
        assert logs_dir.exists()
        
        print("✅ All logging components working correctly!")
        return True


if __name__ == '__main__':
    test_logging_integration()