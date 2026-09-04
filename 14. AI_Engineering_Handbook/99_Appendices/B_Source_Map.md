# Appendix B · Source Map

Every handbook document, and the original file(s) it was built from. Paths are relative to the repository root. **The originals are untouched**; this handbook was assembled from them, and this map is how provenance is preserved as the handbook grows.

Treatment codes: **R** rewritten into the handbook voice · **C** copied with a handbook header (performance artefacts and personal narratives) · **N** new for the handbook · **P** project code copied (caches, `runs/`, and the Chroma index excluded).

## Root and Module 00

| Handbook doc | Treatment | Source |
|---|---|---|
| `README.md` | N | — |
| `00_Orientation/01_How_To_Use_This_Handbook.md` | N | — |
| `00_Orientation/02_The_Three_Roles.md` | N | `4. FDE_Related_Preparation/Senior_FDE_Day_to_Day.md` (three-lens model) |
| `00_Orientation/03_The_First_Ten_Minutes.md` | R | `3. AI_Engineer_Interview_Preparation/Cross Cutting Preparation/00-first-ten-minutes.html` |

## Module 01 · LLM Systems Foundations

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_What_RAG_Actually_Is.md` | R | `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/01-theory.md` §1–3 |
| `02_Chunking_Retrieval_Fusion.md` | R | same, §4–6 |
| `03_What_An_Agent_Actually_Is.md` | R | `1. Company_Wise_Preparation/2. DevRev/Coding_Round/agent_tool_calling_demo/README.md`, `src/tools.py`, `src/brain.py`; `Enterprise Agentic Workflow Automation Platform/docs/01-theory.md` §A.2–A.4 |
| `04_Tool_Calling_Loop_From_Scratch.md` | R | `agent_tool_calling_demo/src/scratch_agent.py`, `src/brain.py`, `README.md`, `tests/test_agent.py` |
| `05_Same_Loop_In_LangGraph.md` | R | `agent_tool_calling_demo/src/langgraph_agent.py`, `README.md` |
| `project/` | P | `1. Company_Wise_Preparation/2. DevRev/Coding_Round/agent_tool_calling_demo/` (minus `docs/`) |

## Module 02 · System Design Fundamentals

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_The_12_Part_Framework.md` | R | `4. FDE_Related_Preparation/System_Design and Delivery/2. System Design Components.md` |
| `02_The_15_Principles.md` | R | `…/3. System Design Principles.md` |
| `03_Monolith_vs_Microservices.md` | R | `…/4. Monolith vs Microservice Architecture.md` |
| `04_Worked_Example_Travel_Agent.md` | R | `…/1. System Design Overview.md` |
| `05_The_60_Minute_Whiteboard_Method.md` | N | synthesised from the four `INTERVIEW_SCRIPT*.md` files (see Module 09) |

