# Parallelization Pattern

## What It Is

Parallelization runs multiple LLM calls **concurrently** instead of one after
another. There are two common variants:

- **Sectioning**: split a task into independent subtasks, run them in
  parallel, then combine the results (e.g., review a document for tone,
  factual accuracy, and grammar — simultaneously, by three separate calls)
- **Voting**: run the *same* task multiple times in parallel and aggregate
  the answers (e.g., majority vote, or pick the most common classification)

Like all workflow patterns, the fan-out and fan-in points are fixed in code —
the graph always launches the same set of parallel branches and always
combines them the same way.

## When To Use It

- Independent subtasks that don't depend on each other's output
  (sectioning) — this reduces wall-clock latency versus running them in
  sequence
- Tasks where a single LLM call is noisy and you want redundancy
  (voting) — trades tokens for reliability

## When *Not* To Use It

- If subtasks genuinely depend on each other's output → they can't run in
  parallel; use prompt chaining instead
- If the extra calls (and cost) aren't justified by a real latency or
  reliability win

## Control Flow

```
                     ┌─────────┐
                ┌───▶│ BRANCH A │───┐
┌─────────┐     │    └─────────┘    │    ┌─────────┐
│  INPUT  │ ────┼───▶│ BRANCH B │───┼───▶│ COMBINE │
└─────────┘     │    └─────────┘    │    └─────────┘
                └───▶│ BRANCH C │───┘
                     └─────────┘

  all branches launch together — fixed fan-out, fixed fan-in
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | Code — all branches always run, always combined the same way |
| Cost/latency | Higher token cost, but lower wall-clock latency than sequential |
| Failure mode | One slow/failed branch blocks the combine step |
| Typical guardrail | Per-branch timeout; combine step tolerates partial failures |

## LangGraph Implementation

LangGraph runs nodes with no ordering dependency between them concurrently
when the graph fans out from one node to several with no edges between the
parallel nodes themselves — they all feed into a shared combine node.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic


class ReviewState(TypedDict):
    document: str
    tone_review: str
    factual_review: str
    grammar_review: str
    combined: str


llm = ChatAnthropic(model="claude-sonnet-4-6")


# --- Three independent branches — sectioning ---
def tone_node(state: ReviewState):
    response = llm.invoke(f"Review the tone of this document:\n\n{state['document']}")
    return {"tone_review": response.content}

def factual_node(state: ReviewState):
    response = llm.invoke(f"Check this document for factual inconsistencies:\n\n{state['document']}")
    return {"factual_review": response.content}

def grammar_node(state: ReviewState):
    response = llm.invoke(f"Review this document for grammar issues:\n\n{state['document']}")
    return {"grammar_review": response.content}


# --- Fixed combine step — always runs after all three finish ---
def combine_node(state: ReviewState):
    response = llm.invoke(
        "Combine these three reviews into one prioritized action list:\n\n"
        f"Tone review: {state['tone_review']}\n\n"
        f"Factual review: {state['factual_review']}\n\n"
        f"Grammar review: {state['grammar_review']}"
    )
    return {"combined": response.content}


graph = StateGraph(ReviewState)
graph.add_node("tone", tone_node)
graph.add_node("factual", factual_node)
graph.add_node("grammar", grammar_node)
graph.add_node("combine", combine_node)

# fan-out: entry point feeds all three branches
graph.set_entry_point("tone")           # LangGraph requires one entry;
graph.add_edge("tone", "combine")        # a common pattern is a trivial
graph.add_edge("factual", "combine")     # "start" node that fans out —
graph.add_edge("grammar", "combine")     # shown simplified here
graph.add_edge("combine", END)

# To truly fan out from a single entry, add a no-op start node:
# graph.set_entry_point("start")
# graph.add_edge("start", "tone")
# graph.add_edge("start", "factual")
# graph.add_edge("start", "grammar")

app = graph.compile()

result = app.invoke({"document": "Q3 update: revenue grew 12%, though churn ticked up slightly in EMEA..."})
print(result["combined"])
```

**Why this is a workflow and not an agentic pattern:** the set of parallel
branches (`tone`, `factual`, `grammar`) is fixed in the graph definition.
Nothing decides at runtime to add a fourth branch or skip one — the fan-out
and fan-in are structural, not judgment calls.

## Interview Angle

A common follow-up: *"How do you handle one branch failing or timing out?"*
- Wrap each branch call with a timeout and a default/fallback value
- Design `combine_node` to tolerate a missing review rather than crashing
- For voting variants, use a quorum (e.g., 2 of 3 agree) rather than requiring
  unanimous results
