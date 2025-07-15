"""
ADOS Init Command

This module implements the init command for the ADOS CLI.
"""

import sys
from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.config import get_config_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


def init_command(
    force: bool = typer.Option(False, "--force", "-f", help="Force initialization even if project exists"),
    check_only: bool = typer.Option(False, "--check-only", "-c", help="Only check current setup without modifying")
):
    """
    Initialize a new ADOS project workspace.
    
    This command checks the current directory structure, validates dependencies,
    and ensures the ADOS project is properly set up.
    """
    logger.debug("Executing init command")
    
    config_manager = get_config_manager()
    
    # Check if already an ADOS project
    is_ados_project = config_manager.is_ados_project()
    
    if is_ados_project and not force and not check_only:
        console.print(Panel(
            "This directory is already an ADOS project.\n"
            "Use --force to reinitialize or --check-only to validate setup.",
            title="Already Initialized",
            border_style="yellow"
        ))
        return
    
    # Perform initialization checks
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        # Check directory structure
        progress.add_task("Checking directory structure...", total=None)
        dir_status = config_manager.check_directory_structure()
        
        # Check project configuration
        progress.add_task("Validating project configuration...", total=None)
        project_info = config_manager.get_project_info()
        
        # Check dependencies
        progress.add_task("Checking dependencies...", total=None)
        dep_issues = _check_dependencies(project_info)
    
    # Report results
    _report_initialization_results(dir_status, project_info, dep_issues, check_only)
    
    if not check_only:
        _perform_initialization_actions(dir_status, force)
    
    logger.debug("Init command completed")


def _check_dependencies(project_info: dict) -> List[str]:
    """
    Check if required dependencies are available.
    
    Args:
        project_info: Project information dictionary
        
    Returns:
        List of dependency issues
    """
    issues = []
    
    # Check key imports
    required_packages = [
        ("typer", "typer"),
        ("crewai", "crewai"),
        ("openai", "openai"),
        ("chromadb", "chromadb"),
        ("pydantic", "pydantic"),
        ("python-dotenv", "dotenv"),
        ("rich", "rich")
    ]
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            logger.debug(f"✓ {package_name} is available")
        except ImportError:
            issues.append(f"Missing dependency: {package_name}")
            logger.warning(f"✗ {package_name} not found")
    
    return issues


def _report_initialization_results(
    dir_status: dict,
    project_info: dict,
    dep_issues: List[str],
    check_only: bool
):
    """
    Report the results of initialization checks.
    
    Args:
        dir_status: Directory structure status
        project_info: Project information
        dep_issues: Dependency issues
        check_only: Whether this is a check-only operation
    """
    # Directory status
    console.print("\n[bold]Directory Structure:[/bold]")
    for dir_name, exists in dir_status.items():
        status = "✓" if exists else "✗"
        color = "green" if exists else "red"
        console.print(f"  {status} {dir_name}", style=color)
    
    # Project info
    console.print("\n[bold]Project Information:[/bold]")
    console.print(f"  Name: {project_info.get('name', 'Unknown')}")
    console.print(f"  Version: {project_info.get('version', 'Unknown')}")
    console.print(f"  Python Requirements: {project_info.get('python_requires', 'Not specified')}")
    
    # Dependencies
    console.print("\n[bold]Dependencies:[/bold]")
    if dep_issues:
        for issue in dep_issues:
            console.print(f"  ✗ {issue}", style="red")
    else:
        console.print("  ✓ All required dependencies are available", style="green")
    
    # Summary
    missing_dirs = sum(1 for exists in dir_status.values() if not exists)
    total_issues = missing_dirs + len(dep_issues)
    
    if total_issues == 0:
        console.print(Panel(
            "✓ ADOS project is properly initialized and ready to use!",
            title="Initialization Complete",
            border_style="green"
        ))
    else:
        action_text = "would be" if check_only else "will be"
        console.print(Panel(
            f"Found {total_issues} issue(s) that {action_text} addressed.",
            title="Initialization Issues",
            border_style="yellow"
        ))


def _perform_initialization_actions(dir_status: dict, force: bool):
    """
    Perform actual initialization actions.
    
    Args:
        dir_status: Directory structure status
        force: Whether to force initialization
    """
    actions_taken = []
    
    # Create missing directories
    for dir_name, exists in dir_status.items():
        if not exists:
            dir_path = Path.cwd() / dir_name
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                actions_taken.append(f"Created directory: {dir_name}")
                logger.info(f"Created directory: {dir_path}")
            except Exception as e:
                console.print(f"[red]Failed to create directory {dir_name}: {e}[/red]")
                logger.error(f"Failed to create directory {dir_path}: {e}")
    
    # Report actions taken
    if actions_taken:
        console.print("\n[bold]Actions Taken:[/bold]")
        for action in actions_taken:
            console.print(f"  ✓ {action}", style="green")
    else:
        console.print("\n[bold]No actions needed - project structure is complete.[/bold]")


if __name__ == "__main__":
    init_command()