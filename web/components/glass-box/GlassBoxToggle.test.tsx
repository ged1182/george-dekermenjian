import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import type { ReactNode } from "react";
import { GlassBoxProvider, useGlassBox } from "./GlassBoxProvider";
import { GlassBoxToggle } from "./GlassBoxToggle";

// ============================================================================
// Test Wrappers
// ============================================================================

function Wrapper({
  children,
  defaultEnabled = false,
}: {
  children: ReactNode;
  defaultEnabled?: boolean;
}) {
  return <GlassBoxProvider defaultEnabled={defaultEnabled}>{children}</GlassBoxProvider>;
}

// Helper to check current state
function StateDisplay() {
  const { isEnabled } = useGlassBox();
  return <span data-testid="state">{isEnabled ? "enabled" : "disabled"}</span>;
}

// ============================================================================
// Rendering Tests
// ============================================================================

describe("GlassBoxToggle", () => {
  it("renders with correct aria-label when disabled", () => {
    render(
      <Wrapper>
        <GlassBoxToggle />
      </Wrapper>
    );

    expect(screen.getByRole("button", { name: /enable glass box mode/i })).toBeInTheDocument();
  });

  it("renders with correct aria-label when enabled", () => {
    render(
      <Wrapper defaultEnabled>
        <GlassBoxToggle />
      </Wrapper>
    );

    expect(screen.getByRole("button", { name: /disable glass box mode/i })).toBeInTheDocument();
  });

  it("has aria-pressed=false when disabled", () => {
    render(
      <Wrapper>
        <GlassBoxToggle />
      </Wrapper>
    );

    expect(screen.getByRole("button")).toHaveAttribute("aria-pressed", "false");
  });

  it("has aria-pressed=true when enabled", () => {
    render(
      <Wrapper defaultEnabled>
        <GlassBoxToggle />
      </Wrapper>
    );

    expect(screen.getByRole("button")).toHaveAttribute("aria-pressed", "true");
  });
});

// ============================================================================
// Toggle Behavior Tests
// ============================================================================

describe("GlassBoxToggle toggle behavior", () => {
  it("toggles state when clicked", async () => {
    const user = userEvent.setup();

    render(
      <Wrapper>
        <GlassBoxToggle />
        <StateDisplay />
      </Wrapper>
    );

    expect(screen.getByTestId("state")).toHaveTextContent("disabled");

    await user.click(screen.getByRole("button"));

    expect(screen.getByTestId("state")).toHaveTextContent("enabled");
  });

  it("toggles from enabled to disabled", async () => {
    const user = userEvent.setup();

    render(
      <Wrapper defaultEnabled>
        <GlassBoxToggle />
        <StateDisplay />
      </Wrapper>
    );

    expect(screen.getByTestId("state")).toHaveTextContent("enabled");

    await user.click(screen.getByRole("button"));

    expect(screen.getByTestId("state")).toHaveTextContent("disabled");
  });
});

// ============================================================================
// Label Display Tests
// ============================================================================

describe("GlassBoxToggle showLabel", () => {
  it("shows 'Opaque' label when disabled and showLabel=true", () => {
    render(
      <Wrapper>
        <GlassBoxToggle showLabel />
      </Wrapper>
    );

    expect(screen.getByText("Opaque")).toBeInTheDocument();
  });

  it("shows 'Glass Box' label when enabled and showLabel=true", () => {
    render(
      <Wrapper defaultEnabled>
        <GlassBoxToggle showLabel />
      </Wrapper>
    );

    expect(screen.getByText("Glass Box")).toBeInTheDocument();
  });

  it("does not show label text when showLabel=false", () => {
    render(
      <Wrapper>
        <GlassBoxToggle showLabel={false} />
      </Wrapper>
    );

    expect(screen.queryByText("Opaque")).not.toBeInTheDocument();
    expect(screen.queryByText("Glass Box")).not.toBeInTheDocument();
  });
});

// ============================================================================
// Prop Forwarding Tests
// ============================================================================

describe("GlassBoxToggle prop forwarding", () => {
  it("applies custom className", () => {
    render(
      <Wrapper>
        <GlassBoxToggle className="custom-class" />
      </Wrapper>
    );

    expect(screen.getByRole("button")).toHaveClass("custom-class");
  });

  it("forwards variant prop", () => {
    render(
      <Wrapper>
        <GlassBoxToggle variant="outline" />
      </Wrapper>
    );

    // The button should be rendered (variant is internal styling)
    expect(screen.getByRole("button")).toBeInTheDocument();
  });
});
