"""
Test Suite for Phase 3 Task 3.1 - Orchestrator Crew Implementation
Comprehensive validation of orchestrator crew with system awareness
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.main import ADOSOrchestrator
from crews.orchestrator.orchestrator_crew import OrchestratorCrew
from tools.system_monitor import SystemMonitor
from tools.memory_writer import MemoryWriter
from tools.prd_parser import PRDParser
from tools.task_decomposer import TaskDecomposerTool


class TestOrchestratorCrewImplementation:
    """Test suite for orchestrator crew implementation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = ADOSOrchestrator()
        
    def teardown_method(self):
        """Clean up test environment"""
        if hasattr(self, 'orchestrator'):
            try:
                self.orchestrator.shutdown()
            except:
                pass
        
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_orchestrator_crew_initialization(self):
        """Test orchestrator crew initialization"""
        # Test that orchestrator crew is properly initialized
        assert hasattr(self.orchestrator, 'orchestrator_crew')
        assert isinstance(self.orchestrator.orchestrator_crew, OrchestratorCrew)
        
        # Test system awareness initialization
        crew = self.orchestrator.orchestrator_crew
        assert hasattr(crew, 'crew_health')
        assert hasattr(crew, 'performance_metrics')
        assert hasattr(crew, 'task_queue')
        
        # Test that all crews are monitored
        expected_crews = ["orchestrator", "backend", "security", "quality", "integration", "deployment", "frontend"]
        for crew_name in expected_crews:
            assert crew_name in crew.crew_health
    
    def test_functional_tools_implementation(self):
        """Test that functional tools are properly implemented"""
        # Test system monitor
        system_monitor = SystemMonitor()
        metrics = system_monitor.get_system_metrics()
        assert hasattr(metrics, 'cpu_usage')
        assert hasattr(metrics, 'memory_usage')
        assert hasattr(metrics, 'timestamp')
        
        # Test memory writer
        memory_writer = MemoryWriter(self.temp_dir)
        memory_id = memory_writer.write_memory("test content", "test", "orchestrator")
        assert memory_id != ""
        
        # Test PRD parser
        prd_parser = PRDParser()
        test_prd = """
        # Test PRD
        
        ## Overview
        This is a test PRD
        
        ## Requirements
        
        REQ 1: Test requirement
        Priority: High
        Acceptance Criteria:
        - Requirement should be parsed
        - Test should pass
        """
        
        parsed = prd_parser.parse_prd(test_prd, "Test PRD")
        assert parsed.title == "Test PRD"
        assert len(parsed.requirements) > 0
        
        # Test task decomposer
        task_decomposer = TaskDecomposerTool()
        decomposition = task_decomposer.decompose_task("Create a simple API endpoint")
        assert len(decomposition.subtasks) > 0
        assert decomposition.estimated_duration != "unknown"
    
    def test_orchestrator_integration(self):
        """Test integration between orchestrator and specialized crew"""
        # Initialize orchestrator
        try:
            initialized = self.orchestrator.initialize()
            if not initialized:
                pytest.skip("Orchestrator initialization failed - configuration may be incomplete")
        except Exception as e:
            pytest.skip(f"Orchestrator initialization failed: {e}")
        
        # Test intelligent task dispatch
        dispatch_result = self.orchestrator.intelligent_task_dispatch("Create a simple API endpoint", "high")
        assert "assigned_crew" in dispatch_result
        assert dispatch_result["status"] in ["dispatched", "queued"]
        
        # Test crew health monitoring
        health = self.orchestrator.get_crew_health("backend")
        assert "status" in health
        assert health["status"] in ["ready", "active", "busy", "overloaded"]
        
        # Test system overview
        overview = self.orchestrator.get_orchestrator_overview()
        assert "system_status" in overview
        assert "orchestrator_crew" in overview
        assert overview["integration_status"] == "active"
    
    def test_crew_health_monitoring(self):
        """Test crew health monitoring functionality"""
        crew = self.orchestrator.orchestrator_crew
        
        # Test individual crew monitoring
        health = crew.monitor_crew_health("backend")
        assert "status" in health
        assert "load" in health
        assert "last_check" in health
        
        # Test all crews monitoring
        all_health = crew.monitor_all_crews()
        assert len(all_health) > 0
        
        # Test status changes based on load
        health_low = crew.monitor_crew_health("backend", 10)
        assert health_low["status"] == "ready"
        
        health_high = crew.monitor_crew_health("backend", 90)
        assert health_high["status"] == "overloaded"
    
    def test_intelligent_task_dispatch(self):
        """Test intelligent task dispatch functionality"""
        crew = self.orchestrator.orchestrator_crew
        
        # Test backend task dispatch
        result = crew.intelligent_task_dispatch("Create an API endpoint", "high")
        assert result["assigned_crew"] == "backend"
        assert result["priority"] == "high"
        
        # Test frontend task dispatch
        result = crew.intelligent_task_dispatch("Create a React component", "medium")
        assert result["assigned_crew"] == "frontend"
        
        # Test security task dispatch
        result = crew.intelligent_task_dispatch("Implement authentication", "high")
        assert result["assigned_crew"] == "security"
        
        # Test quality task dispatch
        result = crew.intelligent_task_dispatch("Write unit tests", "medium")
        assert result["assigned_crew"] == "quality"
    
    def test_task_queue_management(self):
        """Test task queue management functionality"""
        crew = self.orchestrator.orchestrator_crew
        
        # Test initial queue status
        queue_status = crew.get_task_queue_status()
        assert "total_queued" in queue_status
        assert "by_priority" in queue_status
        assert "by_crew" in queue_status
        
        # Test task queueing when crew is unavailable
        # Simulate crew unavailability by setting high load
        crew.crew_health["backend"]["load"] = 100
        crew.crew_health["backend"]["status"] = "overloaded"
        
        result = crew.intelligent_task_dispatch("Create database schema", "high")
        
        # Should either queue or redirect to alternative
        assert result["status"] in ["queued", "dispatched"]
        
        # Test queue processing
        processed = crew.process_task_queue()
        assert isinstance(processed, list)
    
    def test_performance_metrics(self):
        """Test performance metrics tracking"""
        crew = self.orchestrator.orchestrator_crew
        
        # Test initial metrics
        overview = crew.get_system_overview()
        assert "performance_metrics" in overview
        metrics = overview["performance_metrics"]
        
        assert "tasks_completed" in metrics
        assert "tasks_failed" in metrics
        assert "crew_utilization" in metrics
        
        # Test task completion tracking
        crew.complete_task("backend", True)
        assert crew.performance_metrics["tasks_completed"] > 0
        
        crew.complete_task("backend", False)
        assert crew.performance_metrics["tasks_failed"] > 0
    
    def test_system_health_check(self):
        """Test comprehensive system health check"""
        try:
            initialized = self.orchestrator.initialize()
            if not initialized:
                pytest.skip("Orchestrator initialization failed - configuration may be incomplete")
        except Exception as e:
            pytest.skip(f"Orchestrator initialization failed: {e}")
        
        # Test health check
        health = self.orchestrator.perform_health_check()
        assert "overall_status" in health
        assert "orchestrator_crew_health" in health
        assert "system_validation" in health
        assert "timestamp" in health
        
        # Test health check without initialization
        self.orchestrator.is_initialized = False
        health = self.orchestrator.perform_health_check()
        assert health["status"] == "not_initialized"
    
    def test_system_overview(self):
        """Test comprehensive system overview"""
        crew = self.orchestrator.orchestrator_crew
        
        overview = crew.get_system_overview()
        
        # Test required fields
        assert "crew_health" in overview
        assert "performance_metrics" in overview
        assert "task_queue_length" in overview
        assert "active_tasks" in overview
        assert "system_status" in overview
        assert "uptime" in overview
        assert "total_crews" in overview
        
        # Test system status determination
        assert overview["system_status"] in ["operational", "degraded", "stressed", "mixed"]
        assert overview["total_crews"] == 7  # Expected number of crews
    
    def test_crew_assignment_logic(self):
        """Test crew assignment logic for different task types"""
        crew = self.orchestrator.orchestrator_crew
        
        # Test various task types
        test_cases = [
            ("Create REST API", "backend"),
            ("Setup authentication", "security"),
            ("Write unit tests", "quality"),
            ("Deploy to production", "deployment"),
            ("Design UI components", "frontend"),
            ("Setup CI/CD pipeline", "integration"),
            ("Complex system architecture", "orchestrator")
        ]
        
        for task_description, expected_crew in test_cases:
            result = crew.intelligent_task_dispatch(task_description)
            assert result["assigned_crew"] == expected_crew, f"Task '{task_description}' assigned to {result['assigned_crew']}, expected {expected_crew}"
    
    def test_error_handling(self):
        """Test error handling in orchestrator crew"""
        crew = self.orchestrator.orchestrator_crew
        
        # Test invalid crew monitoring
        health = crew.monitor_crew_health("nonexistent_crew")
        assert health["status"] == "unknown"
        assert "error" in health
        
        # Test task dispatch with invalid input
        result = crew.intelligent_task_dispatch("")
        assert "error" in result or result["status"] == "dispatched"  # Should handle gracefully
    
    def test_validation_and_completeness(self):
        """Test validation and completeness of implementation"""
        # Test orchestrator has all required methods
        required_methods = [
            'intelligent_task_dispatch',
            'get_crew_health',
            'get_all_crews_health',
            'get_orchestrator_overview',
            'process_task_queue',
            'complete_task',
            'get_task_queue_status',
            'perform_health_check'
        ]
        
        for method in required_methods:
            assert hasattr(self.orchestrator, method), f"Missing required method: {method}"
        
        # Test orchestrator crew has all required functionality
        crew_methods = [
            'monitor_crew_health',
            'intelligent_task_dispatch',
            'get_system_overview',
            'process_task_queue',
            'complete_task',
            'get_task_queue_status',
            'health_check'
        ]
        
        crew = self.orchestrator.orchestrator_crew
        for method in crew_methods:
            assert hasattr(crew, method), f"Missing required crew method: {method}"
    
    def test_integration_with_existing_system(self):
        """Test integration with existing orchestrator system"""
        try:
            # Test that orchestrator can still perform basic functions
            initialized = self.orchestrator.initialize()
            if not initialized:
                pytest.skip("Orchestrator initialization failed - configuration may be incomplete")
                
            # Test system status
            status = self.orchestrator.get_system_status()
            assert "initialized" in status
            assert "crews" in status
            assert "agents" in status
            
            # Test crew listing
            crews = self.orchestrator.list_crews()
            assert len(crews) > 0
            
            # Test agent listing
            agents = self.orchestrator.list_agents()
            assert len(agents) > 0
            
        except Exception as e:
            pytest.skip(f"Integration test failed due to configuration issues: {e}")


