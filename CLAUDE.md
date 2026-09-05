# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo is a growing, multi-phase **AI Engineering end-to-end roadmap**. It is organized into 13 numbered phases, each owning exactly one topic — never split the same topic across two phases, and never create a second home for a topic that already has one (see [Roadmap Structure](#roadmap-structure)). Where a topic has framework-specific implementations, they sit as sibling tracks *inside* the one phase that owns that topic (e.g. Phase 4 has both `RAG_with_LangGraph/` and `RAG_with_LangChain/`).

**Built so far:** Phases 2, 3, 4, 5, 7, 8, 13 (fully); Phases 1, 9, 10, 12 (partially). Phases 6, 11 are scaffolded placeholders (folder + scope-describing `README.md`) with no content yet.

For the full, current notebook-by-notebook listing of the built content, see `@NOTEBOOK_INDEX.md` — it is the source of truth for what actually exists, since `README.md`'s tables have historically drifted from it.

## Navigating This Repo — Check `graphify-out/` First

This repo has a local, gitignored code-graph snapshot at `graphify-out/` (produced by an external "Graphify" tool, last generated 2026-08-17 over ~554 files). **Before running a broad `Glob`/`Grep` sweep or opening files to find where something lives, check it first** — it exists specifically to cut down the exploration needed to answer "where is X" / "what touches Y" questions, which otherwise burns a lot of context on this large a repo:

- `graphify-out/GRAPH_REPORT.md` — human-readable: 225 named communities (clusters of related files/functions, e.g. "Adaptive RAG Retrieval Strategies", "Deep Agent Backend & Orchestrator"), god-nodes (most-connected core files), and cross-phase "surprising connections."
  Skim this first to identify which community/area owns the thing you're looking for.
- `graphify-out/graph.json` — the full node/edge graph (files, functions, classes, docs) with relationships (calls, imports, semantic similarity). Use this once you know the rough area, to pinpoint exact files/symbols before reading them.

**How to use it in practice:** grep or read `GRAPH_REPORT.md`/`graph.json` for the concept/file you care about, use what it points to in order to target your actual `Read`/`Edit`/`Grep` calls, instead of guessing paths or globbing wide directory trees.

**Caveats — this is a navigation aid, not a source of truth:**
- It's a snapshot from 2026-08-17. Anything added, moved, or edited since then (including everything reorganized in this session) won't appear in it, or may point at a stale path — if a lookup comes back empty or looks wrong, fall back to normal `Glob`/`Grep`/`Read` rather than assuming the file doesn't exist.
- Never edit based on what the graph *says* a file contains — always `Read` the actual current file before editing it. The graph tells you *where to look*, not what's currently there.
- If `graphify-out/` is ever missing (e.g. a fresh clone — it's `.gitignore`'d), just fall back to `Glob`/`Grep` as normal; regenerating it requires the external Graphify tool, which isn't part of this repo's own tooling.

## Roadmap Structure

```
01_Theory_and_Foundations/               ✅ Partially built — Hugging Face ecosystem, fine-tuning foundations, coding essentials built; math/ML intuition, transformer architecture, RLHF/DPO/LoRA planned
02_LangChain_Fundamentals_and_Prompting/ ✅ Built — LangChain basics (5 modules) + prompt engineering; context engineering planned
03_LangGraph_Fundamentals/               ✅ Built — LangGraph mechanics only (state, graphs, routing, tools, platform capabilities)
04_Retrieval_and_RAG/                    ✅ Built — foundational RAG theory + LangGraph/LangChain/LlamaIndex implementations
05_AI_Agent_Fundamentals/                ✅ Built — all agent-building content, both frameworks
06_Agent_SDKs_First_Party/               🚧 Planned — Google ADK, OpenAI Agents SDK, Google AI SDK
07_Advanced_Agentic_Systems/             ✅ Built — memory, multi-agent orchestration, deep agents, evaluation (RAG/agent/LLM-as-judge)
08_Advanced_RAG/                         ✅ Built — agentic/self-correcting RAG, GraphRAG, comprehensive RAG techniques; CacheRAG planned; needs Phases 5 & 7 first
09_Agent_Protocols/                      ✅ Partially built — MCP built; ACP, A2A planned
10_Alternative_Agent_Frameworks/         ✅ Partially built — CrewAI, AutoGen, DSPy built; PydanticAI + orchestration overview planned
11_Claude_Code_and_AI_Coding_Tools/      🚧 Planned
12_Production_and_Observability/         ✅ Partially built — LLMOps (LangSmith/caching/cost), safety (moderation); DevOps/security planned
13_Projects/                             ✅ Built — 12 projects: LangGraph/LangChain/RAG capstones + 9 more standalone full-stack apps
archive/                                 Retired notebooks from old Reference Course + RAG Bootcamp
docs/                                    Static HTML tutorial microsite (LangGraph mechanics chapters only, for now)
```

