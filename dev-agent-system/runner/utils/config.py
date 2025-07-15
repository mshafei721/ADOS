"""
ADOS Configuration Utilities

This module provides utilities for handling ADOS configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    Configuration manager for ADOS CLI.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            base_path: Base path for configuration files
        """
        self.base_path = base_path or Path.cwd()
        self.config_dir = self.base_path / "config"
        
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML configuration file.
        
        Args:
            filename: Name of the YAML file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.debug(f"Loaded YAML configuration from {config_path}")
            return config or {}
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML file {config_path}: {e}")
            raise
            
    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file.
        
        Args:
            filename: Name of the JSON file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON parsing fails
        """
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"Loaded JSON configuration from {config_path}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {config_path}: {e}")
            raise
            
    def check_directory_structure(self) -> Dict[str, bool]:
        """
        Check if required ADOS directories exist.
        
        Returns:
            Dictionary with directory names and existence status
        """
        required_dirs = [
            "crews",
            "tools", 
            "memory",
            "planner",
            "config",
            "runner",
            "output"
        ]
        
        status = {}
        for dir_name in required_dirs:
            dir_path = self.base_path / dir_name
            status[dir_name] = dir_path.exists() and dir_path.is_dir()
            
        return status
        
    def get_project_info(self) -> Dict[str, Any]:
        """
        Get project information from pyproject.toml.
        
        Returns:
            Project information dictionary
        """
        pyproject_path = self.base_path / "pyproject.toml"
        
        if not pyproject_path.exists():
            return {"name": "ADOS", "version": "unknown"}
            
        try:
            # Try tomllib first (Python 3.11+), fallback to toml
            try:
                import tomllib
                with open(pyproject_path, 'rb') as f:
                    data = tomllib.load(f)
            except ImportError:
                import toml
                with open(pyproject_path, 'r') as f:
                    data = toml.load(f)
            
            project_info = data.get("project", {})
            return {
                "name": project_info.get("name", "ADOS"),
                "version": project_info.get("version", "unknown"),
                "description": project_info.get("description", ""),
                "python_requires": project_info.get("requires-python", ""),
                "dependencies": project_info.get("dependencies", [])
            }
        except Exception as e:
            logger.error(f"Failed to read pyproject.toml: {e}")
            return {"name": "ADOS", "version": "unknown"}
            
    def is_ados_project(self) -> bool:
        """
        Check if current directory is an ADOS project.
        
        Returns:
            True if this is an ADOS project directory
        """
        # Check for key indicators
        indicators = [
            self.base_path / "pyproject.toml",
            self.base_path / "runner",
            self.base_path / "crews",
            self.base_path / "config"
        ]
        
        return all(path.exists() for path in indicators)


def get_config_manager(base_path: Optional[Path] = None) -> ConfigManager:
    """
    Get a configuration manager instance.
    
    Args:
        base_path: Base path for configuration files
        
    Returns:
        ConfigManager instance
    """
    return ConfigManager(base_path)