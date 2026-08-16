# Notebook Index

A single, accurate table of every notebook in this repo, in the order they're meant to be worked through. This reflects the **actual files on disk**. `README.md` and `CLAUDE.md` have since been reconciled to match (see [Known Discrepancies](#known-discrepancies) below for what was fixed and what's still open).

This repo is organized as a sequence of 13 **phases**, each owning exactly one topic — no duplication, framework-specific implementations sit as sibling tracks inside the phase that owns their topic. **Built so far: Phases 2, 3, 5, 13 (fully); Phases 4, 7, 8, 12 (partially).** Phases 1, 6, 9, 10, 11 are scaffolded placeholders with no content yet.

# Phase 2 — LangChain Fundamentals & Prompting (`02_LangChain_Fundamentals_and_Prompting/`)

## `LangChain_Fundamentals/`

| # | Module | Topic |
|---|---|---|
| 1 | `01_Getting_Started/` | Commercial + open-source LLMs, natively and via LangChain (8 nb) |
| 2 | `02_Inputs_Outputs_Prompts/` | Inputs/outputs, prompt templates, LLM vs ChatModel, output parsers (6 nb) |
| 3 | `03_LCEL/` | LangChain Expression Language, Runnables, chain migrations (7 nb) |
| 4 | `04_Chains/` | Chain basics, advanced chains, branching/routing/merging (4 nb) |
| 5 | `05_Summarization/` | Text summarization (2 nb) |

Also has `Docs/` (supporting PDFs/CSV), `images/`, `Reference_Links.md`. Tool-calling/agents, memory, RAG, LangSmith, advanced features, and microservices deployment moved to their own dedicated phases (see Known Discrepancies).

## `Prompt_and_Context_Engineering/Prompt_Engineering/`

| Section | Notebook | Topic |
|---|---|---|
| `01_Core_Patterns/` | `M2_Exploring_Prompt_Engineering_Patterns.ipynb` | Core prompt-engineering patterns |
| `02_Advanced_Patterns/` | `M3_Exploring_Advanced_Prompt_Engineering_Patterns.ipynb` | Advanced prompt-engineering patterns |
| `03_Hands_On_by_Model/` | `M5_Google_Gemini.ipynb`, `M5_OpenAI_ChatGPT.ipynb`, `M6_Meta_Llama_3_2_1B_HuggingFace.ipynb`, `M6_Meta_Llama_3_2_90B_Groq.ipynb` | Hands-on pattern practice across 4 models/providers |
| `04_Multimodal_Prompting/` | `M7_Google_Gemini.ipynb`, `M7_OpenAI_GPT_4o.ipynb` | Multimodal prompting |
| `05_Real_World_Applications/` | `M7_GPT_4o_and_Llama_3_2_Real_World_Tasks.ipynb` | Applying patterns to real-world tasks |
| `Assignments/` | `Assignment.ipynb` | Practice assignment (+ PDF, images) |

## `Prompt_and_Context_Engineering/Context_Engineering/` — 🚧 Planned

# Phase 3 — LangGraph Fundamentals (`03_LangGraph_Fundamentals/`)

## `01_Foundations/`

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

## `02_Core_Capabilities/`

Memory lives in Phase 7 instead — see below.

| Section | Notebook | Topic |
|---|---|---|
| `02_Routing/` | `01_Router_Agentic_RAG_System.ipynb` | Customer-support router agentic RAG system |
| `02_Routing/` | `02_Customer_Support_Router_RAG_Alt.ipynb` | Alternate implementation |
| `02_Routing/` | `03_Customer_Support_Router_RAG_Databricks_Alt.ipynb` | Databricks Vector Search variant |
| `03_Human_in_the_Loop/` | `01_HITL_Basics.ipynb` | Human-in-the-loop basics |
| `03_Human_in_the_Loop/` | `02_HITL_Interrupt_and_Resume.ipynb` | Interrupt/resume approaches |
| `03_Human_in_the_Loop/` | `03_HITL_State_Modification.ipynb` | Approve/reject + state modification pattern |
| `03_Human_in_the_Loop/` | `04_HITL_Dynamic_Breakpoints.ipynb` | Dynamic breakpoints, reviewing tool calls |
| `04_Advanced_State/` | `01_Advanced_State.ipynb` | Input/output state, advanced state patterns |
| `05_Subgraphs/` | `01_Subgraphs.ipynb` | Graph composition via subgraphs |
| `06_Async_and_Streaming/` | `01_Async_and_Streaming.ipynb` | Async operations & streaming output |
| `07_Retries/` | `01_Retries.ipynb` | Fault-tolerant nodes with `RetryPolicy` |

