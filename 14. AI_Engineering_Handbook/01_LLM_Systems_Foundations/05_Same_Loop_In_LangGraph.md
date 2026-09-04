# The Same Loop in LangGraph

> **Level** 🟢 Foundations · **Module** 01 · **Doc** 5 of 5 · **Time** ~30 min + lab
> **Prerequisites:** [The Tool-Calling Loop From Scratch](04_Tool_Calling_Loop_From_Scratch.md)
> **Source material:** `1. Company_Wise_Preparation/2. DevRev/Coding_Round/agent_tool_calling_demo/src/langgraph_agent.py`, `README.md`
> **Lab:** `project/notebooks/langgraph_react_agent.ipynb` · `project/notebooks/robust_langgraph_tool_calling_agent.ipynb` · `project/src/langgraph_agent.py`

## Why this matters

The from-scratch loop proves you understand the mechanics. The framework version proves you can express them in the tool a team actually uses — and, more usefully, it shows you *what the framework is doing for you* so you are never surprised by it. LangGraph is the framework used throughout this handbook: Module 04's RAG pipeline is a LangGraph graph, and Module 05's orchestrator borrows its checkpointing ideas.

The source project builds both versions over the **same** tools, brain, robustness and observability modules. Only the orchestration differs. Read this document with the previous one open; every piece maps.

## The graph

```
    START -> agent --(has tool calls & under budget)--> tools -> agent
                  \--(final / out of budget)--> END
```

Two nodes and a conditional edge. `agent` is THINK. `tools` is ACT. The edge from `tools` back to `agent` is OBSERVE. The conditional edge out of `agent` is the guard and the final-answer exit together.

## State: the thing LangGraph makes explicit

In the scratch version, state was a local `observations` list and an `iterations` counter inside `run()`. LangGraph forces you to declare it:

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    iterations: int
```

Two things to understand here.

**Messages replace observations.** Instead of a list of `(tool_name, result)` tuples, the graph carries a conversation: a `HumanMessage` for the query, an `AIMessage` for each of the brain's decisions, a `ToolMessage` for each result. This is the shape a real LLM with `bind_tools` produces natively, which is the point — the graph is already speaking the model's language.

**`add_messages` is a reducer.** Each node returns a *partial* state update. Without a reducer, returning `{"messages": [new]}` would replace the list. `Annotated[list, add_messages]` tells LangGraph to *append* instead. The `iterations` field has no reducer, so a node that returns `{"iterations": n + 1}` overwrites it — exactly what a counter wants.

Two small helpers bridge the two worlds, so the offline brain can be reused unchanged:

```python
def _observations_from_messages(messages) -> List[Observation]:
    """Rebuild the brain's (tool_name, python_result) list from ToolMessages."""
    return [(m.name, json.loads(m.content)) for m in messages if isinstance(m, ToolMessage)]   # (with a fallback for non-JSON)

def _first_human_query(messages) -> str:
    return next((m.content for m in messages if isinstance(m, HumanMessage)), "")
```

## The nodes

### `agent` — THINK

```python
def agent_node(state: AgentState) -> dict:
    query = _first_human_query(state["messages"])
    observations = _observations_from_messages(state["messages"])
    decision = brain.decide(query, observations)                    # same brain, same contract

    if decision.is_final:
        return {"messages": [AIMessage(content=decision.final)]}    # plain answer, no tool_calls

    call = {"name": decision.tool, "args": decision.args, "id": f"call_{state['iterations']}"}
    return {"messages": [AIMessage(content="", tool_calls=[call])],  # exactly what an LLM would emit
            "iterations": state["iterations"] + 1}
```

The node reconstructs what the brain needs from the message history, calls the identical `.decide()`, and translates the `Decision` into a message. A final answer becomes an `AIMessage` with content and no `tool_calls`. A tool request becomes an `AIMessage` with empty content and a `tool_calls` list — the precise shape `ChatOpenAI(...).bind_tools(...)` returns, which is why swapping in a real model later is a one-line change.

Note where `iterations` is incremented: on the *decision to call a tool*, not on execution. That is the same accounting as the scratch loop.

### `tools` — ACT

```python
def tools_node(state: AgentState) -> dict:
    last = state["messages"][-1]
    out = []
    for tc in last.tool_calls:
        tool = registry.get(tc["name"])
        try:
            result = execute_tool(tool, tc["args"], logger=session.logger,
                                  memo=session.memo, confirm=confirm)     # the SAME safe executor
            content = json.dumps(result, default=str)
        except ConfirmationRequired:
            content = json.dumps({"error": "needs_confirmation", "tool": tc["name"], "args": tc["args"]})
        out.append(ToolMessage(content=content, tool_call_id=tc["id"], name=tc["name"]))
    return {"messages": out}
