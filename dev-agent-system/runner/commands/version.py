"""
ADOS Version Command

This module implements the version command for the ADOS CLI.
"""

import platform
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..utils.config import get_config_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


def version_command():
    """
    Show version information for ADOS and system dependencies.
    """
    logger.debug("Executing version command")
    
    # Get configuration manager
    config_manager = get_config_manager()
    project_info = config_manager.get_project_info()
    
    # Create version table
    table = Table(title="ADOS Version Information", show_header=True)
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Version", style="green", width=15)
    table.add_column("Details", style="white", width=40)
    
    # ADOS Version
    table.add_row(
        "ADOS",
        project_info.get("version", "unknown"),
        project_info.get("description", "AI Dev Orchestration System")
    )
    
    # Python Version
    table.add_row(
        "Python",
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        f"{platform.python_implementation()}"
    )
    
    # System Information
    table.add_row(
        "Platform",
        platform.system(),
        f"{platform.machine()}, {platform.release()}"
    )
    
    # Python Requirements
    python_requires = project_info.get("python_requires", "")
    if python_requires:
        table.add_row(
            "Python Required",
            python_requires,
            "Project requirement"
        )
    
    # Key Dependencies
    dependencies = project_info.get("dependencies", [])
    key_deps = []
    for dep in dependencies:
        if any(pkg in dep.lower() for pkg in ["typer", "crewai", "openai", "chromadb"]):
            key_deps.append(dep)
    
    if key_deps:
        table.add_row(
            "Key Dependencies",
            str(len(key_deps)),
            ", ".join(key_deps[:3]) + ("..." if len(key_deps) > 3 else "")
        )
    
    # Project Status
    is_ados_project = config_manager.is_ados_project()
    project_status = "✓ Valid ADOS Project" if is_ados_project else "✗ Not an ADOS Project"
    project_color = "green" if is_ados_project else "red"
    
    table.add_row(
        "Project Status",
        project_status,
        f"Directory: {Path.cwd()}"
    )
    
    # Display the table
    console.print(table)
    
    # Additional system info panel
    if is_ados_project:
        dir_status = config_manager.check_directory_structure()
        valid_dirs = sum(1 for status in dir_status.values() if status)
        total_dirs = len(dir_status)
        
        status_text = f"Directory Structure: {valid_dirs}/{total_dirs} directories found"
        if valid_dirs == total_dirs:
            status_text += " ✓"
            status_color = "green"
        else:
            status_text += " ⚠"
            status_color = "yellow"
        
        console.print(Panel(status_text, title="Project Health", border_style=status_color))
    
    logger.debug("Version command completed")


if __name__ == "__main__":
    version_command()