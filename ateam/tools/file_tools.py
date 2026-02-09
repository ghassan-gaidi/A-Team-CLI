"""
File handling tools for A-Team CLI.
"""

import os
from pathlib import Path
from typing import Any, Dict
from ateam.tools.base import BaseTool
from ateam.security.validation import InputValidator


class FileReadTool(BaseTool):
    """Reads the contents of a file."""
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read the contents of a file. Provide the path as the tool argument."
        )
        self.validator = InputValidator()

    async def execute(self, path: str, **kwargs) -> str:
        try:
            # Validate path (allow current directory by default for now or project root)
            # In a real app, we'd pass allowed_paths from config
            safe_path = self.validator.validate_file_path(path)
            
            if not safe_path.exists():
                return f"Error: File '{path}' does not exist."
            if not safe_path.is_file():
                return f"Error: '{path}' is a directory, not a file."
                
            return safe_path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file: {str(e)}"


class FileWriteTool(BaseTool):
    """Writes content to a file."""
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a file. Provide 'path' and the content via tag body."
        )
        self.validator = InputValidator()

    async def execute(self, path: str, content: str, **kwargs) -> str:
        try:
            safe_path = self.validator.validate_file_path(path)
            
            # Ensure parent directory exists
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            
            safe_path.write_text(content, encoding="utf-8")
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"


class FileListTool(BaseTool):
    """Lists files in a directory."""
    def __init__(self):
        super().__init__(
            name="list_files",
            description="List files in a directory. Provide the path as the tool argument."
        )
        self.validator = InputValidator()

    async def execute(self, path: str = ".", **kwargs) -> str:
        try:
            # Empty path defaults to current
            if not path:
                path = "."
                
            safe_path = self.validator.validate_file_path(path)
            
            if not safe_path.exists():
                return f"Error: Directory '{path}' does not exist."
            if not safe_path.is_dir():
                return f"Error: '{path}' is not a directory."
            
            files = []
            for item in safe_path.iterdir():
                suffix = "/" if item.is_dir() else ""
                files.append(f"{item.name}{suffix}")
            
            return "\n".join(sorted(files)) if files else "Directory is empty."
        except Exception as e:
            return f"Error listing directory: {str(e)}"
