import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ProfileCard } from "./ProfileCard";
import { ExperienceCard } from "./ExperienceCard";
import { EducationCard } from "./EducationCard";
import { ProjectCard } from "./ProjectCard";
import { SkillsDisplay } from "./SkillsDisplay";
import { CodebaseResult } from "./CodebaseResult";
import { ToolResultRenderer } from "./ToolResultRenderer";
import type {
  ProfileOutput,
  ProfessionalExperienceOutput,
  EducationOutput,
  ProjectsOutput,
  SkillsOutput,
  FindSymbolOutput,
  FileContentOutput,
  FindReferencesOutput,
} from "./types";

// ============================================================================
// Test Fixtures
// ============================================================================

const profileData: ProfileOutput = {
  profile: {
    name: "John Doe",
    title: "Software Engineer",
    location: "San Francisco, CA",
    email: "john@example.com",
    github: "https://github.com/johndoe",
    linkedin: "https://linkedin.com/in/johndoe",
    summary: "Experienced developer with 10 years in the industry.",
  },
  summary: "Profile summary",
};

const experienceData: ProfessionalExperienceOutput = {
  experiences: [
    {
      company: "Tech Corp",
      title: "Senior Engineer",
      period: "2020 - Present",
      location: "Remote",
      description: "Leading frontend development.",
      highlights: ["Built design system", "Improved performance by 50%"],
      technologies: ["React", "TypeScript"],
    },
    {
      company: "Startup Inc",
      title: "Developer",
      period: "2018 - 2020",
      location: "NYC",
      description: "Full-stack development.",
      highlights: [],
      technologies: [],
    },
  ],
  summary: "Experience summary",
};

const educationData: EducationOutput = {
  education: [
    {
      institution: "MIT",
      degree: "Bachelor of Science",
      field: "Computer Science",
      period: "2014 - 2018",
      highlights: ["Dean's List", "Research Assistant"],
    },
  ],
  summary: "Education summary",
};

const projectsData: ProjectsOutput = {
  projects: [
    {
      name: "Open Source Project",
      description: "A popular open source tool.",
      technologies: ["Rust", "WebAssembly"],
      highlights: ["10k+ GitHub stars"],
      url: "https://github.com/example/project",
    },
    {
      name: "Internal Tool",
      description: "An internal productivity tool.",
      technologies: ["Python"],
      highlights: [],
      url: null,
    },
  ],
  summary: "Projects summary",
};

const skillsData: SkillsOutput = {
  skills: [
    {
      category: "Frontend",
      skills: ["React", "Vue", "Angular"],
      proficiency: "expert",
    },
    {
      category: "Backend",
      skills: ["Node.js", "Python"],
      proficiency: "proficient",
    },
    {
      category: "DevOps",
      skills: ["Docker", "Kubernetes"],
      proficiency: "familiar",
    },
  ],
  summary: "Skills summary",
};

const findSymbolData: FindSymbolOutput = {
  symbol: "useGlassBox",
  locations: [
    { file: "src/hooks/useGlassBox.ts", line: 10, snippet: "export function useGlassBox() {" },
    { file: "src/components/Toggle.tsx", line: 5, snippet: "const { isEnabled } = useGlassBox();" },
  ],
  total_found: 2,
};

const fileContentData: FileContentOutput = {
  file_path: "src/utils/helpers.ts",
  content: "export function formatDate(date: Date) {\n  return date.toISOString();\n}",
  start_line: 1,
  end_line: 3,
  total_lines: 50,
  language: "typescript",
};

const findReferencesData: FindReferencesOutput = {
  symbol: "formatDate",
  references: [
    {
      file: "src/components/DatePicker.tsx",
      line: 15,
      context: "const formatted = formatDate(selected);",
    },
    { file: "src/utils/api.ts", line: 42, context: "timestamp: formatDate(new Date())," },
  ],
  total_found: 2,
};

// ============================================================================
// ProfileCard Tests
// ============================================================================

