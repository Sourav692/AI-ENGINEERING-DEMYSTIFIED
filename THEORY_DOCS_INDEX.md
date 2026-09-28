# Theory / Concept Documents Index

Catalog of markdown and HTML files in this repo (outside the root) whose purpose is to teach or
explain an AI-engineering concept in prose — book/course chapters, tutorials, cheat sheets,
pattern/architecture guides, protocol overviews, interview-prep concept guides, roadmap/anthology
explainer READMEs, the `docs/` tutorial microsite, and handbook chapters.

Excluded as non-theoretical: `.venv`/site-packages library docs, Claude Code tooling files
(`SKILL.md`, `CLAUDE.md`, skill `references/*.md`), synthetic RAG demo data, thin structural
`README.md`s that only list folder contents with no concept explanation, and process/meta docs
(task boards, plans, decision logs, progress checklists, gap analyses).

**Note:** section headings below are full repo-relative paths under the stage structure
(`01_Foundations/`, `02_Core/`, `03_Advanced/`, `05_Projects/`) and were
verified against disk on 2026-09-19. The earlier `00_`–`17_` flat numbering this
note used to warn about no longer exists; phase numbers inside each stage are the original ones and
were deliberately not renumbered, which is why there is no `11_` under `03_Advanced/`.

## 01_Foundations/00_Theory_and_Foundations

| Path | Type | Topics Covered |
|---|---|---|
| `Coding_Essentials_for_Agents/README_COURSE.md` | md | Python essentials for agent-building: files/DBs, Flask APIs, raw LLM API calls, threading/GIL, asyncio |

## 02_Core/01_LangChain_Fundamentals

| Path | Type | Topics Covered |
|---|---|---|
| `LangChain_v0_vs_v1_Differences.md` | md | LangChain 0.x vs 1.x API differences, migration concepts |

## 02_Core/03_LangGraph_Fundamentals

*(no standalone theory docs — core theory lives in notebooks and the `docs/` microsite below)*

## 02_Core/04_Retrieval_and_RAG

| Path | Type | Topics Covered |
|---|---|---|
| `03_Indexing_Techniques/Indexing_Techniques_Explained.md` | md | Multi-representation indexing, parent-document retrieval theory |
| `04_Query_Transformation_Techniques/Query_Transformation_Techniques_Explained.md` (+ `.html`) | md/html | Multi-query, RAG-Fusion, decomposition, step-back prompting, HyDE, query routing |

## 02_Core/05_AI_Agent_Fundamentals

| Path | Type | Topics Covered |
|---|---|---|
| `4. Workflow_Pattern/1. Prompt_Chaining/theory/01-prompt-chaining-pattern.md` (+html) | md/html | Prompt chaining pattern |
| `4. Workflow_Pattern/2. Routing/theory/02-routing-pattern.md` (+html) | md/html | Router pattern |
| `4. Workflow_Pattern/3. Parallelization/theory/03-parallelization-pattern.md` (+html) | md/html | Parallelization pattern |
| `4. Workflow_Pattern/4. Orchestrator_Worker/theory/05-orchestrator-workers-pattern.md` (+html) | md/html | Orchestrator-worker pattern |
| `4. Workflow_Pattern/5. Evaluator_Optimizer/theory/04-evaluator-optimizer-pattern.md` (+html) | md/html | Evaluator-optimizer pattern |
| `4. Workflow_Pattern/LangGraph_vs_LangChain_Workflow_Patterns.md` | md | Framework comparison for workflow patterns |
| `4. Workflow_Pattern/Workflow_vs_Agentic_Patterns.md` | md | Predefined workflows vs autonomous agent loops |
| `4. Workflow_Pattern/workflows.md` | md | Anthropic's "Building Effective Agents" patterns overview |
| `4. Workflow_Pattern/README.md` | md | Navigation + workflow-vs-agent framing |
| `5. Agent Pattern/01_Tool_Use/01-react-pattern.md` (+html) | md/html | ReAct pattern |
| `5. Agent Pattern/02_Planning/03-planning-pattern.md` (+html) | md/html | Planning pattern |
| `5. Agent Pattern/03_Reflection/02-reflection-pattern.md` (+html) | md/html | Reflection pattern |
| `5. Agent Pattern/03_Reflection/README_Reflection_Agents.md` | md | Reflection agents concept guide |
| `5. Agent Pattern/03_Reflection/README_Reflexion_Agents.md` | md | Reflexion (self-critique + memory) agents |
| `5. Agent Pattern/04_Advanced_Cognitive_Patterns/README.md` | md | 17+ advanced agentic architectures (PEV, blackboard, tree-of-thoughts, RLHF, etc.) |
| `docs/Agent_Pattern_Grouping.md` | md | Taxonomy of all agent design patterns |
| `docs/Design_Patterns_Reference.md` | md | Reference guide to agentic design patterns |

