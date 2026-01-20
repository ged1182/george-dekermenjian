"""Tests for brain_log_stream.py - Brain Log streaming support."""

from unittest.mock import Mock, patch

import pytest

from app.brain_log_stream import BrainLogChunk, BrainLogEventStream
from app.schemas.brain_log import (
    BrainLogCollector,
    BrainLogEntry,
    LogEntryStatus,
    LogEntryType,
)
from pydantic_ai.ui.vercel_ai import VercelAIEventStream
from tests.conftest import async_iter


# ============================================================================
# Test Helpers
# ============================================================================


def create_test_entry(
    index: int = 0,
    entry_type: LogEntryType = LogEntryType.INPUT,
    status: LogEntryStatus = LogEntryStatus.SUCCESS,
) -> BrainLogEntry:
    """Create a test BrainLogEntry."""
    return BrainLogEntry(
        id=f"test-{index}",
        timestamp=1234567890 + index,
        type=entry_type,
        title=f"Test Entry {index}",
        status=status,
    )


# ============================================================================
# EASY: BrainLogChunk Tests
# ============================================================================


class TestBrainLogChunkFromEntry:
    """Tests for BrainLogChunk.from_entry() class method."""

    def test_creates_chunk_with_correct_type(self):
        """Should create a chunk with type 'data-brain-log'."""
        entry = create_test_entry()

        chunk = BrainLogChunk.from_entry(entry)

        assert chunk.type == "data-brain-log"

    def test_creates_chunk_with_entry_data(self):
        """Should include the entry's stream dict as data."""
        entry = create_test_entry(index=42)

        chunk = BrainLogChunk.from_entry(entry)

        assert chunk.data == entry.to_stream_dict()
        assert chunk.data["id"] == "test-42"

    def test_preserves_entry_type(self):
        """Should preserve the entry type in the chunk data."""
        entry = create_test_entry(entry_type=LogEntryType.TOOL_CALL)

        chunk = BrainLogChunk.from_entry(entry)

        assert chunk.data["type"] == "tool_call"

    def test_preserves_entry_status(self):
        """Should preserve the entry status in the chunk data."""
        entry = create_test_entry(status=LogEntryStatus.FAILURE)

        chunk = BrainLogChunk.from_entry(entry)

        assert chunk.data["status"] == "failure"


class TestBrainLogChunkFromEntries:
    """Tests for BrainLogChunk.from_entries() class method."""

    def test_creates_chunks_for_all_entries(self):
        """Should create a chunk for each entry."""
        entries = [create_test_entry(i) for i in range(3)]

        chunks = BrainLogChunk.from_entries(entries)

        assert len(chunks) == 3

    def test_all_chunks_have_correct_type(self):
        """All chunks should have type 'data-brain-log'."""
        entries = [create_test_entry(i) for i in range(3)]

        chunks = BrainLogChunk.from_entries(entries)

        assert all(c.type == "data-brain-log" for c in chunks)

    def test_preserves_entry_order(self):
        """Should preserve the order of entries."""
        entries = [create_test_entry(i) for i in range(3)]

        chunks = BrainLogChunk.from_entries(entries)

        assert chunks[0].data["id"] == "test-0"
        assert chunks[1].data["id"] == "test-1"
        assert chunks[2].data["id"] == "test-2"

    def test_empty_list_returns_empty(self):
        """Should return empty list for empty input."""
        chunks = BrainLogChunk.from_entries([])

        assert chunks == []

    def test_single_entry_returns_single_chunk(self):
        """Should handle single entry correctly."""
        entries = [create_test_entry(0)]

        chunks = BrainLogChunk.from_entries(entries)

        assert len(chunks) == 1
        assert chunks[0].data["id"] == "test-0"


# ============================================================================
# MEDIUM: Stream Setup Tests
# ============================================================================


class TestBrainLogEventStreamSetup:
    """Tests for BrainLogEventStream initialization and setup."""

    def test_set_collector(self):
        """Should store the collector reference."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        collector = BrainLogCollector()

        stream.set_collector(collector)

        assert stream._collector is collector

    def test_emit_pending_without_collector_returns_empty(self):
        """Should return empty list when no collector is set."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")

        chunks = stream._emit_pending_brain_logs()

        assert chunks == []

    def test_emit_pending_with_collector_returns_chunks(self):
        """Should return chunks for pending entries."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        collector = BrainLogCollector()
        stream.set_collector(collector)

        # Add an entry to the collector
        collector.add_input_entry("Test message")

        chunks = stream._emit_pending_brain_logs()

        assert len(chunks) == 1
        assert chunks[0].type == "data-brain-log"

    def test_emit_pending_clears_pending_entries(self):
        """Should clear pending entries after emitting."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        collector = BrainLogCollector()
        stream.set_collector(collector)

        collector.add_input_entry("Test message")
        stream._emit_pending_brain_logs()

        # Second call should return empty
        chunks = stream._emit_pending_brain_logs()
        assert chunks == []


# ============================================================================
# MEDIUM: Async Stream Method Tests
# ============================================================================


