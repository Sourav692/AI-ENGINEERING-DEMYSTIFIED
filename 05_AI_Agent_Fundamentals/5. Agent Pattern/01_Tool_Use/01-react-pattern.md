# ReAct Pattern (Reason + Act)

## What It Is

ReAct interleaves **reasoning** (the model thinking about what to do) with
**acting** (calling a tool) and **observing** (reading the result), in a loop
that continues until the model decides it has enough information to answer.

- The model is not told which tool to call or how many times — it decides
- Each loop iteration adds a new observation to the model's context
- The loop ends when the model's reasoning concludes the task is complete

This is the most fundamental agentic pattern — most "agent" frameworks are
some variation of ReAct underneath.

## When To Use It

- Open-ended questions where the number of steps isn't known up front
- Tasks that require looking something up, then deciding what to look up next
  based on what was found
- Tool-use scenarios: search, calculators, database queries, API calls

## When *Not* To Use It

- If you already know the fixed sequence of steps → use a **workflow** instead
  (cheaper, more predictable, easier to test)
- If the task never needs external information or tools

## Control Flow

```
User query
    │
    ▼
┌─────────┐
│  THINK  │◄────────────────┐
└────┬────┘                 │
     │ reasoning says:      │
     │ "I need a tool"      │
     ▼                      │
┌─────────┐                 │
│   ACT   │  (call tool)    │
└────┬────┘                 │
     ▼                      │
┌──────────┐                │
│ OBSERVE  │  (tool result) │
└────┬─────┘                │
     │                      │
     └── loop again ────────┘
     │
     │ reasoning says: "I have enough"
     ▼
┌─────────┐
│  ANSWER │
└─────────┘
```

## Key Properties

| Property | Value |
|---|---|
| Who controls next step | The model, at every iteration |
| Cost/latency | Unpredictable — depends on how many loops the model takes |
| Failure mode | Infinite or excessive looping without a cap |
| Typical guardrail | Max iteration count, or a tool-call budget |

## LangGraph Implementation

ReAct in LangGraph is a graph with two nodes — an **agent** node (the LLM
reasoning + deciding on tool calls) and a **tools** node (executes whatever
the agent asked for) — with a conditional edge that loops back to the agent
until no more tool calls are requested.

```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic


# --- 1. Define state: just a running message list ---
class ReActState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# --- 2. Define tools the agent can choose to call ---
@tool
def search_docs(query: str) -> str:
    """Search internal documentation for a query."""
    # placeholder — wire to real retriever
    return f"Top result for '{query}': ... (docs snippet)"


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic math expression."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"error: {e}"


tools = [search_docs, calculator]
tool_node = ToolNode(tools)

llm = ChatAnthropic(model="claude-sonnet-4-6").bind_tools(tools)


# --- 3. Agent node: reason, decide whether to call a tool ---
def agent_node(state: ReActState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# --- 4. Conditional edge: loop back to agent, or stop ---
def should_continue(state: ReActState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


# --- 5. Wire the graph ---
graph = StateGraph(ReActState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")   # after acting, go back to reasoning

app = graph.compile()

# --- 6. Run it ---
result = app.invoke({
    "messages": [("user", "What's 47 * 12, and then search docs for 'rate limits'?")]
})
for m in result["messages"]:
    m.pretty_print()
```

**Why this is ReAct and not a workflow:** the edge from `agent` is
conditional — the graph itself doesn't know in advance whether it will call
`tools` zero, one, or five times. That decision is made fresh by the LLM on
every pass through `agent_node`.

## Interview Angle

A common follow-up: *"How do you prevent runaway loops?"*
- Add a recursion/step limit (`app.invoke(..., config={"recursion_limit": 10})`)
- Track a loop counter in state and force an exit past a threshold
- Add a "final answer" tool the model must call to terminate cleanly
