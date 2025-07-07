import os
from typing import List

from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

async def _load_all_mcp_tools() -> List[StructuredTool]:
    """
    Asynchronously fetch all MCP tool definitions from
    both AWS and K8s MCP servers.
    """
    aws_url = f"http://{os.getenv('AWS_MCP_HOST','aws-mcp')}:{os.getenv('AWS_MCP_PORT','5010')}/mcp"
    k8s_url = f"http://{os.getenv('K8S_MCP_HOST','k8s-mcp')}:{os.getenv('K8S_MCP_PORT','8000')}/mcp"
    client = MultiServerMCPClient({
        "aws": {"url": aws_url, "transport": "streamable_http"},
        "k8s": {"url": k8s_url, "transport": "streamable_http"},
    })
    base_tools = await client.get_tools()
    return [StructuredTool.from_tool(t) for t in base_tools]

def get_tools_from_app_state(app) -> List[StructuredTool]:
    """Retrieve the cached MCP tools loaded at startup."""
    return getattr(app.state, "mcp_tools", [])