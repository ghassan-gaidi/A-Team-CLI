import pytest
from pathlib import Path
from datetime import datetime
from ateam.utils.exporter import ManifestExporter
from ateam.core.history import Message

def test_manifest_exporter_basic(tmp_path):
    # Setup
    room_name = "test_room"
    messages = [
        Message(role="user", content="Hello", timestamp=datetime.now()),
        Message(role="assistant", content="Hi there!", agent_tag="Coder", timestamp=datetime.now()),
        Message(role="system", content="Tool 'shell' executed", timestamp=datetime.now())
    ]
    
    # Run
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        filepath = ManifestExporter.export(room_name, messages)
        path = Path(filepath)
        
        # Assert
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Mission Manifest" in content
        assert "test_room" in content
        assert "Coder" in content
        assert "Hello" in content
    finally:
        os.chdir(original_cwd)

def test_manifest_exporter_empty(tmp_path):
    # Setup
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        filepath = ManifestExporter.export("empty", [])
        path = Path(filepath)
        
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Mission Manifest" in content
        assert "empty" in content
    finally:
        os.chdir(original_cwd)
