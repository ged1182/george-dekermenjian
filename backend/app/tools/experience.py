"""Professional experience tools for the Glass Box Portfolio agent.

These tools provide structured information about George's professional
background, skills, and projects.
"""

from pydantic import BaseModel, Field


class Experience(BaseModel):
    """A professional experience entry."""

    company: str
    title: str
    role: str | None = None
    period: str
    location: str
    description: str
    highlights: list[str]
    technologies: list[str]
    logo: str | None = None


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
    github: str | None = None


class Education(BaseModel):
    """An education entry."""

    institution: str
    degree: str
    field: str
    period: str
    location: str
    highlights: list[str] | None = None


class ProfileInfo(BaseModel):
    """Profile metadata."""

    name: str
    title: str
    location: str
    email: str
    github: str
    linkedin: str
    summary: str


class ProfileData(BaseModel):
    """Complete profile data for the /profile endpoint."""

    profile: ProfileInfo
    experiences: list[Experience]
    skills: list["Skill"]
    projects: list[Project]
    education: list[Education]


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


# Profile metadata
PROFILE = ProfileInfo(
    name="George Dekermenjian",
    title="Director of Data & AI",
    location="Barcelona, Spain",
    email="ged1182@gmail.com",
    github="https://github.com/ged1182",
    linkedin="https://linkedin.com/in/gdekermenjian",
    summary="Hybrid technical executive who builds production AI systems with full audit trails—not POCs. "
    "Specializes in data platform modernization for regulated industries, implementing GenAI workflows "
    "that satisfy compliance requirements (AIFMD, GDPR) while delivering measurable ROI. Track record "
    "includes $1.2M digital transformations, 99.5% latency reductions, and AI document classification "
    "systems processing thousands of documents monthly. Hands-on leader (30-50% technical) who designs "
    "architectures end-to-end while owning strategy and C-suite alignment. Former mathematics professor "
    "who translates complex systems into business outcomes.",
)

