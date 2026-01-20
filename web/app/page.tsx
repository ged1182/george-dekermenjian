"use client";

import { cn } from "@/lib/utils";
import { ChatInterface } from "@/components/chat";
import { BrainLog, GlassBoxToggle, useGlassBox } from "@/components/glass-box";
import { Github, BoxIcon } from "lucide-react";

export default function Page() {
  const { isEnabled } = useGlassBox();

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="flex flex-1 overflow-hidden">
        {/* Chat Area */}
        <div
          className={cn(
            "flex-1 transition-all duration-300",
            isEnabled && "lg:mr-0"
          )}
        >
          <ChatInterface className="h-full" />
        </div>

        {/* Brain Log Panel - slides in from right when enabled */}
        <div
          className={cn(
            "hidden overflow-hidden transition-all duration-300 ease-in-out lg:block",
            isEnabled ? "w-96 border-l" : "w-0"
          )}
        >
          {isEnabled && <BrainLog className="h-full w-96" showCloseButton />}
        </div>
      </main>
    </div>
  );
}

// ============================================================================
// Header Component
// ============================================================================

function Header() {
  return (
    <header className="flex items-center justify-between border-b px-4 py-3">
      {/* Logo / Title */}
      <div className="flex items-center gap-3">
        <div className="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <BoxIcon className="size-4" />
        </div>
        <div className="flex flex-col">
          <h1 className="font-semibold text-sm leading-none">Glass Box</h1>
          <p className="text-xs text-muted-foreground">Portfolio</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <a
          href="https://github.com/george-dekermenjian"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="View on GitHub"
          className="inline-flex size-8 items-center justify-center rounded-md text-sm font-medium hover:bg-muted hover:text-foreground transition-colors"
        >
          <Github className="size-4" />
        </a>
        <GlassBoxToggle showLabel className="hidden sm:flex" />
        <GlassBoxToggle className="sm:hidden" />
      </div>
    </header>
  );
}
