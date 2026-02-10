"""
Shadow Critic: Autonomous Background Auditing for A-Team CLI.
"""

import asyncio
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ateam.core.config import ConfigManager, AgentConfig
from ateam.providers import ProviderFactory, ProviderConfig
from ateam.security import SecureAPIKeyManager


class ShadowCritic:
    """
    Background auditor that observes Coder actions and reports issues.
    """

    def __init__(self, config_manager: ConfigManager, console: Console):
        self.config_manager = config_manager
        self.console = console
        self.key_manager = SecureAPIKeyManager()
        self.critic_name = "Critic" # Convention

    async def audit_action(self, agent_name: str, action: str, result: str, context: str):
        """
        Performs a silent background audit of an agent's action.
        """
        # Don't audit the critic themselves to avoid infinite loops
        if agent_name == self.critic_name:
            return

        # Only audit "mutative" agents (typically Coder)
        if "Coder" not in agent_name and agent_name != self.config_manager.config.default_agent:
            # We skip if it's likely just a researcher, unless it's the default agent
            pass

        try:
            critic_cfg = self.config_manager.get_agent(self.critic_name)
        except ValueError:
            # No Critic defined, skip shadow auditing
            return

        # Get API Key
        api_key = self.key_manager.get_key(critic_cfg.provider)
        if not api_key:
            return

        # Prepare Audit Prompt
        audit_prompt = f"""
[SHADOW AUDIT REQUEST]
Agent '@{agent_name}' just performed an action.
ACTION: {action}
RESULT: {result[:2000]}... (truncated if too long)

CONTEXT OF THE MISSION:
{context[:2000]}

Your task:
1. Review this action for security risks, bugs, or major architectural violations.
2. If the action is SAFE and correct, respond with exactly: "STATUS: CLEAR"
3. If you find a MAJOR or CRITICAL issue, respond with:
   "STATUS: ALERT"
   "SEVERITY: [Critical/Major]"
   "ISSUE: [Brief description]"
   "FIX: [Brief recommendation]"

Be concise. Do not chat.
"""

        # Run Audit in background
        provider_config = ProviderConfig(
            model_name=critic_cfg.model,
            temperature=0.1, # very deterministic
            max_tokens=500
        )
        
        try:
            provider = ProviderFactory.create(critic_cfg.provider, provider_config, api_key)
            response = await provider.complete([{"role": "user", "content": audit_prompt}])
            
            if "STATUS: ALERT" in response.content:
                self._display_alert(agent_name, response.content)
        except Exception as e:
            # Silent failure for background task
            pass

    def _display_alert(self, target_agent: str, alert_text: str):
        """Displays a high-priority interrupt panel."""
        lines = alert_text.splitlines()
        severity = "MAJOR"
        issue = "Unknown issue"
        fix = "Check logs"

        for line in lines:
            if "SEVERITY:" in line: severity = line.split(":", 1)[1].strip()
            if "ISSUE:" in line: issue = line.split(":", 1)[1].strip()
            if "FIX:" in line: fix = line.split(":", 1)[1].strip()

        panel = Panel(
            Text.from_markup(f"[bold red]⚠️  SHADOW CRITIC ALERT[/bold red]\n\n"
                            f"[bold]Target Agent:[/bold] @{target_agent}\n"
                            f"[bold]Severity:[/bold] [red]{severity}[/red]\n"
                            f"[bold]Issue:[/bold] {issue}\n"
                            f"[bold]Refactor Suggestion:[/bold] [green]{fix}[/green]"),
            title="🕵️ Recursive Audit Result",
            border_style="red",
            expand=False
        )
        self.console.print("\n")
        self.console.print(panel)
        self.console.print("\n")
