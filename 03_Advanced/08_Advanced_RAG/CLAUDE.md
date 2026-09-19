<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 08 — Advanced RAG

**Owns:** RAG that **requires agent knowledge** — agentic, self-correcting, graph-based. Stage `03_Advanced/`. Depends on Phases 5 and 7.

| Track | Content |
|---|---|
| `Agentic_RAG/` | Self-correcting retrieval, corrective/adaptive RAG, healthcare router agentic RAG |
| `Comprehensive_RAG_Techniques/` | The NirDiamant `RAG_Techniques` anthology (~35 notebooks) |
| `RAG_Ecosystem/` | Single-notebook RAG stack (basic → query transforms → RAPTOR/ColBERT → CRAG → RAGAS pointers) |
| `GraphRAG/` | Full knowledge-graph + RAG course |
| `CacheRAG/` | Planned |

## Don't

- **Don't split `Comprehensive_RAG_Techniques/`.** Its ~35 notebooks share `helper_functions.py`, `data/` and `images/` through relative paths; splitting breaks all of them. Kept whole deliberately.
- **Don't merge this phase into `02_Core/04_Retrieval_and_RAG/`.** The prerequisite split (foundational vs agent-dependent) is the reason this phase exists and is the reference example for the whole stage scheme.
- **This phase is notebooks only — don't add deployable apps here.** Reversed 2026-09-19: the old rule kept standalone apps here "RAG-first". `building-adaptive-rag/` moved to `05_Projects/Building_Adaptive_RAG/` because it is an application (25 `.py` files, `src/`, `tests/`, `main.py`, `requirements.txt`, zero notebooks) — the same code-tree-plus-manifest test that moved the three Enterprise platforms into Projects that day. The old rationale ("Projects is for general framework capstones") no longer held once `ShopUNow_Agentic_RAG_Capstone/` and `RAG_Systems_Projects/` were already sitting there.
- `mcp_a2a_agentic_rag/` is **not** in this phase and never needs re-adding — it lives in `03_Advanced/09_Agent_Protocols/MCP/04_Applications/`, protocol-first. Several docs claimed a Phase 8 copy existed; that was stale and was corrected 2026-09-19.
