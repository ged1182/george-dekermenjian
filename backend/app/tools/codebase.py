"""Codebase Oracle tools for the Glass Box Portfolio agent.

These tools enable the agent to answer technical questions about the codebase
by structurally understanding the code through file analysis and symbol search.
"""

import os
import re
from pathlib import Path

from pydantic import BaseModel, Field

from ..config import get_settings


class SymbolLocation(BaseModel):
    """Location of a symbol in the codebase."""

    file: str
    line: int
    snippet: str = Field(description="Code snippet around the symbol")


class FindSymbolResult(BaseModel):
    """Result of finding a symbol in the codebase."""

    symbol: str
    locations: list[SymbolLocation]
    total_found: int


class FileContent(BaseModel):
    """Content of a file with metadata."""

    file_path: str
    content: str
    start_line: int
    end_line: int
    total_lines: int
    language: str


class Reference(BaseModel):
    """A reference to a symbol in the codebase."""

    file: str
    line: int
    context: str = Field(description="Line of code containing the reference")


class FindReferencesResult(BaseModel):
    """Result of finding references to a symbol."""

    symbol: str
    references: list[Reference]
    total_found: int


def _get_language(file_path: str) -> str:
    """Determine the programming language from file extension."""
    ext_map = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".json": "json",
        ".md": "markdown",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".css": "css",
        ".html": "html",
    }
    ext = Path(file_path).suffix.lower()
    return ext_map.get(ext, "text")


def _should_skip_path(path: Path) -> bool:
    """Check if a path should be skipped during search."""
    skip_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".next", "dist", "build", ".uv"}
    parts = path.parts
    return any(skip_dir in parts for skip_dir in skip_dirs)


def _get_snippet(lines: list[str], line_num: int, context: int = 2) -> str:
    """Get a code snippet around a specific line."""
    start = max(0, line_num - context - 1)
    end = min(len(lines), line_num + context)
    snippet_lines = []
    for i in range(start, end):
        prefix = ">>> " if i == line_num - 1 else "    "
        snippet_lines.append(f"{prefix}{i + 1}: {lines[i]}")
    return "\n".join(snippet_lines)


def find_symbol(symbol_name: str) -> FindSymbolResult:
    """Find where a function, class, or variable is defined in the codebase.

    Searches for definitions of the given symbol name across all Python
    and TypeScript files in the repository.

    Args:
        symbol_name: The name of the function, class, or variable to find.

    Returns:
        FindSymbolResult with locations where the symbol is defined.
    """
    settings = get_settings()
    root = Path(settings.codebase_root)
    locations: list[SymbolLocation] = []

    # Patterns for finding definitions
    patterns = [
        rf"^\s*def\s+{re.escape(symbol_name)}\s*\(",  # Python function
        rf"^\s*class\s+{re.escape(symbol_name)}\s*[:\(]",  # Python class
        rf"^\s*{re.escape(symbol_name)}\s*=",  # Variable assignment
        rf"^\s*(async\s+)?function\s+{re.escape(symbol_name)}\s*\(",  # JS/TS function
        rf"^\s*(export\s+)?(const|let|var)\s+{re.escape(symbol_name)}\s*=",  # JS/TS variable
        rf"^\s*(export\s+)?class\s+{re.escape(symbol_name)}\s*",  # JS/TS class
        rf"^\s*(export\s+)?interface\s+{re.escape(symbol_name)}\s*",  # TS interface
        rf"^\s*(export\s+)?type\s+{re.escape(symbol_name)}\s*=",  # TS type
    ]

    combined_pattern = re.compile("|".join(patterns), re.IGNORECASE)

    extensions = {".py", ".ts", ".tsx", ".js", ".jsx"}

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix not in extensions:
            continue
        if _should_skip_path(file_path):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            for i, line in enumerate(lines):
                if combined_pattern.search(line):
                    relative_path = str(file_path.relative_to(root))
                    snippet = _get_snippet(lines, i + 1)
                    locations.append(
                        SymbolLocation(
                            file=relative_path,
                            line=i + 1,
                            snippet=snippet,
                        )
                    )
        except (UnicodeDecodeError, PermissionError):
            continue

    return FindSymbolResult(
        symbol=symbol_name,
        locations=locations[:20],  # Limit results
        total_found=len(locations),
    )


def get_file_content(
    file_path: str,
    start_line: int = 1,
    end_line: int | None = None,
) -> FileContent:
    """Get the content of a file in the codebase.

    Retrieves file content with line numbers, useful for understanding
    specific parts of the codebase.

    Args:
        file_path: Relative path to the file from the repository root.
        start_line: First line to retrieve (1-indexed, default: 1).
        end_line: Last line to retrieve (inclusive, default: start_line + max_file_lines).

    Returns:
        FileContent with the requested portion of the file.
    """
    settings = get_settings()
    root = Path(settings.codebase_root)

    # Normalize and validate path
    file_path = file_path.lstrip("/")
    full_path = root / file_path

    # Security: ensure path is within codebase root
    try:
        full_path = full_path.resolve()
        root_resolved = root.resolve()
        if not str(full_path).startswith(str(root_resolved)):
            raise ValueError(f"Path {file_path} is outside the codebase root")
    except (OSError, ValueError) as e:
        return FileContent(
            file_path=file_path,
            content=f"Error: {e}",
            start_line=0,
            end_line=0,
            total_lines=0,
            language="text",
        )

    if not full_path.exists():
        return FileContent(
            file_path=file_path,
            content=f"Error: File not found: {file_path}",
            start_line=0,
            end_line=0,
            total_lines=0,
            language="text",
        )

    try:
        content = full_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        total_lines = len(lines)

        # Apply line range limits
        start_idx = max(0, start_line - 1)
        if end_line is None:
            end_idx = min(total_lines, start_idx + settings.max_file_lines)
        else:
            end_idx = min(total_lines, end_line)

        selected_lines = lines[start_idx:end_idx]

        # Format with line numbers
        numbered_lines = [
            f"{i + start_idx + 1:4d}: {line}"
            for i, line in enumerate(selected_lines)
        ]

        return FileContent(
            file_path=file_path,
            content="\n".join(numbered_lines),
            start_line=start_idx + 1,
            end_line=end_idx,
            total_lines=total_lines,
            language=_get_language(file_path),
        )

    except (UnicodeDecodeError, PermissionError) as e:
        return FileContent(
            file_path=file_path,
            content=f"Error reading file: {e}",
            start_line=0,
            end_line=0,
            total_lines=0,
            language="text",
        )


def find_references(symbol_name: str) -> FindReferencesResult:
    """Find all references to a symbol in the codebase.

    Searches for usages of the given symbol name across all code files,
    helping understand how components are connected.

    Args:
        symbol_name: The name of the symbol to find references for.

    Returns:
        FindReferencesResult with all locations where the symbol is used.
    """
    settings = get_settings()
    root = Path(settings.codebase_root)
    references: list[Reference] = []

    # Pattern to find symbol usage (word boundary match)
    pattern = re.compile(rf"\b{re.escape(symbol_name)}\b")

    extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".yaml", ".yml", ".toml"}

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix not in extensions:
            continue
        if _should_skip_path(file_path):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            for i, line in enumerate(lines):
                if pattern.search(line):
                    relative_path = str(file_path.relative_to(root))
                    references.append(
                        Reference(
                            file=relative_path,
                            line=i + 1,
                            context=line.strip()[:200],  # Limit context length
                        )
                    )
        except (UnicodeDecodeError, PermissionError):
            continue

    return FindReferencesResult(
        symbol=symbol_name,
        references=references[:50],  # Limit results
        total_found=len(references),
    )
