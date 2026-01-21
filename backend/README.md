# Glass Box Portfolio - Backend

FastAPI backend for the Glass Box Portfolio, featuring a pydantic-ai agent with tools for professional experience queries and codebase exploration.

## Tech Stack

- **Runtime**: Python 3.12+
- **Framework**: FastAPI
- **Agent Framework**: pydantic-ai with structured agents and schema validation
- **LLM**: Gemini 3 Flash (`google-gla:gemini-3-flash-preview`) with thinking/reasoning enabled
- **Package Manager**: uv
- **Testing**: pytest-asyncio (mode=auto)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI entrypoint with /chat and /profile endpoints
│   ├── agent.py              # pydantic-ai agent with 11 logged tools
│   ├── config.py             # Pydantic Settings configuration
│   ├── brain_log_stream.py   # Brain Log streaming utilities
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── experience.py     # Professional experience tools
│   │   ├── codebase.py       # Codebase Oracle tools
│   │   ├── semantic.py       # LSP-powered semantic analysis tools
│   │   ├── architecture.py   # Module structure analysis
│   │   └── lsp_client.py     # Language Server Protocol client
│   └── schemas/
│       ├── __init__.py
│       └── brain_log.py      # Brain Log entry schemas
├── tests/                    # pytest-asyncio tests
├── scripts/
│   └── deploy.sh             # Cloud Run deployment script
├── Dockerfile
├── cloud-run-service.yaml
├── pyproject.toml
└── README.md
```

## Setup

### Prerequisites

- Python 3.12+
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
| `/profile` | GET | Full profile data for profile page |
| `/chat` | POST | Streaming chat endpoint with Brain Log (Vercel AI SDK format) |
| `/docs` | GET | OpenAPI documentation |
| `/redoc` | GET | ReDoc documentation |

## Agent Tools

The portfolio agent has 11 tools, all wrapped with `logged_tool` decorator for Brain Log integration:

### Experience Tools

- `get_professional_experience()` - Returns work history and roles
- `get_skills()` - Returns categorized technical skills
- `get_projects()` - Returns notable project details

### Codebase Oracle Tools

- `clone_codebase()` - Clone/access the repository (call first for codebase questions)
- `get_folder_tree(path)` - See directory structure
- `get_file_content(file_path, start_line, end_line)` - Read file content

### Semantic (LSP-Powered) Tools

- `go_to_definition(file_path, symbol)` - Find where a symbol is defined
- `find_all_references(file_path, symbol)` - Find all usages of a symbol
- `get_type_info(file_path, symbol)` - Get type signatures and documentation
- `get_document_symbols(file_path)` - See structure of a file
- `get_callers(file_path, symbol)` - Find what calls a function

## Configuration

Configuration is managed via Pydantic Settings. Options can be set via environment variables or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google AI API key | (required) |
| `MODEL_NAME` | Model identifier | `google-gla:gemini-3-flash-preview` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "https://*.vercel.app"]` |
| `DEBUG` | Enable debug mode | `false` |
| `CODEBASE_ROOT` | Root directory for Codebase Oracle | Current working directory |
| `MAX_FILE_LINES` | Max lines to read from files | `500` |

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

### Using the Deploy Script

```bash
./scripts/deploy.sh --project YOUR_PROJECT_ID
```

### Manual Deployment

```bash
# Build Docker image
docker build -t glass-box-backend .

# Deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT/glass-box-backend
gcloud run deploy glass-box-backend \
  --image gcr.io/PROJECT/glass-box-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Prerequisites for Deployment

1. Enable Cloud Run and Secret Manager APIs
2. Create secret: `echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-`

## Brain Log Schemas

The backend includes structured schemas for Brain Log entries, enabling the Glass Box Mode frontend to visualize agent reasoning:

- `InputLogEntry` - User message received
- `ThinkingLogEntry` - Model reasoning/thinking (when enabled)
- `TextLogEntry` - Model text output
- `ToolCallLogEntry` - Tool invocation (pending state)
- `ToolResultLogEntry` - Tool completion with result preview or error
- `PerformanceLogEntry` - Timing metrics (total_ms, ttft_ms)

Brain Log entries are streamed as `data-brainlog` events in the Vercel AI Data Stream Protocol.

See `app/schemas/brain_log.py` for details.

## Testing

Tests use pytest-asyncio with `asyncio_mode = "auto"`:

```bash
uv run pytest              # Run all tests
uv run pytest -v           # Verbose output
uv run pytest --cov=app    # With coverage
```
