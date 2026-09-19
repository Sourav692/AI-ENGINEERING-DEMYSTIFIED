# Theory / Concept Documents Index

Catalog of markdown and HTML files in this repo (outside the root) whose purpose is to teach or
explain an AI-engineering concept in prose — book/course chapters, tutorials, cheat sheets,
pattern/architecture guides, protocol overviews, interview-prep concept guides, roadmap/anthology
explainer READMEs, the `docs/` tutorial microsite, and handbook chapters.

Excluded as non-theoretical: `.venv`/site-packages library docs, Claude Code tooling files
(`SKILL.md`, `CLAUDE.md`, skill `references/*.md`), synthetic RAG demo data, thin structural
`README.md`s that only list folder contents with no concept explanation, and process/meta docs
(task boards, plans, decision logs, progress checklists, gap analyses).

**Note:** on-disk phase numbering (`00_`–`17_`) has drifted from what the root `CLAUDE.md`
documents (`01_`–`13_`) — the handbook (14), FDE prep (15), interview prep (16), OpenAI prep (17),
plus top-level `docs/` and `14_Interview_Preparation/Study_Guides/`, aren't reflected there at all. This index reflects what's
actually on disk.

## 00_Theory_and_Foundations

| Path | Type | Topics Covered |
|---|---|---|
| `Coding_Essentials_for_Agents/README_COURSE.md` | md | Python essentials for agent-building: files/DBs, Flask APIs, raw LLM API calls, threading/GIL, asyncio |

## 01_LangChain_Fundamentals

| Path | Type | Topics Covered |
|---|---|---|
| `LangChain_v0_vs_v1_Differences.md` | md | LangChain 0.x vs 1.x API differences, migration concepts |

## 03_LangGraph_Fundamentals

*(no standalone theory docs — core theory lives in notebooks and the `docs/` microsite below)*

## 04_Retrieval_and_RAG

| Path | Type | Topics Covered |
|---|---|---|
| `03_Indexing_Techniques/Indexing_Techniques_Explained.md` | md | Multi-representation indexing, parent-document retrieval theory |
| `04_Query_Transformation_Techniques/Query_Transformation_Techniques_Explained.md` (+ `.html`) | md/html | Multi-query, RAG-Fusion, decomposition, step-back prompting, HyDE, query routing |

## 05_AI_Agent_Fundamentals

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
| `5. Agent Pattern/04-multiagent-pattern.md` (+html) | md/html | Multi-agent pattern (supervisor/collaboration) |
| `5. Agent Pattern/04_Advanced_Cognitive_Patterns/README.md` | md | 17+ advanced agentic architectures (PEV, blackboard, tree-of-thoughts, RLHF, etc.) |
| `docs/Agent_Pattern_Grouping.md` | md | Taxonomy of all agent design patterns |
| `docs/Design_Patterns_Reference.md` | md | Reference guide to agentic design patterns |

## 06_Agent_SDKs_First_Party

*(all thin "Planned" scaffolding — no theory content yet)*

## 07_Advanced_Agentic_Systems

| Path | Type | Topics Covered |
|---|---|---|
| `Deep_Agents_and_Harness_Engineering/docs/DEEP_AGENT_OVERVIEW.md` | md | Deep agent architecture, harness engineering, subagents, skills |
| `Deep_Agents_and_Harness_Engineering/docs/MEMORY_TYPES.md` | md | Agent memory types (short/long-term, episodic, semantic) |
| `Memory_and_State/LangGraph/01_Memory/memory/00_Memory_Layers_Guide.md` | md | Layered agent memory architecture |
| `Memory_and_State/LangGraph/01_Memory/memory/02_Agent_Memory_Types_SQLite.md` | md | Agent memory types with SQLite persistence |
| `Multi_Agent_Orchestration/01_Agent_Patterns/README_Supervisor_Multi_Agent_Alt.md` | md | Supervisor multi-agent pattern |
| `Multi_Agent_Orchestration/02_Multi_Agent_Swarm/README.md` | md | Multi-agent swarm architecture |
| `Multi_Agent_Orchestration/04-multiagent-pattern.md` (+html) | md/html | Multi-agent orchestration pattern |

## 08_Advanced_RAG

| Path | Type | Topics Covered |
|---|---|---|
| `Comprehensive_RAG_Techniques/README.md` | md | Anthology overview of 42+ RAG techniques |
| `Comprehensive_RAG_Techniques/README_ROADMAP.md` | md | Curated reading order through the RAG anthology |

## 09_Agent_Protocols

