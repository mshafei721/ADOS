"""
ADOS Backend Crew Implementation
Specialized crew for API development and database management
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from crewai import Agent, Crew, Task, Process

from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory
from tools.backend_tools import BackendTools, APIEndpointSpec, DatabaseModelSpec


class BackendCrew:
    """Specialized backend crew with API and database development capabilities"""
    
    def __init__(self, config_loader: ConfigLoader, agent_factory: AgentFactory):
        """Initialize the backend crew"""
        self.config_loader = config_loader
        self.agent_factory = agent_factory
        self.logger = logging.getLogger(__name__)
        
        # Initialize backend tools
        self.backend_tools = BackendTools(logger=self.logger)
        
        # Crew state
        self.crew_status = "initializing"
        self.active_tasks = []
        self.completed_tasks = []
        self.performance_metrics = {}
        
        # Initialize the crew
        self.initialize_backend_crew()
    
    def initialize_backend_crew(self) -> bool:
        """Initialize backend crew with API and DB agents"""
        try:
            self.logger.info("Initializing backend crew...")
            
            # Setup crew monitoring
            self._setup_crew_monitoring()
            self._setup_performance_tracking()
            self._setup_backend_workspace()
            
            # Create agents
            self.api_agent = self._create_api_agent()
            self.db_agent = self._create_db_agent()
            
            # Create crew
            self.crew = self._create_crew()
            
            self.crew_status = "ready"
            self.logger.info("Backend crew initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize backend crew: {e}")
            self.crew_status = "error"
            return False
    
    def _setup_crew_monitoring(self):
        """Setup crew health monitoring"""
        self.crew_health = {
            "status": "initializing",
            "load": 0,
            "last_check": datetime.now().isoformat(),
            "active_agents": 0,
            "tasks_in_progress": 0,
            "errors": []
        }
    
    def _setup_performance_tracking(self):
        """Setup performance monitoring"""
        self.performance_metrics = {
            "apis_generated": 0,
            "models_generated": 0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "average_generation_time": 0.0,
            "total_endpoints": 0,
            "total_models": 0,
            "start_time": datetime.now()
        }
    
    def _setup_backend_workspace(self):
        """Setup backend workspace directories"""
        try:
            workspace_path = Path("dev-agent-system/workspace/backend")
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Create runtime.md
            runtime_content = f"""# Backend Crew Runtime Context

## Status: {self.crew_status}
## Initialized: {datetime.now().isoformat()}

### Agent Status
- APIAgent: Initializing
- DatabaseAgent: Initializing

### Current Tasks
None

### Performance Metrics
{self.performance_metrics}

