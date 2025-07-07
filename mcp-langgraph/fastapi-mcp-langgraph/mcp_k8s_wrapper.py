from fastapi import FastAPI
from mcp_k8s.k8s_mcp_server.src.k8s_mcp_server.server import app as upstream

app = FastAPI()

@app.get("/")
async def health():
    return {"message": "K8s MCP (wrapper) running"}

# mount the real k8s_mcp_server app under /mcp
app.mount("/mcp", upstream)