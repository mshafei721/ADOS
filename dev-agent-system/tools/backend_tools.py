"""
ADOS Backend Tools Implementation
FastAPI and SQLAlchemy code generation tools for backend crew
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import os

from pydantic import BaseModel, Field


class APIEndpointSpec(BaseModel):
    """Specification for API endpoint generation"""
    name: str = Field(..., description="Name of the endpoint")
    method: str = Field(..., description="HTTP method (GET, POST, PUT, DELETE)")
    path: str = Field(..., description="URL path")
    description: str = Field(..., description="Description of the endpoint")
    request_model: Optional[str] = Field(None, description="Request model class name")
    response_model: Optional[str] = Field(None, description="Response model class name")
    auth_required: bool = Field(False, description="Whether authentication is required")
    tags: List[str] = Field(default_factory=list, description="OpenAPI tags")


class DatabaseModelSpec(BaseModel):
    """Specification for database model generation"""
    name: str = Field(..., description="Model class name")
    table_name: str = Field(..., description="Database table name")
    fields: Dict[str, Any] = Field(..., description="Model fields and types")
    relationships: Dict[str, str] = Field(default_factory=dict, description="Model relationships")
    indexes: List[str] = Field(default_factory=list, description="Database indexes")
    constraints: List[str] = Field(default_factory=list, description="Database constraints")


class BackendTools:
    """Backend development tools for code generation and testing"""
    
    def __init__(self, project_root: str = ".", logger: Optional[logging.Logger] = None):
        """Initialize backend tools"""
        self.project_root = Path(project_root)
        self.logger = logger or logging.getLogger(__name__)
        self.templates_dir = self.project_root / "dev-agent-system" / "crews" / "backend" / "kb"
        
    def generate_fastapi_boilerplate(self, 
                                   app_name: str, 
                                   endpoints: List[APIEndpointSpec],
                                   output_dir: str = "output/generated_code") -> Dict[str, Any]:
        """Generate FastAPI boilerplate code"""
        try:
            self.logger.info(f"Generating FastAPI boilerplate for {app_name}")
            
            output_path = self.project_root / output_dir / "backend" / app_name
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate main.py
            main_content = self._generate_main_py(app_name, endpoints)
            (output_path / "main.py").write_text(main_content)
            
            # Generate router files
            router_files = self._generate_router_files(endpoints, output_path)
            
            # Generate models.py
            models_content = self._generate_pydantic_models(endpoints)
            (output_path / "models.py").write_text(models_content)
            
            # Generate requirements.txt
            requirements_content = self._generate_requirements()
            (output_path / "requirements.txt").write_text(requirements_content)
            
            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile(app_name)
            (output_path / "Dockerfile").write_text(dockerfile_content)
            
            result = {
                "status": "success",
                "app_name": app_name,
                "output_directory": str(output_path),
                "files_generated": [
                    "main.py",
                    "models.py", 
                    "requirements.txt",
                    "Dockerfile"
                ] + router_files,
                "endpoints_count": len(endpoints),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"FastAPI boilerplate generated successfully at {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate FastAPI boilerplate: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_sqlalchemy_models(self, 
                                 models: List[DatabaseModelSpec],
                                 output_dir: str = "output/generated_code") -> Dict[str, Any]:
        """Generate SQLAlchemy model classes"""
        try:
            self.logger.info(f"Generating SQLAlchemy models: {[m.name for m in models]}")
            
            output_path = self.project_root / output_dir / "backend" / "database"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate models.py
            models_content = self._generate_sqlalchemy_models_content(models)
            (output_path / "models.py").write_text(models_content)
            
            # Generate database.py (connection setup)
            database_content = self._generate_database_setup()
            (output_path / "database.py").write_text(database_content)
            
            # Generate alembic.ini
            alembic_content = self._generate_alembic_config()
            (output_path.parent / "alembic.ini").write_text(alembic_content)
            
            # Generate migration script template
            migration_dir = output_path / "migrations"
            migration_dir.mkdir(exist_ok=True)
            
            result = {
                "status": "success",
                "models_generated": [m.name for m in models],
                "output_directory": str(output_path),
                "files_generated": [
                    "models.py",
                    "database.py",
                    "../alembic.ini"
                ],
                "models_count": len(models),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"SQLAlchemy models generated successfully at {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate SQLAlchemy models: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_pytest_tests(self, 
                        test_directory: str = "tests",
                        pattern: str = "test_*.py",
                        verbose: bool = True) -> Dict[str, Any]:
        """Run pytest tests and return results"""
        try:
            import subprocess
            import sys
            
            self.logger.info(f"Running pytest tests in {test_directory}")
            
            test_path = self.project_root / test_directory
            if not test_path.exists():
                return {"status": "error", "error": f"Test directory {test_directory} does not exist"}
            
            # Build pytest command
            cmd = [sys.executable, "-m", "pytest", str(test_path)]
            
            if verbose:
                cmd.append("-v")
            
            cmd.extend(["-k", pattern.replace("test_", "").replace(".py", "")])
            
            # Run tests
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            test_result = {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
                "test_directory": test_directory,
                "timestamp": datetime.now().isoformat()
            }
            
            # Parse test results
            if result.stdout:
                test_result["summary"] = self._parse_pytest_output(result.stdout)
            
            if result.returncode == 0:
                self.logger.info("All tests passed successfully")
            else:
                self.logger.warning(f"Tests failed with return code {result.returncode}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.logger.error("Test execution timed out")
            return {"status": "error", "error": "Test execution timed out after 5 minutes"}
        except Exception as e:
            self.logger.error(f"Failed to run pytest tests: {e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_main_py(self, app_name: str, endpoints: List[APIEndpointSpec]) -> str:
        """Generate main.py FastAPI application"""
        routers = set()
        for endpoint in endpoints:
            # Extract router name from path - handle both /api/v1/users and /users formats
            path_parts = [p for p in endpoint.path.split('/') if p]
            if len(path_parts) >= 3 and path_parts[0] == 'api' and path_parts[1].startswith('v'):
                # Handle /api/v1/users format
                router_name = path_parts[2]
            elif len(path_parts) >= 1:
                # Handle /users format or direct resource
                router_name = path_parts[-1] if not path_parts[-1].startswith('{') else path_parts[-2]
            else:
                router_name = 'default'
            routers.add(router_name)
        
        router_imports = "\n".join([f"from routers import {router}" for router in routers])
        router_includes = "\n".join([f"app.include_router({router}.router)" for router in routers])
        
        return f'''"""
{app_name} FastAPI Application
Generated by ADOS Backend Tools
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging

