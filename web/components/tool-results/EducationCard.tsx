"use client";

import { GraduationCap, Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { EducationOutput, Education } from "./types";

interface EducationCardProps {
  data: EducationOutput;
  toolCallId: string;
}

export function EducationCard({ data }: EducationCardProps) {
  return (
    <div className="my-4 space-y-3">
      {data.education.map((edu, index) => (
        <EducationEntry key={`${edu.institution}-${edu.period}-${index}`} education={edu} />
      ))}
    </div>
  );
}

interface EducationEntryProps {
  education: Education;
}

function EducationEntry({ education }: EducationEntryProps) {
  return (
    <div className="bg-card text-card-foreground overflow-hidden rounded-lg border shadow-sm">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start gap-3">
          <div className="bg-primary/10 rounded-md p-2">
            <GraduationCap className="text-primary size-5" />
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="text-foreground font-semibold">
              {education.degree} in {education.field}
            </h4>
            <p className="text-muted-foreground text-sm">{education.institution}</p>
            <div className="mt-1 flex items-center gap-1">
              <Calendar className="text-muted-foreground size-3.5" />
              <Badge variant="outline" className="px-2 py-0 text-xs">
                {education.period}
              </Badge>
            </div>
          </div>
        </div>

        {/* Highlights */}
        {education.highlights && education.highlights.length > 0 && (
          <div className="mt-3 border-t pt-3">
            <ul className="space-y-1.5">
              {education.highlights.map((highlight, idx) => (
                <li key={idx} className="text-foreground flex items-start gap-2 text-sm">
                  <span className="text-primary mt-1.5 text-xs">•</span>
                  <span>{highlight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
