"""
Base classes for A-Team Tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """
    Abstract base class for all A-Team tools.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """
        Execute the tool with given arguments.
        
        Returns:
        A string representation of the result.
        """
        pass

    def get_schema(self) -> Dict[str, Any]:
        """
        Return a JSON schema or description for the LLM.
        """
        return {
            "name": self.name,
            "description": self.description,
        }
