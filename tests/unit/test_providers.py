"""
Tests for AI Providers and ProviderFactory.

Tests cover:
- Mocked completion for all providers
- ProviderFactory instantiation
- Common configuration handling
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from ateam.providers import (
    ProviderFactory, 
    ProviderConfig, 
    GeminiProvider, 
    AnthropicProvider, 
    OpenAIProvider
)


class TestProviders:
    """Test suite for AI Providers."""

    @pytest.fixture
    def config(self):
        return ProviderConfig(model_name="test-model", temperature=0.5)

    def test_factory_creates_gemini(self, config):
        provider = ProviderFactory.create("gemini", config, "fake-key")
        assert isinstance(provider, GeminiProvider)

    def test_factory_creates_anthropic(self, config):
        provider = ProviderFactory.create("anthropic", config, "fake-key")
        assert isinstance(provider, AnthropicProvider)

    def test_factory_creates_openai(self, config):
        provider = ProviderFactory.create("openai", config, "fake-key")
        assert isinstance(provider, OpenAIProvider)

    def test_factory_invalid_provider(self, config):
        with pytest.raises(ValueError, match="Unknown provider"):
            ProviderFactory.create("unknown", config, "fake-key")

    @pytest.mark.asyncio
    async def test_openai_completion(self, config):
        with patch("openai.AsyncOpenAI") as mock_openai:
            # Setup mock response
            mock_client = mock_openai.return_value
            mock_client.chat.completions.create = AsyncMock()
            
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Hello from AI"
            mock_response.usage.prompt_tokens = 10
            mock_response.usage.completion_tokens = 5
            mock_response.usage.total_tokens = 15
            
            mock_client.chat.completions.create.return_value = mock_response
            
            provider = OpenAIProvider(config, "fake-key")
            response = await provider.complete([{"role": "user", "content": "Hi"}])
            
            assert response.content == "Hello from AI"
            assert response.total_tokens == 15

    @pytest.mark.asyncio
    async def test_anthropic_completion(self, config):
        with patch("anthropic.AsyncAnthropic") as mock_anthropic:
            mock_client = mock_anthropic.return_value
            mock_client.messages.create = AsyncMock()
            
            mock_response = MagicMock()
            mock_response.content = [MagicMock(type="text", text="Hello from Claude")]
            mock_response.usage.input_tokens = 8
            mock_response.usage.output_tokens = 4
            
            mock_client.messages.create.return_value = mock_response
            
            provider = AnthropicProvider(config, "fake-key")
            response = await provider.complete([{"role": "user", "content": "Hi"}])
            
            assert response.content == "Hello from Claude"
            assert response.prompt_tokens == 8

    @pytest.mark.asyncio
    async def test_gemini_completion(self, config):
        with patch("google.generativeai.GenerativeModel") as mock_model_class:
            mock_model = mock_model_class.return_value
            mock_model.generate_content_async = AsyncMock()
            
            mock_response = MagicMock()
            mock_response.text = "Hello from Gemini"
            
            mock_model.generate_content_async.return_value = mock_response
            
            # Mock genai.configure
            with patch("google.generativeai.configure"):
                provider = GeminiProvider(config, "fake-key")
                # Need to mock the model on the instance since __init__ creates it
                provider.model = mock_model
                
                response = await provider.complete([{"role": "user", "content": "Hi"}])
                
                assert response.content == "Hello from Gemini"
