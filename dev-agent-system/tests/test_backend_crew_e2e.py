"""
End-to-End Tests for Backend Crew
Tests complete backend crew workflow in real system environment
"""

import pytest
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import Mock, patch

from crews.backend.backend_crew import BackendCrew
from tools.backend_tools import BackendTools, APIEndpointSpec, DatabaseModelSpec
from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory


class TestBackendCrewE2E:
    """End-to-end tests for backend crew in full system context"""
    
    def setup_method(self):
        """Setup complete test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create full directory structure
        self._create_project_structure()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("e2e_test")
        
        # Create configuration loader mock with full configuration
        self.config_loader = self._create_config_loader()
        
        # Create agent factory mock
        self.agent_factory = self._create_agent_factory()
        
        # Change to temp directory for testing
        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import os
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def _create_project_structure(self):
        """Create complete ADOS project structure"""
        # Core directories
        dirs = [
            "dev-agent-system/crews/backend/kb",
            "dev-agent-system/crews/backend/agents",
            "dev-agent-system/crews/backend/memory",
            "dev-agent-system/crews/backend/workspace",
            "dev-agent-system/workspace/backend",
            "dev-agent-system/config",
            "dev-agent-system/tools",
            "dev-agent-system/orchestrator",
            "dev-agent-system/memory/crew_memory/backend",
            "dev-agent-system/memory/global_kb",
            "dev-agent-system/output/generated_code",
            "dev-agent-system/output/logs",
            "dev-agent-system/output/reports",
            "dev-agent-system/tests",
            "tests"
        ]
        
        for dir_path in dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create knowledge base file
        kb_content = """# FastAPI Patterns and Best Practices

## API Design Principles
- RESTful design
- Proper HTTP status codes
- Comprehensive documentation
- Error handling
- Authentication and authorization

## FastAPI Features
- Automatic OpenAPI documentation
- Type hints for validation
- Dependency injection
- Async support
- Middleware support
"""
        (self.project_root / "dev-agent-system/crews/backend/kb/fastapi_patterns.md").write_text(kb_content)
        
        # Create crew config
        crew_config = """name: backend
description: "Backend development crew"
version: "1.0.0"

crew_settings:
  api_framework: "fastapi"
  database_preference: "postgresql"
  orm_choice: "sqlalchemy"
  architecture_pattern: "microservices"

validation:
  required_tools: ["codegen.fastapi_boilerplate", "codegen.sqlalchemy_models", "test.pytest_runner"]
  required_files: ["runtime.md"]
  health_check_interval: 300