{router_imports}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="{app_name}",
    description="Backend API generated by ADOS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
{router_includes}

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy", "service": "{app_name}"}}

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("{app_name} API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("{app_name} API shutting down...")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _generate_router_files(self, endpoints: List[APIEndpointSpec], output_path: Path) -> List[str]:
        """Generate router files for endpoints"""
        routers_dir = output_path / "routers"
        routers_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        (routers_dir / "__init__.py").write_text("")
        
        # Group endpoints by router
        router_groups = {}
        for endpoint in endpoints:
            # Extract router name from path - handle both /api/v1/users and /users formats
            path_parts = [p for p in endpoint.path.split('/') if p]
            if len(path_parts) >= 3 and path_parts[0] == 'api' and path_parts[1].startswith('v'):
                # Handle /api/v1/users format
                router_name = path_parts[2]
            elif len(path_parts) >= 1:
                # Handle /users format or direct resource
                router_name = path_parts[-1] if not path_parts[-1].startswith('{') else path_parts[-2]
            else:
                router_name = 'default'
            
            if router_name not in router_groups:
                router_groups[router_name] = []
            router_groups[router_name].append(endpoint)
        
        router_files = []
        for router_name, router_endpoints in router_groups.items():
            router_content = self._generate_router_content(router_name, router_endpoints)
            router_file = f"{router_name}.py"
            (routers_dir / router_file).write_text(router_content)
            router_files.append(f"routers/{router_file}")
        
        return router_files
    
    def _generate_router_content(self, router_name: str, endpoints: List[APIEndpointSpec]) -> str:
        """Generate content for a specific router"""
        endpoint_functions = []
        
        for endpoint in endpoints:
            func_name = endpoint.name.lower().replace(' ', '_')
            method = endpoint.method.lower()
            
            # Generate function signature
            params = []
            if endpoint.request_model:
                params.append(f"data: {endpoint.request_model}")
            
            auth_param = ""
            if endpoint.auth_required:
                auth_param = ", token: HTTPAuthorizationCredentials = Depends(security)"
                params.append("token: HTTPAuthorizationCredentials = Depends(security)")
            
            params_str = ", ".join(params)
            
            # Generate response model
            response_annotation = f" -> {endpoint.response_model}" if endpoint.response_model else ""
            
            # Generate function
            endpoint_functions.append(f'''
@router.{method}("{endpoint.path}", tags={endpoint.tags or [router_name]})
async def {func_name}({params_str}){response_annotation}:
    """
    {endpoint.description}
    """
    # TODO: Implement {endpoint.name} logic
    return {{"message": "Not implemented yet", "endpoint": "{endpoint.name}"}}
''')
        
        return f'''"""
{router_name.title()} Router
Generated by ADOS Backend Tools
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any
import logging

from ..models import *

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

{''.join(endpoint_functions)}
'''
    
    def _generate_pydantic_models(self, endpoints: List[APIEndpointSpec]) -> str:
        """Generate Pydantic models from endpoints"""
        models = set()
        
        for endpoint in endpoints:
            if endpoint.request_model:
                models.add(endpoint.request_model)
            if endpoint.response_model:
                models.add(endpoint.response_model)
        
        model_definitions = []
        for model in models:
            model_definitions.append(f'''
class {model}(BaseModel):
    """Generated model for {model}"""
    # TODO: Define fields for {model}
    message: str = Field(..., description="Placeholder field")
''')
        
        return f'''"""
Pydantic Models
Generated by ADOS Backend Tools
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

{''.join(model_definitions)}
'''
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        return '''# FastAPI Backend Requirements
# Generated by ADOS Backend Tools

fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
'''
    
    def _generate_dockerfile(self, app_name: str) -> str:
        """Generate Dockerfile"""
        return f'''# Dockerfile for {app_name}
# Generated by ADOS Backend Tools

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _generate_sqlalchemy_models_content(self, models: List[DatabaseModelSpec]) -> str:
        """Generate SQLAlchemy models content"""
        model_definitions = []
        
        for model in models:
            fields_def = []
            for field_name, field_info in model.fields.items():
                if isinstance(field_info, dict):
                    field_type = field_info.get('type', 'String')
                    nullable = field_info.get('nullable', True)
                    primary_key = field_info.get('primary_key', False)
                    
                    field_line = f"    {field_name} = Column({field_type}"
                    if primary_key:
                        field_line += ", primary_key=True"
                    if not nullable:
                        field_line += ", nullable=False"
                    field_line += ")"
                    fields_def.append(field_line)
                else:
                    fields_def.append(f"    {field_name} = Column({field_info})")
            
            # Add relationships
            for rel_name, rel_info in model.relationships.items():
                fields_def.append(f"    {rel_name} = relationship('{rel_info}')")
            
            model_def = f'''
class {model.name}(Base):
    """Generated SQLAlchemy model for {model.name}"""
    __tablename__ = "{model.table_name}"
    
{chr(10).join(fields_def)}
'''
            model_definitions.append(model_def)
        
        return f'''"""
SQLAlchemy Models
Generated by ADOS Backend Tools
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

{''.join(model_definitions)}
'''
    
    def _generate_database_setup(self) -> str:
        """Generate database setup code"""
        return '''"""
Database Setup
Generated by ADOS Backend Tools
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/dbname"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Drop tables
def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)
'''
    
    def _generate_alembic_config(self) -> str:
        """Generate Alembic configuration"""
        return '''# Alembic Configuration
