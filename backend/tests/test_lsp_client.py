"""Tests for the LSP (Language Server Protocol) client manager.

These tests verify the LSP client infrastructure works correctly,
including process management, JSON-RPC communication, and graceful
handling when LSP servers are not available.
"""

import os
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from app.tools.lsp_client import (
    LanguageServer,
    Position,
    Range,
    Location,
    SymbolInformation,
    HoverResult,
    CallHierarchyItem,
    CodeClient,
    CodeManager,
    get_code_manager,
    shutdown_code_manager,
)


# ============================================================================
# Data Structure Tests
# ============================================================================


class TestPosition:
    """Tests for Position data class."""

    def test_create_position(self):
        pos = Position(line=10, character=5)
        assert pos.line == 10
        assert pos.character == 5

    def test_to_dict(self):
        pos = Position(line=10, character=5)
        assert pos.to_dict() == {"line": 10, "character": 5}


class TestRange:
    """Tests for Range data class."""

    def test_create_range(self):
        start = Position(line=0, character=0)
        end = Position(line=0, character=10)
        range_ = Range(start=start, end=end)
        assert range_.start.line == 0
        assert range_.end.character == 10

    def test_to_dict(self):
        range_ = Range(
            start=Position(line=1, character=2),
            end=Position(line=3, character=4),
        )
        result = range_.to_dict()
        assert result["start"]["line"] == 1
        assert result["end"]["character"] == 4


class TestLocation:
    """Tests for Location data class."""

    def test_create_location(self):
        loc = Location(
            uri="file:///test/file.py",
            range=Range(
                start=Position(line=5, character=0),
                end=Position(line=5, character=10),
            ),
        )
        assert loc.uri == "file:///test/file.py"
        assert loc.range.start.line == 5

    def test_from_dict(self):
        data = {
            "uri": "file:///test/file.py",
            "range": {
                "start": {"line": 10, "character": 0},
                "end": {"line": 10, "character": 20},
            },
        }
        loc = Location.from_dict(data)
        assert loc.uri == "file:///test/file.py"
        assert loc.range.start.line == 10
        assert loc.range.end.character == 20


class TestSymbolInformation:
    """Tests for SymbolInformation data class."""

    def test_create_symbol(self):
        sym = SymbolInformation(
            name="my_function",
            kind=12,  # Function
            location=Location(
                uri="file:///test/file.py",
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=5, character=0),
                ),
            ),
        )
        assert sym.name == "my_function"
        assert sym.kind == 12

    def test_from_dict(self):
        data = {
            "name": "MyClass",
            "kind": 5,  # Class
            "location": {
                "uri": "file:///test/file.py",
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 10, "character": 0},
                },
            },
            "containerName": "module",
        }
        sym = SymbolInformation.from_dict(data)
        assert sym.name == "MyClass"
        assert sym.kind == 5
        assert sym.container_name == "module"


class TestHoverResult:
    """Tests for HoverResult data class."""

    def test_create_hover_result(self):
        result = HoverResult(
            contents="def my_function() -> str",
            range=None,
        )
        assert result.contents == "def my_function() -> str"

    def test_with_range(self):
        result = HoverResult(
            contents="Type: int",
            range=Range(
                start=Position(line=5, character=0),
                end=Position(line=5, character=5),
            ),
        )
        assert result.range is not None
        assert result.range.start.line == 5


class TestCallHierarchyItem:
    """Tests for CallHierarchyItem data class."""

    def test_from_dict(self):
        data = {
            "name": "caller_function",
            "kind": 12,  # Function
            "uri": "file:///test/caller.py",
            "range": {
                "start": {"line": 10, "character": 0},
                "end": {"line": 15, "character": 0},
            },
            "selectionRange": {
                "start": {"line": 10, "character": 4},
                "end": {"line": 10, "character": 19},
            },
            "detail": "module.caller_function",
        }
        item = CallHierarchyItem.from_dict(data)
        assert item.name == "caller_function"
        assert item.kind == 12
        assert item.detail == "module.caller_function"


# ============================================================================
# LSP Client Tests
# ============================================================================


class TestCodeClientLanguageServer:
    """Tests for LanguageServer enum."""

    def test_typescript_server(self):
        assert LanguageServer.TYPESCRIPT.value == "typescript"

    def test_python_server(self):
        assert LanguageServer.PYTHON.value == "python"