Note: `02_Routing/`'s notebooks are also agentic RAG examples — kept here rather than moved to Phase 4/8 since they're the only routing-mechanics demo in this phase (see Known Discrepancies).

# Phase 4 — Retrieval & RAG (`04_Retrieval_and_RAG/`)

Foundational RAG only. Agentic/advanced RAG lives in Phase 8.

## `RAG_with_LangGraph/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_Simple_Agentic_RAG.ipynb` | Simple RAG agent (PDF → Chroma → LLM) |
| 2 | `02_Simple_Agentic_RAG_Databricks.ipynb` | Same agent on Databricks Vector Search |

## `RAG_with_LangChain/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `7.0_RAG_Essentials.ipynb` | RAG essentials |
| 2 | `7.1_RAG_Comprehensive.ipynb` | Comprehensive RAG |
| 3 | `7.2_Filtered_Search.ipynb` | Filtered search |
| 4 | `7.3_Indexing_API.ipynb` | Indexing API |

Plus supporting `api.py`, `docker-compose.yaml`, FAISS/Postgres assets.

## `Embeddings_and_Vector_Databases/`, `RAG_Naive_to_Production/`, `Multimodal_and_Document_Intelligence/` — 🚧 Planned

# Phase 5 — AI Agent Fundamentals (`05_AI_Agent_Fundamentals/`)

## `LangChain_Tools_and_Agents/`

| # | Section | Topic |
|---|---|---|
| 1 | `01_Tools_and_Functions/` | Tool calling, tool-calling agents, OpenAI tool calling (4 nb) |
| 2 | `02_Agents/` | Agents (1 nb) |

## `AI_Agents_with_LangGraph/`

| # | Notebook / Folder | Topic |
|---|---|---|
| 1 | `01_Research_Assistant_Chatbot.ipynb` | Web-search research assistant (Tavily) |
| 2 | `02_Competitive_Intelligence_Agent.ipynb` | Business/competitive intelligence agent with structured output |
| 3 | `03_Multi_Agent_Research_Summarization/` | Multi-agent research + summarization pipeline |
| 4 | `04_Planning_Agent_Deep_Research/` | Planning-pattern deep research agent |
| 5 | `05_Reflective_Code_Generation_Agent/` | Reflective, self-correcting code generation agent |
| 6 | `06_Reflective_Dynamic_Planning_Agent/` | Reflective dynamic planning agent |
| 7 | `07_Supervisor_Multi_Agent_Financial_Research/` | Supervisor-pattern multi-agent financial research system |
| 8 | `08_Web_Research_Agent_ReAct_Alt.ipynb` | Alternate ReAct-pattern web research agent |

## `Workflow_and_Agent_Patterns/`

| Section | Notebook | Topic |
|---|---|---|
| `01_Tool_Use/` | `01_Tool_Use_Agentic_Systems.ipynb`, `02_Tool_Calling_vs_ReAct.ipynb`, `03_Tool_Use_Alt.ipynb`, `04_ReAct_Alt.ipynb` | Tool-use strategies |
| `02_Planning/` | `01_Parallel_Steps_Execution.ipynb`, `02_Map_Reduce_with_Send_API.ipynb`, `03_Parallelization_Alt.ipynb`, `04_Planning_Overview_Alt.ipynb` | Planning patterns |
| `03_Reflection/` | `01_Reflection_Agents.ipynb`, `02_Reflexion_Agents.ipynb`, `03/04_Reflection_Overview_Alt*.ipynb` | Reflection & Reflexion |
| `06_Router/` | `01_Routing.ipynb` | Router pattern |
| `07_Prompt_Chaining/` | `01_Prompt_Chaining.ipynb` | Sequential prompt-chaining |
| `08_Evaluator_Optimizer/` | `01_Evaluator_Optimizer.ipynb` | Evaluator-optimizer loop |
| `09_Orchestrator_Worker/` | `01_Orchestrator_Worker.ipynb` | Runtime-dynamic task delegation |
| `11_Advanced_Cognitive_Patterns/` | `01`–`12` | PEV, blackboard, episodic+semantic memory, tree-of-thoughts, mental loop, meta-controller, graph, ensemble, dry-run, RLHF, cellular automata, reflexive-metacognitive |

Also `Design_Patterns_Reference.md` + `images/`, `Reference_link_Workflow_Patterns.md`.

# Phase 6 — Agent SDKs (First-Party) (`06_Agent_SDKs_First_Party/`) — 🚧 Planned

`Google_ADK/`, `OpenAI_Agents_SDK/`, `Google_AI_SDK/`

