"""Tests for codebase oracle tools."""

import os
from unittest.mock import patch

import pytest

from app.tools.codebase import (
    find_symbol,
    get_file_content,
    find_references,
    _get_language,
    _should_skip_path,
)
from pathlib import Path


@pytest.fixture
def mock_codebase_root():
    """Set codebase root to the project root for tests."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    with patch.dict(os.environ, {"CODEBASE_ROOT": project_root}):
        # Clear settings cache to pick up new env var
        from app.config import get_settings

        get_settings.cache_clear()
        yield project_root
        get_settings.cache_clear()


def test_get_language_python():
    """Test language detection for Python files."""
    assert _get_language("app/main.py") == "python"
    assert _get_language("test.py") == "python"


def test_get_language_typescript():
    """Test language detection for TypeScript files."""
    assert _get_language("component.tsx") == "typescript"
    assert _get_language("utils.ts") == "typescript"


def test_get_language_javascript():
    """Test language detection for JavaScript files."""
    assert _get_language("script.js") == "javascript"
    assert _get_language("component.jsx") == "javascript"


def test_get_language_unknown():
    """Test language detection for unknown extensions."""
    assert _get_language("file.xyz") == "text"
    assert _get_language("README") == "text"


def test_should_skip_path():
    """Test that certain paths are skipped."""
    assert _should_skip_path(Path("project/.git/config")) is True
    assert _should_skip_path(Path("project/node_modules/package/index.js")) is True
    assert _should_skip_path(Path("project/__pycache__/module.pyc")) is True
    assert _should_skip_path(Path("project/.venv/lib/python")) is True
    assert _should_skip_path(Path("project/src/main.py")) is False


def test_find_symbol_python_function(mock_codebase_root):
    """Test finding a Python function definition."""
    result = find_symbol("get_settings")
    assert result.symbol == "get_settings"
    # Should find it in config.py
    assert any("config.py" in loc.file for loc in result.locations)


def test_find_symbol_not_found(mock_codebase_root):
    """Test finding a symbol that doesn't exist."""
    result = find_symbol("this_symbol_does_not_exist_xyz123")
    assert result.total_found == 0
    assert len(result.locations) == 0


def test_get_file_content_success(mock_codebase_root):
    """Test reading a file that exists."""
    result = get_file_content("backend/app/config.py")
    assert result.file_path == "backend/app/config.py"
    assert result.total_lines > 0
    assert result.language == "python"
    assert "Settings" in result.content


def test_get_file_content_not_found(mock_codebase_root):
    """Test reading a file that doesn't exist."""
    result = get_file_content("nonexistent/file.py")
    assert "Error" in result.content or "not found" in result.content.lower()


def test_get_file_content_with_line_range(mock_codebase_root):
    """Test reading specific lines from a file."""
    result = get_file_content("backend/app/config.py", start_line=1, end_line=10)
    assert result.start_line == 1
    assert result.end_line <= 10


def test_get_file_content_path_traversal_blocked(mock_codebase_root):
    """Test that path traversal is blocked."""
    result = get_file_content("../../../etc/passwd")
    assert "Error" in result.content or result.total_lines == 0


def test_find_references(mock_codebase_root):
    """Test finding references to a symbol."""
    result = find_references("Settings")
    assert result.symbol == "Settings"
    # Should find references in config.py and possibly main.py
    assert result.total_found > 0


def test_find_references_not_found(mock_codebase_root):
    """Test finding references to a symbol that doesn't exist."""
    # Use a variable so the literal string doesn't appear in the source
    search_term = "".join(["zzz", "never", "exists", "anywhere", "999"])
    result = find_references(search_term)
    assert result.total_found == 0