**Why RAG and Advanced RAG are separate phases, not duplicated:** Phase 4 covers foundational RAG that doesn't require knowing agents. Phase 8 covers agentic/self-correcting RAG and CacheRAG/GraphRAG, which genuinely depend on Phase 5 (agents) and Phase 7 (advanced agentic systems) — so it's sequenced after both rather than bundled into Phase 4. This was a deliberate, explicit decision after the roadmap's structure went through three revisions in one day (see `NOTEBOOK_INDEX.md`'s Known Discrepancies) — don't re-merge these two phases.

A project-organizing skill lives at `.claude/skills/ai-roadmap-organizer/` and should be consulted whenever new files/folders get dropped into this repo.

### Phase 1 — `01_Theory_and_Foundations/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `Model_Landscape_and_Hugging_Face/` | Hugging Face Hub setup, Transformers, Diffusers, audio/video models, Gradio (21 notebooks) |
| `Fine_Tuning_and_RL/` | SFT / data prep / training / eval (DeepLearning.AI labs) + Llama 2 AutoTrain; `02_Techniques/` (RLHF/DPO/LoRA) 🚧 Planned |
| `Coding_Essentials_for_Agents/` | Python, files/DBs, Flask APIs, raw LLM API calls, threading/GIL, asyncio |
| `Math_and_ML_Intuition/`, `Transformer_Architecture/` | 🚧 Planned |

### Phase 2 — `02_LangChain_Fundamentals_and_Prompting/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `LangChain_Fundamentals/`     | Getting started, I/O & prompts, LCEL, chains, summarization — true fundamentals only (5 modules) |
| `Prompt_and_Context_Engineering/Prompt_Engineering/` | Core/advanced prompting patterns, hands-on-by-model, multimodal, real-world applications |
| `Prompt_and_Context_Engineering/Context_Engineering/` | 🚧 Planned |

### Phase 3 — `03_LangGraph_Fundamentals/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `01_Foundations/`             | Core LangGraph mechanics: state, graphs, routing, tools, ReAct, Pydantic, node/command patterns (11 notebooks) |
| `02_Core_Capabilities/`       | Routing, human-in-the-loop, advanced state, subgraphs, async/streaming, retries |

### Phase 4 — `04_Retrieval_and_RAG/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `Introduction_to_RAG/`        | RAG overview, indexing, LangChain+RAG |
| `Embeddings_and_Vector_Databases/` | Embedding models, vector DB options, retrievers |
| `RAG_Naive_to_Production/`    | Loading → chunking → hybrid search → query enhancement → parent-doc retrieval → postprocessing → full pipelines |
| `Query_Transformation_Techniques/` | Multi-query, RAG-Fusion, decomposition, HyDE, routing, reranking |
| `Multimodal_and_Document_Intelligence/` | Multimodal RAG |
| `RAG_with_LangGraph/`         | Basic agentic RAG (2 notebooks) |
| `RAG_with_LangChain/`         | RAG essentials, comprehensive, filtered search, indexing API (4 notebooks) |
| `RAG_with_LlamaIndex/`        | Chainlit ReAct RAG chatbot over Wikipedia |

Also `shared_data/` at this phase's root — supporting PDFs/data referenced by several notebooks via relative paths inherited from the source repo (`RAG_Demystified`); not re-verified for exact path resolution after the move.

