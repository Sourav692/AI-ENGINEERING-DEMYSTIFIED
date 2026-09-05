# Workflow Patterns in LangChain

The five agentic **workflow** patterns from Anthropic's *Building Effective
Agents*, implemented with LangChain 1.x primitives instead of LangGraph graphs.

These are the LangChain counterparts to
[`05_AI_Agent_Fundamentals/4. Workflow_Pattern/`](../../../05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/),
which builds the same five patterns with `StateGraph`. **Same examples, same test
inputs, same validation rules** — only the framework differs. Read them side by
side to see what each framework makes easy.

## Notebooks

| # | Pattern | Notebook | Core primitive | LangGraph original |
|---|---------|----------|----------------|--------------------|
| 1 | Prompt chaining | [`6.1_Prompt_Chaining.ipynb`](6.1_Prompt_Chaining.ipynb) | `\|`, `.with_retry()`, `.with_fallbacks()` | `1. Prompt_Chaining/` |
| 2 | Routing | [`6.2_Routing.ipynb`](6.2_Routing.ipynb) | `RunnableBranch` | `2. Routing/` |
| 3 | Parallelization | [`6.3_Parallelization.ipynb`](6.3_Parallelization.ipynb) | `RunnableParallel` | `3. Parallelization/` |
| 4 | Orchestrator–worker | [`6.4_Orchestrator_Worker.ipynb`](6.4_Orchestrator_Worker.ipynb) | `Runnable.map()` | `4. Orchestrator_Worker/` |
| 5 | Evaluator–optimizer | [`6.5_Evaluator_Optimizer.ipynb`](6.5_Evaluator_Optimizer.ipynb) | Python loop, or `after_model` + `jump_to` | `5. Evaluator_Optimizer/` |

Run them in order. Each builds on the previous one's mental model, and 6.4 opens
by showing why the primitives from 6.2 and 6.3 cannot express its pattern.

## The primitive map

The whole translation reduces to two questions: **how many workers run**, and
**who decides that number**.

| Primitive | Workers that run | Who decides the count | Pattern |
|---|---|---|---|
| `RunnableBranch` | 1 of a fixed set | nobody — always one | Routing |
| `RunnableParallel` | all of a fixed set | you, when writing the code | Parallelization |
| `Runnable.map()` | the same worker, N times | the input, at run time | Orchestrator–worker |

Everything else maps directly:

| LangGraph | LangChain 1.x |
|---|---|
| `add_edge(a, b)` | the `\|` pipe operator |
| `StateGraph` + `TypedDict` state | a dict grown by `RunnablePassthrough.assign` |
| `add_conditional_edges(node, fn, map)` | `RunnableBranch((cond, chain), ..., default)` |
| fan-out via two `add_edge` calls | `RunnableParallel(a=..., b=...)` |
| `Annotated[list, operator.add]` reducer | **not needed** — each branch owns a dict key |
| `Send("worker", {...})` per subtask | `worker.map()` over a list of task dicts |
| a conditional edge back to an earlier node | `.with_retry()`, a Python loop, or `after_model` + `jump_to="model"` |
| a terminal error node | `.with_fallbacks([...])` |
| `interrupt()` / checkpointers | **no equivalent** — stay on LangGraph |

## Coverage: what LangChain does and does not reach

Four of the five patterns are fully expressible. One is partial.

- **Patterns 1, 2, 3, 5 — full coverage.** The LCEL version is usually shorter
  than the graph, and pattern 3 loses the reducer boilerplate entirely.
- **Pattern 4 — dynamic fan-out and fan-in are covered by `.map()`.** What stays
  LangGraph-only is `Send`'s ability to target **different** nodes per subtask,
  to write into **shared state** through reducers, and to checkpoint or interrupt
  individual workers. Notebook 6.4 measures these gaps rather than glossing them.
- **Cycles are the real dividing line.** LCEL is acyclic: `a | b | a` runs `a`
  twice, it does not loop. Pattern 5 therefore needs either a Python loop or
  LangChain 1.x agent middleware, both of which notebook 6.5 builds.

Reach back for LangGraph whenever you need durability: resuming a half-finished
run, interrupting for human approval, or checkpointing intermediate stages.

## Setup

Notebooks 6.1, 6.2, 6.4 and 6.5 need only the core install plus a model API key.

Notebook 6.3's final section calls Wikipedia and Tavily, which live outside the
core install:

```bash
uv pip install langchain-community wikipedia langchain-tavily
```

Note the modern import. The LangGraph original used `TavilySearchResults` from
`langchain_community`, which is deprecated; these notebooks use `TavilySearch`
from the `langchain-tavily` package.

Environment variables, in a `.env` file at the repo root:

- `OPENAI_API_KEY` — every notebook
- `TAVILY_API_KEY` — notebook 6.3 only

Each notebook builds its model with `init_chat_model("openai:gpt-4o-mini")`.
That string is provider-agnostic, so swapping to
`groq:llama-3.3-70b-versatile`, `google_genai:gemini-2.0-flash` or
`anthropic:claude-sonnet-4-5` is a one-line change and nothing else in the
notebook moves.

> **Optional chain diagrams.** `chain.get_graph().draw_mermaid()` needs no extra
> packages. Its sibling `print_ascii()` requires `pip install grandalf`.

## Verification status

Every code cell was AST-parsed, and all LLM-free logic was executed against
`langchain 1.4.0` / `langchain-core 1.6.1`:

- 6.1 — both test cases run end to end on a scripted fake model. The gate passes
  on attempt 1 for the concrete topic, and the abstract topic exhausts exactly 3
  attempts before the fallback fires.
- 6.2 — all three test inputs route correctly, the dict-lookup alternative agrees
  with `RunnableBranch`, and exactly one specialist chain runs per request.
- 6.3 — the four timing demos were run: sequential 2.16s, parallel 1.51s,
  asymmetric 2.01s, and `max_concurrency=2` throttles six branches from 0.51s to
  1.50s.
- 6.4 — the fan-out produced 2 workers for the trivial topic and 5 for the broad
  one with no code change; the error-semantics and mixed-worker cells run as
  written.
- 6.5 — both loops approve on the third draft, and a never-approving evaluator is
  capped at 5 model calls by `ModelCallLimitMiddleware`.

The Wikipedia and Tavily section of 6.3 was **not** executed — it needs the two
optional packages and a Tavily key.
