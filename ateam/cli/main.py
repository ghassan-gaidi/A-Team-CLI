"""
A-Team CLI - Main entry point.

This module provides the command-line interface for A-Team using Typer.
"""

import typer
from rich.console import Console

from ateam import __version__

app = typer.Typer(
    name="ateam",
    help="Production-grade, security-hardened multi-agent AI orchestration tool",
    add_completion=False,
)
console = Console()


@app.command()
def version() -> None:
    """Show A-Team version information."""
    console.print(f"[bold cyan]A-Team CLI[/bold cyan] version [green]{__version__}[/green]")
    console.print("Multi-agent AI orchestration for your terminal 🚀")


@app.command()
def init() -> None:
    """Initialize A-Team configuration (interactive setup)."""
    console.print("[yellow]⚙️  A-Team initialization coming in Task 1.2![/yellow]")
    console.print("This will set up your API keys and configuration.")


@app.command()
def join(room_name: str) -> None:
    """
    Create or join a conversation room.
    
    Args:
        room_name: Name of the room to join
    """
    console.print(f"[yellow]🚪 Joining room '{room_name}' - coming in Task 1.3![/yellow]")


@app.command()
def rooms() -> None:
    """List all available rooms."""
    console.print("[yellow]📋 Room listing coming in Task 1.3![/yellow]")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
