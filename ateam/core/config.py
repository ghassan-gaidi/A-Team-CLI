"""
Configuration Management for A-Team CLI.

This module handles loading and parsing the config.yaml file, 
defining schemas for agents and security settings.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from pydantic import BaseModel, Field, SecretStr


class AgentConfig(BaseModel):
    """Configuration for an individual agent."""
    provider: str
    model: str
    api_key_env: str
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 4096
    base_url: Optional[str] = None


class SecurityConfig(BaseModel):
    """Security settings from config.yaml."""
    rate_limits_enabled: bool = Field(True, alias="rate_limits.enabled")
    input_validation_enabled: bool = Field(True, alias="input_validation.enabled")
    # Add more as needed


class GlobalConfig(BaseModel):
    """Root configuration object for A-Team."""
    version: str
    default_agent: str
    context_window_size: int = 30
    auto_prune: bool = True
    agents: Dict[str, AgentConfig]
    security: Dict[str, Any] = Field(default_factory=dict)


class ConfigManager:
    """
    Manages loading and accessing A-Team configuration.
    """

    DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ateam" / "config.yaml"

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize the config manager.

        Args:
            config_path: Path to config.yaml. Defaults to ~/.config/ateam/config.yaml
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: Optional[GlobalConfig] = None
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            # Dev search path
            search_paths = [
                Path("config.yaml"),
                Path(".context/config.yaml"),
                Path(__file__).parent.parent.parent / ".context" / "config.yaml",
                Path(__file__).parent.parent.parent / "config.yaml",
            ]
            
            for path in search_paths:
                if path.exists():
                    self.config_path = path
                    break
            else:
                # If still not found, create a minimal default or raise
                raise FileNotFoundError(f"Config file not found. Checked default and dev fallback paths.")

        with open(self.config_path, "r") as f:
            raw_data = yaml.safe_load(f)
            self.config = GlobalConfig(**raw_data)

    def get_agent(self, name: str) -> AgentConfig:
        """Get configuration for a specific agent."""
        if not self.config:
            raise RuntimeError("Config not loaded")
        
        # Exact match
        if name in self.config.agents:
            return self.config.agents[name]
        
        # Case-insensitive match
        for agent_name, cfg in self.config.agents.items():
            if agent_name.lower() == name.lower():
                return cfg
                
        raise ValueError(f"Agent '{name}' not found in configuration.")

    def get_default_agent(self) -> AgentConfig:
        """Get the default agent configuration."""
        if not self.config:
            raise RuntimeError("Config not loaded")
        return self.get_agent(self.config.default_agent)
