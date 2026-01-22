"""Logging configuration for the Glass Box Portfolio backend.

This module sets up structured logging that works well with Cloud Run's
logging infrastructure. Logs are formatted as JSON in production for
easy parsing by Cloud Logging.
"""

import logging
import os
import sys
from typing import Any

# Determine if we're in production
IS_PRODUCTION = os.environ.get("ENVIRONMENT", "development") == "production"


class CloudRunFormatter(logging.Formatter):
    """JSON formatter optimized for Google Cloud Run logging.

    Cloud Run automatically captures stdout/stderr and parses JSON logs
    to extract severity, message, and other fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_entry: dict[str, Any] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add extra fields if present
        if hasattr(record, "tool_name"):
            log_entry["tool_name"] = record.tool_name
        if hasattr(record, "file_path"):
            log_entry["file_path"] = record.file_path
        if hasattr(record, "symbol"):
            log_entry["symbol"] = record.symbol

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging() -> None:
    """Configure logging for the application.

    In production (Cloud Run), uses JSON formatting for Cloud Logging.
    In development, uses a simple human-readable format.
    """
    root_logger = logging.getLogger()

    # Remove any existing handlers
    root_logger.handlers.clear()

    # Set log level based on environment
    log_level = (
        logging.DEBUG if os.environ.get("DEBUG", "").lower() == "true" else logging.INFO
    )
    root_logger.setLevel(log_level)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if IS_PRODUCTION:
        # JSON format for Cloud Run
        handler.setFormatter(CloudRunFormatter())
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
