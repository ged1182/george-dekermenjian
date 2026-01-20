"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { SkillsOutput, Skill } from "./types";

interface SkillsDisplayProps {
  data: SkillsOutput;
  toolCallId: string;
}

export function SkillsDisplay({ data }: SkillsDisplayProps) {
  return (
    <div className="my-4 space-y-4">
      {data.skills.map((skillGroup) => (
        <SkillCategory key={skillGroup.category} skill={skillGroup} />
      ))}
    </div>
  );
}

interface SkillCategoryProps {
  skill: Skill;
}

function SkillCategory({ skill }: SkillCategoryProps) {
  const proficiencyConfig = getProficiencyConfig(skill.proficiency);

  return (
    <div className="bg-card text-card-foreground rounded-lg border p-4 shadow-sm">
      {/* Header with proficiency indicator */}
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-foreground font-semibold">{skill.category}</h4>
        <div className="flex items-center gap-2">
          <ProficiencyBar proficiency={skill.proficiency} />
          <span className={cn("text-xs font-medium capitalize", proficiencyConfig.textColor)}>
            {skill.proficiency}
          </span>
        </div>
      </div>

      {/* Skill tags */}
      <div className="flex flex-wrap gap-2">
        {skill.skills.map((skillName) => (
          <Badge
            key={skillName}
            variant="outline"
            className={cn("px-2.5 py-1 text-xs", proficiencyConfig.badgeClass)}
          >
            {skillName}
          </Badge>
        ))}
      </div>
    </div>
  );
}

interface ProficiencyBarProps {
  proficiency: "expert" | "proficient" | "familiar";
}

function ProficiencyBar({ proficiency }: ProficiencyBarProps) {
  const config = getProficiencyConfig(proficiency);

  return (
    <div className="flex gap-0.5">
      {[1, 2, 3].map((level) => (
        <div
          key={level}
          className={cn(
            "h-3 w-2 rounded-sm transition-colors",
            level <= config.level ? config.barColor : "bg-muted"
          )}
        />
      ))}
    </div>
  );
}

function getProficiencyConfig(proficiency: "expert" | "proficient" | "familiar") {
  switch (proficiency) {
    case "expert":
      return {
        level: 3,
        barColor: "bg-green-500",
        textColor: "text-green-600 dark:text-green-400",
        badgeClass: "border-green-500/30 bg-green-500/10 text-green-700 dark:text-green-300",
      };
    case "proficient":
      return {
        level: 2,
        barColor: "bg-blue-500",
        textColor: "text-blue-600 dark:text-blue-400",
        badgeClass: "border-blue-500/30 bg-blue-500/10 text-blue-700 dark:text-blue-300",
      };
    case "familiar":
      return {
        level: 1,
        barColor: "bg-amber-500",
        textColor: "text-amber-600 dark:text-amber-400",
        badgeClass: "border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-300",
      };
    default:
      return {
        level: 1,
        barColor: "bg-muted-foreground",
        textColor: "text-muted-foreground",
        badgeClass: "",
      };
  }
}
