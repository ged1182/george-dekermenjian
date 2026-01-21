Below is a **self-contained, scope-reduced, production-credible vision document**, written in the same vein and level of rigor as your original, but explicitly **designed to ship after Phase 1** and to scale in clarity—not spectacle—thereafter.

This version assumes **no prior context** and is suitable to hand directly to:

* a hiring manager,
* a technical founder,
* or a staff-level reviewer.

---

# **Project Vision: The Glass Box Portfolio**

**A Production-Grade Demonstration of Explainable, Agentic Systems**

---

## **1. Executive Summary**

Most technical portfolios are **black boxes**: they present polished outcomes without exposing the decision-making, architecture, and failure modes behind them.

The **Glass Box Portfolio** is a deliberately different approach.

It is a **deployable, production-grade web application** that allows users to toggle between:

* a **polished, user-facing experience**, and
* a **transparent engineering view** that reveals how modern AI systems actually behave in production.

The goal is not to overwhelm with internals, but to demonstrate **intentional transparency**:

* how inputs flow through an agentic system,
* how decisions are validated,
* how failures are handled,
* and how infrastructure constraints shape design choices.

This portfolio is designed to answer one question clearly:

> *“Can this person build AI systems that work reliably, explain themselves, and survive real-world conditions?”*

---

## **2. Design Principle: Transparency by Intent, Not Exhaustion**

This project rejects the idea that “more visibility is always better.”

Instead, it follows three principles:

1. **Progressive Disclosure**
   Internal details are revealed only when relevant to the user’s current interaction.

2. **Decision-Centric Transparency**
   The system exposes *why* something happened—not just *what* happened.

3. **Production Realism**
   Every visible behavior corresponds to something that would exist in a real system: validation, routing, latency, retries, and constraints.

This is not an observability dashboard.
It is a **technical narrative system**.

---

## **3. The Core Mechanism: The Glass Box Toggle**

At the center of the application is a global toggle:

### **Mode A: Opaque Mode (Default)**

* Clean, minimalist interface
* Smooth interactions
* No visible system internals
* Optimized for non-technical users

This mode answers:

> “What does this system do?”

---

### **Mode B: Glass Box Mode**

When enabled, the same interaction reveals:

* structured system logs,
* agent decisions,
* schema validation outcomes,
* and performance characteristics.

This mode answers:

> “How and why does this system behave the way it does?”

The key constraint: **the UI does not change behavior**—only visibility.

---

## **4. Core Feature: Production-Grade Agentic Chat**

The portfolio centers around a **single, high-quality interaction**: an agentic chat interface.

This is not a generic chatbot.

### **4.1 Functional Purpose**

The agent answers questions about:

* the author’s professional experience,
* system architecture decisions,
* and the codebase that powers the portfolio itself.

The agent is built using a **structured agent framework** with:

* explicit tool definitions,
* schema-validated outputs,
* and controlled failure handling.

---

### **4.2 Glass Box View: The Brain Log**

When Glass Box Mode is enabled, a secondary panel appears alongside the chat.

It reveals, in real time:

1. **Input Handling**

   * User input received
   * Normalized request shape

2. **Routing Decision**

   * Which tool or reasoning path was selected
   * Why it was selected (rule or heuristic)

3. **Validation**

   * Schema used to validate the model output
   * Pass / fail status
   * Fallback behavior if validation fails

4. **Performance**

   * Time to first token (TTFT)
   * Total request duration

This log is **human-readable**, not raw JSON by default.

---

### **4.3 Failure as a First-Class Citizen**

The system intentionally supports visible failure modes:

* Schema validation failure
* Tool timeout
* Missing context
* Partial responses

In Glass Box Mode, failures are:

* clearly labeled,
* explained in plain language,
* and shown with the system’s recovery action.

This demonstrates maturity far more than perfect responses.

---

## **5. Meaningful RAG: The Codebase Oracle**

Instead of generic text-based retrieval, the portfolio includes a **Codebase Oracle**—a system that answers technical questions by *structurally understanding the code*.

