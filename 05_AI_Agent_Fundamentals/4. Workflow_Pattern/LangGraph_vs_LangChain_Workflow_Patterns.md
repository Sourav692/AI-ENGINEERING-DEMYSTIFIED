# LangGraph vs LangChain: Workflow Patterns

Quick reference for building the same five workflow patterns two ways.

- **LangGraph versions** — this folder's notebooks
- **LangChain versions** — [`02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/06_Workflow_Patterns/`](../../02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/06_Workflow_Patterns/)

Verified against `langchain 1.4.0` / `langchain-core 1.6.1` / `langgraph 1.2.11`.

---

## Part 1 — The four dispatch primitives

Everything reduces to two questions: **how many workers run**, and **who decides
that number**.

| Primitive | Framework | Workers that run | Who decides the count | Output shape |
|---|---|---|---|---|
| `RunnableBranch` | LangChain | **1** of a fixed set | nobody — always one | the chosen branch's output |
| `RunnableParallel` | LangChain | **all** of a fixed set | you, at code-writing time | dict keyed by branch name |
| `Runnable.map()` | LangChain | same worker, **N** times | the input, at run time | ordered list |
| `Send` | LangGraph | **N** workers, each targetable | the input, at run time | merged into shared state |

### Seen side by side

```python
shout   = RunnableLambda(lambda s: f"SHOUT({s.upper()})")
whisper = RunnableLambda(lambda s: f"whisper({s.lower()})")
echo    = RunnableLambda(lambda s: f"echo({s})")

branch   = RunnableBranch((cond_a, shout), (cond_b, whisper), echo)   # pick ONE
parallel = RunnableParallel(loud=shout, soft=whisper, plain=echo)     # run ALL
fanout   = shout.map()                                                # run ONE, N times
```

```text
branch.invoke("hello!")           -> SHOUT(HELLO!)              # one branch fired
parallel.invoke("hello")          -> {'loud': ..., 'soft': ..., 'plain': ...}
fanout.invoke(["a","b"])          -> ['SHOUT(A)', 'SHOUT(B)']   # 2 items -> 2 runs
fanout.invoke(["a","b","c","d"])  -> 4 results                  # 4 items -> 4 runs
```

### The restaurant analogy

- **`RunnableBranch`** is the host. They seat you at one counter. One kitchen cooks.
- **`RunnableParallel`** is a fixed combo meal. Pizza and salad stations both cook, every time.
- **`.map()`** is catering: "one pizza per guest." Guest count arrives with the order.
- **`Send`** is catering where each guest can order from a *different* station.

### `.map()` vs `Send` — the four real gaps

`.map()` is the closest LangChain equivalent to `Send`, but not a full replacement.

| | `Send` | `.map()` |
|---|---|---|
| Worker identity | each `Send` names its own target node | every item hits the **same** runnable |
| Results land in | shared graph state, merged by a reducer | an **ordered list**, positionally matched |
| One worker fails | the graph can route around it | whole batch raises, unless `batch(return_exceptions=True)` |
| Durability | per-worker checkpoints, interrupts, resume | none — the chain is stateless |

**Softening the first gap:** put a `RunnableBranch` *inside* the worker, and each
item picks its own specialist while `.map()` still fans out.

```python
mixed_worker.map().invoke(plan)   # -> ['[coder] ...', '[researcher] ...', '[writer] ...']
```

**One point in `.map()`'s favour:** results come back in **input order**.
Reducer-merged LangGraph state arrives in completion order.

### Choosing

> Could I have hardcoded the exact number of workers before seeing this input?
>
> - **Not applicable, I need one path** → `RunnableBranch`
> - **Yes** → `RunnableParallel`
> - **No, and every worker is the same** → `.map()`
> - **No, and workers differ or need shared state** → `Send`

---

## Part 2 — The five patterns, both ways

