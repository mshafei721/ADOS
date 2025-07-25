"""
Integration Tests for Security Crew Implementation
Tests for SecurityCrew integration with other components
"""

import pytest
import logging
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Import modules under test
from tools.security_tools import SecurityTools, AuthSpec, OAuth2Spec, VulnerabilitySpec, ThreatModelSpec
from crews.security.security_crew import SecurityCrew
from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory


class TestSecurityToolsIntegration:
    """Integration tests for SecurityTools with filesystem and external tools"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def security_tools(self, temp_project_dir):
        """Create SecurityTools instance with temporary directory"""
        logger = logging.getLogger("test_integration")
        return SecurityTools(project_root=temp_project_dir, logger=logger)
    
    @pytest.fixture
    def auth_spec(self):
        """Create AuthSpec for testing"""
        return AuthSpec(
            auth_type="jwt",
            issuer="test_issuer",
            audience="test_audience",
            secret_key="test_secret_key_1234567890",
            algorithm="HS256",
            access_token_expire=30,
            refresh_token_expire=7,
            password_hash_method="bcrypt"
        )
    
    def test_jwt_auth_system_file_creation(self, security_tools, auth_spec, temp_project_dir):
        """Test that JWT auth system files are actually created"""
        result = security_tools.generate_jwt_auth_system(auth_spec)
        
        assert result["status"] == "success"
        
        # Check that output directory exists
        output_dir = Path(temp_project_dir) / "output/generated_code/security/auth"
        assert output_dir.exists()
        
        # Check that all expected files exist
        expected_files = [
            "jwt_handler.py",
            "auth_middleware.py", 
            "password_utils.py",
            "auth_models.py",
            "auth_router.py",
            "security_config.py"
        ]
        
        for file_name in expected_files:
            file_path = output_dir / file_name
            assert file_path.exists(), f"File {file_name} should exist"
            assert file_path.stat().st_size > 0, f"File {file_name} should not be empty"
    
    def test_oauth2_system_file_creation(self, security_tools, temp_project_dir):
        """Test that OAuth2 system files are actually created"""
        oauth2_spec = OAuth2Spec(
            provider="google",
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://example.com/callback",
            scope=["openid", "email", "profile"],
            auth_url="https://accounts.google.com/o/oauth2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v1/userinfo"
        )
        
        result = security_tools.generate_oauth2_system(oauth2_spec)
        
        assert result["status"] == "success"
        
        # Check that output directory exists
        output_dir = Path(temp_project_dir) / "output/generated_code/security/oauth2"
        assert output_dir.exists()
        
        # Check that all expected files exist
        expected_files = [
            "oauth2_client.py",
            "oauth2_handlers.py",
            "oauth2_models.py",
            "oauth2_router.py"
        ]
        
        for file_name in expected_files:
            file_path = output_dir / file_name
            assert file_path.exists(), f"File {file_name} should exist"
            assert file_path.stat().st_size > 0, f"File {file_name} should not be empty"
    
    def test_vulnerability_report_creation(self, security_tools, temp_project_dir):
        """Test that vulnerability reports are actually created"""
        vuln_spec = VulnerabilitySpec(
            scan_type="dependency",
            target_path=".",
            severity_threshold="medium"
        )
        
        with patch('subprocess.run') as mock_subprocess:
            # Mock successful scan result
            mock_result = Mock()
            mock_result.stdout = json.dumps([])
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = security_tools.scan_vulnerabilities(vuln_spec)
        
        assert result["status"] == "success"
        
        # Check that output directory exists
        output_dir = Path(temp_project_dir) / "output/reports/security"
        assert output_dir.exists()
        
        # Check that report file exists
        report_files = list(output_dir.glob("vulnerability_report_dependency_*.json"))
        assert len(report_files) == 1
        
        # Check report content
        report_file = report_files[0]
        assert report_file.stat().st_size > 0
        
        with open(report_file, 'r') as f:
            report_data = json.load(f)
            assert report_data["scan_type"] == "dependency"
            assert "statistics" in report_data
            assert "vulnerabilities" in report_data
    
    def test_threat_model_report_creation(self, security_tools, temp_project_dir):
        """Test that threat model reports are actually created"""
        threat_spec = ThreatModelSpec(
            application_type="web",
            components=["frontend", "backend", "database"],
            data_flow={"input": "user", "output": "response"},
            trust_boundaries=["network", "application", "data"],
            attack_surfaces=["web", "api", "database"]
        )
        
        result = security_tools.generate_threat_model(threat_spec)
        
        assert result["status"] == "success"
        
        # Check that output directory exists
        output_dir = Path(temp_project_dir) / "output/reports/security"
        assert output_dir.exists()
        
        # Check that report file exists
        report_files = list(output_dir.glob("threat_model_web_*.json"))
        assert len(report_files) == 1
        
        # Check report content
        report_file = report_files[0]
        assert report_file.stat().st_size > 0
        
        with open(report_file, 'r') as f:
            report_data = json.load(f)
            assert report_data["application_type"] == "web"
            assert "components" in report_data
            assert "threats" in report_data
            assert "mitigations" in report_data
    
    def test_generated_jwt_handler_syntax(self, security_tools, auth_spec):
        """Test that generated JWT handler has valid Python syntax"""
        content = security_tools._generate_jwt_handler(auth_spec)
        
        # Test that the content can be compiled as Python code
        try:
            compile(content, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Generated JWT handler has invalid syntax: {e}")
    
    def test_generated_oauth2_client_syntax(self, security_tools):
        """Test that generated OAuth2 client has valid Python syntax"""
        oauth2_spec = OAuth2Spec(
            provider="google",
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://example.com/callback",
            scope=["openid"],
            auth_url="https://accounts.google.com/o/oauth2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v1/userinfo"
        )
        
        content = security_tools._generate_oauth2_client(oauth2_spec)
        
        # Test that the content can be compiled as Python code
        try:
            compile(content, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Generated OAuth2 client has invalid syntax: {e}")
    
    def test_security_config_environment_variables(self, security_tools, auth_spec):
        """Test that security config includes proper environment variable handling"""
        content = security_tools._generate_security_config(auth_spec)
        
        # Check that config includes environment variable handling
        assert "os.getenv" in content or "env_file" in content
        assert "JWT_SECRET_KEY" in content
        assert "JWT_ALGORITHM" in content
        assert "BaseSettings" in content
    
    def test_auth_models_validation(self, security_tools):
        """Test that auth models include proper validation"""
        content = security_tools._generate_auth_models()
        
        # Check that models include validation
        assert "EmailStr" in content
        assert "Field" in content
        assert "validator" in content
        assert "min_length" in content
        assert "BaseModel" in content


class TestSecurityCrewIntegration:
    """Integration tests for SecurityCrew with external dependencies"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config_loader(self):
        """Create real ConfigLoader instance"""
        # Mock the config loader with realistic agent configurations
        config_loader = Mock(spec=ConfigLoader)
        config_loader.agents = {
            "AuthAgent": {
                "role": "AuthAgent",
                "goal": "Implement secure authentication and authorization systems using JWT/OAuth2",
                "backstory": "Security engineer who prevented major breaches at financial institutions.",
                "tools": ["codegen.auth_boilerplate", "search.owasp_docs", "test.security_scanner"],
                "llm": "gpt-4",
                "max_iter": 8,
                "verbose": True
            },
            "VulnAgent": {
                "role": "VulnAgent",
                "goal": "Identify and remediate security vulnerabilities through OWASP scanning and threat modeling",
                "backstory": "Former ethical hacker turned security consultant.",
                "tools": ["test.security_scanner", "search.cve_database", "codegen.security_patches"],
                "llm": "gpt-4",
                "max_iter": 10,
                "verbose": True
            }
        }
        return config_loader
    
    @pytest.fixture
    def agent_factory(self):
        """Create mock AgentFactory"""
        factory = Mock(spec=AgentFactory)
        
        # Create mock agents with realistic behavior
        auth_agent = Mock()
        auth_agent.role = "AuthAgent"
        auth_agent.goal = "Implement secure authentication"
        
        vuln_agent = Mock()
        vuln_agent.role = "VulnAgent"  
        vuln_agent.goal = "Identify vulnerabilities"
        
        factory.create_agent.side_effect = [auth_agent, vuln_agent]
        return factory
    
    @pytest.fixture
    def security_crew(self, config_loader, agent_factory, temp_project_dir):
        """Create SecurityCrew instance with temporary directory"""
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'), \
             patch('tools.security_tools.SecurityTools.__init__') as mock_init:
            
            # Mock SecurityTools initialization
            mock_init.return_value = None
            
            crew = SecurityCrew(config_loader, agent_factory)
            crew.security_tools = SecurityTools(project_root=temp_project_dir)
            
            return crew
    
    def test_crew_initialization_with_agents(self, security_crew, agent_factory):
        """Test that crew properly initializes with agents"""
        # Verify agents were created
        assert agent_factory.create_agent.call_count == 2
        
        # Verify crew has agents
        assert hasattr(security_crew, 'auth_agent')
        assert hasattr(security_crew, 'vuln_agent')
        assert hasattr(security_crew, 'crew')
        
        # Verify crew status
        assert security_crew.crew_status == "ready"
    
    def test_workspace_setup_integration(self, security_crew, temp_project_dir):
        """Test that workspace is properly set up"""
        # Manually trigger workspace setup since it's mocked in fixture
        security_crew._setup_security_workspace()
        
        # Check that workspace directory exists
        workspace_dir = Path(temp_project_dir) / "dev-agent-system/workspace/security"
        assert workspace_dir.exists()
        
        # Check that runtime.md exists
        runtime_file = workspace_dir / "runtime.md"
        assert runtime_file.exists()
        
        # Check runtime content
        with open(runtime_file, 'r') as f:
            content = f.read()
            assert "Security Crew Runtime Context" in content
            assert "AuthAgent" in content
            assert "VulnAgent" in content
    
    def test_end_to_end_jwt_authentication(self, security_crew, temp_project_dir):
        """Test end-to-end JWT authentication generation"""
        auth_spec = AuthSpec(
            auth_type="jwt",
            issuer="test_issuer",
            audience="test_audience",
            secret_key="test_secret_key_1234567890",
            algorithm="HS256"
        )
        
        # Mock SecurityTools to use real temp directory
        security_crew.security_tools = SecurityTools(project_root=temp_project_dir)
        
        result = security_crew.generate_jwt_authentication(auth_spec)
        
        assert result["status"] == "success"
        assert result["auth_type"] == "jwt"
        
        # Verify files were created
        output_dir = Path(temp_project_dir) / "output/generated_code/security/auth"
        assert output_dir.exists()
        
        # Verify performance metrics updated
        assert security_crew.performance_metrics["auth_systems_generated"] == 1
        assert security_crew.performance_metrics["total_security_checks"] == 1
    
    def test_end_to_end_vulnerability_scanning(self, security_crew, temp_project_dir):
        """Test end-to-end vulnerability scanning"""
        vuln_spec = VulnerabilitySpec(
            scan_type="dependency",
            target_path=".",
            severity_threshold="medium"
        )
        
        # Mock SecurityTools to use real temp directory
        security_crew.security_tools = SecurityTools(project_root=temp_project_dir)
        
        with patch('subprocess.run') as mock_subprocess:
            # Mock successful scan result
            mock_result = Mock()
            mock_result.stdout = json.dumps([])
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = security_crew.scan_vulnerabilities(vuln_spec)
        
        assert result["status"] == "success"
        assert result["scan_type"] == "dependency"
        
        # Verify report was created
        output_dir = Path(temp_project_dir) / "output/reports/security"
        assert output_dir.exists()
        
        # Verify performance metrics updated
        assert security_crew.performance_metrics["vulnerability_scans"] == 1
        assert security_crew.performance_metrics["security_reports_generated"] == 1
    
    def test_comprehensive_security_assessment_integration(self, security_crew, temp_project_dir):
        """Test comprehensive security assessment integration"""
        # Mock SecurityTools to use real temp directory
        security_crew.security_tools = SecurityTools(project_root=temp_project_dir)
        
        with patch('subprocess.run') as mock_subprocess:
            # Mock successful scan results
            mock_result = Mock()
            mock_result.stdout = json.dumps([])
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = security_crew.perform_security_assessment()
        
        assert result["status"] == "success"
        assert "assessment_results" in result
        
        # Verify all scan types were performed
        results = result["assessment_results"]["results"]
        assert "dependency_scan" in results
        assert "code_scan" in results
        assert "owasp_scan" in results
        
        # Verify reports were created
        output_dir = Path(temp_project_dir) / "output/reports/security"
        assert output_dir.exists()
        
        # Should have 3 vulnerability reports (one for each scan type)
        report_files = list(output_dir.glob("vulnerability_report_*.json"))
        assert len(report_files) == 3
        
        # Verify performance metrics updated
        assert security_crew.performance_metrics["vulnerability_scans"] == 3
        assert security_crew.performance_metrics["security_reports_generated"] == 3
    
    def test_crew_health_monitoring_integration(self, security_crew):
        """Test crew health monitoring integration"""
        # Test healthy state
        health = security_crew.health_check()
        assert health["status"] == "healthy"
        
        # Test with errors
        security_crew.crew_health["errors"] = ["Integration test error"]
        health = security_crew.health_check()
        assert health["status"] == "warning"
        assert "Integration test error" in health["issues"]
        
        # Test critical state
        security_crew.crew_status = "error"
        health = security_crew.health_check()
        assert health["status"] == "critical"
    
    def test_runtime_context_updates(self, security_crew, temp_project_dir):
        """Test runtime context updates integration"""
        # Set up workspace
        workspace_dir = Path(temp_project_dir) / "dev-agent-system/workspace/security"
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Update performance metrics
        security_crew.performance_metrics["auth_systems_generated"] = 5
        security_crew.performance_metrics["vulnerability_scans"] = 3
        
        # Update runtime context
        security_crew.update_runtime_context()
        
        # Verify runtime file was updated
        runtime_file = workspace_dir / "runtime.md"
        assert runtime_file.exists()
        
        with open(runtime_file, 'r') as f:
            content = f.read()
            assert "Auth Systems Generated: 5" in content
            assert "Vulnerability Scans: 3" in content
            assert security_crew.crew_status in content
    
    def test_crew_shutdown_integration(self, security_crew, temp_project_dir):
        """Test crew shutdown integration"""
        # Set up workspace
        workspace_dir = Path(temp_project_dir) / "dev-agent-system/workspace/security"
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Add some active tasks
        security_crew.active_tasks = [Mock(), Mock()]
        
        # Shutdown crew
        security_crew.shutdown()
        
        # Verify cleanup
        assert security_crew.crew_status == "shutdown"
        assert len(security_crew.active_tasks) == 0
        
        # Verify runtime context was updated
        runtime_file = workspace_dir / "runtime.md"
        assert runtime_file.exists()
        
        with open(runtime_file, 'r') as f:
            content = f.read()
            assert "shutdown" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])