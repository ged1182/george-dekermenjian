"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, type UIMessage } from "ai";
import { useState, useCallback, useMemo } from "react";
import { nanoid } from "nanoid";

import { cn } from "@/lib/utils";
import { CHAT_ENDPOINT, parseBrainLogFromData } from "@/lib/api";
import { useGlassBox } from "@/components/glass-box";
import { ToolResultRenderer } from "@/components/tool-results";

// AI Elements
import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message";
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputFooter,
  PromptInputSubmit,
} from "@/components/ai-elements/prompt-input";
import { Loader } from "@/components/ai-elements/loader";
import {
  Reasoning,
  ReasoningTrigger,
  ReasoningContent,
} from "@/components/ai-elements/reasoning";
// Suggestions moved to quick start grid above input

// Icons
import { BotIcon, UserIcon } from "lucide-react";

// ============================================================================
// Types
// ============================================================================

interface ChatInterfaceProps {
  className?: string;
}

// Quick start suggestions for the chat
const STARTER_SUGGESTIONS = [
  "Tell me about your experience",
  "What's your tech stack?",
  "Explain the Glass Box architecture",
  "What projects have you worked on?",
];

// Helper to extract text content from UIMessage parts
function getMessageText(message: UIMessage): string {
  return message.parts
    .filter((p): p is { type: "text"; text: string } => p.type === "text")
    .map((p) => p.text)
    .join("");
}

// ============================================================================
// ChatInterface Component
// ============================================================================

