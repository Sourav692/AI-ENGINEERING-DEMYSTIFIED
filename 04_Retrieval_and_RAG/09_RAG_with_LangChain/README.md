# RAG with LangChain

**Status:** ✅ Built. Partially migrated to `RAG_Curriculum/` (2026-09-10).

> **`7.0_RAG_Essentials.ipynb` and `7.1_RAG_Comprehensive.ipynb` have been retired.**
> Their content is consolidated into
> [`../../RAG_Curriculum/01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb`](../../RAG_Curriculum/01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb),
> which is now the single active lesson for the RAG lifecycle. The originals are preserved in
> `RAG_Curriculum/_archive/` — note that both used LangChain 0.x imports that no longer resolve
> on this repo's LangChain 1.4.

| Notebook | Topic |
|---|---|
| `7.2_Filtered_Search.ipynb` | Metadata-filtered retrieval |
| `7.3_Indexing_API.ipynb` | LangChain indexing API — incremental indexing and record management |

## Retained assets

`bella_vista.txt` (corpus), `index/` and `vs_db/` (pre-built FAISS stores), `postgres/`,
`api.py`, `docker-compose.yaml` — all still in use. `bella_vista.txt` is the corpus for the
canonical lesson above, which reaches it through `rag_paths.asset()` rather than a relative
path, so it must stay here.
