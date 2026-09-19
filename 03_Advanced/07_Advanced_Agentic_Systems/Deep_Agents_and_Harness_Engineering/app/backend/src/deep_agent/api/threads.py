"""Thread management — create, list, rename, delete, fetch history."""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage

from deep_agent.api.schemas import ThreadCreate, ThreadRename
from deep_agent.runtime import get_agent, threads

router = APIRouter(prefix="/api/threads", tags=["threads"])


@router.post("")
async def create_thread(request: ThreadCreate):
    thread_id = str(uuid.uuid4())
    threads[thread_id] = {
        "id": thread_id,
        "title": request.title,
        "created_at": datetime.now().isoformat(),
    }
    return threads[thread_id]


@router.get("")
async def list_threads():
    return list(threads.values())


@router.get("/{thread_id}/messages")
async def get_thread_messages(thread_id: str):
    """Retrieve the message history for a thread from the checkpointer."""
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    agent, _ = get_agent()
    if not agent:
        return []

    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 100}
    try:
        state = agent.get_state(config)
        if not state or not state.values:
            return []

        result = []
        for msg in state.values.get("messages", []):
            if isinstance(msg, HumanMessage):
                result.append({
                    "role": "user",
                    "content": msg.content if isinstance(msg.content, str) else str(msg.content),
                })
            elif isinstance(msg, AIMessage):
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                if content:
                    entry = {"role": "assistant", "content": content}
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        entry["tool_calls"] = [
                            {"name": tc["name"], "args": tc.get("args", {})}
                            for tc in msg.tool_calls
                        ]
                    if hasattr(msg, "name") and msg.name:
                        entry["node"] = msg.name
                    result.append(entry)
            elif hasattr(msg, "type") and msg.type == "tool":
                result.append({
                    "role": "tool",
                    "content": msg.content if isinstance(msg.content, str) else str(msg.content),
                })
        return result
    except Exception:
        return []


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str):
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    deleted = threads.pop(thread_id)
    return {"deleted": deleted}


@router.patch("/{thread_id}")
async def rename_thread(thread_id: str, request: ThreadRename):
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    threads[thread_id]["title"] = request.title
    return threads[thread_id]
