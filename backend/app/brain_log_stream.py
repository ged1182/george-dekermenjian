"""Brain Log streaming support for the Glass Box Portfolio.

This module provides a custom event stream that extends VercelAIEventStream
to emit Brain Log events alongside the standard chat stream events.

The Brain Log events are sent as DataChunk with type 'data-brain-log',
which the frontend can parse and display in the Brain Log panel.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from pydantic_ai.messages import TextPart, ToolCallPart
from pydantic_ai.ui.vercel_ai._event_stream import VercelAIEventStream
from pydantic_ai.ui.vercel_ai.response_types import BaseChunk, DataChunk

from app.schemas.brain_log import (
    BrainLogCollector,
    BrainLogEntry,
    LogEntryStatus,
)


class BrainLogChunk(DataChunk):
    """Custom data chunk for Brain Log events.

    Uses the Vercel AI SDK data stream protocol with a custom type
    that starts with 'data-' prefix.
    """

    type: str = "data-brain-log"

    @classmethod
    def from_entry(cls, entry: BrainLogEntry) -> "BrainLogChunk":
        """Create a BrainLogChunk from a BrainLogEntry."""
        return cls(data=entry.to_stream_dict())

    @classmethod
    def from_entries(cls, entries: list[BrainLogEntry]) -> list["BrainLogChunk"]:
        """Create BrainLogChunks from multiple entries."""
        return [cls.from_entry(entry) for entry in entries]


@dataclass
class BrainLogEventStream(VercelAIEventStream):
    """Extended event stream that emits Brain Log events.

    This class wraps the standard VercelAIEventStream and injects
    Brain Log events at appropriate points in the stream.
    """

    _collector: BrainLogCollector | None = field(default=None, init=False)
    _first_text_emitted: bool = field(default=False, init=False)
    _tool_start_times: dict[str, float] = field(default_factory=dict, init=False)

    def set_collector(self, collector: BrainLogCollector) -> None:
        """Set the Brain Log collector for this stream."""
        self._collector = collector

    def _emit_pending_brain_logs(self) -> list[BrainLogChunk]:
        """Emit any pending Brain Log entries."""
        if self._collector is None:
            return []
        entries = self._collector.get_pending_entries()
        return BrainLogChunk.from_entries(entries)

    async def before_stream(self) -> AsyncIterator[BaseChunk]:
        """Emit start events and any initial Brain Log entries."""
        # First, emit standard start events
        async for chunk in super().before_stream():
            yield chunk

        # Emit any initial Brain Log entries (like input received)
        for chunk in self._emit_pending_brain_logs():
            yield chunk

    async def before_response(self) -> AsyncIterator[BaseChunk]:
        """Emit step start events and any pending Brain Log entries."""
        # Emit pending Brain Log entries before response starts
        for chunk in self._emit_pending_brain_logs():
            yield chunk

        # Then emit standard step start events
        async for chunk in super().before_response():
            yield chunk

    async def handle_text_start(self, part: TextPart, follows_text: bool = False) -> AsyncIterator[BaseChunk]:
        """Handle text start and record first token time."""
        # Record first token time for TTFT calculation
        if not self._first_text_emitted and self._collector:
            self._collector.record_first_token()
            self._first_text_emitted = True

        # Emit any pending Brain Log entries
        for chunk in self._emit_pending_brain_logs():
            yield chunk

        async for chunk in super().handle_text_start(part, follows_text):
            yield chunk

    async def handle_tool_call_start(self, part: ToolCallPart) -> AsyncIterator[BaseChunk]:
        """Handle tool call start and emit Brain Log entry."""
        import time

        # Record start time for duration calculation
        self._tool_start_times[part.tool_call_id] = time.time()

        # Add routing entry if collector is available
        if self._collector:
            self._collector.add_routing_entry(
                selected_tool=part.tool_name,
                reason="LLM selected this tool based on user query",
            )

        # Emit pending Brain Log entries (including the routing entry)
        for chunk in self._emit_pending_brain_logs():
            yield chunk

        # Emit standard tool call start
        async for chunk in super().handle_tool_call_start(part):
            yield chunk

    async def handle_tool_call_end(self, part: ToolCallPart) -> AsyncIterator[BaseChunk]:
        """Handle tool call end."""
        # Emit standard tool call end
        async for chunk in super().handle_tool_call_end(part):
            yield chunk

        # Emit any pending Brain Log entries
        for chunk in self._emit_pending_brain_logs():
            yield chunk

    async def handle_function_tool_result(self, event) -> AsyncIterator[BaseChunk]:
        """Handle function tool result and emit Brain Log entry."""
        import time

        # Calculate duration
        tool_call_id = event.result.tool_call_id
        start_time = self._tool_start_times.pop(tool_call_id, None)
        duration_ms = None
        if start_time:
            duration_ms = (time.time() - start_time) * 1000

        # Determine status and result preview
        if hasattr(event.result, 'content'):
            # Get a preview of the result
            result_str = str(event.result.content)
            result_preview = result_str[:200] + "..." if len(result_str) > 200 else result_str
            status = LogEntryStatus.SUCCESS
            error = None
        else:
            result_preview = None
            status = LogEntryStatus.FAILURE
            error = "Tool execution failed"

        # Add tool call complete entry
        if self._collector:
            # Get tool name from the event
            tool_name = getattr(event.result, 'tool_name', 'unknown')
            self._collector.add_tool_call_complete(
                tool_name=tool_name,
                arguments={},  # Arguments were already logged in tool_call_start
                result_preview=result_preview,
                status=status,
                error=error,
                duration_ms=duration_ms,
            )

        # Emit pending Brain Log entries
        for chunk in self._emit_pending_brain_logs():
            yield chunk

        # Emit standard tool result
        async for chunk in super().handle_function_tool_result(event):
            yield chunk

    async def after_stream(self) -> AsyncIterator[BaseChunk]:
        """Emit final Brain Log entries and finish events."""
        # Add performance metrics
        if self._collector:
            self._collector.add_performance_entry(
                ttft_ms=self._collector.get_ttft_ms(),
                total_ms=self._collector.get_total_ms(),
            )

        # Emit final Brain Log entries
        for chunk in self._emit_pending_brain_logs():
            yield chunk

        # Then emit standard finish events
        async for chunk in super().after_stream():
            yield chunk
