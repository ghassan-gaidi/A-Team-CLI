"""
Google Gemini Provider for A-Team CLI.
"""

from typing import Any, Dict, List, Optional, AsyncIterator
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from ateam.providers.base import BaseProvider, ProviderConfig, CompletionResponse


class GeminiProvider(BaseProvider):
    """
    Adapter for Google's Gemini models (e.g., gemini-1.5-pro, gemini-1.5-flash).
    """

    def __init__(self, config: ProviderConfig, api_key: str) -> None:
        super().__init__(config, api_key)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=self.config.model_name,
            generation_config=self._get_generation_config()
        )

    def _get_generation_config(self) -> Dict[str, Any]:
        """Convert ProviderConfig to Gemini GenerationConfig format."""
        cfg = {
            "temperature": self.config.temperature,
            "max_output_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "stop_sequences": self.config.stop_sequences,
        }
        # Filter out None values
        return {k: v for k, v in cfg.items() if v is not None}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Convert OpenAI-style messages to Gemini history format.
        Gemini uses 'parts' and 'role' (user/model).
        """
        history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            if msg["role"] == "system":
                # System prompts are handled during model initialization 
                # or as specialized user messages in Gemini's older API.
                # In 1.5+, System Instruction is a separate param.
                continue
            history.append({"role": role, "parts": [msg["content"]]})
        return history

    async def complete(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> CompletionResponse:
        """Get a non-streaming completion from Gemini."""
        # For Gemini 1.5, we handle system prompt via instruction attribute if provided
        if system_prompt:
            self.model = genai.GenerativeModel(
                model_name=self.config.model_name,
                generation_config=self._get_generation_config(),
                system_instruction=system_prompt
            )

        history = self._convert_messages(messages)
        # The last message is the "prompt", others are "history"
        prompt = history.pop()["parts"][0]
        chat = self.model.start_chat(history=history)
        
        # NOTE: genai does not have a native async client in the standard SDK yet
        # but we wrap it in a pseudo-async call for consistency.
        # In a real heavy-load app, we'd use a thread pool.
        response: GenerateContentResponse = await self.model.generate_content_async(
            prompt,
            generation_config=self._get_generation_config()
        )

        return CompletionResponse(
            content=response.text,
            model_name=self.config.model_name,
            raw_response=response
        )

    async def stream(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Stream response from Gemini."""
        if system_prompt:
            self.model = genai.GenerativeModel(
                model_name=self.config.model_name,
                generation_config=self._get_generation_config(),
                system_instruction=system_prompt
            )

        history = self._convert_messages(messages)
        prompt = history.pop()["parts"][0]
        chat = self.model.start_chat(history=history)

        response = await self.model.generate_content_async(
            prompt,
            generation_config=self._get_generation_config(),
            stream=True
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text