| Path | Type | Topics Covered |
|---|---|---|
| `MCP/mcp_a2a_agentic_rag/README.md` | md | Combined MCP + A2A + Agentic RAG architecture |
| `MCP/04_Applications/Udemy_MCP_Mastery/07 MCP Tools Resources and Prompts/presentation/mcp_tools_resources_prompts_presentation.html` | html | MCP core primitives: tools, resources, prompts |
| `MCP/04_Applications/Udemy_MCP_Mastery/08 MCP RAG with LangChain/presentation/mcp_rag_architecture.html` | html | RAG-over-MCP with LangChain architecture |
| `MCP/04_Applications/Udemy_MCP_Mastery/09 Research Assistant with MCP and LangGraph/presentation/research_assistant.html` | html | Research-assistant agent combining MCP + LangGraph |

## 10_Alternative_Agent_Frameworks

| Path | Type | Topics Covered |
|---|---|---|
| `CrewAI/01_Foundations/reference_docs/TUTORIAL.md` | md | CrewAI Agent/Task/Crew abstractions and Flow API |

## 12_Production_and_Observability

*(all thin "Planned/Built" scaffolding — no standalone theory content)*

## 13_Projects

| Path | Type | Topics Covered |
|---|---|---|
| `ShopUNow_Agentic_RAG_Capstone/WALKTHROUGH.md` | md | Multi-user conversational agentic RAG: LangGraph nodes, memory, routing |
| `Realtime_Voice_AI_Agent_with_RAG/Docs/PROJECT_REPORT.md` | md | Real-time voice AI assistant + RAG architecture |

## 14_Interview_Preparation/Handbook

Handbook is structured as a full curriculum — every numbered chapter file within each module is a
theory chapter (133 files total; excluded only `project/data/corpus/*.md` synthetic ticket/policy
data, `Progress_Checklist.md`, `Source_Map.md`, and process-only project setup/validation READMEs).

| Path | Type | Topics Covered |
|---|---|---|
| `00_Orientation/*` (3 chapters + README) | md | Handbook usage, 3 AI-engineering roles, first-10-minutes interview framing |
| `01_LLM_Systems_Foundations/*` (5 chapters + README) | md | What RAG is, chunking/retrieval/fusion, tool-calling loop from scratch and in LangGraph |
| `02_System_Design_Fundamentals/*` (5 chapters + README) | md | 12-part system design framework, 15 design principles, monolith vs microservices, worked example, whiteboard method |
| `03_Robust_Agents/*` (5 chapters + README) | md | Retry/fallback/memoization/confirm, state/memory/sessions, parallel vs sequential execution, tool-call observability, guard checks |
| `04_Enterprise_RAG/01–10_*.md` + README | md | ABAC access control, ingestion pipeline, hybrid retrieval + rerank, query graph, output guardrails, eval, observability |
| `05_Agentic_Workflow_Platforms/01–07_*.md` + README | md | Canonical events/channels, determinism over free text, durability/idempotency, approvals/spend caps/staged rollout |
| `06_Cross_Cutting_Concerns/01–07_*.md` + README | md | Identity/secrets/tenant fairness, observability standards, caching/streaming/CI-CD, prompt injection/egress/tenancy, structured data routers, scaling to 20M docs |
| `07_Multi_Agent_Systems/01–05_*.md` + README | md | When multi-agent is justified, handoff reference architecture, failure isolation & evaluation, case studies |
| `07_Multi_Agent_Systems/diagrams/architecture.html, platform-architecture.html` | html | Multi-agent system architecture diagrams |
| `08_AgentOps_And_Platform/01–06_*.md` + README | md | Prompt versioning/rollout/rollback, AgentOps on Databricks, enterprise RAG on Databricks, multi-channel/HITL escalation, red teaming, infra/CI-CD |
| `09_AI_System_Design_Casebook/01–06_*.md` + README | md | Worked AI system designs: enterprise assistant, customer support, coding assistant, recruiting platform, logistics exception handling |
| `09_AI_System_Design_Casebook/whiteboard_scripts/*.md` | md | Whiteboard-style scripts for enterprise RAG w/ access control, RAG on Databricks, agent platform for non-technical users, scoping-to-deployed-agent |
| `10_FDE_Delivery_Operating_Model/01–07_*.md` + README | md | FDE delivery model: day-in-the-life, six-stage delivery process, scoping-to-production in 2 weeks, gates/risks/metrics, cross-team collaboration |
| `11_Telling_The_Story/01–02_*.md` + README | md | Deep-dive vs conversational technical-story formats, proof vs cheat-sheet honesty |
| `11_Telling_The_Story/stories/*.md` (9 files) | md | Technical narrative write-ups of enterprise RAG and multi-agent builds |
| `11_Telling_The_Story/stories/STAR_Stories_Client_Engagements.html, STAR_Stories_Technical_Build_Projects.html` | html | STAR-format technical story narratives |
| `99_Appendices/A_Glossary.md` | md | Glossary of AI-engineering/agent terminology |
| `99_Appendices/C_Interview_QA_Log.md` | md | Logged interview Q&A covering handbook concepts |
| `04_Enterprise_RAG/project/README.md` | md | Meridian Assist: enterprise RAG with attribute-based access control — architecture explanation |
| `05_Agentic_Workflow_Platforms/project/README.md` | md | Deterministic guardrail/orchestration engine for non-technical-user agent platforms |
| `07_Multi_Agent_Systems/reference_code/README.md` | md | Autonomous research agent: multi-agent pipeline, red teaming, LLM eval architecture |
| `10_FDE_Delivery_Operating_Model/project/README.md` | md | Gate-enforcing state machine for scoping-to-deployed-agent delivery framework |

