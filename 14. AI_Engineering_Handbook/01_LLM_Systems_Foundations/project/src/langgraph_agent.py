"""The SAME ReAct loop, built with LangGraph's StateGraph.

Why show both? The from-scratch version proves you understand the mechanics; this
version shows you can express it in the framework the team actually uses. The graph
is two nodes with a conditional edge:

    START -> agent --(has tool calls & under budget)--> tools -> agent
                  \\--(final / out of budget)--> END

The "agent" node uses our offline RuleBasedBrain to emit an AIMessage with tool_calls
(exactly the shape a real LLM with `bind_tools` returns), so it runs with no API key.
The "tools" node runs our robust `execute_tool` and appends ToolMessages.
"""
from __future__ import annotations
import json
from typing import Annotated, Any, List, Optional, Tuple

from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from .tools import ToolRegistry
from .brain import RuleBasedBrain, Observation
from .robustness import execute_tool, ConfirmationRequired, ConfirmPolicy, deny_destructive
from .scratch_agent import Session


class AgentState(TypedDict):
    """LangGraph state. `add_messages` is a reducer that APPENDS new messages."""
    messages: Annotated[list, add_messages]
    iterations: int


def _observations_from_messages(messages: List[Any]) -> List[Observation]:
    """Rebuild the brain's (tool_name, python_result) list from ToolMessages."""
    obs: List[Observation] = []
    for m in messages:
        if isinstance(m, ToolMessage):
            try:
                obs.append((m.name, json.loads(m.content)))
            except json.JSONDecodeError:
                obs.append((m.name, m.content))
    return obs


def _first_human_query(messages: List[Any]) -> str:
    for m in messages:
        if isinstance(m, HumanMessage):
            return m.content
    return ""


def build_graph(
    registry: ToolRegistry,
    session: Session,
    *,
    brain: Optional[RuleBasedBrain] = None,
    max_iterations: int = 6,
    confirm: ConfirmPolicy = deny_destructive,
):
    """Compile and return a LangGraph app for the agent loop."""
    brain = brain or RuleBasedBrain()

    # --- node 1: the agent decides the next action ---
    def agent_node(state: AgentState) -> dict:
        query = _first_human_query(state["messages"])
        observations = _observations_from_messages(state["messages"])
        decision = brain.decide(query, observations)

        if decision.is_final:                                   # produce a plain answer
            return {"messages": [AIMessage(content=decision.final)]}

        # produce a tool call in the exact shape an LLM would emit
        call = {"name": decision.tool, "args": decision.args, "id": f"call_{state['iterations']}"}
        return {"messages": [AIMessage(content="", tool_calls=[call])],
                "iterations": state["iterations"] + 1}

    # --- node 2: run the requested tool(s) robustly ---
    def tools_node(state: AgentState) -> dict:
        last = state["messages"][-1]
        out = []
        for tc in last.tool_calls:
            tool = registry.get(tc["name"])
            try:
                result = execute_tool(tool, tc["args"], logger=session.logger,
                                      memo=session.memo, confirm=confirm)
                content = json.dumps(result, default=str)
            except ConfirmationRequired:
                content = json.dumps({"error": "needs_confirmation",
                                      "tool": tc["name"], "args": tc["args"]})
            out.append(ToolMessage(content=content, tool_call_id=tc["id"], name=tc["name"]))
        return {"messages": out}

    # --- routing: keep looping while there are tool calls and we're under budget ---
    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        has_calls = isinstance(last, AIMessage) and bool(getattr(last, "tool_calls", None))
        if has_calls and state["iterations"] < max_iterations:
            return "tools"
        return END                                             # final answer, or out of budget

    g = StateGraph(AgentState)
    g.add_node("agent", agent_node)
    g.add_node("tools", tools_node)
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    g.add_edge("tools", "agent")                                # observe -> think again
    return g.compile()


def run_query(app, query: str) -> str:
    """Invoke the compiled graph and return the final answer text."""
    final = app.invoke({"messages": [HumanMessage(content=query)], "iterations": 0})
    # The last AIMessage without tool calls is the synthesized answer.
    for m in reversed(final["messages"]):
        if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
            return m.content
    return ""
