"use client";

import { ExternalLink, FolderGit2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { ProjectsOutput, Project } from "./types";

interface ProjectCardProps {
  data: ProjectsOutput;
  toolCallId: string;
}

export function ProjectCard({ data }: ProjectCardProps) {
  return (
    <div className="my-4 space-y-3">
      {data.projects.map((project) => (
        <ProjectEntry key={project.name} project={project} />
      ))}
    </div>
  );
}

interface ProjectEntryProps {
  project: Project;
}

function ProjectEntry({ project }: ProjectEntryProps) {
  return (
    <div className="bg-card text-card-foreground overflow-hidden rounded-lg border shadow-sm">
      <div className="p-4">
        {/* Header */}
        <div className="mb-2 flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <FolderGit2 className="text-primary size-5" />
            <h4 className="text-foreground font-semibold">{project.name}</h4>
          </div>
          {project.url && (
            <a
              href={project.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary flex items-center gap-1 text-xs transition-colors"
            >
              <ExternalLink className="size-3.5" />
              View
            </a>
          )}
        </div>

        {/* Description */}
        <p className="text-muted-foreground mb-3 text-sm">{project.description}</p>

        {/* Highlights */}
        {project.highlights.length > 0 && (
          <div className="mb-3">
            <ul className="space-y-1">
              {project.highlights.map((highlight, idx) => (
                <li key={idx} className="text-foreground flex items-start gap-2 text-sm">
                  <span className="text-primary mt-1.5 text-xs">•</span>
                  <span>{highlight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Technologies */}
        {project.technologies.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {project.technologies.map((tech) => (
              <Badge key={tech} variant="secondary" className="px-2 py-0.5 text-xs">
                {tech}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
