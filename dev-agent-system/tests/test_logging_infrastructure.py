"""
Comprehensive Test Suite for ADOS Logging Infrastructure
Tests all logging components: formatters, handlers, service, monitor, and crew logger
"""

import os
import json
import logging
import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import shutil
import time

from tools.logging.formatters import (
    JSONFormatter, CrewAwareJSONFormatter, PerformanceAwareJSONFormatter,
    StructuredMessageFormatter, create_formatter, configure_json_logging
)
from tools.logging.handlers import (
    ADOSRotatingFileHandler, TimedRotatingFileHandler, 
    StructuredFileHandler, PerformanceLogHandler, create_handler
)
from orchestrator.logging_service import LoggingService, initialize_logging, get_logger
from orchestrator.performance_monitor import (
    PerformanceMonitor, PerformanceMetrics, initialize_performance_monitoring,
    track_operation, timing_decorator
)
from tools.logging.crew_logger import (
    CrewLogger, CrewLoggerFactory, get_crew_logger, log_crew_startup, log_crew_shutdown
)
from config.config_loader import ConfigLoader


class TestJSONFormatter(unittest.TestCase):
    """Test JSON formatting capabilities"""
    
    def setUp(self):
        """Set up test environment"""
        self.formatter = JSONFormatter()
        self.logger = logging.getLogger('test_json_formatter')
        self.logger.setLevel(logging.DEBUG)
    
    def test_basic_json_formatting(self):
        """Test basic JSON log formatting"""
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertIn('timestamp', log_data)
        self.assertIn('level', log_data)
        self.assertIn('logger', log_data)
        self.assertIn('message', log_data)
        self.assertEqual(log_data['level'], 'INFO')
        self.assertEqual(log_data['message'], 'Test message')
    
    def test_exception_formatting(self):
        """Test exception information in JSON logs"""
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name='test_logger',
            level=logging.ERROR,
            pathname='test.py',
            lineno=10,
            msg='Error occurred',
            args=(),
            exc_info=exc_info
        )
        
        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertIn('exception', log_data)
        self.assertIn('type', log_data['exception'])
        self.assertIn('message', log_data['exception'])
        self.assertIn('traceback', log_data['exception'])
        self.assertEqual(log_data['exception']['type'], 'ValueError')
    
    def test_crew_aware_formatter(self):
        """Test crew-aware JSON formatting"""
        formatter = CrewAwareJSONFormatter(
            crew_name='test_crew',
            agent_name='test_agent'
        )
        
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data['crew'], 'test_crew')
        self.assertEqual(log_data['agent'], 'test_agent')
        self.assertEqual(log_data['system'], 'ADOS')
    
    def test_performance_aware_formatter(self):
        """Test performance-aware JSON formatting"""
        formatter = PerformanceAwareJSONFormatter()
        
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # Add performance metrics
        record.performance_metrics = {
            'duration_ms': 100.5,
            'memory_usage_mb': 50.2,
            'cpu_usage_percent': 75.0,
            'operation': 'test_operation'
        }
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertIn('performance', log_data)
        self.assertEqual(log_data['performance']['duration_ms'], 100.5)
        self.assertEqual(log_data['performance']['operation'], 'test_operation')


