# Supervisor to Swarm — study route

A five-session route through notebooks that already live in this folder's siblings.
Open [`SUPERVISOR_TO_SWARM.html`](SUPERVISOR_TO_SWARM.html) alongside them: it carries
the goals, the classes and functions to read for, the exercises and the checkpoints for
each session.

**This folder holds no notebooks.** The route was first built on the `RAG_Curriculum`
branch as a top-level `SUPERVISOR_TO_SWARM/` folder of renamed copies. When it was ported
on 2026-09-28 the copies were dropped: they were byte-identical to the originals, and a
second copy would give multi-agent orchestration two homes in the repo. Work through the
originals below instead, so fixes to them reach you.

## Sessions

| # | Notebook | Session adds |
| --- | --- | --- |
| 1 | [`01_Agent_Patterns/02_Supervisor_Multi_Agent_Alt.ipynb`](../01_Agent_Patterns/02_Supervisor_Multi_Agent_Alt.ipynb) | All five architectures side by side · `Command(goto=)` |
| 2 | [`Production_Course_Multi_Agent/01_multi_agent.ipynb`](../Production_Course_Multi_Agent/01_multi_agent.ipynb) | State schema as the design decision · `RouteDecision` |
| 3 | [`Production_Course_Multi_Agent/06_hierarchical_agents.ipynb`](../Production_Course_Multi_Agent/06_hierarchical_agents.ipynb) | Compiled subgraph as a node · `TeamState` |
| 4 | [`02_Multi_Agent_Swarm/01_Multi_Agent_Swarm.ipynb`](../02_Multi_Agent_Swarm/01_Multi_Agent_Swarm.ipynb) | Handoff tools · `create_swarm` · checkpointer memory |
| 5 | [`Production_Course_Multi_Agent/07_multi_agent_research_system.ipynb`](../Production_Course_Multi_Agent/07_multi_agent_research_system.ipynb) | `Send()` dynamic fan-out · cyclic quality gate |

Next step after session 5:
[`07_Async_and_Streaming/01_Async_Multi_Agent.ipynb`](../07_Async_and_Streaming/01_Async_Multi_Agent.ipynb)
takes the same patterns async.

## Suggested pace

Sessions 1, 2, 3 and 5 are about 90 minutes each. **Session 4 wants two sittings.** It is
46 cells and builds real RAG and NL2SQL subsystems before the swarm exists, so do the
sub-agents first and the assembly second.

## Running them

Everything resolves through the installed `helpers` package and the project-root `.env`,
so notebook depth doesn't matter. Generated artifacts (`chroma_db_swarm/`,
`research_graph.png`) land beside whichever notebook you run.
