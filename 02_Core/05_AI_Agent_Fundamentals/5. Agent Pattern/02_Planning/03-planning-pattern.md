# Planning Agent Pattern

## What It Is

A planning agent first generates an explicit **plan** — a list of steps
toward the goal — then executes the steps, and critically, **replans** when
execution reveals something the original plan didn't account for.

This differs from a workflow's orchestrator-workers pattern in one key way:
the plan itself is not fixed. If step 3 fails or reveals new information, the
agent can throw away the remainder of the plan and generate a new one — the
code doesn't have branches for every possible outcome, the model authors new
branches on the fly.

## When To Use It

- Multi-step tasks where the right sequence isn't knowable until you start
  (e.g., debugging, research tasks, migrations)
- Tasks where early steps can invalidate later ones
- When you want visibility into the agent's plan before/while it executes
  (useful for human-in-the-loop approval)

## When *Not* To Use It

- Tasks with a small, well-known number of steps → a workflow chain is
  simpler and cheaper
- When replanning overhead isn't worth it because the plan basically never
  needs to change

## Control Flow

```
┌──────────┐
│   PLAN   │  (generate ordered steps)
└────┬─────┘
     ▼
┌──────────┐
│ EXECUTE  │◄────────────┐
│  step N  │              │
└────┬─────┘              │
     ▼                    │
┌──────────┐              │
│  CHECK:  │  plan still  │
│ on track?│──────valid───┘
└────┬─────┘
     │ plan invalidated
     ▼
┌──────────┐
│ REPLAN   │──────────────┐
└──────────┘               │
     │                     │
     └── new plan ─────────┘
     │
     │ all steps done
     ▼
┌──────────┐
│  RETURN  │
└──────────┘
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | The plan, but the plan itself is model-authored and revisable |
| Cost/latency | Higher upfront (planning call) + variable execution |
| Failure mode | Thrashing — replanning too often without making progress |
| Typical guardrail | Cap on replan count; require plan to shrink, not grow |

## LangGraph Implementation

A `planner` node produces a structured list of steps. An `executor` node
works through them one at a time. After each step, a `check` node decides:
continue on the current plan, replan, or finish.

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field


class Plan(BaseModel):
    steps: list[str] = Field(description="ordered list of steps to complete the goal")


class StepResult(BaseModel):
    outcome: str
    plan_still_valid: bool = Field(description="False if this result means the remaining plan needs to change")


class PlanningState(TypedDict):
    goal: str
    plan: list[str]
    current_step: int
    results: list[str]
    replans: int


llm = ChatAnthropic(model="claude-sonnet-4-6")
planner_llm = llm.with_structured_output(Plan)


# --- Generate the initial (or revised) plan ---
def plan_node(state: PlanningState):
    context = ""
    if state.get("results"):
        context = f"\n\nProgress so far: {state['results']}\nThis plan replaces the remaining steps."
    plan: Plan = planner_llm.invoke(
        f"Goal: {state['goal']}{context}\n\nProduce a concise ordered plan."
    )
    return {"plan": plan.steps, "current_step": 0}


# --- Execute the current step ---
def execute_node(state: PlanningState):
    step = state["plan"][state["current_step"]]
    response = llm.invoke(f"Goal: {state['goal']}\nExecute this step: {step}")
    results = state.get("results", []) + [response.content]
    return {"results": results, "current_step": state["current_step"] + 1}


# --- Model judges whether the plan still holds ---
checker_llm = llm.with_structured_output(StepResult)

def check_node(state: PlanningState):
    last_result = state["results"][-1]
    check: StepResult = checker_llm.invoke(
        f"Goal: {state['goal']}\nRemaining plan: {state['plan'][state['current_step']:]}\n"
        f"Last step result: {last_result}\n"
        f"Does the remaining plan still make sense given this result?"
    )
    return {"plan_still_valid": check.plan_still_valid}


def route_after_check(state: PlanningState):
    if state["current_step"] >= len(state["plan"]):
        return END
    if not state.get("plan_still_valid", True) and state.get("replans", 0) < 2:
        return "replan"
    return "execute"


def replan_node(state: PlanningState):
    return {"replans": state.get("replans", 0) + 1}


graph = StateGraph(PlanningState)
graph.add_node("plan", plan_node)
graph.add_node("execute", execute_node)
graph.add_node("check", check_node)
graph.add_node("replan", replan_node)

graph.set_entry_point("plan")
graph.add_edge("plan", "execute")
graph.add_edge("execute", "check")
graph.add_conditional_edges("check", route_after_check, {
    "execute": "execute", "replan": "replan", END: END
})
graph.add_edge("replan", "plan")   # replanning re-enters the planner with progress context

app = graph.compile()

result = app.invoke({
    "goal": "Migrate the Barclays Netezza ETL job to a Databricks Delta pipeline",
    "results": [],
    "replans": 0
})
print(f"Plan executed in {result['replans']} replan(s):")
for step, outcome in zip(result["plan"], result["results"]):
    print(f"- {step} -> {outcome[:80]}...")
```

**Why this is agentic planning and not a fixed orchestrator-workers
workflow:** the `replan` path lets the model discard and regenerate the
*rest of the plan itself* based on what execution revealed — the graph
doesn't enumerate what a "step 3 failure" looks like in advance.

## Interview Angle

A common follow-up: *"How do you keep replanning from looping forever?"*
- Cap `replans` (shown above: max 2)
- Require the new plan to make measurable progress (e.g., fewer remaining
  steps, or new information not present before)
- Escalate to a human after N replans instead of retrying indefinitely
