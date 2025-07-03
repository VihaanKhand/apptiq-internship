from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

from api.core.agent.orchestration import make_agent_for_model

app = FastAPI()

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]  # expects list of {role: str, content: str}
    model: str  # model identifier, e.g., 'gpt-4', 'gemini-pro'

@app.post("/api/chat/")
async def chat_endpoint(request: ChatRequest) -> Any:
    """
    Route user messages and model selection through the LangGraph agent.
    """
    agent = make_agent_for_model(request.model)
    # Run the graph with the incoming messages
    result = await agent.ainvoke({"messages": request.messages})
    return result
