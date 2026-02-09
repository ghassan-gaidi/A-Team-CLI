"""
Tests for AgentRouter and ConfigManager.

Tests cover:
- Config loading from YAML
- Agent selection from text tags
- Provider instantiation for specific agents
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from ateam.core.config import ConfigManager
from ateam.core.router import AgentRouter


class TestRouter:
    """Test suite for AgentRouter and Config."""

    @pytest.fixture
    def mock_config(self, tmp_path):
        config_content = """
version: "1.0"
default_agent: "Architect"
agents:
  Architect:
    provider: gemini
    model: gemini-pro
    api_key_env: GOOGLE_API_KEY
    system_prompt: "You are an architect"
    temperature: 0.1
  Coder:
    provider: openai
    model: gpt-4
    api_key_env: OPENAI_API_KEY
    system_prompt: "You are a coder"
    temperature: 0.5
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        return config_file

    def test_config_loading(self, mock_config):
        cm = ConfigManager(mock_config)
        assert cm.config.default_agent == "Architect"
        assert len(cm.config.agents) == 2
        assert cm.get_agent("Coder").provider == "openai"

    def test_agent_selection_default(self, mock_config):
        cm = ConfigManager(mock_config)
        router = AgentRouter(cm)
        
        agent, text = router.select_agent("Hello world")
        assert agent == "Architect"
        assert text == "Hello world"

    def test_agent_selection_tag(self, mock_config):
        cm = ConfigManager(mock_config)
        router = AgentRouter(cm)
        
        agent, text = router.select_agent("@Coder Fix this bug")
        assert agent == "Coder"
        assert text == "Fix this bug"

    def test_multi_tag_selection(self, mock_config):
        cm = ConfigManager(mock_config)
        router = AgentRouter(cm)
        
        # First tag wins or last tag? Currently first one is picked by extract but 
        # let's verify my implementation. 
        # In my code: mentions = self.parse_mentions(text); selected = mentions[0]
        agent, text = router.select_agent("@Architect @Coder What is the plan?")
        assert agent == "Architect"
        assert "@Coder" in text # Other tags remain in text

    @pytest.mark.asyncio
    async def test_routing_to_provider(self, mock_config):
        cm = ConfigManager(mock_config)
        router = AgentRouter(cm)
        
        mock_provider = MagicMock()
        mock_provider.complete = MagicMock() # Will be wrapped in async
        
        with patch("ateam.providers.ProviderFactory.create") as mock_create:
            mock_create.return_value = MagicMock()
            mock_create.return_value.complete = MagicMock(return_value="mocked-response")
            
            # Mock the resolver
            resolver = lambda env: "fake-key"
            
            # We don't actually need to await for simple mock if we are careful,
            # but let's make it a proper async mock.
            from unittest.mock import AsyncMock
            mock_create.return_value.complete = AsyncMock(return_value="mocked-response")
            
            agent, response = await router.route_and_complete(
                "@Coder write tests", 
                [], 
                resolver
            )
            
            assert agent == "Coder"
            assert response == "mocked-response"
            
            # Verify correct model was used
            mock_create.assert_called_once()
            args, kwargs = mock_create.call_args
            # provider_name is first arg in factory.create
            assert args[0] == "openai"
            assert args[1].model_name == "gpt-4"
            assert args[2] == "fake-key"