class TestLogHandlers(unittest.TestCase):
    """Test custom log handlers"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, 'test.log')
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_rotating_file_handler(self):
        """Test rotating file handler"""
        handler = ADOSRotatingFileHandler(
            filename=self.log_file,
            maxBytes=1024,
            backupCount=2
        )
        
        logger = logging.getLogger('test_rotating')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Write logs to trigger rotation
        for i in range(100):
            logger.info(f'Test message {i} - this is a longer message to fill up the log file')
        
        # Check that backup files were created
        self.assertTrue(os.path.exists(self.log_file))
        
        handler.close()
    
    def test_structured_file_handler(self):
        """Test structured file handler"""
        handler = StructuredFileHandler(
            base_directory=self.temp_dir,
            max_file_size=1024,
            backup_count=2
        )
        
        logger = logging.getLogger('test_structured')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Test different log types
        record1 = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record1.log_type = 'performance'
        
        record2 = logging.LogRecord(
            name='test_logger',
            level=logging.ERROR,
            pathname='test.py',
            lineno=20,
            msg='Error message',
            args=(),
            exc_info=None
        )
        record2.log_type = 'error'
        
        handler.emit(record1)
        handler.emit(record2)
        
        # Check that separate files were created
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'performance.log')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'error.log')))
        
        handler.close()


class TestLoggingService(unittest.TestCase):
    """Test logging service functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir)
        
        # Create test configuration
        self.system_settings = {
            "logging": {
                "level": "INFO",
                "format": "json",
                "rotate_size_mb": 10,
                "max_files": 5
            },
            "output": {
                "base_directory": self.temp_dir,
                "structure": {
                    "logs": "logs"
                }
            }
        }
        
        with open(os.path.join(self.config_dir, 'system_settings.json'), 'w') as f:
            json.dump(self.system_settings, f)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('config.config_loader.ConfigLoader')
    def test_logging_service_initialization(self, mock_config_loader):
        """Test logging service initialization"""
        mock_config_loader.return_value.load_system_settings.return_value = self.system_settings
        
        service = LoggingService(mock_config_loader.return_value)
        self.assertTrue(service.initialize())
        self.assertTrue(service.initialized)
        
        # Check that logs directory was created
        logs_dir = os.path.join(self.temp_dir, 'logs')
        self.assertTrue(os.path.exists(logs_dir))
    
    @patch('config.config_loader.ConfigLoader')
    def test_crew_logger_creation(self, mock_config_loader):
        """Test crew logger creation"""
        mock_config_loader.return_value.load_system_settings.return_value = self.system_settings
        
        service = LoggingService(mock_config_loader.return_value)
        service.initialize()
        
        crew_logger = service.create_crew_logger('test_crew', 'test_agent')
        self.assertIsNotNone(crew_logger)
        self.assertEqual(crew_logger.name, 'crew.test_crew.test_agent')
    
    @patch('config.config_loader.ConfigLoader')
    def test_performance_logger_creation(self, mock_config_loader):
        """Test performance logger creation"""
        mock_config_loader.return_value.load_system_settings.return_value = self.system_settings
        
        service = LoggingService(mock_config_loader.return_value)
        service.initialize()
        
        perf_logger = service.create_performance_logger()
        self.assertIsNotNone(perf_logger)
        self.assertEqual(perf_logger.name, 'performance')
    
    @patch('config.config_loader.ConfigLoader')
    def test_logging_status(self, mock_config_loader):
        """Test logging status retrieval"""
        mock_config_loader.return_value.load_system_settings.return_value = self.system_settings
        
        service = LoggingService(mock_config_loader.return_value)
        service.initialize()
        
        status = service.get_logging_status()
        self.assertIn('initialized', status)
        self.assertIn('log_format', status)
        self.assertTrue(status['initialized'])
        self.assertEqual(status['log_format'], 'json')


class TestPerformanceMonitor(unittest.TestCase):
    """Test performance monitoring functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.monitor = PerformanceMonitor(enable_logging=False)
    
    def test_operation_tracking(self):
        """Test operation tracking"""
        # Start operation
        op_id = self.monitor.start_operation('test_operation')
        self.assertIsNotNone(op_id)
        
        # Simulate some work
        time.sleep(0.1)
        
        # End operation
        metrics = self.monitor.end_operation(op_id)
        self.assertIsNotNone(metrics)
        self.assertGreater(metrics.duration_ms, 0)
        self.assertEqual(metrics.operation, 'test_operation')
    
    def test_context_manager(self):
        """Test context manager for operation tracking"""
        with self.monitor.track_operation('context_test'):
            time.sleep(0.1)
        
        # Check that metrics were recorded
        summary = self.monitor.get_metrics_summary()
        self.assertGreater(summary['total_operations'], 0)
    
    def test_timing_decorator(self):
        """Test timing decorator"""
        @self.monitor.timing_decorator('decorated_function')
        def test_function():
            time.sleep(0.1)
            return 'result'
        
        result = test_function()
        self.assertEqual(result, 'result')
        
        # Check metrics
        summary = self.monitor.get_metrics_summary()
        self.assertGreater(summary['total_operations'], 0)
    
    def test_metrics_summary(self):
        """Test metrics summary generation"""
        # Generate some metrics
        for i in range(5):
            with self.monitor.track_operation(f'test_op_{i}'):
                time.sleep(0.05)
        
        summary = self.monitor.get_metrics_summary()
        self.assertEqual(summary['total_operations'], 5)
        self.assertIn('duration_ms', summary)
        self.assertIn('operations_by_type', summary)
    
    def test_slow_operations(self):
        """Test slow operations detection"""
        # Create slow operation
        with self.monitor.track_operation('slow_operation'):
            time.sleep(0.2)
        
        # Create fast operation
        with self.monitor.track_operation('fast_operation'):
            time.sleep(0.01)
        
        # Check slow operations with 100ms threshold
        slow_ops = self.monitor.get_slow_operations(100)
        self.assertEqual(len(slow_ops), 1)
        self.assertEqual(slow_ops[0]['operation'], 'slow_operation')


class TestCrewLogger(unittest.TestCase):
    """Test crew logger functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock logging service
        self.mock_logging_service = Mock()
        self.mock_logger = Mock()
        self.mock_logging_service.create_crew_logger.return_value = self.mock_logger
        
        # Mock performance monitor
        self.mock_performance_monitor = Mock()
        
        # Patch dependencies
        self.logging_service_patcher = patch('tools.logging.crew_logger.get_logging_service')
        self.performance_monitor_patcher = patch('tools.logging.crew_logger.get_performance_monitor')
        
        self.mock_get_logging_service = self.logging_service_patcher.start()
        self.mock_get_performance_monitor = self.performance_monitor_patcher.start()
        
        self.mock_get_logging_service.return_value = self.mock_logging_service
        self.mock_get_performance_monitor.return_value = self.mock_performance_monitor
    
    def tearDown(self):
        """Clean up test environment"""
        self.logging_service_patcher.stop()
        self.performance_monitor_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_crew_logger_creation(self):
        """Test crew logger creation"""
        crew_logger = CrewLogger('test_crew', 'test_agent')
        
        self.assertEqual(crew_logger.crew_name, 'test_crew')
        self.assertEqual(crew_logger.agent_name, 'test_agent')
        self.mock_logging_service.create_crew_logger.assert_called_once_with('test_crew', 'test_agent')
    
    def test_task_lifecycle_logging(self):
        """Test task lifecycle logging"""
        crew_logger = CrewLogger('test_crew', 'test_agent')
        
        # Mock performance monitor
        self.mock_performance_monitor.start_operation.return_value = 'op_123'
        mock_metrics = Mock()
        mock_metrics.to_dict.return_value = {'duration_ms': 100}
        self.mock_performance_monitor.end_operation.return_value = mock_metrics
        
        # Test task start
        crew_logger.log_task_start('test task', 'task_123')
        self.mock_performance_monitor.start_operation.assert_called_once()
        
        # Test task end
        crew_logger.log_task_end('test task', 'task_123', 'success', 'completed')
        self.mock_performance_monitor.end_operation.assert_called_once_with('op_123')
    
    def test_crew_communication_logging(self):
        """Test crew communication logging"""
        crew_logger = CrewLogger('test_crew', 'test_agent')
        
        crew_logger.log_crew_communication('Hello world', 'other_crew', 'info')
        
        # Verify logging call
        self.mock_logger.info.assert_called()
        args, kwargs = self.mock_logger.info.call_args
        self.assertIn('Crew communication', args[0])
        self.assertEqual(kwargs['message'], 'Hello world')
        self.assertEqual(kwargs['target_crew'], 'other_crew')
    
    def test_structured_data_logging(self):
        """Test structured data logging"""
        crew_logger = CrewLogger('test_crew', 'test_agent')
        
        test_data = {'key1': 'value1', 'key2': 'value2'}
        crew_logger.log_structured_data('test_event', test_data)
        
        # Verify logging call
        self.mock_logger.info.assert_called()
        args, kwargs = self.mock_logger.info.call_args
        self.assertIn('Structured event', args[0])
        self.assertEqual(kwargs['event_type'], 'test_event')
        self.assertEqual(kwargs['key1'], 'value1')
        self.assertEqual(kwargs['key2'], 'value2')
    
    def test_child_logger_creation(self):
        """Test child logger creation"""
        crew_logger = CrewLogger('test_crew', 'test_agent')
        child_logger = crew_logger.create_child_logger('child')
        
        self.assertEqual(child_logger.crew_name, 'test_crew')
        self.assertEqual(child_logger.agent_name, 'test_agent.child')


