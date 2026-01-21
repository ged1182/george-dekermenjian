"""LSP-powered semantic code analysis tools.

These tools use Language Server Protocol (LSP) to provide accurate, semantic
code intelligence - going beyond regex pattern matching to true understanding
of code structure, types, and relationships.
"""

import asyncio
import re
from pathlib import Path

from pydantic import BaseModel, Field

from ..config import get_settings
from .lsp_client import get_code_manager


class DefinitionLocation(BaseModel):
    """Location where a symbol is defined."""

    file: str = Field(description="Relative path to the file")
    line: int = Field(description="Line number (1-indexed)")
    character: int = Field(description="Character position")
    preview: str = Field(description="Preview of the code at this location")


class DefinitionResult(BaseModel):
    """Result of a go-to-definition query."""

    symbol: str = Field(description="The symbol that was queried")
    source_file: str = Field(description="File where the query was made")
    source_line: int = Field(description="Line where the query was made")
    definitions: list[DefinitionLocation] = Field(description="Definition locations")
    success: bool = Field(description="Whether LSP query succeeded")
    error: str | None = Field(default=None, description="Error message if failed")


class ReferenceLocation(BaseModel):
    """Location where a symbol is referenced."""

    file: str = Field(description="Relative path to the file")
    line: int = Field(description="Line number (1-indexed)")
    character: int = Field(description="Character position")
    context: str = Field(description="Line of code containing the reference")


class ReferencesResult(BaseModel):
    """Result of a find-references query."""

    symbol: str = Field(description="The symbol that was queried")
    source_file: str = Field(description="File where the query was made")
    references: list[ReferenceLocation] = Field(description="Reference locations")
    total_found: int = Field(description="Total number of references found")
    success: bool = Field(description="Whether LSP query succeeded")
    error: str | None = Field(default=None, description="Error message if failed")


class TypeInfo(BaseModel):
    """Type information for a symbol."""

    symbol: str = Field(description="The symbol that was queried")
    file: str = Field(description="File where the query was made")
    line: int = Field(description="Line number")
    type_signature: str = Field(description="Type signature or documentation")
    success: bool = Field(description="Whether LSP query succeeded")
    error: str | None = Field(default=None, description="Error message if failed")


class DocumentSymbol(BaseModel):
    """A symbol in a document."""

    name: str = Field(description="Symbol name")
    kind: str = Field(description="Symbol kind (function, class, variable, etc.)")
    line: int = Field(description="Line number (1-indexed)")
    container: str | None = Field(default=None, description="Container symbol name")


class DocumentSymbolsResult(BaseModel):
    """Result of document symbols query."""

    file: str = Field(description="File that was analyzed")
    symbols: list[DocumentSymbol] = Field(description="Symbols in the document")
    success: bool = Field(description="Whether LSP query succeeded")
    error: str | None = Field(default=None, description="Error message if failed")


class CallerInfo(BaseModel):
    """Information about a caller of a function."""

    name: str = Field(description="Name of the calling function")
    file: str = Field(description="File containing the caller")
    line: int = Field(description="Line number of the call")


class CallHierarchyResult(BaseModel):
    """Result of call hierarchy query."""

    function_name: str = Field(description="The function that was queried")
    file: str = Field(description="File containing the function")
    callers: list[CallerInfo] = Field(description="Functions that call this function")
    success: bool = Field(description="Whether LSP query succeeded")
    error: str | None = Field(default=None, description="Error message if failed")


# Symbol kind mapping from LSP spec
SYMBOL_KINDS = {
    1: "File",
    2: "Module",
    3: "Namespace",
    4: "Package",
    5: "Class",
    6: "Method",
    7: "Property",
    8: "Field",
    9: "Constructor",
    10: "Enum",
    11: "Interface",
    12: "Function",
    13: "Variable",
    14: "Constant",
    15: "String",
    16: "Number",
    17: "Boolean",
    18: "Array",
    19: "Object",
    20: "Key",
    21: "Null",
    22: "EnumMember",
    23: "Struct",
    24: "Event",
    25: "Operator",
    26: "TypeParameter",
}


def _uri_to_path(uri: str, root: Path) -> str:
    """Convert a file:// URI to a relative path."""
    if uri.startswith("file://"):
        path = uri[7:]
        try:
            return str(Path(path).relative_to(root))
        except ValueError:
            return path
    return uri


def _get_line_content(file_path: Path, line_num: int) -> str:
    """Get the content of a specific line from a file."""
    try:
        lines = file_path.read_text().splitlines()
        if 0 <= line_num < len(lines):
            return lines[line_num].strip()
    except Exception:
        pass
    return ""