## 14_Interview_Preparation/FDE

| Path | Type | Topics Covered |
|---|---|---|
| `Cracking_Agentic_AI_System_Design_Interviews/ch05_tool_use_agent_computer_interface.md` (+html) | md/html | Tool use & agent-computer interface design |
| `Cracking_Agentic_AI_System_Design_Interviews/ch06_orchestration_context_engineering.md` (+html) | md/html | Orchestration and context engineering |
| `Cracking_Agentic_AI_System_Design_Interviews/ch07_knowledge_memory_retrieval.md` (+html) | md/html | Knowledge, memory, and retrieval systems |
| `Cracking_Agentic_AI_System_Design_Interviews/ch08_learning_in_agentic_systems.md` (+html) | md/html | Learning mechanisms in agentic systems |
| `Cracking_Agentic_AI_System_Design_Interviews/ch12_validation_and_measurement.md` (+html) | md/html | Validation and measurement of agentic systems |
| `Cracking_Agentic_AI_System_Design_Interviews/ch23_system_design_patterns.md` (+html) | md/html | Agentic system design patterns |
| `Cracking_Agentic_AI_System_Design_Interviews/ch27_technical_interview.md` (+html) | md/html | Technical interview format/approach for agentic AI system design |
| `Cracking_Agentic_AI_System_Design_Interviews/ch28_system_design_interview.md` (+html) | md/html | System design interview format/approach |
| `Delivery Framework from Scoping to Delivery/docs/01-theory.md` | md | Delivery-framework theory: scoping to deployed agent |
| `Delivery Framework from Scoping to Delivery/docs/02-architecture-end-to-end.md` | md | End-to-end architecture of the delivery framework |
| `Delivery Framework from Scoping to Delivery/docs/03-src-modules-reference.md` | md | Module-by-module reference of the delivery framework's implementation |
| `Delivery Framework from Scoping to Delivery/docs/04-system-design-coverage-map.md` | md | Mapping of system-design concepts covered by the project |
| `Delivery Framework from Scoping to Delivery/docs/05-security-gate-depth-and-tenant-scale.md` | md | Security gates and multi-tenant scaling concepts |
| `Senior_FDE_Day_to_Day.md` | md | Senior Forward Deployed Engineer role/responsibilities |
| `Star_Stories/AIA_Enterprise_RAG_Conversational_Guide.md` | md | Enterprise RAG project narrative (conversational format) |
| `Star_Stories/AIA_Enterprise_RAG_DeepDive_15-20min.md` | md | Enterprise RAG project deep-dive narrative |
| `Star_Stories/AIA_Enterprise_RAG_Governance_FDE_Script.md` | md | Enterprise RAG governance concepts, FDE-oriented script |
| `Star_Stories/AIA_MultiAgent_Architecture_Mermaid.md` | md | Multi-agent system architecture (diagrammed) |
| `Star_Stories/AIA_MultiAgent_Conversational_Guide.md` | md | Multi-agent system narrative (conversational format) |
| `Star_Stories/AIA_MultiAgent_DeepDive_15-20min.md` | md | Multi-agent system deep-dive narrative |
| `Star_Stories/AIA_Technical_Implementation_Flow.md` | md | Technical implementation flow for the AIA projects |
| `Star_Stories/Bajaj_RapidLR_Technical_Implementation_Flow.md` | md | Technical implementation flow for the Bajaj RapidLR project |
| `Star_Stories/Enterprise_RAG_Conversational_Guide.md` | md | Enterprise RAG narrative (conversational format) |
| `Star_Stories/Enterprise_RAG_DeepDive_15-20min.md` | md | Enterprise RAG deep-dive narrative |
| `Star_Stories/STAR Stories — Technical Build Projects.html, star_stories.html` | html | STAR-format technical build project narratives |
| `System_Design and Delivery/1. System Design Overview.md` (+html) | md/html | System design overview |
| `System_Design and Delivery/2. System Design Components.md` (+html) | md/html | System design components |
| `System_Design and Delivery/3. System Design Principles.md` (+html) | md/html | System design principles |
| `System_Design and Delivery/4. Monolith vs Microservice Architecture.md` (+html) | md/html | Monolith vs microservice architecture |
| `System_Design and Delivery/5. Enterprise AI Assistant Design.md` (+html) | md/html | Enterprise AI assistant system design |
| `System_Design and Delivery/6. Customer Support AI Assistant Design.md` (+html) | md/html | Customer support AI assistant system design |
| `System_Design and Delivery/7. AI Powered Coding Assistant Design.md` (+html) | md/html | AI-powered coding assistant system design |
| `System_Design and Delivery/8. AI Powered Recruiting Platform Design.md` (+html) | md/html | AI-powered recruiting platform system design |
| `System_Design and Delivery/9. Proj Delivery.md` (+html) | md/html | Project delivery methodology for AI systems |
| `System_Design and Delivery/10. Cross Team Collaboration.md` (+html) | md/html | Cross-team collaboration in AI delivery |
| `System_Design and Delivery/AI Logistics Exception-Handling Assistant Design.md` (+html) | md/html | AI logistics exception-handling assistant design |
| `System_Design and Delivery/Agentic Coverage Map.html` | html | Coverage map of agentic system design topics |
| `System_Design and Delivery/Mock - AI Exception-Handling Assistant.md` | md | Mock interview design walkthrough for exception-handling assistant |

