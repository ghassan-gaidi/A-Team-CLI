"""
Anthropic Claude Provider for A-Team CLI.
"""

from typing import Any, Dict, List, Optional, AsyncIterator
import anthropic
from ateam.providers.base import BaseProvider, ProviderConfig, CompletionResponse


class AnthropicProvider(BaseProvider):
    """
    Adapter for Anthropic's Claude models (e.g., claude-3-5-sonnet, claude-3-opus).
    """

    def __init__(self, config: ProviderConfig, api_key: str) -> None:
        super().__init__(config, api_key)
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def complete(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> CompletionResponse:
        """Get a non-streaming completion from Claude."""
        response = await self.client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens or 4096,
            system=system_prompt or anthropic.NOT_GIVEN,
            messages=messages,
            temperature=self.config.temperature,
            top_p=self.config.top_p or anthropic.NOT_GIVEN,
            stop_sequences=self.config.stop_sequences or anthropic.NOT_GIVEN,
        )

        # Anthropic provides content as a list of content blocks
        text = ""
        for block in response.content:
            if block.type == "text":
                text += block.text

        return CompletionResponse(
            content=text,
            model_name=self.config.model_name,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            raw_response=response
        )

    async def stream(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Stream response from Claude."""
        async with self.client.messages.stream(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens or 4096,
            system=system_prompt or anthropic.NOT_GIVEN,
            messages=messages,
            temperature=self.config.temperature,
            top_p=self.config.top_p or anthropic.NOT_GIVEN,
        ) as stream:
            async for text in stream.text_stream:
                yield text
