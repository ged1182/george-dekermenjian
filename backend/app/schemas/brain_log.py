"""Brain Log schemas for structured agent execution logging.

These schemas define the log entries emitted during agent execution,
enabling the Glass Box Mode to visualize agent reasoning in real-time.
"""

from contextvars import ContextVar
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class LogEntryType(str, Enum):
    """Types of brain log entries."""

    INPUT = "input"
    ROUTING = "routing"
    THINKING = "thinking"
    TEXT = "text"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
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
    timestamp: datetime = Field(default_factory=_utc_now)
    type: LogEntryType
    title: str
    details: dict[str, Any] = Field(default_factory=dict)
    status: LogEntryStatus = LogEntryStatus.SUCCESS
    duration_ms: float | None = None

    def to_stream_dict(self) -> dict[str, Any]:
        """Convert entry to a dictionary suitable for streaming."""
        return {
            "id": self.id,
            "timestamp": int(self.timestamp.timestamp() * 1000),  # JS timestamp
            "type": self.type.value,
            "title": self.title,
            "details": self.details,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
        }


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


class ThinkingLogEntry(BrainLogEntry):
    """Log entry for model thinking/reasoning."""

    type: LogEntryType = LogEntryType.THINKING

    @classmethod
    def create(
        cls,
        thinking_text: str,
    ) -> "ThinkingLogEntry":
        """Create a thinking log entry."""
        preview = thinking_text[:200] + "..." if len(thinking_text) > 200 else thinking_text
        return cls(
            title="Model reasoning",
            details={
                "preview": preview,
                "length": len(thinking_text),
            },
        )


