"""
Search tools for A-Team CLI.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple
from ateam.tools.base import BaseTool
from ateam.security.validation import InputValidator


class SearchTool(BaseTool):
    """Searches for a keyword or pattern across the workspace."""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="Search for a keyword or regex in the workspace. Argument is the query string."
        )
        self.validator = InputValidator()
        self.ignored_dirs = {".git", "__pycache__", ".venv", ".pytest_cache", "node_modules", ".context"}
        self.ignored_exts = {".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin", ".lock"}

    async def execute(self, query: str, **kwargs) -> str:
        """
        Search for query in the current workspace.
        """
        try:
            root = Path(os.getcwd())
            results: List[str] = []
            
            # Simple keyword search for now
            # In the future, this could be upgraded to use embeddings or ripgrep
            
            count = 0
            max_results = 20
            
            for path in root.rglob("*"):
                if count >= max_results:
                    results.append("\n... (more results found, please refine your search)")
                    break
                    
                # Skip ignored directories
                if any(ignored in path.parts for ignored in self.ignored_dirs):
                    continue
                    
                # Skip directories and non-text files
                if not path.is_file() or path.suffix in self.ignored_exts:
                    continue
                
                try:
                    # Validate path (though rglob should be safe relative to root)
                    self.validator.validate_file_path(str(path), allowed_paths=[os.getcwd()])
                except ValueError:
                    continue

                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    if query.lower() in content.lower():
                        # Find lines with context
                        lines = content.splitlines()
                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                rel_path = path.relative_to(root)
                                results.append(f"{rel_path}:{i+1}: {line.strip()}")
                                count += 1
                                if count >= max_results:
                                    break
                except Exception:
                    continue

            if not results:
                return f"No results found for '{query}'."
            
            return "\n".join(results)

        except Exception as e:
            return f"Error during search: {str(e)}"
