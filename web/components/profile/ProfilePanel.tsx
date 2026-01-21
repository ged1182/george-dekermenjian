"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { ProfilePhoto } from "@/components/ui/profile-photo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import {
  Github,
  Linkedin,
  Mail,
  MapPin,
  ChevronDown,
  ExternalLink,
  Briefcase,
  Code2,
  GraduationCap,
  FolderGit2,
  Download,
  Heart,
  Loader2,
  X,
} from "lucide-react";
import {
  fetchProfile,
  type ProfileData,
  type Experience,
  type Skill,
  type Project,
  type Education,
  type FamilyPhoto,
} from "@/lib/api";
import { useGlassBox } from "@/components/glass-box";

// =============================================================================
// Family Photos Data (Personal Touch)
// =============================================================================

const FAMILY_PHOTOS: FamilyPhoto[] = [
  {
    src: "/family/IMG_5223.jpeg",
    alt: "Family photo",
    caption: "Family moments that matter most",
  },
];

// =============================================================================
// Highlight Hook - for Task 10
// =============================================================================

function useHighlightedSections() {
  const { entries } = useGlassBox();

  const highlighted = new Set<string>();
  entries
    .filter((e) => e.type === "tool_call")
    .forEach((e) => {
      const title = e.title.toLowerCase();
      if (title.includes("experience")) highlighted.add("experience");
      if (title.includes("skill")) highlighted.add("skills");
      if (title.includes("project")) highlighted.add("projects");
      if (title.includes("education")) highlighted.add("education");
    });

  return highlighted;
}

// =============================================================================
// Components
// =============================================================================

interface ProfilePanelProps {
  className?: string;
  showCloseButton?: boolean;
}

function ProfileSummaryCompact({ profile }: { profile: ProfileData["profile"] }) {
  return (
    <div className="px-4 py-3 border-b">
      <div className="flex items-start gap-3">
        <ProfilePhoto src="/profile-pic.jpg" alt={profile.name} size="md" />
        <div className="flex-1 min-w-0">
          <h2 className="text-sm font-semibold truncate">{profile.name}</h2>
          <p className="text-xs text-muted-foreground truncate">{profile.title}</p>
          <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <MapPin className="size-3" />
              {profile.location}
            </span>
          </div>
        </div>
      </div>
      <div className="mt-3 flex items-center gap-2">
        <a
          href="/George_Dekermenjian_Resume.pdf"
          download
          className="inline-flex h-7 items-center gap-1 rounded-md bg-primary px-2 text-xs font-medium text-primary-foreground hover:bg-primary/90"
        >
          <Download className="size-3" />
          Resume
        </a>
        <a
          href={profile.github}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex size-7 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          <Github className="size-3.5" />
        </a>
        <a
          href={profile.linkedin}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex size-7 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          <Linkedin className="size-3.5" />
        </a>
        <a
          href={`mailto:${profile.email}`}
          className="inline-flex size-7 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          <Mail className="size-3.5" />
        </a>
      </div>
    </div>
  );
}

