# Supervisor to Swarm — study pack

**These are copies.** The originals remain in place under
`07_Advanced_Agentic_Systems/Multi_Agent_Orchestration/` and are unchanged.
Nothing was moved.

Copied 2026-09-11 from the five notebooks named in [`../SUPERVISOR_TO_SWARM.html`](../SUPERVISOR_TO_SWARM.html),
renumbered into the study order from that plan. Open the HTML alongside these —
it carries the goals, the specific classes and functions to read for, the
exercises, and the checkpoints for each session.

## Contents

| # | File here | Copied from | Session adds |
| --- | --- | --- | --- |
| 01 | `01_Supervisor_Multi_Agent_Alt.ipynb` | `Multi_Agent_Orchestration/01_Agent_Patterns/02_Supervisor_Multi_Agent_Alt.ipynb` | All five architectures side by side · `Command(goto=)` |
| 02 | `02_multi_agent.ipynb` | `Multi_Agent_Orchestration/Production_Course_Multi_Agent/01_multi_agent.ipynb` | State schema as the design decision · `RouteDecision` |
| 03 | `03_hierarchical_agents.ipynb` | `Multi_Agent_Orchestration/Production_Course_Multi_Agent/06_hierarchical_agents.ipynb` | Compiled subgraph as a node · `TeamState` |
| 04 | `04_Multi_Agent_Swarm.ipynb` | `Multi_Agent_Orchestration/02_Multi_Agent_Swarm/01_Multi_Agent_Swarm.ipynb` | Handoff tools · `create_swarm` · checkpointer memory |
| 05 | `05_multi_agent_research_system.ipynb` | `Multi_Agent_Orchestration/Production_Course_Multi_Agent/07_multi_agent_research_system.ipynb` | `Send()` dynamic fan-out · cyclic quality gate |

Only the filenames changed — every file is byte-identical to its source
(SHA-256 verified on copy).

## These are copies, so they will drift

Edits here do **not** reach the originals, and edits to the originals do not
reach here. If a notebook in `07_Advanced_Agentic_Systems/` is fixed later, this
copy keeps the old version. Treat this folder as a snapshot for working through
the plan, and make lasting changes in the phase folder.

`NOTEBOOK_INDEX.md` lists the originals. It does not list these copies, because
they are not new curriculum content.

## Running them from here

Two path details change because these sit one level below the repository root
rather than four:

- **`04_Multi_Agent_Swarm.ipynb` loads `../.env`.** From here that resolves to
  the repository-root `.env`, so it works. In its original location that path
  pointed at `Multi_Agent_Orchestration/.env`, which does not exist — so the
  copy is actually better off than the original on this one point.
- **Generated artifacts land beside the notebook you run.** The swarm notebook
  creates `chroma_db_swarm/` and the research system writes `research_graph.png`,
  both relative to the working directory. Running from here creates fresh ones in
  this folder rather than reusing whatever exists next to the originals.

Everything else resolves through the installed `helpers` package and the
project-root `.env`, neither of which depends on notebook depth.

## Suggested pace

Sessions 1, 2, 3 and 5 are about 90 minutes each. **Session 4 wants two
sittings** — it is 46 cells and builds real RAG and NL2SQL subsystems before the
swarm exists. Sub-agents first, assembly second.