---

### **5.1 Architectural Pattern**

The application runs as a containerized service with two internal roles:

1. **Main Application**

   * Serves the web UI and API
   * Hosts the agent orchestration layer

2. **Codebase Oracle (Sidecar Role)**

   * Has access to the repository source
   * Exposes code intelligence tools

This separation mirrors real-world isolation of responsibilities.

---

### **5.2 How the Oracle Works**

When a user asks a technical question such as:

> “How does authentication work in this system?”

The agent:

1. Delegates the query to the Oracle
2. Uses language-server tools to:

   * locate symbols,
   * resolve definitions,
   * find references
3. Synthesizes a structured explanation

This avoids hallucinated explanations and demonstrates **tool-grounded reasoning**.

---

### **5.3 Glass Box Visualization**

In Glass Box Mode, the UI shows:

* which files are being inspected,
* which symbols are resolved,
* and how components relate to each other.

This is rendered as a **simple dependency list or graph**, not a 3D visualization.

Clarity is prioritized over spectacle.

---

## **6. Infrastructure Reality (Minimal but Honest)**

The portfolio intentionally exposes **only one infrastructure dimension**:

### **Request-Level Telemetry**

In Glass Box Mode, each interaction shows:

* request duration,
* container instance identifier,
* and cold vs warm start indication (if applicable).

This grounds the system in real deployment constraints without becoming an ops demo.

---

## **7. Tech Stack & Infrastructure**

### **7.1 Frontend**

| Layer | Technology | Notes |
|-------|------------|-------|
| Framework | **Next.js 16.x** | TypeScript, App Router |
| Styling | **Tailwind CSS** | Utility-first CSS |
| Components | **shadcn/ui** | Accessible, customizable primitives |
| AI UI | **Vercel AI SDK** | `ai` package for streaming chat UI |
| Auth | **Clerk** *(optional)* | Deeper experience for logged-in users |
| Deployment | **Vercel** | Edge-optimized, zero-config |

### **7.2 Backend**

| Layer | Technology | Notes |
|-------|------------|-------|
| Runtime | **Python 3.12+** | Stable with latest features |
| Framework | **FastAPI** | Async-first, OpenAPI generation |
| Agent Framework | **pydantic-ai** | Structured agents with schema validation |
| LLM | **Gemini 3 Flash** | `google-gla:gemini-3-flash-preview`, fast inference |
| Streaming | **VercelAIAdapter** | Native integration with Vercel AI SDK |
| Testing | **pytest-asyncio** | Async test support with `asyncio_mode = "auto"` |
| Deployment | **Cloud Run** | Autoscaling, containerized |

**Streaming Pattern:**

```python
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from pydantic_ai import Agent
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

agent = Agent('google-gla:gemini-3-flash-preview')  # Model with thinking/reasoning enabled

app = FastAPI()

@app.post('/chat')
async def chat(request: Request) -> Response:
    return await VercelAIAdapter.dispatch_request(request, agent=agent)
```

### **7.3 Data Layer**

| Layer | Technology | Notes |
|-------|------------|-------|
| Database | **Neon** *(if needed)* | Serverless Postgres, branching |

Potential persistence needs:
* User preferences (Glass Box toggle state)
* Conversation history (for logged-in users)
* Analytics/telemetry aggregates

### **7.4 Infrastructure Decisions**

| Concern | Decision | Rationale |
|---------|----------|-----------|
| Frontend hosting | **Vercel** | Native Next.js support, edge functions |
| Backend hosting | **Cloud Run** | Python runtime, autoscaling, cold start optimization |
| Database | **Neon** | Serverless Postgres, pay-per-use, branching for dev |
| Auth | **Clerk** | Drop-in auth, good DX, deferred to Phase 2 |
| Codebase Oracle | **Sidecar** | Same Cloud Run service, simpler deployment |
| Secrets | **GCP Secret Manager** | Native Cloud Run integration, audit trail |
| Observability | **Cloud Logging** | Sufficient for MVP, upgrade path to OpenTelemetry if needed |