class TestCodeClientServerCommand:
    """Tests for LSP client server command generation."""

    def test_typescript_command(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        cmd = client._get_server_command()
        assert cmd == ["typescript-language-server", "--stdio"]

    def test_python_command(self):
        client = CodeClient(server_type=LanguageServer.PYTHON)
        cmd = client._get_server_command()
        assert cmd == ["pyright-langserver", "--stdio"]


class TestCodeClientLanguageId:
    """Tests for language ID detection."""

    def test_python_language_id(self):
        client = CodeClient(server_type=LanguageServer.PYTHON)
        assert client._get_language_id("/path/to/file.py") == "python"

    def test_typescript_language_id(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        assert client._get_language_id("/path/to/file.ts") == "typescript"

    def test_tsx_language_id(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        assert client._get_language_id("/path/to/component.tsx") == "typescriptreact"

    def test_javascript_language_id(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        assert client._get_language_id("/path/to/script.js") == "javascript"

    def test_jsx_language_id(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        assert client._get_language_id("/path/to/component.jsx") == "javascriptreact"

    def test_json_language_id(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        assert client._get_language_id("/path/to/config.json") == "json"

    def test_unknown_language_id(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        assert client._get_language_id("/path/to/file.xyz") == "plaintext"


class TestCodeClientNotInitialized:
    """Tests for LSP client when not initialized."""

    @pytest.mark.asyncio
    async def test_go_to_definition_not_initialized(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        # _initialized is False by default
        result = await client.go_to_definition("/test/file.ts", 0, 0)
        assert result == []

    @pytest.mark.asyncio
    async def test_find_references_not_initialized(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        result = await client.find_references("/test/file.ts", 0, 0)
        assert result == []

    @pytest.mark.asyncio
    async def test_hover_not_initialized(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        result = await client.hover("/test/file.ts", 0, 0)
        assert result is None

    @pytest.mark.asyncio
    async def test_document_symbols_not_initialized(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        result = await client.document_symbols("/test/file.ts")
        assert result == []

    @pytest.mark.asyncio
    async def test_workspace_symbols_not_initialized(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        result = await client.workspace_symbols("test")
        assert result == []

    @pytest.mark.asyncio
    async def test_prepare_call_hierarchy_not_initialized(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        result = await client.prepare_call_hierarchy("/test/file.ts", 0, 0)
        assert result == []


class TestCodeClientStart:
    """Tests for LSP client start behavior."""

    @pytest.mark.asyncio
    async def test_start_fails_when_server_not_found(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)

        with patch("subprocess.Popen") as mock_popen:
            mock_popen.side_effect = FileNotFoundError("Server not found")
            result = await client.start("/test/workspace")

        assert result is False
        assert client._initialized is False


# ============================================================================
# LSP Manager Tests
# ============================================================================


class TestCodeManager:
    """Tests for CodeManager."""

    def test_create_manager(self):
        manager = CodeManager(workspace_root="/test/workspace")
        assert manager.workspace_root == "/test/workspace"
        assert manager._initialized is False

    def test_get_client_for_typescript(self):
        manager = CodeManager(workspace_root="/test")
        # Add a mock client
        mock_client = MagicMock()
        manager._clients[LanguageServer.TYPESCRIPT] = mock_client

        result = manager.get_client("/path/to/file.ts")
        assert result == mock_client

    def test_get_client_for_tsx(self):
        manager = CodeManager(workspace_root="/test")
        mock_client = MagicMock()
        manager._clients[LanguageServer.TYPESCRIPT] = mock_client

        result = manager.get_client("/path/to/component.tsx")
        assert result == mock_client

    def test_get_client_for_python(self):
        manager = CodeManager(workspace_root="/test")
        mock_client = MagicMock()
        manager._clients[LanguageServer.PYTHON] = mock_client

        result = manager.get_client("/path/to/file.py")
        assert result == mock_client

    def test_get_client_for_unsupported_type(self):
        manager = CodeManager(workspace_root="/test")
        result = manager.get_client("/path/to/file.rb")  # Ruby not supported
        assert result is None

    def test_available_servers_empty(self):
        manager = CodeManager(workspace_root="/test")
        assert manager.available_servers == []

    def test_available_servers_with_clients(self):
        manager = CodeManager(workspace_root="/test")
        manager._clients[LanguageServer.TYPESCRIPT] = MagicMock()
        manager._clients[LanguageServer.PYTHON] = MagicMock()

        servers = manager.available_servers
        assert "typescript" in servers
        assert "python" in servers

    @pytest.mark.asyncio
    async def test_shutdown_clears_clients(self):
        manager = CodeManager(workspace_root="/test")
        mock_client = MagicMock()
        mock_client.stop = AsyncMock()
        manager._clients[LanguageServer.TYPESCRIPT] = mock_client
        manager._initialized = True

        await manager.shutdown()

        mock_client.stop.assert_called_once()
        assert len(manager._clients) == 0
        assert manager._initialized is False


# ============================================================================
# Global Manager Tests
# ============================================================================


class TestGlobalCodeManager:
    """Tests for global LSP manager functions."""

    @pytest.mark.asyncio
    async def test_get_manager_requires_workspace_root(self):
        # Reset global manager
        import app.tools.lsp_client as lsp_module

        lsp_module._code_manager = None

        with pytest.raises(ValueError, match="workspace_root is required"):
            await get_code_manager(None)

    @pytest.mark.asyncio
    async def test_shutdown_handles_none_manager(self):
        # Should not raise even if manager is None
        import app.tools.lsp_client as lsp_module

        lsp_module._code_manager = None

        await shutdown_code_manager()  # Should not raise


# ============================================================================
# Integration Tests
# ============================================================================


class TestCodeClientSendMessage:
    """Tests for LSP client message sending."""

    def test_send_message_without_process_raises(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client.process = None

        with pytest.raises(RuntimeError, match="LSP server not running"):
            client._send_message({"jsonrpc": "2.0", "id": 1, "method": "test"})

    def test_send_message_format(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)

        # Mock process with stdin
        mock_stdin = MagicMock()
        mock_process = MagicMock()
        mock_process.stdin = mock_stdin
        client.process = mock_process

        client._send_message({"jsonrpc": "2.0", "id": 1, "method": "test"})

        # Verify message was written
        mock_stdin.write.assert_called_once()
        mock_stdin.flush.assert_called_once()

        # Check the format includes Content-Length header
        written_data = mock_stdin.write.call_args[0][0]
        assert b"Content-Length:" in written_data


class TestCodeClientReadMessage:
    """Tests for LSP client message reading."""

    def test_read_message_without_process(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client.process = None

        result = client._read_message()
        assert result is None

    def test_read_message_parses_json(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)

        # Create mock with proper header and content
        mock_stdout = MagicMock()
        content = '{"jsonrpc":"2.0","id":1,"result":null}'
        mock_stdout.readline.side_effect = [
            f"Content-Length: {len(content)}\r\n".encode("utf-8"),
            b"\r\n",
        ]
        mock_stdout.read.return_value = content.encode("utf-8")

        mock_process = MagicMock()
        mock_process.stdout = mock_stdout
        client.process = mock_process

        result = client._read_message()
        assert result == {"jsonrpc": "2.0", "id": 1, "result": None}


class TestCodeClientOpenCloseDocument:
    """Tests for document open/close notifications."""

    def test_open_document_sends_notification(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)

        # Mock process
        mock_stdin = MagicMock()
        mock_process = MagicMock()
        mock_process.stdin = mock_stdin
        client.process = mock_process

        client._open_document("/test/file.ts", "const x = 1;", "typescript")

        mock_stdin.write.assert_called_once()
        written_data = mock_stdin.write.call_args[0][0].decode("utf-8")
        assert "textDocument/didOpen" in written_data

    def test_close_document_sends_notification(self):
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)

        mock_stdin = MagicMock()
        mock_process = MagicMock()
        mock_process.stdin = mock_stdin
        client.process = mock_process

        client._close_document("/test/file.ts")

        mock_stdin.write.assert_called_once()
        written_data = mock_stdin.write.call_args[0][0].decode("utf-8")
        assert "textDocument/didClose" in written_data


class TestCodeManagerInitialize:
    """Tests for LSP manager initialization."""

    @pytest.mark.asyncio
    async def test_initialize_returns_status_dict(self):
        manager = CodeManager(workspace_root="/test")

        with patch.object(CodeClient, "start", new_callable=AsyncMock) as mock_start:
            mock_start.return_value = False  # Servers not available

            result = await manager.initialize()

        assert isinstance(result, dict)
        assert "typescript" in result
        assert "python" in result

    @pytest.mark.asyncio
    async def test_initialize_stores_successful_clients(self):
        manager = CodeManager(workspace_root="/test")

        with patch.object(CodeClient, "start", new_callable=AsyncMock) as mock_start:
            # Only TypeScript server succeeds
            mock_start.side_effect = [True, False]

            result = await manager.initialize()

        assert result["typescript"] is True
        assert result["python"] is False
        assert LanguageServer.TYPESCRIPT in manager._clients


class TestCodeClientAsyncMethods:
    """Tests for async LSP client methods with mocked initialization."""

    @pytest.mark.asyncio
    async def test_go_to_definition_with_initialized_client(self):
        """Test go_to_definition when client is initialized."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        # Mock the send_request to return a location
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch("pathlib.Path.read_text", return_value="const x = 1;"):
                        mock_send.return_value = {
                            "uri": "file:///test/file.ts",
                            "range": {
                                "start": {"line": 0, "character": 0},
                                "end": {"line": 0, "character": 5},
                            },
                        }

                        result = await client.go_to_definition("/test/file.ts", 0, 0)

        assert len(result) == 1
        assert result[0].uri == "file:///test/file.ts"

    @pytest.mark.asyncio
    async def test_go_to_definition_handles_list_result(self):
        """Test go_to_definition when LSP returns a list of locations."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch("pathlib.Path.read_text", return_value="const x = 1;"):
                        mock_send.return_value = [
                            {
                                "uri": "file:///test/file1.ts",
                                "range": {
                                    "start": {"line": 0, "character": 0},
                                    "end": {"line": 0, "character": 5},
                                },
                            },
                            {
                                "uri": "file:///test/file2.ts",
                                "range": {
                                    "start": {"line": 5, "character": 0},
                                    "end": {"line": 5, "character": 5},
                                },
                            },
                        ]

                        result = await client.go_to_definition("/test/file.ts", 0, 0)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_go_to_definition_handles_exception(self):
        """Test go_to_definition handles exceptions gracefully."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch("pathlib.Path.read_text", side_effect=Exception("Read error")):
            result = await client.go_to_definition("/test/file.ts", 0, 0)

        assert result == []

    @pytest.mark.asyncio
    async def test_find_references_with_initialized_client(self):
        """Test find_references when client is initialized."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch("pathlib.Path.read_text", return_value="const x = 1;"):
                        mock_send.return_value = [
                            {
                                "uri": "file:///test/ref.ts",
                                "range": {
                                    "start": {"line": 10, "character": 0},
                                    "end": {"line": 10, "character": 5},
                                },
                            }
                        ]

                        result = await client.find_references("/test/file.ts", 0, 0)

        assert len(result) == 1
        assert result[0].uri == "file:///test/ref.ts"

    @pytest.mark.asyncio
    async def test_hover_with_initialized_client(self):
        """Test hover when client is initialized."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch("pathlib.Path.read_text", return_value="const x = 1;"):
                        mock_send.return_value = {
                            "contents": "const x: number",
                            "range": {
                                "start": {"line": 0, "character": 0},
                                "end": {"line": 0, "character": 5},
                            },
                        }

                        result = await client.hover("/test/file.ts", 0, 0)

        assert result is not None
        assert result.contents == "const x: number"

    @pytest.mark.asyncio
    async def test_hover_with_dict_contents(self):
        """Test hover with MarkupContent format."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch("pathlib.Path.read_text", return_value="const x = 1;"):
                        mock_send.return_value = {
                            "contents": {
                                "kind": "markdown",
                                "value": "**Type**: number",
                            },
                        }

                        result = await client.hover("/test/file.ts", 0, 0)

        assert result is not None
        assert "number" in result.contents

    @pytest.mark.asyncio
    async def test_hover_with_list_contents(self):
        """Test hover with MarkedString array format."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch("pathlib.Path.read_text", return_value="const x = 1;"):
                        mock_send.return_value = {
                            "contents": [
                                {"language": "typescript", "value": "const x: number"},
                                "A constant",
                            ],
                        }

                        result = await client.hover("/test/file.ts", 0, 0)

        assert result is not None

    @pytest.mark.asyncio
    async def test_hover_returns_none_when_no_result(self):
        """Test hover returns None when no result."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch("pathlib.Path.read_text", return_value="const x = 1;"):
                        mock_send.return_value = None

                        result = await client.hover("/test/file.ts", 0, 0)

        assert result is None

    @pytest.mark.asyncio
    async def test_document_symbols_with_location_format(self):
        """Test document_symbols with SymbolInformation format."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch("pathlib.Path.read_text", return_value="const x = 1;"):
                        mock_send.return_value = [
                            {
                                "name": "myFunction",
                                "kind": 12,
                                "location": {
                                    "uri": "file:///test/file.ts",
                                    "range": {
                                        "start": {"line": 0, "character": 0},
                                        "end": {"line": 5, "character": 0},
                                    },
                                },
                            }
                        ]

                        result = await client.document_symbols("/test/file.ts")

        assert len(result) == 1
        assert result[0].name == "myFunction"

    @pytest.mark.asyncio
    async def test_document_symbols_with_document_symbol_format(self):
        """Test document_symbols with DocumentSymbol format (has children)."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch(
                        "pathlib.Path.read_text", return_value="class MyClass {}"
                    ):
                        mock_send.return_value = [
                            {
                                "name": "MyClass",
                                "kind": 5,
                                "range": {
                                    "start": {"line": 0, "character": 0},
                                    "end": {"line": 10, "character": 0},
                                },
                                "selectionRange": {
                                    "start": {"line": 0, "character": 6},
                                    "end": {"line": 0, "character": 13},
                                },
                                "children": [
                                    {
                                        "name": "myMethod",
                                        "kind": 6,
                                        "range": {
                                            "start": {"line": 2, "character": 0},
                                            "end": {"line": 5, "character": 0},
                                        },
                                        "selectionRange": {
                                            "start": {"line": 2, "character": 2},
                                            "end": {"line": 2, "character": 10},
                                        },
                                    }
                                ],
                            }
                        ]

                        result = await client.document_symbols("/test/file.ts")

        assert len(result) == 2  # Parent + child
        assert result[0].name == "MyClass"
        assert result[1].name == "myMethod"
        assert result[1].container_name == "MyClass"

    @pytest.mark.asyncio
    async def test_workspace_symbols_with_initialized_client(self):
        """Test workspace_symbols when client is initialized."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = [
                {
                    "name": "globalFunction",
                    "kind": 12,
                    "location": {
                        "uri": "file:///test/file.ts",
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 0},
                        },
                    },
                }
            ]

            result = await client.workspace_symbols("global")

        assert len(result) == 1
        assert result[0].name == "globalFunction"

    @pytest.mark.asyncio
    async def test_prepare_call_hierarchy_with_initialized_client(self):
        """Test prepare_call_hierarchy when client is initialized."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            with patch.object(client, "_open_document"):
                with patch.object(client, "_close_document"):
                    with patch(
                        "pathlib.Path.read_text", return_value="function test() {}"
                    ):
                        mock_send.return_value = [
                            {
                                "name": "test",
                                "kind": 12,
                                "uri": "file:///test/file.ts",
                                "range": {
                                    "start": {"line": 0, "character": 0},
                                    "end": {"line": 0, "character": 20},
                                },
                                "selectionRange": {
                                    "start": {"line": 0, "character": 9},
                                    "end": {"line": 0, "character": 13},
                                },
                            }
                        ]

                        result = await client.prepare_call_hierarchy(
                            "/test/file.ts", 0, 10
                        )

        assert len(result) == 1
        assert result[0].name == "test"

    @pytest.mark.asyncio
    async def test_incoming_calls_with_initialized_client(self):
        """Test incoming_calls when client is initialized."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        client._initialized = True
        client.workspace_root = "/test"

        item = CallHierarchyItem(
            name="test",
            kind=12,
            uri="file:///test/file.ts",
            range=Range(start=Position(0, 0), end=Position(0, 20)),
            selection_range=Range(start=Position(0, 9), end=Position(0, 13)),
        )

        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = [
                {
                    "from": {
                        "name": "caller",
                        "kind": 12,
                        "uri": "file:///test/caller.ts",
                        "range": {
                            "start": {"line": 5, "character": 0},
                            "end": {"line": 10, "character": 0},
                        },
                        "selectionRange": {
                            "start": {"line": 5, "character": 9},
                            "end": {"line": 5, "character": 15},
                        },
                    },
                    "fromRanges": [
                        {
                            "start": {"line": 7, "character": 2},
                            "end": {"line": 7, "character": 8},
                        },
                    ],
                }
            ]

            result = await client.incoming_calls(item)

        assert len(result) == 1
        assert result[0].from_item.name == "caller"
        assert len(result[0].from_ranges) == 1


@pytest.mark.integration
class TestLSPIntegration:
    """Integration tests that require actual LSP servers.

    These tests are skipped by default and require:
    - typescript-language-server
    - pyright-langserver

    Run with: pytest -m integration
    """

    @pytest.fixture
    def workspace_root(self):
        """Get the project workspace root."""
        return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    @pytest.mark.asyncio
    async def test_typescript_server_starts(self, workspace_root):
        """Test that TypeScript server can start."""
        client = CodeClient(server_type=LanguageServer.TYPESCRIPT)
        try:
            result = await client.start(workspace_root)
            # May fail if server not installed, that's okay for CI
            if result:
                assert client._initialized is True
        finally:
            await client.stop()

    @pytest.mark.asyncio
    async def test_python_server_starts(self, workspace_root):
        """Test that Python server can start."""
        client = CodeClient(server_type=LanguageServer.PYTHON)
        try:
            result = await client.start(workspace_root)
            if result:
                assert client._initialized is True
        finally:
            await client.stop()
