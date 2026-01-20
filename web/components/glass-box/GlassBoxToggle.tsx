"use client";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { EyeIcon, EyeOffIcon } from "lucide-react";
import type { ComponentProps } from "react";
import { useGlassBox } from "./GlassBoxProvider";

// ============================================================================
// GlassBoxToggle Component
// ============================================================================

export type GlassBoxToggleProps = Omit<
  ComponentProps<typeof Button>,
  "onClick" | "children"
> & {
  /** Show label text next to icon */
  showLabel?: boolean;
};

export function GlassBoxToggle({
  className,
  showLabel = false,
  variant = "ghost",
  size = showLabel ? "default" : "icon",
  ...props
}: GlassBoxToggleProps) {
  const { isEnabled, toggle } = useGlassBox();

  const button = (
    <Button
      className={cn(
        "gap-2 transition-colors",
        isEnabled && "bg-primary/10 text-primary hover:bg-primary/20",
        className
      )}
      onClick={toggle}
      size={size}
      variant={variant}
      aria-pressed={isEnabled}
      aria-label={isEnabled ? "Disable Glass Box mode" : "Enable Glass Box mode"}
      {...props}
    >
      {isEnabled ? (
        <EyeIcon className="size-4" />
      ) : (
        <EyeOffIcon className="size-4" />
      )}
      {showLabel && (
        <span className="text-sm font-medium">
          {isEnabled ? "Glass Box" : "Opaque"}
        </span>
      )}
    </Button>
  );

  if (showLabel) {
    return button;
  }

  return (
    <Tooltip>
      <TooltipTrigger render={button} />
      <TooltipContent side="bottom" align="end">
        <p>{isEnabled ? "Disable Glass Box mode" : "Enable Glass Box mode"}</p>
      </TooltipContent>
    </Tooltip>
  );
}
