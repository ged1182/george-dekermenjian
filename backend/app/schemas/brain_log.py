"""Brain Log schemas for structured agent execution logging.

These schemas define the log entries emitted during agent execution,
enabling the Glass Box Mode to visualize agent reasoning in real-time.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class LogEntryType(str, Enum):
    """Types of brain log entries."""

    INPUT = "input"
    ROUTING = "routing"
    TOOL_CALL = "tool_call"
    VALIDATION = "validation"
    PERFORMANCE = "performance"


class LogEntryStatus(str, Enum):
    """Status of a log entry."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"


class BrainLogEntry(BaseModel):
    """Base class for all brain log entries."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: LogEntryType
    title: str
    details: dict[str, Any] = Field(default_factory=dict)
    status: LogEntryStatus = LogEntryStatus.SUCCESS
    duration_ms: float | None = None


class InputLogEntry(BrainLogEntry):
    """Log entry for user input received."""

    type: LogEntryType = LogEntryType.INPUT

    @classmethod
    def create(cls, message: str, message_length: int) -> "InputLogEntry":
        """Create an input log entry."""
        return cls(
            title="User message received",
            details={
                "message_preview": message[:100] + "..."
                if len(message) > 100
                else message,
                "length": message_length,
            },
        )


class RoutingLogEntry(BrainLogEntry):
    """Log entry for tool/path routing decisions."""

    type: LogEntryType = LogEntryType.ROUTING

    @classmethod
    def create(
        cls,
        selected_tool: str | None,
        reason: str,
        alternatives: list[str] | None = None,
    ) -> "RoutingLogEntry":
        """Create a routing decision log entry."""
        details: dict[str, Any] = {"reason": reason}
        if selected_tool:
            details["selected_tool"] = selected_tool
        if alternatives:
            details["alternatives_considered"] = alternatives
        return cls(
            title=f"Selected tool: {selected_tool}"
            if selected_tool
            else "Direct response (no tool)",
            details=details,
        )


class ToolCallLogEntry(BrainLogEntry):
    """Log entry for tool execution."""

    type: LogEntryType = LogEntryType.TOOL_CALL

    @classmethod
    def create(
        cls,
        tool_name: str,
        arguments: dict[str, Any],
        result_preview: str | None = None,
        status: LogEntryStatus = LogEntryStatus.SUCCESS,
        error: str | None = None,
        duration_ms: float | None = None,
    ) -> "ToolCallLogEntry":
        """Create a tool call log entry."""
        details: dict[str, Any] = {
            "tool": tool_name,
            "arguments": arguments,
        }
        if result_preview:
            details["result_preview"] = result_preview
        if error:
            details["error"] = error
        return cls(
            title=f"Tool call: {tool_name}",
            details=details,
            status=status,
            duration_ms=duration_ms,
        )


class ValidationLogEntry(BrainLogEntry):
    """Log entry for output schema validation."""

    type: LogEntryType = LogEntryType.VALIDATION

    @classmethod
    def create(
        cls,
        schema_name: str,
        status: LogEntryStatus,
        validation_errors: list[str] | None = None,
        fallback_action: str | None = None,
    ) -> "ValidationLogEntry":
        """Create a validation log entry."""
        details: dict[str, Any] = {"schema": schema_name}
        if validation_errors:
            details["errors"] = validation_errors
        if fallback_action:
            details["fallback_action"] = fallback_action
        return cls(
            title=f"Output schema validated: {schema_name}",
            details=details,
            status=status,
        )


class PerformanceLogEntry(BrainLogEntry):
    """Log entry for performance metrics."""

    type: LogEntryType = LogEntryType.PERFORMANCE

    @classmethod
    def create(
        cls,
        ttft_ms: float | None = None,
        total_ms: float | None = None,
        tokens_in: int | None = None,
        tokens_out: int | None = None,
    ) -> "PerformanceLogEntry":
        """Create a performance metrics log entry."""
        details: dict[str, Any] = {}
        if ttft_ms is not None:
            details["ttft_ms"] = round(ttft_ms, 2)
        if total_ms is not None:
            details["total_ms"] = round(total_ms, 2)
        if tokens_in is not None:
            details["tokens_in"] = tokens_in
        if tokens_out is not None:
            details["tokens_out"] = tokens_out
        return cls(
            title="Request complete",
            details=details,
            duration_ms=total_ms,
        )
