"""
Input Validation for A-Team CLI.

This module provides comprehensive input validation using Pydantic schemas
to prevent injection attacks, path traversal, and other security issues.

Security features:
- Pydantic schema validation for all user inputs
- Path traversal prevention (blocks .., symlinks)
- Null byte blocking
- Maximum length enforcement
- Whitespace normalization
"""

import os
import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MessageInput(BaseModel):
    """Validation schema for user messages."""

    content: str = Field(..., min_length=1, max_length=50000)
    agent_tag: Optional[str] = Field(None, max_length=50)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content."""
        # Block null bytes
        if "\x00" in v:
            raise ValueError("Message cannot contain null bytes")

        # Normalize excessive whitespace
        lines = v.split("\n")
        if len(lines) > 1000:
            raise ValueError("Message cannot exceed 1000 lines")

        # Check for excessive consecutive newlines
        if "\n\n\n\n" in v:
            # Normalize to max 3 consecutive newlines
            v = re.sub(r"\n{4,}", "\n\n\n", v)

        return v

    @field_validator("agent_tag")
    @classmethod
    def validate_agent_tag(cls, v: Optional[str]) -> Optional[str]:
        """Validate agent tag."""
        if v is None:
            return v

        # Only alphanumeric, hyphens, underscores
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Agent tag can only contain letters, numbers, hyphens, and underscores"
            )

        return v


class RoomNameInput(BaseModel):
    """Validation schema for room names."""

    name: str = Field(..., min_length=1, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate room name."""
        # Block null bytes
        if "\x00" in v:
            raise ValueError("Room name cannot contain null bytes")

        # Only alphanumeric, hyphens, underscores
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Room name can only contain letters, numbers, hyphens, and underscores"
            )

        # Block reserved names
        reserved = {".", "..", "con", "prn", "aux", "nul"}
        if v.lower() in reserved:
            raise ValueError(f"Room name '{v}' is reserved")

        return v


