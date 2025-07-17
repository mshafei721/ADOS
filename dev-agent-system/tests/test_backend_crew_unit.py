"""
Unit Tests for Backend Crew Implementation
Tests individual components of the backend crew system
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from crews.backend.backend_crew import BackendCrew
from tools.backend_tools import BackendTools, APIEndpointSpec, DatabaseModelSpec
from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory


class TestBackendTools:
    """Test backend tools functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.backend_tools = BackendTools(".")
        self.logger = logging.getLogger("test")
    
    def test_backend_tools_initialization(self):
        """Test backend tools initialization"""
        tools = BackendTools(".", self.logger)
        assert tools.project_root == Path(".")
        assert tools.logger == self.logger
        assert tools.templates_dir == Path(".") / "dev-agent-system" / "crews" / "backend" / "kb"
    
    def test_get_tool_status(self):
        """Test tool status retrieval"""
        status = self.backend_tools.get_tool_status()
        
        assert status["tool_name"] == "BackendTools"
        assert status["version"] == "1.0.0"
        assert "fastapi_boilerplate_generation" in status["capabilities"]
        assert "sqlalchemy_model_generation" in status["capabilities"]
        assert "pytest_test_runner" in status["capabilities"]
        assert status["status"] == "operational"
    
    def test_api_endpoint_spec_creation(self):
        """Test API endpoint specification creation"""
        spec = APIEndpointSpec(
            name="Get User",
            method="GET",
            path="/api/v1/users/{user_id}",
            description="Get user by ID",
            response_model="UserResponse",
            auth_required=True,
            tags=["users"]
        )
        
        assert spec.name == "Get User"
        assert spec.method == "GET"
        assert spec.path == "/api/v1/users/{user_id}"
        assert spec.auth_required is True
        assert "users" in spec.tags
    
    def test_database_model_spec_creation(self):
        """Test database model specification creation"""
        spec = DatabaseModelSpec(
            name="User",
            table_name="users",
            fields={
                "id": {"type": "Integer", "primary_key": True},
                "email": {"type": "String", "nullable": False},
                "name": {"type": "String", "nullable": True}
            },
            relationships={"posts": "Post"},
            indexes=["email"],
            constraints=["UNIQUE(email)"]
        )
        
        assert spec.name == "User"
        assert spec.table_name == "users"
        assert spec.fields["id"]["primary_key"] is True
        assert spec.relationships["posts"] == "Post"
        assert "email" in spec.indexes
    
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_generate_fastapi_boilerplate(self, mock_write_text, mock_mkdir):
        """Test FastAPI boilerplate generation"""
        endpoints = [
            APIEndpointSpec(
                name="Get Users",
                method="GET",
                path="/api/v1/users",
                description="Get all users",
                response_model="UserList",
                tags=["users"]
            )
        ]
        
        result = self.backend_tools.generate_fastapi_boilerplate(
            app_name="test_app",
            endpoints=endpoints
        )
        
        assert result["status"] == "success"
        assert result["app_name"] == "test_app"
        assert result["endpoints_count"] == 1
        assert "main.py" in result["files_generated"]
        assert "models.py" in result["files_generated"]
        assert "requirements.txt" in result["files_generated"]
        assert "Dockerfile" in result["files_generated"]
    
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_generate_sqlalchemy_models(self, mock_write_text, mock_mkdir):
        """Test SQLAlchemy model generation"""
        models = [
            DatabaseModelSpec(
                name="User",
                table_name="users",
                fields={
                    "id": {"type": "Integer", "primary_key": True},
                    "email": {"type": "String", "nullable": False}
                }
            )
        ]
        
        result = self.backend_tools.generate_sqlalchemy_models(models)
        
        assert result["status"] == "success"
        assert "User" in result["models_generated"]
        assert result["models_count"] == 1
        assert "models.py" in result["files_generated"]
        assert "database.py" in result["files_generated"]
    
    @patch('subprocess.run')
    def test_run_pytest_tests_success(self, mock_run):
        """Test successful pytest execution"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="5 passed in 1.23s",
            stderr=""
        )
        
        result = self.backend_tools.run_pytest_tests("tests")
        
        assert result["status"] == "success"
        assert result["return_code"] == 0
        assert "summary" in result
    
    @patch('subprocess.run')
    def test_run_pytest_tests_failure(self, mock_run):
        """Test failed pytest execution"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="3 passed, 2 failed in 1.23s",
            stderr="Some error"
        )
        
        result = self.backend_tools.run_pytest_tests("tests")
        
        assert result["status"] == "failed"
        assert result["return_code"] == 1
        assert "summary" in result
    
    def test_parse_pytest_output(self):
        """Test pytest output parsing"""
        output = "collected 10 items\n\n5 passed, 2 failed, 1 skipped in 1.23s"
        
        summary = self.backend_tools._parse_pytest_output(output)
        
        assert summary["passed"] == 5
        assert summary["failed"] == 2
        assert summary["skipped"] == 1
        assert summary["total_tests"] == 8


