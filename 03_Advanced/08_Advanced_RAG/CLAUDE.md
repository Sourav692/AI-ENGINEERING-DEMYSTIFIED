<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 08 — Advanced RAG

**Owns:** RAG that **requires agent knowledge** — agentic, self-correcting, graph-based. Stage `03_Advanced/`. Depends on Phases 5 and 7.

| Track | Content |
|---|---|
| `RAG_with_LangGraph_Advanced/` | Self-correcting retrieval, corrective/adaptive RAG, healthcare router agentic RAG |
| `Comprehensive_RAG_Techniques/` | The NirDiamant `RAG_Techniques` anthology (~35 notebooks) |
| `RAG_Ecosystem/` | Single-notebook RAG stack (basic → query transforms → RAPTOR/ColBERT → CRAG → RAGAS pointers) |
| `GraphRAG/` | Full knowledge-graph + RAG course |
| `CacheRAG/` | Planned |
| `building-adaptive-rag/` | Standalone app, kept RAG-first here rather than moved to Projects |

## Don't

- **Don't split `Comprehensive_RAG_Techniques/`.** Its ~35 notebooks share `helper_functions.py`, `data/` and `images/` through relative paths; splitting breaks all of them. Kept whole deliberately.
- **Don't merge this phase into `02_Core/04_Retrieval_and_RAG/`.** The prerequisite split (foundational vs agent-dependent) is the reason this phase exists and is the reference example for the whole stage scheme.
- Don't move the standalone apps to `05_Projects/` — keeping them RAG-first here was an explicit decision.
