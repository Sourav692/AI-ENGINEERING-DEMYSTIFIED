# FDE AI System Design — Interview Learning Roadmap

> **Goal:** Build a reusable problem-decomposition and system-design framework for AI/Agentic FDE interviews.
>
> This is **not** intended to be a deep theoretical system-design course. The focus is:
>
> - What should I ask?
> - What requirement does this create?
> - What component/pattern solves it?
> - Why do I need that component?
> - What trade-off does it introduce?

---

# 0. The FDE Interview Mental Model

For almost any vague AI/Agentic problem:

```text
Vague Customer Problem
        ↓
Discovery
        ↓
Functional + Non-Functional Requirements
        ↓
Happy-Path Architecture
        ↓
Data / RAG / Agent Flow
        ↓
Actions + Safety
        ↓
Scale
        ↓
Latency + Cost
        ↓
Failures + Reliability
        ↓
Evaluation
        ↓
Release
        ↓
Observability + Operations
        ↓
Trade-offs
```

The key principle throughout the interview:

```text
Customer Need
      ↓
Requirement
      ↓
Constraint / Problem
      ↓
Architecture Decision
      ↓
Trade-off
```

Do **not** start with technology.

---

# Module 1 — FDE Problem Decomposition

## Goal

Take a vague customer request and turn it into a well-defined engineering problem.

## Topics

### Business Problem

- What problem are we solving?
- Why does the customer want AI?
- What business outcome matters?
- What happens if we do nothing?

### Current Workflow

- Existing human workflow
- Existing systems
- Manual steps
- Bottlenecks
- Current failure points

### Users & Personas

- End customers
- Internal employees
- Administrators
- Human reviewers

### Scale

- Number of users
- Requests/day
- Peak traffic
- Concurrency
- Expected growth

### Data

- Structured vs unstructured
- Static vs real-time
- Data sources
- Freshness
- Permissions

### AI Autonomy

```text
Answer
   ↓
Recommend
   ↓
Take Action
   ↓
Take High-Risk Action
```

### Success Criteria

- Business KPIs
- AI quality
- Task success
- Latency
- Reliability
- Cost

## Discovery Mental Model

```text
WHY
Business problem

TODAY
Current workflow

WHO
Users

HOW MUCH
Scale

WHAT DATA
Knowledge + live systems

HOW FAR CAN AI GO
Answer → Recommend → Act

SUCCESS
How do we measure it?
```

## 🎯 Practice Questions

1. A bank says, **"We want an AI agent for customer support."** What are the first 5–7 questions you would ask before discussing architecture?
2. A logistics customer says, **"Our operations team spends too much time resolving shipment exceptions."** How would you understand the current workflow before proposing AI?
3. The customer immediately says, **"We want a multi-agent architecture."** How would you determine whether multi-agent is actually required?
4. A customer says they want to **reduce support cost by 30%**. What additional success metrics would you define before designing the system?
5. What questions would you ask to determine whether the AI should **answer, recommend, or autonomously act**?

---

# Module 2 — Functional Requirements

## Goal

Translate discovery into:

> **What must the system do?**

## Topics

### Understand

- Accept user requests
- Understand intent
- Support required modalities

### Maintain Context

- Session context
- Conversation history
- Workflow state

### Retrieve

- Enterprise knowledge
- Relevant context
- Permission-aware information

### Route

- RAG
- Agent
- Tool
- Workflow
- Human

### Reason

- Answer
- Recommendation
- Plan
- Decision proposal

### Use Tools

- APIs
- Databases
- CRM
- ERP
- Internal systems

### Act

- Update tickets
- Cancel orders
- Issue refunds
- Create incidents

### Escalate

- Low confidence
- High risk
- Policy requirement
- Tool failure

### Audit & Feedback

- Decisions
- Evidence
- Actions
- Approvals
- User feedback

## Functional Mental Model

```text
Understand
    ↓
Retrieve
    ↓
Route
    ↓
Reason
    ↓
Tool
    ↓
Act
    ↓
Escalate
    ↓
Audit
```

## 🎯 Practice Questions

1. For an **enterprise customer-support agent**, define 6–8 functional requirements.
2. A support agent must answer policy questions, check order status, and issue eligible refunds. Break these into functional requirements.
3. Which requirements would tell you that the system needs **conversation state**?
4. How would functional requirements change if the system moves from **answer-only** to **taking actions**?
5. When should **human escalation** be considered a functional requirement?

