"""Glass Box Portfolio Backend - FastAPI Application.

This is the main entry point for the Glass Box Portfolio backend API.
It provides:
- Health check endpoint for Cloud Run
- CORS configuration for cross-origin requests from the frontend
- POST /chat endpoint for agentic interactions with Brain Log streaming
"""

import json
import time
from contextlib import asynccontextmanager
from typing import Any

import tokenledger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response, StreamingResponse

from app.config import get_settings
from app.agent import portfolio_agent
from app.tools.experience import get_full_profile, ProfileData
from app.schemas.brain_log import BrainLogCollector, set_brain_log_collector
from app.posthog_client import (
    init_posthog,
    shutdown_posthog,
    set_distinct_id,
    capture,
)
from app.logging_config import setup_logging, get_logger

# Initialize logging before anything else
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events.

    Startup: Initialize any resources (e.g., model connections)
    Shutdown: Clean up resources
    """
    # Startup
    startup_time = time.time()
    app.state.startup_time = startup_time
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Using model: %s", settings.model_name)

    # Initialize TokenLedger for LLM cost tracking
    if settings.tokenledger_enabled and settings.database_url:
        tokenledger.configure(
            database_url=settings.database_url,
            app_name="glass-box-portfolio",
            environment=settings.tokenledger_environment,
            async_mode=True,
            schema_name="public",  # Use public schema (auto-creates tables)
        )
        tokenledger.patch_google()
        logger.info("TokenLedger initialized for cost tracking")
    elif settings.tokenledger_enabled:
        logger.warning("TokenLedger enabled but DATABASE_URL not set - skipping")

    # Initialize PostHog
    init_posthog()

    yield

    # Shutdown
    shutdown_posthog()
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-grade demonstration of explainable, agentic systems.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


def get_cors_origins() -> list[str]:
    """Get CORS origins, filtering out wildcard patterns.

    FastAPI's CORS middleware handles wildcards via allow_origin_regex,
    so we filter them out of the origins list.
    """
    return [origin for origin in settings.cors_origins if "*" not in origin]


# CORS Configuration
# Required for frontend (Vercel) to communicate with backend (Cloud Run)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    # Only allow preview deployments from the george-dekermenjian-web project
    allow_origin_regex=r"https://george-dekermenjian-web-[a-z0-9]+-[a-z0-9-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def posthog_correlation_middleware(request: Request, call_next):
    """Extract PostHog distinct_id from headers for correlation.

    The frontend sends the PostHog distinct_id in the X-PostHog-Distinct-ID header.
    This allows us to correlate backend events with frontend events for the same user.
    """
    distinct_id = request.headers.get("X-PostHog-Distinct-ID")
    set_distinct_id(distinct_id)

    response = await call_next(request)
    return response


@app.get("/health")
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for Cloud Run and container orchestration.

    Returns:
        JSON with status and optional metadata for observability.
    """
    # Calculate uptime if available
    uptime_seconds = None
    if hasattr(request.app.state, "startup_time"):
        uptime_seconds = round(time.time() - request.app.state.startup_time, 2)

    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.app_version,
            "uptime_seconds": uptime_seconds,
        }
    )


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "profile": "/profile",
        "chat": "/chat (POST)",
    }


@app.get("/profile")
async def profile() -> ProfileData:
    """Profile endpoint returning complete profile information.

    Returns professional experience, skills, projects, and education data
    for the profile page.
    """
    return get_full_profile()


def _extract_user_message(messages: list[dict[str, Any]]) -> str:
    """Extract the last user message from a list of messages."""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            # Handle string content
            if isinstance(content, str):
                return content
            # Handle array of parts (Vercel AI SDK format)
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            return part.get("text", "")
                        # Direct text in content array
                        if "text" in part:
                            return part.get("text", "")
                # Join all text parts
                texts = [p.get("text", "") for p in content if isinstance(p, dict)]
                return " ".join(filter(None, texts))
            return str(content)
    return ""


def _format_data_chunk(data: dict[str, Any]) -> str:
    """Format a data part chunk in Vercel AI SDK v5 SSE format.

    AI SDK v5 uses Server-Sent Events format. Data parts should be sent as:
    data: {"type":"data-brainlog","data":{...}}

    The onData callback receives objects with custom type patterns (data-*).
    """
    wrapper = {"type": "data-brainlog", "data": data}
    return f"data: {json.dumps(wrapper)}\n\n"


class _CachedBodyRequest(Request):
    """Request wrapper that caches and replays the body."""

    def __init__(self, scope: dict[str, Any], body: bytes):
        super().__init__(scope)
        self._cached_body = body

    async def body(self) -> bytes:
        return self._cached_body


