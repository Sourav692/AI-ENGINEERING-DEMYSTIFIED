"""Chat endpoint — SSE-streamed agent responses.

Wraps the synchronous ``agent.stream(...)`` iterator in a background thread and
bridges it into an async generator. The async generator periodically emits SSE
comment heartbeats so the connection stays alive while subagents do long-running
work (otherwise browsers / proxies time out the idle TCP stream after ~30-120s).

``subgraphs=True`` is required so events produced inside subagent graphs (the
``task`` tool's invocations) reach this stream — without it, the user sees dead
air for the whole subagent run.
"""

import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import BaseMessage

from deep_agent.api.schemas import ChatRequest
from deep_agent.runtime import agent_init_status, get_agent, threads

logger = logging.getLogger("deep-agent")

router = APIRouter(prefix="/api", tags=["chat"])


# Send a SSE comment line every this many seconds of silence to keep the
# connection alive. Must be lower than typical proxy idle timeouts (~30-60s).
HEARTBEAT_INTERVAL = 10.0

# Sentinel pushed onto the queue when the agent iterator is exhausted.
_AGENT_DONE = object()


def _format_event(mode: str, payload, node_namespace: tuple) -> str | None:
    """Translate a single LangGraph stream event into an SSE data line, or None to skip."""
    # When subgraphs=True is set, every yielded event is namespaced — the
    # node_namespace tuple identifies which (sub)graph emitted it. We surface
    # the deepest namespace component as the node label so the UI can show
    # which subagent is active.
    namespace_label = node_namespace[-1] if node_namespace else ""

    if mode == "messages":
        message, metadata = payload
        if not isinstance(message, BaseMessage):
            return None
        node = namespace_label or metadata.get("langgraph_node", "")
        if message.type != "AIMessageChunk":
            return None
        content = message.content if isinstance(message.content, str) else ""
        tool_calls = None
        if getattr(message, "tool_call_chunks", None):
            tool_calls = [
                {"name": tc.get("name", ""), "args": tc.get("args", {})}
                for tc in message.tool_call_chunks
                if tc.get("name")
            ]
        if not (content or tool_calls):
            return None
        event_data = {"node": node, "type": "ai", "content": content}
        if tool_calls:
            event_data["tool_calls"] = tool_calls
        return f"data: {json.dumps(event_data)}\n\n"

    if mode == "updates":
        for node_name, update in payload.items():
            if not update:
                continue
            messages = update.get("messages", [])
            if not isinstance(messages, list):
                messages = [messages]
            for message in messages:
                if not isinstance(message, BaseMessage):
                    continue
                if message.type == "tool":
                    event_data = {
                        "node": namespace_label or node_name,
                        "type": "tool",
                        "content": (
                            message.content
                            if isinstance(message.content, str)
                            else str(message.content)
                        ),
                    }
                    return f"data: {json.dumps(event_data)}\n\n"
    return None


@router.post("/chat")
async def chat(request: ChatRequest):
    """Stream agent responses as Server-Sent Events."""
    agent, _ = get_agent()
    if not agent:
        return JSONResponse(
            status_code=503,
            content={"detail": f"Agent not initialized: {agent_init_status()['init_error']}"},
        )

    thread_id = request.thread_id
    if thread_id not in threads:
        threads[thread_id] = {
            "id": thread_id,
            "title": request.message[:50],
            "created_at": datetime.now().isoformat(),
        }

    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 100}
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def producer():
        """Consume the sync agent iterator in a thread, push events to the queue."""
        n = 0
        try:
            for event in agent.stream(
                {"messages": [{"role": "user", "content": request.message}]},
                config,
                stream_mode=["updates", "messages"],
                subgraphs=True,
            ):
                n += 1
                # With subgraphs=True, events are 3-tuples: (namespace, mode, payload).
                # Without it (or if a version doesn't namespace), fall back to 2-tuple.
                if isinstance(event, tuple) and len(event) == 3:
                    ns, mode, payload = event
                else:
                    ns, (mode, payload) = (), event
                asyncio.run_coroutine_threadsafe(queue.put((mode, payload, ns)), loop)
        except Exception as e:
            logger.error(f"[chat] producer error after {n} events: {e}", exc_info=True)
            asyncio.run_coroutine_threadsafe(queue.put(("__error__", str(e), ())), loop)
        finally:
            logger.info(f"[chat] producer finished after {n} events")
            asyncio.run_coroutine_threadsafe(queue.put((_AGENT_DONE, None, ())), loop)

    async def event_stream():
        logger.info(f"[chat] starting stream thread_id={thread_id}")
        loop.run_in_executor(None, producer)
        try:
            while True:
                try:
                    mode, payload, ns = await asyncio.wait_for(
                        queue.get(), timeout=HEARTBEAT_INTERVAL
                    )
                except asyncio.TimeoutError:
                    # Silence on the queue -> keep the connection alive.
                    yield ": heartbeat\n\n"
                    continue

                if mode is _AGENT_DONE:
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return
                if mode == "__error__":
                    yield f"data: {json.dumps({'type': 'error', 'content': payload})}\n\n"
                    return

                line = _format_event(mode, payload, ns)
                if line is not None:
                    yield line
        except asyncio.CancelledError:
            logger.info("[chat] client disconnected")
            raise

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