# Phase 7 — Advanced Agentic Systems (`07_Advanced_Agentic_Systems/`)

## `Memory_and_State/LangGraph/`

| Section | Notebook | Topic |
|---|---|---|
| `01_Memory/` | `01_Memory_and_Conversational_Agent.ipynb`, `02_Memory_Optimizations.ipynb` | Memory & threads |
| `01_Memory/memory/` | `02_Agent_Memory_Types_SQLite.ipynb` | Agent memory types with SQLite persistence (self-contained sub-module) |
| `02_Long_Term_Memory/` | `01_Long_Term_Memory.ipynb` | Persistent long-term memory (PostgreSQL) |

## `Memory_and_State/LangChain/Memory/`

9 notebooks — chat message memory, conversation chains, multi-user in-memory & SQL persistent storage, ConversationQA.

## `Multi_Agent_Orchestration/`

| Section | Notebook | Topic |
|---|---|---|
| `01_Agent_Patterns/` | `01_Agent_Patterns.ipynb`, `02_Supervisor_Multi_Agent_Alt.ipynb`, `03_Multi_Agent_Overview_Alt.ipynb` | Supervisor pattern + alternates |
| `02_Multi_Agent_Swarm/` | `01_Multi_Agent_Swarm.ipynb` | Peer-to-peer/swarm multi-agent architecture |

## `Deep_Agents_and_Harness_Engineering/`

Not notebooks — Python scripts + a `deepagents`-based multi-agent system:

| Path | Content |
|---|---|
| `examples/simple_coding_agent.py` | Default agent run — `FilesystemBackend`, no code execution |
| `examples/long_term_memory_agent.py` | Adds cross-thread persistent memory (JSON, upgradeable to PostgreSQL) |
| `skills/senior-developer/`, `code-reviewer/`, `research-agent/`, `memory-manager/` | Core orchestration agents |
| `skills/aia-customer-analytics/`, `aia-distribution-channels/`, `aia-policy-underwriting/`, `aia-claims-analytics/` | Databricks Genie analytics agents |
| `app/` | Standalone deployable version (FastAPI + frontend, Docker) |
| `docs/` | Architecture diagram, memory-types writeup |

## `Evaluation_and_Eval_Harnesses/` — 🚧 Planned

`Agent_Evaluation/`, `RAG_Evaluation/`, `LLM_as_Judge/`

# Phase 8 — Advanced RAG (`08_Advanced_RAG/`)

Depends on Phases 5 & 7 — sequenced after both.

## `RAG_with_LangGraph_Advanced/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_Advanced_RAG_Agent.ipynb` | Advanced retrieval — grading, rewriting |
| 2 | `02_RAG_as_Tool_in_Agents.ipynb` | RAG as a composable tool inside a larger agent (agentic RAG) |

## `CacheRAG/`, `GraphRAG/` — 🚧 Planned

# Phase 9 — Agent Protocols (`09_Agent_Protocols/`) — 🚧 Planned

`MCP/` (4 subfolders), `ACP/` (3 subfolders), `A2A/` (3 subfolders)

# Phase 10 — Alternative Agent Frameworks (`10_Alternative_Agent_Frameworks/`) — 🚧 Planned

`DSPy/`, `CrewAI/` (4 subfolders), `PydanticAI/`, `AutoGen/` (4 subfolders), `Orchestration_Frameworks_Overview/`

# Phase 11 — Claude Code & AI Coding Tools (`11_Claude_Code_and_AI_Coding_Tools/`) — 🚧 Planned

`Claude_Code/`, `Agent_Skills/`, `Claude_API_and_Agent_SDK/`, `AI_Coding_Tool_Landscape/`

# Phase 12 — Production & Observability (`12_Production_and_Observability/`)

## `LLMOps_and_AI_Infrastructure/`

| Section | Notebook | Topic |
|---|---|---|
| `Tracing_and_Observability/LangSmith/` | `01_LangSmith_Basics.ipynb` | LangSmith basics |
| `Tracing_and_Observability/LangFuse/` | — | 🚧 Planned |
| `Tracing_and_Observability/` | `02_Callbacks.ipynb` | LangChain callback mechanism |
| `Caching_and_Performance/` | `01_Caching.ipynb`, `02_Streaming.ipynb` | Caching, streaming |
| `Cost_Monitoring/` | `01_LLM_Cost_Monitoring.ipynb` | Tracking LLM API costs |

Also `00_Advanced_LangChain_Overview.ipynb`.

## `Safety_and_Alignment/`

