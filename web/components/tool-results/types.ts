/**
 * TypeScript interfaces matching backend Pydantic models.
 * These types define the structure of tool output data.
 */

// =============================================================================
// Experience Tool Types
// =============================================================================

export interface Experience {
  company: string;
  title: string;
  period: string;
  location: string;
  description: string;
  highlights: string[];
  technologies: string[];
}

export interface ProfessionalExperienceOutput {
  experiences: Experience[];
  summary: string;
}

// =============================================================================
// Skills Tool Types
// =============================================================================

export interface Skill {
  category: string;
  skills: string[];
  proficiency: "expert" | "proficient" | "familiar";
}

export interface SkillsOutput {
  skills: Skill[];
  summary: string;
}

// =============================================================================
// Projects Tool Types
// =============================================================================

export interface Project {
  name: string;
  description: string;
  technologies: string[];
  highlights: string[];
  url?: string | null;
}

export interface ProjectsOutput {
  projects: Project[];
  summary: string;
}

// =============================================================================
// Education Tool Types
// =============================================================================

export interface Education {
  institution: string;
  degree: string;
  field: string;
  period: string;
  highlights: string[];
}

export interface EducationOutput {
  education: Education[];
  summary: string;
}

// =============================================================================
// Profile Tool Types
// =============================================================================

export interface ProfileInfo {
  name: string;
  title: string;
  location: string;
  email: string;
  github: string;
  linkedin: string;
  summary: string;
}

export interface ProfileOutput {
  profile: ProfileInfo;
  summary: string;
}

// =============================================================================
// Codebase Tool Types
// =============================================================================

export interface SymbolLocation {
  file: string;
  line: number;
  snippet: string;
}

export interface FindSymbolOutput {
  symbol: string;
  locations: SymbolLocation[];
  total_found: number;
}

export interface FileContentOutput {
  file_path: string;
  content: string;
  start_line: number;
  end_line: number;
  total_lines: number;
  language: string;
}

export interface Reference {
  file: string;
  line: number;
  context: string;
}

export interface FindReferencesOutput {
  symbol: string;
  references: Reference[];
  total_found: number;
}

// =============================================================================
// Tool Result Renderer Props
// =============================================================================

export type ToolState =
  | "input-streaming"
  | "input-available"
  | "output-streaming"
  | "output-available"
  | "output-error";

export interface ToolResultRendererProps {
  toolName: string;
  toolCallId: string;
  state: ToolState;
  input?: unknown;
  output?: unknown;
  errorText?: string;
}
