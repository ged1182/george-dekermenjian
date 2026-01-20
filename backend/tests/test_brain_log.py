"""Tests for brain log schemas."""

import time

import pytest

from app.schemas.brain_log import (
    LogEntryType,
    LogEntryStatus,
    BrainLogEntry,
    InputLogEntry,
    RoutingLogEntry,
    ToolCallLogEntry,
    ValidationLogEntry,
    PerformanceLogEntry,
    BrainLogCollector,
    get_brain_log_collector,
    set_brain_log_collector,
)


class TestLogEntryEnums:
    """Test enum values."""

    def test_log_entry_types(self):
        """Test LogEntryType enum values."""
        assert LogEntryType.INPUT.value == "input"
        assert LogEntryType.ROUTING.value == "routing"
        assert LogEntryType.TOOL_CALL.value == "tool_call"
        assert LogEntryType.VALIDATION.value == "validation"
        assert LogEntryType.PERFORMANCE.value == "performance"

    def test_log_entry_status(self):
        """Test LogEntryStatus enum values."""
        assert LogEntryStatus.PENDING.value == "pending"
        assert LogEntryStatus.SUCCESS.value == "success"
        assert LogEntryStatus.FAILURE.value == "failure"


class TestBrainLogEntry:
    """Test BrainLogEntry base class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        entry = BrainLogEntry(type=LogEntryType.INPUT, title="Test")
        assert entry.id is not None
        assert entry.timestamp > 0
        assert entry.status == LogEntryStatus.SUCCESS
        assert entry.duration_ms is None
        assert entry.details == {}

    def test_to_stream_dict(self):
        """Test serialization to stream format."""
        entry = BrainLogEntry(
            type=LogEntryType.INPUT,
            title="Test",
            details={"key": "value"},
        )
        stream_dict = entry.to_stream_dict()
        assert stream_dict["type"] == "input"
        assert stream_dict["title"] == "Test"
        assert stream_dict["details"] == {"key": "value"}
        assert stream_dict["status"] == "success"


class TestInputLogEntry:
    """Test InputLogEntry class."""

    def test_create_short_message(self):
        """Test creating entry with short message."""
        entry = InputLogEntry.create("Hello world", 11)
        assert entry.type == LogEntryType.INPUT
        assert entry.title == "User message received"
        assert entry.details["message_preview"] == "Hello world"
        assert entry.details["length"] == 11

    def test_create_long_message(self):
        """Test creating entry with message longer than 100 chars."""
        long_message = "x" * 150
        entry = InputLogEntry.create(long_message, 150)
        assert entry.details["message_preview"] == "x" * 100 + "..."


class TestRoutingLogEntry:
    """Test RoutingLogEntry class."""

    def test_create_with_tool(self):
        """Test creating entry with selected tool."""
        entry = RoutingLogEntry.create(
            selected_tool="get_skills",
            reason="User asked about skills",
            alternatives=["get_experience", "get_profile"],
        )
        assert entry.type == LogEntryType.ROUTING
        assert "get_skills" in entry.title
        assert entry.details["selected_tool"] == "get_skills"
        assert entry.details["reason"] == "User asked about skills"
        assert entry.details["alternatives_considered"] == ["get_experience", "get_profile"]

    def test_create_direct_response(self):
        """Test creating entry for direct response (no tool)."""
        entry = RoutingLogEntry.create(
            selected_tool=None,
            reason="Simple greeting",
        )
        assert "no tool" in entry.title.lower()
        assert "selected_tool" not in entry.details


class TestToolCallLogEntry:
    """Test ToolCallLogEntry class."""

    def test_create_success(self):
        """Test creating successful tool call entry."""
        entry = ToolCallLogEntry.create(
            tool_name="get_skills",
            arguments={"category": "ai"},
            result_preview="Skills: Python, AI...",
            status=LogEntryStatus.SUCCESS,
            duration_ms=150.5,
        )
        assert entry.type == LogEntryType.TOOL_CALL
        assert "get_skills" in entry.title
        assert entry.details["tool"] == "get_skills"
        assert entry.details["arguments"] == {"category": "ai"}
        assert entry.details["result_preview"] == "Skills: Python, AI..."
        assert entry.duration_ms == 150.5

    def test_create_failure(self):
        """Test creating failed tool call entry."""
        entry = ToolCallLogEntry.create(
            tool_name="get_file_content",
            arguments={"path": "/invalid"},
            status=LogEntryStatus.FAILURE,
            error="File not found",
        )
        assert entry.status == LogEntryStatus.FAILURE
        assert entry.details["error"] == "File not found"

    def test_create_pending(self):
        """Test creating pending tool call entry."""
        entry = ToolCallLogEntry.create_pending("get_skills", {"category": "all"})
        assert entry.status == LogEntryStatus.PENDING
        assert "Calling" in entry.title


class TestValidationLogEntry:
    """Test ValidationLogEntry class."""

    def test_create_success(self):
        """Test creating successful validation entry."""
        entry = ValidationLogEntry.create(
            schema_name="SkillsResponse",
            status=LogEntryStatus.SUCCESS,
        )
        assert entry.type == LogEntryType.VALIDATION
        assert "SkillsResponse" in entry.title
        assert entry.details["schema"] == "SkillsResponse"

    def test_create_failure_with_errors(self):
        """Test creating validation entry with errors."""
        entry = ValidationLogEntry.create(
            schema_name="ProfileResponse",
            status=LogEntryStatus.FAILURE,
            validation_errors=["Missing required field: email"],
            fallback_action="Using default profile",
        )
        assert entry.status == LogEntryStatus.FAILURE
        assert entry.details["errors"] == ["Missing required field: email"]
        assert entry.details["fallback_action"] == "Using default profile"


class TestPerformanceLogEntry:
    """Test PerformanceLogEntry class."""

    def test_create_with_all_metrics(self):
        """Test creating performance entry with all metrics."""
        entry = PerformanceLogEntry.create(
            ttft_ms=250.123,
            total_ms=1500.456,
            tokens_in=100,
            tokens_out=500,
        )
        assert entry.type == LogEntryType.PERFORMANCE
        assert entry.title == "Request complete"
        assert entry.details["ttft_ms"] == 250.12  # Rounded
        assert entry.details["total_ms"] == 1500.46  # Rounded
        assert entry.details["tokens_in"] == 100
        assert entry.details["tokens_out"] == 500

    def test_create_with_partial_metrics(self):
        """Test creating performance entry with partial metrics."""
        entry = PerformanceLogEntry.create(total_ms=500.0)
        assert "ttft_ms" not in entry.details
        assert entry.details["total_ms"] == 500.0


class TestBrainLogCollector:
    """Test BrainLogCollector class."""

    def test_add_entry(self):
        """Test adding entries to collector."""
        collector = BrainLogCollector()
        entry = BrainLogEntry(type=LogEntryType.INPUT, title="Test")
        collector.add(entry)
        assert len(collector.entries) == 1

    def test_record_first_token(self):
        """Test recording first token time."""
        collector = BrainLogCollector()
        assert collector.first_token_time is None
        collector.record_first_token()
        assert collector.first_token_time is not None
        # Second call should not update
        first_time = collector.first_token_time
        time.sleep(0.01)
        collector.record_first_token()
        assert collector.first_token_time == first_time

    def test_get_ttft_ms(self):
        """Test getting time to first token."""
        collector = BrainLogCollector()
        assert collector.get_ttft_ms() is None
        time.sleep(0.01)
        collector.record_first_token()
        ttft = collector.get_ttft_ms()
        assert ttft is not None
        assert ttft > 0

    def test_get_total_ms(self):
        """Test getting total request duration."""
        collector = BrainLogCollector()
        time.sleep(0.01)
        total = collector.get_total_ms()
        assert total > 0

    def test_get_pending_entries(self):
        """Test getting and clearing pending entries."""
        collector = BrainLogCollector()
        entry1 = BrainLogEntry(type=LogEntryType.INPUT, title="Test1")
        entry2 = BrainLogEntry(type=LogEntryType.ROUTING, title="Test2")
        collector.add(entry1)
        collector.add(entry2)

        entries = collector.get_pending_entries()
        assert len(entries) == 2
        assert len(collector.entries) == 0  # Cleared

    def test_add_input_entry(self):
        """Test convenience method for adding input entry."""
        collector = BrainLogCollector()
        collector.add_input_entry("Hello")
        assert len(collector.entries) == 1
        assert collector.entries[0].type == LogEntryType.INPUT

    def test_add_routing_entry(self):
        """Test convenience method for adding routing entry."""
        collector = BrainLogCollector()
        collector.add_routing_entry("get_skills", "User asked about skills")
        assert len(collector.entries) == 1
        assert collector.entries[0].type == LogEntryType.ROUTING

    def test_add_tool_call_pending(self):
        """Test adding pending tool call and getting ID."""
        collector = BrainLogCollector()
        entry_id = collector.add_tool_call_pending("get_skills", {})
        assert entry_id is not None
        assert len(collector.entries) == 1
        assert collector.entries[0].status == LogEntryStatus.PENDING

    def test_update_tool_call(self):
        """Test updating tool call entry."""
        collector = BrainLogCollector()
        entry_id = collector.add_tool_call_pending("get_skills", {})
        collector.update_tool_call(
            entry_id,
            status=LogEntryStatus.SUCCESS,
            result_preview="Skills found",
            duration_ms=100.0,
        )
        assert collector.entries[0].status == LogEntryStatus.SUCCESS
        assert collector.entries[0].details["result_preview"] == "Skills found"
        assert collector.entries[0].duration_ms == 100.0

    def test_update_tool_call_failure(self):
        """Test updating tool call entry with failure."""
        collector = BrainLogCollector()
        entry_id = collector.add_tool_call_pending("get_file", {"path": "bad"})
        collector.update_tool_call(
            entry_id,
            status=LogEntryStatus.FAILURE,
            error="File not found",
        )
        assert collector.entries[0].status == LogEntryStatus.FAILURE
        assert "failed" in collector.entries[0].title.lower()

    def test_add_tool_call_complete(self):
        """Test adding a complete tool call entry."""
        collector = BrainLogCollector()
        collector.add_tool_call_complete(
            "get_skills",
            {"category": "ai"},
            result_preview="Skills: ...",
            duration_ms=50.0,
        )
        assert len(collector.entries) == 1
        assert collector.entries[0].status == LogEntryStatus.SUCCESS

    def test_add_validation_entry(self):
        """Test convenience method for adding validation entry."""
        collector = BrainLogCollector()
        collector.add_validation_entry("Schema", LogEntryStatus.SUCCESS)
        assert len(collector.entries) == 1
        assert collector.entries[0].type == LogEntryType.VALIDATION

    def test_add_performance_entry(self):
        """Test convenience method for adding performance entry."""
        collector = BrainLogCollector()
        collector.add_performance_entry(ttft_ms=100.0, total_ms=500.0)
        assert len(collector.entries) == 1
        assert collector.entries[0].type == LogEntryType.PERFORMANCE


class TestContextVar:
    """Test context variable management."""

    def test_get_set_collector(self):
        """Test getting and setting the collector in context."""
        # Initially None
        assert get_brain_log_collector() is None

        # Set a collector
        collector = BrainLogCollector()
        set_brain_log_collector(collector)
        assert get_brain_log_collector() is collector

        # Clear it
        set_brain_log_collector(None)
        assert get_brain_log_collector() is None
