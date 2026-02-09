"""
Tests for RateLimiter.

Tests cover:
- Token bucket algorithm
- Rate limit enforcement
- Wait time calculation
- Retry logic with exponential backoff
- Per-provider limits
"""

import time

import pytest

from ateam.security.rate_limiter import RateLimiter, RateLimitConfig, TokenBucket


class TestTokenBucket:
    """Test suite for TokenBucket."""

    def test_init_full_capacity(self) -> None:
        """Test that token bucket initializes to full capacity."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        
        assert bucket.get_available_tokens() == 100

    def test_consume_tokens(self) -> None:
        """Test consuming tokens from the bucket."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        
        assert bucket.consume(10) is True
        assert bucket.get_available_tokens() == 90

    def test_consume_insufficient_tokens(self) -> None:
        """Test consuming more tokens than available."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        assert bucket.consume(5) is True
        assert bucket.consume(10) is False  # Only 5 left
        assert bucket.get_available_tokens() == 5

    def test_refill_tokens(self) -> None:
        """Test that tokens refill over time."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)  # 10 tokens/second
        
        # Consume some tokens
        bucket.consume(50)
        assert bucket.get_available_tokens() == 50
        
        # Wait for refill (0.5 seconds = 5 tokens)
        time.sleep(0.5)
        
        # Should have ~55 tokens (50 + 5)
        available = bucket.get_available_tokens()
        assert 54 <= available <= 56  # Allow small timing variance

    def test_refill_cap_at_capacity(self) -> None:
        """Test that refill doesn't exceed capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=100.0)  # Fast refill
        
        bucket.consume(5)
        time.sleep(0.2)  # Wait for refill
        
        # Should cap at capacity (10)
        assert bucket.get_available_tokens() == 10

    def test_get_wait_time_available(self) -> None:
        """Test wait time when tokens are available."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        
        wait_time = bucket.get_wait_time(10)
        assert wait_time == 0.0

    def test_get_wait_time_insufficient(self) -> None:
        """Test wait time when tokens are insufficient."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/second
        
        bucket.consume(10)  # Empty the bucket
        
        wait_time = bucket.get_wait_time(5)  # Need 5 tokens
        
        # Should need ~0.5 seconds (5 tokens / 10 tokens/sec)
        assert 0.4 <= wait_time <= 0.6


class TestRateLimiter:
    """Test suite for RateLimiter."""

    @pytest.fixture
    def limiter(self) -> RateLimiter:
        """Create a RateLimiter instance."""
        return RateLimiter()

    def test_init_default_limits(self, limiter: RateLimiter) -> None:
        """Test that default limits are set correctly."""
        assert "gemini" in limiter.buckets
        assert "anthropic" in limiter.buckets
        assert "openai" in limiter.buckets
        assert "ollama" in limiter.buckets

    def test_init_custom_limits(self) -> None:
        """Test initializing with custom limits."""
        custom_limits = {
            "gemini": RateLimitConfig(limit=50, window=60),
        }
        
        limiter = RateLimiter(custom_limits=custom_limits)
        
        # Gemini should have custom limit
        assert limiter.buckets["gemini"].capacity == 50

    def test_check_limit_allowed(self, limiter: RateLimiter) -> None:
        """Test that requests are allowed when under limit."""
        assert limiter.check_limit("gemini") is True

    def test_check_limit_exceeded(self) -> None:
        """Test that requests are blocked when limit is exceeded."""
        # Create limiter with very low limit
        custom_limits = {
            "gemini": RateLimitConfig(limit=2, window=60),
        }
        limiter = RateLimiter(custom_limits=custom_limits)
        
        # First two requests should succeed
        assert limiter.check_limit("gemini") is True
        assert limiter.check_limit("gemini") is True
        
        # Third request should fail
        assert limiter.check_limit("gemini") is False

    def test_check_limit_unknown_provider(self, limiter: RateLimiter) -> None:
        """Test that unknown providers are allowed by default."""
        assert limiter.check_limit("unknown_provider") is True

    def test_get_wait_time(self) -> None:
        """Test getting wait time for next request."""
        custom_limits = {
            "gemini": RateLimitConfig(limit=10, window=10),  # 1 token/second
        }
        limiter = RateLimiter(custom_limits=custom_limits)
        
        # Consume all tokens
        for _ in range(10):
            limiter.check_limit("gemini")
        
        # Should need to wait ~1 second for next token
        wait_time = limiter.get_wait_time("gemini")
        assert 0.9 <= wait_time <= 1.1

    def test_get_available_tokens(self, limiter: RateLimiter) -> None:
        """Test getting available tokens."""
        available = limiter.get_available_tokens("gemini")
        
        # Should start at full capacity (100)
        assert available == 100

    def test_get_available_tokens_after_consumption(self) -> None:
        """Test getting available tokens after consumption."""
        custom_limits = {
            "gemini": RateLimitConfig(limit=10, window=60),
        }
        limiter = RateLimiter(custom_limits=custom_limits)
        
        limiter.check_limit("gemini")  # Consume 1 token
        
        assert limiter.get_available_tokens("gemini") == 9

    def test_wait_if_needed_not_needed(self, limiter: RateLimiter) -> None:
        """Test wait_if_needed when no wait is needed."""
        start = time.time()
        limiter.wait_if_needed("gemini")
        elapsed = time.time() - start
        
        # Should return immediately
        assert elapsed < 0.1

    def test_wait_if_needed_waits(self) -> None:
        """Test wait_if_needed actually waits when needed."""
        custom_limits = {
            "gemini": RateLimitConfig(limit=5, window=5),  # 1 token/second
        }
        limiter = RateLimiter(custom_limits=custom_limits)
        
        # Consume all tokens
        for _ in range(5):
            limiter.check_limit("gemini")
        
        # This should wait ~1 second
        start = time.time()
        limiter.wait_if_needed("gemini")
        elapsed = time.time() - start
        
        assert 0.9 <= elapsed <= 1.2  # Allow some timing variance

    def test_retry_count_tracking(self, limiter: RateLimiter) -> None:
        """Test retry count tracking."""
        assert limiter.get_retry_count("gemini") == 0
        
        limiter.increment_retry_count("gemini")
        assert limiter.get_retry_count("gemini") == 1
        
        limiter.increment_retry_count("gemini")
        assert limiter.get_retry_count("gemini") == 2
        
        limiter.reset_retry_count("gemini")
        assert limiter.get_retry_count("gemini") == 0

    def test_should_retry_enabled(self, limiter: RateLimiter) -> None:
        """Test should_retry when auto-retry is enabled."""
        assert limiter.should_retry("gemini") is True
        
        limiter.increment_retry_count("gemini")
        assert limiter.should_retry("gemini") is True
        
        limiter.increment_retry_count("gemini")
        assert limiter.should_retry("gemini") is True
        
        limiter.increment_retry_count("gemini")
        # Should be False after max_retries (3)
        assert limiter.should_retry("gemini") is False

    def test_should_retry_disabled(self) -> None:
        """Test should_retry when auto-retry is disabled."""
        limiter = RateLimiter(enable_auto_retry=False)
        
        assert limiter.should_retry("gemini") is False

    def test_get_backoff_time(self, limiter: RateLimiter) -> None:
        """Test exponential backoff calculation."""
        # First retry: 1 * (2^0) = 1 second
        assert limiter.get_backoff_time("gemini") == 1.0
        
        limiter.increment_retry_count("gemini")
        # Second retry: 1 * (2^1) = 2 seconds
        assert limiter.get_backoff_time("gemini") == 2.0
        
        limiter.increment_retry_count("gemini")
        # Third retry: 1 * (2^2) = 4 seconds
        assert limiter.get_backoff_time("gemini") == 4.0

    def test_get_stats(self, limiter: RateLimiter) -> None:
        """Test getting rate limit statistics."""
        stats = limiter.get_stats("gemini")
        
        assert "available_tokens" in stats
        assert "capacity" in stats
        assert "wait_time" in stats
        assert "retry_count" in stats
        
        assert stats["available_tokens"] == 100
        assert stats["capacity"] == 100
        assert stats["wait_time"] == 0.0
        assert stats["retry_count"] == 0

    def test_get_stats_after_usage(self) -> None:
        """Test getting stats after some usage."""
        custom_limits = {
            "gemini": RateLimitConfig(limit=10, window=60),
        }
        limiter = RateLimiter(custom_limits=custom_limits)
        
        limiter.check_limit("gemini")  # Consume 1 token
        limiter.increment_retry_count("gemini")
        
        stats = limiter.get_stats("gemini")
        
        assert stats["available_tokens"] == 9
        assert stats["capacity"] == 10
        assert stats["retry_count"] == 1

    def test_get_stats_unknown_provider(self, limiter: RateLimiter) -> None:
        """Test getting stats for unknown provider."""
        stats = limiter.get_stats("unknown")
        
        # Should return unlimited stats
        assert stats["available_tokens"] == 999999
        assert stats["capacity"] == 999999
