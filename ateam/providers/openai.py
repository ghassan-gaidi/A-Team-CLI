"""
OpenAI GPT Provider for A-Team CLI.
"""

from typing import Any, Dict, List, Optional, AsyncIterator
import openai
from ateam.providers.base import BaseProvider, ProviderConfig, CompletionResponse


class OpenAIProvider(BaseProvider):
    """
    Adapter for OpenAI's GPT models (e.g., gpt-4o, gpt-4-turbo, gpt-3.5-turbo).
    """

    def __init__(self, config: ProviderConfig, api_key: str) -> None:
        super().__init__(config, api_key)
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    async def complete(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> CompletionResponse:
        """Get a non-streaming completion from GPT."""
        formatted_messages = self._format_messages(messages, system_prompt)
        
        response = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=formatted_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
            stop=self.config.stop_sequences,
        )

        content = response.choices[0].message.content or ""
        
        return CompletionResponse(
            content=content,
            model_name=self.config.model_name,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            raw_response=response
        )

    async def stream(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Stream response from GPT."""
        formatted_messages = self._format_messages(messages, system_prompt)
        
        stream = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=formatted_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
