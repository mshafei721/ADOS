"""
End-to-end test for task decomposition and execution
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from orchestrator.main import ADOSOrchestrator
from orchestrator.task_decomposer import TaskDecomposer


class TestEndToEnd:
    """Test complete end-to-end workflow"""
    
    def test_task_decomposer_integration(self):
        """Test that TaskDecomposer is properly integrated into orchestrator"""
        # Mock configuration loading to avoid file dependencies
        with patch('orchestrator.main.ConfigLoader') as mock_config_loader:
            mock_config_loader.return_value = MagicMock()
            
            # Mock agent and crew factories
            with patch('orchestrator.main.AgentFactory') as mock_agent_factory:
                with patch('orchestrator.main.CrewFactory') as mock_crew_factory:
                    mock_agent_factory.return_value = MagicMock()
                    mock_crew_factory.return_value = MagicMock()
                    
                    # Create orchestrator
                    orchestrator = ADOSOrchestrator()
                    
                    # Check that task decomposer is initialized
                    assert hasattr(orchestrator, 'task_decomposer')
                    assert isinstance(orchestrator.task_decomposer, TaskDecomposer)
    
    def test_decompose_and_execute_task_method(self):
        """Test that decompose_and_execute_task method exists and has correct signature"""
        # Mock configuration loading
        with patch('orchestrator.main.ConfigLoader') as mock_config_loader:
            mock_config_loader.return_value = MagicMock()
            
            # Mock agent and crew factories
            with patch('orchestrator.main.AgentFactory') as mock_agent_factory:
                with patch('orchestrator.main.CrewFactory') as mock_crew_factory:
                    mock_agent_factory.return_value = MagicMock()
                    mock_crew_factory.return_value = MagicMock()
                    
                    # Create orchestrator
                    orchestrator = ADOSOrchestrator()
                    
                    # Check that decompose_and_execute_task method exists
                    assert hasattr(orchestrator, 'decompose_and_execute_task')
                    assert callable(orchestrator.decompose_and_execute_task)
    
    def test_decompose_and_execute_task_not_initialized(self):
        """Test that decompose_and_execute_task raises error when not initialized"""
        # Mock configuration loading
        with patch('orchestrator.main.ConfigLoader') as mock_config_loader:
            mock_config_loader.return_value = MagicMock()
            
            # Mock agent and crew factories
            with patch('orchestrator.main.AgentFactory') as mock_agent_factory:
                with patch('orchestrator.main.CrewFactory') as mock_crew_factory:
                    mock_agent_factory.return_value = MagicMock()
                    mock_crew_factory.return_value = MagicMock()
                    
                    # Create orchestrator (not initialized)
                    orchestrator = ADOSOrchestrator()
                    
                    # Should raise RuntimeError when not initialized
                    with pytest.raises(RuntimeError, match="Orchestrator not initialized"):
                        orchestrator.decompose_and_execute_task("Test task")
    
    def test_task_decomposer_standalone(self):
        """Test that TaskDecomposer works standalone"""
        decomposer = TaskDecomposer()
        
        # Test a simple task decomposition
        result = decomposer.decompose_task("Create a simple API endpoint")
        
        assert result['status'] == 'decomposed'
        assert 'original_task' in result
        assert 'subtasks' in result
        assert 'execution_order' in result
        assert 'routing' in result
        
        # Should identify backend crew for API tasks
        crews_involved = [subtask['crew'] for subtask in result['subtasks']]
        assert 'backend' in crews_involved
        assert 'orchestrator' in crews_involved
    
    def test_task_decomposer_complex_task(self):
        """Test TaskDecomposer with complex task"""
        decomposer = TaskDecomposer()
        
        # Test a complex task decomposition
        result = decomposer.decompose_task("Build a complete user authentication system with database and frontend")
        
        assert result['status'] == 'decomposed'
        assert result['complexity'] in ['complex', 'epic']
        
        # Should identify multiple crews
        crews_involved = [subtask['crew'] for subtask in result['subtasks']]
        assert 'backend' in crews_involved
        assert 'security' in crews_involved
        assert 'frontend' in crews_involved
        
        # Should have proper dependency ordering
        execution_order = result['execution_order']
        if 'security' in execution_order and 'backend' in execution_order:
            assert execution_order.index('security') < execution_order.index('backend')
    
    def test_task_decomposer_error_handling(self):
        """Test TaskDecomposer error handling"""
        decomposer = TaskDecomposer()
        
        # Mock analyze_task_complexity to raise an exception
        with patch.object(decomposer, 'analyze_task_complexity', side_effect=Exception("Test error")):
            result = decomposer.decompose_task("Test task")
            
            assert result['status'] == 'failed'
            assert 'error' in result
            assert result['error'] == "Test error"


if __name__ == "__main__":
    pytest.main([__file__])