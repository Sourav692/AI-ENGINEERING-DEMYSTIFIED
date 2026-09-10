# Agentic RAG Architectures Covered in This Repo

A map of every agentic-RAG architecture built in this roadmap, grouped by **architecture** rather than by folder. Five architectures are covered end-to-end — **CRAG, Adaptive RAG, Self-RAG, domain-router RAG, and retrieval-as-tool** — each with a LangGraph implementation in Phase 8 plus an independent anthology implementation alongside it.

All links are repo-relative — click through from this file. Last surveyed: 2026-09-10.

---

## 1. Core architectures — [`08_Advanced_RAG/RAG_with_LangGraph_Advanced/`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/)

The canonical home. Five notebooks, each a distinct control-flow architecture. Graph shapes below are the actual `add_node` / `add_conditional_edges` structures in the notebooks.

| Architecture | Notebook | Graph shape |
|---|---|---|
| **Agentic RAG with query rewriting + guardrails** | [`01_Advanced_RAG_Agent.ipynb`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/01_Advanced_RAG_Agent.ipynb) | `validate_topic → optimize_query → fetch_content → assess_relevance → enhance_query ⟲ → generate_response`, with `handle_off_topic` / `handle_no_results` terminal branches |
| **Retrieval-as-a-tool (ReAct-style)** | [`02_RAG_as_Tool_in_Agents.ipynb`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/02_RAG_as_Tool_in_Agents.ipynb) | `topic_decision → agent ⇄ tools/retrieve → generate_answer`; the retriever is a tool the LLM *chooses* to call, not a fixed pipeline step |
| **Domain-router agentic RAG** | [`1. Build_a_Healthcare_Customer_Support_Router_Agentic_RAG_System.ipynb`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/1.%20Build_a_Healthcare_Customer_Support_Router_Agentic_RAG_System.ipynb) | `categorize_inquiry` + `analyze_inquiry_sentiment` → `generate_department_response`, with `escalate_to_human_agent` / `escalate_to_oncall_team` human-in-the-loop branches (data: [`healthcare_db.json`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/healthcare_db.json)) |
| **Corrective RAG (CRAG)** | [`2. Build_an_Agentic_Corrective_RAG_System_with_LangGraph.ipynb`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/2.%20Build_an_Agentic_Corrective_RAG_System_with_LangGraph.ipynb) | `retrieve → grade_documents → (rewrite_query ⟲ \| web_search) → generate_answer` — web search as the fallback corpus when retrieval grades poorly |
| **Adaptive RAG** | [`3. Build_an_Adaptive_RAG_System.ipynb`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/3.%20Build_an_Adaptive_RAG_System.ipynb) | Routes the query to `retrieve_vectordb` **or** `web_search` up front, then `grade_documents → generate_answer → grade_hallucinations`, with separate `rewrite_query_vectordb` / `rewrite_query_web_search` retry loops per source |
| **Self-RAG** | [`4. Build_a_Self_RAG_System.ipynb`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/4.%20Build_a_Self_RAG_System.ipynb) | `decide_retrieval → retrieve → grade_relevance → generate → grade_groundedness → grade_utility`, plus a `rephrase_and_retry` loop — the full reflection-token triad (retrieve? / grounded? / useful?) |

Supporting material: [`research_papers/`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/research_papers/) (attention, chain-of-thought, diffusion, DINO, PEFT PDFs) used as the corpus. Track README: [`README.md`](08_Advanced_RAG/RAG_with_LangGraph_Advanced/README.md).

---

## 2. Entry-level agentic RAG — [`04_Retrieval_and_RAG/08_RAG_with_LangGraph/`](04_Retrieval_and_RAG/08_RAG_with_LangGraph/)

| Notebook | Content |
|---|---|
| [`01_Simple_Agentic_RAG.ipynb`](04_Retrieval_and_RAG/08_RAG_with_LangGraph/01_Simple_Agentic_RAG.ipynb) | Minimal version — PDF → Chroma → agent loop |
| [`02_Simple_Agentic_RAG_Databricks.ipynb`](04_Retrieval_and_RAG/08_RAG_with_LangGraph/02_Simple_Agentic_RAG_Databricks.ipynb) | Same agent on Databricks Vector Search |

