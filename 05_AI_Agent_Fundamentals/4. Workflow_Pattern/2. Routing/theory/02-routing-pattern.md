# Routing Pattern

## What It Is

Routing uses a classification step to send input down one of several
**predefined branches**. A cheap model (or rule) categorizes the input, and
code then dispatches to the matching handler.

This can look superficially like agentic delegation, but the difference is
that every possible branch is authored in advance. The classifier picks
*among* known options — it never invents a new path.

## When To Use It

- Distinct categories of input that genuinely need different handling
  (e.g., billing question vs. technical issue vs. sales inquiry)
- You want to route cheap/simple requests to a smaller model and complex ones
  to a stronger model
- Each branch has its own well-defined prompt, tools, or downstream system

## When *Not* To Use It

- If categories overlap heavily or the "right" category is itself
  ambiguous and needs judgment → consider letting an agent reason about it
  instead of forcing a hard classification
- If there's really only one branch — routing adds a classification call for
  no benefit

## Control Flow

```
                    ┌────────────┐
                    │ CLASSIFIER │
                    └─────┬──────┘
             ┌─────────────┼─────────────┐
             ▼              ▼              ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ BRANCH A │  │ BRANCH B │  │ BRANCH C │
       └────┬─────┘  └────┬─────┘  └────┬─────┘
            └───────────────┼───────────────┘
                             ▼
                       ┌──────────┐
                       │  OUTPUT  │
                       └──────────┘

  all three branches pre-written — classifier only picks among them
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | Code — the classifier picks from a fixed menu |
| Cost/latency | Predictable — one classification call + one branch call |
| Failure mode | Misclassification sends input down the wrong (still fixed) branch |
| Typical guardrail | Confidence threshold + fallback/default branch |

## LangGraph Implementation

A classifier node produces a label from a closed set (enforced via structured
output / enum), and a conditional edge maps that label to a pre-written node.
The set of possible destinations is fixed at graph-build time.

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field


class RoutingState(TypedDict):
    ticket: str
    category: str
    response: str


llm = ChatAnthropic(model="claude-sonnet-4-6")


class Classification(BaseModel):
    category: Literal["billing", "technical", "sales"] = Field(
        description="the single best-fit category for this ticket"
    )


classifier_llm = llm.with_structured_output(Classification)


# --- Classify into one of a fixed, known set of categories ---
def classify_node(state: RoutingState):
    result: Classification = classifier_llm.invoke(
        f"Classify this support ticket:\n\n{state['ticket']}"
    )
    return {"category": result.category}


# --- Each branch is pre-written; the classifier just selects among them ---
def billing_node(state: RoutingState):
    response = llm.invoke(f"Respond as a billing specialist to:\n\n{state['ticket']}")
    return {"response": response.content}

def technical_node(state: RoutingState):
    response = llm.invoke(f"Respond as a technical support specialist to:\n\n{state['ticket']}")
    return {"response": response.content}

def sales_node(state: RoutingState):
    response = llm.invoke(f"Respond as a sales rep to:\n\n{state['ticket']}")
    return {"response": response.content}


def route(state: RoutingState) -> str:
    # a closed mapping — every possible output of the classifier maps
    # to a pre-existing node; there is no "invent a new branch" option
    return state["category"]


graph = StateGraph(RoutingState)
graph.add_node("classify", classify_node)
graph.add_node("billing", billing_node)
graph.add_node("technical", technical_node)
graph.add_node("sales", sales_node)

graph.set_entry_point("classify")
graph.add_conditional_edges("classify", route, {
    "billing": "billing", "technical": "technical", "sales": "sales"
})
graph.add_edge("billing", END)
graph.add_edge("technical", END)
graph.add_edge("sales", END)

app = graph.compile()

result = app.invoke({"ticket": "I was charged twice for my subscription this month."})
print(f"Routed to: {result['category']}")
print(result["response"])
```

**Why this is a workflow and not an agentic pattern:** the conditional edge's
mapping dict — `{"billing": "billing", "technical": "technical", "sales":
"sales"}` — is closed and known ahead of time. The classifier chooses among
options the developer already wrote, rather than deciding the next action
freely the way a ReAct loop does.

## Interview Angle

A common follow-up: *"How do you handle a ticket that doesn't fit any
category well?"*
- Add a `general` / `other` fallback branch and route low-confidence
  classifications there
- Log misclassifications to periodically refine category definitions
- If categories are frequently ambiguous, that's a signal the task may need
  agentic reasoning instead of a fixed classifier