### **7.5 Cross-Origin Configuration**

The frontend (Vercel) and backend (Cloud Run) run on different domains, requiring CORS configuration.

**Cloud Run CORS Setup:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://*.vercel.app",  # Preview deployments
        "http://localhost:3000",  # Local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Environment-specific origins:**
* Production: `https://glassbox.yourdomain.com`
* Preview: `https://*.vercel.app`
* Local: `http://localhost:3000`

---

## **8. Phased Development & Deployment Plan**

This project is explicitly designed to **ship early and grow intentionally**.

---

### **Phase 1 — Deployable MVP (Required to Ship)**

**Goal:** Demonstrate end-to-end agentic transparency with one core interaction.

**Includes:**

* Glass Box toggle
* Agentic chat with streaming responses
* Brain Log (routing, validation, latency)
* Codebase Oracle (basic LSP integration)
* Production deployment (Vercel + Cloud Run)

**Tech Scope:**
* Next.js frontend on Vercel
* FastAPI + pydantic-ai backend on Cloud Run
* Gemini 3 Flash (`gemini-3-flash-preview`) for inference
* Codebase Oracle as sidecar in same Cloud Run service
* Secrets via GCP Secret Manager
* No auth required (defer Clerk to Phase 2)
* No database required (stateless)

**Outcome:**
A live, credible portfolio that already stands on its own.

> This phase alone is sufficient for hiring evaluation.

---

### **Phase 2 — Depth & Failure Narratives**

**Goal:** Demonstrate resilience and operational maturity.

**Adds:**

* Explicit failure simulations
* Retry and fallback visualization
* Human-in-the-loop mock escalation
* Expanded Oracle explanations
* Clerk auth for personalized experience
* Neon database for conversation persistence

**Outcome:**
Shows how the system behaves under stress and uncertainty.

---

### **Phase 3 — Advanced Transparency (Optional)**

**Goal:** Enhance insight for deeply technical reviewers.

**Adds:**

* Optional embedding-space visualization
* Advanced dependency graphs
* Selective load simulation

These features are **off by default** and clearly marked as exploratory.

---

## **9. Phase 1 Implementation Plan**

This section provides the detailed execution plan for shipping Phase 1.

---

### **9.1 Project Structure**

```
george-dekermenjian/
├── web/                         # Next.js 16 app
│   ├── app/
│   │   ├── layout.tsx          # Root layout with GlassBoxProvider
│   │   ├── page.tsx            # Landing / chat interface
│   │   └── profile/page.tsx    # Profile page
│   ├── components/
│   │   ├── ui/                 # shadcn components
│   │   ├── ai-elements/        # AI Elements library components
│   │   ├── chat/
│   │   │   └── ChatInterface.tsx
│   │   ├── glass-box/
│   │   │   ├── GlassBoxToggle.tsx
│   │   │   ├── GlassBoxProvider.tsx
│   │   │   ├── BrainLog.tsx
│   │   │   └── LogEntry.tsx
│   │   └── tool-results/       # Rich tool result renderers
│   ├── lib/
│   │   ├── api.ts              # Backend client + Brain Log types
│   │   └── utils.ts            # cn() helper
│   └── package.json
│
├── backend/                     # FastAPI app
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint with Brain Log streaming
│   │   ├── agent.py            # pydantic-ai agent with logged tools
│   │   ├── brain_log_stream.py # Brain Log streaming utilities
│   │   ├── config.py           # Pydantic Settings
│   │   ├── tools/
│   │   │   ├── experience.py   # Profile/experience tools
│   │   │   ├── codebase.py     # Codebase Oracle tools
│   │   │   ├── semantic.py     # LSP-powered semantic tools
│   │   │   ├── architecture.py # Module structure analysis
│   │   │   └── lsp_client.py   # Language Server Protocol client
│   │   └── schemas/
│   │       └── brain_log.py    # Brain Log entry schemas
│   ├── tests/                  # pytest-asyncio tests
│   ├── scripts/deploy.sh       # Cloud Run deployment
│   ├── Dockerfile
│   └── pyproject.toml
│
├── .github/workflows/ci.yml    # CI pipeline
├── vision.md                   # This document
└── CLAUDE.md                   # Claude Code instructions
```

