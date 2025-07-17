#!/usr/bin/env python3
"""
Phase 3.1 Comprehensive Test Runner
Runs unit, integration, and end-to-end tests for Phase 3.1 orchestrator crew
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
class TestSuiteResult:
    """Test suite result data structure."""
    suite_name: str
    test_type: str  # "unit", "integration", "e2e"
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    duration: float
    success_rate: float
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

class Phase31TestRunner:
    """Comprehensive test runner for Phase 3.1"""
    
    def __init__(self):
        self.results: List[TestSuiteResult] = []
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    async def run_unit_tests(self) -> TestSuiteResult:
        """Run unit tests for Phase 3.1 components."""
        self.log("🔬 Running Phase 3.1 Unit Tests")
        start_time = time.time()
        
        try:
            # Run pytest on the unit test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "../test_phase_3_1_unit_tests.py", 
                "-v", "--tb=short", "--asyncio-mode=auto"
            ], capture_output=True, text=True, timeout=300)
            
            duration = time.time() - start_time
            
            # Parse results from pytest output
            if result.returncode == 0:
                self.log(f"✅ Unit tests completed successfully ({duration:.2f}s)")
                
                # Parse results from pytest output
                total, passed, failed, skipped = self._parse_pytest_output(result.stdout)
                
            else:
                self.log(f"❌ Unit tests failed ({duration:.2f}s)")
                self.log(f"Exit code: {result.returncode}")
                if result.stderr:
                    self.log(f"Errors: {result.stderr[:500]}")
                
                total, passed, failed, skipped = self._parse_pytest_output(result.stdout)
            
            success_rate = (passed / total * 100) if total > 0 else 0
            
            return TestSuiteResult(
                suite_name="Phase 3.1 Unit Tests",
                test_type="unit",
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                skipped_tests=skipped,
                duration=duration,
                success_rate=success_rate,
                details={
                    "exit_code": result.returncode,
                    "stdout_lines": len(result.stdout.split('\n')) if result.stdout else 0,
                    "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0
                }
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log(f"⏰ Unit tests timed out after {duration:.2f}s")
            return TestSuiteResult(
                suite_name="Phase 3.1 Unit Tests",
                test_type="unit",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                duration=duration,
                success_rate=0,
                details={"error": "timeout"}
            )
        
        except Exception as e:
            duration = time.time() - start_time
            self.log(f"❌ Unit tests failed with exception: {e}")
            return TestSuiteResult(
                suite_name="Phase 3.1 Unit Tests",
                test_type="unit",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                duration=duration,
                success_rate=0,
                details={"error": str(e)}
            )
    
    async def run_integration_tests(self) -> TestSuiteResult:
        """Run integration tests for Phase 3.1 components."""
        self.log("🔗 Running Phase 3.1 Integration Tests")
        start_time = time.time()
        
        try:
            # Run pytest on the integration test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "../test_phase_3_1_integration_tests.py", 
                "-v", "--tb=short", "--asyncio-mode=auto"
            ], capture_output=True, text=True, timeout=600)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log(f"✅ Integration tests completed successfully ({duration:.2f}s)")
            else:
                self.log(f"❌ Integration tests failed ({duration:.2f}s)")
                if result.stderr:
                    self.log(f"Errors: {result.stderr[:500]}")
            
            # Parse results from pytest output
            total, passed, failed, skipped = self._parse_pytest_output(result.stdout)
            
            success_rate = (passed / total * 100) if total > 0 else 0
            
            return TestSuiteResult(
                suite_name="Phase 3.1 Integration Tests",
                test_type="integration",
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                skipped_tests=skipped,
                duration=duration,
                success_rate=success_rate,
                details={
                    "exit_code": result.returncode,
                    "stdout_lines": len(result.stdout.split('\n')) if result.stdout else 0
                }
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log(f"⏰ Integration tests timed out after {duration:.2f}s")
            return TestSuiteResult(
                suite_name="Phase 3.1 Integration Tests",
                test_type="integration",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                duration=duration,
                success_rate=0,
                details={"error": "timeout"}
            )
        
        except Exception as e:
            duration = time.time() - start_time
            self.log(f"❌ Integration tests failed with exception: {e}")
            return TestSuiteResult(
                suite_name="Phase 3.1 Integration Tests",
                test_type="integration",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                duration=duration,
                success_rate=0,
                details={"error": str(e)}
            )
    
    async def run_e2e_tests(self) -> TestSuiteResult:
        """Run end-to-end tests for Phase 3.1 workflows."""
        self.log("🌍 Running Phase 3.1 End-to-End Tests")
        start_time = time.time()
        
        try:
            # Run pytest on the e2e test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "../test_phase_3_1_e2e_tests.py", 
                "-v", "--tb=short", "--asyncio-mode=auto", "-s"
            ], capture_output=True, text=True, timeout=900)  # Longer timeout for e2e
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log(f"✅ End-to-end tests completed successfully ({duration:.2f}s)")
            else:
                self.log(f"❌ End-to-end tests failed ({duration:.2f}s)")
                if result.stderr:
                    self.log(f"Errors: {result.stderr[:500]}")
            
            # Parse results from pytest output
            total, passed, failed, skipped = self._parse_pytest_output(result.stdout)
            
            success_rate = (passed / total * 100) if total > 0 else 0
            
            return TestSuiteResult(
                suite_name="Phase 3.1 End-to-End Tests",
                test_type="e2e",
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                skipped_tests=skipped,
                duration=duration,
                success_rate=success_rate,
                details={
                    "exit_code": result.returncode,
                    "stdout_lines": len(result.stdout.split('\n')) if result.stdout else 0
                }
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log(f"⏰ End-to-end tests timed out after {duration:.2f}s")
            return TestSuiteResult(
                suite_name="Phase 3.1 End-to-End Tests",
                test_type="e2e",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                duration=duration,
                success_rate=0,
                details={"error": "timeout"}
            )
        
        except Exception as e:
            duration = time.time() - start_time
            self.log(f"❌ End-to-end tests failed with exception: {e}")
            return TestSuiteResult(
                suite_name="Phase 3.1 End-to-End Tests",
                test_type="e2e",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                duration=duration,
                success_rate=0,
                details={"error": str(e)}
            )
    
    def _parse_pytest_output(self, output: str) -> tuple:
        """Parse pytest output to extract test counts."""
        if not output:
            return 0, 0, 0, 0
        
        # Look for pytest summary line
        lines = output.split('\n')
        for line in lines:
            if 'passed' in line and ('failed' in line or 'error' in line or 'skipped' in line):
                # Try to extract numbers from summary line
                import re
                numbers = re.findall(r'(\d+)', line)
                if len(numbers) >= 2:
                    passed = int(numbers[0])
                    failed = int(numbers[1]) if len(numbers) > 1 else 0
                    skipped = int(numbers[2]) if len(numbers) > 2 else 0
                    total = passed + failed + skipped
                    return total, passed, failed, skipped
        
        # Fallback: count test outcomes in output
        passed = output.count('PASSED')
        failed = output.count('FAILED') + output.count('ERROR')
        skipped = output.count('SKIPPED')
        total = passed + failed + skipped
        
        return total, passed, failed, skipped
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_duration = time.time() - self.start_time
        
        # Calculate aggregate statistics
        total_tests = sum(result.total_tests for result in self.results)
        total_passed = sum(result.passed_tests for result in self.results)
        total_failed = sum(result.failed_tests for result in self.results)
        total_skipped = sum(result.skipped_tests for result in self.results)
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Group results by test type
        results_by_type = {}
        for result in self.results:
            results_by_type[result.test_type] = result.to_dict()
        
        report = {
            "summary": {
                "total_test_suites": len(self.results),
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_skipped": total_skipped,
                "overall_success_rate": f"{overall_success_rate:.1f}%",
                "total_duration": f"{total_duration:.2f}s",
                "timestamp": datetime.now().isoformat()
            },
            "test_suites": results_by_type,
            "detailed_results": [result.to_dict() for result in self.results],
            "phase_info": {
                "phase": "3.1",
                "component": "Orchestrator Crew Implementation",
                "test_types": ["unit", "integration", "e2e"],
                "key_components": [
                    "Orchestrator Tools",
                    "Agent Factory",
                    "Orchestrator Crew",
                    "Tool Integration",
                    "Workflow Management"
                ]
            }
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print test summary to console."""
        summary = report['summary']
        
        self.log("📊 PHASE 3.1 TEST RESULTS SUMMARY")
        self.log("=" * 50)
        self.log(f"Total Test Suites: {summary['total_test_suites']}")
        self.log(f"Total Tests: {summary['total_tests']}")
        self.log(f"Passed: {summary['total_passed']}")
        self.log(f"Failed: {summary['total_failed']}")
        self.log(f"Skipped: {summary['total_skipped']}")
        self.log(f"Success Rate: {summary['overall_success_rate']}")
        self.log(f"Duration: {summary['total_duration']}")
        
        self.log("\n📋 Test Suite Breakdown:")
        for result in self.results:
            status_icon = "✅" if result.success_rate >= 80 else "❌"
            self.log(f"  {status_icon} {result.suite_name}: {result.success_rate:.1f}% "
                    f"({result.passed_tests}/{result.total_tests}) in {result.duration:.2f}s")
        
        # Performance analysis
        self.log("\n⚡ Performance Analysis:")
        fastest = min(self.results, key=lambda x: x.duration)
        slowest = max(self.results, key=lambda x: x.duration)
        self.log(f"  Fastest: {fastest.suite_name} ({fastest.duration:.2f}s)")
        self.log(f"  Slowest: {slowest.suite_name} ({slowest.duration:.2f}s)")
        
        # Quality assessment
        avg_success_rate = sum(r.success_rate for r in self.results) / len(self.results)
        if avg_success_rate >= 90:
            self.log(f"\n🎉 EXCELLENT: Average success rate {avg_success_rate:.1f}%")
        elif avg_success_rate >= 80:
            self.log(f"\n✅ GOOD: Average success rate {avg_success_rate:.1f}%")
        elif avg_success_rate >= 70:
            self.log(f"\n⚠️  ACCEPTABLE: Average success rate {avg_success_rate:.1f}%")
        else:
            self.log(f"\n❌ NEEDS IMPROVEMENT: Average success rate {avg_success_rate:.1f}%")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 3.1 tests and return comprehensive report."""
        self.log("🚀 Starting Phase 3.1 Comprehensive Test Suite")
        self.log(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run all test suites
            unit_result = await self.run_unit_tests()
            self.results.append(unit_result)
            
            integration_result = await self.run_integration_tests()
            self.results.append(integration_result)
            
            e2e_result = await self.run_e2e_tests()
            self.results.append(e2e_result)
            
        except Exception as e:
            self.log(f"❌ Test suite failed with error: {e}")
            traceback.print_exc()
        
        # Generate and return report
        report = self.generate_report()
        self.print_summary(report)
        
        return report

async def main():
    """Main test runner function."""
    runner = Phase31TestRunner()
    report = await runner.run_all_tests()
    
    # Save report to file
    report_file = project_root / "phase_3_1_test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    runner.log(f"📄 Full test report saved to: {report_file}")
    
    # Exit with appropriate code
    overall_success_rate = float(report['summary']['overall_success_rate'].rstrip('%'))
    failed_count = report['summary']['total_failed']
    
    if overall_success_rate >= 80 and failed_count == 0:
        runner.log(f"\n🎉 Phase 3.1 testing completed successfully!")
        sys.exit(0)
    elif overall_success_rate >= 70:
        runner.log(f"\n⚠️  Phase 3.1 testing completed with warnings")
        sys.exit(0)
    else:
        runner.log(f"\n❌ Phase 3.1 testing failed - needs attention")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())