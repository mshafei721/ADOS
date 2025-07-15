"""
ADOS Agent Factory
Factory for creating CrewAI agents from flat configuration
"""

import logging
from typing import Dict, List, Optional, Any

from crewai import Agent

from config.config_loader import ConfigLoader, AgentConfig


class AgentFactory:
    """Factory for creating CrewAI agents from ADOS configuration"""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the agent factory"""
        self.config_loader = config_loader
        self.logger = logging.getLogger(__name__)
        
        # Cache for created agents
        self._agent_cache: Dict[str, Agent] = {}
        
        # Mock tools registry (in real implementation, this would load actual tools)
        self._mock_tools_registry = self._setup_mock_tools()
    
    def _setup_mock_tools(self) -> Dict[str, Any]:
        """Setup mock tools registry for demonstration"""
        # In a real implementation, this would load actual tool implementations
        return {
            "task_decomposer": "MockTaskDecomposer",
            "memory_writer": "MockMemoryWriter",
            "prd_parser": "MockPRDParser",
            "system_monitor": "MockSystemMonitor",
            "codegen.fastapi_boilerplate": "MockFastAPIBoilerplate",
            "codegen.sqlalchemy_models": "MockSQLAlchemyModels",
            "codegen.auth_boilerplate": "MockAuthBoilerplate",
            "codegen.test_boilerplate": "MockTestBoilerplate",
            "codegen.formatter": "MockFormatter",
            "codegen.ci_pipeline": "MockCIPipeline",
            "codegen.api_client": "MockAPIClient",
            "codegen.dockerfile": "MockDockerfile",
            "codegen.k8s_manifests": "MockK8sManifests",
            "codegen.component_generator": "MockComponentGenerator",
            "codegen.style_templates": "MockStyleTemplates",
            "codegen.security_patches": "MockSecurityPatches",
            "search.python_docs": "MockPythonDocs",
            "search.database_docs": "MockDatabaseDocs",
            "search.owasp_docs": "MockOWASPDocs",
            "search.style_guides": "MockStyleGuides",
            "search.best_practices": "MockBestPractices",
            "search.cicd_docs": "MockCICDDocs",
            "search.api_docs": "MockAPIDocs",
            "search.docker_docs": "MockDockerDocs",
            "search.k8s_docs": "MockK8sDocs",
            "search.frontend_docs": "MockFrontendDocs",
            "search.design_docs": "MockDesignDocs",
            "search.cve_database": "MockCVEDatabase",
            "search.testing_best_practices": "MockTestingBestPractices",
            "test.pytest_runner": "MockPytestRunner",
            "test.db_tester": "MockDBTester",
            "test.security_scanner": "MockSecurityScanner",
            "test.coverage_reporter": "MockCoverageReporter",
            "test.linter": "MockLinter",
            "test.static_analyzer": "MockStaticAnalyzer",
            "test.integration_tester": "MockIntegrationTester",
            "test.e2e_testing": "MockE2ETesting",
            "test.visual_regression": "MockVisualRegression",
            "deploy.pipeline_runner": "MockPipelineRunner",
            "deploy.docker_builder": "MockDockerBuilder",
            "deploy.k8s_deployer": "MockK8sDeployer",
            "deploy.secrets_manager": "MockSecretsManager"
        }
    
    def create_agent(self, agent_name: str, agent_config: AgentConfig) -> Agent:
        """Create a CrewAI agent from configuration"""
        # Check cache first
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]
        
        try:
            self.logger.debug(f"Creating agent: {agent_name}")
            
            # Get tools for the agent
            tools = self._get_agent_tools(agent_config.tools)
            
            # Create the agent
            agent = Agent(
                role=agent_config.role,
                goal=agent_config.goal,
                backstory=agent_config.backstory,
                tools=tools,
                verbose=agent_config.verbose,
                max_iter=agent_config.max_iter,
                allow_delegation=False,  # Disable delegation for now
                memory=True  # Enable memory for better performance
            )
            
            # Cache the agent
            self._agent_cache[agent_name] = agent
            
            self.logger.debug(f"Successfully created agent: {agent_name}")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create agent '{agent_name}': {e}")
            raise
    
    def _get_agent_tools(self, tool_names: List[str]) -> List[Any]:
        """Get tools for an agent based on tool names"""
        tools = []
        
        for tool_name in tool_names:
            if tool_name in self._mock_tools_registry:
                # In a real implementation, this would instantiate actual tools
                # For now, we'll just log the tool name
                self.logger.debug(f"Mock tool loaded: {tool_name}")
                # tools.append(self._mock_tools_registry[tool_name])
            else:
                self.logger.warning(f"Unknown tool: {tool_name}")
        
        # Return empty list for now (no actual tools implemented)
        return tools
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get a cached agent by name"""
        return self._agent_cache.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """List all cached agent names"""
        return list(self._agent_cache.keys())
    
    def clear_cache(self):
        """Clear the agent cache"""
        self._agent_cache.clear()
        self.logger.debug("Agent cache cleared")
    
    def create_agents_for_crew(self, crew_name: str) -> List[Agent]:
        """Create all agents for a specific crew"""
        agents = []
        
        # Get all agents for this crew
        crew_agents = self.config_loader.get_crew_agents(crew_name)
        
        for agent_config in crew_agents:
            # Find the agent name from the configuration
            agent_name = None
            for name, config in self.config_loader.load_agents_config().items():
                if config == agent_config:
                    agent_name = name
                    break
            
            if agent_name:
                agent = self.create_agent(agent_name, agent_config)
                agents.append(agent)
            else:
                self.logger.warning(f"Could not find agent name for crew '{crew_name}'")
        
        return agents
    
    def validate_agent_configuration(self, agent_name: str, agent_config: AgentConfig) -> Dict[str, Any]:
        """Validate agent configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate required fields
            if not agent_config.role:
                validation_results["errors"].append("Role is required")
                validation_results["valid"] = False
            
            if not agent_config.goal:
                validation_results["errors"].append("Goal is required")
                validation_results["valid"] = False
            
            if not agent_config.backstory:
                validation_results["errors"].append("Backstory is required")
                validation_results["valid"] = False
            
            if not agent_config.crew:
                validation_results["errors"].append("Crew assignment is required")
                validation_results["valid"] = False
            
            # Validate tools
            if not agent_config.tools:
                validation_results["warnings"].append("No tools specified for agent")
            else:
                for tool_name in agent_config.tools:
                    if tool_name not in self._mock_tools_registry:
                        validation_results["warnings"].append(f"Unknown tool: {tool_name}")
            
            # Validate workspace configuration
            if agent_config.workspace:
                if not agent_config.workspace.runtime_folder:
                    validation_results["warnings"].append("Runtime folder not specified")
                if not agent_config.workspace.memory_access:
                    validation_results["warnings"].append("Memory access not specified")
                if not agent_config.workspace.output_folder:
                    validation_results["warnings"].append("Output folder not specified")
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation failed: {e}")
        
        return validation_results
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about an agent"""
        agents_config = self.config_loader.load_agents_config()
        
        if agent_name not in agents_config:
            return None
        
        agent_config = agents_config[agent_name]
        cached_agent = self._agent_cache.get(agent_name)
        
        return {
            "name": agent_name,
            "role": agent_config.role,
            "goal": agent_config.goal,
            "backstory": agent_config.backstory,
            "crew": agent_config.crew,
            "tools": agent_config.tools,
            "llm": agent_config.llm,
            "max_iter": agent_config.max_iter,
            "verbose": agent_config.verbose,
            "workspace": agent_config.workspace.dict() if agent_config.workspace else None,
            "cached": cached_agent is not None,
            "validation": self.validate_agent_configuration(agent_name, agent_config)
        }
    
    def get_all_agents_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all agents"""
        agents_info = {}
        
        for agent_name in self.config_loader.load_agents_config().keys():
            agents_info[agent_name] = self.get_agent_info(agent_name)
        
        return agents_info