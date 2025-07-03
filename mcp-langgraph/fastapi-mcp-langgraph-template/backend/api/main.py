from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from api.core.agent.orchestration import get_graph
from api.core.agent.tools import get_tools  # your tools loader
from langchain_openai import ChatOpenAI

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/api/messages")
async def run_graph(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    llm = ChatOpenAI(model="gpt-4o")  # or Gemini when hooked
    tools = get_tools()  # adapt if needed
    graph = get_graph(llm=llm, tools=tools)

    result = graph.invoke({"messages": [HumanMessage(content=user_message)], "next": "agent_node"})
    return {"response": result["messages"][-1].content}
