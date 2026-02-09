"""
Test basic package installation and imports.
"""

import ateam


def test_version_exists() -> None:
    """Test that version is defined."""
    assert hasattr(ateam, "__version__")
    assert isinstance(ateam.__version__, str)
    assert ateam.__version__ == "0.1.0"


def test_author_exists() -> None:
    """Test that author is defined."""
    assert hasattr(ateam, "__author__")
    assert isinstance(ateam.__author__, str)


def test_package_imports() -> None:
    """Test that package can be imported without errors."""
    import ateam.cli.main
    import ateam.core
    import ateam.providers
    import ateam.security
    import ateam.mcp
    import ateam.utils
    
    # Verify main CLI app exists
    assert hasattr(ateam.cli.main, "app")
    assert hasattr(ateam.cli.main, "main")
