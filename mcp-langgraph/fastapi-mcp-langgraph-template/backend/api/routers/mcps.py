from fastapi import APIRouter, Request, HTTPException
from ..core.mcps import mcp_sse_client

router = APIRouter()

def resolve_host(agent_id: str) -> str:
    if "aws" in agent_id:
        return "aws-mcp:5010"  # or public DNS/IP if deployed
    elif "k8s" in agent_id or "kubernetes" in agent_id:
        return "k8s-mcp:8000"
    raise HTTPException(status_code=400, detail="Unknown agent_id")

@router.post("/tools")
async def get_tools(request: Request):
    body = await request.json()
    agent_id = body.get("agent_id")
    mcp_host = resolve_host(agent_id)

    async with mcp_sse_client(mcp_host=mcp_host) as session:
        response = await session.list_tools()
        return response.tools

@router.post("/invoke_tool")
async def invoke_tool(request: Request):
    body = await request.json()
    agent_id = body.get("agent_id")
    tool_name = body.get("tool_name")
    args = body.get("args", {})
    mcp_host = resolve_host(agent_id)

    async with mcp_sse_client(mcp_host=mcp_host) as session:
        response = await session.call_tool(tool_name, arguments=args)
        return response.content[0].text

@router.post("/routing_description")
async def routing_description(request: Request):
    body = await request.json()
    agent_id = body.get("agent_id")
    mcp_host = resolve_host(agent_id)

    async with mcp_sse_client(mcp_host=mcp_host) as session:
        response = await session.routing_description()
        return response