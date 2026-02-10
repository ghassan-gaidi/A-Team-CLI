"""
Lightweight Workspace Indexing for A-Team CLI.
"""

import os
import ast
from pathlib import Path
from typing import Dict, List, Optional


class WorkspaceIndexer:
    """
    Scans the workspace to build a map of available code context.
    """

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.index: Dict[str, List[str]] = {} # path -> list of snippets/signatures

    def refresh(self):
        """Re-scans the workspace."""
        self.index = {}
        ignored_dirs = {".git", "__pycache__", ".venv", ".pytest_cache", "node_modules", ".context"}
        
        for path in self.root_dir.rglob("*"):
            if any(ignored in path.parts for ignored in ignored_dirs):
                continue
            
            if not path.is_file():
                continue

            if path.suffix == ".py":
                self._index_python(path)
            elif path.suffix in (".md", ".txt"):
                self._index_text(path)

    def _index_python(self, path: Path):
        """Extracts function and class signatures from Python files."""
        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            signatures = []
            
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    signatures.append(f"Function: {node.name}")
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    signatures.append(f"Class: {node.name} (Methods: {', '.join(methods)})")
            
            if signatures:
                self.index[str(path.relative_to(self.root_dir))] = signatures
        except Exception:
            pass

    def _index_text(self, path: Path):
        """Extracts headers or short summaries from text files."""
        try:
            content = path.read_text(encoding="utf-8")
            lines = content.splitlines()
            headers = [line for line in lines if line.strip().startswith("#")][:5]
            if headers:
                self.index[str(path.relative_to(self.root_dir))] = headers
        except Exception:
            pass

    def get_summary(self) -> str:
        """Returns a string representation of the workspace overview."""
        if not self.index:
            return "No workspace context indexed."
        
        summary = "Workspace Context Map:\n"
        for path, items in self.index.items():
            summary += f"- {path}:\n"
            for item in items:
                summary += f"  * {item}\n"
        return summary

    def find_relevant_files(self, query: str) -> List[str]:
        """Simple keyword search for relevant files."""
        query = query.lower()
        relevant = []
        for path, items in self.index.items():
            if query in path.lower() or any(query in item.lower() for item in items):
                relevant.append(path)
        return relevant
