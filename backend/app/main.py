"""Glass Box Portfolio Backend - FastAPI Application.

This is the main entry point for the Glass Box Portfolio backend API.
It provides:
- Health check endpoint for Cloud Run
- CORS configuration for cross-origin requests from the frontend
- POST /chat endpoint for agentic interactions
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

from app.config import get_settings
from app.agent import portfolio_agent

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
        "chat": "/chat (POST)",
    }


@app.post("/chat")
async def chat(request: Request) -> Response:
    """Streaming chat endpoint using VercelAIAdapter.

    This is the one-liner from pydantic-ai that handles all protocol details
    for Vercel AI SDK compatibility. The adapter:
    - Parses incoming UI Messages format requests
    - Runs the agent with streaming enabled
    - Emits SSE events in Data Stream Protocol format
    - Handles tool calls and deferred approval flows
    """
    return await VercelAIAdapter.dispatch_request(request, agent=portfolio_agent)
