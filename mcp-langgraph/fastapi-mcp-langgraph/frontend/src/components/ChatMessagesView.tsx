import type React from 'react';
import type { Message } from '@langchain/langgraph-sdk';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Copy, CopyCheck } from 'lucide-react';
import { InputForm } from '@/components/InputForm';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import {
  ActivityTimeline,
  ProcessedEvent,
} from '@/components/ActivityTimeline'; // Assuming ActivityTimeline is in the same dir or adjust path
import { AVAILABLE_AGENTS } from '@/types/agents';
import { ToolMessageDisplay } from '@/components/ToolMessageDisplay';
import {
  extractToolCallsFromMessage,
  findToolMessageForCall,
} from '@/types/messages';
import { ToolCall } from '@/types/tools';
import { AgentId } from '@/types/agents';

// Group messages to combine AI responses with their tool calls and results
interface MessageGroup {
  id: string;
  type: 'human' | 'ai_complete';
  messages: Message[];
  primaryMessage: Message;
  toolCalls: ToolCall[];
  toolResults: Message[];
}

const groupMessages = (messages: Message[]): MessageGroup[] => {
  const groups: MessageGroup[] = [];
  let currentGroup: MessageGroup | null = null;

  for (const message of messages) {
    if (message.type === 'human') {
      // Human messages are always standalone
      groups.push({
        id: message.id || `human-${Date.now()}`,
        type: 'human',
        messages: [message],
        primaryMessage: message,
        toolCalls: [],
        toolResults: [],
      });
      currentGroup = null;
    } else if (message.type === 'ai') {
      // Start a new AI group or continue existing one
      if (!currentGroup || currentGroup.type !== 'ai_complete') {
        // Create new AI group
        currentGroup = {
          id: message.id || `ai-${Date.now()}`,
          type: 'ai_complete',
          messages: [message],
          primaryMessage: message,
          toolCalls: [], // Don't accumulate tool calls at group level
          toolResults: [],
        };
        groups.push(currentGroup);
      } else {
        // Add to existing AI group (for cases with multiple AI messages)
        currentGroup.messages.push(message);
        // Don't accumulate tool calls to avoid duplication
        // Update primary message to the latest one with content
        if (
          message.content &&
          typeof message.content === 'string' &&
          message.content.trim()
        ) {
          currentGroup.primaryMessage = message;
        }
      }
    } else if (message.type === 'tool') {
      // Tool results belong to the current AI group
      if (currentGroup && currentGroup.type === 'ai_complete') {
        currentGroup.toolResults.push(message);
        currentGroup.messages.push(message);
      }
    }
  }

  return groups;
};

