# Glass Box Portfolio Backend
# Production-grade Dockerfile optimized for Google Cloud Run
#
# Build: docker build -t glass-box-backend .
# Run:   docker run -p 8080:8080 -e GEMINI_API_KEY=... glass-box-backend

# -----------------------------------------------------------------------------
# Stage 1: Build stage - Install dependencies with uv
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS builder

# Install uv for fast dependency management
# https://docs.astral.sh/uv/
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
# --frozen: Use exact versions from uv.lock
# --no-dev: Skip dev dependencies for production
# --no-editable: Don't install the project itself in editable mode
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application code
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

# -----------------------------------------------------------------------------
# Stage 2: Runtime stage - Minimal production image
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

# Security: Create non-root user
# Cloud Run runs as non-root by default, but this ensures consistency
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copy application code
COPY --from=builder --chown=appuser:appgroup /app /app

# Set environment variables
# - PATH: Include the virtual environment binaries
# - PYTHONDONTWRITEBYTECODE: Don't write .pyc files (already compiled)
# - PYTHONUNBUFFERED: Ensure logs are immediately flushed (important for Cloud Run)
# - PYTHONFAULTHANDLER: Better error tracebacks
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

# Cloud Run default port
ENV PORT=8080

# Switch to non-root user
USER appuser

# Expose the port Cloud Run expects
EXPOSE 8080

# Health check for container orchestration
# Cloud Run has its own health checks, but this helps with local testing
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run uvicorn with production settings
# - host 0.0.0.0: Accept connections from outside the container
# - port from env: Cloud Run sets PORT environment variable
# - workers 1: Cloud Run handles scaling via container instances
# - no-access-log: Cloud Run handles request logging
# - timeout-keep-alive 75: Slightly longer than Cloud Run's LB timeout (60s)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--timeout-keep-alive", "75"]
