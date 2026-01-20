"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Building2, MapPin, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { ProfessionalExperienceOutput, Experience } from "./types";

interface ExperienceCardProps {
  data: ProfessionalExperienceOutput;
  toolCallId: string;
}

export function ExperienceCard({ data }: ExperienceCardProps) {
  return (
    <div className="my-4 space-y-3">
      {data.experiences.map((exp, index) => (
        <ExperienceEntry key={`${exp.company}-${exp.period}-${index}`} experience={exp} />
      ))}
    </div>
  );
}

interface ExperienceEntryProps {
  experience: Experience;
}

function ExperienceEntry({ experience }: ExperienceEntryProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-card text-card-foreground overflow-hidden rounded-lg border shadow-sm">
      {/* Header - Always Visible */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="hover:bg-muted/50 flex w-full items-start justify-between px-4 py-3 text-left transition-colors"
      >
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="text-foreground font-semibold">{experience.title}</h4>
          </div>
          <div className="text-muted-foreground mt-1 flex flex-wrap items-center gap-3 text-sm">
            <span className="flex items-center gap-1">
              <Building2 className="size-3.5" />
              {experience.company}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="size-3.5" />
              {experience.period}
            </span>
            {experience.location && (
              <span className="flex items-center gap-1">
                <MapPin className="size-3.5" />
                {experience.location}
              </span>
            )}
          </div>
        </div>
        <div className="text-muted-foreground ml-2">
          {isExpanded ? <ChevronUp className="size-5" /> : <ChevronDown className="size-5" />}
        </div>
      </button>

      {/* Expandable Content */}
      <div
        className={cn(
          "overflow-hidden transition-all duration-200",
          isExpanded ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"
        )}
      >
        <div className="bg-muted/30 border-t px-4 pt-1 pb-4">
          {/* Description */}
          <p className="text-muted-foreground mb-3 text-sm">{experience.description}</p>

          {/* Highlights */}
          {experience.highlights.length > 0 && (
            <div className="mb-3">
              <h5 className="text-muted-foreground mb-2 text-xs font-medium tracking-wide uppercase">
                Key Achievements
              </h5>
              <ul className="space-y-1.5">
                {experience.highlights.map((highlight, idx) => (
                  <li key={idx} className="text-foreground flex items-start gap-2 text-sm">
                    <span className="text-primary mt-1.5 text-xs">•</span>
                    <span>{highlight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Technologies */}
          {experience.technologies.length > 0 && (
            <div>
              <h5 className="text-muted-foreground mb-2 text-xs font-medium tracking-wide uppercase">
                Technologies
              </h5>
              <div className="flex flex-wrap gap-1.5">
                {experience.technologies.map((tech) => (
                  <Badge key={tech} variant="secondary" className="px-2 py-0.5 text-xs">
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
