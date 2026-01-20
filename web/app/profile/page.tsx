"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { ProfilePhoto } from "@/components/ui/profile-photo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import {
  BoxIcon,
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
  ArrowLeft,
  Download,
  Heart,
  Loader2,
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
// Components
// =============================================================================

function ProfileHeader({ profile }: { profile?: ProfileData["profile"] }) {
  return (
    <header className="flex items-center justify-between border-b px-4 py-3">
      <div className="flex items-center gap-3">
        <Link href="/">
          <Button variant="ghost" size="icon-sm">
            <ArrowLeft className="size-4" />
          </Button>
        </Link>
        <div className="flex items-center gap-3">
          <div className="bg-primary text-primary-foreground flex size-8 items-center justify-center rounded-md">
            <BoxIcon className="size-4" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm leading-none font-semibold">Glass Box</h1>
            <p className="text-muted-foreground text-xs">Profile</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {/* PDF Download Button */}
        <a
          href="/George_Dekermenjian_Resume.pdf"
          download
          className="bg-primary text-primary-foreground hover:bg-primary/90 inline-flex h-8 items-center gap-1.5 rounded-md px-3 text-sm font-medium transition-colors"
        >
          <Download className="size-4" />
          <span className="hidden sm:inline">Resume</span>
        </a>
        {profile && (
          <>
            <a
              href={profile.github}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="View on GitHub"
              className="hover:bg-muted hover:text-foreground inline-flex size-8 items-center justify-center rounded-md text-sm font-medium transition-colors"
            >
              <Github className="size-4" />
            </a>
            <a
              href={profile.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="View on LinkedIn"
              className="hover:bg-muted hover:text-foreground inline-flex size-8 items-center justify-center rounded-md text-sm font-medium transition-colors"
            >
              <Linkedin className="size-4" />
            </a>
          </>
        )}
      </div>
    </header>
  );
}

function ProfileSummary({ profile }: { profile: ProfileData["profile"] }) {
  return (
    <Card className="border-none shadow-none">
      <CardHeader className="pb-2">
        <div className="flex items-start gap-4">
          <ProfilePhoto src="/profile-pic.jpg" alt={profile.name} size="lg" />
          <div className="flex-1">
            <CardTitle className="text-xl font-bold">{profile.name}</CardTitle>
            <CardDescription className="text-foreground/80 text-sm font-medium">
              {profile.title}
            </CardDescription>
            <div className="text-muted-foreground mt-2 flex flex-wrap items-center gap-3 text-xs">
              <span className="flex items-center gap-1">
                <MapPin className="size-3" />
                {profile.location}
              </span>
              <a
                href={`mailto:${profile.email}`}
                className="hover:text-foreground flex items-center gap-1 transition-colors"
              >
                <Mail className="size-3" />
                {profile.email}
              </a>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground text-sm leading-relaxed">{profile.summary}</p>
      </CardContent>
    </Card>
  );
}

function FamilyGallery() {
  const [selectedPhoto, setSelectedPhoto] = useState<FamilyPhoto | null>(null);
  // Derive directly from constant - no state needed
  const hasPhotos = FAMILY_PHOTOS.length > 0;

  if (!hasPhotos) {
    return (
      <section>
        <div className="mb-4 flex items-center gap-2 px-4">
          <Heart className="text-primary size-4" />
          <h2 className="text-sm font-semibold">Personal</h2>
        </div>

        <div className="px-4">
          <Card className="border-dashed">
            <CardContent className="py-8 text-center">
              <Heart className="text-muted-foreground/50 mx-auto mb-3 size-8" />
              <p className="text-muted-foreground mb-2 text-sm">Family photos coming soon</p>
              <p className="text-muted-foreground/70 text-xs">
                Add photos to{" "}
                <code className="bg-muted rounded px-1 py-0.5 text-xs">web/public/family/</code> and
                update FAMILY_PHOTOS in this file
              </p>
            </CardContent>
          </Card>
        </div>
      </section>
    );
  }

  return (
    <section>
      <div className="mb-4 flex items-center gap-2 px-4">
        <Heart className="text-primary size-4" />
        <h2 className="text-sm font-semibold">Personal</h2>
      </div>

      <div className="px-4">
        <div
          className={cn(
            "grid gap-3",
            FAMILY_PHOTOS.length === 1
              ? "max-w-xs grid-cols-1"
              : FAMILY_PHOTOS.length === 2
                ? "max-w-md grid-cols-2"
                : "grid-cols-3"
          )}
        >
          {FAMILY_PHOTOS.map((photo) => (
            <button
              key={photo.src}
              type="button"
              onClick={() => setSelectedPhoto(photo)}
              className="group focus:ring-primary relative aspect-square cursor-pointer overflow-hidden rounded-lg focus:ring-2 focus:outline-none"
            >
              <Image
                src={photo.src}
                alt={photo.alt}
                fill
                className="object-cover transition-transform group-hover:scale-105"
                sizes="(max-width: 768px) 50vw, 250px"
              />
              <div className="absolute inset-0 bg-black/0 transition-colors group-hover:bg-black/20" />
            </button>
          ))}
        </div>
      </div>

      {/* Photo Modal */}
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

function ExperienceTimeline({ experiences }: { experiences: Experience[] }) {
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
    <section>
      <div className="mb-4 flex items-center gap-2 px-4">
        <Briefcase className="text-primary size-4" />
        <h2 className="text-sm font-semibold">Experience</h2>
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="bg-border absolute top-0 bottom-0 left-6 w-px" />

        <div className="space-y-2">
          {experiences.map((exp, index) => (
            <Collapsible
              key={index}
              open={expandedItems.has(index)}
              onOpenChange={() => toggleItem(index)}
            >
              <div className="relative pl-10">
                {/* Timeline dot */}
                <div
                  className={cn(
                    "bg-background absolute top-3 left-4 size-4 rounded-full border-2 transition-colors",
                    expandedItems.has(index)
                      ? "border-primary bg-primary"
                      : "border-muted-foreground"
                  )}
                />

                <Card className="border-none shadow-none">
                  <CollapsibleTrigger className="w-full text-left">
                    <CardHeader className="hover:bg-muted/50 cursor-pointer transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-sm font-semibold">{exp.title}</CardTitle>
                          <CardDescription className="text-xs">
                            {exp.company} &bull; {exp.location}
                          </CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {exp.period}
                          </Badge>
                          <ChevronDown
                            className={cn(
                              "text-muted-foreground size-4 transition-transform",
                              expandedItems.has(index) && "rotate-180"
                            )}
                          />
                        </div>
                      </div>
                    </CardHeader>
                  </CollapsibleTrigger>

                  <CollapsibleContent>
                    <CardContent className="pt-0">
                      <p className="text-muted-foreground mb-3 text-xs">{exp.description}</p>

                      <ul className="mb-3 space-y-1.5">
                        {exp.highlights.map((highlight, i) => (
                          <li key={i} className="text-muted-foreground flex gap-2 text-xs">
                            <span className="text-primary mt-0.5">-</span>
                            <span>{highlight}</span>
                          </li>
                        ))}
                      </ul>

                      <div className="flex flex-wrap gap-1">
                        {exp.technologies.map((tech) => (
                          <Badge key={tech} variant="secondary" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </CollapsibleContent>
                </Card>
              </div>
            </Collapsible>
          ))}
        </div>
      </div>
    </section>
  );
}

function SkillsVisualization({ skills }: { skills: Skill[] }) {
  const proficiencyColors = {
    expert: "bg-primary",
    proficient: "bg-chart-3",
    familiar: "bg-chart-5",
  };

  const proficiencyWidths = {
    expert: "w-full",
    proficient: "w-3/4",
    familiar: "w-1/2",
  };

  return (
    <section>
      <div className="mb-4 flex items-center gap-2 px-4">
        <Code2 className="text-primary size-4" />
        <h2 className="text-sm font-semibold">Skills</h2>
      </div>

      <div className="space-y-4 px-4">
        {skills.map((skillCategory) => (
          <div key={skillCategory.category}>
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-medium">{skillCategory.category}</span>
              <Badge
                variant={skillCategory.proficiency === "expert" ? "default" : "secondary"}
                className="text-xs capitalize"
              >
                {skillCategory.proficiency}
              </Badge>
            </div>

            {/* Skill bar */}
            <div className="bg-muted mb-2 h-1.5 overflow-hidden rounded-full">
              <div
                className={cn(
                  "h-full rounded-full transition-all duration-500",
                  proficiencyColors[skillCategory.proficiency],
                  proficiencyWidths[skillCategory.proficiency]
                )}
              />
            </div>

            {/* Skill tags */}
            <div className="flex flex-wrap gap-1">
              {skillCategory.skills.map((skill) => (
                <Badge key={skill} variant="outline" className="text-xs font-normal">
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

function ProjectsSection({ projects }: { projects: Project[] }) {
  return (
    <section>
      <div className="mb-4 flex items-center gap-2 px-4">
        <FolderGit2 className="text-primary size-4" />
        <h2 className="text-sm font-semibold">Projects</h2>
      </div>

      <div className="space-y-3 px-4">
        {projects.map((project) => (
          <Card key={project.name} className="border shadow-none">
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <CardTitle className="text-sm font-semibold">{project.name}</CardTitle>
                {project.url && (
                  <a
                    href={project.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <ExternalLink className="size-3.5" />
                  </a>
                )}
              </div>
              <CardDescription className="text-xs">{project.description}</CardDescription>
            </CardHeader>
            <CardContent className="pt-0">
              <ul className="mb-3 space-y-1">
                {project.highlights.map((highlight, i) => (
                  <li key={i} className="text-muted-foreground flex gap-2 text-xs">
                    <span className="text-primary mt-0.5">-</span>
                    <span>{highlight}</span>
                  </li>
                ))}
              </ul>

              <div className="flex flex-wrap gap-1">
                {project.technologies.map((tech) => (
                  <Badge key={tech} variant="secondary" className="text-xs">
                    {tech}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}

function EducationSection({ education }: { education: Education[] }) {
  return (
    <section>
      <div className="mb-4 flex items-center gap-2 px-4">
        <GraduationCap className="text-primary size-4" />
        <h2 className="text-sm font-semibold">Education</h2>
      </div>

      <div className="space-y-3 px-4">
        {education.map((edu) => (
          <Card key={edu.institution} className="border-none shadow-none">
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-sm font-semibold">
                    {edu.degree} in {edu.field}
                  </CardTitle>
                  <CardDescription className="text-xs">{edu.institution}</CardDescription>
                </div>
                <Badge variant="outline" className="text-xs">
                  {edu.period}
                </Badge>
              </div>
            </CardHeader>
            {edu.highlights && edu.highlights.length > 0 && (
              <CardContent className="pt-0">
                <ul className="space-y-1">
                  {edu.highlights.map((highlight, i) => (
                    <li key={i} className="text-muted-foreground flex gap-2 text-xs">
                      <span className="text-primary mt-0.5">-</span>
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            )}
          </Card>
        ))}
      </div>
    </section>
  );
}

function LoadingState() {
  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-3">
          <Link href="/">
            <Button variant="ghost" size="icon-sm">
              <ArrowLeft className="size-4" />
            </Button>
          </Link>
          <div className="flex items-center gap-3">
            <div className="bg-primary text-primary-foreground flex size-8 items-center justify-center rounded-md">
              <BoxIcon className="size-4" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-sm leading-none font-semibold">Glass Box</h1>
              <p className="text-muted-foreground text-xs">Profile</p>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="text-primary size-8 animate-spin" />
          <p className="text-muted-foreground text-sm">Loading profile...</p>
        </div>
      </div>
    </div>
  );
}

function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="flex h-screen flex-col">
      <ProfileHeader />

      <div className="flex flex-1 items-center justify-center">
        <div className="flex flex-col items-center gap-4 px-4 text-center">
          <div className="bg-destructive/10 flex size-12 items-center justify-center rounded-full">
            <span className="text-2xl">!</span>
          </div>
          <div>
            <p className="text-sm font-medium">Failed to load profile</p>
            <p className="text-muted-foreground mt-1 text-xs">{error}</p>
          </div>
          <Button variant="outline" size="sm" onClick={onRetry}>
            Try again
          </Button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main Page
// =============================================================================

export default function ProfilePage() {
  const [data, setData] = useState<ProfileData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

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
    return <LoadingState />;
  }

  if (error || !data) {
    return <ErrorState error={error || "No data"} onRetry={loadProfile} />;
  }

  return (
    <div className="flex h-screen flex-col">
      <ProfileHeader profile={data.profile} />

      <ScrollArea className="flex-1">
        <main className="mx-auto max-w-3xl space-y-8 py-6">
          <ProfileSummary profile={data.profile} />

          <Separator />

          <FamilyGallery />

          <Separator />

          <ExperienceTimeline experiences={data.experiences} />

          <Separator />

          <SkillsVisualization skills={data.skills} />

          <Separator />

          <ProjectsSection projects={data.projects} />

          <Separator />

          <EducationSection education={data.education} />

          {/* Footer spacing */}
          <div className="h-8" />
        </main>
      </ScrollArea>
    </div>
  );
}
