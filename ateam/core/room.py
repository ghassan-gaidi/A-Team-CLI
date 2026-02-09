"""
Room Management for A-Team CLI.

This module manages conversation rooms - persistent workspaces where
multi-agent conversations take place with shared context and history.

Features:
- Create and join rooms
- List all rooms
- Room metadata (creation time, last active, message count)
- Room persistence across sessions
- Room validation and security
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from ateam.security.validation import InputValidator


class RoomMetadata(BaseModel):
    """Metadata for a conversation room."""

    name: str = Field(..., description="Room name")
    created_at: str = Field(..., description="ISO timestamp of creation")
    last_active: str = Field(..., description="ISO timestamp of last activity")
    message_count: int = Field(default=0, description="Total messages in room")
    description: Optional[str] = Field(None, description="Optional room description")

    def update_last_active(self) -> None:
        """Update the last active timestamp to now."""
        self.last_active = datetime.utcnow().isoformat()

    def increment_message_count(self) -> None:
        """Increment the message count."""
        self.message_count += 1


class RoomManager:
    """
    Manages conversation rooms for A-Team CLI.

    Rooms are stored in ~/.config/ateam/rooms/ with the following structure:
    - rooms/
      - my-project/
        - metadata.json    (room metadata)
        - history.db       (SQLite database with messages)

    Example:
        >>> manager = RoomManager()
        >>> manager.create_room("my-project")
        >>> manager.join_room("my-project")
        >>> rooms = manager.list_rooms()
        >>> print(rooms[0].name)
        "my-project"
    """

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        """
        Initialize the room manager.

        Args:
            base_dir: Optional base directory for rooms.
                     Defaults to ~/.config/ateam/rooms/
        """
        if base_dir is None:
            # Default to ~/.config/ateam/rooms/
            config_dir = Path.home() / ".config" / "ateam"
            self.base_dir = config_dir / "rooms"
        else:
            self.base_dir = Path(base_dir)

        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Input validator for security
        self.validator = InputValidator()

        # Currently active room
        self.current_room: Optional[str] = None

    def _get_room_dir(self, room_name: str) -> Path:
        """
        Get the directory path for a room.

        Args:
            room_name: Name of the room

        Returns:
            Path to the room directory
        """
        return self.base_dir / room_name

    def _get_metadata_path(self, room_name: str) -> Path:
        """
        Get the path to a room's metadata file.

        Args:
            room_name: Name of the room

        Returns:
            Path to metadata.json
        """
        return self._get_room_dir(room_name) / "metadata.json"

    def _load_metadata(self, room_name: str) -> RoomMetadata:
        """
        Load metadata for a room.

        Args:
            room_name: Name of the room

        Returns:
            RoomMetadata object

        Raises:
            FileNotFoundError: If room doesn't exist
        """
        metadata_path = self._get_metadata_path(room_name)

        if not metadata_path.exists():
            raise FileNotFoundError(f"Room '{room_name}' does not exist")

        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return RoomMetadata(**data)

    def _save_metadata(self, room_name: str, metadata: RoomMetadata) -> None:
        """
        Save metadata for a room.

        Args:
            room_name: Name of the room
            metadata: RoomMetadata to save
        """
        metadata_path = self._get_metadata_path(room_name)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata.model_dump(), f, indent=2)

    def room_exists(self, room_name: str) -> bool:
        """
        Check if a room exists.

        Args:
            room_name: Name of the room

        Returns:
            True if room exists, False otherwise
        """
        return self._get_room_dir(room_name).exists()

    def create_room(
        self, room_name: str, description: Optional[str] = None
    ) -> RoomMetadata:
        """
        Create a new conversation room.

        Args:
            room_name: Name of the room (alphanumeric, hyphens, underscores)
            description: Optional description of the room

        Returns:
            RoomMetadata for the created room

        Raises:
            ValueError: If room name is invalid or room already exists
        """
        # Validate room name
        validated = self.validator.validate_room_name(room_name)
        room_name = validated.name

        # Check if room already exists
        if self.room_exists(room_name):
            raise ValueError(f"Room '{room_name}' already exists")

        # Create room directory
        room_dir = self._get_room_dir(room_name)
        room_dir.mkdir(parents=True, exist_ok=True)

        # Create metadata
        now = datetime.utcnow().isoformat()
        metadata = RoomMetadata(
            name=room_name,
            created_at=now,
            last_active=now,
            message_count=0,
            description=description,
        )

        # Save metadata
        self._save_metadata(room_name, metadata)

        return metadata

    def join_room(self, room_name: str) -> RoomMetadata:
        """
        Join an existing room (or create if it doesn't exist).

        Args:
            room_name: Name of the room

        Returns:
            RoomMetadata for the room

        Raises:
            ValueError: If room name is invalid
        """
        # Validate room name
        validated = self.validator.validate_room_name(room_name)
        room_name = validated.name

        # Create room if it doesn't exist
        if not self.room_exists(room_name):
            metadata = self.create_room(room_name)
        else:
            metadata = self._load_metadata(room_name)
            # Update last active time
            metadata.update_last_active()
            self._save_metadata(room_name, metadata)

        # Set as current room
        self.current_room = room_name

        return metadata

    def leave_room(self) -> None:
        """Leave the current room."""
        self.current_room = None

    def get_current_room(self) -> Optional[str]:
        """
        Get the name of the currently active room.

        Returns:
            Room name if in a room, None otherwise
        """
        return self.current_room

    def list_rooms(self) -> list[RoomMetadata]:
        """
        List all available rooms.

        Returns:
            List of RoomMetadata objects, sorted by last active (newest first)
        """
        rooms = []

        # Iterate through room directories
        if not self.base_dir.exists():
            return rooms

        for room_dir in self.base_dir.iterdir():
            if room_dir.is_dir():
                metadata_path = room_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        metadata = RoomMetadata(**data)
                        rooms.append(metadata)
                    except (json.JSONDecodeError, ValueError):
                        # Skip corrupted metadata files
                        continue

        # Sort by last active (newest first)
        rooms.sort(key=lambda r: r.last_active, reverse=True)

        return rooms

    def delete_room(self, room_name: str) -> None:
        """
        Delete a room and all its data.

        Args:
            room_name: Name of the room to delete

        Raises:
            FileNotFoundError: If room doesn't exist
        """
        # Validate room name
        validated = self.validator.validate_room_name(room_name)
        room_name = validated.name

        if not self.room_exists(room_name):
            raise FileNotFoundError(f"Room '{room_name}' does not exist")

        # If this is the current room, leave it
        if self.current_room == room_name:
            self.leave_room()

        # Delete room directory and all contents
        room_dir = self._get_room_dir(room_name)
        import shutil

        shutil.rmtree(room_dir)

    def get_room_metadata(self, room_name: str) -> RoomMetadata:
        """
        Get metadata for a specific room.

        Args:
            room_name: Name of the room

        Returns:
            RoomMetadata object

        Raises:
            FileNotFoundError: If room doesn't exist
        """
        return self._load_metadata(room_name)

    def update_room_metadata(
        self, room_name: str, description: Optional[str] = None
    ) -> RoomMetadata:
        """
        Update metadata for a room.

        Args:
            room_name: Name of the room
            description: New description (optional)

        Returns:
            Updated RoomMetadata

        Raises:
            FileNotFoundError: If room doesn't exist
        """
        metadata = self._load_metadata(room_name)

        if description is not None:
            metadata.description = description

        metadata.update_last_active()
        self._save_metadata(room_name, metadata)

        return metadata

    def get_history(self, room_name: str) -> "HistoryManager":
        """
        Get the HistoryManager for a specific room.

        Args:
            room_name: Name of the room

        Returns:
            HistoryManager instance for the room

        Raises:
            FileNotFoundError: If room doesn't exist
        """
        from ateam.core.history import HistoryManager
        
        if not self.room_exists(room_name):
            raise FileNotFoundError(f"Room '{room_name}' does not exist")
            
        db_path = self._get_room_dir(room_name) / "history.db"
        return HistoryManager(db_path)

    def get_room_path(self, room_name: str) -> Path:
        """
        Get the filesystem path for a room.

        Args:
            room_name: Name of the room

        Returns:
            Path to the room directory

        Raises:
            FileNotFoundError: If room doesn't exist
        """
        if not self.room_exists(room_name):
            raise FileNotFoundError(f"Room '{room_name}' does not exist")

        return self._get_room_dir(room_name)
