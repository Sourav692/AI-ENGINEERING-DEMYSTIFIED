# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo is a growing, multi-phase **AI Engineering end-to-end roadmap**. It is organized into 15 numbered phases (`00_`–`14_`, 0-indexed on disk), each owning exactly one topic — never split the same topic across two phases, and never create a second home for a topic that already has one (see [Roadmap Structure](#roadmap-structure)). Where a topic has framework-specific implementations, they sit as sibling tracks *inside* the one phase that owns that topic (e.g. Phase 4 has both `RAG_with_LangGraph/` and `RAG_with_LangChain/`).

**Built so far (disk numbering):** 00, 01, 02, 03, 04, 05, 07, 08, 13, 14 (fully); 09, 10, 12 (partially). 06 and 11 are scaffolded placeholders with no content yet.

**Evaluation is not in this repo.** It lives in the sibling repo `Agent_Evaluation_Demystified` (removed here 2026-09-19 after a content-hash comparison found 147 duplicated files and none unique). Don't recreate an evaluation track here.

For the full, current notebook-by-notebook listing of the built content, see `@NOTEBOOK_INDEX.md` — it is the source of truth for what actually exists, since `README.md`'s tables have historically drifted from it.

## Roadmap Structure

```
01_Foundations/                              no prerequisites
  00_Theory_and_Foundations/                 ✅ Partially built — HF ecosystem, fine-tuning foundations, coding essentials; math/ML intuition, transformer architecture, RLHF/DPO/LoRA planned
  02_Prompt_and_Context_Engineering/         ✅ Built — prompt engineering; context engineering planned

02_Core/                                     needs Foundations
  01_LangChain_Fundamentals/                 ✅ Built — LangChain basics (5 modules)
  03_LangGraph_Fundamentals/                 ✅ Built — LangGraph mechanics only (state, graphs, routing, tools, platform capabilities)
  04_Retrieval_and_RAG/                      ✅ Built — foundational RAG theory + LangGraph/LangChain/LlamaIndex implementations
  05_AI_Agent_Fundamentals/                  ✅ Built — all agent-building content, both frameworks

03_Advanced/                                 needs Core (specifically agents)
  06_Agent_SDKs_First_Party/                 🚧 Planned — Google ADK, OpenAI Agents SDK, Google AI SDK, Anthropic Agent SDK
  07_Advanced_Agentic_Systems/               ✅ Built — memory, multi-agent orchestration, deep agents
  08_Advanced_RAG/                           ✅ Built — agentic/self-correcting RAG, GraphRAG, comprehensive RAG techniques; CacheRAG planned
  09_Agent_Protocols/                        ✅ Partially built — MCP built; ACP, A2A planned
  10_Alternative_Agent_Frameworks/           ✅ Partially built — CrewAI, AutoGen, DSPy built; PydanticAI + orchestration overview planned
  12_Production_and_Observability/           ✅ Partially built — LLMOps (LangSmith/caching/cost), safety (moderation); DevOps/security planned

04_AI_Coding_Tools/                          🚧 Planned — Claude Code, Codex, Cursor, Agent Skills, Claude API & Agent SDK
05_Projects/                                 ✅ Built — 16 projects: capstones + standalone apps + 3 enterprise platforms
06_Interview_Prep/                           ✅ Built — Handbook · FDE ⚠purchased · AI_Engineer · OpenAI_Applied · Study_Guides

archive/                                     Retired notebooks, frozen — never reorganize
docs/  helpers/  plugins/  site/             Support: microsite, LLM factory, plugin, Next.js site
```

**Stage folders group phases by prerequisite, not by difficulty** (added 2026-09-19). "Advanced" means *requires agents knowledge*, which is objective and stable — it is the same criterion that keeps foundational RAG in `02_Core/04_` and agentic RAG in `03_Advanced/08_`. Phase numbers inside the stages are the original ones and were deliberately not renumbered: every "Phase 7" reference across the docs stays true, and the gap (no `11_` under `03_Advanced/`) is the cost of that.

**Evaluation is not in this repo.** It lives in the sibling repo `Agent_Evaluation_Demystified`. Removed here 2026-09-19 after a content-hash comparison found 147 duplicated files and none unique. Don't recreate an evaluation track.

**Why RAG and Advanced RAG are separate phases, not duplicated:** Phase 4 covers foundational RAG that doesn't require knowing agents. Phase 8 covers agentic/self-correcting RAG and CacheRAG/GraphRAG, which genuinely depend on Phase 5 (agents) and Phase 7 (advanced agentic systems) — so it's sequenced after both rather than bundled into Phase 4. This was a deliberate, explicit decision after the roadmap's structure went through three revisions in one day (see `NOTEBOOK_INDEX.md`'s Known Discrepancies) — don't re-merge these two phases.

