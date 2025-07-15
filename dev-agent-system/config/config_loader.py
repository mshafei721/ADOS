"""
ADOS Configuration Loader
Handles loading and validation of all ADOS configuration files
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator


class CrewConfig(BaseModel):
    """Model for crew configuration"""
    goal: str
    constraints: List[str]
    dependencies: List[str] = Field(default_factory=list)
    tools: List[str]

    @validator('constraints', 'tools')
    def list_not_empty(cls, v):
        if not v:
            raise ValueError("List cannot be empty")
        return v


class WorkspaceConfig(BaseModel):
    """Model for agent workspace configuration"""
    runtime_folder: str
    memory_access: str
    output_folder: str
    communication_channels: List[str]


class AgentConfig(BaseModel):
    """Model for agent configuration"""
    role: str
    goal: str
    backstory: str
    tools: List[str]
    llm: Optional[str] = "gpt-4"
    max_iter: Optional[int] = 5
    verbose: Optional[bool] = True
    workspace: Optional[WorkspaceConfig] = None


class ConfigLoader:
    """Main configuration loader for ADOS system"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize config loader with config directory path"""
        if config_dir is None:
            # Assume we're running from dev-agent-system directory
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)
            
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")
    
    def load_crews_config(self) -> Dict[str, CrewConfig]:
        """Load and validate crews configuration"""
        crews_file = self.config_dir / "crews.yaml"
        
        if not crews_file.exists():
            raise FileNotFoundError(f"Crews config file not found: {crews_file}")
        
        with open(crews_file, 'r') as f:
            crews_data = yaml.safe_load(f)
        
        # Validate each crew configuration
        crews = {}
        for crew_name, crew_data in crews_data.items():
            try:
                crews[crew_name] = CrewConfig(**crew_data)
            except Exception as e:
                raise ValueError(f"Invalid configuration for crew '{crew_name}': {e}")
        
        # Validate dependencies exist
        crew_names = set(crews.keys())
        for crew_name, crew_config in crews.items():
            for dep in crew_config.dependencies:
                if dep not in crew_names:
                    raise ValueError(f"Crew '{crew_name}' has invalid dependency: '{dep}'")
        
        return crews
    
    def load_agents_config(self) -> Dict[str, List[AgentConfig]]:
        """Load and validate agents configuration"""
        agents_file = self.config_dir / "agents.yaml"
        
        if not agents_file.exists():
            # Return empty dict if file doesn't exist yet
            return {}
        
        with open(agents_file, 'r') as f:
            agents_data = yaml.safe_load(f)
        
        # Validate agent configurations by crew
        agents = {}
        for crew_name, crew_agents in agents_data.items():
            agents[crew_name] = []
            for agent_data in crew_agents:
                try:
                    agents[crew_name].append(AgentConfig(**agent_data))
                except Exception as e:
                    raise ValueError(f"Invalid agent configuration in crew '{crew_name}': {e}")
        
        return agents
    
    def load_tech_stack(self) -> Dict[str, Any]:
        """Load technology stack preferences"""
        tech_stack_file = self.config_dir / "tech_stack.json"
        
        if not tech_stack_file.exists():
            return {}
        
        with open(tech_stack_file, 'r') as f:
            return json.load(f)
    
    def load_system_settings(self) -> Dict[str, Any]:
        """Load system settings"""
        settings_file = self.config_dir / "system_settings.json"
        
        if not settings_file.exists():
            return {}
        
        with open(settings_file, 'r') as f:
            return json.load(f)
    
    def validate_config_integrity(self) -> Dict[str, Any]:
        """Validate overall configuration integrity"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Load all configurations
            crews = self.load_crews_config()
            agents = self.load_agents_config()
            tech_stack = self.load_tech_stack()
            settings = self.load_system_settings()
            
            # Check that all crews have at least one agent (if agents.yaml exists)
            if agents:
                for crew_name in crews:
                    if crew_name not in agents or not agents[crew_name]:
                        validation_results["warnings"].append(
                            f"Crew '{crew_name}' has no agents defined"
                        )
            
            # Validate tool references
            all_tools = set()
            for crew_config in crews.values():
                all_tools.update(crew_config.tools)
            
            # Check for tool naming consistency
            for tool in all_tools:
                if '.' not in tool and tool not in ['task_decomposer', 'memory_writer', 
                                                     'prd_parser', 'system_monitor']:
                    validation_results["warnings"].append(
                        f"Tool '{tool}' doesn't follow namespace.tool_name convention"
                    )
            
            # Validate workspace configuration
            workspace_config = settings.get("communication", {}).get("workspace", {})
            if workspace_config:
                workspace_dir = Path(workspace_config.get("directory", "./workspace"))
                if not workspace_dir.exists():
                    validation_results["warnings"].append(
                        f"Workspace directory '{workspace_dir}' does not exist"
                    )
                else:
                    # Check for required workspace files
                    required_files = ["todo.md", "activeContext.md", "progress.md", "techContext.md"]
                    for file_name in required_files:
                        file_path = workspace_dir / file_name
                        if not file_path.exists():
                            validation_results["warnings"].append(
                                f"Workspace file '{file_name}' missing in {workspace_dir}"
                            )
            
            # Validate communication channels
            channels = settings.get("communication", {}).get("channels", {})
            if channels:
                for channel_name, channel_path in channels.items():
                    if not Path(channel_path).exists():
                        validation_results["warnings"].append(
                            f"Communication channel '{channel_name}' file not found: {channel_path}"
                        )
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(str(e))
        
        return validation_results
    
    def get_crew_config(self, crew_name: str) -> Optional[CrewConfig]:
        """Get configuration for a specific crew"""
        crews = self.load_crews_config()
        return crews.get(crew_name)
    
    def get_crew_agents(self, crew_name: str) -> List[AgentConfig]:
        """Get all agents for a specific crew"""
        agents = self.load_agents_config()
        return agents.get(crew_name, [])
    
    def get_workspace_config(self) -> Dict[str, Any]:
        """Get workspace configuration"""
        settings = self.load_system_settings()
        return settings.get("communication", {}).get("workspace", {})
    
    def get_communication_channels(self) -> Dict[str, str]:
        """Get communication channels configuration"""
        settings = self.load_system_settings()
        return settings.get("communication", {}).get("channels", {})
    
    def validate_workspace_setup(self) -> Dict[str, Any]:
        """Validate workspace setup specifically"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "workspace_ready": False
        }
        
        try:
            workspace_config = self.get_workspace_config()
            channels = self.get_communication_channels()
            
            if not workspace_config:
                validation_results["errors"].append("No workspace configuration found")
                validation_results["valid"] = False
                return validation_results
            
            # Check workspace directory
            workspace_dir = Path(workspace_config.get("directory", "./workspace"))
            if not workspace_dir.exists():
                validation_results["errors"].append(f"Workspace directory '{workspace_dir}' does not exist")
                validation_results["valid"] = False
                return validation_results
            
            # Check workspace files
            workspace_files_exist = True
            required_files = ["todo.md", "activeContext.md", "progress.md", "techContext.md"]
            for file_name in required_files:
                file_path = workspace_dir / file_name
                if not file_path.exists():
                    validation_results["warnings"].append(f"Workspace file '{file_name}' missing")
                    workspace_files_exist = False
            
            # Check communication channels
            channels_valid = True
            for channel_name, channel_path in channels.items():
                if not Path(channel_path).exists():
                    validation_results["warnings"].append(f"Channel '{channel_name}' file not found: {channel_path}")
                    channels_valid = False
            
            validation_results["workspace_ready"] = workspace_files_exist and channels_valid
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(str(e))
        
        return validation_results
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration data"""
        return {
            "crews": self.load_crews_config(),
            "agents": self.load_agents_config(),
            "tech_stack": self.load_tech_stack(),
            "system_settings": self.load_system_settings(),
            "workspace": self.get_workspace_config(),
            "communication_channels": self.get_communication_channels(),
            "validation": self.validate_config_integrity(),
            "workspace_validation": self.validate_workspace_setup()
        }


# Utility functions for external use
def load_config(config_dir: Optional[Path] = None) -> ConfigLoader:
    """Factory function to create a ConfigLoader instance"""
    return ConfigLoader(config_dir)


def validate_ados_config(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Quick validation of ADOS configuration"""
    loader = ConfigLoader(config_dir)
    return loader.validate_config_integrity()