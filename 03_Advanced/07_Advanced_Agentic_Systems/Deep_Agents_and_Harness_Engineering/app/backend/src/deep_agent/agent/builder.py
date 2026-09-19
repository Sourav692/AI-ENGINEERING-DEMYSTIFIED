"""Wires the deep agent — model, tools, subagents, prompts, backend, checkpointer."""

from deepagents import create_deep_agent

from deep_agent.agent.backend import build_backend
from deep_agent.agent.checkpointer import build_checkpointer
from deep_agent.agent.model import build_model
from deep_agent.agent.prompts import ORCHESTRATOR_SYSTEM_PROMPT
from deep_agent.agent.subagents import SUBAGENTS
from deep_agent.tools.analytics import (
    ask_claims_analytics,
    ask_customer_analytics,
    ask_distribution_channels,
    ask_policy_underwriting,
)
from deep_agent.tools.memory import forget_memory, recall_memories, save_memory
from deep_agent.tools.projects import (
    list_project_files,
    name_project,
    write_project_file,
)
from deep_agent.tools.search import internet_search


ORCHESTRATOR_TOOLS = [
    name_project,
    write_project_file,
    list_project_files,
    internet_search,
    save_memory,
    recall_memories,
    forget_memory,
    ask_customer_analytics,
    ask_distribution_channels,
    ask_policy_underwriting,
    ask_claims_analytics,
]


_agent = None
_checkpointer = None


def build_agent():
    """Build (and cache) the orchestrator agent and its checkpointer."""
    global _agent, _checkpointer
    if _agent is not None:
        return _agent, _checkpointer

    _checkpointer = build_checkpointer()
    _agent = create_deep_agent(
        model=build_model(),
        tools=ORCHESTRATOR_TOOLS,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        skills=["/skills/"],
        subagents=SUBAGENTS,
        backend=build_backend(),
        checkpointer=_checkpointer,
    )
    return _agent, _checkpointer
