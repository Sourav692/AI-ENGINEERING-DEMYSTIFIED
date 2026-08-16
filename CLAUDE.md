
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Educational repository teaching agentic AI design patterns using LangGraph. Contains Jupyter notebooks organized by chapter/difficulty, Streamlit apps, and a full-stack capstone project. Package name: `langgraph_demystified` (see `pyproject.toml`).

For the full, current notebook-by-notebook listing (with topics), see `@NOTEBOOK_INDEX.md` — it is the source of truth for what actually exists, since `README.md`'s chapter tables have drifted from the real files (see Known Gaps below).

## Environment Setup

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"       # includes pytest, jupyter, ruff
# or install everything: uv pip install -e ".[all]"
# extras: [dev], [apps] (streamlit), [fullstack] (fastapi+postgres), [all]
```

Always use `uv` for dependency management. `pyproject.toml` is the single source of truth for dependencies; `requirements.txt` is a pinned mirror — update both when adding deps.

## Running Things

```bash
# Notebooks
jupyter lab

# Lint
ruff check .

# Streamlit apps
cd 06_Production/streamlit_apps/doc-entity-extractor
streamlit run app.py

# Full-stack capstone (FastAPI + Angular + Postgres)
cd 06_Production/fullstackapp
docker compose up
# Backend: localhost:8000, Frontend: localhost:5555, Postgres: localhost:5433

# Tests
cd 06_Production/unit_tests
pytest

# Deep Agents (runs off the root env — no separate install needed)
cd 07_Deep_Agents
python examples/simple_coding_agent.py
```

## Required Environment Variables (.env at project root)

- `OPENAI_API_KEY` — OpenAI models
- `GROQ_API_KEY` — Groq models (used on Windows)
- `GOOGLE_API_KEY` — LangExtract Streamlit apps
- `TAVILY_API_KEY` — web search notebooks
- Databricks credentials — used on macOS (default provider)

## Architecture

### `helpers/` — Shared LLM/Embedding Factory Package

Installed as an editable package (`hatchling` build). Imported in all notebooks via:

```python
from helpers import get_llm, get_embeddings
```

`get_llm(provider=None, model=None, temperature=0, verbose=True)` and `get_embeddings(provider=None, model=None, verbose=True)` — both keyword-only, both platform-aware when `provider`/`model` are omitted.

**Platform-aware defaults** (auto-selected when no provider specified):

- **Windows**: Groq for LLM (`openai/gpt-oss-120b`), OpenAI for embeddings (`text-embedding-3-small`)
- **macOS**: Databricks (`databricks-claude-opus-4-6` for LLM, `databricks-gte-large-en` for embeddings)

Override: `get_llm(provider="openai", model="gpt-4o")`. Note `get_databricks_llm`'s own standalone default model is `databricks-gpt-5-2` — distinct from the macOS platform-default override above, which is applied by `get_llm()` specifically.

All LLM/embedding initialization in notebooks goes through this factory — never instantiate `ChatOpenAI`/`ChatGroq`/`ChatDatabricks` directly in a notebook.

### Tutorial Structure

| Directory                       | Content                                                                                                    |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `01_Foundations/`             | Core LangGraph: state, graphs, routing, tools, ReAct, Pydantic, node/command patterns (11 notebooks)       |
| `02_Core_Capabilities/`       | Platform features: memory, routing, HITL, advanced state, subgraphs, async/streaming, retries (7 sections) |
| `03_RAG/`                     | Retrieval-augmented generation: basic → Databricks → advanced → RAG-as-tool                             |
| `04_Agents/`                  | Real-world agents: research assistant, competitive intelligence                                            |
| `05_Agentic_Design_Patterns/` | Design patterns: tool use, planning, agent patterns, long-term memory                                      |
| `06_Production/`              | Deployment: full-stack app, unit tests, Streamlit apps                                                     |
| `07_Deep_Agents/`              | Multi-agent orchestration via `deepagents` — see its own `CLAUDE.md`                                      |
| `docs/`                       | Static HTML tutorial microsite (`chapter-1.html`…`chapter-7.html`)                                    |
| `archive/`                    | Retired notebooks from old Reference Course + RAG Bootcamp                                                 |
| `databricks.yml`              | Databricks Asset Bundle config (required by the Databricks VS Code extension; single`dev` target)        |

### Agentic Patterns Covered

ReAct, Tool Use (direct + ReAct), RAG (standalone + as-tool), Planning (parallel execution, `Send` API / map-reduce), Agent Patterns (supervisor), Long-Term Memory.

## Known Gaps (don't build against these as if they exist)

- **`05_Agentic_Design_Patterns/03_Reflection/` does not exist.** Numbering jumps `02_Planning` → `04_Agent_Patterns`; Reflection is unimplemented ("coming soon" per README).

## Notebook Conventions

- Title cell: `# Title` in first markdown cell
- Section headers use `##` / `###` / `####` hierarchy
- Code cells start with banner comments: `# ============ SECTION NAME ============`
- Imports grouped: stdlib → third-party → local (`from helpers import get_llm`)
- LLM initialization uses the `helpers` factory, never direct provider instantiation
- Final cell: summary markdown with key takeaways

## Conventions

- Python >= 3.11 required (target 3.12 for venv)
- Directory names use numeric prefixes without spaces (e.g., `01_Foundations/`, `05_Agentic_Design_Patterns/01_Tool_Use/`) — no need to quote these paths
- No linting was configured before this pass; `ruff` is now wired into `[tool.ruff]` in `pyproject.toml` (line length 100, target py311, rules `E,F,I,UP`) and excludes `archive/` and the Angular frontend
