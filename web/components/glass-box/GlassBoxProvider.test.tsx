import { renderHook, act } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { ReactNode } from "react";
import type { BrainLogEntry } from "@/lib/api";
import { GlassBoxProvider, useGlassBox } from "./GlassBoxProvider";

// ============================================================================
// Test Fixtures
// ============================================================================

const createEntry = (overrides: Partial<BrainLogEntry> = {}): BrainLogEntry => ({
  id: "test-" + Math.random().toString(36).slice(2, 9),
  timestamp: Date.now(),
  type: "tool_call",
  title: "Test Entry",
  details: {},
  status: "success",
  ...overrides,
});

// Wrapper component for the hook
const wrapper = ({ children }: { children: ReactNode }) => (
  <GlassBoxProvider>{children}</GlassBoxProvider>
);

const wrapperWithDefaultEnabled = ({ children }: { children: ReactNode }) => (
  <GlassBoxProvider defaultEnabled>{children}</GlassBoxProvider>
);

// ============================================================================
// useGlassBox Hook Tests
// ============================================================================

describe("useGlassBox", () => {
  it("throws error when used outside provider", () => {
    // Suppress console.error for this test since React logs the error
    const originalError = console.error;
    console.error = () => {};

    expect(() => {
      renderHook(() => useGlassBox());
    }).toThrow("useGlassBox must be used within a GlassBoxProvider");

    console.error = originalError;
  });

  it("has correct initial state", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });

    expect(result.current.isEnabled).toBe(false);
    expect(result.current.entries).toEqual([]);
  });

  it("respects defaultEnabled prop", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper: wrapperWithDefaultEnabled });

    expect(result.current.isEnabled).toBe(true);
  });
});

// ============================================================================
// Toggle State Tests
// ============================================================================

describe("toggle, enable, disable", () => {
  it("toggle() flips isEnabled", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });

    expect(result.current.isEnabled).toBe(false);

    act(() => {
      result.current.toggle();
    });
    expect(result.current.isEnabled).toBe(true);

    act(() => {
      result.current.toggle();
    });
    expect(result.current.isEnabled).toBe(false);
  });

  it("enable() sets isEnabled to true", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });

    act(() => {
      result.current.enable();
    });
    expect(result.current.isEnabled).toBe(true);

    // Calling enable again should keep it true
    act(() => {
      result.current.enable();
    });
    expect(result.current.isEnabled).toBe(true);
  });

  it("disable() sets isEnabled to false", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper: wrapperWithDefaultEnabled });

    expect(result.current.isEnabled).toBe(true);

    act(() => {
      result.current.disable();
    });
    expect(result.current.isEnabled).toBe(false);

    // Calling disable again should keep it false
    act(() => {
      result.current.disable();
    });
    expect(result.current.isEnabled).toBe(false);
  });
});

// ============================================================================
// Entry Management Tests
// ============================================================================

describe("addEntry", () => {
  it("adds a new entry", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entry = createEntry({ id: "entry-1" });

    act(() => {
      result.current.addEntry(entry);
    });

    expect(result.current.entries).toHaveLength(1);
    expect(result.current.entries[0]).toEqual(entry);
  });

  it("adds multiple entries sequentially", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entry1 = createEntry({ id: "entry-1" });
    const entry2 = createEntry({ id: "entry-2" });

    act(() => {
      result.current.addEntry(entry1);
    });
    act(() => {
      result.current.addEntry(entry2);
    });

    expect(result.current.entries).toHaveLength(2);
    expect(result.current.entries[0].id).toBe("entry-1");
    expect(result.current.entries[1].id).toBe("entry-2");
  });

  it("updates existing entry with same ID", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entry1 = createEntry({ id: "entry-1", status: "pending" });
    const entry1Updated = { ...entry1, status: "success" as const, duration_ms: 150 };

    act(() => {
      result.current.addEntry(entry1);
    });
    expect(result.current.entries[0].status).toBe("pending");

    act(() => {
      result.current.addEntry(entry1Updated);
    });

    expect(result.current.entries).toHaveLength(1);
    expect(result.current.entries[0].status).toBe("success");
    expect(result.current.entries[0].duration_ms).toBe(150);
  });
});

describe("addEntries", () => {
  it("adds multiple entries at once", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entries = [
      createEntry({ id: "batch-1" }),
      createEntry({ id: "batch-2" }),
      createEntry({ id: "batch-3" }),
    ];

    act(() => {
      result.current.addEntries(entries);
    });

    expect(result.current.entries).toHaveLength(3);
    expect(result.current.entries.map((e) => e.id)).toEqual(["batch-1", "batch-2", "batch-3"]);
  });

  it("updates existing entries in batch", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entry1 = createEntry({ id: "entry-1", status: "pending" });
    const entry2 = createEntry({ id: "entry-2", status: "pending" });

    act(() => {
      result.current.addEntries([entry1, entry2]);
    });

    const updatedEntries = [
      { ...entry1, status: "success" as const },
      createEntry({ id: "entry-3" }),
    ];

    act(() => {
      result.current.addEntries(updatedEntries);
    });

    expect(result.current.entries).toHaveLength(3);
    expect(result.current.entries[0].status).toBe("success");
    expect(result.current.entries[2].id).toBe("entry-3");
  });

  it("handles empty array", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });

    act(() => {
      result.current.addEntries([]);
    });

    expect(result.current.entries).toEqual([]);
  });
});

describe("clearEntries", () => {
  it("removes all entries", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entries = [createEntry({ id: "entry-1" }), createEntry({ id: "entry-2" })];

    act(() => {
      result.current.addEntries(entries);
    });
    expect(result.current.entries).toHaveLength(2);

    act(() => {
      result.current.clearEntries();
    });

    expect(result.current.entries).toEqual([]);
  });

  it("can be called on empty entries", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });

    act(() => {
      result.current.clearEntries();
    });

    expect(result.current.entries).toEqual([]);
  });
});

describe("updateEntry", () => {
  it("updates specific fields of an entry", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entry = createEntry({ id: "entry-1", status: "pending", title: "Original Title" });

    act(() => {
      result.current.addEntry(entry);
    });

    act(() => {
      result.current.updateEntry("entry-1", {
        status: "success",
        duration_ms: 200,
      });
    });

    expect(result.current.entries[0].status).toBe("success");
    expect(result.current.entries[0].duration_ms).toBe(200);
    expect(result.current.entries[0].title).toBe("Original Title");
  });

  it("does not affect entries with different IDs", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entry1 = createEntry({ id: "entry-1", status: "pending" });
    const entry2 = createEntry({ id: "entry-2", status: "pending" });

    act(() => {
      result.current.addEntries([entry1, entry2]);
    });

    act(() => {
      result.current.updateEntry("entry-1", { status: "success" });
    });

    expect(result.current.entries[0].status).toBe("success");
    expect(result.current.entries[1].status).toBe("pending");
  });

  it("does nothing if ID not found", () => {
    const { result } = renderHook(() => useGlassBox(), { wrapper });
    const entry = createEntry({ id: "entry-1", status: "pending" });

    act(() => {
      result.current.addEntry(entry);
    });

    act(() => {
      result.current.updateEntry("non-existent", { status: "success" });
    });

    expect(result.current.entries).toHaveLength(1);
    expect(result.current.entries[0].status).toBe("pending");
  });
});
