"""
Integration Tests for Backend Crew
Tests integration between backend crew and other system components
"""

import pytest
import logging
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from crews.backend.backend_crew import BackendCrew
from tools.backend_tools import BackendTools, APIEndpointSpec, DatabaseModelSpec
from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory


class TestBackendCrewIntegration:
    """Integration tests for backend crew with system components"""
    
    def setup_method(self):
        """Setup test environment with real components"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_path = Path(self.temp_dir)
        
        # Create minimal directory structure
        (self.test_project_path / "dev-agent-system" / "crews" / "backend" / "kb").mkdir(parents=True)
        (self.test_project_path / "dev-agent-system" / "workspace" / "backend").mkdir(parents=True)
        (self.test_project_path / "output" / "generated_code").mkdir(parents=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("test_integration")
        
        # Create real backend tools instance
        self.backend_tools = BackendTools(str(self.test_project_path), self.logger)
        
        # Mock configuration loader
        self.mock_config_loader = Mock(spec=ConfigLoader)
        self.mock_config_loader.agents = {
            "APIAgent": {
                "role": "APIAgent",
                "goal": "Design and implement RESTful APIs",
                "backstory": "Expert backend developer",
                "llm": "gpt-4",
                "max_iter": 8,
                "verbose": True
            },
            "DatabaseAgent": {
                "role": "DatabaseAgent",
                "goal": "Design database schemas and models",
                "backstory": "Database architect",
                "llm": "gpt-4", 
                "max_iter": 8,
                "verbose": True
            }
        }
        
        # Mock agent factory
        self.mock_agent_factory = Mock(spec=AgentFactory)
        self.mock_api_agent = Mock()
        self.mock_db_agent = Mock()
        self.mock_agent_factory.create_agent.side_effect = [
            self.mock_api_agent,
            self.mock_db_agent
        ]
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_backend_tools_real_file_operations(self):
        """Test backend tools with real file operations"""
        # Test FastAPI boilerplate generation
        endpoints = [
            APIEndpointSpec(
                name="Get Users",
                method="GET",
                path="/api/v1/users",
                description="Get all users",
                response_model="UserList",
                tags=["users"]
            ),
            APIEndpointSpec(
                name="Create User",
                method="POST",
                path="/api/v1/users",
                description="Create a new user",
                request_model="UserCreate",
                response_model="UserResponse",
                auth_required=True,
                tags=["users"]
            )
        ]
        
        result = self.backend_tools.generate_fastapi_boilerplate("test_app", endpoints)
        
        assert result["status"] == "success"
        assert result["app_name"] == "test_app"
        assert result["endpoints_count"] == 2
        
        # Verify files were created
        output_dir = self.test_project_path / "output" / "generated_code" / "backend" / "test_app"
        assert (output_dir / "main.py").exists()
        assert (output_dir / "models.py").exists()
        assert (output_dir / "requirements.txt").exists()
        assert (output_dir / "Dockerfile").exists()
        assert (output_dir / "routers" / "users.py").exists()
        
        # Verify file contents
        main_content = (output_dir / "main.py").read_text()
        assert "test_app" in main_content
        assert "from routers import users" in main_content
        assert "app.include_router(users.router)" in main_content
        
        models_content = (output_dir / "models.py").read_text()
        assert "UserList" in models_content
        assert "UserCreate" in models_content
        assert "UserResponse" in models_content
        
        requirements_content = (output_dir / "requirements.txt").read_text()
        assert "fastapi" in requirements_content
        assert "uvicorn" in requirements_content
        assert "sqlalchemy" in requirements_content
    
    def test_backend_tools_sqlalchemy_models(self):
        """Test SQLAlchemy model generation with real files"""
        models = [
            DatabaseModelSpec(
                name="User",
                table_name="users",
                fields={
                    "id": {"type": "Integer", "primary_key": True},
                    "email": {"type": "String", "nullable": False},
                    "name": {"type": "String", "nullable": True},
                    "created_at": {"type": "DateTime", "nullable": False}
                },
                relationships={"posts": "Post"},
                indexes=["email"],
                constraints=["UNIQUE(email)"]
            ),
            DatabaseModelSpec(
                name="Post",
                table_name="posts",
                fields={
                    "id": {"type": "Integer", "primary_key": True},
                    "title": {"type": "String", "nullable": False},
                    "content": {"type": "Text", "nullable": True},
                    "user_id": {"type": "Integer", "nullable": False}
                },
                relationships={"user": "User"}
            )
        ]
        
        result = self.backend_tools.generate_sqlalchemy_models(models)
        
        assert result["status"] == "success"
        assert "User" in result["models_generated"]
        assert "Post" in result["models_generated"]
        assert result["models_count"] == 2
        
        # Verify files were created
        output_dir = self.test_project_path / "output" / "generated_code" / "backend" / "database"
        assert (output_dir / "models.py").exists()
        assert (output_dir / "database.py").exists()
        assert (output_dir.parent / "alembic.ini").exists()
        
        # Verify model content
        models_content = (output_dir / "models.py").read_text()
        assert "class User(Base):" in models_content
        assert "class Post(Base):" in models_content
        assert "__tablename__ = \"users\"" in models_content
        assert "__tablename__ = \"posts\"" in models_content
        assert "primary_key=True" in models_content
        assert "nullable=False" in models_content
        assert "relationship(" in models_content
        
        # Verify database setup
        database_content = (output_dir / "database.py").read_text()
        assert "create_engine" in database_content
        assert "SessionLocal" in database_content
        assert "get_db" in database_content
    
    @patch('crews.backend.backend_crew.Crew')
    @patch('crews.backend.backend_crew.Task')
    def test_backend_crew_with_real_tools(self, mock_task, mock_crew):
        """Test backend crew with real backend tools"""
        # Patch the backend tools in the crew to use our real instance
        with patch('crews.backend.backend_crew.BackendTools') as mock_backend_tools:
            mock_backend_tools.return_value = self.backend_tools
            
            crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
            
            # Test API generation
            endpoints = [
                APIEndpointSpec(
                    name="Get Items",
                    method="GET", 
                    path="/api/v1/items",
                    description="Get all items",
                    response_model="ItemList"
                )
            ]
            
            result = crew.generate_api_endpoints("integration_app", endpoints)
            
            assert result["status"] == "success"
            assert result["app_name"] == "integration_app"
            assert crew.performance_metrics["apis_generated"] == 1
            assert crew.performance_metrics["total_endpoints"] == 1
            
            # Verify files were actually created
            output_dir = self.test_project_path / "output" / "generated_code" / "backend" / "integration_app"
            assert (output_dir / "main.py").exists()
            assert (output_dir / "models.py").exists()
            
            # Test database model generation
            models = [
                DatabaseModelSpec(
                    name="Item",
                    table_name="items",
                    fields={
                        "id": {"type": "Integer", "primary_key": True},
                        "name": {"type": "String", "nullable": False}
                    }
                )
            ]
            
            result = crew.generate_database_models(models)
            
            assert result["status"] == "success"
            assert crew.performance_metrics["models_generated"] == 1
            assert crew.performance_metrics["total_models"] == 1
            
            # Verify database files were created
            db_output_dir = self.test_project_path / "output" / "generated_code" / "backend" / "database"
            assert (db_output_dir / "models.py").exists()
            assert (db_output_dir / "database.py").exists()
    
    def test_backend_tools_error_handling(self):
        """Test backend tools error handling with real file operations"""
        # Test with invalid directory
        invalid_tools = BackendTools("/invalid/path", self.logger)
        
        endpoints = [
            APIEndpointSpec(
                name="Test",
                method="GET",
                path="/test",
                description="Test endpoint"
            )
        ]
        
        # This should still work as it creates directories
        result = invalid_tools.generate_fastapi_boilerplate("test_app", endpoints)
        assert result["status"] == "success"  # Creates directories as needed
        
        # Test with malformed endpoint specs
        malformed_endpoints = [
            APIEndpointSpec(
                name="",  # Empty name
                method="INVALID",  # Invalid method
                path="",  # Empty path
                description=""
            )
        ]
        
        result = self.backend_tools.generate_fastapi_boilerplate("test_app", malformed_endpoints)
        assert result["status"] == "success"  # Should handle gracefully
    
    def test_backend_crew_workspace_integration(self):
        """Test backend crew workspace integration"""
        with patch('crews.backend.backend_crew.BackendTools') as mock_backend_tools:
            mock_backend_tools.return_value = self.backend_tools
            
            with patch('crews.backend.backend_crew.Crew') as mock_crew:
                crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
                
                # Check that workspace was created
                workspace_path = self.test_project_path / "dev-agent-system" / "workspace" / "backend"
                assert workspace_path.exists()
                assert (workspace_path / "runtime.md").exists()
                
                # Test runtime context update
                crew.update_runtime_context()
                
                runtime_content = (workspace_path / "runtime.md").read_text()
                assert "Backend Crew Runtime Context" in runtime_content
                assert crew.crew_status in runtime_content
                assert "APIAgent" in runtime_content
                assert "DatabaseAgent" in runtime_content
    
    def test_backend_crew_performance_metrics(self):
        """Test backend crew performance metrics tracking"""
        with patch('crews.backend.backend_crew.BackendTools') as mock_backend_tools:
            mock_backend_tools.return_value = self.backend_tools
            
            with patch('crews.backend.backend_crew.Crew') as mock_crew:
                with patch('crews.backend.backend_crew.Task') as mock_task:
                    crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
                    
                    # Test API generation metrics
                    endpoints = [
                        APIEndpointSpec(name="Test1", method="GET", path="/test1", description="Test1"),
                        APIEndpointSpec(name="Test2", method="POST", path="/test2", description="Test2")
                    ]
                    
                    result = crew.generate_api_endpoints("metrics_app", endpoints)
                    
                    assert result["status"] == "success"
                    metrics = crew.performance_metrics
                    assert metrics["apis_generated"] == 1
                    assert metrics["total_endpoints"] == 2
                    
                    # Test database model metrics
                    models = [
                        DatabaseModelSpec(name="Model1", table_name="table1", fields={"id": "Integer"}),
                        DatabaseModelSpec(name="Model2", table_name="table2", fields={"id": "Integer"}),
                        DatabaseModelSpec(name="Model3", table_name="table3", fields={"id": "Integer"})
                    ]
                    
                    result = crew.generate_database_models(models)
                    
                    assert result["status"] == "success"
                    metrics = crew.performance_metrics
                    assert metrics["models_generated"] == 1
                    assert metrics["total_models"] == 3
                    
                    # Test combined metrics
                    status = crew.get_crew_status()
                    assert status["performance_metrics"]["apis_generated"] == 1
                    assert status["performance_metrics"]["models_generated"] == 1
                    assert status["performance_metrics"]["total_endpoints"] == 2
                    assert status["performance_metrics"]["total_models"] == 3
    
    def test_backend_crew_health_monitoring(self):
        """Test backend crew health monitoring"""
        with patch('crews.backend.backend_crew.BackendTools') as mock_backend_tools:
            mock_backend_tools.return_value = self.backend_tools
            
            with patch('crews.backend.backend_crew.Crew') as mock_crew:
                crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
                
                # Test healthy state
                health = crew.health_check()
                assert health["status"] == "healthy"
                assert health["checks"]["crew_initialization"] is True
                assert health["checks"]["api_agent"] is True
                assert health["checks"]["db_agent"] is True
                assert health["checks"]["backend_tools"] is True
                
                # Test with errors
                crew.crew_health["errors"].append("Test error")
                health = crew.health_check()
                assert health["status"] == "warning"
                assert "Test error" in health["issues"]
                
                # Test error state
                crew.crew_status = "error"
                health = crew.health_check()
                assert health["status"] == "critical"
                assert "Crew is in error state" in health["issues"]
    
    def test_end_to_end_backend_workflow(self):
        """Test complete end-to-end backend workflow"""
        with patch('crews.backend.backend_crew.BackendTools') as mock_backend_tools:
            mock_backend_tools.return_value = self.backend_tools
            
            with patch('crews.backend.backend_crew.Crew') as mock_crew:
                with patch('crews.backend.backend_crew.Task') as mock_task:
                    crew = BackendCrew(self.mock_config_loader, self.mock_agent_factory)
                    
                    # Step 1: Generate API endpoints
                    endpoints = [
                        APIEndpointSpec(
                            name="List Users",
                            method="GET",
                            path="/api/v1/users",
                            description="Get all users",
                            response_model="UserList",
                            tags=["users"]
                        ),
                        APIEndpointSpec(
                            name="Create User",
                            method="POST",
                            path="/api/v1/users",
                            description="Create a new user",
                            request_model="UserCreate",
                            response_model="UserResponse",
                            auth_required=True,
                            tags=["users"]
                        )
                    ]
                    
                    api_result = crew.generate_api_endpoints("e2e_app", endpoints)
                    assert api_result["status"] == "success"
                    
                    # Step 2: Generate database models
                    models = [
                        DatabaseModelSpec(
                            name="User",
                            table_name="users",
                            fields={
                                "id": {"type": "Integer", "primary_key": True},
                                "email": {"type": "String", "nullable": False},
                                "name": {"type": "String", "nullable": True}
                            }
                        )
                    ]
                    
                    db_result = crew.generate_database_models(models)
                    assert db_result["status"] == "success"
                    
                    # Step 3: Verify all files were created
                    api_output_dir = self.test_project_path / "output" / "generated_code" / "backend" / "e2e_app"
                    db_output_dir = self.test_project_path / "output" / "generated_code" / "backend" / "database"
                    
                    assert (api_output_dir / "main.py").exists()
                    assert (api_output_dir / "models.py").exists()
                    assert (api_output_dir / "routers" / "users.py").exists()
                    assert (db_output_dir / "models.py").exists()
                    assert (db_output_dir / "database.py").exists()
                    
                    # Step 4: Verify metrics
                    final_status = crew.get_crew_status()
                    assert final_status["performance_metrics"]["apis_generated"] == 1
                    assert final_status["performance_metrics"]["models_generated"] == 1
                    assert final_status["performance_metrics"]["total_endpoints"] == 2
                    assert final_status["performance_metrics"]["total_models"] == 1
                    
                    # Step 5: Verify crew health
                    health = crew.health_check()
                    assert health["status"] == "healthy"
                    
                    # Step 6: Test shutdown
                    crew.shutdown()
                    assert crew.crew_status == "shutdown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])