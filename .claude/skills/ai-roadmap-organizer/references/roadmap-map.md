# Roadmap Map

This file is the skill's memory of the roadmap's actual shape. **Update it every time a phase or track is created, renamed, or changes status** — same discipline as `NOTEBOOK_INDEX.md`. Don't let it drift from disk.

The repo is 13 numbered phases, each owning **exactly one topic** — this is the hard-won rule (see History below): earlier structures let the same topic (RAG, agents, memory, observability) live in 2–3 different phases at once, which is what made the roadmap feel confusing. **Never create a second home for a topic that already has one.** Where a topic has framework-specific implementations, they're sibling tracks *inside* the one phase that owns it (e.g. Phase 4 has `RAG_with_LangGraph/` and `RAG_with_LangChain/` side by side, not split across two phases).

## Phase 2 — `02_LangChain_Fundamentals_and_Prompting/` — ✅ Built

Owns: LangChain's core building blocks + prompting. Does NOT own: RAG, tool-use/agents, memory, LangSmith/observability, deployment — each of those moved to the phase that owns that topic.

| Track | Status | Content |
|---|---|---|
| `LangChain_Fundamentals/` | ✅ Built | `01_Getting_Started` … `05_Summarization` — trimmed to true fundamentals |
| `Prompt_and_Context_Engineering/Prompt_Engineering/` | ✅ Built | Regrouped by technique from `Prompt-Engineering-Demystified` |
| `Prompt_and_Context_Engineering/Context_Engineering/` | 🚧 Planned | |

## Phase 3 — `03_LangGraph_Fundamentals/` — ✅ Built

Owns: LangGraph mechanics only. Does NOT own: RAG, agent builds, design patterns — those moved to Phases 4/5/8.

| Track | Status | Content |
|---|---|---|
| `01_Foundations/` | ✅ Built | State/graph basics through Command objects (11 nb) |
| `02_Core_Capabilities/` | ✅ Built | Routing, HITL, advanced state, subgraphs, async/streaming, retries. Memory moved to Phase 7. |

Note: `02_Routing/` contains 3 "Agentic RAG System" notebooks. By the topic-ownership rule these arguably belong in Phase 4 or 8, but the user explicitly chose to keep them here since they're this phase's only routing-mechanics demo — a deliberate exception, not an oversight. Don't move them without asking.

## Phase 4 — `04_Retrieval_and_RAG/` — ✅ Built

Owns: **foundational** RAG — theory + straightforward framework implementations, nothing that requires already knowing agents. Advanced/agentic RAG is Phase 8's job, not this one's.

| Track | Status | Content |
|---|---|---|
| `Introduction_to_RAG/` | ✅ Built | Overview, indexing, LangChain+RAG (from `RAG_Demystified`) |
| `Embeddings_and_Vector_Databases/` | ✅ Built | Embedding models, vector DB options, retrievers (from `RAG_Demystified`); embedding comparison + hybrid search/reranking (from `Vector_Database_and_Embedding_Demystified`) |
| `RAG_Naive_to_Production/` | ✅ Built | Loading → chunking → hybrid search → query enhancement → parent-doc retrieval → postprocessing → full pipelines (from `RAG_Demystified`) |
| `Query_Transformation_Techniques/` | ✅ Built | Multi-query, RAG-Fusion, decomposition, HyDE, routing, reranking — from `RAG_Demystified`'s "Advanced RAG" module; despite that name it's foundational, no agent knowledge needed, so it landed here not Phase 8 |
| `Multimodal_and_Document_Intelligence/` | ✅ Built (light) | Multimodal RAG (from `RAG_Demystified`) |
| `RAG_with_LangGraph/` | ✅ Built | 2 nb — basic agentic RAG (simple + Databricks variant) |
| `RAG_with_LangChain/` | ✅ Built | 4 nb — essentials, comprehensive, filtered search, indexing API |

Also `shared_data/` at this phase's root — a copy of `RAG_Demystified`'s shared `data/` folder, since several `RAG_Naive_to_Production/` notebooks reference it via relative paths. Path depth wasn't reconstructed exactly after the move (would require editing notebook content) — flag this if a notebook can't find its data file.

## Phase 5 — `05_AI_Agent_Fundamentals/` — ✅ Built

Owns: all agent-building content, both frameworks, in one place.

