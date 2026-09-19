<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working anywhere under this stage. Each phase inside also has its own CLAUDE.md, which is loaded on top of this one. -->

# Stage 02 — Core

**Entry rule: needs Foundations only.** The framework mechanics plus the two capabilities — retrieval and agents — that `03_Advanced/` composes. If content requires *agent* knowledge, it belongs in `03_Advanced/`, not here.

| Phase | Owns |
|---|---|
| `01_LangChain_Fundamentals/` | LangChain mechanics only |
| `03_LangGraph_Fundamentals/` | LangGraph mechanics only |
| `04_Retrieval_and_RAG/` | Foundational RAG — no agent prerequisite |
| `05_AI_Agent_Fundamentals/` | All agent building, both frameworks |

## Routing — where does new content go?

- LangChain chain/LCEL/prompt-template mechanics → `01_LangChain_Fundamentals/`
- LangGraph state/graph/routing mechanics → `03_LangGraph_Fundamentals/`
- Retrieval, embeddings, chunking, reranking → `04_Retrieval_and_RAG/` — **including its LangChain/LangGraph/LlamaIndex variants**, which are sibling tracks inside that phase, never separate phases
- Tool calling, agent loops, agent design patterns → `05_AI_Agent_Fundamentals/`, in whichever framework
- Memory → **not this stage.** `03_Advanced/07_Advanced_Agentic_Systems/Memory_and_State/` owns it for both frameworks, deliberately consolidated there rather than left in the fundamentals phases.
- Self-correcting or agentic RAG → **not this stage.** It needs agents, so `03_Advanced/08_Advanced_RAG/`.

## Stage-wide convention — `helpers` usage is NOT uniform here

This trips people up. Within one stage, two phases do the opposite thing:

| Phase | Factory |
|---|---|
| `03_LangGraph_Fundamentals/` | **Use it.** `from helpers import get_llm, get_embeddings`. Never instantiate `ChatOpenAI`/`ChatGroq`/`ChatDatabricks` directly. 15 files already do |
| `05_AI_Agent_Fundamentals/` | Use it for LangGraph-based notebooks (14 files do) |
| `04_Retrieval_and_RAG/` | Mixed — use it for new LangGraph-flavoured work; `RAG_Demystified`-sourced notebooks instantiate directly and stay that way |
| `01_LangChain_Fundamentals/` | **Don't.** Direct instantiation is inherited from the source repo and is explicitly not a violation to fix |

Check the phase's own `CLAUDE.md` before adding a notebook.

## Size

239 notebooks — the bulk of the repo. `05_AI_Agent_Fundamentals/` alone is 92.
