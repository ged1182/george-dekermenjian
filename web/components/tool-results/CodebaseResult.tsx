"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, FileCode, Search, Link2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { CodeBlock, CodeBlockCopyButton } from "@/components/ai-elements/code-block";
import type { BundledLanguage } from "shiki";
import type { FindSymbolOutput, FileContentOutput, FindReferencesOutput } from "./types";

// Map file extensions to Shiki languages
function getLanguageFromPath(filePath: string): BundledLanguage {
  const ext = filePath.split(".").pop()?.toLowerCase() || "";
  // Handle files without extensions (Makefile, Dockerfile)
  const fileName = filePath.split("/").pop()?.toLowerCase() || "";
  if (fileName === "makefile") return "makefile";
  if (fileName === "dockerfile") return "dockerfile";
  if (fileName === "docker-compose.yml" || fileName === "docker-compose.yaml") return "yaml";

  const languageMap: Record<string, BundledLanguage> = {
    ts: "typescript",
    tsx: "tsx",
    js: "javascript",
    jsx: "jsx",
    py: "python",
    rs: "rust",
    go: "go",
    java: "java",
    css: "css",
    scss: "scss",
    html: "html",
    json: "json",
    yaml: "yaml",
    yml: "yaml",
    md: "markdown",
    mdx: "mdx",
    sh: "bash",
    bash: "bash",
    zsh: "bash",
    sql: "sql",
    graphql: "graphql",
    toml: "toml",
    xml: "xml",
    vue: "vue",
    svelte: "svelte",
  };
  return languageMap[ext] || "javascript";
}

// Map language string (from backend) to Shiki BundledLanguage
function normalizeLanguage(lang: string): BundledLanguage {
  const langLower = lang.toLowerCase();
  const languageMap: Record<string, BundledLanguage> = {
    typescript: "typescript",
    javascript: "javascript",
    python: "python",
    rust: "rust",
    go: "go",
    java: "java",
    css: "css",
    html: "html",
    json: "json",
    yaml: "yaml",
    markdown: "markdown",
    dockerfile: "dockerfile",
    makefile: "makefile",
    bash: "bash",
    shell: "bash",
    sql: "sql",
    tsx: "tsx",
    jsx: "jsx",
  };
  return languageMap[langLower] || "javascript";
}

// Strip line number prefixes from backend content (e.g., "1: code" -> "code")
function stripLineNumbers(content: string): string {
  return content
    .split("\n")
    .map((line) => {
      // Match patterns like "1: ", "12:\t", "123: " at the start of lines
      const match = line.match(/^\s*\d+[:\t]\s?/);
      return match ? line.slice(match[0].length) : line;
    })
    .join("\n");
}

interface CodebaseResultProps {
  toolName: string;
  data: unknown;
  toolCallId: string;
}

