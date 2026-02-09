"""
Tests for A-Team Tool System.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from ateam.tools.manager import ToolManager
from ateam.tools.shell import ShellTool
from ateam.tools.file_tools import FileReadTool, FileWriteTool, FileListTool


class TestTools:
    """Test suite for ToolManager and built-in tools."""

    @pytest.fixture
    def tool_manager(self):
        return ToolManager()

    def test_parse_simple_call(self, tool_manager):
        text = 'Check this: <tool_call name="shell">ls -la</tool_call>'
        calls = tool_manager.parse_calls(text)
        assert len(calls) == 1
        assert calls[0]["name"] == "shell"
        assert calls[0]["body"] == "ls -la"
        assert calls[0]["args"] == {}

    def test_parse_attributed_call(self, tool_manager):
        text = '<tool_call name="write_file" path="test.py">print("hello")</tool_call>'
        calls = tool_manager.parse_calls(text)
        assert len(calls) == 1
        assert calls[0]["name"] == "write_file"
        assert calls[0]["args"]["path"] == "test.py"
        assert calls[0]["body"] == 'print("hello")'

    def test_parse_multiple_calls(self, tool_manager):
        text = """
        I will read then write.
        <tool_call name="read_file">old.txt</tool_call>
        <tool_call name="write_file" path="new.txt">content</tool_call>
        """
        calls = tool_manager.parse_calls(text)
        assert len(calls) == 2
        assert calls[0]["name"] == "read_file"
        assert calls[1]["name"] == "write_file"

    @pytest.mark.asyncio
    async def test_file_read_tool(self, tmp_path):
        test_file = tmp_path / "hello.txt"
        test_file.write_text("world")
        
        tool = FileReadTool()
        # Mocking validator to allow this path or just use absolute path
        with patch.object(tool.validator, "validate_file_path", return_value=test_file):
            result = await tool.execute(path="hello.txt")
            assert result == "world"

    @pytest.mark.asyncio
    async def test_file_write_tool(self, tmp_path):
        target_file = tmp_path / "out.txt"
        tool = FileWriteTool()
        
        with patch.object(tool.validator, "validate_file_path", return_value=target_file):
            result = await tool.execute(path="out.txt", content="new content")
            assert "Successfully" in result
            assert target_file.read_text() == "new content"

    @pytest.mark.asyncio
    async def test_tool_manager_execution(self, tool_manager):
        from unittest.mock import AsyncMock
        # Test routing and arg mapping in manager
        with patch.object(ShellTool, "execute", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = "ls result"
            call_info = {"name": "shell", "args": {}, "body": "ls"}
            result = await tool_manager.run_tool(call_info)
            assert result == "ls result"
            mock_exec.assert_called_once_with(command="ls")
            
        with patch.object(FileWriteTool, "execute", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = "wrote"
            call_info = {"name": "write_file", "args": {"path": "a.txt"}, "body": "content"}
            result = await tool_manager.run_tool(call_info)
            assert result == "wrote"
            mock_write.assert_called_once_with(path="a.txt", content="content")
