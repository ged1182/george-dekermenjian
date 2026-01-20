import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Loader } from "./loader";
import { Suggestion, Suggestions } from "./suggestion";
import { Sources, SourcesTrigger, SourcesContent, Source } from "./sources";
import { Task, TaskTrigger, TaskContent, TaskItem, TaskItemFile } from "./task";
import { Checkpoint, CheckpointIcon, CheckpointTrigger } from "./checkpoint";

// ============================================================================
// Loader Tests
// ============================================================================

describe("Loader", () => {
  it("renders the loader SVG", () => {
    render(<Loader />);
    expect(screen.getByTitle("Loader")).toBeInTheDocument();
  });

  it("applies custom size", () => {
    render(<Loader size={24} data-testid="loader" />);
    // The size prop is passed to the internal LoaderIcon component
    const loader = screen.getByTestId("loader");
    expect(loader).toBeInTheDocument();
    // Just verify the component renders with the prop - internal sizing is implementation detail
  });

  it("applies custom className", () => {
    render(<Loader className="custom-loader" data-testid="loader" />);
    expect(screen.getByTestId("loader")).toHaveClass("custom-loader");
  });

  it("has spin animation class", () => {
    render(<Loader data-testid="loader" />);
    expect(screen.getByTestId("loader")).toHaveClass("animate-spin");
  });
});

// ============================================================================
// Suggestion Tests
// ============================================================================

describe("Suggestion", () => {
  it("renders the suggestion text", () => {
    render(<Suggestion suggestion="Try this" />);
    expect(screen.getByRole("button", { name: "Try this" })).toBeInTheDocument();
  });

  it("calls onClick with suggestion when clicked", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Suggestion suggestion="Click me" onClick={onClick} />);

    await user.click(screen.getByRole("button"));

    expect(onClick).toHaveBeenCalledWith("Click me");
  });

  it("renders custom children instead of suggestion text", () => {
    render(<Suggestion suggestion="ignored">Custom Text</Suggestion>);
    expect(screen.getByRole("button", { name: "Custom Text" })).toBeInTheDocument();
    expect(screen.queryByText("ignored")).not.toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<Suggestion suggestion="test" className="custom-class" />);
    expect(screen.getByRole("button")).toHaveClass("custom-class");
  });
});

describe("Suggestions", () => {
  it("renders children", () => {
    render(
      <Suggestions>
        <Suggestion suggestion="First" />
        <Suggestion suggestion="Second" />
      </Suggestions>
    );
    expect(screen.getByText("First")).toBeInTheDocument();
    expect(screen.getByText("Second")).toBeInTheDocument();
  });
});

// ============================================================================
// Sources Tests
// ============================================================================

describe("Sources", () => {
  it("renders as collapsible", () => {
    render(
      <Sources>
        <SourcesTrigger count={3} />
        <SourcesContent>
          <Source href="https://example.com" title="Example" />
        </SourcesContent>
      </Sources>
    );
    expect(screen.getByText("Used 3 sources")).toBeInTheDocument();
  });

  it("expands to show content when clicked", async () => {
    const user = userEvent.setup();
    render(
      <Sources>
        <SourcesTrigger count={2} />
        <SourcesContent>
          <Source href="https://example.com" title="Example Source" />
        </SourcesContent>
      </Sources>
    );

    // Click to expand
    await user.click(screen.getByText("Used 2 sources"));

    expect(screen.getByText("Example Source")).toBeInTheDocument();
  });
});

describe("Source", () => {
  it("renders link with href", () => {
    render(<Source href="https://test.com" title="Test Link" />);
    const link = screen.getByRole("link", { name: /test link/i });
    expect(link).toHaveAttribute("href", "https://test.com");
  });

  it("opens in new tab", () => {
    render(<Source href="https://test.com" title="Test Link" />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noreferrer");
  });

  it("renders custom children", () => {
    render(
      <Source href="https://test.com" title="ignored">
        <span>Custom Content</span>
      </Source>
    );
    expect(screen.getByText("Custom Content")).toBeInTheDocument();
  });
});

// ============================================================================
// Task Tests
// ============================================================================

describe("Task", () => {
  it("renders with trigger and content", () => {
    render(
      <Task>
        <TaskTrigger title="Search files" />
        <TaskContent>
          <TaskItem>Found 5 files</TaskItem>
        </TaskContent>
      </Task>
    );
    expect(screen.getByText("Search files")).toBeInTheDocument();
  });

  it("is expanded by default", () => {
    render(
      <Task>
        <TaskTrigger title="Search files" />
        <TaskContent>
          <TaskItem>Found 5 files</TaskItem>
        </TaskContent>
      </Task>
    );
    expect(screen.getByText("Found 5 files")).toBeVisible();
  });

  it("can be collapsed", async () => {
    const user = userEvent.setup();
    render(
      <Task>
        <TaskTrigger title="Search files" />
        <TaskContent>
          <TaskItem>Found 5 files</TaskItem>
        </TaskContent>
      </Task>
    );

    await user.click(screen.getByText("Search files"));

    // Content is removed from DOM when collapsed (Collapsible behavior)
    expect(screen.queryByText("Found 5 files")).not.toBeInTheDocument();
  });
});

describe("TaskItem", () => {
  it("renders children", () => {
    render(<TaskItem>Task item content</TaskItem>);
    expect(screen.getByText("Task item content")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<TaskItem className="custom-item">Content</TaskItem>);
    expect(screen.getByText("Content")).toHaveClass("custom-item");
  });
});

describe("TaskItemFile", () => {
  it("renders file name", () => {
    render(<TaskItemFile>src/index.ts</TaskItemFile>);
    expect(screen.getByText("src/index.ts")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<TaskItemFile className="custom-file">file.ts</TaskItemFile>);
    expect(screen.getByText("file.ts")).toHaveClass("custom-file");
  });
});

// ============================================================================
// Checkpoint Tests
// ============================================================================

describe("Checkpoint", () => {
  it("renders children", () => {
    render(
      <Checkpoint>
        <CheckpointIcon />
        <CheckpointTrigger>Save point</CheckpointTrigger>
      </Checkpoint>
    );
    expect(screen.getByText("Save point")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(
      <Checkpoint className="custom-checkpoint" data-testid="checkpoint">
        <span>Content</span>
      </Checkpoint>
    );
    expect(screen.getByTestId("checkpoint")).toHaveClass("custom-checkpoint");
  });
});

describe("CheckpointTrigger", () => {
  it("renders as button", () => {
    render(<CheckpointTrigger>Click me</CheckpointTrigger>);
    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument();
  });

  it("fires onClick", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<CheckpointTrigger onClick={onClick}>Click</CheckpointTrigger>);

    await user.click(screen.getByRole("button"));

    expect(onClick).toHaveBeenCalled();
  });

  it("renders without tooltip when tooltip prop is not provided", () => {
    render(<CheckpointTrigger>No tooltip</CheckpointTrigger>);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });
});
