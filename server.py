"""FastAPI server with SSE streaming for the LangGraph Code Agent."""

import json
import os
import uuid

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

if not os.getenv("DASHSCOPE_API_KEY"):
    raise RuntimeError("DASHSCOPE_API_KEY not found in .env")

from agent.graph import agent_graph  # noqa: E402

app = FastAPI(title="Code Agent API")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    thread_id: str
    success: bool


def _sse_events(thread_id: str, message: str):
    """Generator that yields SSE-formatted events from agent_graph.astream()."""
    config = {"configurable": {"thread_id": thread_id}}

    try:
        for event in agent_graph.stream(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            stream_mode="values",
        ):
            messages = event.get("messages", [])
            if not messages:
                continue

            last_msg = messages[-1]

            # Tool call events
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    yield f"event: tool_call\ndata: {json.dumps({'id': tc['id'], 'name': tc['name'], 'args': tc['args']}, ensure_ascii=False)}\n\n"

            # Tool result events
            if hasattr(last_msg, "tool_call_id") and last_msg.tool_call_id:
                content = last_msg.content if hasattr(last_msg, "content") else ""
                yield f"event: tool_result\ndata: {json.dumps({'tool_call_id': last_msg.tool_call_id, 'content': content[:2000]}, ensure_ascii=False)}\n\n"

            # Text message events (assistant final response)
            if (
                hasattr(last_msg, "content")
                and last_msg.content
                and not getattr(last_msg, "tool_calls", None)
            ):
                # Only send if this is a non-tool message (type == "ai" or similar)
                msg_type = getattr(last_msg, "type", "")
                if msg_type in ("ai", "assistant") or not hasattr(last_msg, "tool_call_id"):
                    content = last_msg.content
                    yield f"event: message\ndata: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

        yield "event: done\ndata: {}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"


@app.get("/")
async def serve_frontend():
    """Serve the chat frontend."""
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.post("/api/chat")
async def chat(req: ChatRequest):
    thread_id = req.thread_id or str(uuid.uuid4())
    return StreamingResponse(
        _sse_events(thread_id, req.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Thread-Id": thread_id,
        },
    )


@app.post("/api/chat/new")
async def new_chat():
    """Create a new conversation session."""
    thread_id = str(uuid.uuid4())
    return ChatResponse(thread_id=thread_id, success=True)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=9000, reload=False)
