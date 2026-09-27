# Naming audit and recommended taxonomy

## Verdict

The individual names are mostly understandable, but the naming system is not yet coherent. It mixes topics, page formats, interview stages, and product collections at the same level. The most serious issue is that “module” refers to both the 15-item preparation roadmap and the separate 18-item Last-Day sequence.

Visible labels can be corrected without changing existing URLs, route IDs, storage keys, or source filenames.

## Naming principles

1. Use the top-level navigation for learning modes, not implementation structure.
2. Reserve “module” for a real instructional unit with a defined outcome.
3. Use “practice,” “case study,” “review,” and “guide” as content-type labels.
4. Prefer concrete topic names over internal production terms such as “standalone.”
5. Qualify duplicate scenario names by content type in search and breadcrumbs.
6. Use one editorial dialect. The existing interface predominantly uses British English (`practise`, `behavioural`, `judgement`, `prioritise`, `organisation`), so retain that style in editorial copy while preserving standard API/product terminology where spelling is fixed.
7. Use “and” in page and section titles. Reserve `&` for compact metadata where space is genuinely constrained.

## Global product and navigation

| Current | Recommended | Reason |
| --- | --- | --- |
| Forward Deployed | Forward Deployed | The brand is distinctive; pair it with a descriptor on first contact |
| The end-to-end FDE interview prep system | FDE interview practice and system-design review | More concrete and easier to understand without knowing the product |
| Modules | Practice | The destination contains exercises, not a complete module catalogue |
| FDE Case Studies | Case Studies | FDE is already established by the site context |
| Last-Day Prep | Last-Day Review | Sounds intentional and professional while keeping the same purpose |
| How to use | How It Works | Clear global-navigation label; the page title may remain “How to use this site” |
| The preparation path | Explore by learning mode | The existing list mixes topics, activities, libraries, and interview stages |
| Night-before cram pass | Focused final review | Keeps urgency without sounding improvised |

Recommended primary navigation:

**Practice · Case Studies · Last-Day Review · How It Works**

## Main application sections

| Current | Recommended visible name |
| --- | --- |
| Module 01 — Customer Discovery & Decomposition | Customer Discovery and Problem Decomposition |
| Module 14 — Behavioural & Leadership Round | Behavioural and Leadership Practice |
| Module 15 — FDE Case Studies | Case Studies |

The numbers can remain in route IDs and internal metadata. Do not make `01`, `14`, and `15` the primary visible identity while twelve intermediate modules are unavailable. If roadmap numbers remain visible, present them under a clearly labelled “15-part curriculum roadmap,” separate from the live learning modes.

The planned roadmap currently mixes several kinds of item:

- **Topics:** Architecture and System Design; Enterprise Data, RAG and Agents; Evaluation and Security.
- **Interview activities:** Coding Practice; Mock Interviews; Readiness Assessment.
- **Libraries and projects:** Case Study Library; Hands-On Labs.
- **Career preparation:** Answer Language; Career and Portfolio Assets.

Group these under phases or learning modes before treating them as one numbered list.

## Practice track names

| Current | Recommended |
| --- | --- |
| Core Scenarios | Discovery Foundations |
| System Design Scenarios | System Design Practice |
| Hiring Manager Round | Hiring Manager Questions |
| Leadership Principles | Leadership Principle Questions |

“Core” does not tell the user what skill is being practised, and “round” describes the interview schedule rather than the content.

## Case-study track names

| Current | Recommended |
| --- | --- |
| Knowledge & Retrieval | Knowledge and Retrieval |
| Agents That Act | Tool-Using and Action-Taking Agents |
| Platforms & Scale | AI Platforms and Scale |
| Delivery, Evaluation & Operations | Delivery, Evaluation, and Operations |
| Model Development | Model Development and Post-Training |
| Standalone Designs | Additional System Designs |
| Judgement & Decomposition | Product Judgement and Problem Decomposition |

“Standalone Designs” describes how files are organised, not what users will learn. “Agents That Act” is memorable but less precise than the rest of the taxonomy.

## Case-study document labels

