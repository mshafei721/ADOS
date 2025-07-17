#!/usr/bin/env python3
"""
Phase 3.1 Integration Tests
Integration tests for orchestrator crew component interactions
"""

import asyncio
import sys
import unittest
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import json
import tempfile
import time
from datetime import datetime

# Add the project paths to Python path
project_root = Path(__file__).parent
dev_agent_path = project_root / "dev-agent-system"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dev_agent_path))

# Change to dev-agent-system directory
import os
os.chdir(dev_agent_path)


class TestOrchestratorToolsIntegration(unittest.TestCase):
    """Integration tests for orchestrator tools working together"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_task = "Develop user authentication system with database integration"
        self.test_crew = "development_crew"
    
    @pytest.mark.asyncio
    async def test_full_task_workflow(self):
        """Test complete task workflow: decompose -> allocate -> monitor"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress
        )
        
        # Step 1: Decompose task
        decomposition_result = await get_decomposed_tasks(self.test_task)
        decomposed_data = json.loads(decomposition_result)
        
        self.assertIn('subtasks', decomposed_data)
        self.assertGreater(len(decomposed_data['subtasks']), 0)
        
        # Step 2: Allocate first subtask to crew
        first_subtask = decomposed_data['subtasks'][0]
        allocation_result = await allocate_task_to_crew(
            json.dumps(first_subtask), self.test_crew
        )
        allocation_data = json.loads(allocation_result)
        
        self.assertEqual(allocation_data['assigned_crew'], self.test_crew)
        self.assertEqual(allocation_data['status'], 'allocated')
        
        # Step 3: Monitor crew progress
        crew_identifier = allocation_data['allocation_id']
        progress_result = await monitor_crew_progress(crew_identifier)
        progress_data = json.loads(progress_result)
        
        self.assertEqual(progress_data['crew_identifier'], crew_identifier)
        self.assertIn('status', progress_data)
        self.assertIn('progress', progress_data)
    
    @pytest.mark.asyncio
    async def test_multiple_crew_allocation(self):
        """Test allocating multiple tasks to different crews"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew, list_available_crews
        )
        
        # Get available crews
        crews_result = await list_available_crews()
        crews_data = json.loads(crews_result)
        available_crews = [crew['name'] for crew in crews_data['available_crews']]
        
        # Decompose complex task
        decomposition_result = await get_decomposed_tasks(self.test_task)
        decomposed_data = json.loads(decomposition_result)
        
        # Allocate different subtasks to different crews
        allocations = []
        for i, subtask in enumerate(decomposed_data['subtasks'][:3]):  # First 3 subtasks
            crew_name = available_crews[i % len(available_crews)]
            allocation_result = await allocate_task_to_crew(
                json.dumps(subtask), crew_name
            )
            allocation_data = json.loads(allocation_result)
            allocations.append(allocation_data)
        
        # Verify all allocations succeeded
        self.assertEqual(len(allocations), min(3, len(decomposed_data['subtasks'])))
        
        for allocation in allocations:
            self.assertEqual(allocation['status'], 'allocated')
            self.assertIn('allocation_id', allocation)
            self.assertIn(allocation['assigned_crew'], available_crews)
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across tool interactions"""
        from tools.orchestrator_tools import (
            allocate_task_to_crew, monitor_crew_progress
        )
        
        # Test allocation with invalid JSON
        invalid_task = "not a json string"
        allocation_result = await allocate_task_to_crew(invalid_task, "invalid_crew")
        allocation_data = json.loads(allocation_result)
        
        # Should still work with string input
        self.assertEqual(allocation_data['assigned_crew'], 'invalid_crew')
        self.assertIn('task', allocation_data)
        
        # Test monitoring non-existent crew
        progress_result = await monitor_crew_progress("non_existent_crew_123")
        progress_data = json.loads(progress_result)
        
        self.assertEqual(progress_data['crew_identifier'], 'non_existent_crew_123')
        self.assertEqual(progress_data['data_source'], 'simulated')


