# 03 — Advanced

**Prerequisites: `02_Core/`, specifically agents.** Everything here assumes you can already build a single agent and a working RAG pipeline. That prerequisite — not difficulty — is what puts a phase in this group.

**6 phases · 172 notebooks**

## Topics covered

### `06_Agent_SDKs_First_Party/` — 3 notebooks 🚧 mostly planned
- Google ADK
- Google AI SDK
- OpenAI Agents SDK

### `07_Advanced_Agentic_Systems/` — 37 notebooks

**`Memory_and_State/`**
- Short-term, session, semantic, episodic and procedural memory
- Threads and checkpointers
- Long-term PostgreSQL memory
- Multi-user SQL persistence
- Both LangGraph and LangChain, consolidated here rather than left in their fundamentals phases

**`Multi_Agent_Orchestration/`**
- Supervisor pattern
- Swarm architecture

**`Deep_Agents_and_Harness_Engineering/`**
- The `deepagents` framework
- Its own app, examples and skills

### `08_Advanced_RAG/` — 61 notebooks
RAG that needs agents.

**`RAG_with_LangGraph_Advanced/`**
- Self-correcting retrieval
- Corrective RAG
- Adaptive RAG
- Healthcare router agentic RAG

**`Comprehensive_RAG_Techniques/`**
- The NirDiamant anthology, ~35 notebooks, kept whole

**`GraphRAG/`**
- Knowledge graphs plus RAG, full course

**`RAG_Ecosystem/`**
- RAPTOR
- ColBERT
- CRAG

**Other**
- `building-adaptive-rag/` — standalone app
- 🚧 `CacheRAG/` — planned

### `09_Agent_Protocols/` — 10 notebooks

**`MCP/`**
- Foundations
- Building servers
- Building clients
- Applications
- An MCP + A2A agentic RAG app

**`ACP/`** · **`A2A/`**
- 🚧 Planned

### `10_Alternative_Agent_Frameworks/` — 47 notebooks

**`CrewAI/`**
- Foundations
- Flows
- Multi-agent patterns
- 9 project sets

**`AutoGen/`**
- Conversable, sequential, tools, code and multimodal labs
- Group and swarm patterns
- 8 project sets

**`DSPy/`**
- Context engineering, levels 1–5

**`PydanticAI/`** · **`Orchestration_Frameworks_Overview/`**
- 🚧 Planned

### `12_Production_and_Observability/` — 14 notebooks
- LangSmith tracing
- Callbacks
- Caching and performance
- Cost monitoring
- Content moderation
- Red teaming with `deepteam`
- 🚧 DevOps/deployment and security/compliance — planned

## Why there's no `11_`

Phase 11 (AI Coding Tools) is its own top-level group — it's tooling you use, not a topic in the learning arc. Phase numbers were never renumbered when the stage folders were introduced, so the gap is expected.

## Dependency warning

**CrewAI cannot share an environment with the rest of the repo.** It hard-pins `chromadb<1.2`, which conflicts with `langchain-chroma` 1.1. Install it in its own venv from its per-folder `requirements.txt`.

## What is deliberately *not* here

**Evaluation.** It lives in the sibling repo `Agent_Evaluation_Demystified`.