# Professional experience data
EXPERIENCES: list[Experience] = [
    Experience(
        company="Fundcraft",
        title="VP Data & AI",
        period="Jul 2025 - Dec 2025",
        location="Remote (Luxembourg)",
        description="Luxembourg-based fund administrator (AIFMD regulated)",
        highlights=[
            "Built tamper-proof audit trail system for AI+human document classification workflows—every AI decision logged, every human override captured, full traceability for compliance (AIFMD, GDPR)",
            "Deployed GenAI document classification (OpenAI/Anthropic APIs) processing thousands of fund, KYC, and transaction documents monthly; reduced classification time from 45-60 seconds to near-zero (80%+ confident) or 10 seconds (human review), saving 150-300 hours/month",
            "Reduced financial reporting latency by 99.5% (40s → 200ms) through real-time architecture redesign using ClickHouse—eliminated client complaints on NAV reporting",
            "Scaled data team from 6 to 12 in 4 months; established Data Governance framework using dbt contracts and custom schema validation",
            "Led AI-First culture transformation: trained 40+ developers in AI-assisted development, reduced code review cycles by 50%",
        ],
        technologies=[
            "ClickHouse",
            "OpenAI",
            "Anthropic",
            "dbt",
            "Python",
            "AIFMD/GDPR Compliance",
        ],
    ),
    Experience(
        company="Decipher AI (YC W24)",
        title="Senior Data Platform Engineer",
        period="Mar 2025 - Jun 2025",
        location="Remote",
        description="AI-powered session replay analytics",
        highlights=[
            "Partnered with founders on data platform modernization for enterprise growth; worked in TypeScript/Next.js codebase with OpenAI SDK integration",
            "Executed zero-downtime cloud migration from Supabase to Azure PostgreSQL: partitioned tables, TTL policies, schema versioning—reduced query latency from 15s to 2s (87% improvement)",
            "Architected real-time analytics platform: ClickHouse with Kafka ingestion, MaterializedViews, AggregatingMergeTree—95% latency reduction for AI-powered funnel analysis",
        ],
        technologies=[
            "TypeScript",
            "Next.js",
            "OpenAI SDK",
            "Azure PostgreSQL",
            "ClickHouse",
            "Kafka",
        ],
    ),
    Experience(
        company="Mouseflow",
        title="Director of Data & Analytics",
        period="Jan 2023 - Feb 2025",
        location="Barcelona, Spain",
        description="Session replay and heatmap analytics platform",
        highlights=[
            "Led $1.2M digital transformation and cloud migration (GCP): migrated 500TB data estate across EU + US datacenters, processing 500M monthly pageviews—enabled 30% increase in enterprise customer adoption",
            "Built data organization from 1 to 4 members; established documentation standards, engineering best practices, and data quality frameworks",
            "Implemented real-time analytics on ClickHouse: 90% query latency reduction, enabled cohort retention analysis and funnel visualization previously impossible",
            "Partnered with CTO/CEO on data strategy alignment; secured executive buy-in for multi-year infrastructure investment",
        ],
        technologies=[
            "GCP",
            "ClickHouse",
            "BigQuery",
            "Dataflow",
            "Python",
        ],
    ),
    Experience(
        company="Mouseflow",
        title="Data Scientist",
        period="Oct 2021 - Dec 2022",
        location="Copenhagen, Denmark",
        description="Session replay and heatmap analytics platform",
        highlights=[
            "Conducted infrastructure assessment of legacy Elasticsearch and HBase systems; created prototype 'flows' visualization that became key enterprise differentiator",
            "Established cross-functional relationships with Product, Sales, and Customer Success to align technical solutions with business needs",
        ],
        technologies=[
            "Elasticsearch",
            "HBase",
            "Python",
            "Data Visualization",
        ],
    ),
    Experience(
        company="Independent",
        title="Cloud Data Solutions Consultant",
        period="2018 - Present",
        location="Remote",
        description="Startups and regulated industries",
        highlights=[
            "Architected cloud-native migrations and real-time analytics solutions using GCP (BigQuery, Dataflow, Pub/Sub) for clients transitioning from legacy systems",
            "Developed data strategies incorporating governance, security, and compliance requirements",
        ],
        technologies=[
            "GCP",
            "BigQuery",
            "Dataflow",
            "Pub/Sub",
            "Terraform",
        ],
    ),
    Experience(
        company="Cubris (A Thales Company)",
        title="Data Scientist",
        period="Nov 2020 - Sep 2021",
        location="Copenhagen, Denmark",
        description="Railway technology",
        highlights=[
            "Achieved 75% improvement in GPS data processing algorithms for European rail operations while maintaining accuracy standards",
        ],
        technologies=[
            "Python",
            "GPS Processing",
            "Algorithm Optimization",
        ],
    ),
    Experience(
        company="BMW Group",
        title="Data Scientist (Master's Thesis)",
        period="Jan 2020 - Jul 2020",
        location="Munich, Germany",
        description="Master's thesis research",
        highlights=[
            "Developed metamodel using adapted stochastic gradient descent for B-splines—reduced vehicle crash simulation time from 24+ hours to minutes",
        ],
        technologies=[
            "Python",
            "Machine Learning",
            "Numerical Optimization",
            "B-splines",
        ],
    ),
    Experience(
        company="Los Angeles City College",
        title="Professor of Mathematics",
        role="Including Mathematics Department Chair",
        period="2007 - 2017",
        location="Los Angeles, USA",
        description="Higher education",
        highlights=[
            "10 years in higher education: developed communication, organizational leadership, and ability to simplify complex technical concepts for diverse audiences",
        ],
        technologies=[
            "Mathematics",
            "Teaching",
            "Leadership",
            "Curriculum Development",
        ],
    ),
]

SKILLS: list[Skill] = [
    Skill(
        category="Real-Time Data & Analytics",
        skills=[
            "ClickHouse",
            "Kafka",
            "Materialized Views",
            "Low-Latency Architecture",
            "Streaming ETL",
            "BigQuery",
        ],
        proficiency="expert",
    ),
    Skill(
        category="Cloud & Infrastructure",
        skills=[
            "GCP (Professional Data Engineer certified)",
            "Azure",
            "PostgreSQL",
            "Terraform",
            "Docker",
            "Cloud Run",
            "Dataflow",
            "Pub/Sub",
        ],
        proficiency="expert",
    ),
    Skill(
        category="AI/ML & GenAI",
        skills=[
            "LLM APIs (OpenAI, Anthropic, Gemini)",
            "Agentic Frameworks (pydantic-ai, Temporal)",
            "RAG Pipelines",
            "Human-in-the-Loop Workflows",
            "Python",
            "FastAPI",
        ],
        proficiency="expert",
    ),
    Skill(
        category="Data Governance",
        skills=[
            "dbt contracts",
            "Custom Schema Validation",
            "Audit Trail Design",
            "AIFMD/GDPR Compliance",
        ],
        proficiency="proficient",
    ),
    Skill(
        category="Leadership",
        skills=[
            "Digital Transformation",
            "Team Scaling (1→12)",
            "Regulated Industries",
            "C-Suite Stakeholder Management",
        ],
        proficiency="expert",
    ),
]