---

# Module 3 — Non-Functional Requirements

## Goal

Define:

> **How well must the system work?**

## Topics

- Scalability
- Latency
- Reliability
- AI quality
- Security
- Safety
- Cost
- Observability
- Auditability

## NFR Mental Model

```text
Scale
Latency
Reliability
Quality
Security
Safety
Cost
Observability
Auditability
```

## 🎯 Practice Questions

1. The customer says, **"The system should be fast."** How would you turn that into a measurable NFR?
2. The system serves **50 enterprise customers and 100K total users**. Which NFRs become especially important?
3. A refund agent handles financial actions. Which NFRs would you prioritize and why?
4. How would the NFRs differ between a **real-time voice agent** and a **10-minute deep-research agent**?
5. What AI-quality NFRs would you define beyond traditional uptime and latency?

---

# Module 4 — Core Architecture Building Blocks

## Goal

Know the reusable building blocks and, more importantly, **what requirement triggers each one**.

## Topics

### API Gateway

```text
User
 ↓
API Gateway
 ↓
AI Application
```

Handles:

- Authentication
- Authorization
- Tenant context
- Rate limits
- Quotas
- Request validation

### Model Gateway

```text
AI Application
      ↓
Model Gateway
      ↓
Model Providers
```

Handles:

- Model routing
- Provider abstraction
- Retry/fallback
- Provider limits
- Token/cost tracking

### Router

- Intent routing
- Agent routing
- Tool routing

### Orchestrator

- Workflow state
- Branching
- Tool calls
- Retry
- Checkpoints

### State Store

- Session state
- Workflow state
- Approval state

### Cache

- Response
- Semantic
- Retrieval
- Tool result

### Queue / Event Bus

- Async work
- Bursts
- Background jobs
- Long-running workflows

## Component Selection Rule

```text
What does it do?
      ↓
Why do I need it?
      ↓
Which requirement triggered it?
```

## 🎯 Practice Questions

1. Explain the difference between an **API Gateway and Model Gateway** in 30 seconds.
2. When would you introduce an **orchestrator** rather than putting everything inside one agent?
3. A customer has three LLM providers and wants automatic fallback. Which component owns this responsibility?
4. When would you add a **queue** rather than processing the request synchronously?
5. The interviewer points to one of your architecture boxes and asks, **"Why do you need this?"** How would you justify components based on requirements rather than technology preference?

---

# Module 5 — RAG & Enterprise Data

## Goal

Design practical enterprise RAG without unnecessary theoretical depth.

## Core Flow

```text
Source
 ↓
Parse
 ↓
Chunk
 ↓
Embed
 ↓
Index

Question
 ↓
Permission Filter
 ↓
Search
 ↓
Rerank
 ↓
Context
 ↓
LLM
```

## Topics

- Chunking
- Embeddings
- Vector search
- Keyword/hybrid search
- Metadata filtering
- Reranking
- Recall
- Precision
- Permission-aware retrieval
- Static vs live data
- Groundedness

## 🎯 Practice Questions

1. Your RAG system frequently **fails to retrieve the correct document**. What would you investigate?
2. It retrieves the correct document but also returns **many irrelevant chunks**. What problem is this and how would you improve it?
3. Why should **current order status** normally come from an API instead of RAG?
4. Two employees have different document permissions. How would you prevent unauthorized information from entering the LLM context?
5. The customer says, **"The model is hallucinating."** What parts of the RAG pipeline would you investigate before simply changing the model?

---

# Module 6 — Agentic Architecture

## Goal

Know when agents are useful and how to prevent uncontrolled execution.

## Topics

- Workflow vs agent
- Single vs multi-agent
- Routing
- Agent trajectory
- Tool calling
- Execution bounds
- Durable execution

## Core Flow

```text
Reason
 ↓
Tool
 ↓
Observe
 ↓
Reason
 ↓
Action
```

## 🎯 Practice Questions

1. When would you choose a **deterministic workflow instead of an agent**?
2. A customer wants separate RAG, refund, order and escalation agents. Would you accept this architecture immediately? What would you ask first?
3. An agent occasionally executes **20–30 tool calls** for a simple request. How would you control it?
4. What happens if a long-running agent crashes after completing 8 of 10 steps?
5. How would you explain **agent trajectory** and why it matters for evaluation?

