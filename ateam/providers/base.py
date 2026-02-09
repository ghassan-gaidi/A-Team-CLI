"""
Base Provider Interface for A-Team CLI.

This module defines the abstract interface that all AI providers (Gemini, 
Anthropic, OpenAI, etc.) must implement. This ensures a unified way to 
interact with different LLMs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncIterator
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Configuration for an AI provider."""
    model_name: str = Field(..., description="The name of the model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, description="Max tokens in response")
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    stop_sequences: Optional[List[str]] = Field(default=None)
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class CompletionResponse(BaseModel):
    """Standardized response from any AI provider."""
    content: str = Field(..., description="The generated text content")
    model_name: str = Field(..., description="The actual model used")
    prompt_tokens: Optional[int] = Field(None)
    completion_tokens: Optional[int] = Field(None)
    total_tokens: Optional[int] = Field(None)
    raw_response: Any = Field(default=None, exclude=True)


class BaseProvider(ABC):
    """
    Abstract base class for all AI providers.
    
    All concrete providers must implement chat-based completion and
    ideally streaming support.
    """

    def __init__(self, config: ProviderConfig, api_key: str) -> None:
        """
        Initialize the provider.

        Args:
            config: Provider configuration
            api_key: The API key for the provider
        """
        self.config = config
        self.api_key = api_key

    @abstractmethod
    async def complete(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> CompletionResponse:
        """
        Send a set of messages to the model and get a completion.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system instructions

        Returns:
            CompletionResponse containing the generated text and metadata
        """
        pass

    @abstractmethod
    async def stream(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Stream the completion response token by token.

        Args:
            messages: List of message dictionaries
            system_prompt: Optional system instructions

        Yields:
            Chunks of text as they are generated
        """
        pass

    def _format_messages(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Generic helper to prep messages, including system prompt.
        Concrete classes might override this based on API requirements.
        """
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        formatted.extend(messages)
        return formatted
