import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from starlette.responses import Response

from api.core.dependencies import LLMDep

router = APIRouter(prefix="/chat", tags=["chat"])

# —— 1) JSON Chat Endpoint —— #
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    llm = Depends(LLMDep),
) -> ChatResponse:
    accumulated = ""
    async for chunk in llm.astream_events(payload.message):
        accumulated += chunk
    return ChatResponse(response=accumulated)


# —— 2) Raw LLM SSE Endpoint —— #
@router.get("/completions")
async def completions(
    query: str,
    llm = Depends(LLMDep),
) -> Response:
    return EventSourceResponse(_stream_completions(query, llm))


async def _stream_completions(
    query: str,
    llm,
) -> AsyncGenerator[Dict[str, str], None]:
    async for chunk in llm.astream_events(query):
        yield {"data": chunk}


# —— 3) Thread Schema & Store —— #
class Message(BaseModel):
    role: Literal["human", "assistant", "system"]
    content: str
    id: str


class ThreadInput(BaseModel):
    messages: List[Message]
    model: str


class ThreadCreateRequest(BaseModel):
    input: ThreadInput


class ThreadCreatedResponse(BaseModel):
    threadId: str


# In-memory store for threads; stores ThreadInput instances
threads_store: Dict[str, ThreadInput] = {}


@router.post("/threads", response_model=ThreadCreatedResponse)
async def create_thread(
    req: ThreadCreateRequest,
) -> ThreadCreatedResponse:
    """
    Create a new chat thread with validated input.
    """
    tid = str(uuid.uuid4())
    threads_store[tid] = req.input
    return ThreadCreatedResponse(threadId=tid)


# —— 4) Thread Events SSE Endpoint —— #
@router.get("/threads/{thread_id}/events")
async def thread_events(
    thread_id: str,
    llm = Depends(LLMDep),
) -> Response:
    """
    Stream LLM events for the last user message in a specific thread.
    """
    data = threads_store.get(thread_id)
    if not data:
        raise HTTPException(404, "Thread not found")

    msgs = data.messages
    if not msgs:
        raise HTTPException(400, "No messages in thread")
    last = msgs[-1].content

    async def event_gen() -> AsyncGenerator[Dict[str, str], None]:
        async for chunk in llm.astream_events(last):
            yield {"data": chunk}

    return EventSourceResponse(event_gen())


# —— 5) Runs Stream SSE Endpoint —— #
@router.get("/runs/stream")
async def runs_stream(
    threadId: Optional[str] = Query(None, description="ID of the chat thread"),
    llm = Depends(LLMDep),
) -> Response:
    """
    Stream LLM tokens as SSE for the given thread, or fallback to the latest thread.
    """
    # Retrieve the thread input
    thread_input = None
    if threadId:
        thread_input = threads_store.get(threadId)
        if not thread_input:
            raise HTTPException(404, "Thread not found")
    else:
        if not threads_store:
            raise HTTPException(400, "No thread available")
        _, thread_input = next(reversed(threads_store.items()))

    msgs = thread_input.messages
    if not msgs:
        raise HTTPException(400, "No messages to send to LLM")
    last = msgs[-1].content

    async def event_gen():
        async for chunk in llm.astream_events(last):
            yield {"data": chunk}

    return EventSourceResponse(event_gen())
