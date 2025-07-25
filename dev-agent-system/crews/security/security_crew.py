"""
ADOS Security Crew Implementation
Specialized crew for authentication systems and vulnerability assessment
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from crewai import Agent, Crew, Task, Process

from config.config_loader import ConfigLoader
from orchestrator.agent_factory import AgentFactory
from tools.security_tools import SecurityTools, AuthSpec, OAuth2Spec, VulnerabilitySpec, ThreatModelSpec


class SecurityCrew:
    """Specialized security crew with authentication and vulnerability assessment capabilities"""
    
    def __init__(self, config_loader: ConfigLoader, agent_factory: AgentFactory):
        """Initialize the security crew"""
        self.config_loader = config_loader
        self.agent_factory = agent_factory
        self.logger = logging.getLogger(__name__)
        
        # Initialize security tools
        self.security_tools = SecurityTools(logger=self.logger)
        
        # Crew state
        self.crew_status = "initializing"
        self.active_tasks = []
        self.completed_tasks = []
        self.performance_metrics = {}
        
        # Initialize the crew
        self.initialize_security_crew()
    
    def initialize_security_crew(self) -> bool:
        """Initialize security crew with Auth and Vulnerability agents"""
        try:
            self.logger.info("Initializing security crew...")
            
            # Setup crew monitoring
            self._setup_crew_monitoring()
            self._setup_performance_tracking()
            self._setup_security_workspace()
            
            # Create agents
            self.auth_agent = self._create_auth_agent()
            self.vuln_agent = self._create_vuln_agent()
            
            # Create crew
            self.crew = self._create_crew()
            
            self.crew_status = "ready"
            self.logger.info("Security crew initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security crew: {e}")
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
            "auth_systems_generated": 0,
            "oauth2_systems_generated": 0,
            "vulnerability_scans": 0,
            "threats_identified": 0,
            "vulnerabilities_found": 0,
            "security_reports_generated": 0,
            "average_scan_time": 0.0,
            "total_security_checks": 0,
            "start_time": datetime.now()
        }
    
    def _setup_security_workspace(self):
        """Setup security workspace directories"""
        try:
            workspace_path = Path("dev-agent-system/workspace/security")
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Create runtime.md
            runtime_content = f"""# Security Crew Runtime Context

## Status: {self.crew_status}
## Initialized: {datetime.now().isoformat()}

### Agent Status
- AuthAgent: Initializing
- VulnAgent: Initializing

### Current Tasks
None

### Performance Metrics
{self.performance_metrics}

