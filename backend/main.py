"""Vercel entrypoint - exposes FastAPI app."""

from app.main import app

__all__ = ["app"]
