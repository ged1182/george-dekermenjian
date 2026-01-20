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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response, StreamingResponse

from app.config import get_settings
from app.agent import portfolio_agent
from app.tools.experience import get_full_profile, ProfileData
from app.schemas.brain_log import BrainLogCollector, set_brain_log_collector

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
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Using model: {settings.model_name}")
    yield
    # Shutdown
    print("Shutting down...")


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
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    """Format a data annotation chunk in Vercel AI Data Stream Protocol.

    The Vercel AI SDK collects all type 8 data chunks into an array that
    gets passed to the onData callback. We emit each entry directly (not
    wrapped in an array) so the frontend receives [{entry1}, {entry2}, ...].
    """
    return f"8:{json.dumps(data)}\n"


class _CachedBodyRequest(Request):
    """Request wrapper that caches and replays the body."""

    def __init__(self, scope: dict, body: bytes):
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

    # Create brain log collector for this request
    collector = BrainLogCollector()
    collector.add_input_entry(user_message)
    set_brain_log_collector(collector)

    # Create a new request with the cached body for VercelAIAdapter
    cached_request = _CachedBodyRequest(request.scope, body_bytes)

    # Get the streaming response from VercelAIAdapter
    adapter_response = await VercelAIAdapter.dispatch_request(
        cached_request, agent=portfolio_agent
    )

    # Wrap the response to inject brain log entries
    async def generate_with_brain_log():
        # Emit initial brain log entries (input received)
        for entry in collector.get_pending_entries():
            yield _format_data_chunk(entry.to_stream_dict())

        # Stream the adapter response
        async for chunk in adapter_response.body_iterator:
            yield chunk

        # Emit performance metrics at the end
        collector.add_performance_entry(
            total_ms=collector.get_total_ms(),
            ttft_ms=collector.get_ttft_ms(),
        )
        for entry in collector.get_pending_entries():
            yield _format_data_chunk(entry.to_stream_dict())

    return StreamingResponse(
        generate_with_brain_log(),
        media_type=adapter_response.media_type,
        headers=dict(adapter_response.headers),
    )
