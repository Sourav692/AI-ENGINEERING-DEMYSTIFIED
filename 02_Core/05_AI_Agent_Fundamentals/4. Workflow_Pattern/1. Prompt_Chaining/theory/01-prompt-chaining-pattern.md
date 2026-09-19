# Prompt Chaining Pattern

## What It Is

Prompt chaining runs a fixed sequence of LLM calls where the output of each
step feeds directly into the next. The **path is fixed by code** — step 2
always runs after step 1, every time, regardless of what step 1 produced.

The LLM fills in *content* at each step, but never decides *which step
happens next* or *whether to skip one*.

## When To Use It

- The task naturally decomposes into a known sequence of sub-tasks
- Each step benefits from a fresh, focused prompt rather than one giant prompt
- You want to insert a programmatic check between steps (e.g., validate step
  1's output before spending tokens on step 2)

## When *Not* To Use It

- If the right sequence of steps isn't knowable in advance → use a
  **planning agent** instead
- If a single well-crafted prompt already does the job — chaining adds
  latency and cost for no benefit

## Control Flow

```
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│ STEP 1  │ ───▶ │ STEP 2  │ ───▶ │ STEP 3  │ ───▶ │ OUTPUT  │
└─────────┘      └─────────┘      └─────────┘      └─────────┘
   fixed            fixed            fixed
  next step        next step        next step
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | The developer's code — always step N+1 |
| Cost/latency | Predictable — fixed number of calls |
| Failure mode | An early step's error propagates silently downstream |
| Typical guardrail | A programmatic check ("gate") between steps |

## LangGraph Implementation

Each node is a plain LLM call. Edges are unconditional (`add_edge`), not
conditional — the graph shape never changes at runtime.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic


class ChainState(TypedDict):
    raw_notes: str
    outline: str
    draft: str
    final: str


llm = ChatAnthropic(model="claude-sonnet-4-6")


# --- Step 1: turn raw notes into a structured outline ---
def outline_node(state: ChainState):
    response = llm.invoke(
        f"Turn these raw meeting notes into a structured outline:\n\n{state['raw_notes']}"
    )
    return {"outline": response.content}


# --- Gate: programmatic check before spending tokens on step 2 ---
def outline_is_valid(state: ChainState) -> bool:
    return len(state["outline"].strip()) > 20   # trivial example check


# --- Step 2: expand the outline into a draft ---
def draft_node(state: ChainState):
    response = llm.invoke(f"Expand this outline into a full draft:\n\n{state['outline']}")
    return {"draft": response.content}


# --- Step 3: polish the draft ---
def polish_node(state: ChainState):
    response = llm.invoke(f"Tighten and polish this draft for a leadership update:\n\n{state['draft']}")
    return {"final": response.content}


graph = StateGraph(ChainState)
graph.add_node("outline", outline_node)
graph.add_node("draft", draft_node)
graph.add_node("polish", polish_node)

graph.set_entry_point("outline")
graph.add_edge("outline", "draft")     # unconditional — always happens
graph.add_edge("draft", "polish")      # unconditional — always happens
graph.add_edge("polish", END)

app = graph.compile()

result = app.invoke({
    "raw_notes": "Talked about Q3 migration timeline, Barclays go-live slipping two weeks, need sign-off from compliance."
})
print(result["final"])
```

**Why this is a workflow and not an agentic pattern:** every `add_edge` call
is unconditional. The graph's shape — outline, then draft, then polish — is
fully determined before the first token is generated. Nothing in the code
asks the model "what should happen next?"

## Interview Angle

A common follow-up: *"Why not just use one big prompt?"*
- Smaller, focused prompts are easier to debug and iterate on independently
- You can insert cheap programmatic gates between steps (like `outline_is_valid`
  above) to fail fast before an expensive downstream call
- Each step can use a different model size — a cheap model for outlining, a
  stronger one for polish
