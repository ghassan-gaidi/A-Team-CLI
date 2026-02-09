"""
Tests for RoomManager.

Tests cover:
- Room creation
- Room joining (create if not exists)
- Room listing
- Room deletion
- Metadata management
- Room validation
"""

import tempfile
from pathlib import Path

import pytest

from ateam.core.room import RoomManager, RoomMetadata


class TestRoomManager:
    """Test suite for RoomManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_dir):
        """Create a RoomManager with temporary directory."""
        return RoomManager(base_dir=temp_dir)

    # ========================================================================
    # Room Creation Tests
    # ========================================================================

    def test_create_room_valid(self, manager: RoomManager) -> None:
        """Test creating a room with a valid name."""
        metadata = manager.create_room("my-project")

        assert metadata.name == "my-project"
        assert metadata.message_count == 0
        assert metadata.created_at is not None
        assert metadata.last_active is not None

    def test_create_room_with_description(self, manager: RoomManager) -> None:
        """Test creating a room with a description."""
        metadata = manager.create_room("my-project", description="Test project")

        assert metadata.name == "my-project"
        assert metadata.description == "Test project"

    def test_create_room_invalid_name(self, manager: RoomManager) -> None:
        """Test that invalid room names are rejected."""
        with pytest.raises(ValueError, match="can only contain"):
            manager.create_room("invalid room!")

    def test_create_room_already_exists(self, manager: RoomManager) -> None:
        """Test that creating a duplicate room raises an error."""
        manager.create_room("my-project")

        with pytest.raises(ValueError, match="already exists"):
            manager.create_room("my-project")

    def test_create_room_creates_directory(self, manager: RoomManager, temp_dir: Path) -> None:
        """Test that creating a room creates the directory structure."""
        manager.create_room("my-project")

        room_dir = temp_dir / "my-project"
        assert room_dir.exists()
        assert room_dir.is_dir()

        metadata_file = room_dir / "metadata.json"
        assert metadata_file.exists()

    # ========================================================================
    # Room Existence Tests
    # ========================================================================

    def test_room_exists_true(self, manager: RoomManager) -> None:
        """Test room_exists returns True for existing room."""
        manager.create_room("my-project")

        assert manager.room_exists("my-project") is True

    def test_room_exists_false(self, manager: RoomManager) -> None:
        """Test room_exists returns False for non-existent room."""
        assert manager.room_exists("nonexistent") is False

    # ========================================================================
    # Room Joining Tests
    # ========================================================================

    def test_join_existing_room(self, manager: RoomManager) -> None:
        """Test joining an existing room."""
        manager.create_room("my-project")
        metadata = manager.join_room("my-project")

        assert metadata.name == "my-project"
        assert manager.get_current_room() == "my-project"

    def test_join_creates_room_if_not_exists(self, manager: RoomManager) -> None:
        """Test that joining a non-existent room creates it."""
        assert not manager.room_exists("new-room")

        metadata = manager.join_room("new-room")

        assert metadata.name == "new-room"
        assert manager.room_exists("new-room")
        assert manager.get_current_room() == "new-room"

    def test_join_updates_last_active(self, manager: RoomManager) -> None:
        """Test that joining a room updates last_active timestamp."""
        metadata1 = manager.create_room("my-project")
        original_last_active = metadata1.last_active

        import time
        time.sleep(0.1)  # Small delay to ensure timestamp changes

        metadata2 = manager.join_room("my-project")

        assert metadata2.last_active > original_last_active

    # ========================================================================
    # Room Leaving Tests
    # ========================================================================

    def test_leave_room(self, manager: RoomManager) -> None:
        """Test leaving a room."""
        manager.join_room("my-project")
        assert manager.get_current_room() == "my-project"

        manager.leave_room()
        assert manager.get_current_room() is None

    # ========================================================================
    # Room Listing Tests
    # ========================================================================

    def test_list_rooms_empty(self, manager: RoomManager) -> None:
        """Test listing rooms when none exist."""
        rooms = manager.list_rooms()

        assert rooms == []

    def test_list_rooms_single(self, manager: RoomManager) -> None:
        """Test listing a single room."""
        manager.create_room("my-project")
        rooms = manager.list_rooms()

        assert len(rooms) == 1
        assert rooms[0].name == "my-project"

    def test_list_rooms_multiple(self, manager: RoomManager) -> None:
        """Test listing multiple rooms."""
        manager.create_room("project-1")
        manager.create_room("project-2")
        manager.create_room("project-3")

        rooms = manager.list_rooms()

        assert len(rooms) == 3
        room_names = {r.name for r in rooms}
        assert room_names == {"project-1", "project-2", "project-3"}

    def test_list_rooms_sorted_by_last_active(self, manager: RoomManager) -> None:
        """Test that rooms are sorted by last active (newest first)."""
        import time

        manager.create_room("old-room")
        time.sleep(0.1)
        manager.create_room("new-room")

        rooms = manager.list_rooms()

        # Newest room should be first
        assert rooms[0].name == "new-room"
        assert rooms[1].name == "old-room"

    # ========================================================================
    # Room Deletion Tests
    # ========================================================================

    def test_delete_room(self, manager: RoomManager) -> None:
        """Test deleting a room."""
        manager.create_room("my-project")
        assert manager.room_exists("my-project")

        manager.delete_room("my-project")

        assert not manager.room_exists("my-project")

    def test_delete_nonexistent_room(self, manager: RoomManager) -> None:
        """Test that deleting a non-existent room raises an error."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            manager.delete_room("nonexistent")

    def test_delete_current_room(self, manager: RoomManager) -> None:
        """Test that deleting the current room leaves it."""
        manager.join_room("my-project")
        assert manager.get_current_room() == "my-project"

        manager.delete_room("my-project")

        assert manager.get_current_room() is None

    # ========================================================================
    # Metadata Tests
    # ========================================================================

    def test_get_room_metadata(self, manager: RoomManager) -> None:
        """Test getting metadata for a room."""
        manager.create_room("my-project", description="Test project")

        metadata = manager.get_room_metadata("my-project")

        assert metadata.name == "my-project"
        assert metadata.description == "Test project"

    def test_get_metadata_nonexistent_room(self, manager: RoomManager) -> None:
        """Test that getting metadata for non-existent room raises error."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            manager.get_room_metadata("nonexistent")

    def test_update_room_metadata(self, manager: RoomManager) -> None:
        """Test updating room metadata."""
        manager.create_room("my-project", description="Old description")

        updated = manager.update_room_metadata("my-project", description="New description")

        assert updated.description == "New description"

        # Verify it was saved
        metadata = manager.get_room_metadata("my-project")
        assert metadata.description == "New description"

    def test_metadata_update_last_active(self) -> None:
        """Test that RoomMetadata.update_last_active() works."""
        import time

        metadata = RoomMetadata(
            name="test", created_at="2024-01-01T00:00:00", last_active="2024-01-01T00:00:00"
        )

        original_last_active = metadata.last_active
        time.sleep(0.1)

        metadata.update_last_active()

        assert metadata.last_active > original_last_active

    def test_metadata_increment_message_count(self) -> None:
        """Test that RoomMetadata.increment_message_count() works."""
        metadata = RoomMetadata(
            name="test", created_at="2024-01-01T00:00:00", last_active="2024-01-01T00:00:00"
        )

        assert metadata.message_count == 0

        metadata.increment_message_count()
        assert metadata.message_count == 1

        metadata.increment_message_count()
        assert metadata.message_count == 2

    # ========================================================================
    # Path Tests
    # ========================================================================

    def test_get_room_path(self, manager: RoomManager, temp_dir: Path) -> None:
        """Test getting the filesystem path for a room."""
        manager.create_room("my-project")

        path = manager.get_room_path("my-project")

        assert path == temp_dir / "my-project"
        assert path.exists()

    def test_get_room_path_nonexistent(self, manager: RoomManager) -> None:
        """Test that getting path for non-existent room raises error."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            manager.get_room_path("nonexistent")


if __name__ == "__main__":
    # Run tests manually
    import sys

    temp_dir = Path(tempfile.mkdtemp())
    manager = RoomManager(base_dir=temp_dir)

    print("Testing RoomManager...")

    # Test create
    metadata = manager.create_room("test-room", description="Test room")
    print(f"✓ Created room: {metadata.name}")

    # Test join
    manager.join_room("test-room")
    print(f"✓ Joined room: {manager.get_current_room()}")

    # Test list
    rooms = manager.list_rooms()
    print(f"✓ Listed {len(rooms)} room(s)")

    # Test delete
    manager.delete_room("test-room")
    print("✓ Deleted room")

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir)

    print("\n✅ All manual tests passed!")
