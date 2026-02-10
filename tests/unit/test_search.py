import os
import pytest
from pathlib import Path
from ateam.tools.search import SearchTool

@pytest.mark.asyncio
async def test_search_tool_basic(tmp_path):
    # Create some files in a temp directory
    tool = SearchTool()
    
    # We need to mock os.getcwd() or change dir because SearchTool uses os.getcwd()
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        (tmp_path / "file1.txt").write_text("Hello world", encoding="utf-8")
        (tmp_path / "file2.py").write_text("print('test search')", encoding="utf-8")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.md").write_text("Context is key", encoding="utf-8")
        
        # Test search
        result = await tool.execute("search")
        assert "file2.py" in result
        assert "test search" in result
        
        result = await tool.execute("Context")
        assert "file3.md" in result
        assert "Context is key" in result
        
        result = await tool.execute("nonexistent")
        assert "No results found" in result
        
    finally:
        os.chdir(original_cwd)

@pytest.mark.asyncio
async def test_search_tool_ignored(tmp_path):
    tool = SearchTool()
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "secret.txt").write_text("hidden", encoding="utf-8")
        (tmp_path / "normal.txt").write_text("visible", encoding="utf-8")
        
        result = await tool.execute("hidden")
        assert "No results found" in result
        
        result = await tool.execute("visible")
        assert "normal.txt" in result
        
    finally:
        os.chdir(original_cwd)
