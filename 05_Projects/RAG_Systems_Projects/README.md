# RAG Systems Projects

**Status:** ✅ Built.

Applied RAG capstone notebooks, merged from `RAG_Demystified`.

| Notebook | Topic |
|---|---|
| `1. Build_Document_Retriever_Search_Engine.ipynb` | Document retriever search engine |
| `2. Multi-user Conversational RAG System.ipynb` | Multi-user conversational RAG |
| `M8_Multimodal_RAG_System_with_GPT_4o.ipynb` | Multimodal RAG with GPT-4o |
| `M8_Simple_RAG,_Conversational_RAG_and_Multi_User_Conversational_RAG_Systems.ipynb` | Combined simple/conversational/multi-user RAG |
| `RAG system for Question Answering.ipynb` | RAG for Q&A (alternate) |

Also `data/` and `final_project/` (a built Chroma DB from the source repo).

Two numbered stubs were retired on 2026-09-19: `3. Multimodal RAG System.ipynb` (one empty cell) and `4. Develop a RAG system for Question Answering.ipynb` (0 bytes, not valid JSON). Both arrived empty from the source repo and were never non-empty in this repo's history; the real versions are `M8_Multimodal_RAG_System_with_GPT_4o.ipynb` and `RAG system for Question Answering.ipynb` above. This is why the numbering now reads 1, 2, then unnumbered. The multimodal stub went to `archive/`; the 0-byte one had to be deleted outright, because `nbstripout` (run by `pre-commit` repo-wide, `archive/` included) rejects anything that is not a valid notebook. It remains recoverable from git history.
