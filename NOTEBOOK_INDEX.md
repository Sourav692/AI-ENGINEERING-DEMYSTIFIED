# Notebook Index

A single, accurate table of every notebook in this repo, in the order they're meant to be worked through. This reflects the **actual files on disk**. `README.md` and `CLAUDE.md` have since been reconciled to match (see [Known Discrepancies](#known-discrepancies) below for what was fixed and what's still open).

## Chapter 1 — Foundations (`01_Foundations/`)

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_State_and_Graph_Basics.ipynb` | Building a simple agent graph and managing state |
| 2 | `02_MessageState.ipynb` | `MessagesState` — the pre-built state for chat graphs |
| 3 | `03_Conditional_Routing.ipynb` | Conditional routing (`add_conditional_edges`) |
| 4 | `04_LLM_Powered_Chatbot.ipynb` | Building an LLM-powered chatbot |
| 5 | `05_Augmented_LLM_with_Tools.ipynb` | Augmented LLM with tools (`bind_tools`) |
| 6 | `06_ReAct_Agent.ipynb` | Simple tool-use ReAct agent |
| 7 | `07_Different_Graph_States.ipynb` | Four ways to define graph state |
| 8 | `08_Pydantic_State_Validation.ipynb` | `TypedDict` vs Pydantic state validation |
| 9 | `09_Node_Patterns.ipynb` | Node arguments, config & runtime context |
| 10 | `10_Runtime_Context.ipynb` | Injecting external dependencies via runtime context |
| 11 | `11_Command_Objects.ipynb` | `Command` — combined routing + state updates |

## Chapter 2 — Core Capabilities (`02_Core_Capabilities/`)

| Section | Notebook | Topic |
|---|---|---|
| `01_Memory/` | `01_Memory_and_Conversational_Agent.ipynb` | Memory & threads in conversational agents |
| `01_Memory/` | `02_Memory_Optimizations.ipynb` | Memory optimization strategies |
| `01_Memory/memory/` | `02_Agent_Memory_Types_SQLite.ipynb` | Agent memory types with SQLite persistence (self-contained sub-module — own `README.md`/`requirements.txt`) |
| `02_Routing/` | `01_Router_Agentic_RAG_System.ipynb` | Customer-support router agentic RAG system |
| `03_Human_in_the_Loop/` | `01_HITL_Basics.ipynb` | Human-in-the-loop basics |
| `03_Human_in_the_Loop/` | `02_HITL_Interrupt_and_Resume.ipynb` | Interrupt/resume approaches |
| `03_Human_in_the_Loop/` | `03_HITL_State_Modification.ipynb` | Approve/reject + state modification pattern |
| `03_Human_in_the_Loop/` | `04_HITL_Dynamic_Breakpoints.ipynb` | Dynamic breakpoints, reviewing tool calls |
| `04_Advanced_State/` | `01_Advanced_State.ipynb` | Input/output state, advanced state patterns |
| `05_Subgraphs/` | `01_Subgraphs.ipynb` | Graph composition via subgraphs |
| `06_Async_and_Streaming/` | `01_Async_and_Streaming.ipynb` | Async operations & streaming output |
| `07_Retries/` | `01_Retries.ipynb` | Fault-tolerant nodes with `RetryPolicy` |

## Chapter 3 — RAG (`03_RAG/`)

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_Simple_Agentic_RAG.ipynb` | Simple RAG agent (PDF → Chroma → LLM) |
| 2 | `02_Simple_Agentic_RAG_Databricks.ipynb` | Same agent on Databricks Vector Search |
| 3 | `03_Advanced_RAG_Agent.ipynb` | Advanced retrieval — grading, rewriting |
| 4 | `04_RAG_as_Tool_in_Agents.ipynb` | RAG as a composable tool inside a larger agent |