A project-organizing skill lives at `.claude/skills/ai-roadmap-organizer/` and should be consulted whenever new files/folders get dropped into this repo.

The five LangChain 1.x migration pipeline skills (audit → plan-to-tasks → plan-to-teaching-notebook → notebook-review, plus the `langchain-v1-pipeline` runner) are grouped as a local plugin at `plugins/langchain-v1-migration/`, registered via `.claude-plugin/marketplace.json` and enabled in `.claude/settings.json`. Invoke them as `/langchain-v1-migration:<skill>`; call their scripts by repo-relative path under `plugins/langchain-v1-migration/skills/`.

## Per-phase `CLAUDE.md` — read the one for the folder you're in

Every phase carries its own `CLAUDE.md`. Claude Code loads the root file always, plus any `CLAUDE.md` in a subdirectory when it touches files under that subtree, so they compose — this file holds only what is cross-cutting.

**The per-phase track tables that used to live here have moved into those files.** Keeping them in two places is the same duplication the one-topic-one-phase rule exists to prevent. Go to the phase file for what a phase contains, what conventions apply inside it, and what must not be added to it.

**Stage files** — loaded whenever you work anywhere under that stage. They carry the stage's entry rule and a routing table for which phase owns which topic.

| Stage file | Covers |
|---|---|
| `01_Foundations/CLAUDE.md` | entry rule: no framework dependency; why `helpers` is deliberately unused across the whole stage |
| `02_Core/CLAUDE.md` | routing across the four core phases; **`helpers` usage is not uniform here** — a per-phase table |
| `03_Advanced/CLAUDE.md` | entry rule: requires agent knowledge; stage-wide gotchas (CrewAI env, Deep Agents file lock, don't-split rules) |

**Phase files** — loaded on top of the stage file when you work inside that phase.

| Phase file | Covers |
|---|---|
| `01_Foundations/00_Theory_and_Foundations/CLAUDE.md` | HF ecosystem, fine-tuning, coding essentials — and why the `helpers` factory is deliberately unused here |
| `01_Foundations/02_Prompt_and_Context_Engineering/CLAUDE.md` | prompting as a discipline; what belongs to LangChain instead |
| `02_Core/01_LangChain_Fundamentals/CLAUDE.md` | LangChain mechanics; why direct client instantiation here is not a violation |
| `02_Core/03_LangGraph_Fundamentals/CLAUDE.md` | LangGraph mechanics; strongest `helpers` requirement in the repo |
| `02_Core/04_Retrieval_and_RAG/CLAUDE.md` | foundational RAG, 10 tracks, the `shared_data/` naming rule |
| `02_Core/05_AI_Agent_Fundamentals/CLAUDE.md` | all agent building, both frameworks; the `N. Name` folder convention |
| `03_Advanced/06_Agent_SDKs_First_Party/CLAUDE.md` | vendor-native SDKs; first-party vs third-party boundary |
| `03_Advanced/07_Advanced_Agentic_Systems/CLAUDE.md` | memory, orchestration, deep agents; the Deep Agents file-lock gotcha |
| `03_Advanced/08_Advanced_RAG/CLAUDE.md` | agentic RAG; why `Comprehensive_RAG_Techniques/` must not be split |
| `03_Advanced/09_Agent_Protocols/CLAUDE.md` | MCP built, ACP/A2A planned; per-subproject environments |
| `03_Advanced/10_Alternative_Agent_Frameworks/CLAUDE.md` | CrewAI/AutoGen/DSPy; the CrewAI `chromadb<1.2` conflict |
| `03_Advanced/12_Production_and_Observability/CLAUDE.md` | LLMOps, safety; the observability-vs-evaluation line |
| `04_AI_Coding_Tools/CLAUDE.md` | Claude Code, Codex, Cursor, Agent Skills |
| `05_Projects/CLAUDE.md` | 16 projects, one venv each, the ruff-exclude rule |
| `06_Interview_Prep/CLAUDE.md` | ⚠ purchased material and the path-anchored `.gitignore` that protects it |

Files compose rather than override: root → stage → phase → any deeper file. Two deeper files also exist and take precedence inside their trees: `03_Advanced/07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering/CLAUDE.md` and `site/CLAUDE.md`.

## Path-anchored config — repoint these whenever a folder moves

Three places hard-code repository paths. All three broke silently during the 2026-09-19 restructure and were caught only by explicit checking. **If you move a folder, fix these in the same commit:**

| File | What it anchors | Failure mode |
|---|---|---|
| `.gitignore` lines ~160–162 | keeps purchased FDE material out of git except `.md` | ~107 vendor PDFs silently become committable |
| `site/scripts/sync-content.mjs` `SOURCE_ROOT` | the public site builds from `06_Interview_Prep/FDE` | site build reads a dead path |
| `pyproject.toml` `[tool.ruff] extend-exclude` | 5 JS frontend paths | frontends get linted as Python |

Verification after any move — **this is now automated**, run it directly or let the
commit hook run it:
```bash
python3 scripts/check_repo_invariants.py
```
It asserts, repo-wide: every notebook is valid JSON and non-empty; every relative
`data/` reference in a code cell resolves; every path named in `NOTEBOOK_INDEX.md`'s
phase headings, `THEORY_DOCS_INDEX.md`'s headings and `Study_Guides/TOPIC_DOCS_MAP.md`'s
links exists; all three path-anchored configs above still point at real folders; and no
vendor `.pdf`/`.docx`/`.pptx` is tracked under `06_Interview_Prep/FDE`. Takes ~0.6s over
526 notebooks and is wired into `.pre-commit-config.yaml`, so a commit that breaks any of
them fails.

**Each check exists because that thing actually broke silently**, most of them during the
2026-09-19 restructure. Fix the path or the doc — don't weaken the check. The one
deliberate exclusion is a `PROSE_NOT_PATHS` set in the script, for English text like
"data/AI technologies" that pattern-matches as a path; it is keyed on the whole token so a
real path cannot be silenced by accident.


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
cd 05_Projects/LangGraph_Fullstack_Capstone/streamlit_apps/doc-entity-extractor
streamlit run app.py

# Full-stack capstone (FastAPI + Angular + Postgres)
cd 05_Projects/LangGraph_Fullstack_Capstone/fullstackapp
docker compose up
# Backend: localhost:8000, Frontend: localhost:5555, Postgres: localhost:5433

# Tests
cd 05_Projects/LangGraph_Fullstack_Capstone/unit_tests
pytest

# Deep Agents (runs off the root env — no separate install needed)
cd 03_Advanced/07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering
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

ReAct, Tool Use (direct + ReAct), RAG (foundational + agentic/self-correcting), Planning (parallel execution, `Send` API / map-reduce), Router, Prompt Chaining, Evaluator-Optimizer, Orchestrator-Worker, Reflection & Reflexion, Agent Patterns (supervisor, swarm), Long-Term Memory, plus a dozen advanced cognitive patterns (PEV, blackboard, tree-of-thoughts, RLHF, and others — see `02_Core/05_AI_Agent_Fundamentals/Workflow_and_Agent_Patterns/11_Advanced_Cognitive_Patterns/`).

## Known Gaps (don't build against these as if they exist)

- **Every phase/track marked 🚧 Planned above has no content** — folders and scope-describing `README.md`s exist, but no notebooks/code. Don't assume any file exists under them without checking.
- **154 notebooks** don't open with a proper `# Title` markdown cell (counted 2026-09-19, excluding `archive/` and `site/`) — e.g. `02_Core/03_LangGraph_Fundamentals/02_Core_Capabilities/05_Subgraphs/01_Subgraphs.ipynb`, `03_Advanced/07_Advanced_Agentic_Systems/Memory_and_State/LangGraph/01_Memory/02_Memory_Optimizations.ipynb`. Fixing it means editing notebook content, so it is deliberately unfixed. See `NOTEBOOK_INDEX.md`'s "Still open" section.

## Notebook Conventions

- Title cell: `# Title` in first markdown cell
- Section headers use `##` / `###` / `####` hierarchy
- Code cells start with banner comments: `# ============ SECTION NAME ============`
- Imports grouped: stdlib → third-party → local (`from helpers import get_llm`)
- LangGraph-phase notebooks use the `helpers` factory for LLM initialization
- Final cell: summary markdown with key takeaways

## Conventions

- Python >= 3.11 required (target 3.12 for venv)
- Directory names use numeric prefixes without spaces for phases (e.g., `02_Core/05_AI_Agent_Fundamentals/`), with descriptive track/topic names nested inside (e.g., `.../AI_Agents_with_LangGraph/`) — no need to quote these paths
- No linting was configured before this pass; `ruff` is now wired into `[tool.ruff]` in `pyproject.toml` (line length 100, target py311, rules `E,F,I,UP`) and excludes `archive/` and five JS frontends (`05_Projects/LangGraph_Fullstack_Capstone/fullstackapp/frontend`, `05_Projects/LangChain_Microservices_Capstone/frontend`, `03_Advanced/07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering/app/frontend`, `03_Advanced/10_Alternative_Agent_Frameworks/CrewAI/01_Foundations/Some_Simple_Agents/app/frontend`, `05_Projects/Realtime_Voice_AI_Agent_with_RAG/Codes/rag_voice_ai_agent-deployment_live/frontend`)
