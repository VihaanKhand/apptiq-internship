export enum AgentId {
  DEEP_RESEARCHER = 'deep_researcher',
  CHATBOT = 'chatbot',
  MATH_AGENT = 'math_agent',
  MCP_AGENT = 'mcp_agent',
}

export interface Agent {
  id: AgentId;
  name: string;
  description: string;
  icon: string;
  capabilities: string[];
  showActivityTimeline: boolean;
}

export const AVAILABLE_AGENTS: Agent[] = [
  {
    id: AgentId.DEEP_RESEARCHER,
    name: 'Deep Researcher',
    description: 'Advanced deep research with enhanced analysis',
    icon: 'search',
    capabilities: ['Advanced Web Research', 'Deep Analysis'],
    showActivityTimeline: true,
  },
  {
    id: AgentId.CHATBOT,
    name: 'Chat Assistant',
    description: 'Simple conversational assistant',
    icon: 'message-circle',
    capabilities: ['General Chat', 'Quick Responses'],
    showActivityTimeline: false,
  },
  {
    id: AgentId.MATH_AGENT,
    name: 'Math Solver',
    description: 'Advanced mathematical problem solving and calculations',
    icon: 'calculator',
    capabilities: [
      'Mathematical Calculations',
      'Problem Solving',
      'Formula Analysis',
    ],
    showActivityTimeline: false,
  },
  {
    id: AgentId.MCP_AGENT,
    name: 'MCP Agent',
    description: 'Model Context Protocol agent with external tool integrations',
    icon: 'wrench',
    capabilities: ['Model context protocol (MCP)'],
    showActivityTimeline: false,
  },
];

export const DEFAULT_AGENT = AgentId.CHATBOT;
