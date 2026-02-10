import pytest
from pathlib import Path
from ateam.core.indexer import WorkspaceIndexer

def test_indexer_python(tmp_path):
    # Create a dummy python file
    py_file = tmp_path / "logic.py"
    py_file.write_text("""
class Calculator:
    def add(self, a, b):
        return a + b
    def sub(self, a, b):
        return a - b

def helper():
    pass
""", encoding="utf-8")

    indexer = WorkspaceIndexer(root_dir=tmp_path)
    indexer.refresh()
    
    assert "logic.py" in indexer.index
    items = indexer.index["logic.py"]
    assert "Class: Calculator (Methods: add, sub)" in items
    assert "Function: helper" in items

def test_indexer_markdown(tmp_path):
    md_file = tmp_path / "README.md"
    md_file.write_text("""
# Project Alpha
## Installation
Follow the steps.
""", encoding="utf-8")

    indexer = WorkspaceIndexer(root_dir=tmp_path)
    indexer.refresh()
    
    assert "README.md" in indexer.index
    items = indexer.index["README.md"]
    assert "# Project Alpha" in items
    assert "## Installation" in items

def test_indexer_summary(tmp_path):
    indexer = WorkspaceIndexer(root_dir=tmp_path)
    (tmp_path / "test.txt").write_text("# Test Header", encoding="utf-8")
    indexer.refresh()
    
    summary = indexer.get_summary()
    assert "test.txt" in summary
    assert "# Test Header" in summary
