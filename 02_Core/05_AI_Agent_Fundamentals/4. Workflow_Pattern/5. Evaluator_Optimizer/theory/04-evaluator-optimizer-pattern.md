# Evaluator-Optimizer Pattern

## What It Is

One LLM call generates an output; a second, separate step **evaluates** it
against a fixed rubric; if it fails, the generator revises — looping until
the rubric passes or a fixed round cap is hit.

This looks similar to the agentic Reflection pattern, but the control is
different: here, the evaluator applies a **fixed, code-defined rubric** and
the loop bound is set in advance. The model doesn't decide what "good" means
— the rubric does.

## When To Use It

- The quality bar is objective and can be written down as a checklist
  (e.g., "must include a call-to-action," "must be under 200 words," "must
  cite at least one source")
- You want a cheaper/simpler model to do the evaluating, separate from the
  (possibly more expensive) generator
- Predictability matters — you want to know the maximum number of rounds
  in advance

## When *Not* To Use It

- If "good enough" is genuinely fuzzy and hard to write down as a rubric →
  use agentic **Reflection**, where the model's own open-ended judgment
  decides
- If a single generation almost always passes — the evaluation step is
  pure overhead

## Control Flow

```
┌───────────┐
│ GENERATE  │◄─────────────┐
└─────┬─────┘               │
      ▼                     │
┌───────────┐               │
│ EVALUATE  │  (fixed rubric)│
└─────┬─────┘               │
      │                     │
      │ fail, rounds < cap ─┘
      │
      │ pass, OR rounds == cap
      ▼
┌───────────┐
│  RETURN   │
└───────────┘
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | Code — a fixed rubric decides pass/fail, fixed cap bounds the loop |
| Cost/latency | Bounded — known maximum number of rounds |
| Failure mode | Rubric is too strict (endless failing) or too loose (false pass) |
| Typical guardrail | Hard round cap; rubric versioned and testable independently |

## LangGraph Implementation

The evaluator node applies a fixed, enumerable rubric (not open-ended
judgment) and the loop is bounded by an explicit round counter checked in
code — both are deterministic, unlike Reflection's model-judged verdict.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic


class EvalOptState(TypedDict):
    task: str
    draft: str
    failures: list[str]
    rounds: int


llm = ChatAnthropic(model="claude-sonnet-4-6")

MAX_ROUNDS = 3   # fixed cap — known in advance, not a safety net


# --- Generate / revise based on rubric failures ---
def generate_node(state: EvalOptState):
    if state.get("failures"):
        prompt = (
            f"Task: {state['task']}\n\nPrevious draft:\n{state['draft']}\n\n"
            f"Fix these specific rubric failures:\n" + "\n".join(f"- {f}" for f in state["failures"])
        )
    else:
        prompt = f"Task: {state['task']}\n\nWrite a draft."
    response = llm.invoke(prompt)
    return {"draft": response.content, "rounds": state.get("rounds", 0) + 1}


# --- Fixed, code-defined rubric — not open-ended model judgment ---
def evaluate_node(state: EvalOptState):
    draft = state["draft"]
    failures = []
    if len(draft.split()) > 150:
        failures.append("exceeds 150-word limit")
    if "?" not in draft and "call to action" in state["task"].lower():
        failures.append("missing a call-to-action")
    if not draft.strip():
        failures.append("empty draft")
    return {"failures": failures}


def route_after_eval(state: EvalOptState):
    if not state["failures"]:
        return END
    if state["rounds"] >= MAX_ROUNDS:      # hard cap, known ahead of time
        return END
    return "generate"


graph = StateGraph(EvalOptState)
graph.add_node("generate", generate_node)
graph.add_node("evaluate", evaluate_node)

graph.set_entry_point("generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges("evaluate", route_after_eval, {"generate": "generate", END: END})

app = graph.compile()

result = app.invoke({
    "task": "Write a short call-to-action email inviting customers to a webinar.",
    "rounds": 0
})
print(f"Rounds taken: {result['rounds']}, failures remaining: {result['failures']}")
print(result["draft"])
```

**Why this is a workflow and not agentic Reflection:** `evaluate_node`
applies fixed, enumerable checks (`word count > 150`, `missing "?"`) written
in plain Python — no LLM judgment involved in the pass/fail decision. The
`MAX_ROUNDS` cap is also the primary stopping mechanism the design relies on,
not a backstop for unpredictable model behavior.

## Interview Angle

A common follow-up: *"When would you switch this to agentic Reflection
instead?"*
- When the rubric keeps growing new special cases because "good" is hard to
  pin down as fixed rules
- When you want the evaluator to catch issues you didn't think to write a
  rule for
- The trade-off: fixed rubric = predictable and cheap; model judgment =
  more thorough but unpredictable in cost and less testable in isolation