| # | Pattern | LangGraph | LangChain 1.x | Coverage |
|---|---------|-----------|---------------|----------|
| 1 | Prompt chaining | nodes + `add_edge`, loop edge, fail node | `\|`, `.with_retry()`, `.with_fallbacks()` | ✅ full |
| 2 | Routing | `add_conditional_edges` | `RunnableBranch` | ✅ full |
| 3 | Parallelization | fan-out edges + reducers | `RunnableParallel` | ✅ full |
| 4 | Orchestrator–worker | `Send` per subtask | `Runnable.map()` | ⚠️ partial |
| 5 | Evaluator–optimizer | conditional edge back to generator | Python loop, or `after_model` + `jump_to="model"` | ✅ full |

### Construct-by-construct

| LangGraph | LangChain 1.x |
|---|---|
| `add_edge(a, b)` | the `\|` pipe operator |
| `StateGraph` + `TypedDict` state | a dict grown by `RunnablePassthrough.assign` |
| `add_conditional_edges(node, fn, map)` | `RunnableBranch((cond, chain), ..., default)` |
| two `add_edge` calls for fan-out | `RunnableParallel(a=..., b=...)` |
| `Annotated[list, operator.add]` reducer | **not needed** — each branch owns a dict key |
| `add_edge(["x", "c"], "d")` sync point | a branch whose value is a multi-step chain |
| `Send("worker", {...})` | `worker.map()` |
| conditional edge back to an earlier node | `.with_retry()`, a Python loop, or `jump_to="model"` |
| terminal error node | `.with_fallbacks([...])` |
| `interrupt()`, checkpointers, `Command(resume=...)` | **no equivalent** |
| no built-in throttle | `config={"max_concurrency": N}` |

### The three things that genuinely differ

1. **Reducers disappear.** A reducer exists to stop concurrent writes from
   clobbering each other. `RunnableParallel` returns a keyed dict, so there is no
   collision to resolve.

2. **LCEL is acyclic.** `a | b | a` runs `a` twice — it does not loop. Cycles come
   from a Python loop, from agent middleware, or from LangGraph. This is why
   pattern 5 is the only one needing a non-LCEL mechanism.

3. **Retry is exception-driven.** A LangChain gate *raises* instead of returning a
   route name. "Try again" becomes a decorator on the chain rather than an edge in
   a diagram. Note that `.with_retry()` retries **blind** — it carries no memory of
   why the last attempt failed, which is exactly why it cannot implement
   evaluator–optimizer.

---

## Part 3 — Which framework to reach for

**Use LangChain when** the flow is acyclic, the pattern maps onto one primitive,
and you want less code. Parallelization in particular loses all the reducer
boilerplate.

**Use LangGraph when** you need any of:

- **Durability** — resume a half-finished run, checkpoint intermediate stages
- **Human-in-the-loop** — `interrupt()` for approval mid-flow
- **Shared worker state** — workers writing into one reduced state key
- **Heterogeneous dispatch** — different subtasks to genuinely different nodes
- **Cyclic graphs** with more than a simple back-edge

Rule of thumb: **workflow shape → LangChain; workflow durability → LangGraph.**

---

## Measured behaviour

Executed on `langchain-core 1.6.1` with 0.5s-per-step stubs:

| Demo | Result |
|---|---|
| 4 steps sequential | 2.16s |
| Same steps, middle two parallel | 1.51s |
| Asymmetric paths (`B→X` alongside `C`) | 2.01s — paced by the longer path, not the sum of 2.5s |
| 6 branches, unbounded | 0.51s |
| 6 branches, `max_concurrency=2` | 1.50s |
| `.map()` on a 2-section plan | 2 workers |
| `.map()` on a 5-section plan | 5 workers, no code change |
| Never-approving evaluator | capped at 5 calls by `ModelCallLimitMiddleware` |

---

## See also

- [`README.md`](README.md) — which notebook to open for each pattern
- [`workflows.md`](workflows.md) — pattern definitions, diagrams, LangGraph reference code
- [`Workflow_vs_Agentic_Patterns.md`](Workflow_vs_Agentic_Patterns.md) — workflow vs agent boundary
- [`06_Workflow_Patterns/README.md`](../../02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/06_Workflow_Patterns/README.md) — the LangChain implementations
