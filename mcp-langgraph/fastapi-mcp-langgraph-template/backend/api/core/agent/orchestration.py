import os
from typing import Any, List, Dict

from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer


def make_agent_for_model(
    model_name: str,
    tools: List[StructuredTool],
) -> Any:
    """
    Build a LangChain agent for the given model (OpenAI or Gemini),
    attach MCP tools, and enable LangSmith tracing per the official docs.
    """
    # 1️⃣ Choose the LLM implementation
    if model_name.startswith("gpt-"):
        llm = ChatOpenAI(
            model_name=model_name,
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
    elif model_name.startswith("gemini-"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable is not set.")
        try:
            import google.generativeai as genai
        except ImportError:
            raise RuntimeError("Please install the 'google-generativeai' SDK to use Gemini models.")
        genai.configure(api_key=api_key)

        class GeminiChatAdapter:
            """
            Adapter for Google Generative AI chat completion per SDK docs.
            """
            def __init__(self, model: str):
                self.model = model
                self.genai = genai

            async def __call__(self, prompt: str) -> str:
                resp = self.genai.chat.completions.create(
                    model=self.model,
                    messages=[{"author": "user", "content": prompt}],
                )
                if hasattr(resp, "last"):
                    return resp.last
                data = getattr(resp, "candidates", None)
                if data:
                    first = data[0]
                    return getattr(first, "text", None) or first.get("text", "")
                return getattr(resp, "text", None) or resp.get("text", "")

        llm = GeminiChatAdapter(model=model_name)
    else:
        raise ValueError(f"Unknown model: {model_name}")

    # 2️⃣ Setup tracer and callback manager (LangSmith)
    tracer = LangChainTracer(project_name="mcp-agent-traces")
    callback_manager = CallbackManager(callbacks=[tracer])

    # 3️⃣ Initialize an agent with tool support and tracing
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        callback_manager=callback_manager,
        verbose=True,
    )
    return agent
