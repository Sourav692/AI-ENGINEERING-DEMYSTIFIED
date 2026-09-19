<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 05 — AI Agent Fundamentals

**Owns:** all agent-building content, both frameworks. Stage `02_Core/`. The largest phase in the repo at 92 notebooks.

| Track | Content |
|---|---|
| `1. Building_Agents_From_Scratch/` | OpenAI API + the `agentic_patterns` package — no LangGraph |
| `2. LangChain_Tools_and_Agents/` | Tool calling, tool-calling agents, agents, plus 16 applied builds |
| `3. AI_Agents_with_LangGraph/` | 11 full real-world agent builds |
| `4. Workflow_Pattern/` · `5. Agent Pattern/` | Named agentic design patterns — tool use, planning, reflection, router, prompt chaining, evaluator-optimizer, orchestrator-worker, advanced cognitive patterns |

## Conventions here

- `helpers` factory used in 14 files — use it for LangGraph-based notebooks.
- **Track folders use `N. Name` with a space.** Inconsistent with the rest of the repo, but established — match it when adding to an existing track rather than mixing styles inside the phase.
- `1. Building_Agents_From_Scratch/Agentic Patterns/` ships a real installable package under `src/agentic_patterns/`. Don't treat it as loose notebooks.

## Don't

- Don't add memory, multi-agent orchestration, or harness content — those are `03_Advanced/07_Advanced_Agentic_Systems/`.
- Don't add evaluation. **Evaluation is not in this repo** — it lives in the sibling repo `Agent_Evaluation_Demystified`.
