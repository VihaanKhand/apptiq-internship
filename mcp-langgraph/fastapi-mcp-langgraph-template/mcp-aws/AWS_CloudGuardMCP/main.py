from fastapi import FastAPI, Request
app = FastAPI()

@app.get("/")
def root():
    return {"message": "AWS MCP running"}

@app.post("/mcp")
async def list_tools(request: Request):
    """
    MultiServerMCPClient.get_tools() will POST here.
    For now we just return an empty list of tools.
    """
    return []