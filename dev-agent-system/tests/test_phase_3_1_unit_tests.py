#!/usr/bin/env python3
"""
Phase 3.1 Unit Tests
Unit tests for individual orchestrator crew components
"""

import asyncio
import sys
import unittest
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime

# Add the project paths to Python path
project_root = Path(__file__).parent
dev_agent_path = project_root / "dev-agent-system"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dev_agent_path))

# Change to dev-agent-system directory
import os
os.chdir(dev_agent_path)


class TestOrchestratorTools(unittest.TestCase):
    """Unit tests for orchestrator tools"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_task = "Analyze user requirements and create development plan"
        self.test_crew = "development_crew"
        self.test_identifier = "test_crew_001"
    
    @pytest.mark.asyncio
    async def test_get_decomposed_tasks_success(self):
        """Test successful task decomposition"""
        from tools.orchestrator_tools import get_decomposed_tasks
        
        result = await get_decomposed_tasks(self.test_task)
        
        # Verify result is valid JSON
        parsed_result = json.loads(result)
        self.assertIn('subtasks', parsed_result)
        self.assertIn('dependencies', parsed_result)
        self.assertIn('crew_assignments', parsed_result)
        self.assertIsInstance(parsed_result['subtasks'], list)
        self.assertGreater(len(parsed_result['subtasks']), 0)
    
    @pytest.mark.asyncio
    async def test_get_decomposed_tasks_with_real_decomposer(self):
        """Test task decomposition with mock TaskDecomposer"""
        from tools.orchestrator_tools import get_decomposed_tasks
        
        # Mock the TaskDecomposer import
        mock_result = {
            "task_id": "test_task_123",
            "subtasks": [
                {"id": "subtask_1", "title": "Test Subtask 1"},
                {"id": "subtask_2", "title": "Test Subtask 2"}
            ],
            "dependencies": [],
            "crew_assignments": {"subtask_1": "crew_a", "subtask_2": "crew_b"}
        }
        
        with patch('tools.orchestrator_tools.TaskDecomposer') as mock_decomposer_class:
            mock_decomposer = Mock()
            mock_decomposer.decompose_task = AsyncMock(return_value=mock_result)
            mock_decomposer_class.return_value = mock_decomposer
            
            result = await get_decomposed_tasks(self.test_task)
            parsed_result = json.loads(result)
            
            self.assertEqual(parsed_result['task_id'], "test_task_123")
            self.assertEqual(len(parsed_result['subtasks']), 2)
    
    @pytest.mark.asyncio
    async def test_allocate_task_to_crew_success(self):
        """Test successful task allocation"""
        from tools.orchestrator_tools import allocate_task_to_crew
        
        task_info = json.dumps({
            "id": "test_task",
            "description": "Test task description",
            "priority": "high"
        })
        
        result = await allocate_task_to_crew(task_info, self.test_crew)
        parsed_result = json.loads(result)
        
        self.assertIn('allocation_id', parsed_result)
        self.assertEqual(parsed_result['assigned_crew'], self.test_crew)
        self.assertEqual(parsed_result['status'], 'allocated')
        self.assertIn('allocated_at', parsed_result)
    
    @pytest.mark.asyncio 
    async def test_allocate_task_to_crew_string_input(self):
        """Test task allocation with string input"""
        from tools.orchestrator_tools import allocate_task_to_crew
        
        result = await allocate_task_to_crew(self.test_task, self.test_crew)
        parsed_result = json.loads(result)
        
        self.assertEqual(parsed_result['assigned_crew'], self.test_crew)
        self.assertIn('task', parsed_result)
        self.assertEqual(parsed_result['task']['description'], self.test_task)
    
    @pytest.mark.asyncio
    async def test_monitor_crew_progress_success(self):
        """Test successful crew progress monitoring"""
        from tools.orchestrator_tools import monitor_crew_progress
        
        result = await monitor_crew_progress(self.test_identifier)
        parsed_result = json.loads(result)
        
        self.assertEqual(parsed_result['crew_identifier'], self.test_identifier)
        self.assertIn('monitoring_timestamp', parsed_result)
        self.assertIn('status', parsed_result)
        self.assertIn('progress', parsed_result)
        self.assertIn('agents', parsed_result)
    
    @pytest.mark.asyncio
    async def test_monitor_crew_progress_with_status_file(self):
        """Test crew monitoring with existing status file"""
        from tools.orchestrator_tools import monitor_crew_progress
        
        # Create a temporary workspace with status file
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_dir = Path(temp_dir) / "workspace"
            workspace_dir.mkdir()
            
            status_file = workspace_dir / f"{self.test_identifier}_status.json"
            status_data = {
                "real_status": True,
                "custom_field": "test_value",
                "crew_identifier": self.test_identifier
            }
            
            with open(status_file, 'w') as f:
                json.dump(status_data, f)
            
            # Temporarily change to temp directory
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result = await monitor_crew_progress(self.test_identifier)
                parsed_result = json.loads(result)
                
                self.assertTrue(parsed_result.get('real_status'))
                self.assertEqual(parsed_result.get('custom_field'), 'test_value')
                self.assertEqual(parsed_result['data_source'], 'real_status_file')
            finally:
                os.chdir(old_cwd)
    
    @pytest.mark.asyncio
    async def test_list_available_crews(self):
        """Test listing available crews"""
        from tools.orchestrator_tools import list_available_crews
        
        result = await list_available_crews()
        parsed_result = json.loads(result)
        
        self.assertIn('available_crews', parsed_result)
        self.assertIn('total_crews', parsed_result)
        self.assertIsInstance(parsed_result['available_crews'], list)
        self.assertGreater(parsed_result['total_crews'], 0)
        
        # Check first crew structure
        first_crew = parsed_result['available_crews'][0]
        self.assertIn('name', first_crew)
        self.assertIn('description', first_crew)
        self.assertIn('specialization', first_crew)
        self.assertIn('status', first_crew)
    
    @pytest.mark.asyncio
    async def test_get_orchestrator_status(self):
        """Test getting orchestrator status"""
        from tools.orchestrator_tools import get_orchestrator_status
        
        result = await get_orchestrator_status()
        parsed_result = json.loads(result)
        
        self.assertIn('orchestrator_status', parsed_result)
        self.assertIn('system_health', parsed_result)
        self.assertIn('system_metrics', parsed_result)
        self.assertIn('component_status', parsed_result)
        self.assertIn('timestamp', parsed_result)


class TestAgentFactory(unittest.TestCase):
    """Unit tests for agent factory"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_config_loader = Mock()
        self.mock_config_loader.load_agents_config.return_value = {
            'orchestrator': {
                'role': 'System Orchestrator',
                'goal': 'Coordinate system operations',
                'backstory': 'Expert in system coordination',
                'tools': ['system_monitor', 'memory_writer']
            },
            'analysis': {
                'role': 'System Analyst', 
                'goal': 'Analyze system performance',
                'backstory': 'Expert in system analysis',
                'tools': ['system_monitor', 'get_alerts']
            }
        }
    
    def test_agent_factory_initialization(self):
        """Test agent factory initialization"""
        from orchestrator.agent_factory import AgentFactory
        
        factory = AgentFactory(self.mock_config_loader)
        
        self.assertEqual(factory.config_loader, self.mock_config_loader)
        self.assertIsInstance(factory._agent_cache, dict)
        self.assertIsInstance(factory._tools_registry, dict)
        
        # Check that functional tools are registered
        self.assertIn('system_monitor', factory._tools_registry)
        self.assertIn('memory_writer', factory._tools_registry)
    
    def test_setup_functional_tools(self):
        """Test functional tools setup"""
        from orchestrator.agent_factory import AgentFactory
        
        factory = AgentFactory(self.mock_config_loader)
        tools_registry = factory._tools_registry
        
        # Verify essential tools are present
        expected_tools = [
            'system_monitor', 'memory_writer', 'prd_parser', 'task_decomposer',
            'monitor_crew', 'get_alerts', 'write_crew_memory', 'search_memory'
        ]
        
        for tool in expected_tools:
            self.assertIn(tool, tools_registry)
            self.assertIsNotNone(tools_registry[tool])
    
    @patch('orchestrator.agent_factory.Agent')
    def test_create_agent_from_config(self, mock_agent_class):
        """Test creating agent from configuration"""
        from orchestrator.agent_factory import AgentFactory
        
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        factory = AgentFactory(self.mock_config_loader)
        
        # Test creating orchestrator agent
        agent_config = {
            'role': 'Test Orchestrator',
            'goal': 'Test coordination',
            'backstory': 'Test backstory',
            'tools': ['system_monitor']
        }
        
        result = factory._create_agent_from_config('test_orchestrator', agent_config)
        
        self.assertEqual(result, mock_agent)
        mock_agent_class.assert_called_once()
        
        # Verify the agent was created with correct parameters
        call_kwargs = mock_agent_class.call_args.kwargs
        self.assertEqual(call_kwargs['role'], 'Test Orchestrator')
        self.assertEqual(call_kwargs['goal'], 'Test coordination')
        self.assertEqual(call_kwargs['backstory'], 'Test backstory')
    
    @patch('orchestrator.agent_factory.Agent')
    def test_agent_caching(self, mock_agent_class):
        """Test agent caching mechanism"""
        from orchestrator.agent_factory import AgentFactory
        
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        factory = AgentFactory(self.mock_config_loader)
        
        # Create same agent twice
        agent1 = factory.create_orchestrator_agent()
        agent2 = factory.create_orchestrator_agent()
        
        # Should return cached agent second time
        self.assertEqual(agent1, agent2)
        # Agent constructor should only be called once due to caching
        self.assertEqual(mock_agent_class.call_count, 1)


