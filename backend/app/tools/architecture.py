"""Architecture analysis tools for understanding codebase structure.

These tools provide high-level insights into the codebase architecture,
including module structure, dependency relationships, data flow, and
API contracts.
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel, Field

from ..config import get_settings


class ModuleInfo(BaseModel):
    """Information about a module/directory in the codebase."""

    path: str = Field(description="Relative path to the module/directory")
    purpose: str = Field(description="Inferred purpose of this module")
    file_count: int = Field(description="Number of files in this module")
    main_files: list[str] = Field(description="Key files in this module")
    exports: list[str] = Field(description="Main exports from this module")


class ModuleStructureResult(BaseModel):
    """Result of module structure analysis."""

    root_path: str = Field(description="Root path analyzed")
    modules: list[ModuleInfo] = Field(description="Modules found in the codebase")
    architecture_type: str = Field(description="Detected architecture pattern")
    layers: dict[str, list[str]] = Field(
        description="Architectural layers and their modules"
    )


class DependencyEdge(BaseModel):
    """A dependency relationship between two files."""

    source: str = Field(description="File that imports")
    target: str = Field(description="File being imported")
    import_type: str = Field(description="Type of import (default, named, namespace)")


class DependencyGraphResult(BaseModel):
    """Result of dependency graph analysis."""

    nodes: list[str] = Field(description="All files in the graph")
    edges: list[DependencyEdge] = Field(description="Import relationships")
    entry_points: list[str] = Field(description="Files with no incoming edges")
    leaf_nodes: list[str] = Field(description="Files with no outgoing edges")
    circular_dependencies: list[list[str]] = Field(
        description="Detected circular dependencies"
    )


class DataFlowStep(BaseModel):
    """A step in a data flow path."""

    file: str = Field(description="File involved in this step")
    function: str = Field(description="Function/component involved")
    line: int = Field(description="Line number")
    description: str = Field(description="What happens at this step")


class DataFlowResult(BaseModel):
    """Result of data flow tracing."""

    entity: str = Field(description="Entity being traced")
    flow_type: str = Field(description="Type of flow (request, event, data)")
    steps: list[DataFlowStep] = Field(description="Steps in the flow")
    entry_point: str = Field(description="Where the flow starts")
    exit_point: str = Field(description="Where the flow ends")


class SchemaField(BaseModel):
    """A field in a schema/interface."""

    name: str
    type_annotation: str
    required: bool = True
    description: str | None = None


class SchemaInfo(BaseModel):
    """Information about a data schema."""

    name: str = Field(description="Schema/interface name")
    file: str = Field(description="File where defined")
    line: int = Field(description="Line number")
    fields: list[SchemaField] = Field(description="Fields in the schema")
    base_classes: list[str] = Field(description="Parent classes/interfaces")


class APIContractsResult(BaseModel):
    """Result of API contracts analysis."""

    schemas: list[SchemaInfo] = Field(description="All schemas/interfaces found")
    endpoints: list[dict] = Field(description="API endpoints if applicable")


class ArchitectureOverview(BaseModel):
    """High-level architecture overview."""

    summary: str = Field(description="Brief architecture summary")
    tech_stack: dict[str, list[str]] = Field(
        description="Technologies used by category"
    )
    architecture_pattern: str = Field(description="Main architectural pattern")
    key_components: list[dict] = Field(description="Key components and their roles")
    data_stores: list[str] = Field(description="Data storage mechanisms")
    external_integrations: list[str] = Field(description="External services/APIs")
    entry_points: list[dict] = Field(description="Application entry points")


# Purpose inference based on directory/file names
PURPOSE_PATTERNS = {
    "components": "UI components",
    "pages": "Route pages/views",
    "app": "Application entry and routing",
    "lib": "Utility libraries and helpers",
    "utils": "Utility functions",
    "hooks": "React hooks",
    "services": "Service layer / business logic",
    "api": "API routes or client",
    "tools": "Agent tools or utilities",
    "schemas": "Data schemas and validation",
    "models": "Data models",
    "controllers": "Request handlers",
    "middleware": "Request/response middleware",
    "config": "Configuration",
    "tests": "Test files",
    "__tests__": "Test files",
    "types": "Type definitions",
    "interfaces": "Interface definitions",
    "constants": "Constants and enums",
    "assets": "Static assets",
    "public": "Public static files",
    "styles": "Stylesheets",
}


def _should_skip_path(path: Path) -> bool:
    """Check if a path should be skipped during analysis."""
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".next",
        "dist",
        "build",
        ".uv",
        ".pytest_cache",
        "coverage",
    }
    parts = path.parts
    return any(skip_dir in parts for skip_dir in skip_dirs)


def _infer_purpose(dir_name: str, files: list[str]) -> str:
    """Infer the purpose of a directory from its name and contents."""
    name_lower = dir_name.lower()

    # Check direct matches
    if name_lower in PURPOSE_PATTERNS:
        return PURPOSE_PATTERNS[name_lower]

    # Check partial matches
    for pattern, purpose in PURPOSE_PATTERNS.items():
        if pattern in name_lower:
            return purpose

    # Infer from file contents
    if any("test" in f.lower() for f in files):
        return "Test files"
    if any(f.endswith(".css") or f.endswith(".scss") for f in files):
        return "Stylesheets"
    if any(f.endswith(".json") for f in files):
        return "Configuration or data files"

    return "Application module"


def _get_main_exports_python(file_path: Path) -> list[str]:
    """Extract main exports from a Python file."""
    exports = []
    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    exports.append(f"def {node.name}")
            elif isinstance(node, ast.AsyncFunctionDef):
                if not node.name.startswith("_"):
                    exports.append(f"async def {node.name}")
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    exports.append(f"class {node.name}")
    except Exception:
        pass

    return exports[:10]  # Limit to 10


def _get_main_exports_typescript(file_path: Path) -> list[str]:
    """Extract main exports from a TypeScript/JavaScript file."""
    exports = []
    try:
        content = file_path.read_text()

        # Export patterns
        patterns = [
            r"export\s+(?:default\s+)?(?:async\s+)?function\s+(\w+)",
            r"export\s+(?:default\s+)?class\s+(\w+)",
            r"export\s+(?:const|let|var)\s+(\w+)",
            r"export\s+(?:default\s+)?interface\s+(\w+)",
            r"export\s+type\s+(\w+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            exports.extend(matches)

    except Exception:
        pass

    return list(set(exports))[:10]


def _extract_python_imports(file_path: Path, root: Path) -> list[tuple[str, str, str]]:
    """Extract imports from a Python file.

    Returns list of (source_file, target_module, import_type)
    """
    imports = []
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        relative_path = str(file_path.relative_to(root))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((relative_path, alias.name, "namespace"))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_type = "named" if node.names else "namespace"
                    imports.append((relative_path, node.module, import_type))
    except Exception:
        pass

    return imports


def _extract_typescript_imports(
    file_path: Path, root: Path
) -> list[tuple[str, str, str]]:
    """Extract imports from a TypeScript/JavaScript file.

    Returns list of (source_file, target_path, import_type)
    """
    imports = []
    try:
        content = file_path.read_text()
        relative_path = str(file_path.relative_to(root))

        # Various import patterns
        patterns = [
            # import X from "path"
            (r'import\s+(\w+)\s+from\s+["\']([^"\']+)["\']', "default"),
            # import { X } from "path"
            (r'import\s+\{[^}]+\}\s+from\s+["\']([^"\']+)["\']', "named"),
            # import * as X from "path"
            (r'import\s+\*\s+as\s+\w+\s+from\s+["\']([^"\']+)["\']', "namespace"),
            # import "path"
            (r'import\s+["\']([^"\']+)["\']', "side-effect"),
        ]

        for pattern, import_type in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                target = match if isinstance(match, str) else match[-1]
                imports.append((relative_path, target, import_type))

    except Exception:
        pass

    return imports


def _extract_pydantic_schemas(file_path: Path, root: Path) -> list[SchemaInfo]:
    """Extract Pydantic model schemas from a Python file."""
    schemas = []
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        relative_path = str(file_path.relative_to(root))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from BaseModel or similar
                base_names = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_names.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_names.append(base.attr)

                if any(b in ["BaseModel", "BaseSettings"] for b in base_names):
                    fields = []
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(
                            item.target, ast.Name
                        ):
                            field_name = item.target.id
                            type_str = (
                                ast.unparse(item.annotation)
                                if item.annotation
                                else "Any"
                            )
                            fields.append(
                                SchemaField(
                                    name=field_name,
                                    type_annotation=type_str,
                                    required=item.value is None,
                                )
                            )

                    schemas.append(
                        SchemaInfo(
                            name=node.name,
                            file=relative_path,
                            line=node.lineno,
                            fields=fields,
                            base_classes=base_names,
                        )
                    )
    except Exception:
        pass

    return schemas


def _extract_typescript_interfaces(file_path: Path, root: Path) -> list[SchemaInfo]:
    """Extract TypeScript interfaces from a file."""
    schemas = []
    try:
        content = file_path.read_text()
        relative_path = str(file_path.relative_to(root))

        # Match interface definitions
        interface_pattern = (
            r"(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+([^{]+))?\s*\{([^}]+)\}"
        )

        for match in re.finditer(interface_pattern, content, re.MULTILINE | re.DOTALL):
            name = match.group(1)
            extends = match.group(2)
            body = match.group(3)

            base_classes = []
            if extends:
                base_classes = [b.strip() for b in extends.split(",")]

            fields = []
            # Simple field pattern
            field_pattern = r"(\w+)\??:\s*([^;]+)"
            for field_match in re.finditer(field_pattern, body):
                field_name = field_match.group(1)
                field_type = field_match.group(2).strip()
                required = "?" not in field_match.group(0).split(":")[0]
                fields.append(
                    SchemaField(
                        name=field_name,
                        type_annotation=field_type,
                        required=required,
                    )
                )

            line_num = content[: match.start()].count("\n") + 1
            schemas.append(
                SchemaInfo(
                    name=name,
                    file=relative_path,
                    line=line_num,
                    fields=fields,
                    base_classes=base_classes,
                )
            )

    except Exception:
        pass

    return schemas


def get_module_structure() -> ModuleStructureResult:
    """Analyze the high-level module structure of the codebase.

    USE THIS TOOL when the user asks about:
    - "What's the overall structure?"
    - "How is the codebase organized?"
    - "What are the main modules?"
    - "Explain the architecture"

    Returns:
        ModuleStructureResult with module information and architecture pattern.
    """
    print("[TOOL] get_module_structure called")
    settings = get_settings()
    root = Path(settings.codebase_root)

    modules = []
    layers: dict[str, list[str]] = defaultdict(list)

    # Scan top-level directories
    for item in sorted(root.iterdir()):
        if not item.is_dir():
            continue
        if _should_skip_path(item):
            continue

        dir_name = item.name
        files = []
        main_files = []
        exports = []

        # Scan files in this directory
        for file_path in item.rglob("*"):
            if not file_path.is_file():
                continue
            if _should_skip_path(file_path):
                continue

            rel_path = str(file_path.relative_to(item))
            files.append(rel_path)

            # Identify main files
            if file_path.name in [
                "index.ts",
                "index.tsx",
                "index.js",
                "__init__.py",
                "main.py",
            ]:
                main_files.append(rel_path)

            # Get exports
            if file_path.suffix == ".py":
                exports.extend(_get_main_exports_python(file_path))
            elif file_path.suffix in [".ts", ".tsx", ".js", ".jsx"]:
                exports.extend(_get_main_exports_typescript(file_path))

        purpose = _infer_purpose(dir_name, files)
        modules.append(
            ModuleInfo(
                path=dir_name,
                purpose=purpose,
                file_count=len(files),
                main_files=main_files[:5],
                exports=exports[:10],
            )
        )

        # Assign to layers
        if "api" in dir_name.lower() or "routes" in dir_name.lower():
            layers["API Layer"].append(dir_name)
        elif "service" in dir_name.lower() or "business" in dir_name.lower():
            layers["Service Layer"].append(dir_name)
        elif "component" in dir_name.lower() or "ui" in dir_name.lower():
            layers["Presentation Layer"].append(dir_name)
        elif "model" in dir_name.lower() or "schema" in dir_name.lower():
            layers["Data Layer"].append(dir_name)
        elif "tool" in dir_name.lower():
            layers["Tools Layer"].append(dir_name)
        else:
            layers["Core"].append(dir_name)

    # Detect architecture pattern
    has_frontend = any(
        "web" in m.path.lower() or "app" in m.path.lower() for m in modules
    )
    has_backend = any(
        "backend" in m.path.lower() or "api" in m.path.lower() for m in modules
    )

    if has_frontend and has_backend:
        arch_type = "Full-stack monorepo (Frontend + Backend)"
    elif has_backend:
        arch_type = "Backend service"
    elif has_frontend:
        arch_type = "Frontend application"
    else:
        arch_type = "Library/Package"

    return ModuleStructureResult(
        root_path=str(root),
        modules=modules,
        architecture_type=arch_type,
        layers=dict(layers),
    )


def get_dependency_graph(scope: str = "all") -> DependencyGraphResult:
    """Build a dependency graph showing import relationships.

    USE THIS TOOL when the user asks about:
    - "What depends on X?"
    - "Show me the import graph"
    - "Are there circular dependencies?"
    - "What files are entry points?"

    Args:
        scope: Scope of analysis - "all", "backend", "frontend", or a specific path

    Returns:
        DependencyGraphResult with nodes, edges, and analysis.
    """
    print(f"[TOOL] get_dependency_graph called with scope: {scope}")
    settings = get_settings()
    root = Path(settings.codebase_root)

    # Determine scope
    if scope == "backend":
        search_root = root / "backend"
    elif scope == "frontend" or scope == "web":
        search_root = root / "web"
    elif scope == "all":
        search_root = root
    else:
        search_root = root / scope

    if not search_root.exists():
        search_root = root

    nodes: set[str] = set()
    edges: list[DependencyEdge] = []
    imports_map: dict[str, list[str]] = defaultdict(list)

    # Collect all imports
    for file_path in search_root.rglob("*"):
        if not file_path.is_file():
            continue
        if _should_skip_path(file_path):
            continue

        if file_path.suffix == ".py":
            imports = _extract_python_imports(file_path, root)
        elif file_path.suffix in [".ts", ".tsx", ".js", ".jsx"]:
            imports = _extract_typescript_imports(file_path, root)
        else:
            continue

        rel_path = str(file_path.relative_to(root))
        nodes.add(rel_path)

        for source, target, import_type in imports:
            edges.append(
                DependencyEdge(source=source, target=target, import_type=import_type)
            )
            imports_map[source].append(target)

    # Find entry points (no incoming edges)
    targets = {e.target for e in edges}
    entry_points = [n for n in nodes if n not in targets]

    # Find leaf nodes (no outgoing edges)
    sources = {e.source for e in edges}
    leaf_nodes = [n for n in nodes if n not in sources]

    # Detect circular dependencies (simple version)
    circular: list[list[str]] = []
    for node in nodes:
        visited: set[str] = set()
        path: list[str] = []

        def dfs(current: str) -> bool:
            if current in path:
                cycle_start = path.index(current)
                circular.append(path[cycle_start:] + [current])
                return True
            if current in visited:
                return False

            visited.add(current)
            path.append(current)

            for target in imports_map.get(current, []):
                if dfs(target):
                    return True

            path.pop()
            return False

        dfs(node)

    return DependencyGraphResult(
        nodes=sorted(nodes),
        edges=edges[:200],  # Limit edges
        entry_points=entry_points[:20],
        leaf_nodes=leaf_nodes[:20],
        circular_dependencies=circular[:10],
    )


def get_api_contracts() -> APIContractsResult:
    """Extract all data schemas, interfaces, and API contracts.

    USE THIS TOOL when the user asks about:
    - "What data structures are used?"
    - "What's the schema for X?"
    - "What are the API contracts?"
    - "Show me the type definitions"

    Returns:
        APIContractsResult with all schemas and endpoints.
    """
    print("[TOOL] get_api_contracts called")
    settings = get_settings()
    root = Path(settings.codebase_root)

    schemas: list[SchemaInfo] = []
    endpoints: list[dict] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if _should_skip_path(file_path):
            continue

        if file_path.suffix == ".py":
            schemas.extend(_extract_pydantic_schemas(file_path, root))

            # Extract FastAPI endpoints
            try:
                content = file_path.read_text()
                endpoint_pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
                for match in re.finditer(endpoint_pattern, content):
                    method = match.group(1).upper()
                    path = match.group(2)
                    line_num = content[: match.start()].count("\n") + 1
                    endpoints.append(
                        {
                            "method": method,
                            "path": path,
                            "file": str(file_path.relative_to(root)),
                            "line": line_num,
                        }
                    )
            except Exception:
                pass

        elif file_path.suffix in [".ts", ".tsx"]:
            schemas.extend(_extract_typescript_interfaces(file_path, root))

    return APIContractsResult(
        schemas=schemas[:50],
        endpoints=endpoints[:30],
    )


def explain_architecture() -> ArchitectureOverview:
    """Generate a high-level architecture overview of the entire codebase.

    USE THIS TOOL when the user asks:
    - "Explain the overall architecture"
    - "Give me a system overview"
    - "What technologies are used?"
    - "How does everything fit together?"

    This tool provides a comprehensive summary suitable for onboarding.

    Returns:
        ArchitectureOverview with summary, tech stack, and key components.
    """
    print("[TOOL] explain_architecture called")
    settings = get_settings()
    root = Path(settings.codebase_root)

    # Detect tech stack
    tech_stack: dict[str, list[str]] = {
        "frontend": [],
        "backend": [],
        "database": [],
        "deployment": [],
        "testing": [],
    }

    # Check package.json
    package_json = root / "web" / "package.json"
    if not package_json.exists():
        package_json = root / "package.json"

    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            if "next" in deps:
                tech_stack["frontend"].append("Next.js")
            if "react" in deps:
                tech_stack["frontend"].append("React")
            if "tailwindcss" in deps or "@tailwindcss/vite" in deps:
                tech_stack["frontend"].append("Tailwind CSS")
            if "typescript" in deps:
                tech_stack["frontend"].append("TypeScript")
            if "ai" in deps or "@ai-sdk/react" in deps:
                tech_stack["frontend"].append("Vercel AI SDK")
            if "vitest" in deps or "jest" in deps:
                tech_stack["testing"].append("Vitest" if "vitest" in deps else "Jest")
        except Exception:
            pass

    # Check pyproject.toml
    pyproject = root / "backend" / "pyproject.toml"
    if not pyproject.exists():
        pyproject = root / "pyproject.toml"

    if pyproject.exists():
        try:
            content = pyproject.read_text()
            if "fastapi" in content.lower():
                tech_stack["backend"].append("FastAPI")
            if "pydantic" in content.lower():
                tech_stack["backend"].append("Pydantic")
            if "pydantic-ai" in content.lower():
                tech_stack["backend"].append("pydantic-ai")
            if "uvicorn" in content.lower():
                tech_stack["backend"].append("Uvicorn")
            if "pytest" in content.lower():
                tech_stack["testing"].append("pytest")
        except Exception:
            pass

    # Check for Docker
    if (root / "Dockerfile").exists() or (root / "backend" / "Dockerfile").exists():
        tech_stack["deployment"].append("Docker")

    # Check for cloud configs
    if (root / "vercel.json").exists():
        tech_stack["deployment"].append("Vercel")
    if any(root.rglob("*cloud-run*.yaml")):
        tech_stack["deployment"].append("Google Cloud Run")

    # Identify key components
    key_components = []

    # Check for agent
    agent_file = root / "backend" / "app" / "agent.py"
    if agent_file.exists():
        key_components.append(
            {
                "name": "AI Agent",
                "file": "backend/app/agent.py",
                "role": "pydantic-ai agent with registered tools for handling queries",
            }
        )

    # Check for main API
    main_file = root / "backend" / "app" / "main.py"
    if main_file.exists():
        key_components.append(
            {
                "name": "API Server",
                "file": "backend/app/main.py",
                "role": "FastAPI application with streaming chat endpoint",
            }
        )

    # Check for frontend components
    chat_interface = root / "web" / "components" / "chat" / "ChatInterface.tsx"
    if chat_interface.exists():
        key_components.append(
            {
                "name": "Chat Interface",
                "file": "web/components/chat/ChatInterface.tsx",
                "role": "React component for agentic chat using Vercel AI SDK",
            }
        )

    glass_box = root / "web" / "components" / "glass-box"
    if glass_box.exists():
        key_components.append(
            {
                "name": "Glass Box System",
                "file": "web/components/glass-box/",
                "role": "Transparency layer showing agent reasoning and tool calls",
            }
        )

    # Identify entry points
    entry_points = []

    if (root / "web" / "app" / "page.tsx").exists():
        entry_points.append(
            {
                "type": "frontend",
                "file": "web/app/page.tsx",
                "description": "Next.js app router main page",
            }
        )

    if main_file.exists():
        entry_points.append(
            {
                "type": "backend",
                "file": "backend/app/main.py",
                "description": "FastAPI application entry point",
            }
        )

    # Determine architecture pattern
    has_agent = agent_file.exists()
    has_glass_box = glass_box.exists()

    if has_agent and has_glass_box:
        arch_pattern = "Explainable Agentic System (Glass Box Architecture)"
    elif has_agent:
        arch_pattern = "Agentic Application (AI-powered backend)"
    else:
        arch_pattern = "Full-stack Web Application"

    # Generate summary
    frontend_tech = ", ".join(tech_stack["frontend"]) or "Unknown"
    backend_tech = ", ".join(tech_stack["backend"]) or "Unknown"

    summary = f"""This is a {arch_pattern}.

