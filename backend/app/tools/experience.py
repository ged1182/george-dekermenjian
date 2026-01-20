"""Professional experience tools for the Glass Box Portfolio agent.

These tools provide structured information about George's professional
background, skills, and projects.
"""

from pydantic import BaseModel, Field


class Experience(BaseModel):
    """A professional experience entry."""

    company: str
    title: str
    period: str
    description: str
    highlights: list[str]
    technologies: list[str]


class Skill(BaseModel):
    """A skill category with proficiency."""

    category: str
    skills: list[str]
    proficiency: str = Field(description="One of: expert, proficient, familiar")


class Project(BaseModel):
    """A project entry."""

    name: str
    description: str
    technologies: list[str]
    highlights: list[str]
    url: str | None = None


class ProfessionalExperience(BaseModel):
    """Complete professional experience response."""

    experiences: list[Experience]
    summary: str


class SkillsResponse(BaseModel):
    """Complete skills response."""

    skills: list[Skill]
    summary: str


class ProjectsResponse(BaseModel):
    """Complete projects response."""

    projects: list[Project]
    summary: str


# Professional experience data
EXPERIENCES: list[Experience] = [
    Experience(
        company="Landing AI",
        title="Staff Software Engineer",
        period="2022 - Present",
        description="Leading development of agentic AI systems and production ML infrastructure.",
        highlights=[
            "Architected and built document intelligence platform processing millions of documents",
            "Designed multi-tenant SaaS architecture with hot/cold storage for compliance",
            "Led adoption of pydantic-ai for structured agent development",
            "Built real-time streaming inference pipelines with sub-second latency",
        ],
        technologies=["Python", "FastAPI", "pydantic-ai", "GCP", "Cloud Run", "Document AI", "PostgreSQL"],
    ),
    Experience(
        company="Previous Company",
        title="Senior Software Engineer",
        period="2019 - 2022",
        description="Full-stack development with focus on data-intensive applications.",
        highlights=[
            "Built real-time data processing pipelines handling 100K+ events/second",
            "Led migration from monolith to microservices architecture",
            "Mentored team of 5 engineers on best practices and code quality",
        ],
        technologies=["Python", "TypeScript", "React", "PostgreSQL", "Redis", "Kubernetes"],
    ),
]

SKILLS: list[Skill] = [
    Skill(
        category="AI/ML Engineering",
        skills=["pydantic-ai", "LangChain", "Gemini", "Claude", "OpenAI", "RAG Systems", "Agent Architectures"],
        proficiency="expert",
    ),
    Skill(
        category="Backend Development",
        skills=["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "gRPC", "REST APIs"],
        proficiency="expert",
    ),
    Skill(
        category="Frontend Development",
        skills=["TypeScript", "React", "Next.js", "Tailwind CSS", "Vercel AI SDK"],
        proficiency="proficient",
    ),
    Skill(
        category="Cloud & Infrastructure",
        skills=["GCP", "Cloud Run", "Cloud SQL", "Pub/Sub", "Docker", "Kubernetes", "Terraform"],
        proficiency="expert",
    ),
    Skill(
        category="Data Engineering",
        skills=["Apache Beam", "BigQuery", "Data Pipelines", "ETL", "Stream Processing"],
        proficiency="proficient",
    ),
]

PROJECTS: list[Project] = [
    Project(
        name="Glass Box Portfolio",
        description="Production-grade demonstration of explainable, agentic systems with transparent visibility into AI decision-making.",
        technologies=["Next.js", "FastAPI", "pydantic-ai", "Gemini", "Vercel", "Cloud Run"],
        highlights=[
            "Toggle between polished UX and transparent engineering view",
            "Real-time Brain Log showing agent reasoning and tool execution",
            "Codebase Oracle for answering questions about the system itself",
        ],
        url="https://github.com/george-dekermenjian/george-dekermenjian",
    ),
    Project(
        name="DocIntel",
        description="Enterprise document intelligence platform with schema projection and compliance-ready architecture.",
        technologies=["FastAPI", "Cloud Run", "Document AI", "PostgreSQL", "GCS"],
        highlights=[
            "Hot/Cold architecture for fast queries and compliance storage",
            "Multi-schema projection - ingest once, query many ways",
            "Row-level security for multi-tenant isolation",
        ],
    ),
]


def get_professional_experience() -> ProfessionalExperience:
    """Get George's professional experience and work history.

    Returns structured information about past roles, responsibilities,
    and key achievements.
    """
    return ProfessionalExperience(
        experiences=EXPERIENCES,
        summary=f"George has {len(EXPERIENCES)} professional experiences spanning AI/ML engineering and full-stack development.",
    )


def get_skills() -> SkillsResponse:
    """Get George's technical skills and proficiencies.

    Returns categorized skills with proficiency levels (expert, proficient, familiar).
    """
    return SkillsResponse(
        skills=SKILLS,
        summary=f"George has expertise across {len(SKILLS)} skill categories, with particular depth in AI/ML engineering and backend development.",
    )


def get_projects() -> ProjectsResponse:
    """Get George's notable projects and contributions.

    Returns detailed information about significant projects including
    technologies used and key highlights.
    """
    return ProjectsResponse(
        projects=PROJECTS,
        summary=f"George has worked on {len(PROJECTS)} notable projects demonstrating production-grade AI systems.",
    )
