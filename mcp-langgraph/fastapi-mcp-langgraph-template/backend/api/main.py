from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from api.core.agent.tools import _load_all_mcp_tools, get_tools_from_app_state
from api.core.agent.orchestration import make_agent_for_model

app = FastAPI()

@app.on_event("startup")
async def load_mcp_tools():
    """
    On startup, discover all MCP tools and cache them in app.state.
    """
    try:
        tools = await _load_all_mcp_tools()
        app.state.mcp_tools = tools
        print(f"✅ Loaded {len(tools)} MCP tools at startup")
    except Exception as e:
        app.state.mcp_tools = []
        print("⚠️ Warning: failed to load MCP tools at startup:", e)

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]  # [{"role":"user","content":"..."}]
    model: str                       # e.g. "gpt-3.5-turbo" or "gemini-pro"

@app.post("/chat/")
async def chat_endpoint(request: ChatRequest) -> Any:
    print("➡️ /chat/ called with model=", request.model)
    tools = get_tools_from_app_state(app)
    print("✅ get_tools returned", len(tools), "tools")

    try:
        agent = make_agent_for_model(request.model, tools)
        print("✅ make_agent_for_model created agent")
        # Agents expose a simple `.run()` method synchronously or async `.arun()`
        response = await agent.arun(request.messages[-1]["content"])
        print("✅ agent.arun returned result")
        return {"content": response}
    except Exception as e:
        print("🚨 ERROR in /chat/:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint so you can smoke-test the service
    via GET /api/health when using --root-path=/api
    """
    return {"status": "ok"}