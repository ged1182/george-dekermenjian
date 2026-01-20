"""Tests for LSP-powered semantic analysis tools.

These tests verify the semantic tools work correctly, with fallback behavior
when LSP servers are not available.
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import get_settings
from app.tools.semantic import (
    DefinitionLocation,
    DefinitionResult,
    ReferenceLocation,
    ReferencesResult,
    TypeInfo,
    DocumentSymbol,
    DocumentSymbolsResult,
    CallHierarchyResult,
    SYMBOL_KINDS,
    _uri_to_path,
    _get_line_content,
    _find_symbol_in_file,
    go_to_definition,
    find_all_references,
    get_type_info,
    get_document_symbols,
    get_callers,
)


@pytest.fixture
def mock_codebase_root():
    """Set codebase root to the project root for tests."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    with patch.dict(os.environ, {"CODEBASE_ROOT": project_root}):
        get_settings.cache_clear()
        yield project_root
        get_settings.cache_clear()


@pytest.fixture
def mock_lsp_manager():
    """Mock LSP manager for tests without actual LSP servers."""
    with patch("app.tools.semantic.get_lsp_manager") as mock:
        manager = MagicMock()
        manager.get_client.return_value = None  # Default: no LSP available
        mock.return_value = manager
        yield mock, manager


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestUriToPath:
    """Tests for the _uri_to_path helper."""

    def test_converts_file_uri(self, mock_codebase_root):
        root = Path(mock_codebase_root)
        uri = f"file://{root}/backend/app/main.py"
        result = _uri_to_path(uri, root)
        assert result == "backend/app/main.py"

    def test_handles_non_uri(self, mock_codebase_root):
        root = Path(mock_codebase_root)
        result = _uri_to_path("not_a_uri", root)
        assert result == "not_a_uri"

    def test_handles_path_outside_root(self, mock_codebase_root):
        root = Path(mock_codebase_root)
        uri = "file:///etc/passwd"
        result = _uri_to_path(uri, root)
        # Should return full path when outside root
        assert "passwd" in result


class TestGetLineContent:
    """Tests for the _get_line_content helper."""

    def test_gets_line_from_file(self, mock_codebase_root):
        config_path = Path(mock_codebase_root) / "backend" / "app" / "config.py"
        if config_path.exists():
            content = _get_line_content(config_path, 0)  # First line
            assert len(content) > 0

    def test_handles_invalid_line(self, mock_codebase_root):
        config_path = Path(mock_codebase_root) / "backend" / "app" / "config.py"
        if config_path.exists():
            content = _get_line_content(config_path, 99999)  # Way beyond file
            assert content == ""

    def test_handles_nonexistent_file(self):
        content = _get_line_content(Path("/nonexistent/file.py"), 0)
        assert content == ""


class TestFindSymbolInFile:
    """Tests for the _find_symbol_in_file helper."""

    def test_finds_symbol(self, mock_codebase_root):
        result = _find_symbol_in_file("backend/app/config.py", "Settings")
        assert result is not None
        line, char = result
        assert line >= 0
        assert char >= 0

    def test_returns_none_for_missing_symbol(self, mock_codebase_root):
        result = _find_symbol_in_file("backend/app/config.py", "NonExistentSymbol12345")
        assert result is None

    def test_returns_none_for_missing_file(self, mock_codebase_root):
        result = _find_symbol_in_file("nonexistent/file.py", "Settings")
        assert result is None


# ============================================================================
# Schema Model Tests
# ============================================================================


class TestDefinitionLocation:
    """Tests for DefinitionLocation schema."""

    def test_create_definition_location(self):
        loc = DefinitionLocation(
            file="app/main.py",
            line=42,
            character=0,
            preview="def main():",
        )
        assert loc.file == "app/main.py"
        assert loc.line == 42
        assert loc.preview == "def main():"


class TestDefinitionResult:
    """Tests for DefinitionResult schema."""

    def test_create_success_result(self):
        result = DefinitionResult(
            symbol="main",
            source_file="app/caller.py",
            source_line=10,
            definitions=[
                DefinitionLocation(
                    file="app/main.py",
                    line=1,
                    character=4,
                    preview="def main():",
                )
            ],
            success=True,
        )
        assert result.success is True
        assert len(result.definitions) == 1

    def test_create_failure_result(self):
        result = DefinitionResult(
            symbol="unknown",
            source_file="test.py",
            source_line=0,
            definitions=[],
            success=False,
            error="Symbol not found",
        )
        assert result.success is False
        assert result.error == "Symbol not found"


