# Chapter 3: RAG — How Do I Build Retrieval Systems?

> Build retrieval-augmented generation pipelines — from basic to advanced.

## What You'll Learn

- Build a **basic RAG agent** that answers questions from PDFs
- Deploy RAG on **Databricks Vector Search** for enterprise scale
- Implement **advanced retrieval** patterns (grading, rewriting, routing)
- Use **RAG as a composable tool** inside larger agent systems

## Prerequisites

- [Chapter 1: Foundations](../01_Foundations/) completed
- [Chapter 2: Core Capabilities](../02_Core_Capabilities/) recommended
- API keys: OpenAI (required), Databricks (for notebook 2)

## Notebooks

| # | Notebook | What You'll Build | Key Concepts |
|---|---|---|---|
| 1 | [Simple RAG Agent (OpenAI)](01_Simple_RAG_Agent_OpenAI.ipynb) | PDF question-answering agent | PDF loading, Chroma, retrieval grading, query rewriting |
| 2 | [Simple RAG Agent (Databricks)](02_Simple_RAG_Agent_Databricks.ipynb) | Enterprise RAG agent | Databricks Vector Search |
| 3 | [Advanced RAG Agent](03_Advanced_RAG_Agent.ipynb) | Production RAG pipeline | Advanced retrieval patterns, routing |
| 4 | [RAG as Tool in Agents](04_RAG_as_Tool_in_Agents.ipynb) | RAG as a composable tool | RAG-as-tool pattern, agent composition |

## Progression

```
Notebook 1: Build a RAG agent from scratch (PDF → Chroma → LLM)
Notebook 2: Deploy the same agent on Databricks (enterprise)
Notebook 3: Add advanced retrieval (grading, rewriting, fallbacks)
Notebook 4: Use the RAG pipeline as a tool inside a larger agent
```

## What's Next?

Move to **[Chapter 4: Agents](../04_Agents/)** to build complete, real-world agents.
