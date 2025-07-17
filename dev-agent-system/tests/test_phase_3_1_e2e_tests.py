#!/usr/bin/env python3
"""
Phase 3.1 End-to-End Tests
End-to-end tests for complete orchestrator crew workflows
"""

import asyncio
import sys
import unittest
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import json
import tempfile
import time
import uuid
from datetime import datetime, timedelta

# Add the project paths to Python path
project_root = Path(__file__).parent
dev_agent_path = project_root / "dev-agent-system"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dev_agent_path))

# Change to dev-agent-system directory
import os
os.chdir(dev_agent_path)


class TestCompleteOrchestratorWorkflow(unittest.TestCase):
    """End-to-end tests for complete orchestrator workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.complex_project_task = """
        Develop a comprehensive Customer Relationship Management (CRM) system with the following requirements:
        
        1. User Management:
           - Multi-role authentication (Admin, Sales, Support)
           - User profile management
           - Permission-based access control
        
        2. Customer Management:
           - Customer database with contact information
           - Interaction history tracking
           - Customer segmentation and tagging
        
        3. Sales Pipeline:
           - Lead management and qualification
           - Opportunity tracking with stages
           - Sales forecasting and reporting
        
        4. Communication:
           - Email integration for customer communication
           - Task and appointment scheduling
           - Notification system for follow-ups
        
        5. Reporting & Analytics:
           - Sales performance dashboards
           - Customer behavior analytics
           - Revenue tracking and forecasting
        
        Technical Requirements:
        - Modern web application (React frontend, Node.js backend)
        - PostgreSQL database with proper schema design
        - RESTful API with authentication
        - Real-time notifications
        - Mobile-responsive design
        - Docker containerization for deployment
        """
        
        self.test_workspace = None
    
    def tearDown(self):
        """Clean up test environment"""
        if self.test_workspace and self.test_workspace.exists():
            import shutil
            shutil.rmtree(self.test_workspace)
    
    @pytest.mark.asyncio
    async def test_complete_project_lifecycle(self):
        """Test complete project lifecycle from decomposition to monitoring"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress,
            list_available_crews, get_orchestrator_status
        )
        
        print("\n🚀 Starting Complete Project Lifecycle Test")
        
        # Phase 1: Project Analysis and Decomposition
        print("📋 Phase 1: Task Decomposition")
        decomposition_result = await get_decomposed_tasks(self.complex_project_task)
        decomposed_data = json.loads(decomposition_result)
        
        self.assertIn('subtasks', decomposed_data)
        subtasks = decomposed_data['subtasks']
        self.assertGreater(len(subtasks), 3, "Complex project should have multiple subtasks")
        
        print(f"   ✅ Decomposed into {len(subtasks)} subtasks")
        for i, subtask in enumerate(subtasks[:3]):  # Show first 3
            print(f"      {i+1}. {subtask.get('title', subtask.get('id', 'Unknown'))}")
        
        # Phase 2: Crew Allocation Strategy
        print("\n👥 Phase 2: Crew Allocation")
        crews_result = await list_available_crews()
        crews_data = json.loads(crews_result)
        available_crews = crews_data['available_crews']
        
        self.assertGreater(len(available_crews), 0, "Should have available crews")
        
        print(f"   ✅ Found {len(available_crews)} available crews")
        
        # Allocate tasks to different crews based on specialization
        allocations = []
        for i, subtask in enumerate(subtasks[:4]):  # Allocate first 4 tasks
            # Select crew based on task requirements
            crew_name = self._select_optimal_crew(subtask, available_crews)
            
            allocation_result = await allocate_task_to_crew(
                json.dumps(subtask), crew_name
            )
            allocation_data = json.loads(allocation_result)
            allocations.append(allocation_data)
            
            print(f"      Allocated '{subtask.get('title', 'Task')}' to {crew_name}")
        
        self.assertEqual(len(allocations), min(4, len(subtasks)))
        
        # Phase 3: System Status Monitoring
        print("\n📊 Phase 3: System Monitoring")
        status_result = await get_orchestrator_status()
        status_data = json.loads(status_result)
        
        self.assertIn('orchestrator_status', status_data)
        self.assertEqual(status_data['orchestrator_status'], 'operational')
        
        print(f"   ✅ System Status: {status_data['orchestrator_status']}")
        print(f"      Active Tasks: {status_data.get('active_tasks', 0)}")
        print(f"      System Health: {status_data.get('system_health', 'unknown')}")
        
        # Phase 4: Progress Monitoring
        print("\n🔍 Phase 4: Progress Monitoring")
        monitoring_results = []
        
        for allocation in allocations[:2]:  # Monitor first 2 allocations
            crew_id = allocation['allocation_id']
            progress_result = await monitor_crew_progress(crew_id)
            progress_data = json.loads(progress_result)
            monitoring_results.append(progress_data)
            
            completion = progress_data.get('progress', {}).get('overall_completion', 'Unknown')
            status = progress_data.get('status', 'Unknown')
            print(f"      Crew {crew_id[:8]}...: {status} ({completion})")
        
        self.assertEqual(len(monitoring_results), 2)
        
        # Phase 5: Validation and Reporting
        print("\n✅ Phase 5: Validation")
        
        # Validate all operations succeeded
        for allocation in allocations:
            self.assertEqual(allocation['status'], 'allocated')
            self.assertIn('allocation_id', allocation)
        
        for progress in monitoring_results:
            self.assertIn('crew_identifier', progress)
            self.assertIn('status', progress)
        
        print("   ✅ All workflow phases completed successfully")
        print(f"   📈 Total subtasks: {len(subtasks)}")
        print(f"   🎯 Allocated tasks: {len(allocations)}")
        print(f"   👀 Monitored crews: {len(monitoring_results)}")
    
    def _select_optimal_crew(self, subtask, available_crews):
        """Select optimal crew based on task requirements"""
        task_title = subtask.get('title', '').lower()
        task_desc = subtask.get('description', '').lower()
        task_content = f"{task_title} {task_desc}"
        
        # Crew selection logic based on keywords
        if any(keyword in task_content for keyword in ['database', 'schema', 'data']):
            return 'development_crew'
        elif any(keyword in task_content for keyword in ['test', 'quality', 'validation']):
            return 'qa_crew'
        elif any(keyword in task_content for keyword in ['deploy', 'docker', 'production']):
            return 'deployment_crew'
        elif any(keyword in task_content for keyword in ['research', 'analysis', 'requirements']):
            return 'research_crew'
        elif any(keyword in task_content for keyword in ['plan', 'strategy', 'architecture']):
            return 'planning_crew'
        else:
            return 'development_crew'  # Default crew
    
    @pytest.mark.asyncio
    async def test_concurrent_project_execution(self):
        """Test concurrent execution of multiple projects"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew
        )
        
        print("\n🔄 Starting Concurrent Project Execution Test")
        
        # Define multiple projects
        projects = [
            "Build a todo list mobile app with cloud sync",
            "Create an inventory management system for retail",
            "Develop a blog platform with user comments"
        ]
        
        # Phase 1: Concurrent Decomposition
        print("📋 Phase 1: Concurrent Task Decomposition")
        decomposition_tasks = [
            get_decomposed_tasks(project) for project in projects
        ]
        
        start_time = time.time()
        decomposition_results = await asyncio.gather(*decomposition_tasks)
        decomposition_time = time.time() - start_time
        
        print(f"   ✅ Decomposed {len(projects)} projects in {decomposition_time:.2f}s")
        
        # Validate all decompositions
        all_subtasks = []
        for i, result in enumerate(decomposition_results):
            data = json.loads(result)
            subtasks = data['subtasks']
            all_subtasks.extend(subtasks)
            print(f"      Project {i+1}: {len(subtasks)} subtasks")
        
        # Phase 2: Concurrent Allocation
        print("\n👥 Phase 2: Concurrent Task Allocation")
        allocation_tasks = []
        
        # Create allocation tasks for first 2 subtasks from each project
        crews = ['development_crew', 'research_crew', 'qa_crew']
        for i, result in enumerate(decomposition_results):
            data = json.loads(result)
            subtasks = data['subtasks'][:2]  # First 2 subtasks
            
            for j, subtask in enumerate(subtasks):
                crew = crews[(i + j) % len(crews)]  # Distribute across crews
                allocation_tasks.append(
                    allocate_task_to_crew(json.dumps(subtask), crew)
                )
        
        start_time = time.time()
        allocation_results = await asyncio.gather(*allocation_tasks)
        allocation_time = time.time() - start_time
        
        print(f"   ✅ Allocated {len(allocation_tasks)} tasks in {allocation_time:.2f}s")
        
        # Validate allocations
        successful_allocations = 0
        for result in allocation_results:
            data = json.loads(result)
            if data.get('status') == 'allocated':
                successful_allocations += 1
        
        print(f"      Successful allocations: {successful_allocations}/{len(allocation_results)}")
        self.assertGreater(successful_allocations, len(allocation_results) * 0.8)  # 80% success
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test error recovery in orchestrator workflows"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress
        )
        
        print("\n🛠️ Starting Error Recovery Workflow Test")
        
        # Test scenarios with various error conditions
        error_scenarios = [
            {
                "name": "Empty Task",
                "task": "",
                "crew": "development_crew",
                "should_handle": True
            },
            {
                "name": "Invalid Crew",
                "task": "Valid task description",
                "crew": "nonexistent_crew",
                "should_handle": True
            },
            {
                "name": "Very Long Task",
                "task": "A" * 10000,  # Very long task description
                "crew": "development_crew", 
                "should_handle": True
            },
            {
                "name": "Special Characters",
                "task": "Task with special chars: !@#$%^&*(){}[]|\\:;\"'<>?,./ 中文 العربية",
                "crew": "development_crew",
                "should_handle": True
            }
        ]
        
        for scenario in error_scenarios:
            print(f"\n   🧪 Testing: {scenario['name']}")
            
            try:
                # Test decomposition
                decomp_result = await get_decomposed_tasks(scenario['task'])
                decomp_data = json.loads(decomp_result)
                
                # Should return valid structure even with errors
                if 'error' in decomp_data:
                    print(f"      ⚠️  Decomposition error handled: {decomp_data['error'][:50]}...")
                else:
                    print(f"      ✅ Decomposition succeeded")
                
                # Test allocation
                alloc_result = await allocate_task_to_crew(scenario['task'], scenario['crew'])
                alloc_data = json.loads(alloc_result)
                
                if 'error' in alloc_data:
                    print(f"      ⚠️  Allocation error handled: {alloc_data['error'][:50]}...")
                else:
                    print(f"      ✅ Allocation succeeded")
                
                # Test monitoring
                monitor_result = await monitor_crew_progress("test_crew_error")
                monitor_data = json.loads(monitor_result)
                
                if 'error' in monitor_data:
                    print(f"      ⚠️  Monitoring error handled: {monitor_data['error'][:50]}...")
                else:
                    print(f"      ✅ Monitoring succeeded")
                
            except Exception as e:
                if scenario['should_handle']:
                    self.fail(f"Unhandled exception in {scenario['name']}: {e}")
                else:
                    print(f"      ❌ Expected exception: {e}")
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self):
        """Test performance benchmarks for orchestrator operations"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress,
            list_available_crews, get_orchestrator_status
        )
        
        print("\n⚡ Starting Performance Benchmark Test")
        
        # Benchmark individual operations
        operations = [
            ("Task Decomposition", lambda: get_decomposed_tasks("Build a simple web application")),
            ("Task Allocation", lambda: allocate_task_to_crew("Test task", "development_crew")),
            ("Crew Monitoring", lambda: monitor_crew_progress("test_crew_perf")),
            ("List Crews", lambda: list_available_crews()),
            ("System Status", lambda: get_orchestrator_status())
        ]
        
        benchmarks = {}
        
        for operation_name, operation_func in operations:
            print(f"\n   🔄 Benchmarking: {operation_name}")
            
            # Run operation multiple times
            times = []
            for i in range(3):  # 3 iterations
                start_time = time.time()
                result = await operation_func()
                end_time = time.time()
                times.append(end_time - start_time)
                
                # Validate result
                if isinstance(result, str):
                    json.loads(result)  # Should be valid JSON
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            benchmarks[operation_name] = {
                "average": avg_time,
                "min": min_time,
                "max": max_time,
                "iterations": len(times)
            }
            
            print(f"      Average: {avg_time:.3f}s (min: {min_time:.3f}s, max: {max_time:.3f}s)")
        
        # Performance assertions
        for operation_name, metrics in benchmarks.items():
            # Most operations should complete within reasonable time
            if operation_name == "Task Decomposition":
                self.assertLess(metrics["average"], 10.0, f"{operation_name} too slow")
            else:
                self.assertLess(metrics["average"], 2.0, f"{operation_name} too slow")
        
        print(f"\n   ✅ All {len(benchmarks)} operations within performance thresholds")
    
    @pytest.mark.asyncio
    async def test_real_world_scenario_simulation(self):
        """Test simulation of real-world development scenario"""
        from tools.orchestrator_tools import (
            get_decomposed_tasks, allocate_task_to_crew, monitor_crew_progress
        )
        
        print("\n🌍 Starting Real-World Scenario Simulation")
        
        # Simulate a realistic software development project timeline
        project_phases = [
            {
                "phase": "Discovery & Planning",
                "tasks": [
                    "Conduct stakeholder interviews and requirements gathering",
                    "Create technical architecture documentation",
                    "Define project scope and deliverables"
                ]
            },
            {
                "phase": "Design & Prototyping", 
                "tasks": [
                    "Create UI/UX wireframes and mockups",
                    "Design database schema and API specifications",
                    "Build functional prototype for user testing"
                ]
            },
            {
                "phase": "Development",
                "tasks": [
                    "Implement core application features",
                    "Develop API endpoints and data layer",
                    "Create responsive frontend components"
                ]
            },
            {
                "phase": "Testing & Deployment",
                "tasks": [
                    "Implement automated testing suite",
                    "Perform security and performance testing",
                    "Deploy to production environment"
                ]
            }
        ]
        
        total_allocations = 0
        phase_results = []
        
        for phase_info in project_phases:
            print(f"\n   📅 Phase: {phase_info['phase']}")
            
            phase_allocations = []
            
            # Process each task in the phase
            for task in phase_info['tasks']:
                # Decompose task
                decomp_result = await get_decomposed_tasks(task)
                decomp_data = json.loads(decomp_result)
                
                # Allocate to appropriate crew
                crew = self._select_crew_for_phase(phase_info['phase'])
                alloc_result = await allocate_task_to_crew(
                    json.dumps(decomp_data['subtasks'][0] if decomp_data['subtasks'] else {'description': task}),
                    crew
                )
                alloc_data = json.loads(alloc_result)
                phase_allocations.append(alloc_data)
                
                print(f"      ✓ {task[:50]}... → {crew}")
            
            phase_results.append({
                "phase": phase_info['phase'],
                "allocations": phase_allocations
            })
            total_allocations += len(phase_allocations)
        
        # Simulate monitoring during development
        print(f"\n   👀 Monitoring {total_allocations} active tasks...")
        
        # Monitor a sample of allocations
        sample_size = min(3, total_allocations)
        sample_allocations = []
        for phase_result in phase_results:
            if phase_result['allocations']:
                sample_allocations.append(phase_result['allocations'][0])
                if len(sample_allocations) >= sample_size:
                    break
        
        monitoring_results = []
        for allocation in sample_allocations:
            monitor_result = await monitor_crew_progress(allocation['allocation_id'])
            monitor_data = json.loads(monitor_result)
            monitoring_results.append(monitor_data)
        
        print(f"      ✅ Monitored {len(monitoring_results)} crews successfully")
        
        # Validate end-to-end workflow
        self.assertEqual(len(phase_results), 4)  # All phases processed
        self.assertGreater(total_allocations, 8)  # Reasonable number of tasks
        self.assertEqual(len(monitoring_results), sample_size)  # All monitored
        
        print(f"\n   🎉 Simulation Complete:")
        print(f"      Phases: {len(phase_results)}")
        print(f"      Total Tasks: {total_allocations}")
        print(f"      Monitored: {len(monitoring_results)}")
    
    def _select_crew_for_phase(self, phase_name):
        """Select appropriate crew based on project phase"""
        phase_crew_mapping = {
            "Discovery & Planning": "research_crew",
            "Design & Prototyping": "planning_crew", 
            "Development": "development_crew",
            "Testing & Deployment": "qa_crew"
        }
        return phase_crew_mapping.get(phase_name, "development_crew")


if __name__ == "__main__":
    # Run async tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-s"])