---

### **9.2 Work Streams**

#### **Stream A: Project Scaffolding**

| Task | Description | Deliverable |
|------|-------------|-------------|
| A1 | Create monorepo structure | `frontend/` and `backend/` directories |
| A2 | Initialize Next.js 16.x with TypeScript | Working `npm run dev` |
| A3 | Configure Tailwind CSS | `tailwind.config.ts` |
| A4 | Install and configure shadcn/ui | Base components available |
| A5 | Initialize FastAPI project | Working `uvicorn` server |
| A6 | Configure pydantic-ai with Gemini | Agent responds to test prompt |
| A7 | Set up local development workflow | Both services run with hot reload |

**Exit Criteria:** `npm run dev` serves frontend, `uvicorn` serves backend, agent responds.

---

#### **Stream B: Backend — Agent Core**

| Task | Description | Deliverable |
|------|-------------|-------------|
| B1 | Define agent system prompt | `agent.py` with persona and boundaries |
| B2 | Implement `/chat` endpoint with VercelAIAdapter | Streaming responses work |
| B3 | Create `experience` tool | Returns structured professional info |
| B4 | Create `architecture` tool | Explains system design decisions |
| B5 | Add structured output validation | Pydantic models for all tool outputs |
| B6 | Implement Brain Log event emission | Each step emits structured log entry |
| B7 | Add CORS middleware | Frontend can call backend |

**Exit Criteria:** Agent responds with tools, Brain Log events captured.

**Agent System Prompt (Draft):**

```python
SYSTEM_PROMPT = """
You are an AI assistant embedded in George's portfolio website.
Your purpose is to answer questions about:
1. George's professional experience and background
2. The architecture and design decisions of this portfolio system
3. The codebase that powers this application

You have access to tools that provide grounded, accurate information.
Always use tools when available rather than relying on general knowledge.

When you don't know something, say so clearly.
When a question is outside your scope, explain your boundaries.
"""
```

---

#### **Stream C: Backend — Codebase Oracle**

| Task | Description | Deliverable |
|------|-------------|-------------|
| C1 | Set up code index at build time | Repository files accessible |
| C2 | Implement `find_symbol` tool | Locates function/class definitions |
| C3 | Implement `get_file_content` tool | Returns file with line numbers |
| C4 | Implement `find_references` tool | Shows where symbols are used |
| C5 | Add LSP-powered semantic tools | `go_to_definition`, `find_all_references`, `get_type_info`, `get_document_symbols`, `get_callers` |
| C6 | Add tool output to Brain Log | Oracle operations visible |

**Exit Criteria:** Agent can answer "How does the chat endpoint work?" with actual code references.

**Oracle Tool Definitions:**

```python
from pydantic_ai import Tool
from pydantic import BaseModel

class SymbolLocation(BaseModel):
    file: str
    line: int
    snippet: str

class FindSymbolResult(BaseModel):
    symbol: str
    locations: list[SymbolLocation]

@agent.tool
async def find_symbol(symbol_name: str) -> FindSymbolResult:
    """Find where a function, class, or variable is defined in the codebase."""
    # Implementation uses tree-sitter or simple regex
    ...

@agent.tool
async def get_file_content(file_path: str, start_line: int = 1, end_line: int | None = None) -> str:
    """Get the content of a file in the codebase."""
    ...
```

---

#### **Stream D: Frontend — Chat Interface**

