# Roadmap Map

This file is the skill's memory of the roadmap's actual shape. **Update it every time a top-level section is created or changes status** — same discipline as `NOTEBOOK_INDEX.md`. It has two parts: sections that exist on disk today, and sections the user has named as coming but hasn't started yet. Both are living lists — add, edit, or remove entries as reality changes. Don't let this file drift from disk.

## Existing sections (on disk)

### `01_Foundations/` through `07_Deep_Agents/` — LangGraph
The first and so far only fully-built-out framework section. Internal shape: `01_Foundations` (core graph/state/routing mechanics, flat numbered notebooks) → `02_Core_Capabilities` (platform features — memory, HITL, subgraphs, streaming, retries — each in its own numbered subfolder) → `03_RAG` → `04_Agents` (full real-world agent builds) → `05_Agentic_Design_Patterns` (named patterns, each its own numbered subfolder) → `06_Production` (deployable apps/tests, not notebooks) → `07_Deep_Agents` (the `deepagents` multi-agent framework specifically, vendored in, keeps its own `CLAUDE.md`).

This progression (fundamentals → core capabilities → applied → patterns → production) is a reasonable template for other framework sections but was designed around LangGraph's own shape — don't assume every future framework needs exactly these six stages.

### `archive/`
Retired/superseded notebooks. Frozen — don't add to it proactively.

### `docs/` (root)
Static HTML tutorial microsite mirroring the LangGraph chapters. Framework-specific; a new framework section publishing its own microsite pages would extend this, not replace it — ask the user how they want new sections represented here, if at all.

### Root scaffolding
`helpers/` (shared LangGraph/LLM factory code), `pyproject.toml`/`requirements.txt`/`uv.lock`/`databricks.yml` (root env, currently scoped to what LangGraph content needs), `README.md`/`CLAUDE.md`/`NOTEBOOK_INDEX.md`, `links.md`, `LICENSE`. As other frameworks arrive with their own dependencies, decide per-section whether they share the root env or get a self-contained `requirements.txt` (precedent: `02_Core_Capabilities/01_Memory/memory/` is self-contained within LangGraph already) — don't assume, ask.

## Anticipated sections (named by the user, not yet created)

These don't have folders yet. When the first real file for one of these shows up, treat it as that section's first content — propose creating the top-level folder (next number in sequence) rather than treating the item as ambiguous or forcing it into an existing LangGraph chapter.

- **LangChain** — likely its own foundations→application progression, distinct from LangGraph despite shared lineage (different abstraction, different idioms).
- **CrewAI** — role-based multi-agent framework; expect crew/agent/task-definition content, possibly its own "patterns" analog to `05_Agentic_Design_Patterns`.
- **AutoGen** — Microsoft's multi-agent conversation framework.
- **MCP** (Model Context Protocol) — a protocol, not a framework; likely server/client implementation notebooks rather than a foundations→production learning arc. May not need the six-stage template at all.
- **ADK** — Google's Agent Development Kit.
- **OpenAI SDK** — OpenAI's Agents SDK / Responses API-based agent building.
- **Google SDK** — Google's general AI SDK (separate from ADK — clarify with the user which is which when content for both starts arriving, since the names overlap).
- **A2A** (Agent-to-Agent protocol) — another protocol section, likely small and focused like MCP.
- **Fine-Tuning** — cross-cutting competency, not tied to one framework.
- **Evaluation & Observability** — cross-cutting competency: LLM-as-judge, tracing, eval harnesses, monitoring. Applies across every framework section above.
- **Projects** — capstone/integration work combining multiple frameworks. Ask the user whether this should be numbered into the main sequence or kept as a parallel, unnumbered area (like `archive/`) — its placement wasn't decided as of the last update to this file.

When any of the above gets its first real content, move its entry up into "Existing sections," fill in its actual internal shape once one exists, and give it a number continuing from the current highest top-level number on disk.