## 03_Advanced/06_Agent_SDKs_First_Party

*(all thin "Planned" scaffolding — no theory content yet)*

## 03_Advanced/07_Advanced_Agentic_Systems

| Path | Type | Topics Covered |
|---|---|---|
| `Deep_Agents_and_Harness_Engineering/docs/DEEP_AGENT_OVERVIEW.md` | md | Deep agent architecture, harness engineering, subagents, skills |
| `Deep_Agents_and_Harness_Engineering/docs/MEMORY_TYPES.md` | md | Agent memory types (short/long-term, episodic, semantic) |
| `Memory_and_State/LangGraph/01_Memory/memory/00_Memory_Layers_Guide.md` | md | Layered agent memory architecture |
| `Memory_and_State/LangGraph/01_Memory/memory/02_Agent_Memory_Types_SQLite.md` | md | Agent memory types with SQLite persistence |
| `Multi_Agent_Orchestration/01_Agent_Patterns/README_Supervisor_Multi_Agent_Alt.md` | md | Supervisor multi-agent pattern |
| `Multi_Agent_Orchestration/02_Multi_Agent_Swarm/README.md` | md | Multi-agent swarm architecture |
| `Multi_Agent_Orchestration/04-multiagent-pattern.md` (+html) | md/html | Multi-agent orchestration pattern |

## 03_Advanced/08_Advanced_RAG

| Path | Type | Topics Covered |
|---|---|---|
| `Comprehensive_RAG_Techniques/README.md` | md | Anthology overview of 42+ RAG techniques |
| `Comprehensive_RAG_Techniques/README_ROADMAP.md` | md | Curated reading order through the RAG anthology |

## 03_Advanced/09_Agent_Protocols

| Path | Type | Topics Covered |
|---|---|---|
| `MCP/04_Applications/mcp_a2a_agentic_rag/README.md` | md | Combined MCP + A2A + Agentic RAG architecture |
| `MCP/04_Applications/Udemy_MCP_Mastery/07 MCP Tools Resources and Prompts/presentation/mcp_tools_resources_prompts_presentation.html` | html | MCP core primitives: tools, resources, prompts |
| `MCP/04_Applications/Udemy_MCP_Mastery/08 MCP RAG with LangChain/presentation/mcp_rag_architecture.html` | html | RAG-over-MCP with LangChain architecture |
| `MCP/04_Applications/Udemy_MCP_Mastery/09 Research Assistant with MCP and LangGraph/presentation/research_assistant.html` | html | Research-assistant agent combining MCP + LangGraph |

## 03_Advanced/10_Alternative_Agent_Frameworks

| Path | Type | Topics Covered |
|---|---|---|
| `CrewAI/01_Foundations/reference_docs/TUTORIAL.md` | md | CrewAI Agent/Task/Crew abstractions and Flow API |

## 03_Advanced/12_Production_and_Observability

*(all thin "Planned/Built" scaffolding — no standalone theory content)*

## 05_Projects

| Path | Type | Topics Covered |
|---|---|---|
| `ShopUNow_Agentic_RAG_Capstone/WALKTHROUGH.md` | md | Multi-user conversational agentic RAG: LangGraph nodes, memory, routing |
| `Realtime_Voice_AI_Agent_with_RAG/Docs/PROJECT_REPORT.md` | md | Real-time voice AI assistant + RAG architecture |

## docs/ (static HTML tutorial microsite)

| Path | Type | Topics Covered |
|---|---|---|
| `docs/index.html` | html | Microsite landing page / table of contents for LangGraph mechanics chapters |
| `docs/chapter-1.html` | html | LangGraph fundamentals chapter 1 |
| `docs/chapter-2.html` | html | LangGraph fundamentals chapter 2 |
| `docs/chapter-3.html` | html | LangGraph fundamentals chapter 3 |
| `docs/chapter-4.html` | html | LangGraph fundamentals chapter 4 |
| `docs/chapter-5.html` | html | LangGraph fundamentals chapter 5 |
| `docs/chapter-6.html` | html | LangGraph fundamentals chapter 6 |
| `docs/chapter-7.html` | html | LangGraph fundamentals chapter 7 |
| `docs/tutorial_chapters.excalidraw` | excalidraw | Chapter map of the seven microsite chapters (moved here from the repo root 2026-09-19 — it diagrams exactly these files) |

**Interview prep moved out (2026-09-29).** The `06_Interview_Prep/` sections this index used to carry
(Handbook, FDE, AI_Engineer, OpenAI_Applied, Study_Guides) left with that folder for the separate
`Sourav692/Forward-Deployed-Engineer-Interview-Prep` repo.