function FamilyGalleryCompact() {
  const [selectedPhoto, setSelectedPhoto] = useState<FamilyPhoto | null>(null);
  const hasPhotos = FAMILY_PHOTOS.length > 0;

  if (!hasPhotos) return null;

  return (
    <section className="px-4 py-3">
      <div className="mb-2 flex items-center gap-2">
        <Heart className="size-3.5 text-primary" />
        <h3 className="text-xs font-semibold">Personal</h3>
      </div>

      <div className="flex gap-2">
        {FAMILY_PHOTOS.slice(0, 3).map((photo) => (
          <button
            key={photo.src}
            type="button"
            onClick={() => setSelectedPhoto(photo)}
            className="group relative size-16 cursor-pointer overflow-hidden rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <Image
              src={photo.src}
              alt={photo.alt}
              fill
              className="object-cover transition-transform group-hover:scale-105"
              sizes="64px"
            />
          </button>
        ))}
      </div>

      <Dialog open={selectedPhoto !== null} onOpenChange={() => setSelectedPhoto(null)}>
        <DialogContent className="overflow-hidden p-0 sm:max-w-lg">
          <DialogTitle className="sr-only">{selectedPhoto?.alt || "Photo"}</DialogTitle>
          {selectedPhoto && (
            <div>
              <div className="relative aspect-square w-full">
                <Image
                  src={selectedPhoto.src}
                  alt={selectedPhoto.alt}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, 512px"
                />
              </div>
              <div className="bg-background p-4">
                <p className="text-muted-foreground text-sm">{selectedPhoto.caption}</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </section>
  );
}

function ExperienceCompact({
  experiences,
  highlighted,
}: {
  experiences: Experience[];
  highlighted: boolean;
}) {
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set([0]));

  const toggleItem = (index: number) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  return (
    <section
      className={cn(
        "px-4 py-3 transition-all",
        highlighted && "ring-2 ring-primary/50 ring-inset bg-primary/5"
      )}
    >
      <div className="mb-2 flex items-center gap-2">
        <Briefcase className="size-3.5 text-primary" />
        <h3 className="text-xs font-semibold">Experience</h3>
      </div>

      <div className="space-y-2">
        {experiences.map((exp, index) => (
          <Collapsible
            key={index}
            open={expandedItems.has(index)}
            onOpenChange={() => toggleItem(index)}
          >
            <Card className="border-none shadow-none bg-muted/50">
              <CollapsibleTrigger className="w-full text-left">
                <CardHeader className="p-2 hover:bg-muted cursor-pointer transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-xs font-semibold truncate">{exp.title}</CardTitle>
                      <CardDescription className="text-xs truncate">
                        {exp.company}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-1 ml-2">
                      <Badge variant="outline" className="text-[10px] px-1 py-0">
                        {exp.period}
                      </Badge>
                      <ChevronDown
                        className={cn(
                          "size-3 text-muted-foreground transition-transform",
                          expandedItems.has(index) && "rotate-180"
                        )}
                      />
                    </div>
                  </div>
                </CardHeader>
              </CollapsibleTrigger>

              <CollapsibleContent>
                <CardContent className="p-2 pt-0">
                  <ul className="mb-2 space-y-1">
                    {exp.highlights.slice(0, 3).map((highlight, i) => (
                      <li key={i} className="text-muted-foreground flex gap-1.5 text-[10px]">
                        <span className="text-primary">-</span>
                        <span>{highlight}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="flex flex-wrap gap-1">
                    {exp.technologies.slice(0, 5).map((tech) => (
                      <Badge key={tech} variant="secondary" className="text-[10px] px-1 py-0">
                        {tech}
                      </Badge>
                    ))}
                    {exp.technologies.length > 5 && (
                      <Badge variant="secondary" className="text-[10px] px-1 py-0">
                        +{exp.technologies.length - 5}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>
        ))}
      </div>
    </section>
  );
}

function SkillsCompact({ skills, highlighted }: { skills: Skill[]; highlighted: boolean }) {
  return (
    <section
      className={cn(
        "px-4 py-3 transition-all",
        highlighted && "ring-2 ring-primary/50 ring-inset bg-primary/5"
      )}
    >
      <div className="mb-2 flex items-center gap-2">
        <Code2 className="size-3.5 text-primary" />
        <h3 className="text-xs font-semibold">Skills</h3>
      </div>

      <div className="space-y-3">
        {skills.map((skillCategory) => (
          <div key={skillCategory.category}>
            <div className="mb-1 flex items-center justify-between">
              <span className="text-[10px] font-medium">{skillCategory.category}</span>
              <Badge
                variant={skillCategory.proficiency === "expert" ? "default" : "secondary"}
                className="text-[10px] px-1 py-0 capitalize"
              >
                {skillCategory.proficiency}
              </Badge>
            </div>
            <div className="flex flex-wrap gap-1">
              {skillCategory.skills.map((skill) => (
                <Badge key={skill} variant="outline" className="text-[10px] px-1 py-0 font-normal">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ProjectsCompact({ projects, highlighted }: { projects: Project[]; highlighted: boolean }) {
  return (
    <section
      className={cn(
        "px-4 py-3 transition-all",
        highlighted && "ring-2 ring-primary/50 ring-inset bg-primary/5"
      )}
    >
      <div className="mb-2 flex items-center gap-2">
        <FolderGit2 className="size-3.5 text-primary" />
        <h3 className="text-xs font-semibold">Projects</h3>
      </div>

      <div className="space-y-2">
        {projects.map((project) => (
          <Card key={project.name} className="border shadow-none">
            <CardHeader className="p-2">
              <div className="flex items-start justify-between">
                <CardTitle className="text-xs font-semibold">{project.name}</CardTitle>
                {project.url && (
                  <a
                    href={project.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <ExternalLink className="size-3" />
                  </a>
                )}
              </div>
              <CardDescription className="text-[10px]">{project.description}</CardDescription>
            </CardHeader>
            <CardContent className="p-2 pt-0">
              <div className="flex flex-wrap gap-1">
                {project.technologies.slice(0, 4).map((tech) => (
                  <Badge key={tech} variant="secondary" className="text-[10px] px-1 py-0">
                    {tech}
                  </Badge>
                ))}
                {project.technologies.length > 4 && (
                  <Badge variant="secondary" className="text-[10px] px-1 py-0">
                    +{project.technologies.length - 4}
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}

function EducationCompact({
  education,
  highlighted,
}: {
  education: Education[];
  highlighted: boolean;
}) {
  return (
    <section
      className={cn(
        "px-4 py-3 transition-all",
        highlighted && "ring-2 ring-primary/50 ring-inset bg-primary/5"
      )}
    >
      <div className="mb-2 flex items-center gap-2">
        <GraduationCap className="size-3.5 text-primary" />
        <h3 className="text-xs font-semibold">Education</h3>
      </div>

      <div className="space-y-2">
        {education.map((edu) => (
          <Card key={edu.institution} className="border-none shadow-none bg-muted/50">
            <CardHeader className="p-2">
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1">
                  <CardTitle className="text-xs font-semibold truncate">
                    {edu.degree} in {edu.field}
                  </CardTitle>
                  <CardDescription className="text-[10px] truncate">{edu.institution}</CardDescription>
                </div>
                <Badge variant="outline" className="text-[10px] px-1 py-0 ml-2">
                  {edu.period}
                </Badge>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </section>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ProfilePanel({ className, showCloseButton }: ProfilePanelProps) {
  const { setRightPanelMode } = useGlassBox();
  const [data, setData] = useState<ProfileData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const highlighted = useHighlightedSections();

  const loadProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const profileData = await fetchProfile();
      setData(profileData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  if (loading) {
    return (
      <div className={cn("flex h-full flex-col overflow-hidden", className)}>
        <div className="flex-shrink-0 flex items-center justify-between border-b px-4 py-2">
          <h2 className="text-sm font-semibold">Profile</h2>
          {showCloseButton && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => setRightPanelMode("none")}
              aria-label="Close profile panel"
            >
              <X className="size-4" />
            </Button>
          )}
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="size-6 animate-spin text-primary" />
            <p className="text-xs text-muted-foreground">Loading profile...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className={cn("flex h-full flex-col overflow-hidden", className)}>
        <div className="flex-shrink-0 flex items-center justify-between border-b px-4 py-2">
          <h2 className="text-sm font-semibold">Profile</h2>
          {showCloseButton && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => setRightPanelMode("none")}
              aria-label="Close profile panel"
            >
              <X className="size-4" />
            </Button>
          )}
        </div>
        <div className="flex flex-1 items-center justify-center p-4">
          <div className="text-center">
            <p className="text-sm font-medium">Failed to load profile</p>
            <p className="mt-1 text-xs text-muted-foreground">{error}</p>
            <Button variant="outline" size="sm" className="mt-3" onClick={loadProfile}>
              Try again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("flex h-full flex-col overflow-hidden", className)}>
      {/* Header */}
      <div className="flex-shrink-0 flex items-center justify-between border-b px-4 py-2">
        <h2 className="text-sm font-semibold">Profile</h2>
        {showCloseButton && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setRightPanelMode("none")}
            aria-label="Close profile panel"
          >
            <X className="size-4" />
          </Button>
        )}
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 min-h-0">
        <div>
          <ProfileSummaryCompact profile={data.profile} />

          <FamilyGalleryCompact />

          <div className="border-t" />

          <ExperienceCompact
            experiences={data.experiences}
            highlighted={highlighted.has("experience")}
          />

          <div className="border-t" />

          <SkillsCompact skills={data.skills} highlighted={highlighted.has("skills")} />

          <div className="border-t" />

          <ProjectsCompact projects={data.projects} highlighted={highlighted.has("projects")} />

          <div className="border-t" />

          <EducationCompact education={data.education} highlighted={highlighted.has("education")} />

          {/* Footer spacing */}
          <div className="h-4" />
        </div>
      </ScrollArea>
    </div>
  );
}

export default ProfilePanel;