"""
        (self.project_root / "dev-agent-system/crews/backend/crew_config.yaml").write_text(crew_config)
    
    def _create_config_loader(self):
        """Create mock configuration loader with full config"""
        config_loader = Mock(spec=ConfigLoader)
        
        config_loader.agents = {
            "APIAgent": {
                "role": "APIAgent",
                "goal": "Design and implement RESTful and GraphQL APIs following best practices",
                "backstory": "Backend engineer with expertise in microservices architecture",
                "tools": ["codegen.fastapi_boilerplate", "search.python_docs", "test.pytest_runner"],
                "llm": "gpt-4",
                "max_iter": 8,
                "verbose": True,
                "crew": "backend"
            },
            "DatabaseAgent": {
                "role": "DatabaseAgent",
                "goal": "Design database schemas, implement ORMs, and optimize SQL queries",
                "backstory": "Database architect who worked on high-scale systems",
                "tools": ["codegen.sqlalchemy_models", "search.database_docs", "test.db_tester"],
                "llm": "gpt-4",
                "max_iter": 8,
                "verbose": True,
                "crew": "backend"
            }
        }
        
        config_loader.crews = {
            "backend": {
                "name": "backend",
                "description": "Backend development crew",
                "agents": ["APIAgent", "DatabaseAgent"],
                "tools": ["codegen.fastapi_boilerplate", "codegen.sqlalchemy_models", "test.pytest_runner"],
                "memory_access": "./memory/crew_memory/backend",
                "workspace": "./workspace/backend"
            }
        }
        
        return config_loader
    
    def _create_agent_factory(self):
        """Create mock agent factory"""
        agent_factory = Mock(spec=AgentFactory)
        
        # Mock agents
        api_agent = Mock()
        api_agent.role = "APIAgent"
        api_agent.goal = "Design and implement RESTful APIs"
        
        db_agent = Mock()
        db_agent.role = "DatabaseAgent"
        db_agent.goal = "Design database schemas"
        
        agent_factory.create_agent.side_effect = [api_agent, db_agent]
        
        return agent_factory
    
    def test_complete_backend_application_generation(self):
        """Test complete backend application generation workflow"""
        with patch('crews.backend.backend_crew.Crew') as mock_crew:
            with patch('crews.backend.backend_crew.Task') as mock_task:
                # Initialize backend crew
                crew = BackendCrew(self.config_loader, self.agent_factory)
                
                # Define comprehensive API specification
                endpoints = [
                    APIEndpointSpec(
                        name="List Users",
                        method="GET",
                        path="/api/v1/users",
                        description="Get paginated list of users",
                        response_model="UserList",
                        tags=["users"]
                    ),
                    APIEndpointSpec(
                        name="Get User",
                        method="GET",
                        path="/api/v1/users/{user_id}",
                        description="Get user by ID",
                        response_model="UserResponse",
                        auth_required=True,
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
                    ),
                    APIEndpointSpec(
                        name="Update User",
                        method="PUT",
                        path="/api/v1/users/{user_id}",
                        description="Update existing user",
                        request_model="UserUpdate",
                        response_model="UserResponse",
                        auth_required=True,
                        tags=["users"]
                    ),
                    APIEndpointSpec(
                        name="Delete User",
                        method="DELETE",
                        path="/api/v1/users/{user_id}",
                        description="Delete user",
                        auth_required=True,
                        tags=["users"]
                    ),
                    APIEndpointSpec(
                        name="List Posts",
                        method="GET",
                        path="/api/v1/posts",
                        description="Get paginated list of posts",
                        response_model="PostList",
                        tags=["posts"]
                    ),
                    APIEndpointSpec(
                        name="Create Post",
                        method="POST",
                        path="/api/v1/posts",
                        description="Create a new post",
                        request_model="PostCreate",
                        response_model="PostResponse",
                        auth_required=True,
                        tags=["posts"]
                    )
                ]
                
                # Generate API
                api_result = crew.generate_api_endpoints("blog_api", endpoints)
                
                assert api_result["status"] == "success"
                assert api_result["app_name"] == "blog_api"
                assert api_result["endpoints_count"] == 7
                
                # Define comprehensive database schema
                models = [
                    DatabaseModelSpec(
                        name="User",
                        table_name="users",
                        fields={
                            "id": {"type": "Integer", "primary_key": True},
                            "email": {"type": "String", "nullable": False},
                            "username": {"type": "String", "nullable": False},
                            "password_hash": {"type": "String", "nullable": False},
                            "first_name": {"type": "String", "nullable": True},
                            "last_name": {"type": "String", "nullable": True},
                            "is_active": {"type": "Boolean", "nullable": False},
                            "created_at": {"type": "DateTime", "nullable": False},
                            "updated_at": {"type": "DateTime", "nullable": False}
                        },
                        relationships={"posts": "Post"},
                        indexes=["email", "username"],
                        constraints=["UNIQUE(email)", "UNIQUE(username)"]
                    ),
                    DatabaseModelSpec(
                        name="Post",
                        table_name="posts",
                        fields={
                            "id": {"type": "Integer", "primary_key": True},
                            "title": {"type": "String", "nullable": False},
                            "content": {"type": "Text", "nullable": False},
                            "excerpt": {"type": "String", "nullable": True},
                            "published": {"type": "Boolean", "nullable": False},
                            "user_id": {"type": "Integer", "nullable": False},
                            "created_at": {"type": "DateTime", "nullable": False},
                            "updated_at": {"type": "DateTime", "nullable": False}
                        },
                        relationships={"user": "User", "tags": "Tag"},
                        indexes=["user_id", "published", "created_at"],
                        constraints=["FOREIGN KEY(user_id) REFERENCES users(id)"]
                    ),
                    DatabaseModelSpec(
                        name="Tag",
                        table_name="tags",
                        fields={
                            "id": {"type": "Integer", "primary_key": True},
                            "name": {"type": "String", "nullable": False},
                            "slug": {"type": "String", "nullable": False},
                            "created_at": {"type": "DateTime", "nullable": False}
                        },
                        relationships={"posts": "Post"},
                        indexes=["slug"],
                        constraints=["UNIQUE(slug)"]
                    )
                ]
                
                # Generate database models
                db_result = crew.generate_database_models(models)
                
                assert db_result["status"] == "success"
                assert "User" in db_result["models_generated"]
                assert "Post" in db_result["models_generated"]
                assert "Tag" in db_result["models_generated"]
                assert db_result["models_count"] == 3
                
                # Verify complete application structure
                self._verify_application_structure(crew)
                
                # Verify metrics
                self._verify_performance_metrics(crew, endpoints, models)
                
                # Verify crew health
                health = crew.health_check()
                assert health["status"] == "healthy"
                
                return crew
    
    def _verify_application_structure(self, crew):
        """Verify complete application file structure"""
        # API application files
        api_dir = self.project_root / "output" / "generated_code" / "backend" / "blog_api"
        assert api_dir.exists()
        
        # Core application files
        assert (api_dir / "main.py").exists()
        assert (api_dir / "models.py").exists()
        assert (api_dir / "requirements.txt").exists()
        assert (api_dir / "Dockerfile").exists()
        
        # Router files
        routers_dir = api_dir / "routers"
        assert routers_dir.exists()
        assert (routers_dir / "users.py").exists()
        assert (routers_dir / "posts.py").exists()
        
        # Database files
        db_dir = self.project_root / "output" / "generated_code" / "backend" / "database"
        assert db_dir.exists()
        assert (db_dir / "models.py").exists()
        assert (db_dir / "database.py").exists()
        assert (db_dir.parent / "alembic.ini").exists()
        
        # Workspace files
        workspace_dir = self.project_root / "dev-agent-system" / "workspace" / "backend"
        assert workspace_dir.exists()
        assert (workspace_dir / "runtime.md").exists()
        
        # Verify file contents
        self._verify_file_contents(api_dir, db_dir)
    
    def _verify_file_contents(self, api_dir, db_dir):
        """Verify generated file contents"""
        # Verify main.py
        main_content = (api_dir / "main.py").read_text()
        assert "blog_api" in main_content
        assert "FastAPI" in main_content
        assert "from routers import users" in main_content
        assert "from routers import posts" in main_content
        assert "app.include_router(users.router)" in main_content
        assert "app.include_router(posts.router)" in main_content
        assert "/health" in main_content
        
        # Verify models.py
        models_content = (api_dir / "models.py").read_text()
        assert "UserList" in models_content
        assert "UserCreate" in models_content
        assert "UserUpdate" in models_content
        assert "UserResponse" in models_content
        assert "PostList" in models_content
        assert "PostCreate" in models_content
        assert "PostResponse" in models_content
        
        # Verify requirements.txt
        requirements_content = (api_dir / "requirements.txt").read_text()
        assert "fastapi" in requirements_content
        assert "uvicorn" in requirements_content
        assert "sqlalchemy" in requirements_content
        assert "alembic" in requirements_content
        assert "psycopg2-binary" in requirements_content
        assert "pytest" in requirements_content
        
        # Verify Dockerfile
        dockerfile_content = (api_dir / "Dockerfile").read_text()
        assert "FROM python:3.11-slim" in dockerfile_content
        assert "COPY requirements.txt" in dockerfile_content
        assert "pip install" in dockerfile_content
        assert "EXPOSE 8000" in dockerfile_content
        assert "uvicorn" in dockerfile_content
        
        # Verify router files
        users_router = (api_dir / "routers" / "users.py").read_text()
        assert "router.get" in users_router
        assert "router.post" in users_router
        assert "router.put" in users_router
        assert "router.delete" in users_router
        assert "/api/v1/users" in users_router
        
        posts_router = (api_dir / "routers" / "posts.py").read_text()
        assert "router.get" in posts_router
        assert "router.post" in posts_router
        assert "/api/v1/posts" in posts_router
        
        # Verify database models
        db_models_content = (db_dir / "models.py").read_text()
        assert "class User(Base):" in db_models_content
        assert "class Post(Base):" in db_models_content
        assert "class Tag(Base):" in db_models_content
        assert "__tablename__ = \"users\"" in db_models_content
        assert "__tablename__ = \"posts\"" in db_models_content
        assert "__tablename__ = \"tags\"" in db_models_content
        assert "relationship(" in db_models_content
        assert "primary_key=True" in db_models_content
        assert "nullable=False" in db_models_content
        
        # Verify database setup
        database_content = (db_dir / "database.py").read_text()
        assert "create_engine" in database_content
        assert "SessionLocal" in database_content
        assert "get_db" in database_content
        assert "create_tables" in database_content
        assert "drop_tables" in database_content
        
        # Verify alembic config
        alembic_content = (db_dir.parent / "alembic.ini").read_text()
        assert "[alembic]" in alembic_content
        assert "script_location = migrations" in alembic_content
        assert "sqlalchemy.url" in alembic_content
    
    def _verify_performance_metrics(self, crew, endpoints, models):
        """Verify performance metrics tracking"""
        metrics = crew.performance_metrics
        
        assert metrics["apis_generated"] == 1
        assert metrics["models_generated"] == 1
        assert metrics["total_endpoints"] == len(endpoints)
        assert metrics["total_models"] == len(models)
        
        # Verify crew status
        status = crew.get_crew_status()
        assert status["crew_name"] == "backend"
        assert status["status"] == "ready"
        assert status["active_tasks"] == 0
        assert status["completed_tasks"] == 2  # API generation + Model generation
        
        # Verify agent status
        assert status["agents"]["api_agent"]["status"] == "active"
        assert status["agents"]["api_agent"]["role"] == "APIAgent"
        assert status["agents"]["db_agent"]["status"] == "active"
        assert status["agents"]["db_agent"]["role"] == "DatabaseAgent"
        
        # Verify tools status
        tools_status = status["tools_status"]
        assert tools_status["tool_name"] == "BackendTools"
        assert tools_status["status"] == "operational"
        assert "fastapi_boilerplate_generation" in tools_status["capabilities"]
        assert "sqlalchemy_model_generation" in tools_status["capabilities"]
        assert "pytest_test_runner" in tools_status["capabilities"]
    
    def test_backend_crew_error_recovery(self):
        """Test backend crew error handling and recovery"""
        with patch('crews.backend.backend_crew.Crew') as mock_crew:
            crew = BackendCrew(self.config_loader, self.agent_factory)
            
            # Test API generation error
            with patch.object(crew.backend_tools, 'generate_fastapi_boilerplate') as mock_generate:
                mock_generate.side_effect = Exception("API generation failed")
                
                endpoints = [
                    APIEndpointSpec(
                        name="Test",
                        method="GET",
                        path="/test",
                        description="Test endpoint"
                    )
                ]
                
                result = crew.generate_api_endpoints("test_app", endpoints)
                
                assert result["status"] == "error"
                assert "API generation failed" in result["error"]
                assert crew.crew_status == "error"
                
                # Verify error is tracked in health
                health = crew.health_check()
                assert health["status"] == "critical"
                assert "Crew is in error state" in health["issues"]
            
            # Test recovery after error
            with patch.object(crew.backend_tools, 'generate_fastapi_boilerplate') as mock_generate:
                mock_generate.return_value = {"status": "success", "app_name": "recovery_app", "endpoints_count": 1}
                
                # Reset crew status
                crew.crew_status = "ready"
                crew.crew_health["errors"] = []
                
                result = crew.generate_api_endpoints("recovery_app", endpoints)
                
                assert result["status"] == "success"
                assert crew.crew_status == "ready"
                
                health = crew.health_check()
                assert health["status"] == "healthy"
    
    def test_backend_crew_concurrent_operations(self):
        """Test backend crew handling concurrent operations"""
        with patch('crews.backend.backend_crew.Crew') as mock_crew:
            with patch('crews.backend.backend_crew.Task') as mock_task:
                crew = BackendCrew(self.config_loader, self.agent_factory)
                
                # Simulate concurrent API and database operations
                endpoints = [
                    APIEndpointSpec(name="API1", method="GET", path="/api1", description="API 1"),
                    APIEndpointSpec(name="API2", method="POST", path="/api2", description="API 2")
                ]
                
                models = [
                    DatabaseModelSpec(name="Model1", table_name="table1", fields={"id": "Integer"}),
                    DatabaseModelSpec(name="Model2", table_name="table2", fields={"id": "Integer"})
                ]
                
                # Generate API first
                api_result = crew.generate_api_endpoints("concurrent_app", endpoints)
                assert api_result["status"] == "success"
                
                # Generate models while API might still be "active"
                db_result = crew.generate_database_models(models)
                assert db_result["status"] == "success"
                
                # Verify both operations completed successfully
                metrics = crew.performance_metrics
                assert metrics["apis_generated"] == 1
                assert metrics["models_generated"] == 1
                assert metrics["total_endpoints"] == 2
                assert metrics["total_models"] == 2
                
                # Verify crew is still healthy
                health = crew.health_check()
                assert health["status"] == "healthy"
    
    def test_backend_crew_shutdown_and_cleanup(self):
        """Test backend crew shutdown and cleanup"""
        with patch('crews.backend.backend_crew.Crew') as mock_crew:
            crew = BackendCrew(self.config_loader, self.agent_factory)
            
            # Perform some operations
            endpoints = [APIEndpointSpec(name="Test", method="GET", path="/test", description="Test")]
            api_result = crew.generate_api_endpoints("shutdown_test", endpoints)
            assert api_result["status"] == "success"
            
            # Verify crew is active
            assert crew.crew_status == "ready"
            assert crew.performance_metrics["apis_generated"] == 1
            
            # Shutdown crew
            crew.shutdown()
            
            # Verify shutdown state
            assert crew.crew_status == "shutdown"
            assert len(crew.active_tasks) == 0
            
            # Verify runtime context was updated
            workspace_dir = self.project_root / "dev-agent-system" / "workspace" / "backend"
            runtime_content = (workspace_dir / "runtime.md").read_text()
            assert "Backend Crew Runtime Context" in runtime_content
            assert "shutdown" in runtime_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])