"""
Trust Management for A-Team CLI.

This module handles temporary bypass of human-in-the-loop confirmations 
for trusted agents or specific operations.
"""

import time
from typing import Dict, Optional


class TrustManager:
    """
    Manages temporary trust "Flow State" for agents.
    """

    def __init__(self) -> None:
        # Maps agent_name to expiration timestamp (float)
        self._trusted_agents: Dict[str, float] = {}

    def trust_agent(self, agent_name: str, duration_seconds: int) -> None:
        """
        Grants temporary trust to an agent.
        
        Args:
            agent_name: The name of the agent (e.g., 'Coder').
            duration_seconds: How long the trust lasts.
        """
        self._trusted_agents[agent_name] = time.time() + duration_seconds

    def revoke_trust(self, agent_name: str) -> None:
        """Removes trust for an agent immediately."""
        if agent_name in self._trusted_agents:
            del self._trusted_agents[agent_name]

    def is_agent_trusted(self, agent_name: str) -> bool:
        """
        Checks if an agent is currently in a trusted 'Flow State'.
        """
        expiration = self._trusted_agents.get(agent_name)
        if not expiration:
            return False
            
        if time.time() >= expiration:
            # Clean up expired trust
            del self._trusted_agents[agent_name]
            return False
            
        return True

    def get_remaining_time(self, agent_name: str) -> int:
        """Returns remaining trust time in seconds."""
        expiration = self._trusted_agents.get(agent_name)
        if not expiration:
            return 0
        remaining = int(expiration - time.time())
        return max(0, remaining)
