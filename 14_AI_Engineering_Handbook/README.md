# The AI Engineering Handbook

**From first principles to production-grade agentic systems — and the Forward Deployed Engineer who ships them.**

This handbook turns a working body of interview-preparation material — three fully built platform projects, a from-scratch agent loop, a system-design framework, a delivery operating model, and a set of real client narratives — into one ordered curriculum. You can start with no knowledge of RAG or agents and finish able to design, build, secure, evaluate, operate and *explain* an enterprise AI system under interview pressure.

Everything here is grounded in code that runs. Where a module teaches a concept, the `project/` folder next to it contains the implementation, the notebooks, and the tests.

---

## The four levels

| Level | Who you are when you start | What you can do when you finish | Modules |
|---|---|---|---|
| 🟢 **1 · Foundations** | You know Python and have used an LLM API. | Explain RAG and agents from first principles; write a tool-calling loop from scratch and in LangGraph; run a structured system-design conversation. | 00 · 01 · 02 |
| 🟡 **2 · Building Production Systems** | You can build a demo. | Build agents that survive retries, crashes and bad tools; build an enterprise RAG system with attribute-based access control; build a deterministic agent-workflow platform for non-technical users. | 03 · 04 · 05 |
| 🟠 **3 · Scale, Security, Operations** | You can build one system for one customer. | Reason about identity, tenancy, observability, cost, prompt injection, 20-million-document scale, multi-agent orchestration and AgentOps — with real tools named. | 06 · 07 · 08 |
| 🔴 **4 · Design Mastery & the FDE Role** | You can build and operate. | Run a 60-minute AI system-design interview on any prompt; take a customer from scoping doc to production in two weeks; tell the story of what you built with honesty and precision. | 09 · 10 · 11 |

---

## Curriculum

### 🟢 Level 1 — Foundations

| Module | What it teaches | Docs | Hands-on |
|---|---|---|---|
| [00 · Orientation](00_Orientation/README.md) | How to use this handbook, the three roles it prepares you for, and the habit that underlies all of them: ask before you architect. | 3 | — |
| [01 · LLM Systems Foundations](01_LLM_Systems_Foundations/README.md) | What RAG actually is; chunking, dense vs lexical retrieval, fusion, reranking; what an agent actually is; the ReAct loop coded from scratch and then in LangGraph. | 5 | `project/` — 4 notebooks, 12 tests, zero API keys needed |
| [02 · System Design Fundamentals](02_System_Design_Fundamentals/README.md) | The 12-part framework, the 15 principles, monolith vs microservices, a worked example, and the 60-minute whiteboard method used by every script in this handbook. | 5 | — |

### 🟡 Level 2 — Building Production Systems

| Module | What it teaches | Docs | Hands-on |
|---|---|---|---|
| [03 · Robust Agents](03_Robust_Agents/README.md) | Retry, fallback, memoization, confirmation gates, disambiguation; state and memory across turns; parallel vs sequential tool calls; per-call observability; the eight guard checks. | 5 | reuses Module 01 `project/` |
| [04 · Enterprise RAG](04_Enterprise_RAG/README.md) | The Meridian Assist project as a course: ABAC access control, ingestion, hybrid retrieval, the LangGraph query pipeline, output guardrails, evaluation with golden sets and judges, observability. | 10 | `project/` — 11-part notebook series, corpus, tests, eval harness |
| [05 · Agentic Workflow Platforms](05_Agentic_Workflow_Platforms/README.md) | The Agent Platform project as a course: canonical events and channel adapters, deterministic routing, durable and idempotent orchestration, approvals, spend caps and staged rollout. | 7 | `project/` — notebook, demo scripts, tests |

### 🟠 Level 3 — Scale, Security, Operations

| Module | What it teaches | Docs | Hands-on |
|---|---|---|---|
| [06 · Cross-Cutting Concerns](06_Cross_Cutting_Concerns/README.md) | Identity and secrets, tenant fairness, observability standards and failure patterns, semantic caching and streaming, CI/CD rigor, build vs buy, prompt injection and egress, structured-data routing, scaling to 20M documents. | 7 | — |
| [07 · Multi-Agent Systems](07_Multi_Agent_Systems/README.md) | When multi-agent is justified (and when it is not), handoffs, failure isolation, evaluation; two case studies — a nine-layer research platform on AWS and a supervisor-to-deep-agent evolution. | 5 | `reference_code/` (deployed AWS platform), `diagrams/` |
| [08 · AgentOps & Platform](08_AgentOps_And_Platform/README.md) | Prompt versioning, canary rollout and rollback; AgentOps on Databricks with MLflow and Unity Catalog; Enterprise RAG on Databricks; multi-channel delivery and human escalation; red teaming; infrastructure and CI/CD. | 6 | Module 04 `project/databricks/`, `project/notebooks/04-*` |

