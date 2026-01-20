# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Glass Box Portfolio** - a production-grade demonstration of explainable, agentic systems. The portfolio toggles between "Opaque Mode" (clean UX) and "Glass Box Mode" (transparent engineering view showing agent reasoning, tool selection, and schema validation).

**Current Status**: Phase 1 MVP implemented. See `vision.md` for the complete product vision and phased development plan.

## Repository Structure

```
george-dekermenjian/
├── web/                          # Next.js 16 frontend
│   ├── app/                      # App Router pages
│   │   ├── layout.tsx            # Root layout with GlassBoxProvider
│   │   └── page.tsx              # Main page with chat + Brain Log
│   ├── components/
│   │   ├── ai-elements/          # AI Elements components (chat UI)
│   │   ├── chat/                 # Chat interface components
│   │   │   ├── ChatInterface.tsx # Main chat with AI SDK useChat
│   │   │   └── index.ts
│   │   ├── glass-box/            # Glass Box mode components
│   │   │   ├── BrainLog.tsx      # Brain Log panel
│   │   │   ├── GlassBoxProvider.tsx # Context for Glass Box state
│   │   │   ├── GlassBoxToggle.tsx # Toggle button
│   │   │   ├── LogEntry.tsx      # Individual log entry
│   │   │   └── index.ts
│   │   └── ui/                   # shadcn/ui components
│   └── lib/
│       ├── api.ts                # Backend API client + Brain Log types
│       └── utils.ts              # cn() helper
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint with /chat endpoint
│   │   ├── agent.py              # pydantic-ai agent with tools
│   │   ├── config.py             # Pydantic Settings
│   │   ├── tools/
│   │   │   ├── experience.py     # Professional experience tools
│   │   │   └── codebase.py       # Codebase Oracle tools
│   │   └── schemas/
│   │       └── brain_log.py      # Brain Log entry schemas
│   ├── Dockerfile                # Production Docker image
│   ├── cloud-run-service.yaml    # Cloud Run deployment config
│   ├── scripts/deploy.sh         # Deployment script
│   ├── pyproject.toml
│   └── .env.example
└── vision.md                     # Master vision document
```

## Development Commands

### Frontend (web/)

```bash
cd web
pnpm install          # Install dependencies
pnpm dev              # Start dev server (http://localhost:3000)
pnpm build            # Production build
pnpm lint             # Run ESLint
```

### Backend (backend/)

```bash
cd backend
uv sync                                    # Install dependencies
export GEMINI_API_KEY=your_api_key         # Set API key
uv run uvicorn app.main:app --reload       # Start dev server (http://localhost:8000)
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
- **Components**: shadcn/ui (base-lyra style) + AI Elements
- **AI Integration**: Vercel AI SDK v4 (`ai`, `@ai-sdk/react`)
- **Icons**: Lucide React
- **Utilities**: `cn()` helper in `lib/utils.ts` (clsx + tailwind-merge)

### Backend
- **Runtime**: Python 3.13+
- **Framework**: FastAPI
- **Agent Framework**: pydantic-ai with VercelAIAdapter for streaming
- **LLM**: Google Gemini (`google-gla:gemini-2.0-flash`)
- **Package Manager**: uv

## Architecture

### Glass Box Mode
The core differentiator is transparent visibility into agentic systems:
- **Opaque Mode**: Standard clean chat experience
- **Glass Box Mode**: Shows Brain Log panel with real-time agent reasoning, tool calls, validation status, and performance metrics

### Agent Tools
The pydantic-ai agent has 6 registered tools:

**Experience Tools** (`tools/experience.py`):
- `get_professional_experience()` - Returns work history and roles
- `get_skills()` - Returns categorized technical skills
- `get_projects()` - Returns notable project details

**Codebase Oracle Tools** (`tools/codebase.py`):
- `find_symbol(symbol_name)` - Find function/class definitions
- `get_file_content(file_path, start_line, end_line)` - Read file content
- `find_references(symbol_name)` - Find all usages of a symbol

### Brain Log Entry Types
```typescript
type LogEntryType = 'input' | 'routing' | 'tool_call' | 'validation' | 'performance';
type LogEntryStatus = 'pending' | 'success' | 'failure';
```

### API Endpoints
- `GET /` - API info
- `GET /health` - Health check with uptime
- `POST /chat` - Streaming chat endpoint (Vercel AI protocol)

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
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
CODEBASE_ROOT=/path/to/repo  # For Codebase Oracle
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

Available: conversation, message, prompt-input, tool, reasoning, chain-of-thought, code-block, sources, loader, panel, task, checkpoint, suggestion

### Path Aliases
TypeScript path alias configured: `@/*` maps to the web root:
```typescript
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useGlassBox } from "@/components/glass-box"
```

## Phase 1 Completion Checklist

- [x] Glass Box toggle shows/hides Brain Log panel
- [x] Agentic chat with streaming responses
- [x] Brain Log shows: input received, tool calls, validation, timing
- [x] Codebase Oracle tools implemented
- [x] Dockerfile and Cloud Run config ready
- [ ] Production deployment (pending)
- [ ] Cold start latency documented (pending)
