import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from './ui/collapsible';
import { Badge } from './ui/badge';
import {
  ChevronRight,
  Wrench,
  Clock,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { ToolCall, ToolMessage } from '@/types/tools';
import { cn } from '@/lib/utils';

interface ToolMessageDisplayProps {
  toolCall: ToolCall;
  toolMessage?: ToolMessage;
  isExpanded: boolean;
  onToggle: () => void;
}

// Tool execution status indicators
const getStatusBadge = (toolMessage?: ToolMessage) => {
  if (!toolMessage) {
    return (
      <Badge
        variant="secondary"
        className="bg-amber-500/10 text-amber-600 border-amber-500/20 text-xs font-medium"
      >
        <Clock className="h-3 w-3 mr-1" />
        Running
      </Badge>
    );
  }
  if (toolMessage.is_error) {
    return (
      <Badge
        variant="destructive"
        className="bg-red-500/10 text-red-600 border-red-500/20 text-xs font-medium"
      >
        <XCircle className="h-3 w-3 mr-1" />
        Error
      </Badge>
    );
  }
  return (
    <Badge
      variant="default"
      className="mr-2 bg-green-500/10 text-green-600 border-green-500/20 text-xs font-medium"
    >
      <CheckCircle className="h-3 w-3 mr-1" />
      Success
    </Badge>
  );
};

// JSON syntax highlighting for inputs/outputs
const JsonDisplay = ({ data, title }: { data: unknown; title: string }) => (
  <div className="space-y-2">
    <h4 className="text-xs font-medium text-neutral-400 uppercase tracking-wider">
      {title}
    </h4>
    <div className="bg-neutral-900/50 rounded-lg p-3 border border-neutral-700/50 overflow-x-auto">
      <pre className="text-xs overflow-x-auto text-neutral-200 font-mono leading-relaxed whitespace-pre-wrap break-words min-w-0">
        <code>{JSON.stringify(data, null, 2)}</code>
      </pre>
    </div>
  </div>
);

export function ToolMessageDisplay({
  toolCall,
  toolMessage,
  isExpanded,
  onToggle,
}: ToolMessageDisplayProps) {
  return (
    <div className="border border-neutral-600/40 bg-neutral-800/30 rounded-lg overflow-hidden mt-4 mb-4 min-w-0">
      <Collapsible open={isExpanded} onOpenChange={onToggle}>
        <CollapsibleTrigger asChild>
          <button className="w-full px-4 py-3 hover:bg-neutral-700/20 transition-all duration-200 text-left focus:outline-none focus:bg-neutral-700/20">
            <div className="flex items-center justify-between min-w-0">
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <div className="p-1.5 rounded-md bg-neutral-700/50 flex-shrink-0">
                    <Wrench className="h-3.5 w-3.5 text-neutral-300" />
                  </div>
                  <div className="flex flex-col gap-1 min-w-0 flex-1">
                    <span className="font-medium text-neutral-100 text-sm truncate">
                      {toolCall.name}
                    </span>
                  </div>
                </div>
                <div className="flex-shrink-0">
                  {getStatusBadge(toolMessage)}
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                <ChevronRight
                  className={cn(
                    'h-4 w-4 text-neutral-400 transition-transform duration-200',
                    isExpanded && 'rotate-90'
                  )}
                />
              </div>
            </div>
          </button>
        </CollapsibleTrigger>
        <CollapsibleContent
          className={cn(
            'data-[state=open]:animate-collapsible-down data-[state=closed]:animate-collapsible-up'
          )}
        >
          <div className="px-4 pb-4 space-y-4 border-t border-neutral-700/30 overflow-x-auto">
            <div className="pt-4 min-w-0">
              {/* Tool inputs */}
              {Object.keys(toolCall.args).length > 0 && (
                <JsonDisplay data={toolCall.args} title="Input" />
              )}

              {/* Tool outputs */}
              {toolMessage && (
                <div className="space-y-2 mt-4">
                  <h4 className="text-xs font-medium text-neutral-400 uppercase tracking-wider">
                    Output
                  </h4>
                  <div
                    className={cn(
                      'rounded-lg p-3 text-sm border overflow-x-auto',
                      toolMessage.is_error
                        ? 'bg-red-900/10 border-red-500/20 text-red-200'
                        : 'bg-neutral-900/50 border-neutral-700/50 text-neutral-200'
                    )}
                  >
                    {typeof toolMessage.content === 'string' ? (
                      <pre className="whitespace-pre-wrap overflow-x-auto font-mono text-xs leading-relaxed break-words min-w-0">
                        {toolMessage.content}
                      </pre>
                    ) : (
                      <pre className="overflow-x-auto font-mono text-xs leading-relaxed min-w-0">
                        <code className="whitespace-pre-wrap break-words">
                          {JSON.stringify(toolMessage.content, null, 2)}
                        </code>
                      </pre>
                    )}
                  </div>
                </div>
              )}

              {/* Show waiting message if no tool message yet */}
              {!toolMessage && (
                <div className="text-xs text-neutral-500 italic mt-4 p-3 bg-neutral-800/20 rounded-lg border border-neutral-700/30">
                  <div className="flex items-center gap-2">
                    <Clock className="h-3 w-3 animate-pulse flex-shrink-0" />
                    <span>Waiting for tool response...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
