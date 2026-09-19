<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 03 — LangGraph Fundamentals

**Owns:** LangGraph mechanics only — state, graphs, routing, tools, platform capabilities. Stage `02_Core/`.

| Track | Content |
|---|---|
| `01_Foundations/` | State, graphs, routing, tools, ReAct, Pydantic, node/command patterns (11 notebooks) |
| `02_Core_Capabilities/` | Routing, human-in-the-loop, advanced state, subgraphs, async/streaming, retries |

## Conventions here

- **Use the `helpers` factory — this phase is the strongest case for it.** 15 files already do `from helpers import get_llm, get_embeddings`. Never instantiate `ChatOpenAI`/`ChatGroq`/`ChatDatabricks` directly in this phase.
- 25 notebooks.
- This folder carries a large untracked `.venv/` (~1 GB). It is gitignored; don't be alarmed by directory-size tools reporting this phase as the biggest.

## Known gaps

- `02_Core_Capabilities/03_Human_in_the_Loop/01_HITL_Basics.ipynb` doesn't open with a `# Title` markdown cell (mid-document subheading instead). Pre-existing; fixing it means editing notebook content.

## Don't

- Don't add agent *applications* here — real-world agent builds belong to `02_Core/05_AI_Agent_Fundamentals/3. AI_Agents_with_LangGraph/`. This phase is mechanics only.
- Don't add RAG graphs here — `02_Core/04_Retrieval_and_RAG/08_RAG_with_LangGraph/` owns the basic ones, `03_Advanced/08_Advanced_RAG/` the agentic ones.