**Frontend**: Built with {frontend_tech}. Provides a chat interface with optional "Glass Box" mode for transparency into agent reasoning.

**Backend**: Built with {backend_tech}. Implements an AI agent with tools for answering questions about professional experience and codebase analysis.

**Key Innovation**: The Glass Box system shows real-time brain logs including input processing, tool selection, validation, and performance metrics - making the AI's decision-making transparent."""

    return ArchitectureOverview(
        summary=summary,
        tech_stack={k: v for k, v in tech_stack.items() if v},
        architecture_pattern=arch_pattern,
        key_components=key_components,
        data_stores=["In-memory (agent tools contain static data)"],
        external_integrations=["Google Gemini API (LLM)", "Vercel AI SDK (streaming)"],
        entry_points=entry_points,
    )


def trace_data_flow(entity_name: str) -> DataFlowResult:
    """Trace how a piece of data flows through the system.

    USE THIS TOOL when the user asks:
    - "How does X flow through the system?"
    - "What happens when Y is processed?"
    - "Trace the path of Z"

    Args:
        entity_name: Name of the data entity to trace (e.g., "message", "BrainLogEntry")

    Returns:
        DataFlowResult with the traced path through the system.
    """
    print(f"[TOOL] trace_data_flow called with: {entity_name}")
    settings = get_settings()
    root = Path(settings.codebase_root)

    steps: list[DataFlowStep] = []

    # Search for the entity across the codebase
    entity_lower = entity_name.lower()

    # Common flow patterns based on entity type
    if "message" in entity_lower or "chat" in entity_lower:
        # Chat message flow
        steps = [
            DataFlowStep(
                file="web/components/chat/ChatInterface.tsx",
                function="handleSubmit",
                line=0,
                description="User submits message through chat input",
            ),
            DataFlowStep(
                file="web/components/chat/ChatInterface.tsx",
                function="useChat",
                line=0,
                description="Vercel AI SDK sends message to backend API",
            ),
            DataFlowStep(
                file="backend/app/main.py",
                function="chat_endpoint",
                line=0,
                description="FastAPI receives POST /chat request",
            ),
            DataFlowStep(
                file="backend/app/brain_log_stream.py",
                function="BrainLogAdapter",
                line=0,
                description="Adapter wraps agent for streaming with brain logs",
            ),
            DataFlowStep(
                file="backend/app/agent.py",
                function="portfolio_agent.run",
                line=0,
                description="pydantic-ai agent processes message and selects tools",
            ),
            DataFlowStep(
                file="backend/app/tools/",
                function="tool functions",
                line=0,
                description="Agent executes selected tools to gather information",
            ),
            DataFlowStep(
                file="backend/app/brain_log_stream.py",
                function="BrainLogEventStream",
                line=0,
                description="Stream events including brain logs back to client",
            ),
            DataFlowStep(
                file="web/components/chat/ChatInterface.tsx",
                function="useChat.onDataChunk",
                line=0,
                description="Frontend receives and displays streaming response",
            ),
        ]
        flow_type = "request"
        entry_point = "User chat input"
        exit_point = "Rendered response in chat"

    elif "brainlog" in entity_lower or "log" in entity_lower:
        # Brain log flow
        steps = [
            DataFlowStep(
                file="backend/app/schemas/brain_log.py",
                function="BrainLogCollector",
                line=0,
                description="Collector initialized at request start",
            ),
            DataFlowStep(
                file="backend/app/brain_log_stream.py",
                function="before_stream",
                line=0,
                description="Input log entry emitted",
            ),
            DataFlowStep(
                file="backend/app/brain_log_stream.py",
                function="handle_tool_call_start",
                line=0,
                description="Tool selection logged",
            ),
            DataFlowStep(
                file="backend/app/brain_log_stream.py",
                function="handle_tool_call_end",
                line=0,
                description="Tool result logged",
            ),
            DataFlowStep(
                file="backend/app/brain_log_stream.py",
                function="after_stream",
                line=0,
                description="Performance metrics logged",
            ),
            DataFlowStep(
                file="web/lib/api.ts",
                function="parseBrainLogChunk",
                line=0,
                description="Frontend parses brain log from stream",
            ),
            DataFlowStep(
                file="web/components/glass-box/BrainLog.tsx",
                function="BrainLog",
                line=0,
                description="Brain log entries rendered in Glass Box panel",
            ),
        ]
        flow_type = "event"
        entry_point = "Agent processing start"
        exit_point = "Brain Log panel display"

    else:
        # Generic search for the entity
        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if _should_skip_path(file_path):
                continue
            if file_path.suffix not in [".py", ".ts", ".tsx", ".js", ".jsx"]:
                continue

            try:
                content = file_path.read_text()
                if entity_name in content:
                    rel_path = str(file_path.relative_to(root))
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if entity_name in line:
                            steps.append(
                                DataFlowStep(
                                    file=rel_path,
                                    function="(see context)",
                                    line=i + 1,
                                    description=line.strip()[:100],
                                )
                            )
                            if len(steps) >= 10:
                                break
            except Exception:
                continue

            if len(steps) >= 10:
                break

        flow_type = "data"
        entry_point = "Unknown"
        exit_point = "Unknown"

    return DataFlowResult(
        entity=entity_name,
        flow_type=flow_type,
        steps=steps,
        entry_point=entry_point,
        exit_point=exit_point,
    )
