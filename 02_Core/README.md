# 02 — Core

**Prerequisites: `01_Foundations/`.** The framework mechanics plus the two capabilities — retrieval and agents — that everything in `03_Advanced/` composes.

**4 phases · 239 notebooks** — the bulk of the repo.

## Topics covered

### `01_LangChain_Fundamentals/` — 48 notebooks
- Getting started
- Inputs, outputs and prompts
- Legacy chains
- LCEL
- Summarization
- Workflow patterns
- LangChain 1.x agents and middleware
- Production-course foundations

### `03_LangGraph_Fundamentals/` — 25 notebooks

**`01_Foundations/`**
- State
- Graphs
- Conditional routing
- Tools
- ReAct
- Pydantic state
- Node and `Command` patterns

**`02_Core_Capabilities/`**
- Routing
- Human-in-the-loop
- Advanced state
- Subgraphs
- Async and streaming
- Retries

### `04_Retrieval_and_RAG/` — 74 notebooks
Foundational RAG — everything that does *not* need agents, ordered by pipeline stage.

**`01_Introduction_to_RAG/`** — concepts
- RAG overview
- Indexing
- LangChain + RAG

**`02_Embeddings_and_Vector_Databases/`**
- Embedding models
- Vector database options
- Retrievers

**`03_Indexing_Techniques/`**
- Multi-representation indexing
- Parent-document retrieval

**`04_Query_Transformation_Techniques/`**
- Multi-query
- RAG-Fusion
- Decomposition
- Step-back prompting
- HyDE
- Query routing
- Self-querying retrieval

**`05_Post_Retrieval_Techniques/`**
- Cross-encoder reranking

**`06_RAG_Naive_to_Production/`**
- Loading
- Chunking
- Hybrid search
- Query enhancement
- Parent-document retrieval
- Postprocessing
- Full pipelines

**`07_Multimodal_and_Document_Intelligence/`**
- Multimodal RAG

**Framework variants** — sibling tracks, never separate phases
- `08_RAG_with_LangGraph/`
- `09_RAG_with_LangChain/`
- `10_RAG_with_LlamaIndex/`

### `05_AI_Agent_Fundamentals/` — 92 notebooks
The largest phase. Agent building in both frameworks.

**`1. Building_Agents_From_Scratch/`**
- The agent loop with the raw OpenAI API
- An installable `agentic_patterns` package
- No framework involved

**`2. LangChain_Tools_and_Agents/`**
- Tool calling
- Tool-calling agents
- 16 applied builds

**`3. AI_Agents_with_LangGraph/`**
- 11 full real-world agent builds

**`4. Workflow_Pattern/`** · **`5. Agent Pattern/`** — the named design patterns
- Tool use
- Planning
- Reflection and Reflexion
- Router
- Prompt chaining
- Evaluator-optimizer
- Orchestrator-worker
- A dozen advanced cognitive patterns

## How to work through it

LangChain → LangGraph → RAG → Agents. RAG and Agents are independent of each other; either order works, but do both before `03_Advanced/`.

## Convention that matters here

LangGraph-phase notebooks initialise models through the shared factory — `from helpers import get_llm, get_embeddings` — never by instantiating `ChatOpenAI` directly. The LangChain phase does the opposite, inherited from its source repo. Each phase's `CLAUDE.md` says which applies.