### Phase 5 — `05_AI_Agent_Fundamentals/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `LangChain_Tools_and_Agents/` | Tool calling, tool-calling agents, agents, + `03_Applied_Projects/` (16 applied builds) |
| `AI_Agents_with_LangGraph/`   | Full real-world agent builds (11) |
| `Workflow_and_Agent_Patterns/` | Named agentic design patterns — tool use, planning, reflection, router, prompt chaining, evaluator-optimizer, orchestrator-worker, advanced cognitive patterns (8 pattern subfolders, ~27 notebooks) |
| `Building_Agents_From_Scratch/` | OpenAI API + `agentic_patterns` package (no LangGraph) |

### Phase 7 — `07_Advanced_Agentic_Systems/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `Memory_and_State/`           | `LangGraph/` (memory & threads, long-term PostgreSQL memory) + `LangChain/` (chat/conversation memory, multi-user SQL persistence) |
| `Multi_Agent_Orchestration/`  | Supervisor pattern, multi-agent swarm architecture |
| `Deep_Agents_and_Harness_Engineering/` | Multi-agent orchestration via `deepagents` — see its own `CLAUDE.md` |
| `Evaluation_and_Eval_Harnesses/` | `RAG_Evaluation/` (retriever/generator/end-to-end metrics, DeepEval drills, RAGAS, LLM-as-judge G-Eval); `Agent_Evaluation/` (DeepLearning.AI + Arize labs, CrewAI travel-planner eval); `LLM_as_Judge/` (DeepEval G-Eval intro) |

### Phase 8 — `08_Advanced_RAG/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `RAG_with_LangGraph_Advanced/` | Self-correcting retrieval, corrective/adaptive RAG, healthcare router agentic RAG |
| `Comprehensive_RAG_Techniques/` | The NirDiamant `RAG_Techniques` anthology (~35 notebooks, kept whole — see its `README_ROADMAP.md`) |
| `RAG_Ecosystem/`              | Single-notebook RAG stack (basic → query transforms → RAPTOR/ColBERT → CRAG pointers → RAGAS) |
| `GraphRAG/`                   | Full knowledge-graph + RAG course |
| `CacheRAG/`                   | 🚧 Planned |
| `building-adaptive-rag/`, `mcp_a2a_agentic_rag/` | Standalone apps — MCP+A2A agentic RAG kept RAG-first here; a copy also lives under Phase 9 `MCP/` |

### Phase 9 — `09_Agent_Protocols/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `MCP/` | Foundations (Anthropic + Educative), building servers (Educative Mastering + Databricks Apps), building clients (MCP Essential), applications (Udemy MCP Mastery), plus `mcp_a2a_agentic_rag/` |
| `ACP/`, `A2A/` | 🚧 Planned |

### Phase 12 — `12_Production_and_Observability/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `LLMOps_and_AI_Infrastructure/` | `Tracing_and_Observability/` (LangSmith built, LangFuse planned, callbacks), `Caching_and_Performance/`, `Cost_Monitoring/` |
| `Safety_and_Alignment/`       | Content moderation, red teaming (`deepteam`) |
| `DevOps_and_Deployment/`, `Security_and_Compliance/` | 🚧 Planned |

### Phase 10 — `10_Alternative_Agent_Frameworks/` — internal tracks

| Track | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `CrewAI/`                     | `01_Foundations/` (basics + 8 simple agents + comprehensive tutorial), `02_Core_Capabilities/` (Flows), `03_Multi_Agent_Patterns/`, `04_Applications/` (9 project sets) |
| `AutoGen/`                    | Foundations (3 nb) + core labs (conversable/sequential/tools/code/multimodal) + group/swarm patterns + 8 application project sets |
| `DSPy/`                       | `context-engineering-dspy/` levels 1–5 (kept whole) |
| `PydanticAI/`, `Orchestration_Frameworks_Overview/` | 🚧 Planned |

### Phase 13 — `13_Projects/`

| Project | Content |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `LangGraph_Fullstack_Capstone/` | Full-stack app (FastAPI + Angular + Postgres), unit tests, Streamlit apps |
| `LangChain_Microservices_Capstone/` | LangChain deployed as microservices (Docker, k8s-style manifests, frontend) |
| `RAG_Systems_Projects/`       | 7 applied RAG capstone notebooks — document search engine, multi-user conversational RAG, multimodal RAG, Q&A systems |
| `ShopUNow_Agentic_RAG_Capstone/` | Vector DB + agentic RAG e-commerce capstone |
| `AI_Powered_Customer_Support/`, `Automated_Candidate_Interview_Evaluation_System/`, `End_to_End_Medical_Chatbot/`, `Pipecat_QuickStart/`, `Realtime_Source_Code_Analyzer/`, `Realtime_Voice_AI_Agent_with_RAG/`, `Personalized_Holiday_Management_Agent/`, `Resume_Genie/` | 8 more standalone full-stack apps |

