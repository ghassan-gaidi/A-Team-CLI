"""
Tests for SecureAPIKeyManager.

Tests cover:
- Key storage and retrieval
- Storage hierarchy (keyring > env > config)
- Key redaction
- Key filtering from text
- Provider validation
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from ateam.security.api_keys import SecureAPIKeyManager


class TestSecureAPIKeyManager:
    """Test suite for SecureAPIKeyManager."""

    @pytest.fixture
    def manager(self) -> SecureAPIKeyManager:
        """Create a SecureAPIKeyManager instance."""
        return SecureAPIKeyManager()

    @pytest.fixture
    def mock_keyring(self):
        """Mock the keyring module."""
        with patch("ateam.security.api_keys.keyring") as mock:
            yield mock

    def test_store_key_valid_provider(self, manager: SecureAPIKeyManager, mock_keyring) -> None:
        """Test storing a key for a valid provider."""
        manager.store_key("gemini", "test-api-key-12345")
        
        mock_keyring.set_password.assert_called_once_with(
            "ateam-cli", "gemini_api_key", "test-api-key-12345"
        )

    def test_store_key_invalid_provider(self, manager: SecureAPIKeyManager) -> None:
        """Test storing a key for an invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            manager.store_key("invalid_provider", "test-key")

    def test_store_key_empty(self, manager: SecureAPIKeyManager) -> None:
        """Test storing an empty key raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            manager.store_key("gemini", "")

    def test_get_key_from_keyring(self, manager: SecureAPIKeyManager, mock_keyring) -> None:
        """Test retrieving a key from keyring (highest priority)."""
        mock_keyring.get_password.return_value = "keyring-key"
        
        key = manager.get_key("gemini")
        
        assert key == "keyring-key"
        mock_keyring.get_password.assert_called_once_with("ateam-cli", "gemini_api_key")

    def test_get_key_from_env(self, manager: SecureAPIKeyManager, mock_keyring) -> None:
        """Test retrieving a key from environment (second priority)."""
        mock_keyring.get_password.return_value = None
        
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key"}):
            key = manager.get_key("gemini")
        
        assert key == "env-key"

    def test_get_key_from_config(self, manager: SecureAPIKeyManager, mock_keyring) -> None:
        """Test retrieving a key from config (lowest priority)."""
        mock_keyring.get_password.return_value = None
        
        with patch.dict(os.environ, {}, clear=True):
            key = manager.get_key("gemini", config_value="config-key")
        
        assert key == "config-key"

    def test_get_key_hierarchy(self, manager: SecureAPIKeyManager, mock_keyring) -> None:
        """Test that keyring takes priority over env and config."""
        mock_keyring.get_password.return_value = "keyring-key"
        
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key"}):
            key = manager.get_key("gemini", config_value="config-key")
        
        # Should return keyring key (highest priority)
        assert key == "keyring-key"

    def test_get_key_not_found(self, manager: SecureAPIKeyManager, mock_keyring) -> None:
        """Test retrieving a non-existent key returns None."""
        mock_keyring.get_password.return_value = None
        
        with patch.dict(os.environ, {}, clear=True):
            key = manager.get_key("gemini")
        
        assert key is None

    def test_delete_key(self, manager: SecureAPIKeyManager, mock_keyring) -> None:
        """Test deleting a key from keyring."""
        manager.delete_key("gemini")
        
        mock_keyring.delete_password.assert_called_once_with("ateam-cli", "gemini_api_key")

    def test_list_stored_keys(self, manager: SecureAPIKeyManager, mock_keyring) -> None:
        """Test listing stored keys."""
        def get_password_side_effect(service, key):
            if key == "gemini_api_key":
                return "gemini-key"
            elif key == "anthropic_api_key":
                return "anthropic-key"
            return None
        
        mock_keyring.get_password.side_effect = get_password_side_effect
        
        stored = manager.list_stored_keys()
        
        assert "gemini" in stored
        assert "anthropic" in stored
        assert "openai" not in stored

    def test_redact_key_standard(self) -> None:
        """Test redacting a standard API key."""
        key = "sk-abc123456789xyz"
        redacted = SecureAPIKeyManager.redact_key(key)
        
        assert redacted == "sk-abc12345...xyz"
        assert "6789" not in redacted

    def test_redact_key_short(self) -> None:
        """Test redacting a short key."""
        key = "short"
        redacted = SecureAPIKeyManager.redact_key(key)
        
        assert redacted == "***"

    def test_redact_key_empty(self) -> None:
        """Test redacting an empty key."""
        redacted = SecureAPIKeyManager.redact_key("")
        
        assert redacted == "[EMPTY]"

    def test_filter_keys_from_text(self) -> None:
        """Test filtering keys from text."""
        text = "Error: Invalid API key sk-abc123456789xyz was rejected"
        keys = ["sk-abc123456789xyz"]
        
        filtered = SecureAPIKeyManager.filter_keys_from_text(text, keys)
        
        assert "sk-abc123456789xyz" not in filtered
        assert "sk-abc12345...xyz" in filtered

    def test_filter_multiple_keys_from_text(self) -> None:
        """Test filtering multiple keys from text."""
        text = "Keys: sk-key1234567890abc and sk-xyz9876543210def"
        keys = ["sk-key1234567890abc", "sk-xyz9876543210def"]
        
        filtered = SecureAPIKeyManager.filter_keys_from_text(text, keys)
        
        assert "sk-key1234567890abc" not in filtered
        assert "sk-xyz9876543210def" not in filtered
        assert "sk-key12345...abc" in filtered
        assert "sk-xyz98765...def" in filtered

    def test_get_env_var_name(self, manager: SecureAPIKeyManager) -> None:
        """Test getting environment variable name for a provider."""
        assert manager.get_env_var_name("gemini") == "GOOGLE_API_KEY"
        assert manager.get_env_var_name("anthropic") == "ANTHROPIC_API_KEY"
        assert manager.get_env_var_name("openai") == "OPENAI_API_KEY"
        assert manager.get_env_var_name("invalid") is None