---

# Module 7 — Tools, Actions & Enterprise Integration

## Goal

Move from chatbot architecture to production action-taking systems.

## Core Pattern

```text
Agent
 ↓
Recommendation
 ↓
Policy
 ↓
Executor
 ↓
Enterprise System
```

## Topics

- Controlled tool layer
- CRM/ERP/API integrations
- Read vs write tools
- Executor
- Idempotency
- Timeout
- Retry
- Circuit breaker

## 🎯 Practice Questions

1. Why would you avoid giving an LLM direct unrestricted access to a production CRM?
2. An agent issues a refund, the API times out, and the agent retries. How do you prevent a **double refund**?
3. A downstream ERP API frequently takes 30 seconds or fails. How would you protect the agent workflow?
4. Why might you separate the **agent's decision** from the **actual execution**?
5. How would you treat a read-only `get_order_status` tool differently from an `issue_refund` tool?

---

# Module 8 — Guardrails, Policy & Human Approval

## Goal

Safely allow agents to perform real business actions.

## Core Pattern

```text
Agent recommends
      ↓
Policy decides
      ↓
Executor acts
```

## Topics

- Deterministic policy
- Risk classification
- HITL
- Fail-open vs fail-closed
- Kill switch
- Least privilege

## 🎯 Practice Questions

1. Refunds below $100 can happen automatically, while refunds above $500 require manager approval. Where should this rule live?
2. Why shouldn't the LLM itself be the final authority for a deterministic financial policy?
3. The policy service becomes unavailable during a $10,000 transaction. Should the system fail-open or fail-closed, and why?
4. How would you design a workflow where human approval may take several hours?
5. What would a **kill switch** disable in an action-taking agent?

---

# Module 9 — Scaling AI Systems

## Goal

Handle:

> **"Great. Now scale it to 100K users."**

## Topics

- Throughput
- Concurrency
- Horizontal scaling
- Stateless workers
- Rate limiting
- Admission control
- Backpressure
- Queueing
- Fair queueing
- Noisy neighbor
- Load shedding
- Multi-tenancy

## 🎯 Practice Questions

1. Your prototype supports 100 users. The customer now expects **100K users**. Walk through what changes.
2. Tenant A suddenly consumes 70% of model capacity and Tenant B starts experiencing poor latency. What is happening?
3. Explain the difference between **rate limiting and admission control**.
4. Incoming traffic is 10K requests/sec but the system can process only 5K. What mechanisms would you consider?
5. Why would you prefer **stateless workers + external durable state** when horizontally scaling agents?

---

# Module 10 — Latency Optimization ⚡

## Goal

Diagnose latency before optimizing.

## Latency Decomposition

```text
Total Latency
     │
     ├── Queue
     ├── Retrieval
     ├── LLM
     ├── Agent
     ├── Tools
     └── Network
```

## Topics

- P50/P95/P99
- TTFT
- Streaming
- Parallelization
- Sequential LLM hops
- Retrieval latency
- Tool latency
- Queue latency
- Async processing

## 🎯 Practice Questions

1. Average latency is 3 seconds but P99 is 25 seconds. What does this tell you?
2. Your agent calls CRM, order and ticket APIs sequentially. Each takes 1 second. What obvious optimization would you consider?
3. The model itself takes only 2 seconds but total latency is 12 seconds. How would you investigate?
4. When does **streaming** improve perceived latency without actually reducing total compute time?
5. A research task takes five minutes. Would you continue optimizing it as a synchronous API request or change the interaction model?

---

# Module 11 — Cost Optimization 💰

## Goal

Understand and control AI economics.

## Cost Decomposition

```text
Cost / Task
    │
    ├── Model
    ├── Input Tokens
    ├── Output Tokens
    ├── Retrieval
    ├── Tools
    ├── Compute
    └── Retries
```

## Topics

- Model routing
- Context optimization
- Caching
- Reduce model calls
- Deterministic logic
- Agent bounds
- Batch processing
- Cost attribution
- Cost per successful task

## 🎯 Practice Questions

1. The customer's LLM bill doubles after launching an agent. What would you inspect first?
2. Why might **model routing** reduce cost without materially reducing quality?
3. Conversation history grows indefinitely and token cost keeps increasing. What would you change?
4. Why is **cost per successful task** often more meaningful than cost/request?
5. Your architecture uses five LLM calls for every request. How would you determine whether all five are necessary?

