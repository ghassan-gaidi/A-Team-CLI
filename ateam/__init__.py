"""
A-Team CLI - Production-grade, security-hardened multi-agent AI orchestration tool.

A-Team enables you to orchestrate multiple AI agents (Gemini, Claude, GPT, Ollama)
in persistent conversation rooms with shared context and memory.
"""

__version__ = "0.1.0"
__author__ = "A-Team Contributors"

from ateam.core.room import RoomManager, RoomMetadata
from ateam.core.history import HistoryManager, Message
from ateam.core.context import ContextManager
from ateam.core.config import ConfigManager
from ateam.core.router import AgentRouter
from ateam.tools.manager import ToolManager
from ateam.providers import BaseProvider, ProviderConfig, ProviderFactory

__all__ = [
    "RoomManager",
    "RoomMetadata",
    "HistoryManager",
    "Message",
    "ContextManager",
    "ConfigManager",
    "AgentRouter",
    "ToolManager",
    "BaseProvider",
    "ProviderConfig",
    "ProviderFactory",
]
