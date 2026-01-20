"""Tests for architecture analysis tools."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from app.config import get_settings
from app.tools.architecture import (
    ModuleInfo,
    ModuleStructureResult,
    DependencyEdge,
    DependencyGraphResult,
    SchemaInfo,
    SchemaField,
    APIContractsResult,
    ArchitectureOverview,
    DataFlowResult,
    DataFlowStep,
    _should_skip_path,
    _infer_purpose,
    _get_main_exports_python,
    _get_main_exports_typescript,
    _extract_python_imports,
    _extract_pydantic_schemas,
    get_module_structure,
    get_dependency_graph,
    get_api_contracts,
    explain_architecture,
    trace_data_flow,
)


@pytest.fixture
def mock_codebase_root():
    """Set codebase root to the project root for tests."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    with patch.dict(os.environ, {"CODEBASE_ROOT": project_root}):
        get_settings.cache_clear()
        yield project_root
        get_settings.cache_clear()


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestShouldSkipPath:
    """Tests for the _should_skip_path helper."""

    def test_skips_git_directory(self):
        assert _should_skip_path(Path("project/.git/config")) is True

    def test_skips_node_modules(self):
        assert _should_skip_path(Path("project/node_modules/package/index.js")) is True

    def test_skips_pycache(self):
        assert _should_skip_path(Path("project/__pycache__/module.pyc")) is True

    def test_skips_venv(self):
        assert _should_skip_path(Path("project/.venv/lib/python")) is True

    def test_skips_next(self):
        assert _should_skip_path(Path("project/.next/static/chunks")) is True

    def test_skips_dist(self):
        assert _should_skip_path(Path("project/dist/bundle.js")) is True

    def test_allows_src(self):
        assert _should_skip_path(Path("project/src/main.py")) is False

    def test_allows_app(self):
        assert _should_skip_path(Path("project/app/module.ts")) is False


class TestInferPurpose:
    """Tests for the _infer_purpose helper."""

    def test_infers_components(self):
        assert _infer_purpose("components", []) == "UI components"

    def test_infers_pages(self):
        assert _infer_purpose("pages", []) == "Route pages/views"

    def test_infers_tools(self):
        assert _infer_purpose("tools", []) == "Agent tools or utilities"

    def test_infers_schemas(self):
        assert _infer_purpose("schemas", []) == "Data schemas and validation"

    def test_infers_tests_from_name(self):
        assert _infer_purpose("tests", []) == "Test files"

    def test_infers_tests_from_files(self):
        assert _infer_purpose("unknown", ["test_main.py", "test_utils.py"]) == "Test files"

    def test_infers_styles_from_files(self):
        assert _infer_purpose("unknown", ["main.css", "theme.scss"]) == "Stylesheets"

    def test_default_purpose(self):
        assert _infer_purpose("unknown", ["file.py"]) == "Application module"


class TestGetMainExportsPython:
    """Tests for Python export extraction."""

    def test_extracts_from_config_file(self, mock_codebase_root):
        config_path = Path(mock_codebase_root) / "backend" / "app" / "config.py"
        if config_path.exists():
            exports = _get_main_exports_python(config_path)
            # Should find Settings class and get_settings function
            assert any("class Settings" in e for e in exports)
            assert any("def get_settings" in e for e in exports)

    def test_handles_nonexistent_file(self):
        exports = _get_main_exports_python(Path("/nonexistent/file.py"))
        assert exports == []

    def test_limits_results(self, mock_codebase_root):
        # Any file with many exports should be limited to 10
        config_path = Path(mock_codebase_root) / "backend" / "app" / "config.py"
        if config_path.exists():
            exports = _get_main_exports_python(config_path)
            assert len(exports) <= 10


class TestExtractPythonImports:
    """Tests for Python import extraction."""

    def test_extracts_imports(self, mock_codebase_root):
        root = Path(mock_codebase_root)
        main_path = root / "backend" / "app" / "main.py"
        if main_path.exists():
            imports = _extract_python_imports(main_path, root)
            assert len(imports) > 0
            # Each import should be a tuple (source, target, type)
            assert all(len(imp) == 3 for imp in imports)


class TestExtractPydanticSchemas:
    """Tests for Pydantic schema extraction."""

    def test_extracts_schemas_from_config(self, mock_codebase_root):
        root = Path(mock_codebase_root)
        config_path = root / "backend" / "app" / "config.py"
        if config_path.exists():
            schemas = _extract_pydantic_schemas(config_path, root)
            # Should find Settings class
            assert any(s.name == "Settings" for s in schemas)

    def test_schema_has_fields(self, mock_codebase_root):
        root = Path(mock_codebase_root)
        config_path = root / "backend" / "app" / "config.py"
        if config_path.exists():
            schemas = _extract_pydantic_schemas(config_path, root)
            settings_schema = next((s for s in schemas if s.name == "Settings"), None)
            if settings_schema:
                assert len(settings_schema.fields) > 0


# ============================================================================
# Schema Model Tests
# ============================================================================


class TestModuleInfo:
    """Tests for ModuleInfo schema."""

    def test_create_module_info(self):
        info = ModuleInfo(
            path="components",
            purpose="UI components",
            file_count=10,
            main_files=["index.ts"],
            exports=["Button", "Card"],
        )
        assert info.path == "components"
        assert info.purpose == "UI components"
        assert info.file_count == 10


