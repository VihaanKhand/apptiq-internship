from mcp.server.fastmcp import FastMCP
from langchain_core.messages import AIMessage, HumanMessage
from typing import List, Optional, Union

mcp = FastMCP()

@mcp.tool()
def diagnose_k8s(pod_name: str) -> str:
    return f"Diagnosing Kubernetes pod: {pod_name}"

@mcp.tool()
def diagnose_aws(service_name: str) -> str:
    return f"Checking AWS service: {service_name}"
