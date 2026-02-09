"""
Rate Limiting for A-Team CLI.

This module implements rate limiting using the token bucket algorithm
to prevent API abuse, protect quotas, and handle rate limit errors gracefully.

Features:
- Token bucket algorithm for smooth rate limiting
- Per-provider limits (Gemini, Claude, GPT, Ollama)
- Automatic retry with exponential backoff
- Rate limit tracking and reporting
"""

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit."""

    limit: int = 100  # Maximum requests per window
    window: int = 60  # Time window in seconds


@dataclass
class TokenBucket:
    """
    Token bucket for rate limiting.

    The token bucket algorithm allows bursts while maintaining an average rate.
    Tokens are added at a constant rate, and each request consumes one token.

    Attributes:
        capacity: Maximum number of tokens (burst size)
        refill_rate: Tokens added per second
        tokens: Current number of tokens available
        last_refill: Timestamp of last refill
    """

    capacity: int
    refill_rate: float
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self) -> None:
        """Initialize token bucket to full capacity."""
        self.tokens = float(self.capacity)
        self.last_refill = time.time()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume (default: 1)

        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get the time to wait until tokens are available.

        Args:
            tokens: Number of tokens needed (default: 1)

        Returns:
            Seconds to wait (0 if tokens available now)
        """
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        # Calculate time needed to accumulate required tokens
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate

    def get_available_tokens(self) -> int:
        """
        Get the number of available tokens.

        Returns:
            Number of tokens currently available
        """
        self._refill()
        return int(self.tokens)


class RateLimiter:
    """
    Rate limiter for API calls using token bucket algorithm.

    Supports per-provider rate limits and automatic retry with exponential backoff.

    Example:
        >>> limiter = RateLimiter()
        >>> if limiter.check_limit("gemini"):
        ...     # Make API call
        ...     response = call_gemini_api()
        ... else:
        ...     wait_time = limiter.get_wait_time("gemini")
        ...     print(f"Rate limited. Wait {wait_time:.1f}s")
    """

    # Default rate limits per provider (requests per minute)
    DEFAULT_LIMITS = {
        "gemini": RateLimitConfig(limit=100, window=60),
        "anthropic": RateLimitConfig(limit=50, window=60),
        "openai": RateLimitConfig(limit=60, window=60),
        "ollama": RateLimitConfig(limit=1000, window=60),  # Local, higher limit
    }

    def __init__(
        self,
        custom_limits: Optional[dict[str, RateLimitConfig]] = None,
        enable_auto_retry: bool = True,
        max_retries: int = 3,
        backoff_multiplier: float = 2.0,
    ) -> None:
        """
        Initialize the rate limiter.

        Args:
            custom_limits: Optional custom rate limits per provider
            enable_auto_retry: Enable automatic retry with backoff (default: True)
            max_retries: Maximum number of retries (default: 3)
            backoff_multiplier: Backoff multiplier for retries (default: 2.0)
        """
        self.enable_auto_retry = enable_auto_retry
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier

        # Merge custom limits with defaults
        limits = {**self.DEFAULT_LIMITS}
        if custom_limits:
            limits.update(custom_limits)

        # Create token buckets for each provider
        self.buckets: dict[str, TokenBucket] = {}
        for provider, config in limits.items():
            # Calculate refill rate (tokens per second)
            refill_rate = config.limit / config.window

            self.buckets[provider] = TokenBucket(
                capacity=config.limit, refill_rate=refill_rate
            )

        # Track retry counts
        self.retry_counts: dict[str, int] = {}

    def check_limit(self, provider: str, tokens: int = 1) -> bool:
        """
        Check if a request is allowed under the rate limit.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)
            tokens: Number of tokens to consume (default: 1)

        Returns:
            True if request is allowed, False if rate limited
        """
        if provider not in self.buckets:
            # Unknown provider, allow by default
            return True

        bucket = self.buckets[provider]
        return bucket.consume(tokens)

    def get_wait_time(self, provider: str, tokens: int = 1) -> float:
        """
        Get the time to wait before the next request is allowed.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)
            tokens: Number of tokens needed (default: 1)

        Returns:
            Seconds to wait (0 if request allowed now)
        """
        if provider not in self.buckets:
            return 0.0

        bucket = self.buckets[provider]
        return bucket.get_wait_time(tokens)

    def get_available_tokens(self, provider: str) -> int:
        """
        Get the number of available tokens for a provider.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)

        Returns:
            Number of available tokens
        """
        if provider not in self.buckets:
            return 999999  # Unlimited for unknown providers

        bucket = self.buckets[provider]
        return bucket.get_available_tokens()

    def wait_if_needed(self, provider: str, tokens: int = 1) -> None:
        """
        Wait if rate limit is exceeded.

        This is a blocking call that waits until tokens are available.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)
            tokens: Number of tokens needed (default: 1)
        """
        wait_time = self.get_wait_time(provider, tokens)
        if wait_time > 0:
            time.sleep(wait_time)

    def reset_retry_count(self, provider: str) -> None:
        """
        Reset the retry count for a provider.

        Call this after a successful request.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)
        """
        self.retry_counts[provider] = 0

    def increment_retry_count(self, provider: str) -> int:
        """
        Increment the retry count for a provider.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)

        Returns:
            New retry count
        """
        current = self.retry_counts.get(provider, 0)
        self.retry_counts[provider] = current + 1
        return self.retry_counts[provider]

    def get_retry_count(self, provider: str) -> int:
        """
        Get the current retry count for a provider.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)

        Returns:
            Current retry count
        """
        return self.retry_counts.get(provider, 0)

    def should_retry(self, provider: str) -> bool:
        """
        Check if a retry should be attempted.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)

        Returns:
            True if retry should be attempted, False otherwise
        """
        if not self.enable_auto_retry:
            return False

        return self.get_retry_count(provider) < self.max_retries

    def get_backoff_time(self, provider: str) -> float:
        """
        Calculate exponential backoff time for retries.

        Backoff formula: base_delay * (multiplier ^ retry_count)
        Example: 1s, 2s, 4s, 8s with multiplier=2

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)

        Returns:
            Seconds to wait before retry
        """
        retry_count = self.get_retry_count(provider)
        base_delay = 1.0  # 1 second base delay
        return base_delay * (self.backoff_multiplier**retry_count)

    def get_stats(self, provider: str) -> dict[str, any]:
        """
        Get rate limit statistics for a provider.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)

        Returns:
            Dictionary with statistics:
            - available_tokens: Current available tokens
            - capacity: Maximum tokens (burst size)
            - wait_time: Time to wait for next token
            - retry_count: Current retry count
        """
        if provider not in self.buckets:
            return {
                "available_tokens": 999999,
                "capacity": 999999,
                "wait_time": 0.0,
                "retry_count": 0,
            }

        bucket = self.buckets[provider]
        return {
            "available_tokens": bucket.get_available_tokens(),
            "capacity": bucket.capacity,
            "wait_time": bucket.get_wait_time(1),
            "retry_count": self.get_retry_count(provider),
        }