## 14_Interview_Preparation/AI_Engineer

| Path | Type | Topics Covered |
|---|---|---|
| `Cross Cutting Preparation/00-first-ten-minutes.html` | html | First-ten-minutes interview framing for system design |
| `Cross Cutting Preparation/01-identity-secrets-and-tenant-fairness.md` | md | Identity, secrets management, tenant fairness |
| `Cross Cutting Preparation/02-observability-standards-and-failure-patterns.md` | md | Observability standards and failure patterns |
| `Cross Cutting Preparation/03-cost-latency-cicd-rigor-and-build-vs-buy.md` | md | Cost/latency, CI/CD rigor, build-vs-buy decisions |
| `Cross Cutting Preparation/04-agentops-on-databricks.md` | md | AgentOps concepts on Databricks |
| `Cross Cutting Preparation/05-guarding-tool-calls.md` | md | Guardrails for agent tool calls |
| `Cross Cutting Preparation/Cross_Cutting_System_Design_Quick_Reference_v2.md` | md | Quick-reference summary of cross-cutting system design concerns |
| `Enteprise Multi-Agent AI Research Platform/ARCHITECTURE DIAGRAMS/LAYERS_EXPLAINED.md` | md | Layered architecture explanation for a multi-agent research platform |
| `Enteprise Multi-Agent AI Research Platform/ARCHITECTURE DIAGRAMS/architecture.html, architecture_mermaid.html, platform-architecture.html` | html | Multi-agent research platform architecture diagrams |
| `Enterprise Agentic Workflow Automation Platform/docs/01-theory.md` | md | Theory of enterprise agentic workflow automation |
| `Enterprise Agentic Workflow Automation Platform/docs/02-architecture-end-to-end.md` | md | End-to-end architecture for the workflow automation platform |
| `Enterprise Agentic Workflow Automation Platform/docs/03-src-modules-reference.md` | md | Module reference for the workflow automation platform |
| `Enterprise Agentic Workflow Automation Platform/docs/04-system-design-coverage-map.md` | md | System design coverage map for the platform |
| `Enterprise Agentic Workflow Automation Platform/docs/05-security-tenancy-and-observability-gaps.md` | md | Security, tenancy, and observability gap analysis concepts |
| `Enterprise Agentic Workflow Automation Platform/INTERVIEW_SCRIPT.md` | md | Interview walkthrough script covering the platform's architecture/concepts |
| `Enterprise RAG Platform/docs/01-theory.md` | md | Enterprise RAG theory |
| `Enterprise RAG Platform/docs/03-theory-databricks.md` | md | Enterprise RAG theory specific to Databricks |
| `Enterprise RAG Platform/docs/04-security-checks-reference.md` | md | Security checks reference for enterprise RAG |
| `Enterprise RAG Platform/docs/05-src-modules-reference.md` | md | Source module reference |
| `Enterprise RAG Platform/docs/06-architecture-end-to-end.md` | md | End-to-end architecture |
| `Enterprise RAG Platform/docs/07-system-design-coverage-map.md` | md | System design coverage map |
| `Enterprise RAG Platform/docs/08-structured-data-and-connectors.md` | md | Structured data and connector integration concepts |
| `Enterprise RAG Platform/docs/09-multi-agent-orchestration.md` | md | Multi-agent orchestration within enterprise RAG |
| `Enterprise RAG Platform/docs/10-agent-ops-and-channels.md` | md | AgentOps and multi-channel concepts |
| `Enterprise RAG Platform/docs/QA.md` | md | Q&A covering enterprise RAG platform concepts |
| `Enterprise RAG Platform/docs/Scale_Optimization.md` | md | Scale optimization strategies for enterprise RAG |
| `Enterprise RAG Platform/INTERVIEW_SCRIPT.md, INTERVIEW_SCRIPT_DATABRICKS.md` | md | Interview walkthrough scripts covering the RAG platform's architecture/concepts |

