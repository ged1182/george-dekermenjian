import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";
import type { BrainLogEntry } from "@/lib/api";
import { GlassBoxProvider, useGlassBox } from "./GlassBoxProvider";
import { BrainLog } from "./BrainLog";

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

// Wrapper that allows setting initial entries
function TestWrapper({
  children,
  entries = [],
}: {
  children: ReactNode;
  entries?: BrainLogEntry[];
}) {
  return (
    <GlassBoxProvider defaultEnabled>
      <EntryInjector entries={entries}>{children}</EntryInjector>
    </GlassBoxProvider>
  );
}

// Component to inject entries into the context
function EntryInjector({ children, entries }: { children: ReactNode; entries: BrainLogEntry[] }) {
  const { addEntries } = useGlassBox();

  // Add entries on first render only
  if (entries.length > 0) {
    // Use setTimeout to avoid updating state during render
    setTimeout(() => addEntries(entries), 0);
  }

  return <>{children}</>;
}

// ============================================================================
// Rendering Tests
// ============================================================================

describe("BrainLog", () => {
  it("renders the header with Brain Log title", () => {
    render(
      <TestWrapper>
        <BrainLog />
      </TestWrapper>
    );

    expect(screen.getByText("Brain Log")).toBeInTheDocument();
  });

  it("renders empty state when no entries", () => {
    render(
      <TestWrapper>
        <BrainLog />
      </TestWrapper>
    );

    expect(screen.getByText("No activity yet")).toBeInTheDocument();
    expect(
      screen.getByText("Send a message to see agent reasoning and decisions here")
    ).toBeInTheDocument();
  });

  it("has correct aria-label", () => {
    render(
      <TestWrapper>
        <BrainLog />
      </TestWrapper>
    );

    expect(screen.getByRole("complementary", { name: /brain log/i })).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(
      <TestWrapper>
        <BrainLog className="custom-class" data-testid="brain-log" />
      </TestWrapper>
    );

    expect(screen.getByTestId("brain-log")).toHaveClass("custom-class");
  });
});

// ============================================================================
// Close Button Tests
// ============================================================================

describe("BrainLog close button", () => {
  it("does not show close button by default", () => {
    render(
      <TestWrapper>
        <BrainLog />
      </TestWrapper>
    );

    expect(screen.queryByRole("button", { name: /close brain log/i })).not.toBeInTheDocument();
  });

  it("shows close button when showCloseButton is true", () => {
    render(
      <TestWrapper>
        <BrainLog showCloseButton />
      </TestWrapper>
    );

    expect(screen.getByRole("button", { name: /close brain log/i })).toBeInTheDocument();
  });

  it("calls onClose when close button clicked", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <TestWrapper>
        <BrainLog showCloseButton onClose={onClose} />
      </TestWrapper>
    );

    await user.click(screen.getByRole("button", { name: /close brain log/i }));

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});

// ============================================================================
// Entry Count Badge Tests
// ============================================================================

describe("BrainLog entry count", () => {
  it("does not show count badge when no entries", () => {
    render(
      <TestWrapper>
        <BrainLog />
      </TestWrapper>
    );

    // The entry count badge should not be present
    const header = screen.getByText("Brain Log").closest("div");
    expect(header).not.toHaveTextContent(/^\d+$/);
  });
});

// ============================================================================
// Clear Button Tests
// ============================================================================

describe("BrainLog clear button", () => {
  it("does not show clear button when no entries", () => {
    render(
      <TestWrapper>
        <BrainLog />
      </TestWrapper>
    );

    expect(screen.queryByRole("button", { name: /clear log entries/i })).not.toBeInTheDocument();
  });
});

// ============================================================================
// Integration with entries
// ============================================================================

describe("BrainLog with entries", () => {
  it("renders entry titles", async () => {
    const entries = [
      createEntry({ id: "1", title: "First Entry" }),
      createEntry({ id: "2", title: "Second Entry" }),
    ];

    render(
      <GlassBoxProvider defaultEnabled>
        <BrainLogWithEntries entries={entries} />
      </GlassBoxProvider>
    );

    // Wait for entries to be rendered
    expect(await screen.findByText("First Entry")).toBeInTheDocument();
    expect(await screen.findByText("Second Entry")).toBeInTheDocument();
  });

  it("shows clear button when entries exist", async () => {
    const entries = [createEntry({ id: "1", title: "Test Entry" })];

    render(
      <GlassBoxProvider defaultEnabled>
        <BrainLogWithEntries entries={entries} />
      </GlassBoxProvider>
    );

    // Wait for entries and clear button
    expect(await screen.findByText("Test Entry")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /clear log entries/i })).toBeInTheDocument();
  });

  it("shows entry count badge when entries exist", async () => {
    const entries = [
      createEntry({ id: "1", title: "Entry One" }),
      createEntry({ id: "2", title: "Entry Two" }),
      createEntry({ id: "3", title: "Entry Three" }),
    ];

    render(
      <GlassBoxProvider defaultEnabled>
        <BrainLogWithEntries entries={entries} />
      </GlassBoxProvider>
    );

    // Wait for entries to load
    await screen.findByText("Entry One");

    // Find the count badge - it has specific styling that distinguishes it from footer stats
    const countBadges = screen.getAllByText("3");
    // The count badge is the one with bg-muted class (the entry count in header)
    const countBadge = countBadges.find((el) => el.classList.contains("bg-muted"));
    expect(countBadge).toBeInTheDocument();
  });
});

// Helper component to add entries and render BrainLog
function BrainLogWithEntries({ entries }: { entries: BrainLogEntry[] }) {
  const { addEntries, entries: currentEntries } = useGlassBox();

  // Add entries if not already added
  if (currentEntries.length === 0 && entries.length > 0) {
    setTimeout(() => addEntries(entries), 0);
  }

  return <BrainLog />;
}
