# Glass Box Portfolio

[![CI](https://github.com/ged1182/george-dekermenjian/actions/workflows/ci.yml/badge.svg)](https://github.com/ged1182/george-dekermenjian/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade demonstration of explainable, agentic AI systems. This portfolio showcases transparent AI decision-making through a unique "Glass Box" mode that reveals agent reasoning, tool selection, and execution in real-time.

## Why Glass Box?

Most AI systems are black boxes - they present polished outputs without exposing how decisions are made. The Glass Box Portfolio takes a different approach:

- **Transparency by Design**: See exactly how the AI agent reasons through problems
- **Production Realism**: Every visible behavior corresponds to something that exists in real production systems
- **Decision-Centric**: The system exposes *why* something happened, not just *what* happened

## Features

- **Glass Box Mode**: Toggle between polished UX and transparent engineering view
- **Brain Log**: Real-time visibility into agent reasoning, tool calls, and validation
- **Codebase Oracle**: Ask the AI questions about its own codebase
- **Streaming Responses**: Real-time streaming chat powered by Vercel AI SDK
- **Professional Experience Tools**: Structured access to work history, skills, and projects

## Demo

<!-- TODO: Add screenshots or demo GIF -->

*Coming soon: Live demo at [george-dekermenjian.vercel.app](https://george-dekermenjian.vercel.app)*

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, Tailwind CSS v4, Vercel AI SDK |
| **Backend** | FastAPI, pydantic-ai, Python 3.13+ |
| **LLM** | Google Gemini 2.0 Flash |
| **Deployment** | Vercel (frontend), Cloud Run (backend) |
| **Testing** | pytest (backend), Vitest (frontend) |

## Quick Start

### Prerequisites

- Node.js 20+ and pnpm
- Python 3.13+ and [uv](https://docs.astral.sh/uv/)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/ged1182/george-dekermenjian.git
cd george-dekermenjian
```

### 2. Start the Backend

```bash
cd backend
uv sync
export GEMINI_API_KEY=your_api_key_here
uv run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### 3. Start the Frontend

```bash
cd web
pnpm install
pnpm dev
```

The app will be available at http://localhost:3000

### Using Make (Recommended)

```bash
make install    # Install all dependencies
make dev        # Run both frontend and backend
make test       # Run all tests
make lint       # Run linters
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `CODEBASE_ROOT` | Path to codebase for Codebase Oracle | No | Current directory |
| `DEBUG` | Enable debug mode | No | `false` |

### Frontend (`web/.env.local`)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | No | `http://localhost:8000` |

## Architecture

```
                    +------------------+
                    |    Next.js UI    |
                    |  (Glass Box Mode)|
                    +--------+---------+
                             |
                    Vercel AI SDK (streaming)
                             |
                    +--------v---------+
                    |    FastAPI       |
                    |  /chat endpoint  |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   pydantic-ai    |
                    |     Agent        |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
+-------v-------+   +--------v-------+   +-------v-------+
| Experience    |   | Codebase       |   | Architecture  |
| Tools         |   | Oracle Tools   |   | Tools         |
+---------------+   +----------------+   +---------------+
```

### Agent Tools (Currently Registered)

The pydantic-ai agent uses 6 tools:

**Experience Tools** (`tools/experience.py`):
- `get_professional_experience()` - Returns work history and roles
- `get_skills()` - Returns categorized technical skills
- `get_projects()` - Returns notable project details

**Codebase Oracle Tools** (`tools/codebase.py`):
- `find_symbol(symbol_name)` - Find function/class definitions
- `get_file_content(file_path, start_line, end_line)` - Read file content
- `find_references(symbol_name)` - Find all usages of a symbol

### Additional Tool Modules (Available)

- `tools/architecture.py` - Module structure and dependency analysis
- `tools/semantic.py` - LSP-powered semantic code analysis
- `tools/lsp_client.py` - Language Server Protocol client

## Development

### Backend Quality Checks

```bash
cd backend
uv sync --dev
uv run ruff check app/        # Lint
uv run ruff format app/       # Format
uv run mypy app/              # Type check
uv run pytest                 # Run tests with coverage
```

### Frontend Quality Checks

```bash
cd web
pnpm lint                     # ESLint
pnpm typecheck                # TypeScript
pnpm test                     # Run Vitest tests
pnpm build                    # Production build
```

## Deployment

### Frontend (Vercel)

```bash
cd web
vercel --prod
```

### Backend (Cloud Run)

```bash
cd backend
./scripts/deploy.sh --project YOUR_PROJECT_ID
```

See [backend/README.md](backend/README.md) for detailed deployment instructions.

## Project Structure

```
george-dekermenjian/
├── .github/workflows/       # CI/CD configuration
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── tools/          # Agent tool implementations
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── agent.py        # pydantic-ai agent definition
│   │   ├── config.py       # Settings management
│   │   └── main.py         # FastAPI application
│   └── tests/              # pytest test suite
├── web/                     # Next.js frontend
│   ├── app/                # App Router pages
│   ├── components/
│   │   ├── ai-elements/    # Chat UI components
│   │   ├── chat/           # Chat interface
│   │   ├── glass-box/      # Glass Box mode components
│   │   ├── tool-results/   # Tool result renderers
│   │   └── ui/             # shadcn/ui components
│   └── lib/                # Utilities and API client
├── vision.md               # Product vision document
├── CONTRIBUTING.md         # Contribution guidelines
└── Makefile               # Development commands
```

## Contributing

This is a personal portfolio project, so we kindly do not accept pull requests. However, you're welcome to:

- **Fork the repository** and create your own version
- **Open issues** to report bugs or ask questions

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on creating your own version.

## Security

For security concerns, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**George Dekermenjian** - Staff Software Engineer specializing in AI/ML systems and production-grade agentic architectures.

---

Built with transparency in mind.
