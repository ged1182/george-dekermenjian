# Glass Box Portfolio - Backend

FastAPI backend for the Glass Box Portfolio, featuring a pydantic-ai agent with tools for professional experience queries and codebase exploration.

## Tech Stack

- **Runtime**: Python 3.14+
- **Framework**: FastAPI
- **Agent Framework**: pydantic-ai with structured agents and schema validation
- **LLM**: Gemini 2.0 Flash (via Google AI)
- **Package Manager**: uv

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI entrypoint with /chat endpoint
│   ├── agent.py            # pydantic-ai agent definition
│   ├── config.py           # Pydantic Settings configuration
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── experience.py   # Professional experience tools
│   │   └── codebase.py     # Codebase Oracle tools
│   └── schemas/
│       ├── __init__.py
│       └── brain_log.py    # Brain Log entry schemas
├── pyproject.toml
└── README.md
```

## Setup

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- Gemini API key

### Installation

1. Clone the repository and navigate to the backend directory:

```bash
cd backend
```

2. Install dependencies using uv:

```bash
uv sync
```

3. Create a `.env` file with your configuration:

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Or set environment variables directly:

```bash
export GEMINI_API_KEY=your_api_key_here
```

### Running the Server

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

Or using the configured script:

```bash
uv run start
```

The server will be available at `http://localhost:8000`.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check for Cloud Run |
| `/chat` | POST | Streaming chat endpoint (Vercel AI SDK format) |
| `/docs` | GET | OpenAPI documentation |
| `/redoc` | GET | ReDoc documentation |

## Agent Tools

The portfolio agent has access to the following tools:

### Experience Tools

- `get_professional_experience()` - Returns work history and roles
- `get_skills()` - Returns categorized technical skills
- `get_projects()` - Returns notable project details

### Codebase Oracle Tools

- `find_symbol(symbol_name)` - Find function/class definitions
- `get_file_content(file_path, start_line, end_line)` - Read file content
- `find_references(symbol_name)` - Find all usages of a symbol

## Configuration

Configuration is managed via Pydantic Settings. Options can be set via environment variables or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google AI API key | (required) |
| `MODEL_NAME` | Model identifier | `google-gla:gemini-2.0-flash` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |
| `DEBUG` | Enable debug mode | `false` |
| `CODEBASE_ROOT` | Root directory for Codebase Oracle | `/home/george-dekermenjian/git/george-dekermenjian` |

## Development

### Testing

```bash
uv run pytest
```

### Type Checking

```bash
uv run mypy app
```

## Deployment

The backend is designed to deploy on Google Cloud Run.

### Build Docker Image

```bash
docker build -t glass-box-backend .
```

### Deploy to Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT/glass-box-backend
gcloud run deploy glass-box-backend \
  --image gcr.io/PROJECT/glass-box-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Brain Log Schemas

The backend includes structured schemas for Brain Log entries, enabling the Glass Box Mode frontend to visualize agent reasoning:

- `InputLogEntry` - User message received
- `RoutingLogEntry` - Tool/path selection decisions
- `ToolCallLogEntry` - Tool execution details
- `ValidationLogEntry` - Schema validation results
- `PerformanceLogEntry` - Timing and token metrics

See `app/schemas/brain_log.py` for details.
