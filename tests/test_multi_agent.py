
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from ateam.cli.chat import ChatInterface
from ateam.core.config import ConfigManager

@pytest.mark.asyncio
async def test_multi_agent_routing():
    # Mock dependencies
    mock_console = MagicMock()
    
    # Initialize ChatInterface with mocks
    chat = ChatInterface("test-room", console=mock_console)
    
    # Mock the internal methods to avoid actual API calls
    chat._run_single_agent_turn = AsyncMock()
    chat.history_manager.add_message = MagicMock()
    
    # Test input with multiple agents
    user_input = "@Architect @Coder Build a hello world script"
    
    # Run the process
    await chat._process_message(user_input)
    
    # Verify sequence
    assert chat._run_single_agent_turn.call_count == 2
    
    # Verify call order and arguments
    calls = chat._run_single_agent_turn.call_args_list
    assert calls[0][0][0] == "Architect"
    assert calls[1][0][0] == "Coder"
    
    # Verify user message was added ONLY ONCE
    chat.history_manager.add_message.assert_called_once()
    args = chat.history_manager.add_message.call_args[1]
    assert args['role'] == 'user'
    assert args['content'] == user_input

@pytest.mark.asyncio
async def test_single_agent_routing():
    # Mock dependencies
    mock_console = MagicMock()
    chat = ChatInterface("test-room", console=mock_console)
    chat._run_single_agent_turn = AsyncMock()
    chat.history_manager.add_message = MagicMock()
    
    # Test input with single agent
    # Note: Using Coder as it's guaranteed to be in default config
    user_input = "@Coder Write some code"
    
    await chat._process_message(user_input)
    
    # Verify single call
    chat._run_single_agent_turn.assert_called_once_with("Coder", user_input)

@pytest.mark.asyncio
async def test_default_agent_routing():
    # Mock dependencies
    mock_console = MagicMock()
    chat = ChatInterface("test-room", console=mock_console)
    chat._run_single_agent_turn = AsyncMock()
    chat.history_manager.add_message = MagicMock()
    
    # Test input with NO agent tag
    user_input = "Hello world"
    default_agent = chat.config_manager.config.default_agent
    
    await chat._process_message(user_input)
    
    # Verify default agent called
    chat._run_single_agent_turn.assert_called_once_with(default_agent, user_input)
