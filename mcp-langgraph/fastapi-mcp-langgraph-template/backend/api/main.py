from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.routers.llms import router as llm_router  # assuming your agent logic is modular

# FastAPI app setup
app = FastAPI()

# CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with exact URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount your LangGraph-related routes
app.include_router(llm_router)