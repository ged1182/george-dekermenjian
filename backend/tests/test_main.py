"""Tests for FastAPI endpoints."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import BrainLogAdapter, get_cors_origins


# ============================================================================
# BrainLogAdapter Tests
# ============================================================================


class TestBrainLogAdapterExtractUserMessage:
    """Tests for BrainLogAdapter._extract_user_message() method."""

    def test_extracts_last_user_message(self, mock_env_vars: None):
        """Should extract text from the last user message."""
        # Create mock messages with proper structure
        text_part = Mock()
        text_part.text = "Hello, tell me about yourself"

        user_message = Mock()
        user_message.role = "user"
        user_message.parts = [text_part]

        assistant_message = Mock()
        assistant_message.role = "assistant"
        assistant_message.parts = []

        run_input = Mock()
        run_input.messages = [user_message, assistant_message]

        # Create adapter with mocked dependencies
        adapter = BrainLogAdapter.__new__(BrainLogAdapter)
        adapter.run_input = run_input

        result = adapter._extract_user_message()
        assert result == "Hello, tell me about yourself"

    def test_returns_none_for_no_user_messages(self, mock_env_vars: None):
        """Should return None when no user messages exist."""
        assistant_message = Mock()
        assistant_message.role = "assistant"
        assistant_message.parts = []

        run_input = Mock()
        run_input.messages = [assistant_message]

        adapter = BrainLogAdapter.__new__(BrainLogAdapter)
        adapter.run_input = run_input

        result = adapter._extract_user_message()
        assert result is None

    def test_returns_none_for_empty_messages(self, mock_env_vars: None):
        """Should return None when messages list is empty."""
        run_input = Mock()
        run_input.messages = []

        adapter = BrainLogAdapter.__new__(BrainLogAdapter)
        adapter.run_input = run_input

        result = adapter._extract_user_message()
        assert result is None

    def test_returns_none_when_user_message_has_no_text_part(self, mock_env_vars: None):
        """Should return None when user message has no text part."""
        # Part without text attribute
        non_text_part = Mock(spec=[])  # No text attribute

        user_message = Mock()
        user_message.role = "user"
        user_message.parts = [non_text_part]

        run_input = Mock()
        run_input.messages = [user_message]

        adapter = BrainLogAdapter.__new__(BrainLogAdapter)
        adapter.run_input = run_input

        result = adapter._extract_user_message()
        assert result is None

    def test_handles_exception_gracefully(self, mock_env_vars: None):
        """Should return None when an exception occurs."""
        run_input = Mock()
        run_input.messages = Mock(side_effect=Exception("Error"))

        adapter = BrainLogAdapter.__new__(BrainLogAdapter)
        adapter.run_input = run_input

        result = adapter._extract_user_message()
        assert result is None

    def test_extracts_from_multiple_user_messages(self, mock_env_vars: None):
        """Should extract from the LAST user message (most recent)."""
        text_part1 = Mock()
        text_part1.text = "First message"

        text_part2 = Mock()
        text_part2.text = "Second message"

        user_message1 = Mock()
        user_message1.role = "user"
        user_message1.parts = [text_part1]

        assistant_message = Mock()
        assistant_message.role = "assistant"
        assistant_message.parts = []

        user_message2 = Mock()
        user_message2.role = "user"
        user_message2.parts = [text_part2]

        run_input = Mock()
        run_input.messages = [user_message1, assistant_message, user_message2]

        adapter = BrainLogAdapter.__new__(BrainLogAdapter)
        adapter.run_input = run_input

        result = adapter._extract_user_message()
        assert result == "Second message"


class TestBrainLogAdapterBuildEventStream:
    """Tests for BrainLogAdapter.build_event_stream() method."""

    def test_builds_event_stream_with_collector(self, mock_env_vars: None):
        """Should create BrainLogEventStream and set collector."""
        from app.brain_log_stream import BrainLogEventStream

        text_part = Mock()
        text_part.text = "Test message"

        user_message = Mock()
        user_message.role = "user"
        user_message.parts = [text_part]

        run_input = Mock()
        run_input.messages = [user_message]

        adapter = BrainLogAdapter.__new__(BrainLogAdapter)
        adapter.run_input = run_input
        adapter.accept = "*/*"
        adapter._collector = None

        with patch("app.main.set_brain_log_collector") as mock_set_collector:
            stream = adapter.build_event_stream()

            assert isinstance(stream, BrainLogEventStream)
            assert adapter._collector is not None
            mock_set_collector.assert_called_once_with(adapter._collector)

    def test_reuses_existing_collector(self, mock_env_vars: None):
        """Should reuse existing collector if already set."""
        from app.schemas.brain_log import BrainLogCollector

        run_input = Mock()
        run_input.messages = []

        existing_collector = BrainLogCollector()

        adapter = BrainLogAdapter.__new__(BrainLogAdapter)
        adapter.run_input = run_input
        adapter.accept = "*/*"
        adapter._collector = existing_collector

        with patch("app.main.set_brain_log_collector") as mock_set_collector:
            stream = adapter.build_event_stream()

            # Should not create a new collector
            assert adapter._collector is existing_collector
            mock_set_collector.assert_not_called()


# ============================================================================
# CORS Tests
# ============================================================================


class TestCorsOrigins:
    """Tests for get_cors_origins() function."""

    def test_filters_wildcard_origins(self, mock_env_vars: None):
        """Should filter out origins containing wildcards."""
        with patch("app.main.settings") as mock_settings:
            mock_settings.cors_origins = [
                "http://localhost:3000",
                "https://*.vercel.app",
                "https://example.com",
            ]
            result = get_cors_origins()
            assert result == ["http://localhost:3000", "https://example.com"]

    def test_returns_all_non_wildcard_origins(self, mock_env_vars: None):
        """Should return all origins when none contain wildcards."""
        with patch("app.main.settings") as mock_settings:
            mock_settings.cors_origins = [
                "http://localhost:3000",
                "https://example.com",
            ]
            result = get_cors_origins()
            assert result == ["http://localhost:3000", "https://example.com"]


# ============================================================================
# Endpoint Tests
# ============================================================================


def test_root_endpoint(test_client: TestClient):
    """Test the root endpoint returns API info."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Glass Box Portfolio"


