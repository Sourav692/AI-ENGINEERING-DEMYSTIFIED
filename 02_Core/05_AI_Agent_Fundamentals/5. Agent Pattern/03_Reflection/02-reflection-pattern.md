# Reflection Pattern

## What It Is

Reflection has the model **generate**, then **critique its own output**, then
**revise** — repeating until the model itself judges the output good enough
to stop.

This looks similar to the workflow "evaluator-optimizer" pattern, but the
difference is control: in a workflow evaluator-optimizer, the loop bound and
the pass/fail bar are fixed by code. In agentic reflection, the model decides
when it's satisfied — the stopping condition is itself a judgment call, not a
hardcoded threshold.

## When To Use It

- Writing tasks where quality matters more than latency (code generation,
  long-form content, complex reasoning chains)
- Tasks where a "good enough" bar is fuzzy and hard to encode as a rule
- Self-correction on factual or logical errors before returning to the user

## When *Not* To Use It

- Latency-sensitive paths — reflection roughly doubles (or more) the token
  cost and turnaround time
- Tasks with an objective, checkable pass/fail bar → a fixed
  evaluator-optimizer workflow is cheaper and just as effective

## Control Flow

```
┌───────────┐
│ GENERATE  │◄─────────────┐
└─────┬─────┘               │
      ▼                     │
┌───────────┐               │
│ CRITIQUE  │  (self-review)│
└─────┬─────┘               │
      │                     │
      │ "needs work" ───────┘
      │
      │ "good enough"
      ▼
┌───────────┐
│  RETURN   │
└───────────┘
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | The model's own critique step |
| Cost/latency | 2–4x a single generation, unbounded without a cap |
| Failure mode | Model is either too easily satisfied, or never satisfied |
| Typical guardrail | Max reflection rounds as a safety net |

## LangGraph Implementation

Two LLM-backed nodes — `generate` and `critique` — with a conditional edge
where the critique step's own verdict (not external code) decides whether to
loop back or finish.

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field


class ReflectionState(TypedDict):
    task: str
    draft: str
    critique: str
    verdict: Literal["revise", "accept"]
    rounds: int


llm = ChatAnthropic(model="claude-sonnet-4-6")


class Critique(BaseModel):
    verdict: Literal["revise", "accept"] = Field(description="accept if the draft fully solves the task")
    feedback: str = Field(description="specific, actionable feedback if revise")


critique_llm = llm.with_structured_output(Critique)


# --- Generate / revise the draft ---
def generate_node(state: ReflectionState):
    if state.get("draft"):
        prompt = (
            f"Task: {state['task']}\n\n"
            f"Previous draft:\n{state['draft']}\n\n"
            f"Feedback to address:\n{state['critique']}\n\n"
            f"Write an improved draft."
        )
    else:
        prompt = f"Task: {state['task']}\n\nWrite a draft."

    response = llm.invoke(prompt)
    return {"draft": response.content, "rounds": state.get("rounds", 0) + 1}


# --- Model critiques its own draft ---
def critique_node(state: ReflectionState):
    result: Critique = critique_llm.invoke(
        f"Task: {state['task']}\n\nDraft:\n{state['draft']}\n\n"
        f"Critique this draft honestly. Only accept if it's genuinely complete and correct."
    )
    return {"critique": result.feedback, "verdict": result.verdict}


# --- Model's own verdict decides whether to loop ---
def route_after_critique(state: ReflectionState):
    if state["verdict"] == "accept":
        return END
    if state["rounds"] >= 4:          # safety net, not the primary stop condition
        return END
    return "generate"


graph = StateGraph(ReflectionState)
graph.add_node("generate", generate_node)
graph.add_node("critique", critique_node)

graph.set_entry_point("generate")
graph.add_edge("generate", "critique")
graph.add_conditional_edges("critique", route_after_critique, {"generate": "generate", END: END})

app = graph.compile()

result = app.invoke({
    "task": "Write a 3-sentence explanation of Unity Catalog row filters for a non-technical stakeholder.",
    "rounds": 0
})
print(f"Rounds taken: {result['rounds']}")
print(result["draft"])
```

**Why this is agentic reflection and not a workflow evaluator-optimizer:**
the `verdict` field is produced by the model's own judgment on each pass, not
by a fixed rubric or external check. The `rounds >= 4` cap is a safety net,
not the actual stopping logic.

## Interview Angle

A common follow-up: *"How is this different from an evaluator-optimizer
workflow?"*
- Evaluator-optimizer (workflow): a separate, often simpler evaluator applies
  a fixed rubric; loop count and pass bar are set in code
- Reflection (agentic): the same or a paired model applies open-ended
  judgment; the model decides what "good" means for this specific draft