PROJECTS: list[Project] = [
    Project(
        name="Glass Box Portfolio",
        description="Production-grade demonstration of explainable, agentic systems with transparent visibility into AI decision-making.",
        technologies=[
            "Next.js",
            "FastAPI",
            "pydantic-ai",
            "Gemini",
            "Vercel",
            "Cloud Run",
        ],
        highlights=[
            "Toggle between polished UX and transparent engineering view",
            "Real-time Brain Log showing agent reasoning and tool execution",
            "Codebase Oracle for answering questions about the system itself",
        ],
        url="https://george-dekermenjian.vercel.app",
        github="https://github.com/ged1182/george-dekermenjian",
    ),
    Project(
        name="Auditable AI Document Classification",
        description="AIFMD/GDPR compliant document classification system with full audit trails for fund administration.",
        technologies=[
            "OpenAI",
            "Anthropic",
            "Python",
            "ClickHouse",
            "dbt",
        ],
        highlights=[
            "Tamper-proof audit trail for AI+human workflows",
            "150-300 hours/month saved across operations team",
            "Full traceability for regulatory compliance",
        ],
    ),
    Project(
        name="Real-Time Financial Reporting",
        description="99.5% latency reduction for NAV reporting using ClickHouse real-time architecture.",
        technologies=[
            "ClickHouse",
            "Kafka",
            "MaterializedViews",
            "Python",
        ],
        highlights=[
            "Reduced reporting latency from 40s to 200ms",
            "Eliminated client complaints on NAV reporting",
            "Real-time architecture redesign",
        ],
    ),
]

EDUCATION: list[Education] = [
    Education(
        institution="Technical University of Munich",
        degree="M.S.",
        field="Mathematics in Data Science",
        period="2020",
        location="Munich, Germany",
        highlights=[
            "Master's thesis at BMW Group on crash simulation optimization",
        ],
    ),
    Education(
        institution="Claremont Graduate University",
        degree="M.S.",
        field="Mathematics",
        period="2009",
        location="Claremont, CA",
    ),
    Education(
        institution="American University of Beirut",
        degree="B.A.",
        field="Mathematics",
        period="2003",
        location="Beirut, Lebanon",
    ),
]


def get_professional_experience() -> ProfessionalExperience:
    """Get George's professional experience and work history.

    Returns structured information about past roles, responsibilities,
    and key achievements.
    """
    return ProfessionalExperience(
        experiences=EXPERIENCES,
        summary=f"George has {len(EXPERIENCES)} professional experiences spanning AI/ML, data engineering, and mathematics education.",
    )


def get_skills() -> SkillsResponse:
    """Get George's technical skills and proficiencies.

    Returns categorized skills with proficiency levels (expert, proficient, familiar).
    """
    return SkillsResponse(
        skills=SKILLS,
        summary=f"George has expertise across {len(SKILLS)} skill categories, with particular depth in real-time data systems and AI/ML.",
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


class EducationResponse(BaseModel):
    """Complete education response."""

    education: list[Education]
    summary: str


class ProfileResponse(BaseModel):
    """Profile info response."""

    profile: ProfileInfo


class LatestExperienceResponse(BaseModel):
    """Latest experience response."""

    experience: Experience
    summary: str


def get_education() -> EducationResponse:
    """Get George's educational background.

    Returns structured information about degrees and institutions.
    """
    return EducationResponse(
        education=EDUCATION,
        summary=f"George has {len(EDUCATION)} degree(s) in Mathematics and Data Science, plus Google Cloud Professional Data Engineer certification.",
    )


def get_profile() -> ProfileResponse:
    """Get George's profile information.

    Returns contact information and professional summary.
    """
    return ProfileResponse(profile=PROFILE)


def get_latest_experience() -> LatestExperienceResponse:
    """Get George's most recent professional experience.

    Returns information about the current role only.
    """
    latest = EXPERIENCES[0]
    return LatestExperienceResponse(
        experience=latest,
        summary=f"George's most recent role is {latest.title} at {latest.company}.",
    )


def get_full_profile() -> ProfileData:
    """Get complete profile data for the /profile endpoint.

    Returns all profile information including experiences, skills,
    projects, and education.
    """
    return ProfileData(
        profile=PROFILE,
        experiences=EXPERIENCES,
        skills=SKILLS,
        projects=PROJECTS,
        education=EDUCATION,
    )