def test_health_endpoint(test_client: TestClient):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data


def test_profile_endpoint(test_client: TestClient):
    """Test the profile endpoint returns all profile data."""
    response = test_client.get("/profile")
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert "experiences" in data
    assert "skills" in data
    assert "projects" in data
    assert "education" in data
    # Check profile has expected fields
    assert "name" in data["profile"]
    assert "title" in data["profile"]
    # Check experiences is a list
    assert isinstance(data["experiences"], list)
    assert len(data["experiences"]) > 0


def test_cors_headers(test_client: TestClient):
    """Test that CORS headers are set correctly."""
    response = test_client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # CORS preflight should return 200
    assert response.status_code == 200


# ============================================================================
# Chat Endpoint Tests
# ============================================================================


@pytest.mark.asyncio
async def test_chat_endpoint_dispatches_request(mock_env_vars: None):
    """Test that /chat endpoint calls BrainLogAdapter.dispatch_request."""
    from unittest.mock import AsyncMock

    import httpx

    from app.main import app

    # Mock the dispatch_request to avoid actual agent execution
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.body = b"data: test\n"

    with patch.object(
        BrainLogAdapter, "dispatch_request", new_callable=AsyncMock
    ) as mock_dispatch:
        mock_dispatch.return_value = mock_response

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/chat",
                json={
                    "trigger": "submit-message",
                    "id": "test-id",
                    "messages": [
                        {
                            "id": "msg-1",
                            "role": "user",
                            "parts": [{"type": "text", "text": "Hello"}],
                        }
                    ],
                },
            )

            # Verify dispatch_request was called
            mock_dispatch.assert_called_once()


@pytest.mark.asyncio
async def test_chat_endpoint_cleans_up_collector(mock_env_vars: None):
    """Test that /chat endpoint cleans up the brain log collector after request."""
    from unittest.mock import AsyncMock

    import httpx

    from app.main import app

    mock_response = MagicMock()
    mock_response.status_code = 200

    with (
        patch.object(
            BrainLogAdapter, "dispatch_request", new_callable=AsyncMock
        ) as mock_dispatch,
        patch("app.main.set_brain_log_collector") as mock_set_collector,
    ):
        mock_dispatch.return_value = mock_response

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/chat",
                json={
                    "trigger": "submit-message",
                    "id": "test-id",
                    "messages": [
                        {
                            "id": "msg-1",
                            "role": "user",
                            "parts": [{"type": "text", "text": "Hello"}],
                        }
                    ],
                },
            )

            # Verify collector was cleaned up (set to None)
            mock_set_collector.assert_called_with(None)