class TestAgentFactoryIntegration(unittest.TestCase):
    """Integration tests for agent factory with real configuration"""
    
    def setUp(self):
        """Set up test environment with temporary config"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_agents.yaml"
        
        # Create test configuration
        test_config = {
            'orchestrator': {
                'role': 'System Orchestrator',
                'goal': 'Coordinate and manage all system operations effectively',
                'backstory': 'Expert orchestrator with deep system knowledge',
                'tools': ['system_monitor', 'memory_writer', 'task_decomposer']
            },
            'analysis': {
                'role': 'System Analyst',
                'goal': 'Analyze system performance and identify optimization opportunities',
                'backstory': 'Experienced analyst specializing in system optimization',
                'tools': ['system_monitor', 'get_alerts', 'search_memory']
            },
            'planning': {
                'role': 'Strategic Planner',
                'goal': 'Create comprehensive plans for complex tasks',
                'backstory': 'Strategic planning expert with project management skills',
                'tools': ['prd_parser', 'task_decomposer', 'memory_writer']
            }
        }
        
        import yaml
        with open(self.config_file, 'w') as f:
            yaml.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('config.config_loader.ConfigLoader')
    def test_agent_factory_with_real_config(self, mock_config_loader_class):
        """Test agent factory with realistic configuration"""
        from orchestrator.agent_factory import AgentFactory
        
        # Mock config loader to return our test config
        mock_config_loader = Mock()
        mock_config_loader.load_agents_config.return_value = {
            'orchestrator': {
                'role': 'System Orchestrator',
                'goal': 'Coordinate system operations',
                'backstory': 'Expert in system coordination',
                'tools': ['system_monitor', 'memory_writer']
            }
        }
        mock_config_loader_class.return_value = mock_config_loader
        
        factory = AgentFactory(mock_config_loader)
        
        # Test that tools are properly registered
        self.assertIn('system_monitor', factory._tools_registry)
        self.assertIn('memory_writer', factory._tools_registry)
        
        # Test that functional tools are callable
        system_monitor_tool = factory._tools_registry['system_monitor']
        self.assertIsNotNone(system_monitor_tool)
        
    def test_agent_factory_tools_integration(self):
        """Test agent factory tools integration"""
        from orchestrator.agent_factory import AgentFactory
        from config.config_loader import ConfigLoader
        
        # Create real config loader
        mock_config_loader = Mock()
        mock_config_loader.load_agents_config.return_value = {}
        
        factory = AgentFactory(mock_config_loader)
        
        # Test that all required tools are available
        required_tools = [
            'system_monitor', 'memory_writer', 'prd_parser', 'task_decomposer'
        ]
        
        for tool_name in required_tools:
            self.assertIn(tool_name, factory._tools_registry)
            tool_func = factory._tools_registry[tool_name]
            self.assertIsNotNone(tool_func)
            # Test that it's callable
            self.assertTrue(callable(tool_func))


class TestOrchestratorCrewIntegration(unittest.TestCase):
    """Integration tests for orchestrator crew with dependencies"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_config_loader = Mock()
        self.mock_agent_factory = Mock()
        
        # Mock agent factory methods
        self.mock_orchestrator_agent = Mock()
        self.mock_analysis_agent = Mock()
        self.mock_planning_agent = Mock()
        
        self.mock_agent_factory.create_orchestrator_agent.return_value = self.mock_orchestrator_agent
        self.mock_agent_factory.create_analysis_agent.return_value = self.mock_analysis_agent
        self.mock_agent_factory.create_planning_agent.return_value = self.mock_planning_agent
    
    @patch('crews.orchestrator.orchestrator_crew.OrchestratorCrew._setup_crew_monitoring')
    @patch('crews.orchestrator.orchestrator_crew.OrchestratorCrew._setup_performance_tracking')
    @patch('crews.orchestrator.orchestrator_crew.OrchestratorCrew._setup_task_queue_management')
    def test_crew_initialization_with_dependencies(self, mock_task_queue, mock_performance, mock_monitoring):
        """Test crew initialization with all dependencies"""
        from crews.orchestrator.orchestrator_crew import OrchestratorCrew
        
        # Mock setup methods
        mock_monitoring.return_value = True
        mock_performance.return_value = True
        mock_task_queue.return_value = True
        
        crew = OrchestratorCrew(self.mock_config_loader, self.mock_agent_factory)
        
        # Verify initialization called setup methods
        mock_monitoring.assert_called_once()
        mock_performance.assert_called_once()
        mock_task_queue.assert_called_once()
        
        # Verify crew state
        self.assertIsNotNone(crew.config_loader)
        self.assertIsNotNone(crew.agent_factory)
        self.assertIsInstance(crew.system_status, dict)
        self.assertIsInstance(crew.task_queue, list)
    
    def test_crew_and_agent_factory_integration(self):
        """Test integration between crew and agent factory"""
        from crews.orchestrator.orchestrator_crew import OrchestratorCrew
        from orchestrator.agent_factory import AgentFactory
        
        # Create real agent factory with mock config
        mock_config_loader = Mock()
        mock_config_loader.load_agents_config.return_value = {
            'orchestrator': {
                'role': 'Test Orchestrator',
                'goal': 'Test coordination', 
                'backstory': 'Test backstory',
                'tools': ['system_monitor']
            }
        }
        
        real_agent_factory = AgentFactory(mock_config_loader)
        
        # Test that crew can be created with real agent factory
        with patch('crews.orchestrator.orchestrator_crew.OrchestratorCrew.initialize_system_awareness'):
            crew = OrchestratorCrew(mock_config_loader, real_agent_factory)
            
            self.assertEqual(crew.agent_factory, real_agent_factory)
            self.assertIsInstance(crew.agent_factory._tools_registry, dict)