## Module 03 · Robust Agents

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_Retry_Fallback_Memo_Confirm.md` | R | `agent_tool_calling_demo/src/robustness.py`, `docs/DESIGN.md` §4, `tests/test_agent.py` |
| `02_State_Memory_Sessions.md` | R | `agent_tool_calling_demo/docs/DESIGN.md` §1, `src/scratch_agent.py`; `System_Design and Delivery/6. Customer Support AI Assistant Design.md` §6 |
| `03_Parallel_vs_Sequential.md` | R | `agent_tool_calling_demo/docs/DESIGN.md` §3 |
| `04_Observability_For_Tool_Calls.md` | R | `agent_tool_calling_demo/src/observability.py`, `docs/DESIGN.md` §2 |
| `05_The_Eight_Guard_Checks.md` | R | `Cross Cutting Preparation/05-guarding-tool-calls.md`; `agent_tool_calling_demo/src/robustness.py` |

## Module 04 · Enterprise RAG

All sources under `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/`.

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_Why_Enterprise_Changes_The_Problem.md` | R | `README.md` (business case); `docs/01-theory.md` §2, §7 |
| `02_Access_Control_ABAC.md` | R | `docs/04-security-checks-reference.md`; `docs/01-theory.md` §7 |
| `03_Ingestion_Pipeline.md` | R | `docs/06-architecture-end-to-end.md` §1–2; `docs/05-src-modules-reference.md` (`ingest/*`); `docs/07-system-design-coverage-map.md` §4.2 |
| `04_Retrieval_Hybrid_Rerank.md` | R | `docs/06-architecture-end-to-end.md` §4–5; `docs/05-src-modules-reference.md` (`retrieval/*`); `README.md` (strategy table) |
| `05_The_Query_Graph.md` | R | `docs/06-architecture-end-to-end.md` §3, §5, §6; `docs/05-src-modules-reference.md` (`graph/*`, `llm/client.py`, `authz/rate_limit.py`) |
| `06_Output_Guardrails.md` | R | `docs/01-theory.md` §8; `docs/04-security-checks-reference.md` §6 |
| `07_Evaluation_Golden_Sets_Judges.md` | R | `docs/01-theory.md` §9; `docs/06-architecture-end-to-end.md` §7; `docs/05-src-modules-reference.md` (`evaluation/`); `README.md` (verified results); `docs/07` §4.5 |
| `08_Observability.md` | R | `docs/01-theory.md` §10; `docs/05-src-modules-reference.md` (`observability/`, `llm/client.py` → `Usage`) |
| `09_Module_Reference.md` | R | `docs/05-src-modules-reference.md`; `docs/06-architecture-end-to-end.md` §8 |
| `10_Coverage_Map.md` | R | `docs/07-system-design-coverage-map.md` |
| `project/` | P | the project root (minus `docs/`, the two `INTERVIEW_SCRIPT*.md`, `runs/`, `data/chroma/`, caches) |

## Module 05 · Agentic Workflow Platforms

All sources under `3. AI_Engineer_Interview_Preparation/Enterprise Agentic Workflow Automation Platform/`.

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_The_Problem_In_Plain_English.md` | R | `docs/01-theory.md` Part A, §B.1, §B.6; `README.md` |
| `02_Canonical_Events_And_Channels.md` | R | `docs/01-theory.md` §B.1–B.2; `docs/02-architecture-end-to-end.md` §1–2; `docs/03-src-modules-reference.md` |
| `03_Determinism_Over_Free_Text.md` | R | `docs/01-theory.md` §A.6, §B.3, §B.4; `docs/03-src-modules-reference.md`; `README.md` |
| `04_Durability_And_Idempotency.md` | R | `docs/02-architecture-end-to-end.md` §3; `docs/03-src-modules-reference.md` (`orchestrator.py`); `docs/01-theory.md` §B.5; `README.md` |
| `05_Approvals_Spend_Caps_Staged_Rollout.md` | R | `README.md` (guardrail rules, staged rollout); `docs/01-theory.md` §A.6–A.7, §B.4; `docs/03-src-modules-reference.md` |
| `06_Module_Reference.md` | R | `docs/03-src-modules-reference.md`; `docs/02-architecture-end-to-end.md` §4 |
| `07_Coverage_Map.md` | R | `docs/04-system-design-coverage-map.md` |
| `project/` | P | the project root (minus `docs/`, `INTERVIEW_SCRIPT.md`, `runs/`, caches) |

## Module 06 · Cross-Cutting Concerns

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_Identity_Secrets_Tenant_Fairness.md` | R | `Cross Cutting Preparation/01-identity-secrets-and-tenant-fairness.md` |
| `02_Observability_Standards_Failure_Patterns.md` | R | `Cross Cutting Preparation/02-observability-standards-and-failure-patterns.md`; `Enterprise Agentic Workflow Automation Platform/docs/05-security-tenancy-and-observability-gaps.md` §4 |
| `03_Caching_Streaming_CICD_BuildVsBuy.md` | R | `Cross Cutting Preparation/03-cost-latency-cicd-rigor-and-build-vs-buy.md` |
| `04_Prompt_Injection_Egress_Tenancy.md` | R | `Enterprise Agentic Workflow Automation Platform/docs/05-security-tenancy-and-observability-gaps.md` §1–3 |
| `05_Structured_Data_Routers_Connectors.md` | R | `Enterprise RAG Platform/docs/08-structured-data-and-connectors.md` |
| `06_Scaling_To_20M_Documents.md` | R | `Enterprise RAG Platform/docs/Scale_Optimization.md` |
| `07_Consolidated_Quick_Reference.md` | C | `Cross Cutting Preparation/Cross_Cutting_System_Design_Quick_Reference_v2.md` |

