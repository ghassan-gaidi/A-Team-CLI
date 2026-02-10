"""
A-Team CLI - Main entry point.

This module provides the command-line interface for A-Team using Typer.
"""

import typer
from pathlib import Path
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
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from ateam.security import SecureAPIKeyManager
    from ateam.core import ConfigManager
    import yaml
    
    console.print(Panel(
        "[bold cyan]Welcome to the A-Team Initialization Wizard![/bold cyan]\n"
        "This will set up your configuration file and help you securely store your API keys.",
        title="🚀 A-Team Setup"
    ))
    
    config_dir = Path.home() / ".config" / "ateam"
    config_path = config_dir / "config.yaml"
    
    if config_path.exists():
        if not Confirm.ask(f"[yellow]Configuration already exists at {config_path}. Overwrite?[/yellow]"):
            console.print("[yellow]Aborted.[/yellow]")
            return

    # Create directory
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Basic Config Template
    config_data = {
        "version": "1.0",
        "default_agent": "Architect",
        "context_window_size": 30,
        "auto_prune": True,
        "show_token_usage": True,
        "agents": {
            "Architect": {
                "provider": "gemini",
                "model": "gemini-2.5-flash",
                "api_key_env": "GOOGLE_API_KEY",
                "system_prompt": "You are a senior software architect. Focus on system design and high-level decisions.",
                "temperature": 0.7
            },
            "Coder": {
                "provider": "openai",
                "model": "gpt-4o",
                "api_key_env": "OPENAI_API_KEY",
                "system_prompt": "You are an expert engineer. Focus on writing clean, efficient, and well-tested code.",
                "temperature": 0.3
            }
        }
    }
    
    with open(config_path, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False)
    
    console.print(f"[green]✓[/green] Created configuration at [bold]{config_path}[/bold]")
    
    # Key Storage
    key_manager = SecureAPIKeyManager()
    
    if Confirm.ask("\nWould you like to store your API keys in the system keyring now?"):
        for agent_name, cfg in config_data["agents"].items():
            env_var = cfg["api_key_env"]
            if Confirm.ask(f"Add key for [bold cyan]{agent_name}[/bold cyan] ({env_var})?"):
                key = Prompt.ask(f"Enter your [bold yellow]{env_var}[/bold yellow]", password=True)
                if key:
                    key_manager.store_key(cfg["provider"], key)
                    console.print(f"[green]✓[/green] Key stored for {cfg['provider']} ({env_var})")
    
    console.print("\n[bold green]Success![/bold green] A-Team is ready to roll.")
    console.print("Try joining a room: [cyan]ateam join alpha[/cyan]")


@app.command()
def join(
    room_name: str = typer.Argument(..., help="Name of the room to join"),
    description: str = typer.Option(None, "--description", "-d", help="Room description (for new rooms)"),
) -> None:
    """
    Create or join a conversation room.
    
    If the room doesn't exist, it will be created automatically.
    
    Args:
        room_name: Name of the room to join
        description: Optional description for new rooms
    """
    from ateam.core import RoomManager
    from rich.panel import Panel
    
    try:
        manager = RoomManager()
        
        # Check if room exists
        is_new = not manager.room_exists(room_name)
        
        # Join (or create) the room
        metadata = manager.join_room(room_name)
        
        # Update description if provided
        if description and is_new:
            metadata = manager.update_room_metadata(room_name, description=description)
        
        # Display success message
        if is_new:
            console.print(Panel(
                f"[green]✓[/green] Created and joined room: [bold cyan]{room_name}[/bold cyan]\n"
                f"Messages: {metadata.message_count}\n"
                f"Created: {metadata.created_at[:19]}",
                title="🚪 New Room",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[green]✓[/green] Joined room: [bold cyan]{room_name}[/bold cyan]\n"
                f"Messages: {metadata.message_count}\n"
                f"Last active: {metadata.last_active[:19]}",
                title="🚪 Joined Room",
                border_style="cyan"
            ))
        
        # Launch Chat Loop
        from ateam.cli.chat import ChatInterface
        import asyncio
        
        chat = ChatInterface(room_name, console=console)
        asyncio.run(chat.run())
            
    except ValueError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        # Avoid stack trace on Ctrl+C during room entry
        console.print("\n[yellow]Exit.[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error:[/red] {e}")
        import traceback
        # console.print(traceback.format_exc()) # Debug
        raise typer.Exit(1)