```

Same `execute_tool`, same confirmation gate, memo and retry. One difference from the scratch loop is instructive: here a `ConfirmationRequired` becomes a `ToolMessage` carrying an error *rather than* pausing the run. The graph keeps going and the brain sees the refusal as an observation. Both designs are legitimate; the scratch version's explicit pause (`blocked_on`) is the better production shape, and LangGraph offers `interrupt_before` and a checkpointer to do the same — the `robust_langgraph_tool_calling_agent.ipynb` notebook explores that.

Also note the `for tc in last.tool_calls` loop: an LLM can emit *several* tool calls in one message. The node handles them all. Module 03 discusses when running them in parallel is worth it.

### The conditional edge — guard and exit

```python
def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    has_calls = isinstance(last, AIMessage) and bool(getattr(last, "tool_calls", None))
    if has_calls and state["iterations"] < max_iterations:
        return "tools"
    return END          # final answer, or out of budget
```

This single function is the scratch loop's `while` condition *and* its `if decision.is_final` combined. Two ways to reach `END`: the last message has no tool calls (the brain finished), or the budget is spent. LangGraph will happily run forever if you forget the second clause; the framework gives you a graph, not a guard.

### Wiring

```python
g = StateGraph(AgentState)
g.add_node("agent", agent_node)
g.add_node("tools", tools_node)
g.add_edge(START, "agent")
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")          # observe -> think again
app = g.compile()
```

And running it:

```python
final = app.invoke({"messages": [HumanMessage(content=query)], "iterations": 0})
# the last AIMessage without tool_calls is the synthesized answer
```

## Scratch ↔ LangGraph, side by side

| Concept | Scratch (`scratch_agent.py`) | LangGraph (`langgraph_agent.py`) |
|---|---|---|
| Working memory within a run | `observations: List[(tool, result)]` | `state["messages"]` — Human / AI / Tool messages |
| Step counter | local `iterations` | `state["iterations"]` (overwrite, no reducer) |
| THINK | `brain.decide(...)` inside the `while` | `agent_node` → `brain.decide(...)` |
| Tool request | `Decision(tool=..., args=...)` | `AIMessage(tool_calls=[{name, args, id}])` |
| Final answer | `Decision(final=...)` | `AIMessage(content=..., tool_calls=None)` |
| ACT | `execute_tool(...)` in the loop body | `tools_node` → `execute_tool(...)` |
| OBSERVE | `observations.append(...)` | `ToolMessage` appended via `add_messages` |
| Guard + exit | `while iterations < max` and `if is_final` | `should_continue` → `"tools"` or `END` |
| Confirmation needed | raise → `RunResult.blocked_on` (pause) | `ToolMessage` with `needs_confirmation` (continue) |
| Cross-turn state | `Session` | `Session` (shared), plus LangGraph checkpointers for durability |

## What the framework buys you

Having built it both ways, you can say precisely what LangGraph adds:

- **Declared state with reducers** — no accidental list replacement, and state is inspectable between nodes.
- **The model's native message format** — a real LLM slots in with `bind_tools` and nothing else changes.
- **Checkpointing** — a `MemorySaver` or durable saver persists state after every node, which gives you crash recovery and human-in-the-loop pauses (`interrupt_before=["tools"]`) without writing them yourself. Module 05's orchestrator implements the same idea by hand so you understand it.
- **Composability** — nodes can be subgraphs. Module 04's nine-step RAG pipeline is one graph; Module 07's multi-agent designs are graphs of graphs.

And what it does *not* buy you: the step budget, the confirmation policy, the retry/fallback distinction, the destructive flag. Those are yours to write, in any framework.

## In the code

| Concept | Where |
|---|---|
| State schema | `project/src/langgraph_agent.py` → `AgentState` |
| Nodes and edge | `build_graph` → `agent_node`, `tools_node`, `should_continue` |
| Running | `run_query` |
| Guided notebook | `project/notebooks/langgraph_react_agent.ipynb` (+ `.py` twin) |
| Checkpointing and interrupts | `project/notebooks/robust_langgraph_tool_calling_agent.ipynb` |
| Real-LLM variant | `project/notebooks/agent_tool_calling_demo_openai.ipynb` (needs an API key) |

## Interview lens

When asked "why LangGraph?" the weak answer is "it's what people use". The strong answer names what you get and what you still own:

> *"LangGraph gives me declared state, the model's native tool-call message shape, and checkpointing for pause and resume. It does not give me a step budget or a confirmation policy — those are still my code, and they're the same code in both versions."*

## Checkpoint

- What does `add_messages` do, and what would happen without it?
- Why does the `agent` node emit an `AIMessage` with `tool_calls` rather than returning a `Decision` directly?
- Where is the max-iteration guard in the graph version, and what happens if you delete that clause?
- How do the two versions differ in handling `ConfirmationRequired`, and which shape is better for production?
- Name three things the framework provides and three it does not.

**Next →** [Module 02 · System Design Fundamentals](../02_System_Design_Fundamentals/README.md) — or, to go deeper on the safety layer you just used as a black box, jump ahead to [Module 03 · Robust Agents](../03_Robust_Agents/README.md).
