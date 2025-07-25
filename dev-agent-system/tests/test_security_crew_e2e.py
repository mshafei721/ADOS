"""
End-to-End Tests for Security Crew Implementation
Full system tests for SecurityCrew in realistic scenarios
"""

import pytest
import logging
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Import modules under test
from tools.security_tools import SecurityTools, AuthSpec, OAuth2Spec, VulnerabilitySpec, ThreatModelSpec
from crews.security.security_crew import SecurityCrew
from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory


class TestSecurityCrewE2E:
    """End-to-end tests for SecurityCrew in realistic scenarios"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing"""
        temp_dir = tempfile.mkdtemp()
        # Create a realistic project structure
        project_path = Path(temp_dir)
        
        # Create source files
        src_dir = project_path / "src"
        src_dir.mkdir()
        
        # Create a sample Python file with potential security issues
        sample_code = '''
import os
import subprocess
import sqlite3

# Potential security issues for testing
def vulnerable_function(user_input):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def command_injection(user_command):
    # Command injection vulnerability
    os.system(f"echo {user_command}")

def weak_crypto():
    # Weak cryptography
    import hashlib
    password = "admin123"
    return hashlib.md5(password.encode()).hexdigest()

# Good security practices
def secure_function(user_input):
    # Parameterized query
    query = "SELECT * FROM users WHERE name = ?"
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, (user_input,))
    return cursor.fetchall()
'''
        
        (src_dir / "app.py").write_text(sample_code)
        
        # Create requirements.txt with some packages
        requirements = '''
flask==2.0.1
requests==2.25.1
django==3.2.5
numpy==1.21.0
'''
        (project_path / "requirements.txt").write_text(requirements)
        
        # Create pyproject.toml
        pyproject = '''
[tool.poetry]
name = "test-project"
version = "0.1.0"
description = "Test project for security crew"

[tool.poetry.dependencies]
python = "^3.9"
flask = "^2.0.1"
requests = "^2.25.1"
'''
        (project_path / "pyproject.toml").write_text(pyproject)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def realistic_config_loader(self):
        """Create realistic ConfigLoader with full agent configurations"""
        config_loader = Mock(spec=ConfigLoader)
        config_loader.agents = {
            "AuthAgent": {
                "role": "AuthAgent",
                "goal": "Implement secure authentication and authorization systems using JWT/OAuth2",
                "backstory": "Security engineer who prevented major breaches at financial institutions. Paranoid about security but pragmatic about usability.",
                "tools": [
                    "codegen.auth_boilerplate",
                    "search.owasp_docs", 
                    "test.security_scanner"
                ],
                "llm": "gpt-4",
                "max_iter": 8,
                "verbose": True
            },
            "VulnAgent": {
                "role": "VulnAgent",
                "goal": "Identify and remediate security vulnerabilities through OWASP scanning and threat modeling",
                "backstory": "Former ethical hacker turned security consultant. Thinks like an attacker to build better defenses.",
                "tools": [
                    "test.security_scanner",
                    "search.cve_database",
                    "codegen.security_patches"
                ],
                "llm": "gpt-4",
                "max_iter": 10,
                "verbose": True
            }
        }
        return config_loader
    
    @pytest.fixture
    def realistic_agent_factory(self):
        """Create realistic AgentFactory with proper agent creation"""
        factory = Mock(spec=AgentFactory)
        
        # Create realistic mock agents
        def create_agent(name, role, goal, backstory, tools, llm, max_iter, verbose):
            agent = Mock()
            agent.name = name
            agent.role = role
            agent.goal = goal
            agent.backstory = backstory
            agent.tools = tools
            agent.llm = llm
            agent.max_iter = max_iter
            agent.verbose = verbose
            return agent
        
        factory.create_agent = create_agent
        return factory
    
    @pytest.fixture
    def security_crew(self, realistic_config_loader, realistic_agent_factory, temp_project_dir):
        """Create SecurityCrew instance for end-to-end testing"""
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'):
            
            crew = SecurityCrew(realistic_config_loader, realistic_agent_factory)
            crew.security_tools = SecurityTools(project_root=temp_project_dir)
            
            return crew
    
    def test_full_authentication_system_generation(self, security_crew, temp_project_dir):
        """Test complete authentication system generation workflow"""
        # Define authentication requirements
        auth_spec = AuthSpec(
            auth_type="jwt",
            issuer="test-company",
            audience="test-app",
            secret_key="super_secret_key_for_testing_1234567890",
            algorithm="HS256",
            access_token_expire=30,
            refresh_token_expire=7,
            password_hash_method="bcrypt"
        )
        
        # Generate JWT authentication system
        result = security_crew.generate_jwt_authentication(auth_spec)
        
        assert result["status"] == "success"
        assert result["auth_type"] == "jwt"
        assert result["algorithm"] == "HS256"
        
        # Verify complete file structure was created
        auth_dir = Path(temp_project_dir) / "output/generated_code/security/auth"
        assert auth_dir.exists()
        
        expected_files = [
            "jwt_handler.py",
            "auth_middleware.py",
            "password_utils.py", 
            "auth_models.py",
            "auth_router.py",
            "security_config.py"
        ]
        
        for file_name in expected_files:
            file_path = auth_dir / file_name
            assert file_path.exists(), f"Missing file: {file_name}"
            
            # Verify file content is substantial
            assert file_path.stat().st_size > 1000, f"File {file_name} seems too small"
            
            # Verify file contains expected classes/functions
            content = file_path.read_text()
            if file_name == "jwt_handler.py":
                assert "class JWTHandler" in content
                assert "create_access_token" in content
                assert "verify_token" in content
            elif file_name == "auth_middleware.py":
                assert "class AuthMiddleware" in content
                assert "get_current_user" in content
            elif file_name == "password_utils.py":
                assert "class PasswordUtils" in content
                assert "hash_password" in content
                assert "verify_password" in content
        
        # Verify performance metrics
        assert security_crew.performance_metrics["auth_systems_generated"] == 1
        assert security_crew.performance_metrics["total_security_checks"] == 1
        
        # Verify crew health
        health = security_crew.health_check()
        assert health["status"] == "healthy"
    
    def test_oauth2_system_generation_workflow(self, security_crew, temp_project_dir):
        """Test complete OAuth2 system generation workflow"""
        # Define OAuth2 requirements for Google
        oauth2_spec = OAuth2Spec(
            provider="google",
            client_id="test_google_client_id",
            client_secret="test_google_client_secret",
            redirect_uri="https://myapp.com/auth/google/callback",
            scope=["openid", "email", "profile"],
            auth_url="https://accounts.google.com/o/oauth2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v1/userinfo"
        )
        
        # Generate OAuth2 system
        result = security_crew.generate_oauth2_system(oauth2_spec)
        
        assert result["status"] == "success"
        assert result["provider"] == "google"
        assert result["scopes"] == ["openid", "email", "profile"]
        
        # Verify complete file structure was created
        oauth2_dir = Path(temp_project_dir) / "output/generated_code/security/oauth2"
        assert oauth2_dir.exists()
        
        expected_files = [
            "oauth2_client.py",
            "oauth2_handlers.py",
            "oauth2_models.py",
            "oauth2_router.py"
        ]
        
        for file_name in expected_files:
            file_path = oauth2_dir / file_name
            assert file_path.exists(), f"Missing file: {file_name}"
            
            # Verify file content is substantial
            assert file_path.stat().st_size > 1000, f"File {file_name} seems too small"
            
            # Verify file contains expected classes/functions
            content = file_path.read_text()
            if file_name == "oauth2_client.py":
                assert "class OAuth2Client" in content
                assert "get_authorization_url" in content
                assert "exchange_code_for_tokens" in content
            elif file_name == "oauth2_handlers.py":
                assert "class OAuth2Handler" in content
                assert "handle_oauth2_callback" in content
        
        # Verify performance metrics
        assert security_crew.performance_metrics["oauth2_systems_generated"] == 1
        assert security_crew.performance_metrics["total_security_checks"] == 1
    
    def test_comprehensive_vulnerability_assessment(self, security_crew, temp_project_dir):
        """Test comprehensive vulnerability assessment workflow"""
        # Mock external security tools
        with patch('subprocess.run') as mock_subprocess:
            # Mock different responses for different scan types
            def mock_subprocess_side_effect(cmd, *args, **kwargs):
                if "safety" in cmd:
                    # Mock dependency scan results
                    result = Mock()
                    result.stdout = json.dumps([
                        {
                            "package": "flask",
                            "installed_version": "2.0.1",
                            "id": "CVE-2023-30861",
                            "severity": "medium",
                            "advisory": "Flask vulnerability in cookie handling",
                            "fix": "Update to Flask 2.3.0 or later"
                        },
                        {
                            "package": "requests",
                            "installed_version": "2.25.1", 
                            "id": "CVE-2023-32681",
                            "severity": "high",
                            "advisory": "Requests vulnerability in proxy handling",
                            "fix": "Update to requests 2.31.0 or later"
                        }
                    ])
                    result.stderr = ""
                    result.returncode = 0
                    return result
                elif "bandit" in cmd:
                    # Mock code scan results
                    result = Mock()
                    result.stdout = json.dumps({
                        "results": [
                            {
                                "filename": "src/app.py",
                                "line_number": 10,
                                "test_id": "B608",
                                "test_name": "hardcoded_sql_expressions",
                                "issue_severity": "medium",
                                "issue_confidence": "high",
                                "issue_text": "Possible SQL injection vector through string-based query construction",
                                "code": "query = f\"SELECT * FROM users WHERE name = '{user_input}'\""
                            },
                            {
                                "filename": "src/app.py",
                                "line_number": 16,
                                "test_id": "B605",
                                "test_name": "start_process_with_a_shell",
                                "issue_severity": "high",
                                "issue_confidence": "high",
                                "issue_text": "Starting a process with a shell: Seems safe, but may be changed in the future",
                                "code": "os.system(f\"echo {user_command}\")"
                            },
                            {
                                "filename": "src/app.py",
                                "line_number": 21,
                                "test_id": "B303",
                                "test_name": "md5_hash",
                                "issue_severity": "medium",
                                "issue_confidence": "high",
                                "issue_text": "Use of insecure MD5 hash function",
                                "code": "hashlib.md5(password.encode()).hexdigest()"
                            }
                        ]
                    })
                    result.stderr = ""
                    result.returncode = 0
                    return result
                else:
                    # Default mock response
                    result = Mock()
                    result.stdout = ""
                    result.stderr = ""
                    result.returncode = 0
                    return result
            
            mock_subprocess.side_effect = mock_subprocess_side_effect
            
            # Perform comprehensive security assessment
            result = security_crew.perform_security_assessment(target_path=temp_project_dir)
        
        assert result["status"] == "success"
        assert "assessment_results" in result
        
        assessment = result["assessment_results"]
        assert assessment["assessment_type"] == "comprehensive"
        assert assessment["target_path"] == temp_project_dir
        
        # Verify all scan types were performed
        assert "dependency_scan" in assessment["results"]
        assert "code_scan" in assessment["results"]
        assert "owasp_scan" in assessment["results"]
        
        # Verify summary includes vulnerabilities
        summary = assessment["summary"]
        assert summary["total_vulnerabilities"] > 0
        assert summary["dependency_vulnerabilities"] >= 0
        assert summary["code_vulnerabilities"] >= 0
        assert summary["owasp_vulnerabilities"] >= 0
        
        # Verify vulnerability reports were created
        reports_dir = Path(temp_project_dir) / "output/reports/security"
        assert reports_dir.exists()
        
        # Should have 3 vulnerability reports
        report_files = list(reports_dir.glob("vulnerability_report_*.json"))
        assert len(report_files) == 3
        
        # Verify report content
        for report_file in report_files:
            with open(report_file, 'r') as f:
                report_data = json.load(f)
                assert "scan_type" in report_data
                assert "statistics" in report_data
                assert "vulnerabilities" in report_data
                assert "generated_at" in report_data
        
        # Verify performance metrics
        assert security_crew.performance_metrics["vulnerability_scans"] == 3
        assert security_crew.performance_metrics["security_reports_generated"] == 3
        assert security_crew.performance_metrics["vulnerabilities_found"] > 0
    
    def test_threat_modeling_workflow(self, security_crew, temp_project_dir):
        """Test complete threat modeling workflow"""
        # Define threat model for web application
        threat_spec = ThreatModelSpec(
            application_type="web",
            components=[
                "React Frontend",
                "FastAPI Backend", 
                "PostgreSQL Database",
                "Redis Cache",
                "AWS S3 Storage"
            ],
            data_flow={
                "user_input": "Frontend → Backend → Database",
                "file_upload": "Frontend → Backend → S3",
                "authentication": "Frontend → Backend → Redis",
                "data_retrieval": "Database → Backend → Frontend"
            },
            trust_boundaries=[
                "Internet/DMZ",
                "Application/Database",
                "Internal/External Services"
            ],
            attack_surfaces=[
                "Web Interface",
                "API Endpoints",
                "Database Connections",
                "File Upload",
                "Authentication System"
            ]
        )
        
        # Generate threat model
        result = security_crew.generate_threat_model(threat_spec)
        
        assert result["status"] == "success"
        assert result["application_type"] == "web"
        assert result["threats_identified"] > 0
        assert result["mitigations_suggested"] > 0
        
        # Verify threat model report was created
        reports_dir = Path(temp_project_dir) / "output/reports/security"
        assert reports_dir.exists()
        
        # Find threat model report
        report_files = list(reports_dir.glob("threat_model_web_*.json"))
        assert len(report_files) == 1
        
        # Verify report content
        report_file = report_files[0]
        with open(report_file, 'r') as f:
            report_data = json.load(f)
            
            assert report_data["application_type"] == "web"
            assert len(report_data["components"]) == 5
            assert "data_flow" in report_data
            assert "trust_boundaries" in report_data
            assert "attack_surfaces" in report_data
            assert "threats" in report_data
            assert "mitigations" in report_data
            
            # Verify threats cover STRIDE categories
            threats = report_data["threats"]
            threat_types = [threat["threat_type"] for threat in threats]
            stride_categories = ["Spoofing", "Tampering", "Repudiation", 
                               "Information Disclosure", "Denial of Service", 
                               "Elevation of Privilege"]
            
            for category in stride_categories:
                assert category in threat_types, f"Missing STRIDE category: {category}"
            
            # Verify mitigations are provided
            mitigations = report_data["mitigations"]
            assert len(mitigations) > 0
            
            for mitigation in mitigations:
                assert "threat_id" in mitigation
                assert "strategy" in mitigation
                assert "priority" in mitigation
        
        # Verify performance metrics
        assert security_crew.performance_metrics["threats_identified"] > 0
        assert security_crew.performance_metrics["security_reports_generated"] == 1
    
    def test_full_security_lifecycle_workflow(self, security_crew, temp_project_dir):
        """Test complete security lifecycle: auth + vulnerability + threat modeling"""
        # Step 1: Generate authentication system
        auth_spec = AuthSpec(
            auth_type="jwt",
            issuer="myapp",
            audience="users",
            secret_key="lifecycle_test_secret_key_1234567890",
            algorithm="HS256"
        )
        
        auth_result = security_crew.generate_jwt_authentication(auth_spec)
        assert auth_result["status"] == "success"
        
        # Step 2: Generate OAuth2 system
        oauth2_spec = OAuth2Spec(
            provider="github",
            client_id="github_client_id",
            client_secret="github_client_secret",
            redirect_uri="https://myapp.com/auth/github/callback",
            scope=["user:email", "read:user"],
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            user_info_url="https://api.github.com/user"
        )
        
        oauth2_result = security_crew.generate_oauth2_system(oauth2_spec)
        assert oauth2_result["status"] == "success"
        
        # Step 3: Perform vulnerability assessment
        with patch('subprocess.run') as mock_subprocess:
            mock_result = Mock()
            mock_result.stdout = json.dumps([])
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            assessment_result = security_crew.perform_security_assessment(target_path=temp_project_dir)
        
        assert assessment_result["status"] == "success"
        
        # Step 4: Generate threat model
        threat_spec = ThreatModelSpec(
            application_type="web",
            components=["Frontend", "Backend", "Database"],
            data_flow={"user": "frontend", "api": "backend"},
            trust_boundaries=["network", "application"],
            attack_surfaces=["web", "api"]
        )
        
        threat_result = security_crew.generate_threat_model(threat_spec)
        assert threat_result["status"] == "success"
        
        # Verify complete security setup
        output_dir = Path(temp_project_dir) / "output"
        
        # Check authentication files
        auth_dir = output_dir / "generated_code/security/auth"
        assert auth_dir.exists()
        assert len(list(auth_dir.glob("*.py"))) == 6  # 6 auth files
        
        # Check OAuth2 files
        oauth2_dir = output_dir / "generated_code/security/oauth2"
        assert oauth2_dir.exists()
        assert len(list(oauth2_dir.glob("*.py"))) == 4  # 4 OAuth2 files
        
        # Check security reports
        reports_dir = output_dir / "reports/security"
        assert reports_dir.exists()
        
        # Should have 3 vulnerability reports + 1 threat model
        vulnerability_reports = list(reports_dir.glob("vulnerability_report_*.json"))
        threat_reports = list(reports_dir.glob("threat_model_*.json"))
        
        assert len(vulnerability_reports) == 3
        assert len(threat_reports) == 1
        
        # Verify final performance metrics
        metrics = security_crew.performance_metrics
        assert metrics["auth_systems_generated"] == 1
        assert metrics["oauth2_systems_generated"] == 1
        assert metrics["vulnerability_scans"] == 3
        assert metrics["threats_identified"] > 0
        assert metrics["security_reports_generated"] == 4  # 3 vuln + 1 threat
        assert metrics["total_security_checks"] == 2  # auth + oauth2
        
        # Verify crew health after full workflow
        health = security_crew.health_check()
        assert health["status"] == "healthy"
        assert health["checks"]["crew_initialization"] == True
        assert health["checks"]["auth_agent"] == True
        assert health["checks"]["vuln_agent"] == True
        assert len(health["issues"]) == 0
        
        # Verify crew status
        status = security_crew.get_crew_status()
        assert status["crew_name"] == "security"
        assert status["status"] == "ready"
        assert status["completed_tasks"] == 4  # auth + oauth2 + 3 scans + threat model


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])