class TestIntegration(unittest.TestCase):
    """Integration tests for the entire logging infrastructure"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.system_settings = {
            "logging": {
                "level": "INFO",
                "format": "json",
                "rotate_size_mb": 10,
                "max_files": 5
            },
            "output": {
                "base_directory": self.temp_dir,
                "structure": {
                    "logs": "logs"
                }
            }
        }
    
    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('config.config_loader.ConfigLoader')
    def test_end_to_end_logging(self, mock_config_loader):
        """Test end-to-end logging workflow"""
        mock_config_loader.return_value.load_system_settings.return_value = self.system_settings
        
        # Initialize logging service
        service = LoggingService(mock_config_loader.return_value)
        self.assertTrue(service.initialize())
        
        # Initialize performance monitoring
        perf_monitor = initialize_performance_monitoring(enable_logging=True)
        
        # Create crew logger
        crew_logger = get_crew_logger('test_crew', 'test_agent')
        
        # Test complete workflow
        crew_logger.log_task_start('integration test task', 'int_task_1')
        
        with perf_monitor.track_operation('test_operation'):
            time.sleep(0.1)
            crew_logger.info('Task in progress')
        
        crew_logger.log_task_end('integration test task', 'int_task_1', 'success')
        
        # Verify log files were created
        logs_dir = os.path.join(self.temp_dir, 'logs')
        self.assertTrue(os.path.exists(logs_dir))
        
        # Check for crew-specific log file
        crew_log_file = os.path.join(logs_dir, 'crew_test_crew.log')
        self.assertTrue(os.path.exists(crew_log_file))
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration"""
        # Initialize performance monitoring
        perf_monitor = initialize_performance_monitoring(enable_logging=False)
        
        # Test with timing decorator
        @timing_decorator('decorated_test')
        def test_function():
            time.sleep(0.1)
            return 'success'
        
        result = test_function()
        self.assertEqual(result, 'success')
        
        # Check metrics
        summary = perf_monitor.get_metrics_summary()
        self.assertGreater(summary['total_operations'], 0)
        
        # Test slow operations
        slow_ops = perf_monitor.get_slow_operations(50)  # 50ms threshold
        self.assertGreater(len(slow_ops), 0)


if __name__ == '__main__':
    # Import sys for exception handling test
    import sys
    
    # Run tests with verbose output
    unittest.main(verbosity=2)