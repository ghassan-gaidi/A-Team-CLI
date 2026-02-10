import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from rich.console import Console
from ateam.security.critic import ShadowCritic

@pytest.mark.asyncio
async def test_shadow_critic_clear():
    # Setup
    mock_config_manager = MagicMock()
    class DummyConfig:
        def __init__(self):
            self.default_agent = "Architect"
            self.agents = {"Critic": MagicMock()}
    mock_config_manager.config = DummyConfig()
    
    critic_agent_cfg = MagicMock()
    critic_agent_cfg.provider = "openai"
    critic_agent_cfg.model = "gpt-4"
    critic_agent_cfg.system_prompt = "You are a critic."
    mock_config_manager.get_agent.return_value = critic_agent_cfg
    
    mock_console = MagicMock(spec=Console)
    
    with patch("ateam.security.critic.SecureAPIKeyManager") as mock_key_mgr_class, \
         patch("ateam.security.critic.ProviderFactory") as mock_factory_class:
        
        mock_key_mgr = mock_key_mgr_class.return_value
        mock_key_mgr.get_key.return_value = "fake-key"
        
        mock_provider = AsyncMock()
        mock_provider.complete.return_value = MagicMock(content="STATUS: CLEAR")
        mock_factory_class.create.return_value = mock_provider
        
        critic = ShadowCritic(mock_config_manager, mock_console)
        await critic.audit_action("Coder", "write_file", "success", "mission context")
        
        # Should NOT print an alert if clear
        # (It prints newlines even if clear? Let's check critic.py)
        # Actually in critic.py it only prints if "STATUS: ALERT" in response
        assert mock_console.print.call_count == 0

@pytest.mark.asyncio
async def test_shadow_critic_alert():
    # Setup
    mock_config_manager = MagicMock()
    class DummyConfig:
        def __init__(self):
            self.default_agent = "Architect"
            self.agents = {"Critic": MagicMock()}
    mock_config_manager.config = DummyConfig()

    critic_agent_cfg = MagicMock()
    critic_agent_cfg.provider = "openai"
    critic_agent_cfg.model = "gpt-4"
    critic_agent_cfg.system_prompt = "You are a critic."
    mock_config_manager.get_agent.return_value = critic_agent_cfg
    
    mock_console = MagicMock(spec=Console)
    
    with patch("ateam.security.critic.SecureAPIKeyManager") as mock_key_mgr_class, \
         patch("ateam.security.critic.ProviderFactory") as mock_factory_class:
        
        mock_key_mgr = mock_key_mgr_class.return_value
        mock_key_mgr.get_key.return_value = "fake-key"
        
        mock_provider = AsyncMock()
        mock_provider.complete.return_value = MagicMock(content="STATUS: ALERT\nSEVERITY: Major\nISSUE: Bug")
        mock_factory_class.create.return_value = mock_provider
        
        critic = ShadowCritic(mock_config_manager, mock_console)
        await critic.audit_action("Coder", "shell_exec", "rm -rf /", "context")
        
        # Should print alert (panel + newlines)
        assert mock_console.print.call_count >= 1