---

## 3. Router mechanics — [`03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/`](03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/)

| Notebook | Content |
|---|---|
| [`01_Router_Agentic_RAG_System.ipynb`](03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/01_Router_Agentic_RAG_System.ipynb) | Customer-support router agentic RAG |
| [`02_Router_Agentic_RAG_System_Modular.ipynb`](03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/02_Router_Agentic_RAG_System_Modular.ipynb) | Same system, refactored into modules |

These are agentic-RAG examples kept in Phase 3 because they are that phase's only routing-mechanics demo — see [`NOTEBOOK_INDEX.md`](NOTEBOOK_INDEX.md)'s Known Discrepancies.

---

## 4. Anthology variants — [`08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/)

Independent implementations of the same architectures, useful as second opinions:

| Notebook | Note |
|---|---|
| [`Agentic_RAG.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/Agentic_RAG.ipynb) | Managed-SDK flavour — parsing, reranking, grounded generation |
| [`crag.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/crag.ipynb) | Corrective RAG |
| [`self_rag.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/self_rag.ipynb) | Self-RAG |
| [`adaptive_retrieval.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/adaptive_retrieval.ipynb) | Query-**type** strategy routing (factual / analytical / opinion) — distinct from CRAG's document-grading loop |
| [`retrieval_with_feedback_loop.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/retrieval_with_feedback_loop.ipynb) | Feedback-driven retrieval |
| [`raptor.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/raptor.ipynb) | Recursive hierarchical summarization index |
| [`graph_rag.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/graph_rag.ipynb) · [`graph_rag_local_attribution.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/graph_rag_local_attribution.ipynb) · [`Microsoft_GraphRag.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/Microsoft_GraphRag.ipynb) · [`graphrag_with_milvus_vectordb.ipynb`](08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/graphrag_with_milvus_vectordb.ipynb) | GraphRAG family |

---

## 5. Deployed / application forms

| Location | Content |
|---|---|
| [`08_Advanced_RAG/building-adaptive-rag/`](08_Advanced_RAG/building-adaptive-rag/) | Adaptive RAG as a real Python app, not a notebook: [`src/workflow/graph.py`](08_Advanced_RAG/building-adaptive-rag/src/workflow/graph.py) + [`nodes/`](08_Advanced_RAG/building-adaptive-rag/src/workflow/nodes/) (`retrieve`, `grade_documents`, `generate`, `web_search`) + [`chains/`](08_Advanced_RAG/building-adaptive-rag/src/workflow/chains/) (`router`, `retrieval_grader`, `hallucination_grader`, `answer_grader`). The cleanest reference for how the grader chains factor out of the graph. |
| [`09_Agent_Protocols/MCP/mcp_a2a_agentic_rag/`](09_Agent_Protocols/MCP/mcp_a2a_agentic_rag/) | Agentic RAG where retrieval tools are served over **MCP** and agents coordinate over **A2A** — [`agents/`](09_Agent_Protocols/MCP/mcp_a2a_agentic_rag/agents/), [`mcp/`](09_Agent_Protocols/MCP/mcp_a2a_agentic_rag/mcp/), [`mcp_config.json`](09_Agent_Protocols/MCP/mcp_a2a_agentic_rag/mcp_config.json) |
| [`13_Projects/ShopUNow_Agentic_RAG_Capstone/`](13_Projects/ShopUNow_Agentic_RAG_Capstone/) | Two-stage capstone: [`01_create_vector_databases.ipynb`](13_Projects/ShopUNow_Agentic_RAG_Capstone/01_create_vector_databases.ipynb) → [`02_agentic_rag_system.ipynb`](13_Projects/ShopUNow_Agentic_RAG_Capstone/02_agentic_rag_system.ipynb) over 7 department JSON datasets |

---

## Gaps

- **CacheRAG** — [`08_Advanced_RAG/CacheRAG/`](08_Advanced_RAG/CacheRAG/) exists as a scaffolded placeholder with no content.