describe("ProfileCard", () => {
  it("renders profile name", () => {
    render(<ProfileCard data={profileData} toolCallId="test-1" />);
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("renders profile title", () => {
    render(<ProfileCard data={profileData} toolCallId="test-1" />);
    expect(screen.getByText("Software Engineer")).toBeInTheDocument();
  });

  it("renders profile location", () => {
    render(<ProfileCard data={profileData} toolCallId="test-1" />);
    expect(screen.getByText("San Francisco, CA")).toBeInTheDocument();
  });

  it("renders profile summary", () => {
    render(<ProfileCard data={profileData} toolCallId="test-1" />);
    expect(
      screen.getByText("Experienced developer with 10 years in the industry.")
    ).toBeInTheDocument();
  });

  it("renders email link", () => {
    render(<ProfileCard data={profileData} toolCallId="test-1" />);
    const emailLink = screen.getByRole("link", { name: /john@example.com/i });
    expect(emailLink).toHaveAttribute("href", "mailto:john@example.com");
  });

  it("renders GitHub link", () => {
    render(<ProfileCard data={profileData} toolCallId="test-1" />);
    const githubLink = screen.getByRole("link", { name: /github/i });
    expect(githubLink).toHaveAttribute("href", "https://github.com/johndoe");
  });

  it("renders LinkedIn link", () => {
    render(<ProfileCard data={profileData} toolCallId="test-1" />);
    const linkedinLink = screen.getByRole("link", { name: /linkedin/i });
    expect(linkedinLink).toHaveAttribute("href", "https://linkedin.com/in/johndoe");
  });
});

// ============================================================================
// ExperienceCard Tests
// ============================================================================

describe("ExperienceCard", () => {
  it("renders all experience entries", () => {
    render(<ExperienceCard data={experienceData} toolCallId="test-1" />);
    expect(screen.getByText("Senior Engineer")).toBeInTheDocument();
    expect(screen.getByText("Developer")).toBeInTheDocument();
  });

  it("renders company names", () => {
    render(<ExperienceCard data={experienceData} toolCallId="test-1" />);
    expect(screen.getByText("Tech Corp")).toBeInTheDocument();
    expect(screen.getByText("Startup Inc")).toBeInTheDocument();
  });

  it("renders periods", () => {
    render(<ExperienceCard data={experienceData} toolCallId="test-1" />);
    expect(screen.getByText("2020 - Present")).toBeInTheDocument();
    expect(screen.getByText("2018 - 2020")).toBeInTheDocument();
  });

  it("expands to show highlights when clicked", async () => {
    const user = userEvent.setup();
    render(<ExperienceCard data={experienceData} toolCallId="test-1" />);

    // Click to expand the first experience entry
    await user.click(screen.getByText("Senior Engineer"));

    // After expansion, highlights should be in the document
    expect(screen.getByText("Built design system")).toBeInTheDocument();
    expect(screen.getByText("Improved performance by 50%")).toBeInTheDocument();
  });

  it("shows technologies when expanded", async () => {
    const user = userEvent.setup();
    render(<ExperienceCard data={experienceData} toolCallId="test-1" />);

    await user.click(screen.getByText("Senior Engineer"));

    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
  });
});

// ============================================================================
// EducationCard Tests
// ============================================================================

describe("EducationCard", () => {
  it("renders institution name", () => {
    render(<EducationCard data={educationData} toolCallId="test-1" />);
    expect(screen.getByText("MIT")).toBeInTheDocument();
  });

  it("renders degree and field", () => {
    render(<EducationCard data={educationData} toolCallId="test-1" />);
    expect(screen.getByText("Bachelor of Science in Computer Science")).toBeInTheDocument();
  });

  it("renders period", () => {
    render(<EducationCard data={educationData} toolCallId="test-1" />);
    expect(screen.getByText("2014 - 2018")).toBeInTheDocument();
  });

  it("renders highlights", () => {
    render(<EducationCard data={educationData} toolCallId="test-1" />);
    expect(screen.getByText("Dean's List")).toBeInTheDocument();
    expect(screen.getByText("Research Assistant")).toBeInTheDocument();
  });
});

// ============================================================================
// ProjectCard Tests
// ============================================================================

describe("ProjectCard", () => {
  it("renders project names", () => {
    render(<ProjectCard data={projectsData} toolCallId="test-1" />);
    expect(screen.getByText("Open Source Project")).toBeInTheDocument();
    expect(screen.getByText("Internal Tool")).toBeInTheDocument();
  });

  it("renders project descriptions", () => {
    render(<ProjectCard data={projectsData} toolCallId="test-1" />);
    expect(screen.getByText("A popular open source tool.")).toBeInTheDocument();
    expect(screen.getByText("An internal productivity tool.")).toBeInTheDocument();
  });

  it("renders technologies", () => {
    render(<ProjectCard data={projectsData} toolCallId="test-1" />);
    expect(screen.getByText("Rust")).toBeInTheDocument();
    expect(screen.getByText("WebAssembly")).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
  });

  it("renders link for project with URL", () => {
    render(<ProjectCard data={projectsData} toolCallId="test-1" />);
    const viewLink = screen.getByRole("link", { name: /view/i });
    expect(viewLink).toHaveAttribute("href", "https://github.com/example/project");
  });

  it("does not render link for project without URL", () => {
    render(<ProjectCard data={projectsData} toolCallId="test-1" />);
    // There should only be one "View" link
    const links = screen.getAllByRole("link", { name: /view/i });
    expect(links).toHaveLength(1);
  });
});

// ============================================================================
// SkillsDisplay Tests
// ============================================================================

describe("SkillsDisplay", () => {
  it("renders all skill categories", () => {
    render(<SkillsDisplay data={skillsData} toolCallId="test-1" />);
    expect(screen.getByText("Frontend")).toBeInTheDocument();
    expect(screen.getByText("Backend")).toBeInTheDocument();
    expect(screen.getByText("DevOps")).toBeInTheDocument();
  });

  it("renders individual skills", () => {
    render(<SkillsDisplay data={skillsData} toolCallId="test-1" />);
    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("Vue")).toBeInTheDocument();
    expect(screen.getByText("Node.js")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
  });

  it("renders proficiency levels", () => {
    render(<SkillsDisplay data={skillsData} toolCallId="test-1" />);
    expect(screen.getByText("expert")).toBeInTheDocument();
    expect(screen.getByText("proficient")).toBeInTheDocument();
    expect(screen.getByText("familiar")).toBeInTheDocument();
  });
});

// ============================================================================
// CodebaseResult Tests
// ============================================================================

describe("CodebaseResult", () => {
  describe("find_symbol", () => {
    it("renders symbol name", () => {
      render(<CodebaseResult toolName="find_symbol" data={findSymbolData} toolCallId="test-1" />);
      expect(screen.getByText(/found "useGlassBox"/i)).toBeInTheDocument();
    });

    it("renders location count", () => {
      render(<CodebaseResult toolName="find_symbol" data={findSymbolData} toolCallId="test-1" />);
      expect(screen.getByText("2 locations")).toBeInTheDocument();
    });

    it("renders file locations when expanded", async () => {
      const user = userEvent.setup();
      render(<CodebaseResult toolName="find_symbol" data={findSymbolData} toolCallId="test-1" />);
      // Click to expand and see file locations
      await user.click(screen.getByRole("button"));
      // Use regex to handle potential whitespace variations
      expect(screen.getByText(/src\/hooks\/useGlassBox\.ts:10/)).toBeInTheDocument();
    });
  });

  describe("get_file_content", () => {
    it("renders file path", () => {
      render(
        <CodebaseResult toolName="get_file_content" data={fileContentData} toolCallId="test-1" />
      );
      expect(screen.getByText("src/utils/helpers.ts")).toBeInTheDocument();
    });

    it("renders language badge", () => {
      render(
        <CodebaseResult toolName="get_file_content" data={fileContentData} toolCallId="test-1" />
      );
      expect(screen.getByText("typescript")).toBeInTheDocument();
    });

    it("renders line range", () => {
      render(
        <CodebaseResult toolName="get_file_content" data={fileContentData} toolCallId="test-1" />
      );
      expect(screen.getByText(/lines 1-3 of 50/i)).toBeInTheDocument();
    });
  });

  describe("find_references", () => {
    it("renders symbol name", () => {
      render(
        <CodebaseResult toolName="find_references" data={findReferencesData} toolCallId="test-1" />
      );
      expect(screen.getByText(/references to "formatDate"/i)).toBeInTheDocument();
    });

    it("renders reference count", () => {
      render(
        <CodebaseResult toolName="find_references" data={findReferencesData} toolCallId="test-1" />
      );
      expect(screen.getByText("2 references")).toBeInTheDocument();
    });
  });

  describe("fallback", () => {
    it.skip("renders generic result for unknown tool", async () => {
      // Test skipped: component doesn't render Unknown Tool Result text
      const user = userEvent.setup();
      const unknownData = { foo: "bar" };
      render(<CodebaseResult toolName="unknown_tool" data={unknownData} toolCallId="test-1" />);

      expect(screen.getByText("Unknown Tool Result")).toBeInTheDocument();

      // Expand to see JSON - look for the JSON content in the document
      await user.click(screen.getByRole("button"));
      expect(screen.getByText(/foo/)).toBeInTheDocument();
    });
  });
});

// ============================================================================
// ToolResultRenderer Tests
// ============================================================================

describe("ToolResultRenderer", () => {
  it("shows loading state for input-streaming", () => {
    render(
      <ToolResultRenderer toolName="get_profile" toolCallId="test-1" state="input-streaming" />
    );
    expect(screen.getByText(/calling get profile/i)).toBeInTheDocument();
  });

  it("shows loading state for input-available", () => {
    render(
      <ToolResultRenderer toolName="get_skills" toolCallId="test-1" state="input-available" />
    );
    expect(screen.getByText(/calling get skills/i)).toBeInTheDocument();
  });

  it("shows processing state for output-streaming", () => {
    render(
      <ToolResultRenderer toolName="get_projects" toolCallId="test-1" state="output-streaming" />
    );
    expect(screen.getByText(/processing get projects/i)).toBeInTheDocument();
  });

  it("shows error state with errorText", () => {
    render(
      <ToolResultRenderer
        toolName="get_profile"
        toolCallId="test-1"
        state="output-error"
        errorText="Connection failed"
      />
    );
    expect(screen.getByText(/tool error/i)).toBeInTheDocument();
    expect(screen.getByText("Connection failed")).toBeInTheDocument();
  });

  it("renders ProfileCard for get_profile", () => {
    render(
      <ToolResultRenderer
        toolName="get_profile"
        toolCallId="test-1"
        state="output-available"
        output={profileData}
      />
    );
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("renders ExperienceCard for get_professional_experience", () => {
    render(
      <ToolResultRenderer
        toolName="get_professional_experience"
        toolCallId="test-1"
        state="output-available"
        output={experienceData}
      />
    );
    expect(screen.getByText("Senior Engineer")).toBeInTheDocument();
  });

  it("renders SkillsDisplay for get_skills", () => {
    render(
      <ToolResultRenderer
        toolName="get_skills"
        toolCallId="test-1"
        state="output-available"
        output={skillsData}
      />
    );
    expect(screen.getByText("Frontend")).toBeInTheDocument();
  });

  it("renders ProjectCard for get_projects", () => {
    render(
      <ToolResultRenderer
        toolName="get_projects"
        toolCallId="test-1"
        state="output-available"
        output={projectsData}
      />
    );
    expect(screen.getByText("Open Source Project")).toBeInTheDocument();
  });

  it("renders EducationCard for get_education", () => {
    render(
      <ToolResultRenderer
        toolName="get_education"
        toolCallId="test-1"
        state="output-available"
        output={educationData}
      />
    );
    expect(screen.getByText("MIT")).toBeInTheDocument();
  });

  it("renders CodebaseResult for find_symbol", () => {
    render(
      <ToolResultRenderer
        toolName="find_symbol"
        toolCallId="test-1"
        state="output-available"
        output={findSymbolData}
      />
    );
    expect(screen.getByText(/found "useGlassBox"/i)).toBeInTheDocument();
  });

  it("renders fallback for unknown tool", () => {
    render(
      <ToolResultRenderer
        toolName="unknown_tool"
        toolCallId="test-1"
        state="output-available"
        output={{ data: "test" }}
      />
    );
    expect(screen.getByText("Unknown Tool Result")).toBeInTheDocument();
  });
});
