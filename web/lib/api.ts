/**
 * API Client and Type Definitions for Glass Box Portfolio
 *
 * This module handles communication with the backend and defines
 * the Brain Log event types for transparent agent visibility.
 */

// ============================================================================
// Profile Types (for /profile page)
// ============================================================================

export interface Experience {
  company: string;
  title: string;
  role?: string;
  period: string;
  location: string;
  description: string;
  highlights: string[];
  technologies: string[];
  logo?: string;
}

export interface Skill {
  category: string;
  proficiency: 'expert' | 'proficient' | 'familiar';
  skills: string[];
}

export interface Project {
  name: string;
  description: string;
  highlights: string[];
  technologies: string[];
  url?: string;
  github?: string;
}

export interface Education {
  institution: string;
  degree: string;
  field: string;
  period: string;
  location: string;
  highlights?: string[];
}

export interface FamilyPhoto {
  src: string;
  alt: string;
  caption?: string;
}

export interface ProfileData {
  profile: {
    name: string;
    title: string;
    location: string;
    email: string;
    github: string;
    linkedin: string;
    summary: string;
  };
  experiences: Experience[];
  skills: Skill[];
  projects: Project[];
  education: Education[];
}

// ============================================================================
// Brain Log Types
// ============================================================================

export type LogEntryType = 'input' | 'routing' | 'thinking' | 'text' | 'tool_call' | 'tool_result' | 'validation' | 'performance';

export type LogEntryStatus = 'pending' | 'success' | 'failure';

export interface BrainLogEntry {
  id: string;
  timestamp: number;
  type: LogEntryType;
  title: string;
  details: Record<string, unknown>;
  status: LogEntryStatus;
  duration_ms?: number;
}

// ============================================================================
// API Configuration
// ============================================================================

// For local development, use the backend directly
// For production (Vercel), use the proxy API route to handle Cloud Run auth
const isProduction = process.env.NODE_ENV === 'production';
const LOCAL_BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8080';

export const API_BASE_URL = isProduction ? '' : LOCAL_BACKEND_URL;

// Chat endpoint: use /api/chat proxy in production, direct backend in development
export const CHAT_ENDPOINT = isProduction ? '/api/chat' : `${LOCAL_BACKEND_URL}/chat`;

// ============================================================================
// Type Guards
// ============================================================================

export function isBrainLogEntry(data: unknown): data is BrainLogEntry {
  if (typeof data !== 'object' || data === null) return false;

  const entry = data as Record<string, unknown>;

  return (
    typeof entry.id === 'string' &&
    typeof entry.timestamp === 'number' &&
    typeof entry.type === 'string' &&
    ['input', 'routing', 'thinking', 'text', 'tool_call', 'tool_result', 'validation', 'performance'].includes(entry.type) &&
    typeof entry.title === 'string' &&
    typeof entry.details === 'object' &&
    entry.details !== null &&
    typeof entry.status === 'string' &&
    ['pending', 'success', 'failure'].includes(entry.status)
  );
}

// ============================================================================
// Brain Log Event Parsing
// ============================================================================

/**
 * Parses Brain Log entries from the Vercel AI SDK data stream.
 * The backend sends Brain Log events as data annotations in the stream.
 */
export function parseBrainLogFromData(data: unknown[]): BrainLogEntry[] {
  const entries: BrainLogEntry[] = [];

  for (const item of data) {
    if (isBrainLogEntry(item)) {
      entries.push(item);
    } else if (typeof item === 'object' && item !== null) {
      const wrapped = item as Record<string, unknown>;

      // Check if it's in AI SDK v5 data-* format: {"type": "data-brainlog", "data": {...}}
      if (wrapped.type === 'data-brainlog' && wrapped.data && isBrainLogEntry(wrapped.data)) {
        entries.push(wrapped.data as BrainLogEntry);
      }
      // Check if it's wrapped in a brainLog property (legacy)
      else if (wrapped.brainLog && isBrainLogEntry(wrapped.brainLog)) {
        entries.push(wrapped.brainLog);
      }
      // Check if it's an array of entries (legacy)
      else if (Array.isArray(wrapped.brainLogEntries)) {
        for (const entry of wrapped.brainLogEntries) {
          if (isBrainLogEntry(entry)) {
            entries.push(entry);
          }
        }
      }
    }
  }

  return entries;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Formats a timestamp for display
 */
export function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3,
  });
}

/**
 * Formats duration in milliseconds for display
 */
export function formatDuration(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) {
    return '';
  }
  if (ms >= 1000) {
    return `${(ms / 1000).toFixed(2)}s`;
  }
  if (ms >= 1) {
    return `${Math.round(ms)}ms`;
  }
  // Zero: show as 0ms
  if (ms === 0) {
    return '0ms';
  }
  // Sub-millisecond (non-zero): show 2 decimal places
  return `${ms.toFixed(2)}ms`;
}

/**
 * Gets a human-readable label for a log entry type
 */
export function getLogTypeLabel(type: LogEntryType): string {
  const labels: Record<LogEntryType, string> = {
    input: 'Input',
    routing: 'Routing',
    thinking: 'Thinking',
    text: 'Text',
    tool_call: 'Tool Call',
    tool_result: 'Tool Result',
    validation: 'Validation',
    performance: 'Performance',
  };
  return labels[type];
}

/**
 * Gets a color class for a log entry status
 */
export function getStatusColorClass(status: LogEntryStatus): string {
  const colors: Record<LogEntryStatus, string> = {
    pending: 'text-yellow-600',
    success: 'text-green-600',
    failure: 'text-red-600',
  };
  return colors[status];
}

/**
 * Gets a background color class for a log entry type
 */
export function getTypeColorClass(type: LogEntryType): string {
  const colors: Record<LogEntryType, string> = {
    input: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    routing: 'bg-purple-500/10 text-purple-600 dark:text-purple-400',
    thinking: 'bg-pink-500/10 text-pink-600 dark:text-pink-400',
    text: 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400',
    tool_call: 'bg-orange-500/10 text-orange-600 dark:text-orange-400',
    tool_result: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
    validation: 'bg-green-500/10 text-green-600 dark:text-green-400',
    performance: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
  };
  return colors[type];
}

// ============================================================================
// Profile API
// ============================================================================

/**
 * Fetches profile data from the backend
 */
export async function fetchProfile(): Promise<ProfileData> {
  const response = await fetch(`${API_BASE_URL}/profile`);
  if (!response.ok) {
    throw new Error(`Failed to fetch profile: ${response.statusText}`);
  }
  return response.json();
}
