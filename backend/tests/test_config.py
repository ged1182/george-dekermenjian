"""Tests for configuration settings."""

import os
from unittest.mock import patch

import pytest

from app.config import Settings, get_settings


def test_settings_defaults():
    """Test that settings have sensible defaults."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False):
        settings = Settings()
        assert settings.app_name == "Glass Box Portfolio"
        assert settings.app_version == "0.1.0"
        assert settings.debug is False
        assert settings.model_name == "google-gla:gemini-2.0-flash"
        assert settings.max_file_lines == 500


def test_settings_cors_origins():
    """Test CORS origins include localhost."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False):
        settings = Settings()
        assert "http://localhost:3000" in settings.cors_origins


def test_settings_codebase_root_default():
    """Test codebase_root defaults to current working directory."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False):
        settings = Settings()
        # Should default to cwd, not a hardcoded path
        assert settings.codebase_root == os.getcwd()


def test_settings_codebase_root_from_env():
    """Test codebase_root can be set from environment."""
    with patch.dict(
        os.environ,
        {"GEMINI_API_KEY": "test-key", "CODEBASE_ROOT": "/custom/path"},
        clear=False,
    ):
        settings = Settings()
        assert settings.codebase_root == "/custom/path"


def test_get_settings_cached():
    """Test that get_settings returns a cached instance."""
    # Clear the cache first
    get_settings.cache_clear()
    settings1 = get_settings()
    settings2 = get_settings()
    # Should be the same cached instance
    assert settings1 is settings2
