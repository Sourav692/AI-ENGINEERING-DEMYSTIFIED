<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 04 — Retrieval & RAG

**Owns:** foundational RAG — everything that does **not** require agent knowledge. Stage `02_Core/`.

| Track | Content |
|---|---|
| `01_Introduction_to_RAG/` | Overview, indexing, LangChain+RAG |
| `02_Embeddings_and_Vector_Databases/` | Embedding models, vector DB options, retrievers |
| `03_Indexing_Techniques/` | Multi-representation indexing, parent-document retrieval — split out because these change the *index*, not the query |
| `04_Query_Transformation_Techniques/` | Multi-query, RAG-Fusion, decomposition, step-back, HyDE, routing, self-querying |
| `05_Post_Retrieval_Techniques/` | Cross-encoder reranking — re-scores already-retrieved results |
| `06_RAG_Naive_to_Production/` | Loading → chunking → hybrid search → query enhancement → parent-doc → postprocessing → full pipelines |
| `07_Multimodal_and_Document_Intelligence/` | Multimodal RAG |
| `08_RAG_with_LangGraph/` · `09_RAG_with_LangChain/` · `10_RAG_with_LlamaIndex/` | Framework implementations — sibling tracks inside this phase, never separate phases |
| `RAG_Production_Course/` | Merged-in production course |
| `RAG_Curriculum/` | Concept-first lesson route (9 of 70 lessons built) — one teaching notebook per concept, with its plan, migration manifest and `_support/` tooling. Ported 2026-09-28 from the `RAG_Curriculum` branch |

## Conventions here

- `helpers` factory used in 10 files. Prefer it for new LangGraph-flavoured notebooks; the `RAG_Demystified`-sourced ones instantiate clients directly and that is left as-is.
- 76 notebooks — the second-largest phase.
- **`RAG_Curriculum/` lessons resolve assets with `_support/helpers/rag_paths.py`**, by filename across `ASSET_ROOTS`, never by `../../` path. A new asset goes in `shared_data/`. The module is deliberately not named `utils`/`helpers` — both names already collide in this phase.

## Known gaps

- **`shared_data/` is the one data folder here — use that name.** Fixed 2026-09-19: five `06_RAG_Naive_to_Production/` notebooks still pointed at `../../data/`, a name that stopped existing when the folder was brought over as `shared_data/`. They now use `../../shared_data/`, matching `03_Indexing_Techniques/` and `04_Query_Transformation_Techniques/`, which had already been migrated. All data references in this phase resolve; `scripts/check_repo_invariants.py` asserts it on every commit. Don't reintroduce a bare `data/`.

## Don't

- **Don't build the curriculum plan's `06_Evaluation/`, `07_Agentic_RAG/` or `08_Advanced_Architectures/` here.** `RAG_CURRICULUM.md` was written when the curriculum was a top-level folder; as a Phase 4 track it owns foundational RAG only. Evaluation → `Agent_Evaluation_Demystified`; anything needing agents → `03_Advanced/08_Advanced_RAG/`.
- **Don't retire a source notebook just because a curriculum lesson looks like it covers it.** Retire only once `RAG_Curriculum/RAG_MIGRATION_MANIFEST.md` records the disposition and the lesson has been validated, then `git mv` it to `archive/04_Retrieval_and_RAG/…` with a `RETIRED_MANIFEST.md` row and repoint every inbound reference in the same commit.
- **Don't merge this phase with `03_Advanced/08_Advanced_RAG/`.** The split is deliberate: Phase 8 depends on agents (Phase 5) and advanced agentic systems (Phase 7), so it is sequenced after both. This decision survived three restructurings — don't relitigate it.