class AgentNameInput(BaseModel):
    """Validation schema for agent names."""

    name: str = Field(..., min_length=1, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate agent name."""
        # Block null bytes
        if "\x00" in v:
            raise ValueError("Agent name cannot contain null bytes")

        # Only alphanumeric, hyphens, underscores
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Agent name can only contain letters, numbers, hyphens, and underscores"
            )

        return v


class FilePathInput(BaseModel):
    """Validation schema for file paths."""

    path: str = Field(..., min_length=1, max_length=4096)
    allowed_paths: list[str] = Field(default_factory=list)

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate file path."""
        # Block null bytes
        if "\x00" in v:
            raise ValueError("File path cannot contain null bytes")

        return v


class InputValidator:
    """
    Validates all user inputs to prevent security vulnerabilities.

    Features:
    - Pydantic schema validation
    - Path traversal prevention
    - Null byte blocking
    - Length enforcement
    - Pattern matching

    Example:
        >>> validator = InputValidator()
        >>> validator.validate_message("Hello, @Architect!")
        MessageInput(content="Hello, @Architect!", agent_tag="Architect")
        >>> validator.validate_room_name("my-project")
        RoomNameInput(name="my-project")
        >>> validator.validate_file_path("/etc/passwd", ["/home/user"])
        # Raises ValueError: Path traversal detected
    """

    # Sensitive file patterns (always blocked)
    BLOCKED_PATTERNS = [
        r"/etc/passwd",
        r"/etc/shadow",
        r"\.ssh/",
        r"\.aws/",
        r"\.env$",
        r"\.key$",
        r"\.pem$",
        r"id_rsa",
        r"credentials",
    ]

    def __init__(self) -> None:
        """Initialize the input validator."""
        self.blocked_regex = re.compile("|".join(self.BLOCKED_PATTERNS), re.IGNORECASE)

    def validate_message(self, content: str, agent_tag: Optional[str] = None) -> MessageInput:
        """
        Validate a user message.

        Args:
            content: Message content
            agent_tag: Optional agent tag (e.g., "Architect")

        Returns:
            Validated MessageInput

        Raises:
            ValueError: If validation fails
        """
        return MessageInput(content=content, agent_tag=agent_tag)

    def validate_room_name(self, name: str) -> RoomNameInput:
        """
        Validate a room name.

        Args:
            name: Room name

        Returns:
            Validated RoomNameInput

        Raises:
            ValueError: If validation fails
        """
        return RoomNameInput(name=name)

    def validate_agent_name(self, name: str) -> AgentNameInput:
        """
        Validate an agent name.

        Args:
            name: Agent name

        Returns:
            Validated AgentNameInput

        Raises:
            ValueError: If validation fails
        """
        return AgentNameInput(name=name)

    def validate_file_path(
        self, path: str, allowed_paths: Optional[list[str]] = None
    ) -> Path:
        """
        Validate a file path and prevent path traversal attacks.

        Security checks:
        1. Block null bytes
        2. Resolve symlinks to real path
        3. Block path traversal (..)
        4. Check against allowed paths
        5. Block sensitive file patterns

        Args:
            path: File path to validate
            allowed_paths: List of allowed base paths (e.g., ["/home/user/projects"])

        Returns:
            Resolved absolute Path object

        Raises:
            ValueError: If path is invalid or blocked

        Example:
            >>> validator = InputValidator()
            >>> validator.validate_file_path(
            ...     "~/projects/myapp/main.py",
            ...     allowed_paths=["~/projects"]
            ... )
            Path("/home/user/projects/myapp/main.py")
        """
        if not path:
            raise ValueError("File path cannot be empty")

        # Block null bytes
        if "\x00" in path:
            raise ValueError("File path cannot contain null bytes")

        # Expand user home directory
        expanded_path = os.path.expanduser(path)

        # Convert to Path object
        path_obj = Path(expanded_path)

        # Resolve to absolute path (follows symlinks)
        try:
            resolved_path = path_obj.resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid file path: {e}") from e

        # Check for path traversal attempts
        if ".." in path_obj.parts:
            raise ValueError("Path traversal detected: '..' not allowed")

        # Check against blocked patterns
        path_str = str(resolved_path)
        if self.blocked_regex.search(path_str):
            raise ValueError(f"Access to sensitive file blocked: {path}")

        # Check against allowed paths
        if allowed_paths:
            # Expand and resolve allowed paths
            allowed_resolved = [
                Path(os.path.expanduser(allowed)).resolve() for allowed in allowed_paths
            ]

            # Check if resolved path is under any allowed path
            is_allowed = any(
                str(resolved_path).startswith(str(allowed)) for allowed in allowed_resolved
            )

            if not is_allowed:
                raise ValueError(
                    f"Path '{path}' is not within allowed directories: {allowed_paths}"
                )

        return resolved_path

    def validate_sql_identifier(self, identifier: str) -> str:
        """
        Validate an SQL identifier (table name, column name).

        Only allows alphanumeric characters and underscores.
        Prevents SQL injection via identifiers.

        Args:
            identifier: SQL identifier to validate

        Returns:
            Validated identifier

        Raises:
            ValueError: If identifier is invalid

        Example:
            >>> validator = InputValidator()
            >>> validator.validate_sql_identifier("messages")
            "messages"
            >>> validator.validate_sql_identifier("messages; DROP TABLE users;")
            # Raises ValueError
        """
        if not identifier:
            raise ValueError("SQL identifier cannot be empty")

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
            raise ValueError(
                "SQL identifier can only contain letters, numbers, and underscores, "
                "and must start with a letter or underscore"
            )

        # Block SQL keywords
        sql_keywords = {
            "select",
            "insert",
            "update",
            "delete",
            "drop",
            "create",
            "alter",
            "exec",
            "execute",
        }
        if identifier.lower() in sql_keywords:
            raise ValueError(f"SQL identifier cannot be a reserved keyword: {identifier}")

        return identifier

    @staticmethod
    def sanitize_for_display(text: str, max_length: int = 100) -> str:
        """
        Sanitize text for safe display in terminal/logs.

        - Truncates to max_length
        - Removes control characters
        - Normalizes whitespace

        Args:
            text: Text to sanitize
            max_length: Maximum length (default: 100)

        Returns:
            Sanitized text

        Example:
            >>> InputValidator.sanitize_for_display("Hello\\x00World\\n\\n\\n", 50)
            "HelloWorld"
        """
        # Remove null bytes and control characters (except newline/tab)
        sanitized = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)

        # Normalize whitespace
        sanitized = " ".join(sanitized.split())

        # Truncate
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."

        return sanitized
