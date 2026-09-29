# Repository Catalog and Source Mapping

The mappings below describe the destination owner. They are not blind directory moves: every source item must pass the boundary audit before migration.

## 01 — `ai-engineering-demystified-01-foundations`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-01-foundations](https://github.com/Sourav692/ai-engineering-demystified-01-foundations) — ✅ created and migrated 2026-09-29 (private).

**Owns:** Python and async essentials, direct provider APIs, model landscape, model selection, transformer intuition, Hugging Face basics, and fine-tuning fundamentals.

**Source:** `01_Foundations/00_Theory_and_Foundations/`.

**Suggested modules:**

```text
modules/
├── 01_python_for_ai_engineering/
├── 02_files_data_and_apis/
├── 03_concurrency_and_asyncio/
├── 04_llm_provider_apis/
├── 05_model_landscape_and_selection/
├── 06_transformer_and_ml_intuition/
├── 07_hugging_face_models/
└── 08_fine_tuning_fundamentals/
```

**Must not contain:** prompt-engineering curricula, LangChain, LangGraph, RAG, or agents. Direct API examples use plain prompts only to demonstrate the API.

## 02 — `ai-engineering-demystified-02-prompt-context-engineering`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-02-prompt-context-engineering](https://github.com/Sourav692/ai-engineering-demystified-02-prompt-context-engineering) — ✅ created and migrated 2026-09-29 (private).

**Owns:** prompt patterns, structured prompting, multimodal prompting, context assembly, context-window strategy, and prompt evaluation at the prompt level.

**Source:** `01_Foundations/02_Prompt_and_Context_Engineering/`.

**Suggested modules:**

```text
modules/
├── 01_prompting_basics/
├── 02_advanced_prompt_patterns/
├── 03_model_specific_practice/
├── 04_multimodal_prompting/
├── 05_context_engineering/
└── 06_applied_prompting/
```

**Must not contain:** LangChain abstractions, graph orchestration, retrieval pipelines, memory systems, or tool-using agents.

## 03 — `ai-engineering-demystified-03-langchain-fundamentals`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-03-langchain-fundamentals](https://github.com/Sourav692/ai-engineering-demystified-03-langchain-fundamentals) — ✅ created and migrated 2026-09-29 (private).

**Owns:** LangChain model interfaces, messages, prompt templates, output parsers, Runnables/LCEL, composition, summarization, and deterministic workflow primitives.

**Primary source:** `02_Core/01_LangChain_Fundamentals/`.

**Relocate before extraction:**

- `07_LangChain_1x_Agents_and_Middleware/` -> repository 06.
- `08_Production_Course_Foundations/08_conversation_memory.ipynb` -> repository 08.
- `08_Production_Course_Foundations/09_langsmith_setup.ipynb` -> repository 13.
- Any tool-calling lesson whose objective is the autonomous agent loop -> repository 06.

**Must not contain:** agents, durable memory, RAG, LangGraph, or observability setup.

## 04 — `ai-engineering-demystified-04-langgraph-fundamentals`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-04-langgraph-fundamentals](https://github.com/Sourav692/ai-engineering-demystified-04-langgraph-fundamentals) — ✅ created and migrated 2026-09-29 (private).

**Owns:** state graphs, nodes, edges, reducers, messages state, conditional edges, runtime context, commands, subgraphs, checkpoint mechanics, interrupts, retry mechanics, async, and streaming.

**Primary source:** `02_Core/03_LangGraph_Fundamentals/`.

**Relocate or rewrite before extraction:**

- ReAct and tool-use agent lessons -> repository 06.
- `02_Core_Capabilities/02_Routing/` agentic-RAG examples -> repository 09, or replace them here with a neutral non-RAG router example.
- Multi-agent examples -> repository 08.
- Production error-handling lessons whose objective is operations rather than graph mechanics -> repository 13.

**Must not contain:** agent design patterns, RAG, multi-agent orchestration, or production monitoring.

## 05 — `ai-engineering-demystified-05-retrieval-rag`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-05-retrieval-rag](https://github.com/Sourav692/ai-engineering-demystified-05-retrieval-rag) — ✅ created and migrated 2026-09-29 (private).

**Owns:** document loading, chunking, embeddings, vector stores, indexing, retrievers, hybrid search, query transformation, reranking, citations, multimodal retrieval, and standard non-agentic RAG.

**Primary source:** `02_Core/04_Retrieval_and_RAG/`.

**Relocate before extraction:**

- `RAG_with_LangGraph/` agentic examples -> repository 09.
- Any corrective/adaptive/self/graph/agentic RAG material -> repository 09.
- Evaluation content whose objective is production quality control -> repository 13 or the existing evaluation repository.

