from fastapi import APIRouter, Request, HTTPException
from ..core.mcps import MCPs  # make sure the path is correct
import httpx

router = APIRouter()

@router.post("/tools")
async def get_tools(request: Request):
    body = await request.json()
    agent_id = body.get("agent_id")
    client = resolve_client(agent_id)
    return await client.post("/tools", json=body)

@router.post("/invoke_tool")
async def invoke_tool(request: Request):
    body = await request.json()
    agent_id = body.get("agent_id")
    client = resolve_client(agent_id)
    return await client.post("/invoke_tool", json=body)

@router.post("/routing_description")
async def routing_description(request: Request):
    body = await request.json()
    agent_id = body.get("agent_id")
    client = resolve_client(agent_id)
    return await client.post("/routing_description", json=body)

def resolve_client(agent_id: str) -> httpx.AsyncClient:
    if "aws" in agent_id:
        return MCPs["aws"]
    elif "kubernetes" in agent_id:
        return MCPs["kubernetes"]
    raise HTTPException(status_code=400, detail="Unknown agent_id")
