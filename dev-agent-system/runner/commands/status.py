"""
ADOS Status Command

This module implements the status command for the ADOS CLI.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns

from ..utils.config import get_config_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


def status_command(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed status information"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output status as JSON")
):
    """
    Show current system status and configuration.
    
    This command displays the current state of the ADOS project including
    directory structure, configuration files, and system health.
    """
    logger.debug("Executing status command")
    
    config_manager = get_config_manager()
    
    # Gather status information
    project_info = config_manager.get_project_info()
    dir_status = config_manager.check_directory_structure()
    is_ados_project = config_manager.is_ados_project()
    config_files = _check_configuration_files(config_manager)
    
    if json_output:
        _output_json_status(project_info, dir_status, is_ados_project, config_files)
    else:
        _output_formatted_status(project_info, dir_status, is_ados_project, config_files, detailed)
    
    logger.debug("Status command completed")


def _check_configuration_files(config_manager) -> Dict[str, bool]:
    """
    Check the status of configuration files.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        Dictionary with config file status
    """
    config_files = {
        "pyproject.toml": (config_manager.base_path / "pyproject.toml").exists(),
        "requirements.txt": (config_manager.base_path / "requirements.txt").exists(),
        ".env.example": (config_manager.base_path / ".env.example").exists(),
        ".env": (config_manager.base_path / ".env").exists(),
        ".gitignore": (config_manager.base_path / ".gitignore").exists(),
    }
    
    # Check for future config files
    config_dir = config_manager.base_path / "config"
    if config_dir.exists():
        config_files.update({
            "config/crews.yaml": (config_dir / "crews.yaml").exists(),
            "config/agents.yaml": (config_dir / "agents.yaml").exists(),
            "config/tech_stack.json": (config_dir / "tech_stack.json").exists(),
            "config/system_settings.json": (config_dir / "system_settings.json").exists(),
        })
    
    return config_files


def _output_json_status(
    project_info: dict,
    dir_status: dict,
    is_ados_project: bool,
    config_files: dict
):
    """
    Output status information as JSON.
    
    Args:
        project_info: Project information
        dir_status: Directory structure status
        is_ados_project: Whether this is an ADOS project
        config_files: Configuration files status
    """
    import json
    
    status_data = {
        "project": {
            "name": project_info.get("name", "unknown"),
            "version": project_info.get("version", "unknown"),
            "description": project_info.get("description", ""),
            "python_requires": project_info.get("python_requires", ""),
            "is_ados_project": is_ados_project,
            "directory": str(Path.cwd())
        },
        "directories": dir_status,
        "configuration_files": config_files,
        "summary": {
            "directories_valid": sum(1 for exists in dir_status.values() if exists),
            "directories_total": len(dir_status),
            "config_files_found": sum(1 for exists in config_files.values() if exists),
            "config_files_total": len(config_files),
            "overall_status": "healthy" if is_ados_project and all(dir_status.values()) else "issues"
        }
    }
    
    console.print(json.dumps(status_data, indent=2))


def _output_formatted_status(
    project_info: dict,
    dir_status: dict,
    is_ados_project: bool,
    config_files: dict,
    detailed: bool
):
    """
    Output formatted status information.
    
    Args:
        project_info: Project information
        dir_status: Directory structure status
        is_ados_project: Whether this is an ADOS project
        config_files: Configuration files status
        detailed: Whether to show detailed information
    """
    # Project Overview
    console.print(Panel.fit(
        f"[bold]{project_info.get('name', 'Unknown Project')}[/bold] v{project_info.get('version', 'unknown')}\n"
        f"[dim]{project_info.get('description', 'No description available')}[/dim]\n"
        f"Location: {Path.cwd()}",
        title="Project Overview",
        border_style="blue"
    ))
    
    # Project Status
    if is_ados_project:
        status_text = "✓ Valid ADOS Project"
        status_color = "green"
    else:
        status_text = "✗ Not an ADOS Project"
        status_color = "red"
    
    console.print(f"\n[bold]Project Status:[/bold] [{status_color}]{status_text}[/{status_color}]")
    
    # Directory Structure
    console.print(f"\n[bold]Directory Structure:[/bold]")
    dir_table = Table(show_header=True, header_style="bold cyan")
    dir_table.add_column("Directory", style="white", width=20)
    dir_table.add_column("Status", style="white", width=10)
    dir_table.add_column("Purpose", style="dim", width=40)
    
    directory_purposes = {
        "crews": "Agent crews and team configurations",
        "tools": "Shared tools and utilities",
        "memory": "Knowledge base and crew memory",
        "planner": "Task planning and orchestration",
        "config": "Configuration files and settings",
        "runner": "CLI application and commands",
        "output": "Generated outputs and reports"
    }
    
    for dir_name, exists in dir_status.items():
        status = "✓" if exists else "✗"
        color = "green" if exists else "red"
        purpose = directory_purposes.get(dir_name, "ADOS component")
        dir_table.add_row(dir_name, f"[{color}]{status}[/{color}]", purpose)
    
    console.print(dir_table)
    
    # Configuration Files
    if detailed or not all(config_files.values()):
        console.print(f"\n[bold]Configuration Files:[/bold]")
        config_table = Table(show_header=True, header_style="bold cyan")
        config_table.add_column("File", style="white", width=25)
        config_table.add_column("Status", style="white", width=10)
        config_table.add_column("Description", style="dim", width=35)
        
        file_descriptions = {
            "pyproject.toml": "Project metadata and dependencies",
            "requirements.txt": "Pinned dependency versions",
            ".env.example": "Environment variable template",
            ".env": "Local environment configuration",
            ".gitignore": "Git ignore patterns",
            "config/crews.yaml": "Crew templates and definitions",
            "config/agents.yaml": "Agent configurations",
            "config/tech_stack.json": "Technology preferences",
            "config/system_settings.json": "System configuration"
        }
        
        for filename, exists in config_files.items():
            status = "✓" if exists else "✗"
            color = "green" if exists else "red"
            desc = file_descriptions.get(filename, "Configuration file")
            config_table.add_row(filename, f"[{color}]{status}[/{color}]", desc)
        
        console.print(config_table)
    
    # Summary
    dir_valid = sum(1 for exists in dir_status.values() if exists)
    dir_total = len(dir_status)
    config_found = sum(1 for exists in config_files.values() if exists)
    config_total = len(config_files)
    
    summary_panels = []
    
    # Directory summary
    if dir_valid == dir_total:
        dir_summary = f"✓ {dir_valid}/{dir_total} directories"
        dir_color = "green"
    else:
        dir_summary = f"⚠ {dir_valid}/{dir_total} directories"
        dir_color = "yellow"
    
    summary_panels.append(Panel(dir_summary, title="Directories", border_style=dir_color))
    
    # Config summary
    if config_found >= 5:  # At least basic files
        config_summary = f"✓ {config_found}/{config_total} files"
        config_color = "green"
    else:
        config_summary = f"⚠ {config_found}/{config_total} files"
        config_color = "yellow"
    
    summary_panels.append(Panel(config_summary, title="Configuration", border_style=config_color))
    
    # Overall health
    if is_ados_project and dir_valid == dir_total and config_found >= 5:
        health_summary = "✓ Healthy"
        health_color = "green"
    elif is_ados_project:
        health_summary = "⚠ Issues Found"
        health_color = "yellow"
    else:
        health_summary = "✗ Not Ready"
        health_color = "red"
    
    summary_panels.append(Panel(health_summary, title="Overall Health", border_style=health_color))
    
    console.print("\n[bold]Summary:[/bold]")
    console.print(Columns(summary_panels))
    
    # Suggestions
    if not is_ados_project:
        console.print(Panel(
            "Run 'ados init' to initialize this directory as an ADOS project.",
            title="Suggestion",
            border_style="blue"
        ))
    elif dir_valid < dir_total:
        console.print(Panel(
            "Run 'ados init' to create missing directories.",
            title="Suggestion",
            border_style="blue"
        ))


if __name__ == "__main__":
    status_command()