def _find_symbol_in_file(file_path: str, symbol_name: str) -> tuple[int, int] | None:
    """Find the position of a symbol in a file using regex.

    Returns (line, character) 0-indexed, or None if not found.
    """
    settings = get_settings()
    root = Path(settings.codebase_root)
    full_path = root / file_path

    if not full_path.exists():
        return None

    try:
        content = full_path.read_text()
        lines = content.splitlines()

        # Pattern to find the symbol as a word
        pattern = re.compile(rf"\b{re.escape(symbol_name)}\b")

        for line_num, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                return (line_num, match.start())
    except Exception:
        pass

    return None


async def go_to_definition(
    file_path: str,
    symbol_name: str,
    line: int | None = None,
    character: int | None = None,
) -> DefinitionResult:
    """Find the definition of a symbol using LSP (semantic analysis).

    USE THIS TOOL when you need PRECISE definition locations with type awareness.
    This uses Language Server Protocol for accurate semantic analysis, unlike
    the regex-based find_symbol which can have false positives.

    Args:
        file_path: Relative path to the file containing the symbol
        symbol_name: Name of the symbol to find the definition for
        line: Line number (1-indexed). If not provided, will search for the symbol.
        character: Character position. If not provided, will search for the symbol.

    Returns:
        DefinitionResult with the definition locations and type info.
    """
    print(f"[TOOL] go_to_definition called: {symbol_name} in {file_path}")
    settings = get_settings()
    root = Path(settings.codebase_root)
    full_path = root / file_path

    # Validate path
    if not full_path.exists():
        return DefinitionResult(
            symbol=symbol_name,
            source_file=file_path,
            source_line=line or 0,
            definitions=[],
            success=False,
            error=f"File not found: {file_path}",
        )

    # If line/character not provided, find the symbol in the file
    if line is None or character is None:
        pos = _find_symbol_in_file(file_path, symbol_name)
        if pos is None:
            return DefinitionResult(
                symbol=symbol_name,
                source_file=file_path,
                source_line=0,
                definitions=[],
                success=False,
                error=f"Symbol '{symbol_name}' not found in {file_path}",
            )
        line, character = pos[0] + 1, pos[1]  # Convert to 1-indexed

    try:
        manager = await get_code_manager(str(root))
        client = manager.get_client(str(full_path))

        if client is None:
            return DefinitionResult(
                symbol=symbol_name,
                source_file=file_path,
                source_line=line,
                definitions=[],
                success=False,
                error=f"No LSP server available for {Path(file_path).suffix} files",
            )

        # LSP uses 0-indexed positions
        locations = await client.go_to_definition(str(full_path), line - 1, character)

        definitions = []
        for loc in locations:
            rel_path = _uri_to_path(loc.uri, root)
            def_line = loc.range.start.line + 1  # Convert to 1-indexed

            # Get preview
            loc_full_path = (
                root / rel_path if not Path(rel_path).is_absolute() else Path(rel_path)
            )
            preview = _get_line_content(loc_full_path, loc.range.start.line)

            definitions.append(
                DefinitionLocation(
                    file=rel_path,
                    line=def_line,
                    character=loc.range.start.character,
                    preview=preview,
                )
            )

        return DefinitionResult(
            symbol=symbol_name,
            source_file=file_path,
            source_line=line,
            definitions=definitions,
            success=True,
        )

    except Exception as e:
        return DefinitionResult(
            symbol=symbol_name,
            source_file=file_path,
            source_line=line,
            definitions=[],
            success=False,
            error=str(e),
        )


async def find_all_references(
    file_path: str,
    symbol_name: str,
    line: int | None = None,
    character: int | None = None,
) -> ReferencesResult:
    """Find ALL usages of a symbol using LSP (semantic analysis).

    USE THIS TOOL when you need ACCURATE reference finding that understands
    scoping, imports, and type information. Unlike regex-based search, this
    won't match unrelated symbols that happen to have the same name.

    Args:
        file_path: Relative path to the file containing the symbol
        symbol_name: Name of the symbol to find references for
        line: Line number (1-indexed). If not provided, will search for the symbol.
        character: Character position. If not provided, will search for the symbol.

    Returns:
        ReferencesResult with all reference locations.
    """
    print(f"[TOOL] find_all_references called: {symbol_name} in {file_path}")
    settings = get_settings()
    root = Path(settings.codebase_root)
    full_path = root / file_path

    # Validate path
    if not full_path.exists():
        return ReferencesResult(
            symbol=symbol_name,
            source_file=file_path,
            references=[],
            total_found=0,
            success=False,
            error=f"File not found: {file_path}",
        )

    # If line/character not provided, find the symbol in the file
    if line is None or character is None:
        pos = _find_symbol_in_file(file_path, symbol_name)
        if pos is None:
            return ReferencesResult(
                symbol=symbol_name,
                source_file=file_path,
                references=[],
                total_found=0,
                success=False,
                error=f"Symbol '{symbol_name}' not found in {file_path}",
            )
        line, character = pos[0] + 1, pos[1]

    try:
        manager = await get_code_manager(str(root))
        client = manager.get_client(str(full_path))

        if client is None:
            return ReferencesResult(
                symbol=symbol_name,
                source_file=file_path,
                references=[],
                total_found=0,
                success=False,
                error=f"No LSP server available for {Path(file_path).suffix} files",
            )

        # LSP uses 0-indexed positions
        locations = await client.find_references(str(full_path), line - 1, character)

        references = []
        for loc in locations:
            rel_path = _uri_to_path(loc.uri, root)
            ref_line = loc.range.start.line + 1

            # Get context
            loc_full_path = (
                root / rel_path if not Path(rel_path).is_absolute() else Path(rel_path)
            )
            context = _get_line_content(loc_full_path, loc.range.start.line)

            references.append(
                ReferenceLocation(
                    file=rel_path,
                    line=ref_line,
                    character=loc.range.start.character,
                    context=context[:200],
                )
            )

        return ReferencesResult(
            symbol=symbol_name,
            source_file=file_path,
            references=references[:100],  # Limit results
            total_found=len(locations),
            success=True,
        )

    except Exception as e:
        return ReferencesResult(
            symbol=symbol_name,
            source_file=file_path,
            references=[],
            total_found=0,
            success=False,
            error=str(e),
        )