---

# Module 12 — Reliability & Failure Handling

## Goal

Answer:

> **"What happens when something fails?"**

## Topics

- Timeout
- Retry
- Exponential backoff
- Jitter
- Circuit breaker
- Idempotency
- Graceful degradation
- Model fallback
- DLQ
- Checkpointing
- Blast radius

## Failure Mental Model

```text
Failure
 ↓
Timeout?
 ↓
Retry?
 ↓
Fallback?
 ↓
Degrade?
 ↓
Recover?
 ↓
Escalate?
```

## 🎯 Practice Questions

1. Your primary model provider becomes unavailable. What happens next?
2. A tool API returns intermittent 503 errors. What retry strategy would you use?
3. Why can aggressive retries actually make an outage worse?
4. A recommendation feature fails. Should the entire customer-support system become unavailable?
5. A background event fails processing after several retries. What should happen next?

---

# Module 13 — AI Evaluation

## Goal

Make AI quality measurable.

## Topics

### RAG

- Retrieval relevance
- Recall
- Groundedness
- Correctness

### Agents

- Routing
- Tool selection
- Tool arguments
- Trajectory
- Task success

### Evaluation Types

- Deterministic
- Non-deterministic
- Offline
- Online

## Key Principle

```text
Good Answer
    ≠
Successful Task
```

## 🎯 Practice Questions

1. How would you evaluate a customer-support system containing both **RAG and action-taking agents**?
2. Give examples of **deterministic checks** for an agent.
3. Which checks require semantic or non-deterministic evaluation?
4. The final response sounds perfect, but the agent used the wrong tool and never actually cancelled the order. How should evaluation catch this?
5. Why do we need both **offline and online evaluation**?

---

# Module 14 — Release & Change Management

## Goal

Safely ship AI changes.

## Core Flow

```text
Candidate
   ↓
Offline Evaluation
   ↓
Release Gate
   ↓
Shadow / Canary
   ↓
Production
   ↓
Monitor
```

## Topics

- Versioning
- Release gates
- Canary
- Shadow traffic
- Feature flags
- Rollback
- Kill switch

## 🎯 Practice Questions

1. Your team creates a new prompt that performs better on 20 examples. Would you immediately deploy it?
2. Explain when you would use **shadow traffic vs canary deployment**.
3. How would you release a new agent to only two enterprise customers first?
4. Which artifacts should be versioned besides the model itself?
5. Production quality suddenly drops after a new release. What mechanisms should allow you to respond quickly?

---

# Module 15 — Observability & Production Operations

## Goal

Understand what is happening inside the system after deployment.

## Topics

- Logs
- Metrics
- Distributed traces
- AI telemetry
- Audit
- SLI
- SLO
- SLA

## Trace Mental Model

```text
Request
 ↓
Router
 ↓
Agent
 ↓
LLM
 ↓
Retriever
 ↓
Tool
 ↓
Response
```

## 🎯 Practice Questions

1. A user says, **"My request took 18 seconds yesterday."** What telemetry would you inspect?
2. Explain the difference between **logging, metrics and tracing** using an agent request.
3. Which AI-specific telemetry would you capture beyond normal infrastructure metrics?
4. Compliance asks, **"Why did the agent issue this refund?"** What information should be available?
5. Explain **SLI vs SLO vs SLA** using an AI assistant latency example.

---

# Module 16 — Security & Enterprise Multi-Tenancy

## Goal

Make the system enterprise-ready.

## Topics

- Authentication
- Authorization
- RBAC
- Permission-aware RAG
- Least privilege
- Tenant isolation
- Secrets
- Sensitive data
- Data residency
- Defense in depth

## Core Mental Model

```text
Identity
 ↓
Authorization
 ↓
Data Permission
 ↓
Tool Permission
 ↓
Policy
 ↓
Human Approval
 ↓
Audit
```

## 🎯 Practice Questions

1. Employee A can access HR documents while Employee B cannot. How should this affect retrieval?
2. Why is filtering unauthorized documents **after generation** a weak security design?
3. What permissions would you give a refund agent following least-privilege principles?
4. A shared platform serves 50 enterprise tenants. What needs tenant isolation?
5. A European customer says their data cannot leave a particular region. What architectural concerns does this introduce?

