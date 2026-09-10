# Reference Links — Courses Mapped to the AI Engineering Track

External course material, grouped by the roadmap phase whose content it covers.
Each course is listed **once**, under the phase it primarily serves; where it
meaningfully covers a second phase, that is noted in the *Also covers* column
rather than repeated as a separate entry.

**42 distinct courses.** Reorganized 2026-09-10 from a flat, partly duplicated
list, then extended the same day with 11 more — see [Audit notes](#audit-notes)
at the end for what changed and what could not be verified.

Most Udemy links carry the coupon `PMNVD2025`. Coupons expire; a dead coupon
does not mean a dead course — strip the `?couponCode=` query to reach the
course page.

---

## Phase 00 — Theory and Foundations

LLM internals, fine-tuning, the model landscape.

| Course | Also covers |
| --- | --- |
| [AI Engineer Core Track: LLM Engineering, RAG, QLoRA, Agents](https://www.udemy.com/course/llm-engineering-master-ai-and-large-language-models/?couponCode=PMNVD2025) | 04 RAG, 05 Agents — QLoRA/fine-tuning is the part unique to this phase |
| [OpenAI API Engineer](https://www.udemy.com/course/openai-engineer-api/?couponCode=PMNVD2025) | 06 Agent SDKs — raw provider API work; pairs with `Coding_Essentials_for_Agents/` |

---

## Phase 01 — LangChain Fundamentals

The framework itself: chains, LCEL, prompts, I/O.

| Course | Also covers |
| --- | --- |
| [LangChain in Action: Develop LLM-Powered Applications](https://www.udemy.com/course/langchain-in-action-develop-llm-powered-applications) | — |
| [The Complete LangChain Bootcamp: Build LLM-Powered Apps 2026](https://www.udemy.com/course/the-complete-langchain-bootcamp-build-llmpowered-apps-2026/?couponCode=PMNVD2025) | — |
| [Introduction to LangChain for Agentic AI](https://courses.analyticsvidhya.com/courses/take/introduction-to-langchain-for-agentic-ai/lessons/61748853-course-introduction) *(Analytics Vidhya)* | 05 Agents |
| [LangChain for Beginners: Building AI Agents, RAG & ChatBots](https://www.udemy.com/course/build-ai-agent-chatbot-rag-langchain-local-llm/?couponCode=PMNVD2025) | 04 RAG, 05 Agents |
| [Master LangChain v1 and Ollama — Chatbot, RAG and AI Agents](https://www.udemy.com/course/ollama-and-langchain/?couponCode=PMNVD2025) | 04 RAG — local-model track |

---

## Phase 02 — Prompt and Context Engineering

| Course | Also covers |
| --- | --- |
| [Context Engineering](https://www.udemy.com/course/context-engineering/?couponCode=PMNVD2025) | — **fills the previously empty `Context_Engineering/` track** |

---

## Phase 03 — LangGraph Fundamentals

Graph mechanics: state, nodes, routing, LangSmith.

| Course | Also covers |
| --- | --- |
| [The Complete LangChain, LangGraph & LangSmith Course](https://www.udemy.com/course/the-complete-langchain-langgraph-langsmith-course/?couponCode=PMNVD2025) | 01 LangChain, 12 Observability |
| [Complete Agentic AI Bootcamp With LangGraph and LangChain](https://www.udemy.com/course/complete-agentic-ai-bootcamp-with-langgraph-and-langchain/?couponCode=PMNVD2025) | 05 Agents |

---

## Phase 04 — Retrieval and RAG

Foundational RAG: indexing, chunking, embeddings, retrieval.

| Course | Also covers |
| --- | --- |
| [Hands-On RAG with LangChain: Build Real-World Projects](https://www.udemy.com/course/hands-on-rag-with-langchain-build-real-world-projects/?couponCode=PMNVD2025) | 13 Projects |
| [Ultimate RAG Bootcamp Using LangChain, LangGraph & LangSmith](https://www.udemy.com/course/ultimate-rag-bootcamp-using-langchainlanggraph-langsmith/?couponCode=PMNVD2025) | 08 Advanced RAG, 12 Observability |

---

## Phase 05 — AI Agent Fundamentals

Tool calling, agent loops, workflow patterns.

| Course | Also covers |
| --- | --- |
| [Building AI Agents with LangChain](https://courses.analyticsvidhya.com/courses/take/building-ai-agents-with-langchain/lessons/64877940-course-introduction) *(Analytics Vidhya)* | — |
| [LangChain 20 Drills: Build AI Agents with `create_agent` & RAG](https://www.udemy.com/course/langchain-20-drills-build-ai-agents-with-create_agent-rag/?couponCode=PMNVD2025) | 04 RAG — LangChain 1.x `create_agent` API |
| [AI Agents & Workflows: The Practical Guide](https://www.udemy.com/course/ai-agents-workflows-the-practical-guide/?couponCode=PMNVD2025) | 07 — workflow vs. agent patterns |
| [LangChain AI Agent Projects](https://www.udemy.com/course/langchain-ai-agent-projects/) | 13 Projects |
| [Build Autonomous AI Agents From Scratch With Python](https://www.udemy.com/course/build-autonomous-ai-agents-from-scratch-with-python/?couponCode=PMNVD2025) | — no-framework track, pairs with `Building_Agents_From_Scratch/` |

---

## Phase 07 — Advanced Agentic Systems

Multi-agent orchestration, deep agents, memory, evaluation.

| Course | Also covers |
| --- | --- |
| [Build AI Agents with LangChain v1: Deep Agents & Tools 2026](https://www.udemy.com/course/build-ai-agents-with-langchain-v1-deep-agents-tools-2026/?couponCode=PMNVD2025) | 01 — LangChain 1.x |
| [Deep Agent — Multi-Agent RAG with Gemini and LangChain](https://www.udemy.com/course/deep-agent/?couponCode=PMNVD2025) | 08 Advanced RAG |
| [Multi-Agents with LangChain & LangGraph](https://www.udemy.com/course/multi-agents-with-langchain-langgraph/?couponCode=PMNVD2025) | 03 LangGraph |
| [Agentic AI Architectures with Patterns, Frameworks and MCP](https://www.udemy.com/course/agentic-ai-architectures-with-patterns-frameworks-and-mcp/?couponCode=PMNVD2025) | **09 Protocols** — MCP |
| [Agentic Harness Engineering](https://www.udemy.com/course/agentic-harness-engineering/?couponCode=PMNVD2025) | — maps directly to `Deep_Agents_and_Harness_Engineering/` |

### Evaluation and eval harnesses

| Course | Also covers |
| --- | --- |
| [Testing AI Systems with DeepEval: AI Agents, Chatbots & RAG](https://www.udemy.com/course/rag-llm-evaluation-ai-test/?couponCode=PMNVD2025) | 04/08 RAG evaluation |
| [AI Agents, RAG & LLM Evals for Beginners: DeepEval & RAGAS](https://www.udemy.com/course/ai-testing-deepeval-ragas-ollama/?couponCode=PMNVD2025) | 04/08 RAG evaluation |
| [AI Testing with DeepEval: Chatbot, RAG, Agent & MCP](https://www.udemy.com/course/ai-testing-deepeval-chatbot-rag-agent-mcp/?couponCode=PMNVD2025) | **09 Protocols** — the only MCP *testing* coverage |
| [Evaluation for LLM Applications](https://www.udemy.com/course/evaluation-for-llm-applications/?couponCode=PMNVD2025) | 12 — evaluation as a production discipline |
| [AI Evals: Test LLM Apps, RAG and Agents Like an Engineer](https://www.udemy.com/course/ai-evals-test-llm-apps-rag-and-agents-like-an-engineer/?couponCode=PMNVD2025) | 04/08 RAG evaluation |

---

## Phase 08 — Advanced RAG

Agentic/self-correcting RAG, GraphRAG, production RAG architecture.

| Course | Also covers |
| --- | --- |
| [Advanced RAG Engineering: Build Production-Ready Enterprise](https://www.udemy.com/course/advanced-rag-engineering-build-production-ready-enterprise/?couponCode=PMNVD2025) | 12 Production |
| [Supercharge AI with Knowledge Graphs: RAG System Mastery](https://www.udemy.com/course/knowledge-graphs-rag/?couponCode=PMNVD2025) | — maps to `08_Advanced_RAG/GraphRAG/` |
| [RAG Strategy & Execution: Build Enterprise Knowledge Systems](https://www.udemy.com/course/rag-strategy-execution-build-enterprise-knowledge-systems/) | 14 Handbook — strategy/architecture, lighter on code |

---

## Phase 11 — Claude Code and AI Coding Tools

| Course | Also covers |
| --- | --- |
| [OpenCode Beginner to Pro: Agentic Coding with Free AI Models](https://www.udemy.com/course/opencode/?couponCode=PMNVD2025) | — the only entry for this phase |

---

## Phase 12 — Production and Observability

LLMOps, tracing, cost, guardrails, security.

| Course | Also covers |
| --- | --- |
| [Production AI Agents with LangChain + LangGraph (2026)](https://www.udemy.com/course/production-ai-agents/?couponCode=PMNVD2025) | 07 Agents |
| [LLM Observability and Cost Management: Langfuse, Monitoring](https://www.udemy.com/course/llm-observability-cost/?couponCode=PMNVD2025) | — fills the LangFuse gap in `Tracing_and_Observability/` |
| [LLM Token Optimization: Optimize Cost, Speed & Performance](https://www.udemy.com/course/llm-token-optimization-optimize-cost-speed-performance/?couponCode=PMNVD2025) | — maps to `Cost_Monitoring/` |
| [AI Security Bootcamp: Guardrails, LLM Gateways, Observability](https://www.udemy.com/course/ai-security-bootcamp-guardrailsllm-gatewaysobservability/?couponCode=PMNVD2025) | — maps to `Safety_and_Alignment/` + the planned `Security_and_Compliance/` |
| [AI Architect: Enterprise AI System Design](https://www.udemy.com/course/ai-architect-rag-agents-llmops-security/?couponCode=PMNVD2025) | 08 RAG, 14 Handbook — LLMOps + security |
| [LLM Token Optimization: Enterprise Cost & Performance](https://www.udemy.com/course/llm-token-optimization-enterprise-cost-performance/?couponCode=PMNVD2025) | — see the near-duplicate note in [Audit notes](#audit-notes) |
| [AI / LLM Deployment Engineer](https://www.udemy.com/course/ai-llm-deployment-engineer/?couponCode=PMNVD2025) | — **fills the previously empty `DevOps_and_Deployment/` track** |
| [AI Hallucinations: Management & Fact-Checking in LLMs](https://www.udemy.com/course/ai-hallucinations-management-fact-checking-in-llms/?couponCode=PMNVD2025) | 07 Evaluation, 08 — grounding and self-correcting RAG; maps to `Safety_and_Alignment/` |
| [Enterprise Agentic AI Architecture: Design to Production](https://www.udemy.com/course/enterprise-agentic-ai-architecture-design-to-production/?couponCode=PMNVD2025) | 07 Agents, 14 Handbook |

---

## Phase 13/14 — Projects and Handbook

| Course | Also covers |
| --- | --- |
| [The Complete Full Stack AI Engineering Bootcamp](https://www.udemy.com/course/full-stack-ai-engineering-bootcamp/?couponCode=PMNVD2025) | end-to-end build; pairs with the capstones in `13_Projects/` |
| [Become an LLM & Agentic AI Engineer — 14-Day Bootcamp 2025](https://www.udemy.com/course/become-an-llm-agentic-ai-engineer-14-day-bootcamp-2025/?couponCode=PMNVD2025) | spans 00–12; a full-track bootcamp rather than a phase-specific course |

---

## Coverage gaps

Phases in the track with **no course in this list**:

| Phase | Status |
| --- | --- |
| 06 — Agent SDKs (Google ADK, OpenAI Agents SDK) | Only adjacent — *OpenAI API Engineer* covers the raw API, not the Agents SDK. No Google ADK coverage. |
| 09 — Agent Protocols (MCP, ACP, A2A) | MCP appears in two courses (*Agentic AI Architectures*, *AI Testing with DeepEval*), neither MCP-first. **No ACP or A2A coverage at all.** |
| 10 — Alternative Frameworks (CrewAI, AutoGen, DSPy, PydanticAI) | **No coverage** — the single largest gap. Phase 10 has built content in the repo but nothing external behind it. |
| 15 / 16 — FDE prep, interview prep | No coverage. |

**Closed by the 2026-09-10 additions:** Phase 02 (*Context Engineering*),
Phase 12's `DevOps_and_Deployment/` (*AI / LLM Deployment Engineer*), and
Phase 07's harness track (*Agentic Harness Engineering*).

The list remains LangChain-weighted, though less so than before: **25 of 42**
courses are LangChain- or LangGraph-based, down from 24 of 31. The 11 additions
were almost all framework-agnostic — evaluation, cost, deployment, safety.

---

## Pending topics

Study queue. `~~struck through~~` = done.

### Agents — Krish Naik Agent Course

1. End-to-End Agent Project — ***10th Sep***
2. ~~LLM Structured Output using Pydantic / TypedDict — 9th Sep~~
3. ~~Human in the Loop (Agentic Project) — 10th Sep~~
4. Guardrails in LangChain — ***10th Sep***
5. Agent Evaluation — ***10th Sep***
6. ~~Retry, Backoff and Failure/Error Handling in Agentic Applications — 10th Sep~~
7. ~~Usage Cap and Unlimited-Run Handling in LangGraph — 10th Sep~~
8. ~~Model Fallback and Router — 10th Sep~~

### RAG — Krish Naik RAG Course

9. ~~Advanced Chunking — 9th Sep~~
10. ~~Agentic RAG — 9th Sep~~
11. ~~Autonomous RAG — 9th Sep~~
12. ~~Multi-Agent RAG — 9th Sep~~
13. ~~Corrective RAG — 9th Sep~~
14. ~~Adaptive RAG — 9th Sep~~
15. ~~Hybrid Search — 9th Sep~~
16. Different Streaming Techniques — ***pending***
17. RAG With Memory — ***10th Sep***
18. RAG Project — ***10th Sep***

> Original items 12–16 repeated items 6–11 verbatim and have been merged;
> item 12's "Different Streaming Technique" was the only unique content in that
> run and is preserved above as item 16.

---

## Audit notes

### 2026-09-10 — 11 courses added

16 URLs supplied → 14 distinct → 3 already present → **11 new**.

Repeated inside the supplied list: `ai-evals-test-llm-apps-rag-and-agents-like-an-engineer` (2×), `agentic-harness-engineering` (2×).

Already in the file, so not re-added: `llm-engineering-master-ai-and-large-language-models` (Phase 00), `the-complete-langchain-langgraph-langsmith-course` (Phase 03), `multi-agents-with-langchain-langgraph` (Phase 07).

**Two pairs to confirm — similar names, different slugs, kept as separate courses:**

| New | Existing |
| --- | --- |
| `llm-token-optimization-enterprise-cost-performance` | `llm-token-optimization-optimize-cost-speed-performance` |
| `ai-testing-deepeval-chatbot-rag-agent-mcp` | `ai-testing-deepeval-ragas-ollama` |

Each pair looks like two editions or two courses from the same author rather than one course re-slugged, but that could not be checked (see the verification note below). If either pair is really one course, delete the older entry.

**Titles for all 11 are derived from their URL slugs, not read from the course pages** — the pages are unreachable to automated requests. Treat them as approximations of the real titles.

### 2026-09-10 — initial reorganization

**Duplicates removed** — 58 URL occurrences collapsed to 31 distinct courses:

| Course | Appeared |
| --- | --- |
| `langchain-ai-agent-projects` | **25×** — a self-nested markdown link that had recursively swallowed itself |
| `production-ai-agents` | 3× |
| `ultimate-rag-bootcamp-...` | 2× |
| `deep-agent` | 2× |

**Malformed links repaired**

- *OpenCode Beginner to Pro* had an empty target — `[title]([www.udemy.com/course/opencode/...]())`. The URL was recoverable from the text and is now a working link. It had **no `https://` scheme**, so it was invisible to any link checker.
- *LangChain AI Agent Projects* — the 25× nested link was unparseable; rebuilt as a single clean entry.
- Seven entries were bare URLs with no title; titles are now derived from their slugs.

**Entries that had no link at all** — carried over as text, unresolved:

- *GenAI Application Architecture — Scalable and Secure AI Design* → belongs in Phase 12/14 once a link exists.
- *LLM Obeservibility and Cost Management* (sic) → appears to be a duplicate of *LLM Observability and Cost Management: Langfuse* in Phase 12; dropped as a duplicate rather than kept as a broken entry. Restore it if it was meant to be a different course.

**What was NOT verified: whether any of these courses still exist.**
Udemy returns HTTP 403 to automated requests — including for a deliberately
fabricated course slug used as a control — so a link checker cannot distinguish
a live course from a deleted one. Every URL here is structurally valid and
correctly formed; none has been confirmed to resolve. The two Analytics Vidhya
links point at *lesson* URLs inside a course, which typically require
enrolment.

**Phase numbering** follows the directories actually on disk (`00_`–`16_`),
which differ from the 13-phase scheme described in `CLAUDE.md`.