class TextLogEntry(BrainLogEntry):
    """Log entry for model text output."""

    type: LogEntryType = LogEntryType.TEXT

    @classmethod
    def create(
        cls,
        text: str,
        is_partial: bool = False,
    ) -> "TextLogEntry":
        """Create a text output log entry."""
        preview = text[:200] + "..." if len(text) > 200 else text
        return cls(
            title="Text response" if not is_partial else "Text chunk",
            details={
                "preview": preview,
                "length": len(text),
                "is_partial": is_partial,
            },
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

    @classmethod
    def create_pending(
        cls,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> "ToolCallLogEntry":
        """Create a pending tool call log entry."""
        details: dict[str, Any] = {
            "tool": tool_name,
            "arguments": arguments,
        }
        return cls(
            title=f"Calling {tool_name}...",
            details=details,
            status=LogEntryStatus.PENDING,
        )


class ToolResultLogEntry(BrainLogEntry):
    """Log entry for tool execution results (separate from invocation)."""

    type: LogEntryType = LogEntryType.TOOL_RESULT

    @classmethod
    def create(
        cls,
        tool_name: str,
        result_preview: str | None = None,
        status: LogEntryStatus = LogEntryStatus.SUCCESS,
        error: str | None = None,
        duration_ms: float | None = None,
    ) -> "ToolResultLogEntry":
        """Create a tool result log entry."""
        details: dict[str, Any] = {"tool": tool_name}
        if result_preview:
            details["result_preview"] = result_preview
        if error:
            details["error"] = error

        title = f"Tool result: {tool_name}"
        if status == LogEntryStatus.FAILURE:
            title = f"Tool failed: {tool_name}"

        return cls(
            title=title,
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


class BrainLogCollector:
    """Collector for Brain Log entries during agent execution.

    Tracks entries and timing information for the Glass Box mode display.
    """

    def __init__(self) -> None:
        """Initialize the collector."""
        import time

        self.entries: list[BrainLogEntry] = []
        self._pending: list[BrainLogEntry] = []
        self._start_time: float = time.time()
        self.first_token_time: float | None = None
        self._entry_id_map: dict[str, BrainLogEntry] = {}

    def add(self, entry: BrainLogEntry) -> None:
        """Add an entry to the collector."""
        self.entries.append(entry)
        self._pending.append(entry)
        self._entry_id_map[entry.id] = entry

    def add_entry(self, entry: BrainLogEntry) -> None:
        """Add an entry to the collector (alias for add)."""
        self.add(entry)

    def get_pending_entries(self) -> list[BrainLogEntry]:
        """Get and clear pending entries."""
        pending = self.entries.copy()
        self.entries.clear()
        self._pending.clear()
        return pending

    def get_all_entries(self) -> list[BrainLogEntry]:
        """Get all collected entries."""
        return list(self._entry_id_map.values())

    def record_first_token(self) -> None:
        """Record when the first token was received."""
        import time

        if self.first_token_time is None:
            self.first_token_time = time.time()

    def get_ttft_ms(self) -> float | None:
        """Get time to first token in milliseconds."""
        if self.first_token_time is None:
            return None
        return (self.first_token_time - self._start_time) * 1000

    def get_total_ms(self) -> float:
        """Get total elapsed time in milliseconds."""
        import time

        return (time.time() - self._start_time) * 1000

    def add_input_entry(self, message: str) -> None:
        """Add an input received entry."""
        entry = InputLogEntry.create(
            message=message,
            message_length=len(message),
        )
        self.add(entry)

    def add_routing_entry(
        self,
        selected_tool: str | None,
        reason: str,
        alternatives: list[str] | None = None,
    ) -> None:
        """Add a routing decision entry."""
        entry = RoutingLogEntry.create(
            selected_tool=selected_tool,
            reason=reason,
            alternatives=alternatives,
        )
        self.add(entry)

    def add_tool_call_pending(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> str:
        """Add a pending tool call entry and return its ID."""
        entry = ToolCallLogEntry.create_pending(
            tool_name=tool_name,
            arguments=arguments,
        )
        self.add(entry)
        return entry.id

    def update_tool_call(
        self,
        entry_id: str,
        status: LogEntryStatus,
        result_preview: str | None = None,
        error: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """Update a tool call entry with result."""
        entry = self._entry_id_map.get(entry_id)
        if entry is None:
            return

        # Update the entry fields
        entry.status = status
        entry.duration_ms = duration_ms

        if result_preview:
            entry.details["result_preview"] = result_preview
        if error:
            entry.details["error"] = error

        # Update title based on status
        tool_name = entry.details.get("tool", "unknown")
        if status == LogEntryStatus.SUCCESS:
            entry.title = f"Tool call: {tool_name}"
        elif status == LogEntryStatus.FAILURE:
            entry.title = f"Tool call failed: {tool_name}"

        # Add updated entry back to pending list for streaming
        self.entries.append(entry)
        self._pending.append(entry)

    def add_tool_call_complete(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        result_preview: str | None = None,
        status: LogEntryStatus = LogEntryStatus.SUCCESS,
        error: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """Add a tool call completion entry."""
        entry = ToolCallLogEntry.create(
            tool_name=tool_name,
            arguments=arguments,
            result_preview=result_preview,
            status=status,
            error=error,
            duration_ms=duration_ms,
        )
        self.add(entry)

    def add_validation_entry(
        self,
        schema_name: str,
        status: LogEntryStatus,
        validation_errors: list[str] | None = None,
        fallback_action: str | None = None,
    ) -> None:
        """Add a validation entry."""
        entry = ValidationLogEntry.create(
            schema_name=schema_name,
            status=status,
            validation_errors=validation_errors,
            fallback_action=fallback_action,
        )
        self.add(entry)

    def add_performance_entry(
        self,
        ttft_ms: float | None = None,
        total_ms: float | None = None,
        tokens_in: int | None = None,
        tokens_out: int | None = None,
    ) -> None:
        """Add a performance metrics entry."""
        entry = PerformanceLogEntry.create(
            ttft_ms=ttft_ms,
            total_ms=total_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )
        self.add(entry)

    def add_thinking_entry(self, thinking_text: str) -> None:
        """Add a thinking/reasoning entry."""
        entry = ThinkingLogEntry.create(thinking_text=thinking_text)
        self.add(entry)

    def add_text_entry(self, text: str, is_partial: bool = False) -> None:
        """Add a text output entry."""
        entry = TextLogEntry.create(text=text, is_partial=is_partial)
        self.add(entry)

    def add_tool_result_entry(
        self,
        tool_name: str,
        result_preview: str | None = None,
        status: LogEntryStatus = LogEntryStatus.SUCCESS,
        error: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """Add a tool result entry (separate from invocation)."""
        entry = ToolResultLogEntry.create(
            tool_name=tool_name,
            result_preview=result_preview,
            status=status,
            error=error,
            duration_ms=duration_ms,
        )
        self.add(entry)


# Context variable for accessing collector during request processing
_brain_log_collector_var: ContextVar[BrainLogCollector | None] = ContextVar(
    "brain_log_collector", default=None
)


def get_brain_log_collector() -> BrainLogCollector | None:
    """Get the current brain log collector from context."""
    return _brain_log_collector_var.get()


def set_brain_log_collector(collector: BrainLogCollector | None) -> None:
    """Set the brain log collector in context."""
    _brain_log_collector_var.set(collector)
