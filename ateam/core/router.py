"""
Multi-Agent Routing for A-Team CLI.

This module handles parsing @mentions in user messages and routing 
requests to the appropriate AI agent/provider.
"""

import re
from typing import Dict, List, Optional, Tuple
from ateam.core.config import ConfigManager, AgentConfig
from ateam.providers import ProviderFactory, BaseProvider, ProviderConfig, CompletionResponse


class AgentRouter:
    """
    Routes user messages to the correct AI agent.
    """

    # Matches @AgentName at the start or middle of a message
    # Allows alphanumeric characters and underscores
    AGENT_TAG_PATTERN = re.compile(r"@([a-zA-Z0-9_]+)")

    def __init__(self, config_manager: ConfigManager) -> None:
        """
        Initialize the router.

        Args:
            config_manager: The loaded configuration manager.
        """
        self.config = config_manager
        self._provider_cache: Dict[str, BaseProvider] = {}

    def parse_mentions(self, text: str) -> List[str]:
        """
        Extract @agent_tags from message text.

        Returns:
            List of agent names found (without the @).
        """
        return self.AGENT_TAG_PATTERN.findall(text)

    def select_agent(self, text: str) -> Tuple[str, str]:
        """
        Determine which agent should respond and return the cleaned text.
        
        If multiple tags are present, the last one takes precedence.
        If no tags are present, the default agent is used.

        Returns:
            Tuple of (agent_name, cleaned_text)
        """
        mentions = self.parse_mentions(text)
        
        if not mentions:
            return self.config.config.default_agent, text

        # Use the first mention for now (or last, but first is more common for command style)
        selected = mentions[0]
        
        # Clean the text if the tag is at the start
        cleaned = text.replace(f"@{selected}", "").strip()
        
        # If multiple mentions, we might want to keep the others in text? 
        # For now, just return the first one as the active agent.
        return selected, cleaned

    def get_provider_for_agent(self, agent_name: str, api_key: str) -> BaseProvider:
        """
        Instantiate or get a cached provider for a specific agent.
        """
        # We cache by agent_name to preserve the specific ProviderConfig
        if agent_name in self._provider_cache:
            return self._provider_cache[agent_name]

        agent_cfg = self.config.get_agent(agent_name)
        
        provider_config = ProviderConfig(
            model_name=agent_cfg.model,
            temperature=agent_cfg.temperature,
            max_tokens=agent_cfg.max_tokens,
            extra_params={"base_url": agent_cfg.base_url} if agent_cfg.base_url else {}
        )

        provider = ProviderFactory.create(
            agent_cfg.provider,
            provider_config,
            api_key
        )
        
        self._provider_cache[agent_name] = provider
        return provider

    async def route_and_complete(
        self, 
        text: str, 
        history: List[Dict[str, str]], 
        api_key_resolver, # Callable that takes agent_cfg.api_key_env and returns the key
    ) -> Tuple[str, CompletionResponse]:
        """
        High-level method to:
        1. Select agent from text
        2. Resolve API key
        3. Get provider
        4. Execute completion
        
        Returns:
            Tuple of (agent_name, response)
        """
        agent_name, cleaned_text = self.select_agent(text)
        agent_cfg = self.config.get_agent(agent_name)
        
        api_key = api_key_resolver(agent_cfg.api_key_env)
        if not api_key:
            raise ValueError(f"API Key for {agent_cfg.api_key_env} not found.")

        provider = self.get_provider_for_agent(agent_name, api_key)
        
        # Prepare messages
        messages = history + [{"role": "user", "content": cleaned_text}]
        
        # We pass the agent's system prompt to the provider
        response = await provider.complete(
            messages, 
            system_prompt=agent_cfg.system_prompt
        )
        
        return agent_name, response