class TestBackendCrew:
    """Test backend crew functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.mock_config_loader = Mock(spec=ConfigLoader)
        self.mock_agent_factory = Mock(spec=AgentFactory)
        self.mock_logger = Mock(spec=logging.Logger)
        
        # Mock agent configurations
        self.mock_config_loader.agents = {
            "APIAgent": {
                "role": "APIAgent",
                "goal": "Design and implement APIs",
                "backstory": "Expert backend developer",
                "llm": "gpt-4",
                "max_iter": 8,
                "verbose": True
            },
            "DatabaseAgent": {
                "role": "DatabaseAgent", 
                "goal": "Design database schemas",
                "backstory": "Database architect",
                "llm": "gpt-4",
                "max_iter": 8,
                "verbose": True
            }
        }
        
        # Mock agent factory
        self.mock_api_agent = Mock()
        self.mock_db_agent = Mock()
        self.mock_agent_factory.create_agent.side_effect = [
            self.mock_api_agent,
            self.mock_db_agent
        ]
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_backend_crew_initialization(self, mock_write_text, mock_mkdir, mock_crew, mock_backend_tools):
        """Test backend crew initialization"""
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        assert crew.config_loader == self.mock_config_loader
        assert crew.agent_factory == self.mock_agent_factory
        assert crew.crew_status == "ready"
        assert hasattr(crew, 'api_agent')
        assert hasattr(crew, 'db_agent')
        assert hasattr(crew, 'crew')
        assert hasattr(crew, 'backend_tools')
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_crew_status_tracking(self, mock_write_text, mock_mkdir, mock_crew, mock_backend_tools):
        """Test crew status tracking"""
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        status = crew.get_crew_status()
        
        assert status["crew_name"] == "backend"
        assert status["status"] == "ready"
        assert "health" in status
        assert "performance_metrics" in status
        assert "agents" in status
        assert status["agents"]["api_agent"]["role"] == "APIAgent"
        assert status["agents"]["db_agent"]["role"] == "DatabaseAgent"
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_performance_metrics_tracking(self, mock_write_text, mock_mkdir, mock_crew, mock_backend_tools):
        """Test performance metrics tracking"""
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        metrics = crew.performance_metrics
        
        assert metrics["apis_generated"] == 0
        assert metrics["models_generated"] == 0
        assert metrics["tests_run"] == 0
        assert metrics["tests_passed"] == 0
        assert metrics["tests_failed"] == 0
        assert "start_time" in metrics
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('crews.backend.backend_crew.Task')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_generate_api_endpoints(self, mock_write_text, mock_mkdir, mock_task, mock_crew, mock_backend_tools):
        """Test API endpoint generation"""
        # Mock backend tools
        mock_backend_tools_instance = Mock()
        mock_backend_tools.return_value = mock_backend_tools_instance
        mock_backend_tools_instance.generate_fastapi_boilerplate.return_value = {
            "status": "success",
            "app_name": "test_app",
            "endpoints_count": 1
        }
        
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        endpoints = [
            APIEndpointSpec(
                name="Get Users",
                method="GET",
                path="/api/v1/users",
                description="Get all users"
            )
        ]
        
        result = crew.generate_api_endpoints("test_app", endpoints)
        
        assert result["status"] == "success"
        assert result["app_name"] == "test_app"
        assert crew.performance_metrics["apis_generated"] == 1
        assert crew.performance_metrics["total_endpoints"] == 1
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('crews.backend.backend_crew.Task')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_generate_database_models(self, mock_write_text, mock_mkdir, mock_task, mock_crew, mock_backend_tools):
        """Test database model generation"""
        # Mock backend tools
        mock_backend_tools_instance = Mock()
        mock_backend_tools.return_value = mock_backend_tools_instance
        mock_backend_tools_instance.generate_sqlalchemy_models.return_value = {
            "status": "success",
            "models_count": 1
        }
        
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        models = [
            DatabaseModelSpec(
                name="User",
                table_name="users",
                fields={"id": {"type": "Integer", "primary_key": True}}
            )
        ]
        
        result = crew.generate_database_models(models)
        
        assert result["status"] == "success"
        assert crew.performance_metrics["models_generated"] == 1
        assert crew.performance_metrics["total_models"] == 1
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_run_backend_tests(self, mock_write_text, mock_mkdir, mock_crew, mock_backend_tools):
        """Test backend test execution"""
        # Mock backend tools
        mock_backend_tools_instance = Mock()
        mock_backend_tools.return_value = mock_backend_tools_instance
        mock_backend_tools_instance.run_pytest_tests.return_value = {
            "status": "success",
            "summary": {"passed": 5, "failed": 0}
        }
        
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        result = crew.run_backend_tests("tests")
        
        assert result["status"] == "success"
        assert crew.performance_metrics["tests_run"] == 1
        assert crew.performance_metrics["tests_passed"] == 5
        assert crew.performance_metrics["tests_failed"] == 0
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_health_check(self, mock_write_text, mock_mkdir, mock_crew, mock_backend_tools):
        """Test crew health check"""
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        health = crew.health_check()
        
        assert health["status"] == "healthy"
        assert health["checks"]["crew_initialization"] is True
        assert health["checks"]["api_agent"] is True
        assert health["checks"]["db_agent"] is True
        assert health["checks"]["backend_tools"] is True
        assert "metrics" in health
        assert "timestamp" in health
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('crews.backend.backend_crew.Task')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_crew_error_handling(self, mock_write_text, mock_mkdir, mock_task, mock_crew, mock_backend_tools):
        """Test crew error handling"""
        # Mock backend tools to raise exception
        mock_backend_tools_instance = Mock()
        mock_backend_tools.return_value = mock_backend_tools_instance
        mock_backend_tools_instance.generate_fastapi_boilerplate.side_effect = Exception("Test error")
        
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        endpoints = [APIEndpointSpec(name="Test", method="GET", path="/test", description="Test")]
        result = crew.generate_api_endpoints("test_app", endpoints)
        
        assert result["status"] == "error"
        assert "Test error" in result["error"]
        assert crew.crew_status == "error"
    
    @patch('crews.backend.backend_crew.BackendTools')
    @patch('crews.backend.backend_crew.Crew')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_crew_shutdown(self, mock_write_text, mock_mkdir, mock_crew, mock_backend_tools):
        """Test crew shutdown"""
        crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
        
        crew.shutdown()
        
        assert crew.crew_status == "shutdown"
        assert len(crew.active_tasks) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])