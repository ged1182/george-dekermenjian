"use client";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { BrainIcon, TrashIcon, XIcon } from "lucide-react";
import type { ComponentProps } from "react";
import { memo, useEffect, useRef } from "react";
import { useGlassBox } from "./GlassBoxProvider";
import { LogEntry } from "./LogEntry";

// ============================================================================
// BrainLog Panel Component
// ============================================================================

export type BrainLogProps = Omit<ComponentProps<"aside">, "children"> & {
  /** Whether to show a close button */
  showCloseButton?: boolean;
  /** Called when close button is clicked */
  onClose?: () => void;
};

export const BrainLog = memo(function BrainLog({
  className,
  showCloseButton = false,
  onClose,
  ...props
}: BrainLogProps) {
  const { entries, clearEntries, disable } = useGlassBox();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new entries arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [entries.length]);

  const handleClose = () => {
    if (onClose) {
      onClose();
    } else {
      disable();
    }
  };

  return (
    <aside
      className={cn(
        "flex h-full flex-col overflow-hidden border-l bg-card",
        className
      )}
      aria-label="Brain Log - Agent reasoning and decisions"
      {...props}
    >
      {/* Header */}
      <div className="flex-shrink-0 flex items-center justify-between gap-2 border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <BrainIcon className="size-4 text-primary" />
          <h2 className="font-semibold text-sm">Brain Log</h2>
          {entries.length > 0 && (
            <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
              {entries.length}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {entries.length > 0 && (
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={clearEntries}
              aria-label="Clear log entries"
            >
              <TrashIcon className="size-3.5" />
            </Button>
          )}
          {showCloseButton && (
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={handleClose}
              aria-label="Close Brain Log"
            >
              <XIcon className="size-3.5" />
            </Button>
          )}
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 min-h-0">
        <div ref={scrollRef} className="p-2">
          {entries.length === 0 ? (
            <BrainLogEmptyState />
          ) : (
            <div className="space-y-1">
              {entries.map((entry, index) => (
                <LogEntry
                  key={entry.id}
                  entry={entry}
                  // Auto-expand the most recent entry
                  defaultOpen={index === entries.length - 1}
                />
              ))}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer with stats */}
      {entries.length > 0 && <BrainLogFooter />}
    </aside>
  );
});

// ============================================================================
// Empty State
// ============================================================================

function BrainLogEmptyState() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
      <div className="flex size-12 items-center justify-center rounded-full bg-muted">
        <BrainIcon className="size-6 text-muted-foreground" />
      </div>
      <div className="space-y-1">
        <p className="font-medium text-sm">No activity yet</p>
        <p className="text-xs text-muted-foreground max-w-[200px]">
          Send a message to see agent reasoning and decisions here
        </p>
      </div>
    </div>
  );
}

// ============================================================================
// Footer with Stats
// ============================================================================

function BrainLogFooter() {
  const { entries } = useGlassBox();

  // Calculate stats
  const stats = {
    total: entries.length,
    pending: entries.filter((e) => e.status === "pending").length,
    success: entries.filter((e) => e.status === "success").length,
    failure: entries.filter((e) => e.status === "failure").length,
    totalDuration: entries
      .filter((e) => e.duration_ms !== undefined)
      .reduce((sum, e) => sum + (e.duration_ms || 0), 0),
  };

  return (
    <div className="flex-shrink-0 border-t px-4 py-2">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="size-2 rounded-full bg-green-500" />
            {stats.success}
          </span>
          {stats.pending > 0 && (
            <span className="flex items-center gap-1">
              <span className="size-2 rounded-full bg-yellow-500" />
              {stats.pending}
            </span>
          )}
          {stats.failure > 0 && (
            <span className="flex items-center gap-1">
              <span className="size-2 rounded-full bg-red-500" />
              {stats.failure}
            </span>
          )}
        </div>
        {stats.totalDuration > 0 && (
          <span className="font-mono">
            {stats.totalDuration < 1000
              ? `${stats.totalDuration}ms`
              : `${(stats.totalDuration / 1000).toFixed(2)}s`}
          </span>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// BrainLogInline - Compact view for mobile or inline display
// ============================================================================

export type BrainLogInlineProps = ComponentProps<"div">;

export const BrainLogInline = memo(function BrainLogInline({
  className,
  ...props
}: BrainLogInlineProps) {
  const { entries, isEnabled } = useGlassBox();

  if (!isEnabled || entries.length === 0) {
    return null;
  }

  // Show only the last few entries
  const recentEntries = entries.slice(-3);

  return (
    <div
      className={cn(
        "rounded-md border bg-muted/30 p-2 text-xs",
        className
      )}
      {...props}
    >
      <div className="flex items-center gap-2 mb-2">
        <BrainIcon className="size-3 text-primary" />
        <span className="font-medium text-muted-foreground">Brain Log</span>
      </div>
      <div className="space-y-1">
        {recentEntries.map((entry) => (
          <div
            key={entry.id}
            className="flex items-center gap-2 text-muted-foreground"
          >
            <span
              className={cn(
                "size-1.5 rounded-full",
                entry.status === "success" && "bg-green-500",
                entry.status === "pending" && "bg-yellow-500",
                entry.status === "failure" && "bg-red-500"
              )}
            />
            <span className="truncate">{entry.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
});
