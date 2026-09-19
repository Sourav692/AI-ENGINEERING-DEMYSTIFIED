# Topic Docs Map

Every **prose topic explainer** that lives out in the roadmap phases, indexed in one place.

These files are *not* stored here. They stay beside the notebooks they explain — moving them
would split a phase's topic across two homes, which the repo's one-topic-one-phase rule exists
to prevent, and would break the `theory/` co-location several of them depend on. This file is
the discovery layer instead: browse by topic, click through to the file in its real home.

**Scope:** 23 concept explainers across stages `01_Foundations/` → `05_Projects/`, verified
against disk 2026-09-19. Excluded by design: runtime inputs that code reads (RAG corpora,
`SKILL.md` agent definitions, CrewAI task instructions, `chainlit.md`), project-bound docs
(architecture / deployment / module references), and link-list files (`Reference_link*.md`).

> Related: [`THEORY_DOCS_INDEX.md`](../../THEORY_DOCS_INDEX.md) catalogs *all* teaching prose
> repo-wide including HTML and handbook chapters. This map is the narrower cut — standalone
> concept explainers only, the ones worth revising from before an interview.

## Agent & workflow patterns

The five workflow patterns sit in `theory/` folders *inside* their own pattern folder, next to
the notebook that implements each one. Read the doc, then run the notebook beside it.

| Topic | Doc | Home |
|---|---|---|
| Prompt Chaining | [Prompt Chaining Pattern](../../02_Core/05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/1.%20Prompt_Chaining/theory/01-prompt-chaining-pattern.md) | Phase 5 |
| Routing | [Routing Pattern](../../02_Core/05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/2.%20Routing/theory/02-routing-pattern.md) | Phase 5 |
| Parallelization | [Parallelization Pattern](../../02_Core/05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/3.%20Parallelization/theory/03-parallelization-pattern.md) | Phase 5 |
| Orchestrator-Workers | [Orchestrator-Workers Pattern](../../02_Core/05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/4.%20Orchestrator_Worker/theory/05-orchestrator-workers-pattern.md) | Phase 5 |
| Evaluator-Optimizer | [Evaluator-Optimizer Pattern](../../02_Core/05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/5.%20Evaluator_Optimizer/theory/04-evaluator-optimizer-pattern.md) | Phase 5 |
| ReAct | [ReAct Pattern (Reason + Act)](../../02_Core/05_AI_Agent_Fundamentals/5.%20Agent%20Pattern/01_Tool_Use/01-react-pattern.md) | Phase 5 |
| Planning | [Planning Agent Pattern](../../02_Core/05_AI_Agent_Fundamentals/5.%20Agent%20Pattern/02_Planning/03-planning-pattern.md) | Phase 5 |
| Reflection | [Reflection Pattern](../../02_Core/05_AI_Agent_Fundamentals/5.%20Agent%20Pattern/03_Reflection/02-reflection-pattern.md) | Phase 5 |
| Multi-Agent / Agent-as-Tool | [Multi-Agent / Agent-as-Tool Pattern](../../03_Advanced/07_Advanced_Agentic_Systems/Multi_Agent_Orchestration/04-multiagent-pattern.md) | Phase 7 |

### Cross-cutting comparisons

Start here if you're trying to decide *which* pattern applies — these compare rather than teach one.

| Topic | Doc | Home |
|---|---|---|
| Workflow vs. agent — when each is right | [Workflows and Agents](../../02_Core/05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/workflows.md) | Phase 5 |
| Deterministic workflow vs. agentic control | [Workflow vs. Agentic Patterns](../../02_Core/05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/Workflow_vs_Agentic_Patterns.md) | Phase 5 |
| Same pattern, two frameworks | [LangGraph vs LangChain: Workflow Patterns](../../02_Core/05_AI_Agent_Fundamentals/4.%20Workflow_Pattern/LangGraph_vs_LangChain_Workflow_Patterns.md) | Phase 5 |
| How the patterns group together | [Agent Pattern Grouping](../../02_Core/05_AI_Agent_Fundamentals/docs/Agent_Pattern_Grouping.md) | Phase 5 |
| The full catalog in one doc | [Complete Guide to AI Agent Design Patterns](../../02_Core/05_AI_Agent_Fundamentals/docs/Design_Patterns_Reference.md) | Phase 5 |

## Retrieval & RAG

| Topic | Doc | Home |
|---|---|---|
| Multi-representation vs. parent-document indexing | [Indexing Techniques Explained](../../02_Core/04_Retrieval_and_RAG/03_Indexing_Techniques/Indexing_Techniques_Explained.md) | Phase 4 |
| Rewriting, multi-query, RAG-Fusion, HyDE, step-back | [Query Transformation Techniques](../../02_Core/04_Retrieval_and_RAG/04_Query_Transformation_Techniques/Query_Transformation_Techniques_Explained.md) | Phase 4 |

## Memory & state

| Topic | Doc | Home |
|---|---|---|
| Short-term / long-term / episodic memory layers | [Agent Memory Layers — A Field Guide](../../03_Advanced/07_Advanced_Agentic_Systems/Memory_and_State/LangGraph/01_Memory/memory/00_Memory_Layers_Guide.md) | Phase 7 |
| Persisting memory with LangGraph + SQLite | [Agent Memory Types — LangGraph + SQLite](../../03_Advanced/07_Advanced_Agentic_Systems/Memory_and_State/LangGraph/01_Memory/memory/02_Agent_Memory_Types_SQLite.md) | Phase 7 |
| Memory inside a deep-agent harness | [Memory Types in Deep Agent](../../03_Advanced/07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering/docs/MEMORY_TYPES.md) | Phase 7 |

## Deep agents & harness engineering

| Topic | Doc | Home |
|---|---|---|
| What a deep agent is, and the harness around it | [Deep Agent — Synaptic Command](../../03_Advanced/07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering/docs/DEEP_AGENT_OVERVIEW.md) | Phase 7 |
| Self-test questions | [Test Questions for Deep Agent](../../03_Advanced/07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering/docs/Questions.md) | Phase 7 |

## Frameworks

| Topic | Doc | Home |
|---|---|---|
| What changed between LangChain 0.x and 1.x | [LangChain 0.x vs 1.x — What Actually Changed](../../02_Core/01_LangChain_Fundamentals/LangChain_v0_vs_v1_Differences.md) | Phase 2b |
| First agent in CrewAI | [Building Your First AI Agent with CrewAI](../../03_Advanced/10_Alternative_Agent_Frameworks/CrewAI/01_Foundations/reference_docs/TUTORIAL.md) | Phase 10 |

## Maintenance

- Added 2026-09-19 after auditing all 120 non-`README` markdown files across the five stages.
- **Don't move a file here to "tidy" it.** If a doc explains a topic, it belongs beside that
  topic's notebooks; add a row to this table instead.
- `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/04-multiagent-pattern.md` (+`.html`) was a
  byte-identical duplicate of Phase 7's copy and was retired to `archive/` on 2026-09-19 — see
  [`archive/RETIRED_MANIFEST.md`](../../archive/RETIRED_MANIFEST.md). The Phase 7 copy above is
  canonical, since Phase 7 owns multi-agent orchestration.