### 🔴 Level 4 — Design Mastery & the FDE Role

| Module | What it teaches | Docs | Hands-on |
|---|---|---|---|
| [09 · AI System Design Casebook](09_AI_System_Design_Casebook/README.md) | Five worked AI system designs (enterprise assistant, customer support, coding assistant, recruiting, logistics exception handling), the agentic coverage map, and four full 60-minute whiteboard scripts. | 6 + 4 scripts | — |
| [10 · FDE Delivery & Operating Model](10_FDE_Delivery_Operating_Model/README.md) | What an FDE does all day; the six-stage AI delivery framework; scoping-doc to production in two weeks as a gate-enforcing state machine; gates, risks and metrics; cross-team collaboration. | 7 | `project/` — delivery pipeline engine, gates, tests |
| [11 · Telling the Story](11_Telling_The_Story/README.md) | How to narrate a build in 15–20 minutes or in open conversation; the proof-vs-cheat-sheet honesty discipline; nine worked narratives from real engagements as templates. | 2 + 9 stories | — |
| [99 · Appendices](99_Appendices/README.md) | Glossary, source map (every handbook doc → its original file), interview Q&A log, progress checklist. | 4 | — |

---

## How to read it

**Linear (recommended the first time).** Modules are numbered in dependency order. Each module's README lists its prerequisites, the reading order, and estimated time.

**By role.** If you already know where you are heading:

| Track | Path |
|---|---|
| **AI Engineer** (build RAG and agent systems) | 00 → 01 → 02 → 03 → 04 → 06 → 08 → 09 |
| **Agentic Systems Designer** (platforms, orchestration, safety) | 00 → 01 → 03 → 05 → 06 → 07 → 08 → 09 |
| **Forward Deployed Engineer** (customer-facing delivery) | 00 → 02 → 04 → 05 → 06 → 09 → 10 → 11 |

**By question.** Appendix A (glossary) and Appendix B (source map) index every concept and every document.

## Conventions

Every document opens with the same header block:

> **Level** 🟢 · **Module** 01 · **Doc** 1 of 5 · **Time** ~20 min
> **Prerequisites:** what you should have read first
> **Source material:** the original file(s) this was built from

and closes with a **Checkpoint** — questions you should be able to answer before moving on — and a **Next →** pointer.

Three recurring sections appear throughout:

- **Why this matters** — the problem the concept solves, before the concept itself.
- **Interview lens** — how the concept is tested in a design round and the sentence that carries it.
- **In the code** — where the concept is implemented in the module's `project/` folder.

## Running the labs

Each `project/` folder is self-contained with its own `requirements.txt`. From the handbook root:

```bash
# Module 01 — no API key required
cd 01_LLM_Systems_Foundations/project && pip install -r requirements.txt && python -m pytest -q

# Module 04 — needs OPENAI_API_KEY in a .env at the project root
cd 04_Enterprise_RAG/project && pip install -r requirements.txt && python scripts/ingest.py

# Module 05 and Module 10 — no API key required
cd 05_Agentic_Workflow_Platforms/project && python -m pytest -q
cd 10_FDE_Delivery_Operating_Model/project && python -m pytest -q
```

Module 07's `reference_code/` is a deployed AWS platform (Terraform, ECS, Bedrock, TensorZero, PyRIT); it is included for reading, not for local execution.

## Where this came from

The handbook was assembled from three source folders in this repository, which remain untouched:

- `3. AI_Engineer_Interview_Preparation/` — the three platform projects and the cross-cutting notes
- `4. FDE_Related_Preparation/` — system design, delivery framework, STAR stories, day-in-the-life
- `1. Company_Wise_Preparation/2. DevRev/Coding_Round/agent_tool_calling_demo/` — the tool-calling loop

Appendix B maps every handbook document back to its source. The handbook is designed to grow: new modules slot into the level structure, and the source map records provenance as material is added.
