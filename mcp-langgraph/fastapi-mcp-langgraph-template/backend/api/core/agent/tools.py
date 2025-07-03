import os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import StructuredTool
from typing import List

async def _load_all_mcp_tools() -> List[StructuredTool]:
    """
    Connect to both the AWS and K8s MCP servers,
    discover every tool they expose, and wrap them
    as StructuredTool for LangGraph.
    """
    # Hosts and ports come from your compose-dev.yaml or env
    aws_url = f"http://{os.getenv('AWS_MCP_HOST','aws-mcp')}:" \
              f"{os.getenv('AWS_MCP_PORT','5010')}/mcp"
    k8s_url = f"http://{os.getenv('K8S_MCP_HOST','k8s-mcp')}:" \
              f"{os.getenv('K8S_MCP_PORT','8000')}/mcp"

    connections = {
        "aws": {"url": aws_url,  "transport": "streamable_http"},
        "k8s": {"url": k8s_url,  "transport": "streamable_http"},
    }

    client = MultiServerMCPClient(connections)
    base_tools = await client.get_tools()  
    # base_tools is a List[BaseTool] – wrap each one:
    return [StructuredTool.from_tool(t) for t in base_tools]

def get_tools() -> List[StructuredTool]:
    return asyncio.run(_load_all_mcp_tools())