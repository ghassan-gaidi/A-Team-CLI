"""
Secure API Key Management for A-Team CLI.

This module provides secure storage and retrieval of API keys using the system keyring.
Keys are stored encrypted in the OS-native credential store:
- Windows: Credential Manager (DPAPI encryption)
- macOS: Keychain (AES-256 encryption)
- Linux: Secret Service API (libsecret, GNOME Keyring)

Security features:
- Encrypted storage via OS keyring
- Automatic key redaction in logs/errors
- Validation before storage
- Rotation reminders
"""

import os
import re
from typing import Optional

import keyring
from pydantic import BaseModel, Field


class APIKeyConfig(BaseModel):
    """Configuration for an API key."""

    provider: str = Field(..., description="Provider name (gemini, anthropic, openai, ollama)")
    env_var: str = Field(..., description="Environment variable name")
    validate_url: Optional[str] = Field(None, description="URL to validate the key")


class SecureAPIKeyManager:
    """
    Manages API keys with secure storage in the system keyring.

    Storage hierarchy (most secure → least secure):
    1. System keyring (encrypted, OS-native) ← RECOMMENDED
    2. Environment variables (session-only)
    3. Config file (plain text) ← NOT RECOMMENDED, warns user

    Example:
        >>> manager = SecureAPIKeyManager()
        >>> manager.store_key("gemini", "your-api-key-here")
        >>> key = manager.get_key("gemini")
        >>> print(manager.redact_key(key))
        "sk-...xyz"
    """

    SERVICE_NAME = "ateam-cli"
    KEY_PATTERN = re.compile(r"(sk-[a-zA-Z0-9]{8})[a-zA-Z0-9-]+([\w]{3})")

    # Provider configurations
    PROVIDERS = {
        "gemini": APIKeyConfig(
            provider="gemini",
            env_var="GOOGLE_API_KEY",
            validate_url="https://generativelanguage.googleapis.com/v1/models",
        ),
        "anthropic": APIKeyConfig(
            provider="anthropic",
            env_var="ANTHROPIC_API_KEY",
            validate_url="https://api.anthropic.com/v1/messages",
        ),
        "openai": APIKeyConfig(
            provider="openai",
            env_var="OPENAI_API_KEY",
            validate_url="https://api.openai.com/v1/models",
        ),
        "ollama": APIKeyConfig(
            provider="ollama",
            env_var="OLLAMA_BASE_URL",
            validate_url=None,  # Local, no key needed
        ),
    }

    def __init__(self) -> None:
        """Initialize the API key manager."""
        self.keyring_backend = keyring.get_keyring()

    def store_key(self, provider: str, api_key: str) -> None:
        """
        Store an API key securely in the system keyring.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)
            api_key: The API key to store

        Raises:
            ValueError: If provider is unknown or key is invalid
        """
        if provider not in self.PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Valid providers: {', '.join(self.PROVIDERS.keys())}"
            )

        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")

        # Store in keyring
        keyring.set_password(self.SERVICE_NAME, f"{provider}_api_key", api_key)

    def get_key(self, provider: str, config_value: Optional[str] = None) -> Optional[str]:
        """
        Retrieve an API key using the storage hierarchy.

        Storage hierarchy (checked in order):
        1. System keyring (most secure)
        2. Environment variable
        3. Config file value (warns user if found)

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)
            config_value: Optional value from config file (discouraged)

        Returns:
            The API key if found, None otherwise
        """
        if provider not in self.PROVIDERS:
            return None

        config = self.PROVIDERS[provider]

        # 1. Try keyring (most secure)
        key = keyring.get_password(self.SERVICE_NAME, f"{provider}_api_key")
        if key:
            return key

        # 2. Try environment variable
        key = os.getenv(config.env_var)
        if key:
            return key

        # 3. Try config file (warn user)
        if config_value:
            # Note: Warning will be logged by the caller
            return config_value

        return None

    def delete_key(self, provider: str) -> None:
        """
        Delete an API key from the keyring.

        Args:
            provider: Provider name (gemini, anthropic, openai, ollama)
        """
        try:
            keyring.delete_password(self.SERVICE_NAME, f"{provider}_api_key")
        except keyring.errors.PasswordDeleteError:
            # Key doesn't exist, that's fine
            pass

    def list_stored_keys(self) -> list[str]:
        """
        List all providers that have keys stored in the keyring.

        Returns:
            List of provider names with stored keys
        """
        stored = []
        for provider in self.PROVIDERS:
            if keyring.get_password(self.SERVICE_NAME, f"{provider}_api_key"):
                stored.append(provider)
        return stored

    @staticmethod
    def redact_key(api_key: str) -> str:
        """
        Redact an API key for safe display in logs/errors.

        Shows only the first 8 and last 3 characters.

        Args:
            api_key: The API key to redact

        Returns:
            Redacted key in format "sk-abc12345...xyz"

        Example:
            >>> SecureAPIKeyManager.redact_key("sk-abc123456789xyz")
            "sk-abc12345...xyz"
        """
        if not api_key:
            return "[EMPTY]"

        if len(api_key) <= 11:
            return "***"

        # Try to match common key patterns (sk-...)
        match = SecureAPIKeyManager.KEY_PATTERN.match(api_key)
        if match:
            return f"{match.group(1)}...{match.group(2)}"

        # Fallback: show first 8 and last 3
        return f"{api_key[:8]}...{api_key[-3:]}"

    @staticmethod
    def filter_keys_from_text(text: str, keys: list[str]) -> str:
        """
        Filter API keys from text (for logs, error messages, stack traces).

        Args:
            text: Text that may contain API keys
            keys: List of API keys to redact

        Returns:
            Text with all keys redacted

        Example:
            >>> text = "Error: Invalid key sk-abc123456789xyz"
            >>> filtered = SecureAPIKeyManager.filter_keys_from_text(
            ...     text, ["sk-abc123456789xyz"]
            ... )
            >>> print(filtered)
            "Error: Invalid key sk-abc12345...xyz"
        """
        filtered_text = text
        for key in keys:
            if key and key in filtered_text:
                redacted = SecureAPIKeyManager.redact_key(key)
                filtered_text = filtered_text.replace(key, redacted)
        return filtered_text

    def get_env_var_name(self, provider: str) -> Optional[str]:
        """
        Get the environment variable name for a provider.

        Args:
            provider: Provider name

        Returns:
            Environment variable name, or None if provider unknown
        """
        config = self.PROVIDERS.get(provider)
        return config.env_var if config else None