**Special handling:** split `Comprehensive_RAG_Techniques` by learning objective. Foundational notebooks move here; advanced notebooks move to repository 09. Duplicate only the small helpers/data required to keep both destinations runnable.

**Must not contain:** autonomous retrieval decisions, retrieval grading loops, corrective/adaptive/self RAG, knowledge-graph RAG, or RAG as an agent tool.

## 06 — `ai-engineering-demystified-06-agent-fundamentals`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-06-agent-fundamentals](https://github.com/Sourav692/ai-engineering-demystified-06-agent-fundamentals) — ✅ created and migrated 2026-09-29 (private).

**Owns:** agent loop, tools and function calling, ReAct, planning, reflection, routing, prompt chaining, parallelization, evaluator-optimizer, orchestrator-worker as a single-agent workflow, human approval basics, and building agents from scratch.

**Primary source:** `02_Core/05_AI_Agent_Fundamentals/` plus agent-specific material removed from repositories 03 and 04.

**Move onward before extraction:**

- Multi-agent projects, supervisor systems, swarms, handoffs, and agent communication -> repository 08.
- Durable multi-session/long-term memory -> repository 08.
- Computer-use harness engineering and deep-agent systems -> repository 08.
- Agentic RAG -> repository 09.
- Production tracing, evaluation, security, and deployment -> repository 13.

**Must not contain:** first-party SDK instruction, multi-agent orchestration, advanced memory, agent protocols, or agentic RAG.

## 07 — `ai-engineering-demystified-07-first-party-agent-sdks`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-07-first-party-agent-sdks](https://github.com/Sourav692/ai-engineering-demystified-07-first-party-agent-sdks) — ✅ created and migrated 2026-09-29 (private).

**Owns:** provider-native agent SDK fundamentals for OpenAI, Anthropic, and Google, including model/tool/session APIs and SDK-specific lifecycle concepts.

**Source:** `03_Advanced/06_Agent_SDKs_First_Party/`.

**Suggested modules:**

```text
modules/
├── 01_openai_agents_sdk/
├── 02_anthropic_agent_sdk/
├── 03_google_adk/
└── 04_sdk_comparison/
```

**Boundary:** SDK examples may implement the single-agent patterns learned in repository 06. Multi-agent handoffs/orchestration are owned by repository 08; protocol interoperability is owned by repository 10.

## 08 — `ai-engineering-demystified-08-advanced-agent-systems`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-08-advanced-agent-systems](https://github.com/Sourav692/ai-engineering-demystified-08-advanced-agent-systems) — ✅ created and migrated 2026-09-29 (private).

**Owns:** short- and long-term memory, persistent state, multi-agent architectures, supervisors, swarms, handoffs, communication, hierarchical/parallel agents, deep agents, agent harnesses, and safe code/computer execution patterns.

**Primary source:** `03_Advanced/07_Advanced_Agentic_Systems/` plus advanced/multi-agent material removed from repositories 04, 06, and 07.

**Keep external:** agent and RAG evaluation curricula already live in `Agent_Evaluation_Demystified`; link to that repository instead of copying it.

**Must not contain:** corrective/adaptive/self/graph RAG, MCP/A2A/ACP protocol instruction, or production deployment/observability curricula.

## 09 — `ai-engineering-demystified-09-advanced-rag`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-09-advanced-rag](https://github.com/Sourav692/ai-engineering-demystified-09-advanced-rag) — ✅ created and migrated 2026-09-29 (private).

**Owns:** RAG as an agent tool, retrieval grading and rewriting, corrective RAG, adaptive RAG, self-RAG, RAPTOR, GraphRAG/knowledge graphs, CacheRAG, retrieval feedback loops, and other agentic retrieval architectures.

**Primary source:** `03_Advanced/08_Advanced_RAG/` plus the agentic-RAG material removed from repositories 04 and 05.

**Refactor required:** `Comprehensive_RAG_Techniques/` and `RAG_Ecosystem/` currently repeat foundational RAG. Keep only advanced lessons here; replace their basic sections with prerequisite links or short recap pages. Preserve runnable helpers and local data.

**Must not contain:** MCP/A2A/ACP, framework surveys, or production operations.

## 10 — `ai-engineering-demystified-10-agent-protocols`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-10-agent-protocols](https://github.com/Sourav692/ai-engineering-demystified-10-agent-protocols) — ✅ created and migrated 2026-09-29 (private).

**Owns:** MCP foundations, servers, clients, resources/prompts/tools, transports, authentication considerations, A2A, and ACP.

**Source:** `03_Advanced/09_Agent_Protocols/`.

**Boundary:** `MCP + A2A agentic RAG` belongs here because protocol composition is its learning objective. Its README should list repository 09 as a prerequisite and should not reteach agentic RAG.

