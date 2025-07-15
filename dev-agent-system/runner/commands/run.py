"""
ADOS Run Command

This module implements the run command for the ADOS CLI.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.config import get_config_manager
from ..utils.logger import get_logger
from orchestrator.main import ADOSOrchestrator

logger = get_logger(__name__)
console = Console()


def run_command(
    task: Optional[str] = typer.Argument(None, help="Specific task to run"),
    crew: Optional[str] = typer.Option(None, "--crew", "-c", help="Specific crew to execute"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be executed without running"),
    config_file: Optional[str] = typer.Option(None, "--config", help="Path to configuration file"),
):
    """
    Execute ADOS orchestration.
    
    This command runs the ADOS orchestration system to execute AI crews
    and manage development workflows. In Phase 1, this is a placeholder
    that validates the setup and shows future capabilities.
    """
    logger.debug("Executing run command")
    
    config_manager = get_config_manager()
    
    # Check if this is an ADOS project
    if not config_manager.is_ados_project():
        console.print(Panel(
            "This directory is not an ADOS project.\n"
            "Run 'ados init' to initialize the project first.",
            title="Not an ADOS Project",
            border_style="red"
        ))
        logger.error("Attempted to run ADOS in non-ADOS project directory")
        raise typer.Exit(1)
    
    # Validate project setup
    dir_status = config_manager.check_directory_structure()
    missing_dirs = [name for name, exists in dir_status.items() if not exists]
    
    if missing_dirs:
        console.print(Panel(
            f"Missing required directories: {', '.join(missing_dirs)}\n"
            "Run 'ados init' to create missing directories.",
            title="Project Setup Issues",
            border_style="yellow"
        ))
        logger.warning(f"Missing directories: {missing_dirs}")
        if not dry_run:
            raise typer.Exit(1)
    
    # Show what would be executed
    if dry_run:
        _show_dry_run_info(task, crew, config_file)
        return
    
    # Phase 2 Implementation - Core Orchestrator
    _run_with_orchestrator(task, crew, config_file)
    
    logger.debug("Run command completed")


def _show_dry_run_info(task: Optional[str], crew: Optional[str], config_file: Optional[str]):
    """
    Show what would be executed in a dry run.
    
    Args:
        task: Specific task to run
        crew: Specific crew to execute
        config_file: Path to configuration file
    """
    console.print(Panel.fit(
        "[bold cyan]Dry Run - What Would Be Executed:[/bold cyan]",
        border_style="cyan"
    ))
    
    console.print(f"[bold]Task:[/bold] {task or 'Default orchestration'}")
    console.print(f"[bold]Crew:[/bold] {crew or 'All available crews'}")
    console.print(f"[bold]Config:[/bold] {config_file or 'Default configuration'}")
    console.print(f"[bold]Working Directory:[/bold] {Path.cwd()}")
    
    console.print("\n[bold]Execution Plan:[/bold]")
    console.print("1. Load configuration from config/ directory")
    console.print("2. Initialize crew managers and agents")
    console.print("3. Execute task orchestration")
    console.print("4. Generate outputs to output/ directory")
    console.print("5. Update crew memory and knowledge base")
    
    console.print("\n[dim]Note: This is a dry run. No actual execution performed.[/dim]")


def _run_with_orchestrator(task: Optional[str], crew: Optional[str], config_file: Optional[str]):
    """
    Run ADOS with the new orchestrator system.
    
    Args:
        task: Specific task to run
        crew: Specific crew to execute
        config_file: Path to configuration file
    """
    console.print(Panel.fit(
        "[bold green]ADOS Phase 2 - Core Orchestrator[/bold green]",
        border_style="green"
    ))
    
    try:
        # Initialize orchestrator
        console.print("Initializing ADOS orchestrator...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            init_task = progress.add_task("Loading configuration and initializing crews...", total=None)
            
            # Create and initialize orchestrator
            orchestrator = ADOSOrchestrator()
            success = orchestrator.initialize()
            
            if not success:
                console.print("[red]Failed to initialize orchestrator[/red]")
                raise typer.Exit(1)
        
        # Show system status
        status = orchestrator.get_system_status()
        console.print(f"✓ Orchestrator initialized successfully")
        console.print(f"✓ {status['crews']['initialized']}/{status['crews']['total']} crews initialized")
        console.print(f"✓ {status['agents']['initialized']}/{status['agents']['total']} agents initialized")
        
        # Show crew distribution
        console.print("\n[bold]Crew Distribution:[/bold]")
        for crew_name, agent_count in status['crew_distribution'].items():
            console.print(f"• {crew_name}: {agent_count} agents")
        
        # Execute task if specified
        if task:
            console.print(f"\n[bold]Executing task:[/bold] {task}")
            target_crew = crew or "orchestrator"
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                exec_task = progress.add_task(f"Executing task with {target_crew} crew...", total=None)
                
                result = orchestrator.execute_simple_task(task, target_crew)
                
                if result:
                    console.print(f"✓ Task completed successfully")
                    console.print(Panel(result, title="Task Result", border_style="green"))
                else:
                    console.print("[red]Task execution failed[/red]")
        else:
            console.print("\n[dim]No task specified. Use --help for usage information.[/dim]")
        
        # Show available crews
        console.print("\n[bold]Available Crews:[/bold]")
        for crew_name in orchestrator.list_crews():
            console.print(f"• {crew_name}")
        
        # Show validation status
        validation = orchestrator.validate_system()
        if validation['configuration_valid']:
            console.print("\n✓ System validation passed")
        else:
            console.print("\n⚠️  System validation warnings:")
            for warning in validation.get('warnings', []):
                console.print(f"  • {warning}")
        
        # Shutdown orchestrator
        orchestrator.shutdown()
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        logger.error(f"Orchestrator execution failed: {e}")
        raise typer.Exit(1)


def _show_phase1_implementation(task: Optional[str], crew: Optional[str], config_file: Optional[str]):
    """
    Show Phase 1 implementation status (kept for reference).
    
    Args:
        task: Specific task to run
        crew: Specific crew to execute
        config_file: Path to configuration file
    """
    console.print(Panel.fit(
        "[bold yellow]ADOS Phase 1 - Development Status[/bold yellow]",
        border_style="yellow"
    ))
    
    # Show current implementation status
    console.print("[bold]Current Implementation Status:[/bold]")
    console.print("✓ CLI Foundation (Phase 1, Task 1.3) - [green]COMPLETED[/green]")
    console.print("✓ Configuration System (Phase 1, Task 1.4) - [green]COMPLETED[/green]")
    console.print("✓ Basic Validation (Phase 1, Task 1.5) - [green]COMPLETED[/green]")
    console.print("✓ Core Orchestrator (Phase 2, Task 2.1) - [green]COMPLETED[/green]")
    console.print("• Task Decomposer (Phase 2, Task 2.2) - [yellow]PENDING[/yellow]")
    console.print("• Memory Coordination (Phase 2, Task 2.3) - [yellow]PENDING[/yellow]")
    console.print("• Logging Infrastructure (Phase 2, Task 2.4) - [yellow]PENDING[/yellow]")
    
    # Development timeline
    console.print(Panel(
        "🔄 [bold]Development Timeline:[/bold]\n"
        "• Phase 1: Core Setup (Tasks 1.1-1.5) - [green]COMPLETED[/green]\n"
        "• Phase 2: System Backbone - [yellow]IN PROGRESS[/yellow]\n"
        "• Phase 3: Core Crews Implementation - [dim]PLANNED[/dim]\n"
        "• Phase 4: Output Handling - [dim]PLANNED[/dim]\n"
        "• Phase 5: Memory & Knowledge Base - [dim]PLANNED[/dim]\n"
        "\n[dim]Core orchestration is now available![/dim]",
        title="Development Roadmap",
        border_style="blue"
    ))


if __name__ == "__main__":
    run_command()