async def get_type_info(
    file_path: str,
    symbol_name: str,
    line: int | None = None,
    character: int | None = None,
) -> TypeInfo:
    """Get type information and documentation for a symbol.

    USE THIS TOOL when you need to understand:
    - What type a variable or parameter is
    - Function signatures and return types
    - Interface/class definitions
    - Documentation for a symbol

    Args:
        file_path: Relative path to the file containing the symbol
        symbol_name: Name of the symbol to get type info for
        line: Line number (1-indexed). If not provided, will search for the symbol.
        character: Character position. If not provided, will search for the symbol.

    Returns:
        TypeInfo with the type signature and documentation.
    """
    print(f"[TOOL] get_type_info called: {symbol_name} in {file_path}")
    settings = get_settings()
    root = Path(settings.codebase_root)
    full_path = root / file_path

    # Validate path
    if not full_path.exists():
        return TypeInfo(
            symbol=symbol_name,
            file=file_path,
            line=line or 0,
            type_signature="",
            success=False,
            error=f"File not found: {file_path}",
        )

    # If line/character not provided, find the symbol in the file
    if line is None or character is None:
        pos = _find_symbol_in_file(file_path, symbol_name)
        if pos is None:
            return TypeInfo(
                symbol=symbol_name,
                file=file_path,
                line=0,
                type_signature="",
                success=False,
                error=f"Symbol '{symbol_name}' not found in {file_path}",
            )
        line, character = pos[0] + 1, pos[1]

    try:
        manager = await get_code_manager(str(root))
        client = manager.get_client(str(full_path))

        if client is None:
            return TypeInfo(
                symbol=symbol_name,
                file=file_path,
                line=line,
                type_signature="",
                success=False,
                error=f"No LSP server available for {Path(file_path).suffix} files",
            )

        # LSP uses 0-indexed positions
        hover = await client.hover(str(full_path), line - 1, character)

        if hover is None:
            return TypeInfo(
                symbol=symbol_name,
                file=file_path,
                line=line,
                type_signature="",
                success=False,
                error="No type information available",
            )

        return TypeInfo(
            symbol=symbol_name,
            file=file_path,
            line=line,
            type_signature=hover.contents,
            success=True,
        )

    except Exception as e:
        return TypeInfo(
            symbol=symbol_name,
            file=file_path,
            line=line,
            type_signature="",
            success=False,
            error=str(e),
        )


async def get_document_symbols(file_path: str) -> DocumentSymbolsResult:
    """Get all symbols (functions, classes, variables) defined in a file.

    USE THIS TOOL when you want to:
    - See the structure of a file
    - Find all functions/classes in a module
    - Get an overview of what a file contains

    Args:
        file_path: Relative path to the file to analyze

    Returns:
        DocumentSymbolsResult with all symbols in the file.
    """
    print(f"[TOOL] get_document_symbols called: {file_path}")
    settings = get_settings()
    root = Path(settings.codebase_root)
    full_path = root / file_path

    # Validate path
    if not full_path.exists():
        return DocumentSymbolsResult(
            file=file_path,
            symbols=[],
            success=False,
            error=f"File not found: {file_path}",
        )

    try:
        manager = await get_code_manager(str(root))
        client = manager.get_client(str(full_path))

        if client is None:
            return DocumentSymbolsResult(
                file=file_path,
                symbols=[],
                success=False,
                error=f"No LSP server available for {Path(file_path).suffix} files",
            )

        lsp_symbols = await client.document_symbols(str(full_path))

        symbols = []
        for sym in lsp_symbols:
            kind_name = SYMBOL_KINDS.get(sym.kind, f"Unknown({sym.kind})")
            symbols.append(
                DocumentSymbol(
                    name=sym.name,
                    kind=kind_name,
                    line=sym.location.range.start.line + 1,  # Convert to 1-indexed
                    container=sym.container_name,
                )
            )

        return DocumentSymbolsResult(
            file=file_path,
            symbols=symbols,
            success=True,
        )

    except Exception as e:
        return DocumentSymbolsResult(
            file=file_path,
            symbols=[],
            success=False,
            error=str(e),
        )