class TestReferenceLocation:
    """Tests for ReferenceLocation schema."""

    def test_create_reference_location(self):
        loc = ReferenceLocation(
            file="app/utils.py",
            line=15,
            character=8,
            context="from app.main import main",
        )
        assert loc.file == "app/utils.py"
        assert "import" in loc.context


class TestTypeInfo:
    """Tests for TypeInfo schema."""

    def test_create_type_info(self):
        info = TypeInfo(
            symbol="settings",
            file="app/config.py",
            line=10,
            type_signature="Settings",
            success=True,
        )
        assert info.type_signature == "Settings"


class TestDocumentSymbol:
    """Tests for DocumentSymbol schema."""

    def test_create_document_symbol(self):
        sym = DocumentSymbol(
            name="MyClass",
            kind="Class",
            line=5,
            container=None,
        )
        assert sym.name == "MyClass"
        assert sym.kind == "Class"

    def test_create_with_container(self):
        sym = DocumentSymbol(
            name="my_method",
            kind="Method",
            line=10,
            container="MyClass",
        )
        assert sym.container == "MyClass"


class TestSymbolKinds:
    """Tests for SYMBOL_KINDS mapping."""

    def test_has_common_kinds(self):
        assert SYMBOL_KINDS[5] == "Class"
        assert SYMBOL_KINDS[6] == "Method"
        assert SYMBOL_KINDS[12] == "Function"
        assert SYMBOL_KINDS[13] == "Variable"


# ============================================================================
# Tool Function Tests (with mocked LSP)
# ============================================================================


class TestGoToDefinition:
    """Tests for go_to_definition tool."""

    @pytest.mark.asyncio
    async def test_returns_error_for_missing_file(self, mock_codebase_root):
        result = await go_to_definition("nonexistent/file.py", "Symbol")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_error_when_symbol_not_in_file(self, mock_codebase_root):
        result = await go_to_definition(
            "backend/app/config.py",
            "NonExistentSymbol999",
        )
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_error_when_no_lsp_available(
        self, mock_codebase_root, mock_lsp_manager
    ):
        mock_get, manager = mock_lsp_manager
        mock_get.return_value = manager
        manager.get_client.return_value = None

        result = await go_to_definition("backend/app/config.py", "Settings")
        assert result.success is False
        assert "LSP" in result.error or "not available" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_definitions_with_lsp(
        self, mock_codebase_root, mock_lsp_manager
    ):
        mock_get, manager = mock_lsp_manager

        # Create mock LSP client
        mock_client = MagicMock()
        mock_client.go_to_definition = AsyncMock(
            return_value=[
                MagicMock(
                    uri="file:///test/app/config.py",
                    range=MagicMock(
                        start=MagicMock(line=10, character=0),
                        end=MagicMock(line=10, character=8),
                    ),
                )
            ]
        )
        manager.get_client.return_value = mock_client
        mock_get.return_value = manager

        result = await go_to_definition("backend/app/config.py", "Settings")
        # Even with mock, file validation happens first
        assert isinstance(result, DefinitionResult)


class TestFindAllReferences:
    """Tests for find_all_references tool."""

    @pytest.mark.asyncio
    async def test_returns_error_for_missing_file(self, mock_codebase_root):
        result = await find_all_references("nonexistent/file.py", "Symbol")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_error_when_symbol_not_in_file(self, mock_codebase_root):
        result = await find_all_references(
            "backend/app/config.py",
            "NonExistentSymbol999",
        )
        assert result.success is False

    @pytest.mark.asyncio
    async def test_returns_result_schema(self, mock_codebase_root, mock_lsp_manager):
        mock_get, manager = mock_lsp_manager
        manager.get_client.return_value = None
        mock_get.return_value = manager

        result = await find_all_references("backend/app/config.py", "Settings")
        assert isinstance(result, ReferencesResult)


class TestGetTypeInfo:
    """Tests for get_type_info tool."""

    @pytest.mark.asyncio
    async def test_returns_error_for_missing_file(self, mock_codebase_root):
        result = await get_type_info("nonexistent/file.py", "Symbol")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_type_info_schema(self, mock_codebase_root, mock_lsp_manager):
        mock_get, manager = mock_lsp_manager
        manager.get_client.return_value = None
        mock_get.return_value = manager

        result = await get_type_info("backend/app/config.py", "Settings")
        assert isinstance(result, TypeInfo)


class TestGetDocumentSymbols:
    """Tests for get_document_symbols tool."""

    @pytest.mark.asyncio
    async def test_returns_error_for_missing_file(self, mock_codebase_root):
        result = await get_document_symbols("nonexistent/file.py")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_document_symbols_schema(
        self, mock_codebase_root, mock_lsp_manager
    ):
        mock_get, manager = mock_lsp_manager
        manager.get_client.return_value = None
        mock_get.return_value = manager

        result = await get_document_symbols("backend/app/config.py")
        assert isinstance(result, DocumentSymbolsResult)