## Chapter 4 — Agents (`04_Agents/`)

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_Research_Assistant_Chatbot.ipynb` | Web-search research assistant (Tavily) |
| 2 | `02_Competitive_Intelligence_Agent.ipynb` | Business/competitive intelligence agent with structured output |

## Chapter 5 — Agentic Design Patterns (`05_Agentic_Design_Patterns/`)

| Section | Notebook | Topic |
|---|---|---|
| `01_Tool_Use/` | `01_Tool_Use_Agentic_Systems.ipynb` | Tool-use agentic systems (math agent) |
| `01_Tool_Use/` | `02_Tool_Calling_vs_ReAct.ipynb` | Direct tool/function calling vs. ReAct |
| `02_Planning/` | `01_Parallel_Steps_Execution.ipynb` | Parallel steps execution |
| `02_Planning/` | `02_Map_Reduce_with_Send_API.ipynb` | Dynamic parallel execution — map-reduce with `Send` |
| `04_Agent_Patterns/` | `01_Agent_Patterns.ipynb` | Reusable production agent templates (supervisor pattern) |
| `05_Long_Term_Memory/` | `01_Long_Term_Memory.ipynb` | Persistent long-term memory (PostgreSQL) |

*Note: `03_Reflection/` is referenced in the README as "coming soon" and has no folder yet.*

## Chapter 6 — Production (`06_Production/`)

Not notebooks — deployable apps and tests:

| Component | Path |
|---|---|
| Full-stack app (FastAPI + Angular + Postgres) | `fullstackapp/` |
| Unit tests (pytest) | `unit_tests/` |
| Streamlit apps | `streamlit_apps/doc-entity-extractor/`, `streamlit_apps/knowledge-graphs-with-langextract/` |

## Chapter 7 — Deep Agents (`07_Deep_Agents/`)

Not notebooks — Python scripts + a `deepagents`-based multi-agent system, vendored in from the standalone `Deep_Agent_Demystified` repo:

| Path | Content |
|---|---|
| `examples/simple_coding_agent.py` | Default agent run — `FilesystemBackend`, no code execution |
| `examples/long_term_memory_agent.py` | Adds cross-thread persistent memory (JSON, upgradeable to PostgreSQL) |
| `skills/senior-developer/`, `code-reviewer/`, `research-agent/`, `memory-manager/` | Core orchestration agents |
| `skills/aia-customer-analytics/`, `aia-distribution-channels/`, `aia-policy-underwriting/`, `aia-claims-analytics/` | Databricks Genie analytics agents (insurance-domain demo) |
| `app/` | Standalone deployable version (FastAPI backend + frontend, Docker) — see `app/README.md` |
| `docs/` | Architecture diagram, memory-types writeup |

Runs off the project-root environment — no separate install. See `07_Deep_Agents/CLAUDE.md` and `07_Deep_Agents/README.md` for details.

## Archive (`archive/`)

Retired notebooks, kept for reference but not part of the learning path: `04_Reference_Course/` (9 notebooks) and `Ultimate_RAG_Bootcamp/` (6 notebooks + PDFs).

---

## Known Discrepancies

**Fixed:**
- **Chapter 1** docs described 6 notebooks; the actual folder has **11** — `README.md`/`CLAUDE.md` now list all 11.
- **Chapter 3 (RAG)** had two files both prefixed `02_`, a missing `03_`, and file names that didn't match the README's documented titles or order — renamed to a clean `01–04` sequence matching the README's intended pedagogical order (simple → Databricks → advanced → RAG-as-tool).
- **`05_Agentic_Design_Patterns/02_Planning/`** had two files both prefixed `02_` covering the same `Send` API fan-out topic. The shorter/rougher one (`02_send.ipynb`) has been removed as a confirmed duplicate of `02_Map_Reduce_with_Send_API.ipynb`.
- **`07_Deep_Agents/`** didn't exist in this clone — now vendored in from `Deep_Agent_Demystified`, with `README.md`/`CLAUDE.md` updated to match. Its copied-in `pyproject.toml`/`requirements.txt`/`uv.lock`/`databricks.yml`/`CLAUDE.md` were duplicates of this repo's own root scaffolding (same package name, same stale content) — removed, since the root env already covers its dependencies (`deepagents`, `databricks-langchain`, `tavily-python`, `langgraph`). Its `.github/workflows/databricks-app-deploy.yml` was also dropped — GitHub Actions only reads workflows from the repo root's `.github/workflows/`, so it was inert at its nested location; wire it up at the root manually if you want the deploy pipeline.
- **`02_Core_Capabilities/07_Retries/`** existed but wasn't mentioned in the docs — now listed.
- README's `git clone` command used the wrong repo name (`LangGraph_Demystified` with an underscore instead of the actual `LangGraph-Demystified` with a hyphen) — fixed.

**Still open:**
- Several notebooks (e.g. `02_Core_Capabilities/01_Memory/02_Memory_Optimizations.ipynb`, `03_Human_in_the_Loop/01_HITL_Basics.ipynb`, `05_Subgraphs/01_Subgraphs.ipynb`) don't open with a proper `# Title` markdown cell — their first markdown cell is a mid-document subheading instead, so they don't follow the notebook convention documented in `CLAUDE.md` (title cell, then `##`/`###` hierarchy). Not fixed — would require editing notebook content, not just docs.
