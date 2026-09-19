<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 01 — LangChain Fundamentals

**Owns:** LangChain mechanics only. Stage `02_Core/`.

| Track | Content |
|---|---|
| `01_Getting_Started/` … `05_Summarization/` | The original five fundamentals modules |
| `06_Workflow_Patterns/` | Chain-level workflow patterns (incl. evaluator-optimizer) |
| `07_LangChain_1x_Agents_and_Middleware/` | LangChain 1.x agents + middleware |
| `08_Production_Course_Foundations/` | Merged-in production-course material |

## Conventions here

- **This phase does NOT use the `helpers` factory** — it instantiates `ChatOpenAI`/etc. directly. That is a pre-existing property of the merged-in source repo (`LangChain_Demystified`), explicitly **not** a convention violation to "fix". Leave it.
- 48 notebooks.
- The LangChain 1.x migration tooling lives at `plugins/langchain-v1-migration/` and targets this phase. Invoke as `/langchain-v1-migration:<skill>`.

## Don't

- Don't add agent-building content — tool calling and agents belong to `02_Core/05_AI_Agent_Fundamentals/`, including their LangChain implementations.
- Don't add memory content — `03_Advanced/07_Advanced_Agentic_Systems/Memory_and_State/LangChain/` owns it, deliberately consolidated there rather than left in this fundamentals phase.
