"""
Unified AI Providers for A-Team CLI.
"""

from typing import Optional, Type
from ateam.providers.base import BaseProvider, ProviderConfig, CompletionResponse
from ateam.providers.gemini import GeminiProvider
from ateam.providers.anthropic import AnthropicProvider
from ateam.providers.openai import OpenAIProvider

__all__ = [
    "BaseProvider",
    "ProviderConfig",
    "CompletionResponse",
    "GeminiProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "ProviderFactory",
]


class ProviderFactory:
    """
    Factory class to instantiate AI providers based on their name.
    """

    _PROVIDERS = {
        "gemini": GeminiProvider,
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def create(
        cls, 
        provider_name: str, 
        config: ProviderConfig, 
        api_key: str
    ) -> BaseProvider:
        """
        Create a provider instance.

        Args:
            provider_name: One of 'gemini', 'anthropic', 'openai'
            config: Configuration for the specific provider/model
            api_key: The API key to use

        Returns:
            An instance of BaseProvider

        Raises:
            ValueError: If the provider name is unknown
        """
        provider_class = cls._PROVIDERS.get(provider_name.lower())
        if not provider_class:
            valid = ", ".join(cls._PROVIDERS.keys())
            raise ValueError(
                f"Unknown provider '{provider_name}'. Valid options: {valid}"
            )
        
        return provider_class(config, api_key)