## 14_Interview_Preparation/OpenAI_Applied

*(the one file here, `OpenAI_Applied_AI_Engineer_Coverage_Gap_Analysis.md`, is a personal gap-analysis/planning doc rather than a concept explainer — excluded)*

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

## 14_Interview_Preparation/Study_Guides/ (top-level, standalone interview/tutorial content)

| Path | Type | Topics Covered |
|---|---|---|
| `14_Interview_Preparation/Study_Guides/01_langchain_foundations_INTERVIEW_TUTORIAL.md` | md | LangChain foundations interview tutorial |
| `14_Interview_Preparation/Study_Guides/04_rag_and_retrieval_INTERVIEW_TUTORIAL.md` | md | RAG and retrieval interview tutorial |
| `14_Interview_Preparation/Study_Guides/03_langgraph_fundamentals_INTERVIEW_TUTORIAL.md` | md | LangGraph fundamentals interview tutorial |
| `14_Interview_Preparation/Study_Guides/07_multi_agent_systems_INTERVIEW_TUTORIAL.md` | md | Multi-agent systems interview tutorial |
| `14_Interview_Preparation/Study_Guides/12_production_and_operations_INTERVIEW_TUTORIAL.md` | md | Production/operations (LLMOps) interview tutorial |
| `14_Interview_Preparation/Study_Guides/agent_fundamentals_and_advanced_agentic_systems_INTERVIEW_TUTORIAL.md` (+html) | md/html | Agent fundamentals & advanced agentic systems interview tutorial |
| `14_Interview_Preparation/Study_Guides/INTERVIEW_DRILL_HUB.html` | html | Hub linking/organizing all interview drill tutorials |
| `14_Interview_Preparation/Study_Guides/chunking/01-chunking-strategies-by-doc-type.md` (+html) | md/html | Chunking strategies by document type |
| `14_Interview_Preparation/Study_Guides/chunking/chunking-by-doc-type.md` (+html) | md/html | Chunking by document type (companion/alt version) |
| `14_Interview_Preparation/Study_Guides/evaluation/00-evaluation-index.md` (+html) | md/html | Index of RAG/agent evaluation topics |
| `14_Interview_Preparation/Study_Guides/evaluation/01-deterministic-retrieval-metrics.md` (+html) | md/html | Deterministic retrieval evaluation metrics |
| `14_Interview_Preparation/Study_Guides/evaluation/02-llm-judged-retrieval-metrics.md` (+html) | md/html | LLM-as-judge retrieval evaluation metrics |
| `14_Interview_Preparation/Study_Guides/evaluation/03-generator-metrics.md` (+html) | md/html | Generator (answer-quality) evaluation metrics |
| `14_Interview_Preparation/Study_Guides/evaluation/04-tool-use-evaluation.md` (+html) | md/html | Tool-use evaluation for agents |
| `14_Interview_Preparation/Study_Guides/evaluation/05-agent-trajectory-evaluation.md` (+html) | md/html | Agent trajectory evaluation |
| `14_Interview_Preparation/Study_Guides/multi_agent_coordination_patterns.md` (+html) | md/html | Multi-agent coordination patterns |
| `14_Interview_Preparation/Study_Guides/multi_agent_systems_qa_reference.html` | html | Q&A reference on multi-agent systems |
| `14_Interview_Preparation/Study_Guides/parent_document_retrieval_INTERVIEW_TUTORIAL.md` (+html) | md/html | Parent-document retrieval technique |
| `14_Interview_Preparation/Study_Guides/retrieval_strategies/rag_retrieval_strategies.md` (+html) | md/html | RAG retrieval strategies overview |
