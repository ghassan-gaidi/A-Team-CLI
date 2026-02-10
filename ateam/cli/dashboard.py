"""
Interactive Mission Control Dashboard for A-Team CLI.
"""

import time
import asyncio
import os
import msvcrt # Windows specific
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.columns import Columns

from ateam.core import RoomManager, RoomMetadata
from ateam.core.history import Message


class Dashboard:
    """
    Real-time interactive dashboard for monitoring rooms and agents.
    """

    def __init__(self):
        self.console = Console()
        self.room_manager = RoomManager()
        self.start_time = time.time()
        self.selected_index = 0
        self.rooms: List[RoomMetadata] = []
        self.running = True
        self.activity_log: List[str] = ["Dashboard initialized."]

    def _get_room_status(self, last_active_str: str) -> Text:
        last_active = datetime.fromisoformat(last_active_str)
        delta = datetime.utcnow() - last_active
        
        if delta.total_seconds() < 600: # 10 minutes
            return Text("● ACTIVE", style="bold green")
        elif delta.total_seconds() < 3600: # 1 hour
            return Text("● IDLE", style="bold yellow")
        else:
            return Text("● ASLEEP", style="dim white")

    def _get_token_bar(self, tokens: int) -> Progress:
        progress = Progress(
            BarColumn(bar_width=15, complete_style="cyan", finished_style="green"),
            TextColumn("[bold blue]{task.fields[val]}"),
            auto_refresh=False
        )
        # Using 100k as a sensible "full" bar for short sessions, adjust as needed
        max_val = 100000
        usage = min(tokens, max_val)
        progress.add_task("Usage", total=max_val, completed=usage, val=f"{tokens:,}")
        return progress

    def _generate_layout(self) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="upper", size=3),
            Layout(name="main", ratio=1),
            Layout(name="lower", size=10)
        )
        
        # Header
        layout["upper"].update(Panel(
            Text.from_markup(f"[bold cyan]A-TEAM MISSION CONTROL[/bold cyan] | [dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"),
            border_style="cyan"
        ))
        
        # Main content - Table
        self.rooms = self.room_manager.list_rooms()
        if not self.rooms:
            layout["main"].update(Panel(Text("No active missions found.", justify="center"), title="📡 Rooms", border_style="blue"))
        else:
            table = Table(show_header=True, header_style="bold magenta", expand=True, box=None)
            table.add_column("S", width=2)
            table.add_column("Status", width=12)
            table.add_column("Room Name", style="cyan", no_wrap=True)
            table.add_column("Agent", style="green")
            table.add_column("Msgs", justify="right")
            table.add_column("Token Usage", width=25)
            table.add_column("Last Activity", style="dim")

            for i, room in enumerate(self.rooms):
                selector = ">" if i == self.selected_index else " "
                row_style = "bold white on blue" if i == self.selected_index else ""
                
                last_agent = "None"
                tokens = 0
                try:
                    history = self.room_manager.get_history(room.name)
                    tokens = history.get_token_usage()
                    last_msgs = history.get_last_messages(1)
                    if last_msgs:
                        last_agent = f"@{last_msgs[0].agent_tag}" if last_msgs[0].agent_tag else "User"
                except Exception:
                    pass
                
                table.add_row(
                    selector,
                    self._get_room_status(room.last_active),
                    room.name,
                    last_agent,
                    str(room.message_count),
                    self._get_token_bar(tokens).get_renderable(),
                    room.last_active[11:19],
                    style=row_style
                )

            layout["main"].update(Panel(table, title="📡 Active Missions (Use ↑/↓, Enter to select)", border_style="blue"))
        
        # Lower Section - Activity Log
        log_text = Text("\n".join(self.activity_log[-8:]))
        layout["lower"].update(Panel(log_text, title="📟 Activity Feed", border_style="dim"))
        
        return layout

    def _handle_input(self):
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0': # Special key
                key = msvcrt.getch()
                if key == b'H': # Up
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == b'P': # Down
                    self.selected_index = min(len(self.rooms) - 1, self.selected_index + 1)
            elif key.lower() == b'q':
                self.running = False
            elif key == b'\r': # Enter
                if self.rooms:
                    room = self.rooms[self.selected_index]
                    self.activity_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Pinging room: {room.name}")

    async def run(self):
        """Runs the live dashboard."""
        self.console.clear()
        with Live(self._generate_layout(), console=self.console, refresh_per_second=4, screen=True) as live:
            try:
                while self.running:
                    self._handle_input()
                    live.update(self._generate_layout())
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                # Basic error logging into the feed if we can
                self.activity_log.append(f"ERROR: {str(e)}")
                await asyncio.sleep(2)
