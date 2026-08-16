# Comprehensive RAG Techniques — Roadmap Note

**Status:** ✅ Built.

This is the well-known NirDiamant `RAG_Techniques` collection, merged in whole (not split notebook-by-notebook) because its dozens of notebooks share `helper_functions.py`, `data/`, and `images/` via relative paths — splitting would break those imports. It ranges from basic (`simple_rag.ipynb`) to advanced (CRAG, Self-RAG, RAPTOR, GraphRAG, adaptive retrieval, fusion retrieval) — placed in Phase 8 since its own identity/fame is as an advanced-techniques anthology, even though some individual notebooks are basic.

| Path | Content |
|---|---|
| `all_rag_techniques/` | ~35 technique notebooks (LangChain + several LlamaIndex variants) |
| `all_rag_techniques_runnable_scripts/` | Standalone `.py` scripts mirroring several of the notebooks |
| `evaluation/` | Evaluation metrics/harnesses for this collection specifically (see also `07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/RAG_Evaluation/` for the main RAG eval track) |
| `data/`, `images/` | Shared assets used across the notebooks |
| `tests/` | Import tests |

See the collection's own `README.md` (source repo's original) for the full technique-by-technique index.
