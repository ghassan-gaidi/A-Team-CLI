"""
Integration tests for security components.

These tests verify that all security components work together correctly.
"""

from ateam.security import SecureAPIKeyManager, InputValidator, RateLimiter


def test_security_components_integration():
    """Test that all security components can be instantiated and used together."""
    # API Key Manager
    manager = SecureAPIKeyManager()
    assert manager is not None
    assert "gemini" in manager.PROVIDERS
    
    # Input Validator
    validator = InputValidator()
    assert validator is not None
    msg = validator.validate_message("Test message")
    assert msg.content == "Test message"
    
    # Rate Limiter
    limiter = RateLimiter()
    assert limiter is not None
    assert limiter.check_limit("gemini") is True


def test_api_key_redaction():
    """Test API key redaction works correctly."""
    key = "sk-abc123456789xyz"
    redacted = SecureAPIKeyManager.redact_key(key)
    
    assert "sk-abc12345...xyz" == redacted
    assert "6789" not in redacted


def test_input_validation_security():
    """Test input validation prevents security issues."""
    validator = InputValidator()
    
    # Test null byte blocking
    try:
        validator.validate_message("test\x00message")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "null bytes" in str(e)
    
    # Test room name validation
    room = validator.validate_room_name("valid-room-123")
    assert room.name == "valid-room-123"
    
    # Test invalid room name
    try:
        validator.validate_room_name("invalid room!")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "can only contain" in str(e)


def test_rate_limiting_basic():
    """Test basic rate limiting functionality."""
    from ateam.security.rate_limiter import RateLimitConfig
    
    # Create limiter with low limit for testing
    custom_limits = {
        "test": RateLimitConfig(limit=2, window=60),
    }
    limiter = RateLimiter(custom_limits=custom_limits)
    
    # First two requests should succeed
    assert limiter.check_limit("test") is True
    assert limiter.check_limit("test") is True
    
    # Third should fail
    assert limiter.check_limit("test") is False
    
    # Check stats
    stats = limiter.get_stats("test")
    assert stats["available_tokens"] == 0
    assert stats["capacity"] == 2


if __name__ == "__main__":
    test_security_components_integration()
    print("✓ Integration test passed")
    
    test_api_key_redaction()
    print("✓ API key redaction test passed")
    
    test_input_validation_security()
    print("✓ Input validation test passed")
    
    test_rate_limiting_basic()
    print("✓ Rate limiting test passed")
    
    print("\n✅ All integration tests passed!")