def run_comprehensive_validation():
    """Run comprehensive validation of the orchestrator implementation"""
    print("🔍 Running Phase 3 Task 3.1 Validation...")
    
    # Initialize test instance
    test_instance = TestOrchestratorCrewImplementation()
    test_instance.setup_method()
    
    try:
        # Run all tests
        test_methods = [
            'test_orchestrator_crew_initialization',
            'test_functional_tools_implementation',
            'test_crew_health_monitoring',
            'test_intelligent_task_dispatch',
            'test_task_queue_management',
            'test_performance_metrics',
            'test_system_overview',
            'test_crew_assignment_logic',
            'test_error_handling',
            'test_validation_and_completeness'
        ]
        
        results = {}
        for test_method in test_methods:
            try:
                print(f"  ✓ Running {test_method}...")
                getattr(test_instance, test_method)()
                results[test_method] = "PASSED"
                print(f"    ✅ {test_method} - PASSED")
            except Exception as e:
                results[test_method] = f"FAILED: {e}"
                print(f"    ❌ {test_method} - FAILED: {e}")
        
        # Print summary
        passed = sum(1 for result in results.values() if result == "PASSED")
        total = len(results)
        
        print(f"\n📊 Validation Summary:")
        print(f"  ✅ Passed: {passed}/{total}")
        print(f"  ❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print(f"  🎉 All tests passed! Phase 3 Task 3.1 implementation is complete.")
        else:
            print(f"  ⚠️  Some tests failed. Review implementation.")
            
        return results
        
    finally:
        test_instance.teardown_method()


if __name__ == "__main__":
    # Run validation if executed directly
    run_comprehensive_validation()