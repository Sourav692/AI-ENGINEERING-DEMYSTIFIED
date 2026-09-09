# RAG: Naive → Production

**Status:** ✅ Built.

Merged from `RAG_Demystified`'s "Building Retrieval Systems" concept sections — the full maturity curve from loading raw data to a complete production-shaped pipeline.

| # | Section | Topic |
|---|---|---|
| 1 | `01_Loading_Data/` | Document loaders — text, markdown, CSV, JSON, PDF, Word, directory, YouTube transcript, URL, custom |
| 2 | `02_Splitting_and_Chunking/` | Document splitters/chunkers, semantic chunking |
| 3 | `03_Hybrid_Search_Strategies/` | Dense+sparse hybrid search, reranking, MMR |
| 4 | `04_Query_Enhancement/` | Query expansion, decomposition, HyDE, multi-query retrieval |
| 5 | `05_Parent_Document_Retriever/` | Two-stage (parent-document) retrieval |
| 6 | `06_Postprocessing_Documents/` | Cross-encoder reranking |
| 7 | `07_Building_RAG_Systems/` | Simple RAG, contextual retrieval, RAG with sources, RAG with citations |

Some notebooks reference a shared `data/` folder via relative paths from the source repo — see `04_Retrieval_and_RAG/shared_data/` (brought along, but exact relative-path depth wasn't re-verified after the move; fix paths if a notebook can't find its data file).
