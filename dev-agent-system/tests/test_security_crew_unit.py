"""
Unit Tests for Security Crew Implementation
Tests for SecurityTools and SecurityCrew classes
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path
import json

# Import modules under test
from tools.security_tools import SecurityTools, AuthSpec, OAuth2Spec, VulnerabilitySpec, ThreatModelSpec
from crews.security.security_crew import SecurityCrew
from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory


class TestSecurityTools:
    """Unit tests for SecurityTools class"""
    
    @pytest.fixture
    def security_tools(self):
        """Create SecurityTools instance for testing"""
        logger = logging.getLogger("test")
        return SecurityTools(project_root="test_project", logger=logger)
    
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
    
    @pytest.fixture
    def oauth2_spec(self):
        """Create OAuth2Spec for testing"""
        return OAuth2Spec(
            provider="google",
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://example.com/callback",
            scope=["openid", "email", "profile"],
            auth_url="https://accounts.google.com/o/oauth2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v1/userinfo"
        )
    
    @pytest.fixture
    def vuln_spec(self):
        """Create VulnerabilitySpec for testing"""
        return VulnerabilitySpec(
            scan_type="dependency",
            target_path=".",
            severity_threshold="medium",
            output_format="json",
            include_dev_dependencies=False
        )
    
    @pytest.fixture
    def threat_spec(self):
        """Create ThreatModelSpec for testing"""
        return ThreatModelSpec(
            application_type="web",
            components=["frontend", "backend", "database"],
            data_flow={"input": "user", "output": "response"},
            trust_boundaries=["network", "application", "data"],
            attack_surfaces=["web", "api", "database"]
        )
    
    def test_security_tools_initialization(self, security_tools):
        """Test SecurityTools initialization"""
        assert security_tools.project_root == Path("test_project")
        assert security_tools.logger.name == "test"
        assert security_tools.templates_dir == Path("test_project/dev-agent-system/crews/security/kb")
    
    def test_get_tool_status(self, security_tools):
        """Test get_tool_status method"""
        status = security_tools.get_tool_status()
        
        assert status["tool_name"] == "SecurityTools"
        assert status["version"] == "1.0.0"
        assert "jwt_authentication" in status["capabilities"]
        assert "oauth2_authentication" in status["capabilities"]
        assert "vulnerability_scanning" in status["capabilities"]
        assert "threat_modeling" in status["capabilities"]
        assert status["status"] == "operational"
    
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_generate_jwt_auth_system_success(self, mock_write_text, mock_mkdir, security_tools, auth_spec):
        """Test successful JWT auth system generation"""
        result = security_tools.generate_jwt_auth_system(auth_spec)
        
        assert result["status"] == "success"
        assert result["auth_type"] == "jwt"
        assert result["algorithm"] == "HS256"
        assert "jwt_handler.py" in result["files_generated"]
        assert "auth_middleware.py" in result["files_generated"]
        assert "password_utils.py" in result["files_generated"]
        assert "auth_models.py" in result["files_generated"]
        assert "auth_router.py" in result["files_generated"]
        assert "security_config.py" in result["files_generated"]
        
        # Verify files were created
        assert mock_mkdir.called
        assert mock_write_text.call_count == 6  # 6 files should be created
    
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_generate_oauth2_system_success(self, mock_write_text, mock_mkdir, security_tools, oauth2_spec):
        """Test successful OAuth2 system generation"""
        result = security_tools.generate_oauth2_system(oauth2_spec)
        
        assert result["status"] == "success"
        assert result["provider"] == "google"
        assert result["scopes"] == ["openid", "email", "profile"]
        assert "oauth2_client.py" in result["files_generated"]
        assert "oauth2_handlers.py" in result["files_generated"]
        assert "oauth2_models.py" in result["files_generated"]
        assert "oauth2_router.py" in result["files_generated"]
        
        # Verify files were created
        assert mock_mkdir.called
        assert mock_write_text.call_count == 4  # 4 files should be created
    
    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_scan_dependencies_success(self, mock_write_text, mock_mkdir, mock_subprocess, security_tools, vuln_spec):
        """Test successful dependency vulnerability scan"""
        # Mock subprocess response
        mock_result = Mock()
        mock_result.stdout = json.dumps([
            {
                "package": "requests",
                "installed_version": "2.25.1",
                "id": "CVE-2023-1234",
                "severity": "medium",
                "advisory": "Test vulnerability",
                "fix": "Update to 2.28.0"
            }
        ])
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        result = security_tools.scan_vulnerabilities(vuln_spec)
        
        assert result["status"] == "success"
        assert result["scan_type"] == "dependency"
        assert result["vulnerabilities_found"] == 1
        assert mock_subprocess.called
        assert mock_write_text.called
    
    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_scan_code_success(self, mock_write_text, mock_mkdir, mock_subprocess, security_tools):
        """Test successful code vulnerability scan"""
        vuln_spec = VulnerabilitySpec(
            scan_type="code",
            target_path=".",
            severity_threshold="medium"
        )
        
        # Mock subprocess response
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "results": [
                {
                    "filename": "test.py",
                    "line_number": 10,
                    "test_id": "B101",
                    "test_name": "assert_used",
                    "issue_severity": "medium",
                    "issue_confidence": "high",
                    "issue_text": "Use of assert detected",
                    "code": "assert user_input"
                }
            ]
        })
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        result = security_tools.scan_vulnerabilities(vuln_spec)
        
        assert result["status"] == "success"
        assert result["scan_type"] == "code"
        assert result["vulnerabilities_found"] == 1
        assert mock_subprocess.called
        assert mock_write_text.called
    
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_generate_threat_model_success(self, mock_write_text, mock_mkdir, security_tools, threat_spec):
        """Test successful threat model generation"""
        result = security_tools.generate_threat_model(threat_spec)
        
        assert result["status"] == "success"
        assert result["application_type"] == "web"
        assert result["threats_identified"] > 0
        assert result["mitigations_suggested"] > 0
        assert mock_mkdir.called
        assert mock_write_text.called
    
    def test_map_safety_severity(self, security_tools):
        """Test severity mapping for safety tool"""
        assert security_tools._map_safety_severity("low") == "low"
        assert security_tools._map_safety_severity("HIGH") == "high"
        assert security_tools._map_safety_severity("unknown") == "medium"
    
    def test_analyze_threats(self, security_tools, threat_spec):
        """Test threat analysis"""
        threats = security_tools._analyze_threats(threat_spec)
        
        assert len(threats) > 0
        assert all("id" in threat for threat in threats)
        assert all("component" in threat for threat in threats)
        assert all("threat_type" in threat for threat in threats)
        assert all("severity" in threat for threat in threats)
    
    def test_generate_mitigations(self, security_tools):
        """Test mitigation generation"""
        threats = [
            {"id": "test_spoofing", "threat_type": "Spoofing", "component": "auth", "severity": "high"},
            {"id": "test_tampering", "threat_type": "Tampering", "component": "api", "severity": "medium"}
        ]
        
        mitigations = security_tools._generate_mitigations(threats)
        
        assert len(mitigations) == 2
        assert all("threat_id" in mitigation for mitigation in mitigations)
        assert all("strategy" in mitigation for mitigation in mitigations)
        assert all("priority" in mitigation for mitigation in mitigations)
    
    def test_generate_jwt_handler_content(self, security_tools, auth_spec):
        """Test JWT handler content generation"""
        content = security_tools._generate_jwt_handler(auth_spec)
        
        assert "class JWTHandler" in content
        assert "create_access_token" in content
        assert "create_refresh_token" in content
        assert "verify_token" in content
        assert auth_spec.secret_key in content
        assert auth_spec.algorithm in content
    
    def test_generate_auth_middleware_content(self, security_tools, auth_spec):
        """Test auth middleware content generation"""
        content = security_tools._generate_auth_middleware(auth_spec)
        
        assert "class AuthMiddleware" in content
        assert "get_current_user" in content
        assert "require_roles" in content
        assert "require_permissions" in content
        assert "HTTPBearer" in content
    
    def test_generate_password_utils_content(self, security_tools, auth_spec):
        """Test password utils content generation"""
        content = security_tools._generate_password_utils(auth_spec)
        
        assert "class PasswordUtils" in content
        assert "hash_password" in content
        assert "verify_password" in content
        assert "generate_password" in content
        assert "check_password_strength" in content
        assert auth_spec.password_hash_method in content
    
    def test_generate_auth_models_content(self, security_tools):
        """Test auth models content generation"""
        content = security_tools._generate_auth_models()
        
        assert "class UserLogin" in content
        assert "class UserRegister" in content
        assert "class TokenResponse" in content
        assert "class UserProfile" in content
        assert "class PasswordChange" in content
        assert "EmailStr" in content
    
    def test_generate_oauth2_client_content(self, security_tools, oauth2_spec):
        """Test OAuth2 client content generation"""
        content = security_tools._generate_oauth2_client(oauth2_spec)
        
        assert "class OAuth2Client" in content
        assert "get_authorization_url" in content
        assert "exchange_code_for_tokens" in content
        assert "get_user_info" in content
        assert oauth2_spec.provider in content
        assert oauth2_spec.client_id in content


class TestSecurityCrew:
    """Unit tests for SecurityCrew class"""
    
    @pytest.fixture
    def mock_config_loader(self):
        """Create mock ConfigLoader"""
        config_loader = Mock(spec=ConfigLoader)
        config_loader.agents = {
            "AuthAgent": {
                "role": "AuthAgent",
                "goal": "Implement secure authentication",
                "backstory": "Security expert",
                "llm": "gpt-4",
                "max_iter": 8,
                "verbose": True
            },
            "VulnAgent": {
                "role": "VulnAgent", 
                "goal": "Identify vulnerabilities",
                "backstory": "Security researcher",
                "llm": "gpt-4",
                "max_iter": 10,
                "verbose": True
            }
        }
        return config_loader
    
    @pytest.fixture
    def mock_agent_factory(self):
        """Create mock AgentFactory"""
        factory = Mock(spec=AgentFactory)
        factory.create_agent.return_value = Mock()
        return factory
    
    @pytest.fixture
    def security_crew(self, mock_config_loader, mock_agent_factory):
        """Create SecurityCrew instance for testing"""
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'), \
             patch('crews.security.security_crew.SecurityCrew._create_crew') as mock_create_crew, \
             patch('crewai.Task') as mock_task:
            
            # Mock crew creation to return a mock crew
            mock_create_crew.return_value = Mock()
            
            # Mock task creation to return a mock task
            mock_task.return_value = Mock()
            
            crew = SecurityCrew(mock_config_loader, mock_agent_factory)
            return crew
    
    def test_security_crew_initialization(self, security_crew):
        """Test SecurityCrew initialization"""
        assert security_crew.crew_status == "ready"
        assert hasattr(security_crew, 'security_tools')
        assert hasattr(security_crew, 'auth_agent')
        assert hasattr(security_crew, 'vuln_agent')
        assert hasattr(security_crew, 'crew')
        assert security_crew.performance_metrics["auth_systems_generated"] == 0
    
    def test_setup_crew_monitoring(self, security_crew):
        """Test crew monitoring setup"""
        assert security_crew.crew_health["status"] == "initializing"
        assert security_crew.crew_health["load"] == 0
        assert security_crew.crew_health["active_agents"] == 0
        assert security_crew.crew_health["tasks_in_progress"] == 0
        assert security_crew.crew_health["errors"] == []
    
    def test_setup_performance_tracking(self, security_crew):
        """Test performance tracking setup"""
        metrics = security_crew.performance_metrics
        assert metrics["auth_systems_generated"] == 0
        assert metrics["oauth2_systems_generated"] == 0
        assert metrics["vulnerability_scans"] == 0
        assert metrics["threats_identified"] == 0
        assert metrics["vulnerabilities_found"] == 0
        assert metrics["security_reports_generated"] == 0
        assert metrics["total_security_checks"] == 0
    
    @patch('pathlib.Path.write_text')
    def test_update_runtime_context(self, mock_write_text, security_crew):
        """Test runtime context update"""
        security_crew.update_runtime_context()
        
        assert mock_write_text.called
        args, kwargs = mock_write_text.call_args
        content = args[0]
        assert "Security Crew Runtime Context" in content
        assert security_crew.crew_status in content
    
    def test_get_crew_status(self, security_crew):
        """Test crew status retrieval"""
        status = security_crew.get_crew_status()
        
        assert status["crew_name"] == "security"
        assert status["status"] == "ready"
        assert "health" in status
        assert "performance_metrics" in status
        assert "agents" in status
        assert "auth_agent" in status["agents"]
        assert "vuln_agent" in status["agents"]
        assert "tools_status" in status
    
    def test_health_check_healthy(self, security_crew):
        """Test health check when crew is healthy"""
        health = security_crew.health_check()
        
        assert health["status"] == "healthy"
        assert health["checks"]["crew_initialization"] == True
        assert health["checks"]["auth_agent"] == True
        assert health["checks"]["vuln_agent"] == True
        assert health["checks"]["security_tools"] == True
        assert health["checks"]["workspace_setup"] == True
    
    def test_health_check_with_errors(self, security_crew):
        """Test health check with errors"""
        security_crew.crew_health["errors"] = ["Test error"]
        
        health = security_crew.health_check()
        
        assert health["status"] == "warning"
        assert "Test error" in health["issues"]
    
    def test_health_check_critical_status(self, security_crew):
        """Test health check with critical status"""
        security_crew.crew_status = "error"
        
        health = security_crew.health_check()
        
        assert health["status"] == "critical"
        assert "Crew is in error state" in health["issues"]
    
    @patch('tools.security_tools.SecurityTools.generate_jwt_auth_system')
    def test_generate_jwt_authentication_success(self, mock_generate, security_crew):
        """Test successful JWT authentication generation"""
        mock_generate.return_value = {"status": "success", "files_generated": ["jwt_handler.py"]}
        
        auth_spec = AuthSpec(
            auth_type="jwt",
            issuer="test",
            audience="test",
            secret_key="test_key",
            algorithm="HS256"
        )
        
        result = security_crew.generate_jwt_authentication(auth_spec)
        
        assert result["status"] == "success"
        assert security_crew.performance_metrics["auth_systems_generated"] == 1
        assert security_crew.performance_metrics["total_security_checks"] == 1
        assert mock_generate.called
    
    @patch('tools.security_tools.SecurityTools.generate_oauth2_system')
    def test_generate_oauth2_system_success(self, mock_generate, security_crew):
        """Test successful OAuth2 system generation"""
        mock_generate.return_value = {"status": "success", "provider": "google"}
        
        oauth2_spec = OAuth2Spec(
            provider="google",
            client_id="test",
            client_secret="test",
            redirect_uri="https://example.com/callback",
            scope=["openid"],
            auth_url="https://accounts.google.com/o/oauth2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v1/userinfo"
        )
        
        result = security_crew.generate_oauth2_system(oauth2_spec)
        
        assert result["status"] == "success"
        assert security_crew.performance_metrics["oauth2_systems_generated"] == 1
        assert security_crew.performance_metrics["total_security_checks"] == 1
        assert mock_generate.called
    
    @patch('tools.security_tools.SecurityTools.scan_vulnerabilities')
    def test_scan_vulnerabilities_success(self, mock_scan, security_crew):
        """Test successful vulnerability scan"""
        mock_scan.return_value = {"status": "success", "vulnerabilities_found": 5}
        
        vuln_spec = VulnerabilitySpec(
            scan_type="dependency",
            target_path=".",
            severity_threshold="medium"
        )
        
        result = security_crew.scan_vulnerabilities(vuln_spec)
        
        assert result["status"] == "success"
        assert security_crew.performance_metrics["vulnerability_scans"] == 1
        assert security_crew.performance_metrics["vulnerabilities_found"] == 5
        assert security_crew.performance_metrics["security_reports_generated"] == 1
        assert mock_scan.called
    
    @patch('tools.security_tools.SecurityTools.generate_threat_model')
    def test_generate_threat_model_success(self, mock_generate, security_crew):
        """Test successful threat model generation"""
        mock_generate.return_value = {"status": "success", "threats_identified": 10}
        
        threat_spec = ThreatModelSpec(
            application_type="web",
            components=["frontend", "backend"],
            data_flow={},
            trust_boundaries=[],
            attack_surfaces=[]
        )
        
        result = security_crew.generate_threat_model(threat_spec)
        
        assert result["status"] == "success"
        assert security_crew.performance_metrics["threats_identified"] == 10
        assert security_crew.performance_metrics["security_reports_generated"] == 1
        assert mock_generate.called
    
    @patch('crews.security.security_crew.SecurityCrew.scan_vulnerabilities')
    def test_perform_security_assessment_success(self, mock_scan, security_crew):
        """Test successful comprehensive security assessment"""
        mock_scan.return_value = {"status": "success", "vulnerabilities_found": 3}
        
        result = security_crew.perform_security_assessment()
        
        assert result["status"] == "success"
        assert "assessment_results" in result
        assert result["assessment_results"]["assessment_type"] == "comprehensive"
        assert "dependency_scan" in result["assessment_results"]["results"]
        assert "code_scan" in result["assessment_results"]["results"]
        assert "owasp_scan" in result["assessment_results"]["results"]
        assert result["assessment_results"]["summary"]["total_vulnerabilities"] == 9  # 3 * 3 scans
        assert mock_scan.call_count == 3
    
    def test_shutdown(self, security_crew):
        """Test crew shutdown"""
        security_crew.active_tasks = [Mock(), Mock()]
        
        with patch.object(security_crew, 'update_runtime_context') as mock_update:
            security_crew.shutdown()
            
            assert security_crew.crew_status == "shutdown"
            assert len(security_crew.active_tasks) == 0
            assert mock_update.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])