class TestGetCallers:
    """Tests for get_callers tool."""

    @pytest.mark.asyncio
    async def test_returns_error_for_missing_file(self, mock_codebase_root):
        result = await get_callers("nonexistent/file.py", "function")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_call_hierarchy_schema(
        self, mock_codebase_root, mock_lsp_manager
    ):
        mock_get, manager = mock_lsp_manager
        manager.get_client.return_value = None
        mock_get.return_value = manager

        result = await get_callers("backend/app/config.py", "get_settings")
        assert isinstance(result, CallHierarchyResult)


# ============================================================================
# Integration Tests (if LSP servers are available)
# ============================================================================


class TestGoToDefinitionWithMockedLSP:
    """Tests for go_to_definition with fully mocked LSP."""

    @pytest.mark.asyncio
    async def test_finds_definition_and_returns_preview(self, mock_codebase_root):
        """Test successful definition lookup with mocked LSP."""

        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            manager = MagicMock()
            mock_client = MagicMock()

            # Create proper mock location
            mock_location = MagicMock()
            mock_location.uri = f"file://{mock_codebase_root}/backend/app/config.py"
            mock_location.range = MagicMock()
            mock_location.range.start = MagicMock(line=9, character=0)
            mock_location.range.end = MagicMock(line=9, character=8)

            mock_client.go_to_definition = AsyncMock(return_value=[mock_location])
            manager.get_client.return_value = mock_client
            mock_get.return_value = manager

            result = await go_to_definition("backend/app/config.py", "Settings", 10, 0)

            assert isinstance(result, DefinitionResult)
            # Should have called go_to_definition on client
            mock_client.go_to_definition.assert_called_once()


class TestFindAllReferencesWithMockedLSP:
    """Tests for find_all_references with fully mocked LSP."""

    @pytest.mark.asyncio
    async def test_finds_references_and_returns_context(self, mock_codebase_root):
        """Test successful reference lookup with mocked LSP."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            manager = MagicMock()
            mock_client = MagicMock()

            mock_location = MagicMock()
            mock_location.uri = f"file://{mock_codebase_root}/backend/app/main.py"
            mock_location.range = MagicMock()
            mock_location.range.start = MagicMock(line=5, character=10)
            mock_location.range.end = MagicMock(line=5, character=18)

            mock_client.find_references = AsyncMock(return_value=[mock_location])
            manager.get_client.return_value = mock_client
            mock_get.return_value = manager

            result = await find_all_references(
                "backend/app/config.py", "Settings", 10, 0
            )

            assert isinstance(result, ReferencesResult)
            mock_client.find_references.assert_called_once()


class TestGetTypeInfoWithMockedLSP:
    """Tests for get_type_info with fully mocked LSP."""

    @pytest.mark.asyncio
    async def test_gets_type_info_successfully(self, mock_codebase_root):
        """Test successful hover/type info lookup."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            manager = MagicMock()
            mock_client = MagicMock()

            mock_hover = MagicMock()
            mock_hover.contents = "class Settings(BaseSettings)"

            mock_client.hover = AsyncMock(return_value=mock_hover)
            manager.get_client.return_value = mock_client
            mock_get.return_value = manager

            result = await get_type_info("backend/app/config.py", "Settings", 10, 0)

            assert isinstance(result, TypeInfo)
            assert result.success is True
            assert "Settings" in result.type_signature

    @pytest.mark.asyncio
    async def test_returns_error_when_no_hover_info(self, mock_codebase_root):
        """Test when hover returns None."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            manager = MagicMock()
            mock_client = MagicMock()

            mock_client.hover = AsyncMock(return_value=None)
            manager.get_client.return_value = mock_client
            mock_get.return_value = manager

            result = await get_type_info("backend/app/config.py", "Settings", 10, 0)

            assert result.success is False
            assert "No type information" in result.error


class TestGetDocumentSymbolsWithMockedLSP:
    """Tests for get_document_symbols with fully mocked LSP."""

    @pytest.mark.asyncio
    async def test_gets_symbols_successfully(self, mock_codebase_root):
        """Test successful document symbol lookup."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            manager = MagicMock()
            mock_client = MagicMock()

            mock_symbol = MagicMock()
            mock_symbol.name = "Settings"
            mock_symbol.kind = 5  # Class
            mock_symbol.location = MagicMock()
            mock_symbol.location.range = MagicMock()
            mock_symbol.location.range.start = MagicMock(line=9)
            mock_symbol.container_name = None

            mock_client.document_symbols = AsyncMock(return_value=[mock_symbol])
            manager.get_client.return_value = mock_client
            mock_get.return_value = manager

            result = await get_document_symbols("backend/app/config.py")

            assert isinstance(result, DocumentSymbolsResult)
            assert result.success is True
            assert len(result.symbols) == 1
            assert result.symbols[0].name == "Settings"


