"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { BrainLogEntry } from "@/lib/api";

// ============================================================================
// Context Types
// ============================================================================

/** Which panel is shown on the right side */
export type RightPanelMode = "none" | "brainlog" | "profile";

interface GlassBoxContextValue {
  /** Whether Glass Box mode is enabled */
  isEnabled: boolean;
  /** Toggle Glass Box mode */
  toggle: () => void;
  /** Enable Glass Box mode */
  enable: () => void;
  /** Disable Glass Box mode */
  disable: () => void;
  /** Brain Log entries */
  entries: BrainLogEntry[];
  /** Add a Brain Log entry */
  addEntry: (entry: BrainLogEntry) => void;
  /** Add multiple Brain Log entries */
  addEntries: (entries: BrainLogEntry[]) => void;
  /** Clear all Brain Log entries */
  clearEntries: () => void;
  /** Update an existing entry by ID */
  updateEntry: (id: string, updates: Partial<BrainLogEntry>) => void;
  /** Current right panel mode */
  rightPanelMode: RightPanelMode;
  /** Set right panel mode */
  setRightPanelMode: (mode: RightPanelMode) => void;
  /** Toggle a specific panel (opens it or closes if already open) */
  togglePanel: (panel: "brainlog" | "profile") => void;
}

// ============================================================================
// Context
// ============================================================================

const GlassBoxContext = createContext<GlassBoxContextValue | null>(null);

// ============================================================================
// Hook
// ============================================================================

export function useGlassBox(): GlassBoxContextValue {
  const context = useContext(GlassBoxContext);
  if (!context) {
    throw new Error("useGlassBox must be used within a GlassBoxProvider");
  }
  return context;
}

// ============================================================================
// Provider
// ============================================================================

interface GlassBoxProviderProps {
  children: ReactNode;
  /** Initial enabled state */
  defaultEnabled?: boolean;
}

export function GlassBoxProvider({
  children,
  defaultEnabled = false,
}: GlassBoxProviderProps) {
  const [isEnabled, setIsEnabled] = useState(defaultEnabled);
  const [entries, setEntries] = useState<BrainLogEntry[]>([]);
  const [rightPanelMode, setRightPanelModeInternal] = useState<RightPanelMode>("none");

  // Wrapper to sync isEnabled when setting rightPanelMode
  const setRightPanelMode = useCallback((mode: RightPanelMode) => {
    setRightPanelModeInternal(mode);
    // Sync isEnabled with brainlog panel visibility
    setIsEnabled(mode === "brainlog");
  }, []);

  const toggle = useCallback(() => {
    setIsEnabled((prev) => !prev);
  }, []);

  const togglePanel = useCallback((panel: "brainlog" | "profile") => {
    setRightPanelModeInternal((prev: RightPanelMode) => {
      const newMode: RightPanelMode = prev === panel ? "none" : panel;
      // Sync isEnabled with brainlog panel visibility
      setIsEnabled(newMode === "brainlog");
      return newMode;
    });
  }, []);

  const enable = useCallback(() => {
    setIsEnabled(true);
  }, []);

  const disable = useCallback(() => {
    setIsEnabled(false);
  }, []);

  const addEntry = useCallback((entry: BrainLogEntry) => {
    setEntries((prev) => {
      // Check if entry already exists (by ID)
      const existingIndex = prev.findIndex((e) => e.id === entry.id);
      if (existingIndex >= 0) {
        // Update existing entry
        const updated = [...prev];
        updated[existingIndex] = entry;
        return updated;
      }
      // Add new entry
      return [...prev, entry];
    });
  }, []);

  const addEntries = useCallback((newEntries: BrainLogEntry[]) => {
    setEntries((prev) => {
      const result = [...prev];
      for (const entry of newEntries) {
        const existingIndex = result.findIndex((e) => e.id === entry.id);
        if (existingIndex >= 0) {
          result[existingIndex] = entry;
        } else {
          result.push(entry);
        }
      }
      return result;
    });
  }, []);

  const clearEntries = useCallback(() => {
    setEntries([]);
  }, []);

  const updateEntry = useCallback(
    (id: string, updates: Partial<BrainLogEntry>) => {
      setEntries((prev) =>
        prev.map((entry) =>
          entry.id === id ? { ...entry, ...updates } : entry
        )
      );
    },
    []
  );

  const value = useMemo<GlassBoxContextValue>(
    () => ({
      isEnabled,
      toggle,
      enable,
      disable,
      entries,
      addEntry,
      addEntries,
      clearEntries,
      updateEntry,
      rightPanelMode,
      setRightPanelMode,
      togglePanel,
    }),
    [
      isEnabled,
      toggle,
      enable,
      disable,
      entries,
      addEntry,
      addEntries,
      clearEntries,
      updateEntry,
      rightPanelMode,
      togglePanel,
    ]
  );

  return (
    <GlassBoxContext.Provider value={value}>
      {children}
    </GlassBoxContext.Provider>
  );
}
