"""LangGraph checkpointer for conversation state.

In-memory today. Swap with PostgresSaver / SqliteSaver for persistence.
"""

from langgraph.checkpoint.memory import MemorySaver


def build_checkpointer() -> MemorySaver:
    return MemorySaver()
