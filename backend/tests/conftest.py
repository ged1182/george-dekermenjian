"""Shared pytest fixtures for the Glass Box Portfolio backend."""

import os
from collections.abc import AsyncGenerator, AsyncIterator, Generator
from typing import TypeVar
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from pydantic_ai.models.test import TestModel


# Set environment variables BEFORE any app imports
# This is needed because pydantic-ai's Google provider checks for GOOGLE_API_KEY at import time
os.environ.setdefault("GOOGLE_API_KEY", "test-api-key-for-tests")
os.environ.setdefault("GEMINI_API_KEY", "test-api-key-for-tests")


# Note: Custom markers are registered in pyproject.toml [tool.pytest.ini_options]


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio as the async backend."""
    return "asyncio"


@pytest.fixture
def test_model() -> TestModel:
    """Provide a TestModel instance for agent testing."""
    return TestModel()


@pytest.fixture
def mock_env_vars() -> Generator[None, None, None]:
    """Mock environment variables for testing."""
    env_vars = {
        "GEMINI_API_KEY": "test-api-key",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "CODEBASE_ROOT": os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def test_client(mock_env_vars: None) -> Generator[TestClient, None, None]:
    """Provide a synchronous test client for FastAPI."""
    from app.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client(mock_env_vars: None) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client for FastAPI."""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def override_agent_model(test_model: TestModel) -> Generator[None, None, None]:
    """Override the portfolio agent with TestModel."""
    from app.agent import portfolio_agent

    with portfolio_agent.override(model=test_model):
        yield


# ============================================================================
# Async Test Helpers
# ============================================================================

T = TypeVar("T")


async def async_iter(items: list[T]) -> AsyncIterator[T]:
    """Convert a list to an async iterator for testing async generators."""
    for item in items:
        yield item


# ============================================================================
# Codebase and Architecture Tool Fixtures
# ============================================================================


@pytest.fixture
def project_root() -> str:
    """Get the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def mock_codebase_settings(project_root: str) -> Generator[str, None, None]:
    """Mock codebase settings for architecture/semantic tests."""
    from app.config import get_settings

    with patch.dict(os.environ, {"CODEBASE_ROOT": project_root}):
        get_settings.cache_clear()
        yield project_root
        get_settings.cache_clear()


@pytest.fixture
def mock_lsp_disabled() -> Generator[None, None, None]:
    """Disable LSP for tests that don't need it."""
    from app.config import get_settings

    with patch.dict(os.environ, {"LSP_ENABLED": "false"}):
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()


@pytest.fixture
def mock_lsp_manager_fixture() -> Generator[tuple[MagicMock, MagicMock], None, None]:
    """Provide a mocked LSP manager for testing semantic tools."""
    with patch("app.tools.semantic.get_lsp_manager") as mock_get:
        manager = MagicMock()
        manager.get_client.return_value = None  # Default: no LSP available
        mock_get.return_value = manager
        yield mock_get, manager
