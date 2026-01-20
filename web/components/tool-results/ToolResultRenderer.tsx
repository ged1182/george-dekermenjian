"use client";

import { Loader } from "@/components/ai-elements/loader";
import type {
  ToolResultRendererProps,
  ProfessionalExperienceOutput,
  SkillsOutput,
  ProjectsOutput,
  EducationOutput,
  ProfileOutput,
  FindSymbolOutput,
  FileContentOutput,
  FindReferencesOutput,
} from "./types";
import { ExperienceCard } from "./ExperienceCard";
import { SkillsDisplay } from "./SkillsDisplay";
import { ProjectCard } from "./ProjectCard";
import { EducationCard } from "./EducationCard";
import { ProfileCard } from "./ProfileCard";
import { CodebaseResult } from "./CodebaseResult";

/**
 * Routes tool results to the appropriate rich UI component.
 * Shows loading state when tool is executing, error state on failure,
 * and renders the appropriate visualization based on tool name.
 */
export function ToolResultRenderer({
  toolName,
  toolCallId,
  state,
  output,
  errorText,
}: ToolResultRendererProps) {
  // Show loading state when tool is still processing
  if (state === "input-streaming" || state === "input-available") {
    return (
      <div className="text-muted-foreground flex items-center gap-2 py-2">
        <Loader size={14} />
        <span className="text-sm">Calling {formatToolName(toolName)}...</span>
      </div>
    );
  }

  // Show error state
  if (state === "output-error" || errorText) {
    return (
      <div className="border-destructive/50 bg-destructive/10 text-destructive my-2 rounded-md border p-3 text-sm">
        <p className="font-medium">Tool Error: {formatToolName(toolName)}</p>
        <p className="mt-1 text-xs">{errorText || "Unknown error occurred"}</p>
      </div>
    );
  }

  // No output yet (still streaming or no data)
  if (!output || state === "output-streaming") {
    return (
      <div className="text-muted-foreground flex items-center gap-2 py-2">
        <Loader size={14} />
        <span className="text-sm">Processing {formatToolName(toolName)}...</span>
      </div>
    );
  }

  // Route to appropriate component based on tool name
  switch (toolName) {
    case "get_professional_experience":
    case "get_latest_experience":
      return (
        <ExperienceCard data={output as ProfessionalExperienceOutput} toolCallId={toolCallId} />
      );

    case "get_skills":
      return <SkillsDisplay data={output as SkillsOutput} toolCallId={toolCallId} />;

    case "get_projects":
      return <ProjectCard data={output as ProjectsOutput} toolCallId={toolCallId} />;

    case "get_education":
      return <EducationCard data={output as EducationOutput} toolCallId={toolCallId} />;

    case "get_profile":
      return <ProfileCard data={output as ProfileOutput} toolCallId={toolCallId} />;

    case "find_symbol":
      return (
        <CodebaseResult
          toolName={toolName}
          data={output as FindSymbolOutput}
          toolCallId={toolCallId}
        />
      );

    case "get_file_content":
      return (
        <CodebaseResult
          toolName={toolName}
          data={output as FileContentOutput}
          toolCallId={toolCallId}
        />
      );

    case "find_references":
      return (
        <CodebaseResult
          toolName={toolName}
          data={output as FindReferencesOutput}
          toolCallId={toolCallId}
        />
      );

    default:
      // Fallback: render as JSON for unknown tools
      return <CodebaseResult toolName={toolName} data={output} toolCallId={toolCallId} />;
  }
}

/**
 * Format tool name for display (snake_case -> Title Case)
 */
function formatToolName(name: string): string {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