### Workspace Files
- runtime.md (this file)
- Generated code output: ./output/generated_code/backend/
"""
            (workspace_path / "runtime.md").write_text(runtime_content)
            
            self.logger.info("Backend workspace setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup backend workspace: {e}")
    
    def _create_api_agent(self) -> Agent:
        """Create API development agent"""
        try:
            agent_config = self.config_loader.agents.get("APIAgent")
            if not agent_config:
                raise ValueError("APIAgent configuration not found")
            
            # Create agent using agent factory
            api_agent = self.agent_factory.create_agent(
                name="APIAgent",
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                tools=self._get_api_agent_tools(),
                llm=agent_config.get("llm", "gpt-4"),
                max_iter=agent_config.get("max_iter", 8),
                verbose=agent_config.get("verbose", True)
            )
            
            self.logger.info("API Agent created successfully")
            return api_agent
            
        except Exception as e:
            self.logger.error(f"Failed to create API Agent: {e}")
            raise
    
    def _create_db_agent(self) -> Agent:
        """Create database development agent"""
        try:
            agent_config = self.config_loader.agents.get("DatabaseAgent")
            if not agent_config:
                raise ValueError("DatabaseAgent configuration not found")
            
            # Create agent using agent factory
            db_agent = self.agent_factory.create_agent(
                name="DatabaseAgent",
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                tools=self._get_db_agent_tools(),
                llm=agent_config.get("llm", "gpt-4"),
                max_iter=agent_config.get("max_iter", 8),
                verbose=agent_config.get("verbose", True)
            )
            
            self.logger.info("Database Agent created successfully")
            return db_agent
            
        except Exception as e:
            self.logger.error(f"Failed to create Database Agent: {e}")
            raise
    
    def _get_api_agent_tools(self) -> List[Any]:
        """Get tools for API agent"""
        # In a real implementation, these would be actual tool instances
        # For now, return tool names that would be resolved by the agent factory
        return [
            self.backend_tools.generate_fastapi_boilerplate,
            self.backend_tools.run_pytest_tests,
            "search.python_docs"  # Would be resolved by agent factory
        ]
    
    def _get_db_agent_tools(self) -> List[Any]:
        """Get tools for database agent"""
        return [
            self.backend_tools.generate_sqlalchemy_models,
            self.backend_tools.run_pytest_tests,
            "search.database_docs"  # Would be resolved by agent factory
        ]
    
    def _create_crew(self) -> Crew:
        """Create the backend crew"""
        try:
            crew = Crew(
                agents=[self.api_agent, self.db_agent],
                verbose=True,
                process=Process.sequential,
                max_rpm=10
            )
            
            self.logger.info("Backend crew created successfully")
            return crew
            
        except Exception as e:
            self.logger.error(f"Failed to create backend crew: {e}")
            raise
    
    def generate_api_endpoints(self, 
                             app_name: str,
                             endpoints: List[APIEndpointSpec]) -> Dict[str, Any]:
        """Generate API endpoints using backend crew"""
        try:
            self.logger.info(f"Generating API endpoints for {app_name}")
            
            # Create task for API agent
            task = Task(
                description=f"Generate FastAPI boilerplate for {app_name} with {len(endpoints)} endpoints",
                agent=self.api_agent,
                expected_output="Complete FastAPI application with all endpoints and proper structure"
            )
            
            # Update crew status
            self.crew_status = "executing"
            self.active_tasks.append(task)
            
            # Generate using backend tools
            result = self.backend_tools.generate_fastapi_boilerplate(
                app_name=app_name,
                endpoints=endpoints
            )
            
            # Update metrics
            if result["status"] == "success":
                self.performance_metrics["apis_generated"] += 1
                self.performance_metrics["total_endpoints"] += len(endpoints)
                self.crew_health["status"] = "active"
            else:
                self.crew_health["errors"].append(result.get("error", "Unknown error"))
            
            # Update task status
            self.active_tasks.remove(task)
            self.completed_tasks.append({
                "task": task,
                "result": result,
                "completed_at": datetime.now().isoformat()
            })
            
            self.crew_status = "ready"
            self.logger.info(f"API generation completed with status: {result['status']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate API endpoints: {e}")
            self.crew_status = "error"
            return {"status": "error", "error": str(e)}
    
    def generate_database_models(self, models: List[DatabaseModelSpec]) -> Dict[str, Any]:
        """Generate database models using backend crew"""
        try:
            self.logger.info(f"Generating database models: {[m.name for m in models]}")
            
            # Create task for database agent
            task = Task(
                description=f"Generate SQLAlchemy models for {len(models)} database entities",
                agent=self.db_agent,
                expected_output="Complete SQLAlchemy models with proper relationships and constraints"
            )
            
            # Update crew status
            self.crew_status = "executing"
            self.active_tasks.append(task)
            
            # Generate using backend tools
            result = self.backend_tools.generate_sqlalchemy_models(models)
            
            # Update metrics
            if result["status"] == "success":
                self.performance_metrics["models_generated"] += 1
                self.performance_metrics["total_models"] += len(models)
                self.crew_health["status"] = "active"
            else:
                self.crew_health["errors"].append(result.get("error", "Unknown error"))
            
            # Update task status
            self.active_tasks.remove(task)
            self.completed_tasks.append({
                "task": task,
                "result": result,
                "completed_at": datetime.now().isoformat()
            })
            
            self.crew_status = "ready"
            self.logger.info(f"Model generation completed with status: {result['status']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate database models: {e}")
            self.crew_status = "error"
            return {"status": "error", "error": str(e)}
    
    def run_backend_tests(self, test_directory: str = "tests") -> Dict[str, Any]:
        """Run backend tests using pytest"""
        try:
            self.logger.info(f"Running backend tests in {test_directory}")
            
            # Run tests using backend tools
            result = self.backend_tools.run_pytest_tests(test_directory)
            
            # Update metrics
            self.performance_metrics["tests_run"] += 1
            if result["status"] == "success":
                if "summary" in result:
                    summary = result["summary"]
                    self.performance_metrics["tests_passed"] += summary.get("passed", 0)
                    self.performance_metrics["tests_failed"] += summary.get("failed", 0)
            else:
                self.performance_metrics["tests_failed"] += 1
                self.crew_health["errors"].append(result.get("error", "Test execution failed"))
            
            self.logger.info(f"Backend tests completed with status: {result['status']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to run backend tests: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get current crew status"""
        return {
            "crew_name": "backend",
            "status": self.crew_status,
            "health": self.crew_health,
            "performance_metrics": self.performance_metrics,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "agents": {
                "api_agent": {
                    "status": "active" if hasattr(self, 'api_agent') else "not_initialized",
                    "role": "APIAgent"
                },
                "db_agent": {
                    "status": "active" if hasattr(self, 'db_agent') else "not_initialized",
                    "role": "DatabaseAgent"
                }
            },
            "tools_status": self.backend_tools.get_tool_status(),
            "timestamp": datetime.now().isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "crew_initialization": hasattr(self, 'crew'),
                    "api_agent": hasattr(self, 'api_agent'),
                    "db_agent": hasattr(self, 'db_agent'),
                    "backend_tools": True,
                    "workspace_setup": True
                },
                "metrics": self.performance_metrics,
                "issues": []
            }
            
            # Check for issues
            if self.crew_health["errors"]:
                health_status["issues"].extend(self.crew_health["errors"])
                health_status["status"] = "warning"
            
            if self.crew_status == "error":
                health_status["status"] = "critical"
                health_status["issues"].append("Crew is in error state")
            
            if len(self.active_tasks) > 5:
                health_status["issues"].append("High number of active tasks")
                health_status["status"] = "warning"
            
            # Check test success rate
            total_tests = self.performance_metrics["tests_passed"] + self.performance_metrics["tests_failed"]
            if total_tests > 0:
                success_rate = self.performance_metrics["tests_passed"] / total_tests
                if success_rate < 0.8:  # Less than 80% success rate
                    health_status["issues"].append("Low test success rate")
                    health_status["status"] = "warning"
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def update_runtime_context(self):
        """Update runtime context file"""
        try:
            workspace_path = Path("dev-agent-system/workspace/backend")
            runtime_content = f"""# Backend Crew Runtime Context

## Status: {self.crew_status}
## Last Updated: {datetime.now().isoformat()}

### Agent Status
- APIAgent: {"Active" if hasattr(self, 'api_agent') else "Not Initialized"}
- DatabaseAgent: {"Active" if hasattr(self, 'db_agent') else "Not Initialized"}

### Current Tasks
{len(self.active_tasks)} active tasks

### Performance Metrics
- APIs Generated: {self.performance_metrics['apis_generated']}
- Models Generated: {self.performance_metrics['models_generated']}
- Tests Run: {self.performance_metrics['tests_run']}
- Tests Passed: {self.performance_metrics['tests_passed']}
- Tests Failed: {self.performance_metrics['tests_failed']}
- Total Endpoints: {self.performance_metrics['total_endpoints']}
- Total Models: {self.performance_metrics['total_models']}

### Health Status
{self.crew_health}

### Recent Tasks
{len(self.completed_tasks)} completed tasks

### Workspace Files
- runtime.md (this file)
- Generated code output: ./output/generated_code/backend/
"""
            (workspace_path / "runtime.md").write_text(runtime_content)
            
        except Exception as e:
            self.logger.error(f"Failed to update runtime context: {e}")
    
    def shutdown(self):
        """Shutdown the backend crew"""
        try:
            self.logger.info("Shutting down backend crew...")
            
            # Update runtime context one final time
            self.update_runtime_context()
            
            # Clean up resources
            self.crew_status = "shutdown"
            self.active_tasks.clear()
            
            self.logger.info("Backend crew shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown backend crew: {e}")