#!/usr/bin/env python3
"""
Minimal test CLI to isolate the issue
"""

import typer
from rich.console import Console

app = typer.Typer(
    name="ados",
    help="ADOS - AI Dev Orchestration System",
    no_args_is_help=True,
    add_completion=False
)

console = Console()

@app.command()
def test_command():
    """Test command"""
    console.print("Test command executed")

@app.callback()
def main():
    """Main callback"""
    pass

if __name__ == "__main__":
    app()