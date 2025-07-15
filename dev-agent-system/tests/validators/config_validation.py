"""
Configuration Validation Validator

This validator ensures that all ADOS configuration files load correctly
and contain the expected structure and data.

Validates:
- All 5 configuration files exist and are readable
- Configuration files parse correctly (YAML/JSON)
- All 7 crews are defined with required fields
- All 15 agents are defined with proper configuration
- Configuration integrity and validation rules
- Configuration file relationships and dependencies
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List

from tests.validators import BaseValidator


class ConfigValidationValidator(BaseValidator):
    """Validates all ADOS configuration files and their contents"""
    
    def __init__(self):
        super().__init__("ConfigValidationValidator")
        
        # Define expected configuration files
        self.config_files = {
            'crews.yaml': 'yaml',
            'agents.yaml': 'yaml', 
            'tech_stack.json': 'json',
            'system_settings.json': 'json',
            'config_loader.py': 'python'
        }
        
        # Expected crews
        self.expected_crews = [
            'orchestrator',
            'frontend',
            'backend', 
            'security',
            'quality',
            'integration',
            'deployment'
        ]
        
        # Expected agents per crew
        self.expected_agents = {
            'orchestrator': ['TaskDecomposer', 'WorkflowManager'],
            'frontend': ['UIDevAgent', 'StyleAgent'],
            'backend': ['APIAgent', 'DatabaseAgent'],
            'security': ['AuthAgent', 'VulnAgent'],
            'quality': ['UnitTester', 'Linter', 'CodeReviewer'],
            'integration': ['CIAgent', 'APIIntegrator'],
            'deployment': ['DockerAgent', 'CloudAgent']
        }
        
        # Configuration data storage
        self.config_data = {}
    
    def validate(self) -> bool:
        """Run all configuration validation checks"""
        
        # Validate configuration files exist and are readable
        self._validate_config_files_exist()
        
        # Load and parse configuration files
        self._load_configuration_files()
        
        # Validate configuration structure
        self._validate_configuration_structure()
        
        # Validate crews configuration
        self._validate_crews_configuration()
        
        # Validate agents configuration
        self._validate_agents_configuration()
        
        # Validate configuration integrity
        self._validate_configuration_integrity()
        
        # Test configuration loader
        self._test_configuration_loader()
        
        # Return overall validation result
        return all(result.passed for result in self.results)
    
    def _validate_config_files_exist(self):
        """Validate all configuration files exist and are readable"""
        config_path = self.base_path / 'config'
        
        if not config_path.exists():
            self.add_result(
                "config_directory",
                False,
                "Configuration directory does not exist",
                {"expected_path": str(config_path)}
            )
            return
        
        self.add_result(
            "config_directory",
            True,
            "Configuration directory exists"
        )
        
        # Check each configuration file
        for filename, file_type in self.config_files.items():
            file_path = config_path / filename
            
            if file_path.exists() and file_path.is_file():
                self.add_result(
                    f"config_file_{filename.replace('.', '_')}",
                    True,
                    f"Configuration file '{filename}' exists"
                )
                
                # Test file is readable
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            self.add_result(
                                f"config_readable_{filename.replace('.', '_')}",
                                True,
                                f"Configuration file '{filename}' is readable and has content"
                            )
                        else:
                            self.add_result(
                                f"config_readable_{filename.replace('.', '_')}",
                                False,
                                f"Configuration file '{filename}' is empty"
                            )
                except Exception as e:
                    self.add_result(
                        f"config_readable_{filename.replace('.', '_')}",
                        False,
                        f"Cannot read configuration file '{filename}': {str(e)}"
                    )
            else:
                self.add_result(
                    f"config_file_{filename.replace('.', '_')}",
                    False,
                    f"Configuration file '{filename}' is missing",
                    {"expected_path": str(file_path)}
                )
    
    def _load_configuration_files(self):
        """Load and parse configuration files"""
        config_path = self.base_path / 'config'
        
        for filename, file_type in self.config_files.items():
            file_path = config_path / filename
            
            if not file_path.exists():
                continue
            
            try:
                if file_type == 'yaml':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        self.config_data[filename] = data
                        
                    self.add_result(
                        f"config_parse_{filename.replace('.', '_')}",
                        True,
                        f"Successfully parsed YAML file '{filename}'"
                    )
                
                elif file_type == 'json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.config_data[filename] = data
                        
                    self.add_result(
                        f"config_parse_{filename.replace('.', '_')}",
                        True,
                        f"Successfully parsed JSON file '{filename}'"
                    )
                
                elif file_type == 'python':
                    # For Python files, just validate they can be imported
                    self.add_result(
                        f"config_parse_{filename.replace('.', '_')}",
                        True,
                        f"Python file '{filename}' exists (import validation in loader test)"
                    )
                    
            except yaml.YAMLError as e:
                self.add_result(
                    f"config_parse_{filename.replace('.', '_')}",
                    False,
                    f"YAML parsing error in '{filename}': {str(e)}"
                )
                
            except json.JSONDecodeError as e:
                self.add_result(
                    f"config_parse_{filename.replace('.', '_')}",
                    False,
                    f"JSON parsing error in '{filename}': {str(e)}"
                )
                
            except Exception as e:
                self.add_result(
                    f"config_parse_{filename.replace('.', '_')}",
                    False,
                    f"Error loading '{filename}': {str(e)}"
                )
    
    def _validate_configuration_structure(self):
        """Validate the structure of configuration files"""
        
        # Validate crews.yaml structure
        if 'crews.yaml' in self.config_data:
            crews_data = self.config_data['crews.yaml']
            
            if isinstance(crews_data, dict) and 'crews' in crews_data:
                self.add_result(
                    "crews_structure",
                    True,
                    "crews.yaml has correct structure"
                )
            else:
                self.add_result(
                    "crews_structure",
                    False,
                    "crews.yaml missing 'crews' key or invalid structure"
                )
        
        # Validate agents.yaml structure
        if 'agents.yaml' in self.config_data:
            agents_data = self.config_data['agents.yaml']
            
            if isinstance(agents_data, dict) and 'agents' in agents_data:
                self.add_result(
                    "agents_structure",
                    True,
                    "agents.yaml has correct structure"
                )
            else:
                self.add_result(
                    "agents_structure",
                    False,
                    "agents.yaml missing 'agents' key or invalid structure"
                )
        
        # Validate tech_stack.json structure
        if 'tech_stack.json' in self.config_data:
            tech_data = self.config_data['tech_stack.json']
            
            expected_keys = ['backend', 'frontend', 'database', 'infrastructure']
            if isinstance(tech_data, dict) and all(key in tech_data for key in expected_keys):
                self.add_result(
                    "tech_stack_structure",
                    True,
                    "tech_stack.json has correct structure"
                )
            else:
                self.add_result(
                    "tech_stack_structure",
                    False,
                    f"tech_stack.json missing required keys: {expected_keys}"
                )
        
        # Validate system_settings.json structure
        if 'system_settings.json' in self.config_data:
            system_data = self.config_data['system_settings.json']
            
            expected_keys = ['memory', 'logging', 'communication']
            if isinstance(system_data, dict) and all(key in system_data for key in expected_keys):
                self.add_result(
                    "system_settings_structure",
                    True,
                    "system_settings.json has correct structure"
                )
            else:
                self.add_result(
                    "system_settings_structure",
                    False,
                    f"system_settings.json missing required keys: {expected_keys}"
                )
    
    def _validate_crews_configuration(self):
        """Validate crews configuration completeness"""
        if 'crews.yaml' not in self.config_data:
            return
        
        crews_data = self.config_data['crews.yaml']
        if 'crews' not in crews_data:
            return
        
        crews = crews_data['crews']
        
        # Check total number of crews
        actual_crews = len(crews)
        expected_crews = len(self.expected_crews)
        
        if actual_crews == expected_crews:
            self.add_result(
                "crews_count",
                True,
                f"Correct number of crews: {actual_crews}"
            )
        else:
            self.add_result(
                "crews_count",
                False,
                f"Expected {expected_crews} crews, found {actual_crews}"
            )
        
        # Check each expected crew
        for crew_name in self.expected_crews:
            if crew_name in crews:
                crew_config = crews[crew_name]
                
                # Check required fields
                required_fields = ['goal', 'backstory', 'agents']
                missing_fields = [field for field in required_fields if field not in crew_config]
                
                if not missing_fields:
                    self.add_result(
                        f"crew_{crew_name}_config",
                        True,
                        f"Crew '{crew_name}' has all required fields"
                    )
                else:
                    self.add_result(
                        f"crew_{crew_name}_config",
                        False,
                        f"Crew '{crew_name}' missing fields: {missing_fields}"
                    )
            else:
                self.add_result(
                    f"crew_{crew_name}_exists",
                    False,
                    f"Crew '{crew_name}' not found in configuration"
                )
    
    def _validate_agents_configuration(self):
        """Validate agents configuration completeness"""
        if 'agents.yaml' not in self.config_data:
            return
        
        agents_data = self.config_data['agents.yaml']
        if 'agents' not in agents_data:
            return
        
        agents = agents_data['agents']
        
        # Count total expected agents
        total_expected_agents = sum(len(agent_list) for agent_list in self.expected_agents.values())
        actual_agents = len(agents)
        
        if actual_agents == total_expected_agents:
            self.add_result(
                "agents_count",
                True,
                f"Correct number of agents: {actual_agents}"
            )
        else:
            self.add_result(
                "agents_count",
                False,
                f"Expected {total_expected_agents} agents, found {actual_agents}"
            )
        
        # Check each expected agent
        for crew_name, agent_list in self.expected_agents.items():
            for agent_name in agent_list:
                if agent_name in agents:
                    agent_config = agents[agent_name]
                    
                    # Check required fields
                    required_fields = ['role', 'goal', 'backstory', 'tools']
                    missing_fields = [field for field in required_fields if field not in agent_config]
                    
                    if not missing_fields:
                        self.add_result(
                            f"agent_{agent_name}_config",
                            True,
                            f"Agent '{agent_name}' has all required fields"
                        )
                    else:
                        self.add_result(
                            f"agent_{agent_name}_config",
                            False,
                            f"Agent '{agent_name}' missing fields: {missing_fields}"
                        )
                else:
                    self.add_result(
                        f"agent_{agent_name}_exists",
                        False,
                        f"Agent '{agent_name}' not found in configuration"
                    )
    
    def _validate_configuration_integrity(self):
        """Validate configuration integrity and cross-references"""
        
        # Check if agents referenced in crews exist
        if 'crews.yaml' in self.config_data and 'agents.yaml' in self.config_data:
            crews_data = self.config_data['crews.yaml']
            agents_data = self.config_data['agents.yaml']
            
            if 'crews' in crews_data and 'agents' in agents_data:
                crews = crews_data['crews']
                agents = agents_data['agents']
                
                for crew_name, crew_config in crews.items():
                    if 'agents' in crew_config:
                        for agent_name in crew_config['agents']:
                            if agent_name in agents:
                                self.add_result(
                                    f"integrity_{crew_name}_{agent_name}",
                                    True,
                                    f"Agent '{agent_name}' referenced in crew '{crew_name}' exists"
                                )
                            else:
                                self.add_result(
                                    f"integrity_{crew_name}_{agent_name}",
                                    False,
                                    f"Agent '{agent_name}' referenced in crew '{crew_name}' does not exist"
                                )
    
    def _test_configuration_loader(self):
        """Test the configuration loader functionality"""
        try:
            # Import the config loader
            from config.config_loader import ConfigLoader
            
            self.add_result(
                "config_loader_import",
                True,
                "ConfigLoader can be imported successfully"
            )
            
            # Test loading configuration
            try:
                config_loader = ConfigLoader()
                self.add_result(
                    "config_loader_instantiate",
                    True,
                    "ConfigLoader can be instantiated"
                )
                
                # Test loading crews
                try:
                    crews = config_loader.load_crews()
                    if crews and len(crews) == len(self.expected_crews):
                        self.add_result(
                            "config_loader_crews",
                            True,
                            f"ConfigLoader successfully loads {len(crews)} crews"
                        )
                    else:
                        self.add_result(
                            "config_loader_crews",
                            False,
                            f"ConfigLoader loaded {len(crews) if crews else 0} crews, expected {len(self.expected_crews)}"
                        )
                except Exception as e:
                    self.add_result(
                        "config_loader_crews",
                        False,
                        f"ConfigLoader failed to load crews: {str(e)}"
                    )
                
                # Test loading agents
                try:
                    agents = config_loader.load_agents()
                    total_expected_agents = sum(len(agent_list) for agent_list in self.expected_agents.values())
                    
                    if agents and len(agents) == total_expected_agents:
                        self.add_result(
                            "config_loader_agents",
                            True,
                            f"ConfigLoader successfully loads {len(agents)} agents"
                        )
                    else:
                        self.add_result(
                            "config_loader_agents",
                            False,
                            f"ConfigLoader loaded {len(agents) if agents else 0} agents, expected {total_expected_agents}"
                        )
                except Exception as e:
                    self.add_result(
                        "config_loader_agents",
                        False,
                        f"ConfigLoader failed to load agents: {str(e)}"
                    )
                
                # Test loading complete configuration
                try:
                    all_config = config_loader.get_all_config()
                    if all_config and 'crews' in all_config and 'agents' in all_config:
                        self.add_result(
                            "config_loader_complete",
                            True,
                            "ConfigLoader successfully loads complete configuration"
                        )
                    else:
                        self.add_result(
                            "config_loader_complete",
                            False,
                            "ConfigLoader failed to load complete configuration"
                        )
                except Exception as e:
                    self.add_result(
                        "config_loader_complete",
                        False,
                        f"ConfigLoader failed to load complete config: {str(e)}"
                    )
                    
            except Exception as e:
                self.add_result(
                    "config_loader_instantiate",
                    False,
                    f"ConfigLoader instantiation failed: {str(e)}"
                )
        
        except ImportError as e:
            self.add_result(
                "config_loader_import",
                False,
                f"ConfigLoader import failed: {str(e)}"
            )
        except Exception as e:
            self.add_result(
                "config_loader_import",
                False,
                f"ConfigLoader import error: {str(e)}"
            )
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of configuration validation results"""
        summary = {
            'config_files': len(self.config_files),
            'loaded_files': len(self.config_data),
            'crews_found': 0,
            'agents_found': 0,
            'missing_crews': [],
            'missing_agents': [],
            'integrity_issues': []
        }
        
        # Count crews and agents
        if 'crews.yaml' in self.config_data:
            crews_data = self.config_data['crews.yaml']
            if 'crews' in crews_data:
                summary['crews_found'] = len(crews_data['crews'])
        
        if 'agents.yaml' in self.config_data:
            agents_data = self.config_data['agents.yaml']
            if 'agents' in agents_data:
                summary['agents_found'] = len(agents_data['agents'])
        
        # Identify missing components
        for result in self.results:
            if 'crew_' in result.name and not result.passed:
                summary['missing_crews'].append(result.name)
            elif 'agent_' in result.name and not result.passed:
                summary['missing_agents'].append(result.name)
            elif 'integrity_' in result.name and not result.passed:
                summary['integrity_issues'].append(result.name)
        
        return summary