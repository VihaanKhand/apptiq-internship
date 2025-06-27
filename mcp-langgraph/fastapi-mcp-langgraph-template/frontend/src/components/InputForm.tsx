import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  SquarePen,
  Brain,
  Send,
  StopCircle,
  Zap,
  Cpu,
  Bot,
  Search,
  MessageCircle,
  Calculator,
  Wrench,
} from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { AVAILABLE_AGENTS, AgentId } from '@/types/agents';
import { AVAILABLE_MODELS, DEFAULT_MODEL } from '@/types/models';
import { getAgentById } from '@/lib/agents';
import { isValidModelId } from '@/lib/models';

// Updated InputFormProps
interface InputFormProps {
  onSubmit: (
    inputValue: string,
    effort: string,
    model: string,
    agentId: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
  selectedAgent: string;
  onAgentChange: (agentId: string) => void;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
  hasHistory,
  selectedAgent,
  onAgentChange,
}) => {
  const [internalInputValue, setInternalInputValue] = useState('');
  const [effort, setEffort] = useState('medium');
  const [model, setModel] = useState(DEFAULT_MODEL);

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim()) return;
    onSubmit(internalInputValue, effort, model, selectedAgent);
    setInternalInputValue('');
  };

  const handleModelChange = (value: string) => {
    if (isValidModelId(value)) {
      setModel(value);
    }
  };

  const handleInternalKeyDown = (
    e: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleInternalSubmit();
    }
  };

  const isSubmitDisabled = !internalInputValue.trim() || isLoading;
  const selectedAgentInfo = getAgentById(selectedAgent);

  const getAgentIcon = (iconName: string) => {
    switch (iconName) {
      case 'search':
        return <Search className="h-4 w-4 mr-2" />;
      case 'message-circle':
        return <MessageCircle className="h-4 w-4 mr-2" />;
      case 'calculator':
        return <Calculator className="h-4 w-4 mr-2" />;
      case 'wrench':
        return <Wrench className="h-4 w-4 mr-2" />;
      default:
        return <Bot className="h-4 w-4 mr-2" />;
    }
  };

  const getModelIcon = (iconName: string, iconColor: string) => {
    switch (iconName) {
      case 'zap':
        return <Zap className={`h-4 w-4 mr-2 ${iconColor}`} />;
      case 'cpu':
        return <Cpu className={`h-4 w-4 mr-2 ${iconColor}`} />;
      default:
        return <Cpu className="h-4 w-4 mr-2" />;
    }
  };

  // Show effort selector for agents that can benefit from it
  const showEffortSelector = selectedAgent === AgentId.DEEP_RESEARCHER;

  return (
    <form
      onSubmit={handleInternalSubmit}
      className={`flex flex-col gap-2 p-3 `}
    >
      {/* Show selected agent indicator */}
      {selectedAgentInfo && (
        <div className="flex items-center gap-2 text-xs text-neutral-400 px-2">
          <Bot className="h-3 w-3" />
          Using {selectedAgentInfo.name}: {selectedAgentInfo.description}
        </div>
      )}

      <div
        className={`flex flex-row items-center justify-between text-white rounded-3xl rounded-bl-sm ${
          hasHistory ? 'rounded-br-sm' : ''
        } break-words min-h-7 bg-neutral-700 px-4 pt-3 `}
      >
        <Textarea
          value={internalInputValue}
          onChange={(e) => setInternalInputValue(e.target.value)}
          onKeyDown={handleInternalKeyDown}
          placeholder="Hello world!"
          className={`w-full text-neutral-100 placeholder-neutral-500 resize-none border-0 focus:outline-none focus:ring-0 outline-none focus-visible:ring-0 shadow-none 
                        md:text-base  min-h-[56px] max-h-[200px]`}
          rows={1}
        />
        <div className="-mt-3">
          {isLoading ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="text-red-500 hover:text-red-400 hover:bg-red-500/10 p-2 cursor-pointer rounded-full transition-all duration-200"
              onClick={onCancel}
            >
              <StopCircle className="h-5 w-5" />
            </Button>
          ) : (
            <Button
              type="submit"
              variant="ghost"
              className={`${
                isSubmitDisabled
                  ? 'text-neutral-500'
                  : 'text-blue-500 hover:text-blue-400 hover:bg-blue-500/10'
              } p-2 cursor-pointer rounded-full transition-all duration-200 text-base`}
              disabled={isSubmitDisabled}
            >
              <Send className="h-5 w-5" />
            </Button>
          )}
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex flex-row gap-2">
          {/* Only show agent selector when no conversation history */}
          {!hasHistory && (
            <div className="flex flex-row gap-2 bg-neutral-700 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl rounded-t-sm pl-2  max-w-[100%] sm:max-w-[90%]">
              <div className="flex flex-row items-center text-sm">
                <Bot className="h-4 w-4 mr-2" />
                Agent
              </div>
              <Select value={selectedAgent} onValueChange={onAgentChange}>
                <SelectTrigger className="w-[150px] bg-transparent border-none cursor-pointer">
                  <SelectValue placeholder="Agent" />
                </SelectTrigger>
                <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                  {AVAILABLE_AGENTS.map((agent) => (
                    <SelectItem
                      key={agent.id}
                      value={agent.id}
                      className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                    >
                      <div className="flex items-center">
                        {getAgentIcon(agent.icon)}
                        {agent.name}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          {/* Show effort selector for certain agents when no conversation history */}
          {showEffortSelector && !hasHistory && (
            <div className="flex flex-row gap-2 bg-neutral-700 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl rounded-t-sm pl-2  max-w-[100%] sm:max-w-[90%]">
              <div className="flex flex-row items-center text-sm">
                <Brain className="h-4 w-4 mr-2" />
                Effort
              </div>
              <Select value={effort} onValueChange={setEffort}>
                <SelectTrigger className="w-[120px] bg-transparent border-none cursor-pointer">
                  <SelectValue placeholder="Effort" />
                </SelectTrigger>
                <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                  <SelectItem
                    value="low"
                    className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                  >
                    Low
                  </SelectItem>
                  <SelectItem
                    value="medium"
                    className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                  >
                    Medium
                  </SelectItem>
                  <SelectItem
                    value="high"
                    className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                  >
                    High
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
          <div className="flex flex-row gap-2 bg-neutral-700 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl rounded-t-sm pl-2  max-w-[100%] sm:max-w-[90%]">
            <div className="flex flex-row items-center text-sm ml-2">
              <Cpu className="h-4 w-4 mr-2" />
              Model
            </div>
            <Select value={model} onValueChange={handleModelChange}>
              <SelectTrigger className="w-[150px] bg-transparent border-none cursor-pointer">
                <SelectValue placeholder="Model" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                {AVAILABLE_MODELS.map((modelInfo) => (
                  <SelectItem
                    key={modelInfo.id}
                    value={modelInfo.id}
                    className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer"
                  >
                    <div className="flex items-center">
                      {getModelIcon(modelInfo.icon, modelInfo.iconColor)}
                      {modelInfo.name}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        {hasHistory && (
          <Button
            className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer rounded-xl rounded-t-sm pl-2 "
            variant="default"
            onClick={() => window.location.reload()}
          >
            <SquarePen size={16} />
            New Chat
          </Button>
        )}
      </div>
    </form>
  );
};
