"""Lazy-loaded process singletons + in-memory thread registry.

Centralises shared mutable state used across API routers so we don't
re-instantiate the agent / memory store per request.
"""

import logging
import traceback

logger = logging.getLogger("deep-agent")


# ============ Agent ============
_agent = None
_checkpointer = None
_agent_init_error: str | None = None
_agent_init_attempted = False


def get_agent():
    """Lazy-load the agent on first use. Returns (agent, checkpointer) or (None, None)."""
    global _agent, _checkpointer, _agent_init_error, _agent_init_attempted
    if _agent_init_attempted:
        return _agent, _checkpointer
    _agent_init_attempted = True
    try:
        logger.info("Initializing agent...")
        from deep_agent.agent.builder import build_agent
        _agent, _checkpointer = build_agent()
        logger.info("Agent initialized")
    except Exception as e:
        _agent_init_error = f"{e}\n{traceback.format_exc()}"
        logger.error(f"Agent init failed: {_agent_init_error}")
    return _agent, _checkpointer


def agent_init_status() -> dict:
    return {
        "agent_loaded": _agent is not None,
        "init_attempted": _agent_init_attempted,
        "init_error": _agent_init_error,
    }


# ============ Memory store ============
_memory_db = None
_memory_init_attempted = False


def get_memory_store():
    """Lazy-load the memory store. Returns None if init failed."""
    global _memory_db, _memory_init_attempted
    if _memory_init_attempted:
        return _memory_db
    _memory_init_attempted = True
    try:
        from deep_agent.stores.lakebase import get_memory_db
        _memory_db = get_memory_db()
        _memory_db.ensure_table()
    except Exception as e:
        logger.error(f"Memory store init failed: {e}", exc_info=True)
        _memory_db = None
    return _memory_db


# ============ In-memory thread registry ============
# NOTE: lost on restart — swap for Postgres-backed checkpointer when needed.
threads: dict[str, dict] = {}
