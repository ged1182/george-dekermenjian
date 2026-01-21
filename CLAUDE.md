# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Glass Box Portfolio** - a production-grade demonstration of explainable, agentic systems. The portfolio toggles between "Opaque Mode" (clean UX) and "Glass Box Mode" (transparent engineering view showing agent reasoning, tool selection, and schema validation).

**Current Status**: Phase 1 MVP implemented. See `vision.md` for the complete product vision and phased development plan.

## Repository Structure

```
george-dekermenjian/
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions CI pipeline
├── web/                          # Next.js 16 frontend
│   ├── app/                      # App Router pages
│   │   ├── layout.tsx            # Root layout with GlassBoxProvider
│   │   ├── page.tsx              # Main page with chat + Brain Log
│   │   ├── profile/
│   │   │   └── page.tsx          # Profile page
│   │   └── globals.css           # Global styles
│   ├── components/
│   │   ├── ai-elements/          # AI Elements components (chat UI)
│   │   │   ├── chain-of-thought.tsx
│   │   │   ├── checkpoint.tsx
│   │   │   ├── code-block.tsx
│   │   │   ├── conversation.tsx
│   │   │   ├── loader.tsx
│   │   │   ├── message.tsx
│   │   │   ├── panel.tsx
│   │   │   ├── prompt-input.tsx
│   │   │   ├── reasoning.tsx
│   │   │   ├── shimmer.tsx
│   │   │   ├── sources.tsx
│   │   │   ├── suggestion.tsx
│   │   │   ├── task.tsx
│   │   │   ├── tool.tsx
│   │   │   └── ai-elements.test.tsx
│   │   ├── chat/                 # Chat interface components
│   │   │   ├── ChatInterface.tsx # Main chat with AI SDK useChat
│   │   │   └── index.ts
│   │   ├── glass-box/            # Glass Box mode components
│   │   │   ├── BrainLog.tsx      # Brain Log panel
│   │   │   ├── BrainLog.test.tsx
│   │   │   ├── GlassBoxProvider.tsx # Context for Glass Box state
│   │   │   ├── GlassBoxProvider.test.tsx
│   │   │   ├── GlassBoxToggle.tsx # Toggle button
│   │   │   ├── GlassBoxToggle.test.tsx
│   │   │   ├── LogEntry.tsx      # Individual log entry
│   │   │   └── index.ts
│   │   ├── tool-results/         # Tool result renderers
│   │   │   ├── CodebaseResult.tsx
│   │   │   ├── EducationCard.tsx
│   │   │   ├── ExperienceCard.tsx
│   │   │   ├── ProfileCard.tsx
│   │   │   ├── ProjectCard.tsx
│   │   │   ├── SkillsDisplay.tsx
│   │   │   ├── ToolResultRenderer.tsx
│   │   │   ├── tool-results.test.tsx
│   │   │   ├── types.ts
│   │   │   └── index.ts
│   │   └── ui/                   # shadcn/ui components
│   ├── lib/
│   │   ├── api.ts                # Backend API client + Brain Log types
│   │   ├── api.test.ts
│   │   └── utils.ts              # cn() helper
│   ├── vitest.config.ts          # Vitest configuration
│   └── vitest.setup.ts           # Vitest setup
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI entrypoint with /chat endpoint
│   │   ├── agent.py              # pydantic-ai agent with tools
│   │   ├── config.py             # Pydantic Settings
│   │   ├── brain_log_stream.py   # Brain Log streaming utilities
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── experience.py     # Professional experience tools
│   │   │   ├── codebase.py       # Codebase Oracle tools
│   │   │   ├── architecture.py   # Module structure analysis
│   │   │   ├── semantic.py       # LSP-powered semantic analysis
│   │   │   └── lsp_client.py     # Language Server Protocol client
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── brain_log.py      # Brain Log entry schemas
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py           # pytest fixtures
│   │   ├── test_main.py
│   │   ├── test_config.py
│   │   ├── test_experience.py
│   │   ├── test_codebase.py
│   │   ├── test_architecture.py
│   │   ├── test_semantic.py
│   │   ├── test_lsp_client.py
│   │   ├── test_brain_log.py
│   │   └── test_brain_log_stream.py
│   ├── scripts/
│   │   └── deploy.sh             # Cloud Run deployment script
│   ├── Dockerfile                # Production Docker image
│   ├── cloud-run-service.yaml    # Cloud Run deployment config
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env.example
│   └── README.md
├── vision.md                     # Master vision document
├── CONTRIBUTING.md               # Contribution guidelines
├── SECURITY.md                   # Security policy
├── LICENSE                       # MIT License
├── Makefile                      # Development commands
└── CLAUDE.md                     # This file
```

