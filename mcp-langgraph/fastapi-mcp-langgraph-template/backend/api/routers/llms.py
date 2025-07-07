import uuid
from typing import Any, AsyncGenerator, Dict

from fastapi import APIRouter, Depends, HTTPException, Body, Request
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
async def chat(payload: ChatRequest, llm=Depends(LLMDep)) -> ChatResponse:
    """
    Collects all streamed tokens into one response string.
    """
    accumulated = ""
    async for chunk in llm.astream_events(payload.message):
        accumulated += chunk
    return ChatResponse(response=accumulated)


# —— 2) Raw LLM SSE Endpoint —— #
@router.get("/completions")
async def completions(query: str, llm=Depends(LLMDep)) -> Response:
    """
    Streams raw LLM completions as Server-Sent Events.
    """
    return EventSourceResponse(_stream_completions(query, llm))


async def _stream_completions(
    query: str, llm
) -> AsyncGenerator[Dict[str, str], None]:
    """
    Generator for raw LLM SSE chunks.
    """
    async for chunk in llm.astream_events(query):
        yield {"data": chunk}


# —— 3) Threads API for useStream —— #

# In-memory store for threads
threads_store: Dict[str, Dict[str, Any]] = {}


@router.post("/threads")
async def create_thread(payload: Dict[str, Any] = Body(...)):
    """
    Accept whatever the frontend sends, store it under a UUID, and return threadId.
    """
    tid = str(uuid.uuid4())
    threads_store[tid] = payload
    return {"threadId": tid}


@router.get("/threads/{thread_id}/events")
async def thread_events(thread_id: str, llm=Depends(LLMDep)) -> Response:
    """
    Stream LLM events based on the last user message in that thread.
    """
    data = threads_store.get(thread_id)
    if not data:
        raise HTTPException(404, "Thread not found")

    # SDK sends messages as an array of { role, content }
    last = ""
    msgs = data.get("messages")
    if isinstance(msgs, list) and msgs:
        last = msgs[-1].get("content", "")

    async def event_gen() -> AsyncGenerator[Dict[str, str], None]:
        async for chunk in llm.astream_events(last):
            yield {"data": chunk}

    return EventSourceResponse(event_gen())

@router.post("/runs/stream")
async def runs_stream(request: Request, llm=Depends(LLMDep)) -> Response:
    # 1) Read the raw bytes
    body_bytes = await request.body()
    raw = body_bytes.decode("utf-8", errors="ignore")
    print("🔍 runs_stream raw body:", raw)  # inspect in your API logs

    # 2) Try to parse JSON, but don't crash if empty/invalid
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    # 3) Look up thread payload (from POST /chat/threads)
    #    or fallback to the only thread we have
    thread_id = payload.get("threadId")
    if thread_id and thread_id in threads_store:
        thread_req = threads_store[thread_id]
    else:
        if not threads_store:
            raise HTTPException(400, "No thread available")
        # take the last-created thread
        _, thread_req = next(reversed(threads_store.items()))

    # 4) Extract last user message
    msgs = thread_req.get("messages", [])
    if not isinstance(msgs, list) or not msgs:
        raise HTTPException(400, "No messages in thread")
    last = msgs[-1].get("content", "")
    if not isinstance(last, str):
        raise HTTPException(400, "Last message content invalid")

    # 5) Stream the LLM tokens
    async def event_gen():
        async for chunk in llm.astream_events(last):
            yield {"data": chunk}

    return EventSourceResponse(event_gen())