---

# Module 17 — Trade-Off Thinking

## Goal

Explain **why** you made architecture decisions.

## Core Principle

> **"I'm choosing X because of requirement Y. The trade-off is Z."**

## Topics

### Cost ↔ Quality ↔ Latency

```text
             QUALITY
              /   \
             /     \
          COST ─── LATENCY
```

### Common Trade-Offs

- More retrieval → recall ↑, cost/latency ↑
- More agents → possible quality ↑, complexity/cost ↑
- Cache → latency/cost ↓, freshness risk ↑
- Strong model → quality ↑, latency/cost ↑
- More autonomy → human effort ↓, business risk ↑
- Async → better scalability, immediate response ↓

## 🎯 Practice Questions

1. You can improve answer quality by adding another LLM critic, but it adds 3 seconds and 40% cost. How would you reason about the decision?
2. The customer wants maximum retrieval recall but also very low latency. What trade-off would you discuss?
3. When might you intentionally choose a smaller model even if a larger model performs slightly better?
4. Caching tool responses reduces latency dramatically. What new risk does caching introduce?
5. The interviewer asks, **"Why did you choose this architecture instead of a simpler one?"** How would you structure your answer?

---

# Module 18 — End-to-End FDE Interview Execution

## Goal

Combine everything into one repeatable interview flow.

```text
1. Business Problem
        ↓
2. Current Workflow
        ↓
3. Discovery
        ↓
4. Functional Requirements
        ↓
5. NFRs
        ↓
6. Happy-Path Architecture
        ↓
7. Data / RAG
        ↓
8. Agents + Tools
        ↓
9. Policy / HITL
        ↓
10. Scale
        ↓
11. Latency
        ↓
12. Cost
        ↓
13. Reliability
        ↓
14. Evaluation
        ↓
15. Release
        ↓
16. Observability
        ↓
17. Trade-Offs
```

## 🎯 Full Case-Study Practice

These should be solved **without looking at the earlier modules**.

### Case 1 — Customer Support Agent

> A large e-commerce company wants an AI customer-support system that can answer questions, check orders and issue refunds.

Cover:

```text
Discovery
→ Requirements
→ Architecture
→ RAG
→ Tools
→ Policy
→ Scale
→ Cost/Latency
→ Evaluation
```

---

### Case 2 — Enterprise Knowledge Assistant

> A multinational company wants a ChatGPT-style assistant over millions of internal documents, but employees have different access permissions.

Focus on:

```text
RAG
Permission-aware retrieval
Scale
Latency
Security
Evaluation
```

---

### Case 3 — Logistics Exception Agent

> A logistics company wants AI to detect shipment exceptions and automatically resolve routine cases.

Focus on:

```text
Events
Agents
Tools
Policy
HITL
Idempotency
Reliability
Audit
```

---

### Case 4 — SRE Incident Agent

> An enterprise wants an AI agent that investigates production incidents and can execute remediation actions.

Focus on:

```text
Tools
Observability
Agent reasoning
Permissions
Policy
HITL
Kill switch
Audit
```

---

### Case 5 — Deep Research Agent

> Build an enterprise research agent that searches multiple sources and may run for 10–20 minutes.

Focus on:

```text
Async execution
Queue
Checkpoint
Agent bounds
Cost
Long-running state
Evaluation
```

---

### Case 6 — Multi-Tenant AI Platform

> Build a shared AI platform supporting 100 enterprise customers and multiple LLM providers.

Focus on:

```text
API Gateway
Model Gateway
Multi-tenancy
Quotas
Fairness
Model routing
Cost attribution
Observability
```

---

# Recommended Learning Sequence

## Phase 1 — Problem Decomposition

```text
Module 1 — Discovery
Module 2 — Functional Requirements
Module 3 — Non-Functional Requirements
```

**Outcome:** Understand before designing.

---

## Phase 2 — Architecture

```text
Module 4 — Core Components
Module 5 — RAG
Module 6 — Agents
Module 7 — Tools
Module 8 — Policy / HITL
```

**Outcome:** Build the right system.

---

## Phase 3 — Production Scale

```text
Module 9  — Scaling
Module 10 — Latency
Module 11 — Cost
Module 12 — Reliability
```

**Outcome:** Turn the POC into production.

---

