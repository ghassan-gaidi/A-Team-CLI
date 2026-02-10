"""
Plugin/MCP Manager for A-Team CLI.

This module handles dynamic loading of custom tools from the mcp directory.
"""

import importlib.util
import os
from pathlib import Path
from typing import List, Type
from ateam.tools.base import BaseTool


class PluginManager:
    """
    Loads and manages dynamic tool plugins (MCP-style).
    """

    def __init__(self, mcp_dir: str = "ateam/mcp"):
        self.mcp_dir = Path(mcp_dir)
        self.tools: List[BaseTool] = []

    def load_plugins(self) -> List[BaseTool]:
        """
        Walks the mcp directory and loads any class inheriting from BaseTool.
        """
        if not self.mcp_dir.exists():
            return []

        for file_path in self.mcp_dir.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            # Load module dynamically
            module_name = f"ateam.mcp.{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    
                    # Find and instantiate classes that inherit from BaseTool
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseTool) and 
                            attr is not BaseTool):
                            try:
                                tool_instance = attr()
                                self.tools.append(tool_instance)
                            except Exception as e:
                                print(f"Error instantiating tool {attr_name}: {e}")
                except Exception as e:
                    print(f"Error loading plugin {file_path}: {e}")

        return self.tools