@app.post("/chat")
async def chat(request: Request) -> Response:
    """Streaming chat endpoint with Brain Log support.

    This endpoint wraps the standard VercelAIAdapter to add Brain Log
    streaming for the Glass Box mode. Brain Log entries are emitted as
    data annotations in the Vercel AI Data Stream Protocol.
    """
    # Import here to avoid circular imports
    from pydantic_ai.ui.vercel_ai import VercelAIAdapter

    # Read and cache the request body
    body_bytes = await request.body()
    body = json.loads(body_bytes)
    messages = body.get("messages", [])
    user_message = _extract_user_message(messages)

    # Extract user ID for cost attribution
    distinct_id = request.headers.get("X-PostHog-Distinct-ID")

    # Create brain log collector for this request
    collector = BrainLogCollector()
    collector.add_input_entry(user_message)
    set_brain_log_collector(collector)

    # Track chat message received
    capture(
        "chat_message_sent",
        {
            "message_length": len(user_message),
            "message_count": len(messages),
        },
    )

    # Create a new request with the cached body for VercelAIAdapter
    cached_request = _CachedBodyRequest(dict(request.scope), body_bytes)

    # Set TokenLedger attribution context for cost tracking
    # Using persistent=True because streaming responses are consumed after
    # the context manager exits. Context stays active until clear_attribution().
    tokenledger.attribution(
        user_id=distinct_id,
        feature="chat",
        page="/chat",
        persistent=True,
    ).__enter__()

    # Get the streaming response from VercelAIAdapter
    adapter_response = await VercelAIAdapter.dispatch_request(
        cached_request, agent=portfolio_agent
    )

    # Check if we got a StreamingResponse (normal case) or plain Response (error case)
    if not hasattr(adapter_response, "body_iterator"):
        return adapter_response

    # Wrap the response to inject brain log entries
    async def generate_with_brain_log():
        # Emit initial brain log entries (input received)
        for entry in collector.get_pending_entries():
            yield _format_data_chunk(entry.to_stream_dict())

        # Track accumulated content for brain log entries
        reasoning_buffers: dict[str, str] = {}
        text_buffers: dict[str, str] = {}
        first_text_logged = False

        # Stream the adapter response, parsing events for brain log
        async for chunk in adapter_response.body_iterator:
            yield chunk

            # Parse SSE chunk to extract event data
            chunk_str = chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk
            for line in chunk_str.split("\n"):
                if not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    continue
                try:
                    event = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                event_type = event.get("type", "")
                event_id = event.get("id", "")

                # Track reasoning/thinking
                if event_type == "reasoning-start":
                    reasoning_buffers[event_id] = ""
                elif event_type == "reasoning-delta":
                    if event_id in reasoning_buffers:
                        reasoning_buffers[event_id] += event.get("delta", "")
                elif event_type == "reasoning-end":
                    if event_id in reasoning_buffers:
                        text = reasoning_buffers.pop(event_id)
                        if text:
                            collector.add_thinking_entry(text)
                            for entry in collector.get_pending_entries():
                                yield _format_data_chunk(entry.to_stream_dict())

                # Track text output
                elif event_type == "text-start":
                    text_buffers[event_id] = ""
                    # Log first text token time
                    if not first_text_logged:
                        collector.record_first_token()
                        first_text_logged = True
                elif event_type == "text-delta":
                    if event_id in text_buffers:
                        text_buffers[event_id] += event.get("delta", "")
                    elif not first_text_logged:
                        collector.record_first_token()
                        first_text_logged = True
                elif event_type == "text-end":
                    if event_id in text_buffers:
                        text = text_buffers.pop(event_id)
                        if text:
                            collector.add_text_entry(text)
                            for entry in collector.get_pending_entries():
                                yield _format_data_chunk(entry.to_stream_dict())

            # Check for new entries (tool calls added during streaming)
            for entry in collector.get_pending_entries():
                yield _format_data_chunk(entry.to_stream_dict())

        # Emit any remaining text buffers
        for text in text_buffers.values():
            if text:
                collector.add_text_entry(text)
                for entry in collector.get_pending_entries():
                    yield _format_data_chunk(entry.to_stream_dict())

        # Emit performance metrics at the end
        total_ms = collector.get_total_ms()
        ttft_ms = collector.get_ttft_ms()
        collector.add_performance_entry(
            total_ms=total_ms,
            ttft_ms=ttft_ms,
        )
        for entry in collector.get_pending_entries():
            yield _format_data_chunk(entry.to_stream_dict())

        # Track chat completion
        capture(
            "chat_message_completed",
            {
                "total_ms": total_ms,
                "ttft_ms": ttft_ms,
            },
        )

        # Clear persistent attribution context now that streaming is complete
        tokenledger.clear_attribution()

    return StreamingResponse(
        generate_with_brain_log(),
        media_type=adapter_response.media_type,
        headers=dict(adapter_response.headers),
    )
