"""Vercel serverless function entry point.

This module exposes the FastAPI app for Vercel's Python runtime.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app/
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

# Vercel looks for 'app' or 'handler' variable
# FastAPI apps are ASGI-compatible which Vercel supports
