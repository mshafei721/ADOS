"""
Knowledge Base Validator

This validator ensures that all ADOS knowledge base files are present,
properly structured, and contain appropriate content.

Validates:
- All 14 knowledge base files exist and are readable
- Files have proper markdown structure
- Content is appropriate for each crew's domain
- File organization follows expected structure
- Knowledge base files are accessible to their respective crews
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import re

from tests.validators import BaseValidator


class KnowledgeBaseValidator(BaseValidator):
    """Validates all ADOS knowledge base files and their contents"""
    
    def __init__(self):
        super().__init__("KnowledgeBaseValidator")
        
        # Define expected knowledge base files per crew
        self.expected_kb_files = {
            'orchestrator': ['system_design.md', 'task_decomposition.md'],
            'frontend': ['react_patterns.md', 'accessibility.md'],
            'backend': ['fastapi_patterns.md'],
            'security': ['owasp_guidelines.md'],
            'quality': ['testing_frameworks.md'],
            'integration': ['cicd_pipelines.md'],
            'deployment': ['docker_best_practices.md']
        }
        
        # Total expected files
        self.total_expected_files = sum(len(files) for files in self.expected_kb_files.values())
        
        # Expected content patterns for validation
        self.content_patterns = {
            'system_design.md': ['architecture', 'system', 'design', 'components'],
            'task_decomposition.md': ['task', 'decomposition', 'workflow', 'planning'],
            'react_patterns.md': ['react', 'component', 'patterns', 'frontend'],
            'accessibility.md': ['accessibility', 'a11y', 'wcag', 'inclusive'],
            'fastapi_patterns.md': ['fastapi', 'api', 'backend', 'python'],
            'owasp_guidelines.md': ['owasp', 'security', 'vulnerability', 'guidelines'],
            'testing_frameworks.md': ['testing', 'framework', 'unit', 'integration'],
            'cicd_pipelines.md': ['ci', 'cd', 'pipeline', 'deployment'],
            'docker_best_practices.md': ['docker', 'container', 'best', 'practices']
        }
        
        # Minimum content length per file (characters)
        self.min_content_length = 100
        
        # Markdown structure requirements
        self.markdown_requirements = {
            'headers': r'^#',
            'content': r'\\w+',
            'structure': r'^#\\s+.+$'
        }
    
    def validate(self) -> bool:
        """Run all knowledge base validations"""
        
        # Validate KB directory structure
        self._validate_kb_directory_structure()
        
        # Validate all KB files exist
        self._validate_kb_files_exist()
        
        # Validate file contents
        self._validate_file_contents()
        
        # Validate markdown structure
        self._validate_markdown_structure()
        
        # Validate file accessibility
        self._validate_file_accessibility()
        
        # Validate content appropriateness
        self._validate_content_appropriateness()
        
        # Return overall validation result
        return all(result.passed for result in self.results)
    
    def _validate_kb_directory_structure(self):
        """Validate the knowledge base directory structure"""
        crews_path = self.base_path / 'crews'
        
        if not crews_path.exists():
            self.add_result(
                "kb_crews_directory",
                False,
                "Crews directory does not exist"
            )
            return
        
        # Check each crew has kb directory
        for crew_name in self.expected_kb_files.keys():
            crew_kb_path = crews_path / crew_name / 'kb'
            
            if crew_kb_path.exists() and crew_kb_path.is_dir():
                self.add_result(
                    f"kb_directory_{crew_name}",
                    True,
                    f"KB directory exists for crew '{crew_name}'"
                )
            else:
                self.add_result(
                    f"kb_directory_{crew_name}",
                    False,
                    f"KB directory missing for crew '{crew_name}'",
                    {"expected_path": str(crew_kb_path)}
                )
    
    def _validate_kb_files_exist(self):
        """Validate all expected knowledge base files exist"""
        crews_path = self.base_path / 'crews'
        
        for crew_name, kb_files in self.expected_kb_files.items():
            crew_kb_path = crews_path / crew_name / 'kb'
            
            if not crew_kb_path.exists():
                continue
            
            for kb_file in kb_files:
                kb_file_path = crew_kb_path / kb_file
                
                if kb_file_path.exists() and kb_file_path.is_file():
                    self.add_result(
                        f"kb_file_{crew_name}_{kb_file.replace('.', '_')}",
                        True,
                        f"KB file '{kb_file}' exists for crew '{crew_name}'"
                    )
                else:
                    self.add_result(
                        f"kb_file_{crew_name}_{kb_file.replace('.', '_')}",
                        False,
                        f"KB file '{kb_file}' missing for crew '{crew_name}'",
                        {"expected_path": str(kb_file_path)}
                    )
    
    def _validate_file_contents(self):
        """Validate the contents of knowledge base files"""
        crews_path = self.base_path / 'crews'
        
        for crew_name, kb_files in self.expected_kb_files.items():
            crew_kb_path = crews_path / crew_name / 'kb'
            
            if not crew_kb_path.exists():
                continue
            
            for kb_file in kb_files:
                kb_file_path = crew_kb_path / kb_file
                
                if not kb_file_path.exists():
                    continue
                
                try:
                    with open(kb_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file has content
                    if len(content.strip()) >= self.min_content_length:
                        self.add_result(
                            f"kb_content_{crew_name}_{kb_file.replace('.', '_')}",
                            True,
                            f"KB file '{kb_file}' has adequate content ({len(content)} chars)"
                        )
                    else:
                        self.add_result(
                            f"kb_content_{crew_name}_{kb_file.replace('.', '_')}",
                            False,
                            f"KB file '{kb_file}' has insufficient content ({len(content)} chars, min {self.min_content_length})"
                        )
                    
                    # Check file is readable
                    self.add_result(
                        f"kb_readable_{crew_name}_{kb_file.replace('.', '_')}",
                        True,
                        f"KB file '{kb_file}' is readable"
                    )
                    
                except Exception as e:
                    self.add_result(
                        f"kb_readable_{crew_name}_{kb_file.replace('.', '_')}",
                        False,
                        f"KB file '{kb_file}' is not readable: {str(e)}"
                    )
                    
                    self.add_result(
                        f"kb_content_{crew_name}_{kb_file.replace('.', '_')}",
                        False,
                        f"KB file '{kb_file}' content could not be validated due to read error"
                    )
    
    def _validate_markdown_structure(self):
        """Validate markdown structure of knowledge base files"""
        crews_path = self.base_path / 'crews'
        
        for crew_name, kb_files in self.expected_kb_files.items():
            crew_kb_path = crews_path / crew_name / 'kb'
            
            if not crew_kb_path.exists():
                continue
            
            for kb_file in kb_files:
                kb_file_path = crew_kb_path / kb_file
                
                if not kb_file_path.exists():
                    continue
                
                try:
                    with open(kb_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for markdown headers
                    if re.search(self.markdown_requirements['headers'], content, re.MULTILINE):
                        self.add_result(
                            f"kb_markdown_{crew_name}_{kb_file.replace('.', '_')}",
                            True,
                            f"KB file '{kb_file}' has proper markdown headers"
                        )
                    else:
                        self.add_result(
                            f"kb_markdown_{crew_name}_{kb_file.replace('.', '_')}",
                            False,
                            f"KB file '{kb_file}' missing markdown headers"
                        )
                    
                    # Check for structured content
                    if re.search(self.markdown_requirements['structure'], content, re.MULTILINE):
                        self.add_result(
                            f"kb_structure_{crew_name}_{kb_file.replace('.', '_')}",
                            True,
                            f"KB file '{kb_file}' has structured content"
                        )
                    else:
                        self.add_result(
                            f"kb_structure_{crew_name}_{kb_file.replace('.', '_')}",
                            False,
                            f"KB file '{kb_file}' lacks structured content"
                        )
                    
                except Exception as e:
                    self.add_result(
                        f"kb_markdown_{crew_name}_{kb_file.replace('.', '_')}",
                        False,
                        f"KB file '{kb_file}' markdown validation failed: {str(e)}"
                    )
    
    def _validate_file_accessibility(self):
        """Validate files are accessible with proper permissions"""
        crews_path = self.base_path / 'crews'
        
        for crew_name, kb_files in self.expected_kb_files.items():
            crew_kb_path = crews_path / crew_name / 'kb'
            
            if not crew_kb_path.exists():
                continue
            
            # Test directory permissions
            try:
                list(crew_kb_path.iterdir())
                self.add_result(
                    f"kb_access_{crew_name}_directory",
                    True,
                    f"KB directory for crew '{crew_name}' is accessible"
                )
            except PermissionError:
                self.add_result(
                    f"kb_access_{crew_name}_directory",
                    False,
                    f"KB directory for crew '{crew_name}' is not accessible"
                )
            
            # Test file permissions
            for kb_file in kb_files:
                kb_file_path = crew_kb_path / kb_file
                
                if not kb_file_path.exists():
                    continue
                
                try:
                    with open(kb_file_path, 'r', encoding='utf-8') as f:
                        f.read(1)  # Try to read one character
                    
                    self.add_result(
                        f"kb_access_{crew_name}_{kb_file.replace('.', '_')}",
                        True,
                        f"KB file '{kb_file}' is accessible"
                    )
                except PermissionError:
                    self.add_result(
                        f"kb_access_{crew_name}_{kb_file.replace('.', '_')}",
                        False,
                        f"KB file '{kb_file}' is not accessible"
                    )
                except Exception as e:
                    self.add_result(
                        f"kb_access_{crew_name}_{kb_file.replace('.', '_')}",
                        False,
                        f"KB file '{kb_file}' accessibility test failed: {str(e)}"
                    )
    
    def _validate_content_appropriateness(self):
        """Validate content is appropriate for each crew's domain"""
        crews_path = self.base_path / 'crews'
        
        for crew_name, kb_files in self.expected_kb_files.items():
            crew_kb_path = crews_path / crew_name / 'kb'
            
            if not crew_kb_path.exists():
                continue
            
            for kb_file in kb_files:
                kb_file_path = crew_kb_path / kb_file
                
                if not kb_file_path.exists():
                    continue
                
                try:
                    with open(kb_file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    # Check for expected content patterns
                    expected_patterns = self.content_patterns.get(kb_file, [])
                    if expected_patterns:
                        patterns_found = [
                            pattern for pattern in expected_patterns 
                            if pattern in content
                        ]
                        
                        # Require at least half the patterns to be found
                        required_patterns = max(1, len(expected_patterns) // 2)
                        
                        if len(patterns_found) >= required_patterns:
                            self.add_result(
                                f"kb_appropriate_{crew_name}_{kb_file.replace('.', '_')}",
                                True,
                                f"KB file '{kb_file}' has appropriate content for domain"
                            )
                        else:
                            self.add_result(
                                f"kb_appropriate_{crew_name}_{kb_file.replace('.', '_')}",
                                False,
                                f"KB file '{kb_file}' may not have appropriate content for domain",
                                {"expected_patterns": expected_patterns, "found_patterns": patterns_found}
                            )
                    else:
                        # No specific patterns defined, just check it's not empty
                        if content.strip():
                            self.add_result(
                                f"kb_appropriate_{crew_name}_{kb_file.replace('.', '_')}",
                                True,
                                f"KB file '{kb_file}' has content"
                            )
                        else:
                            self.add_result(
                                f"kb_appropriate_{crew_name}_{kb_file.replace('.', '_')}",
                                False,
                                f"KB file '{kb_file}' is empty"
                            )
                    
                except Exception as e:
                    self.add_result(
                        f"kb_appropriate_{crew_name}_{kb_file.replace('.', '_')}",
                        False,
                        f"KB file '{kb_file}' content validation failed: {str(e)}"
                    )
    
    def get_kb_summary(self) -> Dict[str, Any]:
        """Get a summary of knowledge base validation results"""
        summary = {
            'total_expected_files': self.total_expected_files,
            'existing_files': 0,
            'readable_files': 0,
            'properly_structured': 0,
            'appropriate_content': 0,
            'missing_files': [],
            'crews_with_kb': 0,
            'crews_missing_kb': []
        }
        
        # Count existing files
        for crew_name, kb_files in self.expected_kb_files.items():
            crew_has_kb = False
            
            for kb_file in kb_files:
                file_key = f"kb_file_{crew_name}_{kb_file.replace('.', '_')}"
                
                # Check if file exists
                if any(result.passed for result in self.results if result.name == file_key):
                    summary['existing_files'] += 1
                    crew_has_kb = True
                else:
                    summary['missing_files'].append(f"{crew_name}/{kb_file}")
                
                # Check if file is readable
                readable_key = f"kb_readable_{crew_name}_{kb_file.replace('.', '_')}"
                if any(result.passed for result in self.results if result.name == readable_key):
                    summary['readable_files'] += 1
                
                # Check if file has proper structure
                structure_key = f"kb_structure_{crew_name}_{kb_file.replace('.', '_')}"
                if any(result.passed for result in self.results if result.name == structure_key):
                    summary['properly_structured'] += 1
                
                # Check if file has appropriate content
                content_key = f"kb_appropriate_{crew_name}_{kb_file.replace('.', '_')}"
                if any(result.passed for result in self.results if result.name == content_key):
                    summary['appropriate_content'] += 1
            
            if crew_has_kb:
                summary['crews_with_kb'] += 1
            else:
                summary['crews_missing_kb'].append(crew_name)
        
        return summary