export function CodebaseResult({ toolName, data }: CodebaseResultProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Handle specific codebase tool outputs with better formatting
  if (toolName === "find_symbol" && isValidFindSymbolOutput(data)) {
    return <SymbolResult data={data} />;
  }

  if (toolName === "get_file_content" && isValidFileContentOutput(data)) {
    return <FileContentResult data={data} />;
  }

  if (toolName === "find_references" && isValidFindReferencesOutput(data)) {
    return <ReferencesResult data={data} />;
  }

  // Fallback: render as collapsible JSON
  return (
    <div className="bg-card text-card-foreground my-4 overflow-hidden rounded-lg border shadow-sm">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="hover:bg-muted/50 flex w-full items-center justify-between px-4 py-3 text-left transition-colors"
      >
        <div className="flex items-center gap-2">
          <FileCode className="text-muted-foreground size-4" />
          <span className="text-sm font-medium">{formatToolName(toolName)} Result</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="text-muted-foreground size-4" />
        ) : (
          <ChevronDown className="text-muted-foreground size-4" />
        )}
      </button>
      {isExpanded && (
        <div className="border-t">
          <CodeBlock
            code={JSON.stringify(data, null, 2)}
            language="json"
            className="max-h-80 border-0 rounded-none"
          >
            <CodeBlockCopyButton />
          </CodeBlock>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Symbol Result Component
// =============================================================================

function SymbolResult({ data }: { data: FindSymbolOutput }) {
  const [isExpanded, setIsExpanded] = useState(data.total_found <= 3);

  return (
    <div className="bg-card text-card-foreground my-4 overflow-hidden rounded-lg border shadow-sm">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="hover:bg-muted/50 flex w-full items-center justify-between px-4 py-3 text-left transition-colors"
      >
        <div className="flex items-center gap-2">
          <Search className="text-primary size-4" />
          <span className="text-sm font-medium">Found &quot;{data.symbol}&quot;</span>
          <Badge variant="secondary" className="text-xs">
            {data.total_found} location{data.total_found !== 1 ? "s" : ""}
          </Badge>
        </div>
        {isExpanded ? (
          <ChevronUp className="text-muted-foreground size-4" />
        ) : (
          <ChevronDown className="text-muted-foreground size-4" />
        )}
      </button>
      {isExpanded && (
        <div className="mt-0 space-y-3 border-t px-4 pb-4 pt-3">
          {data.locations.map((loc, idx) => (
            <div key={`${loc.file}-${loc.line}-${idx}`}>
              <div className="text-muted-foreground mb-1 flex items-center gap-2 text-xs">
                <FileCode className="size-3" />
                <span className="font-mono">
                  {loc.file}:{loc.line}
                </span>
              </div>
              <CodeBlock
                code={loc.snippet}
                language={getLanguageFromPath(loc.file)}
                className="text-xs"
              >
                <CodeBlockCopyButton />
              </CodeBlock>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// File Content Result Component
// =============================================================================

function FileContentResult({ data }: { data: FileContentOutput }) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="bg-card text-card-foreground my-4 overflow-hidden rounded-lg border shadow-sm">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="hover:bg-muted/50 flex w-full items-center justify-between px-4 py-3 text-left transition-colors"
      >
        <div className="flex items-center gap-2">
          <FileCode className="text-primary size-4" />
          <span className="font-mono text-sm font-medium">{data.file_path}</span>
          <Badge variant="outline" className="text-xs">
            {data.language}
          </Badge>
          <span className="text-muted-foreground text-xs">
            Lines {data.start_line}-{data.end_line} of {data.total_lines}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="text-muted-foreground size-4" />
        ) : (
          <ChevronDown className="text-muted-foreground size-4" />
        )}
      </button>
      {isExpanded && (
        <div className="border-t">
          <CodeBlock
            code={stripLineNumbers(data.content)}
            language={normalizeLanguage(data.language)}
            showLineNumbers
            className="max-h-96 border-0 rounded-none"
          >
            <CodeBlockCopyButton />
          </CodeBlock>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// References Result Component
// =============================================================================

function ReferencesResult({ data }: { data: FindReferencesOutput }) {
  const [isExpanded, setIsExpanded] = useState(data.total_found <= 5);

  return (
    <div className="bg-card text-card-foreground my-4 overflow-hidden rounded-lg border shadow-sm">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="hover:bg-muted/50 flex w-full items-center justify-between px-4 py-3 text-left transition-colors"
      >
        <div className="flex items-center gap-2">
          <Link2 className="text-primary size-4" />
          <span className="text-sm font-medium">References to &quot;{data.symbol}&quot;</span>
          <Badge variant="secondary" className="text-xs">
            {data.total_found} reference{data.total_found !== 1 ? "s" : ""}
          </Badge>
        </div>
        {isExpanded ? (
          <ChevronUp className="text-muted-foreground size-4" />
        ) : (
          <ChevronDown className="text-muted-foreground size-4" />
        )}
      </button>
      {isExpanded && (
        <div className="bg-muted/30 mt-0 space-y-1 border-t px-4 pb-4">
          {data.references.map((ref, idx) => (
            <div
              key={`${ref.file}-${ref.line}-${idx}`}
              className="mt-2 flex items-start gap-2 text-xs"
            >
              <span className="text-muted-foreground font-mono whitespace-nowrap">
                {ref.file}:{ref.line}
              </span>
              <code className="text-foreground flex-1 truncate">{ref.context}</code>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Type Guards
// =============================================================================

function isValidFindSymbolOutput(data: unknown): data is FindSymbolOutput {
  return (
    typeof data === "object" &&
    data !== null &&
    "symbol" in data &&
    "locations" in data &&
    Array.isArray((data as FindSymbolOutput).locations)
  );
}

function isValidFileContentOutput(data: unknown): data is FileContentOutput {
  return (
    typeof data === "object" &&
    data !== null &&
    "file_path" in data &&
    "content" in data &&
    "language" in data
  );
}

function isValidFindReferencesOutput(data: unknown): data is FindReferencesOutput {
  return (
    typeof data === "object" &&
    data !== null &&
    "symbol" in data &&
    "references" in data &&
    Array.isArray((data as FindReferencesOutput).references)
  );
}

function formatToolName(name: string): string {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
