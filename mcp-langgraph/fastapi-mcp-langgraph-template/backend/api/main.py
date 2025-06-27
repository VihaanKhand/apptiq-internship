from fastapi import FastAPI

from routers import checkpoints, llms, mcps, mcp_router


app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True})
app.include_router(llms.router)
app.include_router(mcps.router)
app.include_router(checkpoints.router)