class TestBeforeStream:
    """Tests for before_stream() async generator method."""

    @pytest.mark.asyncio
    async def test_yields_parent_chunks_first(self):
        """Should yield chunks from parent's before_stream first."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")

        # Create a mock chunk from parent
        parent_chunk = Mock()
        parent_chunk.type = "parent-chunk"

        with patch.object(
            VercelAIEventStream,
            "before_stream",
            return_value=async_iter([parent_chunk]),
        ):
            chunks = [c async for c in stream.before_stream()]

        # Parent chunk should be in results
        assert parent_chunk in chunks

    @pytest.mark.asyncio
    async def test_yields_brain_log_chunks_after_parent(self):
        """Should yield Brain Log chunks after parent chunks."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        collector = BrainLogCollector()
        stream.set_collector(collector)

        # Add an entry before calling before_stream
        collector.add_input_entry("Test input")

        parent_chunk = Mock()
        parent_chunk.type = "parent-chunk"

        with patch.object(
            VercelAIEventStream,
            "before_stream",
            return_value=async_iter([parent_chunk]),
        ):
            chunks = [c async for c in stream.before_stream()]

        # Should have both parent and brain log chunks
        assert len(chunks) == 2
        assert chunks[0] == parent_chunk  # Parent first
        assert chunks[1].type == "data-brain-log"  # Brain log second

    @pytest.mark.asyncio
    async def test_works_without_collector(self):
        """Should work when no collector is set (no brain log chunks)."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        # No collector set

        parent_chunk = Mock()

        with patch.object(
            VercelAIEventStream,
            "before_stream",
            return_value=async_iter([parent_chunk]),
        ):
            chunks = [c async for c in stream.before_stream()]

        # Only parent chunk
        assert len(chunks) == 1
        assert chunks[0] == parent_chunk


class TestBeforeResponse:
    """Tests for before_response() async generator method."""

    @pytest.mark.asyncio
    async def test_yields_brain_log_chunks_first(self):
        """Should yield Brain Log chunks before parent chunks."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        collector = BrainLogCollector()
        stream.set_collector(collector)

        # Add an entry
        collector.add_input_entry("Test input")

        parent_chunk = Mock()
        parent_chunk.type = "parent-chunk"

        with patch.object(
            VercelAIEventStream,
            "before_response",
            return_value=async_iter([parent_chunk]),
        ):
            chunks = [c async for c in stream.before_response()]

        # Brain log first, then parent
        assert len(chunks) == 2
        assert chunks[0].type == "data-brain-log"  # Brain log first
        assert chunks[1] == parent_chunk  # Parent second

    @pytest.mark.asyncio
    async def test_yields_parent_chunks_after_brain_log(self):
        """Should yield parent chunks after Brain Log chunks."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        # No collector - no brain log chunks

        parent_chunk = Mock()

        with patch.object(
            VercelAIEventStream,
            "before_response",
            return_value=async_iter([parent_chunk]),
        ):
            chunks = [c async for c in stream.before_response()]

        # Only parent chunk
        assert len(chunks) == 1
        assert chunks[0] == parent_chunk


class TestHandleTextStart:
    """Tests for handle_text_start() async generator method."""

    @pytest.mark.asyncio
    async def test_records_first_token_time(self):
        """Should record first token time on first text."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        collector = BrainLogCollector()
        stream.set_collector(collector)

        # Verify first_token_time is not set yet
        assert collector.first_token_time is None

        text_part = Mock()

        with patch.object(
            VercelAIEventStream,
            "handle_text_start",
            return_value=async_iter([]),
        ):
            _ = [c async for c in stream.handle_text_start(text_part)]

        # First token time should now be set
        assert collector.first_token_time is not None
        assert stream._first_text_emitted is True

    @pytest.mark.asyncio
    async def test_does_not_record_on_subsequent_text(self):
        """Should not record first token time on subsequent text."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        collector = BrainLogCollector()
        stream.set_collector(collector)

        # Simulate first text already emitted
        stream._first_text_emitted = True
        collector.first_token_time = 12345.0  # Already recorded

        text_part = Mock()

        with patch.object(
            VercelAIEventStream,
            "handle_text_start",
            return_value=async_iter([]),
        ):
            _ = [c async for c in stream.handle_text_start(text_part)]

        # First token time should be unchanged
        assert collector.first_token_time == 12345.0

    @pytest.mark.asyncio
    async def test_emits_pending_brain_log_chunks(self):
        """Should emit pending Brain Log chunks."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        collector = BrainLogCollector()
        stream.set_collector(collector)

        # Add a pending entry
        collector.add_input_entry("Test")

        text_part = Mock()

        with patch.object(
            VercelAIEventStream,
            "handle_text_start",
            return_value=async_iter([]),
        ):
            chunks = [c async for c in stream.handle_text_start(text_part)]

        # Should have brain log chunk
        assert len(chunks) == 1
        assert chunks[0].type == "data-brain-log"

    @pytest.mark.asyncio
    async def test_yields_parent_chunks(self):
        """Should yield chunks from parent's handle_text_start."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")

        text_part = Mock()
        parent_chunk = Mock()

        with patch.object(
            VercelAIEventStream,
            "handle_text_start",
            return_value=async_iter([parent_chunk]),
        ):
            chunks = [c async for c in stream.handle_text_start(text_part)]

        assert parent_chunk in chunks

    @pytest.mark.asyncio
    async def test_works_without_collector(self):
        """Should work when no collector is set."""
        run_input = Mock()
        stream = BrainLogEventStream(run_input=run_input, accept="*/*")
        # No collector

        text_part = Mock()
        parent_chunk = Mock()

        with patch.object(
            VercelAIEventStream,
            "handle_text_start",
            return_value=async_iter([parent_chunk]),
        ):
            chunks = [c async for c in stream.handle_text_start(text_part)]

        # Should still work, just no TTFT recording
        assert len(chunks) == 1
        assert stream._first_text_emitted is False  # Not set without collector
