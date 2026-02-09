"""
Orchestrates tool discovery and execution.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from ateam.tools.base import BaseTool
from ateam.tools.shell import ShellTool
from ateam.tools.file_tools import FileReadTool, FileWriteTool, FileListTool


class ToolManager:
    """
    Manages available tools and parses tool calls from text.
    """

    # Matches <tool_call name="..." attr="...">body</tool_call>
    # Group 1: Attributes string
    # Group 2: Body content
    TOOL_PATTERN = re.compile(r'<tool_call\s+([^>]+)>(.*?)</tool_call>', re.DOTALL)
    # Matches key="value"
    ATTR_PATTERN = re.compile(r'([a-zA-Z_]+)="([^"]*)"')

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(ShellTool())
        self.register(FileReadTool())
        self.register(FileWriteTool())
        self.register(FileListTool())

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def get_tool_descriptions(self) -> str:
        """Return a string describing all tools for the system prompt."""
        if not self.tools:
            return ""
        
        info = "Available Tools:\n"
        for name, tool in self.tools.items():
            info += f"- {name}: {tool.description}\n"
        
        info += "\nHow to call tools:\n"
        info += "1. Simple arg: <tool_call name=\"read_file\">path/to/file</tool_call>\n"
        info += "2. Named arg: <tool_call name=\"write_file\" path=\"test.txt\">Hello world</tool_call>\n"
        info += "3. Shell: <tool_call name=\"shell\">ls -la</tool_call>\n"
        return info

    def parse_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls and their arguments.
        Returns a list of dicts: {"name": str, "args": dict, "body": str}
        """
        calls = []
        for attr_str, body in self.TOOL_PATTERN.findall(text):
            attrs = dict(self.ATTR_PATTERN.findall(attr_str))
            if "name" not in attrs:
                continue
            
            name = attrs.pop("name")
            calls.append({
                "name": name,
                "args": attrs,
                "body": body.strip()
            })
        return calls

    async def run_tool(self, call_info: Dict[str, Any]) -> str:
        """Execute a tool based on call info."""
        name = call_info["name"]
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        
        tool = self.tools[name]
        kwargs = call_info["args"]
        body = call_info["body"]

        # Strategy for arguments:
        # If it's a 'read_file' or 'shell' or 'list_files', the body is the main arg.
        if name in ("shell", "read_file", "list_files") and "path" not in kwargs and "command" not in kwargs:
            if name == "shell":
                kwargs["command"] = body
            else:
                kwargs["path"] = body
        elif name == "write_file":
            # body is content
            kwargs["content"] = body
            
        return await tool.execute(**kwargs)
