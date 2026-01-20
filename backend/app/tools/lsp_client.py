"""LSP (Language Server Protocol) client manager for semantic code analysis.

This module provides a unified interface to TypeScript and Python language servers,
enabling semantic code intelligence features like go-to-definition, find-references,
hover information, and more.
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LanguageServer(Enum):
    """Supported language servers."""

    TYPESCRIPT = "typescript"
    PYTHON = "python"


@dataclass
class Position:
    """A position in a text document (0-indexed)."""

    line: int
    character: int

    def to_dict(self) -> dict[str, int]:
        return {"line": self.line, "character": self.character}


@dataclass
class Range:
    """A range in a text document."""

    start: Position
    end: Position

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclass
class Location:
    """A location in a text document."""

    uri: str
    range: Range

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Location":
        return cls(
            uri=data["uri"],
            range=Range(
                start=Position(
                    line=data["range"]["start"]["line"],
                    character=data["range"]["start"]["character"],
                ),
                end=Position(
                    line=data["range"]["end"]["line"],
                    character=data["range"]["end"]["character"],
                ),
            ),
        )


@dataclass
class SymbolInformation:
    """Information about a symbol in a document."""

    name: str
    kind: int  # SymbolKind enum value
    location: Location
    container_name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SymbolInformation":
        return cls(
            name=data["name"],
            kind=data["kind"],
            location=Location.from_dict(data["location"]),
            container_name=data.get("containerName"),
        )


@dataclass
class HoverResult:
    """Result of a hover request."""

    contents: str
    range: Range | None = None


@dataclass
class CallHierarchyItem:
    """An item in the call hierarchy."""

    name: str
    kind: int
    uri: str
    range: Range
    selection_range: Range
    detail: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CallHierarchyItem":
        return cls(
            name=data["name"],
            kind=data["kind"],
            uri=data["uri"],
            range=Range(
                start=Position(
                    line=data["range"]["start"]["line"],
                    character=data["range"]["start"]["character"],
                ),
                end=Position(
                    line=data["range"]["end"]["line"],
                    character=data["range"]["end"]["character"],
                ),
            ),
            selection_range=Range(
                start=Position(
                    line=data["selectionRange"]["start"]["line"],
                    character=data["selectionRange"]["start"]["character"],
                ),
                end=Position(
                    line=data["selectionRange"]["end"]["line"],
                    character=data["selectionRange"]["end"]["character"],
                ),
            ),
            detail=data.get("detail"),
        )


@dataclass
class CallHierarchyIncomingCall:
    """An incoming call in the call hierarchy."""

    from_item: CallHierarchyItem
    from_ranges: list[Range]


@dataclass
class LSPClient:
    """Client for communicating with an LSP server."""

    server_type: LanguageServer
    process: subprocess.Popen | None = None
    request_id: int = field(default=0)
    workspace_root: str = ""
    _initialized: bool = field(default=False)
    _pending_responses: dict[int, asyncio.Future] = field(default_factory=dict)
    _reader_task: asyncio.Task | None = field(default=None)

    def _get_server_command(self) -> list[str]:
        """Get the command to start the language server."""
        if self.server_type == LanguageServer.TYPESCRIPT:
            return ["typescript-language-server", "--stdio"]
        elif self.server_type == LanguageServer.PYTHON:
            return ["pyright-langserver", "--stdio"]
        raise ValueError(f"Unknown server type: {self.server_type}")

    async def start(self, workspace_root: str) -> bool:
        """Start the language server process."""
        self.workspace_root = workspace_root

        try:
            cmd = self._get_server_command()
            logger.info(f"Starting LSP server: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=workspace_root,
            )

            # Initialize the server
            init_result = await self._initialize()
            if init_result:
                self._initialized = True
                await self._initialized_notification()
                logger.info(
                    f"LSP server {self.server_type.value} initialized successfully"
                )
                return True
            return False

        except FileNotFoundError as e:
            logger.error(f"LSP server not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to start LSP server: {e}")
            return False

    async def stop(self) -> None:
        """Stop the language server process."""
        if self.process:
            try:
                await self._send_request("shutdown", {})
                self._send_notification("exit", {})
            except Exception:
                pass
            finally:
                self.process.terminate()
                self.process = None
                self._initialized = False

    def _send_message(self, message: dict[str, Any]) -> None:
        """Send a JSON-RPC message to the server."""
        if not self.process or not self.process.stdin:
            raise RuntimeError("LSP server not running")

        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"
        full_message = header + content

        self.process.stdin.write(full_message.encode("utf-8"))
        self.process.stdin.flush()

    def _read_message(self) -> dict[str, Any] | None:
        """Read a JSON-RPC message from the server."""
        if not self.process or not self.process.stdout:
            return None

        # Read headers
        headers: dict[str, str] = {}
        while True:
            line = self.process.stdout.readline().decode("utf-8")
            if line == "\r\n" or line == "\n":
                break
            if not line:
                return None
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        # Read content
        content_length = int(headers.get("Content-Length", 0))
        if content_length == 0:
            return None

        content = self.process.stdout.read(content_length).decode("utf-8")
        return json.loads(content)

    async def _send_request(self, method: str, params: dict[str, Any]) -> Any:
        """Send a request and wait for response."""
        self.request_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params,
        }

        self._send_message(message)

        # Wait for response (simple sync read for now)
        while True:
            response = self._read_message()
            if response and response.get("id") == self.request_id:
                if "error" in response:
                    logger.error(f"LSP error: {response['error']}")
                    return None
                return response.get("result")

    def _send_notification(self, method: str, params: dict[str, Any]) -> None:
        """Send a notification (no response expected)."""
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        self._send_message(message)

    async def _initialize(self) -> dict[str, Any] | None:
        """Send the initialize request."""
        params = {
            "processId": os.getpid(),
            "rootUri": f"file://{self.workspace_root}",
            "rootPath": self.workspace_root,
            "capabilities": {
                "textDocument": {
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "definition": {"linkSupport": True},
                    "references": {},
                    "documentSymbol": {
                        "hierarchicalDocumentSymbolSupport": True,
                    },
                    "callHierarchy": {},
                },
                "workspace": {
                    "symbol": {"symbolKind": {"valueSet": list(range(1, 27))}},
                },
            },
            "workspaceFolders": [
                {
                    "uri": f"file://{self.workspace_root}",
                    "name": Path(self.workspace_root).name,
                }
            ],
        }
        return await self._send_request("initialize", params)

    async def _initialized_notification(self) -> None:
        """Send the initialized notification."""
        self._send_notification("initialized", {})

    def _open_document(self, file_path: str, content: str, language_id: str) -> None:
        """Notify the server that a document is open."""
        uri = f"file://{file_path}"
        self._send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": language_id,
                    "version": 1,
                    "text": content,
                }
            },
        )

    def _close_document(self, file_path: str) -> None:
        """Notify the server that a document is closed."""
        uri = f"file://{file_path}"
        self._send_notification(
            "textDocument/didClose",
            {"textDocument": {"uri": uri}},
        )

    async def go_to_definition(
        self, file_path: str, line: int, character: int
    ) -> list[Location]:
        """Find the definition of a symbol at the given position.

        Args:
            file_path: Absolute path to the file
            line: Line number (0-indexed)
            character: Character position (0-indexed)

        Returns:
            List of definition locations
        """
        if not self._initialized:
            return []

        # Open the document first
        try:
            content = Path(file_path).read_text()
            lang_id = self._get_language_id(file_path)
            self._open_document(file_path, content, lang_id)

            uri = f"file://{file_path}"
            result = await self._send_request(
                "textDocument/definition",
                {
                    "textDocument": {"uri": uri},
                    "position": {"line": line, "character": character},
                },
            )

            self._close_document(file_path)

            if not result:
                return []

            # Result can be a single Location or a list of Locations
            if isinstance(result, dict):
                return [Location.from_dict(result)]
            elif isinstance(result, list):
                return [Location.from_dict(loc) for loc in result]
            return []

        except Exception as e:
            logger.error(f"Error in go_to_definition: {e}")
            return []

    async def find_references(
        self,
        file_path: str,
        line: int,
        character: int,
        include_declaration: bool = True,
    ) -> list[Location]:
        """Find all references to a symbol at the given position.

        Args:
            file_path: Absolute path to the file
            line: Line number (0-indexed)
            character: Character position (0-indexed)
            include_declaration: Whether to include the declaration

        Returns:
            List of reference locations
        """
        if not self._initialized:
            return []

        try:
            content = Path(file_path).read_text()
            lang_id = self._get_language_id(file_path)
            self._open_document(file_path, content, lang_id)

            uri = f"file://{file_path}"
            result = await self._send_request(
                "textDocument/references",
                {
                    "textDocument": {"uri": uri},
                    "position": {"line": line, "character": character},
                    "context": {"includeDeclaration": include_declaration},
                },
            )

            self._close_document(file_path)

            if not result:
                return []

            return [Location.from_dict(loc) for loc in result]

        except Exception as e:
            logger.error(f"Error in find_references: {e}")
            return []

    async def hover(
        self, file_path: str, line: int, character: int
    ) -> HoverResult | None:
        """Get hover information at the given position.

        Args:
            file_path: Absolute path to the file
            line: Line number (0-indexed)
            character: Character position (0-indexed)

        Returns:
            HoverResult with type info and documentation, or None
        """
        if not self._initialized:
            return None

        try:
            content = Path(file_path).read_text()
            lang_id = self._get_language_id(file_path)
            self._open_document(file_path, content, lang_id)

            uri = f"file://{file_path}"
            result = await self._send_request(
                "textDocument/hover",
                {
                    "textDocument": {"uri": uri},
                    "position": {"line": line, "character": character},
                },
            )

            self._close_document(file_path)

            if not result or "contents" not in result:
                return None

            contents = result["contents"]
            if isinstance(contents, str):
                text = contents
            elif isinstance(contents, dict):
                text = contents.get("value", str(contents))
            elif isinstance(contents, list):
                text = "\n".join(
                    c.get("value", str(c)) if isinstance(c, dict) else str(c)
                    for c in contents
                )
            else:
                text = str(contents)

            hover_range = None
            if "range" in result:
                r = result["range"]
                hover_range = Range(
                    start=Position(r["start"]["line"], r["start"]["character"]),
                    end=Position(r["end"]["line"], r["end"]["character"]),
                )

            return HoverResult(contents=text, range=hover_range)

        except Exception as e:
            logger.error(f"Error in hover: {e}")
            return None

    async def document_symbols(self, file_path: str) -> list[SymbolInformation]:
        """Get all symbols in a document.

        Args:
            file_path: Absolute path to the file

        Returns:
            List of symbols in the document
        """
        if not self._initialized:
            return []

        try:
            content = Path(file_path).read_text()
            lang_id = self._get_language_id(file_path)
            self._open_document(file_path, content, lang_id)

            uri = f"file://{file_path}"
            result = await self._send_request(
                "textDocument/documentSymbol",
                {"textDocument": {"uri": uri}},
            )

            self._close_document(file_path)

            if not result:
                return []

            # Result can be DocumentSymbol[] or SymbolInformation[]
            symbols = []
            for item in result:
                if "location" in item:
                    # SymbolInformation format
                    symbols.append(SymbolInformation.from_dict(item))
                elif "range" in item:
                    # DocumentSymbol format - convert to SymbolInformation
                    symbols.append(
                        SymbolInformation(
                            name=item["name"],
                            kind=item["kind"],
                            location=Location(
                                uri=uri,
                                range=Range(
                                    start=Position(
                                        item["range"]["start"]["line"],
                                        item["range"]["start"]["character"],
                                    ),
                                    end=Position(
                                        item["range"]["end"]["line"],
                                        item["range"]["end"]["character"],
                                    ),
                                ),
                            ),
                        )
                    )
                    # Recursively add children if present
                    if "children" in item:
                        for child in item["children"]:
                            symbols.append(
                                SymbolInformation(
                                    name=child["name"],
                                    kind=child["kind"],
                                    location=Location(
                                        uri=uri,
                                        range=Range(
                                            start=Position(
                                                child["range"]["start"]["line"],
                                                child["range"]["start"]["character"],
                                            ),
                                            end=Position(
                                                child["range"]["end"]["line"],
                                                child["range"]["end"]["character"],
                                            ),
                                        ),
                                    ),
                                    container_name=item["name"],
                                )
                            )
            return symbols

        except Exception as e:
            logger.error(f"Error in document_symbols: {e}")
            return []

    async def workspace_symbols(self, query: str) -> list[SymbolInformation]:
        """Search for symbols across the workspace.

        Args:
            query: Search query string

        Returns:
            List of matching symbols
        """
        if not self._initialized:
            return []

        try:
            result = await self._send_request(
                "workspace/symbol",
                {"query": query},
            )

            if not result:
                return []

            return [SymbolInformation.from_dict(item) for item in result]

        except Exception as e:
            logger.error(f"Error in workspace_symbols: {e}")
            return []

    async def prepare_call_hierarchy(
        self, file_path: str, line: int, character: int
    ) -> list[CallHierarchyItem]:
        """Prepare call hierarchy at the given position.

        Args:
            file_path: Absolute path to the file
            line: Line number (0-indexed)
            character: Character position (0-indexed)

        Returns:
            List of call hierarchy items at this position
        """
        if not self._initialized:
            return []

        try:
            content = Path(file_path).read_text()
            lang_id = self._get_language_id(file_path)
            self._open_document(file_path, content, lang_id)

            uri = f"file://{file_path}"
            result = await self._send_request(
                "textDocument/prepareCallHierarchy",
                {
                    "textDocument": {"uri": uri},
                    "position": {"line": line, "character": character},
                },
            )

            self._close_document(file_path)

            if not result:
                return []

            return [CallHierarchyItem.from_dict(item) for item in result]

        except Exception as e:
            logger.error(f"Error in prepare_call_hierarchy: {e}")
            return []

    async def incoming_calls(
        self, item: CallHierarchyItem
    ) -> list[CallHierarchyIncomingCall]:
        """Get incoming calls to a call hierarchy item.

        Args:
            item: The call hierarchy item to get callers for

        Returns:
            List of incoming calls
        """
        if not self._initialized:
            return []

        try:
            result = await self._send_request(
                "callHierarchy/incomingCalls",
                {
                    "item": {
                        "name": item.name,
                        "kind": item.kind,
                        "uri": item.uri,
                        "range": item.range.to_dict(),
                        "selectionRange": item.selection_range.to_dict(),
                    }
                },
            )

            if not result:
                return []

            calls = []
            for call in result:
                from_item = CallHierarchyItem.from_dict(call["from"])
                from_ranges = [
                    Range(
                        start=Position(r["start"]["line"], r["start"]["character"]),
                        end=Position(r["end"]["line"], r["end"]["character"]),
                    )
                    for r in call.get("fromRanges", [])
                ]
                calls.append(
                    CallHierarchyIncomingCall(
                        from_item=from_item, from_ranges=from_ranges
                    )
                )
            return calls

        except Exception as e:
            logger.error(f"Error in incoming_calls: {e}")
            return []

    def _get_language_id(self, file_path: str) -> str:
        """Get the language ID for a file."""
        ext = Path(file_path).suffix.lower()
        mapping = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescriptreact",
            ".js": "javascript",
            ".jsx": "javascriptreact",
            ".json": "json",
        }
        return mapping.get(ext, "plaintext")


class LSPManager:
    """Manager for multiple LSP clients."""

    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self._clients: dict[LanguageServer, LSPClient] = {}
        self._initialized = False

    async def initialize(self) -> dict[str, bool]:
        """Initialize all available LSP servers.

        Returns:
            Dict mapping server names to initialization status
        """
        results = {}

        # Try to start TypeScript server
        ts_client = LSPClient(server_type=LanguageServer.TYPESCRIPT)
        ts_success = await ts_client.start(self.workspace_root)
        results["typescript"] = ts_success
        if ts_success:
            self._clients[LanguageServer.TYPESCRIPT] = ts_client

        # Try to start Python server
        py_client = LSPClient(server_type=LanguageServer.PYTHON)
        py_success = await py_client.start(self.workspace_root)
        results["python"] = py_success
        if py_success:
            self._clients[LanguageServer.PYTHON] = py_client

        self._initialized = True
        return results

    async def shutdown(self) -> None:
        """Shutdown all LSP clients."""
        for client in self._clients.values():
            await client.stop()
        self._clients.clear()
        self._initialized = False

    def get_client(self, file_path: str) -> LSPClient | None:
        """Get the appropriate LSP client for a file.

        Args:
            file_path: Path to the file

        Returns:
            The appropriate LSP client, or None if not available
        """
        ext = Path(file_path).suffix.lower()

        if ext in {".ts", ".tsx", ".js", ".jsx"}:
            return self._clients.get(LanguageServer.TYPESCRIPT)
        elif ext == ".py":
            return self._clients.get(LanguageServer.PYTHON)

        return None

    @property
    def available_servers(self) -> list[str]:
        """Get list of available server names."""
        return [server.value for server in self._clients.keys()]


# Global LSP manager instance (lazily initialized)
_lsp_manager: LSPManager | None = None


async def get_lsp_manager(workspace_root: str | None = None) -> LSPManager:
    """Get or create the global LSP manager.

    Args:
        workspace_root: Workspace root path (required for first call)

    Returns:
        The LSP manager instance
    """
    global _lsp_manager

    if _lsp_manager is None:
        if workspace_root is None:
            raise ValueError("workspace_root is required for first initialization")
        _lsp_manager = LSPManager(workspace_root)
        await _lsp_manager.initialize()

    return _lsp_manager


async def shutdown_lsp_manager() -> None:
    """Shutdown the global LSP manager."""
    global _lsp_manager
    if _lsp_manager:
        await _lsp_manager.shutdown()
        _lsp_manager = None
