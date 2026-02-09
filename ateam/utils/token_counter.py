"""
Token Counter Utility for A-Team CLI.

Provides robust token estimation for different AI providers.
While not as precise as provider-specific tokenizers, this provides
a consistent and efficient way to manage context windows.
"""

from typing import Dict, List, Union


class TokenCounter:
    """
    Estimates token counts for various models and providers.
    """

    # Average characters per token based on empirical data for common LLMs
    CHARS_PER_TOKEN = 4.0

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """
        Estimate the number of tokens in a string.
        
        Using 4 characters per token as a standard baseline for English.
        """
        if not text:
            return 0
        return max(1, int(len(text) / cls.CHARS_PER_TOKEN))

    @classmethod
    def estimate_message_tokens(cls, messages: List[Dict[str, str]]) -> int:
        """
        Estimate tokens for a list of messages.
        Includes typical overhead for message framing.
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            # Add 4 tokens overhead per message (role + framing)
            total += cls.estimate_tokens(content) + 4
        
        # Add a small buffer for the final response framing
        return total + 3

    @classmethod
    def get_max_context(cls, model_name: str) -> int:
        """
        Get the maximum context window for a given model.
        Defaults to safety limits if unknown.
        """
        model_name = model_name.lower()
        
        # Gemini
        if "gemini-1.5-pro" in model_name:
            return 2_000_000
        if "gemini-1.5-flash" in model_name:
            return 1_000_000
        if "gemini-1.0-pro" in model_name:
            return 32_768
            
        # Anthropic Claude
        if "claude-3" in model_name:
            return 200_000
        if "claude-2" in model_name:
            return 100_000
            
        # OpenAI GPT
        if "gpt-4o" in model_name:
            return 128_000
        if "gpt-4-turbo" in model_name:
            return 128_000
        if "gpt-4" in model_name:
            return 8_192
        if "gpt-3.5-turbo" in model_name:
            return 16_385
            
        # Default fallback
        return 4_096
