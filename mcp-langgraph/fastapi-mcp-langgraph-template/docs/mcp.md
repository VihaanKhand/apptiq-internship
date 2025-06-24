# Model Context Protocol

> [!INFO]
> MCP is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect AI models to different data sources and tools.

Learn more [here](https://modelcontextprotocol.io/introduction).

[![MCP Client](https://img.shields.io/github/stars/modelcontextprotocol/python-sdk?logo=modelcontextprotocol&label=MCP-Client)](https://github.com/modelcontextprotocol/python-sdk) [![MCP Server](https://img.shields.io/github/stars/modelcontextprotocol/servers?logo=modelcontextprotocol&label=MCP-Servers)](https://github.com/modelcontextprotocol/servers)

## Key Features

> MCP helps you build agents and complex workflows on top of LLMs. LLMs frequently need to integrate with data and tools, and MCP provides:
> - A growing list of pre-built integrations that your LLM can directly plug into
> - The flexibility to switch between LLM providers and vendors
> - Best practices for securing your data within your infrastructure

## Inspector

Explore community and your custom MCP servers via Inspector at [http://localhost:6274](http://localhost:6274) in [Development](./quick-start#development).

Left Sidebar:

- Select SSE `Transport Type`
- Input `http://<mcp server>:<MCP_SERVER_PORT>/sse` in `URL`
- Click `Connect`

Explore the following tabs in the Top Navbar:

- `Resources`
- `Prompts`
- `Tools`

See demo videos to learn more.

## Community MCP Servers

Before building your own custom MCP servers, explore the growing list of hundreds of [community MCP servers](https://github.com/modelcontextprotocol/servers). With integrations spanning databases, cloud services, and web resources, the perfect fit might already exist.

### DBHub

Learn more [here](https://github.com/bytebase/dbhub). Explore more in [Inspector](#inspector).

Easily plug in this MCP into LLM to allow LLM to:

- Perform read-only SQL query validation for secure operations

- Enable deterministic introspection of DB
  - List schemas
  - List tables in schemas
  - Retrieve table structures

- Enrich user queries deterministically
  - Ground DB related queries with DB schemas
  - Provide SQL templates for translating natural language to SQL

### Youtube

Learn more [here](https://github.com/Klavis-AI/klavis/tree/main/mcp_servers/youtube). Explore more in [Inspector](#inspector).

Instead of building logic to:

- Scrape YouTube content
- Adapt outputs for LLM compatibility
- Validate tool invocation by the LLM
- Chain these steps to fetch transcripts from URLs

Simply plug in this MCP to enable LLM to:

- Fetch transcripts from any YouTube URL on demand

Check out the [demo video](#video-demo) at the top.

## Custom MCP

Should you require a custom MCP server, a template is provided [here](https://github.com/NicholasGoh/fastapi-mcp-langgraph-template/blob/main/backend/shared_mcp/tools.py) for you to reference in development.

```python
import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "MCP Server",
    port=os.environ["MCP_SERVER_PORT"],
)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
```
