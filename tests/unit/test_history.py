"""
Tests for HistoryManager.

Tests cover:
- Database initialization
- Adding messages
- Retrieving history with paging
- Retrieving last messages
- Searching messages
- Clearing history
"""

import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from ateam.core.history import HistoryManager, Message


class TestHistoryManager:
    """Test suite for HistoryManager."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        yield tmp_path
        if tmp_path.exists():
            tmp_path.unlink()

    @pytest.fixture
    def manager(self, temp_db_path):
        """Create a HistoryManager with temporary database."""
        return HistoryManager(temp_db_path)

    def test_init_creates_table(self, temp_db_path):
        """Test that initialization creates the messages table."""
        manager = HistoryManager(temp_db_path)
        assert temp_db_path.exists()
        
        # Verify table exists
        import sqlite3
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_add_message(self, manager: HistoryManager):
        """Test adding a message."""
        msg = manager.add_message(role="user", content="Hello, test!", agent_tag="User")
        
        assert msg.id is not None
        assert msg.role == "user"
        assert msg.content == "Hello, test!"
        assert msg.agent_tag == "User"
        assert isinstance(msg.timestamp, datetime)

    def test_get_history(self, manager: HistoryManager):
        """Test retrieving history."""
        manager.add_message("user", "Msg 1")
        manager.add_message("assistant", "Msg 2")
        
        history = manager.get_history()
        assert len(history) == 2
        assert history[0].content == "Msg 1"
        assert history[1].content == "Msg 2"

    def test_get_history_paging(self, manager: HistoryManager):
        """Test history paging with limit and offset."""
        for i in range(10):
            manager.add_message("user", f"Msg {i}")
            
        # First 5
        page1 = manager.get_history(limit=5)
        assert len(page1) == 5
        assert page1[0].content == "Msg 0"
        assert page1[4].content == "Msg 4"
        
        # Next 5
        page2 = manager.get_history(limit=5, offset=5)
        assert len(page2) == 5
        assert page2[0].content == "Msg 5"
        assert page2[4].content == "Msg 9"

    def test_get_last_messages(self, manager: HistoryManager):
        """Test retrieving the last N messages in ascending order."""
        for i in range(10):
            manager.add_message("user", f"Msg {i}")
            
        last_3 = manager.get_last_messages(count=3)
        assert len(last_3) == 3
        # Should be Msg 7, 8, 9 in that order
        assert last_3[0].content == "Msg 7"
        assert last_3[1].content == "Msg 8"
        assert last_3[2].content == "Msg 9"

    def test_clear_history(self, manager: HistoryManager):
        """Test clearing the history."""
        manager.add_message("user", "Kill me")
        assert manager.get_message_count() == 1
        
        manager.clear_history()
        assert manager.get_message_count() == 0

    def test_search_messages(self, manager: HistoryManager):
        """Test searching for specific content."""
        manager.add_message("user", "Find this needle")
        manager.add_message("user", "Just some hay")
        manager.add_message("user", "Another needle here")
        
        results = manager.search_messages("needle")
        assert len(results) == 2
        assert "needle" in results[0].content
        assert "needle" in results[1].content

    def test_message_to_dict(self):
        """Test converting Message to dictionary for API providers."""
        msg = Message(role="user", content="Test dict")
        d = msg.to_dict()
        assert d == {"role": "user", "content": "Test dict"}
