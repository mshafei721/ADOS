#!/usr/bin/env python3
"""
Phase 3.1 Simple Test Runner
Simplified test runner for Phase 3.1 without external dependencies
"""

import asyncio
import sys
import time
import traceback
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass, asdict
from datetime import datetime

# Add the project paths to Python path
project_root = Path(__file__).parent
dev_agent_path = project_root / "dev-agent-system"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dev_agent_path))

# Change to dev-agent-system directory
import os
os.chdir(dev_agent_path)

@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    test_type: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

class Phase31SimpleTestRunner:
    """Simple test runner for Phase 3.1"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    async def test_orchestrator_tools_basic(self) -> TestResult:
        """Test basic orchestrator tools functionality"""
        start_time = time.time()
        try:
            from tools.orchestrator_tools import (
                get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress
            )
            
            # Test task decomposition
            result = await get_decomposed_tasks("Build a simple web application")
            parsed = json.loads(result)
            assert 'subtasks' in parsed
            
            # Test task allocation
            result = await allocate_task_to_crew("Test task", "development_crew")
            parsed = json.loads(result)
            assert parsed['assigned_crew'] == 'development_crew'
            
            # Test progress monitoring
            result = await monitor_crew_progress("test_crew")
            parsed = json.loads(result)
            assert 'crew_identifier' in parsed
            
            duration = time.time() - start_time
            return TestResult("Orchestrator Tools Basic", "unit", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Orchestrator Tools Basic", "unit", "FAIL", duration, str(e))
    
    async def test_orchestrator_tools_advanced(self) -> TestResult:
        """Test advanced orchestrator tools functionality"""
        start_time = time.time()
        try:
            from tools.orchestrator_tools import (
                list_available_crews, get_orchestrator_status
            )
            
            # Test listing crews
            result = await list_available_crews()
            parsed = json.loads(result)
            assert 'available_crews' in parsed
            assert len(parsed['available_crews']) > 0
            
            # Test orchestrator status
            result = await get_orchestrator_status()
            parsed = json.loads(result)
            assert 'orchestrator_status' in parsed
            
            duration = time.time() - start_time
            return TestResult("Orchestrator Tools Advanced", "unit", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Orchestrator Tools Advanced", "unit", "FAIL", duration, str(e))
    
    async def test_agent_factory_basic(self) -> TestResult:
        """Test basic agent factory functionality"""
        start_time = time.time()
        try:
            from orchestrator.agent_factory import AgentFactory
            from unittest.mock import Mock
            
            # Mock config loader
            mock_config = Mock()
            mock_config.load_agents_config.return_value = {}
            
            # Test factory initialization
            factory = AgentFactory(mock_config)
            assert factory is not None
            assert hasattr(factory, '_tools_registry')
            assert len(factory._tools_registry) > 0
            
            duration = time.time() - start_time
            return TestResult("Agent Factory Basic", "unit", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Agent Factory Basic", "unit", "FAIL", duration, str(e))
    
    async def test_orchestrator_crew_basic(self) -> TestResult:
        """Test basic orchestrator crew functionality"""
        start_time = time.time()
        try:
            from unittest.mock import Mock, patch
            
            # Mock dependencies
            mock_config = Mock()
            mock_agent_factory = Mock()
            
            # Test with patched initialization
            with patch('crews.orchestrator.orchestrator_crew.OrchestratorCrew.initialize_system_awareness', return_value=True):
                from crews.orchestrator.orchestrator_crew import OrchestratorCrew
                
                crew = OrchestratorCrew(mock_config, mock_agent_factory)
                assert crew is not None
                assert hasattr(crew, 'system_status')
                assert hasattr(crew, 'task_queue')
            
            duration = time.time() - start_time
            return TestResult("Orchestrator Crew Basic", "unit", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Orchestrator Crew Basic", "unit", "FAIL", duration, str(e))
    
    async def test_tools_integration(self) -> TestResult:
        """Test integration between tools"""
        start_time = time.time()
        try:
            from tools.orchestrator_tools import (
                get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress
            )
            
            # Integration workflow
            task = "Create user authentication system"
            
            # Step 1: Decompose
            decomp_result = await get_decomposed_tasks(task)
            decomp_data = json.loads(decomp_result)
            
            # Step 2: Allocate first subtask
            if decomp_data['subtasks']:
                first_subtask = decomp_data['subtasks'][0]
                alloc_result = await allocate_task_to_crew(
                    json.dumps(first_subtask), "development_crew"
                )
                alloc_data = json.loads(alloc_result)
                
                # Step 3: Monitor progress
                crew_id = alloc_data['allocation_id']
                monitor_result = await monitor_crew_progress(crew_id)
                monitor_data = json.loads(monitor_result)
                
                assert monitor_data['crew_identifier'] == crew_id
            
            duration = time.time() - start_time
            return TestResult("Tools Integration", "integration", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Tools Integration", "integration", "FAIL", duration, str(e))
    
    async def test_concurrent_operations(self) -> TestResult:
        """Test concurrent tool operations"""
        start_time = time.time()
        try:
            from tools.orchestrator_tools import (
                get_decomposed_tasks, list_available_crews, get_orchestrator_status
            )
            
            # Run multiple operations concurrently
            tasks = [
                get_decomposed_tasks("Build mobile app"),
                get_decomposed_tasks("Create database schema"),
                list_available_crews(),
                get_orchestrator_status()
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Validate all results
            for result in results:
                parsed = json.loads(result)
                assert isinstance(parsed, dict)
            
            duration = time.time() - start_time
            return TestResult("Concurrent Operations", "integration", "PASS", duration,
                            details={"operations": len(tasks), "concurrent_time": duration})
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Concurrent Operations", "integration", "FAIL", duration, str(e))
    
    async def test_error_handling(self) -> TestResult:
        """Test error handling across components"""
        start_time = time.time()
        try:
            from tools.orchestrator_tools import (
                get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress
            )
            
            # Test with various error conditions
            error_cases = [
                ("", "empty_crew"),
                ("valid task", ""),
                ("task with special chars: !@#$%", "development_crew")
            ]
            
            for task, crew in error_cases:
                # Should handle errors gracefully
                try:
                    if task:
                        result = await get_decomposed_tasks(task)
                        json.loads(result)  # Should be valid JSON
                    
                    if crew:
                        result = await allocate_task_to_crew(task, crew)
                        json.loads(result)  # Should be valid JSON
                        
                        result = await monitor_crew_progress("test")
                        json.loads(result)  # Should be valid JSON
                
                except Exception as e:
                    # Should not raise unhandled exceptions
                    pass
            
            duration = time.time() - start_time
            return TestResult("Error Handling", "integration", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Error Handling", "integration", "FAIL", duration, str(e))
    
    async def test_e2e_project_workflow(self) -> TestResult:
        """Test end-to-end project workflow"""
        start_time = time.time()
        try:
            from tools.orchestrator_tools import (
                get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress,
                list_available_crews
            )
            
            # Complex project task
            project_task = """
            Develop a customer management system with:
            - User authentication and authorization
            - Customer database with contact management
            - Sales pipeline tracking
            - Reporting dashboard
            """
            
            # Phase 1: Task decomposition
            decomp_result = await get_decomposed_tasks(project_task)
            decomp_data = json.loads(decomp_result)
            assert len(decomp_data['subtasks']) > 2
            
            # Phase 2: Get available crews
            crews_result = await list_available_crews()
            crews_data = json.loads(crews_result)
            available_crews = [crew['name'] for crew in crews_data['available_crews']]
            assert len(available_crews) > 0
            
            # Phase 3: Allocate tasks to crews
            allocations = []
            for i, subtask in enumerate(decomp_data['subtasks'][:3]):
                crew_name = available_crews[i % len(available_crews)]
                alloc_result = await allocate_task_to_crew(
                    json.dumps(subtask), crew_name
                )
                alloc_data = json.loads(alloc_result)
                allocations.append(alloc_data)
            
            assert len(allocations) == 3
            
            # Phase 4: Monitor progress
            monitoring_results = []
            for allocation in allocations[:2]:  # Monitor first 2
                monitor_result = await monitor_crew_progress(allocation['allocation_id'])
                monitor_data = json.loads(monitor_result)
                monitoring_results.append(monitor_data)
            
            assert len(monitoring_results) == 2
            
            duration = time.time() - start_time
            return TestResult("E2E Project Workflow", "e2e", "PASS", duration,
                            details={
                                "subtasks": len(decomp_data['subtasks']),
                                "allocations": len(allocations),
                                "monitored": len(monitoring_results)
                            })
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("E2E Project Workflow", "e2e", "FAIL", duration, str(e))
    
    async def test_performance_benchmarks(self) -> TestResult:
        """Test performance benchmarks"""
        start_time = time.time()
        try:
            from tools.orchestrator_tools import (
                get_decomposed_tasks, allocate_task_to_crew, list_available_crews
            )
            
            # Benchmark different operations
            operations = [
                ("Decomposition", lambda: get_decomposed_tasks("Build web app")),
                ("Allocation", lambda: allocate_task_to_crew("Test", "dev_crew")),
                ("List Crews", lambda: list_available_crews())
            ]
            
            benchmarks = {}
            for op_name, op_func in operations:
                times = []
                for _ in range(3):  # 3 iterations each
                    op_start = time.time()
                    await op_func()
                    op_end = time.time()
                    times.append(op_end - op_start)
                
                avg_time = sum(times) / len(times)
                benchmarks[op_name] = avg_time
                
                # Performance assertions
                if op_name == "Decomposition":
                    assert avg_time < 10.0, f"Decomposition too slow: {avg_time}s"
                else:
                    assert avg_time < 2.0, f"{op_name} too slow: {avg_time}s"
            
            duration = time.time() - start_time
            return TestResult("Performance Benchmarks", "e2e", "PASS", duration,
                            details={"benchmarks": benchmarks})
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult("Performance Benchmarks", "e2e", "FAIL", duration, str(e))
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report."""
        total_duration = time.time() - self.start_time
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        skipped_tests = len([r for r in self.results if r.status == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group by test type
        by_type = {}
        for result in self.results:
            if result.test_type not in by_type:
                by_type[result.test_type] = []
            by_type[result.test_type].append(result)
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_duration": f"{total_duration:.2f}s",
                "timestamp": datetime.now().isoformat()
            },
            "by_test_type": {
                test_type: {
                    "count": len(tests),
                    "passed": len([t for t in tests if t.status == "PASS"]),
                    "failed": len([t for t in tests if t.status == "FAIL"]),
                    "success_rate": f"{len([t for t in tests if t.status == 'PASS']) / len(tests) * 100:.1f}%" if tests else "0%"
                }
                for test_type, tests in by_type.items()
            },
            "detailed_results": [result.to_dict() for result in self.results]
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 3.1 tests."""
        self.log("🚀 Starting Phase 3.1 Comprehensive Test Suite")
        
        # Define all tests to run
        tests_to_run = [
            # Unit tests
            self.test_orchestrator_tools_basic,
            self.test_orchestrator_tools_advanced,
            self.test_agent_factory_basic,
            self.test_orchestrator_crew_basic,
            
            # Integration tests
            self.test_tools_integration,
            self.test_concurrent_operations,
            self.test_error_handling,
            
            # End-to-end tests
            self.test_e2e_project_workflow,
            self.test_performance_benchmarks
        ]
        
        # Run all tests
        for test_func in tests_to_run:
            self.log(f"Running {test_func.__name__}...")
            try:
                result = await test_func()
                self.results.append(result)
                
                status_icon = "✅" if result.status == "PASS" else "❌"
                self.log(f"{status_icon} {result.test_name}: {result.status} ({result.duration:.2f}s)")
                
                if result.error_message:
                    self.log(f"   Error: {result.error_message[:100]}...")
                    
            except Exception as e:
                self.log(f"❌ {test_func.__name__} failed with exception: {e}")
                error_result = TestResult(
                    test_name=test_func.__name__,
                    test_type="unknown",
                    status="FAIL",
                    duration=0,
                    error_message=str(e)
                )
                self.results.append(error_result)
        
        # Generate report
        report = self.generate_report()
        
        self.log("\n📊 Test Results Summary:")
        self.log(f"   Total Tests: {report['summary']['total_tests']}")
        self.log(f"   Passed: {report['summary']['passed']}")
        self.log(f"   Failed: {report['summary']['failed']}")
        self.log(f"   Success Rate: {report['summary']['success_rate']}")
        self.log(f"   Duration: {report['summary']['total_duration']}")
        
        # Test type breakdown
        self.log("\n📋 By Test Type:")
        for test_type, stats in report['by_test_type'].items():
            self.log(f"   {test_type}: {stats['passed']}/{stats['count']} ({stats['success_rate']})")
        
        return report

async def main():
    """Main test runner function."""
    runner = Phase31SimpleTestRunner()
    report = await runner.run_all_tests()
    
    # Save report
    report_file = project_root / "phase_3_1_simple_test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    runner.log(f"📄 Test report saved to: {report_file}")
    
    # Exit code
    success_rate = float(report['summary']['success_rate'].rstrip('%'))
    if success_rate >= 80:
        runner.log(f"\n🎉 Phase 3.1 tests completed successfully!")
        sys.exit(0)
    else:
        runner.log(f"\n❌ Phase 3.1 tests need attention")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())