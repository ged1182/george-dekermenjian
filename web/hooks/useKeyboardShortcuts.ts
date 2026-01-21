"use client";

import { useEffect, useCallback } from "react";

export interface KeyboardShortcutHandlers {
  onToggleGlassBox: () => void;
  onToggleProfile: () => void;
  onFocusInput: () => void;
  onEscape: () => void;
}

/**
 * Hook to handle global keyboard shortcuts.
 *
 * Shortcuts:
 * - G: Toggle Glass Box (Brain Log) panel
 * - P: Toggle Profile panel
 * - /: Focus chat input
 * - Esc: Close panels / blur input
 */
export function useKeyboardShortcuts(handlers: KeyboardShortcutHandlers) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Get the active element
      const target = e.target as HTMLElement;
      const isTyping =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target.isContentEditable;

      // Handle Escape key globally (works even when typing)
      if (e.key === "Escape") {
        handlers.onEscape();
        return;
      }

      // Skip other shortcuts if user is typing
      if (isTyping) {
        return;
      }

      // Handle shortcuts (case-insensitive)
      switch (e.key.toLowerCase()) {
        case "g":
          e.preventDefault();
          handlers.onToggleGlassBox();
          break;
        case "p":
          e.preventDefault();
          handlers.onToggleProfile();
          break;
        case "/":
          e.preventDefault();
          handlers.onFocusInput();
          break;
      }
    },
    [handlers]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);
}
