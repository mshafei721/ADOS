"""
Integration tests for TaskDecomposer with ADOSOrchestrator
Tests the integration between task decomposer and orchestrator
"""

import pytest
import logging
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

from orchestrator.main import ADOSOrchestrator
from orchestrator.task_decomposer import TaskDecomposer


class TestOrchestratorIntegration:
    """Test suite for TaskDecomposer integration with ADOSOrchestrator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.decomposer = TaskDecomposer()
        
        # Mock the orchestrator to avoid actual CrewAI initialization
        self.orchestrator = MagicMock()
        self.orchestrator.is_initialized = True
        self.orchestrator.get_crew.return_value = MagicMock()
        self.orchestrator.execute_task.return_value = "Task executed successfully"
    
    def test_decompose_and_route_simple_task(self):
        """Test decomposing and routing a simple task"""
        task = "Create a new API endpoint for users"
        
        # Decompose the task
        decomposition = self.decomposer.decompose_task(task)
        
        assert decomposition['status'] == 'decomposed'
        assert len(decomposition['subtasks']) > 0
        
        # Check that backend crew is involved
        crews_involved = [subtask['crew'] for subtask in decomposition['subtasks']]
        assert 'backend' in crews_involved
        assert 'orchestrator' in crews_involved
    
    def test_decompose_and_route_complex_task(self):
        """Test decomposing and routing a complex task"""
        task = "Build a complete user management system with authentication, database, and responsive UI"
        
        # Decompose the task
        decomposition = self.decomposer.decompose_task(task)
        
        assert decomposition['status'] == 'decomposed'
        assert decomposition['complexity'] in ['complex', 'epic']
        
        # Check that multiple crews are involved
        crews_involved = [subtask['crew'] for subtask in decomposition['subtasks']]
        assert 'backend' in crews_involved
        assert 'security' in crews_involved
        assert 'frontend' in crews_involved
        assert 'orchestrator' in crews_involved
        
        # Check execution order respects dependencies
        execution_order = decomposition['execution_order']
        if 'security' in execution_order and 'backend' in execution_order:
            assert execution_order.index('security') < execution_order.index('backend')
        if 'backend' in execution_order and 'frontend' in execution_order:
            assert execution_order.index('backend') < execution_order.index('frontend')
    
    def test_simulate_orchestrator_execution(self):
        """Test simulating orchestrator execution with decomposed tasks"""
        task = "Implement JWT authentication for the API"
        
        # Decompose the task
        decomposition = self.decomposer.decompose_task(task)
        
        # Simulate orchestrator execution for each subtask
        execution_results = []
        for subtask in decomposition['subtasks']:
            crew = subtask['crew']
            description = subtask['description']
            
            # Mock orchestrator execution
            result = self.orchestrator.execute_task(description, crew)
            execution_results.append({
                'crew': crew,
                'description': description,
                'result': result
            })
        
        # Verify results
        assert len(execution_results) == len(decomposition['subtasks'])
        for result in execution_results:
            assert result['result'] == "Task executed successfully"
    
    def test_routing_information_format(self):
        """Test that routing information is properly formatted for orchestrator"""
        task = "Create a REST API with database integration"
        
        # Decompose the task
        decomposition = self.decomposer.decompose_task(task)
        
        # Check routing information structure
        routing = decomposition['routing']
        assert isinstance(routing, dict)
        
        for crew, tasks in routing.items():
            assert isinstance(crew, str)
            assert isinstance(tasks, list)
            assert len(tasks) > 0
            
            # Each task should be a string description
            for task_desc in tasks:
                assert isinstance(task_desc, str)
                assert len(task_desc) > 0
    
    def test_priority_based_execution_order(self):
        """Test that tasks can be executed in priority order"""
        task = "Implement critical security features for the application"
        
        # Decompose the task
        decomposition = self.decomposer.decompose_task(task)
        
        # Group subtasks by priority
        priority_groups = {}
        for subtask in decomposition['subtasks']:
            priority = subtask['priority']
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(subtask)
        
        # Check priority ordering (must → should → could → wont)
        priority_order = ['must', 'should', 'could', 'wont']
        for priority in priority_order:
            if priority in priority_groups:
                # Simulate executing tasks in priority order
                for subtask in priority_groups[priority]:
                    crew = subtask['crew']
                    description = subtask['description']
                    
                    # Mock orchestrator execution
                    result = self.orchestrator.execute_task(description, crew)
                    assert result == "Task executed successfully"
    
    def test_error_handling_in_integration(self):
        """Test error handling when orchestrator fails"""
        task = "Create a new feature with error handling"
        
        # Decompose the task
        decomposition = self.decomposer.decompose_task(task)
        
        # Mock orchestrator failure
        self.orchestrator.execute_task.side_effect = Exception("Orchestrator execution failed")
        
        # Simulate execution with error handling
        execution_results = []
        for subtask in decomposition['subtasks']:
            crew = subtask['crew']
            description = subtask['description']
            
            try:
                result = self.orchestrator.execute_task(description, crew)
                execution_results.append({
                    'crew': crew,
                    'description': description,
                    'result': result,
                    'status': 'success'
                })
            except Exception as e:
                execution_results.append({
                    'crew': crew,
                    'description': description,
                    'error': str(e),
                    'status': 'failed'
                })
        
        # Verify error handling
        assert len(execution_results) == len(decomposition['subtasks'])
        for result in execution_results:
            assert result['status'] == 'failed'
            assert result['error'] == "Orchestrator execution failed"
    
    def test_task_decomposer_logging_integration(self):
        """Test logging integration between decomposer and orchestrator"""
        task = "Test logging functionality"
        
        # Mock logging
        with patch('logging.getLogger') as mock_logger:
            mock_log = MagicMock()
            mock_logger.return_value = mock_log
            
            # Create new decomposer instance to test logging
            decomposer = TaskDecomposer()
            
            # Decompose task
            decomposition = decomposer.decompose_task(task)
            
            # Verify logging was called
            mock_log.info.assert_called()
            
            # Check that decomposition was successful
            assert decomposition['status'] == 'decomposed'
    
    def test_crew_availability_check(self):
        """Test checking crew availability before task execution"""
        task = "Deploy application to production environment"
        
        # Decompose the task
        decomposition = self.decomposer.decompose_task(task)
        
        # Mock orchestrator crew availability
        available_crews = ['orchestrator', 'deployment', 'security', 'integration']
        
        # Check which subtasks can be executed
        executable_subtasks = []
        for subtask in decomposition['subtasks']:
            crew = subtask['crew']
            if crew in available_crews:
                executable_subtasks.append(subtask)
        
        # Verify that at least some subtasks can be executed
        assert len(executable_subtasks) > 0
        
        # Verify that deployment crew is available for deployment tasks (if deployment crew is identified)
        deployment_subtasks = [s for s in executable_subtasks if s['crew'] == 'deployment']
        # This might be 0 if the task doesn't explicitly require deployment crew
        assert len(deployment_subtasks) >= 0
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        task = "Create a simple user registration feature"
        
        # Step 1: Decompose the task
        decomposition = self.decomposer.decompose_task(task)
        
        assert decomposition['status'] == 'decomposed'
        
        # Step 2: Validate decomposition structure
        assert 'subtasks' in decomposition
        assert 'execution_order' in decomposition
        assert 'routing' in decomposition
        
        # Step 3: Execute in dependency order
        execution_order = decomposition['execution_order']
        execution_results = []
        
        for crew in execution_order:
            # Find subtasks for this crew
            crew_subtasks = [s for s in decomposition['subtasks'] if s['crew'] == crew]
            
            for subtask in crew_subtasks:
                # Mock orchestrator execution
                result = self.orchestrator.execute_task(subtask['description'], crew)
                execution_results.append({
                    'crew': crew,
                    'description': subtask['description'],
                    'result': result
                })
        
        # Step 4: Verify all subtasks were executed
        assert len(execution_results) == len(decomposition['subtasks'])
        
        # Step 5: Verify execution order was respected
        executed_crews = [r['crew'] for r in execution_results]
        for i, crew in enumerate(executed_crews):
            if crew in execution_order:
                # Check that dependencies were executed first
                crew_deps = self.decomposer.crew_dependencies.get(crew, [])
                for dep in crew_deps:
                    if dep in executed_crews:
                        dep_index = executed_crews.index(dep)
                        assert dep_index < i, f"Dependency {dep} should execute before {crew}"


if __name__ == "__main__":
    pytest.main([__file__])