// Markdown components (from former ReportView.tsx)
const mdComponents = {
  h1: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h1 className={cn('text-2xl font-bold mt-4 mb-2', className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h2 className={cn('text-xl font-bold mt-3 mb-2', className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h3 className={cn('text-lg font-bold mt-3 mb-1', className)} {...props}>
      {children}
    </h3>
  ),
  p: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLParagraphElement>) => (
    <p className={cn('mb-3 leading-7', className)} {...props}>
      {children}
    </p>
  ),
  a: ({
    className,
    children,
    href,
    ...props
  }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <Badge className="text-xs mx-0.5">
      <a
        className={cn('text-blue-400 hover:text-blue-300 text-xs', className)}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    </Badge>
  ),
  ul: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLUListElement>) => (
    <ul className={cn('list-disc pl-6 mb-3', className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLOListElement>) => (
    <ol className={cn('list-decimal pl-6 mb-3', className)} {...props}>
      {children}
    </ol>
  ),
  li: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLLIElement>) => (
    <li className={cn('mb-1', className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLQuoteElement>) => (
    <blockquote
      className={cn(
        'border-l-4 border-neutral-600 pl-4 italic my-3 text-sm',
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLElement>) => (
    <code
      className={cn(
        'bg-neutral-900 rounded px-1 py-0.5 font-mono text-xs',
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({
    className,
    children,
    ...props
  }: React.HTMLAttributes<HTMLPreElement>) => (
    <pre
      className={cn(
        'bg-neutral-900 p-3 rounded-lg overflow-x-auto font-mono text-xs my-3',
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }: React.HTMLAttributes<HTMLHRElement>) => (
    <hr className={cn('border-neutral-600 my-4', className)} {...props} />
  ),
  table: ({
    className,
    children,
    ...props
  }: React.TableHTMLAttributes<HTMLTableElement>) => (
    <div className="my-3 overflow-x-auto">
      <table className={cn('border-collapse w-full', className)} {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({
    className,
    children,
    ...props
  }: React.ThHTMLAttributes<HTMLTableHeaderCellElement>) => (
    <th
      className={cn(
        'border border-neutral-600 px-3 py-2 text-left font-bold',
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({
    className,
    children,
    ...props
  }: React.TdHTMLAttributes<HTMLTableDataCellElement>) => (
    <td
      className={cn('border border-neutral-600 px-3 py-2', className)}
      {...props}
    >
      {children}
    </td>
  ),
};

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  group: MessageGroup;
  mdComponents: typeof mdComponents;
}

// HumanMessageBubble Component
const HumanMessageBubble: React.FC<HumanMessageBubbleProps> = ({
  group,
  mdComponents,
}) => {
  const message = group.primaryMessage;
  return (
    <div
      className={`text-white rounded-3xl break-words min-h-7 bg-neutral-700 max-w-[100%] sm:max-w-[90%] px-4 pt-3 rounded-br-lg`}
    >
      <ReactMarkdown components={mdComponents}>
        {typeof message.content === 'string'
          ? message.content
          : JSON.stringify(message.content)}
      </ReactMarkdown>
    </div>
  );
};

// Props for AiMessageBubble
interface AiMessageBubbleProps {
  group: MessageGroup;
  historicalActivity: ProcessedEvent[] | undefined;
  liveActivity: ProcessedEvent[] | undefined;
  isLastGroup: boolean;
  isOverallLoading: boolean;
  mdComponents: typeof mdComponents;
  handleCopy: (text: string, messageId: string) => void;
  copiedMessageId: string | null;
  selectedAgentId: string;
  allMessages: Message[];
}

// AiMessageBubble Component
const AiMessageBubble: React.FC<AiMessageBubbleProps> = ({
  group,
  historicalActivity,
  liveActivity,
  isLastGroup,
  isOverallLoading,
  mdComponents,
  handleCopy,
  copiedMessageId,
  selectedAgentId,
  allMessages,
}) => {
  // Tool message state
  const [expandedTools, setExpandedTools] = useState<Set<string>>(new Set());

  const toggleTool = (toolId: string) => {
    setExpandedTools((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(toolId)) {
        newSet.delete(toolId);
      } else {
        newSet.add(toolId);
      }
      return newSet;
    });
  };

  // Determine which activity events to show and if it's for a live loading message
  const activityForThisBubble =
    isLastGroup && isOverallLoading ? liveActivity : historicalActivity;
  const isLiveActivityForThisBubble = isLastGroup && isOverallLoading;

  // Get current agent configuration
  const currentAgent = AVAILABLE_AGENTS.find(
    (agent) => agent.id === selectedAgentId
  );
  const shouldShowActivity =
    currentAgent?.showActivityTimeline &&
    (isLiveActivityForThisBubble ||
      (activityForThisBubble && activityForThisBubble.length > 0));

  // Check if we should hide tool messages for DeepResearcher
  const shouldHideToolMessages = selectedAgentId === AgentId.DEEP_RESEARCHER;

  // Check if we should hide copy button (when still loading for this message group)
  const shouldHideCopyButton = isLastGroup && isOverallLoading;

  // Combine all text content for copy functionality
  const combinedTextContent = group.messages
    .filter((msg) => msg.type === 'ai' && msg.content)
    .map((msg) =>
      typeof msg.content === 'string'
        ? msg.content
        : JSON.stringify(msg.content)
    )
    .filter((content) => content.trim())
    .join('\n\n');

  return (
    <div
      className={`relative break-words flex flex-col group max-w-[85%] md:max-w-[80%] w-full ${
        shouldShowActivity
          ? 'rounded-xl p-3 shadow-sm bg-neutral-800 text-neutral-100 rounded-bl-none min-h-[56px]'
          : ''
      }`}
    >
      {shouldShowActivity && (
        <div className="mb-3 border-b border-neutral-700 pb-3 text-xs">
          <ActivityTimeline
            processedEvents={activityForThisBubble || []}
            isLoading={isLiveActivityForThisBubble}
          />
        </div>
      )}

      {/* Render messages in chronological order */}
      {group.messages.map((message, index) => {
        if (message.type === 'ai') {
          const toolCalls = extractToolCallsFromMessage(message);
          const hasContent =
            message.content &&
            typeof message.content === 'string' &&
            message.content.trim();

          return (
            <div key={message.id || `ai-${index}`} className="space-y-3">
              {/* Render AI content if present */}
              {hasContent && (
                <ReactMarkdown components={mdComponents}>
                  {typeof message.content === 'string'
                    ? message.content
                    : JSON.stringify(message.content)}
                </ReactMarkdown>
              )}

              {/* Render tool calls immediately after the AI message that triggered them */}
              {!shouldHideToolMessages && toolCalls.length > 0 && (
                <div className="space-y-2">
                  {toolCalls.map((toolCall) => (
                    <ToolMessageDisplay
                      key={toolCall.id}
                      toolCall={toolCall}
                      toolMessage={findToolMessageForCall(
                        allMessages,
                        toolCall.id
                      )}
                      isExpanded={expandedTools.has(toolCall.id)}
                      onToggle={() => toggleTool(toolCall.id)}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        }
        // Skip tool messages as they're handled by ToolMessageDisplay above
        return null;
      })}

      {!shouldHideCopyButton && (
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 self-start mt-2 hover:bg-neutral-600/50 text-neutral-400 hover:text-neutral-200"
          onClick={() =>
            handleCopy(combinedTextContent, group.primaryMessage.id!)
          }
        >
          {copiedMessageId === group.primaryMessage.id ? (
            <CopyCheck className="h-3 w-3" />
          ) : (
            <Copy className="h-3 w-3" />
          )}
        </Button>
      )}
    </div>
  );
};

interface ChatMessagesViewProps {
  messages: Message[];
  isLoading: boolean;
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
  onSubmit: (
    inputValue: string,
    effort: string,
    model: string,
    agentId: string
  ) => void;
  onCancel: () => void;
  liveActivityEvents: ProcessedEvent[];
  historicalActivities: Record<string, ProcessedEvent[]>;
  selectedAgentId: string;
  onAgentChange: (agentId: string) => void;
}

export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  liveActivityEvents,
  historicalActivities,
  selectedAgentId,
  onAgentChange,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  // Group messages to combine related AI responses and tool calls
  const messageGroups = groupMessages(messages);

  return (
    <div className="flex flex-col h-full min-h-0">
      <ScrollArea className="flex-1 min-h-0" ref={scrollAreaRef}>
        <div className="p-4 md:p-6 space-y-2 max-w-4xl mx-auto pt-16 pb-4">
          {messageGroups.map((group, index) => {
            const isLast = index === messageGroups.length - 1;
            return (
              <div key={group.id} className="space-y-3">
                <div
                  className={`flex items-start gap-3 ${
                    group.type === 'human' ? 'justify-end' : ''
                  }`}
                >
                  {group.type === 'human' ? (
                    <HumanMessageBubble
                      group={group}
                      mdComponents={mdComponents}
                    />
                  ) : (
                    <AiMessageBubble
                      group={group}
                      historicalActivity={
                        historicalActivities[group.primaryMessage.id!]
                      }
                      liveActivity={liveActivityEvents}
                      isLastGroup={isLast}
                      isOverallLoading={isLoading}
                      mdComponents={mdComponents}
                      handleCopy={handleCopy}
                      copiedMessageId={copiedMessageId}
                      selectedAgentId={selectedAgentId}
                      allMessages={messages}
                    />
                  )}
                </div>
              </div>
            );
          })}
          {isLoading &&
            (messageGroups.length === 0 ||
              messageGroups[messageGroups.length - 1].type === 'human') && (
              <div className="flex items-start gap-3 mt-3">
                {(() => {
                  const currentAgent = AVAILABLE_AGENTS.find(
                    (agent) => agent.id === selectedAgentId
                  );
                  const shouldShowActivity = currentAgent?.showActivityTimeline;

                  if (shouldShowActivity) {
                    return (
                      <div className="relative group max-w-[85%] md:max-w-[80%] rounded-xl p-3 shadow-sm break-words bg-neutral-800 text-neutral-100 rounded-bl-none w-full min-h-[56px]">
                        <div className="text-xs">
                          <ActivityTimeline
                            processedEvents={liveActivityEvents}
                            isLoading={true}
                          />
                        </div>
                      </div>
                    );
                  } else {
                    return (
                      <div className="flex items-center justify-start h-full min-h-[56px]">
                        <div className="flex justify-center items-center gap-1">
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.32s]"></div>
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.16s]"></div>
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                        </div>
                      </div>
                    );
                  }
                })()}
              </div>
            )}
        </div>
      </ScrollArea>
      <div className="flex-shrink-0">
        <InputForm
          onSubmit={onSubmit}
          isLoading={isLoading}
          onCancel={onCancel}
          hasHistory={messages.length > 0}
          selectedAgent={selectedAgentId}
          onAgentChange={onAgentChange}
        />
      </div>
    </div>
  );
}