| Track | Status | Content |
|---|---|---|
| `LangChain_Tools_and_Agents/` | ✅ Built | Tool calling + agents (from `LangChain_Demystified`'s modules 06 & 10), plus `03_Applied_Projects/` (16 nb, from `AgenticAI_Projects_Demystified`) |
| `AI_Agents_with_LangGraph/` | ✅ Built | 11 real-world agent builds (8 original + 3 from `AgenticAI_Projects_Demystified` after 5 duplicates were skipped — see History §6) |
| `Workflow_and_Agent_Patterns/` | ✅ Built | 8 pattern subfolders, ~27 notebooks |

## Phase 6 — `06_Agent_SDKs_First_Party/` — 🚧 Planned

Promoted to its own top-level phase (was a track inside the old combined LangGraph phase). `Google_ADK/`, `OpenAI_Agents_SDK/`, `Google_AI_SDK/`.

## Phase 7 — `07_Advanced_Agentic_Systems/` — ✅ Partially built (3 of 4 tracks built)

Owns: composing agents into systems — memory, orchestration, harnesses, evaluation.

| Track | Status | Content |
|---|---|---|
| `Memory_and_State/` | ✅ Built | `LangGraph/` + `LangChain/` (from `LangChain_Demystified`'s module 05) — both frameworks' memory content consolidated here, not left in their fundamentals phases |
| `Multi_Agent_Orchestration/` | ✅ Built | Supervisor pattern + swarm |
| `Deep_Agents_and_Harness_Engineering/` | ✅ Built | The `deepagents` multi-agent framework — own `CLAUDE.md`, `app/`, `examples/`, `skills/`, `docs/`. **This directory (specifically its `app/` subfolder) has hit a Windows file lock 3 separate times** across different restructurings — always drain-contents-then-remove-shell, never assume `mv`/`git mv` will just work on it. |
| `Evaluation_and_Eval_Harnesses/` | ✅ Partially built | `RAG_Evaluation/` built (retriever/generator/end-to-end metrics, LLM-as-judge G-Eval — from `RAG_Demystified`); `Agent_Evaluation/`, `LLM_as_Judge/` still 🚧 planned |

## Phase 8 — `08_Advanced_RAG/` — ✅ Built

**Deliberately sequenced after Phases 5 and 7**, not bundled into Phase 4 — agentic/self-correcting RAG and GraphRAG genuinely require already knowing agents and advanced agentic systems. This was an explicit user correction mid-restructuring; don't merge this back into Phase 4 even though the topic is "RAG" in both — the ownership split here is by *prerequisite*, not by keyword.

| Track | Status | Content |
|---|---|---|
| `RAG_with_LangGraph_Advanced/` | ✅ Built | Self-correcting retrieval + RAG-as-tool (agentic RAG), extended with `RAG_Demystified`'s corrective/adaptive/healthcare-router agentic RAG notebooks |
| `Comprehensive_RAG_Techniques/` | ✅ Built | The NirDiamant `RAG_Techniques` collection (~35 nb) — kept whole rather than split by notebook, since it shares `helper_functions.py`/`data/`/`images/` across the collection via relative paths. Placed here (not Phase 4) because its own identity is an *advanced*-techniques anthology even though some individual notebooks are basic. |
| `GraphRAG/` | ✅ Built | Knowledge-graph + RAG course (from `RAG_Demystified`) |
| `CacheRAG/` | 🚧 Planned | |

Also two standalone apps merged from `RAG_Demystified`: `building-adaptive-rag/` and `mcp_a2a_agentic_rag/` (an MCP+A2A agentic RAG app — kept RAG-first here rather than split to Phase 9, per user decision).

## Phase 9 — `09_Agent_Protocols/` — 🚧 Planned

`MCP/` (4 subfolders), `ACP/` (3 subfolders), `A2A/` (3 subfolders).

## Phase 10 — `10_Alternative_Agent_Frameworks/` — ✅ Partially built

Frameworks to pick up *after* Phases 2/3/5 — each standalone. **If a new agent framework shows up and doesn't obviously belong to an earlier phase, this is very likely where it goes.**

| Track | Status | Content |
|---|---|---|
| `CrewAI/` | ✅ Built | `01_Foundations/Some_Simple_Agents/` (8 nb) + `04_Applications/` (9 project sets) — from `AgenticAI_Projects_Demystified` |
| `AutoGen/` | ✅ Built | `01_Foundations/Some_Simple_Agents/` (3 nb) + `04_Applications/` (7 project sets) — from `AgenticAI_Projects_Demystified` |
| `DSPy/`, `PydanticAI/`, `Orchestration_Frameworks_Overview/` | 🚧 Planned | |

Note: `02_Core_Capabilities/` and `03_Multi_Agent_Patterns/` were removed from both `CrewAI/` and `AutoGen/`'s skeleton when real content arrived, since the source repo's projects split cleanly into Foundations/Applications only — don't recreate those two subfolders unless content actually needs them.

## Phase 11 — `11_Claude_Code_and_AI_Coding_Tools/` — 🚧 Planned

`Claude_Code/`, `Agent_Skills/`, `Claude_API_and_Agent_SDK/`, `AI_Coding_Tool_Landscape/`.

## Phase 1 — `01_Theory_and_Foundations/` — 🚧 Planned (optional/compressible)

Math/ML intuition, transformer architecture, model landscape & Hugging Face, `Fine_Tuning_and_RL/`.

## Phase 12 — `12_Production_and_Observability/` — ✅ Partially built

Owns: deployment, LLMOps, observability, security, safety.

| Track | Status | Content |
|---|---|---|
| `LLMOps_and_AI_Infrastructure/` | ✅ Partially built | `Tracing_and_Observability/` (LangSmith built, LangFuse planned sibling, callbacks), `Caching_and_Performance/`, `Cost_Monitoring/` — all split out of `LangChain_Demystified`'s module 09 + 11 |
| `Safety_and_Alignment/` | ✅ Partially built | Content moderation (from module 09) |
| `DevOps_and_Deployment/`, `Security_and_Compliance/` | 🚧 Planned | |

## Phase 13 — `13_Projects/` — ✅ Built (10 projects)

Capstone/integration projects, kept flat (one folder per project, no grouping parent — explicit user decision even as the count grew past 10). `LangGraph_Fullstack_Capstone/` + `LangChain_Microservices_Capstone/` (from `LangChain_Demystified`'s module 12) + `RAG_Systems_Projects/` (7 nb, from `RAG_Demystified`'s Projects module) + `ShopUNow_Agentic_RAG_Capstone/` + 6 more standalone full-stack apps (`AI_Powered_Customer_Support/`, `Automated_Candidate_Interview_Evaluation_System/`, `End_to_End_Medical_Chatbot/`, `Pipecat_QuickStart/`, `Realtime_Source_Code_Analyzer/`, `Realtime_Voice_AI_Agent_with_RAG/` — all from `AgenticAI_Projects_Demystified`). More capstones get added here as new phases produce content worth integrating.

## `archive/`, `docs/`, root scaffolding

- `archive/` — retired/superseded notebooks, frozen, don't add to it proactively.
- `docs/` — static HTML tutorial microsite, mirrors Phase 3's LangGraph-mechanics chapters + a few others; internal links point at current phase paths, keep in sync if those move again.
- `helpers/`, `pyproject.toml`/`requirements.txt`/`uv.lock`/`databricks.yml`, `README.md`/`CLAUDE.md`/`NOTEBOOK_INDEX.md`, `links.md`, `LICENSE` — root scaffolding. `pyproject.toml`'s ruff `extend-exclude` hardcodes 3 JS frontend paths (LangGraph capstone, LangChain capstone, deep-agents app) — add a 4th if another JS app shows up.
- `.claude/skills-candidates/` — reusable Claude Code skills recovered from merged-in repos, not auto-loaded, awaiting the user's review. Add to this (don't silently merge into `.claude/skills/` or delete) whenever a merged repo has its own genuinely reusable skills.

## History: how we got to 13 phases (read before proposing another big restructuring)

1. LangGraph's 7 chapters sat loose at the repo root while other frameworks would've gotten named folders — inconsistent.
2. Fixed by nesting LangGraph under one `01_LangGraph/` parent — framework-per-folder pattern.
3. Replaced entirely with a **learning-phase** model (after the user pointed at `aie-learning-tracker.vercel.app`) — but each phase mixed multiple topics together (e.g. one phase held LangGraph mechanics AND RAG AND agents AND patterns all at once), which under the surface just relocated the duplication problem instead of solving it.
4. **This restructuring — the fix that stuck:** merging in `LangChain_Demystified` and `Prompt-Engineering-Demystified` exposed that RAG, agents, memory, and observability each had 2–3 different homes across phases (once for LangGraph's version, once buried inside a LangChain lump, sometimes a third empty "theory" placeholder too). The user's diagnosis, in their own words: "the structure seems little confusing... with duplicate RAG, and other module entries." Fixed by enforcing **one phase per topic**, splitting former multi-topic phases into single-topic ones (the old combined "LangGraph + Core Agent Concepts" phase became three: LangGraph Fundamentals, half of Retrieval & RAG, and half of AI Agent Fundamentals), and consolidating each framework's scattered coverage of a topic into that topic's one phase. Two further corrections during this pass, both worth remembering as precedent:
   - The user pushed back on an early version of this fix that tried to move RAG *out* of the agent-building phase entirely into a pure-theory phase — correctly pointing out that would put applied RAG *before* its framework prerequisite in the numbered sequence. Resolution: foundational RAG stays coupled to its framework (Phase 4), only the advanced/agentic variant — which has a *different* prerequisite (agents) — gets its own later phase (8).
   - Evaluation and Production/Observability didn't have real internal shape until concrete content (LangSmith, caching, cost monitoring, moderation) arrived — they were single flat placeholders. Real content forced them to grow actual subtopics (`Tracing_and_Observability/`, `Caching_and_Performance/`, `Cost_Monitoring/` inside Phase 12; `Agent_Evaluation/`/`RAG_Evaluation/`/`LLM_as_Judge/` inside Phase 7's Evaluation track).

If a fifth restructuring ever seems warranted, that's fine to raise — but re-read this history first, and specifically check whether the proposed change would reintroduce topic duplication across phases. That's the mistake this file exists to prevent repeating.

5. **2026-08-17 — `RAG_Demystified` merged in, no restructuring needed.** The 13-phase, one-topic-per-phase model held up: every one of the ~350 source files had an obvious home, and the merge filled 5 previously-empty placeholders (`Embeddings_and_Vector_Databases/`, `RAG_Naive_to_Production/`, `Multimodal_and_Document_Intelligence/`, `RAG_Evaluation/`, `GraphRAG/`) rather than requiring new phases. Confirms the structure is stable for RAG-topic content specifically — take that as a signal the model is working, not as license to skip checking `roadmap-map.md` before the next merge. Two new patterns worth remembering:
   - **Source folders with shared internal dependencies** (a `helper_functions.py`/`data/`/`images/` used by dozens of notebooks via relative paths) should move as one intact unit, not be split notebook-by-notebook even when individual notebooks would otherwise belong in different phases by topic. `Comprehensive_RAG_Techniques/` in Phase 8 is the reference example — it contains some basic-level notebooks that would "belong" in Phase 4 by strict topic rules, but splitting them out would break the shared imports. When this tension comes up, prefer keeping the collection whole and place it by its own dominant identity, and say so explicitly in its README.
   - **Windows/Git-Bash `mv` can silently misbehave** with multi-source globs (`mv "$SRC"/* "$DEST/"`) when `$DEST` doesn't exist or under certain path-quoting conditions — in this merge it briefly renamed an *existing, unrelated* destination folder (`RAG_with_LangGraph_Advanced/`) to `AgenticRAG` mid-command instead of erroring cleanly. No data was lost (caught via notebook-count verification before/after), but the fix required manually diagning what happened. Prefer the item-by-item `for item in "$SRC"/*; do mv "$item" "$DEST/$(basename "$item")"; done` loop over `mv "$SRC"/* "$DEST/"` when moving multiple items into an existing directory — it's what already reliably works around the Windows directory-lock issue too (see Phase 7 above), so just use it as the default move pattern in this repo rather than reaching for the shortcut form.

6. **2026-08-17 — `AgenticAI_Projects_Demystified` merged in; check for duplicates BEFORE mapping content, not after.** This repo turned out to share an author/ecosystem with `Agentic_Design_Pattern_Demystified` (merged much earlier) — 5 of its "Projects with LangGraph" folders were byte-identical or near-identical to notebooks already in `AI_Agents_with_LangGraph/`. Caught this by comparing file sizes (`ls -la`) between the new source folder and the existing destination *before* doing any moves, for every project whose name looked familiar. **New standing practice: whenever a merged-in repo has project/notebook names that echo anything already in `NOTEBOOK_INDEX.md`, diff file sizes (or content) before merging — don't assume a name match means duplicate, and don't assume a name match means safe-to-merge either; check.** This merge also filled Phase 10 (Alternative Agent Frameworks) from fully-planned to partially-built in one step (`CrewAI/` + `AutoGen/`) — first time a phase jumped straight from empty to built rather than growing incrementally.
