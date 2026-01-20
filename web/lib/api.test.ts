import { describe, expect, it } from "vitest";
import {
  formatDuration,
  formatTimestamp,
  getLogTypeLabel,
  getStatusColorClass,
  getTypeColorClass,
  isBrainLogEntry,
  parseBrainLogFromData,
  type BrainLogEntry,
  type LogEntryStatus,
  type LogEntryType,
} from "./api";

// ============================================================================
// Test Fixtures
// ============================================================================

const validEntry: BrainLogEntry = {
  id: "test-123",
  timestamp: 1700000000000,
  type: "tool_call",
  title: "Test Entry",
  details: { key: "value" },
  status: "success",
  duration_ms: 150,
};

const pendingEntry: BrainLogEntry = {
  id: "pending-456",
  timestamp: 1700000001000,
  type: "input",
  title: "Pending Entry",
  details: {},
  status: "pending",
};

// ============================================================================
// isBrainLogEntry Tests
// ============================================================================

describe("isBrainLogEntry", () => {
  it("returns true for a valid entry", () => {
    expect(isBrainLogEntry(validEntry)).toBe(true);
  });

  it("returns true for entry without optional duration_ms", () => {
    const entry = { ...validEntry, duration_ms: undefined };
    expect(isBrainLogEntry(entry)).toBe(true);
  });

  it("returns false for null", () => {
    expect(isBrainLogEntry(null)).toBe(false);
  });

  it("returns false for undefined", () => {
    expect(isBrainLogEntry(undefined)).toBe(false);
  });

  it("returns false for non-object types", () => {
    expect(isBrainLogEntry("string")).toBe(false);
    expect(isBrainLogEntry(123)).toBe(false);
    expect(isBrainLogEntry(true)).toBe(false);
    expect(isBrainLogEntry([])).toBe(false);
  });

  it("returns false when id is missing", () => {
    const entry = { ...validEntry };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    delete (entry as any).id;
    expect(isBrainLogEntry(entry)).toBe(false);
  });

  it("returns false when id is not a string", () => {
    expect(isBrainLogEntry({ ...validEntry, id: 123 })).toBe(false);
  });

  it("returns false when timestamp is not a number", () => {
    expect(isBrainLogEntry({ ...validEntry, timestamp: "not-a-number" })).toBe(false);
  });

  it("returns false for invalid type values", () => {
    expect(isBrainLogEntry({ ...validEntry, type: "invalid_type" })).toBe(false);
  });

  it("returns true for all valid type values", () => {
    const types: LogEntryType[] = ["input", "routing", "tool_call", "validation", "performance"];
    types.forEach((type) => {
      expect(isBrainLogEntry({ ...validEntry, type })).toBe(true);
    });
  });

  it("returns false for invalid status values", () => {
    expect(isBrainLogEntry({ ...validEntry, status: "unknown" })).toBe(false);
  });

  it("returns true for all valid status values", () => {
    const statuses: LogEntryStatus[] = ["pending", "success", "failure"];
    statuses.forEach((status) => {
      expect(isBrainLogEntry({ ...validEntry, status })).toBe(true);
    });
  });

  it("returns false when details is null", () => {
    expect(isBrainLogEntry({ ...validEntry, details: null })).toBe(false);
  });

  it("returns false when details is not an object", () => {
    expect(isBrainLogEntry({ ...validEntry, details: "string" })).toBe(false);
  });
});

// ============================================================================
// parseBrainLogFromData Tests
// ============================================================================