@app.command()
def rooms() -> None:
    """List all available rooms."""
    from ateam.core import RoomManager
    from rich.table import Table
    
    try:
        manager = RoomManager()
        room_list = manager.list_rooms()
        
        if not room_list:
            console.print("[yellow]No rooms found.[/yellow]")
            console.print("Create a room with: [cyan]ateam join <room-name>[/cyan]")
            return
        
        # Create table
        table = Table(title="📋 Available Rooms", show_header=True, header_style="bold cyan")
        table.add_column("Room Name", style="cyan", no_wrap=True)
        table.add_column("Messages", justify="right", style="green")
        table.add_column("Last Active", style="yellow")
        table.add_column("Description", style="dim")
        
        # Add rows
        for room in room_list:
            # Format last active timestamp
            last_active = room.last_active[:19].replace("T", " ")
            
            table.add_row(
                room.name,
                str(room.message_count),
                last_active,
                room.description or ""
            )
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(room_list)} room(s)[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show current session status and last active room."""
    from ateam.core import RoomManager, ConfigManager
    from rich.panel import Panel
    
    try:
        manager = RoomManager()
        rooms = manager.list_rooms()
        
        if not rooms:
            console.print("[yellow]No active session or rooms found.[/yellow]")
            return

        # Find last active room based on metadata
        last_room = max(rooms, key=lambda r: r.last_active)
        config = ConfigManager()
        
        status_text = f"""
[bold cyan]Last Active Room:[/bold cyan] {last_room.name}
[bold cyan]Messages in Room:[/bold cyan] {last_room.message_count}
[bold cyan]Last Activity:[/bold cyan] {last_room.last_active[:19].replace("T", " ")}
[bold cyan]Default Agent:[/bold cyan] [magenta]@{config.config.default_agent}[/magenta]
[bold cyan]Configuration:[/bold cyan] {config.config_path}
        """
        console.print(Panel(status_text, title="📊 A-Team Status", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def web(port: int = typer.Option(8080, "--port", "-p", help="Port to run the web server on")) -> None:
    """Launch the A-Team Reflection web dashboard."""
    from ateam.web.server import start_server
    import webbrowser
    
    # Try to open browser automatically
    webbrowser.open(f"http://localhost:{port}")
    
    try:
        start_server(port=port)
    except Exception as e:
        console.print(f"[red]✗ Error starting web server:[/red] {e}")


@app.command()
def dash() -> None:
    """Launch the real-time Mission Control dashboard."""
    from ateam.cli.dashboard import Dashboard
    import asyncio
    
    dashboard = Dashboard()
    try:
        asyncio.run(dashboard.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard closed.[/yellow]")


@app.command()
def spawn(
    template: str = typer.Argument(..., help="Template name (python-web, cli-app, security-hardened)"),
    name: str = typer.Argument(..., help="Project directory name"),
) -> None:
    """Spawn a new project from a team-approved template."""
    from rich.status import Status
    import os
    
    target = Path(os.getcwd()) / name
    if target.exists():
        console.print(f"[red]✗ Error:[/red] Directory [bold]{name}[/bold] already exists.")
        raise typer.Exit(1)
        
    console.print(f"\n[bold cyan]🚀 Spawning Project:[/bold cyan] [white]{name}[/white] ([dim]{template}[/dim])")
    
    try:
        with console.status(f"[bold yellow]Initializing from {template} template...[/bold yellow]"):
            target.mkdir(parents=True)
            
            if template == "cli-app":
                (target / "app.py").write_text(
                    'import typer\nfrom rich.console import Console\n\napp = typer.Typer()\nconsole = Console()\n\n'
                    '@app.command()\ndef hello(name: str = "World"):\n    console.print(f"[bold green]Hello {name}![/bold green] 🚀")\n\n'
                    'if __name__ == "__main__":\n    app()', encoding="utf-8"
                )
                (target / "pyproject.toml").write_text(
                    f'[project]\nname = "{name}"\nversion = "0.1.0"\n'
                    'dependencies = ["typer", "rich"]\n\n'
                    '[project.scripts]\n'
                    f'{name} = "app:app"', encoding="utf-8"
                )
                (target / "README.md").write_text(f"# {name}\n\nSpawned by A-Team CLI.", encoding="utf-8")
                
            elif template == "python-web":
                (target / "main.py").write_text(
                    'from fastapi import FastAPI\n\napp = FastAPI()\n\n'
                    '@app.get("/")\ndef read_root():\n    return {"Hello": "World"}\n', encoding="utf-8"
                )
                (target / "requirements.txt").write_text("fastapi\nuvicorn\n", encoding="utf-8")
                
            else:
                console.print(f"[yellow]⚠ Template '{template}' is not fully defined in MVP. Creating empty project.[/yellow]")
                (target / ".keep").touch()

        console.print(f"[bold green]✓ Success![/bold green] Project created at [bold]{target.relative_to(os.getcwd())}[/bold]")
        console.print(f"To get started: [cyan]cd {name} && explorer .[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]✗ Error spawning project:[/bold red] {e}")
        raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