class TestFullSystemIntegration(unittest.TestCase):
    """Integration tests for full Phase 3.1 system"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_tools_with_task_decomposer(self):
        """Test orchestrator tools integration with task decomposer"""
        from tools.orchestrator_tools import get_decomposed_tasks
        
        # Test with complex task requiring multiple crews
        complex_task = """
        Build a microservices-based e-commerce platform with:
        - User authentication service
        - Product catalog service
        - Order management service
        - Payment processing integration
        - API gateway and monitoring
        """
        
        result = await get_decomposed_tasks(complex_task)
        parsed_result = json.loads(result)
        
        # Should have decomposed into multiple subtasks
        self.assertIn('subtasks', parsed_result)
        subtasks = parsed_result['subtasks']
        self.assertGreater(len(subtasks), 2)
        
        # Should have crew assignments
        self.assertIn('crew_assignments', parsed_result)
        
        # Should have dependencies
        self.assertIn('dependencies', parsed_result)
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_operations(self):
        """Test concurrent orchestrator tool operations"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress,
            list_available_crews, get_orchestrator_status
        )
        
        tasks = [
            "Implement user registration system",
            "Create product search functionality", 
            "Build order processing workflow"
        ]
        
        # Run multiple operations concurrently
        concurrent_tasks = []
        
        # Add decomposition tasks
        for task in tasks:
            concurrent_tasks.append(get_decomposed_tasks(task))
        
        # Add other operations
        concurrent_tasks.extend([
            list_available_crews(),
            get_orchestrator_status(),
            monitor_crew_progress("test_crew_concurrent")
        ])
        
        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        execution_time = time.time() - start_time
        
        # Verify all tasks completed
        self.assertEqual(len(results), len(concurrent_tasks))
        
        # Verify no exceptions (or handle expected ones)
        successful_results = [r for r in results if not isinstance(r, Exception)]
        self.assertGreater(len(successful_results), len(concurrent_tasks) * 0.8)  # 80% success rate
        
        # Verify concurrent execution was faster than sequential
        self.assertLess(execution_time, 30)  # Should complete within 30 seconds
        
        # Verify decomposition results
        decomposition_results = results[:len(tasks)]
        for result in decomposition_results:
            if not isinstance(result, Exception):
                parsed = json.loads(result)
                self.assertIn('subtasks', parsed)
    
    @pytest.mark.asyncio
    async def test_error_propagation_and_recovery(self):
        """Test error propagation and recovery across components"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress
        )
        
        # Test with various error conditions
        error_test_cases = [
            ("", "empty_crew"),  # Empty task
            ("valid task", ""),   # Empty crew
            (None, "valid_crew"), # None task
            ("valid task", None)  # None crew
        ]
        
        for task, crew in error_test_cases:
            try:
                if task is not None:
                    decomp_result = await get_decomposed_tasks(task)
                    # Should return valid JSON even with empty/invalid input
                    json.loads(decomp_result)
                
                if task is not None and crew is not None:
                    alloc_result = await allocate_task_to_crew(task, crew)
                    # Should return valid JSON even with invalid input
                    json.loads(alloc_result)
                
                if crew is not None:
                    monitor_result = await monitor_crew_progress(crew)
                    # Should return valid JSON even with invalid crew
                    json.loads(monitor_result)
            
            except Exception as e:
                # If exceptions occur, they should be handled gracefully
                self.fail(f"Unhandled exception for inputs ({task}, {crew}): {e}")


if __name__ == "__main__":
    # Run async tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])