"""
Interactive Chat Interface for A-Team CLI.

This module provides the REPL loop for interacting with agents in a room.
"""

import asyncio
import sys
from typing import Optional, List, Dict
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status
from rich.text import Text

from ateam.core import RoomManager, HistoryManager, AgentRouter, ConfigManager, ContextManager
from ateam.security import SecureAPIKeyManager, InputValidator


class ChatInterface:
    """
    Manages the interactive chat session in a room.
    """

    def __init__(self, room_name: str, console: Optional[Console] = None) -> None:
        self.room_name = room_name
        self.console = console or Console()
        self.validator = InputValidator()
        self.key_manager = SecureAPIKeyManager()
        
        # Core components
        self.room_manager = RoomManager()
        self.history_manager = self.room_manager.get_history(room_name)
        self.config_manager = ConfigManager()
        self.router = AgentRouter(self.config_manager)
        
        # State
        self.current_agent = self.config_manager.config.default_agent
        self.should_exit = False

    def _resolve_api_key(self, env_var: str) -> str:
        """Resolve API key using our secure manager."""
        # Try to get from keyring/env
        key = self.key_manager.get_key(env_var)
        if not key:
            self.console.print(f"[bold red]Error:[/bold red] API key for [yellow]{env_var}[/yellow] not found.")
            self.console.print("Please set it using: [cyan]ateam init[/cyan] (coming soon) or export it to your environment.")
            return ""
        return key

    async def run(self) -> None:
        """Main REPL loop."""
        self.console.print(f"\n[bold cyan]Entering Room:[/bold cyan] [bold white]{self.room_name}[/bold white]")
        self.console.print(f"[dim]Default Agent: {self.current_agent} | Type /help for commands[/dim]\n")

        # Load recent history
        history = self.history_manager.get_last_messages(limit=10)
        for msg in reversed(history):
            self._display_message(msg.role, msg.content, msg.agent_tag)

        while not self.should_exit:
            try:
                # Use asyncio.to_thread for blocking input
                user_input = await asyncio.to_thread(
                    Prompt.ask, 
                    Text(f" {self.room_name} ❯ ", style="bold green")
                )
                
                if not user_input.strip():
                    continue

                if user_input.startswith("/"):
                    await self._handle_command(user_input[1:])
                    continue

                # Validate input
                try:
                    self.validator.validate_message(user_input)
                except ValueError as e:
                    self.console.print(f"[bold red]Security Block:[/bold red] {e}")
                    continue

                await self._process_message(user_input)

            except EOFError:
                self.should_exit = True
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /exit to leave the room safely.[/yellow]")

    def _display_message(self, role: str, content: str, agent_tag: Optional[str] = None) -> None:
        """Render a message to the console."""
        if role == "user":
            self.console.print(f"\n[bold green]You[/bold green]")
            self.console.print(content)
        elif role == "assistant":
            name = agent_tag or "AI"
            self.console.print(f"\n[bold magenta]@{name}[/bold magenta]")
            self.console.print(Markdown(content))
        elif role == "system":
            self.console.print(f"\n[bold yellow]System[/bold yellow]")
            self.console.print(f"[italic]{content}[/italic]")

    async def _process_message(self, text: str) -> None:
        """Route message to agent and handle response."""
        # Detect agent
        agent_name, cleaned_text = self.router.select_agent(text)
        self.current_agent = agent_name
        
        # Save user message
        self.history_manager.add_message(role="user", content=text, agent_tag=None)
        
        try:
            agent_cfg = self.config_manager.get_agent(agent_name)
            api_key = self._resolve_api_key(agent_cfg.api_key_env)
            if not api_key:
                return

            provider = self.router.get_provider_for_agent(agent_name, api_key)
            
            # Prepare context
            # Get full history
            full_history = self.history_manager.get_history(limit=50) # Get more for context
            msgs_for_llm = []
            for m in reversed(full_history):
                # Simple mapping for now
                role = "assistant" if m.role == "assistant" else "user"
                msgs_for_llm.append({"role": role, "content": m.content})

            # Trim context
            ctx_mgr = ContextManager(max_tokens=agent_cfg.max_tokens)
            trimmed_msgs = ctx_mgr.get_trimmed_context(
                msgs_for_llm, 
                system_prompt=agent_cfg.system_prompt
            )

            # Display "Thinking..."
            provider_style = {
                "gemini": "cyan",
                "openai": "green",
                "anthropic": "yellow",
                "ollama": "blue"
            }.get(agent_cfg.provider.lower(), "magenta")
            
            self.console.print(f"\n[bold {provider_style}]@{agent_name}[/bold {provider_style}] [dim]({agent_cfg.provider}/{agent_cfg.model})[/dim]")
            
            full_response = ""
            with Live(Text("Thinking...", style="italic dim"), refresh_per_second=10) as live:
                try:
                    # Use streaming if supported (for better UX)
                    async for chunk in provider.stream(trimmed_msgs):
                        full_response += chunk
                        live.update(Markdown(full_response))
                except NotImplementedError:
                    # Fallback to non-streaming
                    response = await provider.complete(trimmed_msgs)
                    full_response = response.content
                    live.update(Markdown(full_response))

            # Store result
            self.history_manager.add_message(
                role="assistant", 
                content=full_response, 
                agent_tag=agent_name
            )
            
            # Show stats if enabled in config
            if self.config_manager.config.show_token_usage:
                usage = ctx_mgr.get_token_usage(trimmed_msgs + [{"role": "assistant", "content": full_response}])
                self.console.print(f"[dim]Tokens: {usage['total_tokens']} / {usage['max_tokens']} ({usage['usage_percent']}%)[/dim]")

            # Update room metadata
            metadata = self.room_manager._load_metadata(self.room_name)
            metadata.message_count += 2 # User + AI
            self.room_manager._save_metadata(self.room_name, metadata)

        except Exception as e:
            self.console.print(f"\n[bold red]Error:[/bold red] {e}")

    async def _handle_command(self, cmd_line: str) -> None:
        """Handle internal /commands."""
        parts = cmd_line.split()
        cmd = parts[0].lower()
        
        if cmd in ("exit", "quit", "q", "leave"):
            self.should_exit = True
            self.console.print("[dim]Leaving room...[/dim]")
        
        elif cmd == "help":
            help_text = """
[bold cyan]Available Commands:[/bold cyan]
- [bold]/help[/bold]: Show this help message
- [bold]/exit[/bold], [bold]/leave[/bold]: Leave the room and exit the session
- [bold]/switch <room>[/bold]: Switch to a different room
- [bold]/status[/bold]: Show current room and agent information
- [bold]/history[/bold]: Show conversation history (last 50 messages)
- [bold]/clear[/bold]: Clear history in this room (irreversible!)
- [bold]/agents[/bold]: List available agents
- [bold]/agent <name>[/bold]: Switch default agent for this session
            """
            self.console.print(Panel(help_text, title="Help"))

        elif cmd == "status":
            metadata = self.room_manager._load_metadata(self.room_name)
            status_text = f"""
[bold cyan]Room:[/bold cyan] {self.room_name}
[bold cyan]Description:[/bold cyan] {metadata.description or "None"}
[bold cyan]Messages:[/bold cyan] {metadata.message_count}
[bold cyan]Default Agent:[/bold cyan] [magenta]@{self.current_agent}[/magenta]
[bold cyan]Config Path:[/bold cyan] {self.config_manager.config_path}
            """
            self.console.print(Panel(status_text, title="📊 Room Status"))

        elif cmd == "switch":
            if len(parts) > 1:
                new_room = parts[1]
                try:
                    self.validator.validate_room_name(new_room)
                    # Join the new room
                    self.room_name = new_room
                    self.history_manager = self.room_manager.get_history(new_room)
                    self.room_manager.join_room(new_room)
                    
                    self.console.print(f"\n[bold green]✓[/bold green] Switched to room: [bold cyan]{new_room}[/bold cyan]\n")
                    
                    # Display history of new room
                    history = self.history_manager.get_last_messages(limit=5)
                    if history:
                        self.console.print("[dim]Recent context:[/dim]")
                        for msg in reversed(history):
                            self._display_message(msg.role, msg.content, msg.agent_tag)
                            
                except ValueError as e:
                    self.console.print(f"[red]✗ Invalid room name:[/red] {e}")
            else:
                self.console.print("[yellow]Usage: /switch <room_name>[/yellow]")
            
        elif cmd == "history":
            history = self.history_manager.get_history(limit=50)
            self.console.print("\n[bold cyan]--- History ---[/bold cyan]")
            for msg in reversed(history):
                self._display_message(msg.role, msg.content, msg.agent_tag)
            self.console.print("[bold cyan]--- End ---[/bold cyan]\n")
            
        elif cmd == "clear":
            if Prompt.ask("[red]Are you sure you want to clear history?[/red]", choices=["y", "n"]) == "y":
                self.history_manager.clear_history()
                # Reset room counter
                metadata = self.room_manager._load_metadata(self.room_name)
                metadata.message_count = 0
                self.room_manager._save_metadata(self.room_name, metadata)
                self.console.print("[green]History cleared.[/green]")
                
        elif cmd == "agents":
            agents = self.config_manager.config.agents.keys()
            self.console.print(f"Available Agents: [cyan]{', '.join(agents)}[/cyan]")
            self.console.print(f"Current default: [bold magenta]@{self.current_agent}[/bold magenta]")
            
        elif cmd == "agent":
            if len(parts) > 1:
                new_agent = parts[1]
                if new_agent in self.config_manager.config.agents:
                    self.current_agent = new_agent
                    self.console.print(f"Default agent switched to [bold magenta]@{new_agent}[/bold magenta]")
                else:
                    self.console.print(f"[red]Agent '{new_agent}' not found.[/red]")
            else:
                self.console.print(f"Current default: [bold magenta]@{self.current_agent}[/bold magenta]")
        
        else:
            self.console.print(f"[yellow]Unknown command: /{cmd}[/yellow]")
