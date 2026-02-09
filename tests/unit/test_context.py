"""
Tests for ContextManager.

Tests cover:
- Basic trimming logic
- Preserving system prompt
- Preserving grounding messages (preserve_first_n)
- Token usage calculation
"""

import pytest
from ateam.core.context import ContextManager


class TestContextManager:
    """Test suite for ContextManager."""

    def test_no_trimming_needed(self):
        """Test that messages aren't trimmed if they fit."""
        cm = ContextManager(max_tokens=1000)
        messages = [{"role": "user", "content": "Hello"}]
        
        result = cm.get_trimmed_context(messages)
        assert len(result) == 1
        assert result[0]["content"] == "Hello"

    def test_basic_trimming_sliding_window(self):
        """Test that oldest messages are removed first."""
        # Use large differences to avoid rounding issues
        # Msg is approx 100/4 = 25 tokens + 4 = 29.
        # Max tokens 50 -> can fit only 1 message (29 + 3 baseline = 32).
        # Two messages would be 29*2 + 3 = 61.
        cm = ContextManager(max_tokens=50)
        messages = [
            {"role": "user", "content": "A" * 100}, 
            {"role": "user", "content": "B" * 100},
        ]
        
        result = cm.get_trimmed_context(messages)
        assert len(result) == 1
        assert result[0]["content"] == "B" * 100

    def test_preserve_system_prompt(self):
        """Test that system prompt is always kept."""
        # Sys(29) + M1(29) + M2(29) + B(3) = 90
        # Max 70 allows Sys(29) + M2(29) + B(3) = 61
        cm = ContextManager(max_tokens=70)
        
        messages = [
            {"role": "system", "content": "S" * 100},
            {"role": "user", "content": "1" * 100},
            {"role": "user", "content": "2" * 100},
        ]
        
        result = cm.get_trimmed_context(messages)
        
        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert result[1]["content"] == "2" * 100

    def test_preserve_grounding_messages(self):
        """Test that first N messages are preserved."""
        # Sys(29) + G1(29) + M1(29) + M2(29) + B(3) = 119
        # Max 100 allows Sys+G1+M2+B = 90
        cm = ContextManager(max_tokens=100, preserve_first_n=1)
        
        messages = [
            {"role": "system", "content": "S" * 100},
            {"role": "user", "content": "G" * 100},
            {"role": "user", "content": "1" * 100},
            {"role": "user", "content": "2" * 100},
        ]
        
        result = cm.get_trimmed_context(messages)
        
        assert len(result) == 3
        assert result[0]["content"] == "S" * 100
        assert result[1]["content"] == "G" * 100
        assert result[2]["content"] == "2" * 100

    def test_token_usage(self):
        """Test token usage reporting."""
        cm = ContextManager(max_tokens=100)
        messages = [{"role": "user", "content": "A" * 40}] # 10 tokens + 4 = 14. + 3 baseline = 17
        
        usage = cm.get_token_usage(messages)
        assert usage["total_tokens"] == 17
        assert usage["max_tokens"] == 100
        assert usage["usage_percent"] == 17
