"""
LangGraph ReAct (tool-calling) agent — production-shaped reference implementation.

Two builds in one file:
  1. build_from_scratch() -> explicit StateGraph loop  (full control, custom router, step budget)
  2. build_prebuilt()     -> langchain.agents.create_agent one-liner (LangChain 1.x)

Install:
    pip install -U langgraph "langchain>=1.0" langchain-anthropic

Env:
    export ANTHROPIC_API_KEY=sk-ant-...

Run:
    python langgraph_react_agent.py
"""

from __future__ import annotations

import ast
import operator
from typing import Annotated, Literal, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

MODEL = "claude-sonnet-4-6"
MAX_MODEL_STEPS = 8  # hard budget: stops runaway tool loops before token spend explodes

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a data platform assistant.\n"
        "- Use tools whenever a fact could be looked up or computed; never guess numbers.\n"
        "- You may call multiple tools in one turn when they are independent.\n"
        "- If a tool errors, read the error, fix your arguments, and retry at most once.\n"
        "- Finish with a short, direct answer that cites which tool produced each number."
    )
)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Tools
#    Docstring + type hints ARE the schema sent to the model. Write them for an LLM
#    reader: say when to use the tool, what units come back, and how it fails.
# ──────────────────────────────────────────────────────────────────────────────

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression: arithmetic literals and + - * / ** % only.")


@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression and return the numeric result.

    Use for any arithmetic instead of computing mentally.
    Supports + - * / ** % and parentheses over numeric literals, e.g. "(1240 - 870) / 870 * 100".
    Raises ValueError on anything else (no names, no function calls).
    """
    return str(_eval(ast.parse(expression, mode="eval").body))


@tool
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """Semantic search over the internal engineering knowledge base.

    Use for questions about internal architecture, runbooks, and past incidents.
    Returns up to `top_k` chunks as "score | title | snippet" lines, best match first.
    Returns "NO_RESULTS" when nothing clears the relevance threshold — do not invent an answer then.
    """
    corpus = [
        (0.91, "Ingestion runbook", "Bronze autoloader retries 3x with exponential backoff."),
        (0.78, "Cost review Q2", "NRT pipeline runtime cut from 150 min to 87 min after repartition."),
        (0.64, "Streaming SLA", "p99 end-to-end latency target is 90 seconds."),
    ]
    hits = corpus[: max(1, min(top_k, len(corpus)))]






































































































































































































































    return "\n".join(f"{s:.2f} | {t} | {snip}" for s, t, snip in hits) or "NO_RESULTS"


@tool
def get_pipeline_metric(pipeline: str, metric: Literal["runtime_min", "cost_usd", "rows"]) -> str:
    """Fetch the latest value of a metric for a named pipeline.

    Valid pipelines: "nrt_ingest", "batch_reconcile".
    Raises ValueError for unknown pipeline names — call search_knowledge_base to find the right name.
    """
    table = {
        "nrt_ingest": {"runtime_min": 87, "cost_usd": 412.50, "rows": 18_400_000},
        "batch_reconcile": {"runtime_min": 150, "cost_usd": 980.00, "rows": 42_100_000},
    }
    if pipeline not in table:
        raise ValueError(f"Unknown pipeline '{pipeline}'. Known: {list(table)}")
    return f"{pipeline}.{metric} = {table[pipeline][metric]}"


TOOLS = [calculator, search_knowledge_base, get_pipeline_metric]


# ──────────────────────────────────────────────────────────────────────────────
# 2. State
#    `add_messages` is a reducer: nodes return only the NEW messages and LangGraph
#    appends them (matching on id, so a re-emitted message updates in place).
#    `steps` is a plain int -> last write wins, which is what a counter wants.
# ──────────────────────────────────────────────────────────────────────────────


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    steps: int


# ──────────────────────────────────────────────────────────────────────────────
# 3. Hand-rolled ReAct graph
# ──────────────────────────────────────────────────────────────────────────────


def build_from_scratch(checkpointer=None):
    llm = ChatAnthropic(model=MODEL, temperature=0, max_tokens=2048)
    llm_with_tools = llm.bind_tools(TOOLS)  # parallel_tool_calls defaults on for Anthropic

    def agent_node(state: AgentState) -> dict:
        """Reason: one model call over the full transcript. This is the 'Thought' step."""
        response = llm_with_tools.invoke([SYSTEM_PROMPT, *state["messages"]])
        return {"messages": [response], "steps": state.get("steps", 0) + 1}

    # handle_tool_errors=True turns an exception into a ToolMessage the model can read
    # and self-correct from, instead of crashing the whole graph run.
    tool_node = ToolNode(TOOLS, handle_tool_errors=True)

    def route(state: AgentState) -> Literal["tools", "__end__"]:
        """Act-or-answer decision. Equivalent to langgraph.prebuilt.tools_condition,
        written out so the step budget can be enforced in the same place."""
        last = state["messages"][-1]
        if state.get("steps", 0) >= MAX_MODEL_STEPS:
            return END  # budget blown: return whatever the model has so far
        if getattr(last, "tool_calls", None):
            return "tools"
        return END

    graph = (
        StateGraph(AgentState)
        .add_node("agent", agent_node)
        .add_node("tools", tool_node)
        .add_edge(START, "agent")
        .add_conditional_edges("agent", route, {"tools": "tools", END: END})
        .add_edge("tools", "agent")  # <- the loop that makes it ReAct
    )

    # interrupt_before=["tools"] turns this into human-in-the-loop approval.
    return graph.compile(checkpointer=checkpointer)


# ──────────────────────────────────────────────────────────────────────────────
# 4. Prebuilt equivalent
#    langgraph.prebuilt.create_react_agent still works but is deprecated in favour
#    of langchain.agents.create_agent, which wraps the same loop plus middleware.
# ──────────────────────────────────────────────────────────────────────────────


def build_prebuilt(checkpointer=None):
    from langchain.agents import create_agent

    return create_agent(
        model=MODEL,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT.content,
        checkpointer=checkpointer,
        # middleware=[SummarizationMiddleware(...), HumanInTheLoopMiddleware(...)]
    )


# ──────────────────────────────────────────────────────────────────────────────
# 5. Run it
# ──────────────────────────────────────────────────────────────────────────────


def main() -> None:
    checkpointer = InMemorySaver()  # swap for SqliteSaver / PostgresSaver in prod
    app = build_from_scratch(checkpointer=checkpointer)

    print(app.get_graph().draw_ascii())  # or .draw_mermaid()

    config = {
        "configurable": {"thread_id": "sourav-session-1"},
        "recursion_limit": 25,  # graph-level superstep cap, separate from MAX_MODEL_STEPS
    }

    turns = [
        "By what percent is nrt_ingest faster than batch_reconcile on runtime?",
        "And what's the cost difference in dollars?",  # relies on checkpointed history
    ]

    for user_msg in turns:
        print(f"\n=== USER: {user_msg}")
        for chunk in app.stream(
            {"messages": [{"role": "user", "content": user_msg}]},
            config=config,
            stream_mode="values",
        ):
            chunk["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
