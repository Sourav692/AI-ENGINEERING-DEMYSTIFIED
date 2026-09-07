"""Tool registry + an in-memory 'DevRev' ticket backend.

A *tool* is the atomic thing an agent can call: a name, a human-readable
description (what the LLM reads to decide when to use it), the function itself,
and a `destructive` flag (delete / close / refund need a confirmation gate).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


# =====================================================================
# Custom exceptions used across the demo
# =====================================================================
class TransientError(Exception):
    """A temporary failure (network blip, 503) — safe to RETRY."""


class NotFoundError(Exception):
    """A permanent 'no such record' failure — do NOT retry; consider a fallback."""


# =====================================================================
# The Tool abstraction and its registry
# =====================================================================
@dataclass
class Tool:
    name: str                                   # unique id the agent references
    description: str                            # what the model reads to pick a tool
    func: Callable[..., Any]                    # the actual implementation
    destructive: bool = False                   # True -> requires confirmation before running

    def __call__(self, **kwargs) -> Any:
        return self.func(**kwargs)


class ToolRegistry:
    """A name -> Tool lookup, plus a `specs()` view for the model/prompt."""
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"no such tool: {name!r}")
        return self._tools[name]

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __iter__(self):
        return iter(self._tools.values())

    def specs(self) -> List[Dict[str, str]]:
        """What you'd feed an LLM so it knows which tools exist."""
        return [{"name": t.name, "description": t.description, "destructive": t.destructive}
                for t in self._tools.values()]


# =====================================================================
# A tiny in-memory backend so the tools do something real
# =====================================================================
class TicketStore:
    """Stands in for the DevRev API — just a dict of tickets in memory."""
    def __init__(self) -> None:
        self.tickets: Dict[str, dict] = {
            "TKT-1": {"id": "TKT-1", "subject": "Cannot log in",       "status": "open", "tags": ["auth"]},
            "TKT-2": {"id": "TKT-2", "subject": "Billing overcharge",  "status": "open", "tags": ["billing"]},
            "TKT-3": {"id": "TKT-3", "subject": "Login page 500 error", "status": "open", "tags": ["auth", "bug"]},
        }
        self._next = 4

    # --- read operations (safe) ---
    def search(self, query: str) -> List[dict]:
        q = (query or "").lower()
        hits = [t for t in self.tickets.values()
                if q in t["subject"].lower() or any(q in tag for tag in t["tags"])]
        return [{"id": t["id"], "subject": t["subject"], "status": t["status"]} for t in hits]

    def get(self, ticket_id: str) -> dict:
        if ticket_id not in self.tickets:
            raise NotFoundError(f"ticket {ticket_id!r} does not exist")
        return dict(self.tickets[ticket_id])

    # --- write operations ---
    def create(self, subject: str) -> dict:
        tid = f"TKT-{self._next}"; self._next += 1
        self.tickets[tid] = {"id": tid, "subject": subject, "status": "open", "tags": []}
        return dict(self.tickets[tid])

    def close(self, ticket_id: str) -> dict:            # DESTRUCTIVE
        if ticket_id not in self.tickets:
            raise NotFoundError(f"ticket {ticket_id!r} does not exist")
        self.tickets[ticket_id]["status"] = "closed"
        return dict(self.tickets[ticket_id])


def make_flaky(func: Callable[..., Any], fail_times: int = 2) -> Callable[..., Any]:
    """Wrap a function so it raises a TransientError its first `fail_times` calls.
    Used to demonstrate retry-with-backoff on a shaky dependency."""
    state = {"calls": 0}

    def wrapper(**kwargs):
        state["calls"] += 1
        if state["calls"] <= fail_times:
            raise TransientError(f"temporary outage (attempt {state['calls']})")
        return func(**kwargs)
    return wrapper


def build_registry(store: TicketStore, *, flaky_search: bool = False) -> ToolRegistry:
    """Assemble the DevRev-flavored toolset the agent can call."""
    reg = ToolRegistry()

    search_impl = store.search
    if flaky_search:                                    # optional: make search shaky for the retry demo
        search_impl = make_flaky(lambda query: store.search(query), fail_times=2)

    reg.register(Tool(
        "search_tickets",
        "Find open tickets whose subject or tags match a query string. Args: query (str).",
        lambda query: search_impl(query=query) if flaky_search else store.search(query),
    ))
    reg.register(Tool(
        "get_ticket",
        "Fetch full details of one ticket by its id. Args: ticket_id (str).",
        lambda ticket_id: store.get(ticket_id),
    ))
    reg.register(Tool(
        "create_ticket",
        "Create a new ticket with a subject. Args: subject (str).",
        lambda subject: store.create(subject),
    ))
    reg.register(Tool(
        "close_ticket",
        "Close (resolve) a ticket by id. DESTRUCTIVE — needs confirmation. Args: ticket_id (str).",
        lambda ticket_id: store.close(ticket_id),
        destructive=True,
    ))
    return reg