## Phase 4 — Production Quality

```text
Module 13 — Evaluation
Module 14 — Release
Module 15 — Observability
Module 16 — Security
```

**Outcome:** Safely operate the system.

---

## Phase 5 — Interview Mastery

```text
Module 17 — Trade-Offs
Module 18 — Full Case Studies
```

At this stage:

> **Stop adding terminology. Start solving cases.**

---

# 🔥 Trigger → Concept Cheat Sheet

The objective is not to memorize definitions.

Train yourself to hear a customer/interviewer statement and automatically recognize the architecture concern.

| Interviewer Says                               | Your Brain Should Trigger                                  |
| ---------------------------------------------- | ---------------------------------------------------------- |
| **"100K users"**                         | Horizontal scaling, stateless workers, rate limits, queues |
| **"Traffic suddenly spikes"**            | Queue, admission control, backpressure                     |
| **"One tenant generates huge traffic"**  | Noisy neighbor, quota, fair queue                          |
| **"Traffic exceeds capacity"**           | Admission control, load shedding                           |
| **"Multiple enterprise customers"**      | Multi-tenancy, isolation, quotas, cost attribution         |
| **"Request sometimes takes 20 seconds"** | Stage tracing, P95/P99                                     |
| **"Chat feels slow"**                    | Streaming, TTFT, fewer sequential hops                     |
| **"Three independent APIs"**             | Parallelization                                            |
| **"External API is slow"**               | Timeout, cache, async, fallback                            |
| **"External API keeps failing"**         | Retry, backoff, circuit breaker                            |
| **"Action happened twice"**              | Idempotency                                                |
| **"Message may arrive twice"**           | At-least-once + idempotent consumer                        |
| **"Background job keeps failing"**       | Retry → DLQ                                               |
| **"Agent runs 10 minutes"**              | Async + queue + durable state                              |
| **"Agent crashes halfway"**              | Checkpoint + resume, reconcile uncertain actions           |
| **"Human approves tomorrow"**            | Durable state + HITL                                       |
| **"Need conversation history"**          | Session state                                              |
| **"Need long-term preferences"**         | Memory                                                     |
| **"Prompt keeps growing"**               | Bounded context + summarization                            |
| **"Repeated questions"**                 | Cache                                                      |
| **"Information changes frequently"**     | TTL / freshness                                            |
| **"Need company documents"**             | RAG                                                        |
| **"Need current order status"**          | Live API/tool                                              |
| **"RAG can't find answer"**              | Recall, chunking, hybrid search                            |
| **"RAG retrieves junk"**                 | Precision, filtering, reranking                            |
| **"Different document permissions"**     | Permission-aware retrieval                                 |
| **"Unsupported AI claims"**              | Grounding, citations, fallback                             |
| **"Different request types"**            | Router                                                     |
| **"Multiple workflow steps"**            | Orchestrator                                               |
| **"Routing is deterministic"**           | Code/rules before LLM                                      |
| **"Agent keeps calling tools"**          | Execution bounds                                           |
| **"Agent accesses production"**          | Controlled tools                                           |
| **"Agent modifies customer data"**       | Policy + executor + audit                                  |
| **"Large refund needs approval"**        | Deterministic policy + HITL                                |
| **"Agent has powerful credentials"**     | Least privilege                                            |
| **"Policy unavailable"**                 | Fail-closed for risky actions                              |
| **"Agent behaving dangerously"**         | Kill switch                                                |
| **"Multiple models/providers"**          | Model gateway                                              |
| **"Model provider unavailable"**         | Provider fallback                                          |
| **"AI bill exploded"**                   | Model routing, context, cache, calls                       |
| **"Who caused the spend?"**              | Cost attribution                                           |
| **"Need cheaper AI"**                    | Cost per successful task                                   |
| **"New prompt/model"**                   | Offline eval + release gate                                |
| **"Test on real traffic safely"**        | Shadow                                                     |
| **"Gradual production rollout"**         | Canary                                                     |
| **"Only some tenants get feature"**      | Feature flag                                               |
| **"New version performs badly"**         | Rollback                                                   |
| **"Is the agent good?"**                 | Offline + online evaluation                                |
| **"Good answer, task failed"**           | Task success                                               |
| **"Wrong tool used"**                    | Trajectory/tool evaluation                                 |
| **"Exact pass/fail checks"**             | Deterministic evaluator                                    |
| **"Semantic quality"**                   | LLM/human judge                                            |
| **"Why was this slow?"**                 | Observability/tracing                                      |
| **"Why did AI take this action?"**       | Audit                                                      |
| **"Latency commitment"**                 | SLI → SLO → SLA                                          |
| **"Worker dies"**                        | Stateless compute + durable state                          |
| **"Failure shouldn't affect everyone"**  | Blast-radius reduction                                     |
| **"Sensitive enterprise data"**          | AuthN, AuthZ, least privilege, audit                       |
| **"Safe enterprise agent"**              | Defense in depth                                           |