## Environment Setup

```bash
uv venv --python 3.12
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Option A — the pinned, reproducible set (recommended)
uv pip install -r requirements.txt
uv pip install -e . --no-deps    # the local `helpers` package

# Option B — via extras
uv pip install -e ".[dev]"       # core spine + notebooks/pytest/ruff
uv pip install -e ".[all]"       # everything; equals the requirements.txt set

# Activate the git hooks — once per clone, and NOT optional if you run notebooks.
# Installing the packages does nothing on its own; this is what wires them in.
pre-commit install
```

`pre-commit` runs **nbstripout** on every commit, repo-wide (`archive/` included), so
notebooks cannot carry saved outputs into git. That matters for two reasons: notebooks here
ship with cleared outputs so a learner runs them fresh, and committed outputs have
previously leaked absolute filesystem paths. Verified against this repo's notebooks:
outputs are emptied and `execution_count` nulled, while cell `metadata.tags` and the
notebook `kernelspec` survive — the tags matter because the LangChain-1.x explainers mark
their 0.x contrast cells with them. Config: `.pre-commit-config.yaml`.

The distribution is named `ai_engineering_roadmap`. Core (`uv pip install -e .`) is the
LangChain/LangGraph/RAG spine only — ~65 packages. Everything else lives in eleven extras:

| Extra | Covers |
| ------------- | ------------------------------------------------------------------------ |
| `providers`   | Bedrock, Fireworks, Cohere, LiteLLM, Vertex AI, boto3 |
| `protocols`   | Phase 9 — fastmcp, a2a-sdk, google-adk, databricks-mcp |
| `frameworks`  | Phase 10 AutoGen + Phase 7 langmem/langgraph-swarm, mem0ai |
| `retrieval`   | Phases 4/8 — pinecone, pgvector, neo4j, faiss, document loaders |
| `hf`          | Phase 1 — transformers/torch/diffusers/peft/trl (large download) |
| `databricks`  | Databricks Connect, SQL connector, Unity Catalog |
| `eval`        | Phases 7/12 — deepeval, ragas, mlflow, arize-phoenix, pyrit |
| `data`        | scikit-learn, scipy, matplotlib, duckdb, yfinance |
| `fullstack`   | Phase 13 — FastAPI/Flask, Postgres/MySQL/Redis, docker |
| `apps`        | Streamlit + Gradio |
| `dev`         | jupyter, pytest, ruff, black, isort, pre-commit + nbstripout |

Always use `uv` for dependency management. `pyproject.toml` holds the version floors and is
the source of truth for *what* is a dependency; `requirements.txt` is the resolver-verified
pinned mirror (173 direct pins) and `requirements.lock.txt` the full 556-package transitive
lock. Update all three when adding deps — regenerate the lock with:

```bash
uv pip compile requirements.txt --python-version 3.12 -o requirements.lock.txt
```

`requirements.txt`'s header documents the deliberate exclusions (CrewAI cannot share an
environment with `langchain-chroma` 1.1 — it hard-pins `chromadb<1.2`; install it from its
own per-folder `requirements.txt` in a separate venv) and the 18 pins held below their latest
release by real upstream constraints. Don't "helpfully" bump those without re-resolving.

## Running Things

