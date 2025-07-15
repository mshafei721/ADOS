"""
Directory Structure Validator

This validator ensures that the ADOS system has the correct directory structure
including all crew directories, subdirectories, and required files.

Validates:
- All 7 crew directories exist
- Each crew has the required subdirectories (kb/, memory/, agents/, workspace/)
- Required .gitkeep files are present
- Proper permissions and accessibility
- Core system directories (config/, tools/, output/, etc.)
"""

import os
from pathlib import Path
from typing import List, Dict, Any

from tests.validators import BaseValidator


class DirectoryStructureValidator(BaseValidator):
    """Validates the complete ADOS directory structure"""
    
    def __init__(self):
        super().__init__("DirectoryStructureValidator")
        
        # Define expected crews
        self.expected_crews = [
            'orchestrator',
            'frontend', 
            'backend',
            'security',
            'quality',
            'integration',
            'deployment'
        ]
        
        # Define required subdirectories for each crew
        self.crew_subdirs = [
            'kb',
            'memory', 
            'agents',
            'workspace'
        ]
        
        # Define core system directories
        self.core_directories = [
            'config',
            'tools',
            'output',
            'memory',
            'planner',
            'runner',
            'tests'
        ]
        
        # Define output subdirectories
        self.output_subdirs = [
            'reports',
            'logs',
            'generated_code'
        ]
        
        # Define tools subdirectories
        self.tools_subdirs = [
            'search',
            'codegen',
            'test',
            'deploy'
        ]
        
        # Define memory subdirectories
        self.memory_subdirs = [
            'crew_memory',
            'global_kb'
        ]
    
    def validate(self) -> bool:
        """Run all directory structure validations"""
        
        # Validate core system directories
        self._validate_core_directories()
        
        # Validate crews directory and structure
        self._validate_crews_structure()
        
        # Validate crew-specific directories
        self._validate_crew_directories()
        
        # Validate .gitkeep files
        self._validate_gitkeep_files()
        
        # Validate directory permissions
        self._validate_directory_permissions()
        
        # Return overall validation result
        return all(result.passed for result in self.results)
    
    def _validate_core_directories(self):
        """Validate core system directories exist"""
        for dir_name in self.core_directories:
            dir_path = self.base_path / dir_name
            
            if dir_path.exists() and dir_path.is_dir():
                self.add_result(
                    f"core_directory_{dir_name}",
                    True,
                    f"Core directory '{dir_name}' exists"
                )
            else:
                self.add_result(
                    f"core_directory_{dir_name}",
                    False,
                    f"Core directory '{dir_name}' is missing",
                    {"expected_path": str(dir_path)}
                )
        
        # Validate subdirectories
        self._validate_subdirectories('output', self.output_subdirs)
        self._validate_subdirectories('tools', self.tools_subdirs)
        self._validate_subdirectories('memory', self.memory_subdirs)
    
    def _validate_subdirectories(self, parent_dir: str, subdirs: List[str]):
        """Validate subdirectories under a parent directory"""
        parent_path = self.base_path / parent_dir
        
        if not parent_path.exists():
            return
        
        for subdir in subdirs:
            subdir_path = parent_path / subdir
            
            if subdir_path.exists() and subdir_path.is_dir():
                self.add_result(
                    f"{parent_dir}_{subdir}_subdir",
                    True,
                    f"Subdirectory '{parent_dir}/{subdir}' exists"
                )
            else:
                self.add_result(
                    f"{parent_dir}_{subdir}_subdir",
                    False,
                    f"Subdirectory '{parent_dir}/{subdir}' is missing",
                    {"expected_path": str(subdir_path)}
                )
    
    def _validate_crews_structure(self):
        """Validate the crews directory structure"""
        crews_path = self.base_path / 'crews'
        
        if crews_path.exists() and crews_path.is_dir():
            self.add_result(
                "crews_directory",
                True,
                "Main crews directory exists"
            )
        else:
            self.add_result(
                "crews_directory",
                False,
                "Main crews directory is missing",
                {"expected_path": str(crews_path)}
            )
            return
        
        # Check each expected crew directory
        for crew_name in self.expected_crews:
            crew_path = crews_path / crew_name
            
            if crew_path.exists() and crew_path.is_dir():
                self.add_result(
                    f"crew_{crew_name}_directory",
                    True,
                    f"Crew directory '{crew_name}' exists"
                )
            else:
                self.add_result(
                    f"crew_{crew_name}_directory",
                    False,
                    f"Crew directory '{crew_name}' is missing",
                    {"expected_path": str(crew_path)}
                )
    
    def _validate_crew_directories(self):
        """Validate each crew has required subdirectories"""
        crews_path = self.base_path / 'crews'
        
        if not crews_path.exists():
            return
        
        for crew_name in self.expected_crews:
            crew_path = crews_path / crew_name
            
            if not crew_path.exists():
                continue
            
            # Check each required subdirectory
            for subdir in self.crew_subdirs:
                subdir_path = crew_path / subdir
                
                if subdir_path.exists() and subdir_path.is_dir():
                    self.add_result(
                        f"crew_{crew_name}_{subdir}_subdir",
                        True,
                        f"Crew '{crew_name}' has '{subdir}' subdirectory"
                    )
                else:
                    self.add_result(
                        f"crew_{crew_name}_{subdir}_subdir",
                        False,
                        f"Crew '{crew_name}' missing '{subdir}' subdirectory",
                        {"expected_path": str(subdir_path)}
                    )
    
    def _validate_gitkeep_files(self):
        """Validate .gitkeep files exist in empty directories"""
        gitkeep_locations = []
        
        # Add crew subdirectories
        for crew_name in self.expected_crews:
            for subdir in self.crew_subdirs:
                gitkeep_locations.append(f"crews/{crew_name}/{subdir}/.gitkeep")
        
        # Add other key directories
        for subdir in self.output_subdirs:
            gitkeep_locations.append(f"output/{subdir}/.gitkeep")
        
        for subdir in self.tools_subdirs:
            gitkeep_locations.append(f"tools/{subdir}/.gitkeep")
        
        for subdir in self.memory_subdirs:
            gitkeep_locations.append(f"memory/{subdir}/.gitkeep")
        
        # Check each .gitkeep file
        for gitkeep_path in gitkeep_locations:
            full_path = self.base_path / gitkeep_path
            
            if full_path.exists() and full_path.is_file():
                self.add_result(
                    f"gitkeep_{gitkeep_path.replace('/', '_').replace('.', '_')}",
                    True,
                    f".gitkeep file exists: {gitkeep_path}"
                )
            else:
                # Check if directory exists but .gitkeep is missing
                parent_dir = full_path.parent
                if parent_dir.exists() and parent_dir.is_dir():
                    # Check if directory is empty (excluding .gitkeep)
                    contents = list(parent_dir.iterdir())
                    if len(contents) == 0:
                        self.add_result(
                            f"gitkeep_{gitkeep_path.replace('/', '_').replace('.', '_')}",
                            False,
                            f".gitkeep file missing in empty directory: {gitkeep_path}",
                            {"expected_path": str(full_path)}
                        )
                    else:
                        # Directory has content, .gitkeep not strictly required
                        self.add_result(
                            f"gitkeep_{gitkeep_path.replace('/', '_').replace('.', '_')}",
                            True,
                            f".gitkeep not required (directory has content): {gitkeep_path}"
                        )
    
    def _validate_directory_permissions(self):
        """Validate directory permissions and accessibility"""
        critical_paths = [
            self.base_path / 'config',
            self.base_path / 'crews',
            self.base_path / 'output',
            self.base_path / 'tests'
        ]
        
        for path in critical_paths:
            if not path.exists():
                continue
            
            # Test read access
            try:
                list(path.iterdir())
                self.add_result(
                    f"permissions_read_{path.name}",
                    True,
                    f"Directory '{path.name}' is readable"
                )
            except PermissionError:
                self.add_result(
                    f"permissions_read_{path.name}",
                    False,
                    f"Directory '{path.name}' is not readable",
                    {"path": str(path)}
                )
            
            # Test write access (create temporary file)
            try:
                temp_file = path / '.temp_validation_test'
                temp_file.touch()
                temp_file.unlink()
                
                self.add_result(
                    f"permissions_write_{path.name}",
                    True,
                    f"Directory '{path.name}' is writable"
                )
            except (PermissionError, OSError):
                self.add_result(
                    f"permissions_write_{path.name}",
                    False,
                    f"Directory '{path.name}' is not writable",
                    {"path": str(path)}
                )
    
    def get_structure_summary(self) -> Dict[str, Any]:
        """Get a summary of the directory structure"""
        summary = {
            'core_directories': {},
            'crews': {},
            'total_directories': 0,
            'missing_directories': [],
            'gitkeep_files': 0,
            'missing_gitkeep': []
        }
        
        # Count directories and issues
        for result in self.results:
            if 'directory' in result.name:
                summary['total_directories'] += 1
                if not result.passed:
                    summary['missing_directories'].append(result.name)
            elif 'gitkeep' in result.name:
                if result.passed:
                    summary['gitkeep_files'] += 1
                else:
                    summary['missing_gitkeep'].append(result.name)
        
        return summary