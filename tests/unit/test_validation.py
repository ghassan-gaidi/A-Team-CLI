"""
Tests for InputValidator.

Tests cover:
- Message validation
- Room name validation
- Agent name validation
- File path validation and path traversal prevention
- SQL identifier validation
- Text sanitization
"""

import tempfile
from pathlib import Path

import pytest

from ateam.security.validation import InputValidator, MessageInput, RoomNameInput, AgentNameInput


class TestInputValidator:
    """Test suite for InputValidator."""

    @pytest.fixture
    def validator(self) -> InputValidator:
        """Create an InputValidator instance."""
        return InputValidator()

    # ========================================================================
    # Message Validation Tests
    # ========================================================================

    def test_validate_message_valid(self, validator: InputValidator) -> None:
        """Test validating a valid message."""
        result = validator.validate_message("Hello, world!", "Architect")
        
        assert isinstance(result, MessageInput)
        assert result.content == "Hello, world!"
        assert result.agent_tag == "Architect"

    def test_validate_message_no_tag(self, validator: InputValidator) -> None:
        """Test validating a message without an agent tag."""
        result = validator.validate_message("Hello, world!")
        
        assert result.content == "Hello, world!"
        assert result.agent_tag is None

    def test_validate_message_null_bytes(self, validator: InputValidator) -> None:
        """Test that null bytes in messages are rejected."""
        with pytest.raises(ValueError, match="null bytes"):
            validator.validate_message("Hello\x00World")

    def test_validate_message_too_long(self, validator: InputValidator) -> None:
        """Test that messages exceeding max length are rejected."""
        long_message = "x" * 50001
        
        with pytest.raises(ValueError):
            validator.validate_message(long_message)

    def test_validate_message_excessive_newlines(self, validator: InputValidator) -> None:
        """Test that excessive consecutive newlines are normalized."""
        message = "Line 1\n\n\n\n\n\nLine 2"
        result = validator.validate_message(message)
        
        # Should normalize to max 3 consecutive newlines
        assert "\n\n\n\n" not in result.content

    def test_validate_message_invalid_agent_tag(self, validator: InputValidator) -> None:
        """Test that invalid agent tags are rejected."""
        with pytest.raises(ValueError, match="can only contain"):
            validator.validate_message("Hello", "Invalid Tag!")

    # ========================================================================
    # Room Name Validation Tests
    # ========================================================================

    def test_validate_room_name_valid(self, validator: InputValidator) -> None:
        """Test validating a valid room name."""
        result = validator.validate_room_name("my-project")
        
        assert isinstance(result, RoomNameInput)
        assert result.name == "my-project"

    def test_validate_room_name_alphanumeric(self, validator: InputValidator) -> None:
        """Test room names with alphanumeric characters."""
        result = validator.validate_room_name("project123")
        assert result.name == "project123"

    def test_validate_room_name_with_underscore(self, validator: InputValidator) -> None:
        """Test room names with underscores."""
        result = validator.validate_room_name("my_project")
        assert result.name == "my_project"

    def test_validate_room_name_invalid_chars(self, validator: InputValidator) -> None:
        """Test that room names with invalid characters are rejected."""
        with pytest.raises(ValueError, match="can only contain"):
            validator.validate_room_name("my project!")

    def test_validate_room_name_reserved(self, validator: InputValidator) -> None:
        """Test that reserved room names are rejected."""
        with pytest.raises(ValueError, match="reserved"):
            validator.validate_room_name(".")
        
        with pytest.raises(ValueError, match="reserved"):
            validator.validate_room_name("..")

    def test_validate_room_name_null_bytes(self, validator: InputValidator) -> None:
        """Test that null bytes in room names are rejected."""
        with pytest.raises(ValueError, match="null bytes"):
            validator.validate_room_name("room\x00name")

    def test_validate_room_name_too_long(self, validator: InputValidator) -> None:
        """Test that room names exceeding max length are rejected."""
        long_name = "x" * 51
        
        with pytest.raises(ValueError):
            validator.validate_room_name(long_name)

    # ========================================================================
    # Agent Name Validation Tests
    # ========================================================================

    def test_validate_agent_name_valid(self, validator: InputValidator) -> None:
        """Test validating a valid agent name."""
        result = validator.validate_agent_name("Architect")
        
        assert isinstance(result, AgentNameInput)
        assert result.name == "Architect"

    def test_validate_agent_name_invalid_chars(self, validator: InputValidator) -> None:
        """Test that agent names with invalid characters are rejected."""
        with pytest.raises(ValueError, match="can only contain"):
            validator.validate_agent_name("Agent Name!")

    # ========================================================================
    # File Path Validation Tests
    # ========================================================================

    def test_validate_file_path_valid(self, validator: InputValidator) -> None:
        """Test validating a valid file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.touch()
            
            result = validator.validate_file_path(str(test_file), [tmpdir])
            
            assert isinstance(result, Path)
            assert result.is_absolute()

    def test_validate_file_path_traversal_blocked(self, validator: InputValidator) -> None:
        """Test that path traversal attempts are blocked."""
        with pytest.raises(ValueError, match="Path traversal"):
            validator.validate_file_path("../etc/passwd")

    def test_validate_file_path_null_bytes(self, validator: InputValidator) -> None:
        """Test that null bytes in paths are rejected."""
        with pytest.raises(ValueError, match="null bytes"):
            validator.validate_file_path("/path/to\x00/file")

    def test_validate_file_path_sensitive_blocked(self, validator: InputValidator) -> None:
        """Test that sensitive file patterns are blocked."""
        with pytest.raises(ValueError, match="sensitive file"):
            validator.validate_file_path("/etc/passwd")
        
        with pytest.raises(ValueError, match="sensitive file"):
            validator.validate_file_path("/home/user/.ssh/id_rsa")

    def test_validate_file_path_outside_allowed(self, validator: InputValidator) -> None:
        """Test that paths outside allowed directories are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="not within allowed"):
                validator.validate_file_path("/etc/hosts", [tmpdir])

    def test_validate_file_path_home_expansion(self, validator: InputValidator) -> None:
        """Test that ~ is expanded to home directory."""
        result = validator.validate_file_path("~/test.txt")
        
        assert "~" not in str(result)
        assert result.is_absolute()

    def test_validate_file_path_empty(self, validator: InputValidator) -> None:
        """Test that empty paths are rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validator.validate_file_path("")

    # ========================================================================
    # SQL Identifier Validation Tests
    # ========================================================================

    def test_validate_sql_identifier_valid(self, validator: InputValidator) -> None:
        """Test validating a valid SQL identifier."""
        result = validator.validate_sql_identifier("messages")
        assert result == "messages"

    def test_validate_sql_identifier_with_underscore(self, validator: InputValidator) -> None:
        """Test SQL identifiers with underscores."""
        result = validator.validate_sql_identifier("user_messages")
        assert result == "user_messages"

    def test_validate_sql_identifier_starts_with_underscore(
        self, validator: InputValidator
    ) -> None:
        """Test SQL identifiers starting with underscore."""
        result = validator.validate_sql_identifier("_private")
        assert result == "_private"

    def test_validate_sql_identifier_invalid_chars(self, validator: InputValidator) -> None:
        """Test that SQL identifiers with invalid characters are rejected."""
        with pytest.raises(ValueError, match="can only contain"):
            validator.validate_sql_identifier("table-name")
        
        with pytest.raises(ValueError, match="can only contain"):
            validator.validate_sql_identifier("table name")

    def test_validate_sql_identifier_sql_injection(self, validator: InputValidator) -> None:
        """Test that SQL injection attempts are blocked."""
        with pytest.raises(ValueError, match="can only contain"):
            validator.validate_sql_identifier("messages; DROP TABLE users;")

    def test_validate_sql_identifier_reserved_keyword(self, validator: InputValidator) -> None:
        """Test that SQL reserved keywords are rejected."""
        with pytest.raises(ValueError, match="reserved keyword"):
            validator.validate_sql_identifier("select")
        
        with pytest.raises(ValueError, match="reserved keyword"):
            validator.validate_sql_identifier("DROP")

    def test_validate_sql_identifier_empty(self, validator: InputValidator) -> None:
        """Test that empty SQL identifiers are rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validator.validate_sql_identifier("")

    # ========================================================================
    # Text Sanitization Tests
    # ========================================================================

    def test_sanitize_for_display_normal(self) -> None:
        """Test sanitizing normal text."""
        result = InputValidator.sanitize_for_display("Hello, world!")
        assert result == "Hello, world!"

    def test_sanitize_for_display_control_chars(self) -> None:
        """Test that control characters are removed."""
        result = InputValidator.sanitize_for_display("Hello\x00\x01World")
        assert result == "HelloWorld"

    def test_sanitize_for_display_whitespace(self) -> None:
        """Test that whitespace is normalized."""
        result = InputValidator.sanitize_for_display("Hello    \n\n  World")
        assert result == "Hello World"

    def test_sanitize_for_display_truncate(self) -> None:
        """Test that long text is truncated."""
        long_text = "x" * 200
        result = InputValidator.sanitize_for_display(long_text, max_length=50)
        
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_sanitize_for_display_no_truncate(self) -> None:
        """Test that short text is not truncated."""
        short_text = "Hello"
        result = InputValidator.sanitize_for_display(short_text, max_length=50)
        
        assert result == "Hello"
        assert not result.endswith("...")
