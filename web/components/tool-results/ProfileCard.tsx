"use client";

import { MapPin, Mail, ExternalLink, Briefcase } from "lucide-react";
import { ProfilePhoto } from "@/components/ui/profile-photo";
import type { ProfileOutput } from "./types";

interface ProfileCardProps {
  data: ProfileOutput;
  toolCallId: string;
}

export function ProfileCard({ data }: ProfileCardProps) {
  const { profile } = data;

  return (
    <div className="bg-card text-card-foreground my-4 overflow-hidden rounded-lg border shadow-sm">
      <div className="p-4">
        {/* Header with profile photo and name */}
        <div className="flex items-start gap-4">
          <ProfilePhoto src="/profile-pic.jpg" alt={profile.name} size="md" />
          <div className="min-w-0 flex-1">
            <h3 className="text-foreground text-lg font-semibold">{profile.name}</h3>
            <div className="text-muted-foreground flex items-center gap-1 text-sm">
              <Briefcase className="size-3.5" />
              <span>{profile.title}</span>
            </div>
            <div className="text-muted-foreground mt-0.5 flex items-center gap-1 text-sm">
              <MapPin className="size-3.5" />
              <span>{profile.location}</span>
            </div>
          </div>
        </div>

        {/* Summary */}
        <p className="text-muted-foreground mt-4 text-sm leading-relaxed">{profile.summary}</p>

        {/* Contact Links */}
        <div className="mt-4 flex flex-wrap gap-3 border-t pt-4">
          <a
            href={`mailto:${profile.email}`}
            className="text-muted-foreground hover:text-primary flex items-center gap-1.5 text-sm transition-colors"
          >
            <Mail className="size-4" />
            <span>{profile.email}</span>
          </a>
          <a
            href={profile.github}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-primary flex items-center gap-1.5 text-sm transition-colors"
          >
            <ExternalLink className="size-4" />
            <span>GitHub</span>
          </a>
          <a
            href={profile.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-primary flex items-center gap-1.5 text-sm transition-colors"
          >
            <ExternalLink className="size-4" />
            <span>LinkedIn</span>
          </a>
        </div>
      </div>
    </div>
  );
}
