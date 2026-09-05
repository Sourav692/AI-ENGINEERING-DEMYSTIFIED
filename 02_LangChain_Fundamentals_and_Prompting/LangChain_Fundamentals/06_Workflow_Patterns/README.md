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

Notebooks 6.1, 6.2, 6.4 and 6.5 need only the core install plus an
`OPENAI_API_KEY`. Notebook 6.3's Wikipedia and Tavily section additionally needs
three packages, **already installed** in the repo venv:

```bash
uv pip install langchain-community wikipedia langchain-tavily
```

Note the modern Tavily import. The LangGraph original used `TavilySearchResults`
from `langchain_community`; these notebooks use `TavilySearch` from the
`langchain-tavily` package. `langchain-community` itself is now being sunset
upstream and warns on import, which is why only `WikipediaLoader` still comes
from it.

> **Do not run a bare `uv pip install -r requirements.txt` on Windows with a
> Jupyter kernel open.** That file pins `pydantic==2.12.5` against the 2.13.5
> currently installed, so the install tries to replace
> `_pydantic_core.cp312-win_amd64.pyd` — a file any running kernel holds open.
> The install then aborts partway through and leaves `pydantic_core` unimportable,
> which breaks the whole langchain stack. Shut the kernels down first.

### Model setup

Every notebook instantiates the client directly, the convention throughout
`LangChain_Fundamentals`:

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
```

The platform-aware `helpers` factory setup is kept at the bottom of each setup
cell, commented out, if you would rather route by platform. Swapping either way
is a one-line change and nothing else in any notebook moves.

Two notes on `temperature=0.7`:

- **6.2's classifier stays reliable** because `with_structured_output` constrains
  it to the three valid labels. Drop to `0` if you want the routing decision to
  be bit-for-bit repeatable.
- **6.5 requires a non-zero temperature.** A deterministic generator returns the
  same draft on every refinement pass, so the loop could never converge.

Environment variables, in a `.env` file at the repo root:

- `OPENAI_API_KEY` — every notebook
- `TAVILY_API_KEY` — notebook 6.3, Part 4 only

> **Optional chain diagrams.** `chain.get_graph().draw_mermaid()` needs no extra
> packages. Its sibling `print_ascii()` requires `pip install grandalf`.

## Verification status

Every code cell was AST-parsed. Each notebook's setup cell was executed for real
and built a live `ChatOpenAI(gpt-4o-mini, temperature=0.7)`. All remaining
LLM-free logic was executed against `langchain 1.4.0` / `langchain-core 1.6.1`,
with a scripted fake model swapped in after the setup cell so no API calls were
billed:

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