## Development Commands

### Frontend (web/)

```bash
cd web
pnpm install          # Install dependencies
pnpm dev              # Start dev server (http://localhost:3000)
pnpm build            # Production build
pnpm lint             # Run ESLint
pnpm typecheck        # TypeScript type checking
pnpm test             # Run Vitest tests
```

### Backend (backend/)

```bash
cd backend
uv sync                                    # Install dependencies
uv sync --dev                              # Install with dev dependencies
export GEMINI_API_KEY=your_api_key         # Set API key
uv run uvicorn app.main:app --reload       # Start dev server (http://localhost:8000)
uv run pytest                              # Run tests
uv run ruff check app/                     # Lint
uv run ruff format app/                    # Format
uv run mypy app/                           # Type check
```

### Using Makefile

```bash
make install    # Install all dependencies
make dev        # Run both frontend and backend
make test       # Run all tests
make lint       # Run linters
make format     # Format code
```

### Running Both Together

1. Start backend: `cd backend && uv run uvicorn app.main:app --reload`
2. Start frontend: `cd web && pnpm dev`
3. Open http://localhost:3000

## Tech Stack

### Frontend
- **Framework**: Next.js 16.1 with App Router and Turbopack
- **React**: 19.x
- **Styling**: Tailwind CSS v4 with CSS variable theming
- **Components**: shadcn/ui + AI Elements library
- **AI Integration**: Vercel AI SDK v5 (`ai`, `@ai-sdk/react`)
- **Animation**: Motion (formerly Framer Motion)
- **Icons**: Lucide React, HugeIcons
- **Testing**: Vitest
- **Utilities**: `cn()` helper in `lib/utils.ts` (clsx + tailwind-merge)

### Backend
- **Runtime**: Python 3.12+
- **Framework**: FastAPI
- **Agent Framework**: pydantic-ai with VercelAIAdapter for streaming
- **LLM**: Google Gemini (`google-gla:gemini-3-flash-preview`) with thinking/reasoning enabled
- **Package Manager**: uv
- **Testing**: pytest-asyncio (mode=auto) with httpx for async testing

## Architecture

### Glass Box Mode
The core differentiator is transparent visibility into agentic systems:
- **Opaque Mode**: Standard clean chat experience
- **Glass Box Mode**: Shows Brain Log panel with real-time agent reasoning, tool calls, validation status, and performance metrics

### Agent Tools
The pydantic-ai agent currently has **11 registered tools** (defined in `agent.py`), all wrapped with `logged_tool` decorator for Brain Log integration:

**Experience Tools** (`tools/experience.py`):
- `get_professional_experience()` - Returns work history and roles
- `get_skills()` - Returns categorized technical skills
- `get_projects()` - Returns notable project details

**Codebase Oracle Tools** (`tools/codebase.py`):
- `clone_codebase()` - Clone/access the repository (call first for codebase questions)
- `get_folder_tree(path)` - See directory structure
- `get_file_content(file_path, start_line, end_line)` - Read file content with optional line range

**Semantic (LSP-Powered) Tools** (`tools/semantic.py`):
- `go_to_definition(file_path, symbol)` - Find where a symbol is defined
- `find_all_references(file_path, symbol)` - Find all usages of a symbol
- `get_type_info(file_path, symbol)` - Get type signatures and documentation
- `get_document_symbols(file_path)` - See structure of a file
- `get_callers(file_path, symbol)` - Find what calls a function

