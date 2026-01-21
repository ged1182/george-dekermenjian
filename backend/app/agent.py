"""Pydantic-AI agent for the Glass Box Portfolio.

This module defines the portfolio assistant agent with tools for answering
questions about George's experience, system architecture, and the codebase.
"""

import functools
import inspect
import time
from typing import Any, Callable, TypeVar

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModelSettings

from .config import get_settings
from .schemas.brain_log import (
    LogEntryStatus,
    get_brain_log_collector,
)
from .tools.codebase import (
    clone_codebase,
    get_file_content,
    get_folder_tree,
)
from .tools.experience import (
    get_education,
    get_professional_experience,
    get_projects,
    get_skills,
)
from .tools.semantic import (
    find_all_references,
    get_callers,
    get_document_symbols,
    get_type_info,
    go_to_definition,
)

T = TypeVar("T")


def _get_result_preview(result: Any, max_len: int = 200) -> str:
    """Get a preview string from a tool result."""
    if result is None:
        return "None"
    if hasattr(result, "model_dump"):
        # Pydantic model - show a summary
        data = result.model_dump()
        preview = str(data)
    else:
        preview = str(result)
    if len(preview) > max_len:
        return preview[:max_len] + "..."
    return preview


def logged_tool(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log tool calls to the BrainLogCollector.

    Emits separate entries for tool invocation and tool result.
    Works with both sync and async functions.
    """

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        collector = get_brain_log_collector()
        tool_name = func.__name__

        # Log tool invocation (pending)
        start_time = time.time()
        if collector:
            collector.add_tool_call_pending(tool_name, kwargs or {})

        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            # Log tool result (separate entry)
            if collector:
                collector.add_tool_result_entry(
                    tool_name=tool_name,
                    status=LogEntryStatus.SUCCESS,
                    result_preview=_get_result_preview(result),
                    duration_ms=duration_ms,
                )
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log tool failure (separate entry)
            if collector:
                collector.add_tool_result_entry(
                    tool_name=tool_name,
                    status=LogEntryStatus.FAILURE,
                    error=str(e),
                    duration_ms=duration_ms,
                )
            raise

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        collector = get_brain_log_collector()
        tool_name = func.__name__

        # Log tool invocation (pending)
        start_time = time.time()
        if collector:
            collector.add_tool_call_pending(tool_name, kwargs or {})

        try:
            result = await func(*args, **kwargs)  # type: ignore[misc]
            duration_ms = (time.time() - start_time) * 1000

            # Log tool result (separate entry)
            if collector:
                collector.add_tool_result_entry(
                    tool_name=tool_name,
                    status=LogEntryStatus.SUCCESS,
                    result_preview=_get_result_preview(result),
                    duration_ms=duration_ms,
                )
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log tool failure (separate entry)
            if collector:
                collector.add_tool_result_entry(
                    tool_name=tool_name,
                    status=LogEntryStatus.FAILURE,
                    error=str(e),
                    duration_ms=duration_ms,
                )
            raise

    if inspect.iscoroutinefunction(func):
        return async_wrapper  # type: ignore
    return sync_wrapper  # type: ignore


SYSTEM_PROMPT = """
You are an AI assistant for the "Glass Box Portfolio" website.

STOP! Before calling any tool, you MUST first output a text message explaining what you will do.
Example: "I'll explore the Glass Box architecture by cloning the codebase and examining its structure."

## TOOL SELECTION RULES

For questions about ARCHITECTURE, CODE, or HOW THINGS WORK:
- ONLY use: clone_codebase, get_folder_tree, get_file_content
- NEVER use: get_projects, get_skills, get_professional_experience

For questions about GEORGE'S BACKGROUND or EXPERIENCE:
- ONLY use: get_projects, get_skills, get_professional_experience, get_education
- NEVER use: clone_codebase, get_folder_tree, get_file_content

"Glass Box" refers to THIS portfolio website's codebase.

## About George

George is a Director of Data & AI specializing in production AI systems with
full audit trails for regulated industries. He is a hybrid technical executive
who builds GenAI workflows that satisfy compliance requirements (AIFMD, GDPR)
while delivering measurable ROI. His track record includes $1.2M digital
transformations, 99.5% latency reductions, and AI document classification
systems. He is a former mathematics professor who translates complex systems
into business outcomes.

## About This Portfolio

This is the Glass Box Portfolio - a production-grade demonstration of
explainable, agentic systems. The key differentiator is transparent visibility
into how AI systems actually behave:

- **Opaque Mode**: Clean, minimalist interface for end users
- **Glass Box Mode**: Shows the Brain Log with real-time agent reasoning,
  tool selection, schema validation, and performance metrics

The portfolio is built with:
- Frontend: Next.js 16 with React 19, Tailwind CSS v4, shadcn/ui
- Backend: FastAPI with pydantic-ai agents
- LLM: Gemini 2.0 Flash via Google AI
- Deployment: Vercel (frontend) + Cloud Run (backend)

## Tool Selection - IMPORTANT!

**Use Profile Tools ONLY for questions about George personally:**
- "Tell me about your experience" → `get_professional_experience`
- "What are your skills?" → `get_skills`
- "What projects have you worked on?" → `get_projects`
- "What is your education?" → `get_education`

**Use Codebase Tools for architecture/code/system questions:**
- "Explain the architecture" → codebase tools
- "How does X work?" → codebase tools
- "Show me the code for Y" → codebase tools

**DO NOT mix these!** Architecture questions should NEVER call profile tools.

## Codebase Exploration Tools

- `clone_codebase` - Clone the repo (call this FIRST for any codebase question)
- `get_folder_tree` - See directory structure
- `get_file_content` - Read specific files

## Semantic Analysis Tools (LSP-powered)

- `go_to_definition` - Find where a symbol is defined
- `find_all_references` - Find all usages of a symbol
- `get_type_info` - Get type signatures and documentation
- `get_document_symbols` - See structure of a file
- `get_callers` - Find what calls a function

## How to Respond

**ALWAYS explain your plan before making tool calls.** For example:
"I'll explore the Glass Box architecture by first cloning the codebase, then examining the folder structure."

Then make the tool calls.

## Architecture Questions

For architecture/codebase questions, follow this sequence:
1. Briefly explain what you'll do
2. Call `clone_codebase`
3. Call `get_folder_tree` to see the structure
4. Call `get_file_content` on key files
5. Summarize your findings

Never refuse to answer architecture questions - use the tools to discover the answer!

## Response Guidelines

- Be concise but thorough. Provide specific details when available.
- **IMPORTANT**: Do NOT repeat or echo tool output in your response text. The UI
  automatically displays tool results in a rich format. Instead, provide brief
  commentary, explanations, or analysis of the tool output.
- When showing code, let the tool result speak for itself. Add value by explaining
  what the code does, pointing out key sections, or answering the user's question.
"""


def create_agent() -> Agent:
    """Create and configure the portfolio assistant agent."""
    settings = get_settings()

    # Wrap all tools with logging
    logged_tools = [
        # Experience tools
        logged_tool(get_professional_experience),
        logged_tool(get_skills),
        logged_tool(get_projects),
        logged_tool(get_education),
        # Codebase tools
        logged_tool(clone_codebase),
        logged_tool(get_folder_tree),
        logged_tool(get_file_content),
        # Semantic (LSP-powered) tools
        logged_tool(go_to_definition),
        logged_tool(find_all_references),
        logged_tool(get_type_info),
        logged_tool(get_document_symbols),
        logged_tool(get_callers),
    ]

    # Enable thinking/reasoning with Google models
    model_settings = GoogleModelSettings(
        google_thinking_config={"include_thoughts": True}
    )

    agent = Agent(
        model=settings.model_name,
        system_prompt=SYSTEM_PROMPT,
        tools=logged_tools,
        model_settings=model_settings,
    )

    return agent


# Create a singleton agent instance
portfolio_agent = create_agent()