### Workspace Files
- runtime.md (this file)
- Generated security code: ./output/generated_code/security/
- Security reports: ./output/reports/security/
"""
            (workspace_path / "runtime.md").write_text(runtime_content)
            
            self.logger.info("Security workspace setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup security workspace: {e}")
    
    def _create_auth_agent(self) -> Agent:
        """Create authentication agent"""
        try:
            agent_config = self.config_loader.agents.get("AuthAgent")
            if not agent_config:
                raise ValueError("AuthAgent configuration not found")
            
            # Create agent using agent factory
            auth_agent = self.agent_factory.create_agent(
                name="AuthAgent",
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                tools=self._get_auth_agent_tools(),
                llm=agent_config.get("llm", "gpt-4"),
                max_iter=agent_config.get("max_iter", 8),
                verbose=agent_config.get("verbose", True)
            )
            
            self.logger.info("Auth Agent created successfully")
            return auth_agent
            
        except Exception as e:
            self.logger.error(f"Failed to create Auth Agent: {e}")
            raise
    
    def _create_vuln_agent(self) -> Agent:
        """Create vulnerability assessment agent"""
        try:
            agent_config = self.config_loader.agents.get("VulnAgent")
            if not agent_config:
                raise ValueError("VulnAgent configuration not found")
            
            # Create agent using agent factory
            vuln_agent = self.agent_factory.create_agent(
                name="VulnAgent",
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                tools=self._get_vuln_agent_tools(),
                llm=agent_config.get("llm", "gpt-4"),
                max_iter=agent_config.get("max_iter", 10),
                verbose=agent_config.get("verbose", True)
            )
            
            self.logger.info("Vulnerability Agent created successfully")
            return vuln_agent
            
        except Exception as e:
            self.logger.error(f"Failed to create Vulnerability Agent: {e}")
            raise
    
    def _get_auth_agent_tools(self) -> List[Any]:
        """Get tools for authentication agent"""
        return [
            self.security_tools.generate_jwt_auth_system,
            self.security_tools.generate_oauth2_system,
            "search.owasp_docs"  # Would be resolved by agent factory
        ]
    
    def _get_vuln_agent_tools(self) -> List[Any]:
        """Get tools for vulnerability agent"""
        return [
            self.security_tools.scan_vulnerabilities,
            self.security_tools.generate_threat_model,
            "search.cve_database"  # Would be resolved by agent factory
        ]
    
    def _create_crew(self) -> Crew:
        """Create the security crew"""
        try:
            crew = Crew(
                agents=[self.auth_agent, self.vuln_agent],
                verbose=True,
                process=Process.sequential,
                max_rpm=10
            )
            
            self.logger.info("Security crew created successfully")
            return crew
            
        except Exception as e:
            self.logger.error(f"Failed to create security crew: {e}")
            raise
    
    def generate_jwt_authentication(self, auth_spec: AuthSpec) -> Dict[str, Any]:
        """Generate JWT authentication system using security crew"""
        try:
            self.logger.info(f"Generating JWT authentication system")
            
            # Create task for auth agent
            task = Task(
                description=f"Generate JWT authentication system with {auth_spec.algorithm} algorithm",
                agent=self.auth_agent,
                expected_output="Complete JWT authentication system with tokens, middleware, and security configuration"
            )
            
            # Update crew status
            self.crew_status = "executing"
            self.active_tasks.append(task)
            
            # Generate using security tools
            result = self.security_tools.generate_jwt_auth_system(auth_spec)
            
            # Update metrics
            if result["status"] == "success":
                self.performance_metrics["auth_systems_generated"] += 1
                self.performance_metrics["total_security_checks"] += 1
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
            self.logger.info(f"JWT authentication generation completed with status: {result['status']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate JWT authentication: {e}")
            self.crew_status = "error"
            return {"status": "error", "error": str(e)}
    
    def generate_oauth2_system(self, oauth2_spec: OAuth2Spec) -> Dict[str, Any]:
        """Generate OAuth2 authentication system using security crew"""
        try:
            self.logger.info(f"Generating OAuth2 system for {oauth2_spec.provider}")
            
            # Create task for auth agent
            task = Task(
                description=f"Generate OAuth2 authentication system for {oauth2_spec.provider}",
                agent=self.auth_agent,
                expected_output="Complete OAuth2 authentication system with client, handlers, and flow management"
            )
            
            # Update crew status
            self.crew_status = "executing"
            self.active_tasks.append(task)
            
            # Generate using security tools
            result = self.security_tools.generate_oauth2_system(oauth2_spec)
            
            # Update metrics
            if result["status"] == "success":
                self.performance_metrics["oauth2_systems_generated"] += 1
                self.performance_metrics["total_security_checks"] += 1
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
            self.logger.info(f"OAuth2 system generation completed with status: {result['status']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate OAuth2 system: {e}")
            self.crew_status = "error"
            return {"status": "error", "error": str(e)}
    
    def scan_vulnerabilities(self, vuln_spec: VulnerabilitySpec) -> Dict[str, Any]:
        """Scan for vulnerabilities using security crew"""
        try:
            self.logger.info(f"Starting {vuln_spec.scan_type} vulnerability scan")
            
            # Create task for vuln agent
            task = Task(
                description=f"Perform {vuln_spec.scan_type} vulnerability scan on {vuln_spec.target_path}",
                agent=self.vuln_agent,
                expected_output="Complete vulnerability scan report with identified issues and recommendations"
            )
            
            # Update crew status
            self.crew_status = "executing"
            self.active_tasks.append(task)
            
            # Scan using security tools
            result = self.security_tools.scan_vulnerabilities(vuln_spec)
            
            # Update metrics
            if result["status"] == "success":
                self.performance_metrics["vulnerability_scans"] += 1
                self.performance_metrics["vulnerabilities_found"] += result.get("vulnerabilities_found", 0)
                self.performance_metrics["security_reports_generated"] += 1
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
            self.logger.info(f"Vulnerability scan completed with status: {result['status']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to scan vulnerabilities: {e}")
            self.crew_status = "error"
            return {"status": "error", "error": str(e)}
    
    def generate_threat_model(self, threat_spec: ThreatModelSpec) -> Dict[str, Any]:
        """Generate threat model using security crew"""
        try:
            self.logger.info(f"Generating threat model for {threat_spec.application_type}")
            
            # Create task for vuln agent
            task = Task(
                description=f"Generate threat model for {threat_spec.application_type} application",
                agent=self.vuln_agent,
                expected_output="Complete threat model with identified threats, attack vectors, and mitigation strategies"
            )
            
            # Update crew status
            self.crew_status = "executing"
            self.active_tasks.append(task)
            
            # Generate using security tools
            result = self.security_tools.generate_threat_model(threat_spec)
            
            # Update metrics
            if result["status"] == "success":
                self.performance_metrics["threats_identified"] += result.get("threats_identified", 0)
                self.performance_metrics["security_reports_generated"] += 1
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
            self.logger.info(f"Threat model generation completed with status: {result['status']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate threat model: {e}")
            self.crew_status = "error"
            return {"status": "error", "error": str(e)}
    
    def perform_security_assessment(self, 
                                  target_path: str = ".",
                                  assessment_type: str = "comprehensive") -> Dict[str, Any]:
        """Perform comprehensive security assessment"""
        try:
            self.logger.info(f"Starting {assessment_type} security assessment")
            
            assessment_results = {
                "assessment_type": assessment_type,
                "target_path": target_path,
                "results": {},
                "summary": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Dependency scan
            dep_spec = VulnerabilitySpec(
                scan_type="dependency",
                target_path=target_path,
                severity_threshold="medium"
            )
            dep_result = self.scan_vulnerabilities(dep_spec)
            assessment_results["results"]["dependency_scan"] = dep_result
            
            # Code scan
            code_spec = VulnerabilitySpec(
                scan_type="code",
                target_path=target_path,
                severity_threshold="medium"
            )
            code_result = self.scan_vulnerabilities(code_spec)
            assessment_results["results"]["code_scan"] = code_result
            
            # OWASP scan
            owasp_spec = VulnerabilitySpec(
                scan_type="owasp",
                target_path=target_path,
                severity_threshold="medium"
            )
            owasp_result = self.scan_vulnerabilities(owasp_spec)
            assessment_results["results"]["owasp_scan"] = owasp_result
            
            # Generate summary
            total_vulnerabilities = (
                dep_result.get("vulnerabilities_found", 0) +
                code_result.get("vulnerabilities_found", 0) +
                owasp_result.get("vulnerabilities_found", 0)
            )
            
            assessment_results["summary"] = {
                "total_vulnerabilities": total_vulnerabilities,
                "dependency_vulnerabilities": dep_result.get("vulnerabilities_found", 0),
                "code_vulnerabilities": code_result.get("vulnerabilities_found", 0),
                "owasp_vulnerabilities": owasp_result.get("vulnerabilities_found", 0),
                "assessment_status": "completed"
            }
            
            self.logger.info(f"Security assessment completed: {total_vulnerabilities} vulnerabilities found")
            
            return {
                "status": "success",
                "assessment_results": assessment_results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to perform security assessment: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get current crew status"""
        return {
            "crew_name": "security",
            "status": self.crew_status,
            "health": self.crew_health,
            "performance_metrics": self.performance_metrics,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "agents": {
                "auth_agent": {
                    "status": "active" if hasattr(self, 'auth_agent') else "not_initialized",
                    "role": "AuthAgent"
                },
                "vuln_agent": {
                    "status": "active" if hasattr(self, 'vuln_agent') else "not_initialized",
                    "role": "VulnAgent"
                }
            },
            "tools_status": self.security_tools.get_tool_status(),
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
                    "auth_agent": hasattr(self, 'auth_agent'),
                    "vuln_agent": hasattr(self, 'vuln_agent'),
                    "security_tools": True,
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
            
            # Check security scan success rate
            total_scans = self.performance_metrics["vulnerability_scans"]
            if total_scans > 0:
                # If we have errors, consider the success rate
                if len(self.crew_health["errors"]) > total_scans * 0.2:  # More than 20% error rate
                    health_status["issues"].append("High security scan failure rate")
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
            workspace_path = Path("dev-agent-system/workspace/security")
            runtime_content = f"""# Security Crew Runtime Context

## Status: {self.crew_status}
## Last Updated: {datetime.now().isoformat()}

### Agent Status
- AuthAgent: {"Active" if hasattr(self, 'auth_agent') else "Not Initialized"}
- VulnAgent: {"Active" if hasattr(self, 'vuln_agent') else "Not Initialized"}

### Current Tasks
{len(self.active_tasks)} active tasks

### Performance Metrics
- Auth Systems Generated: {self.performance_metrics['auth_systems_generated']}
- OAuth2 Systems Generated: {self.performance_metrics['oauth2_systems_generated']}
- Vulnerability Scans: {self.performance_metrics['vulnerability_scans']}
- Threats Identified: {self.performance_metrics['threats_identified']}
- Vulnerabilities Found: {self.performance_metrics['vulnerabilities_found']}
- Security Reports Generated: {self.performance_metrics['security_reports_generated']}
- Total Security Checks: {self.performance_metrics['total_security_checks']}

### Health Status
{self.crew_health}

### Recent Tasks
{len(self.completed_tasks)} completed tasks

### Workspace Files
- runtime.md (this file)
- Generated security code: ./output/generated_code/security/
- Security reports: ./output/reports/security/
"""
            (workspace_path / "runtime.md").write_text(runtime_content)
            
        except Exception as e:
            self.logger.error(f"Failed to update runtime context: {e}")
    
    def shutdown(self):
        """Shutdown the security crew"""
        try:
            self.logger.info("Shutting down security crew...")
            
            # Update runtime context one final time
            self.update_runtime_context()
            
            # Clean up resources
            self.crew_status = "shutdown"
            self.active_tasks.clear()
            
            self.logger.info("Security crew shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown security crew: {e}")