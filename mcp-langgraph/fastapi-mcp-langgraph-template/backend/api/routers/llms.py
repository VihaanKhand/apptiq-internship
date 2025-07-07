from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from starlette.responses import Response

from api.core.dependencies import LLMDep

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


# —— JSON Chat Endpoint —— #
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, llm=Depends(LLMDep)) -> ChatResponse:
    """
    Simple JSON endpoint: collects all streamed chunks into one string.
    """
    accumulated = ""
    async for chunk in llm.astream_events(payload.message):
        accumulated += chunk
    return ChatResponse(response=accumulated)


# —— Raw LLM SSE —— #
@router.get("/completions")
async def completions(query: str, llm=Depends(LLMDep)) -> Response:
    """
    Stream raw LLM completions as Server-Sent Events.
    """
    return EventSourceResponse(_stream_completions(query, llm))


async def _stream_completions(
    query: str, llm
) -> AsyncGenerator[dict[str, str], None]:
    async for chunk in llm.astream_events(query):
        yield {"data": chunk}