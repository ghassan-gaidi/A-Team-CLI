"""
History Management for A-Team CLI.

This module provides persistent storage for conversation history using SQLite.
Each room maintains its own independent history.db file.

Features:
- Thread-safe SQLite operations
- Automatic schema initialization
- Paging support for long conversations
- Support for agent tags and token tracking
- Context-aware retrieval
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Dict

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in the conversation history."""

    id: Optional[int] = Field(None, description="Database ID of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    role: str = Field(..., description="Role of the sender (user, assistant, system)")
    content: str = Field(..., description="The message content")
    agent_tag: Optional[str] = Field(None, description="Tag of the agent (e.g., Architect)")
    tokens: Optional[int] = Field(0, description="Estimated token count")

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for API providers."""
        return {
            "role": self.role,
            "content": self.content
        }


class HistoryManager:
    """
    Manages persistent conversation history using SQLite.

    Each room directory contains a history.db file. This manager handles 
    connections and SQL operations for a specific room.
    """

    def __init__(self, db_path: Path) -> None:
        """
        Initialize the history manager.

        Args:
            db_path: Path to the SQLite database file for the room.
        """
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        agent_tag TEXT,
                        tokens INTEGER DEFAULT 0
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)")
        finally:
            conn.close()

    def add_message(
        self, 
        role: str, 
        content: str, 
        agent_tag: Optional[str] = None, 
        tokens: int = 0
    ) -> Message:
        """
        Add a new message to the history.

        Args:
            role: Sender role (user, assistant, system)
            content: Message content
            agent_tag: Optional agent identification
            tokens: Token count for the message

        Returns:
            The created Message object
        """
        timestamp = datetime.utcnow().isoformat()
        
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO messages (timestamp, role, content, agent_tag, tokens) VALUES (?, ?, ?, ?, ?)",
                    (timestamp, role, content, agent_tag, tokens)
                )
                msg_id = cursor.lastrowid
        finally:
            conn.close()
            
        return Message(
            id=msg_id,
            timestamp=datetime.fromisoformat(timestamp),
            role=role,
            content=content,
            agent_tag=agent_tag,
            tokens=tokens
        )

    def get_history(self, limit: int = 50, offset: int = 0) -> List[Message]:
        """
        Retrieve messages from the history.

        Args:
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of Message objects, ordered by timestamp ascending
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM messages ORDER BY timestamp ASC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        return [
            Message(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                role=row["role"],
                content=row["content"],
                agent_tag=row["agent_tag"],
                tokens=row["tokens"]
            )
            for row in rows
        ]

    def get_last_messages(self, limit: int = 5) -> List[Message]:
        """
        Retrieve the most recent messages.

        Args:
            limit: Number of recent messages to return

        Returns:
            List of Message objects, ordered by timestamp ascending
        """
        conn = self._get_connection()
        try:
            # We sub-select to get them in ascending order for context windows
            cursor = conn.execute(
                "SELECT * FROM (SELECT * FROM messages ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
                (limit,)
            )
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        return [
            Message(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                role=row["role"],
                content=row["content"],
                agent_tag=row["agent_tag"],
                tokens=row["tokens"]
            )
            for row in rows
        ]

    def clear_history(self) -> None:
        """Delete all messages from the history."""
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM messages")
        finally:
            conn.close()

    def get_message_count(self) -> int:
        """Get the total number of messages in the room."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            count = cursor.fetchone()[0]
        finally:
            conn.close()
        return count

    def search_messages(self, query: str) -> List[Message]:
        """
        Search for messages containing the query string.

        Args:
            query: Text to search for

        Returns:
            List of matching Message objects
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM messages WHERE content LIKE ? ORDER BY timestamp DESC",
                (f"%{query}%",)
            )
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        return [
            Message(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                role=row["role"],
                content=row["content"],
                agent_tag=row["agent_tag"],
                tokens=row["tokens"]
            )
            for row in rows
        ]
