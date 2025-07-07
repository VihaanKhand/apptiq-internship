import { InputForm } from './InputForm';

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string,
    model: string,
    agentId: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
  selectedAgent: string;
  onAgentChange: (agentId: string) => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
  selectedAgent,
  onAgentChange,
}) => (
  <div className="flex flex-col items-center justify-center text-center px-4 flex-1 mb-16 w-full max-w-3xl mx-auto gap-4">
    <div className="flex flex-col items-center gap-6">
      <img
        src="./logo-icon.svg"
        alt="Company Logo Icon"
        className="h-24 w-24 text-primary"
      />
      <div>
        <h1 className="text-5xl md:text-6xl font-semibold text-neutral-100 mb-3">
          Welcome.
        </h1>
        <p className="text-xl md:text-2xl text-neutral-400">
          How can I help you today?
        </p>
      </div>
    </div>
    <div className="w-full mt-4">
      <InputForm
        onSubmit={handleSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        hasHistory={false}
        selectedAgent={selectedAgent}
        onAgentChange={onAgentChange}
      />
    </div>
    <p className="text-xs text-neutral-500">
      Powered by LangChain and LangGraph.
    </p>
  </div>
);
