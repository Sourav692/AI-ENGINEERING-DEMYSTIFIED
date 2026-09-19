# Multi-Agent / Agent-as-Tool Pattern

## What It Is

A supervisor (or "orchestrator") agent delegates subtasks to other
**autonomous** agents — each sub-agent runs its own reasoning loop (often its
own ReAct loop internally) and makes independent decisions about how to
complete its piece, rather than following a fixed sub-routine.

This is the agentic cousin of the workflow "orchestrator-workers" pattern.
The difference: in the workflow version, the orchestrator decomposes the task
into a fixed set of well-understood subtasks dispatched to workers that just
execute. In the agentic version, both the **supervisor's delegation
decisions** and **each sub-agent's internal execution** are open-ended — the
supervisor can decide mid-run to loop back to an agent, add a new sub-agent
call, or change its own plan based on what a sub-agent reports back.

## When To Use It

- Distinct domains of expertise needed (e.g., a "research agent" +
  a "coding agent" + a "review agent")
- Tasks large enough that a single agent's context window / focus degrades
- When sub-agents genuinely need autonomy (not just a fixed function call)

## When *Not* To Use It

- If sub-tasks are simple, well-scoped, and don't need their own reasoning
  loop → dispatch them as plain tool calls or workflow workers instead
- Small tasks — multi-agent overhead (coordination, context-passing) isn't
  worth it below a certain complexity

## Control Flow

```
                 ┌────────────┐
                 │ SUPERVISOR │
                 └─────┬──────┘
                        │ decides which agent, if any
       ┌────────────────┼────────────────┐
       ▼                 ▼                 ▼
 ┌───────────┐    ┌────────────┐   ┌─────────────┐
 │ RESEARCH  │    │   CODE     │   │   REVIEW    │
 │  AGENT    │    │   AGENT    │   │   AGENT     │
 │ (own loop)│    │ (own loop) │   │  (own loop) │
 └─────┬─────┘    └─────┬──────┘   └──────┬──────┘
       └────────────────┼──────────────────┘
                        ▼
                 ┌────────────┐
                 │ SUPERVISOR │  (decides: done, or delegate again)
                 └─────┬──────┘
                        ▼
                  ┌──────────┐
                  │  RETURN  │
                  └──────────┘
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | Supervisor decides delegation; each sub-agent controls its own internal loop |
| Cost/latency | Highest of all patterns — nested unpredictability |
| Failure mode | Sub-agents contradicting each other; supervisor delegation thrash |
| Typical guardrail | Per-agent step budgets; supervisor delegation cap |

## LangGraph Implementation

The supervisor is itself an LLM call with structured output choosing the
next agent (or "finish"). Each specialist is a small sub-graph (its own
ReAct-style loop) invoked as a node.

```python
from typing import Annotated, TypedDict, Literal
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field


class SupervisorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    next_agent: str
    delegations: int


llm = ChatAnthropic(model="claude-sonnet-4-6")


class Routing(BaseModel):
    next_agent: Literal["research", "code", "review", "finish"] = Field(
        description="which specialist should act next, or finish if the task is complete"
    )
    instructions: str = Field(description="what this specialist should do")


router_llm = llm.with_structured_output(Routing)


# --- Supervisor: decides which autonomous specialist runs next ---
def supervisor_node(state: SupervisorState):
    routing: Routing = router_llm.invoke(
        [HumanMessage(content=(
            "Conversation so far:\n"
            + "\n".join(f"{m.type}: {m.content}" for m in state["messages"])
            + "\n\nDecide which specialist should act next, or finish."
        ))]
    )
    return {
        "next_agent": routing.next_agent,
        "messages": [HumanMessage(content=f"[supervisor -> {routing.next_agent}] {routing.instructions}")],
        "delegations": state.get("delegations", 0) + 1,
    }


# --- Each specialist is its own autonomous agent (simplified: single reasoning call) ---
# In production each of these would be its own compiled ReAct sub-graph with its own tools.
def research_agent(state: SupervisorState):
    response = llm.invoke(state["messages"] + [HumanMessage(content="Act as the research specialist.")])
    return {"messages": [response]}

def code_agent(state: SupervisorState):
    response = llm.invoke(state["messages"] + [HumanMessage(content="Act as the coding specialist.")])
    return {"messages": [response]}

def review_agent(state: SupervisorState):
    response = llm.invoke(state["messages"] + [HumanMessage(content="Act as the review specialist.")])
    return {"messages": [response]}


def route_from_supervisor(state: SupervisorState):
    if state["delegations"] >= 6:          # safety net against delegation thrash
        return END
    return state["next_agent"] if state["next_agent"] != "finish" else END


graph = StateGraph(SupervisorState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("research", research_agent)
graph.add_node("code", code_agent)
graph.add_node("review", review_agent)

graph.set_entry_point("supervisor")
graph.add_conditional_edges("supervisor", route_from_supervisor, {
    "research": "research", "code": "code", "review": "review", END: END
})
# every specialist reports back to the supervisor, which decides what's next
graph.add_edge("research", "supervisor")
graph.add_edge("code", "supervisor")
graph.add_edge("review", "supervisor")

app = graph.compile()

result = app.invoke({
    "messages": [HumanMessage(content="Build and validate a Delta Live Tables pipeline for claims ingestion.")],
    "delegations": 0
})
for m in result["messages"]:
    m.pretty_print()
```

**Why this is agentic multi-agent and not a fixed orchestrator-workers
workflow:** the supervisor's routing decision (`Routing.next_agent`) is a
fresh LLM judgment every time it runs, so the same task can visit `code` zero
times or three times depending on what specialists report back — there's no
hardcoded dispatch table.

## Interview Angle

A common follow-up: *"How do you stop agents from talking past each other or
looping indefinitely?"*
- Cap total delegations (shown above: 6) as a hard ceiling
- Give the supervisor visibility into full history, not just the last
  message, so it can detect repetition
- Consider a shared scratchpad/state object instead of passing full message
  history to every specialist, to control context growth