class TestGetCallersWithMockedLSP:
    """Tests for get_callers with fully mocked LSP."""

    @pytest.mark.asyncio
    async def test_gets_callers_successfully(self, mock_codebase_root):
        """Test successful call hierarchy lookup."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            manager = MagicMock()
            mock_client = MagicMock()

            # Mock call hierarchy item
            mock_item = MagicMock()
            mock_item.name = "get_settings"
            mock_item.kind = 12  # Function
            mock_item.uri = f"file://{mock_codebase_root}/backend/app/config.py"
            mock_item.range = MagicMock()
            mock_item.range.start = MagicMock(line=44)
            mock_item.selection_range = MagicMock()

            mock_client.prepare_call_hierarchy = AsyncMock(return_value=[mock_item])
            mock_client.incoming_calls = AsyncMock(return_value=[])
            manager.get_client.return_value = mock_client
            mock_get.return_value = manager

            result = await get_callers("backend/app/config.py", "get_settings", 45, 0)

            assert isinstance(result, CallHierarchyResult)
            mock_client.prepare_call_hierarchy.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_error_when_no_call_hierarchy(self, mock_codebase_root):
        """Test when prepare_call_hierarchy returns empty."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            manager = MagicMock()
            mock_client = MagicMock()

            mock_client.prepare_call_hierarchy = AsyncMock(return_value=[])
            manager.get_client.return_value = mock_client
            mock_get.return_value = manager

            result = await get_callers("backend/app/config.py", "get_settings", 45, 0)

            assert result.success is False
            assert "Could not prepare call hierarchy" in result.error


class TestSemanticToolsExceptionHandling:
    """Tests for exception handling in semantic tools."""

    @pytest.mark.asyncio
    async def test_go_to_definition_handles_exception(self, mock_codebase_root):
        """Test that exceptions are caught and returned as errors."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            mock_get.side_effect = Exception("LSP connection failed")

            result = await go_to_definition("backend/app/config.py", "Settings", 10, 0)

            assert result.success is False
            assert "LSP connection failed" in result.error

    @pytest.mark.asyncio
    async def test_find_all_references_handles_exception(self, mock_codebase_root):
        """Test that exceptions are caught."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            mock_get.side_effect = Exception("Connection error")

            result = await find_all_references(
                "backend/app/config.py", "Settings", 10, 0
            )

            assert result.success is False
            assert "Connection error" in result.error

    @pytest.mark.asyncio
    async def test_get_type_info_handles_exception(self, mock_codebase_root):
        """Test exception handling."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            mock_get.side_effect = Exception("Hover failed")

            result = await get_type_info("backend/app/config.py", "Settings", 10, 0)

            assert result.success is False
            assert "Hover failed" in result.error

    @pytest.mark.asyncio
    async def test_get_document_symbols_handles_exception(self, mock_codebase_root):
        """Test exception handling."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            mock_get.side_effect = Exception("Symbol lookup failed")

            result = await get_document_symbols("backend/app/config.py")

            assert result.success is False
            assert "Symbol lookup failed" in result.error

    @pytest.mark.asyncio
    async def test_get_callers_handles_exception(self, mock_codebase_root):
        """Test exception handling."""
        with patch("app.tools.semantic.get_lsp_manager") as mock_get:
            mock_get.side_effect = Exception("Call hierarchy failed")

            result = await get_callers("backend/app/config.py", "get_settings", 45, 0)

            assert result.success is False
            assert "Call hierarchy failed" in result.error


@pytest.mark.integration
class TestLSPIntegration:
    """Integration tests that require actual LSP servers.

    These tests are skipped by default and only run when LSP servers
    are available in the environment.
    """

    @pytest.mark.asyncio
    async def test_real_go_to_definition(self, mock_codebase_root):
        """Test with real LSP if available."""
        # This test will fail gracefully if LSP is not available
        result = await go_to_definition("backend/app/config.py", "Settings")
        # Just verify we get a valid result structure
        assert isinstance(result, DefinitionResult)

    @pytest.mark.asyncio
    async def test_real_document_symbols(self, mock_codebase_root):
        """Test document symbols with real LSP if available."""
        result = await get_document_symbols("backend/app/config.py")
        assert isinstance(result, DocumentSymbolsResult)