```bash
# Notebooks
jupyter lab

# Lint
ruff check .

# Streamlit apps
cd 13_Projects/LangGraph_Fullstack_Capstone/streamlit_apps/doc-entity-extractor
streamlit run app.py

# Full-stack capstone (FastAPI + Angular + Postgres)
cd 13_Projects/LangGraph_Fullstack_Capstone/fullstackapp
docker compose up
# Backend: localhost:8000, Frontend: localhost:5555, Postgres: localhost:5433

# Tests
cd 13_Projects/LangGraph_Fullstack_Capstone/unit_tests
pytest

# Deep Agents (runs off the root env — no separate install needed)
cd 07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering
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

Installed as an editable package (`hatchling` build). Imported in LangGraph-phase notebooks via:

```python
from helpers import get_llm, get_embeddings
```

`get_llm(provider=None, model=None, temperature=0, verbose=True)` and `get_embeddings(provider=None, model=None, verbose=True)` — both keyword-only, both platform-aware when `provider`/`model` are omitted.

**Platform-aware defaults** (auto-selected when no provider specified):

- **Windows**: Groq for LLM (`openai/gpt-oss-120b`), OpenAI for embeddings (`text-embedding-3-small`)
- **macOS**: Databricks (`databricks-claude-opus-4-6` for LLM, `databricks-gte-large-en` for embeddings)

Override: `get_llm(provider="openai", model="gpt-4o")`. Note `get_databricks_llm`'s own standalone default model is `databricks-gpt-5-2` — distinct from the macOS platform-default override above, which is applied by `get_llm()` specifically.

LangGraph-phase notebooks route all LLM/embedding initialization through this factory — never instantiate `ChatOpenAI`/`ChatGroq`/`ChatDatabricks` directly there. `LangChain_Fundamentals/` and its descendants, and the `RAG_Demystified`-sourced content in Phases 4/7/8/13, instantiate clients directly instead — a pre-existing property of the merged-in source repos, not a convention violation to fix.

### Agentic Patterns Covered

ReAct, Tool Use (direct + ReAct), RAG (foundational + agentic/self-correcting), Planning (parallel execution, `Send` API / map-reduce), Router, Prompt Chaining, Evaluator-Optimizer, Orchestrator-Worker, Reflection & Reflexion, Agent Patterns (supervisor, swarm), Long-Term Memory, plus a dozen advanced cognitive patterns (PEV, blackboard, tree-of-thoughts, RLHF, and others — see `05_AI_Agent_Fundamentals/Workflow_and_Agent_Patterns/11_Advanced_Cognitive_Patterns/`).

## Known Gaps (don't build against these as if they exist)

- **Every phase/track marked 🚧 Planned above has no content** — folders and scope-describing `README.md`s exist, but no notebooks/code. Don't assume any file exists under them without checking.
- Several LangGraph notebooks (e.g. `03_LangGraph_Fundamentals/02_Core_Capabilities/03_Human_in_the_Loop/01_HITL_Basics.ipynb`, `07_Advanced_Agentic_Systems/Memory_and_State/LangGraph/01_Memory/02_Memory_Optimizations.ipynb`) don't open with a proper `# Title` markdown cell — see `NOTEBOOK_INDEX.md`'s "Still open" section.
- Some `RAG_Demystified`-sourced notebooks in `04_Retrieval_and_RAG/RAG_Naive_to_Production/` reference a shared `data/` folder via relative paths (`../../data/`-style) that may not resolve correctly post-move — a copy was brought along as `04_Retrieval_and_RAG/shared_data/`, but exact path depth wasn't reconstructed.

## Notebook Conventions

- Title cell: `# Title` in first markdown cell
- Section headers use `##` / `###` / `####` hierarchy
- Code cells start with banner comments: `# ============ SECTION NAME ============`
- Imports grouped: stdlib → third-party → local (`from helpers import get_llm`)
- LangGraph-phase notebooks use the `helpers` factory for LLM initialization
- Final cell: summary markdown with key takeaways

## Conventions

- Python >= 3.11 required (target 3.12 for venv)
- Directory names use numeric prefixes without spaces for phases (e.g., `05_AI_Agent_Fundamentals/`), with descriptive track/topic names nested inside (e.g., `.../AI_Agents_with_LangGraph/`) — no need to quote these paths
- No linting was configured before this pass; `ruff` is now wired into `[tool.ruff]` in `pyproject.toml` (line length 100, target py311, rules `E,F,I,UP`) and excludes `archive/` and five JS frontends (`13_Projects/LangGraph_Fullstack_Capstone/fullstackapp/frontend`, `13_Projects/LangChain_Microservices_Capstone/frontend`, `07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering/app/frontend`, `10_Alternative_Agent_Frameworks/CrewAI/01_Foundations/Some_Simple_Agents/app/frontend`, `13_Projects/Realtime_Voice_AI_Agent_with_RAG/Codes/rag_voice_ai_agent-deployment_live/frontend`)