**Must not contain:** general alternative-framework tutorials, coding-assistant usage, or production monitoring.

## 11 — `ai-engineering-demystified-11-alternative-agent-frameworks`

**Repository:** [https://github.com/Sourav692/ai-engineering-demystified-11-alternative-agent-frameworks](https://github.com/Sourav692/ai-engineering-demystified-11-alternative-agent-frameworks) — ✅ created and migrated 2026-09-29 (private).

**Owns:** CrewAI, AutoGen/AG2, DSPy, PydanticAI, and a comparison of orchestration frameworks.

**Source:** `03_Advanced/10_Alternative_Agent_Frameworks/`.

**Boundary:** teach what is unique about each framework. Projects may apply RAG, tools, or multi-agent patterns learned earlier, but must not reintroduce their general theory. Deployable product applications move to repository 14.

**Must not contain:** AI coding-tool instruction or production operations as primary topics.

## 12 — `ai-engineering-demystified-12-ai-coding-tools`

**Owns:** the coding-agent tool landscape, Claude Code, coding-agent CLI usage, agent skills, repository instructions, and building a small coding agent with provider APIs.

**Source:** `04_AI_Coding_Tools/`.

**Boundary:** this is about using and configuring coding agents. General agent-loop theory belongs to repository 06; deep harness engineering belongs to repository 08; production rollout and monitoring belong to repository 13.

## 13 — `ai-engineering-demystified-13-production-observability`

**Owns:** tracing, callbacks, monitoring, token/cost controls, caching/performance, reliability/fallbacks, testing, evaluation integration, safety, guardrails, red teaming, security, compliance, CI/CD, deployment, and operational infrastructure.

**Primary source:** `03_Advanced/12_Production_and_Observability/`, plus production material removed from earlier repositories.

**Also consider:** reusable deployment lessons extracted from mature projects, while the project-specific manifests stay with the project.

**Must not contain:** a new application domain or capstone whose primary purpose is feature building; those belong in repository 14.

## 14 — `ai-engineering-demystified-14-projects`

**Owns:** all 18 applications and capstones, organized by prerequisite level and system complexity.

### Group 01 — Foundational projects

Small and medium applications that mainly reinforce repositories 01-07.

```text
projects/01_foundational_projects/
├── README.md
├── 01_agent_tool_calling_foundations/
├── 02_automated_candidate_interview_evaluation/
├── 03_personalized_holiday_management_agent/
├── 04_resume_genie/
└── 05_rag_systems_projects/
```

**Sources:** matching folders under `05_Projects/`.

Each project keeps its own environment and tests. If `RAG_Systems_Projects` is too notebook-heavy to be an application, turn each notebook into an ordered project module rather than preserving a miscellaneous bucket.

### Group 02 — Retrieval and agent projects

Integrated RAG, agentic RAG, knowledge-base, and full-stack agent applications that mainly reinforce repositories 05-10.

```text
projects/02_retrieval_agent_projects/
├── README.md
├── 01_building_adaptive_rag/
├── 02_shopunow_agentic_rag/
├── 03_end_to_end_medical_chatbot/
├── 04_realtime_source_code_analyzer/
├── 05_ai_powered_customer_support/
├── 06_langgraph_fullstack_capstone/
└── 07_langchain_microservices_capstone/
```

**Sources:** matching folders under `05_Projects/`.

### Group 03 — Enterprise and realtime capstones

The most operationally demanding systems: enterprise platforms, multi-agent research, delivery frameworks, voice/realtime systems, and deployment-focused capstones.

```text
projects/03_enterprise_realtime_capstones/
├── README.md
├── 01_enterprise_rag_platform/
├── 02_enterprise_agentic_workflow_platform/
├── 03_enterprise_multi_agent_research_platform/
├── 04_fde_delivery_framework/
├── 05_realtime_voice_ai_agent_with_rag/
└── 06_pipecat_quickstart/
```

**Sources:** matching folders under `05_Projects/`.

Repository 14 is the final integration stage. Every project should name which repositories 01-13 are prerequisites and provide its own architecture, setup, tests, and deployment notes. The group folders establish recommended progression; they do not share runtime dependencies.

## Content not migrated into the sequence

```text
archive/                 keep only in the frozen legacy monorepo
.venv/ and caches        delete from extracted history/tips
.databricks/bundle/      generated state; do not migrate
.mcp_data/               local runtime state; do not migrate
.remember/ .tracker/     local tool state; do not migrate
temp/ outputs            remove unless they are intentional fixtures
.env                     never migrate; create .env.example files instead
```

Root `docs/`, `NOTEBOOK_INDEX.md`, and roadmap material should be converted into per-repository curriculum maps and the organization-level learning path. Root helpers are copied only into destinations that actually use them.
