"""
Agent Protocol Validator

This validator ensures that the agent communication protocol and workspace
structure are properly configured and functional.

Validates:
- Workspace communication structure exists
- Agent invocation capabilities are configured
- Memory access systems are properly set up
- Runtime files and communication channels work
- Agent configuration supports protocol requirements
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile
import shutil

from tests.validators import BaseValidator


class AgentProtocolValidator(BaseValidator):
    """Validates agent communication protocol and workspace functionality"""
    
    def __init__(self):
        super().__init__("AgentProtocolValidator")
        
        # Define expected crews and their workspace requirements
        self.expected_crews = [
            'orchestrator',
            'frontend',
            'backend',
            'security',
            'quality',
            'integration',
            'deployment'
        ]
        
        # Define workspace structure requirements
        self.workspace_requirements = {
            'runtime_files': ['runtime.md'],
            'communication_channels': ['workspace'],
            'memory_access': ['memory'],
            'output_channels': ['output']
        }
        
        # Define agent protocol requirements
        self.protocol_requirements = {
            'agent_invocation': ['role', 'goal', 'backstory', 'tools'],
            'workspace_config': ['workspace_path', 'memory_access', 'output_path'],
            'communication_format': ['file_based', 'structured_data']
        }
    
    def validate(self) -> bool:
        """Run all agent protocol validations"""
        
        # Validate workspace structure
        self._validate_workspace_structure()
        
        # Validate agent configuration supports protocol
        self._validate_agent_configuration()
        
        # Validate communication channels
        self._validate_communication_channels()
        
        # Validate memory access system
        self._validate_memory_access()
        
        # Test agent invocation capabilities
        self._test_agent_invocation()
        
        # Test workspace operations
        self._test_workspace_operations()
        
        # Return overall validation result
        return all(result.passed for result in self.results)
    
    def _validate_workspace_structure(self):
        """Validate the workspace structure for agent communications"""
        workspace_path = self.base_path / 'workspace'
        
        if workspace_path.exists() and workspace_path.is_dir():
            self.add_result(
                "workspace_directory",
                True,
                "Main workspace directory exists"
            )
        else:
            self.add_result(
                "workspace_directory",
                False,
                "Main workspace directory missing",
                {"expected_path": str(workspace_path)}
            )
        
        # Check crew-specific workspace directories
        for crew_name in self.expected_crews:
            crew_workspace = workspace_path / crew_name
            
            if crew_workspace.exists() and crew_workspace.is_dir():
                self.add_result(
                    f"crew_workspace_{crew_name}",
                    True,
                    f"Crew workspace exists for '{crew_name}'"
                )
                
                # Check runtime file
                runtime_file = crew_workspace / 'runtime.md'
                if runtime_file.exists():
                    self.add_result(
                        f"crew_runtime_{crew_name}",
                        True,
                        f"Runtime file exists for crew '{crew_name}'"
                    )
                else:
                    self.add_result(
                        f"crew_runtime_{crew_name}",
                        False,
                        f"Runtime file missing for crew '{crew_name}'"
                    )
            else:
                self.add_result(
                    f"crew_workspace_{crew_name}",
                    False,
                    f"Crew workspace missing for '{crew_name}'",
                    {"expected_path": str(crew_workspace)}
                )
    
    def _validate_agent_configuration(self):
        """Validate agent configuration supports protocol requirements"""
        config_path = self.base_path / 'config'
        
        # Load agents configuration
        agents_config_path = config_path / 'agents.yaml'
        
        if not agents_config_path.exists():
            self.add_result(
                "agent_config_file",
                False,
                "Agents configuration file missing"
            )
            return
        
        try:
            with open(agents_config_path, 'r', encoding='utf-8') as f:
                agents_config = yaml.safe_load(f)
            
            self.add_result(
                "agent_config_load",
                True,
                "Agents configuration loaded successfully"
            )
            
            if 'agents' not in agents_config:
                self.add_result(
                    "agent_config_structure",
                    False,
                    "Agents configuration missing 'agents' key"
                )
                return
            
            agents = agents_config['agents']
            
            # Check each agent has required fields for protocol
            for agent_name, agent_config in agents.items():
                required_fields = self.protocol_requirements['agent_invocation']
                missing_fields = [field for field in required_fields if field not in agent_config]
                
                if not missing_fields:
                    self.add_result(
                        f"agent_protocol_{agent_name}",
                        True,
                        f"Agent '{agent_name}' has required protocol fields"
                    )
                else:
                    self.add_result(
                        f"agent_protocol_{agent_name}",
                        False,
                        f"Agent '{agent_name}' missing protocol fields: {missing_fields}"
                    )
                
                # Check workspace configuration if present
                if 'workspace' in agent_config:
                    workspace_config = agent_config['workspace']
                    
                    if isinstance(workspace_config, dict):
                        self.add_result(
                            f"agent_workspace_{agent_name}",
                            True,
                            f"Agent '{agent_name}' has workspace configuration"
                        )
                    else:
                        self.add_result(
                            f"agent_workspace_{agent_name}",
                            False,
                            f"Agent '{agent_name}' workspace configuration invalid"
                        )
                
        except Exception as e:
            self.add_result(
                "agent_config_load",
                False,
                f"Failed to load agents configuration: {str(e)}"
            )
    
    def _validate_communication_channels(self):
        """Validate communication channels are properly configured"""
        
        # Check file-based communication structure
        workspace_path = self.base_path / 'workspace'
        
        if not workspace_path.exists():
            return
        
        # Test communication channel accessibility
        for crew_name in self.expected_crews:
            crew_workspace = workspace_path / crew_name
            
            if not crew_workspace.exists():
                continue
            
            # Test read/write access to workspace
            try:
                # Create temporary communication file
                test_file = crew_workspace / '.test_communication'
                test_file.write_text("test communication", encoding='utf-8')
                
                # Read it back
                content = test_file.read_text(encoding='utf-8')
                
                # Clean up
                test_file.unlink()
                
                if content == "test communication":
                    self.add_result(
                        f"communication_{crew_name}",
                        True,
                        f"Communication channel working for crew '{crew_name}'"
                    )
                else:
                    self.add_result(
                        f"communication_{crew_name}",
                        False,
                        f"Communication channel data integrity issue for crew '{crew_name}'"
                    )
                    
            except Exception as e:
                self.add_result(
                    f"communication_{crew_name}",
                    False,
                    f"Communication channel test failed for crew '{crew_name}': {str(e)}"
                )
    
    def _validate_memory_access(self):
        """Validate memory access systems are properly configured"""
        
        # Check memory directory structure
        memory_path = self.base_path / 'memory'
        
        if memory_path.exists() and memory_path.is_dir():
            self.add_result(
                "memory_directory",
                True,
                "Memory directory exists"
            )
        else:
            self.add_result(
                "memory_directory",
                False,
                "Memory directory missing"
            )
            return
        
        # Check crew memory access
        crew_memory_path = memory_path / 'crew_memory'
        
        if crew_memory_path.exists() and crew_memory_path.is_dir():
            self.add_result(
                "crew_memory_directory",
                True,
                "Crew memory directory exists"
            )
        else:
            self.add_result(
                "crew_memory_directory",
                False,
                "Crew memory directory missing"
            )
        
        # Check global knowledge base access
        global_kb_path = memory_path / 'global_kb'
        
        if global_kb_path.exists() and global_kb_path.is_dir():
            self.add_result(
                "global_kb_directory",
                True,
                "Global knowledge base directory exists"
            )
        else:
            self.add_result(
                "global_kb_directory",
                False,
                "Global knowledge base directory missing"
            )
        
        # Test memory access permissions
        try:
            # Test creating temporary memory file
            temp_memory_file = crew_memory_path / '.test_memory_access'
            temp_memory_file.write_text("test memory", encoding='utf-8')
            
            # Test reading
            content = temp_memory_file.read_text(encoding='utf-8')
            
            # Clean up
            temp_memory_file.unlink()
            
            if content == "test memory":
                self.add_result(
                    "memory_access_test",
                    True,
                    "Memory access system working"
                )
            else:
                self.add_result(
                    "memory_access_test",
                    False,
                    "Memory access system data integrity issue"
                )
        except Exception as e:
            self.add_result(
                "memory_access_test",
                False,
                f"Memory access test failed: {str(e)}"
            )
    
    def _test_agent_invocation(self):
        """Test agent invocation capabilities"""
        
        # Test configuration loader for agent invocation
        try:
            from config.config_loader import ConfigLoader
            
            config_loader = ConfigLoader()
            
            # Test loading agents for invocation
            try:
                all_config = config_loader.get_all_config()
                
                if 'agents' in all_config and all_config['agents']:
                    self.add_result(
                        "agent_invocation_config",
                        True,
                        "Agent invocation configuration available"
                    )
                    
                    # Test specific agent data structure
                    agents = all_config['agents']
                    sample_agent = next(iter(agents.values()))
                    
                    if 'role' in sample_agent and 'tools' in sample_agent:
                        self.add_result(
                            "agent_invocation_structure",
                            True,
                            "Agent invocation structure valid"
                        )
                    else:
                        self.add_result(
                            "agent_invocation_structure",
                            False,
                            "Agent invocation structure invalid"
                        )
                else:
                    self.add_result(
                        "agent_invocation_config",
                        False,
                        "Agent invocation configuration missing or empty"
                    )
                    
            except Exception as e:
                self.add_result(
                    "agent_invocation_config",
                    False,
                    f"Agent invocation configuration test failed: {str(e)}"
                )
        
        except ImportError:
            self.add_result(
                "agent_invocation_config",
                False,
                "ConfigLoader not available for agent invocation testing"
            )
    
    def _test_workspace_operations(self):
        """Test workspace operations and file handling"""
        
        workspace_path = self.base_path / 'workspace'
        
        if not workspace_path.exists():
            return
        
        # Test workspace operations for each crew
        for crew_name in self.expected_crews:
            crew_workspace = workspace_path / crew_name
            
            if not crew_workspace.exists():
                continue
            
            # Test creating task files
            try:
                task_file = crew_workspace / 'test_task.json'
                task_data = {
                    'task_id': 'test_001',
                    'crew': crew_name,
                    'status': 'testing',
                    'data': {'test': True}
                }
                
                # Write task file
                with open(task_file, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, indent=2)
                
                # Read and verify
                with open(task_file, 'r', encoding='utf-8') as f:
                    read_data = json.load(f)
                
                # Clean up
                task_file.unlink()
                
                if read_data == task_data:
                    self.add_result(
                        f"workspace_operations_{crew_name}",
                        True,
                        f"Workspace operations working for crew '{crew_name}'"
                    )
                else:
                    self.add_result(
                        f"workspace_operations_{crew_name}",
                        False,
                        f"Workspace operations data integrity issue for crew '{crew_name}'"
                    )
                    
            except Exception as e:
                self.add_result(
                    f"workspace_operations_{crew_name}",
                    False,
                    f"Workspace operations test failed for crew '{crew_name}': {str(e)}"
                )
        
        # Test output operations
        output_path = self.base_path / 'output'
        
        if output_path.exists():
            try:
                test_output_file = output_path / 'test_output.txt'
                test_output_file.write_text("test output", encoding='utf-8')
                
                content = test_output_file.read_text(encoding='utf-8')
                test_output_file.unlink()
                
                if content == "test output":
                    self.add_result(
                        "output_operations",
                        True,
                        "Output operations working"
                    )
                else:
                    self.add_result(
                        "output_operations",
                        False,
                        "Output operations data integrity issue"
                    )
                    
            except Exception as e:
                self.add_result(
                    "output_operations",
                    False,
                    f"Output operations test failed: {str(e)}"
                )
    
    def get_protocol_summary(self) -> Dict[str, Any]:
        """Get a summary of agent protocol validation results"""
        summary = {
            'workspace_structure': 0,
            'communication_channels': 0,
            'memory_access': 0,
            'agent_invocation': 0,
            'workspace_operations': 0,
            'total_crews': len(self.expected_crews),
            'crews_with_workspace': 0,
            'crews_with_communication': 0,
            'protocol_ready': False
        }
        
        # Count workspace structures
        for crew_name in self.expected_crews:
            workspace_result = any(
                result.passed for result in self.results 
                if result.name == f"crew_workspace_{crew_name}"
            )
            if workspace_result:
                summary['crews_with_workspace'] += 1
            
            comm_result = any(
                result.passed for result in self.results 
                if result.name == f"communication_{crew_name}"
            )
            if comm_result:
                summary['crews_with_communication'] += 1
        
        # Count other components
        summary['workspace_structure'] = sum(
            1 for result in self.results 
            if 'workspace' in result.name and result.passed
        )
        
        summary['communication_channels'] = sum(
            1 for result in self.results 
            if 'communication' in result.name and result.passed
        )
        
        summary['memory_access'] = sum(
            1 for result in self.results 
            if 'memory' in result.name and result.passed
        )
        
        summary['agent_invocation'] = sum(
            1 for result in self.results 
            if 'agent_invocation' in result.name and result.passed
        )
        
        summary['workspace_operations'] = sum(
            1 for result in self.results 
            if 'workspace_operations' in result.name and result.passed
        )
        
        # Determine if protocol is ready
        critical_components = [
            'workspace_directory',
            'memory_directory',
            'agent_invocation_config'
        ]
        
        summary['protocol_ready'] = all(
            any(result.passed for result in self.results if result.name == component)
            for component in critical_components
        )
        
        return summary