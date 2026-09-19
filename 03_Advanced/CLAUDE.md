<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working anywhere under this stage. Each phase inside also has its own CLAUDE.md, which is loaded on top of this one. -->

# Stage 03 — Advanced

**Entry rule: requires agent knowledge.** That is the test — not difficulty, not how recent the topic is. If someone who finished `02_Core/` could follow it without knowing how an agent works, it belongs in `02_Core/`.

This is the criterion that splits RAG across two phases, and it is the reference example for the whole stage scheme.

| Phase | Owns |
|---|---|
| `06_Agent_SDKs_First_Party/` | Vendor-native agent SDKs |
| `07_Advanced_Agentic_Systems/` | Memory, orchestration, harnesses |
| `08_Advanced_RAG/` | RAG that needs agents |
| `09_Agent_Protocols/` | MCP, ACP, A2A |
| `10_Alternative_Agent_Frameworks/` | CrewAI, AutoGen, DSPy, PydanticAI |
| `12_Production_and_Observability/` | Running LLM systems in production |

## Routing — where does new content go?

- A model vendor's own agent SDK → `06_Agent_SDKs_First_Party/`
- A third-party/community framework → `10_Alternative_Agent_Frameworks/`, as a **track inside it**, never a new phase
- A protocol → `09_Agent_Protocols/`
- Memory, multi-agent orchestration, agent harnesses → `07_Advanced_Agentic_Systems/`
- Self-correcting, corrective, adaptive or graph RAG → `08_Advanced_RAG/`
- Tracing, caching, cost, moderation, red teaming → `12_Production_and_Observability/`
- **Evaluation → none of the above.** It lives in the sibling repo `Agent_Evaluation_Demystified`. The line: measuring *answer quality* is evaluation; measuring *system behaviour* is observability and stays in `12_`.

## Stage-wide gotchas

- **CrewAI cannot share an environment with the root spine** — hard-pins `chromadb<1.2` against `langchain-chroma` 1.1. Separate venv from its own `requirements.txt`. Documented in `requirements.txt`'s header; don't "fix" it by bumping pins.
- **`07_.../Deep_Agents_and_Harness_Engineering/app/` has hit a file lock during 3 separate restructurings.** On a failed move, drain contents one level at a time rather than moving the directory.
- **Don't split `08_.../Comprehensive_RAG_Techniques/`** — its ~35 notebooks share `helper_functions.py`, `data/` and `images/` via relative paths.
- `09_Agent_Protocols/` has 9 dependency manifests; most MCP sub-projects run in their own environment, not the root one.

## Numbering

No `11_` here — Phase 11 (AI Coding Tools) is its own top-level group, since it is tooling you use rather than a topic in the arc. The gap is expected.
