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


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
