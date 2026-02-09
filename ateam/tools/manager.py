"""
Orchestrates tool discovery and execution.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from ateam.tools.base import BaseTool
from ateam.tools.shell import ShellTool


class ToolManager:
    """
    Manages available tools and parses tool calls from text.
    """

    # Format: <tool_call name="tool_name" arg1="val1" ... /> or <tool_call name="tool_name">arg_content</tool_call>
    # We'll support a simple XML-like syntax for terminal reliability across different LLMs.
    TOOL_PATTERN = re.compile(r'<tool_call\s+name="([^"]+)"\s*>(.*?)</tool_call>', re.DOTALL)

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(ShellTool())

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def get_tool_descriptions(self) -> str:
        """Return a string describing all tools for the system prompt."""
        if not self.tools:
            return ""
        
        info = "Available Tools (Call them using <tool_call name='tool_name'>argument_content</tool_call>):\n"
        for name, tool in self.tools.items():
            info += f"- {name}: {tool.description}\n"
        return info

    def parse_calls(self, text: str) -> List[Tuple[str, str]]:
        """Extract tool names and their raw arguments from text."""
        return self.TOOL_PATTERN.findall(text)

    async def run_tool(self, name: str, arg: str) -> str:
        """Execute a tool by name."""
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        
        tool = self.tools[name]
        # For simplicity, we assume the content between tags is the primary argument
        # (usually 'command' for shell, 'path' for read_file, etc.)
        return await tool.execute(command=arg) # Fixed for shell for now
