#!/usr/bin/env python3
"""
Comprehensive Test Suite for ADOS Phases 1-3.1
Tests all functionality from core infrastructure through orchestrator crew implementation.
"""

import asyncio
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import pytest
import subprocess
from dataclasses import dataclass
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "dev-agent-system"))

@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    phase: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ComprehensiveTestRunner:
    """Comprehensive test runner for all ADOS phases."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    async def run_phase_1_tests(self) -> List[TestResult]:
        """Test Phase 1: Core Infrastructure."""
        self.log("=== PHASE 1: CORE INFRASTRUCTURE TESTS ===")
        results = []
        
        # Test 1.1: Configuration System
        result = await self._test_configuration_system()
        results.append(result)
        
        # Test 1.2: Logging Infrastructure
        result = await self._test_logging_infrastructure()
        results.append(result)
        
        # Test 1.3: Base Classes and Types
        result = await self._test_base_classes()
        results.append(result)
        
        # Test 1.4: Workspace Configuration
        result = await self._test_workspace_config()
        results.append(result)
        
        return results
    
    async def run_phase_2_tests(self) -> List[TestResult]:
        """Test Phase 2: Task Decomposition and Crew Management."""
        self.log("=== PHASE 2: TASK DECOMPOSITION AND CREW MANAGEMENT TESTS ===")
        results = []
        
        # Test 2.1: Task Decomposer
        result = await self._test_task_decomposer()
        results.append(result)
        
        # Test 2.2: Memory Coordination
        result = await self._test_memory_coordination()
        results.append(result)
        
        # Test 2.3: Integration Tests
        result = await self._test_phase_2_integration()
        results.append(result)
        
        return results
    
    async def run_phase_3_1_tests(self) -> List[TestResult]:
        """Test Phase 3.1: Orchestrator Crew Implementation."""
        self.log("=== PHASE 3.1: ORCHESTRATOR CREW IMPLEMENTATION TESTS ===")
        results = []
        
        # Test 3.1.1: Orchestrator Crew
        result = await self._test_orchestrator_crew()
        results.append(result)
        
        # Test 3.1.2: Agent Factory
        result = await self._test_agent_factory()
        results.append(result)
        
        # Test 3.1.3: Tool Implementation
        result = await self._test_orchestrator_tools()
        results.append(result)
        
        return results
    
    async def run_integration_tests(self) -> List[TestResult]:
        """Run comprehensive integration tests across all phases."""
        self.log("=== INTEGRATION TESTS ACROSS ALL PHASES ===")
        results = []
        
        # Integration Test 1: End-to-End Workflow
        result = await self._test_end_to_end_workflow()
        results.append(result)
        
        # Integration Test 2: System Health Check
        result = await self._test_system_health()
        results.append(result)
        
        return results
    
    async def _test_configuration_system(self) -> TestResult:
        """Test the configuration system."""
        start_time = time.time()
        try:
            # Import and test configuration
            from dev_agent_system.config.config_loader import ConfigLoader
            from dev_agent_system.config.workspace_config import WorkspaceConfig
            
            # Test config loading
            config_loader = ConfigLoader()
            config = config_loader.load_config()
            
            # Validate essential config components
            assert hasattr(config, 'logging'), "Config missing logging section"
            assert hasattr(config, 'crews'), "Config missing crews section"
            
            # Test workspace config
            workspace_config = WorkspaceConfig()
            workspace_path = workspace_config.get_workspace_path()
            assert workspace_path.exists(), "Workspace path does not exist"
            
            duration = time.time() - start_time
            self.log(f"✅ Configuration system test PASSED ({duration:.2f}s)")
            return TestResult("Configuration System", "Phase 1", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Configuration test failed: {str(e)}"
            self.log(f"❌ Configuration system test FAILED: {error_msg}")
            return TestResult("Configuration System", "Phase 1", "FAIL", duration, error_msg)
    
    async def _test_logging_infrastructure(self) -> TestResult:
        """Test the logging infrastructure."""
        start_time = time.time()
        try:
            from dev_agent_system.core.logging_infrastructure import LoggingInfrastructure
            
            # Initialize logging
            logging_infra = LoggingInfrastructure()
            logger = logging_infra.get_logger("test_logger")
            
            # Test logging functionality
            logger.info("Test log message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            
            duration = time.time() - start_time
            self.log(f"✅ Logging infrastructure test PASSED ({duration:.2f}s)")
            return TestResult("Logging Infrastructure", "Phase 1", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Logging test failed: {str(e)}"
            self.log(f"❌ Logging infrastructure test FAILED: {error_msg}")
            return TestResult("Logging Infrastructure", "Phase 1", "FAIL", duration, error_msg)
    
    async def _test_base_classes(self) -> TestResult:
        """Test base classes and types."""
        start_time = time.time()
        try:
            from dev_agent_system.core.types import TaskId, CrewId, AgentId
            from dev_agent_system.core.base_agent import BaseAgent
            
            # Test type creation
            task_id = TaskId("test-task-123")
            crew_id = CrewId("test-crew-456")
            agent_id = AgentId("test-agent-789")
            
            # Validate types
            assert isinstance(task_id, str), "TaskId should be string-like"
            assert isinstance(crew_id, str), "CrewId should be string-like"
            assert isinstance(agent_id, str), "AgentId should be string-like"
            
            duration = time.time() - start_time
            self.log(f"✅ Base classes test PASSED ({duration:.2f}s)")
            return TestResult("Base Classes", "Phase 1", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Base classes test failed: {str(e)}"
            self.log(f"❌ Base classes test FAILED: {error_msg}")
            return TestResult("Base Classes", "Phase 1", "FAIL", duration, error_msg)
    
    async def _test_workspace_config(self) -> TestResult:
        """Test workspace configuration."""
        start_time = time.time()
        try:
            from dev_agent_system.config.workspace_config import WorkspaceConfig
            
            workspace_config = WorkspaceConfig()
            
            # Test workspace path
            workspace_path = workspace_config.get_workspace_path()
            assert workspace_path.exists(), "Workspace path should exist"
            
            # Test config file paths
            config_file = workspace_config.get_config_file_path()
            assert config_file.parent.exists(), "Config directory should exist"
            
            duration = time.time() - start_time
            self.log(f"✅ Workspace configuration test PASSED ({duration:.2f}s)")
            return TestResult("Workspace Configuration", "Phase 1", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Workspace config test failed: {str(e)}"
            self.log(f"❌ Workspace configuration test FAILED: {error_msg}")
            return TestResult("Workspace Configuration", "Phase 1", "FAIL", duration, error_msg)
    
    async def _test_task_decomposer(self) -> TestResult:
        """Test the task decomposer functionality."""
        start_time = time.time()
        try:
            from dev_agent_system.orchestrator.task_decomposer import TaskDecomposer
            from dev_agent_system.core.types import TaskId
            
            # Initialize task decomposer
            decomposer = TaskDecomposer()
            
            # Test task decomposition
            test_task = "Analyze user requirements and create development plan"
            task_id = TaskId("test-decompose-001")
            
            result = await decomposer.decompose_task(test_task, task_id)
            
            # Validate result structure
            assert 'subtasks' in result, "Result should contain subtasks"
            assert 'dependencies' in result, "Result should contain dependencies"
            assert 'crew_assignments' in result, "Result should contain crew assignments"
            assert len(result['subtasks']) > 0, "Should have at least one subtask"
            
            duration = time.time() - start_time
            self.log(f"✅ Task decomposer test PASSED ({duration:.2f}s)")
            return TestResult("Task Decomposer", "Phase 2", "PASS", duration, 
                            details={"subtasks_count": len(result['subtasks'])})
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Task decomposer test failed: {str(e)}"
            self.log(f"❌ Task decomposer test FAILED: {error_msg}")
            return TestResult("Task Decomposer", "Phase 2", "FAIL", duration, error_msg)
    
    async def _test_memory_coordination(self) -> TestResult:
        """Test memory coordination functionality."""
        start_time = time.time()
        try:
            from dev_agent_system.memory.memory_coordinator import MemoryCoordinator
            
            # Initialize memory coordinator
            memory_coordinator = MemoryCoordinator()
            
            # Test memory operations
            test_data = {"test_key": "test_value", "timestamp": datetime.now().isoformat()}
            
            # Store and retrieve
            await memory_coordinator.store_data("test_session", "test_data", test_data)
            retrieved_data = await memory_coordinator.retrieve_data("test_session", "test_data")
            
            assert retrieved_data == test_data, "Retrieved data should match stored data"
            
            duration = time.time() - start_time
            self.log(f"✅ Memory coordination test PASSED ({duration:.2f}s)")
            return TestResult("Memory Coordination", "Phase 2", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Memory coordination test failed: {str(e)}"
            self.log(f"❌ Memory coordination test FAILED: {error_msg}")
            return TestResult("Memory Coordination", "Phase 2", "FAIL", duration, error_msg)
    
    async def _test_phase_2_integration(self) -> TestResult:
        """Test Phase 2 integration."""
        start_time = time.time()
        try:
            from dev_agent_system.orchestrator.ados_orchestrator import ADOSOrchestrator
            
            # Initialize orchestrator
            orchestrator = ADOSOrchestrator()
            
            # Test decompose and execute
            test_task = "Create a simple test plan"
            result = await orchestrator.decompose_and_execute_task(test_task)
            
            assert 'execution_id' in result, "Result should contain execution_id"
            assert 'status' in result, "Result should contain status"
            
            duration = time.time() - start_time
            self.log(f"✅ Phase 2 integration test PASSED ({duration:.2f}s)")
            return TestResult("Phase 2 Integration", "Phase 2", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Phase 2 integration test failed: {str(e)}"
            self.log(f"❌ Phase 2 integration test FAILED: {error_msg}")
            return TestResult("Phase 2 Integration", "Phase 2", "FAIL", duration, error_msg)
    
    async def _test_orchestrator_crew(self) -> TestResult:
        """Test orchestrator crew implementation."""
        start_time = time.time()
        try:
            from dev_agent_system.crews.orchestrator_crew import OrchestratorCrew
            
            # Initialize orchestrator crew
            crew = OrchestratorCrew()
            
            # Test crew initialization
            assert crew.agents is not None, "Crew should have agents"
            assert len(crew.agents) > 0, "Crew should have at least one agent"
            
            # Test crew execution
            test_task = "Coordinate a simple task execution"
            result = await crew.kickoff({"task": test_task})
            
            assert result is not None, "Crew execution should return a result"
            
            duration = time.time() - start_time
            self.log(f"✅ Orchestrator crew test PASSED ({duration:.2f}s)")
            return TestResult("Orchestrator Crew", "Phase 3.1", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Orchestrator crew test failed: {str(e)}"
            self.log(f"❌ Orchestrator crew test FAILED: {error_msg}")
            return TestResult("Orchestrator Crew", "Phase 3.1", "FAIL", duration, error_msg)
    
    async def _test_agent_factory(self) -> TestResult:
        """Test agent factory functionality."""
        start_time = time.time()
        try:
            from dev_agent_system.agents.agent_factory import AgentFactory
            
            # Initialize agent factory
            factory = AgentFactory()
            
            # Test agent creation
            agent = factory.create_orchestrator_agent()
            assert agent is not None, "Should be able to create orchestrator agent"
            
            analysis_agent = factory.create_analysis_agent()
            assert analysis_agent is not None, "Should be able to create analysis agent"
            
            duration = time.time() - start_time
            self.log(f"✅ Agent factory test PASSED ({duration:.2f}s)")
            return TestResult("Agent Factory", "Phase 3.1", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Agent factory test failed: {str(e)}"
            self.log(f"❌ Agent factory test FAILED: {error_msg}")
            return TestResult("Agent Factory", "Phase 3.1", "FAIL", duration, error_msg)
    
    async def _test_orchestrator_tools(self) -> TestResult:
        """Test orchestrator tools implementation."""
        start_time = time.time()
        try:
            from dev_agent_system.tools.orchestrator_tools import (
                get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress
            )
            
            # Test get_decomposed_tasks
            tasks_result = await get_decomposed_tasks("test task")
            assert isinstance(tasks_result, str), "get_decomposed_tasks should return string"
            
            # Test allocate_task_to_crew
            allocation_result = await allocate_task_to_crew("test task", "test crew")
            assert isinstance(allocation_result, str), "allocate_task_to_crew should return string"
            
            # Test monitor_crew_progress
            progress_result = await monitor_crew_progress("test crew")
            assert isinstance(progress_result, str), "monitor_crew_progress should return string"
            
            duration = time.time() - start_time
            self.log(f"✅ Orchestrator tools test PASSED ({duration:.2f}s)")
            return TestResult("Orchestrator Tools", "Phase 3.1", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Orchestrator tools test failed: {str(e)}"
            self.log(f"❌ Orchestrator tools test FAILED: {error_msg}")
            return TestResult("Orchestrator Tools", "Phase 3.1", "FAIL", duration, error_msg)
    
    async def _test_end_to_end_workflow(self) -> TestResult:
        """Test end-to-end workflow across all phases."""
        start_time = time.time()
        try:
            from dev_agent_system.orchestrator.ados_orchestrator import ADOSOrchestrator
            
            # Full workflow test
            orchestrator = ADOSOrchestrator()
            
            # Test complex task
            complex_task = "Analyze requirements, decompose into subtasks, and coordinate execution"
            result = await orchestrator.decompose_and_execute_task(complex_task)
            
            assert 'execution_id' in result, "Should have execution ID"
            assert 'status' in result, "Should have status"
            
            duration = time.time() - start_time
            self.log(f"✅ End-to-end workflow test PASSED ({duration:.2f}s)")
            return TestResult("End-to-End Workflow", "Integration", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"End-to-end workflow test failed: {str(e)}"
            self.log(f"❌ End-to-end workflow test FAILED: {error_msg}")
            return TestResult("End-to-End Workflow", "Integration", "FAIL", duration, error_msg)
    
    async def _test_system_health(self) -> TestResult:
        """Test overall system health."""
        start_time = time.time()
        try:
            # Check if all core modules can be imported
            imports_to_test = [
                "dev_agent_system.config.config_loader",
                "dev_agent_system.core.logging_infrastructure",
                "dev_agent_system.orchestrator.task_decomposer",
                "dev_agent_system.orchestrator.ados_orchestrator",
                "dev_agent_system.crews.orchestrator_crew",
                "dev_agent_system.agents.agent_factory",
                "dev_agent_system.tools.orchestrator_tools",
                "dev_agent_system.memory.memory_coordinator"
            ]
            
            for module_name in imports_to_test:
                try:
                    __import__(module_name)
                except ImportError as e:
                    raise ImportError(f"Failed to import {module_name}: {e}")
            
            duration = time.time() - start_time
            self.log(f"✅ System health test PASSED ({duration:.2f}s)")
            return TestResult("System Health", "Integration", "PASS", duration, 
                            details={"modules_tested": len(imports_to_test)})
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"System health test failed: {str(e)}"
            self.log(f"❌ System health test FAILED: {error_msg}")
            return TestResult("System Health", "Integration", "FAIL", duration, error_msg)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_duration = time.time() - self.start_time
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        skipped_tests = len([r for r in self.results if r.status == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group by phase
        phase_results = {}
        for result in self.results:
            if result.phase not in phase_results:
                phase_results[result.phase] = []
            phase_results[result.phase].append(result)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_duration": f"{total_duration:.2f}s",
                "timestamp": datetime.now().isoformat()
            },
            "phase_results": phase_results,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "phase": r.phase,
                    "status": r.status,
                    "duration": f"{r.duration:.2f}s",
                    "error_message": r.error_message,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        return report
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive report."""
        self.log("🚀 Starting ADOS Comprehensive Test Suite (Phases 1-3.1)")
        self.log(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run Phase 1 tests
            phase_1_results = await self.run_phase_1_tests()
            self.results.extend(phase_1_results)
            
            # Run Phase 2 tests
            phase_2_results = await self.run_phase_2_tests()
            self.results.extend(phase_2_results)
            
            # Run Phase 3.1 tests
            phase_3_1_results = await self.run_phase_3_1_tests()
            self.results.extend(phase_3_1_results)
            
            # Run integration tests
            integration_results = await self.run_integration_tests()
            self.results.extend(integration_results)
            
        except Exception as e:
            self.log(f"❌ Test suite failed with error: {e}")
            traceback.print_exc()
        
        # Generate and return report
        report = self.generate_report()
        
        self.log("📊 Test Results Summary:")
        self.log(f"   Total Tests: {report['summary']['total_tests']}")
        self.log(f"   Passed: {report['summary']['passed']}")
        self.log(f"   Failed: {report['summary']['failed']}")
        self.log(f"   Success Rate: {report['summary']['success_rate']}")
        self.log(f"   Duration: {report['summary']['total_duration']}")
        
        return report

async def main():
    """Main test runner function."""
    runner = ComprehensiveTestRunner()
    report = await runner.run_all_tests()
    
    # Save report to file
    report_file = Path(__file__).parent / "test_report_phases_1_to_3_1.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    runner.log(f"📄 Full test report saved to: {report_file}")
    
    # Exit with appropriate code
    failed_count = report['summary']['failed']
    sys.exit(0 if failed_count == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())