"use client";

import { Badge } from "@/components/ui/badge";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";
import {
  formatDuration,
  formatTimestamp,
  getLogTypeLabel,
  getStatusColorClass,
  getTypeColorClass,
  type BrainLogEntry,
  type LogEntryStatus,
  type LogEntryType,
} from "@/lib/api";
import {
  CheckCircleIcon,
  ChevronDownIcon,
  ClockIcon,
  FileInputIcon,
  GaugeIcon,
  RouteIcon,
  ShieldCheckIcon,
  WrenchIcon,
  XCircleIcon,
} from "lucide-react";
import type { ComponentProps, ReactNode } from "react";
import { memo, useState } from "react";
import { CodeBlock } from "@/components/ai-elements/code-block";

// ============================================================================
// Icon Mapping
// ============================================================================

function getTypeIcon(type: LogEntryType): ReactNode {
  const icons: Record<LogEntryType, ReactNode> = {
    input: <FileInputIcon className="size-3.5" />,
    routing: <RouteIcon className="size-3.5" />,
    tool_call: <WrenchIcon className="size-3.5" />,
    validation: <ShieldCheckIcon className="size-3.5" />,
    performance: <GaugeIcon className="size-3.5" />,
  };
  return icons[type];
}

function getStatusIcon(status: LogEntryStatus): ReactNode {
  const icons: Record<LogEntryStatus, ReactNode> = {
    pending: <ClockIcon className="size-3 animate-pulse" />,
    success: <CheckCircleIcon className="size-3" />,
    failure: <XCircleIcon className="size-3" />,
  };
  return icons[status];
}

// ============================================================================
// LogEntry Component
// ============================================================================

export type LogEntryProps = ComponentProps<"div"> & {
  entry: BrainLogEntry;
  defaultOpen?: boolean;
};

export const LogEntry = memo(function LogEntry({
  entry,
  defaultOpen = false,
  className,
  ...props
}: LogEntryProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const hasDetails =
    entry.details && Object.keys(entry.details).length > 0;

  return (
    <Collapsible
      open={isOpen}
      onOpenChange={setIsOpen}
      className={cn("group", className)}
      {...props}
    >
      <CollapsibleTrigger
        className={cn(
          "flex w-full items-start gap-3 rounded-md p-2 text-left transition-colors",
          "hover:bg-muted/50",
          hasDetails && "cursor-pointer"
        )}
        disabled={!hasDetails}
      >
        {/* Type Icon */}
        <div
          className={cn(
            "mt-0.5 flex size-6 shrink-0 items-center justify-center rounded",
            getTypeColorClass(entry.type)
          )}
        >
          {getTypeIcon(entry.type)}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-1">
          {/* Header Row */}
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm truncate">{entry.title}</span>
            <Badge
              variant="secondary"
              className={cn(
                "shrink-0 gap-1 px-1.5 py-0.5 text-xs",
                getStatusColorClass(entry.status)
              )}
            >
              {getStatusIcon(entry.status)}
              <span className="capitalize">{entry.status}</span>
            </Badge>
          </div>

          {/* Meta Row */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="font-mono">{formatTimestamp(entry.timestamp)}</span>
            <span className="text-border">|</span>
            <span>{getLogTypeLabel(entry.type)}</span>
            {entry.duration_ms !== undefined && (
              <>
                <span className="text-border">|</span>
                <span>{formatDuration(entry.duration_ms)}</span>
              </>
            )}
          </div>
        </div>

        {/* Expand Icon */}
        {hasDetails && (
          <ChevronDownIcon
            className={cn(
              "size-4 shrink-0 text-muted-foreground transition-transform",
              isOpen && "rotate-180"
            )}
          />
        )}
      </CollapsibleTrigger>

      {/* Collapsible Details */}
      {hasDetails && (
        <CollapsibleContent
          className={cn(
            "overflow-hidden",
            "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:slide-out-to-top-1",
            "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:slide-in-from-top-1"
          )}
        >
          <div className="ml-9 mt-1 rounded-md bg-muted/30 p-2">
            <CodeBlock
              code={JSON.stringify(entry.details, null, 2)}
              language="json"
            />
          </div>
        </CollapsibleContent>
      )}
    </Collapsible>
  );
});

// ============================================================================
// LogEntryCompact - For inline/minimal display
// ============================================================================

export type LogEntryCompactProps = ComponentProps<"div"> & {
  entry: BrainLogEntry;
};

export const LogEntryCompact = memo(function LogEntryCompact({
  entry,
  className,
  ...props
}: LogEntryCompactProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 py-1 text-xs text-muted-foreground",
        className
      )}
      {...props}
    >
      <div
        className={cn(
          "flex size-5 shrink-0 items-center justify-center rounded",
          getTypeColorClass(entry.type)
        )}
      >
        {getTypeIcon(entry.type)}
      </div>
      <span className="truncate">{entry.title}</span>
      <div className={cn("shrink-0", getStatusColorClass(entry.status))}>
        {getStatusIcon(entry.status)}
      </div>
    </div>
  );
});