# Generated by ADOS Backend Tools

[alembic]
script_location = migrations
sqlalchemy.url = postgresql://user:password@localhost/dbname

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output to extract test results"""
        lines = output.strip().split('\n')
        
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0
        }
        
        for line in lines:
            if "passed" in line and "failed" in line:
                # Parse summary line like "5 passed, 2 failed in 1.23s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        if i + 1 < len(parts):
                            status = parts[i + 1]
                            if status.startswith("passed"):
                                summary["passed"] = int(part)
                            elif status.startswith("failed"):
                                summary["failed"] = int(part)
                            elif status.startswith("skipped"):
                                summary["skipped"] = int(part)
                            elif status.startswith("error"):
                                summary["errors"] = int(part)
        
        summary["total_tests"] = summary["passed"] + summary["failed"] + summary["skipped"] + summary["errors"]
        
        return summary
    
    def get_tool_status(self) -> Dict[str, Any]:
        """Get status of backend tools"""
        return {
            "tool_name": "BackendTools",
            "version": "1.0.0",
            "capabilities": [
                "fastapi_boilerplate_generation",
                "sqlalchemy_model_generation", 
                "pytest_test_runner"
            ],
            "project_root": str(self.project_root),
            "templates_directory": str(self.templates_dir),
            "status": "operational",
            "timestamp": datetime.now().isoformat()
        }