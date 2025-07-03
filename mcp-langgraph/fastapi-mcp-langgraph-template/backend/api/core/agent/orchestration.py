import functools, os
from typing import List, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.base import RunnableSequence
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from api.core.agent.tools import get_tools       # ← one‐way import
from api.core.agent.prompts import SYSTEM_PROMPT
from api.core.dependencies import LangfuseHandlerDep


class State(MessagesState):
    next: str


def agent_factory(
    llm: RunnableSequence,
    tools: List[StructuredTool],
    system_prompt: str,
) -> RunnableSequence:
    """
    Build a prompt-to-LLM (and optional tools) pipeline.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    if tools:
        return prompt | llm.bind_tools(tools)
    return prompt | llm


def agent_node_factory(
    state: State,
    agent: RunnableSequence,
) -> State:
    result = agent.invoke(state)
    return dict(messages=[result])


def graph_factory(
    agent_node: functools.partial,
    tools: List[StructuredTool],
    checkpointer: Optional[AsyncPostgresSaver] = None,
    name: str = "agent_node",
) -> CompiledStateGraph:
    """
    Create and compile a LangGraph state graph with a single agent node
    and a tools node, with conditional routing.
    """
    builder = StateGraph(State)
    builder.add_node(name, agent_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_conditional_edges(name, tools_condition)
    builder.add_edge("tools", name)
    builder.set_entry_point(name)
    return builder.compile(checkpointer=checkpointer)


def get_graph(
    llm: RunnableSequence,
    tools: List[StructuredTool] = [],
    system_prompt: str = SYSTEM_PROMPT,
    name: str = "agent_node",
    checkpointer: Optional[AsyncPostgresSaver] = None,
) -> CompiledStateGraph:
    """
    Constructs and compiles the state graph with given llm and tools.
    """
    agent = agent_factory(llm, tools, system_prompt)
    worker = functools.partial(agent_node_factory, agent=agent)
    return graph_factory(worker, tools, checkpointer, name)


def make_agent_for_model(
    model_name: str,
) -> RunnableSequence:
    """
    Instantiate the appropriate LLM client (OpenAI or Gemini),
    load all MCP tools, and return the compiled graph as an agent.
    """
    # Select LLM based on model_name
    if model_name.startswith("gpt-4"):
        llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    elif model_name.startswith("gpt-3.5"):
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    elif model_name.startswith("gemini"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

            class GeminiChat:
                def __init__(self, model: str, temperature: float):
                    self.model = model
                    self.temperature = temperature

                async def __call__(self, messages: List[dict]):
                    resp = genai.chat.create(
                        model=self.model,
                        temperature=self.temperature,
                        messages=[{"author": m["role"], "content": m["content"]} for m in messages],
                    )
                    return {"content": resp.last}

            llm = GeminiChat(model=model_name, temperature=0)
        except ImportError:
            raise RuntimeError("google-generative-ai SDK is not installed")
    else:
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    tools = get_tools()
    return get_graph(llm, tools)


def get_config(langfuse_handler: LangfuseHandlerDep) -> dict[str, Any]:
    """
    Langfuse configuration for logging and callbacks.
    """
    return {
        "configurable": {"thread_id": "1"},
        "callbacks": [langfuse_handler],
    }