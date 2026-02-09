"""
Shell Tool for A-Team CLI.
"""

import asyncio
import subprocess
from typing import Any, Dict
from ateam.tools.base import BaseTool


class ShellTool(BaseTool):
    """
    Executes a shell command on the local system.
    """

    def __init__(self):
        super().__init__(
            name="shell",
            description="Execute a shell command. Use for filesystem operations, git, or running scripts."
        )

    async def execute(self, command: str) -> str:
        """
        Run the command and return output.
        """
        try:
            # We use asyncio.create_subprocess_shell for non-blocking execution
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            result = stdout.decode().strip()
            error = stderr.decode().strip()
            
            if error:
                return f"Output:\n{result}\nErrors:\n{error}"
            return result or "Command executed successfully (no output)."
        except Exception as e:
            return f"Error executing command: {str(e)}"