| Task | Description | Deliverable |
|------|-------------|-------------|
| D1 | Create base layout with header | App shell renders |
| D2 | Implement `ChatInterface` component | Message list + input |
| D3 | Integrate Vercel AI SDK `useChat` | Streaming works end-to-end |
| D4 | Style message bubbles | User/assistant distinction clear |
| D5 | Add loading states | Typing indicator during stream |
| D6 | Handle errors gracefully | Error messages display in chat |
| D7 | Add keyboard shortcuts | Enter to send, Shift+Enter for newline |

**Exit Criteria:** Full chat conversation works with streaming responses.

**Chat Hook Integration:**

```typescript
'use client';

import { useChat } from 'ai/react';

export function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: process.env.NEXT_PUBLIC_BACKEND_URL + '/chat',
  });

  return (
    // ... UI implementation
  );
}
```

---

#### **Stream E: Frontend — Glass Box Mode**

| Task | Description | Deliverable |
|------|-------------|-------------|
| E1 | Create `GlassBoxToggle` component | Toggle in header |
| E2 | Add Glass Box context/state | Mode persists across navigation |
| E3 | Create `BrainLog` panel component | Slides in from right |
| E4 | Implement `LogEntry` component | Single log item rendering |
| E5 | Stream Brain Log events from backend | Real-time updates |
| E6 | Add log entry types | Input, Routing, Validation, Performance |
| E7 | Style log entries by type | Color-coded, icons |
| E8 | Add expand/collapse for log details | Progressive disclosure |

**Exit Criteria:** Toggle shows/hides Brain Log, logs stream in real-time.

**Brain Log Event Schema:**

```typescript
type LogEntryType = 'input' | 'routing' | 'tool_call' | 'validation' | 'performance';

interface BrainLogEntry {
  id: string;
  timestamp: number;
  type: LogEntryType;
  title: string;
  details: Record<string, unknown>;
  status: 'pending' | 'success' | 'failure';
  duration_ms?: number;
}

// Example entries:
// { type: 'input', title: 'User message received', details: { length: 42 } }
// { type: 'routing', title: 'Selected tool: experience', details: { reason: 'query about background' } }
// { type: 'validation', title: 'Output schema validated', details: { schema: 'ExperienceResult' }, status: 'success' }
// { type: 'performance', title: 'Request complete', details: { ttft_ms: 230, total_ms: 1450 } }
```

**Brain Log Streaming:**

The backend emits Brain Log events as Server-Sent Events (SSE) alongside the chat stream. Options:

1. **Inline in chat stream** — Custom event type in Vercel AI protocol
2. **Separate SSE endpoint** — `/chat/{conversation_id}/brain-log`
3. **WebSocket** — More complex, defer unless needed

Recommended: **Option 1** — Use Vercel AI SDK's data stream capabilities:

```python
# Backend: Include brain log in stream metadata
async def chat(request: Request) -> Response:
    return await VercelAIAdapter.dispatch_request(
        request,
        agent=agent,
        on_event=emit_brain_log_entry  # Custom callback
    )
```

```typescript
// Frontend: Access via useChat data
const { messages, data } = useChat({ api: '/chat' });
const brainLog = data as BrainLogEntry[];
```

---

#### **Stream F: Infrastructure & Deployment**

| Task | Description | Deliverable |
|------|-------------|-------------|
| F1 | Create Dockerfile for backend | Builds successfully |
| F2 | Configure GCP Secret Manager | API keys stored securely |
| F3 | Deploy backend to Cloud Run | Responds to health check |
| F4 | Configure Cloud Run environment | Secrets injected, scaling set |
| F5 | Deploy frontend to Vercel | Production URL live |
| F6 | Configure environment variables | Backend URL in frontend |
| F7 | Set up custom domain (optional) | `glassbox.yourdomain.com` |
| F8 | Verify CORS in production | Frontend → Backend works |

**Exit Criteria:** Both services deployed, chat works end-to-end in production.

**Cloud Run Configuration:**

```yaml
# cloud-run-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: glass-box-backend
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "3"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
        - image: gcr.io/PROJECT/glass-box-backend
          resources:
            limits:
              memory: 512Mi
              cpu: "1"
          env:
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: gemini-api-key
                  key: latest
```