class TestOrchestratorCrew(unittest.TestCase):
    """Unit tests for orchestrator crew"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_config_loader = Mock()
        self.mock_agent_factory = Mock()
        
        # Mock agents
        self.mock_orchestrator_agent = Mock()
        self.mock_analysis_agent = Mock()
        self.mock_planning_agent = Mock()
        
        self.mock_agent_factory.create_orchestrator_agent.return_value = self.mock_orchestrator_agent
        self.mock_agent_factory.create_analysis_agent.return_value = self.mock_analysis_agent
        self.mock_agent_factory.create_planning_agent.return_value = self.mock_planning_agent
    
    def test_orchestrator_crew_initialization(self):
        """Test orchestrator crew initialization"""
        from crews.orchestrator.orchestrator_crew import OrchestratorCrew
        
        crew = OrchestratorCrew(self.mock_config_loader, self.mock_agent_factory)
        
        self.assertEqual(crew.config_loader, self.mock_config_loader)
        self.assertEqual(crew.agent_factory, self.mock_agent_factory)
        self.assertIsInstance(crew.system_status, dict)
        self.assertIsInstance(crew.crew_health, dict)
        self.assertIsInstance(crew.task_queue, list)
    
    @patch('crews.orchestrator.orchestrator_crew.OrchestratorCrew._setup_crew_monitoring')
    @patch('crews.orchestrator.orchestrator_crew.OrchestratorCrew._setup_performance_tracking')
    @patch('crews.orchestrator.orchestrator_crew.OrchestratorCrew._setup_task_queue_management')
    def test_initialize_system_awareness(self, mock_task_queue, mock_performance, mock_monitoring):
        """Test system awareness initialization"""
        from crews.orchestrator.orchestrator_crew import OrchestratorCrew
        
        # Mock the setup methods to avoid import issues
        mock_monitoring.return_value = True
        mock_performance.return_value = True
        mock_task_queue.return_value = True
        
        crew = OrchestratorCrew(self.mock_config_loader, self.mock_agent_factory)
        
        result = crew.initialize_system_awareness()
        
        self.assertTrue(result)
        # _setup_crew_monitoring is called during __init__ and again in initialize_system_awareness
        self.assertEqual(mock_monitoring.call_count, 2)
        self.assertEqual(mock_performance.call_count, 2) 
        self.assertEqual(mock_task_queue.call_count, 2)
    
    def test_crew_properties(self):
        """Test crew properties and state management"""
        from crews.orchestrator.orchestrator_crew import OrchestratorCrew
        
        crew = OrchestratorCrew(self.mock_config_loader, self.mock_agent_factory)
        
        # Test initial state
        self.assertEqual(len(crew.task_queue), 0)
        self.assertEqual(len(crew.system_status), 0)
        self.assertEqual(len(crew.crew_health), 0)
        
        # Test adding to task queue
        crew.task_queue.append({"task_id": "test_task", "priority": "high"})
        self.assertEqual(len(crew.task_queue), 1)
        
        # Test system status updates
        crew.system_status["component_1"] = "operational"
        self.assertEqual(crew.system_status["component_1"], "operational")


if __name__ == "__main__":
    # Run async tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])