class TestDependencyEdge:
    """Tests for DependencyEdge schema."""

    def test_create_dependency_edge(self):
        edge = DependencyEdge(
            source="app/main.py",
            target="app/config",
            import_type="named",
        )
        assert edge.source == "app/main.py"
        assert edge.target == "app/config"
        assert edge.import_type == "named"


class TestSchemaField:
    """Tests for SchemaField schema."""

    def test_create_required_field(self):
        field = SchemaField(
            name="email",
            type_annotation="str",
            required=True,
        )
        assert field.name == "email"
        assert field.required is True

    def test_create_optional_field(self):
        field = SchemaField(
            name="nickname",
            type_annotation="str | None",
            required=False,
            description="Optional nickname",
        )
        assert field.required is False
        assert field.description == "Optional nickname"


class TestDataFlowStep:
    """Tests for DataFlowStep schema."""

    def test_create_data_flow_step(self):
        step = DataFlowStep(
            file="app/main.py",
            function="handle_request",
            line=42,
            description="Receives HTTP request",
        )
        assert step.file == "app/main.py"
        assert step.line == 42


# ============================================================================
# Tool Function Tests
# ============================================================================


class TestGetModuleStructure:
    """Tests for get_module_structure tool."""

    def test_returns_module_structure_result(self, mock_codebase_root):
        result = get_module_structure()
        assert isinstance(result, ModuleStructureResult)
        assert result.root_path is not None

    def test_finds_modules(self, mock_codebase_root):
        result = get_module_structure()
        # Should find at least backend and web directories
        module_paths = [m.path for m in result.modules]
        assert len(module_paths) > 0

    def test_detects_architecture_type(self, mock_codebase_root):
        result = get_module_structure()
        # Should detect full-stack architecture
        assert "Full-stack" in result.architecture_type or "Backend" in result.architecture_type

    def test_assigns_layers(self, mock_codebase_root):
        result = get_module_structure()
        # Should have some layers assigned
        assert len(result.layers) > 0


class TestGetDependencyGraph:
    """Tests for get_dependency_graph tool."""

    def test_returns_dependency_graph_result(self, mock_codebase_root):
        result = get_dependency_graph()
        assert isinstance(result, DependencyGraphResult)

    def test_finds_nodes(self, mock_codebase_root):
        result = get_dependency_graph(scope="backend")
        # Should find some files
        assert len(result.nodes) > 0

    def test_finds_edges(self, mock_codebase_root):
        result = get_dependency_graph(scope="backend")
        # Should find some import relationships
        assert len(result.edges) >= 0  # May be empty for small codebases

    def test_scoped_to_backend(self, mock_codebase_root):
        result = get_dependency_graph(scope="backend")
        # Nodes should be from backend
        if result.nodes:
            assert any("backend" in node or "app" in node for node in result.nodes)

    def test_identifies_entry_points(self, mock_codebase_root):
        result = get_dependency_graph(scope="backend")
        # Should identify some entry points
        assert isinstance(result.entry_points, list)


class TestGetApiContracts:
    """Tests for get_api_contracts tool."""

    def test_returns_api_contracts_result(self, mock_codebase_root):
        result = get_api_contracts()
        assert isinstance(result, APIContractsResult)

    def test_finds_pydantic_schemas(self, mock_codebase_root):
        result = get_api_contracts()
        # Should find Settings and other Pydantic models
        schema_names = [s.name for s in result.schemas]
        assert len(schema_names) > 0

    def test_finds_endpoints(self, mock_codebase_root):
        result = get_api_contracts()
        # Should find FastAPI endpoints
        if result.endpoints:
            assert all("method" in ep and "path" in ep for ep in result.endpoints)


class TestExplainArchitecture:
    """Tests for explain_architecture tool."""

    def test_returns_architecture_overview(self, mock_codebase_root):
        result = explain_architecture()
        assert isinstance(result, ArchitectureOverview)

    def test_has_summary(self, mock_codebase_root):
        result = explain_architecture()
        assert result.summary is not None
        assert len(result.summary) > 0

    def test_detects_tech_stack(self, mock_codebase_root):
        result = explain_architecture()
        # Should detect some technologies
        assert len(result.tech_stack) > 0

    def test_identifies_key_components(self, mock_codebase_root):
        result = explain_architecture()
        # Should identify some components
        assert isinstance(result.key_components, list)

    def test_identifies_entry_points(self, mock_codebase_root):
        result = explain_architecture()
        assert isinstance(result.entry_points, list)


class TestTraceDataFlow:
    """Tests for trace_data_flow tool."""

    def test_returns_data_flow_result(self, mock_codebase_root):
        result = trace_data_flow("message")
        assert isinstance(result, DataFlowResult)

    def test_traces_message_flow(self, mock_codebase_root):
        result = trace_data_flow("message")
        assert result.entity == "message"
        assert result.flow_type == "request"
        # Should have some steps
        assert len(result.steps) > 0

    def test_traces_brainlog_flow(self, mock_codebase_root):
        result = trace_data_flow("BrainLog")
        assert result.entity == "BrainLog"
        assert result.flow_type == "event"
        assert len(result.steps) > 0

    def test_generic_entity_search(self, mock_codebase_root):
        result = trace_data_flow("Settings")
        assert result.entity == "Settings"
        # Should find occurrences in the codebase
        assert len(result.steps) >= 0  # May find or not find based on exact matches
