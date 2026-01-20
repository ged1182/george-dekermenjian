"""Tests for FastAPI endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import get_cors_origins


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