| Current | Recommended |
| --- | --- |
| Main | Interview Guide |
| Deep Dive | Technical Deep Dive |
| Cheat Sheet | Quick Review |
| Full Pack | Sources and Full Design |
| Worksheet | Practice Worksheet |
| Answer Key | Model Answer |
| Tutorial V2 | Tutorial |
| Tutorial V1 | Archived Tutorial V1 |
| Tutorial V1 (Uncondensed) | Original Full Tutorial |
| Casebook | Interview Casebook |
| Full Design | Reference Design |
| Guide | Interview Guide |
| Interview Template | Answer Template |
| Framework Overview | 12-Part Framework |

Archived tutorial versions should ultimately leave the primary tab row. Renaming them is an interim measure, not the final information architecture.

## Last-Day Review collection

Use **“Review 01” through “Review 18”** instead of **“Module 1” through “Module 18.”** This removes the collision with the 15-part roadmap while keeping the useful sequence.

| Current | Recommended |
| --- | --- |
| FDE Problem Decomposition | Problem Framing and Decomposition |
| Functional Requirements | Functional Requirements |
| Non-Functional Requirements | Quality Attributes and Non-Functional Requirements |
| Core Architecture Building Blocks | Core Architecture Components |
| RAG & Enterprise Data | Retrieval-Augmented Generation and Enterprise Data |
| Agentic Architecture | Agent Architecture and Orchestration |
| Tools, Actions & Enterprise Integration | Tools, Actions, and Enterprise Integrations |
| Guardrails, Policy & Human Approval | Guardrails, Policy, and Human Approval |
| Scaling AI Systems | Scaling AI Systems |
| Latency Optimization | Latency and Performance |
| Cost Optimization | Cost and Efficiency |
| Reliability & Failure Handling | Reliability and Failure Recovery |
| AI Evaluation | Evaluating AI Systems |
| Release & Change Management | Release and Change Management |
| Observability & Production Operations | Observability and Production Operations |
| Security & Enterprise Multi-Tenancy | Security, Tenant Isolation, and Multi-Tenancy |
| Trade-Off Thinking | Architecture Trade-Offs |
| End-to-End FDE Interview Execution | End-to-End Interview Walkthrough |

Supporting document names:

| Current | Recommended |
| --- | --- |
| Concise Interview Module | Interview Review |
| One-Page Memory Card | One-Page Recall Card |
| Trigger → Concept Cheat Sheet | Trigger-to-Concept Quick Reference |

The current technical meanings remain intact. The proposed titles reduce jargon, spell out important concepts on first contact, and use parallel noun phrases.

## Duplicate case titles

Five technical scenarios appear in both interactive Practice and the Case Study library:

- Secure Multi-Tenant AI Platform
- AI System for an Air-Gapped Environment
- Reliable Workflow Orchestration System
- Configurable Platform for Customer-Specific Workflows
- Enterprise Chatbot Platform

Keep the scenario name stable and qualify its presentation:

- **Enterprise Chatbot Platform · Practice Worksheet**
- **Enterprise Chatbot Platform · Case Study**

Apply the qualifier in search results, breadcrumbs, browser titles, recent-progress lists, and previous/next navigation. Do not encode the qualifier into the scenario’s canonical subject title.

## Case-title cleanup rules

- Preserve established acronyms such as RAG, LLM, SRE, API, SLO, and SLA, but expand less familiar acronyms in the introduction.
- Use consistent compound forms: `multi-tenant`, `air-gapped`, `customer-facing`, `tool-using`, `real-time`, and `post-training`.
- Use title case only for page titles; use sentence case for controls, metadata, and descriptions.
- Avoid mixing “assistant,” “copilot,” “agent,” and “automation” when they describe the same autonomy level. Choose the noun based on behaviour: assistant recommends, copilot collaborates, agent selects actions within bounds, automation follows a defined workflow.
- Retain customer/problem specificity where it distinguishes similar cases.

## Migration rule

Change visible labels and metadata first. Preserve current paths, source filenames, anchors, and local-storage identifiers. Where a future URL change is justified, add explicit redirects and retain canonical links so existing bookmarks continue to work.
