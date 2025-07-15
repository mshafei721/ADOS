"""
ADOS CLI Main Application

This module provides the main entry point for the ADOS CLI.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from typer import Context, CallbackParam
from rich.console import Console

from .utils.logger import setup_logging, get_logger
from .utils.config import get_config_manager
from .commands.init import init_command
from .commands.run import run_command
from .commands.status import status_command
from .commands.version import version_command

# Create Typer app
app = typer.Typer(
    name="ados",
    help="ADOS - AI Dev Orchestration System",
    no_args_is_help=True,
    add_completion=False
)

# Rich console for enhanced output
console = Console()

# Global state
_logger: Optional[object] = None


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    log_file: Optional[str] = typer.Option(None, "--log-file", help="Path to log file")
):
    """
    ADOS - AI Dev Orchestration System
    
    A powerful CLI tool for orchestrating AI development crews and automating 
    software development workflows.
    """
    global _logger
    
    # Setup logging
    _logger = setup_logging(
        level="DEBUG" if verbose else "INFO",
        log_file=log_file,
        verbose=verbose
    )
    
    # Log startup
    logger = get_logger(__name__)
    logger.debug("ADOS CLI starting up")


# Register commands
app.command(name="init", help="Initialize a new ADOS project workspace")(init_command)
app.command(name="run", help="Execute ADOS orchestration")(run_command)
app.command(name="status", help="Show current system status")(status_command)
app.command(name="version", help="Show version information")(version_command)

@app.command(name="help", help="Show help information")
def help_command():
    """Show help information for the ADOS CLI"""
    console.print("""
[bold]ADOS - AI Dev Orchestration System[/bold]

[green]Usage:[/green] ados [OPTIONS] COMMAND [ARGS]...

[green]Options:[/green]
  -v, --verbose         Enable verbose logging
  --log-file TEXT       Path to log file
  --help               Show this message and exit.

[green]Commands:[/green]
  init      Initialize a new ADOS project workspace
  run       Execute ADOS orchestration
  status    Show current system status
  version   Show version information
  help      Show help information
""")


def cli_main():
    """
    Main entry point for the CLI application.
    """
    try:
        # Check for -h flag and convert to --help
        if len(sys.argv) > 1 and sys.argv[1] == '-h':
            sys.argv[1] = '--help'
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if _logger:
            logger = get_logger(__name__)
            logger.exception("Unhandled exception in CLI")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()