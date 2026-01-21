"use client";

import { useCallback, useState } from "react";
import { cn } from "@/lib/utils";
import { ChatInterface } from "@/components/chat";
import { BrainLog, useGlassBox } from "@/components/glass-box";
import { ProfilePanel } from "@/components/profile";
import { useKeyboardShortcuts } from "@/hooks";
import { Github, BoxIcon, User, BrainCircuit } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";

export default function Page() {
  const { rightPanelMode, togglePanel, setRightPanelMode, entries } = useGlassBox();
  const [mobileSheetOpen, setMobileSheetOpen] = useState(false);
  const [mobileSheetContent, setMobileSheetContent] = useState<"brainlog" | "profile">("brainlog");

  // Focus the chat input
  const focusInput = useCallback(() => {
    const textarea = document.querySelector<HTMLTextAreaElement>(
      'textarea[placeholder*="Ask about"]'
    );
    textarea?.focus();
  }, []);

  // Handle escape - close panels or blur input
  const handleEscape = useCallback(() => {
    const active = document.activeElement as HTMLElement;
    if (
      active instanceof HTMLInputElement ||
      active instanceof HTMLTextAreaElement
    ) {
      active.blur();
    } else if (mobileSheetOpen) {
      setMobileSheetOpen(false);
    } else if (rightPanelMode !== "none") {
      setRightPanelMode("none");
    }
  }, [rightPanelMode, setRightPanelMode, mobileSheetOpen]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onToggleGlassBox: () => togglePanel("brainlog"),
    onToggleProfile: () => togglePanel("profile"),
    onFocusInput: focusInput,
    onEscape: handleEscape,
  });

  // Open mobile sheet with specific content
  const openMobileSheet = (content: "brainlog" | "profile") => {
    setMobileSheetContent(content);
    setMobileSheetOpen(true);
  };

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <Header onMobileToggle={openMobileSheet} />

      {/* Main Content */}
      <main className="flex flex-1 overflow-hidden">
        {/* Chat Area */}
        <div
          className={cn(
            "flex-1 transition-all duration-300",
            rightPanelMode !== "none" && "lg:mr-0"
          )}
        >
          <ChatInterface className="h-full" />
        </div>

        {/* Right Panel - slides in from right (desktop only) */}
        <div
          className={cn(
            "hidden overflow-hidden transition-all duration-300 ease-in-out lg:block",
            rightPanelMode !== "none" ? "w-96 border-l" : "w-0"
          )}
        >
          {rightPanelMode === "brainlog" && (
            <BrainLog className="h-full w-96" showCloseButton />
          )}
          {rightPanelMode === "profile" && (
            <ProfilePanel className="h-full w-96" showCloseButton />
          )}
        </div>
      </main>

      {/* Mobile FAB for Brain Log (when there are entries) */}
      {entries.length > 0 && (
        <div className="fixed bottom-20 right-4 lg:hidden">
          <Button
            onClick={() => openMobileSheet("brainlog")}
            size="icon"
            className="size-12 rounded-full shadow-lg"
            aria-label="View Brain Log"
          >
            <BrainCircuit className="size-5" />
            <span className="absolute -right-1 -top-1 flex size-5 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground">
              {entries.length}
            </span>
          </Button>
        </div>
      )}

      {/* Mobile Sheet for panels */}
      <Sheet open={mobileSheetOpen} onOpenChange={setMobileSheetOpen}>
        <SheetContent side="bottom" className="h-[70vh]" showCloseButton={false}>
          <SheetHeader className="sr-only">
            <SheetTitle>
              {mobileSheetContent === "brainlog" ? "Brain Log" : "Profile"}
            </SheetTitle>
          </SheetHeader>
          {mobileSheetContent === "brainlog" ? (
            <BrainLog className="h-full" showCloseButton onClose={() => setMobileSheetOpen(false)} />
          ) : (
            <ProfilePanel className="h-full" showCloseButton />
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

// ============================================================================
// Header Component
// ============================================================================

interface HeaderProps {
  onMobileToggle: (content: "brainlog" | "profile") => void;
}

function Header({ onMobileToggle }: HeaderProps) {
  const { rightPanelMode, togglePanel } = useGlassBox();

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
          href="https://github.com/ged1182/george-dekermenjian"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="View on GitHub"
          className="inline-flex size-8 items-center justify-center rounded-md text-sm font-medium hover:bg-muted hover:text-foreground transition-colors"
        >
          <Github className="size-4" />
        </a>

        {/* Desktop: Profile Toggle */}
        <Button
          variant={rightPanelMode === "profile" ? "default" : "ghost"}
          size="sm"
          onClick={() => togglePanel("profile")}
          aria-label="Toggle Profile (P)"
          className="hidden lg:inline-flex gap-1.5"
        >
          <User className="size-4" />
          <span className="hidden sm:inline">Profile</span>
          <kbd className="ml-1 hidden rounded bg-muted px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground sm:inline">
            P
          </kbd>
        </Button>

        {/* Desktop: Glass Box Toggle */}
        <Button
          variant={rightPanelMode === "brainlog" ? "default" : "ghost"}
          size="sm"
          onClick={() => togglePanel("brainlog")}
          aria-label="Toggle Glass Box (G)"
          className="hidden lg:inline-flex gap-1.5"
        >
          <BoxIcon className="size-4" />
          <span className="hidden sm:inline">Glass Box</span>
          <kbd className="ml-1 hidden rounded bg-muted px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground sm:inline">
            G
          </kbd>
        </Button>

        {/* Mobile: Profile Toggle */}
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => onMobileToggle("profile")}
          aria-label="View Profile"
          className="lg:hidden"
        >
          <User className="size-4" />
        </Button>

        {/* Mobile: Glass Box Toggle */}
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => onMobileToggle("brainlog")}
          aria-label="View Brain Log"
          className="lg:hidden"
        >
          <BoxIcon className="size-4" />
        </Button>
      </div>
    </header>
  );
}