**Deployment Commands:**

```bash
# Backend
gcloud builds submit --tag gcr.io/PROJECT/glass-box-backend ./backend
gcloud run deploy glass-box-backend \
  --image gcr.io/PROJECT/glass-box-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Frontend
cd frontend && vercel --prod
```

---

#### **Stream G: Polish & Testing**

| Task | Description | Deliverable |
|------|-------------|-------------|
| G1 | Add loading skeleton for chat | No layout shift |
| G2 | Implement error boundary | Graceful error handling |
| G3 | Add meta tags / OG image | Good social sharing |
| G4 | Test mobile responsiveness | Works on phone |
| G5 | Test cold start latency | Document actual numbers |
| G6 | Add basic analytics (optional) | Vercel Analytics or similar |
| G7 | Write README for repo | Setup instructions |

**Exit Criteria:** Production-ready, documented, presentable.

---

### **9.3 Implementation Order**

```
Week 1: Foundation
├── Stream A (Scaffolding) ──────────────────────────────────► Done
├── Stream B (Agent Core) ───────────────────────────────────► Done
└── Stream D (Chat Interface) ───────────────────────────────► Done
    └── Milestone: Basic chat works end-to-end

Week 2: Glass Box
├── Stream E (Glass Box Mode) ───────────────────────────────► Done
├── Stream C (Codebase Oracle) ──────────────────────────────► Done
    └── Milestone: Full Glass Box experience works locally

Week 3: Ship
├── Stream F (Infrastructure) ───────────────────────────────► Done
├── Stream G (Polish) ───────────────────────────────────────► Done
    └── Milestone: Production deployment live
```

---

### **9.4 Risk Mitigation**

| Risk | Mitigation |
|------|------------|
| Gemini API latency too high | Add loading states, measure TTFT, consider fallback model |
| Cold start affects UX | Set `minScale: 1` in Cloud Run if needed (increases cost) |
| Brain Log adds too much complexity | Ship chat-only first, add Brain Log incrementally |
| Codebase Oracle too slow | Cache parsed AST, limit search scope |
| CORS issues in production | Test early with staging deployment |

---

### **9.5 Definition of Done (Phase 1)**

Phase 1 is complete when:

- [x] User can have a multi-turn conversation with the agent
- [x] Agent uses tools to answer questions about experience and architecture
- [x] Glass Box toggle shows/hides Brain Log panel
- [x] Brain Log shows: input received, thinking, text, tool calls, tool results, timing
- [x] Codebase Oracle answers "How does X work?" with real code references
- [x] LSP-powered semantic tools for advanced code analysis
- [x] CI/CD pipeline configured (GitHub Actions)
- [x] Test suite with pytest-asyncio (backend) and vitest (frontend)
- [ ] Frontend deployed to Vercel with production URL
- [ ] Backend deployed to Cloud Run, autoscaling works
- [ ] Cold start latency documented
- [x] README explains how to run locally
- [x] A technical reviewer can understand the system in under 5 minutes

---

## **10. What This Portfolio Proves**

This project intentionally demonstrates that the author:

* Builds **production-grade agentic systems**
* Treats **explainability as a design constraint**
* Understands **real deployment trade-offs**
* Designs for **failure, not just success**
* Can communicate complex systems clearly

This is not a showcase of tools.

It is a showcase of **engineering judgment**.

---

## **11. Success Criteria**

The portfolio is successful if:

* A technical reviewer understands the system in under 5 minutes
* A non-technical reviewer is not overwhelmed
* Failures increase credibility rather than reduce it
* The system can be deployed, observed, and evolved incrementally

---

### **Final Note**

This portfolio is intentionally not maximal.

It is **focused, deployable, and honest**—because that is how real systems are built.

---

**Next Steps:**

* Design the **exact Brain Log UI mockups** (Figma or code)
* Create the **repository and scaffold** the project
* Begin **Stream A** implementation