---

# Final Interview Mental Model

```text
                 CUSTOMER
                    ↓
            WHY ARE WE BUILDING?
                    ↓
                DISCOVERY
                    ↓
              REQUIREMENTS
                    ↓
               HAPPY PATH
                    ↓
         ┌──────────┼──────────┐
         ↓          ↓          ↓
        DATA        AI       ACTION
        RAG       Agents      Tools
                              ↓
                       Policy / Human
                    ↓
              PRESSURE TEST
                    ↓
         ┌──────────┼──────────┐
         ↓          ↓          ↓
       Scale      Latency     Cost
         └──────────┼──────────┘
                    ↓
               FAILURES
                    ↓
              EVALUATION
                    ↓
                RELEASE
                    ↓
          OBSERVE + OPERATE
                    ↓
               TRADE-OFFS
```

---

# Final Interview Checklist

Before finishing any architecture, mentally ask:

```text
□ Did I understand the BUSINESS problem?

□ Did I understand the CURRENT workflow?

□ Did I define FUNCTIONAL requirements?

□ Did I define measurable NFRs?

□ Is every major architecture box JUSTIFIED?

□ Where does DATA come from?

□ Does AI ANSWER, RECOMMEND or ACT?

□ What requires HUMAN approval?

□ Does it SCALE?

□ What makes it SLOW?

□ What makes it EXPENSIVE?

□ What happens when dependencies FAIL?

□ How is it SECURED?

□ How do I measure AI QUALITY?

□ How do I RELEASE changes safely?

□ How do I OBSERVE it in production?

□ What are my major TRADE-OFFS?
```

---

# The Core FDE Principle

Do **not** memorize architectures.

Memorize:

```text
Customer says X
      ↓
Requirement Y
      ↓
Problem / Constraint Z
      ↓
Component / Pattern A
      ↓
Trade-off B
```

Example:

```text
"Refunds above $500 are risky."
              ↓
High-risk actions need approval
              ↓
LLM cannot be final authority
              ↓
Policy Engine + HITL
              ↓
Safer execution
but additional latency
```

Another example:

```text
"We expect 100K users."
          ↓
High concurrency
          ↓
Finite model capacity
          ↓
Rate Limit + Queue
+ Horizontal Scaling
          ↓
Better resilience
but more infrastructure
```

> **Interview rule:** Don't name a component until you can explain which requirement caused you to introduce it.

---

# One-Line FDE Framework

> **Start from the customer problem, turn discovery into measurable requirements, build the simplest happy-path architecture, and then pressure-test it across scale, latency, cost, reliability, security, AI quality and operations—adding components only when a requirement justifies them.**

---

## Sources (checked 27 Sep 2026)

- [Google SRE Book - Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — SLI, SLO and SLA definitions
- [Google SRE Workbook - Canarying Releases](https://sre.google/workbook/canarying-releases/) — canary as a partial, time-limited rollout that is evaluated
- [AWS Builders' Library - Timeouts, retries and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter) — retries can amplify an outage; backoff and jitter
- [Azure Architecture Center - Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) — stop calling a failing dependency for a while
- [Amazon SQS Developer Guide - Dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html) — retry, then move to a DLQ
- [Stripe API reference - Idempotent requests](https://docs.stripe.com/api/idempotent_requests) — idempotency keys prevent a double refund on retry
- [Temporal blog - Idempotency and durable execution](https://temporal.io/blog/idempotency-and-durable-execution) — at-least-once delivery; checkpoints don't stop duplicate side effects
- [OWASP GenAI LLM08:2025 Vector and Embedding Weaknesses](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/) — permission-aware retrieval
- [OWASP GenAI LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) — least privilege and controlled tools for agents
