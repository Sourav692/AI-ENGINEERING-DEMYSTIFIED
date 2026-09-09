# Comprehensive RAG Techniques — Roadmap Note

**Status:** ✅ Built.

This is the well-known NirDiamant `RAG_Techniques` collection, merged in whole (not split notebook-by-notebook) because its dozens of notebooks share `helper_functions.py`, `data/`, and `images/` via relative paths — splitting would break those imports. It ranges from basic (`1. simple_rag.ipynb`) to advanced (CRAG, Self-RAG, RAPTOR, GraphRAG, adaptive retrieval, fusion retrieval, LightRAG, MemoRAG) — placed in Phase 8 since its own identity/fame is as an advanced-techniques anthology, even though some individual notebooks are basic.

| Path | Content |
|---|---|
| `all_rag_techniques/` | 42 technique notebooks (LangChain + several LlamaIndex variants) |
| `all_rag_techniques_runnable_scripts/` | Standalone `.py` scripts mirroring several of the notebooks |
| `evaluation/` | Evaluation metrics/harnesses for this collection specifically (see also `07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/RAG_Evaluation/` for the main RAG eval track) |
| `data/`, `images/` | Shared assets used across the notebooks |
| `tests/` | Import tests |

See the collection's own `README.md` (source repo's original) for the full technique-by-technique index.

## Upstream sync — 2026-09-09

A second, fresh clone of the upstream repo had been dropped in at
`all_rag_techniques/RAG_TECHNIQUES/` (nested `.git` and all), duplicating this folder.
It was merged into this one and deleted. What that brought in:

- **7 new notebooks:** `Agentic_RAG`, `graph_rag_local_attribution`, `json_rag`,
  `light_rag`, `local_rag_huggingface_faiss`, `memorag`, `multi_faceted_filtering`.
- **New assets:** 2 runnable scripts, 3 data files, 2 evaluation notebooks
  (`end-2-end_rag_evaluation`, `open-rag-eval-example`), 12 images, `LICENSE`,
  `CONTRIBUTING.md`, and the upstream `README.md` (57 KB → 81 KB).
- **`helper_functions.py` + `evaluation/evalute_rag.py` modernized:**
  `langchain.document_loaders` → `langchain_community.document_loaders`,
  `langchain.text_splitter` → `langchain_text_splitters`,
  `langchain.vectorstores` → `langchain_community.vectorstores`,
  `langchain_core.pydantic_v1` → `pydantic`, `langchain.PromptTemplate` →
  `langchain_core.prompts.PromptTemplate`, and `.get_relevant_documents()` → `.invoke()`.
- 26 unmodified shared notebooks refreshed to upstream.

**Local edits deliberately kept** (these are *not* upstream and must survive future syncs):

| File | Why it differs |
|---|---|
| `1. simple_rag.ipynb` | Colab `!git clone` bootstrap commented out; `sys.path.append("..")` added; local `.env` instead of `google.colab.userdata` |
| `2. simple_csv_rag.ipynb` | Colab download cells commented out; `../data/` paths; extra docstore-inspection cells |
| `3. reliable_rag.ipynb` | Cohere embeddings → `OpenAIEmbeddings`; deprecated `mixtral-8x7b-32768` → `llama-3.1-8b-instant` |
| `5. proposition_chunking.ipynb` | Groq/`pydantic_v1` variant cells commented out |
| `7. HyDe_Hypothetical_Document_Embedding.ipynb` | Colab bootstrap commented out; `../data/` paths |
| `semantic_chunking.ipynb` | Colab bootstrap commented out; `../data/` path |
| `4. choose_chunk_size.ipynb`, `6. query_transformations.ipynb` | Renamed only — content matches upstream |
| `7_BetterQueries.ipynb` | **Not from this repo** — multi-query notebook from a Udemy "Advanced LangChain Techniques" course |

The numeric `N. ` filename prefixes are a local reading-order convention; upstream uses the
bare names. When syncing upstream again, map `simple_rag.ipynb` → `1. simple_rag.ipynb`, etc.,
and diff rather than overwrite.