## Module 07 · Multi-Agent Systems

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_When_Multi_Agent_Is_Justified.md` | R | `Enterprise RAG Platform/docs/09-multi-agent-orchestration.md` §1; `Enterprise Agentic Workflow Automation Platform/docs/05-…-gaps.md` §5; `System_Design and Delivery/6. Customer Support AI Assistant Design.md` §5; `Star_Stories/AIA_Technical_Implementation_Flow.md` §3 |
| `02_Reference_Architecture_Handoffs.md` | R | `Enterprise RAG Platform/docs/09-multi-agent-orchestration.md` §2–3 |
| `03_Failure_Isolation_And_Evaluation.md` | R | same, §4–5 |
| `04_Case_Study_Research_Platform.md` | R | `Enteprise Multi-Agent AI Research Platform/ARCHITECTURE DIAGRAMS/LAYERS_EXPLAINED.md`; `CODE/README.md` |
| `05_Case_Study_Supervisor_To_Deep_Agent.md` | R | `4. FDE_Related_Preparation/Star_Stories/AIA_Technical_Implementation_Flow.md` |
| `diagrams/` | P | `Enteprise Multi-Agent AI Research Platform/ARCHITECTURE DIAGRAMS/*.mmd`, `architecture.html`, `platform-architecture.html`, `PNG DIAAGRAM.png` (renamed `platform-architecture.png`) |
| `reference_code/` | P | `Enteprise Multi-Agent AI Research Platform/CODE/` |

## Module 08 · AgentOps and Platform

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_Prompt_Versioning_Rollout_Rollback.md` | R | `Enterprise RAG Platform/docs/10-agent-ops-and-channels.md` §1 |
| `02_AgentOps_On_Databricks.md` | R | `Cross Cutting Preparation/04-agentops-on-databricks.md` |
| `03_Enterprise_RAG_On_Databricks.md` | R | `Enterprise RAG Platform/docs/03-theory-databricks.md`; `databricks/README.md` |
| `04_Multi_Channel_And_HITL_Escalation.md` | R | `Enterprise RAG Platform/docs/10-agent-ops-and-channels.md` §2–3 |
| `05_Red_Teaming.md` | R | `…/LAYERS_EXPLAINED.md` §8; `Enterprise RAG Platform/notebooks/02-hands-on-parts/part09-attacking-it.ipynb` (the attacks); `docs/04-security-checks-reference.md` §6 |
| `06_Infra_And_CICD.md` | R | `…/LAYERS_EXPLAINED.md` §9; `CODE/README.md`; `Enterprise RAG Platform/docs/03-theory-databricks.md` §12 |

## Module 09 · AI System Design Casebook

All sources under `4. FDE_Related_Preparation/System_Design and Delivery/` unless noted.

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_Enterprise_AI_Assistant.md` | R | `5. Enterprise AI Assistant Design.md` |
| `02_Customer_Support_Assistant.md` | R | `6. Customer Support AI Assistant Design.md` |
| `03_Coding_Assistant.md` | R | `7. AI Powered Coding Assistant Design.md` |
| `04_Recruiting_Platform.md` | R | `8. AI Powered Recruiting Platform Design.md` |
| `05_Logistics_Exception_Handling.md` | R | `AI Logistics Exception-Handling Assistant Design.md`; `Mock - AI Exception-Handling Assistant.md` |
| `06_Agentic_Coverage_Map.md` | R | `Agentic Coverage Map.html` |
| `whiteboard_scripts/01_Enterprise_RAG_With_Access_Control.md` | C | `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/INTERVIEW_SCRIPT.md` |
| `whiteboard_scripts/02_Enterprise_RAG_On_Databricks.md` | C | `…/Enterprise RAG Platform/INTERVIEW_SCRIPT_DATABRICKS.md` |
| `whiteboard_scripts/03_Agent_Platform_For_Non_Technical_Users.md` | C | `…/Enterprise Agentic Workflow Automation Platform/INTERVIEW_SCRIPT.md` |
| `whiteboard_scripts/04_Scoping_Doc_To_Deployed_Agent_In_Two_Weeks.md` | C | `4. FDE_Related_Preparation/Delivery Framework from Scoping to Delivery/INTERVIEW_SCRIPT.md` |

Not carried over: the `.html` twins of the markdown design docs in `System_Design and Delivery/` and its `index.html` (renderings of files already rewritten here).

## Module 10 · FDE Delivery and Operating Model

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_A_Day_In_The_Life.md` | R | `4. FDE_Related_Preparation/Senior_FDE_Day_to_Day.md` |
| `02_End_To_End_AI_Delivery_Six_Stages.md` | R | `System_Design and Delivery/9. Proj Delivery.md` |
| `03_Scoping_To_Production_In_Two_Weeks.md` | R | `Delivery Framework from Scoping to Delivery/docs/01-theory.md`; `docs/02-architecture-end-to-end.md`; `README.md` |
| `04_Gates_Risks_Metrics.md` | R | `…/docs/01-theory.md` §B.3–B.6; `docs/05-security-gate-depth-and-tenant-scale.md`; `README.md` |
| `05_Cross_Team_Collaboration.md` | R | `System_Design and Delivery/10. Cross Team Collaboration.md` |
| `06_Module_Reference.md` | R | `…/docs/03-src-modules-reference.md`; `docs/02-architecture-end-to-end.md` §4 |
| `07_Coverage_Map.md` | R | `…/docs/04-system-design-coverage-map.md`; `README.md` |
| `project/` | P | `4. FDE_Related_Preparation/Delivery Framework from Scoping to Delivery/` (minus `docs/`, `INTERVIEW_SCRIPT.md`, caches) |

## Module 11 · Telling the Story

| Handbook doc | Treatment | Source |
|---|---|---|
| `01_Deep_Dive_And_Conversational_Formats.md` | N | synthesised from the nine narratives in `4. FDE_Related_Preparation/Star_Stories/` |
| `02_Proof_vs_Cheat_Sheet_Honesty.md` | N | synthesised from the three coverage maps and the three project READMEs |
| `stories/*.md` (9 files) | C | `4. FDE_Related_Preparation/Star_Stories/*.md`, same filenames |
| `stories/STAR_Stories_Client_Engagements.html` | C | `Star_Stories/star_stories.html` |
| `stories/STAR_Stories_Technical_Build_Projects.html` | C | `Star_Stories/STAR Stories — Technical Build Projects.html` |

## Appendices

| Handbook doc | Treatment | Source |
|---|---|---|
| `A_Glossary.md` | N | — |
| `B_Source_Map.md` | N | — |
| `C_Interview_QA_Log.md` | C | `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/QA.md` |
| `D_Progress_Checklist.md` | N | — |

## Not included, and why

| Source | Reason |
|---|---|
| `Enterprise RAG Platform/docs/*.pdf` (two Medium articles) | Third-party reading, not the author's material |
| `Enteprise Multi-Agent AI Research Platform/EXCALIDRAW FILES/`, `Layered Architecture.mhtml`, `GITHUB LINK/`, `platform-architecture.visual-check.*` | Working files and renderings; the diagrams' `.mmd` sources are in Module 07 |
| `agent_tool_calling_demo/docs/DESIGN.md` | Fully absorbed into Module 03 docs 1–4 |
| The `.html` twins in `System_Design and Delivery/` | Renderings of markdown already rewritten in Module 09 |
| `.pytest_cache/`, `__pycache__/`, `runs/`, `data/chroma/` in every project | Generated artefacts; the labs regenerate them |
