# Orchestrator-Workers Pattern

## What It Is

A central orchestrator LLM call breaks a task into a set of subtasks, then
dispatches each subtask to a worker LLM call. Unlike Parallelization,
subtasks aren't fixed at graph-build time — the orchestrator **decides the
decomposition at runtime** based on the specific input. But unlike the
agentic Multi-Agent pattern, workers here are simple, single-purpose calls
that execute their assigned piece and return — they don't run their own
autonomous reasoning loop or decide to delegate further.

This pattern sits in between: more flexible than a fixed parallel fan-out,
but the workers themselves have no autonomy of their own.

## When To Use It

- Tasks where the number and nature of subtasks can't be known in advance,
  but each subtask, once identified, is a straightforward single LLM call
- Document-level tasks like "summarize each relevant section" where the
  orchestrator first has to figure out what "each relevant section" even
  means for this specific document
- When you want dynamic fan-out (unlike Parallelization's fixed branches)
  without full worker autonomy (unlike Multi-Agent)

## When *Not* To Use It

- If the subtasks are always the same regardless of input → use fixed
  **Parallelization** instead, it's simpler and doesn't need a decomposition
  call
- If workers genuinely need to reason, use tools, or make their own
  decisions mid-task → use the agentic **Multi-Agent** pattern instead
- If there's naturally only one subtask — this adds an orchestration call
  for no benefit

## Control Flow

```
                ┌──────────────┐
                │ ORCHESTRATOR │  (decides decomposition at runtime)
                └──────┬───────┘
                        │ produces a dynamic list of subtasks
       ┌─────────────────┼─────────────────┐
       ▼                  ▼                  ▼
 ┌───────────┐     ┌───────────┐     ┌───────────┐
 │  WORKER   │     │  WORKER   │     │  WORKER   │   ← number of these
 │ (task 1)  │     │ (task 2)  │     │ (task N)  │     is decided at
 └─────┬─────┘     └─────┬─────┘     └─────┬─────┘     runtime, not fixed
       └──────────────────┼──────────────────┘
                           ▼
                    ┌────────────┐
                    │  SYNTHESIS  │
                    └────────────┘

  workers execute their assigned piece and return — no autonomy of their own
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | Orchestrator decides *what* the subtasks are, at runtime |
| Cost/latency | Variable — depends on how many subtasks get generated |
| Failure mode | Orchestrator over- or under-decomposes the task |
| Typical guardrail | Cap on max subtasks; validate decomposition before dispatch |

## How This Differs From Its Neighbors

| | Parallelization | Orchestrator-Workers | Multi-Agent (agentic) |
|---|---|---|---|
| Branch count | Fixed at build time | Decided at runtime by orchestrator | Decided at runtime by supervisor |
| Worker autonomy | None — single call | None — single call | Full — own reasoning loop |
| Can a worker call more workers? | No | No | Yes, indirectly via re-delegation |

## LangGraph Implementation

The orchestrator produces a structured list of subtasks via structured
output. LangGraph's `Send` API is used to fan out a *variable* number of
worker invocations — this is what distinguishes it from Parallelization's
fixed `add_edge` calls to a known set of nodes.

```python
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langgraph.constants import Send
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field


class OrchestratorState(TypedDict):
    document: str
    subtasks: list[str]
    worker_results: Annotated[list[str], operator.add]   # workers append here
    synthesis: str


class WorkerState(TypedDict):
    subtask: str
    document: str


llm = ChatAnthropic(model="claude-sonnet-4-6")


class Decomposition(BaseModel):
    subtasks: list[str] = Field(
        description="a dynamic list of focused sub-questions or sections to address, "
                    "sized to what THIS document actually needs"
    )


orchestrator_llm = llm.with_structured_output(Decomposition)


# --- Orchestrator: decides the decomposition at runtime, not build time ---
def orchestrator_node(state: OrchestratorState):
    result: Decomposition = orchestrator_llm.invoke(
        f"Break this document into the sections that need individual summaries. "
        f"Only include sections that are substantive enough to need one.\n\n{state['document']}"
    )
    return {"subtasks": result.subtasks}


# --- Fan out to a variable number of workers using Send ---
def dispatch_to_workers(state: OrchestratorState):
    return [
        Send("worker", {"subtask": subtask, "document": state["document"]})
        for subtask in state["subtasks"]
    ]


# --- Worker: a single, focused call — no reasoning loop, no delegation ---
def worker_node(state: WorkerState):
    response = llm.invoke(
        f"Focusing only on this aspect: '{state['subtask']}', "
        f"write a concise summary from this document:\n\n{state['document']}"
    )
    return {"worker_results": [response.content]}


# --- Synthesis: fixed step, always runs after all workers finish ---
def synthesis_node(state: OrchestratorState):
    combined = "\n\n".join(state["worker_results"])
    response = llm.invoke(f"Combine these section summaries into one coherent overview:\n\n{combined}")
    return {"synthesis": response.content}


graph = StateGraph(OrchestratorState)
graph.add_node("orchestrator", orchestrator_node)
graph.add_node("worker", worker_node)
graph.add_node("synthesis", synthesis_node)

graph.set_entry_point("orchestrator")
graph.add_conditional_edges("orchestrator", dispatch_to_workers, ["worker"])
graph.add_edge("worker", "synthesis")
graph.add_edge("synthesis", END)

app = graph.compile()

result = app.invoke({
    "document": "Section 1: Netezza migration timeline... Section 2: compliance sign-off requirements... Section 3: rollback plan...",
    "worker_results": []
})
print(f"Orchestrator identified {len(result['subtasks'])} subtasks")
print(result["synthesis"])
```

**Why this is a workflow and not agentic Multi-Agent:** the orchestrator
decides *how many* workers and *what* they each do, but every worker is a
single, stateless LLM call that returns its result and terminates — it
cannot decide to call a tool in a loop, delegate to another worker, or run
its own multi-step reasoning. The autonomy stops at the orchestrator; the
`Send` fan-out is dynamic, but each destination node's *behavior* is fixed.

## Interview Angle

A common follow-up: *"How is this different from Multi-Agent delegation if
both decide things at runtime?"*
- Orchestrator-Workers: only the *decomposition* is dynamic — workers are
  simple, interchangeable, single-call functions
- Multi-Agent: both the *delegation* and each *specialist's internal
  execution* are dynamic — a specialist can itself loop, call tools, or ask
  to be delegated to again
- Rule of thumb: if a "worker" could be swapped for a plain function with a
  fixed prompt template, you're in Orchestrator-Workers; if it needs its own
  judgment mid-task, you're in Multi-Agent