async def get_callers(
    file_path: str,
    function_name: str,
    line: int | None = None,
    character: int | None = None,
) -> CallHierarchyResult:
    """Find all functions that call a given function.

    USE THIS TOOL when you want to understand:
    - Who calls this function?
    - What's the call chain leading to this code?
    - Impact analysis for changes

    Args:
        file_path: Relative path to the file containing the function
        function_name: Name of the function to find callers for
        line: Line number (1-indexed). If not provided, will search for the symbol.
        character: Character position. If not provided, will search for the symbol.

    Returns:
        CallHierarchyResult with all callers of the function.
    """
    print(f"[TOOL] get_callers called: {function_name} in {file_path}")
    settings = get_settings()
    root = Path(settings.codebase_root)
    full_path = root / file_path

    # Validate path
    if not full_path.exists():
        return CallHierarchyResult(
            function_name=function_name,
            file=file_path,
            callers=[],
            success=False,
            error=f"File not found: {file_path}",
        )

    # If line/character not provided, find the symbol in the file
    if line is None or character is None:
        pos = _find_symbol_in_file(file_path, function_name)
        if pos is None:
            return CallHierarchyResult(
                function_name=function_name,
                file=file_path,
                callers=[],
                success=False,
                error=f"Function '{function_name}' not found in {file_path}",
            )
        line, character = pos[0] + 1, pos[1]

    try:
        manager = await get_code_manager(str(root))
        client = manager.get_client(str(full_path))

        if client is None:
            return CallHierarchyResult(
                function_name=function_name,
                file=file_path,
                callers=[],
                success=False,
                error=f"No LSP server available for {Path(file_path).suffix} files",
            )

        # First, prepare the call hierarchy
        items = await client.prepare_call_hierarchy(str(full_path), line - 1, character)

        if not items:
            return CallHierarchyResult(
                function_name=function_name,
                file=file_path,
                callers=[],
                success=False,
                error="Could not prepare call hierarchy (function not found or not supported)",
            )

        # Get incoming calls for the first item
        incoming = await client.incoming_calls(items[0])

        callers = []
        for call in incoming:
            rel_path = _uri_to_path(call.from_item.uri, root)
            callers.append(
                CallerInfo(
                    name=call.from_item.name,
                    file=rel_path,
                    line=call.from_item.range.start.line + 1,
                )
            )

        return CallHierarchyResult(
            function_name=function_name,
            file=file_path,
            callers=callers,
            success=True,
        )

    except Exception as e:
        return CallHierarchyResult(
            function_name=function_name,
            file=file_path,
            callers=[],
            success=False,
            error=str(e),
        )


# Synchronous wrappers for pydantic-ai tools
# pydantic-ai handles async tools, but we provide sync wrappers for flexibility


def go_to_definition_sync(
    file_path: str,
    symbol_name: str,
    line: int | None = None,
    character: int | None = None,
) -> DefinitionResult:
    """Synchronous wrapper for go_to_definition."""
    return asyncio.get_event_loop().run_until_complete(
        go_to_definition(file_path, symbol_name, line, character)
    )


def find_all_references_sync(
    file_path: str,
    symbol_name: str,
    line: int | None = None,
    character: int | None = None,
) -> ReferencesResult:
    """Synchronous wrapper for find_all_references."""
    return asyncio.get_event_loop().run_until_complete(
        find_all_references(file_path, symbol_name, line, character)
    )


def get_type_info_sync(
    file_path: str,
    symbol_name: str,
    line: int | None = None,
    character: int | None = None,
) -> TypeInfo:
    """Synchronous wrapper for get_type_info."""
    return asyncio.get_event_loop().run_until_complete(
        get_type_info(file_path, symbol_name, line, character)
    )


def get_document_symbols_sync(file_path: str) -> DocumentSymbolsResult:
    """Synchronous wrapper for get_document_symbols."""
    return asyncio.get_event_loop().run_until_complete(get_document_symbols(file_path))


def get_callers_sync(
    file_path: str,
    function_name: str,
    line: int | None = None,
    character: int | None = None,
) -> CallHierarchyResult:
    """Synchronous wrapper for get_callers."""
    return asyncio.get_event_loop().run_until_complete(
        get_callers(file_path, function_name, line, character)
    )
