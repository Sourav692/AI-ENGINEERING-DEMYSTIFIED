<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 10 — Alternative Agent Frameworks

**Owns:** third-party agent frameworks outside the LangChain/LangGraph core path. Stage `03_Advanced/`. 47 notebooks.

| Track | State | Content |
|---|---|---|
| `CrewAI/` | Built | `01_Foundations/`, `02_Core_Capabilities/` (Flows), `03_Multi_Agent_Patterns/`, `04_Applications/` (9 project sets) |
| `AutoGen/` | Built | Foundations + core labs (conversable/sequential/tools/code/multimodal) + group/swarm patterns + 8 application project sets |
| `DSPy/` | Built | `context-engineering-dspy/` levels 1–5, kept whole |
| `PydanticAI/`, `Orchestration_Frameworks_Overview/` | Planned | |

## Dependency warning

- **CrewAI cannot share an environment with the root spine.** It hard-pins `chromadb<1.2`, which conflicts with `langchain-chroma` 1.1. Install it from its own per-folder `requirements.txt` in a separate venv. This exclusion is documented in `requirements.txt`'s header — don't "fix" it by bumping pins.
- The `frameworks` extra covers AutoGen; CrewAI stays out of it for the reason above.

## Don't

- Don't add first-party vendor SDKs here — those are Phase 06.
- A new framework is a **track inside this phase**, not a new phase.