describe("parseBrainLogFromData", () => {
  it("returns empty array for empty input", () => {
    expect(parseBrainLogFromData([])).toEqual([]);
  });

  it("parses direct BrainLogEntry objects", () => {
    const result = parseBrainLogFromData([validEntry, pendingEntry]);
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual(validEntry);
    expect(result[1]).toEqual(pendingEntry);
  });

  it("parses entries wrapped in brainLog property", () => {
    const wrapped = { brainLog: validEntry };
    const result = parseBrainLogFromData([wrapped]);
    expect(result).toHaveLength(1);
    expect(result[0]).toEqual(validEntry);
  });

  it("parses brainLogEntries arrays", () => {
    const batch = { brainLogEntries: [validEntry, pendingEntry] };
    const result = parseBrainLogFromData([batch]);
    expect(result).toHaveLength(2);
  });

  it("filters out invalid entries from brainLogEntries", () => {
    const batch = { brainLogEntries: [validEntry, { invalid: true }, pendingEntry] };
    const result = parseBrainLogFromData([batch]);
    expect(result).toHaveLength(2);
  });

  it("handles mixed input formats", () => {
    const data = [
      validEntry,
      { brainLog: { ...validEntry, id: "wrapped-1" } },
      { brainLogEntries: [{ ...validEntry, id: "batch-1" }] },
      "skip-this",
      null,
    ];
    const result = parseBrainLogFromData(data);
    expect(result).toHaveLength(3);
    expect(result.map((e) => e.id)).toEqual(["test-123", "wrapped-1", "batch-1"]);
  });
});

// ============================================================================
// formatTimestamp Tests
// ============================================================================

describe("formatTimestamp", () => {
  it("formats timestamp with hours, minutes, seconds, and milliseconds", () => {
    // Using a fixed timestamp for predictable testing
    const timestamp = new Date("2024-01-15T14:30:45.123Z").getTime();
    const result = formatTimestamp(timestamp);

    // The format should include milliseconds with 3 decimal places
    // The exact time depends on timezone, but format should be consistent
    expect(result).toMatch(/^\d{2}:\d{2}:\d{2}\.\d{3}$/);
  });

  it("handles midnight correctly", () => {
    const timestamp = new Date("2024-01-01T00:00:00.000Z").getTime();
    const result = formatTimestamp(timestamp);
    expect(result).toMatch(/^\d{2}:\d{2}:\d{2}\.\d{3}$/);
  });
});

// ============================================================================
// formatDuration Tests
// ============================================================================

describe("formatDuration", () => {
  it("formats milliseconds under 1000", () => {
    expect(formatDuration(0)).toBe("0ms");
    expect(formatDuration(100)).toBe("100ms");
    expect(formatDuration(999)).toBe("999ms");
  });

  it("formats milliseconds at or above 1000 as seconds", () => {
    expect(formatDuration(1000)).toBe("1.00s");
    expect(formatDuration(1500)).toBe("1.50s");
    expect(formatDuration(2345)).toBe("2.35s");
  });
});

// ============================================================================
// getLogTypeLabel Tests
// ============================================================================

describe("getLogTypeLabel", () => {
  it("returns correct label for each type", () => {
    expect(getLogTypeLabel("input")).toBe("Input");
    expect(getLogTypeLabel("routing")).toBe("Routing");
    expect(getLogTypeLabel("tool_call")).toBe("Tool Call");
    expect(getLogTypeLabel("validation")).toBe("Validation");
    expect(getLogTypeLabel("performance")).toBe("Performance");
  });
});

// ============================================================================
// getStatusColorClass Tests
// ============================================================================

describe("getStatusColorClass", () => {
  it("returns yellow for pending", () => {
    expect(getStatusColorClass("pending")).toBe("text-yellow-600");
  });

  it("returns green for success", () => {
    expect(getStatusColorClass("success")).toBe("text-green-600");
  });

  it("returns red for failure", () => {
    expect(getStatusColorClass("failure")).toBe("text-red-600");
  });
});

// ============================================================================
// getTypeColorClass Tests
// ============================================================================

describe("getTypeColorClass", () => {
  it("returns correct classes for each type", () => {
    expect(getTypeColorClass("input")).toBe("bg-blue-500/10 text-blue-600 dark:text-blue-400");
    expect(getTypeColorClass("routing")).toBe(
      "bg-purple-500/10 text-purple-600 dark:text-purple-400"
    );
    expect(getTypeColorClass("tool_call")).toBe(
      "bg-orange-500/10 text-orange-600 dark:text-orange-400"
    );
    expect(getTypeColorClass("validation")).toBe(
      "bg-green-500/10 text-green-600 dark:text-green-400"
    );
    expect(getTypeColorClass("performance")).toBe(
      "bg-slate-500/10 text-slate-600 dark:text-slate-400"
    );
  });
});