| # | Notebook | Topic |
|---|---|---|
| 1 | `01_Moderating_Chains.ipynb` | Content moderation in LangChain pipelines |

## `DevOps_and_Deployment/`, `Security_and_Compliance/` — 🚧 Planned

# Phase 13 — Projects (`13_Projects/`)

## `LangGraph_Fullstack_Capstone/`

Not notebooks — deployable apps and tests: `fullstackapp/` (FastAPI + Angular + Postgres), `unit_tests/` (pytest), `streamlit_apps/` (doc-entity-extractor, knowledge-graphs-with-langextract).

## `LangChain_Microservices_Capstone/`

Not notebooks — LangChain deployed as microservices: Docker, k8s-style manifests, frontend, `service2/`, `service3/`.

# Planned Phases (no content yet)

| Phase | Folder |
|---|---|
| 1 | `01_Theory_and_Foundations/` *(optional)* |
| 6 | `06_Agent_SDKs_First_Party/` |
| 9 | `09_Agent_Protocols/` |
| 10 | `10_Alternative_Agent_Frameworks/` |
| 11 | `11_Claude_Code_and_AI_Coding_Tools/` |

## Archive (`archive/`)

Retired notebooks, kept for reference but not part of the learning path: `04_Reference_Course/` (9 notebooks) and `Ultimate_RAG_Bootcamp/` (6 notebooks + PDFs).

---

## Known Discrepancies

**Fixed (abbreviated — full detail in prior entries below):**
- Chapter/notebook count and naming fixes across the original LangGraph course.
- `deepagents` content vendored in from `Deep_Agent_Demystified`.
- `Agentic_Design_Pattern_Demystified-main` merged in — filled the Reflection gap, added Router/Prompt-Chaining/Evaluator-Optimizer/Orchestrator-Worker/Multi-Agent-Swarm/Advanced-Cognitive-Patterns, five new application builds, and several `_Alt` notebooks.
- **2026-08-16 — three successive top-level restructurings**, converging on the current 13-phase model:
  1. LangGraph's 7 chapters, originally loose at the repo root, were nested under one `01_LangGraph/` parent (framework-per-folder pattern).
  2. Replaced entirely: rebuilt around **learning phase** instead of framework, after comparing against a reference tracker (`aie-learning-tracker.vercel.app`) — `01_Theory_and_Foundations/` … `12_Projects/`, LangGraph's content split across several phase tracks.
  3. **Final restructuring (this one):** `LangChain_Demystified-main/` and `Prompt-Engineering-Demystified-main/` were merged in, which exposed real duplication in restructuring #2 (RAG, agents, memory, and observability each had 2–3 different homes across phases). Rebuilt around a stricter rule — **each topic owns exactly one phase**, framework implementations sit as sibling tracks inside it — and split into 13 phases: Theory & Foundations (1), LangChain Fundamentals & Prompting (2, trimmed to true fundamentals), LangGraph Fundamentals (3, mechanics only), Retrieval & RAG (4, foundational only), AI Agent Fundamentals (5, both frameworks' agent-building consolidated), Agent SDKs First-Party (6, promoted to its own phase), Advanced Agentic Systems (7), Advanced RAG (8, new — agentic/self-correcting RAG + CacheRAG/GraphRAG, deliberately sequenced *after* Phases 5 & 7 since it depends on knowing agents), Agent Protocols (9), Alternative Agent Frameworks (10), Claude Code & AI Coding Tools (11), Production & Observability (12, absorbed LangChain's LangSmith/advanced-features/moderation content), Projects (13, absorbed LangChain's microservices module as a second capstone). `LangChain_Demystified`'s `_Archive/` and root scaffolding were discarded per established precedent; its two `.claude/skills/` were preserved at `.claude/skills-candidates/` for separate review. Updated everywhere a path was hardcoded: `pyproject.toml` (ruff excludes — now 3 JS frontends), `README.md`, this file, `CLAUDE.md`, `docs/*.html`, and the `ai-roadmap-organizer` skill's `roadmap-map.md`/`SKILL.md`. The same Windows directory-lock issue hit `Deep_Agents_and_Harness_Engineering` and its `app/` subfolder twice more during this pass — same drain-contents-then-remove-shell workaround each time, no data lost (verified via notebook counts before/after: 132 total).

**Still open:**
- Several notebooks don't open with a proper `# Title` markdown cell (mid-document subheading instead) — pre-existing, not fixed, would require editing notebook content.
- `LangChain_Fundamentals/` and its descendants don't use the `helpers` factory (they instantiate LLM clients directly) — a pre-existing property of the merged-in source repo, not a convention violation.
