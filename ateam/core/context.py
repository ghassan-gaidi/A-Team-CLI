"""
Context Window Management for A-Team CLI.

This module handles token-based trimming and sliding windows to ensure 
conversations stay within the context limits of AI models.
"""

from typing import Dict, List, Optional
from ateam.utils.token_counter import TokenCounter


class ContextManager:
    """
    Manages the conversation context window.
    
    Ensures that the total token count of messages sent to the provider
    stays within specified limits while preserving important context.
    """

    def __init__(
        self, 
        max_tokens: int,
        preserve_system: bool = True,
        preserve_first_n: int = 0
    ) -> None:
        """
        Initialize the context manager.

        Args:
            max_tokens: Maximum allowed tokens for the context window.
            preserve_system: Whether to always keep the system message.
            preserve_first_n: Number of early messages (after system) to always keep.
        """
        self.max_tokens = max_tokens
        self.preserve_system = preserve_system
        self.preserve_first_n = preserve_first_n

    def get_trimmed_context(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Trims a list of messages to fit within the token limit.
        """
        # Prepare full context
        full_context = []
        if system_prompt:
            full_context.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            if msg["role"] == "system" and system_prompt:
                continue
            full_context.append(msg)

        if not full_context:
            return []

        # Baseline tokens for any request
        baseline = 3
        
        # Identify fixed messages (system + first_n)
        fixed_indices = []
        if full_context[0]["role"] == "system":
            fixed_indices.append(0)
            
        for i in range(len(fixed_indices), len(fixed_indices) + self.preserve_first_n):
            if i < len(full_context):
                fixed_indices.append(i)
        
        fixed_msgs = [full_context[i] for i in fixed_indices]
        
        # Calculate tokens for fixed messages
        def count_tokens(msgs: List[Dict[str, str]]) -> int:
            return sum(TokenCounter.estimate_tokens(m["content"]) + 4 for m in msgs)

        fixed_tokens = count_tokens(fixed_msgs)
        
        if baseline + fixed_tokens > self.max_tokens:
            # Over budget even with just fixed messages
            return fixed_msgs[:1] if fixed_msgs else []

        # Available budget for recent messages
        budget = self.max_tokens - baseline - fixed_tokens
        
        # Select recent messages (backwards from the end)
        candidates = []
        current_candidate_tokens = 0
        
        # Iterate from the end, skipping fixed messages
        for i in range(len(full_context) - 1, -1, -1):
            if i in fixed_indices:
                continue
            
            msg = full_context[i]
            msg_tokens = TokenCounter.estimate_tokens(msg["content"]) + 4
            
            if current_candidate_tokens + msg_tokens <= budget:
                candidates.insert(0, msg)
                current_candidate_tokens += msg_tokens
            else:
                break
                
        return fixed_msgs + candidates

    def get_token_usage(self, messages: List[Dict[str, str]]) -> Dict[str, int]:
        """
        Get detailed token usage information.
        """
        total = TokenCounter.estimate_message_tokens(messages)
        return {
            "total_tokens": total,
            "max_tokens": self.max_tokens,
            "usage_percent": int((total / self.max_tokens) * 100) if self.max_tokens > 0 else 0
        }
