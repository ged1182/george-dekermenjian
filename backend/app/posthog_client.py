"""PostHog analytics client for the Glass Box Portfolio backend.

This module provides a singleton PostHog client that integrates with the frontend
PostHog instance via correlation IDs (distinct_id). This allows unified user tracking
across both frontend and backend events.

Correlation ID Flow:
1. Frontend PostHog generates a distinct_id for each user
2. Frontend sends this ID in the X-PostHog-Distinct-ID header
3. Backend reads the header and uses it for all PostHog events
4. This creates a unified view of user activity across both systems
"""

from contextvars import ContextVar
from typing import Any

import posthog
from posthog import Posthog

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)

# Context variable to store the current request's distinct_id
_distinct_id_var: ContextVar[str | None] = ContextVar(
    "posthog_distinct_id", default=None
)

# Singleton client instance
_client: Posthog | None = None


def init_posthog() -> Posthog | None:
    """Initialize the PostHog client.

    Should be called once at application startup.
    Returns None if PostHog is not configured (missing API key).
    """
    global _client
    settings = get_settings()

    if not settings.posthog_api_key:
        logger.info("PostHog API key not configured, analytics disabled")
        return None

    _client = Posthog(
        project_api_key=settings.posthog_api_key,
        host=settings.posthog_host,
        debug=settings.debug,
        on_error=_on_posthog_error,
    )

    # Disable automatic capture - we'll capture events explicitly
    posthog.disabled = False

    logger.info("PostHog initialized with host: %s", settings.posthog_host)
    return _client


def shutdown_posthog() -> None:
    """Shutdown the PostHog client.

    Should be called at application shutdown to flush any pending events.
    """
    global _client
    if _client:
        _client.flush()
        _client.shutdown()
        _client = None
        logger.info("PostHog client shutdown complete")


def _on_posthog_error(error: Exception) -> None:
    """Error handler for PostHog client."""
    logger.error("PostHog error: %s", error)


def set_distinct_id(distinct_id: str | None) -> None:
    """Set the distinct_id for the current request context.

    This should be called by middleware when a request comes in with
    the X-PostHog-Distinct-ID header.
    """
    _distinct_id_var.set(distinct_id)


def get_distinct_id() -> str | None:
    """Get the distinct_id for the current request context."""
    return _distinct_id_var.get()


def capture(
    event: str,
    properties: dict[str, Any] | None = None,
    distinct_id: str | None = None,
) -> None:
    """Capture a PostHog event.

    Args:
        event: The event name (e.g., "chat_message_sent", "tool_invoked")
        properties: Optional dictionary of event properties
        distinct_id: Optional distinct_id. If not provided, uses the
                    context variable set by middleware.
    """
    if not _client:
        return

    # Use provided distinct_id, fall back to context, then to anonymous
    effective_id = distinct_id or get_distinct_id() or "anonymous_backend"

    _client.capture(
        distinct_id=effective_id,
        event=event,
        properties=properties or {},
    )


def set_user_properties(
    distinct_id: str,
    properties: dict[str, Any] | None = None,
) -> None:
    """Set user properties (person properties in PostHog).

    Args:
        distinct_id: The user's distinct_id
        properties: Optional user properties to set
    """
    if not _client:
        return

    _client.set(
        distinct_id=distinct_id,
        properties=properties or {},
    )