export function ChatInterface({ className }: ChatInterfaceProps) {
  const { addEntry, addEntries, isEnabled } = useGlassBox();
  const [input, setInput] = useState("");

  // Create transport that sends UI Messages format (required by VercelAIAdapter)
  const transport = useMemo(
    () => new DefaultChatTransport({ api: CHAT_ENDPOINT }),
    []
  );

  // Type assertion needed because @ai-sdk/react types have augmentation conflicts
  // The runtime API supports transport option per ChatInit interface in 'ai' package
  const chatHelpers = useChat({
    transport,
    id: "glass-box-chat",
    onData: (dataPart: unknown) => {
      // Parse Brain Log entries from the stream
      // AI SDK 5 sends individual data parts, not arrays
      if (dataPart) {
        const entries = parseBrainLogFromData([dataPart]);
        if (entries.length > 0) {
          addEntries(entries);
        }
      }
    },
    onFinish: ({ message }: { message: UIMessage }) => {
      // Log completion with performance data
      if (isEnabled) {
        const textContent = getMessageText(message);
        addEntry({
          id: nanoid(),
          timestamp: Date.now(),
          type: "performance",
          title: "Response complete",
          details: {
            messageLength: textContent.length,
            role: message.role,
          },
          status: "success",
        });
      }
    },
    onError: (err: Error) => {
      // Log errors
      if (isEnabled) {
        addEntry({
          id: nanoid(),
          timestamp: Date.now(),
          type: "validation",
          title: "Error occurred",
          details: {
            message: err.message,
          },
          status: "failure",
        });
      }
    },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } as any);

  const { messages, sendMessage, error, status } = chatHelpers;

  // Derive loading state from status
  const isLoading = status === "submitted" || status === "streaming";

  // Handle input change
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setInput(e.target.value);
    },
    []
  );


  // Handle form submission
  const handleFormSubmit = useCallback(
    (e?: { preventDefault?: () => void }) => {
      e?.preventDefault?.();
      if (!input.trim() || isLoading) return;

      // Log user message for Brain Log
      if (isEnabled) {
        addEntry({
          id: nanoid(),
          timestamp: Date.now(),
          type: "input",
          title: "User message received",
          details: {
            length: input.length,
            preview: input.slice(0, 100) + (input.length > 100 ? "..." : ""),
          },
          status: "success",
        });
      }

      // Send message using v2 API
      sendMessage({ text: input });
      setInput("");
    },
    [input, isLoading, sendMessage, addEntry, isEnabled]
  );

  // Handle quick start suggestion click - sends message directly
  const handleQuickStart = useCallback(
    (suggestion: string) => {
      if (isLoading) return;

      // Log user message for Brain Log
      if (isEnabled) {
        addEntry({
          id: nanoid(),
          timestamp: Date.now(),
          type: "input",
          title: "User message received",
          details: {
            length: suggestion.length,
            preview: suggestion,
          },
          status: "success",
        });
      }

      sendMessage({ text: suggestion });
    },
    [isLoading, sendMessage, addEntry, isEnabled]
  );

  return (
    <div className={cn("flex h-full flex-col", className)}>
      {/* Conversation Area */}
      <Conversation className="flex-1">
        <ConversationContent className="mx-auto max-w-3xl px-4">
          {messages.length === 0 ? (
            <ConversationEmptyState
              title="Welcome to Glass Box"
              description="Ask me anything about my experience, this system's architecture, or the codebase."
              icon={<BotIcon className="size-8" />}
            />
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                isStreaming={
                  isLoading &&
                  index === messages.length - 1 &&
                  message.role === "assistant"
                }
              />
            ))
          )}
          {/* Loading indicator for pending assistant response */}
          {isLoading && messages[messages.length - 1]?.role === "user" && (
            <Message from="assistant">
              <MessageContent>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader size={14} />
                  <span className="text-sm">Thinking...</span>
                </div>
              </MessageContent>
            </Message>
          )}
          {/* Error display */}
          {error && (
            <div className="rounded-md border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
              <p className="font-medium">Error</p>
              <p className="text-xs">{error.message}</p>
            </div>
          )}
        </ConversationContent>
        <ConversationScrollButton />
      </Conversation>

      {/* Quick Start Grid - pinned above input when no messages */}
      {messages.length === 0 && (
        <div className="border-t bg-muted/30 px-4 py-3">
          <div className="mx-auto max-w-3xl">
            <p className="mb-2 text-center text-xs font-medium text-muted-foreground">
              Quick Start
            </p>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {STARTER_SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleQuickStart(suggestion)}
                  disabled={isLoading}
                  className="rounded-md border bg-background px-3 py-2 text-left text-xs transition-colors hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t bg-background p-4">
        <div className="mx-auto max-w-3xl">
          <PromptInput
            onSubmit={() => handleFormSubmit()}
            className="rounded-lg border bg-card shadow-sm"
          >
            <PromptInputTextarea
              value={input}
              onChange={handleInputChange}
              placeholder="Ask about my experience, system architecture, or codebase..."
              className="min-h-[60px]"
              disabled={isLoading}
            />
            <PromptInputFooter>
              <div className="flex-1" />
              <PromptInputSubmit disabled={isLoading || !input.trim()} />
            </PromptInputFooter>
          </PromptInput>
          <p className="mt-2 text-center text-xs text-muted-foreground">
            {isEnabled
              ? "Glass Box mode enabled - See agent reasoning in the panel"
              : "Enable Glass Box mode to see agent internals"}
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// ChatMessage Component
// ============================================================================

interface ChatMessageProps {
  message: UIMessage;
  isStreaming?: boolean;
}

function ChatMessage({ message, isStreaming }: ChatMessageProps) {
  const isUser = message.role === "user";
  const parts = message.parts ?? [];

  // For user messages, just show text
  if (isUser) {
    const textContent = getMessageText(message);
    return (
      <Message from={message.role}>
        <div className="flex items-start gap-3">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <UserIcon className="size-4" />
          </div>
          <MessageContent className="flex-1 pt-1">
            <p className="text-sm whitespace-pre-wrap">{textContent}</p>
          </MessageContent>
        </div>
      </Message>
    );
  }

  // For assistant messages, render parts in order (preserves interleaving)
  return (
    <Message from={message.role}>
      <div className="flex items-start gap-3">
        <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-muted">
          <BotIcon className="size-4" />
        </div>
        <MessageContent className="flex-1 pt-1">
          <div className="prose prose-sm dark:prose-invert max-w-none">
            {parts.map((part, index) => {
              // Text part
              if (part.type === "text") {
                const isLastPart = index === parts.length - 1;
                return (
                  <span key={index}>
                    <MessageResponse>{part.text}</MessageResponse>
                    {isStreaming && isLastPart && (
                      <span className="inline-block ml-1">
                        <Loader size={12} />
                      </span>
                    )}
                  </span>
                );
              }

              // Reasoning/thinking part
              if (part.type === "reasoning") {
                const reasoningPart = part as { type: "reasoning"; text: string };
                return (
                  <Reasoning key={index} isStreaming={isStreaming} defaultOpen={false}>
                    <ReasoningTrigger />
                    <ReasoningContent>{reasoningPart.text}</ReasoningContent>
                  </Reasoning>
                );
              }

              // Step-start part (internal marker, don't render)
              if (part.type === "step-start") {
                return null;
              }

              // Tool part (type is "tool-{toolName}")
              if (typeof part.type === "string" && part.type.startsWith("tool-")) {
                const toolPart = part as {
                  type: string;
                  toolCallId: string;
                  toolName: string;
                  state: string;
                  output?: unknown;
                };
                return (
                  <ToolResultRenderer
                    key={toolPart.toolCallId || index}
                    toolName={toolPart.toolName || toolPart.type.replace("tool-", "")}
                    toolCallId={toolPart.toolCallId}
                    state={toolPart.state as "input-streaming" | "input-available" | "output-streaming" | "output-available" | "output-error"}
                    output={toolPart.output}
                  />
                );
              }

              return null;
            })}
          </div>
        </MessageContent>
      </div>
    </Message>
  );
}

export default ChatInterface;