**Additional Tool Modules** (available but not currently registered in agent):
- `tools/architecture.py` - `get_module_structure()`, `get_dependency_graph()`, `get_api_contract()`
- `tools/lsp_client.py` - Language Server Protocol client manager

### Brain Log Entry Types
The Brain Log captures a complete audit trail of agent activity:
```typescript
type LogEntryType = 'input' | 'thinking' | 'text' | 'tool_call' | 'tool_result' | 'performance';
type LogEntryStatus = 'pending' | 'success' | 'failure';
```

Entry types:
- `input` - User message received
- `thinking` - Model reasoning/thinking (when enabled via GoogleModelSettings)
- `text` - Model text output
- `tool_call` - Tool invocation (pending state)
- `tool_result` - Tool completion with result preview or error
- `performance` - Request timing (total_ms, ttft_ms)

### API Endpoints
- `GET /` - API info
- `GET /health` - Health check with uptime
- `GET /profile` - Full profile data for profile page
- `POST /chat` - Streaming chat endpoint with Brain Log (Vercel AI protocol)
- `GET /docs` - OpenAPI documentation
- `GET /redoc` - ReDoc documentation

## Deployment

### Frontend (Vercel)
```bash
cd web && vercel --prod
```

### Backend (Cloud Run)
```bash
cd backend
./scripts/deploy.sh --project YOUR_PROJECT_ID
```

**Prerequisites**:
1. Enable Cloud Run and Secret Manager APIs
2. Create secret: `echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-`

## Environment Variables

### Frontend (`web/.env.local`)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Backend (`backend/.env`)
```
GEMINI_API_KEY=your_gemini_api_key
DEBUG=false
CODEBASE_ROOT=/path/to/repo  # For Codebase Oracle (defaults to cwd)
```

## Component Patterns

### Adding shadcn/ui Components
```bash
cd web
npx shadcn@latest add <component-name>
```

### Adding AI Elements Components
```bash
cd web
pnpm dlx ai-elements@latest add <component-name>
```

Available: conversation, message, prompt-input, tool, reasoning, chain-of-thought, code-block, sources, loader, panel, task, checkpoint, suggestion, shimmer

### Path Aliases
TypeScript path alias configured: `@/*` maps to the web root:
```typescript
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useGlassBox } from "@/components/glass-box"
```

## Testing

### Backend Tests
```bash
cd backend
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose output
uv run pytest --cov=app          # With coverage
uv run pytest tests/test_main.py # Run specific file
```

### Frontend Tests
```bash
cd web
pnpm test                        # Run all tests
pnpm test:watch                  # Watch mode
pnpm test:coverage               # With coverage
```

## Code Quality

### Backend
- **Linting**: ruff (fast Python linter)
- **Formatting**: ruff format
- **Type Checking**: mypy with strict mode
- **Testing**: pytest with 90%+ coverage target

### Frontend
- **Linting**: ESLint with Next.js config
- **Formatting**: Prettier
- **Type Checking**: TypeScript strict mode
- **Testing**: Vitest with React Testing Library

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push:
1. Backend: lint, type check, test
2. Frontend: lint, type check, build, test

## Phase 1 Completion Checklist

- [x] Glass Box toggle shows/hides Brain Log panel
- [x] Agentic chat with streaming responses
- [x] Brain Log shows: input, thinking, text, tool calls, tool results, timing
- [x] Codebase Oracle tools (clone, folder tree, file content)
- [x] Semantic/LSP tools (go_to_definition, find_references, type_info, etc.)
- [x] Experience tools (professional_experience, skills, projects)
- [x] Dockerfile and Cloud Run config ready
- [x] CI/CD pipeline configured (GitHub Actions)
- [x] Test suite with pytest-asyncio (backend) and vitest (frontend)
- [ ] Production deployment (pending)
- [ ] Cold start latency documented (pending)
